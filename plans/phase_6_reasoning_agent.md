# Phase 6: ReasoningAgent Layer (The Thinker)

## 1. Overview

Nếu IngestAgent là:

```text
The Gatekeeper
```

thì ReasoningAgent là:

```text
The Thinker
```

Đây là lớp chịu trách nhiệm:

- phân tích logic
- bẻ nhỏ bài toán
- hiểu quan hệ dữ liệu
- xây dựng execution strategy

---

# 1.1 Core Philosophy

ReasoningAgent không viết SQL trực tiếp.

Nó:

- suy nghĩ
- phân tích
- lập luận
- decomposite problem

sau đó mới chuyển sang PlanningAgent.

---

# 2. Responsibilities of ReasoningAgent

| Responsibility | Description |
|---|---|
| Query Decomposition | Chia nhỏ bài toán |
| Relationship Mapping | Xác định JOIN path |
| Logic Branching | Quyết định execution path |
| Schema Reasoning | Hiểu metadata |
| CoT Reasoning | Giải thích logic suy luận |

---

# 3. Query Decomposition

Đây là chức năng quan trọng nhất.

ReasoningAgent phải biến:

```text
complex question
```

thành:

```text
small executable tasks
```

---

# 3.1 Example Decomposition

Input:

```text
Tìm khách hàng mua nhiều nhất tháng 5
```

---

## Reasoning Output

```text
Step 1:
Lấy hợp đồng tháng 5

Step 2:
Group theo Account

Step 3:
SUM doanh thu

Step 4:
Sort descending

Step 5:
Lấy Top 1
```

---

# 3.2 Why Decomposition Matters

Nếu AI cố xử lý mọi thứ một lần:

- reasoning yếu
- SQL phức tạp
- dễ hallucination
- khó debug

Decomposition giúp:

- modular execution
- explainability
- retry dễ hơn
- planning ổn định hơn

---

# 4. Relationship Mapping

ReasoningAgent phải hiểu:

- bảng nào liên quan
- foreign key nào dùng để JOIN
- choice table map ra sao

---

# 4.1 Metadata Awareness

ReasoningAgent không đoán schema.

Nó dùng:

```text
db.json metadata
```

để infer relationships.

---

# 4.2 Example Relationship Mapping

Input:

```text
Contacts thuộc Finance Accounts ở Vietnam
```

---

## Required Relationships

```text
hbl_contact
    ↓
hbl_account
    ↓
industry mapping
    ↓
country mapping
```

---

# 4.3 Example JOIN Reasoning

```text
hbl_contact.hbl_contact_accountid
    →
hbl_account.hbl_accountid
```

---

# 5. Logic Branching

ReasoningAgent quyết định:

- dùng SQL mới
- hay reuse memory pattern

---

# 5.1 Example Branching

## Simple Query

```text
→ Generate SQL directly
```

---

## Complex Nested Query

```text
→ Check Learning Memory
→ Reuse successful pattern
```

---

# 6. Model Selection

## Recommended Model

```text
groq/llama3-70b-8192
```

---

# 6.1 Why Groq

Reasoning cần:

- tốc độ cực nhanh
- CoT reasoning
- structured decomposition
- low latency

Groq phù hợp vì:

- LPU architecture
- ultra-fast inference
- near realtime reasoning

---

# 6.2 Recommended Temperature

```python
temperature = 0.1
```

Lý do:

- stable logic
- deterministic output
- ít hallucination

---

# 7. Structured Output Design

ReasoningAgent bắt buộc trả JSON.

---

# 7.1 Output Contract

```json
{
  "thought_process": "",
  "required_tables": [],
  "steps": [],
  "complexity": ""
}
```

---

# 7.2 Why Structured Reasoning Matters

Nếu output là text tự do:

- PlanningAgent khó parse
- khó automation
- khó debug

JSON giúp:

- deterministic orchestration
- machine-readable planning
- execution stability

---

# 8. Implementation

## File: `core/agents/reasoning.py`

```python
from litellm import completion

import json

def reasoning_agent_node(state):

    """
    ReasoningAgent:
    - query decomposition
    - relationship mapping
    - chain-of-thought reasoning
    """

    intent = state["intent"]

    refined_query = state["input"]

    schema_context = """

    Tables:
    - hbl_account
    - hbl_contact
    - hbl_opportunities
    - hbl_contract

    Relationships:
    - contact.accountid -> account.id
    - contract.opportunityid -> opportunity.id
    """

    prompt = f"""
    Bạn là ReasoningAgent.

    Nhiệm vụ:
    Phân tích logic CRM query.

    Context Schema:
    {schema_context}

    User Request:
    {refined_query}

    Intent:
    {intent}

    Hãy suy luận từng bước:

    1. Xác định bảng liên quan.
    2. Xác định JOIN path.
    3. Xác định filtering conditions.
    4. Nếu query lồng nhau:
       chia thành Step 1, Step 2...

    Trả về JSON:

    {{
        "thought_process": str,

        "required_tables": list,

        "steps": [
            {{
                "step": 1,
                "description": str,
                "target": "sql_generation"
            }}
        ],

        "complexity": "simple" | "nested"
    }}
    """

    response = completion(

        model="groq/llama3-70b-8192",

        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    logic_plan = json.loads(
        response.choices[0].message.content
    )

    # Build trace
    new_trace = {

        "node": "ReasoningAgent",

        "msg": (
            f"💡 Suy luận: "
            f"{logic_plan['thought_process'][:100]}..."
            f"(Complexity: "
            f"{logic_plan['complexity']})"
        )
    }

    return {

        "logic_plan": logic_plan,

        "trace": [new_trace],

        "next_step": "planning"
    }
```

---

# 9. Real-World Scenario

## User Question

```text
Thống kê doanh thu tháng 1 của các account
thuộc ngành Finance ở Vietnam
```

---

# 9.1 Reasoning Process

ReasoningAgent sẽ suy luận:

---

## Required Tables

```text
hbl_contract
hbl_account
sys_choice_options
```

---

## Logic Steps

```text
Step 1:
Resolve choice_code cho:
- Finance
- Vietnam

Step 2:
Join hbl_account với:
- industry mapping
- country mapping

Step 3:
Join account → opportunity → contract

Step 4:
SUM doanh thu tháng 1
```

---

# 9.2 Example Output JSON

```json
{
  "thought_process": "Need to resolve Finance and Vietnam labels into choice codes before joining account and contract tables.",

  "required_tables": [
    "hbl_account",
    "hbl_contract",
    "sys_choice_options"
  ],

  "steps": [
    {
      "step": 1,
      "description": "Resolve choice codes",
      "target": "sql_generation"
    },
    {
      "step": 2,
      "description": "Join account and contract tables",
      "target": "aggregation"
    }
  ],

  "complexity": "nested"
}
```

---

# 10. Chain-of-Thought (CoT)

Đây là đặc điểm cực kỳ quan trọng.

ReasoningAgent phải:

```text
explain WHY
```

không chỉ:

```text
generate output
```

---

# 10.1 Why CoT Matters

Giúp:

- debug nhanh
- explain AI decisions
- visualize reasoning
- reduce hallucination

---

# 10.2 Example CoT

```text
Need to resolve label Finance into choice_code first
because account table stores only codes.
```

---

# 11. Complexity Classification

ReasoningAgent phải đánh giá:

```text
simple
```

hoặc:

```text
nested
```

---

# 11.1 Simple Query Example

```text
List all accounts
```

→ `simple`

---

# 11.2 Nested Query Example

```text
Top revenue accounts in Vietnam ngành Finance
```

→ `nested`

---

# 12. Traceability

Mọi reasoning phải được trace.

---

# 12.1 Example Trace

```json
{
  "node": "ReasoningAgent",
  "msg": "💡 Suy luận: Resolve Finance label before JOIN..."
}
```

---

# 12.2 Streamlit Sidebar Example

```text
[ReasoningAgent]

Complexity: nested

Required Tables:
- hbl_account
- hbl_contract
- sys_choice_options

Execution Steps:
1. Resolve labels
2. Build JOIN path
3. Aggregate revenue
```

---

# 13. Integration with PlanningAgent

ReasoningAgent KHÔNG execute.

Nó chỉ:

- build logic plan
- handoff execution blueprint

---

# 13.1 Handoff Contract

PlanningAgent sẽ nhận:

```json
{
  "logic_plan": {}
}
```

để:

- build tasks
- prioritize execution
- generate workflow

---

# 14. Recommended Graph Flow

```text
START
  ↓
IngestAgent
  ↓
ReasoningAgent
  ↓
PlanningAgent
```

---

# 15. Suggested Folder Structure

```text
/core
├── agents/
│   ├── ingest.py
│   └── reasoning.py
│
├── prompts/
│   └── reasoning_prompt.py
│
├── graph/
│   └── graph.py
│
└── state.py
```

---

# 16. Recommended Future Improvements

| Current | Future |
|---|---|
| Static schema context | Dynamic schema retrieval |
| Simple CoT | Graph reasoning |
| Manual decomposition | Recursive planning |
| Static JOIN inference | Semantic relationship inference |

---

# 17. Testing Strategy

## Test Categories

| Test | Purpose |
|---|---|
| Decomposition test | Verify task splitting |
| JOIN reasoning test | Verify relationship mapping |
| Complexity test | Detect nested queries |
| CoT trace test | Verify explainability |

---

# 17.1 Example JOIN Test

```python
def test_join_reasoning():

    state = {
        "input": (
            "Contacts thuộc Finance accounts"
        ),
        "intent": "query"
    }

    result = reasoning_agent_node(state)

    assert (
        "hbl_account"
        in result["logic_plan"]["required_tables"]
    )
```

---

# 18. Phase 6 Completion Checklist

## Core Logic

- [ ] Implement `reasoning_agent_node`
- [ ] Connect Groq Llama3
- [ ] Parse structured JSON
- [ ] Append trace logs

---

## Query Reasoning

- [ ] Decompose nested queries
- [ ] Detect required tables
- [ ] Infer JOIN relationships
- [ ] Build execution steps

---

## Chain-of-Thought

- [ ] Generate explainable reasoning
- [ ] Save thought_process
- [ ] Display reasoning in UI

---

## Integration

- [ ] Pass logic_plan to PlanningAgent
- [ ] Maintain AgentState consistency
- [ ] Handle nested queries correctly

---

# 19. Expected Outcome After Phase 6

Sau khi hoàn thành:

Hệ thống sẽ có:

- Intelligent query decomposition
- Metadata-aware reasoning
- Dynamic relationship mapping
- Explainable AI reasoning
- Structured execution planning
- Ultra-fast Groq-powered thinking

AI Agent sẽ có khả năng:

- hiểu bài toán phức tạp
- tự bẻ nhỏ task
- tự xác định JOIN path
- explain logic reasoning
- build execution blueprint
- giảm hallucination SQL