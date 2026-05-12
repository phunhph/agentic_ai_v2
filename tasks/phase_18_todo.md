# Phase 18 To-Do: Self-Correction & Error-Based Learning

## 1. Failure Capture System
- [x] Implement triggers for capturing failures from:
    - [x] ReflectorAgent detections
    - [x] PostgreSQL execution errors
    - [x] User negative feedback
    - [x] Empty result heuristics
- [x] Implement `Failure Capture` logic to snapshot the query, SQL, reason, and schema

## 2. Error Memory (Negative Knowledge)
- [x] Implement `Error Distillation` using LLM to extract "Pitfalls" from raw failures
- [x] Create `knowledge_zone.failed_patterns` table with `pgvector`
- [x] Implement storage pipeline for distilled "Painful Mistakes"

## 3. Negative RAG Implementation
- [x] Implement `Negative Retrieval` step before SQL generation
- [x] Create `Warning Constraint Builder` from retrieved past failures
- [x] Inject specific warnings (e.g., "Avoid joining X on Y", "Column Z does not exist") into Reasoning prompt

## 4. Self-Healing Reasoning
- [x] Update `ReasoningAgent` to ingest `negative_constraints`
- [x] Implement `Dual-memory` architecture (Positive + Negative RAG)
- [x] Create `Error Clustering` logic to detect weak schema/logic areas

## 5. Testing & Evaluation
- [x] Verify AI avoids repeated hallucinations (e.g., wrong column names)
- [x] Measure reduction in "Repeat Errors" KPI
- [x] Audit the improvement of AI's "Self-healing" behavior over time
