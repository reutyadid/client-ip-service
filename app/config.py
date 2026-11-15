"""Runtime configuration from environment variables.

No values are defined in code: every variable is required and validated at
startup, so a missing or bad value fails fast. Locally they come from .env
(see .env.example); in Kubernetes from the Helm chart's values.yaml.
"""

import ipaddress
import os


def require_env(name: str) -> str:
    """Return a required environment variable, or fail with a clear message."""
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(
            f"Missing required environment variable {name} (see .env.example)"
        )
    return value


def parse_trusted_proxies(raw: str) -> list[str]:
    """Parse a comma-separated list of proxy IPs/CIDRs and validate each entry.

    uvicorn's ProxyHeadersMiddleware silently accepts invalid entries, so a typo
    would quietly disable client-IP detection. We reject it instead.
    """
    entries = [entry.strip() for entry in raw.split(",") if entry.strip()]
    if not entries:
        raise ValueError("FORWARDED_ALLOW_IPS is empty")

    for entry in entries:
        if entry == "*":
            raise ValueError(
                "FORWARDED_ALLOW_IPS='*' trusts every client to set the header; "
                "list the real proxy IPs or CIDR ranges instead"
            )
        try:
            # strict=True also rejects host bits set, e.g. 10.244.0.5/16
            ipaddress.ip_network(entry, strict=True)
        except ValueError as exc:
            raise ValueError(
                f"Invalid entry in FORWARDED_ALLOW_IPS: {entry!r}"
            ) from exc

    return entries


def parse_bool(name: str, raw: str) -> bool:
    """Accept only 'true' or 'false', so a typo like 'yes' fails fast."""
    value = raw.strip().lower()
    if value not in ("true", "false"):
        raise ValueError(f"{name} must be 'true' or 'false', got {raw!r}")
    return value == "true"


def load_docs_enabled() -> bool:
    return parse_bool("DOCS_ENABLED", require_env("DOCS_ENABLED"))


def load_trusted_proxies() -> list[str]:
    return parse_trusted_proxies(require_env("FORWARDED_ALLOW_IPS"))
