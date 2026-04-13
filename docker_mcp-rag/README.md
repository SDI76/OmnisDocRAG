# docker_mcp-rag — Containerised Omnis RAG Stack

This folder contains the Docker setup for running the Omnis RAG stack as containers.
It is a self-contained copy, independent of the local development setup in `OmnisRAGServer/`.

---

## What is in this folder

```text
docker_mcp-rag/
├── mcp-server/
│   ├── server.py          MCP server — Python, Streamable HTTP, MCP 2025-03-26
│   ├── requirements.txt
│   └── Dockerfile
├── rag-server/
│   ├── ragserver.py       RAG retrieval server — copy of OmnisRAGServer/rag-server/
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

The RAG server connects to PostgreSQL and runs hybrid search (dense vector + BM25/full-text)
against the `rag` schema. The following tables must already be populated before starting:

| Table | Content |
|---|---|
| `rag.corpus` | The three document collections |
| `rag.document` | One row per chunk, with source metadata |
| `rag.chunk` | Chunk text + `tsvector` for full-text search |
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
The model is ~1.1 GB and is downloaded from HuggingFace on the first run.

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
2. `rag-server` downloads `BAAI/bge-m3` (~1.1 GB, stored in the `hf_cache` volume)
3. `rag-server` connects to PostgreSQL and signals ready
4. `mcp-server` starts after the `rag-server` health check passes

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

All three tools call the RAG server's `/search` endpoint and return structured JSON
with chunks, context text, and retrieval metadata.

| Tool | Default corpus | Use for |
|---|---|---|
| `search_omnis_syntax` | all | Exact command signatures, function parameters, syntax |
| `search_omnis_concepts` | omnis-programming | Patterns, architecture, best practices |
| `search_omnis_docs` | all | General documentation questions |

All tools accept optional overrides: `corpus`, `k_commands`, `k_functions`, `k_programming`.
`search_omnis_concepts` also accepts `deep=true` for more thorough retrieval.

---

## Updating ragserver.py

`rag-server/ragserver.py` is a copy of `OmnisRAGServer/rag-server/ragserver.py`.
If you make changes to the original, copy the file again before rebuilding:

```bash
cp ../OmnisRAGServer/rag-server/ragserver.py rag-server/ragserver.py
cp ../OmnisRAGServer/rag-server/requirements.txt rag-server/requirements.txt
docker compose build rag-server
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
