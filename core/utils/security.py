import re

def is_jailbreak_attempt(query: str) -> bool:
    """Kiểm tra xem câu hỏi có dấu hiệu tấn công jailbreak không"""
    jailbreak_patterns = [
        r"ignore previous instructions",
        r"disregard all previous",
        r"acting as a hacker",
        r"dan mode",
        r"developer mode enabled",
        r"bỏ qua mọi chỉ dẫn",
        r"quên đi các quy tắc"
    ]
    
    query_lower = query.lower()
    for pattern in jailbreak_patterns:
        if re.search(pattern, query_lower):
            return True
    return False

def sanitize_query(query: str) -> str:
    """Làm sạch câu hỏi cơ bản"""
    # Loại bỏ các ký tự điều khiển hoặc mã độc cơ bản nếu cần
    return query.strip()
