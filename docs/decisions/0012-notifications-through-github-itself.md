# ADR-0012: Notifications through GitHub itself

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- Commit and pull request status checks from every run.
- A `staging` deployment environment, showing the last deployment and its commit.
- Run summaries with the image, scan results and smoke test.
- A PR comment on failure, from the AI diagnosis (ADR-0005).

## Consequences
No secrets or external accounts; a reviewer sees everything on GitHub. Email or
Slack can be added later if needed.
