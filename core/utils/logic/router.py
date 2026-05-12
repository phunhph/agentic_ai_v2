import os
import time
import random
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from litellm import Router, completion

class AgentRouter:
    """
    Phase 14: Quản lý Resilience, Rate Limiting và Fallback Matrix.
    Sử dụng LiteLLM Router để điều phối giữa các providers.
    """
    
    def __init__(self):
        # Cấu hình danh sách các model dự phòng
        model_list = [
            {
                "model_name": "gemini-pro",
                "litellm_params": {
                    "model": "gemini/gemini-1.5-pro",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                },
                "tpm": 100000, "rpm": 1000
            },
            {
                "model_name": "gemini-flash",
                "litellm_params": {
                    "model": "gemini/gemini-1.5-flash",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                },
                "tpm": 1000000, "rpm": 2000
            },
            {
                "model_name": "groq-llama",
                "litellm_params": {
                    "model": "groq/llama-3.1-70b-versatile",
                    "api_key": os.getenv("GROQ_API_KEY"),
                }
            }
        ]
        
        self.router = Router(
            model_list=model_list,
            routing_strategy="latency-based-routing",
            num_retries=3,
            retry_after=5,
            timeout=30
        )

    def completion_with_resilience(self, **kwargs):
        """
        Thực hiện gọi LLM với cơ chế Exponential Backoff và Jitter.
        """
        max_retries = kwargs.pop("max_retries", 3)
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Sử dụng router để tự động fallback và load balance
                return self.router.completion(**kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Exponential Backoff with Jitter
                delay = (base_delay * (2 ** attempt)) + (random.random() * 0.5)
                print(f"⚠️ [Resilience] Lỗi: {e}. Thử lại sau {delay:.2f}s (Lần {attempt+1})...")
                time.sleep(delay)

# Singleton Instance
agent_router = AgentRouter()
