"""
extract.py — PDF → Markdown
Converts all three Omnis PDFs to Markdown using a hybrid approach:
  - pymupdf4llm  → correct document structure (headings, tables, bold, italic)
  - pdfplumber   → correct text spacing in code blocks (monospace font detection)

pymupdf4llm strips spaces from code in PDF code blocks (glyphs are position-encoded,
not space-encoded). pdfplumber handles this correctly via x_tolerance-based word grouping.

Output: output/CommandRef_extracted.md, FunctionRef_extracted.md, Programming_extracted.md
"""

import re
import pymupdf4llm
import pdfplumber
from pathlib import Path

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "output"
OUTPUT.mkdir(exist_ok=True)

DOCS = [
    {
        "pdf": "CommandRef.pdf",
        "out": "CommandRef_extracted.md",
        # Pages 1-10 are index pages (Command group overviews, obsolete lists)
        # pymupdf4llm pages are 0-indexed, so skip pages 0-9
        "skip_pages": list(range(10)),
    },
    {
        "pdf": "FunctionRef.pdf",
        "out": "FunctionRef_extracted.md",
        # Pages 1-7 are intro/index pages with broken multi-column layout
        "skip_pages": list(range(7)),
    },
    {
        "pdf": "Programming_Omnis.pdf",
        "out": "Programming_extracted.md",
        # Chapter 1 (IDE/Environment): pages 8-82  (0-indexed)
        # Chapter 4 (Debugging UI):    pages 156-220
        # TOC: pages 0-5
        "skip_pages": list(range(6)) + list(range(8, 83)) + list(range(156, 221)),
    },
]


# ─────────────────────────────────────────────────────────────
# pdfplumber: extract monospace-font lines (code) per page
# ─────────────────────────────────────────────────────────────

def get_code_lines(pdf_path: str, page_index: int) -> list[str]:
    """
    Return all lines on this page that use a monospace font (code).
    Uses x_tolerance=2 for tight word grouping to preserve intra-word spacing.
    Returns lines as correctly-spaced strings.
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words(
            extra_attrs=["fontname"],
            x_tolerance=2,
            y_tolerance=3,
        )

    # Group words into lines by rounded y-coordinate (top edge)
    line_map: dict[int, list[dict]] = {}
    for w in words:
        y = round(w["top"])
        line_map.setdefault(y, []).append(w)

    code_lines = []
    for y in sorted(line_map.keys()):
        wds = sorted(line_map[y], key=lambda w: w["x0"])
        # A line is "code" when its first word is in a monospace font
        fn = wds[0].get("fontname", "")
        if "Mono" in fn or "Courier" in fn or "mono" in fn.lower() or "Code" in fn:
            code_lines.append(" ".join(w["text"] for w in wds))

    return code_lines


# ─────────────────────────────────────────────────────────────
# Fix code blocks in a page's markdown using pdfplumber lines
# ─────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Normalize a string for matching: remove all whitespace."""
    return re.sub(r"\s+", "", s)


def _prefix_match(norm_query: str, norm_candidates: list[str]) -> str | None:
    """
    Find a candidate whose normalized form starts with norm_query.
    Returns the candidate string if found, else None.
    Used when pymupdf4llm truncates a line that pdfplumber renders in full.
    """
    for cand_norm, cand_orig in norm_candidates:
        if cand_norm == norm_query:
            return cand_orig
        if len(cand_norm) > len(norm_query) and cand_norm.startswith(norm_query):
            # pdfplumber line is longer — reconstruct by counting non-space chars
            # Walk the original candidate text and take chars until we've matched
            # norm_query's length worth of non-space characters.
            count = 0
            cut = 0
            for i, ch in enumerate(cand_orig):
                if ch != " ":
                    count += 1
                if count == len(norm_query):
                    cut = i + 1
                    break
            return cand_orig[:cut] if cut else cand_orig
    return None


def fix_code_blocks(md_text: str, code_lines: list[str]) -> str:
    """
    Replace content inside ``` code blocks with correctly-spaced versions
    from pdfplumber. Matches lines by comparing normalized (spaceless) text.

    Two-pass matching:
      1. Exact match: normalized pymupdf line == normalized pdfplumber line
      2. Prefix match: normalized pdfplumber line starts with normalized pymupdf
         line (handles cases where pymupdf4llm truncates a longer source line).

    Lines with no match are kept as-is.
    """
    if not code_lines:
        return md_text

    # Build lookup: normalized → correctly spaced (exact match)
    lookup: dict[str, str] = {}
    norm_list: list[tuple[str, str]] = []  # (normalized, original) for prefix matching
    for line in code_lines:
        key = _norm(line)
        if key:
            lookup[key] = line
            norm_list.append((key, line))

    def replace_block(m: re.Match) -> str:
        content = m.group(1)
        fixed = []
        for line in content.splitlines():
            key = _norm(line)
            if not key:
                fixed.append(line)
                continue
            if key in lookup:
                fixed.append(lookup[key])
            else:
                prefix = _prefix_match(key, norm_list)
                fixed.append(prefix if prefix is not None else line)
        return "```\n" + "\n".join(fixed) + "\n```"

    return re.sub(r"```\n(.*?)\n```", replace_block, md_text, flags=re.DOTALL)


# ─────────────────────────────────────────────────────────────
# Main extraction
# ─────────────────────────────────────────────────────────────

def extract(doc: dict) -> None:
    pdf_path = BASE / doc["pdf"]
    out_path = OUTPUT / doc["out"]

    if not pdf_path.exists():
        print(f"  SKIP (not found): {pdf_path.name}")
        return

    import fitz
    total_pages = fitz.open(str(pdf_path)).page_count
    skip = set(doc["skip_pages"])
    pages_to_extract = [p for p in range(total_pages) if p not in skip]

    print(f"\n{doc['pdf']}: {total_pages} pages total, extracting {len(pages_to_extract)} pages...")

    # Step 1: pymupdf4llm page-by-page for correct structure
    page_chunks = pymupdf4llm.to_markdown(
        str(pdf_path),
        pages=pages_to_extract,
        page_chunks=True,
        show_progress=True,
    )

    # Step 2: per-page code-block fix using pdfplumber
    fixed_pages = []
    for chunk in page_chunks:
        page_index = chunk["metadata"]["page_number"] - 1  # page_number is 1-indexed
        md = chunk["text"]

        if "```" in md:
            code_lines = get_code_lines(str(pdf_path), page_index)
            md = fix_code_blocks(md, code_lines)

        fixed_pages.append(md)

    # Step 3: join pages
    full_md = "\n\n".join(fixed_pages)

    out_path.write_text(full_md, encoding="utf-8")
    size_kb = out_path.stat().st_size // 1024
    print(f"  -> {out_path.name} ({size_kb} KB, {len(full_md.splitlines())} lines)")


if __name__ == "__main__":
    print("=== PDF Extraction (hybrid: pymupdf4llm + pdfplumber code-fix) ===")
    for doc in DOCS:
        extract(doc)
    print("\nDone. Check output/ folder.")
