-- ============================================================
-- Hybrid Search + Ranking
-- Adds rag.search_hybrid() via Reciprocal Rank Fusion (RRF).
--
-- Run in ragdb after setup_db.sql:
--   psql -U postgres -d ragdb -f setup_ranking.sql
-- ============================================================

SET search_path TO rag, public;


-- ── Reciprocal Rank Fusion ───────────────────────────────────
--
-- Combines dense vector search + BM25 full-text search.
-- Each result gets an RRF score: sum(1 / (k + rank))
--   k = 60  (standard constant, dampens rank differences at the top)
--
-- Parameters:
--   query_vec   — embedded query vector (1024 dim, bge-m3)
--   query_text  — raw query text for BM25 (e.g. '$sendall kRelationalList')
--   p_corpus    — corpus UUID (use corpus_id from rag.corpus)
--   top_k       — final results to return (default 10)
--   candidate_k — how many candidates each method fetches before fusion (default 40)
--   rrf_k       — RRF constant (default 60, rarely needs changing)
--
-- Usage:
--   SELECT * FROM rag.search_hybrid(
--     query_vec   := '[0.1, 0.2, ...]'::vector,
--     query_text  := 'how to iterate over list',
--     p_corpus    := (SELECT corpus_id FROM rag.corpus WHERE name = 'omnis-docs'),
--     top_k       := 10
--   );
--
CREATE OR REPLACE FUNCTION rag.search_hybrid(
  query_vec   vector(1024),
  query_text  text,
  p_corpus    uuid,
  top_k       int   DEFAULT 10,
  candidate_k int   DEFAULT 40,
  rrf_k       int   DEFAULT 60
)
RETURNS TABLE (
  chunk_id     uuid,
  document_id  uuid,
  title        text,
  uri          text,
  chunk_index  int,
  content      text,
  rrf_score    float,
  dense_rank   int,
  fts_rank     int,
  meta         jsonb,
  doc_meta     jsonb
)
LANGUAGE plpgsql STABLE AS $$
DECLARE
  v_tsquery tsquery;
BEGIN
  -- Build tsquery from free text.
  -- Converts "how to iterate" → 'how & to & iterate' (simple dictionary).
  -- Falls back to NULL if query produces no valid tokens (pure notation queries
  -- like "$sendall" may not tokenize well — BM25 still runs, just returns 0 rows).
  BEGIN
    v_tsquery := to_tsquery(
      'simple',
      array_to_string(
        array(
          SELECT token
          FROM unnest(string_to_array(trim(query_text), ' ')) AS token
          WHERE length(trim(token)) > 0
        ),
        ' & '
      )
    );
  EXCEPTION WHEN OTHERS THEN
    v_tsquery := NULL;
  END;

  RETURN QUERY
  WITH

  -- Dense: top candidate_k by cosine distance
  dense AS (
    SELECT
      ch.chunk_id,
      row_number() OVER (ORDER BY e.v <=> query_vec)::int AS rnk
    FROM rag.embedding e
    JOIN rag.chunk    ch ON ch.chunk_id   = e.chunk_id
    JOIN rag.document d  ON d.document_id = ch.document_id
    WHERE d.corpus_id = p_corpus
    ORDER BY e.v <=> query_vec
    LIMIT candidate_k
  ),

  -- BM25: top candidate_k by ts_rank (skipped if tsquery is null)
  fts AS (
    SELECT
      ch.chunk_id,
      row_number() OVER (ORDER BY ts_rank_cd(ch.content_tsv, v_tsquery) DESC)::int AS rnk
    FROM rag.chunk    ch
    JOIN rag.document d ON d.document_id = ch.document_id
    WHERE d.corpus_id = p_corpus
      AND v_tsquery IS NOT NULL
      AND ch.content_tsv @@ v_tsquery
    ORDER BY ts_rank_cd(ch.content_tsv, v_tsquery) DESC
    LIMIT candidate_k
  ),

  -- RRF fusion: full outer join, sum the rank scores
  rrf AS (
    SELECT
      COALESCE(d.chunk_id, f.chunk_id)                              AS chunk_id,
      COALESCE(1.0 / (rrf_k + d.rnk), 0)
        + COALESCE(1.0 / (rrf_k + f.rnk), 0)                       AS rrf_score,
      d.rnk                                                          AS dense_rank,
      f.rnk                                                          AS fts_rank
    FROM dense d
    FULL OUTER JOIN fts f ON d.chunk_id = f.chunk_id
  )

  SELECT
    ch.chunk_id,
    d.document_id,
    d.title,
    d.uri,
    ch.chunk_index,
    ch.content,
    rrf.rrf_score::float,
    rrf.dense_rank::int,
    rrf.fts_rank::int,
    ch.meta,
    d.meta AS doc_meta
  FROM rrf
  JOIN rag.chunk    ch ON ch.chunk_id   = rrf.chunk_id
  JOIN rag.document d  ON d.document_id = ch.document_id
  ORDER BY rrf.rrf_score DESC
  LIMIT top_k;

END;
$$;


-- ── Multi-corpus search ──────────────────────────────────────
-- Queries multiple corpora with individual top_k, returns combined results.
-- Use this for full Omnis doc retrieval (commands + functions + programming).
--
-- Usage:
--   SELECT * FROM rag.search_omnis_docs(
--     query_vec  := <embedded_query>,
--     query_text := 'how to iterate list $add',
--     k_commands := 3,
--     k_functions := 2,
--     k_programming := 4
--   );
CREATE OR REPLACE FUNCTION rag.search_omnis_docs(
  query_vec      vector(1024),
  query_text     text,
  k_commands     int DEFAULT 3,
  k_functions    int DEFAULT 2,
  k_programming  int DEFAULT 4
)
RETURNS TABLE (
  chunk_id    uuid,
  corpus_name text,
  title       text,
  content     text,
  rrf_score   float,
  dense_rank  int,
  fts_rank    int,
  meta        jsonb
)
LANGUAGE plpgsql STABLE AS $$
DECLARE
  id_commands    uuid;
  id_functions   uuid;
  id_programming uuid;
BEGIN
  SELECT corpus_id INTO id_commands    FROM rag.corpus WHERE name = 'omnis-commands';
  SELECT corpus_id INTO id_functions   FROM rag.corpus WHERE name = 'omnis-functions';
  SELECT corpus_id INTO id_programming FROM rag.corpus WHERE name = 'omnis-programming';

  RETURN QUERY

  SELECT h.chunk_id, 'omnis-commands'::text, h.title, h.content,
         h.rrf_score, h.dense_rank, h.fts_rank, h.meta
  FROM rag.search_hybrid(query_vec, query_text, id_commands, k_commands) h

  UNION ALL

  SELECT h.chunk_id, 'omnis-functions'::text, h.title, h.content,
         h.rrf_score, h.dense_rank, h.fts_rank, h.meta
  FROM rag.search_hybrid(query_vec, query_text, id_functions, k_functions) h

  UNION ALL

  SELECT h.chunk_id, 'omnis-programming'::text, h.title, h.content,
         h.rrf_score, h.dense_rank, h.fts_rank, h.meta
  FROM rag.search_hybrid(query_vec, query_text, id_programming, k_programming) h

  ORDER BY rrf_score DESC;
END;
$$;


-- ── Grants ───────────────────────────────────────────────────
GRANT EXECUTE ON FUNCTION rag.search_hybrid TO rag_app, rag_ro;
GRANT EXECUTE ON FUNCTION rag.search_omnis_docs TO rag_app, rag_ro;


-- ── Quick smoke test (run after data is imported) ────────────
-- Replace the zero-vector with a real query embedding.
-- Expected: results ordered by rrf_score DESC, dense_rank and fts_rank visible.
--
-- SELECT
--   chunk_id,
--   left(content, 80) AS preview,
--   rrf_score,
--   dense_rank,
--   fts_rank
-- FROM rag.search_hybrid(
--   query_vec  := array_fill(0, ARRAY[1024])::vector,
--   query_text := 'iterate list $add',
--   p_corpus   := (SELECT corpus_id FROM rag.corpus WHERE name = 'omnis-docs'),
--   top_k      := 5
-- );
