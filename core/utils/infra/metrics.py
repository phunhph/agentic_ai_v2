from __future__ import annotations

import time
from typing import Any, Dict

from .db import get_connection
from .json_utils import json_dumps


def log_metric(name: str, value: float, labels: Dict[str, Any] | None = None) -> None:
    labels = labels or {}
    timestamp = int(time.time())
    query = (
        "INSERT INTO audit_zone.api_metrics (metric_name, metric_value, metric_labels, created_at) "
        "VALUES (%s, %s, %s, to_timestamp(%s))"
    )
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, [name, value, json_dumps(labels), timestamp])
