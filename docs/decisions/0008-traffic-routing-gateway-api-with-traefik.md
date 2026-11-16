# ADR-0008: Traffic routing: Gateway API with Traefik

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
Traefik is the software that receives traffic and routes it (the controller).
Ingress and Gateway API are two formats for writing routing rules; Traefik
reads both. One implementation and one format are needed.

## Decision
Gateway API only. The cluster setup installs the official Gateway API CRDs and
Traefik, which creates the GatewayClass and a Gateway named `web`. The app chart
only attaches an `HTTPRoute` to it (enabled in staging).

## Why
- For new projects in 2026, Gateway API is the recommended format; Ingress is
  still supported but no longer gains features.
- It separates roles: the entry point (Gateway) belongs to the cluster, the
  route (HTTPRoute) to the app.
- Traefik: ingress-nginx was retired in March 2026; Traefik runs in the
  cluster, is installed with Helm, supports both formats, and does not trust
  forwarded headers by default. Measured cost: about 146MiB.

## Consequences
The assignment says "optional Ingress"; the README explains the choice.
