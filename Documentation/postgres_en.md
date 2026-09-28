# PostgreSQL Schema — Omnis RAG (v2)

SQL sources (shared by the Docker stack and the local setup):

- `docker_mcp-rag-pg/postgres-init/sql/20-rag-bootstrap.sql` — roles (Docker, with passwords from `.env`)
- `docker_mcp-rag-pg/postgres-init/sql/30-rag-schema.sql` — tables, full-text vector, corpora
- `docker_mcp-rag-pg/postgres-init/sql/40-rag-ranking.sql` — `rag.search_ranked`

Local PostgreSQL: `scripts/setup_db.sql` and `scripts/setup_ranking.sql` include the files above.
Both schema files are idempotent; `30-rag-schema.sql` migrates a v1 database (drops the old
`content_tsv` column and the per-corpus functions).

---

## Tables

```text
rag.corpus     (corpus_id, name, description)
  └── rag.document  (document_id, corpus_id, external_id, title, meta)          one per chunk
        └── rag.chunk  (chunk_id, document_id, chunk_index, content, meta,
                        title, heading, symbols text[], search_tsv tsvector)
              └── rag.embedding  (chunk_id, model, embedding_dim, v vector(1024))
```

- `document.external_id` = chunk id from `chunk.py` (`cmd_ok_message`, `not_list_properties_1`, …).
- `meta->>'doc_key'` groups the parts of one entry; `part` / `parts` number them.
- `symbols`: normalised names the chunk documents (`do method`, `mid`, `ojson.jsontolistorrow`,
  `line`, `search`, …) — lower case, without `$`, `#`, `()`.

| Corpus | Content |
|---|---|
| `omnis-commands` | Command Reference: commands, overview sections, error code tables |
| `omnis-functions` | Function Reference |
| `omnis-programming` | Programming manual, chapters 1–17 |
| `omnis-notation` | notation nodes with properties, methods, events (doc pack) |

---

## Full-text vector

Built by the trigger `trg_chunk_search_tsv` (function `rag.build_search_tsv`):

| Weight | Field | Config | Purpose |
|---|---|---|---|
| A | title | `english` + `simple` | entry names, unstemmed and stemmed |
| B | heading path | `english` | chapter › section › sub-section |
| C | content | `simple` | exact tokens (`binfrombase64`, `errcode`) |
| D | content | `english` | stemmed prose (`lists` → `list`) |

Ranking uses `ts_rank_cd('{0.2,0.4,0.7,1.0}', search_tsv, query, 1)` (length-normalised).

---

## Indexes

```sql
CREATE INDEX ix_chunk_search_tsv ON rag.chunk USING GIN (search_tsv);
CREATE INDEX ix_chunk_symbols    ON rag.chunk USING GIN (symbols);
CREATE INDEX ix_embedding_hnsw   ON rag.embedding USING hnsw (v vector_cosine_ops) WITH (m = 16, ef_construction = 128);
```

---

## `rag.search_ranked`

```sql
SELECT * FROM rag.search_ranked(
  p_query_vec     := '<1024-dim vector>'::vector,   -- NULL = no semantic leg
  p_terms         := ARRAY['list','search'],         -- OR-combined words; NULL = no full-text leg
  p_websearch     := NULL,                           -- raw query with "phrase", OR, -word (overrides p_terms)
  p_boost_symbols := ARRAY['search'],                -- names found in the query
  p_corpora       := NULL,                           -- NULL = all corpora
  p_top_k         := 8,
  p_candidate_k   := 60,
  p_w_dense       := 1.0,
  p_w_fts         := 0.3,
  p_rrf_k         := 60);
```

1. **dense**: the 60 nearest chunks by cosine distance, across all selected corpora.
2. **fts**: the 60 best chunks by weighted full-text rank. Words are OR-combined in `english` and
   `simple` config; `p_websearch` uses `websearch_to_tsquery` instead.
3. **exact**: chunks whose `symbols` contain a name from the query; boost `0.02 × words in the name`.
4. **fusion**: `w_dense / (60 + dense_rank) + w_fts / (60 + fts_rank) + boost` — one global ranking.
5. **grouping**: one hit per `doc_key`; `ts_headline` snippet for the top hits.

The rag-server builds `p_terms` (stop words removed, common German Omnis words mapped to English),
detects search syntax for `p_websearch` and derives `p_boost_symbols` from the query.

---

## Roles

| Role | Rights |
|---|---|
| `rag_owner` | owns schema and objects; runs the SQL files |
| `rag_app` | read/write data (import, rag-server) |
| `rag_ro` | read-only |

---

## After a bulk import

```bash
cd docker_mcp-rag-pg
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.embedding;"
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.chunk;"
```

`VACUUM` cannot run inside a transaction block — one statement per `-c`.
