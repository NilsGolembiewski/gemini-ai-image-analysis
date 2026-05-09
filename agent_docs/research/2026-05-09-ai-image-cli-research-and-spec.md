# Research: ai-image-cli reference analysis, Gemini SDK validation, and CLI/skill spec

**Date:** 2026-05-09
**Scope:** Inspect this repository, analyze the reference project `JonathanJude/openrouter-image-mcp`, research the current Gemini Python SDK and Gemini API behavior needed for an equivalent Python CLI, verify whether the repository's `.env` credentials can call Gemini 3 Flash, and define an implementation-ready spec for a pip-installable CLI named `ai-image-cli` plus a concise OpenCode skill.

## Repo findings

### Current repository state

- Repository root is minimal and currently contains:
  - `.env`
  - `.gitignore`
  - `.opencode/`
  - `application_instructions.md`
- There is **no existing Python package scaffold** in the repository root:
  - no `pyproject.toml`
  - no `requirements.txt`
  - no `README.md`
- `.opencode/package.json` exists but is only for OpenCode plugin/skill support and depends on `@opencode-ai/plugin`.
- Existing local skills under `.opencode/skills/*` show the house style for skills:
  - YAML frontmatter with `name` and `description`
  - a short title
  - explicit “When to Use” / process guidance
  - file path expectations documented in prose

### Relevant local files

- `/workspace/application_instructions.md` — repeats the end goal and requested sequence.
- `/workspace/.env` — contains a single Gemini API key under a **custom variable name** (`GEMINI_IMAGE_CLI_GOOGLE_API_KEY`), not one of the SDK's auto-detected names.

### Packaging implication

Because the repository currently has no Python packaging structure, the cleanest implementation path is to add a standard `src/`-layout Python package at repository root, e.g.:

```text
pyproject.toml
README.md
src/ai_image_cli/
tests/
skills/ai-image-cli/SKILL.md
```

## Reference project functionality summary

Reference: `https://github.com/JonathanJude/openrouter-image-mcp`

### What the reference project actually does

The reference project is a Node/TypeScript MCP server that exposes **three image-analysis tools** over stdio:

1. **`analyze_image`**
   - General-purpose image analysis.
   - Inputs:
     - `type`: `file | url | base64`
     - `data`
     - optional `mimeType`
     - optional `prompt`
     - optional `format`: `text | json`
     - optional `maxTokens`
     - optional `temperature`

2. **`analyze_webpage_screenshot`**
   - Webpage screenshot specialist.
   - Same image source types.
   - Optional webpage-specific knobs:
     - `focusArea`: `layout | content | navigation | forms | interactive | accessibility`
     - `includeAccessibility`
     - `format` (defaults to JSON-oriented behavior)
     - `maxTokens`
   - Builds a structured webpage-analysis prompt and can request JSON.

3. **`analyze_mobile_app_screenshot`**
   - Mobile UI screenshot specialist.
   - Same image source types.
   - Optional mobile-specific knobs:
     - `platform`: `ios | android | auto-detect`
     - `focusArea`: `ui-design | user-experience | navigation | accessibility | performance | onboarding`
     - `includeUXHeuristics`
     - `format`
     - `maxTokens`
   - Builds a structured mobile UX/design prompt and can request JSON.

### Important UX/behavior patterns worth mirroring in the CLI

- **Single-shot analysis**: every invocation takes one request, analyzes the image, prints result, exits.
- **Multiple image source modes**: local file, URL, and inline/base64.
- **Prompt specialization over multiple models**: the reference project's “special tools” are mostly prompt templates plus a few tool-specific arguments, not fundamentally different APIs.
- **Structured output as first-class behavior**: JSON mode matters.
- **Input validation**:
  - allowed MIME types checked
  - image size capped
  - clear error messages returned
- **Operational resilience**:
  - timeouts around image processing and model calls
  - model connection test/validation on startup in MCP mode

### Functionality that should *not* be mirrored literally

- **Model selection** should not be exposed in the new CLI because the user explicitly wants a single fixed Gemini 3 Flash model.
- **MCP server protocol** should not be recreated; the replacement is a normal CLI.
- OpenRouter/OpenAI compatibility layers are unnecessary.

## Gemini SDK / API research

### Recommended package

- **Recommended SDK:** `google-genai`
- Official docs:
  - SDK docs: `https://googleapis.github.io/python-genai/`
  - SDK repo: `https://github.com/googleapis/python-genai`
  - Gemini quickstart: `https://ai.google.dev/gemini-api/docs/quickstart`
  - Image understanding guide: `https://ai.google.dev/gemini-api/docs/image-understanding`
  - API key guide: `https://ai.google.dev/gemini-api/docs/api-key`
- Current PyPI version observed during research: **`2.0.1`**.
- Context7 library resolution returned the official package as `/googleapis/python-genai` with latest indexed version `v1_33_0`; docs and PyPI indicate the package remains the official Python SDK.

### Current SDK capabilities relevant to this CLI

The current Python SDK supports all core functionality needed for the planned CLI:

1. **Authentication**
   - `genai.Client(api_key=...)`
   - or environment variable autodiscovery from `GEMINI_API_KEY` or `GOOGLE_API_KEY`
   - if both are set, `GOOGLE_API_KEY` takes precedence

2. **Multimodal image input**
   - local bytes via `types.Part.from_bytes(data=..., mime_type=...)`
   - uploaded file references via `client.files.upload(...)` then use returned file object in `contents`
   - URI-based input for supported scenarios

3. **Streaming**
   - `client.models.generate_content_stream(...)` works with multimodal inputs

4. **Structured JSON output**
   - use `GenerateContentConfig(response_mime_type='application/json', response_schema=...)`
   - docs explicitly recommend **not** duplicating the JSON schema in the prompt when using schema-driven output

5. **Model listing**
   - `client.models.list()` is available

6. **File upload API**
   - available on the Gemini Developer API
   - recommended for larger files or reuse across requests

### Recommended SDK usage patterns for this project

#### Auth

- Prefer explicit API key wiring in the CLI implementation:
  - read from CLI option or env resolution layer
  - then instantiate `genai.Client(api_key=resolved_key)`
- Reason: the repository currently stores the key under a custom env var name, so relying only on SDK autodiscovery would fail unless the CLI remaps it.

#### Image input strategy

- **Local small files (<20 MB total request)**: use `types.Part.from_bytes(...)`
- **URL inputs**: download with Python HTTP client, infer MIME type, then pass bytes with `types.Part.from_bytes(...)`
- **Base64/stdin inputs**: decode, validate, then pass bytes with `types.Part.from_bytes(...)`
- **Optional large/reusable image mode**: upload with `client.files.upload(file=...)`

For parity with the reference project, inline bytes are sufficient for most requests. File API support is still worth including for larger inputs.

#### Output strategy

- **Text mode**: print `response.text`
- **JSON mode**:
  - use `response_mime_type='application/json'`
  - provide an actual response schema for webpage/mobile specialist commands
  - print normalized JSON to stdout
- Avoid “prompt-only JSON mode” when schema-based output can be used.

#### Prompt ordering

Per the image-understanding guide, when sending a single image with text, place the **text prompt after the image part** in `contents`.

#### File and token considerations

- Gemini docs state inline image data is best when total request size is **under 20 MB**.
- Gemini supports many images per request, but this CLI likely only needs one image per invocation initially.
- Higher media resolution improves small-text reading but increases token cost and latency; this may become an advanced internal setting later, but it is not required for v1.

### API-version / model-name finding that affects the spec

Research and live calls show:

- `gemini-3-flash-preview` is available and callable right now.
- `gemini-3-flash` returned `404 not found` in `v1beta` during live verification.

That means the implementation should currently:

- expose **no user-selectable model option**, but
- internally define a single constant for the actual API model string.

**Recommendation:**

- Product/UX name: “Gemini 3 Flash”
- Current internal API constant: `gemini-3-flash-preview`
- Include one internal compatibility note in code/docs that the constant should be updated to `gemini-3-flash` once Google exposes the stable ID for `generateContent` in the target API version.

## Credential verification result for `.env`

### Result

**Success, with one caveat.**

The credentials stored in the repository `.env` are valid for Gemini API access and successfully called Gemini 3 Flash **when explicitly mapped/read by the CLI**.

### Caveat

The `.env` variable name in this repo is custom and **will not be auto-detected by the SDK** unless the CLI:

- passes it explicitly as `api_key=...`, or
- remaps it to `GOOGLE_API_KEY` or `GEMINI_API_KEY` before creating `genai.Client()`.

### Safe verification evidence

#### REST verification

- Listing models succeeded.
- `gemini-3-flash` returned 404 with message equivalent to “model not found / not supported for generateContent”.
- `gemini-3-flash-preview` returned a successful response to a minimal prompt, with response snippet: `OK`.

#### SDK verification

- `uv run --with google-genai python ...`
- created `genai.Client(api_key=<repo key>)`
- successfully called `client.models.generate_content(model='gemini-3-flash-preview', ...)`
- returned response text: `SDK_OK`

### Conclusion

- The repository credentials are usable.
- The Gemini Python SDK works in this environment.
- The current callable model identifier is `gemini-3-flash-preview`, not bare `gemini-3-flash`.

## CLI specification for `ai-image-cli`

### Product goal

A pip-installable Python CLI for image analysis with Gemini 3 Flash, matching the practical functionality of the reference MCP server while using normal shell-friendly CLI UX.

### Package and entrypoint

- Package name: **`ai-image-cli`**
- Import package: **`ai_image_cli`**
- Console script: **`ai-image-cli`**
- Python requirement: **3.10+** recommended (3.9+ possible per SDK docs, but 3.10+ is a better modern floor)
- Dependency baseline:
  - `google-genai>=2.0.1,<3`
  - `httpx` or `requests` for URL fetches (if not relying purely on stdlib)
  - `pydantic` optional but recommended for output schemas and config models
  - `python-dotenv` optional but recommended to load `.env` ergonomically
  - `typer` or `click` recommended for CLI UX; `typer` is a strong fit

### Fixed model rule

- The CLI must **not** expose `--model` or any model-selection behavior.
- Internal constant:
  - `MODEL_ID = "gemini-3-flash-preview"` for now
- User-facing docs can describe the tool as using **Gemini 3 Flash**.

### Command structure

Recommended subcommands:

```text
ai-image-cli analyze
ai-image-cli analyze-webpage
ai-image-cli analyze-mobile
```

Optional aliases:

```text
ai-image-cli image
ai-image-cli webpage
ai-image-cli mobile
```

#### 1) `ai-image-cli analyze`

General-purpose image analysis.

**Inputs**

- exactly one image source:
  - `--file PATH`
  - `--url URL`
  - `--base64 STRING`
  - `--stdin-base64`
- optional prompt:
  - `--prompt TEXT`
  - `--prompt-file PATH`
- output mode:
  - `--format text|json` (default: `text`)
- generation options:
  - `--max-output-tokens INT`
  - `--temperature FLOAT`
- convenience:
  - `--mime-type TYPE` (required only when it cannot be inferred)
  - `--upload` to force File API upload instead of inline bytes

**Behavior**

- default prompt if omitted:
  - “Analyze this image in detail. Describe what you see, including objects, text, layout, and notable details.”
- if `--format json`, use a generic schema like:
  - summary
  - detected_text
  - key_elements
  - notable_details
  - confidence_notes

#### 2) `ai-image-cli analyze-webpage`

Specialist webpage screenshot analysis.

**Inputs**

- same image-source options as `analyze`
- optional focus:
  - `--focus layout|content|navigation|forms|interactive|accessibility`
- flags:
  - `--include-accessibility / --no-include-accessibility` (default: include)
- output:
  - `--format text|json` (default: `json`)
- generation options:
  - `--max-output-tokens INT`

**Behavior**

- Uses a specialized webpage-analysis system/prompt template.
- In JSON mode, enforce a schema roughly covering:
  - `page_title`
  - `visible_url`
  - `layout`
  - `content`
  - `interactive_elements`
  - `design`
  - `accessibility`
  - `usability`
  - `technical_notes`

#### 3) `ai-image-cli analyze-mobile`

Specialist mobile app screenshot analysis.

**Inputs**

- same image-source options as `analyze`
- optional platform:
  - `--platform ios|android|auto` (default: `auto`)
- optional focus:
  - `--focus ui-design|user-experience|navigation|accessibility|performance|onboarding`
- flags:
  - `--include-ux-heuristics / --no-include-ux-heuristics` (default: include)
- output:
  - `--format text|json` (default: `json`)
- generation options:
  - `--max-output-tokens INT`

**Behavior**

- Uses a specialized mobile UX/design prompt.
- In JSON mode, enforce a schema roughly covering:
  - `app_name`
  - `platform`
  - `screen_type`
  - `ui_design`
  - `navigation`
  - `content`
  - `interactions`
  - `platform_guidelines`
  - `accessibility`
  - `ux_heuristics`
  - `usability`
  - `technical_notes`

### Global options

Recommended global flags:

- `--api-key TEXT`
  - highest precedence
- `--dotenv-path PATH`
  - default `.env`
- `--output FILE`
  - write result to file instead of stdout
- `--verbose`
- `--quiet`
- `--version`

### Environment-variable resolution spec

Recommended precedence for API key resolution:

1. `--api-key`
2. `GEMINI_API_KEY`
3. `GOOGLE_API_KEY`
4. `GEMINI_IMAGE_CLI_GOOGLE_API_KEY` (repo-specific compatibility)
5. `.env` entries for the same keys, in that order

If a key is found via the custom repo variable, the implementation should pass it explicitly to `genai.Client(api_key=resolved_key)`.

### Stdin/stdout behavior

#### Stdout

- Primary analysis result goes to stdout.
- Text mode prints plain text.
- JSON mode prints valid JSON only.
- No logging/noise on stdout in JSON mode.

#### Stderr

- Human-readable status, warnings, debug logs, and errors.

#### Exit codes

- `0` success
- `2` bad CLI usage / invalid arguments
- `3` input acquisition error (missing file, bad URL, bad base64)
- `4` unsupported MIME type / invalid image
- `5` auth/config error (missing or invalid API key)
- `6` Gemini API/model error
- `7` output parsing/serialization error
- `8` timeout/network error

### File handling spec

- Supported local types for v1:
  - PNG
  - JPEG/JPG
  - WebP
  - GIF
  - HEIC/HEIF if SDK/path supports them reliably, otherwise defer
- Detect MIME type from:
  1. explicit `--mime-type`
  2. file extension / `mimetypes`
  3. content sniffing fallback if needed
- Validate size before upload.
- Default inline mode should reject requests above the Gemini inline-request threshold and suggest `--upload`.

### Prompt-template design

- Keep prompt templates in dedicated module(s), e.g. `prompts.py`.
- Separate:
  - generic image prompt
  - webpage prompt builder
  - mobile prompt builder
- For JSON mode, use SDK response schema config rather than giant inline JSON instructions where possible.

### Error handling spec

- Fail fast on ambiguous image-source selection.
- Normalize SDK/API exceptions into concise stderr messages.
- In `--verbose`, include original exception class and HTTP status if available.
- If JSON mode is requested and the response is malformed, return a non-zero exit code and optionally allow `--raw-fallback` in a later phase (not necessary for v1).

### Recommended implementation structure

```text
src/ai_image_cli/
  __init__.py
  __main__.py
  cli.py
  config.py
  errors.py
  models.py
  prompts.py
  image_inputs.py
  gemini_client.py
  formatters.py
```

### Recommended test surface

- unit tests for:
  - env resolution
  - MIME detection
  - source selection validation
  - prompt builders
  - JSON formatting
- integration tests for:
  - local file input
  - URL input
  - base64/stdin input
  - `analyze-webpage --format json`
  - `analyze-mobile --format json`
  - auth failure behavior

## OpenCode skill recommendations for `skills/ai-image-cli`

### Best-practice findings from this repo / environment

From the local skill corpus and runtime instructions, a compatible skill should:

- be a Markdown file named `SKILL.md`
- start with YAML frontmatter:
  - `name`
  - `description`
- be concise and task-oriented
- explain **when to use** the skill
- give exact command patterns the agent can run
- avoid long theory sections when the skill is meant to be operational
- prefer concrete examples and output expectations

### Recommended path

- `skills/ai-image-cli/SKILL.md`

### Recommended skill shape

This skill should be short, focused on execution, and optimized for agents invoking the CLI. It does **not** need a long methodology section.

Recommended sections:

1. frontmatter
2. title
3. one-paragraph overview
4. when to use
5. command patterns
6. output handling notes
7. examples

### Proposed concise skill content

```md
---
name: ai-image-cli
description: Use the local ai-image-cli to analyze images, webpage screenshots, and mobile app screenshots with Gemini 3 Flash
---

# AI Image CLI

## When to Use

- You need to inspect an image from a local file, URL, or base64 input.
- You need structured analysis of a webpage screenshot.
- You need structured UX/UI analysis of a mobile app screenshot.

## Commands

- General image analysis:
  - `ai-image-cli analyze --file <path>`
  - `ai-image-cli analyze --url <url>`
- Webpage screenshot analysis:
  - `ai-image-cli analyze-webpage --file <path> --format json`
- Mobile screenshot analysis:
  - `ai-image-cli analyze-mobile --file <path> --format json`

## Guidance

- Prefer `--format json` when the result will be parsed or summarized further.
- Use `--focus` for webpage or mobile specialist runs when the task is narrow.
- Treat stdout as the result channel; read stderr only for diagnostics.

## Examples

- `ai-image-cli analyze --file screenshot.png --prompt "Summarize the visible error state"`
- `ai-image-cli analyze-webpage --file homepage.png --focus accessibility --format json`
- `ai-image-cli analyze-mobile --file app.png --platform ios --focus navigation --format json`
```

## Actionable guidance for implementation phase

1. Create a root `pyproject.toml` using `src/` layout and a console script `ai-image-cli`.
2. Use `google-genai` as the only model SDK.
3. Implement a fixed internal model constant set to `gemini-3-flash-preview` for now.
4. Add env resolution that supports the repo's custom key name.
5. Implement three subcommands matching the three reference capabilities.
6. Use response schemas for JSON mode instead of prompt-only JSON instructions.
7. Add the concise skill at `skills/ai-image-cli/SKILL.md` after the CLI exists.
8. During live testing, use a real local image and at least one JSON-mode specialist command.

## Open questions / risks

1. **Model ID drift**
   - User intent says “gemini-3-flash”, but current live API access only succeeded with `gemini-3-flash-preview`.
   - This should be treated as an implementation note, not as a user-facing option.

2. **Large image strategy**
   - v1 can rely mostly on inline bytes.
   - Decide whether File API support ships in v1 or immediately after.

3. **Schema strictness**
   - Strong JSON schemas improve reliability but raise implementation effort.
   - Recommended: use moderate schemas for webpage/mobile commands in v1.

## Sources

- Reference repo README: `https://github.com/JonathanJude/openrouter-image-mcp`
- Reference repo package metadata: `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/package.json`
- Reference repo source files:
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/index.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/tools/analyze-image.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/tools/analyze-webpage.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/tools/analyze-mobile-app.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/utils/image-processor.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/utils/openrouter-client.ts`
  - `https://raw.githubusercontent.com/JonathanJude/openrouter-image-mcp/main/src/config/index.ts`
- Google Gen AI SDK docs: `https://googleapis.github.io/python-genai/`
- Google Gen AI SDK repo: `https://github.com/googleapis/python-genai`
- Gemini API quickstart: `https://ai.google.dev/gemini-api/docs/quickstart`
- Gemini API image understanding: `https://ai.google.dev/gemini-api/docs/image-understanding`
- Gemini API key guide: `https://ai.google.dev/gemini-api/docs/api-key`
- PyPI package metadata: `https://pypi.org/pypi/google-genai/json`
