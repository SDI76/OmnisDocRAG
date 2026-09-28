-- ============================================================
-- RAG ranking (v2)
--
-- rag.search_ranked: one global ranking across all (or selected) corpora.
--
--   dense   cosine distance on bge-m3 embeddings            (semantic)
--   fts     weighted full-text rank on chunk.search_tsv      (lexical)
--   exact   chunk documents a symbol named in the query      (boost)
--
-- Dense and full-text candidates are fused with weighted Reciprocal Rank
-- Fusion over the *global* candidate lists, so ranks are comparable across
-- corpora. Exact-name matches get a fixed boost that scales with the number
-- of words in the matched name ("Do method" beats "Do").
-- Results are grouped by meta->>'doc_key': one hit per entry/section.
--
-- The caller chooses the mode by passing NULL for the unused inputs:
--   semantic  p_query_vec set, p_terms/p_websearch NULL
--   fulltext  p_query_vec NULL, p_terms or p_websearch set
--   hybrid    both set
-- ============================================================

SET ROLE rag_owner;
SET search_path TO rag, public;

-- v1 functions (per-corpus RRF with fixed k per corpus)
DROP FUNCTION IF EXISTS rag.search_omnis_docs(vector, text, int, int, int);
DROP FUNCTION IF EXISTS rag.search_hybrid(vector, text, uuid, int, int, int);

DROP FUNCTION IF EXISTS rag.search_ranked(vector, text[], text, text[], text[], int, int, float, float, int);

CREATE FUNCTION rag.search_ranked(
  p_query_vec     vector(1024),
  p_terms         text[],           -- sanitised query words, OR-combined
  p_websearch     text,             -- raw query with search syntax ("…", OR, -), overrides p_terms
  p_boost_symbols text[],           -- normalised names found in the query
  p_corpora       text[],           -- NULL = all corpora
  p_top_k         int   DEFAULT 8,
  p_candidate_k   int   DEFAULT 60,
  p_w_dense       float DEFAULT 1.0,
  p_w_fts         float DEFAULT 1.0,
  p_rrf_k         int   DEFAULT 60
)
RETURNS TABLE (
  external_id  text,
  corpus       text,
  title        text,
  heading      text,
  content      text,
  meta         jsonb,
  score        float,
  dense_rank   int,
  fts_rank     int,
  exact_symbol text,
  snippet      text
)
LANGUAGE plpgsql STABLE AS $$
#variable_conflict use_column
DECLARE
  q tsquery := NULL;
BEGIN
  IF p_websearch IS NOT NULL AND length(trim(p_websearch)) > 0 THEN
    q := websearch_to_tsquery('english', p_websearch) || websearch_to_tsquery('simple', p_websearch);
  ELSIF p_terms IS NOT NULL AND cardinality(p_terms) > 0 THEN
    q := to_tsquery('english', array_to_string(p_terms, ' | '))
      || to_tsquery('simple',  array_to_string(p_terms, ' | '));
  END IF;
  IF q IS NOT NULL AND numnode(q) = 0 THEN
    q := NULL;
  END IF;

  RETURN QUERY
  WITH base AS (
    SELECT ch.chunk_id, d.external_id, co.name AS corpus, ch.title, ch.heading,
           ch.content, ch.meta, ch.symbols, ch.search_tsv
    FROM rag.chunk ch
    JOIN rag.document d ON d.document_id = ch.document_id
    JOIN rag.corpus co  ON co.corpus_id = d.corpus_id
    WHERE p_corpora IS NULL OR co.name = ANY(p_corpora)
  ),
  dense AS (
    SELECT b.chunk_id,
           row_number() OVER (ORDER BY e.v <=> p_query_vec)::int AS rnk
    FROM base b
    JOIN rag.embedding e ON e.chunk_id = b.chunk_id
    WHERE p_query_vec IS NOT NULL
    ORDER BY e.v <=> p_query_vec
    LIMIT p_candidate_k
  ),
  fts AS (
    SELECT b.chunk_id,
           row_number() OVER (
             ORDER BY ts_rank_cd('{0.2,0.4,0.7,1.0}', b.search_tsv, q, 1) DESC)::int AS rnk
    FROM base b
    WHERE q IS NOT NULL AND b.search_tsv @@ q
    ORDER BY ts_rank_cd('{0.2,0.4,0.7,1.0}', b.search_tsv, q, 1) DESC
    LIMIT p_candidate_k
  ),
  exact AS (
    SELECT DISTINCT ON (b.chunk_id)
           b.chunk_id, s AS sym, cardinality(string_to_array(s, ' ')) AS nwords
    FROM base b
    CROSS JOIN LATERAL unnest(b.symbols) AS s
    WHERE p_boost_symbols IS NOT NULL
      AND b.symbols && p_boost_symbols
      AND s = ANY(p_boost_symbols)
    ORDER BY b.chunk_id, cardinality(string_to_array(s, ' ')) DESC
  ),
  fused AS (
    SELECT chunk_id,
           coalesce(p_w_dense / (p_rrf_k + dn.rnk), 0)
         + coalesce(p_w_fts   / (p_rrf_k + ft.rnk), 0)
         + coalesce(0.02 * x.nwords, 0) AS score,
           dn.rnk AS dense_rank,
           ft.rnk AS fts_rank,
           x.sym  AS exact_symbol
    FROM dense dn
    FULL JOIN fts ft USING (chunk_id)
    FULL JOIN exact x USING (chunk_id)
  ),
  grouped AS (
    SELECT DISTINCT ON (coalesce(b.meta->>'doc_key', b.external_id))
           b.external_id, b.corpus, b.title, b.heading, b.content, b.meta,
           f.score, f.dense_rank, f.fts_rank, f.exact_symbol
    FROM fused f
    JOIN base b ON b.chunk_id = f.chunk_id
    ORDER BY coalesce(b.meta->>'doc_key', b.external_id), f.score DESC
  ),
  top AS (
    SELECT * FROM grouped g ORDER BY g.score DESC LIMIT p_top_k
  )
  SELECT t.external_id, t.corpus, t.title, t.heading, t.content, t.meta,
         t.score::float, t.dense_rank, t.fts_rank, t.exact_symbol,
         -- Snippet around the matching words, without the chunk's own heading line
         -- and without highlight markers (they would land inside code spans).
         CASE WHEN q IS NOT NULL AND t.content IS NOT NULL THEN
           ts_headline('english', regexp_replace(t.content, '^#+[^\n]*\n+', ''), q,
             'MaxWords=35, MinWords=12, MaxFragments=2, FragmentDelimiter=" … ", StartSel="", StopSel=""')
         END AS snippet
  FROM top t
  ORDER BY t.score DESC;
END;
$$;

RESET ROLE;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA rag TO rag_app, rag_ro;
