import sys
import os

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.tools.db.sql_executor import execute_business_query
from core.tools.db.schema_tools import get_db_schema

def test_phase_4_security():
    print("="*50)
    print("TESTING PHASE 4: SECURITY & TOOLS")
    print("="*50)

    # 1. Test Safe Query (Should PASS)
    print("\n[Test 1] Safe SELECT Query...")
    res1 = execute_business_query("SELECT count(*) FROM hbl_account")
    if res1["status"] == "success":
        print(f"[PASS] Result count: {res1.get('row_count')}")
    else:
        print(f"[FAIL] {res1.get('message')}")

    # 2. Test Dangerous Query - DROP (Should be BLOCKED by code)
    print("\n[Test 2] Dangerous DROP Query (Software Filter)...")
    res2 = execute_business_query("DROP TABLE hbl_account")
    if res2["status"] == "error" and "Security Error" in res2["message"]:
        print(f"[PASS] Blocked correctly with message: {res2['message']}")
    else:
        print(f"[FAIL] Query was not blocked or message wrong: {res2}")

    # 3. Test Schema Viewer
    print("\n[Test 3] Schema Viewer...")
    res3 = get_db_schema()
    if res3["status"] == "success":
        print(f"[PASS] Found {len(res3['tables'])} tables.")
        if "hbl_account" in res3["tables"]:
            print("   - Successfully read 'hbl_account' metadata.")
    else:
        print(f"[FAIL] {res3.get('message')}")

    print("\n" + "="*50)
    print("PHASE 4 SECURITY TEST COMPLETED")
    print("="*50)

if __name__ == "__main__":
    test_phase_4_security()
