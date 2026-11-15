# Architecture Decision Records

Each file records one decision: the context, what was decided, why, and the
alternatives that were considered. Code comments point here as `ADR-NNNN`.

| ADR | Decision |
|---|---|
| [0001](0001-python-with-fastapi.md) | Python with FastAPI |
| [0002](0002-hybrid-ci.md) | Hybrid CI: GitHub-hosted runners plus one local runner |
| [0003](0003-hardening-the-local-runner.md) | Hardening the local runner |
| [0004](0004-repository-visibility.md) | Repository visibility: private during development, public at submission |
| [0005](0005-ai-failure-diagnosis-as-the-last-ci-job.md) | AI failure diagnosis as the last CI job |
| [0006](0006-language-model-provider.md) | Language model provider: GitHub Models, without lock-in |
| [0007](0007-repository-name-client-ip-service.md) | Repository name: client-ip-service |
| [0008](0008-development-environment.md) | Development environment |
| [0009](0009-local-cluster-kind-on-docker-desktop-with-wsl2.md) | Local cluster: kind on Docker Desktop with WSL2 |
| [0010](0010-local-runner-actions-runner-controller-arc.md) | Local runner: Actions Runner Controller (ARC) |
| [0011](0011-container-registry-ghcr.md) | Container registry: GHCR |
| [0012](0012-notifications-through-github-itself.md) | Notifications through GitHub itself |
| [0013](0013-image-scanning-with-trivy.md) | Image scanning with Trivy |
| [0014](0014-linting-ruff-and-hadolint.md) | Linting: ruff for Python, hadolint for the Dockerfile |
| [0015](0015-detecting-the-client-s-ip-safely.md) | Detecting the client's IP safely |
| [0016](0016-dependencies-uv-with-a-lockfile.md) | Dependencies: uv with a lockfile |
| [0017](0017-claude-md-for-ai-assisted-development.md) | CLAUDE.md for AI-assisted development |
| [0018](0018-app-behavior-and-health-endpoints.md) | App behavior: JSON response and simple health endpoints |
| [0019](0019-proxy-headers-and-configuration.md) | Proxy headers wired in code; configuration from the environment |
| [0020](0020-base-image-docker-hardened-images.md) | Base image: Docker Hardened Images |
| [0021](0021-traffic-routing-gateway-api-with-traefik.md) | Traffic routing: Gateway API with Traefik |
| [0022](0022-private-image-pull-token.md) | Pulling the private image: a dedicated read-only token |
| [0023](0023-cluster-exposure-nodeport-localhost-only.md) | Cluster exposure: NodePort, localhost only |
| [0024](0024-ai-diagnosis-implementation.md) | AI diagnosis implementation |
| [0025](0025-deploying-to-staging-with-helm.md) | Deploying to staging with Helm |
| [0026](0026-smoke-tests.md) | Smoke tests |
