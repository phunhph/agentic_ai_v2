import os
import json
import re
from litellm import completion
from core.tools.db.schema_tools import get_relevant_schema

def run_execution_agent(plan: list, query_clean: str):
    """
    ExecutionAgent: Chuyển đổi kế hoạch thành câu lệnh SQL.
    Sử dụng Groq Llama 3.3 để sinh SQL chính xác.
    """
    
    # Trích xuất tên bảng từ kế hoạch
    required_tables = set()
    for task in plan:
        task_text = str(task.get("task", "")).lower()
        # Tìm tên bảng có thể có trong mô tả task
        if "account" in task_text or "hbl_account" in task_text:
            required_tables.add("hbl_account")
        if "contract" in task_text or "hbl_contract" in task_text:
            required_tables.add("hbl_contract")
        if "party" in task_text or "hbl_party" in task_text:
            required_tables.add("hbl_party")
    
    # Lấy schema tối ưu chỉ các bảng cần thiết
    schema = get_relevant_schema(list(required_tables) if required_tables else [])
    schema_str = json.dumps(schema, separators=(',', ':'))
    
    prompt = f"""BẠN LÀ EXECUTION AGENT. Tạo RA DUY NHẤT MỘT câu lệnh SQL SELECT dựa trên kế hoạch.

SCHEMA: {schema_str}

KẾ HOẠCH:
{json.dumps(plan, separators=(',', ':'))}

CÂU HỎI GỐC: "{query_clean}"

QUY TẮC:
1. CHỈ SELECT, không UPDATE/DELETE
2. Tên bảng & cột PHẢI khớp schema
3. Sử dụng JOIN với Foreign Keys
4. Trả JSON (không markdown): {{"sql":"SELECT...", "explanation":"...", "complexity":"SIMPLE"}}
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
        print(f"DEBUG: ExecutionAgent Error: {e}")
        return {
            "sql": None,
            "explanation": "Lỗi khi sinh SQL.",
            "error": str(e)
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_plan = [{"id": 1, "task": "Lấy 5 bản ghi từ hbl_account"}]
    print(json.dumps(run_execution_agent(test_plan, "Show me 5 accounts"), indent=2))
