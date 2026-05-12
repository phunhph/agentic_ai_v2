# Phase 11 To-Do: Dynamic Context & Semantic Compression

## 1. Modular Prompt Engineering
- [x] Split monolithic system prompt into modular `Instruction Blocks`
- [x] Implement `Dynamic Prompt Builder` to assemble blocks based on task
- [x] Create `minimal_prompt` templates for speed-optimized requests

## 2. Token Budget Management
- [x] Implement `count_tokens` utility using tiktoken
- [x] Implement `TokenBudgetManager` to track consumption per session
- [x] Implement `filter_relevant_messages` to prune history based on token limits

## 3. Semantic Context Compression
- [x] Implement `ContextCompressor` node in LangGraph
- [x] Add LLM-based summarization for older conversation turns
- [x] Implement "Sliding Window" for raw message retention
- [x] Add `Coreference Resolver` (Phase 11 update) to preserve entity context after compression

## 4. Testing & Optimization
- [x] Measure token reduction % compared to raw history
- [x] Benchmark reasoning accuracy after compression
- [x] Optimize "Summary Refresh" trigger frequency
