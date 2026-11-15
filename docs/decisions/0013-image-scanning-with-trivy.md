# ADR-0013: Image scanning with Trivy

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- `aquasecurity/trivy-action` v0.36.0, pinned to a full commit SHA, with the
  Trivy binary pinned to v0.70.0. v0.36.0 was released after the March 2026
  compromise of the action's tags (GHSA-69fq-xp46-6x23) and pins
  `setup-trivy` to the known-safe v0.2.6.
- The scan runs after the build and before the push, on the exact image tarball
  that is later pushed: a vulnerable image never reaches the registry.
- The gate fails on CRITICAL and HIGH findings that have a fix
  (`ignore-unfixed`). Justified exceptions go in `.trivyignore`, with a reason.
- A CycloneDX SBOM and a SARIF report are saved as run artifacts; a table goes
  in the run summary. SARIF is uploaded to the Security tab only on a public
  repository (code scanning on a private personal repository needs GitHub Code
  Security).

## Alternatives considered
- Grype with Syft.
- Installing the Trivy binary with a checksum check: more to maintain, no cache.
