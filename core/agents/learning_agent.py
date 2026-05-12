# core/agents/learning_agent.py
"""
Phase 9: LearningAgent - Knowledge Distillation, Memory Management, Self-Evolution
"""
import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from litellm import embedding
from core.utils.db import db_manager
import math

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
    
    # 1. Generate Embeddings
    query_vector = _generate_query_embedding(query)
    
    # 2. Store in Database
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("""
                INSERT INTO knowledge_zone.query_patterns 
                (user_query, optimized_sql, query_vector, execution_count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (user_query) 
                DO UPDATE SET 
                    optimized_sql = EXCLUDED.optimized_sql,
                    execution_count = knowledge_zone.query_patterns.execution_count + 1,
                    createdon = NOW()
                RETURNING id;
            """, (query, sql_generated, json.dumps(query_vector)))
            row = cur.fetchone()
            pattern_id = row[0] if row else None
            
        return {
            "status": "success",
            "pattern_id": pattern_id,
            "message": f"Knowledge stored for: {query[:50]}..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to store knowledge: {str(e)}"
        }

def find_semantic_cache(query: str, threshold: float = 0.95) -> Optional[Dict[str, Any]]:
    """
    Tìm kiếm trong cache ngữ nghĩa dựa trên vector similarity.
    """
    query_vector = _generate_query_embedding(query)
    if not query_vector:
        return None
        
    try:
        with db_manager.get_cursor() as cur:
            cur.execute("SELECT user_query, optimized_sql, query_vector FROM knowledge_zone.query_patterns")
            rows = cur.fetchall()
            
            best_match = None
            max_sim = 0.0
            
            vec1 = query_vector
            
            for user_query, optimized_sql, stored_vec_json in rows:
                if not stored_vec_json:
                    continue
                
                try:
                    vec2 = json.loads(stored_vec_json)
                    
                    # Manual Cosine similarity
                    dot_product = sum(a * b for a, b in zip(vec1, vec2))
                    norm1 = math.sqrt(sum(a * a for a in vec1))
                    norm2 = math.sqrt(sum(b * b for b in vec2))
                    
                    if norm1 == 0 or norm2 == 0:
                        sim = 0
                    else:
                        sim = dot_product / (norm1 * norm2)
                    
                    if sim > max_sim:
                        max_sim = sim
                        best_match = {
                            "query": user_query,
                            "sql": optimized_sql,
                            "similarity": float(sim)
                        }
                except Exception as e:
                    continue
            
            if best_match and max_sim >= threshold:
                return best_match
                
    except Exception as e:
        print(f"Error in semantic cache lookup: {e}")
        
    return None

def _generate_query_embedding(query: str) -> List[float]:
    """Generate vector embedding cho query bằng gemini/text-embedding-004"""
    try:
        response = embedding(
            model="gemini/text-embedding-004",
            input=[query]
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
    else:
        return "SIMPLE"
