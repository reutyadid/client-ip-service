"""The app's endpoints answer through the gateway as expected."""

import ipaddress

import pytest

# To check another fixed JSON endpoint, add one line here.
STATUS_ENDPOINTS = [
    pytest.param("/health", {"status": "ok"}, id="health"),
    pytest.param("/ready", {"status": "ready"}, id="ready"),
]

DOCS_ENDPOINTS = ["/docs", "/redoc", "/openapi.json"]


@pytest.mark.parametrize(("path", "expected_body"), STATUS_ENDPOINTS)
def test_status_endpoint_returns_expected_json(gateway, path, expected_body):
    # Arrange: path and expected body come from STATUS_ENDPOINTS

    # Act
    response = gateway.get(path)

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_body


def test_root_returns_the_callers_ip(gateway):
    # Arrange: nothing beyond the gateway fixture

    # Act
    response = gateway.get("/")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"ip"}
    ipaddress.ip_address(body["ip"])  # raises if it is not a valid IP


@pytest.mark.parametrize("path", DOCS_ENDPOINTS)
def test_api_docs_match_the_environment_setting(gateway, settings, path):
    # Arrange
    expected_status = 200 if settings.docs_enabled else 404

    # Act
    response = gateway.get(path)

    # Assert
    assert response.status_code == expected_status
