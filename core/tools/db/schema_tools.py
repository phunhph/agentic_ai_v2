from core.utils.infra.db import db_manager
import time
import json

# Schema cache with TTL
_schema_cache = None
_cache_time = 0
_CACHE_TTL = 300  # 5 minutes

def _get_full_schema() -> dict:
    """Lấy toàn bộ schema metadata từ database"""
    try:
        with db_manager.get_cursor(use_agent=True) as cur:
            # 1. Lấy danh sách các bảng trong public schema
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            schema_info = {}
            for table in tables:
                # 2. Lấy danh sách cột cho mỗi bảng
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = %s
                """, (table,))
                columns = cur.fetchall()
                
                schema_info[table] = {
                    "columns": [
                        {"name": col[0], "type": col[1], "nullable": col[2]} 
                        for col in columns
                    ]
                }
                
            # 3. Lấy thông tin Foreign Keys
            cur.execute("""
                SELECT
                    kcu.table_name AS from_table,
                    kcu.column_name AS from_column,
                    rel_kcu.table_name AS to_table,
                    rel_kcu.column_name AS to_column
                FROM information_schema.table_constraints tco
                JOIN information_schema.key_column_usage kcu
                  ON tco.constraint_name = kcu.constraint_name
                  AND tco.table_schema = kcu.table_schema
                JOIN information_schema.referential_constraints rco
                  ON tco.constraint_name = rco.constraint_name
                JOIN information_schema.key_column_usage rel_kcu
                  ON rco.unique_constraint_name = rel_kcu.constraint_name
                  AND rco.unique_constraint_schema = rel_kcu.table_schema
                WHERE tco.constraint_type = 'FOREIGN KEY'
            """)
            relations = cur.fetchall()
            
            relationships = []
            for rel in relations:
                relationships.append({
                    "from_table": rel[0],
                    "from_column": rel[1],
                    "to_table": rel[2],
                    "to_column": rel[3]
                })
                
            return {
                "status": "success",
                "tables": schema_info,
                "relationships": relationships
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Schema Read Error: {str(e)}"
        }

def get_db_schema(use_cache=True) -> dict:
    """Đọc thông tin schema metadata (với caching)"""
    global _schema_cache, _cache_time
    
    # Kiểm tra cache
    if use_cache and _schema_cache and (time.time() - _cache_time) < _CACHE_TTL:
        return _schema_cache
    
    # Nếu cache expire, lấy lại từ DB
    schema = _get_full_schema()
    _schema_cache = schema
    _cache_time = time.time()
    return schema

def get_relevant_schema(required_tables: list = None) -> dict:
    """Lấy chỉ những bảng + relationships liên quan (để giảm token)"""
    full_schema = get_db_schema()
    
    if full_schema.get("status") == "error":
        return full_schema
    
    if required_tables is None or not required_tables:
        return full_schema
    
    # Lọc chỉ những bảng cần thiết
    filtered_tables = {}
    for table in required_tables:
        if table in full_schema.get("tables", {}):
            filtered_tables[table] = full_schema["tables"][table]
    
    # Lọc relationships chỉ liên quan đến bảng cần thiết
    filtered_relations = []
    for rel in full_schema.get("relationships", []):
        if rel["from_table"] in required_tables or rel["to_table"] in required_tables:
            filtered_relations.append(rel)
    
    return {
        "status": "success",
        "tables": filtered_tables,
        "relationships": filtered_relations
    }

if __name__ == "__main__":
    schema = get_db_schema()
    print(json.dumps(schema))
