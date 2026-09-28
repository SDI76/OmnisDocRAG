"""
Omnis RAG MCP Server — Streamable HTTP
======================================

Thin MCP front-end for the Omnis RAG HTTP server (rag-server). The rag-server
does all ranking and renders the compact text answers; this server only maps
tools to endpoints.

Tools
-----
search_omnis_docs      ranked search over all Omnis documentation (default tool)
get_omnis_doc          full text of results, by id (second step)
search_omnis_syntax    same search, restricted to commands, functions and notation
search_omnis_concepts  same search, restricted to the Programming manual

Answers are plain text without structured output, so every result is sent once.
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

RAG_URL = os.getenv("RAG_SERVER_URL", "http://rag-server:7071")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))

mcp = FastMCP(
    "omnis-rag",
    host=MCP_HOST,
    port=MCP_PORT,
    instructions=(
        "Omnis Studio documentation (Command Reference, Function Reference, Programming manual, "
        "notation reference). Search first with search_omnis_docs; results are short snippets with ids. "
        "Fetch the full text of the relevant ids with get_omnis_doc. mode=fulltext supports "
        '"exact phrases", OR and -exclusion.'
    ),
)


async def _post(path: str, payload: dict) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{RAG_URL}{path}", json=payload)
        if resp.status_code >= 400:
            return f"Omnis RAG error {resp.status_code}: {resp.text[:500]}"
        return resp.json().get("text", "")


async def _search(query: str, mode: str, top_k: int, corpora) -> str:
    return await _post("/search", {"query": query, "mode": mode, "top_k": top_k,
                                   "corpora": corpora, "format": "text"})


@mcp.tool(structured_output=False)
async def search_omnis_docs(query: str, mode: str = "hybrid", top_k: int = 8, corpus: str = "all") -> str:
    """
    Search the Omnis Studio documentation. Returns ranked hits (title, source, id, snippet).

    query:  question, concept or exact name ("mid()", "$search", "Begin reversible block"); English or German
    mode:   hybrid (default) | semantic (meaning only) | fulltext (words; supports "phrase", OR, -word)
    top_k:  number of hits, 1-30 (default 8)
    corpus: all | commands | functions | programming | notation (comma-separated for several)

    Then call get_omnis_doc with the ids you need.
    """
    return await _search(query, mode, top_k, corpus)


@mcp.tool(structured_output=False)
async def get_omnis_doc(ids: list[str]) -> str:
    """
    Full text of documentation chunks by id (from search results), up to 20 ids per call.
    Multi-part entries list the ids of their other parts.
    """
    return await _post("/chunks", {"ids": ids, "format": "text"})


@mcp.tool(structured_output=False)
async def search_omnis_syntax(query: str, top_k: int = 8, mode: str = "hybrid") -> str:
    """
    Search only commands, functions and notation (syntax, parameters, properties, methods).
    Same output as search_omnis_docs; fetch full text with get_omnis_doc.
    """
    return await _search(query, mode, top_k, ["omnis-commands", "omnis-functions", "omnis-notation"])


@mcp.tool(structured_output=False)
async def search_omnis_concepts(query: str, top_k: int = 8, deep: bool = False, mode: str = "hybrid") -> str:
    """
    Search only the Omnis Programming manual (concepts, patterns, SQL, lists, OOP, windows, reports).
    deep=True returns 15 hits instead of top_k. Fetch full text with get_omnis_doc.
    """
    return await _search(query, mode, 15 if deep else top_k, ["omnis-programming"])


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
