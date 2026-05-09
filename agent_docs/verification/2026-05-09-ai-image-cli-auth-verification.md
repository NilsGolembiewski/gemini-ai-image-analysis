# Verification: ai-image-cli auth flow

**Date:** 2026-05-09
**Scope:** Verify the `--auth` update against `agent_docs/plans/2026-05-09-ai-image-cli-auth-update.md`, `agent_docs/plans/2026-05-09-ai-image-cli-implementation-report.md`, `agent_docs/verification/2026-05-09-ai-image-cli-verification.md`, and the changed auth-related files under `src/ai_image_cli/`, `tests/`, `README.md`, and `skills/ai-image-cli/SKILL.md`.
**Verdict:** pass

## Summary

The new top-level `--auth` flow is implemented and matches the requested behavior. Independent source inspection, automated tests, help output, and live CLI checks all confirmed that `ai-image-cli` can cache a Gemini key from `--api-key` or stdin, store it in a sensible per-user config path with private permissions, and reuse the cached key for normal analysis runs without leaking the secret.

## Intent Alignment

The user asked for a `--auth` option that caches the Google/Gemini API key, reading from stdin unless `--api-key` is supplied, with later CLI runs able to use the cached value.

Evidence:

- `src/ai_image_cli/cli.py` adds top-level `--auth` and exits early through `save_api_key(_read_auth_api_key(...))`.
- `src/ai_image_cli/cli.py` gives `--api-key` precedence for `--auth`, then falls back to stdin.
- `src/ai_image_cli/config.py` resolves normal runtime auth in the documented order: explicit key, existing env vars, cached key, then dotenv-loaded env vars.
- `README.md` and `skills/ai-image-cli/SKILL.md` both document the cache flow for future runs.

## Plan Alignment

- Top-level `--auth` command surface — **completed**
  - `ai-image-cli --help` shows `--auth`.
- `--api-key` first / stdin fallback for `--auth` — **completed**
  - Confirmed in `cli.py` and live checks.
- Per-user cache path — **completed**
  - `config.py` uses `${XDG_CONFIG_HOME:-~/.config}/ai-image-cli/google-api-key`.
- Secure storage and atomic replace — **completed**
  - `save_api_key()` writes via `NamedTemporaryFile`, `replace()`, dir `0700`, file `0600`.
- Cached-key reuse in normal commands — **completed**
  - Confirmed in `resolve_api_key()` and a live `analyze --url ...` run with only the cached key available.
- Tests/docs updated — **completed**
  - Added tests in `tests/test_cli.py` and `tests/test_config.py`; README and skill updated.

## Completeness

- [x] `--auth` parser support — **present**
- [x] stdin-based key capture — **present and verified live**
- [x] `--auth --api-key ...` flow — **present and verified live**
- [x] cached-key reuse for normal command — **present and verified live**
- [x] sensible per-user cache location — **present**
- [x] private directory/file permissions — **present and verified live**
- [x] automated test coverage for auth cache behavior — **present**
- [x] required verification report deliverable — **this file**

## Scope Discipline

The change stayed within the planned auth-cache scope: CLI entrypoint handling, config resolution/storage, tests, README, and the related skill. No unrelated implementation changes were required for this verification outcome.

## Quality

High-level quality is good:

- Source behavior matches the requested precedence and failure handling.
- Storage location is a conventional per-user config path for Linux/XDG environments.
- File-system permissions are appropriately private.
- The CLI remained functional in regression checks.

Independent verification evidence:

1. Help output

```bash
/tmp/opencode/ai-image-cli-auth-verify-venv/bin/ai-image-cli --help
```

Result: rendered successfully and showed top-level `--auth`.

2. Automated tests

```bash
PYTHONPATH="/workspace/src" /tmp/opencode/ai-image-cli-auth-verify-venv/bin/python -m unittest discover -s tests -v
```

Result: `Ran 26 tests ... OK`.

3. Live `--auth --api-key ...`

- Used repo credentials loaded from `/workspace/.env` without printing the secret.
- Ran the installed CLI with a temporary `XDG_CONFIG_HOME`.
- Result: exit code `0`, no stdout/stderr output, cache file created, stored value matched the supplied key, directory mode `0700`, file mode `0600`.

4. Live stdin-based `--auth`

- Piped the repo key to `ai-image-cli --auth` without printing the secret.
- Result: exit code `0`, no stdout/stderr output, cache file created, stored value matched stdin input, directory mode `0700`, file mode `0600`.

5. Live normal command using only cached key

- Cleared auth env vars, pointed `XDG_CONFIG_HOME` to the temp cache, and used a nonexistent `--dotenv-path` to avoid dotenv fallback.
- Ran `ai-image-cli analyze --url "https://storage.googleapis.com/generativeai-downloads/images/scones.jpg"`.
- Result: exit code `0`, non-empty analysis output, empty stderr, and no secret value appeared in stdout/stderr.

## Findings

### Blocking

None.

### Non-blocking

None.

### Positive

1. The implementation now hardens previously noted edge cases: blank explicit keys fail cleanly and cached-key read errors are normalized into CLI auth errors.
2. The live verification confirmed both auth write paths and cached-key reuse without relying on ambient auth env vars.
3. Secret handling was clean during verification: no key value appeared in observed stdout/stderr.

## Recommendation

Ready to accept. The auth-cache update satisfies the stated objective and acceptance criteria.
