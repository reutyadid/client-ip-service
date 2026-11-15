#!/usr/bin/env bash
# Installs Actions Runner Controller (ARC) into the kind cluster created by
# setup.sh, plus a runner scale set for this repo (decision 10).
# Safe to re-run.
#
# Prerequisite: the GitHub App secret in namespace arc-runners (see
# arc/runner-scale-set-values.yaml for the command).
set -euo pipefail

KUBE_CONTEXT="kind-client-ip"
ARC_CHART_VERSION="0.15.1"
CHARTS="oci://ghcr.io/actions/actions-runner-controller-charts"

cd "$(dirname "$0")"
kc() { kubectl --context "${KUBE_CONTEXT}" "$@"; }

echo "==> namespaces"
for ns in arc-systems arc-runners; do
  kc create namespace "${ns}" --dry-run=client -o yaml | kc apply -f -
done

if ! kc -n arc-runners get secret github-app >/dev/null 2>&1; then
  echo "Missing secret arc-runners/github-app. Create it first:" >&2
  grep -A3 'kubectl -n arc-runners create secret' arc/runner-scale-set-values.yaml | sed 's/^# *//' >&2
  exit 1
fi

echo "==> runner RBAC and NetworkPolicy"
kc apply -f arc/runner-rbac.yaml -f arc/runner-networkpolicy.yaml

echo "==> ARC controller ${ARC_CHART_VERSION}"
helm upgrade --install arc "${CHARTS}/gha-runner-scale-set-controller" \
  --kube-context "${KUBE_CONTEXT}" \
  --namespace arc-systems \
  --version "${ARC_CHART_VERSION}" \
  --wait --timeout 3m

echo "==> runner scale set 'kind-staging' ${ARC_CHART_VERSION}"
helm upgrade --install kind-staging "${CHARTS}/gha-runner-scale-set" \
  --kube-context "${KUBE_CONTEXT}" \
  --namespace arc-runners \
  --version "${ARC_CHART_VERSION}" \
  --values arc/runner-scale-set-values.yaml \
  --wait --timeout 3m

echo
echo "ARC ready. The listener pod runs in arc-systems; runner pods appear in"
echo "arc-runners only while a job with 'runs-on: kind-staging' is running."
