# Phase 16: Semantic Schema Pruning (RAG for DB Structure)

## Mục tiêu

Giảm lượng schema context gửi vào LLM xuống mức tối thiểu bằng cách:

# Chỉ truy xuất đúng những bảng liên quan đến câu hỏi hiện tại

Sau Phase 16, hệ thống sẽ chuyển từ:

```text
Full Schema Injection
```

sang:

# Dynamic Schema Retrieval

---

# 1. Vấn đề hiện tại (Current Bottlenecks)

## 1.1 Context Bloat

Hiện tại mỗi request đều gửi:

- toàn bộ schema database
- hàng chục bảng
- hàng trăm cột
- relationships
- business rules

Ví dụ:

```text
50 tables
300+ columns
thousands of schema tokens
```

---

# Hệ quả

## Token Explosion

- cực kỳ tốn token
- tăng cost API
- tăng latency
- dễ gặp:
  - `503 High Demand`
  - `Context Window Exceeded`

---

## AI Confusion

LLM bị:

- nhiễu context
- chọn sai bảng
- JOIN nhầm entity
- reasoning sai logic

Ví dụ:

User hỏi:

```text
"Doanh thu hợp đồng tháng 1"
```

nhưng AI lại:

- nhìn thấy bảng warehouse
- inventory
- shipment

→ semantic distraction.

---

## 1.2 Hard-coded Schema Problem

Hiện tại schema thường nằm trong:

```python
schema = """
...
"""
```

hoặc:

```json
schema.json
```

---

# Đây là anti-pattern cực lớn

Khi DB scale lên:

```text
100 → 500 → 1000 tables
```

thì:

- prompt không thể chứa nổi
- maintenance cực kỳ khó
- update schema rất nguy hiểm

---

# 2. Tư duy cốt lõi của Phase 16

## KHÔNG gửi toàn bộ schema nữa

Thay vào đó:

# Schema cũng phải dùng RAG

---

# Tư duy mới

```text
Question
    ↓
Semantic Search
    ↓
Relevant Tables
    ↓
Mini Schema
    ↓
Reasoning Agent
```

---

# 3. Semantic Schema Pruning Architecture

Phase 16 bổ sung:

1. Metadata Vectorization
2. Schema Embedding Store
3. Semantic Table Retrieval
4. Dynamic Mini-schema Generation
5. Context-aware Schema Injection

---

# 4. Vectorize Database Metadata

## Mục tiêu

Biến cấu trúc database thành:

# Searchable Semantic Knowledge

---

# 5. Metadata Structure

Mỗi table sẽ được convert thành document:

```text
Table: hbl_contract

Columns:
- id
- contract_amount
- sign_date
- account_id

Description:
Stores customer contract information,
contract value and signing date.
```

---

# Mỗi column cũng có thể vectorize riêng

Ví dụ:

```text
Column: contract_amount

Meaning:
Total monetary value of the contract.
```

---

# 6. Metadata Embedding Pipeline

## Flow

```text
Database Schema
    ↓
Metadata Extraction
    ↓
Text Serialization
    ↓
Embedding Generation
    ↓
pgvector Storage
```

---

# 7. Schema Metadata Table

## PostgreSQL + pgvector

```sql
CREATE TABLE knowledge_zone.schema_metadata (

    id UUID PRIMARY KEY,

    table_name TEXT,

    column_name TEXT,

    description TEXT,

    metadata_text TEXT,

    embedding VECTOR(1536),

    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 8. Example Stored Metadata

## Example Entry

```json
{
  "table_name": "hbl_contract",

  "column_name": null,

  "description": "Customer contract records",

  "metadata_text": "
    Table: hbl_contract.
    Columns: id, amount, sign_date, account_id.
    Description: Stores contract value and signing information.
  "
}
```

---

# 9. Schema Retrieval

## User Query

```text
"Ai là người ký hợp đồng lớn nhất tháng 1?"
```

---

# Semantic Search Process

Hệ thống sẽ search semantic similarity giữa:

```text
User Query
```

và:

```text
Schema Metadata Embeddings
```

---

# Retrieved Tables

Ví dụ:

| Table | Similarity |
|---|---|
| hbl_contract | 0.94 |
| hbl_account | 0.88 |
| hbl_employee | 0.73 |

---

# Chỉ lấy Top-K tables

Ví dụ:

```python
top_k = 3
```

---

# 10. Dynamic Mini-schema Generation

## Mục tiêu

Tạo schema cực nhỏ dành riêng cho query hiện tại.

---

# Example Output

```sql
TABLE hbl_contract (
    id UUID,
    contract_amount FLOAT,
    sign_date DATE,
    account_id UUID
)

TABLE hbl_account (
    id UUID,
    customer_name TEXT
)
```

---

# Đây gọi là:

# Tailored Schema Context

---

# 11. Lợi ích cực lớn

## Trước đây

```text
100 tables
```

---

## Bây giờ

```text
2–5 tables
```

---

# Kết quả

- token giảm cực mạnh
- reasoning chính xác hơn
- context sạch hơn
- AI ít hallucination hơn

---

# 12. Schema Pruner Node

## File

```text
core/nodes/schema_pruner.py
```

---

# Implementation

```python
def schema_pruner_node(state):

    user_query = state["input"]

    # =====================================================
    # 1. Semantic Table Retrieval
    # =====================================================

    relevant_tables = db.vector_search(

        table="knowledge_zone.schema_metadata",

        query=user_query,

        top_k=3
    )

    # =====================================================
    # 2. Build Tailored Mini-schema
    # =====================================================

    mini_schema_parts = []

    for table in relevant_tables:

        schema_definition = table.get_definition()

        mini_schema_parts.append(schema_definition)

    mini_schema = "\n\n".join(mini_schema_parts)

    # =====================================================
    # 3. Update State
    # =====================================================

    state["current_schema"] = mini_schema

    # =====================================================
    # 4. Trace Logging
    # =====================================================

    selected_tables = [
        table.name
        for table in relevant_tables
    ]

    new_trace = {

        "node": "SchemaPruner",

        "msg": (
            f"✂️ Schema pruned. "
            f"Selected tables: {', '.join(selected_tables)}"
        )
    }

    return {

        "current_schema": mini_schema,

        "trace": [new_trace]
    }
```

---

# 13. LangGraph Flow Update

## Updated Flow

```text
User Query
    ↓
SchemaPrunerNode
    ↓
Mini Schema
    ↓
PlanningAgent
    ↓
SQLGeneratorAgent
    ↓
Execution
```

---

# 14. Dynamic Schema Injection

## Prompt giờ chỉ chứa:

```text
Relevant Schema Only
```

---

# Ví dụ Prompt

```text
You have access to the following schema:

TABLE hbl_contract (...)

TABLE hbl_account (...)

Generate SQL for:
"Top contract signers in January"
```

---

# 15. Column-level Pruning

## Advanced Optimization

Không chỉ prune table.

Hệ thống còn có thể:

# prune columns

---

# Ví dụ

Nếu query không liên quan:

```text
warehouse_location
```

thì column này sẽ không xuất hiện trong prompt.

---

# 16. Relationship-aware Retrieval

## Hệ thống có thể tự suy luận JOIN path

Ví dụ:

```text
contracts.account_id → accounts.id
```

---

# Điều này giúp:

- JOIN chính xác hơn
- ít hallucination hơn
- reasoning tốt hơn

---

# 17. Auto-sync Schema Updates

## Khi DB có bảng mới

KHÔNG cần sửa code.

Chỉ cần:

```text
Run metadata embedding sync
```

---

# Flow

```text
New Table
    ↓
Metadata Extractor
    ↓
Embedding Generator
    ↓
Vector Store Update
```

---

# 18. Scalability Benefits

## Traditional Prompt Injection

| DB Size | Problem |
|---|---|
| 20 tables | Acceptable |
| 100 tables | Heavy |
| 500 tables | Nearly impossible |
| 1000 tables | Context collapse |

---

## Semantic Schema Pruning

| DB Size | Performance |
|---|---|
| 20 tables | Excellent |
| 100 tables | Excellent |
| 500 tables | Excellent |
| 1000 tables | Excellent |

---

# 19. Token Reduction Impact

## Before

```text
Schema Tokens: 8000+
```

---

## After

```text
Schema Tokens: 300–800
```

---

# Token Savings

```text
~90% reduction
```

---

# 20. Best Practices

## Không nên

```python
inject_full_schema = True
```

---

## Nên dùng

```python
semantic_schema_retrieval = True
```

---

## Không nên

```python
hardcoded_schema_json = True
```

---

## Nên dùng

```python
dynamic_metadata_vector_store = True
```

---

## Không nên

```python
all_tables_every_request = True
```

---

## Nên dùng

```python
top_k_relevant_tables_only = True
```

---

# 21. KPI Sau Phase 16

| Metric | Before | After |
|---|---|---|
| Schema Tokens | Very High | Minimal |
| Prompt Size | Bloated | Lean |
| SQL Accuracy | Medium | Very High |
| Hallucinated Tables | Frequent | Rare |
| Context Window Failures | Common | Near Zero |
| DB Scalability | Weak | Massive |

---

# 22. Kết quả cuối cùng

Sau Phase 16, hệ thống sẽ đạt được:

# Schema-aware Retrieval Architecture

---

# Hệ thống giờ có khả năng:

- semantic schema search
- dynamic table selection
- tailored schema generation
- zero hard-coded schema
- scalable database reasoning
- ultra-lean prompting
- context-aware SQL generation

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- Enterprise-scale Databases
- AI Semantic Data Layers
- Autonomous SQL Reasoning
- Massive Multi-schema Systems
- AI-native Database Platforms
- Large-scale Knowledge Graph Agents