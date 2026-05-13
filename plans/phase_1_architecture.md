# Phase 1 — Infrastructure & Data Foundation
## Agentic CRM System (Dataverse → PostgreSQL Semantic AI Layer)

---

# 1. Tổng quan Phase 1

Phase 1 tập trung xây dựng nền móng hạ tầng cho toàn bộ hệ thống Agentic CRM.  
Mục tiêu chính là chuẩn hóa kiến trúc, chuẩn bị môi trường AI orchestration và tạo lớp dữ liệu thân thiện với AI để phục vụ các Agent trong các phase tiếp theo.

Hệ thống sử dụng mô hình:

- Multi-Agent Architecture
- Semantic Database Layer
- AI-first Data Abstraction
- Modular Micro-services Structure

Database chính của hệ thống:

```text
agentic_ai
```

Nguồn dữ liệu:

```text
Microsoft Power Apps Dataverse
```

---

# 2. Objectives (Mục tiêu)

## 2.1 Chuẩn hóa kiến trúc dự án

Thiết lập cấu trúc thư mục theo hướng:

- Micro-modularity
- Domain Isolation
- AI-centric Organization
- MCP-ready Expansion

Mục tiêu:

- Dễ bảo trì
- Dễ scale nhiều Agent
- Dễ debug
- Dễ triển khai MCP servers
- Dễ tích hợp multi-model AI

---

## 2.2 Thiết lập môi trường AI Core

Cài đặt toàn bộ thư viện lõi phục vụ:

- Multi-LLM orchestration
- Agent routing
- LangGraph workflow
- Semantic memory
- RAG pipeline
- API backend
- Frontend dashboard

---

## 2.3 Xây dựng Data Foundation

Khởi tạo PostgreSQL để:

- Clone dữ liệu từ Dataverse
- Lưu AI memory
- Lưu vector embeddings
- Hỗ trợ semantic search
- Hỗ trợ audit trace

---

## 2.4 Xây dựng Semantic Abstraction Layer

Đây là lớp quan trọng nhất trong kiến trúc AI CRM.

Mục tiêu:

- Ẩn toàn bộ cấu trúc relational phức tạp khỏi AI
- Chuyển đổi schema kỹ thuật thành ngôn ngữ nghiệp vụ
- Giảm token schema khi prompt vào LLM
- Tăng độ chính xác khi AI query dữ liệu

AI sẽ thao tác chủ yếu với:

```text
AI-friendly Views
```

thay vì:

```text
Raw Dataverse Tables
```

---

# 3. Project Structure

```plaintext
/project-root
│
├── apps/
│   ├── api/                      # Flask Backend API
│   └── web/                      # Streamlit Frontend
│
├── core/
│   ├── agents/                   # Multi-Agent Logic
│   ├── graph/                    # LangGraph State Machine
│   ├── prompts/                  # Prompt Templates & Modular Prompting
│   └── tools/                    # MCP Tools, SQL Tools, Utilities
│
├── data/
│   ├── migration/                # Dataverse -> PostgreSQL Sync Scripts
│   ├── schema/                   # PostgreSQL Tables, Views, SQL Scripts
│   └── metadata/                 # Semantic Metadata & AI Descriptions
│
├── audit/                        # Audit Logs, Traces, AI Execution History
│
├── tests/                        # Unit & Integration Tests
│
├── docs/                         # Technical Documentation
│
├── .env                          # Environment Variables
├── requirements.txt              # Python Dependencies
├── docker-compose.yml            # PostgreSQL + Services
└── README.md
```

---

# 4. Technology Stack

## 4.1 AI Orchestration

| Library | Purpose |
|---|---|
| langgraph | Agent workflow orchestration |
| langchain | Tooling abstraction & agent runtime |
| litellm | Multi-model routing (Groq, Gemini, OpenRouter, OpenAI...) |

---

## 4.2 Database & Memory

| Library | Purpose |
|---|---|
| psycopg2-binary | PostgreSQL connection |
| pgvector | Vector storage |
| sqlalchemy | ORM & query abstraction |
| alembic | Database migrations |

---

## 4.3 Backend & Frontend

| Library | Purpose |
|---|---|
| flask | REST API backend |
| streamlit | Internal AI dashboard |
| requests | HTTP client |

---

## 4.4 MCP & Agent Tools

| Library | Purpose |
|---|---|
| @modelcontextprotocol/sdk | MCP server integration |
| pydantic | Structured validation |
| python-dotenv | Environment config |

---

# 5. requirements.txt

```txt
langgraph
langchain
litellm

psycopg2-binary
pgvector
sqlalchemy
alembic

flask
streamlit
requests

pydantic
python-dotenv

openai
google-generativeai

tiktoken
numpy
pandas

uvicorn
fastapi

sentence-transformers
```

---

# 6. Environment Configuration (.env)

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agentic_ai
DB_USER=postgres
DB_PASSWORD=your_password

# AI Providers
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=

# Application
APP_ENV=development
DEBUG=true
```

---

# 7. PostgreSQL Setup

## 7.1 Tạo Database

```sql
CREATE DATABASE agentic_ai;
```

---

## 7.2 Kích hoạt Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
```

---

# 8. Data Architecture Strategy

## 8.1 Vấn đề của Dataverse

Dữ liệu Dataverse thường có:

- Quan hệ mapping phức tạp
- Choice tables
- Lookup tables
- Many-to-many relationships
- Tên field khó hiểu
- Schema rất lớn

Ví dụ:

```text
hbl_account_industry_choice
hbl_account_country_choice
cr987_account_am_salesid
```

Những cấu trúc này gây vấn đề lớn cho AI:

- Tăng token context
- AI khó suy luận
- JOIN phức tạp
- Prompt khó maintain
- Query dễ sai

---

# 9. Semantic Abstraction Layer

## 9.1 Triết lý thiết kế

AI không nên:

- JOIN thủ công
- Hiểu foreign keys
- Hiểu mapping tables
- Hiểu raw schema

AI chỉ nên thấy:

- Business entities
- Human-readable labels
- Semantic fields

---

## 9.2 Giải pháp

Tạo:

```text
AI-friendly Views
```

để:

- Flatten relational data
- Convert code → label
- Ẩn complexity
- Chuẩn hóa business language

---

# 10. AI-Friendly View Example

## 10.1 View: v_hbl_account

```sql
CREATE OR REPLACE VIEW v_hbl_account AS
SELECT
    a.hbl_accountid,

    a.hbl_account_name AS account_name,

    a.hbl_account_physical_address AS physical_address,

    (
        SELECT co.choice_label
        FROM choice_option co
        WHERE co.choice_group = 'hbl_cust_choice_industry'
        AND co.choice_code = (
            SELECT hic.choice_code
            FROM hbl_account_industry_choice hic
            WHERE hic.hbl_accountid = a.hbl_accountid
            LIMIT 1
        )
    ) AS industry_label,

    (
        SELECT co.choice_label
        FROM choice_option co
        WHERE co.choice_group = 'hbl_cust_choice_country'
        AND co.choice_code = (
            SELECT hcc.choice_code
            FROM hbl_account_country_choice hcc
            WHERE hcc.hbl_accountid = a.hbl_accountid
            LIMIT 1
        )
    ) AS country_label,

    u.fullname AS am_sales_name,

    a.createdon,
    a.modifiedon

FROM hbl_account a

LEFT JOIN systemuser u
ON a.cr987_account_am_salesid = u.systemuserid;
```

---

# 11. Lợi ích của Semantic Views

## Giảm token schema

Thông thường:

```text
Raw schema → 3000-8000 tokens
```

Sau semantic abstraction:

```text
Semantic views → 300-1000 tokens
```

Giảm:

```text
70% - 90%
```

---

## Tăng độ chính xác cho AI

AI dễ hiểu hơn:

| Raw Schema | Semantic View |
|---|---|
| cr987_account_am_salesid | am_sales_name |
| choice_code | industry_label |
| mapping tables | flattened labels |

---

## Giảm hallucination

AI ít bị:

- JOIN sai
- Mapping sai
- Hiểu sai field
- Query lỗi

---

# 12. Naming Convention

## 12.1 Table Naming

| Type | Prefix |
|---|---|
| Raw tables | hbl_* |
| AI views | v_* |
| Audit tables | audit_* |
| Memory tables | mem_* |
| Metadata tables | meta_* |

---

## 12.2 AI View Naming

Ví dụ:

```text
v_hbl_account
v_hbl_contact
v_hbl_opportunity
v_hbl_activity
```

---

# 13. Migration Strategy

## Dataverse → PostgreSQL Flow

```text
Dataverse
    ↓
db.json Export
    ↓
Migration Scripts
    ↓
Raw PostgreSQL Tables
    ↓
Semantic Views
    ↓
AI Agents
```

---
