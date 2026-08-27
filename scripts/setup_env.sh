#!/usr/bin/env bash
set -euo pipefail
if [ -f .env ]; then
  echo ".env already exists — not overwriting"
  exit 0
fi
if [ -f .env.example ]; then
  cp .env.example .env
  echo "Created .env from .env.example — open .env and add your API keys and tokens before running the service."
else
  echo ".env.example not found — create a .env with required vars (see README.md)"
fi
