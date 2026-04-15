# 1. Expected Improvement

The expected retrieval quality is the same across the supported runtime variants:

- local PostgreSQL + local `rag-server` + stdio MCP bridge
- `docker_mcp-rag/` with PostgreSQL on the host
- `docker_mcp-rag-pg/` with PostgreSQL 18 inside Docker

All three use the same corpora, the same `BAAI/bge-m3` embedding model, and the same PostgreSQL hybrid search functions.

## Baseline without RAG

AI has only baseline Omnis knowledge. Omnis is a proprietary niche language with hardly any presence on the internet. Generated code would look syntactically plausible, but be wrong in substance. Estimate: about `~5%` correct syntax for specific questions.

## With these three RAGs

| Area | Without RAG | With RAG | Limitation |
| --- | --- | --- | --- |
| Function calls (`abs()`, `replace()`, `OJSON.*`) | ~5% | ~90% | `FunctionRef` is complete |
| Command syntax (`Calculate`, `Do`, `If`, options) | ~5% | ~90% | `CommandRef` is complete |
| Notation patterns (`$assign`, `$sendall`, `$open`) | ~15% | ~70% | Programming Guide is conceptually strong |
| Properties per object (`$visible`, `$textcolor`, ...) | ~10% | ~35% | Missing from all three docs |
| Event-handler code | ~10% | ~50% | Only partially documented |
| SQL patterns | ~10% | ~75% | Well covered in the Programming Guide |

## Realistic overall picture

For standard tasks ("write me a method that builds a list and iterates over it"), the generated code should improve from about `~5%` to `~70-80%` directly executable.

The biggest remaining gap is object properties: Which properties does a Data Grid have? A Single Line Entry Field? That is documented in Omnis Help (`F1`), not in these PDFs. The AI will still have to guess there.

Comparison with GitHub Copilot for well-known languages: Copilot reaches about `~85-90%` correct syntax because it has seen millions of examples. With RAG, Omnis can reach about `~70-80%`, which is very strong for a language no LLM has ever really seen.

---

# 2. Token Cost of the Architecture

## Chunk sizes (realistic after extraction)

| Collection | Avg. Tokens/Chunk | Top-K Retrieval |
| --- | --- | --- |
| `omnis_commands` | ~250 Tokens | Top 3-5 |
| `omnis_functions` | ~180 Tokens | Top 3-5 |
| `omnis_programming` | ~450 Tokens | Top 2-3 |

## RAG context injected per request

### Simple question ("how does `replace()` work?")

- Functions: `1 chunk × 180 = 180 tokens`
- Commands: `0`
- Programming: `1 chunk × 450 = 450 tokens`
- RAG overhead: `~630 tokens`

### Standard coding request ("write an SQL method with error handling")

- Commands: `5 chunks × 250 = 1,250 tokens`
- Functions: `3 chunks × 180 = 540 tokens`
- Programming: `3 chunks × 450 = 1,350 tokens`
- RAG overhead: `~3,100 tokens`

### Complex request (agentic, multiple steps)

- RAG overhead: `~4,000-6,000 tokens`

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

- `CommandRef`: `~400 commands × 250 tokens = 100,000 tokens`
- `FunctionRef`: `~350 functions × 180 tokens = 63,000 tokens`
- `Programming`: `~300 sections × 450 tokens = 135,000 tokens`
- Total corpus: `~298,000 tokens`

In the current repository this cost is effectively `$0`, because embeddings are generated locally with `BAAI/bge-m3` via `sentence-transformers`.

Historically, even an OpenAI-based embedding path would have been negligible at this corpus size.

---

# Overall Picture

The RAG architecture costs about `~$0.015` more per turn than running without RAG because of the injected context. That is the trade-off:

- Without RAG: cheap (`~$0.010/turn`), but only `~5%` correct code
- With RAG: `~$0.030/turn`, but about `~75%` correct code

For an agentic IDE, this is a very strong cost/benefit ratio. The biggest lever for further improvement would be getting access to object properties somehow, either by scraping the Omnis online help or by capturing real Omnis developers while they work and using that as few-shot examples.
