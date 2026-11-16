# Architecture Decision Records

Each file records one decision: the context, what was decided, why, and,
where there were any, the alternatives that were considered. Code comments
point here as `ADR-NNNN`.

| ADR | Decision |
|---|---|
| [0001](0001-hybrid-ci.md) | Hybrid CI: GitHub-hosted runners plus one local runner |
| [0002](0002-hardening-the-local-runner.md) | Hardening the local runner |
| [0003](0003-ai-failure-diagnosis.md) | AI failure diagnosis |
| [0004](0004-local-runner-actions-runner-controller-arc.md) | Local runner: Actions Runner Controller (ARC) |
| [0005](0005-detecting-the-client-s-ip-safely.md) | Detecting the client's IP safely |
| [0006](0006-proxy-headers-and-configuration.md) | Proxy headers wired in code; configuration from the environment |
| [0007](0007-base-image-docker-hardened-images.md) | Base image: Docker Hardened Images |
| [0008](0008-traffic-routing-gateway-api-with-traefik.md) | Traffic routing: Gateway API with Traefik |
| [0009](0009-private-image-pull-token.md) | Pulling the private image: a dedicated read-only token |
| [0010](0010-cluster-exposure-nodeport-localhost-only.md) | Cluster exposure: NodePort, localhost only |
| [0011](0011-language-model-provider-groq.md) | Language model provider: Groq, after GitHub Models was retired |
