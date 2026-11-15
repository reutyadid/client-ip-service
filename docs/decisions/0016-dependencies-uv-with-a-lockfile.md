# ADR-0016: Dependencies: uv with a lockfile

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- Dependencies in `pyproject.toml`; `uv.lock` in git pins the full dependency
  tree with checksums.
- Groups: app dependencies; `ci` (the AI diagnosis, not in the image); `dev`
  (tests and lint, includes `ci`).
- A 14-day cooldown (`exclude-newer = "14 days"`): versions uploaded in the last
  two weeks are ignored, keeping new releases out until most malicious ones
  would have been caught. The same rule is used when choosing action versions.
- Docker: `uv sync --locked --no-dev` in the build stage; only the virtualenv is
  copied to the runtime image. CI: `astral-sh/setup-uv`, pinned by SHA.

## Consequences
uv must be installed locally. uv and ruff come from the same company.

## Alternatives considered
pip with pip-tools (two tools, two files); plain pip with `requirements.txt`
(no transitive locking, no checksums).
