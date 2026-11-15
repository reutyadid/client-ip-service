# Troubleshooting

Problems hit while building this project: symptom, cause, and fix.

---

## WSL2: a Service with `sessionAffinity: ClientIP` is unreachable

- **Symptom:** a Service with `sessionAffinity: ClientIP` is unreachable, and so is every Service created after it.
- **Cause:** the WSL2 kernel lacks a module that kube-proxy needs for this setting.
- **Fix:** don't use it. It is unrelated to detecting the client's IP anyway.

## Traefik's LoadBalancer Service stays `<pending>`

- **Symptom:** `EXTERNAL-IP <pending>` on Traefik's Service.
- **Cause:** kind has no cloud provider to assign an external IP.
- **Fix:** expose Traefik as a NodePort Service on a fixed port (30080) and map `localhost:80` to it in `cluster/kind-config.yaml`.

## Slow pull of the GitHub Actions runner image

- **Symptom:** `docker pull ghcr.io/actions/actions-runner` took more than 3 minutes.
- **Cause:** the image is 1.57 GB.
- **Fix:** wait. The image is cached locally, so only the first pull is slow.

## `docker login` fails inside Claude Code

- **Symptom:** `error: cannot perform an interactive login from a non-TTY device`.
- **Cause:** commands run with `!` in Claude Code don't get an interactive terminal, so a password can't be typed.
- **Fix:** run `docker login` in a regular WSL terminal. The login is stored in Docker's config, shared by all terminals. Never pass a token on the command line.

## `kind load` doesn't work with digest-pinned deployments

- **Symptom:** a pod that references `repo@sha256:...` with `imagePullPolicy: Never` stays in `ErrImageNeverPull`, although the image was loaded into the node. The same image referenced by tag runs.
- **Cause:** `kind load` repacks the image, so the node knows it under a different digest than the registry. In our test: `sha256:a7dbc319...` in the registry, `sha256:d636ee76...` on the node.
- **Fix:** the cluster pulls the image from GHCR by digest, with an `imagePullSecret`.

## `helm upgrade --reuse-values` fails after `--set x=null`

- **Symptom:** `at '/imagePullSecrets': got null, want array`.
- **Cause:** `--set imagePullSecrets=null` was stored in the release's values. `--reuse-values` reused it, and `values.schema.json` rejected it.
- **Fix:** pass an empty list with `--set-json 'imagePullSecrets=[]'`. The schema did exactly its job.

## `kubectl create namespace` fails with `AlreadyExists`

- **Symptom:** `Error from server (AlreadyExists): namespaces "arc-runners" already exists` while creating the GitHub App secret.
- **Cause:** the namespace already existed. `kubectl create` is not idempotent.
- **Fix:** harmless; the next command still created the secret. In scripts, use `kubectl create ... --dry-run=client -o yaml | kubectl apply -f -`, as `cluster/setup*.sh` do.
