# Omnis RAG Server / MCP Bridge — Contract

## Purpose

The runtime consists of two parts:

- `rag-server`: HTTP retrieval server against PostgreSQL. The code lives in
  `docker_mcp-rag/rag-server/ragserver.py`; `OmnisRAGServer/rag-server/ragserver.py` is a thin wrapper
  that starts it with the `.env` next to the wrapper.
- `mcp-bridge`: stdio MCP bridge for VS Code that forwards tool calls to `rag-server`.

The bridge depends on the rag-server and must be able to reach it.

Containerised alternatives with Streamable HTTP transport offer the same tools:

- [`docker_mcp-rag/`](../docker_mcp-rag/README.md) — Docker MCP/RAG with PostgreSQL on the host
- [`docker_mcp-rag-pg/`](../docker_mcp-rag-pg/README.md) — full Docker stack with PostgreSQL 18 + `pgvector`

## Tools

| Tool | Arguments | Purpose |
|---|---|---|
| `search_omnis_docs` | `query`, `mode` = hybrid \| semantic \| fulltext, `top_k` (8), `corpus` = all \| commands \| functions \| programming \| notation | ranked search over the documentation |
| `get_omnis_doc` | `ids` (up to 20) | full text of search results |
| `search_omnis_syntax` | `query`, `top_k`, `mode` | search in commands, functions, notation |
| `search_omnis_concepts` | `query`, `top_k`, `deep`, `mode` | search in the Programming manual; `deep=true` → 15 hits |

Queries may be English or German; exact names (`mid()`, `$search`, `#ERRCODE`,
`Begin reversible block`) are recognised and ranked first. In `fulltext` mode the query supports
`"exact phrase"`, `OR` and `-exclusion`.

## Response format

Plain text, no JSON wrapper:

```text
Omnis documentation — 8 results for "set the current line of a list" (hybrid):
1. [notation] List properties ($colcount … $smartlist) — Omnis help 11.1 — id: not_list_properties_1
   - `$line` — The current line in the list This changes when the user clicks on a list line …
2. [command] Set current list — CommandRef p.270 — id: cmd_set_current_list
   …
Full text: get_omnis_doc with one or more ids.
```

`get_omnis_doc` returns each chunk with a header line (`[id] title — source — other parts: …`)
followed by its Markdown text.

## Startup

### 1. Start the RAG server

```bash
cd OmnisDocRAG/OmnisRAGServer/rag-server
source .venv/bin/activate          # dependencies: requirements.txt
python ragserver.py                # http://127.0.0.1:7071
```

### 2. Register the bridge in VS Code

`.vscode/mcp.json` in the workspace root — VS Code starts the bridge itself:

```json
{
  "omnis-rag-local": {
    "type": "stdio",
    "command": "node",
    "args": ["${workspaceFolder}/OmnisRAGServer/mcp-bridge/mcpserver.mjs"],
    "env": { "OMNIS_RAG_SERVER_URL": "http://127.0.0.1:7071" }
  }
}
```

## Wire format

`mcpserver.mjs` uses newline-delimited JSON-RPC (one object per line, no `Content-Length`
headers), as specified for the MCP stdio transport.

## Tests and examples

- `python scripts/test_mcp_rag_bridge.py` — end-to-end test of the bridge against a running rag-server
- `example-tool-call-*.json` — example `tools/call` requests
