from __future__ import annotations

import json
from pathlib import Path

from ai_image_cli.errors import CliError, ExitCode


def normalize_json_output(raw_text: str) -> str:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise CliError("Gemini returned invalid JSON output.", ExitCode.OUTPUT, details=str(exc)) from exc
    return json.dumps(parsed, indent=2, ensure_ascii=False)


def write_output(text: str, output_path: Path | None) -> None:
    if output_path is None:
        return
    output_path.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
