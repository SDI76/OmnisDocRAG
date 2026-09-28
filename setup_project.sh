#!/usr/bin/env bash
# Bootstrap for macOS / Linux. Windows: setup_project.ps1.
# All logic lives in scripts/pipeline.py (standard library only), so every OS
# gets the same setup: .venv for the pipeline, OmnisRAGServer/rag-server/.venv
# for the local rag-server, and a check of what the machine can do.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PY="$(command -v python3 || command -v python || true)"
if [[ -z "$PY" ]]; then
  echo "[setup] Python 3.10+ is required (python3 not found)." >&2
  exit 1
fi

"$PY" scripts/pipeline.py setup --rag-server
"$PY" scripts/pipeline.py doctor

cat <<'EOF'

Next steps:
  source .venv/bin/activate
  python scripts/pipeline.py build              # extract → chunk → validate → embed → import → eval
  python scripts/pipeline.py build --from embed # when the chunks in output/ are current
Local topology: python OmnisRAGServer/rag-server/ragserver.py, then the MCP bridge (VS Code starts it).
EOF
