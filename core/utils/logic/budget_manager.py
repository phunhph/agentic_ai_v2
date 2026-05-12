import json
from core.utils.infra.db import db_manager

class BudgetManager:
    """
    Phase 19: Model Orchestration & Cost-Aware Routing.
    Quản lý ngân sách Token và chi phí.
    """
    
    def __init__(self, daily_limit_usd: float = 5.0):
        self.daily_limit = daily_limit_usd

    def check_budget(self) -> bool:
        """Kiểm tra xem đã vượt ngưỡng chi phí trong ngày chưa."""
        try:
            with db_manager.get_cursor() as cur:
                cur.execute("""
                    SELECT SUM(cost_usd) FROM audit_zone.agent_logs 
                    WHERE createdon >= CURRENT_DATE
                """)
                total_cost = cur.fetchone()[0] or 0.0
                return total_cost < self.daily_limit
        except:
            return True # Fail safe

    def get_optimal_model(self, complexity: str) -> str:
        """Chọn model dựa trên độ phức tạp và ngân sách."""
        if not self.check_budget():
            return "gemini/gemini-1.5-flash" # Chuyển sang model rẻ nhất
            
        if complexity == "HIGH":
            return "gemini/gemini-1.5-pro"
        return "gemini/gemini-1.5-flash"
