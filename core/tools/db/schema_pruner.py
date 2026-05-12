import json
from typing import List, Dict, Any
from core.agents.learning_agent import _generate_query_embedding
from core.utils.infra.db import db_manager

class SchemaPruner:
    """
    Phase 16: Semantic Schema Pruning.
    Sử dụng Vector Search để lấy các bảng liên quan đến query.
    """
    
    def prune(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Tìm các bảng có mô tả gần nhất với query.
        """
        query_vector = _generate_query_embedding(query)
        if not query_vector:
            return {} # Fallback to all tables if embedding fails
            
        try:
            with db_manager.get_cursor() as cur:
                # Giả định có bảng knowledge_zone.schema_metadata chứa mô tả các table
                cur.execute("""
                    SELECT table_name, table_description 
                    FROM knowledge_zone.schema_metadata 
                    ORDER BY table_vector <=> %s::vector 
                    LIMIT %s
                """, (json.dumps(query_vector), top_k))
                rows = cur.fetchall()
                
                selected_tables = [row[0] for row in rows]
                return {"selected_tables": selected_tables}
        except Exception as e:
            print(f"Schema Pruning Error: {e}")
            return {}

def schema_pruner_node(state: Dict[str, Any]):
    print("--- Schema Pruning (RAG) ---")
    query = state.get("query_clean", "")
    pruner = SchemaPruner()
    result = pruner.prune(query)
    
    selected_tables = result.get("selected_tables", [])
    trace_log = state.get("trace_log", [])
    
    if selected_tables:
        trace_log.append(f"🔍 [Schema] Đã chọn {len(selected_tables)} bảng liên quan nhất.")
    
    return {
        "relevant_tables": selected_tables,
        "trace_log": trace_log
    }
