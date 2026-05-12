import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "agentic_ai"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "sa"),
    "port": os.getenv("DB_PORT", "5432")
}

def finalize_phase_2():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("--- Hoan thien Phase 2: AI Infrastructure & Validation ---")

        # 1. Tao Vector Index (HNSW)
        print("Creating Vector Index (HNSW) for query_patterns...")
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS query_patterns_vector_idx 
                ON knowledge_zone.query_patterns 
                USING hnsw (query_vector vector_cosine_ops);
            """)
            print("OK: Vector Index created.")
        except Exception as e:
            print(f"Note: Vector index creation might need pgvector extension or higher permissions: {e}")

        # 2. Validate Lookup Graph
        print("Validating Lookup Graph...")
        cur.execute("SELECT from_table, from_field, to_table FROM sys_relation_metadata;")
        relations = cur.fetchall()
        
        valid = True
        for from_t, from_f, to_t in relations:
            # Check if to_table exists
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);", (to_t,))
            if not cur.fetchone()[0]:
                print(f"Warning: Target table '{to_t}' in relation does not exist.")
                valid = False
        
        if valid:
            print("OK: Lookup Graph validated successfully.")

        # 3. Add Indexes for Lookup Performance
        print("Adding indexes for performance...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hbl_contact_accountid ON hbl_contact (hbl_contact_accountid);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hbl_opp_accountid ON hbl_opportunities (hbl_opportunities_accountid);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hbl_contract_oppid ON hbl_contract (hbl_contract_opportunityid);")

        conn.commit()
        print("\n*** PHASE 2 FINALIZED SUCCESSFULLY! ***")

    except Exception as e:
        print(f"ERROR: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    finalize_phase_2()
