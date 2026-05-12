import psycopg2
import os
import json
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
        # Đảm bảo dùng password từ .env nếu có, thay vì hardcode 'sa'
        self.agent_config.update({
            "user": os.getenv("DB_USER", "postgres"),
            "password": self.default_config["password"]
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

    def log_agent_interaction(self, session_id: str, node: str, input_data: dict, output_data: dict, usage: dict = None):
        """Phase 15: Lưu vết thực thi và token usage vào audit_zone."""
        try:
            with self.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO audit_zone.agent_logs 
                    (session_id, node_name, input_payload, output_payload, token_count, cost_usd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    session_id, node, json.dumps(input_data), json.dumps(output_data),
                    usage.get("total_tokens", 0) if usage else 0,
                    usage.get("total_cost", 0.0) if usage else 0.0
                ))
        except Exception as e:
            print(f"Failed to log interaction: {e}")

    def store_feedback(self, session_id: str, rating: int, comment: str = None):
        """Phase 15: Lưu feedback người dùng."""
        try:
            with self.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO audit_zone.user_feedback (session_id, rating, comment)
                    VALUES (%s, %s, %s)
                """, (session_id, rating, comment))
        except Exception as e:
            print(f"Failed to store feedback: {e}")

# Singleton instance
db_manager = DatabaseManager()
