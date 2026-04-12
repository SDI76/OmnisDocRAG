# Omnis RAG Server / MCP Bridge — Contract

## Purpose

This layer makes agentic access easier without changing the underlying database or embeddings.

The runtime now consists of two parts:

- `rag-server`: local HTTP retrieval server against PostgreSQL
- `mcp-bridge`: stdio MCP bridge for VS Code that forwards requests to `rag-server`

The `mcp-bridge` depends on the `rag-server` and must be started after it.

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

Example:

```bash
cd OmnisDocRAG/OmnisRAGServer/rag-server
python ragserver.py
```

### 2. Start the MCP bridge

```bash
export OMNIS_RAG_SERVER_URL=http://127.0.0.1:7071
cd OmnisDocRAG/OmnisRAGServer/mcp-bridge
node mcpserver.mjs
```

### 3. Register in VS Code

Use a separate MCP server definition for this bridge if you want to keep older variants untouched.

Example configuration:

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

## Example Calls

- `example-tool-call-syntax.json`
- `example-tool-call-concepts.json`
- `example-tool-call-docs.json`

## Implementation Status

- `mcpserver.mjs` is operational and uses the existing `/search` endpoint of the `rag-server`.
