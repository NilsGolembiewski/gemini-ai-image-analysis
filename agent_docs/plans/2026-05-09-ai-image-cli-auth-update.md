# AI Image CLI Auth Cache Update

**Date:** 2026-05-09
**Status:** complete

## Summary

Added a top-level `--auth` flow to `ai-image-cli` that caches a Gemini/Google API key for later runs. The command accepts `--api-key` directly or reads the key from stdin, writes it to a per-user config path, and exits without requiring a subcommand.

## Files changed

- `src/ai_image_cli/cli.py`
- `src/ai_image_cli/config.py`
- `tests/test_cli.py`
- `tests/test_config.py`
- `README.md`
- `skills/ai-image-cli/SKILL.md`
- `agent_docs/development/2026-05-09-ai-image-cli.md`

## Auth cache design

- Cache path: `${XDG_CONFIG_HOME:-~/.config}/ai-image-cli/google-api-key`
- Directory permissions: `0700`
- File permissions: `0600`
- Write strategy: write to a temporary file in the target directory, then replace the final file atomically.

### Resolution precedence

Normal CLI runs now resolve the API key in this order:

1. `--api-key`
2. `GEMINI_API_KEY`
3. `GOOGLE_API_KEY`
4. `GEMINI_IMAGE_CLI_GOOGLE_API_KEY`
5. cached key file
6. matching keys loaded from `--dotenv-path` / `.env`

### `--auth` behavior

- `ai-image-cli --auth --api-key <key>` caches the supplied key and exits successfully.
- `ai-image-cli --auth` reads the key from stdin, trims surrounding whitespace, caches it, and exits successfully.
- `--auth` is intentionally separate from analysis commands and rejects subcommand usage.
- Empty explicit keys now fail cleanly instead of silently falling back to stdin or other auth sources.
- Blank environment variables are ignored so they do not mask a valid cached or dotenv key.
- Empty or unreadable cache files raise CLI auth errors instead of bubbling raw filesystem exceptions.

## Tests run and results

### Automated tests

```bash
PYTHONPATH="/workspace/src" /tmp/opencode/ai-image-cli-venv/bin/python -m unittest discover -s tests -v
```

- Result: 26 tests run, 26 passed

### Live validation

1. Stdin-based cache write and cached-key analysis run
   - Cached the key using `printf '%s' "$KEY" | ai-image-cli --auth`
   - Verified permissions were `700` for the directory and `600` for the file
   - Ran `ai-image-cli analyze --url ... --output ...` with only the cached key available
   - Result: success

2. Flag-based cache write
   - Ran `ai-image-cli --auth --api-key "$KEY"`
   - Verified permissions were `700` for the directory and `600` for the file
   - Result: success

## Caveats

- The cache location is currently Unix/XDG-oriented because this repository is being developed and validated on Linux.
- `--auth` reads the whole stdin stream when `--api-key` is omitted, so an interactive invocation waits for EOF before caching.
