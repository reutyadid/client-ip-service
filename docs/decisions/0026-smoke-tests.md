# ADR-0026: Smoke tests

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- pytest suite in `tests/smoke/`, documented in its `conftest.py`, separate from the unit tests in `tests/unit/`.
  `testpaths = ["tests/unit"]`, so plain `pytest` never runs smoke tests; the
  `smoke-test` job runs `pytest tests/smoke` explicitly.
- Every test follows Arrange, Act, Assert. Shared setup lives in fixtures
  (`settings`, `gateway`, `app_pods`); checks that differ only by input are
  table-driven (`pytest.mark.parametrize`), so a new case is usually one line.
- Settings come from required environment variables with no defaults. A
  missing one fails the run instead of silently skipping it. The one exception
  is `SMOKE_APP_URL`: it is only reachable inside the cluster, so without it
  the NetworkPolicy test is skipped explicitly. CI always sets it.
- The job runs on the ARC runner, inside the cluster, through Traefik's
  Service. The `gateway` fixture waits up to 60 seconds for `/health`, once.
- Dependencies are the `smoke` group (pytest, httpx2), locked in `uv.lock`.
- A JUnit report is uploaded as an artifact; a pass/fail list goes in the run
  summary; cluster state is printed on failure.

## What is checked
- `/health`, `/ready`, `/` (a valid IP), and `/docs`, `/redoc`,
  `/openapi.json` matching the environment's docs setting.
- A spoofed `X-Forwarded-For` through the gateway is ignored (ADR-0015).
- A direct request to the app's Service, bypassing the gateway, times out:
  the NetworkPolicy works (ADR-0015, layer 3). A refused connection or DNS
  error is not accepted as proof.
- No `server: uvicorn` header.
- Every app pod runs exactly the deployed digest, is Ready, and has not
  restarted.

## Why directories rather than markers
Smoke tests run at a different stage, against a different target, with
different dependencies. A directory makes the split visible and can't be
forgotten when adding a test; a marker typo would silently select nothing.

## Verified
Locally against kind: 10 passed, 1 skipped (the NetworkPolicy test, from
outside the cluster). With a wrong `SMOKE_DIGEST`, the digest test failed.
