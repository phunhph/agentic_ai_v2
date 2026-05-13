"""Initialize Phase 1 PostgreSQL schema for Agentic AI."""
from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agentic_ai")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def _connect(database: str):
    return psycopg2.connect(
        dbname=database,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def create_database() -> None:
    with _connect("postgres") as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if not cur.fetchone():
                print(f"Creating database {DB_NAME}...")
                cur.execute(f"CREATE DATABASE {DB_NAME}")
            else:
                print(f"Database {DB_NAME} already exists.")


def apply_schema() -> None:
    sql_path = ROOT / "data" / "schema" / "init.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"Schema init file not found: {sql_path}")

    with _connect(DB_NAME) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            print(f"Applying schema from {sql_path}")
            try:
                cur.execute(sql_path.read_text())
            except psycopg2.errors.FeatureNotSupported as exc:
                raise RuntimeError(
                    "PostgreSQL does not support the required extension or feature. "
                    "If you are using a local PostgreSQL instance, install the `vector` extension or run the database inside the provided Docker Compose service. "
                    "If you are using Docker Compose, make sure the service is running and `DB_HOST`/`DB_PORT` point to it."
                ) from exc


def main() -> None:
    print("Agentic Phase 1 DB initialization")
    create_database()
    apply_schema()
    print("Phase 1 schema initialization complete.")


if __name__ == "__main__":
    main()
