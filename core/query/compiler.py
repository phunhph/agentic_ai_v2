from __future__ import annotations

from .catalog import SchemaCatalog
from .query_plan import QueryPlan


class QueryCompiler:
    def __init__(self, catalog: SchemaCatalog) -> None:
        self.catalog = catalog

    def compile(self, plan: QueryPlan) -> str:
        self._validate_plan(plan)
        aliases = self._aliases(plan)
        select_sql = self._render_select(plan, aliases)
        from_sql = f"FROM {plan.base_table} {aliases[plan.base_table]}"
        join_sql = self._render_joins(plan, aliases)
        where_sql = self._render_filters(plan, aliases)
        limit = max(1, min(plan.limit, 200))
        return " ".join(
            part
            for part in [
                f"SELECT {select_sql}",
                from_sql,
                join_sql,
                where_sql,
                f"LIMIT {limit}",
            ]
            if part
        )

    def _validate_plan(self, plan: QueryPlan) -> None:
        if self.catalog.get_relation(plan.base_table) is None:
            raise ValueError(f"Unknown base table: {plan.base_table}")
        for column_ref in plan.select:
            self._validate_column_ref(column_ref)
        for item in plan.filters:
            self._validate_column_ref(item.column)
        for join in plan.joins:
            self._validate_column_ref(f"{join.left_table}.{join.left_column}")
            self._validate_column_ref(f"{join.right_table}.{join.right_column}")

    def _validate_column_ref(self, column_ref: str) -> None:
        table_name, column_name = self._split_ref(column_ref)
        relation = self.catalog.get_relation(table_name)
        if relation is None:
            raise ValueError(f"Unknown table: {table_name}")
        if not relation.has_column(column_name):
            raise ValueError(f"Unknown column: {column_ref}")

    def _aliases(self, plan: QueryPlan) -> dict[str, str]:
        tables = [plan.base_table]
        for join in plan.joins:
            for table in [join.left_table, join.right_table]:
                if table not in tables:
                    tables.append(table)
        return {table: f"t{index}" for index, table in enumerate(tables)}

    def _render_select(self, plan: QueryPlan, aliases: dict[str, str]) -> str:
        if not plan.select:
            return f"{aliases[plan.base_table]}.*"
        rendered = []
        for column_ref in plan.select:
            table, column = self._split_ref(column_ref)
            rendered.append(f"{aliases[table]}.{column} AS {table.split('.')[-1]}__{column}")
        return ", ".join(rendered)

    def _render_joins(self, plan: QueryPlan, aliases: dict[str, str]) -> str:
        rendered = []
        joined = {plan.base_table}
        for join in plan.joins:
            if join.left_table in joined and join.right_table not in joined:
                target = join.right_table
                condition = (
                    f"{aliases[join.left_table]}.{join.left_column} = "
                    f"{aliases[join.right_table]}.{join.right_column}"
                )
            elif join.right_table in joined and join.left_table not in joined:
                target = join.left_table
                condition = (
                    f"{aliases[join.left_table]}.{join.left_column} = "
                    f"{aliases[join.right_table]}.{join.right_column}"
                )
            else:
                target = join.left_table
                condition = (
                    f"{aliases[join.left_table]}.{join.left_column} = "
                    f"{aliases[join.right_table]}.{join.right_column}"
                )
            rendered.append(f"LEFT JOIN {target} {aliases[target]} ON {condition}")
            joined.add(target)
        return " ".join(rendered)

    def _render_filters(self, plan: QueryPlan, aliases: dict[str, str]) -> str:
        if not plan.filters:
            return ""
        rendered = []
        for item in plan.filters:
            table, column = self._split_ref(item.column)
            left = f"{aliases[table]}.{column}"
            if item.op == "ilike":
                rendered.append(f"{left} ILIKE {self._quote('%' + str(item.value) + '%')}")
            elif item.op == "in":
                values = item.value if isinstance(item.value, list) else [item.value]
                rendered.append(f"{left} IN ({', '.join(self._quote(value) for value in values)})")
            else:
                rendered.append(f"{left} = {self._quote(item.value)}")
        return "WHERE " + " AND ".join(rendered)

    def _split_ref(self, column_ref: str) -> tuple[str, str]:
        parts = column_ref.split(".")
        if len(parts) < 3:
            raise ValueError(f"Column reference must include schema.table.column: {column_ref}")
        return ".".join(parts[:-1]), parts[-1]

    def _quote(self, value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, (int, float)):
            return str(value)
        return "'" + str(value).replace("'", "''") + "'"
