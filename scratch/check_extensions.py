import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_extensions():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "agentic_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "sa"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM pg_available_extensions WHERE name IN ('vector', 'pg_trgm', 'fuzzystrmatch');")
        extensions = cur.fetchall()
        for ext in extensions:
            print(f"Extension {ext[0]} is available (version {ext[1]}).")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_extensions()
