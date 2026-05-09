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
5. matching keys from `--dotenv-path` / `.env`

## Commands

```bash
ai-image-cli analyze --file screenshot.png
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
