# ai-image-cli

`ai-image-cli` is a pip-installable Python CLI for analyzing images, webpage screenshots, and mobile app screenshots with Gemini 3 Flash.

## Install

```bash
pip install .
```

## Authentication

The CLI resolves API keys in this order:

1. `--api-key`
2. `GEMINI_API_KEY`
3. `GOOGLE_API_KEY`
4. `GEMINI_IMAGE_CLI_GOOGLE_API_KEY`
5. cached key at `${XDG_CONFIG_HOME:-~/.config}/ai-image-cli/google-api-key`
6. matching keys from `--dotenv-path` / `.env`

Cache a key for future runs with either:

```bash
ai-image-cli --auth --api-key "$GOOGLE_API_KEY"
printf '%s' "$GOOGLE_API_KEY" | ai-image-cli --auth
```

Use `--auth` by itself, without an analysis subcommand. When reading from stdin, the command waits for EOF before caching.

The cache directory is created with `0700` permissions and the key file is written with `0600` permissions.

## Commands

```bash
ai-image-cli analyze --file screenshot.png
ai-image-cli --auth --api-key "$GOOGLE_API_KEY"
ai-image-cli analyze-webpage --file homepage.png --format json
ai-image-cli analyze-mobile --file app.png --platform ios --format json
```

## Image sources

Each command accepts exactly one of:

- `--file PATH`
- `--url URL`
- `--base64 STRING`
- `--stdin-base64`

## Output formats

- `--format text` prints plain text.
- `--format json` prints valid JSON only.

## Examples

```bash
ai-image-cli analyze --file screenshot.png --prompt "Summarize the visible issue"
ai-image-cli analyze --url https://example.com/example.jpg --format json
printf '%s' "$IMAGE_BASE64" | ai-image-cli analyze-webpage --stdin-base64 --format json
ai-image-cli analyze-mobile --file mobile.png --platform android --focus navigation --format json
```
