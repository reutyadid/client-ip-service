"""Client-IP detection, including X-Forwarded-For spoofing attempts (ADR-0005)."""

from fastapi.testclient import TestClient

from app.main import create_app

TRUSTED_PROXY_RANGE = "10.244.0.0/16"  # kind's pod CIDR, where Traefik runs
TRAEFIK_POD = ("10.244.0.5", 40000)
OUTSIDE_CLIENT = ("198.51.100.9", 40000)

app = create_app([TRUSTED_PROXY_RANGE], docs_enabled=False)


def get_ip(client_addr, headers=None):
    client = TestClient(app, client=client_addr)
    response = client.get("/", headers=headers or {})
    assert response.status_code == 200
    return response.json()["ip"]


def test_no_header_returns_connection_ip():
    assert get_ip(OUTSIDE_CLIENT) == "198.51.100.9"


def test_trusted_proxy_header_is_used():
    headers = {"X-Forwarded-For": "203.0.113.7"}
    assert get_ip(TRAEFIK_POD, headers) == "203.0.113.7"


def test_header_from_untrusted_client_is_ignored():
    # A client that talks to the app directly cannot choose its own IP.
    headers = {"X-Forwarded-For": "1.2.3.4"}
    assert get_ip(OUTSIDE_CLIENT, headers) == "198.51.100.9"


def test_spoofed_entry_before_proxy_entry_is_ignored():
    # The attacker sent "1.2.3.4"; Traefik appended the real address.
    # Only the rightmost entry, added by the trusted proxy, counts.
    headers = {"X-Forwarded-For": "1.2.3.4, 203.0.113.7"}
    assert get_ip(TRAEFIK_POD, headers) == "203.0.113.7"


def test_ipv6_client_address_is_returned():
    headers = {"X-Forwarded-For": "2001:db8::1"}
    assert get_ip(TRAEFIK_POD, headers) == "2001:db8::1"


def test_chain_of_trusted_proxies_is_skipped():
    # The client sent a forged "1.2.3.4". A first trusted proxy (10.244.0.9)
    # appended the client's real address, and Traefik appended that proxy.
    # Trusted hops are skipped from the right; the first untrusted one wins.
    headers = {"X-Forwarded-For": "1.2.3.4, 203.0.113.7, 10.244.0.9"}
    assert get_ip(TRAEFIK_POD, headers) == "203.0.113.7"


def test_x_real_ip_header_is_never_used():
    # Only X-Forwarded-For is read, from the right; X-Real-IP is a single
    # value any client can set, so it is ignored even from the trusted proxy.
    headers = {"X-Real-IP": "1.2.3.4"}
    assert get_ip(TRAEFIK_POD, headers) == "10.244.0.5"
