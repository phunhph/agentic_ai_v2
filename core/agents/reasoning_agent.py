import os
import json
import re
from litellm import completion
from core.tools.db.schema_tools import get_relevant_schema

def run_reasoning_agent(query_clean: str, entities: dict):
    """
    ReasoningAgent: Phân tích logic truy vấn.
    Sử dụng Groq Llama3 để suy luận tốc độ cao.
    """
    
    # Trích xuất tên bảng tiềm năng từ entities
    table_hints = set()
    for key in entities.values():
        if isinstance(key, list):
            for item in key:
                # Chỉ thêm string items (không dict/list)
                if isinstance(item, str):
                    table_hints.add(item)
    
    # Lấy schema chỉ các bảng liên quan
    schema = get_relevant_schema(list(table_hints) if table_hints else [])
    schema_str = json.dumps(schema, separators=(',', ':'))
    
    prompt = f"""BẠN LÀ REASONING AGENT. Phân tích câu hỏi và xác định bảng + logic JOIN cần thiết.

SCHEMA: {schema_str}
CÂU HỎI: "{query_clean}"
THỰC THỂ: {json.dumps(entities)}

TRẢ VỀ JSON (không thêm markdown):
{{"thought_process":"...", "required_tables":[], "join_path":"...", "logic_steps":[], "confidence_score":0.0}}
"""

    try:
        response = completion(
            model=os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
            messages=[{"role": "system", "content": prompt}],
            api_key=os.getenv("GROQ_API_KEY"),
            response_format={ "type": "json_object" }
        )
        
        if hasattr(response, 'choices'):
            result_str = response.choices[0].message.content  # type: ignore
        else:
            result_str = str(response)
        
        if not result_str:
            raise ValueError("Empty response from API")
            
        result_str = re.sub(r'^```json\s*|\s*```$', '', result_str.strip(), flags=re.MULTILINE)
        
        return json.loads(result_str)
        
    except Exception as e:
        print(f"DEBUG: ReasoningAgent Error: {e}")
        return {
            "thought_process": "Lỗi khi thực hiện suy luận.",
            "logic_steps": ["Không thể xác định các bước logic do lỗi hệ thống."],
            "error": str(e)
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_query = "Tìm các hợp đồng của công ty Finance tại Việt Nam"
    test_entities = {"accounts": ["Finance"], "others": ["Vietnam"]}
    print(json.dumps(run_reasoning_agent(test_query, test_entities), indent=2))
