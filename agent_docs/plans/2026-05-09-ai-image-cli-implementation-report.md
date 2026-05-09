# AI Image CLI Implementation Report

**Date:** 2026-05-09
**Status:** complete

## Summary

Implemented a pip-installable Python CLI named `ai-image-cli` with three commands: `analyze`, `analyze-webpage`, and `analyze-mobile`. The implementation uses Gemini through the `google-genai` SDK with a fixed internal model constant of `gemini-3-flash-preview` and includes a concise OpenCode skill at `skills/ai-image-cli/SKILL.md`.

## Files changed

- `pyproject.toml`
- `README.md`
- `src/ai_image_cli/__init__.py`
- `src/ai_image_cli/__main__.py`
- `src/ai_image_cli/cli.py`
- `src/ai_image_cli/config.py`
- `src/ai_image_cli/errors.py`
- `src/ai_image_cli/formatters.py`
- `src/ai_image_cli/gemini_client.py`
- `src/ai_image_cli/image_inputs.py`
- `src/ai_image_cli/models.py`
- `src/ai_image_cli/prompts.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_image_inputs.py`
- `tests/test_prompts.py`
- `skills/ai-image-cli/SKILL.md`

## Architecture decisions

- Used a standard `src/` layout with `setuptools` and a console script entrypoint `ai-image-cli`.
- Kept the CLI implementation on the standard library `argparse` path to reduce dependency surface while still supporting subcommands, aliases, shared options, and shell-friendly output.
- Limited runtime dependencies to `google-genai` and `python-dotenv`.
- Implemented API key resolution with explicit precedence for `--api-key`, standard Gemini env vars, and the repo-specific `GEMINI_IMAGE_CLI_GOOGLE_API_KEY`.
- Kept the model fixed internally with `MODEL_ID = "gemini-3-flash-preview"`; no model-selection UX was added.
- Used prompt builders plus JSON schema-driven output for `--format json`, with specialist schemas for webpage and mobile analysis.
- Added support for local file, URL, inline base64, and stdin base64 image sources.
- Added optional Gemini File API upload mode via `--upload`, using temporary files for non-file sources.
- Normalized CLI errors into defined exit codes for usage, input, image validation, auth, API, output, and timeout failures.

## Tests run and results

### Automated tests

Command:

```bash
/tmp/opencode/ai-image-cli-venv/bin/python -m unittest discover -s tests -v
```

Result:

- 15 tests run
- 15 tests passed

Coverage focus:

- API key resolution
- source validation and MIME detection
- base64/stdin/file input handling
- prompt generation
- JSON CLI output behavior
- prompt file handling
- usage-error handling for conflicting flags

### Packaging / install validation

Command:

```bash
/tmp/opencode/ai-image-cli-venv/bin/pip install -e /workspace
```

Result:

- Editable install succeeded.

### CLI help validation

Command:

```bash
/tmp/opencode/ai-image-cli-venv/bin/ai-image-cli --help
```

Result:

- Help output rendered successfully with all expected subcommands.

### Live Gemini validation

Commands:

```bash
/tmp/opencode/ai-image-cli-venv/bin/ai-image-cli analyze --url "https://storage.googleapis.com/generativeai-downloads/images/scones.jpg" --dotenv-path "/workspace/.env"

/tmp/opencode/ai-image-cli-venv/bin/ai-image-cli analyze-mobile --file "/tmp/opencode/mobile-homepage.png" --platform android --format json --dotenv-path "/workspace/.env"
```

Result:

- General image analysis succeeded against Gemini.
- JSON-mode specialist mobile analysis succeeded against Gemini.

## Gaps / tradeoffs

- HEIC/HEIF support was intentionally not included in v1; the CLI currently supports PNG, JPEG, WebP, and GIF.
- JSON schemas are intentionally moderate and practical rather than exhaustive.
- The CLI uses synchronous request handling with a thread-based timeout wrapper rather than a more complex async implementation.
- `--output` writes the result to a file instead of stdout, matching the report spec; callers should read the output file in that mode.
- File upload mode is implemented for all source types, but only activated when `--upload` is explicitly set.
