#!/bin/sh
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -v rag_owner_pass="$RAG_DB_OWNER_PASS" \
  -v rag_app_pass="$RAG_DB_PASS" \
  -v rag_ro_pass="$RAG_DB_RO_PASS" \
  -f /docker-entrypoint-initdb.d/20-rag-bootstrap.sql

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -c "ALTER DATABASE \"$POSTGRES_DB\" OWNER TO rag_owner;"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/30-rag-schema.sql

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -f /docker-entrypoint-initdb.d/40-rag-ranking.sql
