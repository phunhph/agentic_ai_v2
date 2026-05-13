from __future__ import annotations
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.utils.infra.db import get_connection

ACCOUNTS = [
    {
        "account_name": "Acme Corporation",
        "industry": "Manufacturing",
        "annual_revenue": 12500000,
        "region": "North America",
        "description": "Global manufacturer of industrial components.",
    },
    {
        "account_name": "Orion Labs",
        "industry": "Technology",
        "annual_revenue": 8900000,
        "region": "EMEA",
        "description": "AI-enabled enterprise software provider.",
    },
    {
        "account_name": "Summit Solutions",
        "industry": "Consulting",
        "annual_revenue": 4300000,
        "region": "APAC",
        "description": "Business process and analytics consulting.",
    },
    {
        "account_name": "Horizon Health",
        "industry": "Healthcare",
        "annual_revenue": 17800000,
        "region": "North America",
        "description": "Healthcare services provider with integrated care programs.",
    },
    {
        "account_name": "Velocity Ventures",
        "industry": "Finance",
        "annual_revenue": 21500000,
        "region": "EMEA",
        "description": "Venture capital and growth equity firm.",
    },
    {
        "account_name": "Atlas Retail",
        "industry": "Retail",
        "annual_revenue": 9800000,
        "region": "South America",
        "description": "Omnichannel retail chain focused on consumer electronics.",
    },
    {
        "account_name": "Redwood Banking",
        "industry": "Financial Services",
        "annual_revenue": 30200000,
        "region": "North America",
        "description": "Regional bank supporting small business lending.",
    },
    {
        "account_name": "Nimbus Energy",
        "industry": "Energy",
        "annual_revenue": 12700000,
        "region": "APAC",
        "description": "Renewable energy project developer.",
    },
    {
        "account_name": "Cascade Logistics",
        "industry": "Transportation",
        "annual_revenue": 6400000,
        "region": "Europe",
        "description": "Logistics and freight management services.",
    },
    {
        "account_name": "PolarTech",
        "industry": "Software",
        "annual_revenue": 5400000,
        "region": "North America",
        "description": "Cold chain and supply chain optimization software.",
    },
]

CONTACTS = [
    {
        "full_name": "Ava Reynolds",
        "email": "ava.reynolds@acme.com",
        "phone": "+1-202-555-0148",
        "title": "VP of Operations",
        "region": "North America",
        "last_activity": "2026-05-08",
        "notes": "Interested in improving supply chain visibility.",
        "account_name": "Acme Corporation",
    },
    {
        "full_name": "Ethan Cooper",
        "email": "ethan.cooper@acme.com",
        "phone": "+1-202-555-0185",
        "title": "Director of Engineering",
        "region": "North America",
        "last_activity": "2026-05-11",
        "notes": "Asked for product comparison and integration details.",
        "account_name": "Acme Corporation",
    },
    {
        "full_name": "Mia Johansson",
        "email": "mia.johansson@orionlabs.io",
        "phone": "+44-20-7946-0958",
        "title": "Head of Data Science",
        "region": "EMEA",
        "last_activity": "2026-05-12",
        "notes": "Looking for AI model explainability in dashboards.",
        "account_name": "Orion Labs",
    },
    {
        "full_name": "Luca Ferrari",
        "email": "luca.ferrari@orionlabs.io",
        "phone": "+44-20-7946-1620",
        "title": "VP of Product",
        "region": "EMEA",
        "last_activity": "2026-05-05",
        "notes": "Needs quarterly roadmap summary.",
        "account_name": "Orion Labs",
    },
    {
        "full_name": "Sofia Patel",
        "email": "sofia.patel@summitsolutions.com",
        "phone": "+91-80-555-0192",
        "title": "Principal Consultant",
        "region": "APAC",
        "last_activity": "2026-05-07",
        "notes": "Seeking analysis of client engagement trends.",
        "account_name": "Summit Solutions",
    },
    {
        "full_name": "Noah Kim",
        "email": "noah.kim@summitsolutions.com",
        "phone": "+91-80-555-0163",
        "title": "Client Success Lead",
        "region": "APAC",
        "last_activity": "2026-05-10",
        "notes": "Requested customer retention dashboard.",
        "account_name": "Summit Solutions",
    },
    {
        "full_name": "Olivia Grant",
        "email": "olivia.grant@horizonhealth.com",
        "phone": "+1-303-555-0123",
        "title": "Chief Medical Officer",
        "region": "North America",
        "last_activity": "2026-05-09",
        "notes": "Evaluating analytics for patient outcomes.",
        "account_name": "Horizon Health",
    },
    {
        "full_name": "Samuel Lee",
        "email": "samuel.lee@horizonhealth.com",
        "phone": "+1-303-555-0180",
        "title": "Head of Operations",
        "region": "North America",
        "last_activity": "2026-05-06",
        "notes": "Interested in operational cost reduction.",
        "account_name": "Horizon Health",
    },
    {
        "full_name": "Chloe Martin",
        "email": "chloe.martin@velocityventures.com",
        "phone": "+44-20-555-0140",
        "title": "Investment Director",
        "region": "EMEA",
        "last_activity": "2026-05-08",
        "notes": "Exploring portfolio performance analytics.",
        "account_name": "Velocity Ventures",
    },
    {
        "full_name": "Diego Silva",
        "email": "diego.silva@velocityventures.com",
        "phone": "+44-20-555-0194",
        "title": "Finance Partner",
        "region": "EMEA",
        "last_activity": "2026-05-10",
        "notes": "Requested high-level revenue forecast model.",
        "account_name": "Velocity Ventures",
    },
    {
        "full_name": "Emma Price",
        "email": "emma.price@atlasretail.com",
        "phone": "+55-11-5555-0193",
        "title": "Retail Operations Manager",
        "region": "South America",
        "last_activity": "2026-05-11",
        "notes": "Needs weekly sales performance reports.",
        "account_name": "Atlas Retail",
    },
    {
        "full_name": "Felipe Costa",
        "email": "felipe.costa@atlasretail.com",
        "phone": "+55-11-5555-0131",
        "title": "E-commerce Director",
        "region": "South America",
        "last_activity": "2026-05-12",
        "notes": "Interested in customer purchase patterns.",
        "account_name": "Atlas Retail",
    },
    {
        "full_name": "Grace Kim",
        "email": "grace.kim@redwoodbanking.com",
        "phone": "+1-415-555-0172",
        "title": "Credit Risk Officer",
        "region": "North America",
        "last_activity": "2026-05-05",
        "notes": "Asking for portfolio risk summaries.",
        "account_name": "Redwood Banking",
    },
    {
        "full_name": "Liam Johnson",
        "email": "liam.johnson@redwoodbanking.com",
        "phone": "+1-415-555-0135",
        "title": "Branch Manager",
        "region": "North America",
        "last_activity": "2026-05-09",
        "notes": "Wants branch-level performance data.",
        "account_name": "Redwood Banking",
    },
    {
        "full_name": "Nina Yamamoto",
        "email": "nina.yamamoto@nimbusenergy.com",
        "phone": "+81-3-5555-0111",
        "title": "Project Director",
        "region": "APAC",
        "last_activity": "2026-05-08",
        "notes": "Needs energy usage analytics.",
        "account_name": "Nimbus Energy",
    },
    {
        "full_name": "Owen Park",
        "email": "owen.park@nimbusenergy.com",
        "phone": "+81-3-5555-0177",
        "title": "Finance Lead",
        "region": "APAC",
        "last_activity": "2026-05-10",
        "notes": "Requested profit margin forecasts.",
        "account_name": "Nimbus Energy",
    },
    {
        "full_name": "Paula Becker",
        "email": "paula.becker@cascadelogistics.com",
        "phone": "+49-30-5555-0144",
        "title": "Operations Director",
        "region": "Europe",
        "last_activity": "2026-05-07",
        "notes": "Tracking shipment performance and delays.",
        "account_name": "Cascade Logistics",
    },
    {
        "full_name": "Quentin Meyer",
        "email": "quentin.meyer@cascadelogistics.com",
        "phone": "+49-30-5555-0166",
        "title": "Logistics Analyst",
        "region": "Europe",
        "last_activity": "2026-05-12",
        "notes": "Requires route optimization insights.",
        "account_name": "Cascade Logistics",
    },
    {
        "full_name": "Riley Barnes",
        "email": "riley.barnes@polartech.io",
        "phone": "+1-206-555-0125",
        "title": "Product Marketing Manager",
        "region": "North America",
        "last_activity": "2026-05-08",
        "notes": "Interested in go-to-market telemetry.",
        "account_name": "PolarTech",
    },
    {
        "full_name": "Sienna Brooks",
        "email": "sienna.brooks@polartech.io",
        "phone": "+1-206-555-0150",
        "title": "Customer Success Lead",
        "region": "North America",
        "last_activity": "2026-05-11",
        "notes": "Needs churn prediction and retention metrics.",
        "account_name": "PolarTech",
    },
]

AGENT_EMBEDDINGS = [
    {
        "source_schema": "business_zone",
        "source_table": "accounts",
        "source_name": "Acme Corporation",
        "content": "Acme Corporation is a global manufacturing company with priority on supply chain visibility.",
        "embedding": None,
    },
    {
        "source_schema": "business_zone",
        "source_table": "contacts",
        "source_name": "Mia Johansson",
        "content": "Head of Data Science at Orion Labs interested in AI model explainability.",
        "embedding": None,
    },
    {
        "source_schema": "business_zone",
        "source_table": "accounts",
        "source_name": "Horizon Health",
        "content": "Horizon Health is a healthcare services provider evaluating patient outcome analytics.",
        "embedding": None,
    },
    {
        "source_schema": "business_zone",
        "source_table": "accounts",
        "source_name": "Velocity Ventures",
        "content": "Velocity Ventures is a venture capital firm focused on portfolio performance insights.",
        "embedding": None,
    },
    {
        "source_schema": "business_zone",
        "source_table": "contacts",
        "source_name": "Olivia Grant",
        "content": "Chief Medical Officer reviewing analytics for healthcare operational efficiency.",
        "embedding": None,
    },
]

CHECKPOINTS = [
    {
        "thread_id": "seed-thread-2",
        "session_id": "seed-session-1",
        "checkpoint_data": {
            "checkpoint_id": "checkpoint-1",
            "thread_id": "seed-thread-2",
            "session_id": "seed-session-1",
            "normalized_prompt": "show revenue account performance",
            "intent": "revenue_analysis",
            "entities": {"labels": ["account"]},
            "created_at": "2026-05-13T12:00:00Z",
        },
        "previous_checkpoint_id": None,
        "state_type": "checkpoint",
    },
    {
        "thread_id": "seed-thread-2",
        "session_id": "seed-session-1",
        "checkpoint_data": {
            "plan_id": "plan-1",
            "thread_id": "seed-thread-2",
            "session_id": "seed-session-1",
            "business_intent": "revenue_analysis",
            "complexity": "standard",
            "task_count": 2,
            "tasks": [
                {"task_id": "task_1", "description": "Map entities to views", "depends_on": [], "status": "completed"},
                {"task_id": "task_2", "description": "Build query aggregation plan", "depends_on": ["task_1"], "status": "pending"},
            ],
            "summary": "Sample plan for revenue account performance.",
            "created_at": "2026-05-13T12:00:05Z",
        },
        "previous_checkpoint_id": None,
        "state_type": "planning",
    },
]

API_METRICS = [
    {
        "metric_name": "api_response_latency_ms",
        "metric_value": 132.4,
        "metric_labels": {"session_id": "seed-session-1", "endpoint": "/v1/agent/chat"},
    },
    {
        "metric_name": "api_response_latency_ms",
        "metric_value": 105.1,
        "metric_labels": {"session_id": "seed-session-2", "endpoint": "/v1/agent/chat"},
    },
    {
        "metric_name": "model_cost_estimate",
        "metric_value": 0.62,
        "metric_labels": {"session_id": "seed-session-1", "model_key": "default"},
    },
]

AUDIT_LOGS = [
    {
        "thread_id": "seed-thread-1",
        "event_type": "seed_init",
        "payload": {"message": "Seeding sample business data"},
    },
    {
        "thread_id": "seed-thread-1",
        "event_type": "seed_accounts",
        "payload": {"created_accounts": 10},
    },
    {
        "thread_id": "seed-thread-1",
        "event_type": "seed_contacts",
        "payload": {"created_contacts": 20},
    },
]


def _insert_accounts(cursor: any) -> dict[str, str]: # type: ignore
    account_ids: dict[str, str] = {}
    for account in ACCOUNTS:
        account_id = str(uuid.uuid4())
        account_ids[account["account_name"]] = account_id
        cursor.execute(
            """
            INSERT INTO business_zone.accounts
                (id, account_name, industry, annual_revenue, region, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                account_id,
                account["account_name"],
                account["industry"],
                account["annual_revenue"],
                account["region"],
                account["description"],
            ),
        )
    return account_ids


def _insert_contacts(cursor: any, account_ids: dict[str, str]) -> None: # type: ignore
    for contact in CONTACTS:
        cursor.execute(
            """
            INSERT INTO business_zone.contacts
                (id, account_id, full_name, email, phone, title, region, last_activity, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                account_ids[contact["account_name"]],
                contact["full_name"],
                contact["email"],
                contact["phone"],
                contact["title"],
                contact["region"],
                contact["last_activity"],
                contact["notes"],
            ),
        )


def _insert_agent_embeddings(cursor: any) -> None: # type: ignore
    for embedding in AGENT_EMBEDDINGS:
        cursor.execute(
            """
            INSERT INTO knowledge_zone.agent_embeddings
                (id, source_schema, source_table, source_id, content, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                embedding["source_schema"],
                embedding["source_table"],
                str(uuid.uuid4()),
                embedding["content"],
                embedding["embedding"],
            ),
        )


def _insert_checkpoints(cursor: any) -> None: # type: ignore
    for checkpoint in CHECKPOINTS:
        cursor.execute(
            """
            INSERT INTO audit_zone.checkpoints
                (id, thread_id, session_id, checkpoint_data, previous_checkpoint_id, state_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                checkpoint["thread_id"],
                checkpoint["session_id"],
                json.dumps(checkpoint["checkpoint_data"]),
                checkpoint["previous_checkpoint_id"],
                checkpoint["state_type"],
            ),
        )


def _insert_api_metrics(cursor: any) -> None: # type: ignore
    for metric in API_METRICS:
        cursor.execute(
            """
            INSERT INTO audit_zone.api_metrics
                (id, metric_name, metric_value, metric_labels)
            VALUES (%s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                metric["metric_name"],
                metric["metric_value"],
                json.dumps(metric["metric_labels"]),
            ),
        )


def _insert_audit_logs(cursor: any) -> None: # type: ignore
    for log in AUDIT_LOGS:
        cursor.execute(
            """
            INSERT INTO audit_zone.agent_logs
                (id, thread_id, event_type, payload)
            VALUES (%s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                log["thread_id"],
                log["event_type"],
                json.dumps(log["payload"]),
            ),
        )


def seed_database() -> None:
    print("Seeding PostgreSQL with sample business, audit, embedding, checkpoint, and metrics data...")
    with get_connection() as conn:
        with conn.cursor() as cursor:
            account_ids = _insert_accounts(cursor)
            _insert_contacts(cursor, account_ids)
            _insert_agent_embeddings(cursor)
            _insert_checkpoints(cursor)
            _insert_api_metrics(cursor)
            _insert_audit_logs(cursor)
        conn.commit()
    print("Seed complete: inserted 10 accounts, 20 contacts, 5 embeddings, 2 checkpoints, 3 metrics, and 3 audit log entries.")


if __name__ == "__main__":
    seed_database()
