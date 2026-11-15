"""Shared setup for the smoke tests, which run against a deployed environment.

Every setting comes from an environment variable, with no defaults: a missing
one fails the run instead of silently testing the wrong thing.

    SMOKE_GATEWAY_URL   URL of the gateway (Traefik) in front of the app
    SMOKE_NAMESPACE     namespace the app is deployed to
    SMOKE_RELEASE       Helm release name
    SMOKE_DIGEST        image digest that was deployed (sha256:...)
    SMOKE_DOCS_ENABLED  "true" or "false", as configured for the environment
    SMOKE_APP_URL       optional: the app's Service URL, bypassing the gateway.
                        Only reachable from inside the cluster; without it the
                        NetworkPolicy test is skipped.

Run against a deployment, for example the local kind staging:

    SMOKE_GATEWAY_URL=http://localhost SMOKE_NAMESPACE=staging \
    SMOKE_RELEASE=client-ip-service SMOKE_DIGEST=sha256:... \
    SMOKE_DOCS_ENABLED=true uv run --group smoke pytest tests/smoke

Writing a test:
- Arrange, Act, Assert, each step marked with a comment.
- Shared Arrange work goes in a fixture here: settings, gateway (an HTTP
  client that waits until the app is ready) and app_pods.
- Same check with different inputs: add a row to a parametrize table, e.g.
  STATUS_ENDPOINTS in test_endpoints.py, not a new test.
- One behavior per test, named as a sentence: test_<what>_<expected>.
- One file per topic: endpoints, security, deployment.
"""

import json
import os
import subprocess
import time
from collections.abc import Iterator
from dataclasses import dataclass

import httpx2
import pytest

READY_TIMEOUT_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 5


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable {name}")
    return value


@dataclass(frozen=True)
class SmokeSettings:
    gateway_url: str
    namespace: str
    release: str
    digest: str
    docs_enabled: bool
    app_url: str | None


@pytest.fixture(scope="session")
def settings() -> SmokeSettings:
    docs = _require("SMOKE_DOCS_ENABLED").lower()
    if docs not in ("true", "false"):
        raise RuntimeError("SMOKE_DOCS_ENABLED must be 'true' or 'false'")
    return SmokeSettings(
        gateway_url=_require("SMOKE_GATEWAY_URL"),
        namespace=_require("SMOKE_NAMESPACE"),
        release=_require("SMOKE_RELEASE"),
        digest=_require("SMOKE_DIGEST"),
        docs_enabled=docs == "true",
        app_url=os.environ.get("SMOKE_APP_URL", "").strip() or None,
    )


@pytest.fixture(scope="session")
def gateway(settings: SmokeSettings) -> Iterator[httpx2.Client]:
    """HTTP client for the gateway, returned only once the app answers.

    A fresh deployment or route can take a few seconds to become reachable,
    so the waiting happens here, once, instead of in every test.
    """
    client = httpx2.Client(
        base_url=settings.gateway_url, timeout=REQUEST_TIMEOUT_SECONDS
    )
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            if client.get("/health").status_code == 200:
                yield client
                client.close()
                return
            last_error = "HTTP status was not 200"
        except httpx2.TransportError as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(2)
    client.close()
    pytest.fail(
        f"{settings.gateway_url}/health not ready after "
        f"{READY_TIMEOUT_SECONDS}s ({last_error})"
    )


@pytest.fixture(scope="session")
def app_pods(settings: SmokeSettings) -> list[dict]:
    """The app's pods, as Kubernetes returns them (kubectl get pods -o json)."""
    result = subprocess.run(  # noqa: S603 - fixed command, no shell
        [  # noqa: S607 - kubectl is installed on the runner
            "kubectl",
            "get",
            "pods",
            "--namespace",
            settings.namespace,
            "--selector",
            f"app.kubernetes.io/instance={settings.release}",
            "--output",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    pods = json.loads(result.stdout)["items"]
    assert pods, f"no pods found for release {settings.release}"
    return pods
