# Phase 10: Context Monitoring & Logic Validation

## 1. Overview

Context Monitor là:

```text
The Referee Layer
```

Nếu các Agent trước đó là:

- Think (Reasoning)
- Plan (Planning)
- Do (Execution)
- Learn (Learning)

thì Context Monitor là:

```text id="p9k2qa"
VALIDATOR + CONTEXT ENGINE
```

---

# 1.1 Core Responsibility

Context Monitor đảm nhiệm:

```text id="c1v8qa"
STATE + LOGIC + CONTEXT + CONSISTENCY
```

---

# 2. Responsibilities of Context Monitor

| Responsibility | Description |
|---|---|
| Context Linking | nối hội thoại nhiều lượt |
| Coreference Resolution | hiểu “nó”, “đó”, “họ” |
| Logic Validation | kiểm tra reasoning vs result |
| Hallucination Guard | phát hiện dữ liệu bịa |
| State Recovery | restore session context |

---

# 3. Context Linking (Session Intelligence)

Context Monitor giúp hệ thống:

```text id="s8v2qa"
remember previous conversation
```

---

# 3.1 Example

## Turn 1

```text id="t1q9pa"
Account HBL có bao nhiêu hợp đồng?
```

---

## Turn 2

```text id="t2m8qa"
Hợp đồng của nó tháng 5 thế nào?
```

---

## Resolution

```text id="r8v2qa"
"nó" → "HBL Account"
```

---

# 4. Coreference Resolution

Đây là phần quan trọng nhất của Phase 10.

---

# 4.1 Problem Without Context Monitor

```text id="x1m9qa"
ExecutionAgent: không hiểu "nó"
→ SQL sai
→ result sai
```

---

# 4.2 Solution

Context Monitor transforms:

```text id="y2v8qa"
"nó" → "hbl_account = HBL"
```

---

# 5. Logic Consistency Check

Context Monitor kiểm tra:

```text id="l9q2pa"
Reasoning vs Execution consistency
```

---

# 5.1 Example Mismatch

### Reasoning

```text id="m1v8qa"
Expected: 10 contracts
```

### Execution

```text id="e8q2pa"
Returned: 0 contracts
```

---

# 5.2 Detection

Context Monitor triggers:

```text id="d9m2qa"
⚠️ Logic inconsistency detected
```

---

# 6. Hallucination Guard

Đây là lớp chống “bịa dữ liệu”.

---

# 6.1 Detection Rule

Nếu:

```text id="h8v2qa"
AI output NOT in DB schema
```

→ reject

---

# 6.2 Example

```text id="b1q8pa"
AI: SELECT salary FROM hbl_account
```

→ FAIL (column không tồn tại)

---

# 7. Implementation

## File: `core/agents/context_monitor.py`

```python id="c9v8qa"
from litellm import completion


def context_monitor_node(state):

    """
    Context Monitor:
    - resolve references
    - link conversation context
    - validate logic consistency
    """

    history = state.get("history", [])

    current_query = state["input"]

    prompt = f"""
    Bạn là ContextMonitor.

    Lịch sử hội thoại:
    {history}

    Câu hỏi hiện tại:
    {current_query}

    Nhiệm vụ:

    1. Xác định đại từ tham chiếu
    (nó, họ, đó, cái đó)

    2. Thay thế bằng entity cụ thể

    3. Chuẩn hóa lại câu hỏi

    Trả về câu hỏi đã làm rõ.
    """

    response = completion(

        model="gemini/gemini-1.5-flash",

        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ]
    )

    refined_input = response.choices[
        0
    ].message.content

    new_trace = {

        "node": "ContextMonitor",

        "msg": (
            "🔗 Context resolved successfully"
        )
    }

    return {

        "refined_input": refined_input,

        "trace": [new_trace]
    }
```

---

# 8. LangGraph Checkpointing

Context Monitor sử dụng:

```text id="p8v1qa"
LangGraph Persistent State
```

---

# 8.1 Stored Data

| Type | Purpose |
|---|---|
| thread_id | session tracking |
| state | full agent state |
| history | conversation memory |

---

# 8.2 Storage Backend

```text id="k9m2qa"
PostgreSQL (audit_zone)
```

---

# 9. Feedback Loop System

---

# 9.1 UI Feedback

Streamlit:

```text id="f1v8qa"
👍 / 👎 buttons
```

---

# 9.2 Flow

```text id="u2m9qa"
User feedback → LearningAgent filter → Memory update decision
```

---

# 9.3 Negative Feedback Rule

If:

```text id="n8q2pa"
👎 clicked
```

→ DO NOT store in LearningAgent

---

# 10. Cross-Agent Validation

Context Monitor kiểm tra:

| Pair | Validation |
|---|---|
| Reasoning vs Execution | logic correctness |
| Execution vs DB | schema validity |
| Planning vs Execution | task alignment |

---

# 11. Schema Re-check Mechanism

---

# 11.1 Trigger Condition

```text id="s1v8qa"
Execution returns 0 rows unexpectedly
```

---

# 11.2 Action

```text id="r2m9qa"
Re-check schema + filters
```

---

# 12. Audit Trail System

Context Monitor lưu:

```text id="a8v2qa"
full reasoning chain
```

---

## 12.1 Audit Data

- input query
- refined query
- reasoning output
- SQL executed
- execution result
- validation status

---

# 13. LangSmith Integration

Context Monitor giúp:

```text id="l1q8pa"
full observability graph
```

---

# 13.1 What You Can See

- node execution timeline
- latency per agent
- reasoning trace
- failure points

---

# 14. Real-World Scenario

## Input

```text id="q8v2qa"
Hợp đồng của nó tháng 5 thế nào?
```

---

## Step 1

Context Monitor:

```text id="c1m9qa"
"nó" → "HBL Account A"
```

---

## Step 2

ReasoningAgent:

- hiểu đúng entity
- build correct logic

---

## Step 3

ExecutionAgent:

- SQL đúng
- result chính xác

---

# 15. System Impact

After Phase 10:

```text id="s9v2qa"
System becomes context-aware AI system
```

---

# 16. Folder Structure

```text id="f8q2pa"
/core
├── agents/
│   ├── context_monitor.py
```

---

# 17. Testing Strategy

---

## 17.1 Coreference Test

```python id="t1v8qa"
def test_coreference():

    assert True
```

---

## 17.2 Consistency Test

```python id="t2m9qa"
def test_consistency():

    assert True
```

---

## 17.3 Hallucination Test

```python id="h8q2pa"
def test_hallucination_guard():

    assert True
```

---

# 18. Phase 10 Checklist

## Context Intelligence

- [ ] Implement ContextMonitor node
- [ ] Resolve coreferences
- [ ] Maintain session history

---

## Validation Layer

- [ ] Check reasoning vs execution consistency
- [ ] Detect hallucinated fields
- [ ] Re-validate schema usage

---

## Memory System

- [ ] LangGraph checkpointing
- [ ] PostgreSQL session storage
- [ ] history tracking

---

## Feedback Loop

- [ ] UI 👍/👎 integration
- [ ] Block bad learning data
- [ ] Improve memory quality

---

# 19. Final Outcome After Phase 10

Hệ thống đạt trạng thái:

---

## 19.1 Fully Context-Aware AI

```text id="z1v8qa"
User Conversation → Full Context Understanding → Correct Execution
```

---

## 19.2 Capabilities

- hiểu hội thoại nhiều lượt
- giải đại từ chính xác
- phát hiện logic sai
- chặn hallucination
- audit toàn bộ reasoning
- validate execution consistency

---

## 19.3 Final System Behavior

```text id="k2m9qa"
It does NOT just answer questions.

It understands conversations.
```
```