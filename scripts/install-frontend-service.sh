#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="umdl2-frontend.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Installing ${SERVICE_NAME}..."

if [[ ! -f "${REPO_ROOT}/dist/index.html" ]]; then
  echo "[WARN] dist/ not found. Building frontend before installing service..."
  (cd "${REPO_ROOT}" && npm ci && npm run build)
fi

echo "Copying service file to ${SERVICE_PATH}"
sudo cp "${REPO_ROOT}/${SERVICE_NAME}" "${SERVICE_PATH}"
sudo chmod 644 "${SERVICE_PATH}"

echo "Reloading systemd daemon"
sudo systemctl daemon-reload

echo "Enabling and starting ${SERVICE_NAME}"
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo "Checking status"
sudo systemctl --no-pager -l status "${SERVICE_NAME}"

echo "Done. Service ${SERVICE_NAME} is installed and running."

