---
name: ai-image-cli
description: Use the local ai-image-cli to analyze images, webpage screenshots, and mobile app screenshots with Gemini 3 Flash
---

# AI Image CLI

Use this skill when you need image analysis from a local file, URL, base64 string, or stdin base64.

## When to Use

- Analyze a general image.
- Inspect a webpage screenshot.
- Review a mobile app screenshot.

## Commands

- `ai-image-cli analyze --file <path>`
- `ai-image-cli analyze --url <url>`
- `ai-image-cli analyze-webpage --file <path> --format json`
- `ai-image-cli analyze-mobile --file <path> --format json`

## Guidance

- Prefer `--format json` for structured downstream use.
- Use `--focus` on webpage and mobile commands when the task is narrow.
- Cache a Gemini key once with top-level `ai-image-cli --auth` so later runs can omit `--api-key`.
- Read stdout for results and stderr for diagnostics.

## Examples

- `ai-image-cli analyze --file screenshot.png --prompt "Summarize the visible error state"`
- `printf '%s' "$GOOGLE_API_KEY" | ai-image-cli --auth`
- `ai-image-cli analyze-webpage --file homepage.png --focus accessibility --format json`
- `ai-image-cli analyze-mobile --file app.png --platform ios --focus navigation --format json`
