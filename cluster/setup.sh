#!/usr/bin/env bash
# Creates the local staging cluster: kind + Gateway API CRDs + Traefik + the
# staging namespace. Safe to re-run: every step skips or updates what exists.
#
# Requires: docker, kind, kubectl, helm.
set -euo pipefail

CLUSTER_NAME="client-ip"
KUBE_CONTEXT="kind-${CLUSTER_NAME}"

# Gateway API version Traefik v3.7.18 is built against (its go.mod).
GATEWAY_API_VERSION="v1.6.3"
GATEWAY_API_SHA256="356c2b8e286a964dc20995435659ad1095386329974793af10bbfe3eff977fe5"

TRAEFIK_CHART_VERSION="42.4.0" # Traefik v3.7.18

cd "$(dirname "$0")"

echo "==> kind cluster '${CLUSTER_NAME}'"
if kind get clusters | grep -qx "${CLUSTER_NAME}"; then
  echo "    already exists"
else
  kind create cluster --config kind-config.yaml --wait 120s
fi

kc() { kubectl --context "${KUBE_CONTEXT}" "$@"; }

echo "==> Gateway API CRDs ${GATEWAY_API_VERSION} (checksum verified)"
crds="$(mktemp)"
trap 'rm -f "${crds}"' EXIT
curl -fsSL -o "${crds}" \
  "https://github.com/kubernetes-sigs/gateway-api/releases/download/${GATEWAY_API_VERSION}/standard-install.yaml"
echo "${GATEWAY_API_SHA256}  ${crds}" | sha256sum --check --quiet
kc apply --server-side -f "${crds}"
kc wait --for=condition=Established --timeout=60s \
  crd/gateways.gateway.networking.k8s.io crd/httproutes.gateway.networking.k8s.io

echo "==> namespace staging"
kc create namespace staging --dry-run=client -o yaml | kc apply -f -

echo "==> Traefik chart ${TRAEFIK_CHART_VERSION}"
helm repo add traefik https://traefik.github.io/charts >/dev/null 2>&1 || true
helm repo update traefik >/dev/null
helm upgrade --install traefik traefik/traefik \
  --kube-context "${KUBE_CONTEXT}" \
  --namespace traefik --create-namespace \
  --version "${TRAEFIK_CHART_VERSION}" \
  --values traefik-values.yaml \
  --skip-crds \
  --wait --timeout 3m

echo "==> waiting for Gateway traefik/web"
kc -n traefik wait --for=condition=Programmed --timeout=120s gateway/web

echo
echo "Cluster ready. Context: ${KUBE_CONTEXT}"
echo "Gateway: http://localhost/  (404 until an app attaches an HTTPRoute)"
