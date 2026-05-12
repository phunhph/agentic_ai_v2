# Phase 10 To-Do: Context Monitoring & Logic Validation

## Context Intelligence
- [ ] Implement `ContextMonitor` node in LangGraph
- [ ] Resolve coreferences (giải quyết các đại từ "nó", "họ", "đó")
- [ ] Maintain session history (lưu trữ lịch sử hội thoại)
- [ ] Refine input query based on context

## Validation Layer
- [ ] Check reasoning vs execution consistency (kiểm tra sự logic giữa suy luận và kết quả)
- [ ] Detect hallucinated fields (phát hiện các trường dữ liệu "bịa")
- [ ] Re-validate schema usage (kiểm tra tính hợp lệ của schema)
- [ ] Implement Hallucination Guard rules

## Memory System
- [ ] Configure LangGraph checkpointing (Sử dụng Sqlite hoặc Postgres)
- [ ] Implement PostgreSQL session storage (Lưu vào audit_zone)
- [ ] History tracking (Theo dõi vết hội thoại nhiều lượt)

## Feedback Loop
- [ ] UI 👍/👎 integration (Tích hợp nút feedback vào Streamlit)
- [ ] Block bad learning data (Chặn dữ liệu rác không cho vào LearningAgent)
- [ ] Improve memory quality based on user feedback

## Testing & Audit
- [ ] Test Coreference resolution
- [ ] Test Logic Consistency
- [ ] Test Hallucination detection
- [ ] Full reasoning chain audit logging
