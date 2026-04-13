"""
MCP Bridge End-to-End Regression Test
=====================================

This script validates the local Omnis RAG MCP bridge against a running
rag-server instance.

What this test covers:
1. MCP handshake (`initialize` + `notifications/initialized`)
2. Tool discovery (`tools/list`)
3. Main retrieval flow (`search_omnis_docs`)
4. German query regression for concept mode (`search_omnis_concepts`, deep=false)
5. German query regression for deep mode (`search_omnis_concepts`, deep=true)

Expected prerequisites:
- rag-server reachable at OMNIS_RAG_SERVER_URL (default: http://127.0.0.1:7071)
- Node.js available in PATH
- Bridge file present at OmnisRAGServer/mcp-bridge/mcpserver.mjs

Exit codes:
- 0: all checks passed
- 1: one or more assertions failed
- 2: bridge executable not found
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def _write_framed(proc: subprocess.Popen, payload: dict) -> None:
    """Write one MCP JSON-RPC message using Content-Length framing."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    proc.stdin.write(header)
    proc.stdin.write(body)
    proc.stdin.flush()


def _read_exact(stream, n: int) -> bytes:
    """Read exactly n bytes from stream or fail on early EOF."""
    data = bytearray()
    while len(data) < n:
        chunk = stream.read(n - len(data))
        if not chunk:
            raise RuntimeError("EOF while reading MCP message")
        data.extend(chunk)
    return bytes(data)


def _read_framed(proc: subprocess.Popen, timeout_s: float = 20.0) -> dict:
    """Read one framed MCP JSON message from bridge stdout with timeout."""
    deadline = time.time() + timeout_s
    header = bytearray()
    while b"\r\n\r\n" not in header:
        if time.time() > deadline:
            raise TimeoutError("Timeout while reading MCP header")
        chunk = proc.stdout.read(1)
        if not chunk:
            raise RuntimeError("Bridge process closed stdout")
        header.extend(chunk)

    header_text = header.decode("ascii", errors="replace")
    content_length = None
    for line in header_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break
    if content_length is None:
        raise RuntimeError(f"Missing Content-Length header: {header_text!r}")

    body = _read_exact(proc.stdout, content_length)
    return json.loads(body.decode("utf-8"))


def _expect_response_by_id(proc: subprocess.Popen, request_id: int, timeout_s: float = 30.0) -> dict:
    """Read messages until the response with the matching JSON-RPC id arrives."""
    deadline = time.time() + timeout_s
    while True:
        if time.time() > deadline:
            raise TimeoutError(f"Timeout waiting for response id={request_id}")
        msg = _read_framed(proc, timeout_s=max(1.0, deadline - time.time()))
        if msg.get("id") == request_id:
            return msg


def _check(condition: bool, message: str, failures: list[str]) -> None:
    """Record and print assertion results in a test-friendly format."""
    if condition:
        print(f"[OK] {message}")
    else:
        print(f"[FAIL] {message}")
        failures.append(message)


def main() -> int:
    """Execute the full MCP bridge regression flow and return process exit code."""
    workspace_root = Path(__file__).resolve().parents[1]
    bridge_path = workspace_root / "OmnisRAGServer" / "mcp-bridge" / "mcpserver.mjs"

    if not bridge_path.exists():
        print(f"ERROR: Bridge not found: {bridge_path}")
        return 2

    env = os.environ.copy()
    env.setdefault("OMNIS_RAG_SERVER_URL", "http://127.0.0.1:7071")

    proc = subprocess.Popen(
        ["node", str(bridge_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    failures: list[str] = []

    try:
        # 1) MCP initialize handshake
        _write_framed(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "bridge-smoke", "version": "1.0"},
                },
            },
        )
        initialize_resp = _expect_response_by_id(proc, 1)
        _check("result" in initialize_resp, "initialize returned result", failures)

        # Signal that client initialization is complete.
        _write_framed(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        # 2) Tool discovery
        _write_framed(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools_resp = _expect_response_by_id(proc, 2)

        tools = tools_resp.get("result", {}).get("tools", [])
        tool_names = [t.get("name") for t in tools]
        required_tools = {"search_omnis_docs", "search_omnis_syntax", "search_omnis_concepts"}
        _check(required_tools.issubset(set(tool_names)), "tools/list includes required tools", failures)

        # 3) Primary docs retrieval sanity test
        _write_framed(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_omnis_docs",
                    "arguments": {
                        "query": "Omnis syntax for $sendall parameters and condition usage",
                        "mode": "syntax",
                    },
                },
            },
        )
        call_resp = _expect_response_by_id(proc, 3, timeout_s=60.0)

        _check("error" not in call_resp, "search_omnis_docs call has no RPC error", failures)
        _check(call_resp.get("result", {}).get("isError") is False, "search_omnis_docs isError is false", failures)

        content = call_resp.get("result", {}).get("content", [])
        _check(bool(content), "search_omnis_docs returns content", failures)
        if not content:
            return 1

        # Bridge returns JSON text payload inside MCP content[0].text.
        text_payload = content[0].get("text", "")
        parsed = json.loads(text_payload)
        chunks = parsed.get("chunks", [])
        context_text = parsed.get("context_text", "")
        _check(len(chunks) > 0, "search_omnis_docs returns chunks > 0", failures)
        _check(len(context_text) > 0, "search_omnis_docs returns non-empty context_text", failures)

        print(f"tools/call: OK (chunks={len(chunks)}, context_len={len(context_text)})")
        if chunks:
            first = chunks[0]
            print(
                "top_chunk="
                + json.dumps(
                    {
                        "corpus": first.get("corpus_name"),
                        "rrf": first.get("rrf_score"),
                        "preview": (first.get("content", "")[:160]).replace("\n", " "),
                    },
                    ensure_ascii=False,
                )
            )

        # 4) DE regression: concept mode
        _write_framed(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "search_omnis_concepts",
                    "arguments": {
                        "query": "Wie implementiere ich robustes Error Handling bei Omnis API-Aufrufen?",
                        "query_language": "de",
                        "deep": False,
                    },
                },
            },
        )
        concept_resp = _expect_response_by_id(proc, 4, timeout_s=60.0)
        _check("error" not in concept_resp, "concept(DE) has no RPC error", failures)
        _check(concept_resp.get("result", {}).get("isError") is False, "concept(DE) isError is false", failures)
        concept_payload = json.loads(concept_resp["result"]["content"][0]["text"])
        _check(concept_payload.get("retrieval_mode") == "concept", "concept(DE) retrieval_mode is concept", failures)
        _check(bool(concept_payload.get("rewrite_applied")), "concept(DE) rewrite_applied is true", failures)
        _check((concept_payload.get("chunk_count") or 0) > 0, "concept(DE) chunk_count > 0", failures)

        # 5) DE regression: deep mode
        _write_framed(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "search_omnis_concepts",
                    "arguments": {
                        "query": "Welche Fallstricke gibt es bei Rekursion und Bedingungen in Omnis?",
                        "query_language": "de",
                        "deep": True,
                    },
                },
            },
        )
        deep_resp = _expect_response_by_id(proc, 5, timeout_s=60.0)
        _check("error" not in deep_resp, "deep(DE) has no RPC error", failures)
        _check(deep_resp.get("result", {}).get("isError") is False, "deep(DE) isError is false", failures)
        deep_payload = json.loads(deep_resp["result"]["content"][0]["text"])
        _check(deep_payload.get("retrieval_mode") == "deep", "deep(DE) retrieval_mode is deep", failures)
        _check(bool(deep_payload.get("rewrite_applied")), "deep(DE) rewrite_applied is true", failures)
        _check((deep_payload.get("chunk_count") or 0) > 0, "deep(DE) chunk_count > 0", failures)

        if failures:
            print("\nTest result: FAIL")
            for item in failures:
                print(f" - {item}")
            return 1

        print("\nTest result: PASS")

        return 0
    finally:
        # Always clean up child process to avoid orphaned bridge instances.
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        if proc.stderr:
            err = proc.stderr.read().decode("utf-8", errors="replace").strip()
            if err:
                print("bridge_stderr:")
                print(err)


if __name__ == "__main__":
    sys.exit(main())
