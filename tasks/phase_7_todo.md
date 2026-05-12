# Phase 7 To-Do: PlanningAgent Layer (BabyAGI Pattern)

## Core Planning
- [x] Implement `planning_agent_node`
- [x] Connect Gemini Flash (via litellm)
- [x] Generate structured todo list
- [x] Save task queue into AgentState

## Task Management
- [x] Create dependency-aware tasks
- [x] Prioritize execution order
- [x] Track task status (status: "TODO")
- [ ] Support nested workflows

## Recursive Planning
- [x] Implement loop-back from Execution errors (via LangGraph)
- [x] Self-healing workflow logic (AI-assisted Planning with error context)
- [x] Task re-prioritization on failure
