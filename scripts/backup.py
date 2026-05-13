"""Backup helper for Agentic AI PostgreSQL database."""
from __future__ import annotations
import os
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def backup() -> None:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = ROOT.parent / f"agentic_backup_{timestamp}.sql"

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "agentic_ai")
    db_user = os.getenv("DB_USER", "postgres")

    command = [
        "pg_dump",
        "--dbname",
        f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}",
        "--file",
        str(filename),
    ]

    print(f"Creating backup: {filename}")
    subprocess.run(command, check=True)
    print("Backup created successfully.")


if __name__ == "__main__":
    backup()
