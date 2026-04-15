# OmnisDocRAG — Project Instructions

This document is the short entry point for developers. It explains the actual runtime layout, the correct startup order, and where to find the detailed documentation.

---

## Goal

`OmnisDocRAG` provides a local RAG stack for Omnis Studio documentation:

- extract Omnis PDF manuals into Markdown
- split them into structured chunks
- embed the chunks locally
- import them into PostgreSQL with `pgvector`
- run a local HTTP `rag-server` for retrieval OR
- build and run the `docker_mcp-rag` container against PostgreSQL on the host OR
- build and run the `docker_mcp-rag-pg` full stack with PostgreSQL 18 inside Docker
- expose MCP tools to VS Code via the stdio-based `mcp-bridge` OR one of the HTTP-based Docker variants

The project is built around three corpora:

- `omnis-commands` from `CommandRef.pdf`
- `omnis-functions` from `FunctionRef.pdf`
- `omnis-programming` from `Programming_Omnis.pdf`

---

## Actual Project Structure

```text
OmnisDocRAG/
├── README.md                   Root overview and document index
├── Documentation/              Concepts, architecture, pipeline docs
├── Omnis PDF/                  Source PDFs
├── output/                     Extracted Markdown, chunks, embeddings
├── scripts/                    Extraction, chunking, embedding, DB import
├── docker_mcp-rag-pg/          Full containerised stack with PostgreSQL 18 + pgvector
│   ├── docker-compose.yml      Orchestrates postgres + rag-server + mcp-server
│   ├── postgres-init/          Auto-init SQL and bootstrap scripts
│   ├── .env                    Runtime configuration (copy from .env.example)
│   ├── .env.example            Configuration template
│   └── README.md               Full-stack Docker documentation
├── docker_mcp-rag/             Containerised stack (self-contained, independent of OmnisRAGServer)
│   ├── mcp-server/
│   │   ├── server.py           MCP server — Python FastMCP, Streamable HTTP, port 3000
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── rag-server/
│   │   ├── ragserver.py        FastAPI retrieval server (copy of OmnisRAGServer variant)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── docker-compose.yml      Orchestrates both services
│   ├── .env                    Runtime configuration (copy from .env.example)
│   ├── .env.example            Configuration template
│   └── README.md               Full Docker documentation
└── OmnisRAGServer/
    ├── README.md               Bridge/server contract
    ├── rag-server/
    │   ├── ragserver.py        FastAPI retrieval server
    │   ├── requirements.txt    RAG server dependencies
    │   ├── .env                Runtime configuration
    │   └── .env.example        Template
    └── mcp-bridge/
        └── mcpserver.mjs       stdio MCP bridge for VS Code
```

---

## Read These First

- [Documentation/RAG_concept_en.md](Documentation/RAG_concept_en.md)
- [Documentation/Pipeline_en.md](Documentation/Pipeline_en.md)
- [Documentation/chunking_concept_en.md](Documentation/chunking_concept_en.md)
- [Documentation/embedding_concept_en.md](Documentation/embedding_concept_en.md)
- [Documentation/postgres_en.md](Documentation/postgres_en.md)
- [Documentation/expected_outcome_en.md](Documentation/expected_outcome_en.md)
- [OmnisRAGServer/README.md](OmnisRAGServer/README.md)
- [docker_mcp-rag-pg/README.md](docker_mcp-rag-pg/README.md)
- [docker_mcp-rag/README.md](docker_mcp-rag/README.md)

---

## Setup

### Fastest setup

If you want the project to work on a fresh machine with the fewest external prerequisites,
use the full Docker stack in `docker_mcp-rag-pg/`.

```bash
cd docker_mcp-rag-pg
cp .env.example .env
docker compose up --build -d
```

Then import the generated embeddings from the repository root:

```bash
python scripts/import_to_docker_postgres.py
```

### Local bootstrap helper

From the project root:

```bash
bash setup_project.sh
```

This bootstrap script:

- creates the root pipeline virtual environment at `.venv`
- creates the RAG server virtual environment at `OmnisRAGServer/rag-server/.venv`
- installs all Python dependencies for both environments
- checks that `python3` and `node` are available
- creates `OmnisRAGServer/rag-server/.env` from `.env.example` if it is missing

It does not install system-level dependencies such as PostgreSQL or Node.js itself.

### 1. Pipeline virtual environment

From the project root:

```bash
cd OmnisDocRAG
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r scripts/requirements.txt
```

This installs the dependencies for:

- `scripts/extract.py`
- `scripts/chunk.py`
- `scripts/embed_and_store.py`
- `scripts/import_to_postgres.py`
- `scripts/import_to_docker_postgres.py`

### 2. RAG server environment

The retrieval server has its own runtime folder:

```bash
cd OmnisRAGServer/rag-server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configuration lives in:

```text
OmnisRAGServer/rag-server/.env
```

### 3. Node runtime for the MCP bridge

Use a current Node.js LTS version. Node 20 is a safe default.

```bash
node --version
```

`OmnisRAGServer/mcp-bridge/mcpserver.mjs` currently uses built-in Node APIs only, so no separate `npm install` step is required.

### 4. PostgreSQL runtime

You need PostgreSQL with `pgvector` before importing embeddings.

There are now two supported database paths:

- Local or external PostgreSQL managed outside Docker
- PostgreSQL 18 inside `docker_mcp-rag-pg/` with automatic bootstrap

Use:

- `scripts/setup_db.sql`
- `scripts/setup_ranking.sql`

Manual schema setup is only needed for the local/external PostgreSQL path.
The full Docker stack initializes the database automatically on first startup.

Schema details: [Documentation/postgres_en.md](Documentation/postgres_en.md)

---

## Standard Data Build Workflow

Run these from the project root after activating the pipeline virtual environment:

```bash
python scripts/extract.py
python scripts/chunk.py
python scripts/embed_and_store.py
```

What each step does:

1. `extract.py` converts PDFs to Markdown.
2. `chunk.py` creates JSON chunk files in `output/chunks/`.
3. `embed_and_store.py` creates `output/embeddings.jsonl`.
4. Import the generated embeddings into your target PostgreSQL:
   - local/external PostgreSQL: `python scripts/import_to_postgres.py`
   - Docker PostgreSQL in `docker_mcp-rag-pg/`: `python scripts/import_to_docker_postgres.py`

If chunk content changes, rebuild embeddings with:

```bash
python scripts/embed_and_store.py --force
```

### Import modes (full-sync vs upsert-only)

`scripts/import_to_postgres.py` supports two modes controlled by `DELETE_STALE_DOCS`:

- Full-sync (default): `DELETE_STALE_DOCS=1`
  - Upserts current embeddings.
  - Deletes stale documents in `omnis-commands`, `omnis-functions`, and `omnis-programming` that are no longer present in `output/embeddings.jsonl`.
- Upsert-only: `DELETE_STALE_DOCS=0`
  - Upserts current embeddings.
  - Keeps older rows that are not in the current JSONL.

Examples:

```bash
# full-sync (default)
python scripts/import_to_postgres.py

# explicit full-sync
DELETE_STALE_DOCS=1 python scripts/import_to_postgres.py

# upsert-only
DELETE_STALE_DOCS=0 python scripts/import_to_postgres.py
```

PowerShell equivalents:

```powershell
# explicit full-sync
$env:DELETE_STALE_DOCS = "1"; python scripts/import_to_postgres.py

# upsert-only
$env:DELETE_STALE_DOCS = "0"; python scripts/import_to_postgres.py

# optional cleanup
Remove-Item Env:DELETE_STALE_DOCS
```

`scripts/import_to_docker_postgres.py` delegates to the same importer and therefore
inherits the same full-sync or upsert-only behavior.

---

## Runtime Startup Order

This part is important:

1. PostgreSQL must already contain the imported embeddings.
2. `rag-server` must be running before MCP requests are sent.
3. The MCP layer depends on the active runtime variant:
   - local: `mcp-bridge` forwards to the local `rag-server`
   - Docker: `mcp-server` forwards to the containerized `rag-server`

### Start the RAG server

```bash
cd OmnisRAGServer/rag-server
source .venv/bin/activate
python ragserver.py
```

Default endpoint:

```text
http://127.0.0.1:7071
```

### Start the MCP bridge

If needed, point it to the running RAG server:

```bash
export OMNIS_RAG_SERVER_URL=http://127.0.0.1:7071
```

Then start the bridge:

```bash
cd OmnisRAGServer/mcp-bridge
node mcpserver.mjs
```

The MCP bridge is dependent on the RAG server. If `rag-server` is not running, MCP requests will fail.

---

## Docker Variants

Two Docker paths are available:

- `docker_mcp-rag/`: runs `rag-server` + `mcp-server`, but still connects to PostgreSQL on the host
- `docker_mcp-rag-pg/`: runs `postgres` + `rag-server` + `mcp-server` as one out-of-the-box stack

No local Python environment or Node.js bridge is needed at runtime for either Docker variant.

### Variant A — Docker with host PostgreSQL

### Architecture

```text
VS Code (HTTP MCP client)
    │  HTTP POST http://localhost:3000/mcp
    ▼
mcp-server  (Python FastMCP, Streamable HTTP, port 3000)
    │  HTTP http://rag-server:7071  (internal Docker network)
    ▼
rag-server  (FastAPI, port 7071)
    │  TCP
    ▼
PostgreSQL on host  (host.docker.internal)
```

### Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux)
- PostgreSQL already populated via the pipeline scripts (see [Standard Data Build Workflow](#standard-data-build-workflow))
- PostgreSQL configured to accept connections from the Docker subnet (see `docker_mcp-rag/README.md`)

### First-time setup

```bash
cd docker_mcp-rag
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
```

Edit `.env` and set at minimum:

```env
RAG_DB_USER=rag_app
RAG_DB_PASS=your_password
RAG_DB_NAME=ragdb
```

### Build and start

```bash
cd docker_mcp-rag
docker compose up --build
```

The first start downloads the `BAAI/bge-m3` model (~1.1 GB) into the named volume `hf_cache`.
Subsequent starts reuse the cached model and are much faster.

```bash
# Start in background
docker compose up -d

# Follow logs of the MCP server only
docker compose logs -f mcp-server

# Stop everything
docker compose down
```

### Health check

The `rag-server` container exposes a `/health` endpoint:

```bash
curl http://localhost:7071/health
```

The `mcp-server` only starts after `rag-server` passes its health check (`depends_on: service_healthy`).

### VS Code MCP configuration

**Local stdio variant** (requires local RAG server + Node.js bridge):

```json
{
  "omnis-rag-local": {
    "type": "stdio",
    "command": "node",
    "args": [
      "${workspaceFolder}/OmnisRAGServer/mcp-bridge/mcpserver.mjs"
    ],
    "env": {
      "OMNIS_RAG_SERVER_URL": "http://127.0.0.1:7071"
    }
  }
}
```

**Docker HTTP variant** (requires `docker compose up` in `docker_mcp-rag/`):

```json
{
  "omnis-rag-docker": {
    "type": "http",
    "url": "http://localhost:3000/mcp"
  }
}
```

Both entries can coexist in `.vscode/mcp.json`. Use one or the other depending on which variant is running.

### Variant B — Full Docker stack with PostgreSQL 18

The `docker_mcp-rag-pg/` folder contains the full stack:

```text
VS Code (HTTP MCP client)
    │  HTTP POST http://localhost:3000/mcp
    ▼
mcp-server  (Python FastMCP, Streamable HTTP, port 3000)
    │  HTTP http://rag-server:7071
    ▼
rag-server  (FastAPI, port 7071)
    │  TCP
    ▼
postgres  (Docker, PostgreSQL 18 + pgvector)
```

This is the recommended setup for new machines and shared environments because:

- no local PostgreSQL installation is required
- the database schema and roles are created automatically on first start
- the PostgreSQL host port is configurable in `docker_mcp-rag-pg/.env`
- imports can target the container DB via `python scripts/import_to_docker_postgres.py`

Quick start:

```bash
cd docker_mcp-rag-pg
cp .env.example .env
docker compose up --build -d
cd ..
python scripts/import_to_docker_postgres.py
```

Full details: [docker_mcp-rag-pg/README.md](docker_mcp-rag-pg/README.md)

---

## Important Notes

- Work only inside `OmnisDocRAG` for this finalized project copy.
- Keep German originals in `Documentation/` and add English versions as separate `_en` files.
- Treat `output/` as generated artifacts.
- `embed_and_store.py` uses local `sentence-transformers` with `BAAI/bge-m3`, which downloads a large model on first run.
- `scripts/import_to_postgres.py` reads database environment values from `scripts/.env`.
- `scripts/import_to_docker_postgres.py` reads Docker DB settings from `docker_mcp-rag-pg/.env`.
- Three runtime topologies are available:
  - **Local:** `rag-server (Python) → mcp-bridge (Node.js) → VS Code (stdio)`
  - **Docker with host PostgreSQL:** `PostgreSQL (host) → rag-server (container) → mcp-server (container) → VS Code (HTTP)`
  - **Full Docker stack:** `postgres (container) → rag-server (container) → mcp-server (container) → VS Code (HTTP)`
- `docker_mcp-rag/` is self-contained. Its `rag-server/` and `mcp-server/` are independent copies of the source in `OmnisRAGServer/`.
- `docker_mcp-rag-pg/` reuses those Docker service folders but adds PostgreSQL 18 + `pgvector` and database bootstrap.
- The Docker MCP server uses Python FastMCP with Streamable HTTP (MCP protocol 2025-03-26), not the Node.js stdio bridge.
- The HuggingFace model cache is persisted in the named Docker volume `hf_cache` to avoid repeated downloads.

---

## Quick Start

### Local variant

```bash
# 1. Pipeline — run once to build the data
cd OmnisDocRAG
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r scripts/requirements.txt
python scripts/extract.py
python scripts/chunk.py
python scripts/embed_and_store.py
python scripts/import_to_postgres.py

# 2. RAG server — terminal 1
cd OmnisRAGServer/rag-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ragserver.py

# 3. MCP bridge — terminal 2
cd OmnisRAGServer/mcp-bridge
node mcpserver.mjs
```

### Docker variant

```bash
# 1. Pipeline — run once (same as above, uses local .venv)
python scripts/extract.py
python scripts/chunk.py
python scripts/embed_and_store.py

# 2a. Host-PostgreSQL Docker runtime
cd docker_mcp-rag
copy .env.example .env
docker compose up --build

# 2b. Full Docker stack with PostgreSQL 18
cd ../docker_mcp-rag-pg
copy .env.example .env
docker compose up --build
cd ..
python scripts/import_to_docker_postgres.py
```

After startup, register `http://localhost:3000/mcp` as an HTTP MCP server in VS Code.

If you are new to the codebase, read `RAG_concept_en.md` first, then `Pipeline_en.md`, then `docker_mcp-rag-pg/README.md` or `docker_mcp-rag/README.md` depending on the runtime you want.
