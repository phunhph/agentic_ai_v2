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

def run_init_sql():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("--- Dang thuc thi data/schema/init.sql ---")
        
        with open("data/schema/init.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            
        cur.execute(sql)
        conn.commit()
        print("OK: Init SQL executed successfully.")

    except Exception as e:
        print(f"ERROR: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_init_sql()
