# Phase 12: Advanced RAG & Knowledge Distillation

## Mục tiêu

Nâng cấp hệ thống từ cơ chế Retrieval đơn thuần thành một kiến trúc:

- hiểu logic nghiệp vụ
- học từ các truy vấn thành công
- tự tối ưu chất lượng SQL theo thời gian
- tăng SQL Accuracy lên mức >95%

Sau Phase 12, `knowledge_zone` sẽ không còn là nơi lưu "query chết", mà trở thành:

# Một thư viện giáo án SQL thông minh

---

# 1. Vấn đề hiện tại (Current Limitations)

## 1.1 Simple Retrieval Is Not Enough

Semantic Search thông thường có vấn đề:

- vector giống nhau
- nhưng logic business khác hoàn toàn

Ví dụ:

```text
"Doanh thu tháng này"
```

và:

```text
"Giá trị hợp đồng tháng này"
```

có embedding khá gần nhau, nhưng:

- aggregation khác
- bảng khác
- business meaning khác

Kết quả:

- AI lấy sai SQL pattern
- join sai bảng
- tính toán sai logic

---

## 1.2 Knowledge Decay

Các SQL patterns cũ có thể:

- lỗi thời
- không còn đúng schema
- dùng cột đã bị rename
- dùng business rules cũ

Nhưng hệ thống vẫn retrieval bình thường.

Điều này gây:

- hallucination
- invalid SQL
- silent business errors

---

## 1.3 Lack of Reasoning Context

Hiện tại Agent chỉ lấy được:

```sql
SELECT ...
```

nhưng không hiểu:

- tại sao JOIN bảng đó
- tại sao filter như vậy
- business meaning phía sau

Kết quả:

- copy pattern mù quáng
- fail khi query hơi khác context

---

# 2. Kiến trúc nâng cấp trong Phase 12

Phase 12 bổ sung 3 kỹ thuật lõi:

1. Few-shot Dynamic Selector
2. HyDE Retrieval
3. Knowledge Distillation

---

# 3. Few-shot Dynamic Selector

## Mục tiêu

Thay vì hard-code examples trong prompt:

```python
EXAMPLES = [...]
```

hệ thống sẽ:

# Dynamic Retrieval Examples

---

## Flow

```text
User Query
    ↓
Vector Search
    ↓
Retrieve Top-K Successful Queries
    ↓
Inject into Prompt
    ↓
Reasoning Agent
```

---

## Ví dụ

User hỏi:

```text
"Top khách hàng có doanh thu cao nhất quý này"
```

Hệ thống tìm ra:

- 3 truy vấn revenue tương tự
- có join gần giống
- có aggregation tương tự

và inject vào prompt dưới dạng:

```text
Q: Doanh thu khách hàng tháng trước
SQL: ...
Logic: Revenue aggregation by account

Q: Top hợp đồng theo giá trị
SQL: ...
Logic: Contract ranking query
```

---

## Lợi ích

- AI có "bài mẫu"
- SQL generation ổn định hơn
- Giảm hallucination mạnh

---

# 4. HyDE — Hypothetical Document Embeddings

## Mục tiêu

Giải quyết vấn đề:

- user query quá ngắn
- thiếu technical keywords
- wording mơ hồ

---

## Ví dụ vấn đề

User hỏi:

```text
"Hợp đồng tháng 1 thế nào?"
```

Query này quá ngắn để semantic retrieval hoạt động tốt.

---

# Giải pháp HyDE

Hệ thống sẽ dùng lightweight model:

```text
gemini-2.0-flash
```

để sinh ra:

# Một câu trả lời giả định

---

## Ví dụ

### Input

```text
"Hợp đồng tháng 1 thế nào?"
```

### HyDE Output

```text
"Phân tích các hợp đồng được ký trong tháng 1 bao gồm:
contract value, customer accounts, signed date,
contract status và doanh thu liên quan."
```

---

## Sau đó

Embedding sẽ được tạo từ:

```text
HyDE Output
```

thay vì query gốc.

---

## Kết quả

Search chính xác hơn vì:

- có entity names
- có business terms
- có schema keywords

---

# 5. Knowledge Distillation

## Mục tiêu

Biến các SQL thành công thành:

# Knowledge Recipes

thay vì lưu raw SQL vô nghĩa.

---

# Teacher Agent (Professor Agent)

Sau khi SQL chạy thành công:

- một Agent phụ sẽ phân tích query
- giải thích logic
- trích xuất business meaning
- generate tags

---

## Ví dụ Distillation

### Raw SQL

```sql
SELECT a.name, SUM(c.amount)
FROM contracts c
JOIN accounts a ON c.account_id = a.id
GROUP BY a.name
ORDER BY SUM(c.amount) DESC
```

---

## Distilled Knowledge

### Logic

```text
Revenue aggregation by account using contracts table.
Join accounts for customer identification.
Group by account to calculate total revenue.
```

---

### Tags

```text
#revenue
#contract
#join_account_contract
#aggregation
#ranking
```

---

## Lợi ích

- AI hiểu WHY thay vì chỉ WHAT
- retrieval chính xác hơn
- reasoning tốt hơn
- reusable business intelligence

---

# 6. Update Database Schema

## Update knowledge_zone.query_patterns

```sql
ALTER TABLE knowledge_zone.query_patterns

ADD COLUMN reasoning_steps TEXT,

ADD COLUMN tags TEXT[],

ADD COLUMN rating FLOAT DEFAULT 5.0,

ADD COLUMN metadata JSONB;
```

---

# Ý nghĩa các field

| Column | Purpose |
|---|---|
| reasoning_steps | Giải thích logic business |
| tags | Phân loại semantic |
| rating | User feedback score |
| metadata | Schema version, environment info |

---

# 7. Metadata Design

## Ví dụ metadata

```json
{
  "schema_version": "v2.4",
  "database": "crm_prod",
  "tables": [
    "contracts",
    "accounts"
  ],
  "generated_by": "reasoning_agent",
  "validated": true,
  "created_at": "2026-05-12"
}
```

---

# 8. Advanced Retrieval Pipeline

## Updated Flow

```text
User Query
    ↓
HyDE Generator
    ↓
Hypothetical Answer
    ↓
Vector Search
    ↓
Top-K Query Patterns
    ↓
Few-shot Formatter
    ↓
Reasoning Agent
    ↓
SQL Generation
```

---

# 9. Core Retrieval Node

```python
def knowledge_retrieval_node(state):

    query = state["input"]

    # =====================================================
    # 1. HyDE Generation
    # =====================================================

    hypothetical_answer = generate_hyde_answer(query)

    # =====================================================
    # 2. Vector Search
    # =====================================================

    similar_patterns = search_vector_db(
        query=hypothetical_answer,
        top_k=3
    )

    # =====================================================
    # 3. Few-shot Formatting
    # =====================================================

    examples = []

    for pattern in similar_patterns:

        formatted_example = f"""

Q: {pattern.user_query}

SQL:
{pattern.optimized_sql}

Logic:
{pattern.reasoning_steps}

Tags:
{pattern.tags}

"""

        examples.append(formatted_example)

    # =====================================================
    # 4. Inject into Prompt
    # =====================================================

    state["few_shot_examples"] = "\n".join(examples)

    return state
```

---

# 10. Knowledge Distillation Pipeline

## Sau mỗi successful query

```text
Successful SQL
    ↓
Professor Agent
    ↓
Logic Extraction
    ↓
Tag Generation
    ↓
Recipe Creation
    ↓
Store into knowledge_zone
```

---

# 11. Intelligent Tagging System

## Ví dụ tags

### Business Tags

```text
#revenue
#contract
#customer
#sales
#renewal
```

---

### SQL Logic Tags

```text
#join
#group_by
#window_function
#ranking
#aggregation
```

---

### Domain Tags

```text
#crm
#finance
#hr
#operations
```

---

# 12. Quality Ranking System

## Dynamic Rating

Mỗi query pattern sẽ có score:

```python
rating = (
    execution_success
    + user_feedback
    + sql_performance
    + semantic_similarity
)
```

---

## High-rated patterns

được ưu tiên retrieval.

---

# 13. Schema Version Awareness

## Vấn đề

Schema thay đổi theo thời gian.

Nếu retrieval lấy SQL cũ:

- query fail
- logic sai
- business mismatch

---

## Giải pháp

Mỗi knowledge recipe sẽ lưu:

```json
{
  "schema_version": "v2.4"
}
```

Khi retrieval:

- ưu tiên schema version gần nhất
- bỏ các recipes outdated

---

# 14. Prompt Injection Format

## Final Prompt Structure

```text
SYSTEM PROMPT

+ FEW-SHOT EXAMPLES
+ REASONING RECIPES
+ RELEVANT SCHEMA
+ USER QUERY
```

---

# 15. Best Practices

## Không nên

```python
hardcoded_examples = True
```

---

## Nên dùng

```python
dynamic_fewshot_retrieval = True
```

---

## Không nên

```python
store_raw_sql_only = True
```

---

## Nên dùng

```python
store_reasoning_and_tags = True
```

---

## Không nên

```python
simple_embedding_search = True
```

---

## Nên dùng

```python
hyde_augmented_retrieval = True
```

---

# 16. KPI Sau Phase 12

| Metric | Before | After |
|---|---|---|
| SQL Accuracy | 70–85% | >95% |
| Retrieval Precision | Medium | Very High |
| Hallucination Rate | Medium | Very Low |
| Schema Mismatch | Frequent | Rare |
| Reusability | Low | High |
| Learning Capability | Static | Self-Optimizing |

---

# 17. Kết quả cuối cùng

Sau Phase 12, hệ thống sẽ đạt được:

# Retrieval-Augmented Reasoning

thay vì chỉ:

```text
Vector Search + Prompting
```

---

# Hệ thống giờ có khả năng:

- hiểu logic business
- học từ các truy vấn thành công
- tự xây thư viện kiến thức
- reasoning theo semantic context
- retrieval chính xác theo domain
- thích nghi với schema changes
- tối ưu SQL generation liên tục

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- Autonomous Database Agents
- Self-Improving AI Systems
- Enterprise Semantic Layer
- Multi-hop SQL Reasoning
- AI-native Analytics Platform
- Long-term Knowledge Memory