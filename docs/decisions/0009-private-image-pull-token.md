# ADR-0009: Pulling the private image: a dedicated read-only token

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The image in GHCR is private, so the cluster needs credentials to pull it.

## Decision
A dedicated classic GitHub token with only `read:packages` and a 90-day expiry,
stored as the GitHub secret `GHCR_PULL_TOKEN`. On every deploy, the deploy job
creates or updates the docker-registry Secret `ghcr-pull` in `staging`, and
`values-staging.yaml` references it in `imagePullSecrets`. The node pulls by
digest, as it would in production.

## Why
Without a node identity towards the registry, a dedicated read-only token per
cluster, kept as a secret, is the common practice. Staging then behaves like
production.

## Consequences
GHCR does not support fine-grained tokens, so a classic token can read every
package of the account (currently only this one). It must be renewed before it
expires. In a real cloud cluster the node's own identity (e.g. IAM) would be
used and no secret would be needed.

## Alternatives considered
- `kind load` plus deploy by digest: tested on a throwaway cluster and failed.
  `kind load` repacks the image, so the node knows it under a different digest
  (`sha256:d636ee76...` versus `sha256:a7dbc319...` in the registry) and the pod
  stays in `ErrImageNeverPull`; by tag it ran.
- `kind load` plus deploy by tag: no secret, but kind-specific, and staging
  would differ from production.
- A public image: simplest, but exposes the code before submission.
- A pull secret from the job's `GITHUB_TOKEN`: it expires when the job ends, so
  later pulls would fail.
