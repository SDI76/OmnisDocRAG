"""
chunk.py — structured units → retrieval chunks
==============================================

Input
-----
output/extracted/CommandRef.json, FunctionRef.json, Programming.json  (from extract.py)
Optional: the Omnis doc pack (Markdown built from the Omnis 11.1 HTML help),
passed with --omnisdoc PATH or the OMNISDOC_PACK environment variable. It adds
the notation corpus and the deprecation data of commands.

Output
------
output/chunks/commands_chunks.json
output/chunks/functions_chunks.json
output/chunks/programming_chunks.json
output/chunks/notation_chunks.json        (only with doc pack)

Chunk format (uniform for all corpora)
--------------------------------------
{
  "id":           stable id, e.g. "cmd_ok_message", "prog_ch07_sql_worker_objects_overview"
  "corpus":       omnis-commands | omnis-functions | omnis-programming | omnis-notation
  "title":        entry title (command, function, section, notation node)
  "heading_path": ["Chapter 7—SQL Programming", "SQL Worker Objects", "Overview"]
  "text":         Markdown shown to the reader
  "embed_text":   one context line + text; this is what gets embedded
  "metadata":     source, omnis_version, pages, part/parts, doc_key, entry metadata
}

Chunking rules
--------------
- Commands / functions: one entry = one chunk. Long entries are split at paragraph
  boundaries (never inside a code block or table); every part repeats the title
  and metadata line.
- Programming: one sub-section = one chunk, with the full heading path. Units with
  almost no body (a heading directly followed by a sub-heading) are merged into
  the following unit of the same section. Long units are split like above.
- Notation: one node = one overview chunk plus member chunks of ~300 words.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
EXTRACTED = BASE / "output" / "extracted"
OUTPUT = BASE / "output" / "chunks"

load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent / ".env.local", override=True)

MAX_WORDS = 450          # split threshold per chunk
TARGET_WORDS = 350       # target size of split parts
MIN_BODY_WORDS = 25      # programming units below this are merged forward
NOTATION_GROUP_WORDS = 300


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def slugify(text: str, limit: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.replace("$", "").replace("#", "hash_")
    text = re.sub(r"[^\w\s-]", " ", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)[:limit].strip("_") or "x"


def words(text: str) -> int:
    return len(text.split())


def blocks(md: str) -> list[str]:
    """Split Markdown into paragraphs, keeping code fences and tables intact."""
    out: list[str] = []
    buf: list[str] = []
    fenced = False
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            buf.append(line)
            continue
        if fenced:
            buf.append(line)
            continue
        is_table = line.strip().startswith("|")
        prev_table = bool(buf) and buf[-1].strip().startswith("|")
        if not line.strip():
            if buf:
                out.append("\n".join(buf))
                buf = []
            continue
        if buf and is_table != prev_table and not fenced:
            out.append("\n".join(buf))
            buf = []
        buf.append(line)
    if buf:
        out.append("\n".join(buf))
    return out


def split_block(block: str, limit: int = TARGET_WORDS) -> list[str]:
    """Split one oversized block: tables by rows (header repeated), code by lines, text by sentences."""
    if words(block) <= limit:
        return [block]
    lines = block.split("\n")
    if lines[0].strip().startswith("|"):
        head = lines[:2] if len(lines) > 1 and re.fullmatch(r"\|[\s\-|:]+\|?", lines[1].strip()) else []
        rows = lines[len(head):]
        units, prefix = rows, head
    elif lines[0].strip().startswith("```"):
        units, prefix = lines[1:-1] if lines[-1].strip().startswith("```") else lines[1:], []
        out = []
        for part in split_units(units, limit):
            out.append("```\n" + "\n".join(part) + "\n```")
        return out
    else:
        units, prefix = re.split(r"(?<=[.!?])\s+", block), []
        return [" ".join(p) for p in split_units(units, limit)]
    return ["\n".join(prefix + part) for part in split_units(units, limit)]


def split_units(units: list[str], limit: int) -> list[list[str]]:
    groups: list[list[str]] = [[]]
    size = 0
    for u in units:
        n = words(u)
        if groups[-1] and size + n > limit:
            groups.append([])
            size = 0
        groups[-1].append(u)
        size += n
    return [g for g in groups if g]


def split_body(header: str, body: str) -> list[str]:
    """Split header+body into parts ≤ MAX_WORDS; each part starts with the header."""
    if words(header) + words(body) <= MAX_WORDS:
        return [f"{header}\n\n{body}".strip()]
    parts: list[str] = []
    cur: list[str] = []
    size = 0
    pieces = [p for b in blocks(body) for p in split_block(b)]
    for b in pieces:
        n = words(b)
        if cur and size + n > TARGET_WORDS:
            parts.append("\n\n".join(cur))
            cur, size = [], 0
        cur.append(b)
        size += n
    if cur:
        # avoid a tiny tail part
        if parts and size < 60:
            parts[-1] += "\n\n" + "\n\n".join(cur)
        else:
            parts.append("\n\n".join(cur))
    return [f"{header}\n\n{p}".strip() for p in parts]


def load_units(source: str) -> dict:
    path = EXTRACTED / f"{source}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — run scripts/extract.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def yes(value: str | None) -> bool | None:
    if value is None:
        return None
    return "YES" in value.upper()


def base_meta(doc: dict, unit: dict) -> dict:
    if unit.get("origin") == "docpack":
        return {"source": "OmnisDocPack", "omnis_version": "11.1", "doc_path": unit["doc_path"],
                "kind": unit["kind"]}
    return {
        "source": doc["source"],
        "omnis_version": doc.get("omnis_version"),
        "revision": doc.get("revision"),
        "page_start": unit["page_start"],
        "page_end": unit["page_end"],
        "kind": unit["kind"],
    }


def finalize(chunks: list[dict]) -> list[dict]:
    """Unique ids and part numbering."""
    seen: Counter = Counter()
    for c in chunks:
        seen[c["id"]] += 1
        if seen[c["id"]] > 1:
            c["id"] = f"{c['id']}_{seen[c['id']]}"
    return chunks


def emit(chunks: list[dict], corpus: str, id_base: str, title: str, heading_path: list[str],
         header: str, body: str, context: str, meta: dict) -> None:
    parts = split_body(header, body)
    doc_key = id_base
    for i, text in enumerate(parts):
        m = dict(meta)
        m["doc_key"] = doc_key
        if len(parts) > 1:
            m["part"] = i + 1
            m["parts"] = len(parts)
        chunks.append({
            "id": id_base if len(parts) == 1 else f"{id_base}_p{i + 1}",
            "corpus": corpus,
            "title": title,
            "heading_path": heading_path,
            "text": text,
            "embed_text": f"{context}\n\n{text}",
            "metadata": m,
        })


def split_header(md: str) -> tuple[str, str]:
    """First heading line (+ metadata line for reference entries) vs. body."""
    lines = md.split("\n")
    head = [lines[0]] if lines else []
    rest = lines[1:]
    while rest and not rest[0].strip():
        rest.pop(0)
    if rest and re.match(r"^(Command group|Function group):", rest[0]):
        head.append("")
        head.append(rest.pop(0))
    return "\n".join(head), "\n".join(rest).strip()


# ─────────────────────────────────────────────────────────────
# Doc pack (optional)
# ─────────────────────────────────────────────────────────────

class DocPack:
    def __init__(self, root: Path):
        self.root = root
        cat = root / "catalogs"
        self.commands = [json.loads(l) for l in (cat / "commands.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.functions = [json.loads(l) for l in (cat / "functions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.notation = [json.loads(l) for l in (cat / "notation.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    @staticmethod
    def key(name: str) -> str:
        return re.sub(r"[^a-z0-9$.]", "", name.lower().replace("()", ""))

    def command_info(self) -> dict[str, dict]:
        return {self.key(c["name"]): c for c in self.commands}

    def names(self, kind: str) -> set[str]:
        rows = self.commands if kind == "command" else self.functions
        return {self.key(r["name"]) for r in rows}

    def missing_entries(self, kind: str, existing_titles: list[str]) -> list[dict]:
        """
        Entries of the 11.1 help that the PDF manual (11.0) does not contain,
        converted into the unit format of extract.py.
        """
        rows = self.commands if kind == "command" else self.functions
        existing = {self.key(t) for t in existing_titles}
        units = []
        for row in rows:
            if self.key(row["name"]) in existing:
                continue
            path = self.root / row["markdown_path"]
            if not path.exists():
                continue
            _, body = parse_front_matter(path.read_text(encoding="utf-8"))
            meta, md = self.convert_page(body, row["name"])
            units.append({
                "kind": "entry", "title": row["name"], "heading_path": [row["name"]], "level": 2,
                "page_start": None, "page_end": None, "markdown": md, "meta": meta,
                "origin": "docpack", "doc_path": row["markdown_path"],
            })
        return units

    @staticmethod
    def convert_page(body: str, name: str) -> tuple[dict, str]:
        meta: dict = {}
        out: list[str] = []
        section = None
        for line in body.split("\n"):
            s = line.strip()
            if s.startswith("# ") and not out:
                continue
            if s.startswith("## "):
                section = s[3:].strip()
                if section != "Metadata":
                    out.append(f"### {section}")
                continue
            if section == "Metadata":
                cells = [c.strip() for c in s.strip("|").split("|")] if s.startswith("|") else []
                if len(cells) == 2 and cells[0] not in ("Field", "") and not set(cells[0]) <= set("-: "):
                    meta[cells[0]] = cells[1]
                continue
            if s.startswith("Source: "):
                continue
            out.append(re.sub(r"^```\w+", "```", line))
        meta_line = " | ".join(f"{k}: {v}" for k, v in meta.items())
        md = f"## {name}\n\n{meta_line}\n\n" + "\n".join(out).strip()
        return meta, re.sub(r"\n{3,}", "\n\n", md)


def resolve_pack(arg: str | None) -> DocPack | None:
    path = arg or os.environ.get("OMNISDOC_PACK", "").strip()
    if not path:
        return None
    root = Path(path)
    if not (root / "catalogs" / "notation.jsonl").exists():
        raise FileNotFoundError(f"Doc pack not found or incomplete: {root}")
    return DocPack(root)


# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

def chunk_commands(pack: DocPack | None) -> list[dict]:
    doc = load_units("CommandRef")
    pack_info = pack.command_info() if pack else {}
    units = list(doc["units"])
    if pack:
        units += pack.missing_entries("command", [u["title"] for u in units if u["kind"] == "entry"])
    chunks: list[dict] = []
    for u in units:
        header, body = split_header(u["markdown"])
        meta = base_meta(doc, u)
        if u["kind"] == "entry":
            t = u["meta"]
            info = pack_info.get(DocPack.key(u["title"]))
            if pack and not info:
                meta["in_help_11_1"] = False
                header += "\n\nNot listed in the Omnis 11.1 help (legacy command)."
            deprecated = bool(info and info.get("deprecated")) or "### Deprecated" in u["markdown"]
            meta.update({
                "command_name": u["title"],
                "command_group": t.get("Command group", ""),
                "flag_affected": yes(t.get("Flag affected")),
                "reversible": yes(t.get("Reversible")),
                "execute_on_client": yes(t.get("Execute on client")),
                "platform": t.get("Platform(s)"),
                "deprecated": deprecated,
                "modern_equivalent": (info or {}).get("modern_equivalent"),
            })
            flags = " | ".join(f"{k}: {v}" for k, v in t.items() if k != "Command group")
            context = (f"Omnis command: {u['title']} | Group: {t.get('Command group', '')} | {flags}"
                       + (" | DEPRECATED" if deprecated else ""))
            if deprecated:
                meta["deprecation"] = (info or {}).get("scope_category") or "deprecated"
                note = "Deprecated command (classified as legacy by Omnis"
                note += (f"; modern equivalent: {meta['modern_equivalent']})." if meta["modern_equivalent"]
                         else "; no direct replacement).")
                header += f"\n\n{note}"
            id_base = f"cmd_{slugify(u['title'])}"
        else:
            context = f"Omnis Command Reference: {u['title']}"
            id_base = f"cmd_ref_{slugify(u['title'])}"
        emit(chunks, "omnis-commands", id_base, u["title"], u["heading_path"], header, body, context, meta)
    return finalize(chunks)


# ─────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────

def chunk_functions(pack: DocPack | None) -> list[dict]:
    doc = load_units("FunctionRef")
    units = list(doc["units"])
    if pack:
        units += pack.missing_entries("function", [u["title"] for u in units if u["kind"] == "entry"])
    chunks: list[dict] = []
    for u in units:
        header, body = split_header(u["markdown"])
        meta = base_meta(doc, u)
        if u["kind"] == "entry":
            t = u["meta"]
            if pack and DocPack.key(u["title"]) not in pack.names("function"):
                meta["in_help_11_1"] = False
            meta.update({
                "function_name": u["title"].rstrip("()").strip(),
                "function_signature": u["title"],
                "function_group": re.sub(r"[_*]", "", t.get("Function group", "")).strip(),
                "execute_on_client": yes(t.get("Execute on client")),
                "platform": t.get("Platform(s)"),
            })
            context = (f"Omnis function: {u['title']} | Group: {meta['function_group']} | "
                       f"Execute on client: {t.get('Execute on client', '')} | Platform(s): {t.get('Platform(s)', '')}")
            id_base = f"fn_{slugify(u['title'])}"
        else:
            context = "Omnis Function Reference: overview"
            id_base = f"fn_ref_{slugify(u['title'])}"
        emit(chunks, "omnis-functions", id_base, u["title"], u["heading_path"], header, body, context, meta)
    return finalize(chunks)


# ─────────────────────────────────────────────────────────────
# Programming manual
# ─────────────────────────────────────────────────────────────

def chunk_programming() -> list[dict]:
    doc = load_units("Programming")
    units = doc["units"]

    # Merge units without real body into the next unit of the same section.
    merged: list[dict] = []
    carry: dict | None = None
    for u in units:
        u = dict(u)
        if carry:
            same_section = u["heading_path"][:2] == carry["heading_path"][:2] and u["level"] > carry["level"] - 1
            if same_section and u["kind"] != "chapter":
                u["markdown"] = carry["markdown"] + "\n\n" + u["markdown"]
                u["page_start"] = carry["page_start"]
                u["merged_from"] = carry["title"]
            else:
                merged.append(carry)
            carry = None
        body = u["markdown"].split("\n", 1)[1] if "\n" in u["markdown"] else ""
        if words(body) < MIN_BODY_WORDS:
            carry = u
            continue
        merged.append(u)
    if carry:
        merged.append(carry)

    chunks: list[dict] = []
    for u in merged:
        path = u["heading_path"]
        chapter = path[0]
        m = re.match(r"Chapter (\d+)", chapter)
        ch_num = int(m.group(1)) if m else 0
        meta = base_meta(doc, u)
        meta.update({
            "chapter_number": ch_num,
            "chapter_title": re.sub(r"^Chapter \d+—", "", chapter),
            "section": path[1] if len(path) > 1 else "",
            "subsection": path[2] if len(path) > 2 else "",
        })
        if words(u["markdown"]) < 8:
            continue
        # Heading lines of the unit become part of the text; the path gives context.
        text = u["markdown"]
        first_line, _, body = text.partition("\n")
        header = first_line
        context = "Omnis Programming manual | " + " › ".join(path)
        id_base = f"prog_ch{ch_num:02d}_{slugify(' '.join(path[1:]) or u['title'], 70)}"
        emit(chunks, "omnis-programming", id_base, u["title"], path, header, body.strip(), context, meta)
    return finalize(chunks)


# ─────────────────────────────────────────────────────────────
# Notation (doc pack)
# ─────────────────────────────────────────────────────────────

def norm_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def parse_front_matter(md: str) -> tuple[dict, str]:
    if not md.startswith("---"):
        return {}, md
    end = md.find("\n---", 3)
    fm, body = md[3:end], md[end + 4:]
    meta: dict = {}
    for line in fm.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body.strip()


def notation_members(body: str) -> tuple[str, list[tuple[str, list[tuple[str, str]]]]]:
    """Split a notation page into description and [(section, [(member, text)])]."""
    parts = re.split(r"(?m)^## ", body)
    intro = re.sub(r"(?m)^# .*$", "", parts[0]).strip()
    sections = []
    for part in parts[1:]:
        name, _, rest = part.partition("\n")
        members = []
        rest = re.sub(r"(?m)^Source: .*$", "", rest)
        for row in rest.splitlines():
            if not row.startswith("|") or re.fullmatch(r"\|[\s\-|:]+\|?", row.strip()):
                continue
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0] in ("Object specific", ""):
                continue
            members.append((cells[0], " ".join(c for c in cells[1:] if c).strip()))
        plain = re.sub(r"(?m)^\|.*$", "", rest).strip()
        if not members and len(plain.split()) >= 4:
            members.append(("", plain))
        sections.append((name.strip(), members))
    return intro, sections


def chunk_notation(pack: DocPack) -> list[dict]:
    containers: dict[str, dict] = {}
    deprecated: dict[tuple[str, str], dict] = {}
    for row in pack.notation:
        containers.setdefault(row["markdown_path"].replace("\\", "/"), row)
        deprecated[(row["markdown_path"].replace("\\", "/"), row["name"])] = row

    chunks: list[dict] = []
    root = pack.root
    for path in sorted((root / "md" / "notation").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        fm, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = fm.get("title") or path.stem
        row = containers.get(rel, {})
        node = row.get("container") or rel.removeprefix("md/notation/").removesuffix(".md").replace("/", ".")
        node_path = row.get("container_canonical") or node.lower()
        # The catalog drops the "$" of $root paths ("root.iremoteforms"); the page title keeps it.
        if title.startswith("$") and norm_name(title) == norm_name(node):
            node = title
        intro, sections = notation_members(body)
        meta = {
            "source": "OmnisDocPack",
            "omnis_version": "11.1",
            "notation_node": node,
            "notation_path": node_path,
            "doc_path": rel,
        }
        id_base = f"not_{slugify(node_path, 70)}"
        label = title if norm_name(title) == norm_name(node) else f"{title} ({node})"
        heading = title if norm_name(title) == norm_name(node) else f"{title} — {node}"
        context = f"Omnis notation: {label}"

        member_names = []
        for sec, members in sections:
            if sec.lower() == "children":
                # The children table is a grid of node names, not name/description pairs.
                kids = [t for m, d in members for t in f"{m} {d}".split() if t.startswith("$")]
                if kids:
                    member_names.append("Children: " + " ".join(dict.fromkeys(kids)))
                continue
            names = [m for m, _ in members if m.startswith("$")]
            standard = " ".join(d for m, d in members if m == "Standard")
            if names:
                member_names.append(f"{sec}: " + " ".join(names))
            if standard:
                member_names.append(f"Standard {sec.lower()}: {standard}")
        sections = [(s, m) for s, m in sections if s.lower() != "children"]
        # Pages without member sections can carry everything in one huge intro table.
        intro_blocks = blocks(intro)
        long_intro = words(intro) > NOTATION_GROUP_WORDS and len(intro_blocks) > 1
        head_intro = intro_blocks[0] if long_intro else intro
        overview = f"## {heading}\n\n{head_intro}".strip()
        if member_names:
            overview += "\n\n" + "\n".join(member_names)
        m0 = dict(meta, kind="node", doc_key=id_base)
        chunks.append({"id": id_base, "corpus": "omnis-notation", "title": label,
                       "heading_path": [node], "text": overview,
                       "embed_text": f"{context}\n\n{overview}", "metadata": m0})
        if long_intro:
            rest = "\n\n".join(intro_blocks[1:])
            for k, part in enumerate(split_body(f"## {heading}", rest), 1):
                chunks.append({"id": f"{id_base}_text_{k}", "corpus": "omnis-notation",
                               "title": f"{label}, part {k}", "heading_path": [node],
                               "text": part, "embed_text": f"{context}\n\n{part}",
                               "metadata": dict(meta, kind="text", doc_key=id_base, part=k)})

        for sec, members in sections:
            group: list[str] = []
            size = 0
            n = 0

            def flush() -> None:
                nonlocal group, size, n
                if not group:
                    return
                n += 1
                text = f"## {title} — {sec}\n\n" + "\n".join(group)
                first = re.match(r"- `([^`]+)`", group[0])
                last = re.match(r"- `([^`]+)`", group[-1])
                span = f" ({first.group(1)} … {last.group(1)})" if first and last and first != last else ""
                mm = dict(meta, kind="members", section=sec, doc_key=id_base)
                chunks.append({"id": f"{id_base}_{slugify(sec, 20)}_{n}", "corpus": "omnis-notation",
                               "title": f"{title} {sec.lower()}{span}", "heading_path": [node, sec],
                               "text": text, "embed_text": f"{context} | {sec}\n\n{text}",
                               "metadata": mm})
                group, size = [], 0

            for name, desc in members:
                if name == "Standard":
                    continue          # listed in the node overview chunk
                if not name.startswith(("$", "#", "k")):
                    line = f"- {name}: {desc}" if name else desc
                else:
                    info = deprecated.get((rel, name), {})
                    flag = " (deprecated)" if info.get("deprecated") else ""
                    line = f"- `{name}`{flag} — {desc}"
                # A single member description can be very long (e.g. standard events).
                pieces = split_block(line, NOTATION_GROUP_WORDS) if words(line) > NOTATION_GROUP_WORDS else [line]
                for k, piece in enumerate(pieces):
                    if k and name.startswith("$"):
                        piece = f"- `{name}` (continued) — {piece}"
                    w = words(piece)
                    if group and size + w > NOTATION_GROUP_WORDS:
                        flush()
                    group.append(piece)
                    size += w
            flush()
    return finalize(chunks)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def save(chunks: list[dict], filename: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / filename).write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    sizes = [words(c["text"]) for c in chunks]
    print(f"  {filename}: {len(chunks)} chunks, words avg {sum(sizes) // max(1, len(sizes))}, "
          f"min {min(sizes)}, max {max(sizes)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnisdoc", help="path to the Omnis doc pack (directory with catalogs/ and md/)")
    args = ap.parse_args()
    pack = resolve_pack(args.omnisdoc)

    print("=== Chunking ===")
    print(f"Doc pack: {pack.root if pack else 'not configured (no notation corpus, no deprecation data)'}")
    save(chunk_commands(pack), "commands_chunks.json")
    save(chunk_functions(pack), "functions_chunks.json")
    save(chunk_programming(), "programming_chunks.json")
    if pack:
        save(chunk_notation(pack), "notation_chunks.json")
    else:
        stale = OUTPUT / "notation_chunks.json"
        if stale.exists():
            stale.unlink()
            print("  removed stale notation_chunks.json")


if __name__ == "__main__":
    main()
