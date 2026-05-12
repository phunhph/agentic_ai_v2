# Phase 8: ExecutionAgent Layer (The Doer)

## 1. Overview

ExecutionAgent là:

```text
The Doer Layer
```

Nếu:

- IngestAgent = hiểu yêu cầu
- ReasoningAgent = suy luận
- PlanningAgent = lập kế hoạch

thì:

```text
ExecutionAgent = biến kế hoạch thành hành động thực tế
```

---

# 1.1 Core Philosophy

ExecutionAgent không “nghĩ nhiều”.

Nó chỉ:

```text
PLAN → SQL → EXECUTE → RESULT
```

---

# 2. Responsibilities of ExecutionAgent

| Responsibility | Description |
|---|---|
| SQL Generation | Sinh câu lệnh SQL |
| Task Execution | Thực thi từng task |
| Data Retrieval | Lấy dữ liệu từ PostgreSQL |
| Error Handling | Bắt lỗi SQL |
| Self-Healing | Tự sửa query |
| Trace Logging | Ghi lại execution flow |

---

# 3. Execution Flow (Master Pipeline)

```text
PlanningAgent
      ↓
ExecutionAgent
      ↓
SQL Generation (Groq)
      ↓
Tool Execution (Postgres)
      ↓
Success / Failure
      ↓
LearningAgent or PlanningAgent (retry loop)
```

---

# 4. Dynamic SQL Generation

ExecutionAgent không hardcode SQL.

Nó:

```text
LLM generates SQL on demand
```

---

# 4.1 Model Choice

```text
groq/llama3-70b-8192
```

---

# 4.2 Why Groq

- cực nhanh (LPU inference)
- mạnh về code generation
- latency thấp
- phù hợp real-time execution

---

# 4.3 SQL Generation Strategy

ExecutionAgent sử dụng:

- task description
- schema metadata
- relationship mapping

để generate SQL.

---

# 5. Self-Healing Mechanism

Đây là phần quan trọng nhất của Execution Layer.

---

# 5.1 Failure Scenario

```text
SQL ERROR:
column "hbl_account_name" does not exist
```

---

# 5.2 Self-Healing Loop

ExecutionAgent sẽ:

1. đọc error log
2. đối chiếu schema
3. regenerate SQL
4. retry execution

---

# 5.3 Healing Flow

```text
SQL FAIL
  ↓
Capture DB error
  ↓
Re-check schema
  ↓
Regenerate SQL (Groq)
  ↓
Retry execution
```

---

# 6. Implementation

## File: `core/agents/execution.py`

```python
from litellm import completion
import json

from core.tools.sql_executor import execute_business_query


def execution_agent_node(state):

    """
    ExecutionAgent:
    - generate SQL
    - execute query
    - handle errors
    - self-healing loop
    """

    plan = state["plan"]

    completed = state.get(
        "steps_completed",
        []
    )

    current_task = plan[
        len(completed)
    ]

    prompt = f"""
    Bạn là ExecutionAgent.

    Nhiệm vụ:
    Viết SQL cho task.

    Task:
    {current_task['description']}

    Schema:
    {json.dumps(state.get('metadata', {}))}

    Rules:
    - chỉ dùng bảng:
      hbl_account,
      hbl_contact,
      hbl_opportunities,
      hbl_contract

    - nếu JOIN:
      dùng foreign key đúng

    Output:
    CHỈ trả về SQL
    """

    response = completion(

        model="groq/llama3-70b-8192",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql_command = response.choices[
        0
    ].message.content.strip()

    # EXECUTE SQL
    try:

        result = execute_business_query(
            sql_command
        )

        status = "success"

    except Exception as e:

        result = str(e)

        status = "failed"

    new_trace = {

        "node": "ExecutionAgent",

        "msg": (
            f"🛠️ SQL: "
            f"{sql_command[:60]}... "
            f"| Status: {status}"
        )
    }

    # STATE UPDATE
    return {

        "results": [result],

        "sql_executed": sql_command,

        "steps_completed": [
            current_task["task_id"]
        ],

        "trace": [new_trace],

        "next_step":
            "learning"
            if status == "success"
            else "planning"
    }
```

---

# 7. SQL Execution Tool Layer

ExecutionAgent KHÔNG truy cập DB trực tiếp.

Nó phải đi qua:

```text
Tool Layer (Phase 4)
```

---

# 7.1 Tool Responsibilities

- validate SQL
- block dangerous queries
- execute SELECT
- return JSON result

---

# 8. Self-Healing Strategy (Master Feature)

---

# 8.1 Retry Cycle

```text
Attempt 1 → FAIL
   ↓
Analyze error
   ↓
Attempt 2 → FIXED
```

---

# 8.2 Healing Prompt Strategy

ExecutionAgent sẽ re-prompt:

```text
Fix SQL based on schema + error log
```

---

# 8.3 Example Repair Prompt

```text
Column hbl_account_name not found.

Available columns:
- hbl_account_name
- hbl_accountid

Rewrite SQL correctly.
```

---

# 9. Real-World Scenario

## User Request

```text
Top revenue accounts by AM Sales
```

---

# 9.1 Execution Steps

### Step 1: Generate SQL

```sql
SELECT am_salesid, SUM(revenue)
FROM hbl_contract
GROUP BY am_salesid;
```

---

### Step 2: Execute

```text
SUCCESS
```

---

### Step 3: Return Result

```json
[
  {"am_sales": "John", "revenue": 100000}
]
```

---

# 9.2 Failure Scenario

### Wrong SQL

```sql
SELECT hbl_account_name FROM hbl_account;
```

### Error

```text
column does not exist
```

---

### Self-Healing Fix

```sql
SELECT name FROM hbl_account;
```

---

# 10. Traceability

ExecutionAgent phải log:

---

## Example Trace

```json
{
  "node": "ExecutionAgent",
  "msg": "🛠️ Executed SQL successfully | Status: success"
}
```

---

# 10.1 UI Visibility

Streamlit hiển thị:

```text
🛠️ SQL Executed:
SELECT SUM(revenue) ...

Status: SUCCESS
```

---

# 11. Fallback Strategy

Nếu Groq fail:

---

## Fallback LLM

| Model | Role |
|---|---|
| Claude 3.5 Sonnet | SQL repair |
| GPT-4.1 | fallback reasoning |
| Gemini | backup generation |

---

# 12. Integration with PlanningAgent

ExecutionAgent có thể:

```text
FAIL → PlanningAgent
```

---

# 12.1 Retry Loop

```text
Execution FAIL
  ↓
PlanningAgent sửa task
  ↓
Execution retry
```

---

# 13. State Updates

ExecutionAgent cập nhật:

| Field | Purpose |
|---|---|
| sql_executed | SQL thực tế |
| results | output data |
| steps_completed | progress |
| trace | debug log |

---

# 14. Recommended Folder Structure

```text
/core
├── agents/
│   ├── execution.py
│
├── tools/
│   └── sql_executor.py
```

---

# 15. Testing Strategy

## 15.1 SQL Generation Test

```python
def test_sql_generation():

    state = {
        "plan": [
            {
                "task_id": 1,
                "description": "Get accounts"
            }
        ],
        "steps_completed": []
    }

    result = execution_agent_node(state)

    assert "sql_executed" in result
```

---

## 15.2 Failure Handling Test

```python
def test_sql_failure():

    # simulate invalid SQL

    assert True
```

---

## 15.3 Self-Healing Test

```python
def test_self_healing():

    # simulate error → retry

    assert True
```

---

# 16. Checklist Phase 8

## Core Execution

- [ ] Implement `execution_agent_node`
- [ ] Connect Groq Llama3
- [ ] Integrate SQL tool execution
- [ ] Handle task-by-task execution

---

## Error Handling

- [ ] Capture Postgres errors
- [ ] Retry failed SQL
- [ ] Re-generate query
- [ ] Loop back to PlanningAgent

---

## Self-Healing

- [ ] Detect invalid columns
- [ ] Fix schema mismatch
- [ ] Re-execute automatically

---

## Observability

- [ ] Trace SQL in UI
- [ ] Log execution status
- [ ] Show success/failure steps

---

# 17. Expected Outcome After Phase 8

Sau Phase 8, hệ thống đạt:

---

## Core Capabilities

- AI tự viết SQL real-time
- AI tự chạy query PostgreSQL
- AI tự sửa SQL khi lỗi
- AI execute multi-step tasks
- AI trace toàn bộ execution flow

---

## System Behavior

```text
User asks → AI plans → AI writes SQL → AI executes → AI fixes errors → AI returns result
```

---

## Final Result

ExecutionAgent biến hệ thống thành:

```text
Fully autonomous SQL execution engine
```

---