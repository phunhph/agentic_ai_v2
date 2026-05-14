from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.utils.infra.db import get_connection


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "data" / "migration" / "2026_05_14_tenant_rls.sql"


def main() -> int:
    sql = MIGRATION.read_text(encoding="utf-8")
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
    print(f"Applied migration: {MIGRATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
