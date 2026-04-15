CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE SCHEMA IF NOT EXISTS rag AUTHORIZATION rag_owner;
ALTER SCHEMA rag OWNER TO rag_owner;

SET ROLE rag_owner;
SET search_path TO rag, public;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rag_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT SELECT ON TABLES TO rag_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT USAGE, SELECT ON SEQUENCES TO rag_app, rag_ro;

CREATE TABLE IF NOT EXISTS rag.corpus (
  corpus_id   uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text        NOT NULL UNIQUE,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rag.document (
  document_id uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  corpus_id   uuid        NOT NULL REFERENCES rag.corpus(corpus_id) ON DELETE CASCADE,
  external_id text,
  title       text,
  uri         text,
  hash_sha256 text,
  meta        jsonb       NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (corpus_id, external_id)
);

CREATE INDEX IF NOT EXISTS ix_document_corpus
  ON rag.document(corpus_id);

CREATE TABLE IF NOT EXISTS rag.chunk (
  chunk_id    uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid        NOT NULL REFERENCES rag.document(document_id) ON DELETE CASCADE,
  chunk_index int         NOT NULL,
  content     text        NOT NULL,
  content_tsv tsvector    GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
  char_start  int,
  char_end    int,
  meta        jsonb       NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS ix_chunk_document
  ON rag.chunk(document_id);

CREATE INDEX IF NOT EXISTS ix_chunk_tsv
  ON rag.chunk USING GIN (content_tsv);

CREATE TABLE IF NOT EXISTS rag.embedding (
  chunk_id      uuid         PRIMARY KEY REFERENCES rag.chunk(chunk_id) ON DELETE CASCADE,
  model         text         NOT NULL,
  embedding_dim int          NOT NULL,
  v             vector(1024) NOT NULL,
  created_at    timestamptz  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_embedding_hnsw
  ON rag.embedding USING hnsw (v vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

CREATE OR REPLACE FUNCTION rag.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_document_updated_at ON rag.document;
CREATE TRIGGER trg_document_updated_at
  BEFORE UPDATE ON rag.document
  FOR EACH ROW EXECUTE FUNCTION rag.set_updated_at();

CREATE OR REPLACE FUNCTION rag.search(
  query_vec  vector(1024),
  p_corpus   uuid,
  top_k      int DEFAULT 10,
  min_score  float DEFAULT 0.0
)
RETURNS TABLE (
  chunk_id    uuid,
  document_id uuid,
  title       text,
  uri         text,
  chunk_index int,
  content     text,
  score       float,
  meta        jsonb,
  doc_meta    jsonb
)
LANGUAGE sql STABLE AS $$
  SELECT
    ch.chunk_id,
    d.document_id,
    d.title,
    d.uri,
    ch.chunk_index,
    ch.content,
    (1 - (e.v <=> query_vec))::float AS score,
    ch.meta,
    d.meta AS doc_meta
  FROM rag.embedding e
  JOIN rag.chunk ch ON ch.chunk_id = e.chunk_id
  JOIN rag.document d ON d.document_id = ch.document_id
  WHERE d.corpus_id = p_corpus
    AND (1 - (e.v <=> query_vec)) >= min_score
  ORDER BY e.v <=> query_vec
  LIMIT top_k;
$$;

CREATE OR REPLACE FUNCTION rag.search_fts(
  query_text text,
  p_corpus   uuid,
  top_k      int DEFAULT 20
)
RETURNS TABLE (
  chunk_id    uuid,
  document_id uuid,
  content     text,
  rank        float,
  meta        jsonb
)
LANGUAGE sql STABLE AS $$
  SELECT
    ch.chunk_id,
    ch.document_id,
    ch.content,
    ts_rank_cd(ch.content_tsv, q)::float AS rank,
    ch.meta
  FROM rag.chunk ch
  JOIN rag.document d ON d.document_id = ch.document_id,
  to_tsquery('simple', regexp_replace(trim(query_text), '\s+', ' & ', 'g')) q
  WHERE d.corpus_id = p_corpus
    AND ch.content_tsv @@ q
  ORDER BY rank DESC
  LIMIT top_k;
$$;

INSERT INTO rag.corpus (name, description) VALUES
  ('omnis-commands',    'CommandRef: 475 commands with syntax, options, examples, metadata'),
  ('omnis-functions',   'FunctionRef: 327 functions with syntax, parameters, examples'),
  ('omnis-programming', 'Programming guide: concepts, patterns, SQL, lists, OOP, events (ch. 2,3,5-17)'),
  ('omnis-code',        'Codebase: curated Omnis method chunks from project libraries')
ON CONFLICT (name) DO NOTHING;

RESET ROLE;

GRANT USAGE ON SCHEMA rag TO rag_app, rag_ro;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA rag TO rag_app;
GRANT SELECT
  ON ALL TABLES IN SCHEMA rag TO rag_ro;
GRANT USAGE, SELECT
  ON ALL SEQUENCES IN SCHEMA rag TO rag_app, rag_ro;
GRANT EXECUTE
  ON ALL FUNCTIONS IN SCHEMA rag TO rag_app, rag_ro;
