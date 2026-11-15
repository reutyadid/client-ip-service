# ADR-0018: App behavior: JSON response and simple health endpoints

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- `/` returns `{"ip": "..."}`: easy to extend and to check in the smoke test.
- `/health` (liveness) always returns 200 while the process answers. It never
  checks dependencies: a failing dependency would otherwise restart every pod.
- `/ready` (readiness) returns 200. The app has no dependencies yet; their
  checks belong here, not in `/health`.
- Graceful shutdown: a 5-second `preStop` sleep in the chart, run by the
  kubelet (the image has no shell), and an exec-form `CMD` so SIGTERM reaches
  uvicorn.
- Invalid configuration stops the app at startup.
- A startup probe is not needed; it can be enabled in `values.yaml`.

## Why no readiness flag
uvicorn accepts requests only after startup completes, and on SIGTERM it stops
accepting connections at once, so a "not ready yet" flag would never be seen.
