-- ============================================================
-- RAG Database Setup
-- Omnis Studio RAG System
--
-- Run as superuser (postgres):
--   psql -U postgres -f setup_db.sql
--
-- Embedding model: text-embedding-bge-m3 (1024 dimensions)
-- ============================================================


-- ── Extensions (must run as superuser) ──────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "vector";     -- pgvector


-- ── Roles ───────────────────────────────────────────────────
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_owner') THEN
    CREATE ROLE rag_owner LOGIN PASSWORD 'change_me_owner';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_app') THEN
    CREATE ROLE rag_app LOGIN PASSWORD 'change_me_app';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_ro') THEN
    CREATE ROLE rag_ro LOGIN PASSWORD 'change_me_ro';
  END IF;
END
$$;


-- ── Database ─────────────────────────────────────────────────
-- Run this block separately if the DB doesn't exist yet:
--   createdb -U postgres -O rag_owner ragdb
-- Or uncomment the line below (requires no active connections):
-- CREATE DATABASE ragdb OWNER rag_owner;

-- After creating the DB, connect to it before running the rest:
-- \c ragdb


-- ── Schema ──────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS rag AUTHORIZATION rag_owner;

SET search_path TO rag, public;

GRANT USAGE ON SCHEMA rag TO rag_app, rag_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rag_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT SELECT ON TABLES TO rag_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
  GRANT USAGE, SELECT ON SEQUENCES TO rag_app, rag_ro;


-- ── Tables ──────────────────────────────────────────────────

-- 1) Corpus — top-level collection (e.g. "omnis-docs", "omnis-code")
CREATE TABLE IF NOT EXISTS rag.corpus (
  corpus_id   uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text        NOT NULL UNIQUE,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- 2) Document — one source file / PDF / class export / etc.
CREATE TABLE IF NOT EXISTS rag.document (
  document_id uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  corpus_id   uuid        NOT NULL REFERENCES rag.corpus(corpus_id) ON DELETE CASCADE,
  external_id text,                    -- stable ID: path, Omnis class name, etc.
  title       text,
  uri         text,                    -- file://, omnis://, https://, ...
  hash_sha256 text,                    -- change detection (vcsrevision for code)
  meta        jsonb       NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (corpus_id, external_id)
);

CREATE INDEX IF NOT EXISTS ix_document_corpus
  ON rag.document(corpus_id);

-- 3) Chunk — text segment that gets embedded
CREATE TABLE IF NOT EXISTS rag.chunk (
  chunk_id    uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid        NOT NULL REFERENCES rag.document(document_id) ON DELETE CASCADE,
  chunk_index int         NOT NULL,    -- 0..n per document
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

-- 4) Embedding — one vector per chunk
--    model: text-embedding-bge-m3, dim: 1024
CREATE TABLE IF NOT EXISTS rag.embedding (
  chunk_id      uuid    PRIMARY KEY REFERENCES rag.chunk(chunk_id) ON DELETE CASCADE,
  model         text    NOT NULL,
  embedding_dim int     NOT NULL,
  v             vector(1024) NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- HNSW index for fast approximate nearest-neighbour search.
-- Build AFTER bulk import (drop + recreate is faster than incremental build).
-- m=16, ef_construction=128 is a good default for a few thousand vectors.
CREATE INDEX IF NOT EXISTS ix_embedding_hnsw
  ON rag.embedding USING hnsw (v vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

-- Alternative: IVFFlat (tune lists after knowing final row count)
-- Rule of thumb: lists = sqrt(total_rows), min 10.
-- CREATE INDEX IF NOT EXISTS ix_embedding_ivfflat
--   ON rag.embedding USING ivfflat (v vector_cosine_ops)
--   WITH (lists = 50);


-- ── Trigger: updated_at on document ─────────────────────────
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


-- ── Retrieval function ───────────────────────────────────────
-- Dense vector search within one corpus.
-- Usage:
--   SELECT * FROM rag.search(query_vector, corpus_uuid, top_k := 10);
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
  JOIN rag.chunk    ch ON ch.chunk_id    = e.chunk_id
  JOIN rag.document d  ON d.document_id  = ch.document_id
  WHERE d.corpus_id = p_corpus
    AND (1 - (e.v <=> query_vec)) >= min_score
  ORDER BY e.v <=> query_vec
  LIMIT top_k;
$$;


-- ── BM25 / full-text search helper ──────────────────────────
-- Lexical search within one corpus (for hybrid search).
-- Usage:
--   SELECT * FROM rag.search_fts('$sendall kRelationalList', corpus_uuid, 20);
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


-- ── Initial corpora ──────────────────────────────────────────
-- Three doc corpora (one per source) + one for codebase chunks.
-- Separate corpora allow per-collection top_k tuning in hybrid search,
-- e.g. fetch 3 commands + 2 functions + 4 programming chunks per query.
INSERT INTO rag.corpus (name, description) VALUES
  ('omnis-commands',    'CommandRef: 475 commands with syntax, options, examples, metadata'),
  ('omnis-functions',   'FunctionRef: 327 functions with syntax, parameters, examples'),
  ('omnis-programming', 'Programming guide: concepts, patterns, SQL, lists, OOP, events (ch. 2,3,5-17)'),
  ('omnis-code',        'Codebase: curated Omnis method chunks from project libraries')
ON CONFLICT (name) DO NOTHING;


-- ── Grant on existing objects ────────────────────────────────
-- (Default privileges cover future objects; this covers objects just created.)
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA rag TO rag_app;
GRANT SELECT
  ON ALL TABLES IN SCHEMA rag TO rag_ro;
GRANT EXECUTE
  ON ALL FUNCTIONS IN SCHEMA rag TO rag_app, rag_ro;


-- ── Summary ──────────────────────────────────────────────────
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'rag'
ORDER BY tablename;
