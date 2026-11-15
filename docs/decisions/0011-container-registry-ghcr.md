# ADR-0011: Container registry: GHCR

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
GitHub Container Registry. Images are tagged with the full commit SHA, as the
assignment requires, and deployed by digest.

## Consequences
The push job authenticates with the built-in token and `packages: write`; no
extra secret. The package is private (ADR-0022).
