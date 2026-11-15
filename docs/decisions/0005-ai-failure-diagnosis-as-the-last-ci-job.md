# ADR-0005: AI failure diagnosis as the last CI job

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The assignment asks for a CI step that runs only when the pipeline fails,
collects the logs, sends them to a language model and publishes a diagnosis.

## Decision
A final job, `ai-diagnosis`, with `if: failure()` and `needs` on every other
job, including the ones on the self-hosted runner. It runs a small, tested
Python package (`ci_diagnosis/`) that:
- collects only the failed jobs' logs, cuts them to the relevant part and
  redacts secrets;
- asks the model for a fixed structure: failed stage, root cause, suggested
  fix, confidence, evidence;
- posts one PR comment with a link to the run, updated on later failures;
- falls back to a plain failure notice if the model is unavailable.

Logs are untrusted input: nothing from them, or from the model, is executed.

## Alternatives considered
A separate workflow triggered by `workflow_run`. Rejected: a job in the same
pipeline matches the assignment's wording, shows in the same run graph, and
`workflow_run` is one of the triggers GitHub flags as risky with fork code.

Implementation details: ADR-0024.
