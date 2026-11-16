# Deploy through CI in your own fork

CI deploys to the cluster where its runner is registered, and uses the
repository's own secrets. To have CI build, scan, push and deploy to **your**
cluster, use your own copy of the repository.

Your GitHub user name and the fork's name must be lowercase: the image name is
built from the repository (`ghcr.io/${{ github.repository }}`), and GHCR
accepts only lowercase names. Nothing else in the workflow needs changing; the
fork publishes to `ghcr.io/<you>/client-ip-service` and deploys that image.

## 1. Fork the repository

Fork it on GitHub, then enable workflows in the fork's **Actions** tab (GitHub
disables them on forks).

## 2. Create the cluster

Requires Docker, kind, kubectl and Helm.

```bash
cluster/setup.sh
```

## 3. Register a runner for your fork

The `deploy` and `smoke-test` jobs run on a self-hosted runner inside the
cluster ([ADR-0004](decisions/0004-local-runner-actions-runner-controller-arc.md)).
It registers with GitHub through a GitHub App:

1. Create a GitHub App under **Settings → Developer settings → GitHub Apps**,
   with the repository permissions **Administration: Read and write** and
   **Metadata: Read-only**.
2. Generate a private key, install the app on your fork only, and note the
   App ID and the installation ID (the number at the end of the installation
   page's URL).
3. Store them in the cluster:

   ```bash
   kubectl create namespace arc-runners
   kubectl -n arc-runners create secret generic github-app \
     --from-literal=github_app_id=<APP_ID> \
     --from-literal=github_app_installation_id=<INSTALLATION_ID> \
     --from-file=github_app_private_key=<path/to/key.pem>
   ```

4. Point the runner at your fork: in `cluster/arc/runner-scale-set-values.yaml`,
   set `githubConfigUrl: https://github.com/<you>/client-ip-service`.
5. Install the runner:

   ```bash
   cluster/setup-arc.sh
   ```

## 4. Add the secrets and variables

Under **Settings → Secrets and variables → Actions**, add the GitHub secrets
and variables listed in the [README](../README.md#secrets).

## 5. Push to `main`

The pipeline pushes the image to `ghcr.io/<you>/client-ip-service` and deploys
it to your `staging` namespace. Follow it in the **Actions** tab, then:

```bash
kubectl -n staging get pods
curl http://localhost/
```
