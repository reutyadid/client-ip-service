# ADR-0024: AI diagnosis implementation

- **Status:** Accepted
- **Date:** 2026-11-15

## Principle
Assume prompt injection will eventually succeed, and limit what it can do. The
job never executes anything from the logs or the model; the only thing it
writes is text in one PR comment and the run summary.

## Decision
- **Permissions:** `contents: read`, `actions: read`, `models: read`,
  `pull-requests: write`. The only secret is the optional `AI_API_KEY`.
- **All jobs:** logs of jobs on the ARC runner are streamed to GitHub like any
  other, so deploy and smoke-test failures are diagnosed too. The job itself
  runs on a GitHub-hosted runner, so it works when the local runner is the
  problem. Deploy and smoke-test print cluster state on failure, so it appears
  in their logs.
- **Code:** `ci_diagnosis/`, tested in `tests/ci_diagnosis/`. Dependencies
  (`openai`, `httpx2`, `pydantic`) are in the `ci` group, not in the app image.
- **Flow:** failed (and timed-out) jobs and steps from the GitHub API; each log
  is redacted first, then cut to the lines around errors plus the end, within
  8,000 characters in total. Logs go into the prompt inside tags, HTML-escaped
  so they cannot close the tag, with an instruction that they are data, not
  instructions. The answer is JSON in a fixed shape, validated with Pydantic.
- **Output sanitizing:** HTML escaped; images removed (loading one could leak
  data through its URL); links reduced to text; bare URLs defanged; `@mentions`
  neutralized; evidence lines in a code block whose fence is longer than any
  backtick run inside.
- **Publishing:** always in the run summary; on a PR, one comment found by a
  hidden marker and the bot author, updated on every failure. On `main` without
  a PR, the run summary only.
- **Model failure:** timeouts, rate limits or invalid answers produce a plain
  failure notice. The job always succeeds and reports problems as warnings, so
  the original failure stays the only failure.
- **Provider:** the official `openai` library against any OpenAI-compatible
  API. Defaults in the workflow: Groq and `openai/gpt-oss-120b` (ADR-0027;
  originally GitHub Models, see ADR-0006).

## Alternatives considered
- GitHub's `actions/ai-inference`: it only sends a prompt. Log collection,
  redaction, validation and sanitizing would be custom code anyway, and it is
  tied to GitHub Models.
- Giving the model tool access (MCP): rejected; a model that reads untrusted
  logs should only return text.
- `httpx2` with our own HTTP code instead of `openai`: fewer dependencies, more
  code to maintain.
- Opening an Issue on a failure on `main`: more visible, but needs another
  write permission.
