# Review: ai-image-cli auth cache hardening

**Date:** 2026-05-09
**Scope:** `/workspace/src/ai_image_cli/cli.py`, `/workspace/src/ai_image_cli/config.py`, `/workspace/tests/test_cli.py`, `/workspace/tests/test_config.py`, `/workspace/README.md`, `/workspace/agent_docs/plans/2026-05-09-ai-image-cli-auth-update.md`
**Verdict:** comment-only

## Summary

Reviewed the finalized auth-cache flow and the hardening additions around empty keys, cache-file handling, and `--auth` mode restrictions. The implementation matches the documented precedence and behavior; no correctness issues were found in the reviewed scope.

## Findings

### Critical

- None.

### Important

- None.

### Nitpicks

- **`src/ai_image_cli/config.py:89-103`** — Environment and dotenv-loaded keys are accepted as-is, unlike explicit and cached keys which are stripped and validated for emptiness. This is not a regression against the stated requirements, but it leaves whitespace-only env values as a possible sharp edge.

### Positive

- **`src/ai_image_cli/cli.py:163-169`** — `--auth` is enforced as a top-level mode with a clear usage error when combined with a subcommand, which prevents ambiguous parsing and behavior.
- **`src/ai_image_cli/config.py:47-60`** — Empty cache files and cache read failures are translated into CLI auth errors instead of surfacing raw filesystem exceptions.
- **`tests/test_cli.py:48-103` and `tests/test_config.py:60-76`** — Tests cover the main auth caching paths plus the new empty explicit key and empty cache file hardening behavior.

## Missing

- No direct unit test was added for the unreadable-cache-file branch in `load_cached_api_key`; coverage is still reasonable, but that specific path remains unexercised.

## Questions

- None.
