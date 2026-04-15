# Omnis Studio RAG — Pipeline Documentation

Complete technical documentation for the processing pipeline from the Omnis PDFs to the
PostgreSQL vector database and the supported local or Docker-based runtimes.

---

## Overview

```text
PDF documents
    │
    │  scripts/extract.py
    ▼
Markdown files (output/)
    │
    │  scripts/chunk.py
    ▼
JSON chunk files (output/chunks/)
    │
    │  scripts/embed_and_store.py
    │  Embedding via sentence-transformers (BAAI/bge-m3, one-time)
    ▼
embeddings.jsonl (output/)
    │
    │  scripts/import_to_postgres.py
    ▼
PostgreSQL ragdb
    │
    │  local/external PostgreSQL or docker_mcp-rag-pg/postgres
    ▼
Retrieval database
    │
    │  OmnisRAGServer/rag-server/ragserver.py
    │  Embedding via sentence-transformers (bge-m3, at runtime)
    ▼
Local HTTP retrieval endpoint (/search)
    │
    │  OmnisRAGServer/mcp-bridge/mcpserver.mjs
    ▼
VS Code MCP / stdio tools
```

**Three document collections:**

| Corpus | Source | Chunks | Avg. Words |
|---|---|---|---|
| `omnis-commands` | CommandRef.pdf | 485 | 275 |
| `omnis-functions` | FunctionRef.pdf | 327 | 117 |
| `omnis-programming` | Programming_Omnis.pdf | 1543 | 152 |
| **Total** | | **2355** | |

---

## Prerequisites

**Mac (pipeline + local runtime):**
```bash
python3 --version      # >= 3.10
pip install -r scripts/requirements.txt
```

**PostgreSQL (manual/local path):**
```bash
# PostgreSQL >= 15 with pgvector extension
sudo apt install postgresql-16
sudo apt install postgresql-16-pgvector
```

**Docker alternative:**

- `docker_mcp-rag-pg/` provides PostgreSQL 18 + `pgvector` with automatic bootstrap
- no manual DB installation is required for that path

**Model:** `BAAI/bge-m3` via `sentence-transformers` — downloaded automatically on first use
(~2 GB, then cached under `~/.cache/huggingface/`).

---

## Project Structure

```text
OmnisDocRAG/
├── Documentation/
├── Omnis PDF/
│   ├── CommandRef.pdf
│   ├── FunctionRef.pdf
│   └── Programming_Omnis.pdf
│
├── scripts/
│   ├── requirements.txt          Pipeline dependencies
│   ├── extract.py                Step 1: PDF -> Markdown
│   ├── chunk.py                  Step 2: Markdown -> JSON chunks
│   ├── embed_and_store.py        Step 3: Chunks -> embeddings.jsonl
│   ├── import_to_postgres.py     Step 4: embeddings.jsonl -> PostgreSQL
│   ├── import_to_docker_postgres.py  Step 4b: embeddings.jsonl -> Docker PostgreSQL
│   ├── setup_db.sql              Create database schema
│   └── setup_ranking.sql         Hybrid search functions
│
├── output/
│   ├── CommandRef_extracted.md
│   ├── FunctionRef_extracted.md
│   ├── Programming_extracted.md
│   ├── embeddings.jsonl          (after step 3)
│   └── chunks/
│       ├── commands_chunks.json
│       ├── functions_chunks.json
│       └── programming_chunks.json
│
├── docker_mcp-rag-pg/
│   ├── docker-compose.yml        postgres + rag-server + mcp-server
│   ├── postgres-init/           Database bootstrap for PG18 + pgvector
│   └── README.md                Full Docker-stack runtime docs
│
├── docker_mcp-rag/
│   └── README.md                MCP/RAG Docker stack using PostgreSQL on the host
│
└── OmnisRAGServer/
    ├── README.md                 Bridge/server contract
    ├── rag-server/
    │   ├── ragserver.py         RAG server (FastAPI)
    │   ├── requirements.txt     RAG server dependencies
    │   ├── .env                 Configuration (do not commit)
    │   └── .env.example         Template
    └── mcp-bridge/
        └── mcpserver.mjs        stdio MCP bridge for VS Code
```

---

## Step 1 — Extraction: `extract.py`

**Purpose:** Converts the three Omnis PDFs into Markdown.

**Run:**
```bash
python3 scripts/extract.py
```

**Hybrid approach:**

- `pymupdf4llm` provides document structure (headings, tables, code blocks as Markdown)
- `pdfplumber` fixes code blocks: PDF code is glyph-position-based, and without correction
  spaces disappear (`CalculatelResultas42` instead of `Calculate lResult as 42`)
- Per page, mono-space lines are extracted via `pdfplumber`, whitespace is normalized, and
  inserted back into the `pymupdf4llm` output

**Excluded pages:**

| Document | Excluded pages | Reason |
|---|---|---|
| CommandRef | 0-9 (10 pages) | Index pages, command-group overviews |
| FunctionRef | 0-6 (7 pages) | Intro, multi-column tables (rendering issues) |
| Programming | 0-5, 8-82, 156-220 | TOC, chapter 1 (IDE), chapter 4 (debugger) |

**Output:**

| File | Size | Lines |
|---|---|---|
| `output/CommandRef_extracted.md` | ~785 KB | ~23,700 |
| `output/FunctionRef_extracted.md` | ~249 KB | ~9,900 |
| `output/Programming_extracted.md` | ~1.5 MB | ~27,000 |

---

## Step 2 — Chunking: `chunk.py`

**Purpose:** Splits the Markdown files into semantic chunks with metadata.

**Run:**
```bash
python3 scripts/chunk.py
```

### Chunking Strategy

#### CommandRef — Atomic Command Chunking

1 command = 1 chunk. Chunk boundaries are detected via **lookahead**:
an H2 heading is only treated as a chunk boundary if `|Command group|` appears
within the next 10 lines. This correctly skips syntax demo headings such as
`## Build search list ([ Clear list ])`.

```text
## **Calculate**                      ← Chunk boundary (contains "Command group")
|Command group|...|
|Calculations|NO|YES|YES|All|
## **Syntax**
Calculate field-name as calculation
## **Description**
...                                   ← all of this belongs to the same chunk
## **Example**
...
## **Do**                             ← next chunk boundary
```

**Metadata per command chunk:**
```json
{
  "source": "CommandRef",
  "command_name": "Calculate",
  "command_group": "Calculations",
  "flag_affected": false,
  "reversible": true,
  "execute_on_client": true,
  "platform": "All",
  "deprecated": false,
  "has_options": false
}
```

#### FunctionRef — Atomic Function Chunking

Same strategy as CommandRef, but with lookahead for `|Function group|`.
Special case `abs()`: this function has no H2 heading in the Markdown
(PDF rendering issue) and is extracted separately as the first chunk.

**Metadata per function chunk:**
```json
{
  "source": "FunctionRef",
  "function_name": "replaceall",
  "function_signature": "replaceall()",
  "function_group": "String",
  "execute_on_client": true,
  "platform": "All",
  "has_example": true
}
```

#### Programming_Omnis — Semantic Section Chunking

Starts at `## **Chapter 2—Libraries and Classes**`. Chapters 1 and 4
are already absent because of page exclusion in `extract.py`.

Each H2 heading starts a new chunk. Chapter headings
(`## **Chapter N—...`) set the chapter context for all following chunks.

Chunks > 700 words are split into 500-word pieces with 50-word overlap.

**Extracted chapters:**

| Chapter | Title | Chunks |
|---|---|---|
| 2 | Libraries and Classes | 107 |
| 3 | Omnis Programming | 140 |
| 5 | Object Oriented Programming | 34 |
| 6 | List Programming | 53 |
| 7 | SQL Programming | 139 |
| 8 | SQL Classes and Notation | 52 |
| 9 | Server-Specific Programming | 216 |
| 10 | Report Programming | 106 |
| 11 | Window Components | 371 |
| 12 | Window Programming | 85 |
| 13-17 | Unicode, Localization, VCS, Migration, Deployment | 223 |

**Metadata per programming chunk:**
```json
{
  "source": "Programming_Omnis",
  "chapter_number": 3,
  "chapter_title": "Omnis Programming",
  "section": "Declaration and Scope",
  "word_count": 187
}
```

### Metadata Prefix in the `text` Field

Each chunk starts with a structured prefix line that embeds metadata directly into the
text being embedded. This gives the embedding model immediate context, even for short chunks.

**Commands:**

```text
Command: Calculate | Group: Calculations | Flag: NO | Reversible: YES | Client: YES | Platform: All

## **Calculate**
...
```

**Functions:**

```text
Function: replaceall() | Group: String | Client: YES | Platform: All

## **replaceall()**
...
```

**Programming:**

```text
Programming_Omnis | Chapter 3: Omnis Programming | Section: Declaration and Scope

## **Declaration and Scope**
...
```

### Uniform Chunk Format

```json
{
  "id": "cmd_calculate",
  "text": "Command: Calculate | Group: Calculations | Flag: NO | ...\n\n## **Calculate**\n...",
  "metadata": { "source": "CommandRef", "command_name": "Calculate", ... }
}
```

**Output:**

| File | Chunks | Avg. Words |
|---|---|---|
| `output/chunks/commands_chunks.json` | 485 | 275 |
| `output/chunks/functions_chunks.json` | 327 | 117 |
| `output/chunks/programming_chunks.json` | 1543 | 152 |

---

## Step 3 — Embedding: `embed_and_store.py`

**Purpose:** Generates embedding vectors for all chunks locally via `sentence-transformers`.

**Run:**
```bash
python3 scripts/embed_and_store.py           # Resume mode (skips already embedded items)
python3 scripts/embed_and_store.py --force   # Re-embed everything (after chunk rebuild)
```

**Configuration** (inside the script):
```python
EMBED_MODEL = "BAAI/bge-m3"   # Model, same as the RAG server
EMBED_DIM   = 1024
BATCH_SIZE  = 64
```

**First run:** Downloads `BAAI/bge-m3` (~2 GB) into `~/.cache/huggingface/`.
Apple Silicon (M-series) uses Metal/MPS automatically and is much faster than x86/CPU.

**Resume support:** The script writes in append mode. If it is interrupted, simply
start it again. Already embedded chunks are detected by ID and skipped.

**Output:** `output/embeddings.jsonl`

Each line:
```json
{
  "id": "cmd_calculate",
  "text": "Command: Calculate | ...\n\n## **Calculate**\n...",
  "metadata": { "source": "CommandRef", ... },
  "embedding": [0.0015, -0.0231, ..., 0.0089]
}
```

---

## Step 4 — Database Setup: `setup_db.sql` + `setup_ranking.sql`

### `setup_db.sql`

This step is required when you use PostgreSQL outside Docker.

**Run on the PostgreSQL host:**
```bash
# 1. As superuser: extensions, roles, schema
psql -U postgres -f setup_db.sql

# 2. Create database (one time)
createdb -U postgres -O rag_owner ragdb

# 3. Tables and functions
psql -U postgres -d ragdb -f setup_db.sql
```

**Adjust passwords** before running:
```sql
CREATE ROLE rag_owner LOGIN PASSWORD 'change_me_owner';
CREATE ROLE rag_app   LOGIN PASSWORD 'change_me_app';
CREATE ROLE rag_ro    LOGIN PASSWORD 'change_me_ro';
```

**Created objects:**

| Object | Type | Description |
|---|---|---|
| `rag.corpus` | Table | Collections (`omnis-commands`, `omnis-functions`, `omnis-programming`) |
| `rag.document` | Table | One row per chunk ID (`external_id`) |
| `rag.chunk` | Table | Chunk text + `tsvector` for BM25 |
| `rag.embedding` | Table | 1024-dim `vector(1024)` |
| `ix_chunk_tsv` | GIN index | BM25 full-text search |
| `ix_embedding_hnsw` | HNSW index | Approximate nearest neighbour |
| `rag.search_hybrid()` | Function | Dense + BM25 via RRF |
| `rag.search_omnis_docs()` | Function | Combines all three corpora |

**Table structure:**
```text
corpus (corpus_id, name, description)
  └── document (document_id, corpus_id, external_id, title, hash_sha256, meta)
        └── chunk (chunk_id, document_id, chunk_index, content, content_tsv, meta)
              └── embedding (chunk_id, model, embedding_dim, v::vector(1024))
```

### `setup_ranking.sql`

**Run after** `setup_db.sql`:
```bash
psql -U postgres -d ragdb -f setup_ranking.sql
```

#### `rag.search_hybrid(query_vec, query_text, corpus_id, top_k, candidate_k, rrf_k)`

Combines dense search and BM25 via **Reciprocal Rank Fusion (RRF)**:

```text
RRF score = 1/(60 + dense_rank) + 1/(60 + bm25_rank)
```

#### `rag.search_omnis_docs(query_vec, query_text, k_commands, k_functions, k_programming)`

Calls `search_hybrid` across all three document corpora. Default: `3+2+4 = 9` chunks total.

### Docker note

If you use `docker_mcp-rag-pg/`, these schema and ranking steps are executed automatically
from `docker_mcp-rag-pg/postgres-init/` on first container startup.

---

## Step 5 — Import: `import_to_postgres.py`

**Purpose:** Reads `embeddings.jsonl` and writes all chunks into PostgreSQL.

**Configuration:** Loaded from `scripts/.env`

**Run:**
```bash
# Configure .env: RAG_DB_HOST, RAG_DB_USER, RAG_DB_PASS
python3 scripts/import_to_postgres.py
```

**Docker PostgreSQL target:**

```bash
python3 scripts/import_to_docker_postgres.py
```

**Corpus mapping:**

| `metadata.source` | PostgreSQL corpus |
|---|---|
| `CommandRef` | `omnis-commands` |
| `FunctionRef` | `omnis-functions` |
| `Programming_Omnis` | `omnis-programming` |

`ON CONFLICT DO UPDATE` is used on all tables, so the import is resumable and idempotent.

**After import — optimize indexes:**

For local/external PostgreSQL:

```sql
VACUUM ANALYZE rag.embedding;
VACUUM ANALYZE rag.chunk;
```

For `docker_mcp-rag-pg/`:

```bash
cd docker_mcp-rag-pg
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.embedding;"
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.chunk;"
```

Run each `VACUUM` in its own command. `VACUUM` cannot run inside a transaction block.

---

## RAG Server: `OmnisRAGServer/rag-server/ragserver.py`

**Purpose:** Local FastAPI server that embeds queries and calls PostgreSQL
hybrid search.

**Installation:**
```bash
cd OmnisRAGServer/rag-server
pip install -r requirements.txt
```

**Configuration `.env`:**
```env
RAG_DB_HOST=192.168.1.xxx
RAG_DB_PORT=5432
RAG_DB_NAME=ragdb
RAG_DB_USER=rag_app
RAG_DB_PASS=your_password
EMBED_MODEL=BAAI/bge-m3
PORT=7071
```

**Start:**
```bash
python ragserver.py
# On first start: downloads bge-m3 (~2 GB, cached once)
# -> Uvicorn running on http://127.0.0.1:7071
```

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Status check (`model`, `status`) |
| `POST` | `/search` | Hybrid search, returns `chunks` + `context_text` |

**Search request:**
```json
{
  "query": "how to iterate over a list in Omnis",
  "k_commands": 3,
  "k_functions": 2,
  "k_programming": 4,
  "corpus": "all"
}
```

---

## MCP Bridge: `OmnisRAGServer/mcp-bridge/mcpserver.mjs`

**Purpose:** stdio MCP bridge for VS Code. It forwards tool calls to the running local `rag-server`.

**Wire format:** NDJSON — one JSON-RPC object per line (`\n` terminated), no `Content-Length` headers.
This is the wire format used by VS Code Copilot for stdio MCP servers (MCP spec, stdio transport).

**VS Code starts the bridge automatically.** No manual start needed. Configuration in `.vscode/mcp.json`:

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

**Important:** start the `rag-server` before opening VS Code, otherwise tool calls will fail
(the bridge initialises successfully without the RAG server, but search requests will error).

For the containerised alternative see the [Docker setup](#docker-setup) section below.

---

## Full Execution Order (Initial Setup)

```bash
# ── Mac: Pipeline ────────────────────────────────────────────
pip install -r scripts/requirements.txt
python3 scripts/extract.py                    # ~2 min
python3 scripts/chunk.py                      # ~5 sec
python3 scripts/embed_and_store.py --force    # ~10 min (one-time, M-series)

# ── PostgreSQL: Database (manual path) ───────────────────────
psql -U postgres -f scripts/setup_db.sql
createdb -U postgres -O rag_owner ragdb
psql -U postgres -d ragdb -f scripts/setup_db.sql
psql -U postgres -d ragdb -f scripts/setup_ranking.sql

# ── Import: local/external PostgreSQL ───────────────────────
python3 import_to_postgres.py
psql -U rag_owner -d ragdb -c 'VACUUM ANALYZE rag.embedding;'
psql -U rag_owner -d ragdb -c 'VACUUM ANALYZE rag.chunk;'

# ── Import: Docker PostgreSQL alternative ───────────────────
python3 scripts/import_to_docker_postgres.py
cd docker_mcp-rag-pg
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.embedding;"
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.chunk;"

# ── Local: Start RAG server ──────────────────────────────────
cd OmnisRAGServer/rag-server
# configure .env
pip install -r requirements.txt
python ragserver.py

# ── Local: Start RAG server (required before VS Code opens) ──
cd OmnisRAGServer/rag-server
source .venv/bin/activate
python ragserver.py
# VS Code starts the MCP bridge automatically via mcp.json
```

---

## Docker Setup

Two Docker variants exist:

- `docker_mcp-rag/`: `mcp-server` + `rag-server`, PostgreSQL stays outside Docker
- `docker_mcp-rag-pg/`: `postgres` + `rag-server` + `mcp-server`, fully containerized

Both expose the MCP server via **Streamable HTTP** (MCP protocol 2025-03-26) instead of stdio.

Full documentation:

- [`docker_mcp-rag/README.md`](../docker_mcp-rag/README.md)
- [`docker_mcp-rag-pg/README.md`](../docker_mcp-rag-pg/README.md)

### What changes compared to the local setup

| Aspect | Local | Docker with host PostgreSQL | Full Docker stack |
| --- | --- | --- | --- |
| MCP server | `mcpserver.mjs` (Node.js, stdio) | `server.py` (Python, HTTP) | `server.py` (Python, HTTP) |
| MCP transport | NDJSON over stdio | Streamable HTTP on port 3000 | Streamable HTTP on port 3000 |
| MCP protocol version | 2024-11-05 | 2025-03-26 | 2025-03-26 |
| RAG server startup | manual | `docker compose up` | `docker compose up` |
| PostgreSQL | local/external | local/external | Docker PG18 + `pgvector` |
| Model cache | `~/.cache/huggingface/` | Docker named volume `hf_cache` | Docker named volume `hf_cache` |
| VS Code config | `"type": "stdio"` | `"type": "http"` | `"type": "http"` |

### Quick start

`docker_mcp-rag/`:

```bash
cd docker_mcp-rag
cp .env.example .env
# fill in RAG_DB_PASS and verify RAG_DB_USER in .env
docker compose up --build
```

`docker_mcp-rag-pg/`:

```bash
cd docker_mcp-rag-pg
cp .env.example .env
docker compose up --build
cd ..
python scripts/import_to_docker_postgres.py
```

VS Code connects to `http://localhost:3000/mcp` using the `omnis-rag-docker` entry
already present in `.vscode/mcp.json`.

### Prerequisites for the Docker setup

- Docker Desktop (Windows / macOS) or Docker Engine + Compose plugin (Linux)
- For `docker_mcp-rag/`: PostgreSQL running on the host machine with `ragdb` already populated,
  plus network access for the Docker subnet
- For `docker_mcp-rag-pg/`: no host PostgreSQL installation required
