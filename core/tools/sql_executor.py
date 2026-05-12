from core.utils.db import db_manager
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SQLInput(BaseModel):
    sql_command: str = Field(description="Valid SELECT SQL command")

FORBIDDEN_KEYWORDS = [
    "drop", "delete", "truncate", "update", "alter", 
    "create", "grant", "revoke", "insert", "into"
]

def execute_business_query(sql_command: str) -> Dict[str, Any]:
    """Thực thi câu lệnh SQL SELECT an toàn với agent_user thông qua db_manager"""
    query_lower = sql_command.lower().strip()

    # 1. Chỉ cho phép SELECT
    if not query_lower.startswith("select"):
        return {
            "status": "error",
            "message": "Security Error: Only SELECT queries are allowed."
        }

    # 2. Chặn từ khóa nguy hiểm
    if any(word in query_lower for word in FORBIDDEN_KEYWORDS):
        return {
            "status": "error",
            "message": "Security Error: Bạn không có quyền thực hiện các thao tác thay đổi dữ liệu."
        }

    try:
        # Sử dụng db_manager với use_agent=True để dùng tài khoản giới hạn
        with db_manager.get_cursor(use_agent=True) as cur:
            cur.execute(sql_command)
            
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "status": "success",
                    "results": results,
                    "row_count": len(results)
                }
            else:
                return {"status": "success", "results": [], "row_count": 0}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Database Error: {str(e)}"
        }

if __name__ == "__main__":
    # Test safe query
    print("Testing safe SELECT...")
    print(execute_business_query("SELECT * FROM hbl_account LIMIT 1"))
