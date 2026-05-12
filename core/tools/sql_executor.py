import psycopg2
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FORBIDDEN_KEYWORDS = ["drop", "delete", "truncate", "update", "alter", "create", "grant"]

def validate_sql(sql_query: str) -> bool:
    """
    Basic SQL Validation: Only allow SELECT queries and block forbidden keywords.
    """
    query = sql_query.lower().strip()
    if not query.startswith("select"):
        return False
    if any(keyword in query for keyword in FORBIDDEN_KEYWORDS):
        return False
    return True

def execute_business_query(sql_query: str, agent_name: str = "ExecutionAgent"):
    """
    Executes a SELECT query safely and logs the action to audit_zone.
    """
    if not validate_sql(sql_query):
        return {"status": "error", "message": "Query rejected by security policy (Only SELECT allowed)."}

    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "agentic_ai"),
            user=os.getenv("DB_USER", "agent_user"),
            password=os.getenv("DB_PASSWORD", "secure_password"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        start_time = datetime.now()
        cur.execute(sql_query)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        end_time = datetime.now()
        
        latency = int((end_time - start_time).total_seconds() * 1000)
        
        # Format results
        data = [dict(zip(columns, row)) for row in results]
        
        # Log to audit_zone
        log_audit(cur, agent_name, sql_query, "success", latency)
        conn.commit()
        
        return {"status": "success", "results": data, "latency": latency}
        
    except Exception as e:
        if conn:
            cur = conn.cursor()
            log_audit(cur, agent_name, sql_query, f"error: {str(e)}", 0)
            conn.commit()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()

def log_audit(cur, agent_name: str, query: str, status: str, latency: int):
    """
    Saves the execution log into audit_zone.agent_trace_logs.
    """
    trace_id = str(uuid.uuid4())
    try:
        cur.execute("""
            INSERT INTO audit_zone.agent_trace_logs 
            (trace_id, agent_name, sql_query, execution_status, latency_ms)
            VALUES (%s, %s, %s, %s, %s)
        """, (trace_id, agent_name, query, status, latency))
    except Exception as e:
        print(f"Audit Logging Failed: {str(e)}")
