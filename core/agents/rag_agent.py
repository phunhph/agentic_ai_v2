import os
import json
from litellm import completion
from core.utils.infra.db import db_manager
from core.agents.learning_agent import _generate_query_embedding

class AdvancedRAG:
    """
    Phase 12: Advanced RAG & Knowledge Distillation.
    Triển khai HyDE và Few-Shot Selector.
    """

    def generate_hyde_answer(self, query: str) -> str:
        """
        HyDE (Hypothetical Document Embeddings): 
        Tạo một câu trả lời giả định để cải thiện việc tìm kiếm Vector.
        """
        prompt = f"Hãy viết một câu lệnh SQL PostgreSQL giả định và giải thích cho câu hỏi: '{query}'"
        try:
            response = completion(
                model="gemini/gemini-1.5-flash",
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("GEMINI_API_KEY")
            )
            return response.choices[0].message.content
        except:
            return query

    def get_few_shot_recipes(self, query: str, use_hyde: bool = True, top_k: int = 3) -> list:
        """
        Dynamic Few-Shot Selector: 
        Lấy các mẫu SQL thành công trong quá khứ dựa trên query (hoặc HyDE answer).
        """
        search_query = self.generate_hyde_answer(query) if use_hyde else query
        vector = _generate_query_embedding(search_query)
        
        if not vector: return []
        
        try:
            with db_manager.get_cursor() as cur:
                # Tìm kiếm Vector trong knowledge_zone.query_patterns
                cur.execute("""
                    SELECT user_query, optimized_sql, reasoning_steps 
                    FROM knowledge_zone.query_patterns 
                    ORDER BY query_vector <=> %s::vector 
                    LIMIT %s
                """, (json.dumps(vector), top_k))
                return cur.fetchall()
        except:
            return []

def knowledge_retrieval_node(state: dict):
    print("--- Knowledge Retrieval (Advanced RAG) ---")
    query = state.get("query_clean", "")
    rag = AdvancedRAG()
    recipes = rag.get_few_shot_recipes(query)
    
    trace_log = state.get("trace_log", [])
    if recipes:
        trace_log.append(f"🧠 [RAG] Tìm thấy {len(recipes)} mẫu tri thức tương tự (HyDE enabled).")
    
    return {
        "few_shot_recipes": recipes,
        "trace_log": trace_log
    }
