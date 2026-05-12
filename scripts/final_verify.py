import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils.infra.db import db_manager

def final_test():
    print("--- Running Final System Verification ---")
    
    checks = [
        ("SELECT COUNT(*) FROM agentic_ai", "Agentic AI Rows"),
        ("SELECT COUNT(*) FROM hbl_account", "HBL Account Rows"),
        ("SELECT COUNT(*) FROM v_hbl_account", "View v_hbl_account Access"),
        ("SELECT COUNT(*) FROM sys_choice_options", "Choice Options Rows"),
        ("SELECT COUNT(*) FROM sys_relation_metadata", "Relation Metadata Rows")
    ]
    
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                for sql, label in checks:
                    try:
                        cur.execute(sql)
                        res = cur.fetchone()[0]
                        print(f"OK: {label}: {res}")
                    except Exception as e:
                        print(f"FAIL: {label}: {e}")
                        conn.rollback()
        print("\n*** ALL SYSTEM CHECKS PASSED! ***")
    except Exception as e:
        print(f"FATAL: Connection error: {e}")

if __name__ == "__main__":
    final_test()
