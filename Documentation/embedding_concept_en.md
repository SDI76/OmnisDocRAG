# Embedding and Retrieval Concept: Omnis Studio RAG

## Core problem

Omnis-specific tokens such as `$cwind`, `$sendall`, `kTrue`, `kRelationalList` and `evClick` barely occur
in the training data of embedding models. Dense embeddings capture the *meaning* of a question well
("how do I loop over a list"), but are unreliable for exact names. The retrieval therefore combines
three signals: semantic similarity, weighted full text, and exact-name matching.

---

## Architecture

```text
User query (English or German)
    │
    ├── Dense embedding (bge-m3)          → 60 nearest chunks, all corpora
    ├── Full text (weighted tsvector)     → 60 best chunks, OR over the query words
    └── Name detection ($search, mid(),   → chunks that document that name
        Begin reversible block, #ERRCODE)
                    │
        Weighted Reciprocal Rank Fusion + exact-name boost   (one global ranking)
                    │
        One hit per entry/section, top_k (default 8), snippet per hit
                    │
        Agent reads the list, fetches full text of 1–3 ids (get_omnis_doc)
```

The ranking lives in the database function `rag.search_ranked`
(see [postgres_en.md](postgres_en.md)); the rag-server prepares the query (words, search syntax,
candidate names, German → English mapping of common words for the full-text leg).

### Why global ranking instead of top-k per corpus

v1 retrieved a fixed number of chunks from every corpus and sorted them by a per-corpus RRF score.
Rank 1 of every corpus got the same score, so unrelated commands or functions were mixed into
conceptual answers. A single ranking over all candidates fixed that: on the original 18 test queries
MRR@5 rose from 0.62 to 0.79 with the dense leg alone (see
[retrieval_quality_analysis_en.md](retrieval_quality_analysis_en.md)).

### Why full text still matters — and why it is weighted

| Query | Semantic | Full text |
|---|---|---|
| "how to iterate over a list" | good | weak (common words) |
| "`binfrombase64`" | neighbours (`binfrombase32`) | exact |
| "`$sendall` syntax" | good | good |
| `"reversible block"` (phrase) | — | exact |
| "Wie lösche ich Zeilen aus einer Liste?" | good (multilingual) | only via word mapping |

A naive full-text leg over the raw content (OR of all words, equal weight) made results worse in the
analysis (MRR 0.50), because long chunks with frequent words such as "list" dominate. The v2 full-text
leg therefore uses field weights (title A, heading path B, content C/D), stop-word removal,
length normalisation, and a lower fusion weight than the dense leg (`RAG_W_FTS`, default 0.3, chosen by a parameter sweep with `scripts/eval_retrieval.py`).
Exact names are handled by the separate boost, not by the full-text rank.

---

## Embedding model

### In use: `BAAI/bge-m3`

- multilingual (German questions against English documentation)
- local via `sentence-transformers` — no API key, no cost, no cloud dependency
- 1024 dimensions, normalised vectors, cosine distance
- the same model for indexing (`embed_and_store.py`) and queries (`ragserver.py`)

```text
Model:       BAAI/bge-m3
Dimensions:  1024
Download:    ~2.2 GB (HuggingFace cache; Docker volume hf_cache)
Cost:        $0
```

### What is embedded

`embed_text` of each chunk = one context line + the chunk text, for example

```text
Omnis command: OK message | Group: Message boxes | Flag affected: NO | Reversible: NO | … | DEPRECATED

## OK message
…
```

or `Omnis Programming manual | Chapter 7—SQL Programming › SQL Worker Objects › Overview`. The context
line gives short chunks their meaning (which entry, which chapter) and is not shown to the reader.
Local embedding limits the input to 512 tokens (`--max-seq-length`), which only shortens the longest
chunks; their beginning (title, metadata, syntax) is always embedded.

### Cost of building the embeddings

~6,000 chunks, ~1.7 M tokens:

| Hardware | Duration |
|---|---|
| Apple Silicon (MPS) / NVIDIA GPU | minutes |
| CPU only (12 threads) | 2–4 hours |

`embed_and_store.py` is incremental (only chunks whose text hash changed), writes checkpoints, and can
use the model inside the running rag-server container (`--server http://localhost:7071`).

### Storage

`output/embeddings.jsonl` holds one line per chunk with id, text hash, model, token limit and the
vector as exact float32 bytes in base64 (~5.6 KB per chunk, ~33 MB in total). The file is versioned in
git: embeddings built on a fast machine reach every other machine with a pull, and an import needs no
embedding step. A JSON list of numbers would be twice the size (the v1 file was 57 MB for 2,355 chunks).

### Alternatives considered

- `text-embedding-3-large` (OpenAI): planned originally; replaced by a fully local pipeline.
- Code models (`CodeBERT` …): Omnis is not in their training data.
- A cross-encoder reranker (e.g. `ms-marco-MiniLM`) after fusion is a possible next step; it is not
  used today — measure with `scripts/eval_retrieval.py` before adding it.

---

## Retrieval parameters

| Parameter | Where | Default |
|---|---|---|
| `mode` | tool / `/search` | `hybrid` (`semantic`, `fulltext`) |
| `top_k` | tool / `/search` | 8 (max 30) |
| `corpus` / `corpora` | tool / `/search` | all |
| candidates per leg | `rag.search_ranked` | 60 |
| RRF constant | `RAG_RRF_K` | 60 |
| dense / full-text weight | `RAG_W_DENSE` / `RAG_W_FTS` | 1.0 / 0.3 |
| exact-name boost | `rag.search_ranked` | 0.02 × words in the name |
| snippet length | `RAG_SNIPPET_CHARS` | 240 |

Metadata used at query time: corpus filter, one hit per `doc_key`, `[deprecated]` marker in the result
list. Further metadata (command group, execute on client, platform, pages) is stored with each chunk
and shown in the full text.

---

## How an agent uses it

1. `search_omnis_docs` → compact list (≈ 600–1,000 tokens for 8 hits).
2. `get_omnis_doc` for the relevant ids (≈ 300–600 tokens per chunk).

A typical question costs ~1,500–2,000 tokens of documentation context. v1 returned 15,000–25,000
tokens per search because the same text was sent up to four times.

Expected quality per area: [expected_outcome_en.md](expected_outcome_en.md).
