"""
import_to_postgres.py — chunks + embeddings → PostgreSQL
========================================================

Reads output/chunks/*_chunks.json and output/embeddings.jsonl and upserts
corpus → document → chunk → embedding. Every chunk is its own document
(external_id = chunk id); parts of one entry share metadata.doc_key.

The chunk row carries the v2 search fields:
  title      entry / section title        (full-text weight A)
  heading    heading path joined with " › " (weight B)
  content    chunk text                    (weights C/D; search_tsv is built by trigger)
  symbols    normalised names documented by the chunk (exact-name boost)

Embeddings must match the current chunk text (hash check) — otherwise run
embed_and_store.py again. Documents that no longer exist in the chunk files are
removed (set DELETE_STALE_DOCS=0 to disable).

    python scripts/import_to_postgres.py
"""

from __future__ import annotations

import sys
import base64
import hashlib
import json
import struct
import logging
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

import psycopg2
import psycopg2.extras

if hasattr(sys.stdout, "reconfigure"):   # Windows pipes default to a legacy code page
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DB_HOST = os.environ["RAG_DB_HOST"]
DB_PORT = int(os.environ.get("RAG_DB_PORT", "5432"))
DB_NAME = os.environ.get("RAG_DB_NAME", "ragdb")
DB_USER = os.environ["RAG_DB_USER"]
DB_PASS = os.environ["RAG_DB_PASS"]
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
DELETE_STALE_DOCS = os.environ.get("DELETE_STALE_DOCS", "1").lower() in {"1", "true", "yes"}

BASE = Path(__file__).resolve().parent.parent
CHUNKS = BASE / "output" / "chunks"
EMBEDDINGS = BASE / "output" / "embeddings.jsonl"
BATCH_SIZE = 200


def norm_symbol(text: str) -> str:
    """Normalisation shared with the rag-server (ragserver.py) — keep both identical."""
    text = text.strip().lower()
    text = re.sub(r"[‘’“”'\"`]", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"(^|[\s.])[$#]", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .?!:;,")


def chunk_symbols(c: dict) -> list[str]:
    """Names a chunk documents: entry names, notation node/members, $names in section titles."""
    m = c["metadata"]
    names: list[str] = []
    if m.get("command_name"):
        names.append(m["command_name"])
    if m.get("function_signature"):
        sig = m["function_signature"]
        names.append(sig)
        if "." in sig:                       # OJSON.$jsontolist() → also "jsontolist"
            names.append(sig.rsplit(".", 1)[-1])
    if c["corpus"] == "omnis-notation":
        if m.get("kind") == "node":
            names.append(c["title"].split(" (")[0])
            names.append(m.get("notation_node", "").rsplit(".", 1)[-1])
        names.extend(re.findall(r"^- `([^`]+)`", c["text"], flags=re.M))
    if c["corpus"] == "omnis-programming":
        names.extend(re.findall(r"[$#]\w+", c["title"]))
    return sorted({s for s in (norm_symbol(n) for n in names) if s})


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_inputs(allow_missing: bool = False) -> tuple[list[dict], dict[str, dict]]:
    chunks: list[dict] = []
    for path in sorted(CHUNKS.glob("*_chunks.json")):
        chunks.extend(json.loads(path.read_text(encoding="utf-8")))
    if not EMBEDDINGS.exists():
        raise SystemExit(f"{EMBEDDINGS} missing — run scripts/embed_and_store.py first")
    emb = {}
    with EMBEDDINGS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                emb[rec["id"]] = rec
    stale = [c["id"] for c in chunks if c["id"] not in emb or emb[c["id"]].get("hash") != text_hash(c["embed_text"])]
    if stale and allow_missing:
        log.warning(f"--allow-missing: skipping {len(stale)} chunks without current embedding")
        missing = set(stale)
        chunks = [c for c in chunks if c["id"] not in missing]
    elif stale:
        raise SystemExit(f"{len(stale)} chunks have no current embedding (e.g. {stale[:3]}) — "
                         f"run scripts/embed_and_store.py first")
    return chunks, emb


def vector_of(rec: dict) -> list[float]:
    """Record vector: compact float32/base64 ("vector") or a JSON number list ("embedding")."""
    if "vector" in rec:
        raw = base64.b64decode(rec["vector"])
        return list(struct.unpack(f"<{len(raw) // 4}f", raw))
    return rec["embedding"]


def vec_literal(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.8g}" for x in v) + "]"


def ensure_corpora(cur, names: set[str]) -> dict[str, str]:
    psycopg2.extras.execute_values(
        cur, "INSERT INTO rag.corpus (name) VALUES %s ON CONFLICT (name) DO NOTHING",
        [(n,) for n in sorted(names)])
    cur.execute("SELECT name, corpus_id::text FROM rag.corpus")
    return dict(cur.fetchall())


def upsert_batch(cur, batch: list[dict], emb: dict[str, dict], corpus_ids: dict[str, str]) -> None:
    rows = []
    for c in batch:
        meta = dict(c["metadata"])
        meta["heading_path"] = c["heading_path"]
        rows.append((
            corpus_ids[c["corpus"]], c["id"], c["title"], json.dumps(meta),
            c["text"], " › ".join(c["heading_path"]), chunk_symbols(c),
            vec_literal(vector_of(emb[c["id"]])),
        ))

    psycopg2.extras.execute_values(cur, """
        INSERT INTO rag.document (corpus_id, external_id, title, meta)
        VALUES %s
        ON CONFLICT (corpus_id, external_id) DO UPDATE
          SET title = EXCLUDED.title, meta = EXCLUDED.meta, updated_at = now()
        """, [(r[0], r[1], r[2], r[3]) for r in rows], template="(%s::uuid, %s, %s, %s::jsonb)")

    psycopg2.extras.execute_values(cur, """
        INSERT INTO rag.chunk (document_id, chunk_index, content, meta, title, heading, symbols)
        SELECT d.document_id, 0, v.content, v.meta::jsonb, v.title, v.heading, v.symbols::text[]
        FROM (VALUES %s) AS v(corpus_id, external_id, content, meta, title, heading, symbols)
        JOIN rag.document d ON d.corpus_id = v.corpus_id::uuid AND d.external_id = v.external_id
        ON CONFLICT (document_id, chunk_index) DO UPDATE
          SET content = EXCLUDED.content, meta = EXCLUDED.meta, title = EXCLUDED.title,
              heading = EXCLUDED.heading, symbols = EXCLUDED.symbols
        """, [(r[0], r[1], r[4], r[3], r[2], r[5], r[6]) for r in rows])

    psycopg2.extras.execute_values(cur, f"""
        INSERT INTO rag.embedding (chunk_id, model, embedding_dim, v)
        SELECT ch.chunk_id, '{EMBED_MODEL}', {EMBED_DIM}, v.vec::vector
        FROM (VALUES %s) AS v(corpus_id, external_id, vec)
        JOIN rag.document d ON d.corpus_id = v.corpus_id::uuid AND d.external_id = v.external_id
        JOIN rag.chunk ch ON ch.document_id = d.document_id AND ch.chunk_index = 0
        ON CONFLICT (chunk_id) DO UPDATE
          SET v = EXCLUDED.v, model = EXCLUDED.model, created_at = now()
        """, [(r[0], r[1], r[7]) for r in rows])


def delete_stale(cur, chunks: list[dict], corpus_ids: dict[str, str]) -> int:
    if not chunks:
        raise RuntimeError("no chunks loaded — refusing to delete everything")
    cur.execute("CREATE TEMP TABLE tmp_expected (corpus_id uuid, external_id text) ON COMMIT DROP")
    psycopg2.extras.execute_values(cur, "INSERT INTO tmp_expected VALUES %s",
                                   [(corpus_ids[c["corpus"]], c["id"]) for c in chunks],
                                   template="(%s::uuid, %s)", page_size=1000)
    cur.execute("""
        DELETE FROM rag.document d
        WHERE d.corpus_id = ANY(%s::uuid[])
          AND NOT EXISTS (SELECT 1 FROM tmp_expected t
                          WHERE t.corpus_id = d.corpus_id AND t.external_id = d.external_id)
        """, (sorted({corpus_ids[c["corpus"]] for c in chunks}),))
    return cur.rowcount


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-missing", action="store_true",
                    help="import only chunks that already have a current embedding (testing a partial "
                         "build); stale documents are not deleted in this mode")
    args = ap.parse_args()
    chunks, emb = load_inputs(args.allow_missing)
    log.info(f"Chunks: {len(chunks)} in {len({c['corpus'] for c in chunks})} corpora")
    log.info(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS,
                            connect_timeout=10, options="-c search_path=rag,public")
    t0 = time.time()
    try:
        with conn.cursor() as cur:
            corpus_ids = ensure_corpora(cur, {c["corpus"] for c in chunks})
            for i in range(0, len(chunks), BATCH_SIZE):
                upsert_batch(cur, chunks[i:i + BATCH_SIZE], emb, corpus_ids)
                print(f"\r  {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}", end="", flush=True)
            print()
            removed = delete_stale(cur, chunks, corpus_ids) if DELETE_STALE_DOCS and not args.allow_missing else 0
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    log.info(f"Imported {len(chunks)} chunks, removed {removed} stale documents in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
