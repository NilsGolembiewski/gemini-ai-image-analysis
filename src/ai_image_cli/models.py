from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


OutputFormat = Literal["text", "json"]
CommandName = Literal["analyze", "analyze-webpage", "analyze-mobile"]


@dataclass(slots=True)
class ImagePayload:
    data: bytes
    mime_type: str
    source: str
    file_path: Path | None = None


@dataclass(slots=True)
class AnalysisRequest:
    command: CommandName
    prompt: str
    output_format: OutputFormat
    max_output_tokens: int | None = None
    temperature: float | None = None
    upload: bool = False


@dataclass(slots=True)
class AppConfig:
    api_key: str
    output_path: Path | None = None
    verbose: bool = False
    quiet: bool = False
