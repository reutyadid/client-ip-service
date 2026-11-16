# ADR-0011: Language model provider: Groq, after GitHub Models was retired

- **Status:** Accepted
- **Date:** 2026-11-16

## Context
The AI diagnosis (ADR-0003) first used GitHub Models: no cost, and the
workflow's built-in token as the key. GitHub Models was retired on 2026-07-30.
Its endpoint now answers every request with `200 text/plain` and the body
`OK`, so the AI diagnosis failed with `'str' object has no attribute
'choices'` and posted only the fallback notice.

## Decision
- The code talks to any OpenAI-compatible chat API through one small
  interface, `LLMClient`; the base URL and the model are repository variables
  (`AI_API_BASE_URL`, `AI_MODEL`). A provider without that API needs one new
  class. The prompt is a separate file in git.
- Provider: Groq, through its OpenAI-compatible API
  (`https://api.groq.com/openai/v1`). Switching needed no code change, only
  the repository variables and the `AI_API_KEY` secret. The workflow defaults
  and a clearer error for non-JSON answers were added afterwards.
- Model: `openai/gpt-oss-120b`.
- Both are defaults in the workflow, so the repository shows what runs.
  Repository variables still override them.
- `AI_API_KEY` is a repository secret. Without it, as in pull requests from
  forks, the job posts the plain failure notice instead of calling a model.
- The `models: read` permission and the code that sent the built-in token to
  GitHub Models were removed.
- A non-JSON answer from the API now fails with a clear error that points to
  `AI_API_BASE_URL`, instead of an `AttributeError`.

## Why Groq
| Criterion | Why it matters | Groq |
|---|---|---|
| Free, no credit card | A demo project; a leaked key costs no money | Yes |
| OpenAI-compatible API | No code change behind `LLMClient` | Yes |
| JSON mode | The diagnosis is JSON validated against a schema | All models |
| Limits fit one request per failed run (~4K tokens) | | 8K tokens/min, 1K requests/day |

## Why `openai/gpt-oss-120b`
- A production model, not a preview, and not on the deprecation list.
- Groq's recommended replacement for the models it retired.
- The largest of Groq's free text models.
- Supports strict JSON schema output, for a later improvement.
- Checked on a real failure: it named the failing test and the cause, with
  `high` confidence (demo PR, branch `demo/ai-diagnosis`).

## Consequences
- Keeping the provider in configuration held twice: GitHub Models was replaced, and then
  `llama-3.3-70b-versatile` (retired by Groq on 2026-08-16) was replaced, each
  by changing configuration only.
- Free models are retired quickly. Check the provider's deprecation page when
  choosing a model, not only its model list.
- The model only sees logs, not code: it finds what failed, but may miss why
  it matters (in the demo, it missed the IP-spoofing risk).

## Alternatives considered
- Anthropic: paid; the official SDK needs a new `LLMClient` class.
- Gemini free tier: may use the submitted data to improve products, and the
  data here is CI logs.
- No defaults in the workflow: nothing in the code goes stale, but what runs
  would be visible only in the repository settings.
- Not done: comparing models on a set of known failures (an eval). Here one
  real failure is enough, because switching models is one variable.
