# ADR-0001: Hybrid CI: GitHub-hosted runners plus one local runner

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
Deploying to the local kind cluster requires a runner that can reach it. A
self-hosted runner on a public repository runs code from pull requests on the
owner's machine.

## Decision
- GitHub-hosted runners: lint, test, build, scan, push, helm lint, AI diagnosis.
- Local self-hosted runner (ADR-0004): deploy to staging and the smoke test only.

Only jobs that need the cluster run locally. `helm lint` reads chart files only,
so it runs on a GitHub-hosted runner, after push, as in the assignment's order.

## Consequences
- The local machine runs as little untrusted code as possible.
- Heavy work (builds, scans) does not compete with the cluster for memory.
- If the local runner is offline, deploy jobs wait in the queue instead of failing.
