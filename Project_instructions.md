# OmnisDocRAG — Project Instructions

This document is the short entry point for developers. It explains the actual runtime layout, the correct startup order, and where to find the detailed documentation.

---

## Goal

`OmnisDocRAG` provides a local RAG stack for Omnis Studio documentation:

- extract Omnis PDF manuals into Markdown
- split them into structured chunks
- embed the chunks locally
- import them into PostgreSQL with `pgvector`
- run a local HTTP `rag-server` for retrieval
- expose MCP tools to VS Code via the stdio-based `mcp-bridge`

The project is built around three corpora:

- `omnis-commands` from `CommandRef.pdf`
- `omnis-functions` from `FunctionRef.pdf`
- `omnis-programming` from `Programming_Omnis.pdf`

---

## Actual Project Structure

```text
OmnisDocRAG/
├── Documentation/              Concepts, architecture, pipeline docs
├── Omnis PDF/                  Source PDFs
├── output/                     Extracted Markdown, chunks, embeddings
├── scripts/                    Extraction, chunking, embedding, DB import
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

---

## Setup

### Fastest setup

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

Use:

- `scripts/setup_db.sql`
- `scripts/setup_ranking.sql`

Schema details: [Documentation/postgres_en.md](/Users/stefan/Library/Mobile Documents/com~apple~CloudDocs/07. DevOps/Omnisdocumentation/OmnisDocRAG/Documentation/postgres_en.md)

---

## Standard Data Build Workflow

Run these from the project root after activating the pipeline virtual environment:

```bash
python scripts/extract.py
python scripts/chunk.py
python scripts/embed_and_store.py
python scripts/import_to_postgres.py
```

What each step does:

1. `extract.py` converts PDFs to Markdown.
2. `chunk.py` creates JSON chunk files in `output/chunks/`.
3. `embed_and_store.py` creates `output/embeddings.jsonl`.
4. `import_to_postgres.py` upserts the data into PostgreSQL.

If chunk content changes, rebuild embeddings with:

```bash
python scripts/embed_and_store.py --force
```

---

## Runtime Startup Order

This part is important:

1. PostgreSQL must already contain the imported embeddings.
2. `rag-server` must be running first.
3. `mcp-bridge` starts after that and forwards requests to `rag-server`.

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

### VS Code MCP configuration

Example local stdio registration:

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

---

## Important Notes

- Work only inside `OmnisDocRAG` for this finalized project copy.
- Keep German originals in `Documentation/` and add English versions as separate `_en` files.
- Treat `output/` as generated artifacts.
- `embed_and_store.py` uses local `sentence-transformers` with `BAAI/bge-m3`, which downloads a large model on first run.
- `scripts/import_to_postgres.py` reads database environment values from `scripts/.env`.
- The runtime topology is now `rag-server -> mcp-bridge -> VS Code`.

---

## Quick Start

```bash
cd OmnisDocRAG
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/extract.py
python scripts/chunk.py
python scripts/embed_and_store.py
python scripts/import_to_postgres.py

cd OmnisRAGServer/rag-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ragserver.py

# in a second terminal
cd OmnisRAGServer/mcp-bridge
node mcpserver.mjs
```

If you are new to the codebase, read `RAG_KONZEPT_en.md` first, then `Pipeline_en.md`, then `OmnisRAGServer/README.md`.
