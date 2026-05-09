from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from ai_image_cli.errors import CliError, ExitCode

ENV_KEYS = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_IMAGE_CLI_GOOGLE_API_KEY",
)

CACHE_DIR_ENV_KEY = "XDG_CONFIG_HOME"
CACHE_DIR_NAME = "ai-image-cli"
CACHE_FILE_NAME = "google-api-key"


def _normalize_api_key(api_key: str, *, error_message: str) -> str:
    normalized_api_key = api_key.strip()
    if not normalized_api_key:
        raise CliError(error_message, ExitCode.AUTH)
    return normalized_api_key


def load_dotenv_file(dotenv_path: str | Path | None) -> Path | None:
    if dotenv_path is None:
        return None
    path = Path(dotenv_path)
    if not path.exists():
        return None
    load_dotenv(dotenv_path=path, override=False)
    return path


def _get_env_api_key() -> str | None:
    for key in ENV_KEYS:
        value = os.getenv(key)
        if value is None:
            continue
        normalized_value = value.strip()
        if normalized_value:
            return normalized_value
    return None


def get_api_key_cache_path() -> Path:
    config_home = os.getenv(CACHE_DIR_ENV_KEY)
    if config_home:
        return Path(config_home).expanduser() / CACHE_DIR_NAME / CACHE_FILE_NAME
    return Path.home() / ".config" / CACHE_DIR_NAME / CACHE_FILE_NAME


def load_cached_api_key() -> str | None:
    cache_path = get_api_key_cache_path()
    if not cache_path.exists():
        return None
    try:
        return _normalize_api_key(
            cache_path.read_text(encoding="utf-8"),
            error_message=f"Cached Gemini API key at {cache_path} is empty.",
        )
    except CliError:
        raise
    except OSError as exc:
        raise CliError(f"Unable to read cached Gemini API key at {cache_path}.", ExitCode.AUTH, details=str(exc)) from exc


def save_api_key(api_key: str) -> Path:
    cleaned_api_key = _normalize_api_key(api_key, error_message="No Gemini API key provided for --auth.")

    cache_path = get_api_key_cache_path()
    cache_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(cache_path.parent, stat.S_IRWXU)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=cache_path.parent,
        prefix=f".{CACHE_FILE_NAME}.",
        delete=False,
    ) as temp_file:
        temp_file.write(cleaned_api_key + "\n")
        temp_path = Path(temp_file.name)

    os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)
    temp_path.replace(cache_path)
    os.chmod(cache_path, stat.S_IRUSR | stat.S_IWUSR)
    return cache_path


def resolve_api_key(*, explicit_api_key: str | None, dotenv_path: str | Path | None) -> str:
    if explicit_api_key is not None:
        return _normalize_api_key(explicit_api_key, error_message="--api-key was provided but is empty.")

    env_api_key = _get_env_api_key()
    if env_api_key:
        return env_api_key

    cached_api_key = load_cached_api_key()
    if cached_api_key:
        return cached_api_key

    load_dotenv_file(dotenv_path)

    env_api_key = _get_env_api_key()
    if env_api_key:
        return env_api_key

    raise CliError(
        "No Gemini API key found. Use --api-key or set GEMINI_API_KEY, GOOGLE_API_KEY, or GEMINI_IMAGE_CLI_GOOGLE_API_KEY.",
        ExitCode.AUTH,
    )
