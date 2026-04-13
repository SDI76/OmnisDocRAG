# RAG Concept: Omnis Studio Documentation

## Goal

Create **three** separate vector databases from the Omnis PDFs that serve as the RAG foundation for an agentic IDE / AI assistance for Omnis Studio development.

| Collection | Source | Chunk Type |
|---|---|---|
| `omnis_commands` | CommandRef.pdf | 1 command = 1 chunk |
| `omnis_functions` | FunctionRef.pdf | 1 function = 1 chunk |
| `omnis_programming` | Programming_Omnis.pdf | 1 section (H2/H3) = 1 chunk |

---

## Document Analysis

### CommandRef.pdf (~200 pages) — NEW

**Structure:** Intro/index (pp. 1-10) + alphabetical command entries (p. 11-end)

**Pattern per command:**
```text
Command Name
─────────────────────────────────────────────────────
Command group │ Flag affected │ Reversible │ Execute on client │ Platform
Constructs    │ NO            │ NO         │ YES               │ All
─────────────────────────────────────────────────────
Syntax
Command Name ([Option1][,Option2])

Options
Option1    │ Description of what this option does
Option2    │ Description of what this option does

[Deprecated Command]  ← if deprecated
Description
Description of what the command does.

Example
# comment
Command Name (Option1)
Calculate lVar as ...
```

**Important differences from FunctionRef:**
- Additional **Options** field (parameters/keywords of the command)
- **Flag affected**: does the command set `#F`? Important for error handling
- **Reversible**: can the command be rolled back inside `Begin reversible block`?
- **Deprecated** marker: many old commands are deprecated and no longer visible in the code assistant

**Chunking:** 1 chunk = 1 command (natural separation from the structure)
- Chunk size: `~150-600` tokens (commands often contain more context than functions)
- Skip pages 1-10 (index pages, client command list, obsolete command list)

**Deprecated commands:** Keep them as chunks, but mark them with metadata `deprecated: true`.
Developers maintaining legacy code still need that information.

**Metadata per command chunk:**
```json
{
  "text": "...",
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
```

---

### FunctionRef.pdf (~150 pages)

**Structure:** Intro (pp. 1-7) + alphabetical function entries (p. 8-end)

**Pattern per function:**
```text
functionname()
─────────────────────────────────────────
Function group │ Execute on client │ Platform(s)
String         │ NO                │ All
─────────────────────────────────────────
Syntax
functionname(parameter1, parameter2)

Description
Description of what the function does.

Example
Calculate lResult as functionname('input')
# returns ...
```

**Chunking:** 1 chunk = 1 function (natural separation from the structure)
- Chunk size: `~100-400` tokens
- Skip pages 1-7 (index pages) since they have rendering issues and no RAG value

**Why Docling failed:** The overview tables on pp. 4-7 use multi-column layouts with overlapping text elements. Docling cannot parse them correctly, which causes extraction to fail.

---

### Programming_Omnis.pdf (~508 pages)

**Structure:** 11 chapters with clear H1/H2/H3 headings

**Chapter overview:**
| Chapter | Pages | Topic |
|---------|--------|-------|
| 1 | 9-83 | The Omnis Environment (IDE) |
| 2 | 84-114 | Libraries and Classes |
| 3 | 115-156 | Omnis Programming (Variables, Methods, Events) |
| 4 | 157-221 | Debugging Methods |
| 5 | 222-233 | Object Oriented Programming |
| 6 | 234-249 | List Programming |
| 7 | 250-285 | SQL Programming |
| 8 | 286-300 | SQL Classes and Notation |
| 9 | 301-368 | Server-Specific Programming |
| 10 | 369-405 | Report Programming |
| 11 | 406-508 | Window Components |

**Chunking:** 1 chunk = 1 section (H2/H3 level)
- Target size: `300-800` tokens
- Sections > `800` tokens: split with `~50-token` overlap
- Error-code tables (pp. ~107-115): keep as a single chunk `"Error Codes Reference"`

**What to remove:**
- TOC (pp. 1-6)
- Figure captions (`"Figure 73:"`, `"Figure 74:"`, etc.)
- Pure screenshot pages (detected as empty or image-dominant pages)
- Copyright pages

---

## Toolchain Used

- **PDF -> Markdown:** `pymupdf4llm` for structure + `pdfplumber` for correct code-block spacing fixes (hybrid approach, see `scripts/extract.py`)
- **Chunking:** custom regex parser (commands/functions) + header-based splitting (programming), see `scripts/chunk.py`
- **Embedding:** `sentence-transformers` with `BAAI/bge-m3` (local, 1024 dimensions)
- **Vector database:** PostgreSQL with `pgvector`, hybrid search via RRF (dense + BM25)

Full documentation: `Pipeline_en.md`

---

## Runtime Topology

The retrieval runtime has two separate components:

- `OmnisRAGServer/rag-server/ragserver.py`: local HTTP retrieval server
- `OmnisRAGServer/mcp-bridge/mcpserver.mjs`: stdio MCP bridge for VS Code

Startup order:

1. PostgreSQL must already contain the imported chunk and embedding data.
2. Start `rag-server`.
3. Start `mcp-bridge`.

The MCP bridge depends on the RAG server. It does not perform retrieval on its own.

---

## Pipeline Architecture

### Phase 1: Extraction

```python
# FunctionRef: Markdown extraction
import pymupdf4llm

md_text = pymupdf4llm.to_markdown("FunctionRef.pdf",
                                    page_chunks=False,
                                    show_progress=True)
# Result: one large Markdown file

# Programming_Omnis: page-by-page for better control
md_pages = pymupdf4llm.to_markdown("Programming_Omnis.pdf",
                                    page_chunks=True,  # one list entry per page
                                    show_progress=True)
```

### Phase 2: Chunking

**FunctionRef — regex-based splitting:**
```python
import re

# Every function starts with the pattern: "functionname()\n"
# followed by the metadata table
pattern = r'\n(?=\*\*\w+\(.*?\)\*\*\n)'  # Bold function name
# or adjust to the Markdown output if needed
chunks = re.split(r'\n(?=#{3} \w+\()', md_text)
```

**Programming_Omnis — header-based splitting:**
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "chapter"),
    ("##", "section"),
    ("###", "subsection"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
chunks = splitter.split_text(md_text)

# Afterwards: RecursiveCharacterTextSplitter for oversized chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter
final_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". "]
)
```

### Phase 3: Metadata per chunk

**FunctionRef chunk:**
```json
{
  "text": "...",
  "source": "FunctionRef",
  "function_name": "abs",
  "function_group": "Number",
  "execute_on_client": true,
  "platform": "All",
  "has_example": true
}
```

**Programming chunk:**
```json
{
  "text": "...",
  "source": "Programming_Omnis",
  "chapter": 3,
  "chapter_title": "Omnis Programming",
  "section": "Variables",
  "subsection": "Declaration and Scope",
  "page_start": 116
}
```

### Phase 4: Embedding & vector database

**Embedding model:**
- `text-embedding-3-small` (OpenAI) — inexpensive, good for English
- or `bge-m3` (local/Ollama) — free, good

**Vector database:**
- **ChromaDB** for development/local use (simple, Python-native)
- **Qdrant** for production (fast, Docker-friendly)
- Two separate collections: `omnis_functions` + `omnis_programming`

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
functions_col = client.get_or_create_collection("omnis_functions")
programming_col = client.get_or_create_collection("omnis_programming")
```

---

## Irrelevant Sections (to skip)

### FunctionRef:
- Pages 1-7: intro, function overview lists, copyright
- `"The OWEB functions have been removed..."` (deprecated notice)

### Programming_Omnis:
- Pages 1-6: table of contents
- All `"Figure N:"` captions without surrounding text
- `"About This Manual"` (p. 7): boilerplate
- Copyright pages
- Pure screenshot pages (detected as pages with < 100 characters of text)

**Filter rule:**
```python
def is_relevant_page(page_text: str) -> bool:
    # Skip pages with almost no text (pure images/screenshots)
    if len(page_text.strip()) < 100:
        return False
    # Remove figure-only lines
    page_text = re.sub(r'\nFigure \d+:.*?\n', '\n', page_text)
    return True
```

---

## Quality Control — Test Questions

**FunctionRef:**

- "What parameters does `binfrombase64()` accept?"
- "Which functions can execute on the client?"
- "How do I calculate the average of a list column?"

**Programming:**

- "What is the difference between instance and class variables in Omnis?"
- "How do I set up a database connection?"
- "What is the `$root` notation?"
