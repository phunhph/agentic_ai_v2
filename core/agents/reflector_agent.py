import os
import json
from litellm import completion
from core.utils.logic.json_helper import json_dumps

def run_reflector_agent(query: str, sql: str, results: list, reasoning: str):
    """
    ReflectorAgent: Kiểm tra tính đúng đắn của SQL và kết quả so với ý định người dùng.
    """
    
    # Chuẩn bị kết quả JSON an toàn sử dụng json_helper
    results_json = json_dumps(results[:5], indent=2)

    prompt = f"""
    BẠN LÀ SENIOR DATA QA EXPERT. Nhiệm vụ của bạn là kiểm tra xem câu lệnh SQL và kết quả có khớp với ý định của người dùng hay không.
    
    CÂU HỎI NGƯỜI DÙNG: "{query}"
    LẬP LUẬN CỦA AGENT: "{reasoning}"
    SQL ĐÃ TẠO: 
    {sql}
    
    KẾT QUẢ TRẢ VỀ (TOP 5):
    {results_json}
    
    HÃY KIỂM TRA:
    1. SQL có thực sự giải quyết được câu hỏi không? (Ví dụ: Có JOIN nhầm bảng, nhầm ID không?)
    2. Kết quả trả về có hợp lý không? (Ví dụ: Tổng doanh thu có bị âm, hoặc rỗng một cách vô lý không?)
    3. Có lỗi logic nào trong cách tính toán không?
    
    TRẢ VỀ JSON:
    {{
        "is_correct": true,
        "confidence_score": 0.9,
        "critique": "Giải thích chi tiết nếu sai",
        "suggested_fix": "Gợi ý cách sửa nếu sai"
    }}
    """
    
    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "system", "content": prompt}],
            api_key=os.getenv("GEMINI_API_KEY"),
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"DEBUG: ReflectorAgent Error: {e}")
        return {
            "is_correct": True, 
            "confidence_score": 0.5,
            "critique": f"Reflector Error: {str(e)}",
            "suggested_fix": ""
        }
