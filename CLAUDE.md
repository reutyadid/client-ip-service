# CLAUDE.md

Project facts for Claude Code. The README covers what the project does and how
to run it; this file covers what you need to change it safely.

## Commands
```bash
helm lint charts/client-ip-service --strict --set image.tag=test   # needs an image tag or digest
cluster/setup.sh                         # kind + Traefik + namespace staging (re-runnable)
```
Plain `uv run pytest` runs only the unit tests. Smoke tests run against a
deployment and need every variable, with no defaults:
```bash
SMOKE_GATEWAY_URL=http://localhost SMOKE_NAMESPACE=staging \
SMOKE_RELEASE=client-ip-service SMOKE_DIGEST=sha256:<deployed digest> \
SMOKE_DOCS_ENABLED=true uv run --group smoke pytest tests/smoke
```

## Conventions
- **Commits:** imperative mood, capitalized, no `feat:`/`fix:` prefix, subject
  under ~50 characters, no trailing period, one logical change per commit.
- **Configuration:** no defaults in code. Every environment variable is
  required and validated at startup; a missing one stops the app.
- **GitHub Actions:** every action pinned to a full commit SHA with the version
  in a comment (`@<sha> # v7.0.1`); the repository enforces this. Workflow-level
  `permissions: {}`, and each job requests only what it needs.
- **Dependencies:** uv ignores versions published in the last 14 days
  (`exclude-newer`); the same rule applies when choosing an action version.
- **Comments** point to the decision behind them as `ADR-NNNN`. A significant
  new decision gets an ADR: Context, Decision, Consequences, and alternatives if
  any. Numbers are never reused.
- **Problems** hit along the way get an entry in `docs/troubleshooting.md`:
  symptom, cause, fix.

## Pitfalls
- Never set `FORWARDED_ALLOW_IPS='*'`: any client could forge its IP (ADR-0005).
- `kind load` changes an image's digest, so a loaded image must be deployed by
  tag with `pullPolicy=Never`, never by digest.
- The runtime image has no shell; debug with `kubectl debug`.
- Images that set `USER` by name need a numeric `runAsUser` when
  `runAsNonRoot: true` (see the ARC runner values).
- Do not add `-rA` to the unit test run in CI: the AI diagnosis tests print
  `::warning` lines that GitHub would turn into annotations.
- On WSL2, never use `sessionAffinity: ClientIP` on a Service.
- Building the image needs `docker login dhi.io` first.

## Rules for Claude
- Never run `git commit` or `git push`; `.claude/settings.json` blocks them.
  The author reviews and commits every change.
- Never put secrets in the chart, in git, or on a command line.
