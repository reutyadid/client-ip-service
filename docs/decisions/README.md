# Architecture Decision Records

Each file records one decision: the context, what was decided, why, and the
alternatives that were considered. Code comments point here as `ADR-NNNN`.

| ADR | Decision |
|---|---|
| [0002](0002-hybrid-ci.md) | Hybrid CI: GitHub-hosted runners plus one local runner |
| [0003](0003-hardening-the-local-runner.md) | Hardening the local runner |
| [0005](0005-ai-failure-diagnosis.md) | AI failure diagnosis |
| [0010](0010-local-runner-actions-runner-controller-arc.md) | Local runner: Actions Runner Controller (ARC) |
| [0015](0015-detecting-the-client-s-ip-safely.md) | Detecting the client's IP safely |
| [0019](0019-proxy-headers-and-configuration.md) | Proxy headers wired in code; configuration from the environment |
| [0020](0020-base-image-docker-hardened-images.md) | Base image: Docker Hardened Images |
| [0021](0021-traffic-routing-gateway-api-with-traefik.md) | Traffic routing: Gateway API with Traefik |
| [0022](0022-private-image-pull-token.md) | Pulling the private image: a dedicated read-only token |
| [0023](0023-cluster-exposure-nodeport-localhost-only.md) | Cluster exposure: NodePort, localhost only |
| [0027](0027-language-model-provider-groq.md) | Language model provider: Groq, after GitHub Models was retired |
