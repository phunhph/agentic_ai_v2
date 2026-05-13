"""Deployment helper for Agentic AI."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_command(command: list[str]) -> None:
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def deploy() -> None:
    env = os.getenv("DEPLOY_ENV", "dev")
    print(f"Deploying Agentic AI to {env}")

    print("1. Initializing database")
    run_command([sys.executable, str(ROOT / "init_db.py")])

    print("2. Starting API")
    run_command([sys.executable, str(ROOT.parent / "run.py"), "api"])


if __name__ == "__main__":
    deploy()
