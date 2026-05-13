"""Simple operational monitor for Agentic AI service endpoints."""
from __future__ import annotations
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def check_url(url: str) -> bool:
    req = Request(url, headers={"User-Agent": "agentic-monitor/1.0"})
    try:
        with urlopen(req, timeout=10) as response:
            return response.status == 200
    except (HTTPError, URLError) as exc:
        print(f"Health check failed for {url}: {exc}")
        return False


def main() -> int:
    host = os.getenv("API_HOST", "http://localhost:8000")
    health_url = f"{host}/health"
    ready_url = f"{host}/ready"

    print(f"Checking {health_url}")
    ok_health = check_url(health_url)
    print(f"Checking {ready_url}")
    ok_ready = check_url(ready_url)

    if ok_health and ok_ready:
        print("Service is healthy and ready.")
        return 0

    print("Service check failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
