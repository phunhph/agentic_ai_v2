import tiktoken
from typing import List, Dict

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Đếm số lượng token trong văn bản."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

def count_messages_tokens(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> int:
    """Đếm tổng số token trong danh sách tin nhắn."""
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += count_tokens(value, model)
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens
