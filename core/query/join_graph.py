from __future__ import annotations

from collections import deque

from .catalog import JoinEdge, SchemaCatalog


class JoinGraph:
    def __init__(self, catalog: SchemaCatalog) -> None:
        self.catalog = catalog

    def find_path(self, start_table: str, end_table: str) -> list[JoinEdge]:
        if start_table == end_table:
            return []

        adjacency: dict[str, list[JoinEdge]] = {}
        for edge in self.catalog.joins():
            adjacency.setdefault(edge.left_table, []).append(edge)
            adjacency.setdefault(edge.right_table, []).append(
                JoinEdge(
                    left_table=edge.right_table,
                    left_column=edge.right_column,
                    right_table=edge.left_table,
                    right_column=edge.left_column,
                )
            )

        queue: deque[tuple[str, list[JoinEdge]]] = deque([(start_table, [])])
        visited = {start_table}
        while queue:
            table, path = queue.popleft()
            for edge in adjacency.get(table, []):
                if edge.right_table in visited:
                    continue
                next_path = [*path, edge]
                if edge.right_table == end_table:
                    return next_path
                visited.add(edge.right_table)
                queue.append((edge.right_table, next_path))
        return []
