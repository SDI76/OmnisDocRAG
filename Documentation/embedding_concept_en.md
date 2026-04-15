# Embedding Concept: Omnis Studio RAG

## Core problem

Omnis-specific tokens such as `$cwind`, `$sendall`, `kTrue`, `kRelationalList`, and `evClick` do not exist in the training corpora of embedding models. The model does not understand them semantically because they are effectively unknown tokens.

Consequence: pure dense-embedding retrieval fails for exact notation lookups. The architecture has to compensate for that.

---

## Architecture: Hybrid Search (mandatory)

```text
User Query
    │
    ├─── Dense Embedding ──────────────────────────┐
    │    (semantic: "how do I iterate over a list")│
    │                                               │
    └─── BM25 Sparse Search ───────────────────────┤
         (lexical: "$makelist", "kRelationalList")
                                                    │
                                              Fusion (RRF)
                                                    │
                                        Cross-Encoder Reranking
                                                    │
                                            Top-3 to Top-5 Chunks
                                                    │
                                           Injection into LLM Prompt
```

### Why BM25 is indispensable

| Query type | Dense only | BM25 only | Hybrid |
|---|---|---|---|
| "how to iterate over list" | ✅ good | ❌ no match | ✅ good |
| "`$sendall` syntax" | ⚠️ weak | ✅ good | ✅ good |
| "`binfrombase64` parameters" | ⚠️ weak | ✅ good | ✅ good |
| "SQL connection error handling" | ✅ good | ⚠️ partial | ✅ good |
| "`kFetchAll` constant" | ❌ unknown | ✅ exact | ✅ good |

For Omnis, BM25 is **not optional**. Notation lookups are common and lexically very specific.

---

## Embedding Model

### In use: `BAAI/bge-m3`

**Reasoning:**
- Strong multilingual support (German/English), relevant because queries may be in German while the content is in English
- Runs locally via `sentence-transformers`, no API key, no cost, no cloud dependency
- 1024 dimensions, which is sufficient for about `~2355` chunks of a proprietary niche corpus
- Same model for indexing (`embed_and_store.py`) and runtime (`ragserver.py`), so retrieval stays consistent

**Specifications:**
```text
Model:       BAAI/bge-m3
Dimensions:  1024
Deployment:  sentence-transformers (local, ~2 GB download)
Cost:        $0
```

### Why not `text-embedding-3-large` (OpenAI)?

It was originally planned because of top quality, `3072` dimensions, and only about `~$0.04` total cost.
It was later replaced in favor of a fully local pipeline with no API dependency.
The quality difference is small for this corpus because BM25 already finds the critical Omnis-specific tokens such as `$sendall` and `kRelationalList` lexically.

### Not recommended

- Code-specific models (`CodeBERT`, etc.): Omnis is not present in their training data
- `text-embedding-ada-002`: outdated and weaker than newer models

---

## Retrieval Configuration

### Top-K per collection

| Query type | omnis_commands | omnis_functions | omnis_programming |
|---|---|---|---|
| Simple syntax question | 2 | 2 | 1 |
| Standard coding task | 4 | 3 | 2 |
| Complex architecture question | 3 | 2 | 4 |

Default configuration: **Top-3 per collection** = 9 chunks total, about `~2,000-3,000` tokens of RAG context.

### Fusion: Reciprocal Rank Fusion (RRF)

RRF combines dense and sparse rankings without parameter tuning:
```python
def reciprocal_rank_fusion(dense_results, sparse_results, k=60):
    scores = {}
    for rank, doc_id in enumerate(dense_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, doc_id in enumerate(sparse_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
```

### Cross-encoder reranking (optional but recommended)

After fusion, rerank the top-10 candidates with a cross-encoder before selecting the final top-K.

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
# Local, free, ~100 ms latency for 10 candidates
# Gives significantly better relevance scores than cosine similarity alone
```

**When reranking is worth it:** when the query is very specific and several similar chunks exist, for example many related SQL commands. For clearly unique queries such as direct function lookup, it adds little.

---

## Vector Database

### Current implementation: PostgreSQL + pgvector

The project now uses PostgreSQL with `pgvector` across all supported runtime variants.

Schema overview:

```text
rag.corpus -> rag.document -> rag.chunk -> rag.embedding
```

Key properties:

- one database with three corpora: `omnis-commands`, `omnis-functions`, `omnis-programming`
- HNSW index for dense retrieval
- BM25/full-text via `tsvector`
- hybrid search via Reciprocal Rank Fusion in SQL functions

Deployment variants:

- local or external PostgreSQL populated via `scripts/import_to_postgres.py`
- Docker PostgreSQL 18 + `pgvector` in `docker_mcp-rag-pg/`, populated via `scripts/import_to_docker_postgres.py`

---

## Metadata Filters During Retrieval

Metadata allows targeted retrieval:

```python
# Only commands that can execute on the client
commands_col.query(
    query_embeddings=[query_embedding],
    where={"execute_on_client": True},
    n_results=5
)

# Exclude deprecated commands
commands_col.query(
    query_embeddings=[query_embedding],
    where={"deprecated": False},
    n_results=5
)

# Only functions that run on all platforms
functions_col.query(
    query_embeddings=[query_embedding],
    where={"platform": "All"},
    n_results=5
)
```

---

## Prompt Injection

### Format in the system prompt

```python
def build_rag_context(commands: list, functions: list, programming: list) -> str:
    context = "## Relevant Omnis Documentation\n\n"

    if commands:
        context += "### Commands\n"
        for chunk in commands:
            context += f"**{chunk['metadata']['command_name']}**\n"
            context += chunk['text'] + "\n\n---\n\n"

    if functions:
        context += "### Functions\n"
        for chunk in functions:
            context += f"**{chunk['metadata']['function_name']}**\n"
            context += chunk['text'] + "\n\n---\n\n"

    if programming:
        context += "### Concepts & Patterns\n"
        for chunk in programming:
            context += chunk['text'] + "\n\n---\n\n"

    return context
```

### Token cost per turn (summary)

```text
System prompt (instructions):      ~800 tokens   $0.0024
RAG context (9 chunks, avg):     ~2,500 tokens   $0.0075
Conversation history:            ~1,000 tokens   $0.0030
User question + code:              ~500 tokens   $0.0015
──────────────────────────────────────────────────────────
Total input:                     ~4,800 tokens   $0.0144
Output (code + explanation):     ~1,000 tokens   $0.0150
──────────────────────────────────────────────────────────
Per turn:                                        ~$0.030

Agentic task (5-8 turns):                       ~$0.15-0.24
```

---

## One-Time Corpus Embedding

The repository performs embeddings locally with `sentence-transformers`:

```bash
python scripts/embed_and_store.py
```

That script:

- reads all generated chunk JSON files
- computes `BAAI/bge-m3` embeddings locally
- writes `output/embeddings.jsonl`
- resumes by chunk ID if interrupted

The first run downloads the model once to the HuggingFace cache. There is no per-request or per-corpus API cost.

---

## Expected RAG Quality

| Area | Without RAG | With RAG | Limitation |
|---|---|---|---|
| Function calls | ~5% | ~90% | FunctionRef is complete |
| Command syntax | ~5% | ~90% | CommandRef is complete |
| Notation patterns | ~15% | ~70% | Programming guide is conceptual |
| Object properties | ~10% | ~35% | Missing from all three docs |
| Events/handlers | ~10% | ~50% | Partially documented |
| SQL patterns | ~10% | ~75% | Well covered |

**Overall improvement:** from about `~5%` to `~70-80%` syntactically correct code for standard tasks.

Biggest remaining gap: **object properties**, for example which properties a `Data Grid` has. These live in Omnis Help (`F1`) and not in the three source documents. Mid-term option: scrape the Omnis online help or add it as a fourth RAG collection.

---

## Dependencies

```bash
pip install pymupdf4llm           # PDF -> Markdown extraction
pip install sentence-transformers # Embeddings + optional reranking
pip install psycopg2-binary       # PostgreSQL import/runtime
pip install python-dotenv         # Env loading for import/runtime
pip install langchain-text-splitters  # MarkdownHeaderTextSplitter
```

---

## Next Steps (in order)

1. `pip install pymupdf4llm` and test extraction: `python -c "import pymupdf4llm; print(pymupdf4llm.to_markdown('CommandRef.pdf', pages=[11,12,13]))"`
2. Manually verify: are command names recognized as H2 headings? Are tables readable?
3. Run `extract.py` for all three documents
4. Run `chunk.py` and validate the JSON chunks (chunk sizes, metadata extraction)
5. Run `embed_and_store.py` for local embeddings
6. Import into PostgreSQL with `import_to_postgres.py` or `import_to_docker_postgres.py`
7. Execute test queries and assess quality
