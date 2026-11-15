# ADR-0023: Cluster exposure: NodePort, localhost only

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- `cluster/setup.sh` creates everything in one re-runnable command.
- Traefik is a NodePort Service on fixed port 30080; kind maps `localhost:80` to
  it. `externalTrafficPolicy: Local` keeps the client's source address.
- The mapping listens on `127.0.0.1` only, so other machines on the network
  cannot reach staging.
- Gateway API CRDs v1.6.3, the version Traefik v3.7.18 is built against (its
  `go.mod`), downloaded with a checksum check.
- Traefik chart 42.4.0 with `--skip-crds`: it bundles 25 Traefik and Traefik
  Hub CRDs we don't use, which were most of its memory cost. Only the Gateway
  API provider is enabled, and the Gateway accepts routes only from `staging`.

## Why NodePort
The Kubernetes configuration best practices say to avoid `hostPort` unless
absolutely necessary, because it ties pods to specific nodes, and call a
NodePort Service "the safer, Kubernetes-native way".

## Alternatives considered
- hostPort: common in older kind guides, discouraged by the Kubernetes docs.
- cloud-provider-kind: recommended by the kind docs today and closest to
  production. Its README says WSL2 is "basically supported", it needs `sudo`,
  runs as a separate background process, exposes a random host port, and is
  alpha.

## Verified
Through the gateway: `/` returned the Docker network address (expected on
kind), and `/health`, `/ready` and `/docs` worked. A forged `X-Forwarded-For`
from outside was ignored. App pods have no service-account token volume.
