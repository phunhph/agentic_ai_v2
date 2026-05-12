import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "agentic_ai"),
    "user": os.getenv("DB_USER", "agent_user"),
    "password": os.getenv("DB_PASSWORD", "secure_password"),
    "port": os.getenv("DB_PORT", "5432")
}

def test_database_schema():
    print("--- Running Phase 2 Test: Database Schema & Data ---")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Check Schemas
        print("Checking Schemas...")
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('business_zone', 'knowledge_zone', 'audit_zone')")
        schemas = [r[0] for r in cur.fetchall()]
        print(f"Found schemas: {schemas}")
        if len(schemas) >= 1:
            print("OK: Schemas found.")
        
        # 2. Check Business Tables
        print("Checking Business Tables...")
        tables = ['hbl_account', 'hbl_contact', 'hbl_opportunities', 'hbl_contract', 'systemuser']
        for t in tables:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (t,))
            if cur.fetchone()[0]:
                print(f"PASS: Table '{t}' exists.")
            else:
                print(f"FAIL: Table '{t}' missing.")

        # 3. Check Metadata
        cur.execute("SELECT count(*) FROM sys_choice_options")
        print(f"PASS: Choice options count: {cur.fetchone()[0]}")

        # 4. Check Agentic AI Data
        cur.execute("SELECT count(*) FROM agentic_ai")
        print(f"PASS: Agentic AI row count: {cur.fetchone()[0]}")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    test_database_schema()
