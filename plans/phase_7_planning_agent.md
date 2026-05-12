# Phase 7: PlanningAgent Layer (BabyAGI Pattern)

## 1. Overview

PlanningAgent là lớp:

```text
Task Orchestrator
```

Nếu:

- IngestAgent = hiểu yêu cầu
- ReasoningAgent = suy luận logic

thì:

```text
PlanningAgent = xây dựng execution roadmap
```

---

# 1.1 Core Philosophy

ReasoningAgent trả lời:

```text
CẦN LÀM GÌ
```

PlanningAgent trả lời:

```text
LÀM THEO THỨ TỰ NÀO
```

---

# 2. Responsibilities of PlanningAgent

| Responsibility | Description |
|---|---|
| Task Creation | Sinh task cụ thể |
| Task Prioritization | Sắp xếp thứ tự |
| Dependency Management | Quản lý phụ thuộc |
| Retry Strategy | Tự sửa khi lỗi |
| Stateful Planning | Lưu trạng thái task |

---

# 3. BabyAGI Planning Pattern

PlanningAgent sử dụng:

```text
BabyAGI-style recursive task planning
```

---

# 3.1 Why BabyAGI Matters

Thay vì:

```text
One-shot execution
```

Hệ thống sẽ:

- chia task nhỏ
- execute tuần tự
- đánh giá kết quả
- tự điều chỉnh khi lỗi

---

# 3.2 Planning Workflow

```text
ReasoningAgent
    ↓
PlanningAgent
    ↓
Task Queue Creation
    ↓
ExecutionAgent
    ↓
[Error?]
    ├── YES → Loop Back Planning
    └── NO → Continue
```

---

# 4. Task Creation

PlanningAgent chuyển:

```text
logic steps
```

thành:

```text
structured executable tasks
```

---

# 4.1 Example Input

```json
{
  "steps": [
    {
      "step": 1,
      "description": "Resolve Finance choice code"
    },
    {
      "step": 2,
      "description": "Join account and contract tables"
    }
  ]
}
```

---

# 4.2 Example Planned Tasks

```json
[
  {
    "task_id": 1,
    "action": "execute_sql",
    "description": "Get Finance choice code"
  },
  {
    "task_id": 2,
    "action": "execute_sql",
    "description": "Join account and contract"
  },
  {
    "task_id": 3,
    "action": "format_data",
    "description": "Format revenue report"
  }
]
```

---

# 5. Task Prioritization

PlanningAgent phải hiểu:

```text
dependency order
```

---

# 5.1 Example Dependency

Không thể:

```text
SUM revenue
```

nếu chưa:

```text
JOIN contract tables
```

---

# 5.2 Correct Execution Order

```text
1. Resolve choice_code
2. Build JOIN
3. Aggregate revenue
4. Format result
5. Verify output
```

---

# 6. Dynamic Adjustment

Đây là tính năng "Master".

Nếu ExecutionAgent lỗi:

PlanningAgent sẽ:

- nhận execution feedback
- phân tích lỗi
- tạo task sửa lỗi
- re-prioritize queue

---

# 6.1 Example Failure Scenario

ExecutionAgent trả về:

```text
column hbl_contract_jan does not exist
```

---

# 6.2 PlanningAgent Response

PlanningAgent tạo task mới:

```json
{
  "task_id": 99,
  "action": "repair_sql",
  "description": "Check schema metadata and fix invalid column"
}
```

---

# 6.3 Why Recursive Planning Matters

Nếu không có loop-back:

- workflow chết ngay
- không recover
- UX rất tệ

Recursive planning giúp:

- self-healing workflow
- adaptive execution
- resilient orchestration

---

# 7. Model Selection

## Recommended Model

```text
gemini/gemini-1.5-flash
```

---

# 7.1 Why Gemini Flash

Planning cần:

- structured output
- deterministic task generation
- fast response
- low cost

Gemini Flash phù hợp vì:

- JSON formatting tốt
- stable instruction following
- planning consistency cao

---

# 8. Structured Task Format

PlanningAgent bắt buộc trả JSON.

---

# 8.1 Output Contract

```json
{
  "todo_list": [],
  "status": "ready"
}
```

---

# 8.2 Task Object Format

```json
{
  "task_id": 1,
  "action": "execute_sql",
  "description": "Get revenue data",
  "input_from_task": null
}
```

---

# 8.3 Supported Actions

| Action | Purpose |
|---|---|
| `execute_sql` | Run SQL query |
| `format_data` | Format output |
| `verify_result` | Validate data |
| `repair_sql` | Fix failed SQL |
| `aggregation` | Aggregate data |

---

# 9. Implementation

## File: `core/agents/planning.py`

```python
from litellm import completion

import json

def planning_agent_node(state):

    """
    PlanningAgent:
    - task creation
    - prioritization
    - dependency management
    """

    logic_plan = state["logic_plan"]

    current_tasks = state.get(
        "plan",
        []
    )

    prompt = f"""
    Bạn là PlanningAgent.

    Dựa trên logic plan:

    {json.dumps(logic_plan)}

    Hãy tạo danh sách task
    cho ExecutionAgent.

    Mỗi task phải có:

    1. task_id
    2. action
    3. description
    4. input_from_task

    Action hợp lệ:
    - execute_sql
    - format_data
    - verify_result
    - repair_sql

    Trả về JSON:

    {{
        "todo_list": [
            {{
                "task_id": 1,
                "action": "execute_sql",
                "description": "...",
                "input_from_task": null
            }}
        ],

        "status": "ready"
    }}
    """

    response = completion(

        model="gemini/gemini-1.5-flash",

        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    plan_data = json.loads(
        response.choices[0].message.content
    )

    task_summary = ", ".join(
        [
            t["description"][:30]
            for t in plan_data["todo_list"]
        ]
    )

    new_trace = {

        "node": "PlanningAgent",

        "msg": (
            f"📋 Tasks planned: "
            f"{task_summary}..."
        )
    }

    return {

        "plan": plan_data["todo_list"],

        "trace": [new_trace],

        "next_step": "execution"
    }
```

---

# 10. Dependency Management

PlanningAgent phải đảm bảo:

```text
Task order is valid
```

---

# 10.1 Example Dependency Tree

```text
Task 1:
Resolve Finance code

↓ feeds into

Task 2:
JOIN account tables

↓ feeds into

Task 3:
Aggregate revenue
```

---

# 10.2 Example Task Dependency

```json
{
  "task_id": 2,
  "input_from_task": 1
}
```

---

# 11. Recursive Planning Architecture

Đây là đặc điểm cực kỳ quan trọng.

---

# 11.1 Loop-Back Flow

```text
ExecutionAgent
    ↓
Execution Error
    ↓
PlanningAgent
    ↓
Generate Repair Task
    ↓
ExecutionAgent Retry
```

---

# 11.2 Self-Healing Workflow

Hệ thống có thể:

- detect lỗi
- sửa kế hoạch
- retry execution
- continue workflow

mà không cần user intervention.

---

# 12. Stateful Planning

Toàn bộ task list được lưu trong:

```python
AgentState
```

---

# 12.1 Why Stateful Planning Matters

Giúp:

- resume execution
- track progress
- retry failed tasks
- visualize workflow

---

# 12.2 Example AgentState

```python
{
  "plan": [
    {
      "task_id": 1,
      "status": "completed"
    },
    {
      "task_id": 2,
      "status": "running"
    }
  ]
}
```

---

# 13. Streamlit UI Integration

Sidebar hiển thị:

```text
[PlanningAgent]

✅ Task 1 completed
🔄 Task 2 running
⏳ Task 3 pending
```

---

# 13.1 Progress Tracking

User có thể thấy:

```text
Completed: 2/5 tasks
```

real-time trên UI.

---

# 14. Real-World Scenario

## User Query

```text
Top doanh thu Finance Accounts tại Vietnam
```

---

# 14.1 Generated Plan

```json
{
  "todo_list": [

    {
      "task_id": 1,
      "action": "execute_sql",
      "description": "Resolve Finance choice code"
    },

    {
      "task_id": 2,
      "action": "execute_sql",
      "description": "Resolve Vietnam choice code"
    },

    {
      "task_id": 3,
      "action": "execute_sql",
      "description": "Join account and contract tables",
      "input_from_task": 1
    },

    {
      "task_id": 4,
      "action": "aggregation",
      "description": "Calculate revenue totals",
      "input_from_task": 3
    },

    {
      "task_id": 5,
      "action": "format_data",
      "description": "Format leaderboard report"
    }
  ]
}
```

---

# 15. Traceability

Mọi planning action phải được trace.

---

# 15.1 Example Trace

```json
{
  "node": "PlanningAgent",
  "msg": "📋 Planned 5 execution tasks"
}
```

---

# 15.2 Why Trace Matters

Giúp:

- debug workflows
- visualize orchestration
- replay planning
- optimize execution

---

# 16. Integration with ExecutionAgent

PlanningAgent không execute.

Nó chỉ:

- build task queue
- define dependencies
- assign actions

ExecutionAgent sẽ:

- consume tasks
- run tools
- return results

---

# 16.1 Handoff Contract

```json
{
  "plan": []
}
```

---

# 17. Recommended Graph Flow

```text
START
  ↓
IngestAgent
  ↓
ReasoningAgent
  ↓
PlanningAgent
  ↓
ExecutionAgent
```

---

# 18. Recommended Folder Structure

```text
/core
├── agents/
│   ├── ingest.py
│   ├── reasoning.py
│   ├── planning.py
│   └── execution.py
│
├── graph/
│   └── graph.py
│
└── state.py
```

---

# 19. Recommended Future Improvements

| Current | Future |
|---|---|
| Static task queue | Dynamic task graph |
| Linear planning | Parallel execution |
| Simple retries | Autonomous repair planning |
| Manual dependencies | DAG-based orchestration |

---

# 20. Testing Strategy

## Test Categories

| Test | Purpose |
|---|---|
| Task creation test | Verify todo generation |
| Dependency test | Verify execution order |
| Retry test | Verify loop-back planning |
| State test | Verify task persistence |

---

# 20.1 Example Planning Test

```python
def test_task_generation():

    state = {
        "logic_plan": {
            "steps": [
                {
                    "step": 1,
                    "description": "Resolve Finance code"
                }
            ]
        }
    }

    result = planning_agent_node(state)

    assert len(result["plan"]) > 0
```

---

# 20.2 Example Retry Test

```python
def test_repair_task_creation():

    failed_state = {
        "execution_error": (
            "column does not exist"
        )
    }

    # Simulate planning retry

    assert True
```

---

# 21. Phase 7 Completion Checklist

## Core Planning

- [ ] Implement `planning_agent_node`
- [ ] Connect Gemini Flash
- [ ] Generate structured todo list
- [ ] Save task queue into AgentState

---

## Task Management

- [ ] Create dependency-aware tasks
- [ ] Prioritize execution order
- [ ] Track task status
- [ ] Support nested workflows

---

## Recursive Planning

- [ ] Handle execution failures
- [ ] Generate repair tasks
- [ ] Support loop-back flow
- [ ] Retry failed workflows

---

## UI Integration

- [ ] Display task progress
- [ ] Show running/completed tasks
- [ ] Visualize workflow status

---

# 22. Expected Outcome After Phase 7

Sau khi hoàn thành:

Hệ thống sẽ có:

- BabyAGI-style task orchestration
- Stateful execution planning
- Dependency-aware workflows
- Recursive self-healing planning
- Traceable task execution
- Adaptive retry architecture

AI Agent sẽ có khả năng:

- tự tạo execution roadmap
- quản lý task dependencies
- retry khi execution lỗi
- tự sửa workflow
- visualize tiến trình
- orchestrate complex CRM queries