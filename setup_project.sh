#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_VENV="$ROOT_DIR/.venv"
RAG_SERVER_DIR="$ROOT_DIR/OmnisRAGServer/rag-server"
RAG_SERVER_VENV="$RAG_SERVER_DIR/.venv"
PIPELINE_REQ="$ROOT_DIR/scripts/requirements.txt"
RAG_SERVER_REQ="$RAG_SERVER_DIR/requirements.txt"
PIPELINE_ENV="$ROOT_DIR/scripts/.env"
RAG_SERVER_ENV="$RAG_SERVER_DIR/.env"
RAG_SERVER_ENV_EXAMPLE="$RAG_SERVER_DIR/.env.example"

log() {
  printf '\n[%s] %s\n' "setup" "$1"
}

require_cmd() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '\n[setup] Missing required command: %s\n' "$cmd" >&2
    printf '[setup] %s\n' "$hint" >&2
    exit 1
  fi
}

create_venv_and_install() {
  local venv_path="$1"
  local requirements_file="$2"
  local label="$3"

  log "Preparing ${label} virtual environment at ${venv_path}"
  python3 -m venv "$venv_path"
  # shellcheck disable=SC1090
  source "$venv_path/bin/activate"
  python -m pip install --upgrade pip
  pip install -r "$requirements_file"
  deactivate
}

log "Starting OmnisDocRAG bootstrap"

require_cmd python3 "Install Python 3.10+ and run this script again."
require_cmd node "Install Node.js LTS (recommended: Node 20) and run this script again."

log "Detected Python: $(python3 --version 2>&1)"
log "Detected Node: $(node --version 2>&1)"

create_venv_and_install "$PIPELINE_VENV" "$PIPELINE_REQ" "pipeline"
create_venv_and_install "$RAG_SERVER_VENV" "$RAG_SERVER_REQ" "rag-server"

if [[ ! -f "$RAG_SERVER_ENV" && -f "$RAG_SERVER_ENV_EXAMPLE" ]]; then
  log "Creating rag-server .env from .env.example"
  cp "$RAG_SERVER_ENV_EXAMPLE" "$RAG_SERVER_ENV"
fi

if [[ ! -f "$PIPELINE_ENV" ]]; then
  log "scripts/.env is missing. Create it before running import_to_postgres.py."
fi

log "Bootstrap complete"

printf '\nNext steps:\n'
printf '1. Review scripts/.env for PostgreSQL import settings.\n'
printf '2. Review OmnisRAGServer/rag-server/.env for server runtime settings.\n'
printf '3. Activate the pipeline venv when running build scripts:\n'
printf '   source .venv/bin/activate\n'
printf '4. Activate the rag-server venv when running the HTTP server:\n'
printf '   source OmnisRAGServer/rag-server/.venv/bin/activate\n'
printf '5. Start services in order:\n'
printf '   python OmnisRAGServer/rag-server/ragserver.py\n'
printf '   node OmnisRAGServer/mcp-bridge/mcpserver.mjs\n'
