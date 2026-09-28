"""
pipeline.py — cross-platform entry point (macOS, Windows, Linux)
================================================================

Uses only the Python standard library, so it runs before anything is installed.
It picks the right virtual-environment paths and Python executable for the
operating system and runs every step with the project's `.venv`.

    python scripts/pipeline.py doctor                 # what this machine can do, state of the data
    python scripts/pipeline.py setup [--rag-server]   # create .venv (+ rag-server venv) and install
    python scripts/pipeline.py build                  # extract → chunk → validate → embed → import → eval
    python scripts/pipeline.py build --from embed     # e.g. only embed + import + eval
    python scripts/pipeline.py build --to validate    # e.g. only rebuild chunks
    python scripts/pipeline.py build --target local   # import into scripts/.env database instead of Docker

On macOS/Linux use `python3` if `python` is not available; on Windows `py` works too.

Typical split across machines: build the chunks anywhere (they are in git), run
`build --from embed --to embed` on a machine with a GPU or Apple Silicon, copy
output/embeddings.jsonl to the machine with the database and run
`build --from import`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):   # Windows pipes default to a legacy code page
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
SCRIPTS = BASE / "scripts"
IS_WINDOWS = os.name == "nt"
STEPS = ["extract", "chunk", "validate", "embed", "import", "eval"]
RAG_URL = os.environ.get("OMNIS_RAG_SERVER_URL", "http://localhost:7071")


# ── Environment helpers ───────────────────────────────────────

def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def project_python() -> str:
    py = venv_python(BASE / ".venv")
    if py.exists():
        return str(py)
    print(f"  (no .venv found — using {sys.executable}; run `pipeline.py setup` to create it)")
    return sys.executable


def run(cmd: list[str], cwd: Path = BASE, check: bool = True) -> int:
    print(f"\n$ {' '.join(cmd)}", flush=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(cmd, cwd=cwd, env=env, check=check).returncode


def probe(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (out.stdout or out.stderr).strip() if out.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def http_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def read_env(path: Path) -> dict[str, str]:
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def doc_pack_path() -> str | None:
    return (os.environ.get("OMNISDOC_PACK")
            or read_env(SCRIPTS / ".env.local").get("OMNISDOC_PACK")
            or read_env(SCRIPTS / ".env").get("OMNISDOC_PACK"))


# ── doctor ────────────────────────────────────────────────────

TORCH_PROBE = r"""
import json, torch
mps = getattr(torch.backends, "mps", None)
print(json.dumps({"torch": torch.__version__, "cuda": torch.cuda.is_available(),
                  "mps": bool(mps and mps.is_available()), "threads": torch.get_num_threads()}))
"""


def embedding_state() -> tuple[int, int, int]:
    """(chunks, current embeddings, missing or stale)."""
    chunks = []
    for path in sorted((BASE / "output" / "chunks").glob("*_chunks.json")):
        chunks.extend(json.loads(path.read_text(encoding="utf-8")))
    current = {}
    emb = BASE / "output" / "embeddings.jsonl"
    if emb.exists():
        with emb.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    current[rec["id"]] = rec.get("hash")
    ok = sum(1 for c in chunks
             if current.get(c["id"]) == hashlib.sha256(c["embed_text"].encode("utf-8")).hexdigest()[:16])
    return len(chunks), ok, len(chunks) - ok


def cmd_doctor(_: argparse.Namespace) -> None:
    print("=== System ===")
    print(f"OS:        {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python:    {platform.python_version()} ({sys.executable})")
    venv = BASE / ".venv"
    print(f"Project venv: {'present' if venv_python(venv).exists() else 'missing — run: pipeline.py setup'}")

    device = "unknown"
    if venv_python(venv).exists():
        info = probe([str(venv_python(venv)), "-c", TORCH_PROBE])
        if info:
            t = json.loads(info.splitlines()[-1])
            device = "cuda" if t["cuda"] else "mps" if t["mps"] else "cpu"
            print(f"torch:     {t['torch']}, embedding device: {device}"
                  + (f" ({t['threads']} threads)" if device == "cpu" else ""))
        else:
            print("torch:     not installed in .venv")
    print(f"Node.js:   {probe(['node', '--version']) or 'not found (needed only for the stdio bridge)'}")
    print(f"Docker:    {probe(['docker', 'compose', 'version']) or 'not found (needed only for the Docker stacks)'}")

    print("\n=== Services ===")
    health = http_json(f"{RAG_URL}/health")
    if health:
        print(f"rag-server {RAG_URL}: ok, model {health.get('model')}, chunks {health.get('corpora')}")
    else:
        print(f"rag-server {RAG_URL}: not reachable")
    print(f"Docker DB settings: {'docker_mcp-rag-pg/.env present' if (BASE / 'docker_mcp-rag-pg/.env').exists() else 'docker_mcp-rag-pg/.env missing'}")
    print(f"Local DB settings:  {'scripts/.env present' if (SCRIPTS / '.env').exists() else 'scripts/.env missing'}")

    print("\n=== Data ===")
    pack = doc_pack_path()
    print(f"Doc pack:  {pack if pack and Path(pack).exists() else ('configured but not found: ' + pack) if pack else 'not configured (optional; OMNISDOC_PACK in scripts/.env.local)'}")
    n, ok, todo = embedding_state()
    print(f"Chunks:    {n}   embeddings current: {ok}   missing/stale: {todo}")

    print("\n=== Recommendation ===")
    if todo == 0 and n:
        print("Embeddings are complete: run `pipeline.py build --from import`.")
    elif device in ("cuda", "mps"):
        print(f"This machine embeds on {device}: `pipeline.py build --from embed` takes minutes.")
    elif device == "cpu":
        print(f"{todo} chunks to embed on CPU — this takes hours. Faster: run "
              "`pipeline.py build --from embed --to embed` on a machine with Apple Silicon or an NVIDIA GPU "
              "and copy output/embeddings.jsonl here. On CPU, add `--threads <cores>`.")
    else:
        print("Run `pipeline.py setup` first.")


# ── setup ─────────────────────────────────────────────────────

def create_venv(path: Path, requirements: Path, label: str) -> None:
    py = venv_python(path)
    if not py.exists():
        print(f"\nCreating {label} venv at {path}")
        run([sys.executable, "-m", "venv", str(path)])
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "-r", str(requirements)])


def cmd_setup(args: argparse.Namespace) -> None:
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10 or newer is required.")
    create_venv(BASE / ".venv", SCRIPTS / "requirements.txt", "pipeline")
    if args.rag_server:
        rs = BASE / "OmnisRAGServer" / "rag-server"
        create_venv(rs / ".venv", rs / "requirements.txt", "rag-server")
        if not (rs / ".env").exists() and (rs / ".env.example").exists():
            shutil.copy(rs / ".env.example", rs / ".env")
            print(f"Created {rs / '.env'} from .env.example — adjust the database settings.")
    if not (SCRIPTS / ".env.local").exists():
        print("\nOptional: create scripts/.env.local with OMNISDOC_PACK=<path to the doc pack> "
              "(see scripts/.env.local.example).")
    print("\nSetup done. Check the machine with: python scripts/pipeline.py doctor")


# ── build ─────────────────────────────────────────────────────

def cmd_build(args: argparse.Namespace) -> None:
    py = project_python()
    first, last = STEPS.index(args.from_step), STEPS.index(args.to_step)
    if first > last:
        sys.exit("--from must not come after --to")
    pack = args.omnisdoc or doc_pack_path()
    pack_args = ["--omnisdoc", pack] if pack else []
    for step in STEPS[first:last + 1]:
        if step == "extract":
            run([py, "scripts/extract.py"])
        elif step == "chunk":
            run([py, "scripts/chunk.py", *pack_args])
        elif step == "validate":
            run([py, "scripts/validate.py", *pack_args])
        elif step == "embed":
            extra = ["--server", args.embed_server] if args.embed_server else []
            if args.threads:
                extra += ["--threads", str(args.threads)]
            run([py, "scripts/embed_and_store.py", *extra])
        elif step == "import":
            script = "scripts/import_to_docker_postgres.py" if args.target == "docker" else "scripts/import_to_postgres.py"
            run([py, script])
        elif step == "eval":
            if http_json(f"{RAG_URL}/health"):
                run([py, "scripts/eval_retrieval.py", "--compare"], check=False)
            else:
                print(f"\nSkipping eval: rag-server not reachable at {RAG_URL}")
    print("\nBuild finished.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="show system capabilities, services and data state")
    s = sub.add_parser("setup", help="create the virtual environment(s) and install dependencies")
    s.add_argument("--rag-server", action="store_true", help="also set up OmnisRAGServer/rag-server for the local topology")
    b = sub.add_parser("build", help="run pipeline steps")
    b.add_argument("--from", dest="from_step", choices=STEPS, default="extract")
    b.add_argument("--to", dest="to_step", choices=STEPS, default="eval")
    b.add_argument("--target", choices=["docker", "local"], default="docker",
                   help="import into docker_mcp-rag-pg (default) or the database in scripts/.env")
    b.add_argument("--omnisdoc", help="doc pack path (default: OMNISDOC_PACK)")
    b.add_argument("--embed-server", help="embed with the model of a running rag-server, e.g. http://localhost:7071")
    b.add_argument("--threads", type=int, help="CPU threads for local embedding")
    args = ap.parse_args()
    {"doctor": cmd_doctor, "setup": cmd_setup, "build": cmd_build}[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
