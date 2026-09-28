"""
embed_and_store.py — chunks → embeddings (JSONL)
================================================

Reads every output/chunks/*_chunks.json, embeds each chunk's `embed_text` and
writes output/embeddings.jsonl with one line per chunk:

    {"id": "cmd_ok_message", "hash": "<sha256 of embed_text, 16 hex>",
     "model": "BAAI/bge-m3", "max_seq_length": 512, "vector": "<base64 of 1024 float32, little-endian>"}

The vectors are stored as exact float32 bytes (base64), which keeps the file at
~33 MB for ~6,000 chunks — small enough to live in git, so a build made on one
machine reaches the others with a normal pull. Older files with a JSON number
list ("embedding") are still read.

Incremental: a chunk is only embedded again when its text, the model or the
token limit changed. Chunks that no longer exist are dropped from the file.
Progress is saved every few batches, so an interrupted run continues.

The result does not depend on where it is computed: the same model and token
limit give the same vectors on macOS (Apple GPU), Windows, Linux or inside the
rag-server container. The file can be built on a fast machine and copied to
the machine that runs the import.

    python scripts/embed_and_store.py                       # local model, device chosen automatically
    python scripts/embed_and_store.py --device cpu --threads 12
    python scripts/embed_and_store.py --server http://localhost:7071   # model of the running rag-server
    python scripts/embed_and_store.py --force               # re-embed everything

Devices (auto): NVIDIA GPU (cuda) → Apple Silicon GPU (mps) → CPU.
Rough duration for ~6,000 chunks: minutes on cuda/mps, hours on CPU.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
import struct
import sys
import time
import urllib.request
from pathlib import Path

# Apple GPU: fall back to the CPU for the few operations MPS does not implement.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024
DEFAULT_MAX_SEQ = 512
# Records written before model/max_seq_length were stored used these values.
LEGACY_CONFIG = {"model": EMBED_MODEL, "max_seq_length": DEFAULT_MAX_SEQ}

BASE = Path(__file__).resolve().parent.parent
CHUNKS = BASE / "output" / "chunks"
OUTPUT = BASE / "output" / "embeddings.jsonl"


def encode_vector(v: list[float]) -> str:
    return base64.b64encode(struct.pack(f"<{len(v)}f", *v)).decode("ascii")


def decode_vector(rec: dict) -> list[float]:
    """Vector of a record in either storage format."""
    if "vector" in rec:
        raw = base64.b64decode(rec["vector"])
        return list(struct.unpack(f"<{len(raw) // 4}f", raw))
    return rec["embedding"]


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
                    for k, v in LEGACY_CONFIG.items():
                        rec.setdefault(k, v)
                    if "embedding" in rec:  # number list → compact storage
                        rec["vector"] = encode_vector(rec.pop("embedding"))
                    out[rec["id"]] = rec
    return out


def pick_device(requested: str) -> str:
    import torch
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return "mps"
    return "cpu"


class LocalEmbedder:
    def __init__(self, device: str, threads: int | None, max_seq_length: int):
        import torch
        from sentence_transformers import SentenceTransformer
        if threads:
            torch.set_num_threads(threads)
        self.device = pick_device(device)
        print(f"System: {platform.system()} {platform.machine()}, Python {platform.python_version()}, "
              f"torch {torch.__version__}")
        print(f"Loading {EMBED_MODEL} on {self.device}"
              + (f" with {torch.get_num_threads()} threads" if self.device == "cpu" else "")
              + f", max_seq_length {max_seq_length} (first run downloads ~2.2 GB) ...")
        if self.device == "cpu":
            print("Note: CPU embedding of the full corpus takes hours; a GPU or Apple Silicon takes minutes.")
        self.model = SentenceTransformer(EMBED_MODEL, device=self.device)
        self.model.max_seq_length = max_seq_length

    def __call__(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vecs]


class ServerEmbedder:
    def __init__(self, url: str, max_seq_length: int):
        self.url = url.rstrip("/") + "/embed"
        self.max_seq_length = max_seq_length
        print(f"Embedding via {self.url} (model of the running rag-server), max_seq_length {max_seq_length}")

    def __call__(self, texts: list[str]) -> list[list[float]]:
        body = json.dumps({"texts": texts, "max_seq_length": self.max_seq_length}).encode("utf-8")
        req = urllib.request.Request(self.url, body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=900) as resp:
            data = json.loads(resp.read())
        if data.get("model") != EMBED_MODEL:
            raise RuntimeError(f"server model {data.get('model')!r} != {EMBED_MODEL!r}")
        if data.get("max_seq_length") != self.max_seq_length:
            raise RuntimeError("rag-server ignores max_seq_length — rebuild the rag-server image")
        return data["embeddings"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", help="rag-server base URL, e.g. http://localhost:7071")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "mps", "cuda"],
                    help="local device (default: auto)")
    ap.add_argument("--threads", type=int, help="CPU threads (default: torch default)")
    ap.add_argument("--max-seq-length", type=int, default=DEFAULT_MAX_SEQ,
                    help=f"token limit per chunk (default {DEFAULT_MAX_SEQ}); changing it re-embeds everything")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--checkpoint", type=int, default=10, help="save progress every N batches")
    ap.add_argument("--force", action="store_true", help="re-embed everything")
    args = ap.parse_args()

    config = {"model": EMBED_MODEL, "max_seq_length": args.max_seq_length}
    print("=== Embedding ===")
    chunks = load_chunks()
    existing = {} if args.force else load_existing()
    records: dict[str, dict] = {}
    pending: list[dict] = []
    for c in chunks:
        h = text_hash(c["embed_text"])
        old = existing.get(c["id"])
        if old and old["hash"] == h and all(old.get(k) == v for k, v in config.items()):
            records[c["id"]] = old
        else:
            pending.append({"id": c["id"], "hash": h, "text": c["embed_text"]})
    print(f"Total {len(chunks)}, unchanged {len(records)}, to embed {len(pending)}")

    if not pending:
        write(chunks, records)
        return

    embed = ServerEmbedder(args.server, args.max_seq_length) if args.server \
        else LocalEmbedder(args.device, args.threads, args.max_seq_length)
    # Similar lengths per batch = less padding = noticeably faster.
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
                records[b["id"]] = {"id": b["id"], "hash": b["hash"], **config,
                                    "vector": encode_vector(v)}
            done = min(i + args.batch, len(pending))
            rate = done / max(time.time() - t0, 1e-6)
            print(f"\r  {done}/{len(pending)}  {rate:.1f} chunks/s  ETA {(len(pending) - done) / rate:.0f}s   ",
                  end="", flush=True)
    finally:
        print()
        write(chunks, records)


def write(chunks: list[dict], records: dict[str, dict], quiet: bool = False) -> None:
    """Rewrite the file in chunk order (also after an interruption, so progress is kept)."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.with_suffix(".tmp")
    written = 0
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
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
