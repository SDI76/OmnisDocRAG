# Omnis Studio RAG — Pipeline Documentation

Technical documentation of the path from the Omnis PDFs (and optionally the Omnis doc pack) to the
PostgreSQL database and the MCP tools.

---

## Overview

```text
Omnis PDF/*.pdf  (+ optional doc pack: Omnis 11.1 help as Markdown)
    │  scripts/extract.py        structure from the PDF, content via pymupdf4llm
    ▼
output/extracted/*.json          units: title, heading path, pages, Markdown, metadata
    │  scripts/chunk.py          chunks per corpus (+ notation and 11.1 additions from the doc pack)
    ▼
output/chunks/*_chunks.json
    │  scripts/validate.py       quality gate (exit code 1 on failure)
    │  scripts/embed_and_store.py   BAAI/bge-m3, incremental by text hash
    ▼
output/embeddings.jsonl          (not in git — rebuilt locally)
    │  scripts/import_to_postgres.py / import_to_docker_postgres.py
    ▼
PostgreSQL ragdb (schema rag, v2)
    │  rag-server  (docker_mcp-rag/rag-server/ragserver.py)   /search /chunks /embed /health
    ▼
MCP: docker_mcp-rag/mcp-server/server.py (HTTP)  or  OmnisRAGServer/mcp-bridge/mcpserver.mjs (stdio)
```

| Corpus | Source | Chunks |
|---|---|---|
| `omnis-commands` | CommandRef.pdf, 11.1 additions from the doc pack | 585 |
| `omnis-functions` | FunctionRef.pdf, 11.1 additions from the doc pack | 395 |
| `omnis-programming` | Programming_Omnis.pdf, chapters 1–17 | 1,883 |
| `omnis-notation` | doc pack (optional) | 3,055 |
| **Total** | | **5,918** |

Details of extraction and chunking: [chunking_concept_en.md](chunking_concept_en.md).

---

## Prerequisites

```bash
python3 --version      # >= 3.10
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r scripts/requirements.txt
```

- Model `BAAI/bge-m3` (~2 GB) is downloaded on first local use to `~/.cache/huggingface/`.
- Embedding ~1.7 M tokens takes minutes on a GPU / Apple Silicon (MPS is used automatically) and
  hours on a plain CPU. Alternatively embed through the running rag-server (`--server`), which uses
  the model already cached in its container.
- Optional doc pack: a directory with `catalogs/` and `md/` (built from the Omnis 11.1 HTML help).
  Pass it with `--omnisdoc PATH` or set `OMNISDOC_PACK=PATH` in `scripts/.env.local`.

---

## Project structure

```text
OmnisDocRAG/
├── Omnis PDF/                     CommandRef.pdf, FunctionRef.pdf, Programming_Omnis.pdf
├── scripts/
│   ├── extract.py                 step 1: PDF → units (JSON) + inspection Markdown
│   ├── chunk.py                   step 2: units (+ doc pack) → chunks
│   ├── validate.py                step 3: quality gate
│   ├── embed_and_store.py         step 4: chunks → embeddings.jsonl
│   ├── import_to_postgres.py      step 5: chunks + embeddings → PostgreSQL
│   ├── import_to_docker_postgres.py  step 5 against the Docker PostgreSQL
│   ├── eval_retrieval.py          retrieval regression check (eval_queries.json)
│   ├── test_mcp_rag_bridge.py     end-to-end test of the stdio bridge
│   ├── setup_db.sql / setup_ranking.sql   local PostgreSQL (include the shared SQL)
├── output/
│   ├── extracted/*.json           step 1
│   ├── *_extracted.md             step 1, for reading
│   ├── chunks/*_chunks.json       step 2
│   ├── validation_report.json     step 3
│   └── embeddings.jsonl           step 4 (git-ignored)
├── docker_mcp-rag/                rag-server + mcp-server images (host PostgreSQL)
├── docker_mcp-rag-pg/             full stack: PostgreSQL 18 + pgvector + both servers
│   └── postgres-init/
│       ├── 10-init-ragdb.sh       runs the SQL below once on an empty volume
│       └── sql/                   20 roles, 30 schema, 40 ranking — shared with the local setup
└── OmnisRAGServer/
    ├── rag-server/ragserver.py    local start wrapper around docker_mcp-rag/rag-server/ragserver.py
    └── mcp-bridge/mcpserver.mjs   stdio MCP bridge
```

---

## Step 1 — Extraction (`extract.py`)

```bash
python scripts/extract.py                      # all sources
python scripts/extract.py CommandRef           # one source
```

Prints per source the number of units and warnings (e.g. "title line synthesised" when a title was
rendered inside a table). Output in `output/extracted/` and `output/*_extracted.md`.

## Step 2 — Chunking (`chunk.py`)

```bash
python scripts/chunk.py --omnisdoc /path/to/omnisdoc     # or OMNISDOC_PACK in scripts/.env.local
python scripts/chunk.py                                  # without doc pack: no notation, no 11.1 additions
```

## Step 3 — Validation (`validate.py`)

```bash
python scripts/validate.py --omnisdoc /path/to/omnisdoc
```

Stops the build (exit code 1) when entries are missing, code lines became titles, ligature damage
is left, or chunks are empty/oversized. Prints the doc pack cross-check.

## Step 4 — Embedding (`embed_and_store.py`)

```bash
python scripts/embed_and_store.py                               # local model (MPS/CUDA/CPU)
python scripts/embed_and_store.py --threads 12                  # CPU: use all cores
python scripts/embed_and_store.py --server http://localhost:7071   # via the running rag-server
python scripts/embed_and_store.py --force                       # re-embed everything
```

- Embeds `embed_text` (context line + chunk text), normalised, 1024 dimensions.
- Incremental: only chunks whose text hash changed are embedded again; progress is saved every 10
  batches, so an interrupted run continues where it stopped.
- `--max-seq-length` (default 512 tokens) limits the embedded length of the longest chunks.

## Step 5 — Import

```bash
python scripts/import_to_postgres.py            # RAG_DB_* from scripts/.env
python scripts/import_to_docker_postgres.py     # reads docker_mcp-rag-pg/.env
```

- Refuses to run if an embedding is missing or stale (hash check).
- One transaction: upsert of documents, chunks (title, heading path, symbols, content) and
  embeddings; the full-text vector is built by a trigger; documents that no longer exist are deleted
  (`DELETE_STALE_DOCS=0` disables that).

---

## Database

Schema and ranking live in `docker_mcp-rag-pg/postgres-init/sql/` and are used by both setups:

- Docker: `10-init-ragdb.sh` runs `sql/20…`, `sql/30…`, `sql/40…` once on an empty volume.
- Local: `scripts/setup_db.sql` (roles, then schema via `\ir`) and `scripts/setup_ranking.sql`.

Both SQL files are idempotent; `30-rag-schema.sql` migrates a v1 database. See
[postgres_en.md](postgres_en.md).

---

## Runtime

### rag-server

| Endpoint | Purpose |
|---|---|
| `GET /health` | model and chunk count per corpus |
| `POST /search` | `{query, mode: hybrid\|semantic\|fulltext, top_k, corpora, format: text\|json}` |
| `POST /chunks` | `{ids: [...], format}` — full text of results |
| `POST /embed` | `{texts: [...]}` — embeddings with the server's model |

Tuning via environment: `RAG_W_DENSE` (1.0), `RAG_W_FTS` (0.5), `RAG_SNIPPET_CHARS` (240).

### MCP tools (identical in the Docker server and the stdio bridge)

| Tool | Use |
|---|---|
| `search_omnis_docs` | ranked search over all corpora; `mode`, `top_k`, `corpus` |
| `get_omnis_doc` | full text of result ids |
| `search_omnis_syntax` | search restricted to commands, functions, notation |
| `search_omnis_concepts` | search restricted to the Programming manual (`deep` = 15 hits) |

A search answer is plain text: one line per hit with corpus, title or heading path, source with
pages, id, and a snippet — typically 2–4 KB.

---

## Full rebuild

```bash
source .venv/bin/activate
python scripts/extract.py
python scripts/chunk.py --omnisdoc /path/to/omnisdoc
python scripts/validate.py --omnisdoc /path/to/omnisdoc
python scripts/embed_and_store.py            # or --server http://localhost:7071
python scripts/import_to_docker_postgres.py  # or import_to_postgres.py
python scripts/eval_retrieval.py --compare
```

Schema changes on an existing Docker volume: either recreate the PostgreSQL volume
(`docker compose rm -sf postgres && docker volume rm docker_mcp-rag-pg_postgres_data && docker compose up -d`,
the model cache volume stays) or run `sql/30…` and `sql/40…` against the database as `postgres`.
