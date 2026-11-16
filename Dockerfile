# syntax=docker/dockerfile:1

# Docker Hardened Images (ADR-0007). Pulling from dhi.io needs a Docker Hub
# login: locally `docker login dhi.io`, in CI the DOCKERHUB_TOKEN secret.
# Pinned by version and digest: the tag documents what it is, the digest
# guarantees the exact bytes.
ARG PYTHON_BUILD_IMAGE=dhi.io/python:3.14.10-debian13-dev@sha256:60dbebd00c5332a2d5984a96f33b76d6e42167095a9db8c49cd0038ac388de77
ARG PYTHON_RUNTIME_IMAGE=dhi.io/python:3.14.10-debian13@sha256:d20d953b545c83acd9e1b6b6b6d27cf14de38e6a39689334f71454c33cf41893
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0

FROM ${UV_IMAGE} AS uv

# ---- Build stage: the -dev variant has a shell; install deps into /app/.venv ----
FROM ${PYTHON_BUILD_IMAGE} AS builder

COPY --from=uv /uv /bin/uv

# Compile bytecode at build time; copy files instead of hard-linking from the
# cache mount; never download a Python, use the one in the image.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies only, in their own layer: a code change does not reinstall them.
# --locked fails if uv.lock is out of date; --no-dev leaves pytest/ruff out.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-dev --no-install-project

# ---- Runtime stage: no shell, no package manager, runs as non-root ----
FROM ${PYTHON_RUNTIME_IMAGE} AS runtime

WORKDIR /app

# Same path as in the builder, and Python is at /usr/bin/python3.14 in both
# images, so the venv works unchanged. Files stay owned by root: the app user
# can read its code but not modify it.
COPY --from=builder /app/.venv /app/.venv
COPY app ./app

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The image's built-in "nonroot" user. Set explicitly so it is visible here and
# matches runAsUser in the Helm chart.
USER 65532

EXPOSE 8000

# Exec form (the only option without a shell): uvicorn is PID 1 and receives
# SIGTERM for a graceful shutdown.
# --factory: config is read from the environment at startup (FORWARDED_ALLOW_IPS,
#   DOCS_ENABLED); a missing or invalid value stops the container.
# --no-proxy-headers: X-Forwarded-For is handled inside the app (ADR-0006).
# --no-server-header: do not advertise "server: uvicorn".
CMD ["uvicorn", "--factory", "app.main:app_from_env", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--no-proxy-headers", "--no-server-header"]
