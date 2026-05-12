"""
Phase 10: Context Monitor & Coreference Resolution
Manages multi-turn conversations, context linking, and hallucination detection
"""
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta


class ContextMonitor:
    """Quản lý context trong multi-turn conversations"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict] = []
        self.named_entities: Dict[str, str] = {}  # Store extracted entities
        self.context_window_size = 5  # Số lượt trò chuyện để nhớ
        self.created_at = datetime.now()
    
    def add_turn(self, user_query: str, system_response: Dict[str, Any]):
        """Lưu một lượt hội thoại"""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "system_response": system_response,
            "resolved_entities": {}
        }
        self.conversation_history.append(turn)
    
    def resolve_coreferences(self, query: str) -> str:
        """
        Giải quyết các coreferences (đại từ) trong query
        
        Ví dụ: "HBL account có bao nhiêu hợp đồng?" -> Store: HBL account
        Tiếp theo: "Hợp đồng của nó tháng 5 thế nào?" -> Resolve: "Hợp đồng của HBL account tháng 5 thế nào?"
        """
        resolved_query = query
        
        # Coreference patterns
        pronouns = {
            r'\bnó\b': None,  # it
            r'\bnhững cái\b': None,  # those/these
            r'\bđó\b': None,  # that
            r'\bnhử\b': None,  # those
        }
        
        # Tìm entity cuối cùng được mention
        last_entity = self._get_last_entity()
        
        if last_entity:
            # Replace pronouns với entity
            for pronoun_pattern, _ in pronouns.items():
                resolved_query = re.sub(
                    pronoun_pattern,
                    last_entity,
                    resolved_query,
                    flags=re.IGNORECASE
                )
        
        return resolved_query
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Trích xuất entities từ query"""
        entities = {
            "companies": [],
            "dates": [],
            "numbers": [],
            "keywords": []
        }
        
        # Company names (pattern: words before "account", "công ty", etc.)
        company_pattern = r'(\w+)\s+(?:account|công ty|công|account)'
        for match in re.finditer(company_pattern, query, re.IGNORECASE):
            entities["companies"].append(match.group(1))
        
        # Dates (pattern: month/year or specific dates)
        date_pattern = r'(tháng\s+\d+|ngày\s+\d+|năm\s+\d+)'
        for match in re.finditer(date_pattern, query, re.IGNORECASE):
            entities["dates"].append(match.group(1))
        
        # Numbers
        number_pattern = r'\d+(?:\.\d+)?'
        for match in re.finditer(number_pattern, query):
            entities["numbers"].append(match.group())
        
        # Store first/main entity
        if entities["companies"]:
            self.named_entities["main_entity"] = entities["companies"][0]
        
        return entities
    
    def validate_logic(self, query: str, results: List[Dict], sql: str) -> Dict[str, Any]:
        """
        Kiểm tra tính logic của results so với query
        
        Phát hiện hallucination: result không match với SQL hoặc query intent
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "confidence_score": 1.0
        }
        
        # Check 1: Results count
        if len(results) == 0 and "danh sách" in query.lower():
            validation["issues"].append("Expected results but got empty")
            validation["confidence_score"] -= 0.2
        
        # Check 2: Column presence
        if results and "SELECT" in sql.upper():
            sql_columns = self._extract_sql_columns(sql)
            result_columns = set(results[0].keys()) if results else set()
            
            if not result_columns:
                validation["issues"].append("Results missing expected columns")
                validation["confidence_score"] -= 0.3
        
        # Check 3: Data type sanity
        for row in results[:3]:  # Check first 3 rows
            for key, value in row.items():
                if not self._is_sane_value(key, value):
                    validation["issues"].append(f"Suspicious value in {key}: {value}")
                    validation["confidence_score"] -= 0.1
        
        validation["is_valid"] = validation["confidence_score"] >= 0.7
        return validation
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt context hiện tại"""
        recent_turns = self.conversation_history[-self.context_window_size:]
        
        return {
            "session_id": self.session_id,
            "turn_count": len(self.conversation_history),
            "recent_turns": len(recent_turns),
            "named_entities": self.named_entities,
            "session_age_seconds": (datetime.now() - self.created_at).total_seconds(),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def clear_old_context(self, max_age_hours: int = 24):
        """Xóa context cũ"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        self.conversation_history = [
            turn for turn in self.conversation_history
            if datetime.fromisoformat(turn["timestamp"]) > cutoff_time
        ]
    
    # Private helpers
    def _get_last_entity(self) -> Optional[str]:
        """Lấy entity được mention cuối cùng"""
        for turn in reversed(self.conversation_history):
            entities = self.extract_entities(turn["user_query"])
            if entities["companies"]:
                return entities["companies"][0]
        return None
    
    def _extract_sql_columns(self, sql: str) -> List[str]:
        """Extract column names từ SELECT statement"""
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE)
        if not select_match:
            return []
        
        columns_str = select_match.group(1)
        if columns_str == "*":
            return ["*"]
        
        return [col.strip() for col in columns_str.split(",")]
    
    def validate_schema_usage(self, sql: str) -> Dict[str, Any]:
        """
        Kiểm tra xem SQL có sử dụng schema hợp lệ không
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "used_tables": [],
            "used_columns": []
        }
        
        # Extract tables from SQL
        table_pattern = r'\bFROM\s+(\w+)|JOIN\s+(\w+)'
        tables = []
        for match in re.finditer(table_pattern, sql, re.IGNORECASE):
            table = match.group(1) or match.group(2)
            if table:
                tables.append(table.lower())
        
        validation["used_tables"] = tables
        
        # TODO: Check against actual schema metadata
        # For now, assume common tables are valid
        valid_tables = ["hbl_account", "sys_choice_options", "sys_relation_metadata"]
        
        for table in tables:
            if table not in [t.lower() for t in valid_tables]:
                validation["issues"].append(f"Table '{table}' may not exist in schema")
                validation["is_valid"] = False
        
        return validation
        """Check nếu giá trị hợp lý cho column type"""
        if value is None:
            return True  # NULL is always valid
        
        value_str = str(value).lower()
        
        # Check for common hallucinations
        if any(hallucination in value_str for hallucination in [
            "i don't know",
            "không biết",
            "hallucinated",
            "error",
            "undefined"
        ]):
            return False
        
        # Date columns should look like dates
        if "date" in column_name.lower() or "time" in column_name.lower():
            if not any(c.isdigit() for c in value_str):
                return False
        
        return True


# Global session manager
_session_managers: Dict[str, ContextMonitor] = {}

def get_context_monitor(session_id: str) -> ContextMonitor:
    """Get hoặc create ContextMonitor cho session"""
    if session_id not in _session_managers:
        _session_managers[session_id] = ContextMonitor(session_id)
    return _session_managers[session_id]

def cleanup_old_sessions(max_age_hours: int = 24):
    """Cleanup old sessions"""
    current_time = datetime.now()
    to_delete = []
    
    for session_id, monitor in _session_managers.items():
        age = (current_time - monitor.created_at).total_seconds() / 3600
        if age > max_age_hours:
            to_delete.append(session_id)
    
    for session_id in to_delete:
        del _session_managers[session_id]

if __name__ == "__main__":
    # Test
    import json
    
    monitor = get_context_monitor("test_session_001")
    
    # Turn 1
    query1 = "HBL account có bao nhiêu hợp đồng?"
    monitor.add_turn(query1, {"status": "success", "count": 5})
    
    # Turn 2 (with coreference)
    query2 = "Hợp đồng của nó tháng 5 thế nào?"
    resolved = monitor.resolve_coreferences(query2)
    print(f"Original: {query2}")
    print(f"Resolved: {resolved}")
    
    # Context
    print("\nContext Summary:")
    print(json.dumps(monitor.get_context_summary(), indent=2, ensure_ascii=False))
