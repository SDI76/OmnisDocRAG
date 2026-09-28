# 1. Expected Improvement

The expected retrieval quality is the same across the supported runtime variants:

- local PostgreSQL + local `rag-server` + stdio MCP bridge
- `docker_mcp-rag/` with PostgreSQL on the host
- `docker_mcp-rag-pg/` with PostgreSQL 18 inside Docker

All three use the same corpora, the same `BAAI/bge-m3` embedding model, and the same PostgreSQL search function (`rag.search_ranked`).

## Baseline without RAG

AI has only baseline Omnis knowledge. Omnis is a proprietary niche language with hardly any presence on the internet. Generated code would look syntactically plausible, but be wrong in substance. Estimate: about `~5%` correct syntax for specific questions.

## With the indexed documentation

| Area | Without RAG | With RAG | Limitation |
| --- | --- | --- | --- |
| Function calls (`abs()`, `replace()`, `OJSON.*`) | ~5% | ~90% | `FunctionRef` is complete |
| Command syntax (`Calculate`, `Do`, `If`, options) | ~5% | ~90% | `CommandRef` is complete |
| Notation patterns (`$assign`, `$sendall`, `$open`) | ~15% | ~70% | Programming Guide is conceptually strong |
| Properties per object (`$visible`, `$textcolor`, ...) | ~10% | ~80% | Notation corpus from the Omnis 11.1 help (doc pack) |
| Event-handler code | ~10% | ~50% | Only partially documented |
| SQL patterns | ~10% | ~75% | Well covered in the Programming Guide |

## Realistic overall picture

For standard tasks ("write me a method that builds a list and iterates over it"), the generated code should improve from about `~5%` to `~70-80%` directly executable.

Object properties (which properties does a Data Grid have?) are not in the PDFs; they come from the notation corpus, which is built from the Omnis 11.1 help when the doc pack is available. Without the doc pack this gap remains.

Comparison with GitHub Copilot for well-known languages: Copilot reaches about `~85-90%` correct syntax because it has seen millions of examples. With RAG, Omnis can reach about `~70-80%`, which is very strong for a language no LLM has ever really seen.

---

# 2. Token Cost of the Architecture

## Two-step retrieval

A search returns a compact list — per hit one line (corpus, title, source, id) and a snippet of
~240 characters. Typical size: 8 hits ≈ 2–4 KB ≈ 600–1,000 tokens. The agent then fetches the full
text of the 1–3 relevant ids with `get_omnis_doc` (chunks are ≤ 450 words, ~300–600 tokens each).

| Step | Tokens |
| --- | --- |
| Search (8 hits, snippets) | ~600–1,000 |
| Full text of 2 chunks | ~600–1,200 |
| Typical total per question | ~1,500–2,000 |

Before the rework a single search returned 50–105 KB (the text was included up to four times),
i.e. ~15,000–25,000 tokens per call.

## Full prompt per turn

- System prompt (Omnis context, instructions): `~800 tokens`
- RAG context (injected): `~2,500 tokens`
- Conversation history (grows over time): `~1,000 tokens`
- User question + code: `~500 tokens`
- Total input per turn: `~5,000 tokens`
- Output (generated code + explanation): `~1,000 tokens`

## Cost with `claude-sonnet-4-6`

- Input: `$3.00 / 1M tokens -> 5,000 tokens = $0.015`
- Output: `$15.00 / 1M tokens -> 1,000 tokens = $0.015`
- Per turn: `~$0.030`
- Agentic task (5-8 turns): `~$0.15-0.24`

## One-time embedding cost (entire corpus)

- 6,009 chunks, ~1.7 M tokens in total (commands, functions, programming, notation)
- Local embedding: minutes on a GPU / Apple Silicon, a few hours on a plain CPU; afterwards only
  changed chunks are embedded again

In the current repository this cost is effectively `$0`, because embeddings are generated locally with `BAAI/bge-m3` via `sentence-transformers`.

Historically, even an OpenAI-based embedding path would have been negligible at this corpus size.

---

# Overall Picture

The RAG architecture costs about `~$0.015` more per turn than running without RAG because of the injected context. That is the trade-off:

- Without RAG: cheap (`~$0.010/turn`), but only `~5%` correct code
- With RAG: `~$0.030/turn`, but about `~75%` correct code

For an agentic IDE, this is a very strong cost/benefit ratio. The biggest lever for further improvement would be getting access to object properties somehow, either by scraping the Omnis online help or by capturing real Omnis developers while they work and using that as few-shot examples.
