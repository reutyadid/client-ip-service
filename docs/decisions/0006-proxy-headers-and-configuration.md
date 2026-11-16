# ADR-0006: Proxy headers wired in code; configuration from the environment

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
uvicorn silently accepts invalid `FORWARDED_ALLOW_IPS` entries such as
`not-an-ip` or `10.0.0.0/33`, which would quietly disable client-IP detection.

## Decision
- `app/config.py` validates each entry with `ipaddress` (rejecting `*`, empty
  values and host bits set); `app/main.py` adds uvicorn's
  `ProxyHeadersMiddleware` with the validated list. uvicorn runs with
  `--no-proxy-headers` to avoid handling the header twice. Tests exercise the
  exact production wiring.
- `/docs`, `/redoc` and `/openapi.json` are controlled by `DOCS_ENABLED`: off
  by default, on in staging so the API can be explored.
- No configuration values in code: every variable is required, and a missing
  or invalid one stops the app with a clear message. Locally they come from
  `.env` (git-ignored, template `.env.example`), in Kubernetes from the chart's
  values. uvicorn runs the factory `app.main:app_from_env`, so importing the
  module (e.g. in tests) needs no environment.

## Consequences
`/docs` loads JavaScript and CSS from a public CDN in the browser.
