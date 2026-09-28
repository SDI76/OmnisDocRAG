-- ============================================================
-- RAG schema (v2)
--
-- Single source of truth for the Docker stack and the local setup
-- (scripts/setup_db.sql includes this file).
-- Idempotent: safe on an empty database and on a v1 database.
-- Must run as a role that can SET ROLE rag_owner.
-- ============================================================

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

-- ── Tables ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS rag.corpus (
  corpus_id   uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text        NOT NULL UNIQUE,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- One document per chunk; external_id is the stable chunk id from chunk.py
-- (e.g. "cmd_ok_message"). Parts of one entry share meta->>'doc_key'.
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

CREATE INDEX IF NOT EXISTS ix_document_corpus   ON rag.document(corpus_id);
CREATE INDEX IF NOT EXISTS ix_document_external ON rag.document(external_id);

CREATE TABLE IF NOT EXISTS rag.chunk (
  chunk_id    uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid        NOT NULL REFERENCES rag.document(document_id) ON DELETE CASCADE,
  chunk_index int         NOT NULL,
  content     text        NOT NULL,
  char_start  int,
  char_end    int,
  meta        jsonb       NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, chunk_index)
);

-- v2 columns
ALTER TABLE rag.chunk ADD COLUMN IF NOT EXISTS title      text   NOT NULL DEFAULT '';
ALTER TABLE rag.chunk ADD COLUMN IF NOT EXISTS heading    text   NOT NULL DEFAULT '';
-- Normalised names this chunk documents (command/function name, notation node
-- and member names). Used to boost exact-name matches.
ALTER TABLE rag.chunk ADD COLUMN IF NOT EXISTS symbols    text[] NOT NULL DEFAULT '{}';
ALTER TABLE rag.chunk ADD COLUMN IF NOT EXISTS search_tsv tsvector;

-- v1 had a generated full-text column over the raw content only.
DROP INDEX IF EXISTS rag.ix_chunk_tsv;
ALTER TABLE rag.chunk DROP COLUMN IF EXISTS content_tsv;

CREATE INDEX IF NOT EXISTS ix_chunk_document   ON rag.chunk(document_id);
CREATE INDEX IF NOT EXISTS ix_chunk_search_tsv ON rag.chunk USING GIN (search_tsv);
CREATE INDEX IF NOT EXISTS ix_chunk_symbols    ON rag.chunk USING GIN (symbols);

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

-- ── Full-text vector ────────────────────────────────────────
--
-- Weights (ranked with {D,C,B,A} = {0.2, 0.4, 0.7, 1.0}):
--   A  title          english + simple (symbol names stay unstemmed)
--   B  heading path   english
--   C  content        simple  (exact tokens: binfrombase64, errcode, $line -> line)
--   D  content        english (stemmed prose: "lists" -> "list")
--
CREATE OR REPLACE FUNCTION rag.build_search_tsv(p_title text, p_heading text, p_content text)
RETURNS tsvector
LANGUAGE sql IMMUTABLE AS $$
  SELECT
      setweight(to_tsvector('english'::regconfig, coalesce(p_title, '')), 'A')
   || setweight(to_tsvector('simple'::regconfig,  coalesce(p_title, '')), 'A')
   || setweight(to_tsvector('english'::regconfig, coalesce(p_heading, '')), 'B')
   || setweight(to_tsvector('simple'::regconfig,  coalesce(p_content, '')), 'C')
   || setweight(to_tsvector('english'::regconfig, coalesce(p_content, '')), 'D');
$$;

CREATE OR REPLACE FUNCTION rag.chunk_search_tsv_trigger()
RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.search_tsv := rag.build_search_tsv(NEW.title, NEW.heading, NEW.content);
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_chunk_search_tsv ON rag.chunk;
CREATE TRIGGER trg_chunk_search_tsv
  BEFORE INSERT OR UPDATE OF title, heading, content ON rag.chunk
  FOR EACH ROW EXECUTE FUNCTION rag.chunk_search_tsv_trigger();

-- Fill the vector for rows that existed before the trigger (v1 migration).
UPDATE rag.chunk SET search_tsv = rag.build_search_tsv(title, heading, content)
WHERE search_tsv IS NULL;

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

-- ── Corpora ─────────────────────────────────────────────────

INSERT INTO rag.corpus (name, description) VALUES
  ('omnis-commands',    'Omnis Command Reference: one chunk per command, plus overview sections'),
  ('omnis-functions',   'Omnis Function Reference: one chunk per function'),
  ('omnis-programming', 'Omnis Programming manual: all chapters, one chunk per sub-section'),
  ('omnis-notation',    'Omnis notation reference (Omnis help): nodes with properties, methods and events')
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;

-- The v1 seed advertised a code corpus that never existed.
DELETE FROM rag.corpus c
WHERE c.name = 'omnis-code'
  AND NOT EXISTS (SELECT 1 FROM rag.document d WHERE d.corpus_id = c.corpus_id);

-- v1 helpers that the v2 server no longer uses
DROP FUNCTION IF EXISTS rag.search(vector, uuid, int, float);
DROP FUNCTION IF EXISTS rag.search_fts(text, uuid, int);

RESET ROLE;

GRANT USAGE ON SCHEMA rag TO rag_app, rag_ro;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA rag TO rag_app;
GRANT SELECT ON ALL TABLES IN SCHEMA rag TO rag_ro;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA rag TO rag_app, rag_ro;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA rag TO rag_app, rag_ro;
