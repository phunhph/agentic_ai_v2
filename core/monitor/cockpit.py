from core.utils.infra.db import db_manager

class ObservabilityCockpit:
    """
    Phase 21: Observability Cockpit & Trace Visualization.
    API và logic để hiển thị Dashboard giám sát.
    """
    
    def get_system_metrics(self):
        """Lấy các chỉ số hiệu năng hệ thống."""
        try:
            with db_manager.get_cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_requests,
                        AVG(cost_usd) as avg_cost,
                        SUM(token_count) as total_tokens
                    FROM audit_zone.agent_logs
                """)
                return cur.fetchone()
        except:
            return (0, 0, 0)

    def get_execution_trace(self, session_id: str):
        """Lấy toàn bộ vết thực thi của một session."""
        try:
            with db_manager.get_cursor() as cur:
                cur.execute("""
                    SELECT node_name, input_payload, output_payload, createdon 
                    FROM audit_zone.agent_logs 
                    WHERE session_id = %s 
                    ORDER BY createdon ASC
                """, (session_id,))
                return cur.fetchall()
        except:
            return []
