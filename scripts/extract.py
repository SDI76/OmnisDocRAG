"""
extract.py — PDF → structured units (JSON) + inspection Markdown
===============================================================

Why this design
---------------
The Omnis PDFs are hard to convert: headings are not tagged, FunctionRef and
Programming have no bookmarks, code is set in a *larger* font than section
titles, and code glyphs are positioned without real space characters.

`pymupdf4llm` produces good page Markdown (tables, lists, bold text) but guesses
headings by font size. It therefore turns code lines into headings and renders
some entry titles as bold text only. This script keeps pymupdf4llm for the page
*content* and takes the document *structure* from the PDF itself:

- CommandRef / FunctionRef: an entry starts at the bold line directly before its
  metadata table ("Command group" / "Function group"). Bookmarks, when present,
  are used to verify and canonicalise entry titles.
- Programming: chapter / section / sub-section headings are identified by font
  (Montserrat-Bold at the heading sizes, never the LMMono code font). Bookmarks
  are used instead when the PDF has them.

The Markdown is then cut at those headings, heading markup is rewritten
consistently, and code blocks get their spacing repaired via pdfplumber.

Output
------
output/extracted/<source>.json   units with title, heading path, pages, markdown
output/<source>_extracted.md     concatenated Markdown for manual inspection
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
import pymupdf4llm

if hasattr(sys.stdout, "reconfigure"):   # Windows pipes default to a legacy code page
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
PDF_DIR = BASE / "Omnis PDF"
OUTPUT = BASE / "output"
EXTRACTED = OUTPUT / "extracted"

OMNIS_VERSION = "11"

SOURCES = [
    {
        "source": "CommandRef",
        "pdf": "CommandRef.pdf",
        "kind": "reference",
        "label": "Command group",
        # Overview sections before the first command (1-based pages, from bookmarks).
        "overview_titles": ["Command information", "Command Groups", "Client Commands",
                            "Error Codes", "Obsolete Commands", "Command Filters"],
    },
    {
        "source": "FunctionRef",
        "pdf": "FunctionRef.pdf",
        "kind": "reference",
        "label": "Function group",
        # Pages 3-7 hold multi-column group lists whose text overlaps in the PDF.
        # Only the "function information" page is kept as overview.
        "overview_pages": [2],
    },
    {
        "source": "Programming",
        "pdf": "Programming_Omnis.pdf",
        "kind": "manual",
    },
]

REFERENCE_SUBSECTIONS = {
    "syntax", "description", "options", "example", "examples", "parameters",
    "notes", "note", "see also", "deprecated command", "deprecated function",
}

MONO_HINTS = ("mono", "courier", "code")


# ─────────────────────────────────────────────────────────────
# Low-level helpers
# ─────────────────────────────────────────────────────────────

def norm(text: str) -> str:
    """Normalise a line for matching: no markdown markup, no spaces, lower case."""
    text = re.sub(r"^#+\s*", "", text.strip())
    text = re.sub(r"[`*_]|<br>", "", text)
    # Quotes and ellipses are typeset inconsistently between bookmarks and page text.
    text = re.sub(r"[‘’“”'\"]", "", text).replace("…", "...")
    return re.sub(r"\s+", "", text).lower()


def is_mono(font: str) -> bool:
    f = font.lower()
    return any(h in f for h in MONO_HINTS)


def is_bold(span: dict) -> bool:
    return "bold" in span["font"].lower() or bool(span["flags"] & 16)


@dataclass
class Line:
    page: int          # 0-based page index
    text: str
    font: str
    size: float
    bold: bool         # every non-blank span is bold
    mono: bool         # first span is monospace
    y: float
    block_lines: int   # number of lines in the enclosing block
    x: float = 0.0


def collect_lines(doc: fitz.Document, pages: list[int]) -> list[Line]:
    lines: list[Line] = []
    for p in pages:
        for block in doc[p].get_text("dict", sort=True)["blocks"]:
            blk_lines = block.get("lines", [])
            for ln in blk_lines:
                spans = [s for s in ln["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = re.sub(r"\s+", " ", "".join(s["text"] for s in ln["spans"])).strip()
                lines.append(Line(
                    page=p,
                    text=text,
                    font=spans[0]["font"],
                    size=round(spans[0]["size"], 1),
                    bold=all(is_bold(s) for s in spans),
                    mono=is_mono(spans[0]["font"]),
                    y=ln["bbox"][1],
                    block_lines=len(blk_lines),
                    x=ln["bbox"][0],
                ))
    return lines


# ─────────────────────────────────────────────────────────────
# Ligature repair
# ─────────────────────────────────────────────────────────────

class LigatureRepair:
    """
    PyMuPDF expands the "fi"/"fl" ligatures into two characters at the same
    position; its table extraction de-duplicates them and drops the second one
    ("specifed", "frst", "fag"). Plain page text is intact, so it provides the
    vocabulary: a word that is unknown there is repaired when exactly one
    insertion of "i" or "l" after an "f" yields a known word.
    """

    def __init__(self, doc: fitz.Document):
        self.vocab: set[str] = set()
        for page in doc:
            self.vocab.update(w.lower() for w in re.findall(r"[A-Za-z]+", page.get_text()))
        self.repaired = 0

    def _word(self, m: re.Match) -> str:
        word = m.group(0)
        low = word.lower()
        if len(low) < 3 or low in self.vocab or "f" not in low:
            return word
        candidates = set()
        for i, ch in enumerate(low):
            if ch == "f":
                for ins in ("i", "l"):
                    cand = low[: i + 1] + ins + low[i + 1:]
                    if cand in self.vocab:
                        candidates.add((i, ins))
        if len(candidates) != 1:
            return word
        i, ins = candidates.pop()
        if word[i + 1: i + 2].isupper() or (word.isupper() and len(word) > 1):
            ins = ins.upper()
        self.repaired += 1
        return word[: i + 1] + ins + word[i + 1:]

    def fix(self, md: str) -> str:
        return re.sub(r"[A-Za-z]+", self._word, md)


# ─────────────────────────────────────────────────────────────
# Code-block spacing repair (pdfplumber)
# ─────────────────────────────────────────────────────────────

class CodeFixer:
    """
    pymupdf4llm drops spaces inside code lines ("CalculatelCountas1").
    pdfplumber groups words by x-distance and keeps them. Code lines on a page
    are matched by their space-free form and replaced.
    """

    def __init__(self, pdf_path: Path):
        self.pdf = pdfplumber.open(str(pdf_path))

    def close(self) -> None:
        self.pdf.close()

    def code_lines(self, page_index: int) -> list[str]:
        words = self.pdf.pages[page_index].extract_words(
            extra_attrs=["fontname"], x_tolerance=2, y_tolerance=3)
        rows: dict[int, list[dict]] = {}
        for w in words:
            rows.setdefault(round(w["top"]), []).append(w)
        out = []
        for y in sorted(rows):
            wds = sorted(rows[y], key=lambda w: w["x0"])
            if is_mono(wds[0].get("fontname", "")):
                out.append(" ".join(w["text"] for w in wds))
        return out

    def fix(self, md: str, page_index: int) -> str:
        if "```" not in md and "`" not in md:
            return md
        candidates = [(re.sub(r"\s+", "", c), c) for c in self.code_lines(page_index)]
        candidates = [c for c in candidates if c[0]]
        if not candidates:
            return md
        exact = {k: v for k, v in candidates}

        def repair(line: str) -> str:
            key = re.sub(r"\s+", "", line)
            if not key:
                return line
            if key in exact:
                return exact[key]
            for cand_key, cand in candidates:
                if len(cand_key) > len(key) and cand_key.startswith(key):
                    count = 0
                    for i, ch in enumerate(cand):
                        if ch != " ":
                            count += 1
                        if count == len(key):
                            return cand[: i + 1]
            return line

        def block(m: re.Match) -> str:
            body = "\n".join(repair(l) for l in m.group(1).splitlines())
            return "```\n" + body + "\n```"

        md = re.sub(r"```\n(.*?)\n```", block, md, flags=re.DOTALL)
        # Inline code lines that pymupdf4llm turned into headings: "## `code`"
        md = re.sub(r"(?m)^(#+\s*)`([^`]+)`\s*$",
                    lambda m: m.group(1) + "`" + repair(m.group(2)) + "`", md)
        return md


# ─────────────────────────────────────────────────────────────
# Page Markdown
# ─────────────────────────────────────────────────────────────

def page_markdown(pdf_path: Path, pages: list[int]) -> dict[int, list[str]]:
    """Return {page_index: markdown lines} with repaired code spacing."""
    chunks = pymupdf4llm.to_markdown(str(pdf_path), pages=pages, page_chunks=True,
                                     show_progress=False)
    fixer = CodeFixer(pdf_path)
    ligatures = LigatureRepair(fitz.open(str(pdf_path)))
    result: dict[int, list[str]] = {}
    try:
        for ch in chunks:
            p = ch["metadata"]["page_number"] - 1
            md = fixer.fix(ligatures.fix(ch["text"]), p)
            md = re.sub(r"==> picture \[.*?\] intentionally omitted <==", "", md)
            md = re.sub(r"-{3,} Start of picture text -{3,}.*?-{3,} End of picture text -{3,}",
                        "", md, flags=re.DOTALL)
            result[p] = md.split("\n")
    finally:
        fixer.close()
    print(f"  ligature repairs: {ligatures.repaired}")
    return result


@dataclass
class Marker:
    page: int
    title: str
    level: int                 # 1 chapter, 2 section, 3 sub-section (reference entries: 2)
    kind: str                  # entry | overview | chapter | section | subsection
    extra: list[str] = field(default_factory=list)   # continuation lines of wrapped titles
    meta: dict = field(default_factory=dict)          # metadata table of reference entries


@dataclass
class Unit:
    kind: str
    title: str
    heading_path: list[str]
    level: int
    page_start: int            # 1-based
    page_end: int              # 1-based
    markdown: str
    meta: dict = field(default_factory=dict)


def locate(md_pages: dict[int, list[str]], marker: Marker, cursor: tuple[int, int],
           fallback_label: str | None = None) -> tuple[int, int, bool] | None:
    """
    Find the Markdown line of a marker at or after `cursor` (page, line).
    Returns (page, line, synthetic) — synthetic=True when the title line itself
    was not found and the cut was placed at the metadata table instead.
    """
    target = norm(marker.title)
    pages = [p for p in sorted(md_pages) if cursor[0] <= p <= marker.page + 1]
    for p in pages:
        start = cursor[1] if p == cursor[0] else 0
        lines = md_pages[p]
        for i in range(start, len(lines)):
            if norm(lines[i]) == target:
                return p, i, False
        # Title merged with the next line (wrapped headings)
        for i in range(start, len(lines) - 1):
            if target and norm(lines[i]) and target.startswith(norm(lines[i])) \
                    and norm(lines[i] + lines[i + 1]).startswith(target[: len(norm(lines[i] + lines[i + 1]))]) \
                    and norm(lines[i] + lines[i + 1]) == target:
                return p, i, False
    if fallback_label:
        label = norm(fallback_label)
        for p in pages:
            start = cursor[1] if p == cursor[0] else 0
            lines = md_pages[p]
            for i in range(start, len(lines)):
                if label in norm(lines[i]):
                    # Cut above the table header (and above a directly preceding title fragment)
                    j = i
                    while j > start and not lines[j - 1].strip():
                        j -= 1
                    return p, j, True
    return None


def slice_markdown(md_pages: dict[int, list[str]], start: tuple[int, int],
                   end: tuple[int, int] | None) -> tuple[str, int, int]:
    """Concatenate Markdown from start (inclusive) to end (exclusive)."""
    out: list[str] = []
    pages = sorted(md_pages)
    last_page = start[0]
    for p in pages:
        if p < start[0] or (end and p > end[0]):
            continue
        lines = md_pages[p]
        a = start[1] if p == start[0] else 0
        b = end[1] if end and p == end[0] else len(lines)
        seg = lines[a:b]
        if any(l.strip() for l in seg):
            last_page = p
        out.extend(seg)
    return "\n".join(out), start[0] + 1, last_page + 1


def outside_fences(md: str, fn) -> str:
    """Apply fn(line) -> str | None to every line outside ``` fences (None drops the line)."""
    out, fenced = [], False
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        if fenced:
            out.append(line)
            continue
        res = fn(line)
        if res is not None:
            out.append(res)
    return "\n".join(out)


def clean_markdown(md: str) -> str:
    def fn(line: str) -> str | None:
        if re.fullmatch(r"\s*\d{1,4}\s*", line):          # page numbers
            return None
        if re.match(r"\s*Figure \d+[:.]?", line):          # figure captions
            return None
        return line
    md = outside_fences(md, fn)
    md = re.sub(r"```\n\s*```\n?", "", md)                # empty fences
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


# ─────────────────────────────────────────────────────────────
# Reference manuals (CommandRef, FunctionRef)
# ─────────────────────────────────────────────────────────────

METADATA_KEYS = {
    "commandgroup": "Command group",
    "functiongroup": "Function group",
    "flagaffected": "Flag affected",
    "reversible": "Reversible",
    "executeonclient": "Execute on client",
    "platform(s)": "Platform(s)",
    "platform(s": "Platform(s)",
    "platforms": "Platform(s)",
}

# Header cells can be clipped at the page edge ("Pla", "Execute on"): match by prefix.
METADATA_PREFIXES = [("commandg", "Command group"), ("functiong", "Function group"),
                     ("flag", "Flag affected"), ("rev", "Reversible"),
                     ("exec", "Execute on client"), ("pla", "Platform(s)")]


def metadata_key(text: str) -> str | None:
    n = norm(text)
    if n in METADATA_KEYS:
        return METADATA_KEYS[n]
    if len(n) >= 3:
        for prefix, key in METADATA_PREFIXES:
            if n.startswith(prefix) or (prefix.startswith(n) and len(n) >= 3):
                return key
    return None


def metadata_from_geometry(lines: list[Line], label_idx: int) -> dict:
    """
    Read the metadata table from PDF coordinates instead of rendered Markdown.
    Header cells form one row; each value belongs to the header column whose
    left edge is closest to (and not right of) the value's left edge. Values
    that wrap over two lines (e.g. "Reports and / Printing") are joined.
    """
    page = lines[label_idx].page
    headers: list[tuple[float, str]] = []
    k = label_idx
    while k < len(lines) and lines[k].page == page and metadata_key(lines[k].text) \
            and abs(lines[k].y - lines[label_idx].y) < 3:
        headers.append((lines[k].x, metadata_key(lines[k].text)))
        k += 1
    if not headers:
        return {}
    header_y = lines[k - 1].y
    headers.sort()
    values: dict[str, list[str]] = {h: [] for _, h in headers}
    while k < len(lines) and lines[k].page == page and not lines[k].mono \
            and lines[k].y - header_y < 45 and norm(lines[k].text) not in \
            {norm(s) for s in REFERENCE_SUBSECTIONS}:
        ln = lines[k]
        col = headers[0][1]
        for x, name in headers:
            if x <= ln.x + 6:
                col = name
        values[col].append(ln.text)
        k += 1
    return {h: " ".join(v).strip() for h, v in values.items() if v}


def reference_markers(doc: fitz.Document, cfg: dict, lines: list[Line]) -> tuple[list[Marker], list[str]]:
    """Entry markers = bold line directly before the metadata table label."""
    warnings: list[str] = []
    label = cfg["label"]
    markers: list[Marker] = []
    positions: list[int] = []
    for i, ln in enumerate(lines):
        # The label is regular in most tables, bold in some (bold header row).
        if ln.text != label or ln.mono:
            continue
        j = i - 1
        while j >= 0 and (re.fullmatch(r"\d{1,4}", lines[j].text) or not lines[j].text):
            j -= 1
        if j < 0:
            continue
        title_line = lines[j]
        if not title_line.bold or title_line.mono:
            warnings.append(f"p{ln.page + 1}: table without bold title (previous line: {title_line.text!r})")
            continue
        meta = metadata_from_geometry(lines, i)
        if len(meta) < 3:
            warnings.append(f"incomplete metadata for {title_line.text!r} (p{ln.page + 1}): {meta}")
        markers.append(Marker(page=title_line.page, title=title_line.text, level=2, kind="entry", meta=meta))
        positions.append(j)

    # Canonicalise titles with bookmarks when the PDF has them. Bookmarks without
    # a metadata table (e.g. "FileOps error codes") become their own sections.
    toc = [t for t in doc.get_toc() if t[0] == 3]
    if toc:
        by_norm = {norm(t[1]): t[1] for t in toc}
        found = {norm(m.title) for m in markers}
        for m in markers:
            if norm(m.title) in by_norm:
                m.title = by_norm[norm(m.title)]
            else:
                warnings.append(f"entry not in bookmarks (kept, title from page): {m.title!r} (p{m.page + 1})")
        first_entry_page = min(m.page for m in markers) if markers else 0
        for t in toc:
            if t[2] - 1 < first_entry_page or norm(t[1]) in found:
                continue
            idx = next((i for i, ln in enumerate(lines)
                        if ln.page == t[2] - 1 and ln.bold and norm(ln.text) == norm(t[1])), None)
            if idx is None:
                warnings.append(f"bookmark without detected entry: {t[1]!r} (p{t[2]})")
                continue
            markers.append(Marker(page=t[2] - 1, title=t[1], level=2, kind="section"))
            positions.append(idx)
        order = sorted(range(len(markers)), key=lambda k: positions[k])
        markers = [markers[k] for k in order]
    return markers, warnings


def overview_markers(doc: fitz.Document, cfg: dict) -> list[Marker]:
    titles = cfg.get("overview_titles")
    if not titles:
        return []
    toc = {t[1]: t[2] for t in doc.get_toc()}
    return [Marker(page=toc[t] - 1, title=t, level=2, kind="overview") for t in titles if t in toc]


def skip_own_label(md_pages: dict[int, list[str]], pos: tuple[int, int], label: str,
                   next_title: str | None) -> tuple[int, int]:
    """
    Cursor position just after the entry's own metadata label. The search stops
    at the next entry's title (or after ~25 lines), so it never skips an entry.
    """
    target = norm(label)
    stop = norm(next_title) if next_title else None
    budget = 25
    for p in sorted(md_pages):
        if p < pos[0]:
            continue
        lines = md_pages[p]
        start = pos[1] + 1 if p == pos[0] else 0
        for i in range(start, len(lines)):
            n = norm(lines[i])
            if stop and n == stop:
                return pos[0], pos[1] + 1
            if target in n:
                return p, i + 1
            budget -= 1
            if budget <= 0:
                return pos[0], pos[1] + 1
    return pos[0], pos[1] + 1


METADATA_TOKENS = {"yes", "no", "all", "windows", "macos", "linux", "ios", "android"}


def strip_metadata_rows(md: str, label: str, meta: dict) -> str:
    """
    Remove the rendered metadata table (in whatever form pymupdf4llm produced it)
    from the area between title and first sub-heading. Cells that carry other
    content (e.g. a Syntax block merged into the table) are kept as plain lines.
    """
    meta_values = {norm(v) for v in meta.values()} | {norm(k) for k in meta} \
        | {norm(k) for k in METADATA_KEYS.values()} | METADATA_TOKENS
    lines = md.split("\n")
    out: list[str] = []
    in_head = True
    for line in lines:
        s = line.strip()
        if in_head and s.startswith("### "):
            in_head = False
        if not in_head or s.startswith("## "):
            out.append(line)
            continue
        if s.startswith("|") or norm(label) in norm(s):
            if re.fullmatch(r"\|[-|: ]+\|?", s):
                continue
            cells: list[str] = []
            for c in s.strip("|").split("|"):
                cells.extend(x.strip() for x in c.split("<br>"))
            keep = [c for c in cells if c and norm(c) not in meta_values]
            if s.startswith("|"):
                out.extend(keep)
            else:
                # Flattened table text: drop it if it is only metadata words.
                rest = norm(s)
                for v in sorted(meta_values, key=len, reverse=True):
                    rest = rest.replace(v, "")
                if rest:
                    out.append(line)
            continue
        out.append(line)
    return "\n".join(out)


def metadata_line(meta: dict) -> str:
    return " | ".join(f"{k}: {v}" for k, v in meta.items())


def normalise_reference_markdown(md: str, title: str, label: str, meta: dict) -> str:
    """Title as H2 plus one metadata line, known labels as H3, other pseudo-headings demoted."""
    subsections = {norm(s) for s in REFERENCE_SUBSECTIONS}
    body = md.split("\n")
    # drop the located title line itself
    while body and not body[0].strip():
        body.pop(0)
    if body and norm(body[0]) == norm(title):
        body.pop(0)

    def fn(line: str) -> str:
        stripped = line.strip()
        if not stripped:
            return ""
        plain = re.sub(r"^#+\s*", "", stripped)
        plain_text = re.sub(r"[*_]", "", plain).strip()
        if norm(plain_text) in subsections and len(plain_text) < 25:
            return f"### {plain_text}"
        if stripped.startswith("#"):
            return plain if plain.startswith("`") else plain_text
        return line

    text = strip_metadata_rows("\n".join(body), label, meta)
    text = outside_fences(text, fn)
    head = f"## {title}\n\n" + (metadata_line(meta) + "\n\n" if meta else "")
    return clean_markdown(head + text)


def extract_reference(cfg: dict, doc: fitz.Document, pdf_path: Path) -> tuple[list[Unit], list[str]]:
    all_pages = list(range(doc.page_count))
    lines = collect_lines(doc, all_pages)
    markers, warnings = reference_markers(doc, cfg, lines)
    if not markers:
        raise RuntimeError(f"{cfg['source']}: no entries detected")
    first_entry_page = markers[0].page
    ov_markers = overview_markers(doc, cfg)
    ov_pages = [m.page for m in ov_markers] + [p - 1 for p in cfg.get("overview_pages", [])]
    pages = sorted(set(ov_pages) | set(range(first_entry_page, doc.page_count)))
    md_pages = page_markdown(pdf_path, pages)

    units: list[Unit] = []

    # Overview pages given by page number (no bookmarks)
    for p1 in cfg.get("overview_pages", []):
        md, ps, pe = slice_markdown(md_pages, (p1 - 1, 0), (p1 - 1, len(md_pages.get(p1 - 1, []))))
        md = clean_markdown(outside_fences(md, lambda l: re.sub(r"^#+\s*", "", l)))
        if md:
            title = f"{cfg['source']} overview"
            units.append(Unit("overview", title, [title], 2, ps, pe, f"## {title}\n\n{md}"))

    # Overview sections given by bookmarks: cut between consecutive bookmarks
    located_ov: list[tuple[Marker, tuple[int, int]]] = []
    cursor = (min(ov_pages), 0) if ov_pages else (0, 0)
    for m in ov_markers:
        pos = locate(md_pages, m, cursor)
        if pos is None:
            warnings.append(f"overview section not found in markdown: {m.title!r}")
            continue
        located_ov.append((m, pos[:2]))
        cursor = (pos[0], pos[1] + 1)

    # Entries
    located: list[tuple[Marker, tuple[int, int], bool]] = []
    cursor = (first_entry_page, 0)
    for idx, m in enumerate(markers):
        is_entry = m.kind == "entry"
        pos = locate(md_pages, m, cursor, fallback_label=cfg["label"] if is_entry else None)
        if pos is None:
            warnings.append(f"entry not found in markdown: {m.title!r} (p{m.page + 1})")
            continue
        located.append((m, pos[:2], pos[2]))
        # Continue searching behind this entry's own metadata table, so that a
        # following entry without a title line is not cut at *this* table.
        next_title = markers[idx + 1].title if idx + 1 < len(markers) else None
        cursor = skip_own_label(md_pages, pos[:2], cfg["label"], next_title) if is_entry \
            else (pos[0], pos[1] + 1)

    first_entry_pos = located[0][1] if located else None
    for k, (m, pos) in enumerate(located_ov):
        end = located_ov[k + 1][1] if k + 1 < len(located_ov) else first_entry_pos
        if end is not None and first_entry_pos is not None and end > first_entry_pos:
            end = first_entry_pos
        md, ps, pe = slice_markdown(md_pages, pos, end)
        md = clean_markdown(outside_fences(md, lambda l: re.sub(r"^#+\s*", "", l)))
        body = md.split("\n", 1)[-1] if norm(md.split("\n", 1)[0]) == norm(m.title) else md
        if len(body.split()) >= 15:
            units.append(Unit("overview", m.title, [m.title], 2, ps, pe, f"## {m.title}\n\n{body.strip()}"))

    for k, (m, pos, synthetic) in enumerate(located):
        end = located[k + 1][1] if k + 1 < len(located) else None
        md, ps, pe = slice_markdown(md_pages, pos, end)
        if synthetic:
            warnings.append(f"title line synthesised for {m.title!r} (p{m.page + 1})")
        md = normalise_reference_markdown(md, m.title, cfg["label"], m.meta)
        units.append(Unit(m.kind, m.title, [m.title], 2, ps, pe, md, meta=m.meta))

    # The list of obsolete commands sits on multi-column index pages that the
    # Markdown conversion drops; read it from the plain page text instead.
    obsolete_unit = next((u for u in units if u.kind == "overview" and u.title == "Obsolete Commands"), None)
    if obsolete_unit:
        names = []
        for p in range(first_entry_page):
            for raw in doc[p].get_text().split("\n"):
                m2 = re.fullmatch(r"\s*\*?\s*([A-Z][^*]{1,60}?)\s+OBSOLETE COMMAND\s*", raw)
                if m2 and m2.group(1) not in names:
                    names.append(m2.group(1))
        if names:
            obsolete_unit.markdown += "\n\nCommands marked OBSOLETE COMMAND:\n\n" + "\n".join(f"- {n}" for n in names)
    return units, warnings


# ─────────────────────────────────────────────────────────────
# Programming manual
# ─────────────────────────────────────────────────────────────

CHAPTER_RE = re.compile(r"^Chapter\s+(\d+)\s*[—–-]\s*(.+)$")


def is_toc_page(page: fitz.Page) -> bool:
    text = page.get_text()
    return text.count(". . . .") >= 5


def manual_markers(doc: fitz.Document, lines: list[Line]) -> list[Marker]:
    toc = doc.get_toc()
    if toc:
        return [Marker(page=t[2] - 1, title=t[1], level=min(t[0], 3),
                       kind={1: "chapter", 2: "section"}.get(t[0], "subsection")) for t in toc]

    markers: list[Marker] = []
    prev: Line | None = None
    for ln in lines:
        if ln.mono or not ln.bold or "montserrat" not in ln.font.lower():
            prev = None
            continue
        level = None
        if ln.size >= 10.5 and CHAPTER_RE.match(ln.text):
            level, kind = 1, "chapter"
        elif 8.8 <= ln.size < 10.5:
            level, kind = 2, "section"
        elif 7.5 <= ln.size <= 8.2 and ln.block_lines == 1 and len(ln.text) <= 90 \
                and not ln.text.endswith((".", ",", ":", ";")) and len(ln.text.split()) <= 12:
            level, kind = 3, "subsection"
        if level is None:
            prev = None
            continue
        # Wrapped heading: same level, same page, directly below the previous line
        if prev and markers and markers[-1].level == level and prev.page == ln.page \
                and 0 < ln.y - prev.y < prev.size * 1.8 and level <= 2:
            markers[-1].extra.append(ln.text)
            markers[-1].title += " " + ln.text
            prev = ln
            continue
        markers.append(Marker(page=ln.page, title=ln.text, level=level, kind=kind))
        prev = ln
    return markers


def locate_heading(md_pages: dict[int, list[str]], m: Marker, cursor: tuple[int, int]) -> tuple[int, int, int] | None:
    """Locate a heading as a standalone Markdown line. Returns (page, line, consumed_lines)."""
    target = norm(m.title)
    first = norm(m.title if not m.extra else m.title[: len(m.title) - len(" ".join(m.extra)) - 1])
    for p in sorted(md_pages):
        if p < cursor[0] or p > m.page:
            continue
        lines = md_pages[p]
        start = cursor[1] if p == cursor[0] else 0
        for i in range(start, len(lines)):
            n = norm(lines[i])
            if not n or lines[i].strip().startswith("|"):
                continue
            if n == target:
                return p, i, 1
            if m.extra and n == first:
                # consume continuation lines
                consumed, acc = 1, n
                k = i + 1
                while k < len(lines) and acc != target and len(acc) < len(target):
                    if norm(lines[k]):
                        acc += norm(lines[k])
                    consumed += 1
                    k += 1
                return p, i, consumed
    return None


def extract_manual(cfg: dict, doc: fitz.Document, pdf_path: Path) -> tuple[list[Unit], list[str]]:
    warnings: list[str] = []
    pages = [p for p in range(doc.page_count) if not is_toc_page(doc[p])]
    text_first = " ".join(doc[p].get_text() for p in pages[:3])
    lines = collect_lines(doc, pages)
    markers = manual_markers(doc, lines)
    # Drop everything before the first chapter heading (title page, copyright, "about")
    first_chapter = next((i for i, m in enumerate(markers) if m.kind == "chapter"), 0)
    pre = markers[:first_chapter]
    markers = markers[first_chapter:]
    md_pages = page_markdown(pdf_path, pages)

    located: list[tuple[Marker, int, int, int]] = []
    cursor = (markers[0].page, 0)
    not_found = 0
    for m in markers:
        pos = locate_heading(md_pages, m, cursor)
        if pos is None:
            if m.level <= 2:
                warnings.append(f"heading not found in markdown: L{m.level} {m.title!r} (p{m.page + 1})")
            not_found += 1
            continue
        located.append((m, *pos))
        cursor = (pos[0], pos[1] + pos[2])

    units: list[Unit] = []
    path: dict[int, str] = {}
    for k, (m, p, i, consumed) in enumerate(located):
        end = (located[k + 1][1], located[k + 1][2]) if k + 1 < len(located) else None
        md, ps, pe = slice_markdown(md_pages, (p, i + consumed), end)
        if m.kind == "chapter":
            cm = CHAPTER_RE.match(m.title)
            path = {1: f"Chapter {cm.group(1)}—{cm.group(2).strip()}"} if cm else {1: m.title}
        else:
            path = {lvl: t for lvl, t in path.items() if lvl < m.level}
            path[m.level] = m.title
        heading_path = [path[l] for l in sorted(path)]
        body = demote_pseudo_headings(md)
        units.append(Unit(m.kind, m.title, heading_path, m.level, ps, pe,
                          clean_markdown(f"{'#' * (m.level + 1)} {m.title}\n\n{body}")))
    warnings.append(f"{len(markers)} heading candidates, {len(located)} located, {not_found} not located "
                    f"(sub-section candidates that are table headers or inline bold are expected here)")
    return units, warnings


def demote_pseudo_headings(md: str) -> str:
    """Headings guessed by pymupdf4llm inside a unit are not structure: code → code, text → bold."""
    out = []
    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("#"):
            plain = re.sub(r"^#+\s*", "", s)
            if plain.startswith("`") and plain.endswith("`"):
                out.append("```\n" + plain.strip("`") + "\n```")
            else:
                text = re.sub(r"[*_]", "", plain).strip()
                out.append(f"**{text}**" if text else "")
        else:
            out.append(line)
    md = "\n".join(out)
    return re.sub(r"```\n```\n", "", md)  # merge adjacent fences created above


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def document_revision(doc: fitz.Document) -> str | None:
    text = " ".join(doc[p].get_text() for p in range(min(3, doc.page_count)))
    m = re.search(r"Revision\s+(\d{4,6})", text)
    return m.group(1) if m else None


def run(cfg: dict) -> None:
    pdf_path = PDF_DIR / cfg["pdf"]
    if not pdf_path.exists():
        print(f"  SKIP (not found): {pdf_path}")
        return
    doc = fitz.open(str(pdf_path))
    print(f"\n{cfg['source']}: {pdf_path.name}, {doc.page_count} pages, bookmarks: {len(doc.get_toc())}")
    if cfg["kind"] == "reference":
        units, warnings = extract_reference(cfg, doc, pdf_path)
    else:
        units, warnings = extract_manual(cfg, doc, pdf_path)

    EXTRACTED.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": cfg["source"],
        "pdf": cfg["pdf"],
        "omnis_version": OMNIS_VERSION,
        "revision": document_revision(doc),
        "pages": doc.page_count,
        "bookmarks": len(doc.get_toc()),
        "warnings": warnings,
        "units": [asdict(u) for u in units],
    }
    (EXTRACTED / f"{cfg['source']}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    md = "\n\n".join(f"<!-- p{u.page_start}-{u.page_end} | {' › '.join(u.heading_path)} -->\n{u.markdown}"
                     for u in units)
    (OUTPUT / f"{cfg['source']}_extracted.md").write_text(md, encoding="utf-8", newline="\n")

    kinds: dict[str, int] = {}
    for u in units:
        kinds[u.kind] = kinds.get(u.kind, 0) + 1
    print(f"  units: {kinds}")
    print(f"  warnings: {len(warnings)}")
    for w in warnings[:15]:
        print(f"    - {w}")
    if len(warnings) > 15:
        print(f"    ... {len(warnings) - 15} more in output/extracted/{cfg['source']}.json")


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    print("=== PDF extraction (structure from PDF, content from pymupdf4llm) ===")
    for cfg in SOURCES:
        if not wanted or cfg["source"] in wanted:
            run(cfg)
    print("\nDone.")
