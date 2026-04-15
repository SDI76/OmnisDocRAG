# OmnisDocRAG

Local RAG stack for Omnis Studio documentation — extracts PDF manuals, chunks and embeds them, stores them in PostgreSQL with `pgvector`, and exposes them as MCP tools to VS Code for AI-assisted Omnis development.

---

## Quick orientation

Start here: [Project_instructions.md](Project_instructions.md)

It covers the project goal, directory layout, setup steps, runtime startup order, and the available topologies for local and Docker-based operation.

---

## Documentation index

| Document | What it covers |
|---|---|
| [Project_instructions.md](Project_instructions.md) | Entry point — setup, startup order, quick-start commands |
| [Documentation/RAG_concept_en.md](Documentation/RAG_concept_en.md) | Why RAG, how retrieval works, architecture overview |
| [Documentation/Pipeline_en.md](Documentation/Pipeline_en.md) | Full data-build pipeline (extract → chunk → embed → import) |
| [Documentation/chunking_concept_en.md](Documentation/chunking_concept_en.md) | How chunks are structured and why |
| [Documentation/embedding_concept_en.md](Documentation/embedding_concept_en.md) | Embedding model, dimensions, and storage |
| [Documentation/postgres_en.md](Documentation/postgres_en.md) | Database schema, `pgvector` setup, indexing |
| [Documentation/expected_outcome_en.md](Documentation/expected_outcome_en.md) | What a working system looks like end-to-end |
| [OmnisRAGServer/README.md](OmnisRAGServer/README.md) | Local stdio MCP bridge contract and tool reference |
| [docker_mcp-rag/README.md](docker_mcp-rag/README.md) | Docker stack — `mcp-server` + `rag-server`, using PostgreSQL on the host |
| [docker_mcp-rag-pg/README.md](docker_mcp-rag-pg/README.md) | Full Docker stack — PostgreSQL 18 + `pgvector` + `rag-server` + `mcp-server` |

---

## Three runtime topologies

**Local** — Python RAG server + Node.js stdio MCP bridge:

```
VS Code (stdio) → mcp-bridge (Node.js) → rag-server (Python) → PostgreSQL
```

**Docker with host PostgreSQL** — containerised MCP/RAG runtime, DB remains outside Docker:

```
VS Code (HTTP) → mcp-server (Python, port 3000) → rag-server (Python, port 7071) → PostgreSQL
```

**Full Docker stack** — PostgreSQL 18 + `pgvector` inside Docker:

```
VS Code (HTTP) → mcp-server (Python, port 3000) → rag-server (Python, port 7071) → postgres (Docker, PG18 + pgvector)
```

For existing local database setups, see [docker_mcp-rag/README.md](docker_mcp-rag/README.md).
For the most portable out-of-the-box setup, see [docker_mcp-rag-pg/README.md](docker_mcp-rag-pg/README.md).

---

## MCP tools exposed

| Tool | Use for |
|---|---|
| `search_omnis_syntax` | Command signatures, function parameters, strict syntax |
| `search_omnis_concepts` | Patterns, architecture, best practices |
| `search_omnis_docs` | General documentation questions, mixed queries |

For setup, runtime selection, and MCP wiring details, see [Project_instructions.md](Project_instructions.md).

---

## Minimum quick start (Full Docker stack)

```bash
# 1. Build the data (once)
source .venv/bin/activate
python scripts/extract.py && python scripts/chunk.py
python scripts/embed_and_store.py

# 2. Start the stack
cd docker_mcp-rag-pg
cp .env.example .env   # then edit DB credentials
docker compose up --build

# 3. Import into the Docker PostgreSQL
cd ..
python scripts/import_to_docker_postgres.py

# 4. VS Code — .vscode/mcp.json
# { "omnis-rag-docker": { "type": "http", "url": "http://localhost:3000/mcp" } }
```

If you want Docker only for `mcp-server` and `rag-server` while keeping PostgreSQL on the host,
use [docker_mcp-rag/README.md](docker_mcp-rag/README.md) instead.
