# ADR-0010: Local runner: Actions Runner Controller (ARC)

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
Originally an ephemeral Docker container per job was planned, with ARC as a
later option. The resource measurement showed room for ARC.

## Decision
ARC, GitHub's official runner operator, installed with its two Helm charts
(0.15.1) by `cluster/setup-arc.sh`:
- controller in `arc-systems`; runner scale set `kind-staging` in
  `arc-runners`, scaling from 0 to 2;
- a new runner pod per job, deleted afterwards;
- no Docker-in-Docker and no privileged pods: local jobs only run `helm` and
  `kubectl`;
- non-root, 1Gi memory limit, image pinned by digest, all inbound traffic to
  runner pods denied by a NetworkPolicy.

ARC authenticates as a GitHub App installed on this repository only, with the
runner-administration permission only; it gets one-hour tokens from the App's
private key. The key exists only as the Secret `arc-runners/github-app`,
created by hand, never in git.

## Verified
The listener registered with GitHub. As the runner's ServiceAccount: can manage
Deployments, Secrets and HTTPRoutes and read logs in `staging`; cannot do
anything in `default`, cannot read Secrets in `arc-runners` or `traefik` (so it
cannot read the App key), cannot delete pods, and cannot create namespaces or
cluster-wide permissions.

## Alternatives considered
An ephemeral Docker container with a JIT runner config and a loop script.
Simpler, but its GitHub credential (a `gh` login) acts as the user across all
their repositories, and the cluster token and the loop are ours to maintain.
