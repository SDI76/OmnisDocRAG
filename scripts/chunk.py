"""
chunk.py — Markdown → JSON Chunks
Splits all three extracted Markdown files into RAG-ready chunks with metadata.
Output: output/chunks/commands_chunks.json, functions_chunks.json, programming_chunks.json
"""

import re
import json
import unicodedata
from pathlib import Path

BASE   = Path(__file__).parent.parent
INPUT  = BASE / "output"
OUTPUT = BASE / "output" / "chunks"
OUTPUT.mkdir(parents=True, exist_ok=True)

# H2 headings that are subsections, not command/function/section names
SUBSECTIONS = frozenset([
    "Syntax", "Description", "Options", "Example", "Examples",
    "Parameters", "Notes", "Note", "Commands", "Functions",
    "About This Manual", "Copyright info", "Omnis Software Ltd",
    "Omnis Programming",
])


# ─────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────

def strip_heading(line: str) -> str | None:
    """
    Extract text from a markdown H2 heading line.
    '## **# Comment**'  → '# Comment'
    '## `Begin critical block`' → 'Begin critical block'
    '## acos()'         → 'acos()'
    Returns None if not an H2 heading.
    """
    m = re.match(r"^##\s+(.+?)\s*$", line.strip())
    if not m:
        return None
    h = re.sub(r"[`*_]", "", m.group(1)).strip()
    return h if h else None


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)[:80]


def clean_text(text: str) -> str:
    """Remove page numbers (standalone integers) and figure captions."""
    # Standalone page numbers (a line that is just digits)
    text = re.sub(r"(?m)^\d+\s*$", "", text)
    # Figure captions
    text = re.sub(r"\nFigure \d+[:.][^\n]*", "", text)
    # Picture placeholders from pymupdf4llm
    text = re.sub(r"==> picture \[.*?\] intentionally omitted <==", "", text)
    text = re.sub(r"-{3,} Start of picture text -{3,}.*?-{3,} End of picture text -{3,}", "", text, flags=re.DOTALL)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────
# Metadata prefix helpers
# ─────────────────────────────────────────────────────────────

def cmd_prefix(meta: dict) -> str:
    """One-line metadata summary prepended to every CommandRef chunk text."""
    flag       = "YES" if meta["flag_affected"] else "NO"
    reversible = "YES" if meta["reversible"] else "NO"
    client     = "YES" if meta["execute_on_client"] else "NO"
    dep        = " | DEPRECATED" if meta["deprecated"] else ""
    return (
        f"Command: {meta['command_name']} | "
        f"Group: {meta['command_group']} | "
        f"Flag: {flag} | Reversible: {reversible} | "
        f"Client: {client} | Platform: {meta['platform']}"
        f"{dep}"
    )


def fn_prefix(meta: dict) -> str:
    """One-line metadata summary prepended to every FunctionRef chunk text."""
    client = "YES" if meta["execute_on_client"] else "NO"
    return (
        f"Function: {meta['function_signature']} | "
        f"Group: {meta['function_group']} | "
        f"Client: {client} | Platform: {meta['platform']}"
    )


def prog_prefix(meta: dict) -> str:
    """One-line metadata summary prepended to every Programming chunk text."""
    return (
        f"Programming_Omnis | "
        f"Chapter {meta['chapter_number']}: {meta['chapter_title']} | "
        f"Section: {meta['section']}"
    )


# ─────────────────────────────────────────────────────────────
# CommandRef chunking
# ─────────────────────────────────────────────────────────────

def extract_command_metadata(chunk_text: str, heading: str) -> dict:
    """Parse the command metadata table from a chunk."""
    # Table row after the header row: |Constructs|NO|NO|YES<br>All|
    m = re.search(
        r"\|Command group\|Flag affected\|Reversible\|Execute on client.*?\n"
        r"\|[-|]+\|\n"
        r"\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",
        chunk_text, re.DOTALL
    )
    if m:
        group     = m.group(1).strip()
        flag      = "YES" in m.group(2).upper()
        reversible = "YES" in m.group(3).upper()
        client_raw = m.group(4)
        client     = "YES" in client_raw.upper()
        platform   = re.search(r"(All|Windows|macOS)", client_raw)
        platform   = platform.group(1) if platform else "All"
    else:
        group, flag, reversible, client, platform = "", False, False, False, "All"

    deprecated = bool(re.search(r"deprecated|OBSOLETE", chunk_text, re.IGNORECASE))
    has_options = bool(re.search(r"\*\*Options\*\*|\n## .*Option", chunk_text))

    return {
        "source": "CommandRef",
        "command_name": heading,
        "command_group": group,
        "flag_affected": flag,
        "reversible": reversible,
        "execute_on_client": client,
        "platform": platform,
        "deprecated": deprecated,
        "has_options": has_options,
    }


def find_boundaries(lines: list[str]) -> list[tuple[int, str]]:
    """
    Find H2 heading boundaries that are not subsections.
    Uses lookahead: a heading is a real entry boundary only if |Command group|
    or |Function group| appears within the next 10 lines.
    This reliably skips syntax-demo headings (e.g. '## Build search list (options)')
    that appear inside Syntax sections and have no metadata table.
    """
    boundaries: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        h = strip_heading(line)
        if not h or h in SUBSECTIONS or h.startswith("•"):
            continue
        # Lookahead: check if a metadata table follows within 10 lines
        for j in range(i + 1, min(i + 10, len(lines))):
            l = lines[j]
            if "|Command group|" in l or "|Function group|" in l:
                boundaries.append((i, h))
                break
            if l.strip().startswith("##"):
                break  # hit another heading without finding a table → not an entry
    return boundaries


def split_if_large(chunk: dict, max_words: int = 700) -> list[dict]:
    """Split a chunk that exceeds max_words, preserving metadata."""
    words = chunk["text"].split()
    if len(words) <= max_words:
        return [chunk]
    size, overlap = 500, 50
    parts = []
    i, part = 0, 0
    while i < len(words):
        segment = words[i: i + size]
        c = dict(chunk)
        c["id"] = f"{chunk['id']}_p{part}"
        c["text"] = " ".join(segment)
        c["metadata"] = {**chunk["metadata"], "part": part}
        parts.append(c)
        i += size - overlap
        part += 1
    return parts


def chunk_commands() -> list[dict]:
    path = INPUT / "CommandRef_extracted.md"
    md   = clean_text(path.read_text(encoding="utf-8"))
    lines = md.split("\n")

    boundaries = find_boundaries(lines)

    chunks = []
    for idx, (line_num, heading) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        text = "\n".join(lines[line_num:end]).strip()

        if "Command group" not in text:
            continue

        meta = extract_command_metadata(text, heading)
        chunk = {
            "id": f"cmd_{slugify(heading)}",
            "text": text,
            "metadata": meta,
        }
        for c in split_if_large(chunk):
            c["text"] = cmd_prefix(meta) + "\n\n" + c["text"]
            chunks.append(c)

    return chunks


# ─────────────────────────────────────────────────────────────
# FunctionRef chunking
# ─────────────────────────────────────────────────────────────

def extract_function_metadata(chunk_text: str, heading: str) -> dict:
    m = re.search(
        r"\|Function group\|Execute on client\|Platform.*?\n"
        r"\|[-|]+\|\n"
        r"\|([^|]+)\|([^|]+)\|([^|]+)\|",
        chunk_text, re.DOTALL
    )
    if m:
        group  = re.sub(r"[_*]", "", m.group(1)).strip()
        client = "YES" in m.group(2).upper()
        platform = re.search(r"(All|Windows|macOS)", m.group(3))
        platform = platform.group(1) if platform else "All"
    else:
        group, client, platform = "", False, "All"

    has_example = "## **Example" in chunk_text or "## **Examples" in chunk_text

    return {
        "source": "FunctionRef",
        "function_name": heading.rstrip("()").strip(),
        "function_signature": heading,
        "function_group": group,
        "execute_on_client": client,
        "platform": platform,
        "has_example": has_example,
    }


def chunk_functions() -> list[dict]:
    path = INPUT / "FunctionRef_extracted.md"
    md   = clean_text(path.read_text(encoding="utf-8"))
    lines = md.split("\n")

    boundaries = find_boundaries(lines)

    chunks = []

    # Handle content before the first boundary (abs() has no H2 heading)
    if boundaries:
        pre_text = "\n".join(lines[: boundaries[0][0]]).strip()
        if "Function group" in pre_text:
            # Extract function name from picture alt text or first word
            name_m = re.search(r"End of picture text -----\s*\n+\s*\|Function group", pre_text)
            # fall back: find function name before the table
            head_m = re.search(r"(\w+\(\))", pre_text)
            heading = head_m.group(1) if head_m else "abs()"
            meta = extract_function_metadata(pre_text, heading)
            chunks.append({
                "id": f"fn_{slugify(heading)}",
                "text": fn_prefix(meta) + "\n\n" + pre_text,
                "metadata": meta,
            })

    for idx, (line_num, heading) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        text = "\n".join(lines[line_num:end]).strip()

        if "Function group" not in text:
            continue

        meta = extract_function_metadata(text, heading)
        chunk = {
            "id": f"fn_{slugify(heading)}",
            "text": text,
            "metadata": meta,
        }
        for c in split_if_large(chunk):
            c["text"] = fn_prefix(meta) + "\n\n" + c["text"]
            chunks.append(c)

    return chunks


# ─────────────────────────────────────────────────────────────
# Programming_Omnis chunking
# ─────────────────────────────────────────────────────────────

CHAPTER_PATTERN = re.compile(r"^## \*\*Chapter (\d+)—(.+?)\*\*\s*$")
EXCLUDED_CHAPTERS = {1, 4}   # IDE environment + Debugging UI


def chunk_programming() -> list[dict]:
    path = INPUT / "Programming_extracted.md"
    md   = clean_text(path.read_text(encoding="utf-8"))
    lines = md.split("\n")

    # Find Chapter 2 start — discard everything before it
    chapter2_line = 0
    for i, line in enumerate(lines):
        m = CHAPTER_PATTERN.match(line.strip())
        if m and int(m.group(1)) == 2:
            chapter2_line = i
            break

    # Collect all H2 boundaries from Chapter 2 onwards
    boundaries: list[tuple[int, str]] = []
    for i in range(chapter2_line, len(lines)):
        line = lines[i].strip()
        h = strip_heading(line)
        if h:
            boundaries.append((i, h, line))  # (line_idx, clean_heading, raw_line)
    # Note: programming guide does not deduplicate — chapter structure is clean

    chunks = []
    current_chapter_num  = 0
    current_chapter_title = ""

    for idx, (line_num, heading, raw_line) in enumerate(boundaries):
        end = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        text = "\n".join(lines[line_num:end]).strip()

        # Check if this is a chapter heading
        cm = CHAPTER_PATTERN.match(raw_line)
        if cm:
            current_chapter_num   = int(cm.group(1))
            current_chapter_title = cm.group(2).strip()
            # Chapter intro text (between chapter heading and first section)
            # Keep as a chunk only if it has meaningful content
            content_only = re.sub(r"^##.*\n", "", text, count=1).strip()
            # Remove bullet summary lines (## • ...)
            content_only = re.sub(r"(?m)^## •.*$", "", content_only).strip()
            if len(content_only.split()) < 30:
                continue  # Skip near-empty chapter headers
        elif current_chapter_num in EXCLUDED_CHAPTERS:
            continue
        elif heading.startswith("•"):
            # Bullet summary entries at start of chapter — skip
            continue
        elif heading in SUBSECTIONS:
            continue

        # Remove bullet point intro lines from text body
        text_clean = re.sub(r"(?m)^## •.*$", "", text).strip()
        word_count = len(text_clean.split())

        if word_count < 30:
            continue  # Too small

        chunk_id = f"prog_ch{current_chapter_num:02d}_{slugify(heading)}"
        meta = {
            "source": "Programming_Omnis",
            "chapter_number": current_chapter_num,
            "chapter_title": current_chapter_title,
            "section": heading,
            "word_count": word_count,
        }
        prefix = prog_prefix(meta)

        # If chunk is very large, split it
        if word_count > 700:
            sub_chunks = split_large_chunk(text_clean, chunk_id, current_chapter_num, current_chapter_title, heading)
            for c in sub_chunks:
                c["text"] = prefix + "\n\n" + c["text"]
            chunks.extend(sub_chunks)
        else:
            chunks.append({
                "id": chunk_id,
                "text": prefix + "\n\n" + text_clean,
                "metadata": meta,
            })

    return chunks


def split_large_chunk(text: str, base_id: str, ch_num: int, ch_title: str, section: str) -> list[dict]:
    """Split an oversized chunk into ~500-word pieces with 50-word overlap."""
    words = text.split()
    size, overlap = 500, 50
    sub_chunks = []
    i = 0
    part = 0
    while i < len(words):
        segment = words[i : i + size]
        sub_chunks.append({
            "id": f"{base_id}_p{part}",
            "text": " ".join(segment),
            "metadata": {
                "source": "Programming_Omnis",
                "chapter_number": ch_num,
                "chapter_title": ch_title,
                "section": section,
                "part": part,
                "word_count": len(segment),
            },
        })
        i += size - overlap
        part += 1
    return sub_chunks


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def save(chunks: list[dict], filename: str) -> None:
    # Deduplicate IDs by appending a counter suffix
    from collections import Counter
    id_counts: Counter = Counter()
    for c in chunks:
        id_counts[c["id"]] += 1
        if id_counts[c["id"]] > 1:
            c["id"] = f'{c["id"]}_{id_counts[c["id"]]}'

    out = OUTPUT / filename
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    sizes = [len(c["text"].split()) for c in chunks]
    avg   = sum(sizes) // len(sizes) if sizes else 0
    print(f"  {filename}: {len(chunks)} chunks, avg {avg} words, min {min(sizes)}, max {max(sizes)}")


if __name__ == "__main__":
    print("=== Chunking ===")

    print("\nCommandRef...")
    cmd_chunks = chunk_commands()
    save(cmd_chunks, "commands_chunks.json")

    print("\nFunctionRef...")
    fn_chunks = chunk_functions()
    save(fn_chunks, "functions_chunks.json")

    print("\nProgramming_Omnis...")
    prog_chunks = chunk_programming()
    save(prog_chunks, "programming_chunks.json")

    total = len(cmd_chunks) + len(fn_chunks) + len(prog_chunks)
    print(f"\nTotal: {total} chunks across 3 collections")
    print("Output: output/chunks/")
