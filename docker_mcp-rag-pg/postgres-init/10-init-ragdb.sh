#!/bin/sh
set -eu
# The SQL files live in sql/ so that the postgres entrypoint does not run them
# a second time on its own (it executes every top-level *.sql in this folder).

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -v rag_owner_pass="$RAG_DB_OWNER_PASS" \
  -v rag_app_pass="$RAG_DB_PASS" \
  -v rag_ro_pass="$RAG_DB_RO_PASS" \
  -f /docker-entrypoint-initdb.d/sql/20-rag-bootstrap.sql

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -c "ALTER DATABASE \"$POSTGRES_DB\" OWNER TO rag_owner;"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/sql/30-rag-schema.sql

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/sql/40-rag-ranking.sql
