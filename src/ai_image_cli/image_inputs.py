from __future__ import annotations

import base64
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

from ai_image_cli.errors import CliError, ExitCode
from ai_image_cli.models import ImagePayload

SUPPORTED_MIME_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_INLINE_BYTES = 20 * 1024 * 1024
MAX_INPUT_BYTES = 50 * 1024 * 1024
URL_TIMEOUT_SECONDS = 30


def validate_single_source(*, file: str | None, url: str | None, base64_value: str | None, stdin_base64: bool) -> None:
    selected = [bool(file), bool(url), bool(base64_value), bool(stdin_base64)]
    if sum(selected) != 1:
        raise CliError(
            "Specify exactly one image source: --file, --url, --base64, or --stdin-base64.",
            ExitCode.USAGE,
        )


def _sniff_mime_type(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def detect_mime_type(data: bytes, *, explicit_mime_type: str | None, filename: str | None) -> str:
    sniffed = _sniff_mime_type(data)
    guessed = mimetypes.guess_type(filename or "", strict=False)[0] if filename else None
    chosen = explicit_mime_type or sniffed or guessed
    if chosen not in SUPPORTED_MIME_TYPES:
        raise CliError(
            "Unsupported or unrecognized image type. Supported types: PNG, JPEG, WebP, GIF.",
            ExitCode.IMAGE,
        )
    if explicit_mime_type and sniffed and explicit_mime_type != sniffed:
        raise CliError(
            f"Provided MIME type {explicit_mime_type!r} does not match detected image type {sniffed!r}.",
            ExitCode.IMAGE,
        )
    return chosen


def _check_size(data: bytes, *, upload: bool) -> None:
    if len(data) > MAX_INPUT_BYTES:
        raise CliError("Image exceeds the maximum supported size of 50 MB.", ExitCode.IMAGE)
    if not upload and len(data) > MAX_INLINE_BYTES:
        raise CliError(
            "Image is too large for inline Gemini requests. Re-run with --upload.",
            ExitCode.IMAGE,
        )


def _decode_base64(raw_value: str) -> bytes:
    value = raw_value.strip()
    if not value:
        raise CliError("Base64 input is empty.", ExitCode.INPUT)
    if value.startswith("data:") and "," in value:
        value = value.split(",", 1)[1]
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise CliError("Invalid base64 image input.", ExitCode.INPUT, details=str(exc)) from exc


def _read_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ai-image-cli/0.1.0"})
    try:
        with urllib.request.urlopen(request, timeout=URL_TIMEOUT_SECONDS) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_INPUT_BYTES:
                raise CliError("Remote image exceeds the maximum supported size of 50 MB.", ExitCode.IMAGE)
            data = response.read(MAX_INPUT_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise CliError(f"Failed to download image URL: HTTP {exc.code}.", ExitCode.INPUT, details=str(exc)) from exc
    except urllib.error.URLError as exc:
        raise CliError("Failed to download image URL.", ExitCode.TIMEOUT, details=str(exc)) from exc
    if len(data) > MAX_INPUT_BYTES:
        raise CliError("Remote image exceeds the maximum supported size of 50 MB.", ExitCode.IMAGE)
    return data


def resolve_image_input(
    *,
    file: str | None,
    url: str | None,
    base64_value: str | None,
    stdin_base64: bool,
    mime_type: str | None,
    upload: bool,
    stdin_text: str | None = None,
) -> ImagePayload:
    validate_single_source(file=file, url=url, base64_value=base64_value, stdin_base64=stdin_base64)

    if file:
        file_path = Path(file)
        if not file_path.exists() or not file_path.is_file():
            raise CliError(f"Image file not found: {file}", ExitCode.INPUT)
        data = file_path.read_bytes()
        _check_size(data, upload=upload)
        resolved_mime = detect_mime_type(data, explicit_mime_type=mime_type, filename=file_path.name)
        return ImagePayload(data=data, mime_type=resolved_mime, source=str(file_path), file_path=file_path)

    if url:
        data = _read_url(url)
        _check_size(data, upload=upload)
        resolved_mime = detect_mime_type(data, explicit_mime_type=mime_type, filename=url)
        return ImagePayload(data=data, mime_type=resolved_mime, source=url)

    if base64_value is not None:
        data = _decode_base64(base64_value)
    else:
        raw_stdin = stdin_text if stdin_text is not None else sys.stdin.read()
        data = _decode_base64(raw_stdin)

    _check_size(data, upload=upload)
    resolved_mime = detect_mime_type(data, explicit_mime_type=mime_type, filename=None)
    source = "stdin" if stdin_base64 else "base64"
    return ImagePayload(data=data, mime_type=resolved_mime, source=source)
