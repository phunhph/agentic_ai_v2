import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """Quản lý kết nối PostgreSQL tập trung"""
    
    def __init__(self):
        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "agentic_ai"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "sa"),
            "port": os.getenv("DB_PORT", "5432")
        }

    @contextmanager
    def get_connection(self):
        """Context manager để lấy connection và tự động commit/rollback/close"""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self):
        """Context manager để lấy cursor và tự động đóng"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            try:
                yield cur
            finally:
                cur.close()

# Singleton instance
db_manager = DatabaseManager()
