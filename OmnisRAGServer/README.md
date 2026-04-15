# Omnis RAG Server / MCP Bridge — Contract

## Purpose

This layer makes agentic access easier without changing the underlying database or embeddings.

The runtime consists of two parts:

- `rag-server`: local HTTP retrieval server against PostgreSQL
- `mcp-bridge`: stdio MCP bridge for VS Code that forwards requests to `rag-server`

The `mcp-bridge` depends on the `rag-server` and must be started after it.

Containerised alternatives with Streamable HTTP transport are available in:

- [`docker_mcp-rag/`](../docker_mcp-rag/README.md) for Docker MCP/RAG with PostgreSQL on the host
- [`docker_mcp-rag-pg/`](../docker_mcp-rag-pg/README.md) for the full Docker stack with PostgreSQL 18 + `pgvector`

## Available Tools

### 1) `search_omnis_syntax`

- For signature, parameter, and command questions
- Default: `mode=syntax`
- Optional: `k_commands`, `k_functions`

### 2) `search_omnis_concepts`

- For pattern, design, and best-practice questions
- Default: `mode=concept`
- Optional: `deep=true` (mapped to `mode=deep`)
- Optional: `k_programming`

### 3) `search_omnis_docs`

- Expert mode, compatible with the current V1 behavior
- Full access to `mode`, `corpus`, and `k_*`

## Response Standard

Each tool returns:

- `query`
- `query_original`
- `query_effective`
- `query_language`
- `rewrite_applied`
- `retrieval_mode`
- `effective_retrieval`
- `chunk_count`
- `sources`
- `context_text`
- `chunks`
- optional `guidance.next_query`

## Policy

- Select the tool based on the question type, not random prompt wording.
- For unclear questions, start with `search_omnis_concepts`, then follow up with a more focused syntax query.
- Always return `effective_retrieval` for debugging transparency.

## Language Options

All three tools optionally support:

- `query_language`: `auto` | `de` | `en`
- `query_en`: explicit English retrieval-query override

Behavior:

- With `query_language=auto` and detected German queries, the bridge attempts a light DE -> EN normalization to improve hits on English corpora.
- With `query_en`, a manually written English retrieval query can be forced.

## Startup

### 1. Start the RAG server

Make sure the local RAG server is running on:

```text
http://127.0.0.1:7071
```

```bash
cd OmnisDocRAG/OmnisRAGServer/rag-server
source .venv/bin/activate
python ragserver.py
```

### 2. Start the MCP bridge

The bridge is started automatically by VS Code when the workspace is opened.
It does not need to be started manually.

### 3. Register in VS Code

`.vscode/mcp.json` in the workspace root:

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

## Wire Format

`mcpserver.mjs` uses **NDJSON** (newline-delimited JSON) as the wire format —
one JSON-RPC object per line, no `Content-Length` headers.
This matches the MCP stdio transport specification and how VS Code Copilot
communicates with stdio MCP servers.

## Example Calls

- `example-tool-call-syntax.json`
- `example-tool-call-concepts.json`
- `example-tool-call-docs.json`

## Implementation Status

- `mcpserver.mjs` is operational (Node.js, NDJSON wire format, MCP 2024-11-05).
- For the containerised setup with Streamable HTTP transport see [`docker_mcp-rag/`](../docker_mcp-rag/README.md) or [`docker_mcp-rag-pg/`](../docker_mcp-rag-pg/README.md).
