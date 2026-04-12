"""
Omnis RAG Server (FastAPI)
=========================

Purpose
-------
This server provides a local HTTP interface (`/search`) through which
agents and tools (for example the MCP bridge) can search Omnis documentation semantically.

Per-request flow
----------------
1. The query text is vectorized with a local embedding model.
2. Hybrid retrieval (vector + full-text/BM25) is executed against PostgreSQL.
3. Results are returned as structured chunks and as `context_text`.

Operating mode
--------------
- Runs on `127.0.0.1:7071` by default.
- With `STRICT_PORT=true`, the server exits intentionally on port conflicts
    instead of silently falling back to other ports.
"""

import os
import time
import logging
import socket
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool) -> bool:
    """Robustly converts typical string booleans into Python booleans."""
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _load_env() -> Path:
    """
    Loads configuration from an env file.
    Uses the local `.env` next to `ragserver.py` in dev setups.
    """
    default_env = Path(__file__).parent / ".env"
    configured_env = os.environ.get("OMNIS_RAG_ENV_FILE", "").strip()
    env_path = Path(configured_env) if configured_env else default_env
    load_dotenv(env_path)
    return env_path


ENV_FILE = _load_env()

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Config (from .env) ────────────────────────────────────────
# The DB parameters are intentionally required so misconfiguration is visible
# immediately at startup.
DB_HOST = os.environ["RAG_DB_HOST"]
DB_PORT = int(os.environ.get("RAG_DB_PORT", "5432"))
DB_NAME = os.environ.get("RAG_DB_NAME", "ragdb")
DB_USER = os.environ["RAG_DB_USER"]
DB_PASS = os.environ["RAG_DB_PASS"]

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")
# 7071 matches the MCP bridge configuration in the workspace.
PORT = int(os.environ.get("PORT", "7071"))
# Strict port mode prevents the service and MCP bridge from drifting apart unexpectedly.
STRICT_PORT = _as_bool(os.environ.get("STRICT_PORT"), True)
# ─────────────────────────────────────────────────────────────

# Global runtime objects (initialized during startup).
model: SentenceTransformer = None
db_conn = None
function_exists_cache: dict[str, bool] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifecycle:
    - Start: load model + connect to DB
    - Stop: close the DB connection cleanly
    """
    global model, db_conn

    log.info(f"Loading embedding model: {EMBED_MODEL}")
    t = time.time()
    model = SentenceTransformer(EMBED_MODEL)
    log.info(f"Model loaded in {time.time()-t:.1f}s")

    log.info(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME} (user: {DB_USER})")
    db_conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=10,
        options="-c search_path=rag,public",
    )
    db_conn.autocommit = True
    log.info("DB connected. Ready.")

    yield

    db_conn.close()


app = FastAPI(title="Omnis RAG Server", lifespan=lifespan)
# Open CORS so local tools/extensions can connect without origin issues.
app.add_middleware(CORSMiddleware, allow_origins=["*"])


# ── Request / Response models ─────────────────────────────────

class SearchRequest(BaseModel):
    """Input model for `/search`."""
    query:         str
    # Defaults are aligned with the bridge strategy (mode-neutral baseline mix).
    k_commands:    int = 4
    k_functions:   int = 4
    k_programming: int = 10
    corpus:        str = "all"   # "all" | "omnis-commands" | "omnis-functions" | "omnis-programming"


class Chunk(BaseModel):
    """A single retrieval result."""
    chunk_id:    str
    corpus_name: str
    content:     str
    rrf_score:   float
    dense_rank:  int | None
    fts_rank:    int | None
    meta:        dict


class SearchResponse(BaseModel):
    """HTTP response model for `/search`."""
    query:        str
    chunks:       list[Chunk]
    context_text: str           # pre-formatted for Copilot injection
    embed_ms:     float
    search_ms:    float


# ── Helpers ───────────────────────────────────────────────────

def embed(text: str) -> list[float]:
    """Generates normalized embeddings for a query."""
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def vec_to_pg(v: list[float]) -> str:
    """Converts a Python vector into a pgvector literal (`[x,y,...]`)."""
    return "[" + ",".join(f"{x:.8f}" for x in v) + "]"


def rag_function_exists(function_name: str) -> bool:
    """
    Checks once whether optional DB functions exist.

    The result is cached to avoid extra DB metadata queries on each request.
    """
    cached = function_exists_cache.get(function_name)
    if cached is not None:
        return cached

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'rag'
                  AND p.proname = %s
            )
            """,
            (function_name,),
        )
        exists = bool(cur.fetchone()[0])

    function_exists_cache[function_name] = exists
    return exists


def search_corpus_inline(query_vec: list[float], query_text: str,
                         corpus_name: str, top_k: int) -> list[dict]:
    """
    SQL fallback for hybrid retrieval without DB helper functions.

    Uses Reciprocal Rank Fusion (RRF) over:
    - vector ranking (`embedding <=> query_vec`)
    - full-text ranking (`ts_rank_cd`)
    """
    # DOMAIN: This path is the "no-magic" fallback if DB helper functions
    # (`rag.search_hybrid` / `rag.search_omnis_docs`) are missing.
    # Benefit: the server remains functional as long as the base tables exist.
    with db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            -- 1) Resolve target corpus (name -> corpus_id)
            WITH target_corpus AS (
                SELECT corpus_id
                FROM rag.corpus
                WHERE name = %s::text
            ),
            -- 2) Full-text hits (lexical relevance)
            fts_hits AS (
                SELECT
                    ch.chunk_id,
                    row_number() OVER (
                        ORDER BY ts_rank_cd(ch.content_tsv, websearch_to_tsquery('simple', %s::text)) DESC
                    ) AS rank_fts
                FROM rag.chunk ch
                JOIN rag.document d ON d.document_id = ch.document_id
                JOIN target_corpus tc ON tc.corpus_id = d.corpus_id
                WHERE ch.content_tsv @@ websearch_to_tsquery('simple', %s::text)
                LIMIT %s::integer
            ),
            -- 3) Vector hits (semantic relevance)
            vec_hits AS (
                SELECT
                    e.chunk_id,
                    row_number() OVER (ORDER BY e.v <=> %s::vector(1024)) AS rank_vec
                FROM rag.embedding e
                JOIN rag.chunk ch ON ch.chunk_id = e.chunk_id
                JOIN rag.document d ON d.document_id = ch.document_id
                JOIN target_corpus tc ON tc.corpus_id = d.corpus_id
                LIMIT %s::integer
            ),
            -- 4) Reciprocal Rank Fusion (RRF): robustly combines both rankings
            rrf AS (
                SELECT
                    COALESCE(f.chunk_id, v.chunk_id) AS chunk_id,
                    COALESCE(1.0 / (60 + f.rank_fts), 0.0) + COALESCE(1.0 / (60 + v.rank_vec), 0.0) AS rrf_score,
                    f.rank_fts,
                    v.rank_vec
                FROM fts_hits f
                FULL OUTER JOIN vec_hits v ON f.chunk_id = v.chunk_id
            )
            -- 5) Load hit metadata and sort by combined relevance
            SELECT
                r.chunk_id,
                %s::text AS corpus_name,
                d.title,
                ch.content,
                r.rrf_score,
                r.rank_vec AS dense_rank,
                r.rank_fts AS fts_rank,
                ch.meta
            FROM rrf r
            JOIN rag.chunk ch ON ch.chunk_id = r.chunk_id
            JOIN rag.document d ON d.document_id = ch.document_id
            ORDER BY r.rrf_score DESC
            LIMIT %s::integer
            """,
            (
                # Placeholder order must match the SQL parameter order exactly.
                corpus_name,
                query_text,
                query_text,
                top_k,
                vec_to_pg(query_vec),
                top_k,
                corpus_name,
                top_k,
            ),
        )
        return [dict(r) for r in cur.fetchall()]


def search_all(query_vec: list[float], query_text: str,
               k_commands: int, k_functions: int, k_programming: int) -> list[dict]:
    """
    Runs a search across all Omnis corpora.

    Prefers `rag.search_omnis_docs` and falls back to inline SQL per corpus
    if the DB function is unavailable.
    """
    if not rag_function_exists("search_omnis_docs"):
        log.warning(
            "DB function rag.search_omnis_docs not found. Using inline hybrid SQL fallback."
        )
        # BUSINESS RULE: for `corpus=all`, the partial corpora are searched separately
        # and then sorted together by score.
        rows = []
        rows.extend(search_corpus_inline(query_vec, query_text, "omnis-commands", k_commands))
        rows.extend(search_corpus_inline(query_vec, query_text, "omnis-functions", k_functions))
        rows.extend(search_corpus_inline(query_vec, query_text, "omnis-programming", k_programming))
        # SIDE EFFECT: ordering is intentionally re-sorted globally
        # so no corpus is artificially preferred.
        rows.sort(key=lambda row: row.get("rrf_score", 0.0), reverse=True)
        return rows

    # Primary path: DB function encapsulates the optimized multi-corpus logic.
    with db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM rag.search_omnis_docs(%s::vector(1024), %s::text, %s::integer, %s::integer, %s::integer)",
            (vec_to_pg(query_vec), query_text, k_commands, k_functions, k_programming)
        )
        return [dict(r) for r in cur.fetchall()]


def search_corpus(query_vec: list[float], query_text: str,
                  corpus_name: str, top_k: int) -> list[dict]:
    """
    Runs a search in exactly one corpus.

    Prefers `rag.search_hybrid` and falls back to inline SQL when needed.
    """
    if not rag_function_exists("search_hybrid"):
        log.warning(
            "DB function rag.search_hybrid not found. Using inline hybrid SQL fallback."
        )
        return search_corpus_inline(query_vec, query_text, corpus_name, top_k)

    # Primary path for single-corpus search via the DB function API.
    with db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            -- `search_hybrid` already returns RRF-scored hits.
            SELECT h.chunk_id, %s::text AS corpus_name, h.title, h.content,
                   h.rrf_score, h.dense_rank, h.fts_rank, h.meta
            FROM rag.search_hybrid(
                %s::vector(1024), %s::text,
                (SELECT corpus_id FROM rag.corpus WHERE name = %s),
                %s::integer
            ) h
            """,
            (corpus_name, vec_to_pg(query_vec), query_text, corpus_name, top_k)
        )
        return [dict(r) for r in cur.fetchall()]


def format_context(chunks: list[dict]) -> str:
    """
    Condenses results into a prompt-ready context block.

    The text is structured so agents can quickly recognize signatures, commands,
    and conceptual guidance.
    """
    sections = {
        "omnis-commands":    [],
        "omnis-functions":   [],
        "omnis-programming": [],
        "omnis-code":        [],
    }
    for c in chunks:
        sections.get(c["corpus_name"], sections["omnis-programming"]).append(c)

    out = ["## Relevant Omnis Studio Documentation\n"]

    if sections["omnis-commands"]:
        out.append("### Commands")
        for c in sections["omnis-commands"]:
            name = c.get("meta", {}).get("command_name", "")
            out.append(f"**{name}**\n{c['content']}\n")

    if sections["omnis-functions"]:
        out.append("### Functions")
        for c in sections["omnis-functions"]:
            name = c.get("meta", {}).get("function_signature", "")
            out.append(f"**{name}**\n{c['content']}\n")

    if sections["omnis-programming"]:
        out.append("### Concepts & Patterns")
        for c in sections["omnis-programming"]:
            out.append(c["content"] + "\n")

    if sections["omnis-code"]:
        out.append("### Code Examples from Project")
        for c in sections["omnis-code"]:
            out.append(c["content"] + "\n")

    return "\n".join(out)


def find_available_port(host: str, preferred_port: int, max_tries: int = 50) -> int:
    """Returns the next free port starting from `preferred_port`."""
    for port in range(preferred_port, preferred_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if probe.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(
        f"No free port found in range {preferred_port}-{preferred_port + max_tries - 1}"
    )


def is_port_free(host: str, port: int) -> bool:
    """Lightweight socket probe for a specific port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return probe.connect_ex((host, port)) != 0


# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Minimal liveness endpoint for service and MCP checks."""
    return {"status": "ok", "model": EMBED_MODEL}


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    """
    Core retrieval endpoint.

    Expects a query plus optional K tuning values and returns hits together with
    formatted context and latency metrics.
    """
    if not req.query.strip():
        raise HTTPException(400, "query must not be empty")

    # 1) Vectorize query
    t0 = time.time()
    query_vec = embed(req.query)
    embed_ms = (time.time() - t0) * 1000

    # 2) Search (all corpora or a single corpus)
    t1 = time.time()
    try:
        if req.corpus == "all":
            rows = search_all(query_vec, req.query,
                              req.k_commands, req.k_functions, req.k_programming)
        else:
            top_k = req.k_commands + req.k_functions + req.k_programming
            rows = search_corpus(query_vec, req.query, req.corpus, top_k)
    except Exception as e:
        log.error(f"DB error: {e}")
        raise HTTPException(500, f"Database error: {e}")
    search_ms = (time.time() - t1) * 1000

    # 3) Serialize DB rows into the API model
    chunks = [
        Chunk(
            chunk_id=str(r["chunk_id"]),
            corpus_name=r["corpus_name"],
            content=r["content"],
            rrf_score=float(r["rrf_score"]),
            dense_rank=r.get("dense_rank"),
            fts_rank=r.get("fts_rank"),
            meta=r.get("meta") or {},
        )
        for r in rows
    ]

    log.info(
        f"query={req.query!r:.50} "
        f"chunks={len(chunks)} embed={embed_ms:.0f}ms search={search_ms:.0f}ms"
    )

    # 4) Return raw chunks together with prompt-ready context
    return SearchResponse(
        query=req.query,
        chunks=chunks,
        context_text=format_context([c.model_dump() for c in chunks]),
        embed_ms=embed_ms,
        search_ms=search_ms,
    )


if __name__ == "__main__":
    # Local direct start (for example debug/service wrapper)
    import uvicorn

    host = "127.0.0.1"
    actual_port = PORT

    log.info(
        f"Startup config: env_file={ENV_FILE}, host={host}, port={PORT}, strict_port={STRICT_PORT}"
    )

    if STRICT_PORT:
        # Explicit fail-fast so the MCP bridge does not silently point to the wrong port.
        if not is_port_free(host, PORT):
            raise RuntimeError(
                f"Configured port {PORT} is already in use on {host}. Stop the conflicting process or change PORT."
            )
    else:
        # Optional dev mode: fall back to the next free port.
        actual_port = find_available_port(host, PORT)
        if actual_port != PORT:
            log.warning(
                f"Requested PORT={PORT} is unavailable on {host}. Using PORT={actual_port} instead."
            )

    uvicorn.run(app, host=host, port=actual_port, log_level="info")
