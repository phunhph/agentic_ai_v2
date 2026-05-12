# Phase 3: Project Initialization & Traceable UI

## 1. Flask API (Backend Gateway)

Flask đóng vai trò:

- API Gateway
- Request Dispatcher
- Session Manager
- LangGraph Thread Controller

Mục tiêu:

- Quản lý các Thread của LangGraph
- Streaming trace log realtime
- Trả về execution state cho UI

---

# 1.1 Core Responsibilities

| Component | Responsibility |
|---|---|
| Flask API | Gateway nhận request |
| Thread Manager | Quản lý LangGraph thread |
| Trace Handler | Streaming log realtime |
| Session Layer | Quản lý user session |
| Response Formatter | Chuẩn hóa JSON response |

---

# 1.2 Main Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1/agent/chat` | POST | Gửi câu hỏi tới Agent |
| `/v1/agent/trace/<thread_id>` | GET | Lấy trạng thái Graph |
| `/v1/agent/health` | GET | Health check API |

---

# 1.3 app.py Responsibilities

## `/chat`

Responsibilities:

- Nhận user query
- Generate thread_id
- Initialize AgentState
- Trigger LangGraph execution
- Return response + trace log

---

## `/trace/<thread_id>`

Responsibilities:

- Query current graph state
- Return active node
- Return current model provider
- Return execution logs
- Return latency metrics

---

# 2. Streamlit UI (Traceable Interface)

Mục tiêu UI:

> Không chỉ chat với AI,
> mà còn "mổ xẻ" cách Agent suy nghĩ.

---

# 2.1 UI Philosophy

Người dùng sẽ thấy:

- AI đang ở Agent nào
- Model nào đang chạy
- SQL nào đang được generate
- Task planning diễn ra ra sao
- Latency từng bước

---

# 2.2 Main UI Components

| Component | Purpose |
|---|---|
| Chat Interface | Gửi câu hỏi |
| Agent Process Sidebar | Hiển thị execution flow |
| Code Debug Expander | Hiển thị SQL generated |
| Trace Timeline | Theo dõi graph execution |
| Latency Monitor | So sánh Groq vs Gemini |

---

# 2.3 Chat Interface

Ví dụ câu hỏi:

```text
Show all Finance accounts in Vietnam with active contracts
```

```text
Find contracts expiring next month
```

```text
Which AM manages the highest revenue accounts?
```

---

# 2.4 Agent Process Sidebar

Sidebar hiển thị realtime process.

Ví dụ:

```text
[Ingest]
Gemini 1.5 Flash đang phân tích câu hỏi...

[Reasoning]
Groq đang bóc tách thực thể...

[Planning]
BabyAGI đang lập execution plan...

[Execution]
Generating SQL query...

[Learning]
Saving execution memory...
```

---

# 2.5 Code Debug Expander

Hiển thị:

- SQL generated
- Tool execution
- Raw MCP payload
- Retry attempts
- Query latency

Ví dụ:

```sql
SELECT
    a.hbl_account_name,
    c.choice_label
FROM hbl_account a
JOIN hbl_account_industry_map m
    ON a.hbl_accountid = m.hbl_accountid
JOIN sys_choice_options c
    ON c.choice_code = m.choice_code
WHERE c.choice_label = 'Finance';
```

---

# 3. Tracing & Monitoring System

Mục tiêu:

- Full observability
- Agent debugging
- Replay execution
- Performance tuning
- Audit compliance

---

# 3.1 Trace Storage Strategy

Không chỉ print log.

Toàn bộ trace sẽ lưu vào PostgreSQL schema:

```text
audit_zone
```

---

# 3.2 Trace Table Structure

| Field | Description |
|---|---|
| trace_id | ID của execution session |
| agent_name | Agent đang chạy |
| model_provider | Gemini / Groq / OpenRouter |
| input_payload | Input của Agent |
| output_response | Output của Agent |
| latency | Thời gian xử lý |
| createdon | Timestamp |

---

# 3.3 Example Trace Table

```sql
CREATE TABLE audit_zone.agent_trace_logs (
    trace_id UUID PRIMARY KEY,

    agent_name TEXT,

    model_provider TEXT,

    input_payload JSONB,

    output_response JSONB,

    latency_ms INT,

    createdon TIMESTAMP DEFAULT NOW()
);
```

---

# 4. Standard Implementation

---

# 4.1 File: core/graph/state.py

## Shared AgentState

```python
from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):

    # User input
    query: str

    # Intent classification
    intent: str

    # BabyAGI execution plan
    plan: List[str]

    # Completed tasks
    steps_completed: List[str]

    # Final SQL generated
    sql_query: str

    # Database results
    results: List

    # Accumulated trace logs
    trace_log: Annotated[List[str], operator.add]
```

---

# 4.2 Why trace_log Uses operator.add

```python
Annotated[List[str], operator.add]
```

LangGraph sẽ:

- merge logs tự động
- append xuyên suốt graph
- giữ trace consistency

Ví dụ:

```text
[Ingest] Intent classified
[Reasoning] Entities extracted
[Planning] Task list generated
[Execution] SQL generated
```

---

# 4.3 File: apps/web/ui.py

## Streamlit UI

```python
import streamlit as st
import requests

st.title("🚀 Agentic CRM Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle user input
if prompt := st.chat_input(
    "Hỏi về Account hoặc Contract..."
):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.spinner("Agentic đang tư duy..."):

        response = requests.post(
            "http://localhost:5000/v1/agent/chat",
            json={"query": prompt}
        )

        data = response.json()

        # Sidebar trace logs
        with st.sidebar:

            st.subheader("🕵️ Agent Trace Log")

            for log in data["trace_log"]:
                st.info(log)

        st.session_state.messages.append({
            "role": "assistant",
            "content": data["answer"]
        })

        st.rerun()
```

---

# 4.4 Example Flask API

## File: apps/api/app.py

```python
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

@app.route("/v1/agent/chat", methods=["POST"])
def chat():

    payload = request.json

    query = payload.get("query")

    thread_id = str(uuid.uuid4())

    trace_log = [
        "[Ingest] Gemini analyzing query...",
        "[Reasoning] Groq extracting entities...",
        "[Planning] Building BabyAGI task list...",
        "[Execution] Generating SQL..."
    ]

    return jsonify({
        "thread_id": thread_id,
        "answer": f"Processed query: {query}",
        "trace_log": trace_log
    })

@app.route("/v1/agent/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

---

# 5. Recommended Initial LangGraph Flow

Phase 3 chưa cần logic thật.

Mục tiêu chỉ cần:

- chạy graph
- chuyển node
- update state
- hiển thị trace

---

# 5.1 Initial Graph Topology

```text
START
  ↓
IngestNode
  ↓
ReasoningNode
  ↓
PlanningNode
  ↓
ExecutionNode
  ↓
END
```

---

# 5.2 Example Fake Trace Flow

```text
[Ingest]
Intent detected: REPORT_QUERY

[Reasoning]
Entities:
- Finance
- Vietnam
- Active Contracts

[Planning]
Generated 4 tasks

[Execution]
SQL query generated successfully
```

---

# 6. Real-Time Trace Strategy

Sau này có thể nâng cấp:

| Feature | Future Upgrade |
|---|---|
| Polling | WebSocket Streaming |
| Fake logs | Real LangGraph callbacks |
| Basic sidebar | Interactive graph UI |
| Static trace | Live execution timeline |

---

# 7. Recommended Folder Structure

```text
/project-root
├── apps/
│   ├── api/
│   │   └── app.py
│   │
│   └── web/
│       └── ui.py
│
├── core/
│   ├── agents/
│   ├── graph/
│   │   └── state.py
│   │
│   └── tools/
│
├── audit/
│   └── trace_logger.py
│
├── tests/
│
├── requirements.txt
└── docker-compose.yml
```

---

# 8. Phase 3 Completion Checklist

## Backend

- [ ] Flask API chạy trên port 5000
- [ ] `/chat` endpoint hoạt động
- [ ] `/trace/<thread_id>` hoạt động
- [ ] JSON response chuẩn hóa

---

## Frontend

- [ ] Streamlit UI chạy thành công
- [ ] UI kết nối Flask API
- [ ] Chat history hoạt động
- [ ] Sidebar trace hiển thị realtime

---

## LangGraph

- [ ] Graph khởi tạo thành công
- [ ] Node flow hoạt động
- [ ] AgentState update được
- [ ] Trace log append được

---

## Monitoring

- [ ] Fake trace logs hiển thị
- [ ] PostgreSQL audit table tạo thành công
- [ ] Trace persistence hoạt động

---

# 9. Expected Outcome After Phase 3

Sau khi hoàn thành:

Hệ thống sẽ có:

- Functional Flask backend
- Traceable Streamlit UI
- Initial LangGraph workflow
- Realtime execution sidebar
- SQL debugging interface
- Audit logging foundation

Người dùng sẽ thấy được:

- AI đang suy nghĩ gì
- AI đang gọi model nào
- SQL nào đang được generate
- Task planning diễn ra ra sao
- Execution flow giữa các Agent