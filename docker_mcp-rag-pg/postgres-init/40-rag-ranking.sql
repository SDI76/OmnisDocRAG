SET ROLE rag_owner;
SET search_path TO rag, public;

CREATE OR REPLACE FUNCTION rag.search_hybrid(
  query_vec   vector(1024),
  query_text  text,
  p_corpus    uuid,
  top_k       int DEFAULT 10,
  candidate_k int DEFAULT 40,
  rrf_k       int DEFAULT 60
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
  dense AS (
    SELECT
      ch.chunk_id,
      row_number() OVER (ORDER BY e.v <=> query_vec)::int AS rnk
    FROM rag.embedding e
    JOIN rag.chunk ch ON ch.chunk_id = e.chunk_id
    JOIN rag.document d ON d.document_id = ch.document_id
    WHERE d.corpus_id = p_corpus
    ORDER BY e.v <=> query_vec
    LIMIT candidate_k
  ),
  fts AS (
    SELECT
      ch.chunk_id,
      row_number() OVER (ORDER BY ts_rank_cd(ch.content_tsv, v_tsquery) DESC)::int AS rnk
    FROM rag.chunk ch
    JOIN rag.document d ON d.document_id = ch.document_id
    WHERE d.corpus_id = p_corpus
      AND v_tsquery IS NOT NULL
      AND ch.content_tsv @@ v_tsquery
    ORDER BY ts_rank_cd(ch.content_tsv, v_tsquery) DESC
    LIMIT candidate_k
  ),
  rrf AS (
    SELECT
      COALESCE(d.chunk_id, f.chunk_id) AS chunk_id,
      COALESCE(1.0 / (rrf_k + d.rnk), 0)
        + COALESCE(1.0 / (rrf_k + f.rnk), 0) AS rrf_score,
      d.rnk AS dense_rank,
      f.rnk AS fts_rank
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
  JOIN rag.chunk ch ON ch.chunk_id = rrf.chunk_id
  JOIN rag.document d ON d.document_id = ch.document_id
  ORDER BY rrf.rrf_score DESC
  LIMIT top_k;
END;
$$;

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

RESET ROLE;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA rag TO rag_app, rag_ro;
