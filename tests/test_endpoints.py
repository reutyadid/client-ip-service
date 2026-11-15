from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app(["127.0.0.1"], docs_enabled=False))


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_root_returns_json_with_ip():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert set(response.json()) == {"ip"}


DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


def test_api_docs_are_disabled_by_default():
    for path in DOCS_PATHS:
        assert client.get(path).status_code == 404


def test_api_docs_can_be_enabled():
    docs_client = TestClient(create_app(["127.0.0.1"], docs_enabled=True))
    for path in DOCS_PATHS:
        assert docs_client.get(path).status_code == 200
