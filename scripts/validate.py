"""
validate.py — quality gate for extraction and chunking
======================================================

Run after extract.py and chunk.py, before embedding:

    python scripts/validate.py [--omnisdoc PATH]

Hard checks (exit code 1 on failure)
------------------------------------
- CommandRef: every bookmarked command/section after the index pages has a unit.
- FunctionRef: number of function entries = number of metadata tables in the PDF.
- Programming: chapters are complete and consecutive; no section title is a code line.
- No ligature damage left ("specifed", "frst", "defnes", ...).
- Chunks: unique ids, no empty text, size limit, entry metadata present.

Report only
-----------
- Cross-check against the Omnis doc pack (11.1 HTML help): commands and functions
  that exist on one side only. Naming differs for a few entries between the PDF
  manuals and the help (e.g. "If" vs. "If calculation"), so this is informational.

Writes output/validation_report.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import fitz
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):   # Windows pipes default to a legacy code page
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
EXTRACTED = BASE / "output" / "extracted"
CHUNKS = BASE / "output" / "chunks"
PDF_DIR = BASE / "Omnis PDF"

load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent / ".env.local", override=True)

MAX_CHUNK_WORDS = 600
LIGATURE_DAMAGE = re.compile(
    r"\b(?:specifed|specifes|frst|defne[sd]?|fle[s]?|feld[s]?|fnd|fag[s]?|confgur\w*|identifer[s]?|"
    r"qualifer[s]?|notifcation[s]?|effcient|suffcient|modifcation[s]?|foating)\b", re.I)
# Code lines typically carry notation paths, return clauses or statement punctuation.
CODE_TITLE = re.compile(r"Returns #|\.\$\w|[;{}=]|^#|^Sta:|^Quit method|^Calculate \w+ as ")


def norm(text: str) -> str:
    text = re.sub(r"[‘’“”'\"]", "", text).replace("…", "...")
    return re.sub(r"[^a-z0-9$.#]", "", text.lower().replace("()", ""))


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.info: dict[str, object] = {}

    def check(self, ok: bool, message: str) -> None:
        print(("  OK    " if ok else "  FAIL  ") + message)
        if not ok:
            self.failures.append(message)


def load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def check_commands(r: Report) -> None:
    print("\nCommandRef")
    doc = load(EXTRACTED / "CommandRef.json")
    units = doc["units"]
    titles = {norm(u["title"]) for u in units}
    pdf = fitz.open(str(PDF_DIR / doc["pdf"]))
    first_entry_page = min(u["page_start"] for u in units if u["kind"] == "entry")
    toc = [t for t in pdf.get_toc() if t[0] == 3 and t[2] >= first_entry_page]
    if toc:
        missing = [t[1] for t in toc if norm(t[1]) not in titles]
        r.check(not missing, f"bookmarks covered: {len(toc) - len(missing)}/{len(toc)} {missing[:10] if missing else ''}")
    entries = [u for u in units if u["kind"] == "entry"]
    no_group = [u["title"] for u in entries if not u["meta"].get("Command group")]
    r.check(not no_group, f"command group parsed for {len(entries) - len(no_group)}/{len(entries)} entries {no_group[:5]}")
    r.info["commands"] = len(entries)


def check_functions(r: Report) -> None:
    print("\nFunctionRef")
    doc = load(EXTRACTED / "FunctionRef.json")
    entries = [u for u in doc["units"] if u["kind"] == "entry"]
    pdf = fitz.open(str(PDF_DIR / doc["pdf"]))
    tables = 0
    for page in pdf:
        tables += sum(1 for line in page.get_text().split("\n") if line.strip() == "Function group")
    # the "function information" page explains the table once
    expected = tables - 1
    r.check(len(entries) == expected, f"function entries {len(entries)} = metadata tables in PDF {expected}")
    no_group = [u["title"] for u in entries if not u["meta"].get("Function group")]
    r.check(not no_group, f"function group parsed for {len(entries) - len(no_group)}/{len(entries)} entries {no_group[:5]}")
    r.info["functions"] = len(entries)


def check_programming(r: Report) -> None:
    print("\nProgramming")
    doc = load(EXTRACTED / "Programming.json")
    units = doc["units"]
    chapters = [int(re.match(r"Chapter (\d+)", u["title"]).group(1)) for u in units if u["kind"] == "chapter"]
    r.check(chapters == list(range(1, len(chapters) + 1)) and len(chapters) > 0,
            f"chapters consecutive: {chapters}")
    code_titles = [u["title"] for u in units if u["kind"] != "chapter" and CODE_TITLE.search(u["title"])]
    r.check(len(code_titles) == 0, f"no code lines as titles ({len(code_titles)}) {code_titles[:8]}")
    r.info["programming_units"] = len(units)


def check_chunks(r: Report) -> dict[str, list[dict]]:
    print("\nChunks")
    corpora: dict[str, list[dict]] = {}
    ids: set[str] = set()
    dup = 0
    for path in sorted(CHUNKS.glob("*_chunks.json")):
        chunks = load(path)
        corpora[path.stem] = chunks
        for c in chunks:
            if c["id"] in ids:
                dup += 1
            ids.add(c["id"])
        empty = [c["id"] for c in chunks if len(c["text"].split()) < 3]
        big = [c["id"] for c in chunks if len(c["text"].split()) > MAX_CHUNK_WORDS]
        damaged = [c["id"] for c in chunks if LIGATURE_DAMAGE.search(c["text"])]
        missing_fields = [c.get("id") for c in chunks
                          if not all(k in c for k in ("id", "corpus", "title", "heading_path", "text", "embed_text", "metadata"))]
        r.check(not empty, f"{path.name}: {len(chunks)} chunks, none empty {empty[:5]}")
        r.check(not big, f"{path.name}: none above {MAX_CHUNK_WORDS} words {big[:5]}")
        r.check(not damaged, f"{path.name}: no ligature damage {damaged[:5]}")
        r.check(not missing_fields, f"{path.name}: all fields present {missing_fields[:5]}")
    r.check(dup == 0, f"chunk ids unique ({dup} duplicates)")
    r.info["chunks"] = {k: len(v) for k, v in corpora.items()}
    return corpora


def check_doc_pack(r: Report, pack_root: Path | None) -> None:
    print("\nDoc pack cross-check (informational)")
    if not pack_root:
        print("  skipped: no doc pack configured (--omnisdoc or OMNISDOC_PACK)")
        return
    cat = pack_root / "catalogs"
    pack_cmd = [json.loads(l)["name"] for l in (cat / "commands.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    pack_fn = [json.loads(l)["name"] for l in (cat / "functions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    # Compare against the chunks, which include entries supplemented from the doc pack.
    rag_cmd = {c["metadata"]["command_name"] for c in load(CHUNKS / "commands_chunks.json")
               if c["metadata"].get("command_name")}
    rag_fn = {c["metadata"]["function_signature"] for c in load(CHUNKS / "functions_chunks.json")
              if c["metadata"].get("function_signature")}
    for label, pack_names, rag_names in (("commands", pack_cmd, rag_cmd), ("functions", pack_fn, rag_fn)):
        p = {norm(n): n for n in pack_names}
        q = {norm(n): n for n in rag_names}
        only_pack = sorted(p[k] for k in p.keys() - q.keys())
        only_pdf = sorted(q[k] for k in q.keys() - p.keys())
        print(f"  {label}: doc pack {len(p)}, PDF {len(q)}, common {len(p.keys() & q.keys())}")
        print(f"    only in doc pack ({len(only_pack)}): {only_pack[:25]}{' …' if len(only_pack) > 25 else ''}")
        print(f"    only in PDF ({len(only_pdf)}): {only_pdf[:25]}{' …' if len(only_pdf) > 25 else ''}")
        r.info[f"docpack_{label}"] = {"only_in_docpack": only_pack, "only_in_pdf": only_pdf}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnisdoc", help="path to the Omnis doc pack")
    args = ap.parse_args()
    pack = args.omnisdoc or os.environ.get("OMNISDOC_PACK", "").strip() or None

    r = Report()
    print("=== Validation ===")
    check_commands(r)
    check_functions(r)
    check_programming(r)
    check_chunks(r)
    check_doc_pack(r, Path(pack) if pack else None)

    report = {"failures": r.failures, "info": r.info}
    (BASE / "output" / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"\n{'FAILED' if r.failures else 'PASSED'}: {len(r.failures)} failing checks "
          f"(report: output/validation_report.json)")
    sys.exit(1 if r.failures else 0)


if __name__ == "__main__":
    main()
