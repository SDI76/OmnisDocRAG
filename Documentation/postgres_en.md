# PostgreSQL Schema — Omnis RAG

Reference for the `rag` schema. Full SQL files:
- `scripts/setup_db.sql` — schema, tables, indexes
- `scripts/setup_ranking.sql` — hybrid search functions

This schema is used by:

- local or external PostgreSQL instances populated manually
- the full Docker stack in `docker_mcp-rag-pg/`, where the database is initialized automatically on first startup

---

## Table Structure

```text
rag.corpus     (corpus_id, name, description)
  └── rag.document  (document_id, corpus_id, external_id, title, hash_sha256, meta)
        └── rag.chunk     (chunk_id, document_id, chunk_index, content, content_tsv, meta)
              └── rag.embedding  (chunk_id, model, embedding_dim, v::vector(1024))
```

**Corpora (in the database):**

| name | Source |
|---|---|
| `omnis-commands` | CommandRef.pdf |
| `omnis-functions` | FunctionRef.pdf |
| `omnis-programming` | Programming_Omnis.pdf |

---

## Indexes

```sql
-- BM25 full-text search
CREATE INDEX ix_chunk_tsv ON rag.chunk USING GIN (content_tsv);

-- Approximate nearest neighbour (HNSW)
CREATE INDEX ix_embedding_hnsw ON rag.embedding
  USING hnsw (v vector_cosine_ops) WITH (m = 16, ef_construction = 200);
```

---

## Hybrid Search Functions

### `rag.search_hybrid(query_vec, query_text, corpus_id, top_k)`

Combines dense search and BM25 via Reciprocal Rank Fusion (RRF):

```text
RRF score = 1/(60 + dense_rank) + 1/(60 + bm25_rank)
```

### `rag.search_omnis_docs(query_vec, query_text, k_commands, k_functions, k_programming)`

Calls `search_hybrid` across all three corpora and returns combined results.

```sql
SELECT * FROM rag.search_omnis_docs(
  query_vec     := '<embedded_query>'::vector,
  query_text    := 'how to iterate list $add',
  k_commands    := 3,
  k_functions   := 2,
  k_programming := 4
);
```

---

## After Bulk Import

```sql
VACUUM ANALYZE rag.embedding;
VACUUM ANALYZE rag.chunk;
```

For `docker_mcp-rag-pg/`, run each `VACUUM` as a separate `psql -c` command:

```bash
cd docker_mcp-rag-pg
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.embedding;"
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.chunk;"
```

`VACUUM` cannot run inside a transaction block, so do not combine both statements into one single `-c`.

---

## Roles

```sql
CREATE ROLE rag_owner LOGIN PASSWORD '...';  -- table owner, import
CREATE ROLE rag_app   LOGIN PASSWORD '...';  -- RAG server (SELECT/INSERT/UPDATE)
CREATE ROLE rag_ro    LOGIN PASSWORD '...';  -- read-only (optional)
```
