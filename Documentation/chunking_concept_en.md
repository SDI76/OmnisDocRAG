# Chunking Concept: Omnis Studio RAG

## Overview

Three documents -> three separate collections -> three different chunking strategies.

| Collection | Source | Strategy | Chunk Unit |
|---|---|---|---|
| `omnis_commands` | CommandRef.pdf | Atomic command chunking | 1 command = 1 chunk |
| `omnis_functions` | FunctionRef.pdf | Atomic function chunking | 1 function = 1 chunk |
| `omnis_programming` | Programming_Omnis.pdf | Semantic section chunking | 1 H2/H3 section = 1 chunk |

---

## Extraction (`extract.py`)

`extract.py` uses a **hybrid approach** to generate correct Markdown output:

- **pymupdf4llm** (`page_chunks` mode): provides document structure such as H2 headings, bold/italic text, and tables
- **pdfplumber**: fixes spacing inside code blocks

### Why hybrid?

`pymupdf4llm` loses spaces in code blocks, for example `CalculatelCountas1` instead of `Calculate lCount as 1`. The reason is that code in PDFs is positioned via glyph spacing rather than real space characters. `pdfplumber` handles this correctly using `x_tolerance`-based word detection.

### Per-page flow

1. `pymupdf4llm` extracts the page into Markdown with correct structure but broken code blocks
2. `pdfplumber` extracts mono-font lines (LMMono / Courier) from the same page
3. Code-block lines are replaced by normalized text matching (spaceless comparison)
4. Prefix matching handles cases where `pymupdf4llm` renders a shorter line than `pdfplumber`

### Result (as of April 2026)

| Document | Total code lines | Still incorrect |
|---|---|---|
| CommandRef | 3809 | 4 (< 0.1%) |
| FunctionRef | 683 | 7 (1%) |
| Programming_Omnis | 2226 | ~60 (3%, most of them legitimately spaceless) |

---

## CommandRef.pdf

### Document structure
- Pages 1-10: index pages (command-group overviews, client command list, obsolete commands) -> **skip**
- Page 11-end: alphabetical command entries -> **chunk**

### Chunk structure (observed)
Every command entry follows this exact pattern:
```text
Command Name (bold, heading level)
───────────────────────────────────────────────────────
Command group │ Flag affected │ Reversible │ Execute on client │ Platform
Constructs    │ NO            │ NO         │ YES               │ All
───────────────────────────────────────────────────────
Syntax
Command Name ([Option1][,Option2])

Options (optional, not all commands have this field)
Option1  │ Description
Option2  │ Description

[Deprecated Command] (optional, if deprecated)

Description
Body text...

Example
# comment
Omnis code...
```

### Chunk size
- Minimum: `~100` tokens (simple commands without options)
- Maximum: `~600` tokens (commands with many options and a long example)
- Average: `~250` tokens

### No overlap
These units are atomic and fully self-contained. Overlap would only add noise.

### Deprecated commands
**Keep them**, but mark them with metadata flag `deprecated: true`.
Reason: developers working with legacy code still need this information. Retrieval can later filter them via metadata.

### Pages to skip
- Pages 1-10 completely (intro, group overviews, client command list, obsolete command list, copyright)
- Detection rule: pages with < 200 characters of extracted text -> skip

### Splitting approach after Markdown extraction
After extraction, command names are rendered as H2 headings.
`chunk.py` uses lookahead: an H2 heading is only treated as a real command boundary if a `|Command group|` table appears within the next 10 lines. This reliably filters out syntax demo headings.

```python
# Simplified view; real logic lives in scripts/chunk.py
chunks = [c for c in h2_sections if 'Command group' in c]
```

### Metadata per chunk
```json
{
  "id": "cmd_{command_name_slug}",
  "text": "Command: Begin reversible block | Group: Constructs | Flag: NO | Reversible: NO | Client: NO | Platform: All\n\n## **Begin reversible block**\n...",
  "metadata": {
    "source": "CommandRef",
    "command_name": "Begin reversible block",
    "command_group": "Constructs",
    "flag_affected": false,
    "reversible": false,
    "execute_on_client": false,
    "platform": "All",
    "deprecated": false,
    "has_options": false
  }
}
```

The `text` field starts with a metadata line (`cmd_prefix()`), followed by a blank line and the full chunk Markdown. That gives the embedding model immediate context, even for short chunks.

Metadata is extracted from the `|Command group|` table in the chunk text via regex (logic in `scripts/chunk.py: extract_command_metadata()`).

---

## FunctionRef.pdf

### Document structure
- Pages 1-7: intro, function-group overview, client function list, copyright -> **skip**
- Page 8-end: alphabetical function entries -> **chunk**

### Chunk structure (observed)
```text
functionname()
───────────────────────────────────────
Function group │ Execute on client │ Platform(s)
Number         │ YES               │ All
───────────────────────────────────────
Syntax
functionname(parameter1[, parameter2])

Description
Body text...

Example
Calculate lResult as functionname(argument)
# returns ...
```

### Chunk size
- Minimum: `~80` tokens
- Maximum: `~400` tokens
- Average: `~180` tokens

### Splitting approach
Same lookahead logic as CommandRef: an H2 heading is only a real function boundary if a `|Function group|` table appears within the next 10 lines.

### Rendering note

The overview pages 4-7 (Function Groups tables) contain overlapping text in the PDF rendering. Since those pages are skipped (`skip_pages: range(7)`), this is not a problem for the RAG.

### Metadata per chunk
```json
{
  "id": "fn_{function_name}",
  "text": "Function: abs() | Group: Number | Client: YES | Platform: All\n\n## abs()\n...",
  "metadata": {
    "source": "FunctionRef",
    "function_name": "abs",
    "function_signature": "abs()",
    "function_group": "Number",
    "execute_on_client": true,
    "platform": "All",
    "has_example": true
  }
}
```

---

## Programming_Omnis.pdf

### Document structure (508 pages)

| Chapter | Pages | RAG-relevant? |
|---|---|---|
| 1 — The Omnis Environment | 9-83 | **NO** — IDE navigation, screenshots |
| 2 — Libraries and Classes | 84-114 | YES |
| 3 — Omnis Programming | 115-156 | YES — core chapter |
| 4 — Debugging Methods | 157-221 | **NO** — debugger UI |
| 5 — Object Oriented Programming | 222-233 | YES |
| 6 — List Programming | 234-249 | YES |
| 7 — SQL Programming | 250-285 | YES |
| 8 — SQL Classes and Notation | 286-300 | YES |
| 9 — Server-Specific Programming | 301-368 | YES |
| 10 — Report Programming | 369-405 | YES |
| 11 — Window Components | 406-508 | YES (partially) |

**Exclude chapters 1 and 4 entirely** -> saves about `~140` pages (27% of the document) and removes IDE screenshots and menu descriptions that add no RAG value.

### Three chunk types

**Type A — Concept chunk** (H2 section with explanatory text):
Mostly prose with explanatory text, possibly with tables.
Target size: `300-600` tokens.

**Type B — Pattern chunk** (section primarily made of code examples):
Contains Omnis code examples embedded in explanatory text.
Never separate code examples from their explanation.
Target size: `200-500` tokens.

**Type C — Reference chunk** (tables/lists with reference data):
For example variable scope tables, operator precedence tables, error codes.
Keep as a single chunk, even if somewhat smaller.

### What to remove
```python
import re

def clean_programming_page(text: str) -> str:
    # Remove figure captions
    text = re.sub(r'\nFigure \d+:.*?\n', '\n', text)
    # "About This Manual" boilerplate (page 7)
    # Copyright pages
    # Pages with < 150 chars (pure screenshot pages)
    return text

def is_relevant_page(page_text: str) -> bool:
    return len(page_text.strip()) >= 150
```

### Splitting approach

Every H2 heading in the extracted Markdown becomes one chunk. Oversized chunks (> 700 words) are split into 500-word pieces with 50-word overlap. Minimum size: 30 words (smaller chunks are discarded).

**Overlap rule:** 50-word overlap when splitting large chunks.

### Exclude chapters 1 and 4

Already excluded at extraction time: `extract.py` does not pass those pages to `pymupdf4llm`. `chunk.py` additionally filters by `chapter_number in {1, 4}`.

### Small chunks: no merging

About 15% of Programming chunks are below 50 words. These come from:
- Legitimate short sections (complete concepts in 30-50 words)
- Code demo headings (the PDF uses code snippets as section titles)

**Decision: do not merge neighboring chunks.** Reason: the H2 boundaries are semantic units, and merging would join unrelated sections, for example `"Closing a Library"` + `"Omnis VCS"`. `text-embedding-3-large` handles short, self-contained chunks well. The metadata prefix also gives short chunks enough context for retrieval.

### Metadata per chunk

```json
{
  "id": "prog_ch03_{section_slug}",
  "text": "Programming_Omnis | Chapter 3: Omnis Programming | Section: Variables\n\n## **Variables**\n...",
  "metadata": {
    "source": "Programming_Omnis",
    "chapter_number": 3,
    "chapter_title": "Omnis Programming",
    "section": "Variables",
    "word_count": 312
  }
}
```

---

## Output Files

### Stage 1: Extracted Markdown
```text
/output/
  CommandRef_extracted.md       (~500 KB)
  FunctionRef_extracted.md      (~300 KB)
  Programming_extracted.md      (~2 MB, without chapters 1+4)
```

### Stage 2: JSON chunks (ready to embed)
```text
/output/chunks/
  commands_chunks.json          (~400 entries, ~500 KB)
  functions_chunks.json         (~350 entries, ~350 KB)
  programming_chunks.json       (~300 entries, ~750 KB)
```

### Chunk format (uniform across all three collections)
```json
{
  "id": "string (unique)",
  "text": "string (full chunk text, metadata as readable prose at the front)",
  "metadata": { ... }
}
```

The `text` field contains the metadata as a readable prefix so the embedding context is correct:
```text
"Calculate\nCommand group: Calculations | Flag: YES | Client: YES\n\nSyntax: Calculate variable as expression\n\nDescription: ..."
```

---

## Quality Control

### Automatic checks
```python
def validate_chunk(chunk: dict) -> list[str]:
    issues = []
    tokens = len(chunk["text"].split())
    if tokens < 30:
        issues.append(f"Too small: {tokens} tokens")
    if tokens > 1000:
        issues.append(f"Too large: {tokens} tokens")
    if "Figure" in chunk["text"] and ":" in chunk["text"]:
        issues.append("Possible figure caption not removed")
    return issues
```

### Manual spot checks after extraction
After stage 1 (Markdown), verify:
- [ ] Are command/function names correctly recognized as headings?
- [ ] Are code blocks (`` ``` ``) formatted correctly?
- [ ] Are metadata tables readable (not rendered as gibberish)?
- [ ] No overlapping table text (known problem on FunctionRef pages 4-7)?

### Test queries after ingestion
```text
omnis_commands:    "How do I use Begin reversible block?"
                   "What commands set the flag?"
omnis_functions:   "What parameters does binfrombase64() accept?"
                   "How do I calculate average of list column?"
omnis_programming: "What is the difference between instance and class variables?"
                   "How do I navigate the object tree with $root?"
```

---

## Script Structure

```text
/scripts/
  extract.py          # PDF -> Markdown (hybrid: pymupdf4llm + pdfplumber)
  chunk.py            # Markdown -> JSON chunks (with metadata prefix)
  validate.py         # Chunk quality checks
  embed_and_store.py  # JSON chunks -> vector database
```

Each script runs independently. Output from step N becomes input to step N+1.
That makes every step individually testable and repeatable when needed.
