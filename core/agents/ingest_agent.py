import re
import uuid
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from core.utils.infra.checkpoint import CheckpointStore

logger = logging.getLogger(__name__)

INTENT_KEYWORDS = {
    "sales": ["sales", "revenue", "deal", "quota"],
    "support": ["support", "ticket", "issue", "bug"],
    "customer_success": ["customer success", "onboarding", "renewal"],
    "research": ["market", "analysis", "trend", "insight"],
}

ENTITY_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\+?[0-9][0-9\-\s]{7,}[0-9]",
    "date": r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b",
}

CHECKPOINT_NAMESPACE = "agentic_phase4"


class IngestAgent:
    def __init__(self) -> None:
        self.checkpoint_store = CheckpointStore()

    def process(
        self,
        prompt: str,
        thread_id: str,
        session_id: str | None = None,
        previous_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_prompt = self._normalize_prompt(prompt)
        
        try:
            detected_language = detect(normalized_prompt)
        except LangDetectException:
            detected_language = "en"
            
        intent = self._classify_intent(normalized_prompt)
        entities = self._extract_entities(normalized_prompt)
        state = self._build_state(
            normalized_prompt=normalized_prompt,
            intent=intent,
            entities=entities,
            detected_language=detected_language,
            thread_id=thread_id,
            session_id=session_id,
            previous_state=previous_state,
            metadata=metadata,
        )

        self.checkpoint_store.create_checkpoint(
            thread_id=thread_id,
            session_id=session_id,
            checkpoint_data=state,
            previous_checkpoint_id=(previous_state or {}).get("checkpoint_id") if previous_state else None,
        )
        return state

    def _normalize_prompt(self, prompt: str) -> str:
        text = prompt.strip()
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\u2019", "'")
        return text

    def _classify_intent(self, text: str) -> str:
        lower = text.lower()
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(keyword in lower for keyword in keywords):
                return intent
        return "general"

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities: Dict[str, List[str]] = {}
        for name, pattern in ENTITY_PATTERNS.items():
            found = re.findall(pattern, text)
            if found:
                entities[name] = list({item.strip() for item in found})

        label_matches = []
        if "account" in text.lower():
            label_matches.append("account")
        if "contact" in text.lower():
            label_matches.append("contact")
        if "pipeline" in text.lower():
            label_matches.append("pipeline")
        if label_matches:
            entities["labels"] = label_matches

        return entities

    def _build_state(
        self,
        normalized_prompt: str,
        intent: str,
        entities: Dict[str, List[str]],
        detected_language: str,
        thread_id: str,
        session_id: str,
        previous_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "checkpoint_id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "session_id": session_id,
            "normalized_prompt": normalized_prompt,
            "detected_language": detected_language,
            "intent": intent,
            "entities": entities,
            "metadata": metadata or {},
            "previous_checkpoint_id": (previous_state or {}).get("checkpoint_id"),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "namespace": CHECKPOINT_NAMESPACE,
        }
