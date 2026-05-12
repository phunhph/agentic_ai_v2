# Phase 10 To-Do: Context Monitoring & Logic Validation

## Context Intelligence
- [x] Implement `ContextMonitor` node in LangGraph
- [x] Resolve coreferences (giải quyết các đại từ "nó", "họ", "đó")
- [x] Maintain session history (lưu trữ lịch sử hội thoại)
- [x] Refine input query based on context

## Validation Layer
- [x] Check reasoning vs execution consistency (kiểm tra sự logic giữa suy luận và kết quả)
- [x] Detect hallucinated fields (phát hiện các trường dữ liệu "bịa")
- [x] Re-validate schema usage (kiểm tra tính hợp lệ của schema)
- [x] Implement Hallucination Guard rules

## Memory System
- [x] Configure LangGraph checkpointing (Sử dụng Sqlite hoặc Postgres)
- [x] Implement PostgreSQL session storage (Lưu vào audit_zone)
- [x] History tracking (Theo dõi vết hội thoại nhiều lượt)

## Feedback Loop
- [x] UI 👍/👎 integration (Tích hợp nút feedback vào Streamlit)
- [x] Block bad learning data (Chặn dữ liệu rác không cho vào LearningAgent)
- [x] Improve memory quality based on user feedback

## Testing & Audit
- [x] Test Coreference resolution
- [x] Test Logic Consistency
- [x] Test Hallucination detection
- [x] Full reasoning chain audit logging
