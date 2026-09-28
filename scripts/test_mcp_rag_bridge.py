"""
MCP Bridge End-to-End Regression Test
=====================================

Validates the local stdio MCP bridge (OmnisRAGServer/mcp-bridge/mcpserver.mjs)
against a running rag-server.

Checks
------
1. initialize + notifications/initialized
2. tools/list contains the four tools
3. search_omnis_docs returns ranked hits with ids and stays compact (< 8 KB)
4. get_omnis_doc returns the full text of the first hit
5. German query through search_omnis_concepts returns hits
6. fulltext mode with a quoted phrase returns hits

Prerequisites: rag-server reachable at OMNIS_RAG_SERVER_URL (default
http://127.0.0.1:7071), Node.js in PATH.

Exit codes: 0 pass, 1 failure, 2 bridge not found.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

MAX_SEARCH_BYTES = 8 * 1024


def send(proc: subprocess.Popen, payload: dict) -> None:
    proc.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    proc.stdin.flush()


def receive(proc: subprocess.Popen, request_id: int, timeout_s: float = 60.0) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("bridge closed stdout")
        msg = json.loads(line.decode("utf-8"))
        if msg.get("id") == request_id:
            return msg
    raise TimeoutError(f"no response for id={request_id}")


def call(proc: subprocess.Popen, request_id: int, name: str, arguments: dict) -> str:
    send(proc, {"jsonrpc": "2.0", "id": request_id, "method": "tools/call",
                "params": {"name": name, "arguments": arguments}})
    resp = receive(proc, request_id)
    if "error" in resp or resp["result"].get("isError"):
        raise RuntimeError(json.dumps(resp)[:500])
    return resp["result"]["content"][0]["text"]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    bridge = root / "OmnisRAGServer" / "mcp-bridge" / "mcpserver.mjs"
    if not bridge.exists():
        print(f"ERROR: bridge not found: {bridge}")
        return 2

    env = os.environ.copy()
    env.setdefault("OMNIS_RAG_SERVER_URL", "http://127.0.0.1:7071")
    proc = subprocess.Popen(["node", str(bridge)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    failures: list[str] = []

    def check(ok: bool, message: str) -> None:
        print(("[OK]   " if ok else "[FAIL] ") + message)
        if not ok:
            failures.append(message)

    try:
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "bridge-test", "version": "1"}}})
        check("result" in receive(proc, 1), "initialize")
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {t["name"] for t in receive(proc, 2)["result"]["tools"]}
        check({"search_omnis_docs", "get_omnis_doc", "search_omnis_syntax", "search_omnis_concepts"} <= names,
              f"tools/list: {sorted(names)}")

        text = call(proc, 3, "search_omnis_docs", {"query": "$sendall send a message to all lines of a list"})
        ids = re.findall(r"id: (\S+)", text)
        check(len(ids) > 0, f"search_omnis_docs returns hits ({len(ids)})")
        check(len(text.encode("utf-8")) < MAX_SEARCH_BYTES, f"search response is compact ({len(text.encode())} bytes)")
        print("       " + text.split("\n")[1] if "\n" in text else text)

        if ids:
            full = call(proc, 4, "get_omnis_doc", {"ids": [ids[0]]})
            check(ids[0] in full and len(full) > 100, f"get_omnis_doc returns full text ({len(full)} chars)")

        de = call(proc, 5, "search_omnis_concepts", {"query": "Wie lösche ich Zeilen aus einer Liste?"})
        check("id: " in de, "German concept query returns hits")

        ft = call(proc, 6, "search_omnis_docs", {"query": '"reversible block"', "mode": "fulltext"})
        check("id: " in ft, "fulltext phrase query returns hits")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

    print("\nTest result:", "FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
