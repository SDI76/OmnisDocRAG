"""
Local start of the Omnis RAG server.

The server code lives in one place: docker_mcp-rag/rag-server/ragserver.py
(the Docker image builds from there). This wrapper runs that file with the
`.env` next to this wrapper, so the local topology keeps working unchanged:

    python OmnisRAGServer/rag-server/ragserver.py
"""

import os
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANONICAL = HERE.parent.parent / "docker_mcp-rag" / "rag-server" / "ragserver.py"

os.environ.setdefault("OMNIS_RAG_ENV_FILE", str(HERE / ".env"))
runpy.run_path(str(CANONICAL), run_name="__main__")
