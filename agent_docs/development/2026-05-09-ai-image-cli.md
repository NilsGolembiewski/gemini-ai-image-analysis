# AI Image CLI Development Report

**Date:** 2026-05-09
**Status:** complete

## What Changed

Implemented the new `ai-image-cli` package, added Gemini integration, CLI subcommands, image input handling, tests, docs, and the `skills/ai-image-cli` skill. Added a follow-up auth-cache flow via top-level `--auth` plus cached-key lookup for normal CLI runs.

## Why

The repository needed a pip-installable replacement for the reference image MCP server, but as a Python CLI using Gemini with a fixed internal model.

## Approach

Used a minimal dependency footprint with `argparse`, `google-genai`, and `python-dotenv`. Structured prompts and schemas by command, validated image inputs before model calls, and preserved shell-safe stdout/stderr behavior. For the auth update, added a per-user cache path at `${XDG_CONFIG_HOME:-~/.config}/ai-image-cli/google-api-key`, private permissions (`0700` dir / `0600` file), stdin-based key capture for `--auth`, and cached-key resolution before dotenv fallback.

## Tests

- `python -m unittest discover -s tests -v`
- editable install with `pip install -e /workspace`
- live `ai-image-cli --help`
- live Gemini runs for general and specialist analysis
- live `ai-image-cli --auth` validation from stdin and `--api-key`

## Verification

- Unit tests passed.
- The installed console script executed successfully.
- Live Gemini responses were returned for both general image analysis and JSON specialist mobile analysis.
- Cached auth writes succeeded for both stdin and `--api-key`, and a later analysis run succeeded using only the cached key.

## Caveats

- HEIC/HEIF is deferred.
- The model ID is intentionally pinned to the preview identifier required by the current Gemini API behavior.
- Cached auth storage currently follows the Linux/XDG convention used in this environment.
