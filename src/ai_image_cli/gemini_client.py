from __future__ import annotations

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path

from ai_image_cli.errors import CliError, ExitCode
from ai_image_cli.models import AnalysisRequest, ImagePayload

MODEL_ID = "gemini-3-flash-preview"
REQUEST_TIMEOUT_SECONDS = 90


def _run_with_timeout(func, *args, timeout: int = REQUEST_TIMEOUT_SECONDS, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError as exc:
            raise CliError("Gemini request timed out.", ExitCode.TIMEOUT) from exc


def _build_config(request: AnalysisRequest, response_schema: dict | None):
    config: dict[str, object] = {}
    if request.max_output_tokens is not None:
        config["max_output_tokens"] = request.max_output_tokens
    if request.temperature is not None:
        config["temperature"] = request.temperature
    if request.output_format == "json":
        config["response_mime_type"] = "application/json"
        if response_schema is not None:
            config["response_json_schema"] = response_schema
    return config or None


def _prepare_upload_path(image: ImagePayload) -> tuple[str, str | None]:
    if image.file_path is not None:
        return str(image.file_path), None
    suffix = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[image.mime_type]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp_file.write(image.data)
        temp_file.flush()
    finally:
        temp_file.close()
    return temp_file.name, temp_file.name


def analyze_with_gemini(
    *,
    api_key: str,
    image: ImagePayload,
    request: AnalysisRequest,
    response_schema: dict | None,
) -> str:
    try:
        from google import genai
        from google.genai import errors
        from google.genai import types
    except ImportError as exc:
        raise CliError("Missing dependency google-genai. Install the package dependencies first.", ExitCode.API) from exc

    upload_temp_path: str | None = None
    try:
        with genai.Client(api_key=api_key) as client:
            if request.upload:
                upload_path, upload_temp_path = _prepare_upload_path(image)
                uploaded_file = _run_with_timeout(client.files.upload, file=upload_path)
                contents = [uploaded_file, request.prompt]
            else:
                contents = [types.Part.from_bytes(data=image.data, mime_type=image.mime_type), request.prompt]

            config = _build_config(request, response_schema)
            response = _run_with_timeout(
                client.models.generate_content,
                model=MODEL_ID,
                contents=contents,
                config=config,
            )
            return response.text or ""
    except errors.APIError as exc:
        message = exc.message if getattr(exc, "message", None) else "Gemini API request failed."
        raise CliError(message, ExitCode.API, details=f"HTTP {getattr(exc, 'code', 'unknown')}") from exc
    except CliError:
        raise
    except Exception as exc:
        raise CliError("Unexpected Gemini client error.", ExitCode.API, details=str(exc)) from exc
    finally:
        if upload_temp_path:
            try:
                os.unlink(upload_temp_path)
            except FileNotFoundError:
                pass
