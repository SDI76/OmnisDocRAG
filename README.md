# OmnisDocRAG

Local RAG stack for Omnis Studio documentation — extracts PDF manuals, chunks and embeds them, stores them in PostgreSQL with `pgvector`, and exposes them as MCP tools to VS Code for AI-assisted Omnis development.

---

## Quick orientation

Start here: [Project_instructions.md](Project_instructions.md)

It covers the project goal, directory layout, setup steps, runtime startup order, and both available topologies (local and Docker).

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
| [docker_mcp-rag/README.md](docker_mcp-rag/README.md) | Docker stack — config, startup, VS Code wiring |

---

## Two runtime topologies

**Local** — Python RAG server + Node.js stdio MCP bridge:

```
VS Code (stdio) → mcp-bridge (Node.js) → rag-server (Python) → PostgreSQL
```

**Docker** — fully containerised, Streamable HTTP:

```
VS Code (HTTP) → mcp-server (Python, port 3000) → rag-server (Python, port 7071) → PostgreSQL
```

The Docker variant is recommended for day-to-day use. See [docker_mcp-rag/README.md](docker_mcp-rag/README.md) for setup details.

---

## MCP tools exposed

| Tool | Use for |
|---|---|
| `search_omnis_syntax` | Command signatures, function parameters, strict syntax |
| `search_omnis_concepts` | Patterns, architecture, best practices |
| `search_omnis_docs` | General documentation questions, mixed queries |

For guidance on how a coding agent should use these tools, see the **Agentic Programming** section in [Project_instructions.md](Project_instructions.md).

---

## Minimum quick start (Docker)

```bash
# 1. Build the data (once)
source .venv/bin/activate
python scripts/extract.py && python scripts/chunk.py
python scripts/embed_and_store.py && python scripts/import_to_postgres.py

# 2. Start the stack
cd docker_mcp-rag
cp .env.example .env   # then edit DB credentials
docker compose up --build

# 3. VS Code — .vscode/mcp.json
# { "omnis-rag-docker": { "type": "http", "url": "http://localhost:3000/mcp" } }
```
