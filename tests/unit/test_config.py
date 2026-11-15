import pytest

from app.config import (
    load_docs_enabled,
    load_trusted_proxies,
    parse_bool,
    parse_trusted_proxies,
)


def test_valid_ips_and_cidrs_are_accepted():
    assert parse_trusted_proxies("127.0.0.1, 10.244.0.0/16") == [
        "127.0.0.1",
        "10.244.0.0/16",
    ]


@pytest.mark.parametrize(
    "raw",
    [
        "",  # empty
        "*",  # trusts everyone
        "not-an-ip",  # typo
        "10.0.0.0/33",  # impossible prefix
        "10.244.0.5/16",  # host bits set, probably meant 10.244.0.0/16
    ],
)
def test_invalid_values_fail_fast(raw):
    with pytest.raises(ValueError):
        parse_trusted_proxies(raw)


@pytest.mark.parametrize(("raw", "expected"), [("true", True), (" FALSE ", False)])
def test_bool_accepts_true_and_false(raw, expected):
    assert parse_bool("DOCS_ENABLED", raw) is expected


@pytest.mark.parametrize("raw", ["yes", "1", ""])
def test_bool_rejects_anything_else(raw):
    with pytest.raises(ValueError):
        parse_bool("DOCS_ENABLED", raw)


@pytest.mark.parametrize("loader", [load_trusted_proxies, load_docs_enabled])
def test_missing_env_var_fails_fast(monkeypatch, loader):
    monkeypatch.delenv("FORWARDED_ALLOW_IPS", raising=False)
    monkeypatch.delenv("DOCS_ENABLED", raising=False)
    with pytest.raises(RuntimeError, match="Missing required environment variable"):
        loader()


def test_values_are_read_from_env(monkeypatch):
    monkeypatch.setenv("FORWARDED_ALLOW_IPS", "10.244.0.0/16")
    monkeypatch.setenv("DOCS_ENABLED", "true")
    assert load_trusted_proxies() == ["10.244.0.0/16"]
    assert load_docs_enabled() is True
