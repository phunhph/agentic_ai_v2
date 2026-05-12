from core.tools.db.sql_executor import execute_business_query
from core.tools.db.schema_tools import get_db_schema

def db_query_tool(sql_command: str):
    """Tool để thực thi truy vấn SQL (Chỉ SELECT)"""
    return execute_business_query(sql_command)

def db_schema_tool():
    """Tool để xem cấu trúc và quan hệ bảng"""
    return get_db_schema()
