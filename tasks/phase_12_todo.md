# Phase 12 To-Do: Advanced RAG & Knowledge Distillation

## 1. Multi-Step Retrieval (HyDE)
- [x] Implement `generate_hyde_answer` (Hypothetical Document Embeddings)
- [x] Update retrieval pipeline to search using HyDE generated text
- [x] Benchmark HyDE vs standard vector search accuracy

## 2. Dynamic Few-Shot Selector
- [x] Implement `DynamicFewShotSelector` to pull relevant SQL recipes
- [x] Create prompt formatter to inject recipes into `SQLGeneratorAgent`
- [x] Implement "Complexity-aware" example selection

## 3. Knowledge Distillation (Post-processing)
- [x] Implement `KnowledgeDistiller` to extract logic from successful queries
- [x] Update `LearningAgent` to save `reasoning_steps` and `tags` (JSONB)
- [x] Implement `QualityRanking` formula for stored patterns (Success rate + Complexity)

## 4. LangGraph Integration
- [x] Create `knowledge_retrieval_node` in the graph
- [x] Connect retrieval node to `PlanningAgent` and `ReasoningAgent`
- [x] Implement feedback loop to update pattern ratings in DB
