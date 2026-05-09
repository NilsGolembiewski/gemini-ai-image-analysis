# Verification: ai-image-cli auth-cache

**Date:** 2026-05-09
**Scope:** Verify the auth-cache update against `agent_docs/plans/2026-05-09-ai-image-cli-auth-update.md`, `src/ai_image_cli/cli.py`, `src/ai_image_cli/config.py`, `tests/test_cli.py`, `tests/test_config.py`, `README.md`, and `skills/ai-image-cli/SKILL.md`.
**Verdict:** pass-with-concerns

## Summary

The new top-level `--auth` flow and normal runtime key-resolution order are implemented as planned. The main behavior looks correct, but there are a couple of edge cases around empty explicit keys and malformed/unreadable cache files, plus a few documentation/testing gaps.

## Intent Alignment

The user wanted a top-level `--auth` flow that caches a Gemini/Google API key at a per-user path, taking `--api-key` first or stdin otherwise, and normal CLI runs that resolve keys with precedence `--api-key` → existing env vars → cached key → dotenv-loaded vars.

Evidence:

- `cli.py` adds top-level `--auth` and exits early after `save_api_key(...)`.
- `_read_auth_api_key(...)` uses `--api-key` first, then stdin.
- `config.py` stores the key at `${XDG_CONFIG_HOME:-~/.config}/ai-image-cli/google-api-key`.
- `resolve_api_key(...)` resolves in the documented order: explicit key, env, cache, dotenv-loaded env.

## Plan Alignment

- Top-level `--auth` command surface — **completed**
- `--api-key` first / stdin fallback for `--auth` — **completed**
- Per-user cache path — **completed**
- Secure directory/file permissions and atomic replace — **completed**
- Normal CLI precedence `--api-key` → env → cache → dotenv — **completed**
- Tests/docs updated — **completed, with coverage/detail gaps noted below**

## Completeness

- [x] `cli.py` auth entrypoint present
- [x] `config.py` cache helpers present
- [x] README updated with precedence and cache examples
- [x] Skill updated to mention cached auth flow
- [x] Unit tests added for auth caching and cache resolution
- [x] Verification report deliverable — **this file**

## Scope Discipline

Scope appears disciplined. The touched files match the plan and the change stays focused on auth caching, precedence, docs, and tests.

## Quality

High-level quality is good: the flow is simple, uses a private cache location, trims stored keys, and writes through a temp file before replacement. The main concerns are edge-case handling rather than the primary workflow.

## Findings

### Blocking

None.

### Non-blocking

1. Empty explicit keys are treated as “not provided” rather than invalid.
   - In `cli.py`, `_read_auth_api_key()` checks `if args.api_key`, so `--auth --api-key ""` falls through to stdin instead of failing immediately.
   - In `config.py`, `resolve_api_key()` checks `if explicit_api_key`, so a normal run with an empty explicit key would silently fall back to env/cache/dotenv instead of treating the explicit value as invalid.

2. A malformed or unreadable cache path can raise raw filesystem errors.
   - `load_cached_api_key()` calls `read_text()` directly with no handling for `PermissionError`, `IsADirectoryError`, or other `OSError` cases.
   - `main()` only catches `FileNotFoundError`, so a bad cache file can escape as an unhandled exception instead of a clean CLI auth/input error.

### Positive

1. The precedence order in `resolve_api_key()` matches the plan and README.
2. `save_api_key()` enforces `0700` on the cache directory and `0600` on the file, matching the design.
3. `cli.py` correctly rejects `--auth` when combined with a subcommand.

## Recommendation

Ready to accept if the team is comfortable with the noted edge cases. If desired, follow up with a small hardening patch for empty explicit keys and unreadable-cache handling, and add tests/docs for those cases.
