#!/usr/bin/env bash
# Standalone SAJ H2 Safe Enhanced installer. Only integration files are copied.
set -euo pipefail
REPO="https://github.com/userdc-dev/saj-h2-safe-enhanced/archive/refs/heads/main.tar.gz"
CONFIG="${1:-}"
if [[ -z "${CONFIG}" ]] && command -v docker >/dev/null 2>&1; then
  CONFIG="$(docker inspect homeassistant --format '{{range .Mounts}}{{if eq .Destination "/config"}}{{.Source}}{{end}}{{end}}' 2>/dev/null || true)"
fi
if [[ -z "${CONFIG}" && -d "./.storage" ]]; then CONFIG="$(pwd)"; fi
if [[ -z "${CONFIG}" || ! -d "${CONFIG}" ]]; then
  echo "Cannot locate Home Assistant /config host directory."
  echo "Usage: bash install.sh /path/to/homeassistant/config"
  exit 1
fi
if [[ ! -d "${CONFIG}/.storage" ]]; then
  echo "Selected directory is not a known Home Assistant config folder: ${CONFIG}"
  exit 1
fi
TEMP="$(mktemp -d)"
trap 'rm -rf "${TEMP}"' EXIT
curl -fL --retry 2 --connect-timeout 10 "${REPO}" -o "${TEMP}/source.tgz"
tar -xzf "${TEMP}/source.tgz" -C "${TEMP}"
SOURCE="${TEMP}/saj-h2-safe-enhanced-main/custom_components/saj_h2_safe"
DEST="${CONFIG}/custom_components/saj_h2_safe"
mkdir -p "${DEST}"
cp -a "${SOURCE}/." "${DEST}/"
echo "SAJ H2 Safe Enhanced integration installed into: ${DEST}"
echo "Existing settings and entities are preserved."
if command -v docker >/dev/null 2>&1 && docker inspect homeassistant >/dev/null 2>&1; then
  echo "Restart: docker restart homeassistant"
else
  echo "Restart Home Assistant, then Settings → Devices & services → Add integration → SAJ H2 Safe Monitor."
fi
