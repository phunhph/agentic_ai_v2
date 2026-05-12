import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_vector_extension():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "agentic_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "sa"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        extension = cur.fetchone()
        if extension:
            print("pgvector is installed.")
        else:
            print("pgvector is NOT installed.")
            # Try to install it
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                print("pgvector installed successfully.")
            except Exception as e:
                print(f"Failed to install pgvector: {e}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_vector_extension()
