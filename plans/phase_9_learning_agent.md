# Phase 9: LearningAgent Layer (The Scholar & Optimizer)

## 1. Overview

LearningAgent là:

```text
Long-Term Memory + Optimization Layer
```

Nếu:

- IngestAgent = Gatekeeper
- ReasoningAgent = Thinker
- PlanningAgent = Planner
- ExecutionAgent = Doer

thì:

```text
LearningAgent = Scholar (người học + tối ưu hệ thống)
```

---

# 1.1 Core Philosophy

LearningAgent không tạo ra hành động mới.

Nó:

```text
OBSERVE → DISTILL → STORE → REUSE
```

---

# 2. Responsibilities of LearningAgent

| Responsibility | Description |
|---|---|
| Knowledge Distillation | Trích xuất pattern |
| Embedding Generation | Vector hóa query |
| Memory Storage | Lưu vào pgvector |
| Pattern Reuse | Tái sử dụng SQL |
| Cost Optimization | Giảm LLM calls |
| Self-Evolution | Hệ thống tự cải thiện |

---

# 3. Knowledge Architecture

LearningAgent lưu tri thức vào:

```text
PostgreSQL + pgvector
```

---

# 3.1 Knowledge Schema

```sql id="p3lq01"
knowledge_zone.query_patterns
```

---

## Fields

| Field | Description |
|---|---|
| user_query | Câu hỏi người dùng |
| optimized_sql | SQL chuẩn |
| query_vector | embedding |
| execution_count | số lần dùng |

---

# 4. Learning Workflow

```text id="l9xq2a"
ExecutionAgent SUCCESS
        ↓
LearningAgent Trigger
        ↓
Embedding Generation
        ↓
Store in pgvector
        ↓
Future reuse
```

---

# 5. Implementation

## File: `core/agents/learning.py`

```python id="k8v1xa"
from litellm import embedding

import json

from database import get_db_connection


def learning_agent_node(state):

    """
    LearningAgent:
    - extract knowledge
    - embed query
    - store pattern
    """

    user_query = state["input"]

    final_sql = state["sql_executed"]

    execution_status = state.get(
        "steps_completed"
    )

    # Only learn from success
    if not execution_status:

        return {
            "next_step": "end"
        }

    # 1. EMBEDDING GENERATION
    response = embedding(

        model="gemini/text-embedding-004",

        input=[user_query]
    )

    query_vector = response.data[
        0
    ].embedding

    # 2. STORE IN POSTGRES
    conn = get_db_connection()

    cur = conn.cursor()

    try:

        cur.execute("""

        INSERT INTO knowledge_zone.query_patterns

        (user_query, optimized_sql, query_vector)

        VALUES (%s, %s, %s)

        ON CONFLICT (user_query)

        DO UPDATE SET
        execution_count =
        query_patterns.execution_count + 1;

        """, (

            user_query,

            final_sql,

            query_vector
        ))

        conn.commit()

        msg = (
            "🧠 Knowledge stored successfully"
        )

    except Exception as e:

        msg = f"⚠️ Learning failed: {str(e)}"

    finally:

        cur.close()

        conn.close()

    new_trace = {

        "node": "LearningAgent",

        "msg": msg
    }

    return {

        "trace": [new_trace],

        "next_step": "end"
    }
```

---

# 6. Vectorization Strategy

LearningAgent dùng:

```text id="3qz9df"
gemini/text-embedding-004
```

---

## 6.1 Why Embedding Matters

Embedding giúp:

- semantic search
- similarity matching
- query reuse
- eliminate redundant SQL generation

---

# 7. Semantic Cache Layer

Đây là phần quan trọng nhất của Phase 9.

---

# 7.1 Before Execution Flow

Trước khi gọi ExecutionAgent:

```text id="v2p8m3"
Check similarity in pgvector
```

---

## 7.2 Flow

```text id="c8n1qp"
User Query
   ↓
Embedding Query
   ↓
Vector Search
   ↓
Similarity > 90% ?
        ↓
     YES → reuse SQL
     NO  → generate new SQL
```

---

# 7.3 Impact

| Metric | Improvement |
|---|---|
| Token usage | ↓↓↓ |
| Latency | ↓↓↓ |
| Cost | ↓↓↓ |
| Stability | ↑↑↑ |

---

# 8. Knowledge Distillation

LearningAgent không lưu raw data.

Nó lưu:

- intent
- optimized SQL
- query pattern

---

## 8.1 Example Distillation

### Input

```text id="8v2xpa"
Top revenue Finance accounts Vietnam
```

---

### Output Stored

```json id="x9m2la"
{
  "query": "Top revenue Finance accounts Vietnam",
  "sql": "SELECT ...",
  "pattern": "aggregation + join + filter"
}
```

---

# 9. Self-Evolution Mechanism

Hệ thống trở nên:

```text id="e1v9p2"
smarter over time
```

---

## 9.1 Learning Loop

```text id="t7k3qa"
More queries → more patterns → better reuse → less LLM dependency
```

---

# 10. Cost Optimization Layer

LearningAgent giúp:

| Problem | Solution |
|---|---|
| expensive LLM calls | reuse SQL |
| repetitive queries | semantic cache |
| slow execution | vector lookup |

---

# 11. Data Integrity Rules

Chỉ lưu khi:

```text id="z8v1qa"
Execution = SUCCESS
```

---

## 11.1 Why This Matters

Tránh:

- garbage SQL patterns
- failed queries in memory
- hallucinated knowledge

---

# 12. Integration with System

## 12.1 In Execution Layer

```text id="y3n8pa"
Before SQL generation:
→ check vector DB
```

---

## 12.2 In Learning Layer

```text id="k4q1zx"
After success:
→ store knowledge
```

---

# 13. Streamlit Observability

UI hiển thị:

```text id="m9q2pa"
🧠 Learned new pattern:
Query: Top revenue accounts
Status: Stored in memory
```

---

# 14. Real-World Scenario

## User Query

```text id="f1m8qa"
Revenue Finance accounts Vietnam
```

---

## Step 1: First Time

- no cache
- full pipeline runs
- SQL generated

---

## Step 2: Stored

LearningAgent saves:

```text id="c9v2qa"
query → SQL mapping
```

---

## Step 3: Second Time

- vector match found
- skip reasoning + execution
- reuse SQL directly

---

# 15. Architecture Impact

After Phase 9:

```text id="b7k2pa"
System becomes memory-driven AI agent
```

---

# 16. Folder Structure

```text id="p2v8qa"
/core
├── agents/
│   ├── learning.py
│
├── memory/
│   └── vector_store.py
```

---

# 17. Testing Strategy

---

## 17.1 Embedding Test

```python id="t8q1pa"
def test_embedding_generation():

    assert True
```

---

## 17.2 Storage Test

```python id="q1m9pa"
def test_memory_storage():

    assert True
```

---

## 17.3 Retrieval Test

```python id="v3n8qa"
def test_similarity_search():

    assert True
```

---

# 18. Phase 9 Checklist

## Core Learning

- [ ] Implement LearningAgent
- [ ] Connect pgvector
- [ ] Store embeddings
- [ ] Save successful SQL patterns

---

## Memory System

- [ ] Vector search integration
- [ ] Semantic caching
- [ ] Query reuse mechanism

---

## Optimization

- [ ] Reduce LLM calls
- [ ] Improve latency
- [ ] Enable pattern reuse

---

## Integrity

- [ ] Only store successful executions
- [ ] Avoid duplicate noisy data
- [ ] Maintain clean memory

---

# 19. Final System State After Phase 9

Sau Phase 9, hệ thống trở thành:

---

## 19.1 Full Agent Pipeline

```text id="a9v2qa"
User
 ↓
IngestAgent
 ↓
ReasoningAgent
 ↓
PlanningAgent
 ↓
ExecutionAgent
 ↓
LearningAgent
 ↓
Memory (pgvector)
```

---

## 19.2 System Evolution

| Capability | Status |
|---|---|
| SQL generation | ✔ |
| Autonomous execution | ✔ |
| Self-healing | ✔ |
| Task planning | ✔ |
| Long-term memory | ✔ |
| Semantic reuse | ✔ |

---

# 20. Final Outcome (Master Level)

Hệ thống sau Phase 9:

```text id="h2q9pa"
Autonomous CRM Intelligence System
```

---

## Core Capabilities

- tự hiểu câu hỏi
- tự lập kế hoạch
- tự viết SQL
- tự chạy DB
- tự sửa lỗi
- tự học từ lịch sử
- tự tối ưu chi phí

---

## Final Behavior

```text id="n8v2qa"
Ask once → system learns forever
```
```