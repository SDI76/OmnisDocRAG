// Omnis RAG — local stdio MCP bridge
// ===================================
// Thin MCP front-end for the Omnis RAG HTTP server (rag-server). The rag-server
// ranks and renders the compact text answers; this bridge only maps tools to
// endpoints. The Docker MCP server (docker_mcp-rag/mcp-server/server.py) offers
// the same tools.
//
// Transport: newline-delimited JSON-RPC on stdin/stdout (MCP stdio).

import process from "node:process";
import readline from "node:readline";

const RAG_SERVER_URL = process.env.OMNIS_RAG_SERVER_URL ?? "http://127.0.0.1:7071";

const CORPORA_SYNTAX = ["omnis-commands", "omnis-functions", "omnis-notation"];
const CORPORA_CONCEPTS = ["omnis-programming"];

const INSTRUCTIONS =
  "Omnis Studio documentation (Command Reference, Function Reference, Programming manual, notation reference). " +
  "Search first with search_omnis_docs; results are short snippets with ids. Fetch the full text of the relevant " +
  'ids with get_omnis_doc. mode=fulltext supports "exact phrases", OR and -exclusion.';

const MODE_PROPERTY = {
  type: "string",
  enum: ["hybrid", "semantic", "fulltext"],
  description: 'hybrid (default) | semantic (meaning only) | fulltext (words; supports "phrase", OR, -word)',
};

const TOOLS = [
  {
    name: "search_omnis_docs",
    description:
      "Search the Omnis Studio documentation. Returns ranked hits (title, source, id, snippet). " +
      "Query may be a question, a concept or an exact name (mid(), $search, Begin reversible block), " +
      "English or German. Then call get_omnis_doc with the ids you need.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string" },
        mode: MODE_PROPERTY,
        top_k: { type: "number", description: "Number of hits, 1-30 (default 8)." },
        corpus: {
          type: "string",
          description: "all | commands | functions | programming | notation (comma-separated for several)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "get_omnis_doc",
    description:
      "Full text of documentation chunks by id (from search results), up to 20 ids per call. " +
      "Multi-part entries list the ids of their other parts.",
    inputSchema: {
      type: "object",
      properties: { ids: { type: "array", items: { type: "string" } } },
      required: ["ids"],
    },
  },
  {
    name: "search_omnis_syntax",
    description:
      "Search only commands, functions and notation (syntax, parameters, properties, methods). " +
      "Same output as search_omnis_docs; fetch full text with get_omnis_doc.",
    inputSchema: {
      type: "object",
      properties: { query: { type: "string" }, top_k: { type: "number" }, mode: MODE_PROPERTY },
      required: ["query"],
    },
  },
  {
    name: "search_omnis_concepts",
    description:
      "Search only the Omnis Programming manual (concepts, patterns, SQL, lists, OOP, windows, reports). " +
      "deep=true returns 15 hits instead of top_k. Fetch full text with get_omnis_doc.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string" },
        top_k: { type: "number" },
        deep: { type: "boolean" },
        mode: MODE_PROPERTY,
      },
      required: ["query"],
    },
  },
];

function clampTopK(value, fallback = 8) {
  const n = Number.parseInt(String(value ?? fallback), 10);
  return Number.isFinite(n) ? Math.min(Math.max(n, 1), 30) : fallback;
}

async function post(path, payload) {
  const response = await fetch(`${RAG_SERVER_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.text();
  if (!response.ok) {
    throw new Error(`rag-server ${response.status}: ${body.slice(0, 500)}`);
  }
  return JSON.parse(body).text ?? "";
}

async function callTool(name, args) {
  const query = String(args?.query ?? "").trim();
  const mode = String(args?.mode ?? "hybrid");
  switch (name) {
    case "search_omnis_docs":
      return post("/search", { query, mode, top_k: clampTopK(args?.top_k), corpora: args?.corpus ?? "all" });
    case "get_omnis_doc": {
      const ids = Array.isArray(args?.ids) ? args.ids.map(String) : [String(args?.ids ?? "")];
      return post("/chunks", { ids });
    }
    case "search_omnis_syntax":
      return post("/search", { query, mode, top_k: clampTopK(args?.top_k), corpora: CORPORA_SYNTAX });
    case "search_omnis_concepts":
      return post("/search", {
        query,
        mode,
        top_k: args?.deep ? 15 : clampTopK(args?.top_k),
        corpora: CORPORA_CONCEPTS,
      });
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// ── JSON-RPC over stdio ─────────────────────────────────────

let inFlightRequests = 0;
let stdinEnded = false;

function writeMessage(message) {
  process.stdout.write(JSON.stringify(message) + "\n");
}

function sendResult(id, result) {
  writeMessage({ jsonrpc: "2.0", id, result });
}

function sendError(id, code, message) {
  writeMessage({ jsonrpc: "2.0", id, error: { code, message } });
}

async function handleRequest(request) {
  const { id, method, params } = request;

  if (method === "initialize") {
    return sendResult(id, {
      protocolVersion: params?.protocolVersion ?? "2025-03-26",
      capabilities: { tools: {} },
      serverInfo: { name: "omnis-rag-bridge", version: "2.0.0" },
      instructions: INSTRUCTIONS,
    });
  }
  if (method === "notifications/initialized") {
    return;
  }
  if (method === "ping") {
    return sendResult(id, {});
  }
  if (method === "tools/list") {
    return sendResult(id, { tools: TOOLS });
  }
  if (method === "tools/call") {
    const toolName = params?.name;
    if (!TOOLS.some((t) => t.name === toolName)) {
      return sendError(id, -32602, `Unknown tool: ${String(toolName)}`);
    }
    try {
      const text = await callTool(toolName, params?.arguments ?? {});
      return sendResult(id, { content: [{ type: "text", text }], isError: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return sendResult(id, { content: [{ type: "text", text: `Omnis RAG error: ${message}` }], isError: true });
    }
  }
  if (id !== undefined) {
    return sendError(id, -32601, `Method not found: ${method}`);
  }
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

rl.on("line", (line) => {
  const trimmed = line.trim();
  if (!trimmed) {
    return;
  }
  let request;
  try {
    request = JSON.parse(trimmed);
  } catch {
    return;
  }
  if (!request || request.jsonrpc !== "2.0" || !request.method) {
    return;
  }
  inFlightRequests += 1;
  Promise.resolve(handleRequest(request))
    .catch((error) => {
      const message = error instanceof Error ? error.message : String(error);
      if (request.id !== undefined) {
        sendError(request.id, -32603, message);
      }
    })
    .finally(() => {
      inFlightRequests -= 1;
      if (stdinEnded && inFlightRequests === 0) {
        process.exit(0);
      }
    });
});

rl.on("close", () => {
  stdinEnded = true;
  if (inFlightRequests === 0) {
    process.exit(0);
  }
});
