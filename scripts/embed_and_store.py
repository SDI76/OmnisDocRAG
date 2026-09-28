"""
embed_and_store.py — chunks → embeddings (JSONL)
================================================

Reads every output/chunks/*_chunks.json, embeds each chunk's `embed_text` and
writes output/embeddings.jsonl with one line per chunk:

    {"id": "cmd_ok_message", "hash": "<sha256 of embed_text, 16 hex>", "embedding": [1024 floats]}

Incremental: a chunk is only re-embedded when its embed_text changed (hash).
Chunks that no longer exist are dropped from the file.

Two ways to compute embeddings — both use BAAI/bge-m3, so query and document
vectors always come from the same model:

    python scripts/embed_and_store.py                           # local sentence-transformers
    python scripts/embed_and_store.py --server http://localhost:7071
                                                                # the running rag-server (/embed)
Options:
    --force    re-embed everything
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024

BASE = Path(__file__).resolve().parent.parent
CHUNKS = BASE / "output" / "chunks"
OUTPUT = BASE / "output" / "embeddings.jsonl"


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(CHUNKS.glob("*_chunks.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"  {path.name}: {len(data)} chunks")
        chunks.extend(data)
    return chunks


def load_existing() -> dict[str, dict]:
    if not OUTPUT.exists():
        return {}
    out = {}
    with OUTPUT.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                if "hash" in rec:          # v1 lines (without hash) are re-embedded
                    out[rec["id"]] = rec
    return out


class LocalEmbedder:
    def __init__(self, threads: int | None, max_seq_length: int):
        import torch
        from sentence_transformers import SentenceTransformer
        if threads:
            torch.set_num_threads(threads)
        device = "cuda" if torch.cuda.is_available() else (
            "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
        print(f"Loading model {EMBED_MODEL} on {device} (first run downloads ~2 GB), "
              f"threads {torch.get_num_threads()}, max_seq_length {max_seq_length} ...")
        self.model = SentenceTransformer(EMBED_MODEL, device=device)
        self.model.max_seq_length = max_seq_length

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return [v.tolist() for v in self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)]


class ServerEmbedder:
    def __init__(self, url: str):
        self.url = url.rstrip("/") + "/embed"

    def __call__(self, texts: list[str]) -> list[list[float]]:
        req = urllib.request.Request(self.url, json.dumps({"texts": texts}).encode("utf-8"),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read())
        if data.get("model") != EMBED_MODEL:
            raise RuntimeError(f"server model {data.get('model')!r} != {EMBED_MODEL!r}")
        return data["embeddings"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", help="rag-server base URL, e.g. http://localhost:7071")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--threads", type=int, help="CPU threads for local embedding (default: torch default)")
    ap.add_argument("--max-seq-length", type=int, default=512,
                    help="token limit per chunk for local embedding (longer tails are not embedded)")
    ap.add_argument("--checkpoint", type=int, default=10, help="write the file every N batches")
    args = ap.parse_args()

    print("=== Embedding ===")
    chunks = load_chunks()
    existing = {} if args.force else load_existing()
    records: dict[str, dict] = {}
    pending: list[dict] = []
    for c in chunks:
        h = text_hash(c["embed_text"])
        old = existing.get(c["id"])
        if old and old["hash"] == h:
            records[c["id"]] = old
        else:
            pending.append({"id": c["id"], "hash": h, "text": c["embed_text"]})
    print(f"Total {len(chunks)}, unchanged {len(records)}, to embed {len(pending)}")

    if pending:
        embed = ServerEmbedder(args.server) if args.server else LocalEmbedder(args.threads, args.max_seq_length)
        # Similar lengths per batch = less padding = noticeably faster on CPU.
        pending.sort(key=lambda b: len(b["text"]))
        t0 = time.time()
        try:
            for i in range(0, len(pending), args.batch):
                if i and (i // args.batch) % args.checkpoint == 0:
                    write(chunks, records, quiet=True)
                batch = pending[i:i + args.batch]
                vecs = embed([b["text"] for b in batch])
                for b, v in zip(batch, vecs):
                    if len(v) != EMBED_DIM:
                        raise ValueError(f"unexpected dimension {len(v)} for {b['id']}")
                    records[b["id"]] = {"id": b["id"], "hash": b["hash"],
                                        "embedding": [round(x, 7) for x in v]}
                done = min(i + args.batch, len(pending))
                rate = done / max(time.time() - t0, 1e-6)
                print(f"\r  {done}/{len(pending)}  {rate:.1f} chunks/s  ETA {(len(pending) - done) / rate:.0f}s   ",
                      end="", flush=True)
        finally:
            print()
            write(chunks, records)
    else:
        write(chunks, records)


def write(chunks: list[dict], records: dict[str, dict], quiet: bool = False) -> None:
    """Rewrite the file in chunk order (also after an interruption, so progress is kept)."""
    tmp = OUTPUT.with_suffix(".tmp")
    written = 0
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            rec = records.get(c["id"])
            if rec:
                f.write(json.dumps(rec) + "\n")
                written += 1
    tmp.replace(OUTPUT)
    if quiet:
        return
    print(f"Wrote {written}/{len(chunks)} embeddings to {OUTPUT} ({OUTPUT.stat().st_size / 1e6:.1f} MB)")
    if written == len(chunks):
        print("Next: python scripts/import_to_postgres.py  (or import_to_docker_postgres.py)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
