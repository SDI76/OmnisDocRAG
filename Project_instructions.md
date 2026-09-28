# OmnisDocRAG — Project Instructions

This document is the short entry point for developers. It explains the actual runtime layout, the correct startup order, and where to find the detailed documentation.

---

## Goal

`OmnisDocRAG` provides a local RAG stack for Omnis Studio documentation:

- extract the Omnis PDF manuals (structure from bookmarks, fonts and table positions)
- optionally add the notation reference and 11.1 additions from the Omnis doc pack
- split everything into structured chunks and validate them
- embed the chunks locally
- import them into PostgreSQL with `pgvector`
- run a local HTTP `rag-server` for retrieval OR
- build and run the `docker_mcp-rag` container against PostgreSQL on the host OR
- build and run the `docker_mcp-rag-pg` full stack with PostgreSQL 18 inside Docker
- expose MCP tools to VS Code via the stdio-based `mcp-bridge` OR one of the HTTP-based Docker variants

The project is built around four corpora:

- `omnis-commands` from `CommandRef.pdf` (plus commands that are new in the Omnis 11.1 help)
- `omnis-functions` from `FunctionRef.pdf` (plus functions that are new in the Omnis 11.1 help)
- `omnis-programming` from `Programming_Omnis.pdf`, all chapters
- `omnis-notation` from the Omnis doc pack (optional; Markdown built from the Omnis 11.1 help)

---

## Actual Project Structure

```text
OmnisDocRAG/
├── README.md                   Root overview and document index
├── Documentation/              Concepts, architecture, pipeline docs
├── Omnis PDF/                  Source PDFs
├── output/                     Generated: extracted units, chunks, validation report, embeddings
│   ├── extracted/              Step 1 — units per PDF (JSON)
│   ├── chunks/                 Step 2 — chunks per corpus (JSON)
│   └── embeddings.jsonl        Step 4 — not in git, rebuilt locally
├── scripts/                    extract, chunk, validate, embed, import, eval, bridge test, local SQL setup
├── docker_mcp-rag-pg/          Full containerised stack with PostgreSQL 18 + pgvector
│   ├── docker-compose.yml      Orchestrates postgres + rag-server + mcp-server
│   ├── postgres-init/          10-init-ragdb.sh + sql/ (roles, schema, ranking — shared with the local setup)
│   ├── .env                    Runtime configuration (copy from .env.example)
│   ├── .env.example            Configuration template
│   └── README.md               Full-stack Docker documentation
├── docker_mcp-rag/             Containerised rag-server + mcp-server (PostgreSQL on the host)
│   ├── mcp-server/
│   │   ├── server.py           MCP server — Python FastMCP, Streamable HTTP, port 3000
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── rag-server/
│   │   ├── ragserver.py        FastAPI retrieval server — the only copy of the server code
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── docker-compose.yml      Orchestrates both services
│   ├── .env                    Runtime configuration (copy from .env.example)
│   ├── .env.example            Configuration template
│   └── README.md               Full Docker documentation
└── OmnisRAGServer/
    ├── README.md               Bridge/server contract
    ├── rag-server/
    │   ├── ragserver.py        Local start wrapper for docker_mcp-rag/rag-server/ragserver.py
    │   ├── requirements.txt    RAG server dependencies
    │   ├── .env                Runtime configuration
    │   └── .env.example        Template
    └── mcp-bridge/
        └── mcpserver.mjs       stdio MCP bridge for VS Code
```

---

## Read These First

- [Documentation/Pipeline_en.md](Documentation/Pipeline_en.md)
- [Documentation/chunking_concept_en.md](Documentation/chunking_concept_en.md)
- [Documentation/retrieval_quality_analysis_en.md](Documentation/retrieval_quality_analysis_en.md)
- [Documentation/RAG_concept_en.md](Documentation/RAG_concept_en.md) (original concept, background)
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

Then build the data (see [Standard Data Build Workflow](#standard-data-build-workflow)) and import it
from the repository root:

```bash
python scripts/import_to_docker_postgres.py
```

`output/embeddings.jsonl` is not in git: after a fresh clone run `scripts/embed_and_store.py` first
(minutes on a GPU / Apple Silicon, hours on a plain CPU; `--server http://localhost:7071` uses the
model inside the running rag-server container).

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
- `scripts/validate.py`
- `scripts/embed_and_store.py`
- `scripts/import_to_postgres.py`
- `scripts/import_to_docker_postgres.py`
- `scripts/eval_retrieval.py`

Local settings that must not be committed (e.g. the doc pack path) go into `scripts/.env.local`
(git-ignored):

```env
OMNISDOC_PACK=/path/to/omnisdoc
```

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

Use (they include the shared SQL from `docker_mcp-rag-pg/postgres-init/sql/`):

- `scripts/setup_db.sql` — roles, then schema (run again with `-d ragdb`)
- `scripts/setup_ranking.sql` — `rag.search_ranked`

Manual schema setup is only needed for the local/external PostgreSQL path.
The full Docker stack initializes the database automatically on first startup.

Schema details: [Documentation/postgres_en.md](Documentation/postgres_en.md)

---

## Standard Data Build Workflow

Run these from the project root after activating the pipeline virtual environment:

```bash
python scripts/extract.py
python scripts/chunk.py --omnisdoc /path/to/omnisdoc    # doc pack optional (or OMNISDOC_PACK in scripts/.env.local)
python scripts/validate.py
python scripts/embed_and_store.py                        # or --server http://localhost:7071
```

What each step does:

1. `extract.py` reads the PDF structure (bookmarks, fonts, metadata tables) and writes units to
   `output/extracted/` plus readable Markdown to `output/*_extracted.md`.
2. `chunk.py` creates the chunk files in `output/chunks/` (with the doc pack also the notation corpus
   and entries that are new in 11.1).
3. `validate.py` is the quality gate — it fails when entries are missing, code lines became titles,
   ligature damage is left, or chunks are empty/oversized.
4. `embed_and_store.py` creates `output/embeddings.jsonl` (not in git). It is incremental: only
   changed chunks are embedded again; `--force` re-embeds everything.
5. Import into your target PostgreSQL:
   - local/external PostgreSQL: `python scripts/import_to_postgres.py`
   - Docker PostgreSQL in `docker_mcp-rag-pg/`: `python scripts/import_to_docker_postgres.py`
6. Check retrieval quality: `python scripts/eval_retrieval.py --compare`

Details: [Documentation/Pipeline_en.md](Documentation/Pipeline_en.md),
[Documentation/chunking_concept_en.md](Documentation/chunking_concept_en.md).

### Import modes (full-sync vs upsert-only)

`scripts/import_to_postgres.py` supports two modes controlled by `DELETE_STALE_DOCS`:

- Full-sync (default): `DELETE_STALE_DOCS=1`
  - Upserts the current chunks and embeddings.
  - Deletes documents of the imported corpora that are no longer in `output/chunks/`.
- Upsert-only: `DELETE_STALE_DOCS=0`
  - Upserts the current chunks and embeddings.
  - Keeps older rows that are not in the current chunk files.

The importer refuses to run when an embedding is missing or belongs to an older chunk text.

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

The first start downloads the `BAAI/bge-m3` model (~2.2 GB) into the named volume `hf_cache`.
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
- Documentation in `Documentation/` is written in English (`_en` files).
- Treat `output/` as generated artifacts; `output/embeddings.jsonl` is git-ignored (exceeds GitHub's file limit).
- `embed_and_store.py` uses local `sentence-transformers` with `BAAI/bge-m3` (~2.2 GB download; MPS/CUDA
  used automatically) or, with `--server`, the model of the running rag-server.
- `scripts/import_to_postgres.py` reads database environment values from `scripts/.env`.
- `scripts/import_to_docker_postgres.py` reads Docker DB settings from `docker_mcp-rag-pg/.env`.
- Three runtime topologies are available:
  - **Local:** `rag-server (Python) → mcp-bridge (Node.js) → VS Code (stdio)`
  - **Docker with host PostgreSQL:** `PostgreSQL (host) → rag-server (container) → mcp-server (container) → VS Code (HTTP)`
  - **Full Docker stack:** `postgres (container) → rag-server (container) → mcp-server (container) → VS Code (HTTP)`
- `docker_mcp-rag/rag-server/ragserver.py` is the only copy of the server code; `OmnisRAGServer/rag-server/ragserver.py`
  starts it for the local topology.
- `docker_mcp-rag-pg/` reuses those Docker service folders but adds PostgreSQL 18 + `pgvector` and database bootstrap.
- The Docker MCP server uses Python FastMCP with Streamable HTTP, not the Node.js stdio bridge. `mcp` is pinned
  below 2.0 (2.x renamed FastMCP). Both MCP front-ends offer the same four tools.
- The HuggingFace model cache is persisted in the named Docker volume `hf_cache` to avoid repeated downloads.

---

## Agentic Programming — MCP Setup for VS Code

This section is for developers using a coding agent (GitHub Copilot, Claude Code, or any MCP-aware assistant) inside this workspace.

### VS Code MCP configuration (`.vscode/mcp.json`)

Create `.vscode/mcp.json` in the workspace root (one or both entries, depending on which variant is running):

```json
{
  "servers": {
    "omnis-rag-docker": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    },
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
}
```

- Use `omnis-rag-docker` when `docker compose up` is running in `docker_mcp-rag/`.
- Use `omnis-rag-local` when the RAG server and MCP bridge are started manually (see [Runtime Startup Order](#runtime-startup-order)).
- After changing `mcp.json`, run **MCP: Restart Server** in VS Code to pick up the changes.

### Coding agent instructions (`CLAUDE.md` / `.github/copilot-instructions.md`)

To make the coding agent use these MCP tools automatically, add the following block to your agent instruction file.
For Claude Code that is `CLAUDE.md` in the workspace root; for GitHub Copilot it is `.github/copilot-instructions.md`.

---

#### MCP Usage Defaults (Project-wide)

For Omnis tasks in this repository, prefer MCP knowledge/functions whenever available:

1. **Syntax/Behavior questions first:** If Omnis language behavior or function semantics are unclear, query MCP-provided Omnis docs before implementing.
2. **Class retrieval first:** For missing or outdated local classes, use MCP class retrieval workflow (`getClass`) instead of manually recreating structures.
3. **Source of truth priority:** If local export and MCP payload differ, treat MCP payload as authoritative for reconstruction, then re-check local integration points.
4. **Traceability:** When MCP data is used for implementation decisions, mention briefly which class/payload was used in the handoff summary.

#### Omnis RAG via MCP-Bridge (for Coding Agent)

When working in this workspace, the coding agent should use the MCP bridge server `omnis-rag-docker` or `omnis-rag-local` for Omnis documentation grounding.

1. **Tools:** `search_omnis_docs` (default), `get_omnis_doc`; restricted variants `search_omnis_syntax`
   (commands, functions, notation) and `search_omnis_concepts` (Programming manual).
2. **When to call RAG:** when Omnis syntax or semantics are unclear (uncertainty-first), not for every coding step.
3. **Two steps:** search first — the answer lists hits with title, source, id and a snippet (a few KB).
   Then fetch only the relevant ids with `get_omnis_doc` and base the code on that full text.
4. **Modes of `search_omnis_docs`:**
   - `hybrid` (default) — meaning and words combined; right for most questions, English or German.
   - `semantic` — meaning only; for loosely phrased questions.
   - `fulltext` — words only; for exact terms, error texts, `"exact phrases"`, `OR`, `-exclusion`.
5. **Exact names** (`mid()`, `$search`, `#ERRCODE`, `Begin reversible block`) can be searched directly;
   the matching entry is ranked first.
6. **Deprecated entries** are marked `[deprecated]` in the result list — explain them, do not propose them.
7. **Large topics:** several focused searches beat one broad one (e.g. `$sendall` → `$sendallref`).
8. **Fallback:** if the server is unavailable, say so and continue best-effort from local project patterns.
9. **Runtime:** `omnis-rag-docker` at `http://localhost:3000/mcp`; `omnis-rag-local` needs the rag-server at
   `http://127.0.0.1:7071` (bridge started by VS Code).

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
python scripts/chunk.py --omnisdoc /path/to/omnisdoc   # doc pack optional
python scripts/validate.py
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
python scripts/chunk.py --omnisdoc /path/to/omnisdoc   # doc pack optional
python scripts/validate.py
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

If you are new to the codebase, read `Pipeline_en.md` first, then `chunking_concept_en.md`, then `docker_mcp-rag-pg/README.md` or `docker_mcp-rag/README.md` depending on the runtime you want. `RAG_concept_en.md` documents the original design decisions.
