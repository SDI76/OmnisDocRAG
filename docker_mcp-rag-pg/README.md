# docker_mcp-rag-pg — Full Omnis RAG Stack with PostgreSQL 18

This folder provides a second Docker setup for the project:

- `postgres` with PostgreSQL 18 and `pgvector`
- `rag-server`
- `mcp-server`

It exists alongside `docker_mcp-rag/`, which still targets your local PostgreSQL.
Nothing in the existing local stack or in `scripts/` needs to be changed.

## What this stack is for

Use this setup when you want the project to work out of the box on a fresh machine:

- no local PostgreSQL installation required
- schema and roles are created automatically on first start
- embeddings can be imported from the project into the container database
- the existing `.vscode/mcp.json` entry `omnis-rag-docker` continues to work

## Files

```text
docker_mcp-rag-pg/
├── docker-compose.yml
├── .env.example
├── README.md
└── postgres-init/
    ├── 10-init-ragdb.sh
    ├── 20-rag-bootstrap.sql
    ├── 30-rag-schema.sql
    └── 40-rag-ranking.sql
```

## First start

1. Create the env file:

```bash
cp .env.example .env
```

2. Adjust passwords and ports in `.env`.

The PostgreSQL host port is configurable through:

```env
POSTGRES_HOST_PORT=5432
```

If you want the database reachable from other machines, also change:

```env
POSTGRES_BIND_HOST=0.0.0.0
```

3. Start the stack:

```bash
cd docker_mcp-rag-pg
docker compose up --build -d
```

On the first start, PostgreSQL initializes the database volume and runs the SQL
from `postgres-init/`. The RAG server then waits for the database and starts as soon
as it can connect and load the embedding model.

## Import embeddings into the Docker PostgreSQL

The existing import pipeline stays untouched.

Use the new helper from the repository root:

```bash
python scripts/import_to_docker_postgres.py
```

What it does:

- loads `docker_mcp-rag-pg/.env` if present
- points `scripts/import_to_postgres.py` to the published Docker PostgreSQL port
- keeps the original import script unchanged

You can use a custom env file if needed:

```bash
python scripts/import_to_docker_postgres.py --env-file docker_mcp-rag-pg/.env
```

## Optimize after import

After a larger import, run `VACUUM ANALYZE` inside the PostgreSQL container so the
planner and indexes are up to date:

```bash
cd docker_mcp-rag-pg
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.embedding;"
docker compose exec postgres psql -U rag_owner -d ragdb -c "VACUUM ANALYZE rag.chunk;"
```

Important:

- Run each `VACUUM` in its own `psql -c` call.
- `VACUUM` cannot run inside a transaction block, so do not combine both statements
  into one single `-c`.

## Connect VS Code

The workspace already contains:

```json
{
  "servers": {
    "omnis-rag-docker": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

After the stack is up, restart the MCP server in VS Code and connect to
`omnis-rag-docker`.

## Common commands

Start:

```bash
docker compose up --build -d
```

Logs:

```bash
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f rag-server
docker compose logs -f mcp-server
```

Stop:

```bash
docker compose down
```

Stop and remove the database volume too:

```bash
docker compose down -v
```

## Notes

- Passwords are only applied during initial database bootstrap. If you change them
  later, recreate the PostgreSQL volume with `docker compose down -v`.
- PostgreSQL 18 expects the persistent volume at `/var/lib/postgresql`, not
  `/var/lib/postgresql/data`. The compose file already uses the PG18-compatible
  mount layout.
- `rag-server` and `mcp-server` are built from the existing `docker_mcp-rag` service
  folders, so there is only one code path for those services in the repo.
- The PostgreSQL image is based on the official `pgvector` Docker image for Postgres 18:
  https://github.com/pgvector/pgvector
