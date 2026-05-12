# Phase 2: Database Migration & Schema Optimization

## 1. Kiến trúc Database Target (PostgreSQL)

Chúng ta sẽ triển khai theo mô hình **Relational + Metadata**.

Mục tiêu:

- AI Agent nhìn thấy semantic label thay vì raw code
- Hỗ trợ reasoning và auto SQL generation
- Chuẩn bị cho RAG + pgvector ở các phase sau

Ví dụ:

| Raw Code | Semantic Label |
|---|---|
| 135150011 | Vietnam |
| 135150001 | Finance |

---

# 1.1 Global Choice Table

Thay vì tạo hàng chục bảng mapping riêng cho từng choice field,
sử dụng một bảng global lưu toàn bộ choice metadata.

```sql
CREATE TABLE sys_choice_options (
    choice_group VARCHAR(100),
    choice_code VARCHAR(50),
    choice_label TEXT,

    PRIMARY KEY (choice_group, choice_code)
);
```

## Example Data

| choice_group | choice_code | choice_label |
|---|---|---|
| hbl_cust_choice_country | 135150011 | Vietnam |
| hbl_cust_choice_industry | 135150001 | Finance |

---

# 2. Business Tables

Các bảng nghiệp vụ sẽ được generate từ `db.json`.

Nguyên tắc:

- Chuẩn hóa quan hệ
- Có đầy đủ Foreign Key
- Tối ưu cho AI Query Layer
- Hỗ trợ semantic reasoning

---

# 2.1 Table: hbl_account

```sql
CREATE TABLE hbl_account (
    hbl_accountid UUID PRIMARY KEY,

    hbl_account_name TEXT NOT NULL,
    hbl_account_physical_address TEXT,
    hbl_account_website TEXT,

    hbl_account_annual_it_budget NUMERIC(19,4),
    hbl_account_year_found INT,

    -- Lookup fields
    cr987_account_am_salesid UUID REFERENCES systemuser(systemuserid),
    cr987_account_bdid UUID REFERENCES systemuser(systemuserid),

    createdon TIMESTAMP,
    modifiedon TIMESTAMP
);
```

---

# 2.2 Many-to-Many Choice Mapping Tables

Power Apps hỗ trợ multi-select choice fields.

Do đó cần tạo mapping tables trung gian.

Ví dụ:

- Industry
- Status
- Country
- Tags

---

## Example: Industry Mapping

```sql
CREATE TABLE hbl_account_industry_map (
    hbl_accountid UUID REFERENCES hbl_account(hbl_accountid),

    choice_code VARCHAR(50),

    choice_group VARCHAR(100)
        DEFAULT 'hbl_cust_choice_industry',

    PRIMARY KEY (hbl_accountid, choice_code)
);
```

---

## Example Query

```sql
SELECT
    a.hbl_account_name,
    c.choice_label AS industry
FROM hbl_account a
JOIN hbl_account_industry_map m
    ON a.hbl_accountid = m.hbl_accountid
JOIN sys_choice_options c
    ON c.choice_group = m.choice_group
   AND c.choice_code = m.choice_code;
```

---

# 3. Database Views (AI-Friendly Layer)

Đây là lớp cực kỳ quan trọng cho AI Agent.

Thay vì AI phải tự JOIN phức tạp:

```sql
SELECT *
FROM v_hbl_account;
```

AI sẽ đọc được semantic fields:

- country_name
- am_sales_name
- industry_labels
- status_labels

thay vì raw code.

---

# 3.1 AI View Example

```sql
CREATE VIEW v_hbl_account AS
SELECT
    a.*,

    (
        SELECT choice_label
        FROM sys_choice_options
        WHERE choice_group = 'hbl_cust_choice_country'
          AND choice_code = (
                SELECT choice_code
                FROM hbl_account_country_choice
                WHERE hbl_accountid = a.hbl_accountid
                LIMIT 1
          )
    ) AS country_name,

    u.fullname AS am_sales_name

FROM hbl_account a
LEFT JOIN systemuser u
    ON a.cr987_account_am_salesid = u.systemuserid;
```

---

# 3.2 Recommended AI Views

| View Name | Purpose |
|---|---|
| v_hbl_account | Account semantic reading |
| v_hbl_contact | Contact semantic reading |
| v_hbl_opportunities | Opportunity reasoning |
| v_hbl_contract | Contract relationship graph |
| v_hbl_activity | Timeline AI analysis |

---

# 4. Python Migration Script

## Objective

Script sẽ:

1. Đọc `db.json`
2. Generate schema động
3. Import metadata
4. Import choice options
5. Tạo relations
6. Build AI Views

---

# 4.1 Python Migration Skeleton

```python
import json
import psycopg2

TYPE_MAPPING = {
    "uuid": "UUID",
    "text": "TEXT",
    "decimal": "NUMERIC(19,4)",
    "datetime": "TIMESTAMP",
    "int": "INT",
    "boolean": "BOOLEAN"
}

def migrate_data(json_file):

    # 1. Read db.json
    with open(json_file, "r", encoding="utf-8") as f:
        db_schema = json.load(f)

    conn = psycopg2.connect(
        host="localhost",
        database="crm_ai",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()

    # 2. Insert choice options
    for group in db_schema["choice_groups"]:

        group_name = group["group_name"]

        for item in group["options"]:

            cur.execute("""
                INSERT INTO sys_choice_options
                (choice_group, choice_code, choice_label)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                group_name,
                item["code"],
                item["label"]
            ))

    # 3. Dynamic table generation
    for table in db_schema["tables"]:

        table_name = table["table_name"]

        columns = []

        for field in table["fields"]:

            field_name = field["name"]
            field_type = TYPE_MAPPING.get(field["type"], "TEXT")

            columns.append(f"{field_name} {field_type}")

        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {",".join(columns)}
        );
        """

        cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()

    print("Migration completed.")
```

---

# 5. Metadata Layer for AI Agent

AI Agent cần hiểu:

- bảng nào liên kết bảng nào
- lookup direction
- cardinality
- semantic meaning

Do đó cần lưu relation metadata trong PostgreSQL.

---

# 5.1 System Relation Metadata Table

```sql
CREATE TABLE sys_relation_metadata (
    from_table VARCHAR(100),
    from_field VARCHAR(100),

    to_table VARCHAR(100),

    relation_type VARCHAR(50),

    description TEXT
);
```

---

# 5.2 Example Metadata

| from_table | from_field | to_table | relation_type |
|---|---|---|---|
| hbl_contact | hbl_contact_accountid | hbl_account | Lookup (N:1) |
| hbl_contract | hbl_contract_opportunityid | hbl_opportunities | Lookup (N:1) |

---

# 5.3 Why This Matters for AI

Khi Agent cần reasoning:

```text
Find all contracts related to Finance accounts in Vietnam
```

Agent sẽ:

1. Query relation metadata
2. Xác định đường JOIN
3. Sinh SQL tự động
4. Trả về semantic results

---

# 6. pgvector Setup

Phase sau sẽ cần:

- Embedding search
- Semantic retrieval
- RAG
- AI recommendation
- Memory layer

Do đó bắt buộc cài `pgvector`.

---

# 6.1 Install pgvector

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

# 6.2 AI Embedding Table

```sql
CREATE TABLE ai_embeddings (
    id UUID PRIMARY KEY,

    source_table VARCHAR(100),
    source_id UUID,

    content TEXT,

    embedding VECTOR(1536),

    createdon TIMESTAMP DEFAULT NOW()
);
```

---

# 6.3 Vector Index

```sql
CREATE INDEX idx_ai_embeddings_vector
ON ai_embeddings
USING ivfflat (embedding vector_cosine_ops);
```

---

# 7. Final Architecture

```text
Power Apps
    ↓
db.json
    ↓
Migration Engine (Python)
    ↓
PostgreSQL
    ├── Business Tables
    ├── Choice Metadata
    ├── Relation Metadata
    ├── AI Views
    ├── Vector Embeddings
    └── Agent Query Layer
```

---

# 8. Phase 2 Completion Checklist

## Database Schema

- [ ] Create systemuser
- [ ] Create hbl_account
- [ ] Create hbl_contact
- [ ] Create hbl_opportunities
- [ ] Create hbl_contract

---

## Choice Metadata

- [ ] Import toàn bộ 19+ choice groups
- [ ] Validate duplicate choice_code
- [ ] Create indexes cho lookup performance

---

## AI-Friendly Views

- [ ] Create v_hbl_account
- [ ] Create v_hbl_contact
- [ ] Create v_hbl_opportunities
- [ ] Create v_hbl_contract

---

## Metadata Layer

- [ ] Create sys_relation_metadata
- [ ] Import relations từ db.json
- [ ] Validate lookup graph

---

## AI Infrastructure

- [ ] Install pgvector
- [ ] Create embedding tables
- [ ] Create vector indexes
- [ ] Test semantic search pipeline

---

# 9. Expected Outcome

Sau khi hoàn thành Phase 2:

AI Agent có thể:

- hiểu schema động
- reasoning theo relationship graph
- query semantic labels
- hỗ trợ RAG
- chuẩn bị cho autonomous workflow phase sau

Ví dụ:

```text
Show me all Finance customers in Vietnam
managed by John with active contracts.
```

AI sẽ tự:

- hiểu Finance = choice label
- hiểu Vietnam = country label
- JOIN account → contract
- resolve AM owner
- generate SQL tự động