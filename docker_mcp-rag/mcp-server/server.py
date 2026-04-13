"""
Omnis RAG MCP Server — Streamable HTTP
=======================================
MCP protocol 2025-03-26, Streamable HTTP transport.

Proxies three search tools to the Omnis RAG HTTP server.
Designed to run inside Docker alongside the rag-server container.
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

RAG_URL = os.getenv("RAG_SERVER_URL", "http://rag-server:7071")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "3000"))

mcp = FastMCP("omnis-rag", host=MCP_HOST, port=MCP_PORT)


async def _call_rag(
    query: str,
    corpus: str,
    k_commands: int,
    k_functions: int,
    k_programming: int,
) -> str:
    payload = {
        "query": query,
        "corpus": corpus,
        "k_commands": k_commands,
        "k_functions": k_functions,
        "k_programming": k_programming,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(f"{RAG_URL}/search", json=payload)
        resp.raise_for_status()
        return resp.text


@mcp.tool()
async def search_omnis_syntax(
    query: str,
    corpus: str = "all",
    k_commands: int = 8,
    k_functions: int = 8,
    k_programming: int = 4,
) -> str:
    """
    Focused Omnis syntax/command/function retrieval with syntax-first defaults.
    Use for exact command signatures, function parameters, and syntax questions.
    corpus: all | omnis-commands | omnis-functions | omnis-programming | omnis-code
    """
    return await _call_rag(query, corpus, k_commands, k_functions, k_programming)


@mcp.tool()
async def search_omnis_concepts(
    query: str,
    deep: bool = False,
    corpus: str = "omnis-programming",
    k_commands: int = 2,
    k_functions: int = 4,
    k_programming: int = 12,
) -> str:
    """
    Focused Omnis concept/pattern retrieval with concept-first defaults.
    Use for architecture, patterns, best practices, and conceptual questions.
    Set deep=True for more thorough programming guide retrieval (k_programming=20).
    corpus: all | omnis-commands | omnis-functions | omnis-programming | omnis-code
    """
    if deep:
        k_commands, k_functions, k_programming = 2, 2, 20
    return await _call_rag(query, corpus, k_commands, k_functions, k_programming)


@mcp.tool()
async def search_omnis_docs(
    query: str,
    corpus: str = "all",
    k_commands: int = 4,
    k_functions: int = 4,
    k_programming: int = 10,
) -> str:
    """
    General Omnis documentation retrieval across all corpora.
    corpus: all | omnis-commands | omnis-functions | omnis-programming | omnis-code
    """
    return await _call_rag(query, corpus, k_commands, k_functions, k_programming)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
