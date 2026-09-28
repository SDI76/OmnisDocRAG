"""
eval_retrieval.py — retrieval regression check against the RAG HTTP server
==========================================================================

Sends every query from `eval_queries.json` to `/search` and checks whether a
hit whose key matches the query's `gold` regex appears in the top N.

Key of a hit = "<corpus> :: <title> :: <heading> :: <id>" (lower case), so a gold
pattern can name a title ("do method"), a notation member ("$line") or an id
prefix ("not_list_properties").

Metrics:
- Hit@N   queries with at least one gold hit in the top N
- MRR@N   mean reciprocal rank of the first gold hit (0 if none)
- bytes   size of the compact text answer an agent receives
- ms      wall-clock latency per request

Usage:
    python scripts/eval_retrieval.py                       # hybrid, top 5
    python scripts/eval_retrieval.py --mode semantic
    python scripts/eval_retrieval.py --mode fulltext --show
    python scripts/eval_retrieval.py --compare             # all three modes side by side
    python scripts/eval_retrieval.py --param w_fts=0.3     # override request fields

Run it before and after every retrieval or ingestion change.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

QUERIES = Path(__file__).with_name("eval_queries.json")


def post(url: str, payload: dict) -> tuple[dict, float]:
    t0 = time.time()
    req = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data, (time.time() - t0) * 1000


def key(r: dict) -> str:
    return f"{r['corpus']} :: {r['title']} :: {r['heading']} :: {r['id']}".lower()


def parse_param(value: str) -> tuple[str, object]:
    k, _, raw = value.partition("=")
    try:
        return k, json.loads(raw)
    except json.JSONDecodeError:
        return k, raw


def run(url: str, mode: str, top: int, extra: dict, show: bool, quiet: bool) -> dict:
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    hits, rr, total_bytes, total_ms = 0, 0.0, 0, 0.0
    per_query = {}
    for q in queries:
        payload = {"query": q["query"], "mode": mode, "top_k": top, **extra}
        data, ms = post(url, {**payload, "format": "json"})
        text, _ = post(url, {**payload, "format": "text"})
        results = data["results"][:top]
        rank = next((i for i, r in enumerate(results, 1) if re.search(q["gold"], key(r), re.I)), None)
        hits += rank is not None
        rr += 1 / rank if rank else 0.0
        nbytes = len(text["text"].encode("utf-8"))
        total_bytes += nbytes
        total_ms += ms
        per_query[q["id"]] = rank
        if not quiet:
            print(f"{q['id']} {q['type']:18} rank={rank or '-':<2} {nbytes / 1024:5.1f} KB {ms:5.0f} ms  {q['query']}")
            if show or rank is None:
                for r in results:
                    print(f"      {r['corpus'][6:]:12} {r['title'][:70]}  [{r['id']}]")
    n = len(queries)
    summary = {"mode": mode, "hit": hits, "n": n, "mrr": rr / n,
               "kb": total_bytes / n / 1024, "ms": total_ms / n, "ranks": per_query}
    print(f"\n[{mode}] Hit@{top}: {hits}/{n}   MRR@{top}: {rr / n:.2f}   "
          f"avg answer: {summary['kb']:.1f} KB   avg latency: {summary['ms']:.0f} ms")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:7071/search")
    ap.add_argument("--mode", default="hybrid", choices=["hybrid", "semantic", "fulltext"])
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--param", action="append", default=[], help="extra request field, e.g. w_fts=0.3")
    ap.add_argument("--show", action="store_true", help="print the top titles for every query")
    ap.add_argument("--compare", action="store_true", help="run all three modes")
    args = ap.parse_args()
    extra = dict(parse_param(p) for p in args.param)

    if not args.compare:
        run(args.url, args.mode, args.top, extra, args.show, quiet=False)
        return
    summaries = [run(args.url, m, args.top, extra, False, quiet=True) for m in ("semantic", "fulltext", "hybrid")]
    ids = list(summaries[0]["ranks"])
    print("\nquery  " + "  ".join(f"{s['mode']:>8}" for s in summaries))
    for qid in ids:
        print(f"{qid}    " + "  ".join(f"{(s['ranks'][qid] or '-'):>8}" for s in summaries))


if __name__ == "__main__":
    main()
