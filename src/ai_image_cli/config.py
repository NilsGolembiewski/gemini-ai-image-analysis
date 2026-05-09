from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from ai_image_cli.errors import CliError, ExitCode

ENV_KEYS = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_IMAGE_CLI_GOOGLE_API_KEY",
)


def load_dotenv_file(dotenv_path: str | Path | None) -> Path | None:
    if dotenv_path is None:
        return None
    path = Path(dotenv_path)
    if not path.exists():
        return None
    load_dotenv(dotenv_path=path, override=False)
    return path


def resolve_api_key(*, explicit_api_key: str | None, dotenv_path: str | Path | None) -> str:
    if explicit_api_key:
        return explicit_api_key

    for key in ENV_KEYS:
        value = os.getenv(key)
        if value:
            return value

    load_dotenv_file(dotenv_path)

    for key in ENV_KEYS:
        value = os.getenv(key)
        if value:
            return value

    raise CliError(
        "No Gemini API key found. Use --api-key or set GEMINI_API_KEY, GOOGLE_API_KEY, or GEMINI_IMAGE_CLI_GOOGLE_API_KEY.",
        ExitCode.AUTH,
    )
