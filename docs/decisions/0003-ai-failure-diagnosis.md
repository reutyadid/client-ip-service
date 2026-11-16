# ADR-0003: AI failure diagnosis

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The assignment asks for a CI step that runs only when the pipeline fails,
collects the logs of the failed job, sends them to a language model and
publishes a short diagnosis: the likely root cause, the failing step and a
suggested fix.

The logs are untrusted input: a pull request controls what its jobs print, so
it can try prompt injection. Assume an injection will eventually succeed, and
limit what it can do.

## Decision
A final job, `ai-diagnosis`, with `if: failure()` and `needs` on every other
job, including the ones on the self-hosted runner. It runs a small, tested
Python package, `ci_diagnosis/`. The job never executes anything from the logs
or from the model; the only thing it writes is text in the run summary and in
one PR comment.

- **Permissions:** `contents: read`, `actions: read`, `pull-requests: write`.
  The only secret is `AI_API_KEY`. Without it, as in pull requests from forks,
  the job posts a plain failure notice instead of calling a model.
- **All jobs:** logs of jobs on the ARC runner are streamed to GitHub like any
  other, so deploy and smoke-test failures are diagnosed too. The job itself
  runs on a GitHub-hosted runner, so it works when the local runner is the
  problem. Deploy and smoke-test print cluster state on failure, so it appears
  in their logs.
- **Code:** `ci_diagnosis/`, tested in `tests/unit/ci_diagnosis/`.
  Dependencies (`openai`, `httpx2`, `pydantic`) are in the `ci` group, not in
  the app image.
- **Flow:** failed (and timed-out) jobs and steps from the GitHub API; each log
  is redacted first, then cut to the lines around errors plus the end, within
  8,000 characters in total. Logs go into the prompt inside tags, HTML-escaped
  so they cannot close the tag, with an instruction that they are data, not
  instructions. The answer is JSON in a fixed shape (failed stage, root cause,
  suggested fix, confidence, evidence), validated with Pydantic.
- **Output sanitizing:** HTML escaped; images removed (loading one could leak
  data through its URL); links reduced to text; bare URLs defanged; `@mentions`
  neutralized; `*` and `_` escaped so they cannot turn into emphasis; evidence
  lines in a code block whose fence is longer than any backtick run inside.
- **Publishing:** always in the run summary; on a PR, one comment found by a
  hidden marker and the bot author, updated on every failure, with a link to
  the run. On `main` without a PR, the run summary only.
- **Model failure:** timeouts, rate limits, invalid or non-JSON answers produce
  a plain failure notice. The job always succeeds and reports problems as
  warnings, so the original failure stays the only failure.
- **Provider:** the official `openai` library against any OpenAI-compatible
  API, chosen through repository variables (ADR-0011).

## Consequences
- The model sees logs, not code: it finds what failed, but may miss why it
  matters.
- A failure in the diagnosis never hides or replaces the pipeline's failure.

## Alternatives considered
- A separate workflow triggered by `workflow_run`: a job in the same pipeline
  matches the assignment's wording, shows in the same run graph, and
  `workflow_run` is one of the triggers GitHub flags as risky with fork code.
- GitHub's `actions/ai-inference`: it only sends a prompt. Log collection,
  redaction, validation and sanitizing would be custom code anyway, and it is
  tied to GitHub Models.
- Giving the model tool access (MCP): a model that reads untrusted logs should
  only return text.
- `httpx2` with our own HTTP code instead of `openai`: fewer dependencies, more
  code to maintain.
- Opening an Issue on a failure on `main`: more visible, but needs another
  write permission.
