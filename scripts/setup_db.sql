-- ============================================================
-- RAG Database Setup (local PostgreSQL)
--
-- 1) Create roles (this file, as superuser, in any database):
--      psql -U postgres -f scripts/setup_db.sql
--    then create the database once:
--      createdb -U postgres -O rag_owner ragdb
-- 2) Create schema + ranking in ragdb:
--      psql -U postgres -d ragdb -f scripts/setup_db.sql
--      psql -U postgres -d ragdb -f scripts/setup_ranking.sql
--
-- Running this file inside ragdb applies the shared schema from
-- docker_mcp-rag-pg/postgres-init/sql/30-rag-schema.sql, which is idempotent
-- and also migrates a v1 database.
--
-- Change the passwords below before first use.
-- ============================================================

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

SELECT current_database() = 'ragdb' AS in_ragdb \gset
\if :in_ragdb
  \ir ../docker_mcp-rag-pg/postgres-init/sql/30-rag-schema.sql
\else
  \echo 'Roles ready. Create the database (createdb -U postgres -O rag_owner ragdb) and run this file again with -d ragdb.'
\endif
