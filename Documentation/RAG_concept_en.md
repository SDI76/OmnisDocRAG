# RAG Concept: Omnis Studio Documentation

## Goal

Omnis Studio is a proprietary niche language; language models know little of its commands, functions
and notation and produce plausible-looking but wrong code. This project turns the Omnis documentation
into a searchable knowledge base that coding agents query through MCP before they write Omnis code.

Requirements:

- **complete** — every command, function, notation member and manual section that the sources contain
- **searchable by meaning and by words** — questions in English or German, exact names, phrases
- **cheap per call** — compact answers; full text only on demand
- **local** — no cloud API, reproducible from the files in this repository (+ optional doc pack)

---

## Sources

| Source | Content | Omnis version |
|---|---|---|
| `CommandRef.pdf` (357 pages, 508 bookmarks) | every 4GL command with metadata table, syntax, options, description, example; overview sections, error codes | Studio 11 (rev. 35659) |
| `FunctionRef.pdf` (157 pages, no bookmarks) | every function with metadata table, syntax, description, example | Studio 11 (rev. 35659) |
| `Programming_Omnis.pdf` (614 pages, 17 chapters, no bookmarks) | concepts and patterns: libraries, variables, methods, OOP, lists, SQL, reports, windows, localization, VCS, deployment | Studio 11 |
| Omnis doc pack (optional) | Markdown built from the Omnis 11.1 help: commands, functions, **notation** (1,121 nodes) | 11.1 |

The PDFs are the files Omnis shipped (FunctionRef and Programming re-saved because the originals were
hard to read). The notation reference — which properties and methods an object has — exists only in
the Omnis help, not in the PDFs; the doc pack adds it.

---

## Corpora

| Corpus | Chunk unit | Metadata |
|---|---|---|
| `omnis-commands` | one command (+ overview and error-code sections) | group, flag affected, reversible, execute on client, platform, deprecated, pages |
| `omnis-functions` | one function | group, execute on client, platform, pages |
| `omnis-programming` | one sub-section with its heading path (chapter › section › sub-section) | chapter, section, pages |
| `omnis-notation` | one node overview + groups of members | node path, section, deprecated members |

Design decisions that still hold from the original concept:

- **Natural units.** Commands and functions are self-contained entries; a chunk never mixes two of them.
- **Deprecated entries stay** in the index (legacy code must still be understood) but are marked, so
  agents explain them instead of proposing them.
- **Metadata in the embedding.** A context line (entry name, group, flags or heading path) is embedded
  with the chunk, so even short chunks carry their meaning.
- **Local embeddings.** `BAAI/bge-m3`, multilingual, 1024 dimensions — for indexing and for queries.

---

## Architecture

```text
Omnis PDF/*.pdf ─┐
doc pack (opt.) ─┤ extract.py → chunk.py → validate.py → embed_and_store.py → import
                 ▼
          PostgreSQL + pgvector  (schema rag: corpus → document → chunk → embedding)
                 ▼
          rag-server  /search  /chunks  /embed  /health
                 ▼
          MCP: search_omnis_docs · get_omnis_doc · search_omnis_syntax · search_omnis_concepts
                 ▼
          coding agent (VS Code, Claude Code, Codex, …)
```

Runtime topologies (the MCP layer never retrieves on its own):

1. Local: PostgreSQL → `rag-server` (Python) → stdio bridge `OmnisRAGServer/mcp-bridge/mcpserver.mjs`
2. Docker with host PostgreSQL: `docker_mcp-rag/` (rag-server + mcp-server, HTTP port 3000)
3. Full Docker stack: `docker_mcp-rag-pg/` (PostgreSQL 18 + pgvector + both servers)

---

## How retrieval works

1. The query is embedded (semantic leg), split into words for the weighted full-text leg (stop words
   removed, common German Omnis words mapped to English), and scanned for Omnis names.
2. The database ranks all corpora together: nearest vectors, best full-text matches, and chunks that
   document a name from the query are fused into **one** ranking.
3. One hit per entry/section is returned as a line with title, source, pages, id and a snippet.
4. The agent fetches the full text of the relevant ids.

Details: [embedding_concept_en.md](embedding_concept_en.md), [postgres_en.md](postgres_en.md).
Extraction and chunking: [chunking_concept_en.md](chunking_concept_en.md).
Measurements and the reasons for this design: [retrieval_quality_analysis_en.md](retrieval_quality_analysis_en.md).

---

## Quality control

- **Build time:** `scripts/validate.py` — every bookmarked command and every function table of the PDFs
  must be present, no code line as title, no text damage, all chunk fields present; cross-check with
  the doc pack.
- **Retrieval:** `scripts/eval_retrieval.py` — 40 questions (commands, functions, notation, concepts,
  SQL, German, exact names) with expected hits; Hit@5 and MRR@5 per mode. Run it before and after
  every change.
- **Runtime:** `scripts/test_mcp_rag_bridge.py` — end-to-end test of the MCP tools.
