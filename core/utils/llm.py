import json
import logging
import os
from typing import Any, Type, TypeVar

import litellm
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def get_chat_model() -> str:
    model_key = os.getenv("CHAT_MODEL", "gemini")
    return os.getenv(f"{model_key.upper()}_MODEL", "gemini/gemini-1.5-flash")

def get_reasoning_model() -> str:
    model_key = os.getenv("REASONING_MODEL", "gemini")
    return os.getenv(f"{model_key.upper()}_MODEL", "gemini/gemini-1.5-pro")

def generate_structured_output(prompt: str, schema: Type[T], model: str | None = None) -> T:
    """Generate structured JSON output conforming to a Pydantic schema using LiteLLM."""
    if model is None:
        model = get_reasoning_model()
        
    schema_json = schema.model_json_schema()
    
    messages = [
        {"role": "system", "content": f"You are an expert AI agent. You must respond ONLY with a valid JSON object that strictly adheres to this schema:\n{json.dumps(schema_json)}"},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        return schema.model_validate_json(content)
    except Exception as e:
        logger.error(f"Error generating structured output: {e}")
        # Fallback to basic JSON extraction if response_format fails (some models don't support it)
        response = litellm.completion(
            model=model,
            messages=messages,
            temperature=0.1
        )
        content = response.choices[0].message.content
        # Try to extract JSON from markdown block
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        return schema.model_validate_json(content)
