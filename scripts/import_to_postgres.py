"""
import_to_postgres.py — embeddings.jsonl → PostgreSQL
Reads output/embeddings.jsonl and upserts into ragdb:
  corpus → document → chunk → embedding

Each line in embeddings.jsonl:
  {"id": "cmd_calculate", "text": "...", "metadata": {...}, "embedding": [...1024 floats...]}

The metadata.source field determines the corpus:
  "CommandRef"       → omnis-commands
  "FunctionRef"      → omnis-functions
  "Programming_Omnis"→ omnis-programming

Run:
  python import_to_postgres.py

Supports resume: already-imported chunks are skipped via ON CONFLICT DO UPDATE.
Also performs full-sync cleanup by default: stale documents that are no longer
present in embeddings.jsonl are removed from the three doc corpora.
"""

import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────
DB_HOST     = os.environ["RAG_DB_HOST"]
DB_PORT     = int(os.environ.get("RAG_DB_PORT", "5432"))
DB_NAME     = os.environ.get("RAG_DB_NAME", "ragdb")
DB_USER     = os.environ["RAG_DB_USER"]
DB_PASS     = os.environ["RAG_DB_PASS"]

EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM   = 1024

JSONL_PATH  = Path(__file__).parent.parent / "output" / "embeddings.jsonl"
BATCH_SIZE  = 200
# Read from scripts/.env (loaded above): set DELETE_STALE_DOCS=0 for upsert-only mode.
DELETE_STALE_DOCS = os.environ.get("DELETE_STALE_DOCS", "1").lower() in {"1", "true", "yes"}
# ─────────────────────────────────────────────────────────────

SOURCE_TO_CORPUS = {
    "CommandRef":        "omnis-commands",
    "FunctionRef":       "omnis-functions",
    "Programming_Omnis": "omnis-programming",
}


def connect() -> psycopg2.extensions.connection:
    log.info(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
        connect_timeout=10,
        options="-c search_path=rag,public",
    )
    return conn


def load_corpus_ids(cur) -> dict[str, str]:
    cur.execute("SELECT name, corpus_id FROM rag.corpus")
    ids = {row[0]: str(row[1]) for row in cur.fetchall()}
    missing = [c for c in SOURCE_TO_CORPUS.values() if c not in ids]
    if missing:
        raise RuntimeError(
            f"Missing corpora in DB: {missing}\n"
            f"Run setup_db.sql first."
        )
    log.info(f"Corpora loaded: {list(ids.keys())}")
    return ids


def vec_literal(embedding: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in embedding) + "]"


def upsert_batch(cur, batch: list[dict], corpus_ids: dict[str, str]) -> tuple[int, int]:
    """
    Upsert one batch. Returns (inserted_or_updated, skipped_unknown_source).
    Uses a temporary table for fast bulk insert, then merges into final tables.
    """
    skipped = 0
    rows = []

    for record in batch:
        meta   = record.get("metadata", {})
        source = meta.get("source", "")
        corpus = SOURCE_TO_CORPUS.get(source)

        if not corpus:
            log.warning(f"Unknown source '{source}' for id={record['id']} — skipping")
            skipped += 1
            continue

        rows.append((
            record["id"],                   # external_id / chunk stable id
            corpus_ids[corpus],             # corpus_id (uuid)
            source,                         # title
            meta.get("command_name")
                or meta.get("function_signature")
                or meta.get("section")
                or record["id"],            # human-readable title
            record["text"],                 # chunk content
            json.dumps(meta),               # metadata jsonb
            vec_literal(record["embedding"]),  # vector literal
        ))

    if not rows:
        return 0, skipped

    # ── 1) Upsert document (one per chunk — chunk IS the document here) ──
    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO rag.document (corpus_id, external_id, title, meta)
        VALUES %s
        ON CONFLICT (corpus_id, external_id) DO UPDATE
          SET title      = EXCLUDED.title,
              meta       = rag.document.meta || EXCLUDED.meta,
              updated_at = now()
        """,
        [(r[1], r[0], r[3], r[5]) for r in rows],  # corpus_id, external_id, title, meta
        template="(%s, %s, %s, %s::jsonb)",
    )

    # ── 2) Upsert chunk ──────────────────────────────────────
    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO rag.chunk (document_id, chunk_index, content, meta)
        SELECT d.document_id, 0, v.content, v.meta::jsonb
        FROM (VALUES %s) AS v(corpus_id, external_id, content, meta)
        JOIN rag.document d
          ON d.corpus_id = v.corpus_id::uuid
         AND d.external_id = v.external_id
        ON CONFLICT (document_id, chunk_index) DO UPDATE
          SET content = EXCLUDED.content,
              meta    = rag.chunk.meta || EXCLUDED.meta
        """,
        [(r[1], r[0], r[4], r[5]) for r in rows],  # corpus_id, external_id, content, meta
        template="(%s::uuid, %s, %s, %s)",
    )

    # ── 3) Upsert embedding ──────────────────────────────────
    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO rag.embedding (chunk_id, model, embedding_dim, v)
        SELECT ch.chunk_id, %s, %s, v.vec::vector
        FROM (VALUES %%s) AS v(corpus_id, external_id, vec)
        JOIN rag.document d
          ON d.corpus_id = v.corpus_id::uuid
         AND d.external_id = v.external_id
        JOIN rag.chunk ch
          ON ch.document_id = d.document_id
         AND ch.chunk_index = 0
        ON CONFLICT (chunk_id) DO UPDATE
          SET v          = EXCLUDED.v,
              model      = EXCLUDED.model,
              created_at = now()
        """ % (f"'{EMBED_MODEL}'", EMBED_DIM),
        [(r[1], r[0], r[6]) for r in rows],  # corpus_id, external_id, vec
        template="(%s::uuid, %s, %s)",
    )

    return len(rows), skipped


def delete_stale_documents(
    cur,
    expected_doc_keys: set[tuple[str, str]],
    corpus_ids: dict[str, str],
) -> int:
    """
    Delete documents from the three doc corpora that are not in current import.
    Related chunk/embedding rows are removed by ON DELETE CASCADE.
    """
    if not expected_doc_keys:
        raise RuntimeError(
            "No valid records found for stale cleanup. "
            "Aborting deletion to avoid accidental full wipe."
        )

    cur.execute(
        """
        CREATE TEMP TABLE tmp_expected_docs (
          corpus_id uuid NOT NULL,
          external_id text NOT NULL,
          PRIMARY KEY (corpus_id, external_id)
        ) ON COMMIT DROP
        """
    )

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO tmp_expected_docs (corpus_id, external_id)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        [(corpus_ids[corpus], external_id) for corpus, external_id in expected_doc_keys],
        template="(%s::uuid, %s)",
        page_size=1000,
    )

    cur.execute(
        """
        WITH target_corpora AS (
          SELECT corpus_id
          FROM rag.corpus
          WHERE name = ANY(%s)
        )
        DELETE FROM rag.document d
        USING target_corpora tc
        WHERE d.corpus_id = tc.corpus_id
          AND NOT EXISTS (
            SELECT 1
            FROM tmp_expected_docs ted
            WHERE ted.corpus_id = d.corpus_id
              AND ted.external_id = d.external_id
          )
        """,
        (list(SOURCE_TO_CORPUS.values()),),
    )
    return cur.rowcount


def main() -> None:
    if not JSONL_PATH.exists():
        log.error(f"File not found: {JSONL_PATH}")
        log.error("Run embed_and_store.py first.")
        return

    # Count lines
    total_lines = sum(1 for l in JSONL_PATH.open(encoding="utf-8") if l.strip())
    log.info(f"Input: {JSONL_PATH} ({total_lines} records)")

    conn = connect()
    conn.autocommit = False

    with conn.cursor() as cur:
        corpus_ids = load_corpus_ids(cur)

    imported = 0
    skipped  = 0
    errors   = 0
    removed  = 0
    t_start  = time.time()
    expected_doc_keys: set[tuple[str, str]] = set()

    with JSONL_PATH.open(encoding="utf-8") as f:
        batch: list[dict] = []

        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                log.warning(f"Line {line_num}: JSON parse error — {e}")
                errors += 1
                continue

            meta = record.get("metadata", {})
            source = meta.get("source", "")
            corpus = SOURCE_TO_CORPUS.get(source)
            if corpus:
                expected_doc_keys.add((corpus, record["id"]))

            batch.append(record)

            if len(batch) >= BATCH_SIZE:
                try:
                    with conn.cursor() as cur:
                        n, s = upsert_batch(cur, batch, corpus_ids)
                    conn.commit()
                    imported += n
                    skipped  += s
                except Exception as e:
                    conn.rollback()
                    log.error(f"Batch error at line {line_num}: {e}")
                    errors += len(batch)
                batch = []

            # Progress
            if line_num % BATCH_SIZE == 0:
                elapsed  = time.time() - t_start
                rate     = line_num / elapsed
                remaining = (total_lines - line_num) / rate if rate else 0
                print(
                    f"\r  {line_num}/{total_lines} "
                    f"({line_num/total_lines*100:.1f}%)  "
                    f"{rate:.0f} rec/s  ETA {remaining:.0f}s   ",
                    end="", flush=True,
                )

        # Final batch
        if batch:
            try:
                with conn.cursor() as cur:
                    n, s = upsert_batch(cur, batch, corpus_ids)
                conn.commit()
                imported += n
                skipped  += s
            except Exception as e:
                conn.rollback()
                log.error(f"Final batch error: {e}")
                errors += len(batch)

    if DELETE_STALE_DOCS:
        try:
            with conn.cursor() as cur:
                removed = delete_stale_documents(cur, expected_doc_keys, corpus_ids)
            conn.commit()
            if removed > 0:
                log.info(f"Stale documents removed: {removed}")
            else:
                log.info("Stale documents removed: 0")
        except Exception as e:
            conn.rollback()
            log.error(f"Stale cleanup error: {e}")
            errors += 1
    else:
        log.info("Stale cleanup disabled (DELETE_STALE_DOCS=0)")

    conn.close()

    elapsed = time.time() - t_start
    print()
    log.info("=" * 50)
    log.info(f"Done in {elapsed:.1f}s")
    log.info(f"  Imported : {imported}")
    log.info(f"  Skipped  : {skipped} (unknown source)")
    log.info(f"  Removed  : {removed} (stale documents)")
    log.info(f"  Errors   : {errors}")
    log.info("=" * 50)

    if imported > 0:
        log.info("Run VACUUM ANALYZE to optimize indexes:")
        log.info("  psql -U rag_owner -d ragdb -c 'VACUUM ANALYZE rag.embedding; VACUUM ANALYZE rag.chunk;'")


if __name__ == "__main__":
    main()
