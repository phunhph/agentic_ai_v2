# Phase 18: Self-Correction & Error-Based Learning

## Mục tiêu

Xây dựng:

# Hệ miễn dịch cho AI System

để Agent có khả năng:

- ghi nhớ lỗi cũ
- học từ thất bại
- tránh lặp lại sai lầm
- tự sửa logic theo thời gian
- tiến hóa liên tục mà không cần hard-code prompt fixes

Sau Phase 18, hệ thống sẽ chuyển từ:

```text
Static Knowledge AI
```

sang:

# Experience-driven Self-Improving AI

---

# 1. Vấn đề hiện tại (Current Limitations)

## 1.1 Repetitive Errors

LLM có xu hướng:

# lặp lại cùng một lỗi

---

# Ví dụ

AI liên tục viết:

```sql
id_customer
```

trong khi schema thực tế là:

```sql
customer_id
```

---

# Dù user đã sửa nhiều lần

AI vẫn có thể:

- quên correction
- hallucinate lại
- lặp lại bad joins
- reuse logic sai

---

## 1.2 Knowledge Gap

Ở Phase 12:

hệ thống chỉ lưu:

# Positive Knowledge

---

# Ví dụ

```text
Good SQL examples
Successful patterns
Correct joins
```

---

# Nhưng thiếu:

# Negative Knowledge

---

# Ví dụ

```text
Known bad joins
Dangerous aggregations
Invalid columns
Frequent hallucinations
```

---

# Đây là lỗ hổng cực lớn

AI biết:

```text
What works
```

nhưng không biết:

```text
What fails
```

---

## 1.3 Hard-code Fix Problem

Hiện tại mỗi khi phát hiện lỗi mới:

Phú phải:

- mở prompt
- sửa instructions
- deploy lại code

---

# Đây là anti-pattern

vì:

- khó maintain
- không scalable
- AI không tự tiến hóa được

---

# 2. Tư duy cốt lõi của Phase 18

## AI phải học từ thất bại

giống con người.

---

# Không chỉ nhớ:

```text
Correct Answers
```

---

# Mà còn phải nhớ:

```text
Painful Mistakes
```

---

# 3. Pitfall Map Architecture

## Đây là kiến trúc:

# Error Memory System

---

# Core Components

1. Failure Capture
2. Failure Embedding
3. Pitfall Summarization
4. Negative RAG
5. Constraint Injection
6. Error-aware Reasoning

---

# 4. Failure Capture

## Khi nào hệ thống ghi nhận lỗi?

---

# Trigger Sources

| Source | Example |
|---|---|
| ReflectorAgent | Detect wrong SQL |
| PostgreSQL Error | Column does not exist |
| User 👎 Feedback | Wrong business logic |
| Timeout | Bad query optimization |
| Empty Suspicious Result | Wrong filtering |

---

# 5. Captured Failure Structure

## Hệ thống lưu:

```json
{
  "user_query": "...",

  "failed_sql": "...",

  "failure_reason": "...",

  "reflection_notes": "...",

  "schema_snapshot": "...",

  "created_at": "..."
}
```

---

# 6. Example Failure Entry

```json
{
  "user_query":
    "Top khách hàng doanh thu cao nhất",

  "failed_sql":
    "SELECT COUNT(*) FROM contracts ...",

  "failure_reason":
    "Used COUNT instead of SUM(contract_amount)",

  "reflection_notes":
    "Revenue queries must aggregate monetary values."
}
```

---

# 7. Pitfall Indexing

## Mục tiêu

Biến lỗi thành:

# Reusable Lessons

---

# Dùng LLM để distill failure

---

# Raw Failure

```text
column id_customer does not exist
```

---

# Distilled Pitfall

```text
Use customer_id instead of id_customer
in hbl_account table.
```

---

# Đây gọi là:

# Error Distillation

---

# 8. Failed Patterns Table

## PostgreSQL Schema

```sql
CREATE TABLE knowledge_zone.failed_patterns (

    id UUID PRIMARY KEY,

    user_query TEXT,

    failed_sql TEXT,

    error_description TEXT,

    reflection_notes TEXT,

    embedding VECTOR(1536),

    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 9. Negative RAG

## Đây là nâng cấp cực mạnh

Trước khi generate SQL:

# AI sẽ search lỗi cũ trước

---

# Traditional RAG

```text
Find similar successful examples
```

---

# Negative RAG

```text
Find similar failures to avoid
```

---

# 10. Enhanced Reasoning Flow

## Updated Pipeline

```text
User Query
    ↓
Positive Retrieval
    ↓
Negative Retrieval
    ↓
Warning Constraints
    ↓
Reasoning Agent
    ↓
SQL Generation
```

---

# 11. Enhanced Reasoning Node

## File

```text
core/agents/reasoning.py
```

---

# Implementation

```python
def enhanced_reasoning_node(state):

    query = state["input"]

    # =====================================================
    # 1. Search Similar Past Failures
    # =====================================================

    past_failures = db.vector_search(

        table="knowledge_zone.failed_patterns",

        query=query,

        top_k=2
    )

    # =====================================================
    # 2. Build Warning Constraints
    # =====================================================

    warning_prompt = ""

    if past_failures:

        warning_prompt += (
            "\n⚠️ PAST FAILURE WARNINGS:\n"
        )

        for fail in past_failures:

            warning_prompt += (

                f"- Avoid mistake: "
                f"{fail.error_description}\n"
            )

    # =====================================================
    # 3. Inject Negative Constraints
    # =====================================================

    state["negative_constraints"] = warning_prompt

    return state
```

---

# 12. Example Warning Injection

## Prompt Input

```text
⚠️ PAST FAILURE WARNINGS:

- Do not join contracts.id with accounts.id
- Use SUM(contract_amount) for revenue queries
- customer_id is the valid column name
```

---

# Kết quả

AI sẽ:

- tránh hallucination cũ
- tránh bad joins
- tránh wrong aggregations

---

# 13. Self-Healing Architecture

## Đây là khả năng cực mạnh

Hệ thống có thể:

# tự vá logic của chính nó

---

# Không cần:

- sửa prompt thủ công
- deploy code
- hard-code fixes

---

# Flow

```text
Mistake
    ↓
Failure Capture
    ↓
Error Distillation
    ↓
Negative Memory
    ↓
Future Avoidance
```

---

# 14. Dual-memory Architecture

## Sau Phase 18

AI sẽ có:

---

# Positive Memory

```text
What works
```

---

# Negative Memory

```text
What must never happen
```

---

# Đây là nền tảng của:

# Human-like Learning

---

# 15. Reflection-enhanced Learning

## ReflectorAgent giờ không chỉ retry

mà còn:

# dạy lại hệ thống

---

# Ví dụ

```text
This failure occurred because
the query grouped by contract_id
instead of account_id.
```

---

# Reflection giờ trở thành:

# Structured Learning Signal

---

# 16. Error Clustering

## Advanced Optimization

Hệ thống có thể:

# nhóm các lỗi tương tự

---

# Ví dụ

## Cluster

```text
JOIN errors
```

bao gồm:

- wrong foreign keys
- missing join conditions
- invalid aliases

---

# Điều này giúp:

- detect weak schema areas
- improve prompts intelligently
- prioritize fixes

---

# 17. Explainability

## Phú có thể inspect:

```text
failed_patterns
```

để hiểu:

- AI đang yếu ở đâu
- bảng nào khó reasoning nhất
- loại query nào hay fail

---

# Đây là:

# AI Weakness Observatory

---

# 18. Adaptive Constraints

## Theo thời gian

warning system sẽ evolve:

---

# Frequently failed logic

→ become stronger constraints.

---

# Rare failures

→ lower warning priority.

---

# 19. Long-term Intelligence Growth

## Càng dùng lâu:

AI càng:

- ít hallucination
- ít repeat mistakes
- hiểu schema sâu hơn
- reasoning chính xác hơn

---

# Đây là:

# Experience Accumulation

---

# 20. Best Practices

## Không nên

```python
store_only_successful_sql = True
```

---

## Nên dùng

```python
store_failures_and_successes = True
```

---

## Không nên

```python
hardcode_prompt_fixes = True
```

---

## Nên dùng

```python
dynamic_negative_constraints = True
```

---

## Không nên

```python
ignore_failed_queries = True
```

---

## Nên dùng

```python
failure_memory_enabled = True
```

---

# 21. KPI Sau Phase 18

| Metric | Before | After |
|---|---|---|
| Repeated SQL Errors | Frequent | Rare |
| Hallucinated Columns | Medium | Very Low |
| Self-healing Capability | None | Strong |
| Failure Awareness | None | Full |
| Prompt Maintenance | Manual | Mostly Automatic |
| Long-term Learning | Weak | Continuous |

---

# 22. Kết quả cuối cùng

Sau Phase 18, hệ thống sẽ đạt được:

# Error-aware Self-Improving AI Architecture

---

# Hệ thống giờ có khả năng:

- ghi nhớ lỗi cũ
- học từ thất bại
- tránh repeat hallucinations
- tự sửa reasoning patterns
- xây dựng pitfall memory
- dynamic constraint injection
- self-healing prompt behavior
- long-term experiential learning

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- Autonomous AI Reliability Systems
- Human-level Adaptive Learning
- AI Immune Systems
- Self-correcting Enterprise AI
- Long-term Cognitive Memory
- Experience-driven AI Evolution