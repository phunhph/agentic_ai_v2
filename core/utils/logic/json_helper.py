import json
from decimal import Decimal
from datetime import datetime, date

class AgenticJSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder để xử lý các kiểu dữ liệu đặc biệt từ PostgreSQL:
    - Decimal -> float
    - datetime/date -> ISO string
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(AgenticJSONEncoder, self).default(obj)

def json_dumps(obj, indent=None, ensure_ascii=False):
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii, cls=AgenticJSONEncoder)
