# ADR-0006: Language model provider: GitHub Models, without lock-in

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- Default: GitHub Models, authenticated with the workflow's built-in token and
  the `models: read` permission. No extra key, no cost.
- The API base URL and the model name are repository variables
  (`AI_API_BASE_URL`, `AI_MODEL`), so the model or provider changes without a
  commit. A key for another provider is the secret `AI_API_KEY`.
- The code talks to any OpenAI-compatible chat API (GitHub Models, Ollama,
  OpenAI and others) through one small interface; a provider without that API
  needs one new class.
- The prompt is a separate file in git.

## Consequences
The built-in token is only ever sent to `models.github.ai`; any other provider
requires `AI_API_KEY` (ADR-0024).
