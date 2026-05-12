import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """Quản lý kết nối PostgreSQL tập trung"""
    
    def __init__(self):
        self.default_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "agentic_ai"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "sa"),
            "port": os.getenv("DB_PORT", "5432")
        }
        
        # Cấu hình cho Agent (Restricted User - Phase 4)
        self.agent_config = self.default_config.copy()
        self.agent_config.update({
            "user": "postgres",
            "password": "sa"
        })

    @contextmanager
    def get_connection(self, use_agent=False):
        """Context manager để lấy connection. use_agent=True sẽ dùng tài khoản giới hạn."""
        config = self.agent_config if use_agent else self.default_config
        conn = None
        try:
            conn = psycopg2.connect(**config)
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
    def get_cursor(self, use_agent=False):
        """Context manager để lấy cursor."""
        with self.get_connection(use_agent=use_agent) as conn:
            cur = conn.cursor()
            try:
                yield cur
            finally:
                cur.close()

# Singleton instance
db_manager = DatabaseManager()
