from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from core.utils.infra.db import query

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    name: str
    data_type: str = "text"
    ordinal_position: int = 0


@dataclass
class RelationInfo:
    name: str
    schema_name: str
    relation_type: str
    columns: dict[str, ColumnInfo] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.schema_name}.{self.name}"

    def has_column(self, column: str) -> bool:
        return column in self.columns

    def compact_card(self, max_columns: int = 8) -> dict[str, Any]:
        key_columns = [
            column
            for column in self.columns
            if column.endswith("_id") or column in {"id", "tenant_id", "account_name", "name"}
        ]
        remaining = [column for column in self.columns if column not in key_columns]
        selected = (key_columns + remaining)[:max_columns]
        return {
            "name": self.full_name,
            "type": self.relation_type,
            "columns": selected,
            "column_count": len(self.columns),
        }


@dataclass
class JoinEdge:
    left_table: str
    left_column: str
    right_table: str
    right_column: str

    def as_text(self) -> str:
        return f"{self.left_table}.{self.left_column} -> {self.right_table}.{self.right_column}"


class SchemaCatalog:
    """Small metadata catalog used to keep prompt context compact.

    The catalog reads Postgres metadata when a database is available, and falls
    back to the project semantic views so local/dev flows still work.
    """

    FALLBACK_RELATIONS: dict[str, list[str]] = {
        "business_zone.v_hbl_accounts": [
            "tenant_id",
            "account_id",
            "account_name",
            "name",
            "industry",
            "revenue",
            "region",
            "business_description",
            "created_at",
        ],
        "business_zone.v_hbl_contacts": [
            "tenant_id",
            "contact_id",
            "account_id",
            "contact_name",
            "contact_email",
            "contact_phone",
            "contact_title",
            "contact_region",
            "contact_last_activity",
            "contact_notes",
            "account_name",
            "account_industry",
            "account_revenue",
        ],
    }

    FALLBACK_JOINS: list[JoinEdge] = [
        JoinEdge(
            left_table="business_zone.v_hbl_contacts",
            left_column="account_id",
            right_table="business_zone.v_hbl_accounts",
            right_column="account_id",
        )
    ]

    def __init__(self) -> None:
        self._relations: dict[str, RelationInfo] | None = None
        self._joins: list[JoinEdge] | None = None

    def relations(self) -> dict[str, RelationInfo]:
        if self._relations is None:
            self._relations = self._load_relations()
        return self._relations

    def joins(self) -> list[JoinEdge]:
        if self._joins is None:
            self._joins = self._load_joins()
        return self._joins

    def get_relation(self, full_name: str) -> RelationInfo | None:
        return self.relations().get(full_name)

    def search_relations(self, prompt: str, limit: int = 5) -> list[RelationInfo]:
        prompt_lower = prompt.lower()
        scored: list[tuple[int, RelationInfo]] = []
        for relation in self.relations().values():
            haystack = " ".join([relation.full_name, *relation.columns.keys()]).lower()
            score = sum(1 for token in self._tokens(prompt_lower) if token in haystack)
            if score:
                scored.append((score, relation))
        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [relation for _, relation in scored[:limit]]
        if selected:
            return selected
        return list(self.relations().values())[:limit]

    def relation_cards(self, prompt: str, limit: int = 5) -> list[dict[str, Any]]:
        return [relation.compact_card() for relation in self.search_relations(prompt, limit=limit)]

    def find_column(self, relation_name: str, candidates: list[str]) -> str | None:
        relation = self.get_relation(relation_name)
        if relation is None:
            return None
        for candidate in candidates:
            if candidate in relation.columns:
                return candidate
        return None

    def _load_relations(self) -> dict[str, RelationInfo]:
        try:
            rows = query(
                """
                SELECT table_schema, table_name, column_name, data_type, ordinal_position
                FROM information_schema.columns
                WHERE table_schema IN ('business_zone', 'knowledge_zone', 'audit_zone')
                ORDER BY table_schema, table_name, ordinal_position
                """
            )
        except Exception as exc:
            logger.warning("Falling back to static schema catalog: %s", exc)
            return self._fallback_relations()

        relations: dict[str, RelationInfo] = {}
        for row in rows:
            full_name = f"{row['table_schema']}.{row['table_name']}"
            relation = relations.setdefault(
                full_name,
                RelationInfo(
                    name=row["table_name"],
                    schema_name=row["table_schema"],
                    relation_type="relation",
                ),
            )
            relation.columns[row["column_name"]] = ColumnInfo(
                name=row["column_name"],
                data_type=row.get("data_type", "text"),
                ordinal_position=int(row.get("ordinal_position") or 0),
            )
        return relations or self._fallback_relations()

    def _load_joins(self) -> list[JoinEdge]:
        try:
            rows = query(
                """
                SELECT
                    tc.table_schema || '.' || tc.table_name AS left_table,
                    kcu.column_name AS left_column,
                    ccu.table_schema || '.' || ccu.table_name AS right_table,
                    ccu.column_name AS right_column
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                """
            )
        except Exception as exc:
            logger.warning("Falling back to static join graph: %s", exc)
            return list(self.FALLBACK_JOINS)

        joins = [
            JoinEdge(
                left_table=row["left_table"],
                left_column=row["left_column"],
                right_table=row["right_table"],
                right_column=row["right_column"],
            )
            for row in rows
        ]
        return joins or list(self.FALLBACK_JOINS)

    def _fallback_relations(self) -> dict[str, RelationInfo]:
        relations: dict[str, RelationInfo] = {}
        for full_name, columns in self.FALLBACK_RELATIONS.items():
            schema_name, name = full_name.split(".", 1)
            relation = RelationInfo(name=name, schema_name=schema_name, relation_type="view")
            relation.columns = {
                column: ColumnInfo(name=column, ordinal_position=index)
                for index, column in enumerate(columns, start=1)
            }
            relations[full_name] = relation
        return relations

    def _tokens(self, text: str) -> list[str]:
        return [token for token in text.replace("_", " ").split() if len(token) >= 3]
