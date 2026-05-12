# Phase 13 To-Do: Self-Reflection & Multi-Turn Correction

## 1. Reflector Agent Implementation
- [x] Create `reflector_node` in LangGraph
- [x] Define Reflection Prompt for Senior Data QA Expert
- [x] Implement checks for:
    - [x] Logical alignment with User Intent
    - [x] JOIN condition validity
    - [x] suspicious empty results
    - [x] Aggregation logic correctness
- [x] Implement Confidence Scoring system

## 2. LangGraph Workflow Update
- [x] Update Graph edges to support the loop: `Execution -> Reflection -> (Retry -> Planning) or (Success -> Learning)`
- [x] Implement `retry_count` in AgentState to track reflection rounds
- [x] Implement `MAX_REFLECTION_ROUNDS` limit (e.g., 3 rounds) to avoid infinite loops
- [x] Implement fallback logic when retry budget is exhausted

## 3. Feedback-Driven Correction
- [x] Implement `error_feedback` extraction from ReflectorAgent
- [x] Update `PlanningAgent` and `SQLGeneratorAgent` to ingest and act on reflection feedback
- [x] Implement "Mistake Memory" within the current session state

## 4. Testing & Validation
- [x] Test self-correction on known "trick" queries (e.g., wrong JOINs)
- [x] Verify handling of "Legit Empty" vs "Suspicious Empty" results
- [x] Audit reasoning chains for multi-turn successful corrections
- [x] Measure improvement in SQL Reliability KPI
