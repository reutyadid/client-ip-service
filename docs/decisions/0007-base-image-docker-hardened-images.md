# ADR-0007: Base image: Docker Hardened Images

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The assignment asks for a minimal runtime image. Every package in the image
is attack surface and a possible finding for the Trivy gate in CI.

## Decision
`dhi.io/python:3.14.10-debian13` for runtime and the `-dev` variant for the
build stage, both pinned by digest.

## Why
The runtime image has no shell and no package manager, runs as `nonroot`
(UID 65532) and has very few known vulnerabilities. Our final image is 89MB,
versus 137MB on `python:3.14-slim`. The catalog is free (Apache 2.0).

## Consequences
- Pulling from `dhi.io` needs a Docker Hub login: locally `docker login dhi.io`;
  in CI the secret `DOCKERHUB_TOKEN` and variable `DOCKERHUB_USERNAME`, given
  only to the `build` job. Separate read-only, 90-day tokens for local use and
  CI. Fork pull requests get no secrets, so their build fails.
- No shell to debug in; use `kubectl debug` with an ephemeral container.
- Token-less login (OIDC) is only available to paid Docker organizations.

## Hardening in the Dockerfile
Multi-stage build; uv is not in the final image; files are owned by root so the
app cannot modify its own code; an allow-list `.dockerignore`; exec-form `CMD`.

## Alternatives considered
- `python:3.14-slim`: tried first and verified; no registry login, has a shell,
  but more packages and vulnerabilities.
- Google distroless: its Python comes from Debian 13, i.e. 3.13, not 3.14.
- Chainguard: the free tier offers only the `latest` tag, so it can't be pinned.
