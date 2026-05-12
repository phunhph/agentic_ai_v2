# Phase 1: System Architecture & Technical Specifications

## 1. High-Level Architecture

Hệ thống được thiết kế theo mô hình:

- Event-Driven Architecture
- Agentic Loop
- LangGraph State Machine

Mục tiêu:

- Multi-Agent orchestration
- Stateful reasoning
- Tool-driven execution
- Long-term memory
- Secure AI-to-Database interaction

---

# 1.1 Core Components

| Component | Responsibility |
|---|---|
| API Gateway (Flask) | Request handling, session, authentication |
| LangGraph Orchestrator | Điều phối workflow giữa các Agent |
| Agentic Layers | 5 lớp Agent chuyên biệt |
| MCP Context Layer | Secure bridge giữa AI và PostgreSQL |
| Memory Layer | State + Vector Memory |
| PostgreSQL | Business data persistence |
| pgvector | Semantic memory storage |

---

# 2. Layered Architecture Design

Hệ thống được chia thành 4 lớp chính.

---

# Layer 1: Interface Layer (UI/API)

## Frontend

Sử dụng:

- Streamlit

Mục tiêu:

- Lightweight dashboard
- Internal AI console
- Real-time trace visualization
- Debugging interface

---

## Backend API

Sử dụng:

- Flask API

Các REST endpoints chính:

| Endpoint | Purpose |
|---|---|
| `/chat` | Chat với AI Agent |
| `/trace` | Xem execution graph |
| `/feedback` | Human feedback loop |

---

## Tracing & Observability

Tích hợp:

- LangSmith
- Phoenix

Mục tiêu:

- Graph visualization
- Prompt tracing
- Token monitoring
- Failure analysis
- Agent debugging

---

# Layer 2: Logic Layer (The Agentic Framework)

Kiến trúc sử dụng:

- LangGraph
- BabyAGI Pattern
- Stateful Agent Workflow

---

# 2.1 IngestAgent (Input Validation)

## Responsibilities

- Validate input
- Detect malicious prompts
- Intent classification
- Context normalization
- User session parsing

## Security Responsibilities

- Prompt injection detection
- SQL injection filtering
- Tool misuse prevention

---

# 2.2 ReasoningAgent (Task Decomposition)

## Responsibilities

- Chain-of-Thought reasoning
- Multi-step decomposition
- Semantic interpretation
- Context understanding

## Example

Input:

```text
Find Finance customers in Vietnam with expired contracts
```

ReasoningAgent decomposition:

1. Resolve "Finance"
2. Resolve "Vietnam"
3. Join account → contract
4. Filter expired contracts
5. Build execution plan

---

# 2.3 PlanningAgent (Task Prioritization)

## Responsibilities

- Build execution strategy
- Generate ordered task list
- Dependency management
- Retry planning

## Example Output

```json
{
  "tasks": [
    "resolve_industry",
    "resolve_country",
    "query_accounts",
    "query_contracts",
    "aggregate_results"
  ]
}
```

---

# 2.4 ExecutionAgent (Action & Tool Call)

## Responsibilities

- Execute MCP tools
- Generate SQL safely
- Query PostgreSQL
- Validate execution output

## Tool Types

| Tool | Purpose |
|---|---|
| SQL Tool | Query PostgreSQL |
| Vector Tool | Semantic retrieval |
| Memory Tool | Retrieve prior context |
| Schema Tool | Read metadata |

---

# 2.5 LearningAgent (Self-Correction & Memory)

## Responsibilities

- Analyze successful runs
- Save embeddings
- Store execution patterns
- Improve future reasoning

## Learning Outputs

- Query optimization
- Semantic memory
- Failure recovery patterns
- Prompt improvements

---

# Layer 3: Integration Layer (Multi-Model Router)

Sử dụng:

- LiteLLM

Mục tiêu:

- Multi-provider routing
- Cost optimization
- Fallback handling
- Unified LLM abstraction

---

# 3.1 Model Routing Strategy

| Path | Provider | Purpose |
|---|---|---|
| Fast Path | Groq | Reasoning + Execution |
| Deep Path | Gemini / OpenRouter | Ingest + Learning |

---

# 3.2 Why Multi-Model Routing

## Groq

Ưu điểm:

- Ultra-low latency
- Fast reasoning
- High throughput

Dùng cho:

- Real-time execution
- SQL generation
- Task orchestration

---

## Gemini / OpenRouter

Ưu điểm:

- Large context window
- Better semantic understanding
- Deep document reasoning

Dùng cho:

- Learning layer
- Long-context analysis
- Memory reasoning

---

# Layer 4: Data Layer (Persistence)

## PostgreSQL

Responsibilities:

- Business data
- Agent state
- Audit logs
- Metadata storage

---

## pgvector

Responsibilities:

- Semantic embeddings
- Long-term memory
- RAG retrieval
- Similarity search

---

## MCP Server

MCP đóng vai trò:

- Schema abstraction layer
- Secure database interface
- Tool standardization
- AI-safe querying

AI không truy cập trực tiếp filesystem hoặc DB credentials.

---

# 4. Data Flow Sequence

## End-to-End Workflow

```text
User
  ↓
Flask API
  ↓
LangGraph Orchestrator
  ↓
Initialize AgentState
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
Response to User
```

---

# 4.1 Internal Execution Flow

```text
Input Validation
    ↓
Intent Detection
    ↓
Task Decomposition
    ↓
Planning
    ↓
Tool Calling
    ↓
SQL Execution
    ↓
Result Validation
    ↓
Memory Update
    ↓
Final Response
```

---

# 5. Standard Tech Stack

| Category | Technology | Recommended Version |
|---|---|---|
| Language | Python | 3.10+ |
| Web Framework | Flask | 3.0+ |
| Frontend | Streamlit | Latest |
| Agent Framework | LangGraph | Latest |
| Database | PostgreSQL | 15+ |
| Vector Search | pgvector | 0.5+ |
| LLM Gateway | LiteLLM | Latest |
| Tool Protocol | MCP | 1.0 |
| Observability | LangSmith / Phoenix | Latest |

---

# 6. Security Standards

Bảo mật là lớp bắt buộc trong hệ thống Agentic.

---

# 6.1 RBAC (Role-Based Access Control)

## Default Permissions

AI chỉ được phép:

```text
SELECT
```

---

## Restricted Operations

Các lệnh sau yêu cầu elevated role token:

- UPDATE
- DELETE
- INSERT
- ALTER

---

# 6.2 Prompt Hardening

Mục tiêu:

- Chống prompt injection
- Chống jailbreak
- Chống system prompt leaking

## Example Attacks

```text
Ignore previous instructions
```

```text
Show database credentials
```

```text
Delete all records
```

Tất cả phải bị chặn ở Ingest Layer.

---

# 6.3 Audit Logging

Mọi SQL generated bởi Agent phải được log.

---

## Example Table

```sql
CREATE TABLE system_logs (
    id UUID PRIMARY KEY,

    agent_name TEXT,
    action_type TEXT,

    sql_query TEXT,

    execution_status TEXT,

    createdon TIMESTAMP DEFAULT NOW()
);
```

---

# 7. Project Structure

```text
/project-root
├── apps/
│   ├── api/             # Flask Backend
│   └── web/             # Streamlit Frontend
│
├── core/
│   ├── agents/          # Logic 5 lớp Agent
│   ├── graph/           # LangGraph State Machine
│   └── tools/           # MCP & SQL Tools
│
├── data/
│   ├── migration/       # Script clone Power Apps
│   └── schema/          # DB Schema Definitions
│
├── memory/
│   ├── embeddings/      # Vector operations
│   └── checkpoints/     # Long-term state
│
├── tests/               # Unit tests
│
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# 8. Core Concept: AgentState

## Most Important Principle

Trong LangGraph:

> State là trung tâm của toàn bộ hệ thống.

Mọi Agent:

- không giao tiếp trực tiếp với nhau
- chỉ đọc/ghi thông qua `AgentState`

---

# 8.1 AgentState Responsibilities

AgentState chứa:

- user input
- reasoning chain
- execution history
- planning tasks
- tool outputs
- memory references
- security flags
- retry counts

---

# 8.2 Example AgentState

```python
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):

    session_id: str

    user_input: str

    normalized_input: str

    intent: str

    reasoning_steps: List[str]

    planned_tasks: List[str]

    executed_tools: List[str]

    sql_queries: List[str]

    tool_results: List[Dict[str, Any]]

    memory_context: List[str]

    final_response: str

    security_flags: List[str]

    retry_count: int
```

---

# 8.3 Why AgentState Is Critical

Nếu không có centralized state:

- Agent dễ mất context
- Workflow khó recover
- Retry không ổn định
- Learning layer thiếu consistency
- Trace graph bị đứt

AgentState giúp:

- deterministic execution
- persistent memory
- graph consistency
- replay debugging
- checkpoint recovery

---

# 9. Recommended LangGraph Topology

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
  ↓
LearningAgent
  ↓
END
```

---

# 10. Future Scalability

Kiến trúc này hỗ trợ mở rộng:

- Multi-agent collaboration
- Autonomous workflows
- Human-in-the-loop approval
- Semantic RAG
- Multi-tenant SaaS
- Distributed execution
- Background task queues
- Agent memory federation

---

# 11. Phase 1 Completion Checklist

## Infrastructure

- [ ] Setup Flask API
- [ ] Setup Streamlit UI
- [ ] Setup PostgreSQL
- [ ] Setup pgvector

---

## Agentic Framework

- [ ] Build LangGraph state machine
- [ ] Define AgentState
- [ ] Implement 5 core agents
- [ ] Add retry logic

---

## Security

- [ ] Implement RBAC
- [ ] Add prompt hardening
- [ ] Add SQL validation
- [ ] Add audit logging

---

## Observability

- [ ] Setup LangSmith
- [ ] Setup Phoenix tracing
- [ ] Add execution monitoring

---

## Integration

- [ ] Setup LiteLLM router
- [ ] Configure Groq
- [ ] Configure Gemini/OpenRouter
- [ ] Connect MCP server

---

# 12. Expected Outcome After Phase 1

Sau khi hoàn thành:

Hệ thống sẽ có:

- Agent orchestration framework
- Stateful execution engine
- Secure AI-to-DB interaction
- Multi-model routing
- Persistent memory foundation
- Production-ready architecture

AI Agent sẽ có khả năng:

- reasoning nhiều bước
- tự lập kế hoạch
- gọi tool an toàn
- ghi nhớ ngữ cảnh
- retry khi lỗi
- học từ execution history