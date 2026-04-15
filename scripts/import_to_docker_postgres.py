"""
import_to_docker_postgres.py — run the existing PostgreSQL import against the
containerized PostgreSQL published by docker_mcp-rag-pg/.

This script keeps scripts/import_to_postgres.py unchanged.
It only resolves the Docker stack env file, sets RAG_DB_* overrides, and then
launches the existing importer with the current Python interpreter.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = BASE_DIR / "docker_mcp-rag-pg" / ".env"
IMPORT_SCRIPT = BASE_DIR / "scripts" / "import_to_postgres.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import embeddings into the dockerized PostgreSQL instance."
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the docker_mcp-rag-pg env file.",
    )
    parser.add_argument(
        "--host",
        help="Override the host used to reach the published Docker PostgreSQL port.",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Override the published Docker PostgreSQL port.",
    )
    return parser.parse_args()


def resolve_env_file(env_file: Path) -> Path | None:
    if env_file.exists():
        return env_file
    return None


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment value: {name}")
    return value


def load_env_file(env_file: Path) -> None:
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value[:1] == value[-1:] and value.startswith(("'", '"')):
            value = value[1:-1]

        os.environ.setdefault(key, value)


def main() -> None:
    args = parse_args()
    env_file = resolve_env_file(args.env_file)

    if env_file:
        load_env_file(env_file)

    db_host = args.host or os.environ.get("DOCKER_PG_HOST", "127.0.0.1")
    db_port = args.port or int(os.environ.get("POSTGRES_HOST_PORT", "5432"))
    db_name = os.environ.get("POSTGRES_DB", "ragdb")
    db_user = os.environ.get("RAG_DB_USER", "rag_app")
    db_pass = require_env("RAG_DB_PASS")

    child_env = os.environ.copy()
    child_env.update(
        {
            "RAG_DB_HOST": db_host,
            "RAG_DB_PORT": str(db_port),
            "RAG_DB_NAME": db_name,
            "RAG_DB_USER": db_user,
            "RAG_DB_PASS": db_pass,
        }
    )

    print("=== Docker PostgreSQL Import ===")
    print(f"Env file: {env_file or 'not found, using current environment only'}")
    print(f"Target:   {db_host}:{db_port}/{db_name}")
    print(f"User:     {db_user}")
    print()

    subprocess.run(
        [sys.executable, str(IMPORT_SCRIPT)],
        cwd=BASE_DIR,
        env=child_env,
        check=True,
    )


if __name__ == "__main__":
    main()
