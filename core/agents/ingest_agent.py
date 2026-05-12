import os
import json
import re
from litellm import completion
from core.tools.db.schema_tools import get_db_schema
from core.prompts.security_rules import SECURITY_SYSTEM_PROMPT

def run_ingest_agent(query: str):
    """
    IngestAgent: Phân tích đầu vào, trích xuất thực thể và kiểm tra bảo mật.
    Sử dụng Gemini 1.5 Flash.
    """
    
    # Nếu query rỗng, trả về kết quả mặc định ngay
    if not query or not query.strip():
        return {
            "intent": "UNKNOWN",
            "entities": {"accounts": [], "dates": [], "others": []},
            "security_status": "SAFE",
            "is_ambiguous": True,
            "refined_query": "Câu hỏi rỗng hoặc không rõ ràng.",
            "reasoning": "Câu hỏi của người dùng không có nội dung."
        }

    schema = get_db_schema()
    table_names = list(schema.get("tables", {}).keys())
    
    prompt = f"""{SECURITY_SYSTEM_PROMPT}

BẠN LÀ INGEST AGENT. Phân tích câu hỏi, kiểm tra bảo mật, trích xuất thực thể.

BẢNG TRONG HỆ THỐNG: {json.dumps(table_names)}

CÂU HỎI: "{query}"

TRẢ VỀ JSON (không markdown):
{{"intent":"REPORT_QUERY", "entities":{{"accounts":[], "dates":[], "others":[]}}, "security_status":"SAFE", "is_ambiguous":false, "refined_query":"...", "reasoning":"..."}}
"""

    try:
        response = completion(  # type: ignore
            model=os.getenv("GEMINI_MODEL", "models/gemini-embedding-2-preview"),
            messages=[{"role": "system", "content": prompt}],
            api_key=os.getenv("GEMINI_API_KEY"),
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
        print(f"DEBUG: IngestAgent Error: {e}")
        return {
            "intent": "UNKNOWN",
            "entities": {"accounts": [], "dates": [], "others": []},
            "security_status": "SAFE",
            "is_ambiguous": True,
            "error": str(e),
            "reasoning": "Lỗi khi gọi hoặc phân tích kết quả từ LLM."
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(json.dumps(run_ingest_agent("HBL account contracts in May"), indent=2))
