# docker_mcp-rag-pg — Full Omnis RAG Stack with PostgreSQL 18

This folder provides a second Docker setup for the project:

- `postgres` with PostgreSQL 18 and `pgvector`
- `rag-server`
- `mcp-server`

It exists alongside `docker_mcp-rag/`, which targets PostgreSQL on the host. `rag-server` and
`mcp-server` are built from the `docker_mcp-rag/` service folders.

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
    ├── 10-init-ragdb.sh          runs the SQL files below once, on an empty volume
    └── sql/                      not executed directly by the postgres entrypoint
        ├── 20-rag-bootstrap.sql  roles (passwords from .env)
        ├── 30-rag-schema.sql     schema v2 (idempotent, migrates v1)
        └── 40-rag-ranking.sql    rag.search_ranked
```

The SQL files sit in `sql/` because the postgres entrypoint executes every top-level `*.sql` in
`/docker-entrypoint-initdb.d` itself — the bootstrap would otherwise run a second time without its
password variables and fail.

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

### Schema upgrade on an existing volume

The init scripts only run on an empty volume. After a schema change either recreate the database
volume (the data is rebuilt by the import; the model cache volume `hf_cache` stays):

```bash
docker compose rm -sf postgres
docker volume rm docker_mcp-rag-pg_postgres_data
docker compose up -d
python ../scripts/import_to_docker_postgres.py
```

or apply `sql/30-rag-schema.sql` and `sql/40-rag-ranking.sql` in place:

```bash
docker compose exec -T postgres psql -U postgres -d ragdb -v ON_ERROR_STOP=1 < postgres-init/sql/30-rag-schema.sql
docker compose exec -T postgres psql -U postgres -d ragdb -v ON_ERROR_STOP=1 < postgres-init/sql/40-rag-ranking.sql
```

## Import into the Docker PostgreSQL

The chunks and embeddings in `output/` are versioned, so a checkout can be imported directly.
(Rebuilding them is described in [`Documentation/Pipeline_en.md`](../Documentation/Pipeline_en.md).)

**Inside Docker (recommended on servers — no Python on the host, no published database port):**

```bash
cd docker_mcp-rag-pg
docker compose --profile import run --rm importer
```

The `importer` service runs `scripts/import_to_postgres.py` in the rag-server image against the
`postgres` service and exits (~30 s for ~6,000 chunks).

**From the host** (needs the pipeline `.venv` and the published PostgreSQL port), from the repository root:

```bash
python scripts/import_to_docker_postgres.py
```

What it does:

- loads `docker_mcp-rag-pg/.env` if present
- points `scripts/import_to_postgres.py` to the published Docker PostgreSQL port
- passes further arguments through, e.g. `--allow-missing` to import a partial build while the
  embeddings are still being computed

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

## Deploy on an internal Docker server

Everything the server needs is in the repository: code, SQL, chunks and embeddings. The server
needs Docker with the Compose plugin and git — no Python, no GPU. Images and the `pgvector` image are
multi-arch (amd64 and arm64).

### First installation

```bash
git clone https://github.com/SDI76/OmnisDocRAG.git && cd OmnisDocRAG
git switch <branch>                      # e.g. main once the rework is merged
cd docker_mcp-rag-pg
cp .env.example .env
```

Edit `.env`:

| Setting | Server value |
|---|---|
| `POSTGRES_PASSWORD`, `RAG_DB_PASS`, `RAG_DB_OWNER_PASS`, `RAG_DB_RO_PASS` | own values (applied only on the first start of an empty volume) |
| `POSTGRES_BIND_HOST` | `127.0.0.1` — the database stays local; the importer runs inside Docker |
| `RAG_BIND_HOST` | `127.0.0.1` — only the MCP server talks to the rag-server (Docker network) |
| `MCP_BIND_HOST` / `MCP_PORT` | `0.0.0.0` / `3000` — the endpoint the clients use |

```bash
docker compose up -d --build                        # first start: model download ~2.2 GB into hf_cache
docker compose --profile import run --rm importer   # load output/ into the database
docker compose ps                                    # rag-server healthy, mcp-server up
curl -s http://127.0.0.1:7071/health                 # chunk count per corpus
```

The first start of the rag-server takes a few minutes (model download and load); the MCP server starts
when the rag-server is healthy.

Clients connect to `http://<server>:3000/mcp` (Streamable HTTP), e.g. in `.vscode/mcp.json` or `.mcp.json`:

```json
{ "omnis-doc-reference": { "type": "http", "url": "http://<server>:3000/mcp" } }
```

### Update an existing deployment

```bash
cd OmnisDocRAG && git pull
cd docker_mcp-rag-pg
docker compose up -d --build                        # rebuilds rag-server / mcp-server if their code changed
docker compose --profile import run --rm importer   # only needed when output/ changed
```

If the SQL in `postgres-init/sql/` changed (see the git log), apply it before the import — the init
scripts only run on an empty volume:

```bash
docker compose exec -T postgres psql -U postgres -d ragdb -v ON_ERROR_STOP=1 < postgres-init/sql/30-rag-schema.sql
docker compose exec -T postgres psql -U postgres -d ragdb -v ON_ERROR_STOP=1 < postgres-init/sql/40-rag-ranking.sql
```

**Upgrading a server that still runs the v1 stack** (before the rework): recreate the database volume
instead — the data is rebuilt completely by the importer, the model cache stays:

```bash
docker compose rm -sf postgres
docker volume rm docker_mcp-rag-pg_postgres_data
docker compose up -d --build
docker compose --profile import run --rm importer
```

### Security

The MCP endpoint has no authentication. Publish it only on an internal network (or restrict it with
the host firewall); keep `POSTGRES_BIND_HOST` and `RAG_BIND_HOST` at `127.0.0.1`. The rag-server's
`/embed` endpoint computes embeddings on request and should not be reachable from the network.

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

Remove only the database volume (the data is rebuilt by the import):

```bash
docker compose rm -sf postgres
docker volume rm docker_mcp-rag-pg_postgres_data
```

`docker compose down -v` removes **all** volumes, including the ~2.2 GB model cache `hf_cache`.

## Notes

- Passwords are only applied during initial database bootstrap. If you change them
  later, recreate the PostgreSQL volume (see above).
- PostgreSQL 18 expects the persistent volume at `/var/lib/postgresql`, not
  `/var/lib/postgresql/data`. The compose file already uses the PG18-compatible
  mount layout.
- `rag-server` and `mcp-server` are built from the `docker_mcp-rag` service folders, so there is
  only one code path for those services in the repo.
- Container scripts must keep LF line endings; `.gitattributes` enforces this on Windows checkouts.
- The PostgreSQL image is based on the official `pgvector` Docker image for Postgres 18:
  https://github.com/pgvector/pgvector
