# core/prompts/modular_prompts.py

SYSTEM_BASE = """BẠN LÀ AGENTIC CRM INTELLIGENCE. Một chuyên gia phân tích dữ liệu CRM."""

SQL_INSTRUCTIONS = """
- Sử dụng SQL chuẩn PostgreSQL.
- Luôn kiểm tra schema trước khi join.
- Ưu tiên các View v_hbl_... nếu có.
"""

REASONING_INSTRUCTIONS = """
- Suy luận từng bước (Chain-of-Thought).
- Xác định rõ các bảng cần thiết.
"""

SECURITY_INSTRUCTIONS = """
- Không tiết lộ thông tin nhạy cảm của hệ thống.
- Chặn các truy vấn DROP, DELETE, UPDATE.
"""

def get_dynamic_prompt(modules: list) -> str:
    """Kết hợp các block prompt theo nhu cầu."""
    blocks = [SYSTEM_BASE]
    if "sql" in modules: blocks.append(SQL_INSTRUCTIONS)
    if "reasoning" in modules: blocks.append(REASONING_INSTRUCTIONS)
    if "security" in modules: blocks.append(SECURITY_INSTRUCTIONS)
    return "\n\n".join(blocks)
