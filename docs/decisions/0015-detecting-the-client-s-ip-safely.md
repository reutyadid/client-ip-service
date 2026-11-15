# ADR-0015: Detecting the client's IP safely

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
Behind a proxy the client's address arrives in `X-Forwarded-For`, but any client
can send that header with a fake address. Real systems use that address for
rate limits, allow-lists, audit logs and geo-blocking.

## Decision
Three layers:
1. **Gateway (Traefik):** no `trustedIPs` and no `insecure` mode, since no
   proxy sits in front of it; a forged header from outside is not trusted.
2. **App:** uvicorn's built-in `ProxyHeadersMiddleware` reads the header from
   the right and skips only trusted proxy addresses (`FORWARDED_ALLOW_IPS`,
   set to the pod CIDR in staging, never `*`). The app returns
   `request.client.host` and never parses the header itself. See ADR-0019 for
   how it is wired and validated.
3. **NetworkPolicy:** because the whole pod CIDR is trusted, a compromised pod
   could forge the header. A NetworkPolicy lets only the gateway reach the app.

## Verified
- Unit tests: a header from an untrusted client is ignored; from the trusted
  proxy it is used; `1.2.3.4, 203.0.113.7` resolves to `203.0.113.7`.
- On kind: a forged header sent through the gateway was ignored. A pod in
  `staging` that sent a forged header directly to the app was blocked by the
  NetworkPolicy; without the policy it got `{"ip":"1.2.3.4"}`.

## Alternatives considered
Parsing the header in our own code (more code, more room for bugs); trusting
every address with `*` (safe only if nothing but the gateway can reach the pod).
