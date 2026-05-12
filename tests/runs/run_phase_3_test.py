import requests
import json
import uuid
import sys
import os

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.utils.infra.db import db_manager

def run_phase_3_test():
    print("\n" + "="*50)
    print("RUNNING PHASE 3 TEST: UI & TRACING")
    print("="*50 + "\n")

    api_base = "http://localhost:5000/v1/agent"
    
    # 1. Test API Health
    print("Step 1: Checking API Health...")
    try:
        resp = requests.get(f"{api_base}/health")
        if resp.status_code == 200 and resp.json().get("status") == "ok":
            print("[OK] API Health")
        else:
            print(f"[FAILED] API Health ({resp.status_code})")
            return
    except Exception as e:
        print(f"[ERROR] API Health - {e}")
        return

    # 2. Test Chat Trace
    print("\nStep 2: Testing Chat Trace flow...")
    query = "Hoi ve Finance accounts tai Vietnam"
    payload = {"query": query, "thread_id": str(uuid.uuid4())}
    
    try:
        resp = requests.post(f"{api_base}/chat", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            trace_log = data.get("trace_log", [])
            trace_details = data.get("trace_details", [])
            
            print(f"[OK] Chat API")
            print(f"Trace Steps: {len(trace_log)}")
            
            if len(trace_log) >= 5:
                print("[OK] Full Trace Log detected (5 nodes)")
            else:
                print(f"[WARNING] Incomplete Trace Log: {len(trace_log)} steps")
                
            if trace_details and "input" in trace_details[0] and "output" in trace_details[0]:
                print("[OK] Structured Trace Details (In/Out) detected")
            else:
                print("[FAILED] Structured Trace Details MISSING")
        else:
            print(f"[FAILED] Chat API ({resp.status_code})")
            return
    except Exception as e:
        print(f"[ERROR] Chat API - {e}")
        return

    # 3. Test Database Audit Persistence
    print("\nStep 3: Checking Database Audit Logs...")
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("SELECT count(*) FROM audit_zone.agent_trace_logs")
            count = cur.fetchone()[0]
            print(f"[OK] Database Audit: Found {count} logs in audit_zone.agent_trace_logs")
            
            if count > 0:
                print("[PASS] Trace Persistence")
            else:
                print("[FAILED] Trace Persistence (0 records)")
    except Exception as e:
        print(f"[ERROR] Database Audit - {e}")

    print("\n" + "="*50)
    print("PHASE 3 TEST COMPLETED")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_phase_3_test()
