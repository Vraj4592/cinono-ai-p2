#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — prepares the repo, venv, installs deps and writes systemd unit files using detected paths
ROOT_DIR="$(pwd)"
VENV_DIR="$ROOT_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"
UVCORN_BIN="$VENV_DIR/bin/uvicorn"
USER="$(whoami)"

echo "Deploying Cinono AI from: $ROOT_DIR"

# create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# activate and install
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements.txt || true
if [ -f requirements_extra.txt ]; then
  pip install -r requirements_extra.txt || true
fi

# create .env from example if missing
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo ".env created from .env.example — edit it to add credentials." 
fi

# prepare systemd units by replacing placeholders
SYSTEMD_DIR="systemd"
if [ -d "$SYSTEMD_DIR" ]; then
  echo "Writing systemd units to /etc/systemd/system (requires sudo)"
  API_UNIT="/etc/systemd/system/cinono-api.service"
  WORKER_UNIT="/etc/systemd/system/cinono-worker.service"
  sudo sed "s|/path/to/cinono-ai-p2|$ROOT_DIR|g; s|/path/to/cinono-ai-p2/venv/bin/uvicorn|$UVCORN_BIN|g; s|/path/to/cinono-ai-p2/venv/bin/python|$PYTHON_BIN|g; s|youruser|$USER|g" systemd/cinono-api.service | sudo tee "$API_UNIT" > /dev/null
  sudo sed "s|/path/to/cinono-ai-p2|$ROOT_DIR|g; s|/path/to/cinono-ai-p2/venv/bin/uvicorn|$UVCORN_BIN|g; s|/path/to/cinono-ai-p2/venv/bin/python|$PYTHON_BIN|g; s|youruser|$USER|g" systemd/cinono-worker.service | sudo tee "$WORKER_UNIT" > /dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable --now cinono-api
  sudo systemctl enable --now cinono-worker
  echo "systemd units created and enabled. Check 'journalctl -u cinono-api -f' and 'journalctl -u cinono-worker -f'"
else
  echo "No systemd dir found; skipping systemd setup"
fi

echo "Deployment script finished. Edit .env with your secrets and ensure CUDA and model deps are installed on the GPU machine per docs/GPU_SETUP.md"
