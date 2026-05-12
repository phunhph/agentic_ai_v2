# Phase 1 To-Do: System Architecture & Technical Specifications

## Infrastructure
- [x] Initialize project structure (apps, core, data, memory, tests)
- [x] Setup Flask API (Boilerplate)
- [x] Setup Streamlit UI (Boilerplate)
- [x] Setup PostgreSQL (Schema script)
- [x] Setup pgvector (Included in init.sql)

## Agentic Framework
- [x] Build LangGraph state machine (`core/graph/graph.py`)
- [x] Define AgentState
- [x] Implement 5 core agents (Skeletons)
- [x] Add retry logic (Conditional edges)

## Security
- [x] Implement RBAC (Restricted DB Role)
- [x] Add prompt hardening (Ingest filtering)
- [x] Add SQL validation (SELECT only)
- [x] Add audit logging (audit_zone)

## Observability
- [x] Setup LangSmith (Configured)
- [x] Setup Phoenix tracing (Implemented)
- [x] Add execution monitoring (Trace logs)

## Integration
- [x] Setup LiteLLM router (Configured)
- [x] Configure Groq (Env example)
- [x] Configure Gemini/OpenRouter (Env example)
- [x] Connect MCP server (Placeholder wrapper)
