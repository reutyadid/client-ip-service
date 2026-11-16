# ADR-0003: Hardening the local runner

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The local runner runs inside the cluster it deploys to, and every CI job,
including jobs from pull requests, runs code on it. GitHub warns that on a
public repository a self-hosted runner can be compromised by untrusted code
and stay compromised between jobs.

## Decision
- Ephemeral runners: a fresh pod per job, deleted when the job ends.
- Minimal cluster permissions: a Role that manages the app's resources in the
  `staging` namespace only (`cluster/arc/runner-rbac.yaml`).
- Repository setting that requires approval for workflows from outside
  contributors, enabled before the repository is made public.
- The runner is stopped when it isn't needed.

## Consequences
A compromised job cannot persist on the runner, read secrets outside `staging`
(including the GitHub App key), or act at cluster scope. Verified with
`kubectl auth can-i` (see ADR-0010).
