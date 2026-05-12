# core/agents/learning_agent.py
"""
Phase 9: LearningAgent - Knowledge Distillation, Memory Management, Self-Evolution
"""
import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
# pyrefly: ignore [missing-import]
from litellm import embedding, completion
from core.utils.infra.db import db_manager
import math

EMBEDDING_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/google/gemma-3-12b")
EMBEDDING_API_KEY = os.getenv("OPENROUTER_API_KEY")

def run_learning_agent(
    query: str,
    sql_generated: str,
    success: bool = True,
    execution_time_ms: float = 0.0,
    results_count: int = 0
) -> Dict[str, Any]:
    """
    LearningAgent: Lưu trữ tri thức, tối ưu hóa, và học từ thực thi.
    """
    
    if not success:
        return {
            "status": "skipped",
            "reason": "Query execution failed, not storing pattern"
        }
    
    # 1. Distill Knowledge (Phase 12)
    distilled_info = _distill_knowledge(query, sql_generated)
    reasoning_steps = distilled_info.get("reasoning_steps", "")
    tags = distilled_info.get("tags", [])

    # 2. Generate Embeddings
    query_vector = _generate_query_embedding(query)
    
    # 3. Store in Database
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge_zone.query_patterns 
                (user_query, optimized_sql, query_vector, reasoning_steps, tags, execution_count)
                VALUES (%s, %s, %s, %s, %s, 1)
                ON CONFLICT (user_query) 
                DO UPDATE SET 
                    optimized_sql = EXCLUDED.optimized_sql,
                    reasoning_steps = EXCLUDED.reasoning_steps,
                    tags = EXCLUDED.tags,
                    execution_count = knowledge_zone.query_patterns.execution_count + 1,
                    createdon = NOW()
                RETURNING id;
            """, (query, sql_generated, json.dumps(query_vector), reasoning_steps, tags))
            row = cur.fetchone()
            pattern_id = row[0] if row else None
            
        return {
            "status": "success",
            "pattern_id": pattern_id,
            "distilled": True,
            "message": f"Knowledge distilled and stored for: {query[:50]}..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to store knowledge: {str(e)}"
        }

def _distill_knowledge(query: str, sql: str) -> Dict[str, Any]:
    """Sử dụng LLM để giải thích logic và gán tags (Phase 12)"""
    prompt = f"""
    Analyze this SQL query and explain its logic. Generate relevant business and technical tags.
    
    USER QUERY: {query}
    SQL: {sql}
    
    RETURN JSON (no markdown):
    {{"reasoning_steps": "...", "tags": ["tag1", "tag2"]}}
    """
    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=os.getenv("GEMINI_API_KEY"),
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"reasoning_steps": "Standard SQL execution", "tags": ["general"]}

def find_semantic_cache(query: str, threshold: float = 0.95) -> Optional[Dict[str, Any]]:
    """
    Tìm kiếm trong cache ngữ nghĩa dựa trên vector similarity (sử dụng pgvector).
    """
    query_vector = _generate_query_embedding(query)
    if not query_vector:
        return None
        
    try:
        with db_manager.get_cursor() as cur:
            # Sử dụng toán tử <=> (cosine distance) của pgvector
            # Distance = 1 - Similarity. Nếu Similarity >= 0.95 thì Distance <= 0.05
            distance_threshold = 1.0 - threshold
            
            cur.execute(f"""
                SELECT user_query, optimized_sql, (query_vector <=> %s::vector) as distance
                FROM knowledge_zone.query_patterns
                WHERE (query_vector <=> %s::vector) <= %s
                ORDER BY query_vector <=> %s::vector
                LIMIT 1;
            """, (json.dumps(query_vector), json.dumps(query_vector), distance_threshold, json.dumps(query_vector)))
            
            row = cur.fetchone()
            if row:
                user_query, optimized_sql, distance = row
                return {
                    "query": user_query,
                    "sql": optimized_sql,
                    "similarity": float(1.0 - distance)
                }
                
    except Exception as e:
        print(f"Error in semantic cache lookup: {e}")
        
    return None

def _generate_query_embedding(query: str) -> List[float]:
    """Generate vector embedding cho query using OpenRouter."""
    try:
        response = embedding(
            model=EMBEDDING_MODEL,
            input=[query],
            api_key=EMBEDDING_API_KEY
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        # Fallback hoặc return empty
        return []

def _estimate_complexity(sql: str) -> str:
    """Ước tính độ phức tạp của query"""
    join_count = sql.upper().count("JOIN")
    subquery_count = sql.upper().count("SELECT") - 1
    
    if join_count > 2 or subquery_count > 1:
        return "HIGH"
    elif join_count > 0 or "GROUP BY" in sql.upper():
        return "MEDIUM"
def run_failure_learning(query: str, error_msg: str, sql_failed: str = None):
    """Phase 18: Học từ lỗi để tránh lặp lại (Negative Knowledge)."""
    query_vector = _generate_query_embedding(query)
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge_zone.failed_patterns 
                (user_query, error_message, failed_sql, query_vector)
                VALUES (%s, %s, %s, %s)
            """, (query, error_msg, sql_failed, json.dumps(query_vector)))
        return {"status": "success", "message": "Failure pattern recorded."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_negative_constraints(query: str, threshold: float = 0.8) -> List[str]:
    """Phase 18: Lấy các cảnh báo lỗi trong quá khứ liên quan đến query."""
    query_vector = _generate_query_embedding(query)
    if not query_vector: return []
    
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("""
                SELECT error_message FROM knowledge_zone.failed_patterns 
                ORDER BY query_vector <=> %s::vector LIMIT 3
            """, (json.dumps(query_vector),))
            return [row[0] for row in cur.fetchall()]
    except:
        return []
