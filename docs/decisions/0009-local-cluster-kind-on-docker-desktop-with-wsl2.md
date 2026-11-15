# ADR-0009: Local cluster: kind on Docker Desktop with WSL2

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
kind (Kubernetes in Docker) on the existing Docker Desktop installation.

## Consequences
- Port mappings can only be set when a kind cluster is created, so the cluster
  config is versioned in `cluster/kind-config.yaml`.
- Resource use was measured before choosing the add-ons. WSL2 is limited to
  6GB and 4 CPUs. At idle, available memory went from 4,096 MiB (baseline) to
  3,555 MiB with kind and metrics-server, 3,409 MiB with Traefik, and
  3,234 MiB with the ARC controller: about 860 MiB for the whole stack, and
  about 0.3 of 4 cores. Most of the Traefik and ARC cost came from the API
  server holding their CRDs, not from their own pods (19Mi and 14Mi).

## Alternatives considered
- Docker Engine directly in the WSL Ubuntu distribution: the fallback if
  Docker Desktop causes problems.
- A full VM: too heavy for the machine and adds nothing to the assignment.
