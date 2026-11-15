"""client-ip-service: returns the caller's IP address."""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import load_docs_enabled, load_trusted_proxies


class IPResponse(BaseModel):
    ip: str


class StatusResponse(BaseModel):
    status: str


def create_app(trusted_proxies: list[str], docs_enabled: bool) -> FastAPI:
    # /docs, /redoc and /openapi.json only when DOCS_ENABLED=true:
    # on in staging for exploring the API, off elsewhere to expose less.
    app = FastAPI(
        title="client-ip-service",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    # uvicorn's own X-Forwarded-For handling: reads the header right to left and
    # stops at the first address that is not a trusted proxy. Wired here (not via
    # the uvicorn CLI flag) so the list is validated and the tests exercise the
    # exact production setup. Run uvicorn with --no-proxy-headers.
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=trusted_proxies)

    @app.get("/")
    def client_ip(request: Request) -> IPResponse:
        if request.client is None:
            # Only happens on non-TCP transports (e.g. a Unix socket).
            raise HTTPException(status_code=500, detail="Client address unavailable")
        return IPResponse(ip=request.client.host)

    @app.get("/health")
    def health() -> StatusResponse:
        """Liveness: the process answers. Never checks dependencies."""
        return StatusResponse(status="ok")

    @app.get("/ready")
    def ready() -> StatusResponse:
        """Readiness: no dependencies yet. Add their checks here, not in /health."""
        return StatusResponse(status="ready")

    return app


def app_from_env() -> FastAPI:
    """App factory for uvicorn: reads config from the environment at startup.

    A factory (uvicorn --factory) instead of a module-level `app`, so importing
    this module, e.g. in tests, does not require the environment variables.
    """
    return create_app(load_trusted_proxies(), docs_enabled=load_docs_enabled())
