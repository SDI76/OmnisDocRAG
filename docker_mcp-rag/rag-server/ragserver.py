"""
Omnis RAG Server (FastAPI)
==========================

HTTP service behind the MCP front-ends (Docker `mcp-server`, local stdio bridge).

Endpoints
---------
GET  /health            model, database and corpus counts
POST /search            ranked search, compact by default
POST /chunks            full text of chunks by id (second stage of retrieval)
POST /embed             embeddings with the server's model (used by the ingestion)

Retrieval design
----------------
- One global ranking across all corpora (commands, functions, programming,
  notation) instead of a fixed number of hits per corpus.
- Modes: `semantic` (vector), `fulltext` (weighted full text), `hybrid` (both,
  fused with Reciprocal Rank Fusion). Exact names from the query (`$search`,
  `binfrombase64`, `Begin reversible block`) are boosted.
- One hit per entry/section, with a short snippet. The full text is fetched
  on demand via /chunks, which keeps a search response at a few KB.

All ranking happens in the database function `rag.search_ranked`
(docker_mcp-rag-pg/postgres-init/sql/40-rag-ranking.sql).
"""

from __future__ import annotations

import logging
import os
import re
import socket
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _load_env() -> Path:
    """Load `.env` next to this file, or the file named by OMNIS_RAG_ENV_FILE."""
    default_env = Path(__file__).parent / ".env"
    configured_env = os.environ.get("OMNIS_RAG_ENV_FILE", "").strip()
    env_path = Path(configured_env) if configured_env else default_env
    load_dotenv(env_path)
    return env_path


ENV_FILE = _load_env()

import psycopg2
import psycopg2.extras
import psycopg2.pool
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────
DB_HOST = os.environ["RAG_DB_HOST"]
DB_PORT = int(os.environ.get("RAG_DB_PORT", "5432"))
DB_NAME = os.environ.get("RAG_DB_NAME", "ragdb")
DB_USER = os.environ["RAG_DB_USER"]
DB_PASS = os.environ["RAG_DB_PASS"]

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")
PORT = int(os.environ.get("PORT", "7071"))
STRICT_PORT = _as_bool(os.environ.get("STRICT_PORT"), True)

# Fusion weights; the full-text leg is weighted lower because single frequent
# words ("list", "line") match many chunks. Tuned with scripts/eval_retrieval.py.
W_DENSE = float(os.environ.get("RAG_W_DENSE", "1.0"))
W_FTS = float(os.environ.get("RAG_W_FTS", "0.5"))
SNIPPET_CHARS = int(os.environ.get("RAG_SNIPPET_CHARS", "240"))

CORPORA = ("omnis-commands", "omnis-functions", "omnis-programming", "omnis-notation")
CORPUS_ALIASES = {
    "commands": "omnis-commands", "functions": "omnis-functions",
    "programming": "omnis-programming", "notation": "omnis-notation",
}
CORPUS_LABEL = {
    "omnis-commands": "command", "omnis-functions": "function",
    "omnis-programming": "manual", "omnis-notation": "notation",
}
# ─────────────────────────────────────────────────────────────

model: SentenceTransformer | None = None
pool: psycopg2.pool.ThreadedConnectionPool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, pool
    log.info(f"Loading embedding model: {EMBED_MODEL}")
    t = time.time()
    model = SentenceTransformer(EMBED_MODEL)
    model.encode("warm-up", normalize_embeddings=True)   # first call is slow; do it now
    log.info(f"Model loaded and warmed up in {time.time() - t:.1f}s")

    log.info(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME} (user: {DB_USER})")
    pool = psycopg2.pool.ThreadedConnectionPool(
        1, 4, host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        connect_timeout=10, options="-c search_path=rag,public")
    log.info("DB pool ready.")
    yield
    pool.closeall()


app = FastAPI(title="Omnis RAG Server", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"])


@contextmanager
def db_cursor():
    conn = pool.getconn()
    try:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
    finally:
        pool.putconn(conn)


# ── Query analysis ────────────────────────────────────────────

STOPWORDS = set("""
a an the of to in on at for from by with without into onto over under and or not no is are was were be been
being do does did done doing how what which who whom whose why when where there here this that these those it
its i me my we our you your he she they them their can could should would will shall may might must has have
had get gets got use using used via as if then than so such any all each every some more most other only own
same too very just about also between both
wie was welche welcher welches wer warum wann wo der die das den dem des ein eine einer einem einen und oder
nicht kein keine ist sind war mit ohne für von zu im in am an auf aus bei nach über unter ich du er sie es wir
ihr man kann können soll sollen muss müssen wird werden hat haben mein meine dein deine sein seine
""".split())

# German words frequently used in Omnis questions → English doc vocabulary.
# Only the full-text leg needs this; the embedding model is multilingual.
GERMAN_TERMS = {
    "löschen": "delete remove", "lösche": "delete remove", "entfernen": "remove", "zeile": "line",
    "zeilen": "lines", "liste": "list", "listen": "lists", "suchen": "search", "suche": "search",
    "fenster": "window", "feld": "field", "felder": "fields", "klasse": "class", "klassen": "classes",
    "methode": "method", "methoden": "methods", "tabelle": "table", "datei": "file", "dateien": "files",
    "fehler": "error", "fehlerbehandlung": "error handling", "anzeigen": "display", "sortieren": "sort",
    "speichern": "save", "öffnen": "open", "schließen": "close", "aktuelle": "current", "aktuellen": "current",
    "auswählen": "select", "markieren": "select", "hinzufügen": "add", "einfügen": "insert",
    "ersetzen": "replace", "schleife": "loop", "bedingung": "condition", "verbindung": "connection",
    "abfrage": "query", "zeichenkette": "string", "datum": "date", "zahl": "number", "wert": "value",
    "werte": "values", "objekt": "object", "referenz": "reference", "ereignis": "event",
    "ereignisse": "events", "drucken": "print", "bericht": "report", "sitzung": "session",
    "anweisung": "statement", "rückgabewert": "return value", "beispiel": "example",
    "unterschied": "difference", "variable": "variable", "variablen": "variables", "spalte": "column",
    "spalten": "columns", "zeichen": "character", "text": "text", "aufrufen": "call", "senden": "send",
    "alle": "all", "zeit": "time", "tage": "days", "tag": "day", "leer": "empty", "gleich": "equal",
    "rekursion": "recursion", "konvertieren": "convert", "umwandeln": "convert", "lesen": "read",
    "schreiben": "write", "erstellen": "create", "neu": "new", "berechnen": "calculate",
}

SEARCH_SYNTAX = re.compile(r'"|\bOR\b|(^|\s)-\w')


def norm_symbol(text: str) -> str:
    """Normalisation shared with scripts/import_to_postgres.py (keep both identical)."""
    text = text.strip().lower()
    text = re.sub(r"[‘’“”'\"`]", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"(^|[\s.])[$#]", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .?!:;,")


def analyse_query(query: str) -> dict:
    """Full-text terms, search-syntax flag and candidate symbol names."""
    raw_tokens = re.findall(r"[#$]?[\w.]+(?:\(\))?", query, flags=re.UNICODE)
    terms: list[str] = []
    for tok in raw_tokens:
        low = tok.lower()
        if low in GERMAN_TERMS:
            terms.extend(GERMAN_TERMS[low].split())
            continue
        for part in re.split(r"[.]", re.sub(r"[#$()]", "", low)):
            if len(part) > 1 and part not in STOPWORDS and re.fullmatch(r"[a-z0-9_]+", part):
                terms.append(part)
    terms = list(dict.fromkeys(terms))

    symbols: list[str] = []
    whole = norm_symbol(query)
    if whole and len(whole.split()) <= 6:
        symbols.append(whole)
    words = [w for w in re.findall(r"[#$]?[\w.]+(?:\(\))?", query)]
    for tok in words:
        # Tokens that look like Omnis names: $notation, #hashvar, func(), dotted paths, digits
        if re.search(r"[$#().]|\d", tok) or re.search(r"[a-z][A-Z]", tok):
            symbols.append(norm_symbol(tok))
    plain = [w for w in re.findall(r"[\w/&]+", query.lower())]
    for n in range(2, 6):
        for i in range(len(plain) - n + 1):
            symbols.append(norm_symbol(" ".join(plain[i:i + n])))
    symbols = [s for s in dict.fromkeys(symbols) if s]
    return {"terms": terms, "websearch": query if SEARCH_SYNTAX.search(query) else None, "symbols": symbols}


# ── Request / response models ─────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"                       # hybrid | semantic | fulltext
    top_k: int = Field(8, ge=1, le=30)
    corpora: list[str] | str | None = None     # None/"all" = every corpus
    format: str = "text"                       # text (compact, for agents) | json
    w_dense: float | None = None
    w_fts: float | None = None
    # v1 compatibility: `corpus` was a single corpus name; k_* are ignored now.
    corpus: str | None = None


class ChunksRequest(BaseModel):
    ids: list[str]
    format: str = "text"


class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., max_length=256)


def resolve_corpora(value: list[str] | str | None, legacy: str | None) -> list[str] | None:
    items = value if isinstance(value, list) else ([value] if value else [])
    if legacy and not items:
        items = [legacy]
    out = []
    for item in items:
        for part in str(item).split(","):
            name = part.strip().lower()
            if not name or name == "all":
                continue
            name = CORPUS_ALIASES.get(name, name)
            if name not in CORPORA:
                raise HTTPException(400, f"unknown corpus '{part.strip()}' (use {', '.join(CORPORA)})")
            out.append(name)
    return sorted(set(out)) or None


def source_label(meta: dict) -> str:
    src = meta.get("source", "")
    if src == "OmnisDocPack":
        return "Omnis help 11.1"
    pages = ""
    if meta.get("page_start"):
        ps, pe = meta["page_start"], meta.get("page_end") or meta["page_start"]
        pages = f" p.{ps}" if ps == pe else f" p.{ps}-{pe}"
    return f"{src}{pages}"


def make_snippet(content: str, highlighted: str | None) -> str:
    if highlighted and highlighted.strip():
        text = highlighted
    else:
        lines = [l for l in content.split("\n")
                 if l.strip() and not l.startswith("#")
                 and not re.match(r"^(Command group|Function group):", l)]
        text = " ".join(lines)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > SNIPPET_CHARS:
        text = text[:SNIPPET_CHARS].rsplit(" ", 1)[0] + " …"
    return text


def result_row(r: dict) -> dict:
    meta = r["meta"] or {}
    return {
        "id": r["external_id"],
        "corpus": r["corpus"],
        "title": r["title"],
        "heading": r["heading"],
        "source": source_label(meta),
        "score": round(float(r["score"]), 5),
        "dense_rank": r["dense_rank"],
        "fts_rank": r["fts_rank"],
        "exact_symbol": r["exact_symbol"],
        "deprecated": bool(meta.get("deprecated")),
        "part": f"{meta['part']}/{meta['parts']}" if meta.get("parts") else None,
        "snippet": make_snippet(r["content"], r.get("snippet")),
    }


def render_results(query: str, mode: str, results: list[dict]) -> str:
    if not results:
        return f'No Omnis documentation found for "{query}" ({mode}).'
    out = [f'Omnis documentation — {len(results)} results for "{query}" ({mode}):']
    for i, r in enumerate(results, 1):
        label = CORPUS_LABEL.get(r["corpus"], r["corpus"])
        where = r["heading"] if r["corpus"] == "omnis-programming" and r["heading"] else r["title"]
        flags = " [deprecated]" if r["deprecated"] else ""
        part = f" (part {r['part']})" if r["part"] else ""
        out.append(f"{i}. [{label}] {where}{part}{flags} — {r['source']} — id: {r['id']}")
        if r["snippet"]:
            out.append(f"   {r['snippet']}")
    out.append("Full text: get_omnis_doc with one or more ids.")
    return "\n".join(out)


def render_chunks(rows: list[dict], missing: list[str]) -> str:
    out = []
    for r in rows:
        meta = r["meta"] or {}
        head = f"[{r['id']}] {r['heading'] or r['title']} — {source_label(meta)}"
        if r["siblings"]:
            head += f" — other parts: {', '.join(r['siblings'])}"
        out.append(f"{head}\n\n{r['content']}")
    if missing:
        out.append(f"Not found: {', '.join(missing)}")
    return "\n\n---\n\n".join(out)


# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
def health():
    with db_cursor() as cur:
        cur.execute("""
            SELECT co.name, count(ch.chunk_id)::int AS chunks
            FROM rag.corpus co
            LEFT JOIN rag.document d ON d.corpus_id = co.corpus_id
            LEFT JOIN rag.chunk ch ON ch.document_id = d.document_id
            GROUP BY co.name ORDER BY co.name""")
        corpora = {r["name"]: r["chunks"] for r in cur.fetchall()}
    return {"status": "ok", "model": EMBED_MODEL, "corpora": corpora}


@app.post("/embed")
def embed(req: EmbedRequest):
    vecs = model.encode(req.texts, normalize_embeddings=True, batch_size=16, show_progress_bar=False)
    return {"model": EMBED_MODEL, "embeddings": [v.tolist() for v in vecs]}


@app.post("/search")
def search(req: SearchRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(400, "query must not be empty")
    mode = req.mode.lower()
    if mode not in ("hybrid", "semantic", "fulltext"):
        raise HTTPException(400, "mode must be hybrid, semantic or fulltext")
    corpora = resolve_corpora(req.corpora, req.corpus)
    qa = analyse_query(query)

    t0 = time.time()
    vec = None
    if mode in ("hybrid", "semantic"):
        v = model.encode(query, normalize_embeddings=True)
        vec = "[" + ",".join(f"{x:.7f}" for x in v) + "]"
    embed_ms = (time.time() - t0) * 1000

    use_fts = mode in ("hybrid", "fulltext")
    t1 = time.time()
    with db_cursor() as cur:
        cur.execute(
            """SELECT * FROM rag.search_ranked(%s::vector(1024), %s::text[], %s::text, %s::text[], %s::text[],
                                              %s, 60, %s, %s, 60)""",
            (vec,
             qa["terms"] if use_fts else None,
             qa["websearch"] if use_fts else None,
             qa["symbols"],
             corpora,
             req.top_k,
             req.w_dense if req.w_dense is not None else W_DENSE,
             req.w_fts if req.w_fts is not None else W_FTS))
        rows = cur.fetchall()
    search_ms = (time.time() - t1) * 1000

    results = [result_row(r) for r in rows]
    log.info(f"search mode={mode} q={query!r:.60} hits={len(results)} "
             f"embed={embed_ms:.0f}ms db={search_ms:.0f}ms")
    if req.format == "json":
        return {"query": query, "mode": mode, "corpora": corpora, "terms": qa["terms"],
                "results": results, "embed_ms": round(embed_ms), "search_ms": round(search_ms)}
    return {"text": render_results(query, mode, results)}


@app.post("/chunks")
def chunks(req: ChunksRequest):
    ids = [i.strip() for i in req.ids if i.strip()][:20]
    if not ids:
        raise HTTPException(400, "ids must not be empty")
    with db_cursor() as cur:
        cur.execute("""
            SELECT d.external_id AS id, co.name AS corpus, ch.title, ch.heading, ch.content, ch.meta,
                   ARRAY(SELECT d2.external_id FROM rag.document d2
                         WHERE d2.meta->>'doc_key' = d.meta->>'doc_key'
                           AND d2.external_id <> d.external_id
                           AND d.meta->>'parts' IS NOT NULL
                         ORDER BY (d2.meta->>'part')::int) AS siblings
            FROM rag.document d
            JOIN rag.corpus co ON co.corpus_id = d.corpus_id
            JOIN rag.chunk ch ON ch.document_id = d.document_id
            WHERE d.external_id = ANY(%s)""", (ids,))
        found = {r["id"]: r for r in cur.fetchall()}
    rows = [found[i] for i in ids if i in found]
    missing = [i for i in ids if i not in found]
    if req.format == "json":
        return {"chunks": [{**r, "source": source_label(r["meta"] or {})} for r in rows], "missing": missing}
    return {"text": render_chunks(rows, missing)}


# ── Local start ───────────────────────────────────────────────

def find_available_port(host: str, preferred_port: int, max_tries: int = 50) -> int:
    for port in range(preferred_port, preferred_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if probe.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(f"No free port found in range {preferred_port}-{preferred_port + max_tries - 1}")


def is_port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return probe.connect_ex((host, port)) != 0


if __name__ == "__main__":
    import uvicorn

    host = "127.0.0.1"
    actual_port = PORT
    log.info(f"Startup config: env_file={ENV_FILE}, host={host}, port={PORT}, strict_port={STRICT_PORT}")
    if STRICT_PORT:
        if not is_port_free(host, PORT):
            raise RuntimeError(f"Configured port {PORT} is already in use on {host}.")
    else:
        actual_port = find_available_port(host, PORT)
        if actual_port != PORT:
            log.warning(f"Requested PORT={PORT} is unavailable on {host}. Using PORT={actual_port} instead.")
    uvicorn.run(app, host=host, port=actual_port, log_level="info")
