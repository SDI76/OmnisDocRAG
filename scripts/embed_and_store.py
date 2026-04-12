"""
embed_and_store.py — JSON Chunks → JSONL with embeddings
Reads all three chunk files, embeds via sentence-transformers (bge-m3), writes JSONL.

Output: output/embeddings.jsonl
Each line: {"id": "...", "text": "...", "metadata": {...}, "embedding": [...1024 floats...]}

The "text" field already contains the metadata prefix (e.g.
"Command: Calculate | Group: Calculations | Flag: YES | ...").
That prefix is embedded together with the content — intentional, improves retrieval.

Usage:
  python embed_and_store.py           # resume from existing JSONL
  python embed_and_store.py --force   # wipe JSONL and re-embed from scratch
                                      # required after chunk rebuild (prefix/content changes)

First run downloads BAAI/bge-m3 (~2 GB) to ~/.cache/huggingface/
"""

import json
import sys
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer

# ── Config ────────────────────────────────────────────────────
EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM   = 1024
BATCH_SIZE  = 64      # chunks per encode call (sentence-transformers handles memory)

BASE   = Path(__file__).parent.parent
CHUNKS = [
    BASE / "output" / "chunks" / "commands_chunks.json",
    BASE / "output" / "chunks" / "functions_chunks.json",
    BASE / "output" / "chunks" / "programming_chunks.json",
]
OUTPUT = BASE / "output" / "embeddings.jsonl"
# ─────────────────────────────────────────────────────────────

model: SentenceTransformer = None


def embed_batch(texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    result = [emb.tolist() for emb in embeddings]
    for emb in result:
        if len(emb) != EMBED_DIM:
            raise ValueError(f"Unexpected dim: {len(emb)} (expected {EMBED_DIM})")
    return result


def load_all_chunks() -> list[dict]:
    chunks = []
    for path in CHUNKS:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"  {path.name}: {len(data)} chunks")
        chunks.extend(data)
    return chunks


def already_embedded(output_path: Path) -> set[str]:
    """Return set of IDs already in the output file (for resume support)."""
    if not output_path.exists():
        return set()
    done = set()
    with output_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    done.add(json.loads(line)["id"])
                except Exception:
                    pass
    return done


def main() -> None:
    global model

    force = "--force" in sys.argv

    print("=== Embedding ===")
    print(f"Model:  {EMBED_MODEL}")
    print(f"Batch:  {BATCH_SIZE}")
    if force:
        print("Mode:   --force (wiping existing JSONL)")
    print()

    if force and OUTPUT.exists():
        OUTPUT.unlink()
        print(f"Deleted existing {OUTPUT.name}\n")

    print("Loading chunks...")
    all_chunks = load_all_chunks()
    print(f"Total: {len(all_chunks)} chunks\n")

    done_ids = already_embedded(OUTPUT)
    if done_ids:
        print(f"Resuming: {len(done_ids)} already embedded, skipping.\n")

    pending = [c for c in all_chunks if c["id"] not in done_ids]
    print(f"To embed: {len(pending)} chunks\n")

    if not pending:
        print("Nothing to do.")
        return

    print(f"Loading model {EMBED_MODEL} ...")
    t_load = time.time()
    model = SentenceTransformer(EMBED_MODEL)
    print(f"Model loaded in {time.time() - t_load:.1f}s\n")

    out_file = OUTPUT.open("a", encoding="utf-8")
    total   = len(pending)
    done    = 0
    errors  = 0
    t_start = time.time()

    try:
        for batch_start in range(0, total, BATCH_SIZE):
            batch = pending[batch_start: batch_start + BATCH_SIZE]
            texts = [c["text"] for c in batch]

            try:
                embeddings = embed_batch(texts)
            except Exception as e:
                print(f"\n  ERROR embedding batch at {batch_start}: {e}")
                errors += len(batch)
                done   += len(batch)
                continue

            for chunk, emb in zip(batch, embeddings):
                record = {
                    "id":        chunk["id"],
                    "text":      chunk["text"],
                    "metadata":  chunk["metadata"],
                    "embedding": emb,
                }
                out_file.write(json.dumps(record, ensure_ascii=False) + "\n")

            done += len(batch)
            out_file.flush()

            elapsed   = time.time() - t_start
            rate      = done / elapsed if elapsed > 0 else 0
            remaining = (total - done) / rate if rate > 0 else 0
            print(
                f"\r  {done}/{total} chunks  "
                f"({done/total*100:.1f}%)  "
                f"{rate:.1f} chunks/s  "
                f"ETA {remaining:.0f}s      ",
                end="", flush=True,
            )

    finally:
        out_file.close()

    elapsed = time.time() - t_start
    print(f"\n\nDone in {elapsed:.1f}s")
    print(f"  Embedded: {done - errors}")
    print(f"  Errors:   {errors}")
    print(f"  Output:   {OUTPUT}")
    size_mb = OUTPUT.stat().st_size / 1_000_000
    print(f"  Size:     {size_mb:.1f} MB")
    print()
    print("Next step:")
    print(f"  python scripts/import_to_postgres.py")


if __name__ == "__main__":
    main()
