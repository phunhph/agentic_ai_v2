import os
import json
# pyrefly: ignore [missing-import]
from litellm import completion

def run_commander_agent(query: str):
    """
    Commander Agent: Phân rã nhiệm vụ và chỉ định Agent chuyên biệt.
    """
    
    prompt = f"""
    BẠN LÀ COMMANDER AGENT (ARCHITECT). Phân tích yêu cầu và lập kế hoạch phối hợp.
    
    CÁC AGENT CÓ SẴN:
    1. SQL_SPECIALIST: Truy vấn dữ liệu từ DB.
    2. BUSINESS_ANALYST: Tính toán KPI, dự báo, so sánh.
    3. COMPLIANCE_AGENT: Kiểm tra bảo mật, chính sách.
    
    YÊU CẦU: "{query}"
    
    TRẢ VỀ JSON:
    {{
        "task_decomposition": [
            {{"step": 1, "agent": "AGENT_NAME", "objective": "..."}},
            ...
        ],
        "final_aggregator": "AGENT_NAME"
    }}
    """
    
    try:
        response = completion(
            model="gemini/gemini-1.5-pro",
            messages=[{"role": "system", "content": prompt}],
            api_key=os.getenv("GEMINI_API_KEY"),
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"task_decomposition": [{"step": 1, "agent": "SQL_SPECIALIST", "objective": query}], "final_aggregator": "SQL_SPECIALIST"}
