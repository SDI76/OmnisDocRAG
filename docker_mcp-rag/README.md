# docker_mcp-rag — Containerised Omnis RAG Stack

This folder contains the Docker setup for running the Omnis RAG stack as containers, with
PostgreSQL on the host. Its `rag-server/` and `mcp-server/` folders are the source of both services —
`docker_mcp-rag-pg/` builds from them, and the local start script `OmnisRAGServer/rag-server/ragserver.py`
runs `rag-server/ragserver.py`.

---

## What is in this folder

```text
docker_mcp-rag/
├── mcp-server/
│   ├── server.py          MCP server — Python FastMCP, Streamable HTTP
│   ├── requirements.txt   mcp pinned below 2.0 (2.x renamed FastMCP)
│   └── Dockerfile
├── rag-server/
│   ├── ragserver.py       RAG retrieval server (FastAPI) — the only copy of the server code
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml     Orchestrates both services
├── .env.example           Configuration template
└── README.md              This file
```

---

## What does the RAG server actually access?

The `rag-server` container needs two external resources at runtime:

### 1. PostgreSQL with pgvector (`ragdb`)

The RAG server connects to PostgreSQL and runs `rag.search_ranked` (semantic + weighted full text +
exact-name boost, one ranking across all corpora) against the `rag` schema. The following tables must already be populated before starting:

| Table | Content |
|---|---|
| `rag.corpus` | The document collections (commands, functions, programming, notation) |
| `rag.document` | One row per chunk, with source metadata |
| `rag.chunk` | Chunk text, title, heading path, symbol names, weighted `tsvector` |
| `rag.embedding` | 1024-dimensional `vector(1024)` per chunk |

The database is set up and populated by the pipeline scripts in the main project.
See [`Documentation/Pipeline_en.md`](../Documentation/Pipeline_en.md) for the full process
and [`Documentation/postgres_en.md`](../Documentation/postgres_en.md) for the schema details.

The Docker container connects to your **host machine's PostgreSQL** (not a containerised DB).
`host.docker.internal` is resolved to the host's IP via the `extra_hosts` setting in
`docker-compose.yml`. PostgreSQL must be configured to accept connections from the Docker
subnet (see [PostgreSQL configuration](#postgresql-configuration) below).

### 2. BAAI/bge-m3 embedding model

At startup, the RAG server loads `BAAI/bge-m3` via `sentence-transformers`.
The model is ~2.2 GB and is downloaded from HuggingFace on the first run. The server also offers
`POST /embed`, so `scripts/embed_and_store.py --server http://localhost:7071` can build the document
embeddings with this cached model.

To avoid downloading it every time:
- The Docker Compose setup uses a **named volume** (`hf_cache`) that persists the model
  across container restarts and rebuilds.
- If you already have the model cached locally at `~/.cache/huggingface/`, you can mount
  that directory instead (see the comment in `docker-compose.yml`).

---

## Architecture

```text
┌─────────────────────────────────────────────────┐
│  docker-compose                                   │
│                                                   │
│  ┌──────────────────┐   HTTP    ┌──────────────┐ │
│  │  mcp-server      │ ────────► │  rag-server  │ │
│  │  Python FastMCP  │ :7071     │  FastAPI     │ │
│  │  port 3000       │           │  port 7071   │ │
│  └────────┬─────────┘           └──────┬───────┘ │
│           │                            │         │
└───────────┼────────────────────────────┼─────────┘
            │ HTTP /mcp                  │ TCP
            │ (Streamable HTTP)          │ PostgreSQL + bge-m3
            ▼                            ▼
     VS Code Copilot             Host machine
     (MCP client)                (PostgreSQL on port 5432)
```

**MCP transport:** Streamable HTTP (MCP protocol 2025-03-26)
VS Code connects to `http://localhost:3000/mcp` using `"type": "http"` in `mcp.json`.

---

## Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + Compose plugin (Linux)
- PostgreSQL running on the host machine with the `ragdb` database populated
- Internet access for the first model download (HuggingFace CDN)

---

## Configuration

### 1. Create `.env`

```bash
cp .env.example .env
```

Open `.env` and fill in the database credentials:

```env
RAG_DB_HOST=host.docker.internal   # leave as-is — Docker resolves this to the host IP
RAG_DB_PORT=5432
RAG_DB_NAME=ragdb
RAG_DB_USER=rag_app
RAG_DB_PASS=your_actual_password   # required
EMBED_MODEL=BAAI/bge-m3
RAG_PORT=7071
MCP_PORT=3000
```

`RAG_DB_HOST` should stay `host.docker.internal`. Docker Compose resolves this to the
host machine's IP automatically via the `extra_hosts: host.docker.internal:host-gateway`
setting. You never need to hardcode the host IP.

### 2. PostgreSQL configuration

The `rag-server` container connects from a Docker subnet (typically `172.17.x.x` or
`172.18.x.x`). PostgreSQL must allow these connections.

**`postgresql.conf`** — let PostgreSQL listen on all interfaces:
```
listen_addresses = '*'
```

**`pg_hba.conf`** — allow connections from the Docker subnet:
```
host    ragdb    rag_app    172.0.0.0/8    md5
```

Restart PostgreSQL after these changes.

---

## Start

```bash
cd docker_mcp-rag
docker compose up --build
```

On the **first start**:
1. Docker builds both images (~2–4 min)
2. `rag-server` downloads `BAAI/bge-m3` (~2.2 GB, stored in the `hf_cache` volume)
3. `rag-server` connects to PostgreSQL and signals ready
4. `mcp-server` starts after the `rag-server` health check passes (the health check allows 5 minutes
   for loading the model on a busy CPU)

On **subsequent starts** the model is loaded from the volume and the stack is up in ~30 s.

**Background:**
```bash
docker compose up -d
```

**Logs:**
```bash
docker compose logs -f
docker compose logs -f rag-server
docker compose logs -f mcp-server
```

**Stop:**
```bash
docker compose down
```

---

## Connect VS Code

The `.vscode/mcp.json` in the workspace root already contains the entry:

```json
{
  "omnis-rag-docker": {
    "type": "http",
    "url": "http://localhost:3000/mcp"
  }
}
```

Start the stack with `docker compose up`, then restart the MCP server in VS Code
(**MCP: Restart Server**). The server `omnis-rag-docker` should connect immediately.

---

## Available Tools

The tools call the RAG server (`/search`, `/chunks`) and return compact plain text; the
rag-server does all ranking and rendering.

| Tool | Scope | Use for |
|---|---|---|
| `search_omnis_docs` | all corpora (`corpus` to restrict) | Ranked search; `mode` = hybrid \| semantic \| fulltext, `top_k` |
| `get_omnis_doc` | — | Full text of result ids |
| `search_omnis_syntax` | commands, functions, notation | Signatures, parameters, properties, methods |
| `search_omnis_concepts` | Programming manual | Patterns, architecture; `deep=true` → 15 hits |

See [`OmnisRAGServer/README.md`](../OmnisRAGServer/README.md) for the response format.

---

## Updating ragserver.py

`rag-server/ragserver.py` is the only copy of the server code. The local start script
`OmnisRAGServer/rag-server/ragserver.py` runs this file. After changes:

```bash
docker compose build rag-server && docker compose up -d rag-server
```

---

## Relation to the local development setup

| | Local setup | Docker setup |
|---|---|---|
| MCP transport | stdio NDJSON | Streamable HTTP (MCP 2025-03-26) |
| MCP server | `OmnisRAGServer/mcp-bridge/mcpserver.mjs` (Node.js) | `docker_mcp-rag/mcp-server/server.py` (Python) |
| RAG server | started manually | managed by Docker Compose |
| Model cache | `~/.cache/huggingface/` | Docker named volume `hf_cache` |
| VS Code config | `"type": "stdio"` | `"type": "http"` |

Both setups share the same PostgreSQL database and use the same `BAAI/bge-m3` model.
The local setup is documented in [`OmnisRAGServer/README.md`](../OmnisRAGServer/README.md)
and [`Documentation/Pipeline_en.md`](../Documentation/Pipeline_en.md).
