"""
Phase 10: Context Monitor & Coreference Resolution
Manages multi-turn conversations, context linking, and hallucination detection
"""
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta


from core.utils.infra.db import db_manager
import json

class ContextMonitor:
    """Quản lý context trong multi-turn conversations (Persistent via DB)"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.named_entities: Dict[str, str] = {}  # Store extracted entities
        self.context_window_size = 5  # Số lượt trò chuyện để nhớ
        self.created_at = datetime.now()
    
    def _fetch_history(self) -> List[Dict[str, Any]]:
        """Lấy lịch sử hội thoại từ database"""
        history = []
        try:
            with db_manager.get_cursor() as cur:
                # Lấy các lượt chat chính (Ingest node thường chứa query gốc)
                cur.execute("""
                    SELECT input_payload, output_payload, createdon 
                    FROM audit_zone.agent_logs 
                    WHERE session_id = %s AND node_name = 'LangGraph_Orchestrator'
                    ORDER BY createdon DESC 
                    LIMIT %s
                """, (self.session_id, self.context_window_size))
                
                rows = cur.fetchall()
                for input_p, output_p, createdon in reversed(rows):
                    history.append({
                        "timestamp": createdon.isoformat(),
                        "user_query": input_p.get("query", "") if isinstance(input_p, dict) else json.loads(input_p).get("query", ""),
                        "system_response": output_p if isinstance(output_p, dict) else json.loads(output_p)
                    })
        except Exception as e:
            print(f"Error fetching history: {e}")
        return history

    def add_turn(self, user_query: str, system_response: Dict[str, Any]):
        """
        Lưu một lượt hội thoại. 
        Lưu ý: App.py đã gọi db_manager.log_agent_interaction cho Orchestrator, 
        nên không cần insert thủ công ở đây nếu session_id khớp.
        """
        pass
    
    def resolve_coreferences(self, query: str) -> str:
        """Giải quyết các đại từ (nó, đó,...) dựa trên lịch sử hội thoại"""
        resolved_query = query
        
        # Coreference patterns
        pronouns = [r'\bnó\b', r'\bđó\b', r'\bchúng\b', r'\bcái đó\b']
        
        history = self._fetch_history()
        last_entity = self._get_last_entity(history)
        
        if last_entity:
            for pronoun_pattern in pronouns:
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
        
        # Simple extraction logic (improved)
        company_pattern = r'(\w+)\s+(?:account|công ty|đối tác)'
        for match in re.finditer(company_pattern, query, re.IGNORECASE):
            entities["companies"].append(match.group(1))
        
        date_pattern = r'(tháng\s+\d+|ngày\s+\d+|năm\s+\d+)'
        for match in re.finditer(date_pattern, query, re.IGNORECASE):
            entities["dates"].append(match.group(1))
            
        if entities["companies"]:
            self.named_entities["main_entity"] = entities["companies"][0]
        
        return entities
    
    def validate_logic(self, query: str, results: List[Dict], sql: str) -> Dict[str, Any]:
        """Kiểm tra logic kết quả (Hallucination Guard)"""
        validation = {
            "is_valid": True,
            "issues": [],
            "confidence_score": 1.0,
            "hallucination_detected": False
        }
        
        if not results:
            if any(k in query.lower() for k in ["liệt kê", "danh sách", "show", "list"]):
                validation["issues"].append("⚠️ Kết quả rỗng mặc dù người dùng yêu cầu liệt kê.")
                validation["confidence_score"] -= 0.3
        
        # Check for suspicious values in results
        for row in results[:5]: 
            for key, value in row.items():
                if not self._is_sane_value(key, value):
                    validation["issues"].append(f"🚫 Suspicious value in {key}: {value}")
                    validation["hallucination_detected"] = True
                    validation["confidence_score"] -= 0.2
        
        validation["is_valid"] = validation["confidence_score"] >= 0.7
        return validation
    
    def _get_last_entity(self, history: List[Dict]) -> Optional[str]:
        """Lấy entity được mention cuối cùng trong lịch sử"""
        for turn in reversed(history):
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
    def _is_sane_value(self, column_name: str, value: Any) -> bool:
        """Check nếu giá trị hợp lý cho column type"""
        if value is None:
            return True  # NULL is always valid
        
        value_str = str(value).lower()
        
        # Check for common hallucinations
        if any(hallucination in value_str for hallucination in [
            "i don't know", "không biết", "hallucinated", "error", "undefined"
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
