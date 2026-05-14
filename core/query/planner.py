from __future__ import annotations

import re

from .catalog import SchemaCatalog
from .join_graph import JoinGraph
from .query_plan import QueryFilter, QueryJoin, QueryPlan


class DynamicQueryPlanner:
    """Builds small validated query plans from task intent and catalog metadata."""

    def __init__(self, catalog: SchemaCatalog) -> None:
        self.catalog = catalog
        self.join_graph = JoinGraph(catalog)

    def build_plan(self, prompt: str, task_description: str) -> QueryPlan | None:
        prompt_lower = prompt.lower()
        task_lower = task_description.lower()
        wants_contacts = any(token in f"{prompt_lower} {task_lower}" for token in ["contact", "liên hệ"])
        wants_accounts = any(token in f"{prompt_lower} {task_lower}" for token in ["account", "khách hàng", "customer"])

        account_table = "business_zone.v_hbl_accounts"
        contact_table = "business_zone.v_hbl_contacts"
        account_name = self._extract_named_entity(prompt)

        if wants_contacts and wants_accounts:
            join_plan = self.build_join_plan(prompt)
            if join_plan is not None:
                return join_plan

        if wants_contacts and self.catalog.get_relation(contact_table):
            filters = []
            if account_name and self.catalog.find_column(contact_table, ["account_name"]):
                filters.append(
                    QueryFilter(
                        column=f"{contact_table}.account_name",
                        op="ilike",
                        value=account_name,
                    )
                )
            select = self._select_columns(
                contact_table,
                [
                    "contact_name",
                    "contact_email",
                    "contact_phone",
                    "contact_title",
                    "account_name",
                    "account_id",
                ],
            )
            return QueryPlan(
                strategy="single_table",
                base_table=contact_table,
                select=select,
                filters=filters,
                limit=50,
            )

        if wants_accounts and self.catalog.get_relation(account_table):
            filters = []
            name_column = self.catalog.find_column(account_table, ["account_name", "name"])
            if account_name and name_column:
                filters.append(
                    QueryFilter(
                        column=f"{account_table}.{name_column}",
                        op="ilike",
                        value=account_name,
                    )
                )
            select = self._select_columns(
                account_table,
                ["account_id", "account_name", "name", "industry", "revenue", "region", "business_description"],
            )
            return QueryPlan(
                strategy="single_table",
                base_table=account_table,
                select=select,
                filters=filters,
                limit=50,
            )

        return None

    def build_join_plan(self, prompt: str) -> QueryPlan | None:
        account_table = "business_zone.v_hbl_accounts"
        contact_table = "business_zone.v_hbl_contacts"
        if not self.catalog.get_relation(account_table) or not self.catalog.get_relation(contact_table):
            return None
        path = self.join_graph.find_path(account_table, contact_table)
        if not path:
            return None
        account_name = self._extract_named_entity(prompt)
        joins = [
            QueryJoin(
                left_table=edge.left_table,
                left_column=edge.left_column,
                right_table=edge.right_table,
                right_column=edge.right_column,
            )
            for edge in path
        ]
        name_column = self.catalog.find_column(account_table, ["account_name", "name"])
        filters = []
        if account_name and name_column:
            filters.append(QueryFilter(column=f"{account_table}.{name_column}", op="ilike", value=account_name))
        return QueryPlan(
            strategy="join",
            base_table=account_table,
            select=[
                *self._select_columns(account_table, ["account_id", "account_name", "industry", "revenue", "region"]),
                *self._select_columns(contact_table, ["contact_name", "contact_email", "contact_phone", "contact_title"]),
            ],
            filters=filters,
            joins=joins,
            limit=50,
        )

    def repair_plan(self, plan: QueryPlan, error_message: str) -> QueryPlan | None:
        join_repair = self._repair_missing_join(plan, error_message)
        if join_repair is not None:
            return join_repair

        missing_column = self._extract_missing_column(error_message)
        if not missing_column:
            return None

        replacements = {
            "account_name": ["account_name", "name"],
            "name": ["name", "account_name", "contact_name"],
            "email": ["contact_email", "email"],
            "phone": ["contact_phone", "phone"],
            "title": ["contact_title", "title"],
            "revenue": ["revenue", "account_revenue", "annual_revenue"],
        }
        candidates = replacements.get(missing_column, [])
        if not candidates:
            return None

        updates: dict[str, str] = {}
        involved_tables = [plan.base_table]
        for join in plan.joins:
            involved_tables.extend([join.left_table, join.right_table])

        for table_name in dict.fromkeys(involved_tables):
            replacement = self.catalog.find_column(table_name, candidates)
            if replacement:
                updates[f"{table_name}.{missing_column}"] = f"{table_name}.{replacement}"

        if not updates:
            return None

        repaired = plan.model_copy(deep=True)
        repaired.select = [updates.get(column, column) for column in repaired.select]
        for item in repaired.filters:
            item.column = updates.get(item.column, item.column)
        return repaired

    def _repair_missing_join(self, plan: QueryPlan, error_message: str) -> QueryPlan | None:
        missing_table = self._extract_missing_table(error_message)
        if not missing_table:
            return None

        full_table = self._resolve_table_name(missing_table)
        if full_table is None or full_table == plan.base_table:
            return None

        path = self.join_graph.find_path(plan.base_table, full_table)
        if not path:
            return None

        repaired = plan.model_copy(deep=True)
        existing = {
            (join.left_table, join.left_column, join.right_table, join.right_column)
            for join in repaired.joins
        }
        for edge in path:
            key = (edge.left_table, edge.left_column, edge.right_table, edge.right_column)
            if key not in existing:
                repaired.joins.append(
                    QueryJoin(
                        left_table=edge.left_table,
                        left_column=edge.left_column,
                        right_table=edge.right_table,
                        right_column=edge.right_column,
                    )
                )
        repaired.strategy = "join"
        return repaired

    def _select_columns(self, table_name: str, candidates: list[str]) -> list[str]:
        relation = self.catalog.get_relation(table_name)
        if relation is None:
            return []
        return [f"{table_name}.{column}" for column in candidates if relation.has_column(column)]

    def _extract_named_entity(self, prompt: str) -> str | None:
        patterns = [
            r"account\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
            r"tài khoản\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
            r"khách hàng\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
        ]
        for pattern in patterns:
            match = re.search(pattern, prompt)
            if match:
                value = match.group(1).strip(" .,'\"")
                value = re.split(r",|\bcùng\b|\bvà\b|\bwith\b|\band\b", value, maxsplit=1, flags=re.IGNORECASE)[0]
                return value.strip(" .,'\"") or None
        return None

    def _extract_missing_column(self, error_message: str) -> str | None:
        patterns = [
            r'column "?([A-Za-z_][A-Za-z0-9_]*)"? does not exist',
            r'column "?[A-Za-z0-9_]+"?\."?([A-Za-z_][A-Za-z0-9_]*)"? does not exist',
        ]
        for pattern in patterns:
            match = re.search(pattern, error_message, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_missing_table(self, error_message: str) -> str | None:
        patterns = [
            r'missing FROM-clause entry for table "?([A-Za-z_][A-Za-z0-9_]*)"?',
            r'relation "?([A-Za-z_][A-Za-z0-9_.]*)"? does not exist',
        ]
        for pattern in patterns:
            match = re.search(pattern, error_message, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _resolve_table_name(self, table_name: str) -> str | None:
        if self.catalog.get_relation(table_name):
            return table_name
        suffix = f".{table_name}"
        for relation_name in self.catalog.relations():
            if relation_name.endswith(suffix):
                return relation_name
        return None
