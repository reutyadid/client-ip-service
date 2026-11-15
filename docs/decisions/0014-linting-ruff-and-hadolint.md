# ADR-0014: Linting: ruff for Python, hadolint for the Dockerfile

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- `ruff check` and `ruff format --check` for Python.
- `hadolint` (pinned action) for the Dockerfile, failing on warnings.
- The two lint jobs run in parallel; tests wait for both.

## Why ruff rather than flake8
flake8 only reports problems; it needs black for formatting and isort for
imports, so three tools to pin and configure. ruff does all three with
flake8-compatible rule codes, includes rules that need plugins in flake8
(bugbear, bandit-style security checks), fixes automatically, and is configured
in `pyproject.toml`.

## Consequences
ruff is younger and backed by a company. The assignment names flake8 only as an
example.
