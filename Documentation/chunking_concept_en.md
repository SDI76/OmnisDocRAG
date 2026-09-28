# Extraction and Chunking Concept

## Overview

| Corpus | Source | Chunk unit | Chunks (Sept 2026) |
|---|---|---|---|
| `omnis-commands` | `CommandRef.pdf` (+ doc pack for 11.1 additions) | 1 command; overview sections | 585 |
| `omnis-functions` | `FunctionRef.pdf` (+ doc pack for 11.1 additions) | 1 function | 395 |
| `omnis-programming` | `Programming_Omnis.pdf`, all 17 chapters | 1 sub-section with heading path | 1,883 |
| `omnis-notation` | Omnis doc pack (11.1 help), optional | 1 node overview + member groups | 3,055 |

Pipeline: `extract.py` → `chunk.py` → `validate.py` → `embed_and_store.py` → `import_to_postgres.py`.
Each step reads the output of the previous one from `output/`.

---

## Why the PDFs are hard

The manuals in `Omnis PDF/` are the files Omnis shipped; FunctionRef and Programming were re-saved
(PDFium, macOS Preview) because the originals were hard to read. The consequences:

| Property | CommandRef | FunctionRef | Programming |
|---|---|---|---|
| Bookmarks | 508 (one per command) | none | none |
| Headings tagged in the PDF | no | no | no |
| Entry title font | Montserrat-Bold 8 pt, same as "Syntax" labels | same | — |
| Section titles | — | — | Montserrat-Bold 9.2 pt (sections), 7.7 pt (sub-sections), 11 pt (chapters) |
| Code font | LMMono10 **10 pt** | LMMono10 10 pt | LMMono10 **9.6 pt** — larger than section titles |
| Code spacing | glyphs positioned without space characters | same | same |

`pymupdf4llm` converts pages to good Markdown (tables, lists, bold text) but guesses headings from
font size. It therefore

- turned **code lines into headings** (220 of 1,543 v1 programming chunks had a code line as title),
- rendered some entry titles as **bold text** instead of a heading, so the v1 chunker merged the
  entry into the previous one (66 of 499 commands and ≥ 25 functions were lost),
- lost the **"fi"/"fl" ligatures inside tables** ("specifed", "frst", "fag") — PyMuPDF expands a
  ligature into two characters at the same position and its table extraction drops the second one.

---

## Extraction (`scripts/extract.py`)

**Principle: structure from the PDF, content from pymupdf4llm.**

1. `pymupdf4llm` renders every page to Markdown (`page_chunks=True`).
2. **Code spacing** is repaired per page with `pdfplumber` (x-tolerance word grouping of LMMono lines),
   matching lines by their space-free form.
3. **Ligatures** are repaired with a vocabulary built from the plain page text (which is intact):
   an unknown word is corrected when exactly one insertion of "i" or "l" after an "f" yields a known
   word. 1,158 repairs, e.g. `specifed → specified`, `usequalifers → usequalifiers`, `fag → flag`.
4. The **document structure** is read from the PDF itself (PyMuPDF spans with font and position):
   - **CommandRef / FunctionRef:** an entry starts at the bold line directly before its metadata
     table label ("Command group" / "Function group"). Bookmarks, when present, canonicalise titles;
     bookmarks without a table ("FileOps error codes", "Web Command Error Codes") become sections.
   - **Programming:** chapter / section / sub-section headings by font (Montserrat-Bold at 11 / 9.2 /
     ~7.7 pt, standalone line). LMMono lines are never headings. With bookmarks, the bookmarks are used.
5. The page Markdown is **cut at those markers**. A marker is located as a standalone Markdown line;
   if the title line is missing (title rendered inside a table), the cut is placed at the metadata
   table. The search for the next entry starts behind the current entry's own table, so no entry can
   swallow the next one.
6. **Heading markup is rewritten** consistently: entry title `##`, labels (`Syntax`, `Options`,
   `Description`, `Example`) `###`; every other heading guessed by pymupdf4llm is demoted to text,
   code-like ones become code blocks. Code blocks are never touched by these rewrites.
7. **Metadata tables** are read from PDF coordinates (header cells and the value below them), not
   from the rendered Markdown, which comes in three table variants and sometimes as plain text.
   Header cells clipped at the page edge ("Pla") are matched by prefix.
8. Special cases: the list of **obsolete commands** sits on multi-column index pages that the Markdown
   conversion drops; it is read from the plain page text. The multi-column function group lists of
   FunctionRef (pages 3–7) are skipped — the group of each function is in its metadata.

Output: `output/extracted/<source>.json` (units with title, heading path, pages, Markdown, metadata)
and `output/<source>_extracted.md` for manual inspection.

---

## Chunking (`scripts/chunk.py`)

### Uniform chunk format

```json
{
  "id": "cmd_ok_message",
  "corpus": "omnis-commands",
  "title": "OK message",
  "heading_path": ["OK message"],
  "text": "## OK message\n\nCommand group: Message boxes | Flag affected: NO | ...",
  "embed_text": "Omnis command: OK message | Group: Message boxes | ... | DEPRECATED\n\n## OK message ...",
  "metadata": {"source": "CommandRef", "omnis_version": "11", "page_start": 178, "doc_key": "cmd_ok_message", ...}
}
```

- `text` is what a reader gets; `embed_text` adds one context line and is what gets embedded.
- `doc_key` groups the parts of one entry; search returns one hit per `doc_key`.
- Size limit 450 words. Longer entries are split at paragraph boundaries; oversized single blocks
  are split by table rows (header repeated), code lines or sentences. Every part repeats the entry
  header (title and metadata line).

### Commands and functions

- One entry = one chunk; the metadata line (`Command group: … | Flag affected: … | …`) replaces the
  rendered table.
- Metadata fields: `command_name`, `command_group`, `flag_affected`, `reversible`,
  `execute_on_client`, `platform` (functions: `function_name`, `function_signature`,
  `function_group`, …), `page_start`, `page_end`.
- With the doc pack:
  - `deprecated`, `deprecation` and `modern_equivalent` come from the Omnis 11.1 help (the PDF has no
    reliable flag). 153 commands are classified as legacy there, e.g. `OK message`
    (`deprecated_no_replacement`).
  - Entries that exist in the 11.1 help but not in the PDF (Studio 11.0, rev. 35659) are added from the
    help: `If`, `Else If`, `While`, `Until`, `coalesce()`, `bool()`, `charat()`, `FileOps.$copy()` …
    (`source: OmnisDocPack`).
  - PDF commands that the 11.1 help no longer lists get `in_help_11_1: false` and a note (119 legacy
    commands such as the DDE and Advise groups).

### Programming manual

- One chunk per sub-section; `heading_path` = chapter › section › sub-section, repeated in the
  embedding context line. All 17 chapters are included (v1 excluded chapters 1 and 4).
- Units without a real body (a heading directly followed by a sub-heading) are merged into the next
  unit of the same section instead of becoming near-empty chunks.

### Notation (doc pack)

The PDFs contain no notation reference. With the doc pack (`--omnisdoc PATH` or `OMNISDOC_PACK`) each
notation page (1,121 nodes) becomes:

- a **node chunk**: description plus the names of its properties, methods, events, standard members
  and child nodes (e.g. `Children: $bobjs $objs $toolbars …`),
- **member chunks** of ~300 words: `- \`$line\` — The current line in the list …`, deprecated members
  marked.

---

## Validation (`scripts/validate.py`)

Hard checks (exit code 1):

- CommandRef: every bookmark from the first command on has a unit (499/499).
- FunctionRef: entries = metadata tables in the PDF (357/357).
- Programming: chapters 1–17 consecutive; no section title looks like code.
- No ligature damage; unique ids; no empty or oversized chunk; all fields present.

Informational: commands and functions that exist only in the doc pack or only in the PDF.
Report: `output/validation_report.json`.
