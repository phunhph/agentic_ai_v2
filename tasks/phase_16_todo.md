# Phase 16 To-Do: Semantic Schema Pruning (RAG for DB Structure)

## 1. Metadata Vectorization Pipeline
- [x] Implement `Metadata Extractor` to generate text descriptions for tables and columns
- [x] Create `knowledge_zone.schema_metadata` table with `pgvector` support
- [x] Implement sync script to vectorize and store DB structure as semantic documents
- [x] Add support for relationship-aware metadata (Foreign Keys)

## 2. Schema Pruner Node (LangGraph)
- [x] Create `schema_pruner_node` in LangGraph
- [x] Implement Semantic Search against `schema_metadata` based on User Query
- [x] Implement `Top-K` table selection logic (e.g., retrieve top 3-5 relevant tables)
- [x] Implement Dynamic Mini-schema Builder to format selected tables for the prompt

## 3. LangGraph Integration
- [x] Update Agent workflow: `User Input -> Schema Pruner -> (Planner/Reasoning)`
- [x] Update `AgentState` to hold `current_schema` instead of using a global full schema
- [x] Implement "Relationship-aware" expansion (automatically include tables linked by FKs to selected tables)

## 4. Testing & Optimization
- [x] Benchmark Token Reduction (Target: ~90% reduction in schema tokens)
- [x] Verify SQL Accuracy on large DB structures (100+ tables simulation)
- [x] Test "Semantic Distraction" reduction (AI ignoring irrelevant tables)
- [x] Implement Auto-sync trigger on DB schema changes
