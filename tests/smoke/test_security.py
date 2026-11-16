"""Security properties of the deployed service (ADR-0005, ADR-0006)."""

import httpx2
import pytest

SPOOFED_IP = "1.2.3.4"


def test_spoofed_forwarded_for_header_is_ignored(gateway):
    # Arrange: a client that claims a fake address
    headers = {"X-Forwarded-For": SPOOFED_IP}

    # Act
    response = gateway.get("/", headers=headers)

    # Assert: the gateway and the app ignore it (ADR-0005, layers 1 and 2)
    assert response.status_code == 200
    assert response.json()["ip"] != SPOOFED_IP


def test_server_software_is_not_advertised(gateway):
    # Arrange: nothing beyond the gateway fixture

    # Act
    response = gateway.get("/health")

    # Assert: uvicorn runs with --no-server-header
    assert "uvicorn" not in response.headers.get("server", "").lower()


def test_app_is_not_reachable_without_the_gateway(settings):
    # Arrange: a request straight to the app's Service, with a spoofed header,
    # as a compromised pod inside the cluster would send it
    if settings.app_url is None:
        pytest.skip("SMOKE_APP_URL is not set: only reachable inside the cluster")
    headers = {"X-Forwarded-For": SPOOFED_IP}

    # Act + Assert: the NetworkPolicy drops the connection, so it times out
    # (ADR-0005, layer 3). A refused connection or a DNS error is a different
    # failure, and is not accepted as proof.
    with pytest.raises(httpx2.ConnectTimeout):
        httpx2.get(settings.app_url, headers=headers, timeout=3)
