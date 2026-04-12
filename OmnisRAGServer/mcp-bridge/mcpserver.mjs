import process from "node:process";

const RAG_SERVER_URL = process.env.OMNIS_RAG_SERVER_URL ?? "http://127.0.0.1:7071";

const TOOL_DOCS = "search_omnis_docs";
const TOOL_SYNTAX = "search_omnis_syntax";
const TOOL_CONCEPTS = "search_omnis_concepts";

const DEFAULTS = Object.freeze({
  corpus: "all",
  k_commands: 4,
  k_functions: 4,
  k_programming: 10,
});

const MODES = Object.freeze({
  syntax: Object.freeze({
    corpus: "all",
    k_commands: 8,
    k_functions: 8,
    k_programming: 4,
  }),
  concept: Object.freeze({
    corpus: "omnis-programming",
    k_commands: 2,
    k_functions: 4,
    k_programming: 12,
  }),
  deep: Object.freeze({
    corpus: "omnis-programming",
    k_commands: 2,
    k_functions: 2,
    k_programming: 20,
  }),
});

const ALLOWED_CORPORA = new Set(["all", "omnis-commands", "omnis-functions", "omnis-programming", "omnis-code"]);
const ALLOWED_MODES = new Set(Object.keys(MODES));
const ALLOWED_QUERY_LANGUAGES = new Set(["auto", "de", "en"]);
const MAX_K = 30;

const decoder = new TextDecoder("utf-8");
const encoder = new TextEncoder();
let inputBuffer = Buffer.alloc(0);
let inFlightRequests = 0;
let stdinEnded = false;

function writeMessage(message) {
  const json = JSON.stringify(message);
  const body = encoder.encode(json);
  const header = `Content-Length: ${body.length}\r\n\r\n`;
  process.stdout.write(header);
  process.stdout.write(body);
}

function sendResult(id, result) {
  writeMessage({ jsonrpc: "2.0", id, result });
}

function sendError(id, code, message, data = undefined) {
  const error = { code, message };
  if (data !== undefined) {
    error.data = data;
  }
  writeMessage({ jsonrpc: "2.0", id, error });
}

function parseHeaders(headerBlock) {
  const lines = headerBlock.split("\r\n").filter(Boolean);
  const headers = new Map();
  for (const line of lines) {
    const idx = line.indexOf(":");
    if (idx === -1) {
      continue;
    }
    const key = line.slice(0, idx).trim().toLowerCase();
    const value = line.slice(idx + 1).trim();
    headers.set(key, value);
  }
  return headers;
}

function normalizeK(value, fallback) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return fallback;
  }
  const rounded = Math.round(numeric);
  if (rounded < 1) {
    return 1;
  }
  if (rounded > MAX_K) {
    return MAX_K;
  }
  return rounded;
}

function normalizeCorpus(value) {
  const candidate = String(value ?? DEFAULTS.corpus).trim().toLowerCase();
  if (ALLOWED_CORPORA.has(candidate)) {
    return candidate;
  }
  return DEFAULTS.corpus;
}

function normalizeMode(value) {
  const candidate = String(value ?? "").trim().toLowerCase();
  if (ALLOWED_MODES.has(candidate)) {
    return candidate;
  }
  return "";
}

function normalizeQueryLanguage(value) {
  const candidate = String(value ?? "auto").trim().toLowerCase();
  if (ALLOWED_QUERY_LANGUAGES.has(candidate)) {
    return candidate;
  }
  return "auto";
}

function looksGerman(query) {
  const lower = query.toLowerCase();
  if (/[äöüß]/.test(lower)) {
    return true;
  }
  const germanHints = [
    "wie", "welche", "welcher", "wodurch", "warum", "und", "oder", "mit", "ohne",
    "liste", "listen", "fehler", "beispiel", "parameter", "unterschied", "syntax",
    "robust", "aufbau", "rekursion", "bedingungen", "fallstricke", "konzept",
  ];
  return germanHints.some((word) => lower.includes(` ${word} `) || lower.startsWith(`${word} `));
}

function rewriteGermanToEnglishQuery(query) {
  const replacements = [
    [/\bwie\b/gi, "how"],
    [/\bwelche\b/gi, "which"],
    [/\bwelcher\b/gi, "which"],
    [/\bwelches\b/gi, "which"],
    [/\bwas\b/gi, "what"],
    [/\bunterschied\b/gi, "difference"],
    [/\bzwischen\b/gi, "between"],
    [/\bund\b/gi, "and"],
    [/\boder\b/gi, "or"],
    [/\bmit\b/gi, "with"],
    [/\bohne\b/gi, "without"],
    [/\binklusive\b/gi, "including"],
    [/\bparametern\b/gi, "parameters"],
    [/\bparameter\b/gi, "parameters"],
    [/\bsyntax\b/gi, "syntax"],
    [/\bbefehle\b/gi, "commands"],
    [/\blisten\b/gi, "lists"],
    [/\bliste\b/gi, "list"],
    [/\biteration\b/gi, "iteration"],
    [/\bfehlerbehandlung\b/gi, "error handling"],
    [/\bfehler\b/gi, "error"],
    [/\bkonzept\b/gi, "concept"],
    [/\bkonzepte\b/gi, "concepts"],
    [/\brekursion\b/gi, "recursion"],
    [/\bbedingungen\b/gi, "conditions"],
    [/\bfallstricke\b/gi, "pitfalls"],
    [/\bbeispiele\b/gi, "examples"],
    [/\bbeispiel\b/gi, "example"],
  ];

  let out = query;
  for (const [pattern, replacement] of replacements) {
    out = out.replace(pattern, replacement);
  }

  out = out.replace(/\s+/g, " ").trim();
  return out;
}

function normalizeQueryForCorpus(argumentsObj, originalQuery) {
  const forcedEnglishQuery = String(argumentsObj?.query_en ?? "").trim();
  if (forcedEnglishQuery) {
    return {
      queryEffective: forcedEnglishQuery,
      queryOriginal: originalQuery,
      queryLanguage: "en",
      rewriteApplied: forcedEnglishQuery !== originalQuery,
      rewriteReason: "query_en override",
    };
  }

  const queryLanguage = normalizeQueryLanguage(argumentsObj?.query_language);
  const detectedGerman = queryLanguage === "auto" ? looksGerman(originalQuery) : queryLanguage === "de";

  if (!detectedGerman) {
    return {
      queryEffective: originalQuery,
      queryOriginal: originalQuery,
      queryLanguage: queryLanguage === "auto" ? "en" : queryLanguage,
      rewriteApplied: false,
      rewriteReason: null,
    };
  }

  const rewritten = rewriteGermanToEnglishQuery(originalQuery);
  const changed = rewritten !== originalQuery;
  return {
    queryEffective: changed ? rewritten : originalQuery,
    queryOriginal: originalQuery,
    queryLanguage: "de",
    rewriteApplied: changed,
    rewriteReason: changed ? "de-to-en normalization" : "de-detected-no-change",
  };
}

function buildDocsPayload(argumentsObj) {
  const queryOriginal = String(argumentsObj?.query ?? "").trim();
  if (!queryOriginal) {
    throw new Error("query must not be empty");
  }

  const queryNorm = normalizeQueryForCorpus(argumentsObj, queryOriginal);

  const mode = normalizeMode(argumentsObj?.mode);
  const preset = mode ? MODES[mode] : null;

  return {
    payload: {
      query: queryNorm.queryEffective,
      corpus: normalizeCorpus(argumentsObj?.corpus ?? preset?.corpus ?? DEFAULTS.corpus),
      k_commands: normalizeK(argumentsObj?.k_commands, preset?.k_commands ?? DEFAULTS.k_commands),
      k_functions: normalizeK(argumentsObj?.k_functions, preset?.k_functions ?? DEFAULTS.k_functions),
      k_programming: normalizeK(argumentsObj?.k_programming, preset?.k_programming ?? DEFAULTS.k_programming),
    },
    retrievalMode: mode || null,
    queryNorm,
  };
}

function buildSyntaxPayload(argumentsObj) {
  const queryOriginal = String(argumentsObj?.query ?? "").trim();
  if (!queryOriginal) {
    throw new Error("query must not be empty");
  }

  const queryNorm = normalizeQueryForCorpus(argumentsObj, queryOriginal);

  const preset = MODES.syntax;
  return {
    payload: {
      query: queryNorm.queryEffective,
      corpus: normalizeCorpus(argumentsObj?.corpus ?? preset.corpus),
      k_commands: normalizeK(argumentsObj?.k_commands, preset.k_commands),
      k_functions: normalizeK(argumentsObj?.k_functions, preset.k_functions),
      k_programming: normalizeK(argumentsObj?.k_programming, preset.k_programming),
    },
    retrievalMode: "syntax",
    queryNorm,
  };
}

function buildConceptPayload(argumentsObj) {
  const queryOriginal = String(argumentsObj?.query ?? "").trim();
  if (!queryOriginal) {
    throw new Error("query must not be empty");
  }

  const queryNorm = normalizeQueryForCorpus(argumentsObj, queryOriginal);

  const deep = Boolean(argumentsObj?.deep);
  const preset = deep ? MODES.deep : MODES.concept;

  return {
    payload: {
      query: queryNorm.queryEffective,
      corpus: normalizeCorpus(argumentsObj?.corpus ?? preset.corpus),
      k_commands: normalizeK(argumentsObj?.k_commands, preset.k_commands),
      k_functions: normalizeK(argumentsObj?.k_functions, preset.k_functions),
      k_programming: normalizeK(argumentsObj?.k_programming, preset.k_programming),
    },
    retrievalMode: deep ? "deep" : "concept",
    queryNorm,
  };
}

function buildPayload(toolName, args) {
  if (toolName === TOOL_SYNTAX) {
    return buildSyntaxPayload(args);
  }
  if (toolName === TOOL_CONCEPTS) {
    return buildConceptPayload(args);
  }
  return buildDocsPayload(args);
}

function buildGuidance(mode, effectiveRetrieval) {
  if (mode === "syntax") {
    return {
      next_query: "Falls konzeptionelle Einordnung fehlt, führe im Anschluss search_omnis_concepts mit gleicher Query aus.",
      hint: "Syntax-first retrieval active.",
      effective_retrieval: effectiveRetrieval,
    };
  }

  if (mode === "concept" || mode === "deep") {
    return {
      next_query: "Falls exakte Signatur fehlt, führe im Anschluss search_omnis_syntax mit Methoden-/Commandnamen aus.",
      hint: "Concept-first retrieval active.",
      effective_retrieval: effectiveRetrieval,
    };
  }

  return {
    next_query: "Optional: nutze search_omnis_syntax oder search_omnis_concepts für fokussierte Follow-ups.",
    hint: "General docs retrieval active.",
    effective_retrieval: effectiveRetrieval,
  };
}

async function callRagSearch(toolName, argumentsObj) {
  const { payload, retrievalMode, queryNorm } = buildPayload(toolName, argumentsObj);

  const response = await fetch(`${RAG_SERVER_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(15_000),
  });

  if (!response.ok) {
    throw new Error(`RAG server error ${response.status}`);
  }

  const rag = await response.json();
  const effectiveRetrieval = {
    corpus: payload.corpus,
    k_commands: payload.k_commands,
    k_functions: payload.k_functions,
    k_programming: payload.k_programming,
  };

  return {
    rag,
    retrievalMode,
    effectiveRetrieval,
    queryNorm,
    guidance: buildGuidance(retrievalMode, effectiveRetrieval),
  };
}

function buildToolsList() {
  return [
    {
      name: TOOL_SYNTAX,
      description: "Focused Omnis syntax/command/function retrieval with syntax-first defaults.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Question about exact Omnis syntax/signatures/parameters." },
          query_language: { type: "string", enum: ["auto", "de", "en"], description: "Optional query language hint. German queries can be normalized to English for retrieval." },
          query_en: { type: "string", description: "Optional explicit English retrieval query override." },
          corpus: { type: "string", description: "Optional corpus override: all | omnis-commands | omnis-functions | omnis-programming | omnis-code." },
          k_commands: { type: "number", description: "Optional override for command chunks." },
          k_functions: { type: "number", description: "Optional override for function chunks." },
          k_programming: { type: "number", description: "Optional override for programming chunks." },
        },
        required: ["query"],
      },
    },
    {
      name: TOOL_CONCEPTS,
      description: "Focused Omnis concept/pattern retrieval with concept-first defaults.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Question about Omnis patterns, architecture or best practices." },
          deep: { type: "boolean", description: "Set true to use deep retrieval preset." },
          query_language: { type: "string", enum: ["auto", "de", "en"], description: "Optional query language hint. German queries can be normalized to English for retrieval." },
          query_en: { type: "string", description: "Optional explicit English retrieval query override." },
          corpus: { type: "string", description: "Optional corpus override: all | omnis-commands | omnis-functions | omnis-programming | omnis-code." },
          k_commands: { type: "number", description: "Optional override for command chunks." },
          k_functions: { type: "number", description: "Optional override for function chunks." },
          k_programming: { type: "number", description: "Optional override for programming chunks." },
        },
        required: ["query"],
      },
    },
    {
      name: TOOL_DOCS,
      description: "General Omnis docs retrieval. Supports explicit mode/corpus/k tuning.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "General Omnis documentation question." },
          mode: { type: "string", enum: ["syntax", "concept", "deep"], description: "Optional retrieval preset." },
          query_language: { type: "string", enum: ["auto", "de", "en"], description: "Optional query language hint. German queries can be normalized to English for retrieval." },
          query_en: { type: "string", description: "Optional explicit English retrieval query override." },
          corpus: { type: "string", description: "Optional corpus selector: all | omnis-commands | omnis-functions | omnis-programming | omnis-code." },
          k_commands: { type: "number", description: "Max command chunks (default 4)." },
          k_functions: { type: "number", description: "Max function chunks (default 4)." },
          k_programming: { type: "number", description: "Max programming chunks (default 10)." },
        },
        required: ["query"],
      },
    },
  ];
}

async function handleRequest(request) {
  const { id, method, params } = request;

  if (method === "initialize") {
    return sendResult(id, {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: {
        name: "omnis-rag-bridge-v2",
        version: "0.3.0",
      },
    });
  }

  if (method === "notifications/initialized") {
    return;
  }

  if (method === "ping") {
    return sendResult(id, {});
  }

  if (method === "tools/list") {
    return sendResult(id, { tools: buildToolsList() });
  }

  if (method === "tools/call") {
    const toolName = params?.name;
    const allowed = new Set([TOOL_DOCS, TOOL_SYNTAX, TOOL_CONCEPTS]);
    if (!allowed.has(toolName)) {
      return sendError(id, -32602, `Unknown tool: ${String(toolName)}`);
    }

    try {
      const { rag, retrievalMode, effectiveRetrieval, guidance, queryNorm } = await callRagSearch(toolName, params?.arguments ?? {});
      const sources = Array.from(
        new Set(
          (rag.chunks ?? []).map((chunk) => {
            const meta = chunk.meta ?? {};
            return meta.command_name ?? meta.function_signature ?? meta.section ?? chunk.corpus_name;
          }),
        ),
      ).sort((a, b) => String(a).localeCompare(String(b)));

      const resultPayload = {
        server_url: RAG_SERVER_URL,
        tool: toolName,
        query: rag.query,
        query_original: queryNorm?.queryOriginal ?? rag.query,
        query_effective: queryNorm?.queryEffective ?? rag.query,
        query_language: queryNorm?.queryLanguage ?? "en",
        rewrite_applied: Boolean(queryNorm?.rewriteApplied),
        rewrite_reason: queryNorm?.rewriteReason ?? null,
        retrieval_mode: retrievalMode,
        effective_retrieval: effectiveRetrieval,
        guidance,
        sources,
        chunk_count: (rag.chunks ?? []).length,
        embed_ms: rag.embed_ms,
        search_ms: rag.search_ms,
        context_text: rag.context_text,
        chunks: rag.chunks ?? [],
      };

      return sendResult(id, {
        content: [
          {
            type: "text",
            text: JSON.stringify(resultPayload),
          },
        ],
        isError: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return sendResult(id, {
        content: [
          {
            type: "text",
            text: `RAG bridge V2 error: ${message}`,
          },
        ],
        isError: true,
      });
    }
  }

  return sendError(id, -32601, `Method not found: ${method}`);
}

function processBuffer() {
  while (true) {
    const separator = inputBuffer.indexOf("\r\n\r\n");
    if (separator === -1) {
      return;
    }

    const headerRaw = decoder.decode(inputBuffer.subarray(0, separator));
    const headers = parseHeaders(headerRaw);
    const contentLengthRaw = headers.get("content-length");
    if (!contentLengthRaw) {
      inputBuffer = inputBuffer.subarray(separator + 4);
      continue;
    }

    const contentLength = Number(contentLengthRaw);
    const totalLength = separator + 4 + contentLength;
    if (inputBuffer.length < totalLength) {
      return;
    }

    const bodyBuffer = inputBuffer.subarray(separator + 4, totalLength);
    inputBuffer = inputBuffer.subarray(totalLength);

    let request;
    try {
      request = JSON.parse(decoder.decode(bodyBuffer));
    } catch {
      continue;
    }

    if (!request || request.jsonrpc !== "2.0" || !request.method) {
      continue;
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
  }
}

process.stdin.on("data", (chunk) => {
  inputBuffer = Buffer.concat([inputBuffer, chunk]);
  processBuffer();
});

process.stdin.on("end", () => {
  stdinEnded = true;
  if (inFlightRequests === 0) {
    process.exit(0);
  }
});

process.stdin.resume();
