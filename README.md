# OmnisDocRAG

Local RAG stack for the Omnis Studio documentation — extracts the PDF manuals (and optionally the
notation reference from the Omnis help), chunks and embeds them, stores them in PostgreSQL with
`pgvector`, and exposes semantic and full-text search as MCP tools for AI-assisted Omnis development.

---

## Quick orientation

Start here: [Project_instructions.md](Project_instructions.md)

It covers the project goal, directory layout, setup steps, runtime startup order, and the available
topologies for local and Docker-based operation.

---

## Documentation index

| Document | What it covers |
|---|---|
| [Project_instructions.md](Project_instructions.md) | Entry point — setup, startup order, quick-start commands |
| [Documentation/RAG_concept_en.md](Documentation/RAG_concept_en.md) | Why RAG, how retrieval works, architecture overview |
| [Documentation/Pipeline_en.md](Documentation/Pipeline_en.md) | Data build pipeline (extract → chunk → validate → embed → import), endpoints, tools |
| [Documentation/chunking_concept_en.md](Documentation/chunking_concept_en.md) | How the PDFs are extracted and chunked, and why |
| [Documentation/embedding_concept_en.md](Documentation/embedding_concept_en.md) | Embedding model, dimensions, and storage |
| [Documentation/postgres_en.md](Documentation/postgres_en.md) | Database schema, full-text vector, `rag.search_ranked` |
| [Documentation/expected_outcome_en.md](Documentation/expected_outcome_en.md) | What a working system looks like end-to-end |
| [Documentation/retrieval_quality_analysis_en.md](Documentation/retrieval_quality_analysis_en.md) | Retrieval quality analysis, measurements before/after the rework |
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

---

## What is indexed

| Corpus | Source | Chunks |
|---|---|---|
| `omnis-commands` | Command Reference (every command, overview sections, error code tables) | 585 |
| `omnis-functions` | Function Reference | 395 |
| `omnis-programming` | Programming manual, all 17 chapters | 1,883 |
| `omnis-notation` | Notation reference from the Omnis 11.1 help (optional doc pack) | 3,055 |

## MCP tools

| Tool | Use for |
|---|---|
| `search_omnis_docs` | Ranked search over everything. `mode`: `hybrid` (default), `semantic`, `fulltext` (supports `"phrase"`, `OR`, `-word`) |
| `get_omnis_doc` | Full text of result ids (second step) |
| `search_omnis_syntax` | Same search, only commands, functions, notation |
| `search_omnis_concepts` | Same search, only the Programming manual |

Search answers are compact text (one line + snippet per hit, typically 2–4 KB); the full text is
fetched only for the ids that matter.

---

## Minimum quick start (Full Docker stack)

Works the same on macOS, Windows and Linux (`python3` / `py` instead of `python` where needed).

```bash
# 1. Set up and check the machine
python scripts/pipeline.py setup
python scripts/pipeline.py doctor        # shows whether embedding runs on GPU/Apple Silicon (minutes) or CPU (hours)

# 2. Start the stack
cd docker_mcp-rag-pg
cp .env.example .env   # then edit DB credentials
docker compose up -d --build
cd ..

# 3. Build, import and check (optional doc pack: OMNISDOC_PACK in scripts/.env.local)
python scripts/pipeline.py build

# 4. VS Code — .vscode/mcp.json
# { "omnis-rag-docker": { "type": "http", "url": "http://localhost:3000/mcp" } }
```

If you want Docker only for `mcp-server` and `rag-server` while keeping PostgreSQL on the host,
use [docker_mcp-rag/README.md](docker_mcp-rag/README.md) instead.
