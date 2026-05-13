# Master roadmap & to-do theo phase

*Living document — phạm vi: toàn bộ file `plans/phase_*.md` hiện có trong repo.*

Tài liệu liệt kê **công việc cần làm lần lượt** theo thứ tự phase trong `plans/`. Mỗi phase gồm: **mục tiêu**, **gói giao hàng (deliverables)** và **tiêu chí nghiệm thu** trích từ plan tương ứng.

**Quy ước checkbox:** dùng `- [ ]` cho hạng mục còn việc; đội dự án đánh dấu `- [x]` khi hoàn thành và gắn link PR/commit nếu cần.

> **Lưu ý tên file:** `phase_5_ingest_agent.md` chứa nội dung **Phase 5 — Reasoning & Planning** (không phải Ingest). Luôn đối chiếu cột *Tiêu đề plan* bên dưới.

---

## Bảng ánh xạ nhanh

| STT | File trong `plans/` | Tiêu đề nội dung |
|-----|---------------------|-----------------|
| 1 | `phase_1_architecture.md` | Infrastructure & Data Foundation |
| 2 | `phase_2_database_migration.md` | UI, API Gateway & Observability |
| 3 | `phase_3_ui_and_tracing.md` | MCP, LLM Orchestration & Secure Tooling |
| 4 | `phase_4_tools_and_security.md` | Ingest Layer & Context Nexus |
| 5 | `phase_5_ingest_agent.md` | Reasoning & Planning Layers |
| 6 | `phase_6_reasoning_agent.md` | Execution, Reflection & Continuous Learning |
| 7 | `phase_7_planning_agent.md` | Lean Optimization & Scalability |
| 8 | `phase_8_execution_agent.md` | Finalization, Governance & Project Closure |

---

## Phase 1 — Infrastructure & Data Foundation

**Mục tiêu:** Nền móng repo, PostgreSQL, semantic abstraction, migration Dataverse → Postgres.

### Deliverables

- [ ] Cấu trúc thư mục `apps/`, `core/`, `data/`, `tests/`, `docs/` đúng chuẩn đã thống nhất
- [ ] `requirements.txt` / lockfile đủ dependency orchestration (LangGraph, LiteLLm, DB driver, v.v.)
- [ ] `.env.example` đầy đủ biến DB + AI providers
- [ ] `data/schema/` khởi tạo schema zones (`business_zone`, `knowledge_zone`, `audit_zone`) + extension cần thiết
- [ ] Chiến lược migration Dataverse → PostgreSQL (script hoặc pipeline) được tài liệu hóa
- [ ] Semantic / AI-friendly views (ví dụ `v_hbl_*`) theo naming convention trong plan

### Tiêu chí nghiệm thu

- [ ] Cài đặt môi trường mới có thể chạy `init` schema thành công
- [ ] Tài liệu ngắn mô tả luồng dữ liệu và semantic layer trong `docs/`

**Phụ thuộc:** không có.

---

## Phase 2 — UI, API Gateway & Observability Layer

**Mục tiêu:** Lớp tương tác người–máy, API trung tâm, quan sát & audit sớm.

### Deliverables

- [ ] Flask API: nhận payload, quản lý `thread_id` / session, gọi LangGraph, trả kết quả + trace
- [ ] Streamlit: chat, markdown, bảng kết quả, hiển thị tiến trình / SQL debug / trace (theo mức plan)
- [ ] Observability: API có điểm mở rộng cho trace, health
- [ ] Ghi `audit_zone` (execution log) theo contract thống nhất với code hiện tại (`agent_logs`, v.v.)

### Tiêu chí nghiệm thu

- [ ] Một luồng end-to-end: UI hoặc REST → graph → response
- [ ] Log có thể truy vấn lại để debug phiên

**Phụ thuộc:** Phase 1 (schema + DB).

---

## Phase 3 — MCP, LLM Orchestration & Secure Tooling

**Mục tiêu:** Công cụ chuẩn hóa, router đa model, schema retrieval gọn, policy bảo mật.

### Deliverables

- [ ] Lớp tool DB/MCP thống nhất; deny-by-default; audit mọi execution quan trọng
- [ ] LiteLLM Router (hoặc tương đương): fallback, tier model
- [ ] Semantic schema retrieval — chỉ inject phần schema liên quan câu hỏi
- [ ] Security & execution policy: role DB giới hạn, không secrets trong log

### Tiêu chí nghiệm thu

- [ ] Agent không gọi SQL “trần” ngoài pipeline tool đã định nghĩa
- [ ] Đổi model/provider không phá API contract

**Phụ thuộc:** Phase 2.

---

## Phase 4 — Ingest Layer & Context Nexus

**Mục tiêu:** Gatekeeper đầu vào; Context Nexus (checkpoint, thread isolation, replay).

### Deliverables

- [ ] IngestAgent: normalize, intent, entity, security (injection / probing)
- [ ] Context Nexus: checkpoint state, thread isolation, khả năng resume/replay (theo độ sâu plan)
- [ ] AgentState sạch cho downstream

### Tiêu chí nghiệm thu (theo plan Phase 4)

- [ ] Input normalize chính xác; intent ổn định; entity đúng
- [ ] Prompt injection bị chặn; checkpoint hoạt động; thread isolation hoạt động
- [ ] State replay được; reasoning nhận structured state sạch

**Phụ thuộc:** Phase 3.

---

## Phase 5 — Reasoning & Planning Layers

*(Nội dung trong file `phase_5_ingest_agent.md`)*

**Mục tiêu:** ReasoningAgent + PlanningAgent; không sinh SQL ở tầng reasoning; plan có thứ tự & dependency.

### Deliverables

- [ ] ReasoningAgent: phân rã bài toán, mapping quan hệ, complexity, output JSON có cấu trúc
- [ ] PlanningAgent: task queue BabyAGI-style, dependency, readiness
- [ ] Tích hợp LangGraph; commit state vào Nexus liên tục
- [ ] UI hiển thị reasoning/planning realtime (nếu trong scope UI)

### Tiêu chí nghiệm thu (theo plan Phase 5)

- [ ] Reasoning đúng bài toán; planning tạo task queue rõ; dependency đúng
- [ ] Không sinh SQL ở reasoning layer
- [ ] Execution chỉ nhận structured plan

**Phụ thuộc:** Phase 4.

---

## Phase 6 — Execution, Reflection & Continuous Learning

**Mục tiêu:** Thực thi SQL an toàn; Reflector; vòng retry; học từ thành công/thất bại; pgvector.

### Deliverables

- [ ] ExecutionAgent: tiêu thụ plan, sinh SQL, gọi tool, bắt lỗi
- [ ] ReflectorAgent: logic/data/alignment; quyết định retry / finish
- [ ] Self-healing loop trong graph (giới hạn retry)
- [ ] LearningAgent + lưu pattern / vector (`knowledge_zone`)
- [ ] Audit: execution / reflection / learning

### Tiêu chí nghiệm thu (theo plan Phase 6)

- [ ] Task queue chạy đúng; SQL an toàn; reflector phát hiện lỗi logic
- [ ] Retry có kiểm soát; loop-back khi cần
- [ ] Memory thành công/thất bại; pgvector tra cứu pattern
- [ ] Toàn bộ hành vi có audit và trace rõ

**Phụ thuộc:** Phase 5.

---

## Phase 7 — Lean Optimization & Scalability

**Mục tiêu:** Nén context, cost-aware routing, resilience, observability cockpit, RLS, multi-tenant, DANN/local inference (theo plan).

### Deliverables

- [ ] Context compression / schema pruning / summarization history
- [ ] Cost guardrails + routing matrix + budget
- [ ] Resilience: backoff, circuit breaker (nếu trong scope), graceful degradation
- [ ] Observability cockpit: cost, bottleneck, failure analytics, feedback
- [ ] PostgreSQL RLS + tenant-aware execution; isolation MCP/agent

### Tiêu chí nghiệm thu (theo plan Phase 7)

- [ ] Context nén hiệu quả; token usage giảm đo được
- [ ] Routing theo cost policy; fallback ổn định
- [ ] Dashboard observability; latency đo full pipeline
- [ ] RLS đúng; multi-tenant isolation an toàn
- [ ] Local DANN / lightweight inference đạt latency mục tiêu (khi triển khai)

**Phụ thuộc:** Phase 6.

---

## Phase 8 — Finalization, Governance & Project Closure

**Mục tiêu:** Hardening, bảo mật cuối, RBAC, deploy, backup, tài liệu, handover, đóng dự án vận hành.

### Deliverables

- [ ] E2E + regression + multi-tenant validation
- [ ] Security checklist; secret management; tách môi trường
- [ ] RBAC; audit governance; change management
- [ ] Production checklist; infra validation; backup & recovery
- [ ] Monitoring, alerting, incident process
- [ ] Gói tài liệu: kiến trúc, developer, operations, business
- [ ] Versioning, release notes, runbooks (`rollback`, `incident_response`, `recovery`)
- [ ] Thư mục đích bổ sung: `runbooks/`, `scripts/deploy|backup|monitor`, `docs/deployment`, `data/backups`

### Tiêu chí nghiệm thu (theo plan Phase 8)

- [ ] Workflow ổn định; retry/fallback đúng; observability đủ
- [ ] RLS hoạt động đúng (đồng bộ Phase 7)
- [ ] Documentation hoàn chỉnh; deployment & recovery pass; governance pass; handover pass

**Phụ thuộc:** Phase 7.

---

## Hạng mục xuyên suốt (ongoing)

- [ ] Đồng bộ `plans/` ↔ `tasks/*.md` phase cũ (nếu có) với master này
- [ ] CI chạy test tối thiểu trên PR
- [ ] Security review định kỳ trên ingest + SQL path

---

## Phần mở rộng ngoài `plans/` hiện tại

Trong workspace **chỉ có** các file `phase_1` … `phase_8`. Nếu sau này bổ sung thêm plan (ví dụ phase 9+), nên:

1. Thêm file vào `plans/`
2. Thêm mục tương ứng vào cuối tài liệu này
3. Cập nhật `PROJECT_FINAL_STRUCTURE.md` mục ánh xạ phase

---

*Tài liệu được tạo tự động từ nội dung các plan Phase 1–8; chỉnh sửa trực tiếp trên repo khi scope thay đổi.*
