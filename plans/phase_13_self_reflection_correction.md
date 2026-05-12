# Phase 13: Self-Reflection & Multi-Turn Correction

## Mục tiêu

Xây dựng lớp kiểm soát chất lượng (QC Layer) nội bộ giúp hệ thống:

- tự phát hiện lỗi logic
- tự sửa SQL trước khi trả ra UI
- giảm hallucination
- giảm silent failures
- tăng độ tin cậy lên mức production-grade

Sau Phase 13, hệ thống không còn hoạt động theo kiểu:

```text
Generate → Execute → Return
```

mà chuyển sang:

```text
Generate → Verify → Reflect → Correct → Retry → Finalize
```

---

# 1. Vấn đề hiện tại (Current Failures)

## 1.1 Silent Failures

Đây là loại lỗi nguy hiểm nhất.

Ví dụ:

- SQL chạy thành công
- không báo lỗi syntax
- nhưng:
  - trả về 0 dòng
  - hoặc dữ liệu sai business logic

Trong khi thực tế:

- dữ liệu phải tồn tại
- hoặc query chưa đúng intent user

---

## 1.2 One-shot Limitation

Hiện tại hệ thống chỉ có:

# Một cơ hội duy nhất

để sinh SQL.

Nếu AI sai ở bước:

- chọn bảng
- JOIN logic
- WHERE condition
- aggregation

→ toàn bộ workflow thất bại.

---

## 1.3 Hallucination in Logic

AI có xu hướng:

- cực kỳ tự tin
- ngay cả khi JOIN sai bảng

Ví dụ:

```sql
JOIN contracts c ON c.id = a.id
```

trong khi đúng phải là:

```sql
JOIN contracts c ON c.account_id = a.id
```

Kết quả:

- dữ liệu technically valid
- nhưng business completely wrong

---

# 2. Kiến trúc Self-Reflection

## Tư duy cốt lõi

Sau khi query chạy xong:

# KHÔNG trả kết quả ngay

mà phải qua:

# Internal QC Layer

---

# ReflectorAgent

Đây là Agent chuyên:

- phản biện kết quả
- kiểm tra logic
- phát hiện anomaly
- yêu cầu retry nếu cần

---

# 3. Kiến trúc mới của LangGraph

## Updated Agent Flow

```text
User Query
    ↓
PlanningAgent
    ↓
SQLGeneratorAgent
    ↓
ExecutionAgent
    ↓
ReflectorAgent
    ↓
┌───────────────┬────────────────┐
│               │                │
│ RETRY         │ FINISH         │
│               │                │
↓               ↓                │
PlanningAgent   LearningAgent    │
│                                │
└────────────────────────────────┘
```

---

# 4. Verification Layer

## ReflectorAgent sẽ kiểm tra:

### 4.1 User Intent

```text
User thực sự hỏi gì?
```

---

### 4.2 Generated SQL

```text
SQL này có đúng logic business không?
```

---

### 4.3 Actual Results

```text
Kết quả trả về có hợp lý không?
```

---

# 5. Reflection Questions

ReflectorAgent sẽ tự đặt các câu hỏi như:

---

## Empty Result Detection

```text
"Tại sao dữ liệu lại rỗng?"
```

Có thể do:

- WHERE quá chặt
- sai date range
- sai JOIN
- sai status filter

---

## Schema Validation

```text
"Cột này có thực sự tồn tại không?"
```

Ví dụ:

```sql
amount_jan
```

có thể không tồn tại trong schema hiện tại.

---

## Business Logic Validation

```text
"Kết quả này có thực sự trả lời đúng ý user không?"
```

Ví dụ:

User hỏi:

```text
"Top khách hàng doanh thu cao nhất"
```

nhưng SQL lại:

- đếm số hợp đồng
- không SUM revenue

→ technically valid nhưng semantically wrong.

---

# 6. Reflection Outcomes

ReflectorAgent chỉ có 2 kết quả:

---

## RETRY

Nếu phát hiện:

- dữ liệu bất thường
- logic sai
- query rỗng bất hợp lý
- schema mismatch
- incomplete answer

thì:

```python
state["next_step"] = "planning"
```

và gửi feedback ngược lại.

---

## FINISH

Nếu:

- logic hợp lý
- dữ liệu consistent
- answer đúng intent

thì:

```python
state["next_step"] = "learning"
```

---

# 7. Reflector Node Implementation

```python
def reflector_node(state):

    query = state["input"]

    sql = state["sql_executed"]

    result = state["results"]

    # =====================================================
    # Reflection Prompt
    # =====================================================

    prompt = f"""

    You are a Senior Data QA Expert.

    Validate the following SQL execution.

    User Question:
    {query}

    Generated SQL:
    {sql}

    Query Result:
    {result}

    Your tasks:

    1. Check if the SQL logically answers the question.
    2. Check if JOIN conditions look correct.
    3. Check if empty results are suspicious.
    4. Check if aggregation logic is correct.
    5. Check if the result appears semantically valid.

    If the query is incorrect,
    return:

    RETRY:
    <detailed explanation>

    If the query is valid,
    return:

    FINISH

    """

    # =====================================================
    # Deep Reasoning Verification
    # =====================================================

    check = completion(
        model="gemini/gemini-1.5-pro",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # =====================================================
    # Reflection Decision
    # =====================================================

    if "RETRY" in check.content:

        state["next_step"] = "planning"

        state["error_feedback"] = check.content

        state["reflection_status"] = "retry"

    else:

        state["next_step"] = "learning"

        state["reflection_status"] = "success"

    return state
```

---

# 8. Feedback-driven Correction

## Khi RETRY xảy ra

PlanningAgent sẽ nhận:

```python
state["error_feedback"]
```

Ví dụ:

```text
RETRY:

The JOIN condition between contracts and accounts
appears incorrect.

The query joins on contract.id = account.id,
which is likely invalid.

Use contracts.account_id instead.
```

---

# 9. Multi-turn Self-Correction

## Hệ thống giờ có khả năng:

```text
Attempt #1
    ↓
Reflection
    ↓
Correction
    ↓
Attempt #2
    ↓
Reflection
    ↓
Correction
    ↓
Final Successful Query
```

---

# 10. Retry Budget System

## Giới hạn retry để tránh infinite loops

```python
MAX_REFLECTION_ROUNDS = 3
```

---

## Logic

```python
if state["retry_count"] >= MAX_REFLECTION_ROUNDS:
    fallback_to_safe_response()
```

---

# 11. Confidence Scoring

## ReflectorAgent có thể chấm điểm:

```python
confidence_score = {
    "schema_confidence": 0.95,
    "join_confidence": 0.82,
    "semantic_confidence": 0.91,
    "result_quality": 0.88
}
```

---

## Nếu score thấp

→ trigger retry.

---

# 12. Empty Result Heuristics

## Không phải mọi query rỗng đều sai

Ví dụ:

```text
"Hợp đồng bị hủy tháng sau"
```

có thể thực sự không có dữ liệu.

---

## ReflectorAgent phải phân biệt:

### Legit Empty

```text
Không có dữ liệu là hợp lý
```

---

### Suspicious Empty

```text
Khả năng cao query sai logic
```

---

# 13. SQL Safety Validation

ReflectorAgent cũng kiểm tra:

- Cartesian joins
- Missing GROUP BY
- Dangerous DELETE
- Unbounded queries
- Wrong aggregation

---

# 14. Learning from Mistakes

## Sau mỗi retry thành công

hệ thống sẽ lưu:

```python
{
    "failed_sql": "...",
    "failure_reason": "...",
    "corrected_sql": "...",
    "reflection_notes": "..."
}
```

---

# 15. Self-Improving Loop

## Đây là kiến trúc:

# Feedback Reinforcement

---

## Flow

```text
Mistake
    ↓
Reflection
    ↓
Correction
    ↓
Successful Query
    ↓
Knowledge Storage
    ↓
Future Improvement
```

---

# 16. Best Practices

## Không nên

```python
execute_once_and_return = True
```

---

## Nên dùng

```python
verify_before_return = True
```

---

## Không nên

```python
no_internal_critique = True
```

---

## Nên dùng

```python
reflection_loop_enabled = True
```

---

## Không nên

```python
silent_empty_results = True
```

---

## Nên dùng

```python
empty_result_validation = True
```

---

# 17. KPI Sau Phase 13

| Metric | Before | After |
|---|---|---|
| Silent Failures | Frequent | Rare |
| Wrong JOIN Logic | Medium | Very Low |
| SQL Reliability | Medium | High |
| Empty Result Errors | Common | Minimal |
| User-visible SQL Errors | Frequent | Near Zero |
| Self-correction Capability | None | Multi-turn |

---

# 18. Kết quả cuối cùng

Sau Phase 13, hệ thống sẽ đạt được:

# Self-Reflective Reasoning Architecture

---

# Hệ thống giờ có khả năng:

- tự phản biện chính mình
- tự sửa lỗi SQL
- retry thông minh
- phát hiện logic sai
- kiểm tra chất lượng dữ liệu
- giảm hallucination
- tăng độ tin cậy production

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- Autonomous AI Analysts
- Production-grade AI Data Systems
- Enterprise AI Reliability Layer
- Self-healing Query Pipelines
- Recursive AI Reasoning
- Fully Autonomous Multi-Agent Systems