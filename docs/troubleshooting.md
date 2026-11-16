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

## ARC runner pod stuck in `CreateContainerConfigError`

- **Symptom:** the first CI job on the `kind-staging` runner never started. The runner pod pulled its image, then stayed in `CreateContainerConfigError` with: `container has runAsNonRoot and image has non-numeric user (runner), cannot verify user is non-root`.
- **Cause:** `runAsNonRoot: true` in `cluster/arc/runner-scale-set-values.yaml`. The `actions-runner` image sets `USER runner` by name, and the kubelet does not read `/etc/passwd` inside the image, so it cannot prove the user is not root and refuses to start the container. It only showed up on the first real job, because with `minRunners: 0` no runner pod existed before.
- **Fix:** set the numeric IDs, `runAsUser: 1001` and `runAsGroup: 1001` (checked with `docker run --rm --entrypoint id <image>`), re-run `cluster/setup-arc.sh`, and delete the stuck pod so ARC recreates it from the new template. `runAsNonRoot` stays on.

## AI diagnosis fails with `'str' object has no attribute 'choices'`

- **Symptom:** the AI diagnosis posted only its fallback notice, "the model could not be reached", with the warning `AttributeError: 'str' object has no attribute 'choices'`.
- **Cause:** GitHub Models, the provider at the time, was retired on 2026-07-30. Its endpoint answers every request, with or without a token, with `200 text/plain` and the body `OK`. The `openai` library does not raise on a 200 that is not JSON; it returns the body as a plain string.
- **Fix:** switched to Groq by changing the repository variables and adding `AI_API_KEY` (ADR-0011). The client now checks that the answer is a chat completion and otherwise fails with a clear error that points to `AI_API_BASE_URL`.

## Groq answers `404` for `llama-3.3-70b-versatile`

- **Symptom:** right after switching to Groq: `NotFoundError: Error code: 404 - The model 'llama-3.3-70b-versatile' does not exist or you do not have access to it`.
- **Cause:** Groq retired the model on 2026-08-16. Its model list page still showed it as a production model; only the deprecations page had the shutdown date.
- **Fix:** set the `AI_MODEL` repository variable to `openai/gpt-oss-120b`, Groq's recommended replacement. No commit needed. When choosing a model, check the provider's deprecations page, not only its model list.
