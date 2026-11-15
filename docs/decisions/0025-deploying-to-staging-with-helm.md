# ADR-0025: Deploying to staging with Helm

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
The `deploy` job runs on the ARC runner (`runs-on: kind-staging`) and
authenticates to the cluster with the runner's ServiceAccount and its
`deployer` Role, limited to `staging` (ADR-0010). No kubeconfig.

```bash
helm upgrade --install client-ip-service charts/client-ip-service \
  --namespace staging --values charts/client-ip-service/values-staging.yaml \
  --set image.digest="$DIGEST" \
  --rollback-on-failure --wait --timeout 3m --history-max 10
```

- `upgrade --install` is idempotent: installs the first time, upgrades after.
- `--rollback-on-failure` (Helm 4's name for `--atomic`) waits for the rollout
  and returns to the last working release on failure, so staging is never
  left half-deployed.
- `--history-max 10` bounds the release history, which Helm stores as Secrets.
- The image is deployed by the digest that the `push` job produced, the same
  bytes that were scanned.
- Before Helm runs, the job creates or updates the `ghcr-pull` Secret
  (ADR-0022). The Docker config is built from an environment variable and
  passed on stdin, so the token never appears in a command line.
- `environment: staging` records each deployment on the repository page;
  `concurrency` queues deploys and never cancels one halfway.
- On failure, the job prints pods, events, app logs and the release history
  into its log, where the AI diagnosis reads them (ADR-0024).

## Verified
Before CI, the same Helm command was run locally while impersonating the
runner's ServiceAccount (`--kube-as-user`): the release deployed in 9 seconds,
so the `deployer` Role is sufficient. The pull-secret command was tested the
same way, including a second run that updates the Secret.
