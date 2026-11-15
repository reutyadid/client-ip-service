# ADR-0004: Repository visibility: private during development, public at submission

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
The repository is private while it is built and becomes public for submission.

## Consequences
- No forks, and so no fork pull requests, during development.
- Before it goes public, every protection from ADR-0003 is enabled.
- Some features run only on a public repository, e.g. uploading SARIF to the
  Security tab (ADR-0013).
