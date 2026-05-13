from __future__ import annotations
from typing import Any, Dict


class TenantGuard:
    def __init__(self) -> None:
        self.tenant_map: Dict[str, str] = {}

    def assign_tenant(self, session_id: str | None, tenant_id: str) -> None:
        if session_id:
            self.tenant_map[session_id] = tenant_id

    def get_tenant_id(self, session_id: str | None) -> str | None:
        if not session_id:
            return None
        return self.tenant_map.get(session_id)

    def validate_access(self, thread_id: str, session_id: str | None) -> bool:
        if not session_id:
            return True
        return True

    def attach_context(self, payload: Dict[str, Any], session_id: str | None) -> Dict[str, Any]:
        tenant_id = self.get_tenant_id(session_id)
        if tenant_id:
            payload["tenant_id"] = tenant_id
        return payload
