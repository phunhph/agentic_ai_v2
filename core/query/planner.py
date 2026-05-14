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
