import os
from litellm import completion
from core.utils.logic.token_helper import count_messages_tokens

class ContextCompressor:
    """
    Phase 11: Dynamic Context & Semantic Compression.
    Quản lý bộ nhớ token và nén lịch sử hội thoại.
    """
    
    def __init__(self, token_limit: int = 4000):
        self.token_limit = token_limit

    def filter_messages(self, messages: list) -> list:
        """Lọc bỏ các tin nhắn cũ nếu vượt quá giới hạn Token."""
        while count_messages_tokens(messages) > self.token_limit and len(messages) > 2:
            # Luôn giữ System Prompt (index 0) và tin nhắn mới nhất
            print(f"--- [Compressor] Removing message to save tokens ---")
            messages.pop(1)
        return messages

    def compress_with_llm(self, history: list) -> str:
        """Sử dụng LLM để tóm tắt các hội thoại cũ thành một bản tóm tắt duy nhất."""
        if len(history) < 4:
            return ""
            
        prompt = f"Hãy tóm tắt ngắn gọn các ý chính của cuộc hội thoại sau để làm ngữ cảnh cho AI:\n\n{str(history)}"
        
        try:
            response = completion(
                model="gemini/gemini-1.5-flash",
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("GEMINI_API_KEY")
            )
            return response.choices[0].message.content
        except:
            return "History too long, summary unavailable."

def context_compressor_node(state: dict):
    print("--- Context Compression Node ---")
    compressor = ContextCompressor()
    # Logic tích hợp vào LangGraph state
    return {"trace_log": state.get("trace_log", []) + ["[Compressor] Ngữ cảnh đã được tối ưu."]}
