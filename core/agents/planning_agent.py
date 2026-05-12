import os
import json
import re
from litellm import completion

def run_planning_agent(logic_steps: list, required_tables: list, previous_error=None):
    """
    PlanningAgent: Chuyển đổi logic thành kế hoạch thực thi cụ thể.
    Hỗ trợ Recursive Planning nếu có lỗi từ bước trước.
    """
    
    error_context = ""
    if previous_error:
        error_context = f"\n⚠️ LỖI TRƯỚC: {previous_error}\nHãy điều chỉnh kế hoạch để khắc phục."

    prompt = f"""BẠN LÀ PLANNING AGENT. Lập danh sách công việc cụ thể để ExecutionAgent thực hiện.{error_context}

LOGIC STEPS:
{json.dumps(logic_steps, separators=(',', ':'))}

BẢNG LIÊN QUAN:
{json.dumps(required_tables, separators=(',', ':'))}

TRẢ VỀ JSON (không markdown):
{{"plan_name":"...", "tasks":[{{"id":1, "task":"...", "priority":"HIGH", "status":"TODO"}}], "estimated_complexity":"LOW", "summary":"..."}}
"""

    try:
        response = completion(
            model=os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash"),
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
        print(f"DEBUG: PlanningAgent Error: {e}")
        return {
            "plan_name": "Kế hoạch dự phòng",
            "tasks": [
                {"id": 1, "task": "Thực hiện truy vấn SQL dựa trên logic có sẵn.", "priority": "HIGH", "status": "TODO"}
            ],
            "error": str(e)
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_logic = ["Lọc công ty theo ngành Finance", "Lấy danh sách hợp đồng liên quan"]
    test_tables = ["hbl_account", "hbl_contract"]
    print(json.dumps(run_planning_agent(test_logic, test_tables), indent=2))
