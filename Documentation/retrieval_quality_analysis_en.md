# Retrieval Quality Analysis and Improvement Plan

Status: analysis 2026-09-28; implemented on branch `retrieval-rework` (see section 7).
Scope: the Docker stack `docker_mcp-rag-pg` (which builds `docker_mcp-rag/rag-server` and `docker_mcp-rag/mcp-server`) and the ingestion pipeline in `scripts/`.

Goal: an index that is **as complete as the PDFs**, usable for **semantic and full-text search**, with **compact responses** so each tool call stays cheap for the calling agent.

---

## 1. Summary

The embedding model (`BAAI/bge-m3`) is not the problem. The weak points are, in order of impact:

1. **Response payload** — an MCP call returns 50–105 KB; the same text is included up to four times.
2. **Ranking** — fixed `k` per corpus plus a per-corpus RRF score mixes off-topic hits into the top results.
3. **Full-text leg** — the lexical query ANDs every word, so it almost never matches natural-language questions.
4. **Extraction and chunking** — the PDFs contain the information, but the pipeline loses 13% of the commands, 7% of the functions, and turns 220 code lines into section titles.
5. **Coverage** — only three manuals; notation and several topics are not in the index.

A ranking-only change (one global vector ranking across all corpora, no re-ingestion) already lifts MRR@5 from 0.62 to 0.79 on the test set.

---

## 2. Method

- 18 queries covering commands, functions, notation, concepts, SQL, JSON, JavaScript remote forms, one exact symbol name and one German question.
- Each query has a `gold` regex that must match the title of a relevant chunk (`corpus :: command_name | function_signature | section`).
- Metrics on the top 5: **Hit@5** (gold present) and **MRR@5** (mean reciprocal rank of the first gold hit).
- Query set: [`scripts/eval_queries.json`](../scripts/eval_queries.json); runner: [`scripts/eval_retrieval.py`](../scripts/eval_retrieval.py).

```bash
python scripts/eval_retrieval.py --param k_commands=4 --param k_functions=4 --param k_programming=10
```

Caveat: 18 queries with self-defined gold patterns show a trend, not proof. The data-quality findings in section 4.4 are exact counts.

---

## 3. Baseline results

| Variant | Hit@5 | MRR@5 | Notes |
|---|---|---|---|
| **Current** (`search_omnis_docs` defaults, k = 4/4/10) | 14/18 | 0.62 | avg 52 KB HTTP, ~100 KB via MCP |
| Global vector ranking over all corpora (SQL experiment) | 16/18 | **0.79** | same index, no re-ingestion |
| Global hybrid with naive OR full-text query (SQL experiment) | 12/18 | 0.50 | lexical leg on raw content hurts |

Latency: 140–220 ms warm; the first request after container start took ~14.6 s (model warm-up).

Queries failing in all variants: `binfrombase64` (chunk does not exist, see 4.4) and `set the current line of a list` (`$line` — notation not indexed, see 4.5).

---

## 4. Findings

### 4.1 Response payload and token cost

`mcp-server/server.py` returns `resp.text`, i.e. the full `/search` JSON:

- `chunks[].content` **and** `context_text` contain the same text (×2).
- The tools declare a `str` return type, so FastMCP adds an `outputSchema` and sends the result again as `structuredContent` (×2 again).
- Default `k` values return 14–20 chunks per call.

Measured: 50 KB per query over HTTP, 105 KB for one MCP call (Q01). That is roughly 25k tokens per search.

### 4.2 Ranking: fixed k per corpus + RRF across corpora

`rag.search_omnis_docs` runs `search_hybrid` once per corpus and concatenates the results ordered by `rrf_score`.
RRF is rank-based, so rank 1 of *every* corpus gets the same score (~1/61), regardless of how similar it actually is.
Result: for "extract a substring from a string" the top 3 are an Oracle XML section, `Strip()` and `MailSplit`; `mid()` is not in the top 5.
The three MCP tools differ only in their `k` defaults, which makes it the caller's job to guess the right mix.

### 4.3 Full-text leg

- `search_hybrid` builds `to_tsquery('simple', 'w1 & w2 & ...')`. Every word, including stop words, must occur in the chunk → for natural-language questions `fts_rank` is empty in most results.
- Special characters (`$`, `#`, `()`) can make `to_tsquery` fail; the exception is swallowed and the leg silently disappears.
- `content_tsv` uses the `simple` config (no stemming) over the whole content, with no field weighting. A naive switch to OR makes results worse (MRR 0.50) because long chunks with common words (`list`, `line`) dominate.
- The inline fallback in `ragserver.py` uses `websearch_to_tsquery` — a different behaviour than the DB function.

Full-text search is wanted, but it needs its own design (section 5, phase 3), not just OR instead of AND.

### 4.4 Extraction and chunking

The PDFs contain the information. It is lost in the pipeline.

**CommandRef.pdf** (499 command bookmarks)

| Stage | Count |
|---|---|
| Bookmarks (level 3, from page 11) | 499 |
| Metadata tables in `CommandRef_extracted.md` | 491 |
| Distinct commands in `commands_chunks.json` | 434 |
| **Missing** | **66 (13%)** — e.g. `OK message`, `Yes/No message`, `For each line in list`, `Quit all methods`, `Open window instance`, `Do async method`, `HTTPGet`, `HTTPPost`, `SMTPSend`, `While flag true` |
| Chunks without parsed `command_group` | 168 of 485 |

Root causes:

- `pymupdf4llm` sometimes renders the command title as `**Name**` instead of `## Name` (34 cases). `find_boundaries()` only accepts H2 lines, so the entry is appended to the previous chunk (`Advise on find/next/previous` ends up inside `Add line to list`).
- The metadata table comes in three header variants; `extract_command_metadata()` only parses the 5-column one. The variant `|Reversible<br>Execute on client<br>Platform(s)|` (169 tables) yields an empty group and wrong flags.
- The PDF has **508 bookmarks with page numbers** (LaTeX/hyperref). They are not used; they would give exact entry boundaries.

**FunctionRef.pdf**

| Stage | Count |
|---|---|
| Metadata tables in `FunctionRef_extracted.md` | 352 |
| Chunks in `functions_chunks.json` | 327 |
| **Missing** | **≥ 25 (7%)** — e.g. `binfrombase64()`, `abs()`, `int()`, `bool()`, `errtext()`, `coalesce()`, `charat()` |

Root causes: same bold-title problem (29 titles as `**name()**`); `abs()` is only recovered by a special case. This PDF was re-saved through PDFium and **has no bookmarks**.

**Programming_Omnis.pdf** (614 pages, re-saved through macOS Preview, **no bookmarks**)

- 220 of 1,543 chunks have a **code line as section title** (`Do StatementObj.$prepare() Returns #F`, `.omh text eol=crlf`, `OK message SQL Error {...}`), which also splits sections in the middle.
- Root cause (font profile, pages 85–400):

  | Font | Size | Used for |
  |---|---|---|
  | Montserrat-Bold | 11.0 | Chapter titles |
  | Montserrat-Bold | 9.2 | Section titles |
  | **LMMono10-Regular** | **9.6** | **Code** |
  | Montserrat-Bold | 7.7 | Sub-section titles and inline bold |
  | Montserrat-Regular | 7.8 | Body text |

  `pymupdf4llm` guesses headings by font size; code (9.6 pt) is larger than section titles (9.2 pt), so code lines become headings. A font-aware extractor separates them unambiguously.
- No heading path: a chunk only knows its chapter and its own heading, not the parent section.
- 164 chunks share a title with another chunk (`Session Properties` ×15), which makes titles ambiguous in results.
- `skip_pages` in `extract.py` is hard-coded for a 508-page edition; with the 614-page file it is off by about one page (page index 156, still chapter 3, is skipped). The chapter filter in `chunk.py` catches the rest.

### 4.5 Coverage

- Indexed: CommandRef, FunctionRef, Programming (without chapters 1 and 4).
- Not indexed: the **notation reference** (`$line`, `$search`, `$sendall` as members of list/window/... objects), external component documentation beyond what FunctionRef contains (OJSON, web services), JavaScript/web client component documentation.
- The tools advertise an `omnis-code` corpus that does not exist.

### 4.6 Repository hygiene

- `scripts/.env` and `OmnisRAGServer/rag-server/.env` are tracked despite `.gitignore` (since the initial commit) and contain a DB password. The repository is public.
- `ragserver.py` exists twice (`docker_mcp-rag/rag-server/`, `OmnisRAGServer/rag-server/`), currently identical.
- `Documentation/chunking_concept_en.md` describes a 508-page Programming manual with 11 chapters; the current file has 614 pages and chapters up to 17.

---

## 5. Improvement plan

Rebuilding the index is cheap, so the plan favours a clean re-ingestion over patching the existing chunks. Every phase ends with a run of `scripts/eval_retrieval.py`; results are recorded in section 6.

### Phase 1 — Server: payload and ranking (no re-ingestion)

1. **Compact response.** The MCP tools return formatted text only: per hit `title`, `source + page`, `chunk_id`, content. No raw JSON, no `context_text` duplicate, no `structuredContent` (declare the tools without output schema).
2. **Two-stage retrieval.** `search` returns a ranked list with a short snippet per hit (for full-text: `ts_headline`); a separate `get_chunk(chunk_id)` returns the full text on demand. Target: ≤ 5 KB per search call.
3. **One global ranking** across all corpora with a single `top_k` (default 6–8) and an optional `corpus` filter instead of fixed `k` per corpus. Consolidate the three tools into one search tool with a `mode` parameter (see phase 3).
4. **Group by entry**: at most one chunk per command/function/section in the result list.
5. **Warm-up** the embedding model at startup.

Acceptance: MRR@5 ≥ 0.79, average response ≤ 5 KB, no regression on any query.

### Phase 2 — Re-ingestion with correct boundaries

1. **CommandRef: bookmark-based splitting.** Use `fitz.get_toc()` for entry titles and page ranges; the title from the bookmark is authoritative. Verify: chunk count = bookmark count (499).
2. **FunctionRef and Programming: font-based structure** read directly via PyMuPDF spans:
   - title/heading = Montserrat-Bold at the heading sizes, standalone line;
   - code = LMMono lines → fenced code block (keeps the correct spacing from `pdfplumber` / x-tolerance);
   - FunctionRef entry = heading line followed by the `Function group` table.
   Alternatively obtain the original PDFs with bookmarks (the current FunctionRef and Programming files were re-saved and lost them).
3. **Metadata table parser** that handles all three header variants (normalise `<br>` into separate columns before parsing).
4. **Heading path** per chunk (`Chapter › Section › Sub-section`) in metadata and in the embedded prefix; replaces ambiguous titles like `Session Properties`.
5. **Page numbers** (`page_start`, `page_end`) in metadata for citations.
6. **Validation step** (`scripts/validate.py`, already mentioned in the concept but missing): counts per source against bookmarks/tables, no chunk title that looks like code, no empty `command_group`, no chunk above the size limit.

Acceptance: 499 commands, ≥ 352 functions, 0 code-line titles, 0 chunks without group.

### Phase 3 — Real full-text search

1. **Weighted tsvector**: `setweight(title/symbol, 'A') || setweight(heading path, 'B') || setweight(content, 'D')`.
2. **Two configs**: `english` for prose (stemming, stop words) and `simple` for symbol tokens; keep `$name`, `#NAME`, `name()` as tokens (normalise before indexing and querying).
3. **Query building**: `websearch_to_tsquery` (supports quotes, OR, `-`) with stop-word removal; never a hard AND over all words.
4. **Modes** in the search tool:
   - `semantic` — vector only;
   - `fulltext` — lexical only, ranked by `ts_rank_cd` with weights, snippets via `ts_headline`;
   - `hybrid` (default) — RRF of both, computed **globally**, not per corpus.
5. **Exact-title boost**: if the query equals a command/function title, that entry is rank 1.
6. Optional: a trigram index (`pg_trgm`) on titles for typo-tolerant name search.

Acceptance: exact-name queries (Q03 and similar) at rank 1 in `fulltext` and `hybrid`; hybrid not worse than semantic on the test set.

### Phase 4 — Coverage

1. Add the notation reference and further manuals (external components, web/JavaScript client) as separate corpora.
2. Remove `omnis-code` from the tool descriptions until it exists.
3. Extend `eval_queries.json` by at least 10 queries per new corpus.

### Phase 0 / housekeeping (can run in parallel)

- ~~Remove the tracked `.env` files from git, rotate the DB password~~ — not needed: the database is
  local, runs in Docker and holds no confidential data (owner decision).
- Keep a single `ragserver.py`.
- Update `chunking_concept_en.md` after phase 2.

---

## 6. Results log

| Date | Change | Queries | Mode | Hit@5 | MRR@5 | Answer size |
|---|---|---|---|---|---|---|
| 2026-09-28 | Baseline (v1) | 18 | mixed per corpus | 14/18 | 0.62 | 52 KB HTTP, ~105 KB MCP |
| 2026-09-28 | Rework, first run (`w_fts` 0.5) | 40 | hybrid | 37/40 | 0.86 | 1.9 KB |
| 2026-09-28 | + German word stems, sweep → `w_fts` 0.3, `rrf_k` 60 | 40 | hybrid | **39/40** | **0.92** | 1.9 KB |
| 2026-09-28 | same | 40 | semantic | 37/40 | 0.86 | 1.9 KB |
| 2026-09-28 | same | 40 | fulltext | 34/40 | 0.71 | 1.9 KB |
| 2026-09-28 | same, original 18 queries only | 18 | hybrid | 17/18 | 0.82 | 1.9 KB |

Notes on the measurement:

- The query set grew from 18 to 40 (notation, exact names, German, 11.1 additions, overview). For five of
  the original queries the expected-hit pattern was widened to accept an id (e.g. `not_list_properties`),
  because notation answers are member groups whose title does not name the member.
- Parameter sweep (hybrid, 40 queries): `rrf_k` ∈ {10, 20, 40, 60} × `w_fts` ∈ {0.3, 0.5, 0.7, 1.0} —
  every combination 39/40; MRR 0.87–0.92, `w_fts` 0.3 best for every `rrf_k`. `rrf_k` stays at the
  standard 60 (0.919 vs. best 0.921) to avoid tuning to 40 questions.
- Remaining miss Q18 ("set the current line of a list"): the answer (`$line`) is one line inside the
  "List properties" member chunk and is outranked by the list commands. Smaller notation member groups
  would fix this but need a full re-embedding — candidate for the next round.
- Latency (warm, CPU container): hybrid ~240 ms, semantic ~180 ms, fulltext ~80 ms.
- Answer size over MCP: 1.5–3.5 KB per search (v1: ~105 KB); `get_omnis_doc` returns the full text of
  the chosen ids.

Sizes after the rework: 5,918 chunks (5.3 MB text), `output/embeddings.jsonl` 33 MB (base64 float32,
versioned), database 123 MB (chunks 27 MB, embeddings incl. HNSW index 82 MB).

---

## 7. Implementation (2026-09-28)

### What was built

| Plan item | Implementation |
|---|---|
| Phase 1.1 compact response | rag-server renders plain text; MCP tools have no output schema; no JSON, no duplicates |
| Phase 1.2 two-stage retrieval | `search_omnis_docs` (snippets + ids) and `get_omnis_doc` (`/chunks`) |
| Phase 1.3 global ranking | `rag.search_ranked`: dense and full-text candidates over all selected corpora, weighted RRF |
| Phase 1.4 grouping | one hit per `doc_key` |
| Phase 1.5 warm-up | model encodes once at startup |
| Phase 2.1/2.2 boundaries | entries from the bold title before the metadata table, canonicalised with bookmarks; programming headings by font; LMMono never a heading |
| Phase 2.3 metadata | read from PDF coordinates instead of rendered tables |
| Phase 2.4/2.5 heading path, pages | in every chunk and in the embedded context line |
| Phase 2.6 validation | `scripts/validate.py` (hard gate) |
| Phase 3 full text | weighted `search_tsv` (title A, heading B, content C/D), OR queries without stop words, `websearch` syntax, exact-name boost via `symbols`, modes `hybrid` / `semantic` / `fulltext` |
| Phase 4 coverage | all 17 programming chapters; notation corpus and 11.1 additions from the doc pack |
| Housekeeping | one `ragserver.py`; `omnis-code` removed; docs updated |

Additional findings during the implementation:

- **Ligature loss in tables.** PyMuPDF expands "fi"/"fl" into two characters at the same position and
  its table extraction drops the second one (`specifed`, `frst`, `usequalifers`). Repaired with a
  vocabulary from the intact page text — 1,158 repairs, 0 damaged words left.
- **Entries without title line.** When the title is rendered inside a table, the cut is placed at the
  metadata table; the search for the next entry now starts behind the current entry's own table
  (before, an entry could end up empty).
- **Obsolete command list** is on multi-column index pages that the Markdown conversion drops — read
  from plain page text.
- **Docker init ran the bootstrap twice.** The postgres entrypoint executes every top-level `*.sql` in
  `docker-entrypoint-initdb.d`; `20-rag-bootstrap.sql` failed the second time (no password variables).
  The SQL files now live in `postgres-init/sql/`.
- **`mcp` 2.x breaks the MCP server.** The unpinned requirement pulled `mcp` 2.x (FastMCP renamed) on
  rebuild; pinned to `<2`.
- **Embedding cost.** ~1.7 M tokens with bge-m3: minutes on GPU / Apple Silicon, hours on a plain CPU.
  `embed_and_store.py` is incremental (text hash) and checkpoints, and can use the rag-server's model.

### Data after the rework

| | Before | After |
|---|---|---|
| Commands | 434 (66 of 499 lost) | 499 from the PDF + 4 new in 11.1 + 2 error-code sections + 5 overviews |
| Functions | 327 | 357 from the PDF + 23 new in 11.1 |
| Programming | 1,543 chunks, chapters 1 and 4 excluded, 220 code-line titles | 1,883 chunks, chapters 1–17, 0 code-line titles |
| Notation | — | 3,055 chunks (1,121 nodes) |
| Ligature damage | ~770 words | 0 |
