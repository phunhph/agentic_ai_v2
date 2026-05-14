# Báo cáo hoàn thiện TODO roadmap

*Cập nhật: 2026-05-14*

Tài liệu này tổng hợp các hạng mục đã hoàn thành trong đợt cập nhật hiện tại, dựa trên `tasks/MASTER_PHASE_ROADMAP_TODO.md`, đồng thời chỉ ra phần còn lại theo mức ưu tiên.

---

## 1) Hạng mục đã hoàn thành trong đợt này

### Phase 5 — Reasoning & Planning

- Hoàn thiện **schema validation** cho output reasoning/planning bằng Pydantic contract.
- Bổ sung **contract handoff** từ planner sang execution qua schema chuẩn.
- Nâng cấp UI để hiển thị **realtime state**: reasoning/planning/execution/reflection.
- Thêm test contract:
  - `tests/test_phase5_contracts.py`

### Phase 6 — Execution, Reflection & Learning

- Triển khai **retry policy + backoff + error classification** trong runtime.
- Triển khai **self-healing loop** (retry có giới hạn trước khi kết thúc thất bại).
- Bổ sung **DLQ/failure bucket** khi vượt retry limit.
- Chuẩn hóa taxonomy lỗi thực thi (`timeout`, `rate limit`, `transient`, `logic`, `unknown`).
- Bổ sung **Dynamic Query Engine**:
  - `SchemaCatalog` đọc metadata DB và fallback sang semantic views.
  - `JoinGraph` tìm đường join qua FK/semantic edge.
  - `QueryPlan` chuẩn hóa truy vấn trước khi render SQL.
  - `QueryCompiler` validate bảng/cột/operator và render SQL an toàn.
- `ExecutionAgent` hiện ưu tiên dynamic compiled SQL, sau đó mới fallback sang rule/LLM raw SQL.
- Thêm test retry policy:
  - `tests/test_phase6_retry_policy.py`

### Kết quả test

- Chạy `python -m pytest tests/test_phase5_contracts.py tests/test_phase6_retry_policy.py`
- Kết quả: **4 passed**.

---

## 2) Thay đổi kỹ thuật chính (code-level)

- `core/schemas/agent_contracts.py`: khai báo contract model cho Reasoning/Planning.
- `core/agents/reasoning_agent.py`: validate output theo schema trước khi lưu checkpoint.
- `core/agents/planning_agent.py`: validate planning state trước khi lưu checkpoint.
- `core/graph/langgraph_runtime.py`:
  - thêm retry loop có backoff;
  - phân loại lỗi phục vụ retry decision;
  - ghi DLQ record khi thất bại sau retry.
- `core/query/`: thêm query engine mở rộng gồm catalog, join graph, query plan, compiler và planner.
- `core/tools/semantic_schema.py`: bổ sung relation cards gọn để giảm context schema gửi vào LLM.
- `core/agents/execution_agent.py`: tích hợp dynamic query compiler trước nhánh fallback.
- `apps/web/streamlit_app.py`: hiển thị realtime workflow states sau mỗi prompt.

---

## 3) Mục còn mở (ưu tiên cao → thấp)

### Ưu tiên cao

- Phase 8: E2E + regression + multi-tenant validation.
- Phase 8: Security checklist, RBAC governance, monitoring/alerting, UAT/sign-off.
- Phase 7: Validation test cases cho multi-tenant/RLS và dashboard observability.
- Dynamic query engine: bổ sung dry-run SQL (`EXPLAIN`/`LIMIT 0`) và repair loop theo lỗi có cấu trúc.

### Ưu tiên trung bình

- Phase 7: Cost guardrails + routing matrix theo budget thực tế.
- Phase 7: SLO/SLA và cảnh báo ngưỡng.
- Phase 6: Baseline metrics đầy đủ để làm đầu vào tối ưu pha 7.

### Ưu tiên duy trì liên tục

- CI bắt buộc trên PR (lint + unit + smoke E2E).
- Security review chu kỳ cho ingest + SQL path + log redaction.
- Kiểm tra định kỳ startup/migration rollback và compatibility API contract.

---

## 4) Đề xuất nhịp triển khai tiếp theo

1. Hoàn thiện dry-run validator và repair loop cho `QueryPlan`.
2. Chốt checklist Phase 7 (RLS tests + observability cockpit + SLO alert).
3. Mở gói hardening Phase 8 (security checklist + RBAC + production checklist).
4. Bổ sung pipeline CI chính thức để tự động hóa nghiệm thu roadmap.
