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

- [x] Cấu trúc thư mục `apps/`, `core/`, `data/`, `tests/`, `docs/` đúng chuẩn đã thống nhất
- [x] `requirements.txt` / lockfile đủ dependency orchestration (LangGraph, LiteLLm, DB driver, v.v.)
- [x] Lockfile dependency được duy trì (`poetry.lock`, `requirements.lock`, hoặc tương đương)
- [x] `.env.example` đầy đủ biến DB + AI providers và chỉ dẫn cách sử dụng
- [x] `data/schema/` khởi tạo schema zones (`business_zone`, `knowledge_zone`, `audit_zone`) + extension cần thiết
- [x] `docker-compose` / startup script dev để chạy schema init và môi trường dev
- [x] Chiến lược migration Dataverse → PostgreSQL (script hoặc pipeline) được tài liệu hóa
- [x] Semantic / AI-friendly views (ví dụ `v_hbl_*`) theo naming convention trong plan

### Tiêu chí nghiệm thu

- [x] Cài đặt môi trường mới có thể chạy `init` schema thành công
- [x] Dev setup chạy được qua `docker-compose` / startup script và init schema
- [x] Tài liệu ngắn mô tả luồng dữ liệu và semantic layer trong `docs/`

**Phụ thuộc:** không có.

---

## Phase 2 — UI, API Gateway & Observability Layer

**Mục tiêu:** Lớp tương tác người–máy, API trung tâm, quan sát & audit sớm.

### Deliverables

- [x] Flask API: nhận payload, quản lý `thread_id` / session, gọi LangGraph, trả kết quả + trace
- [x] Streamlit: chat, markdown, bảng kết quả, hiển thị tiến trình / SQL debug / trace (theo mức plan)
- [x] Observability: API có điểm mở rộng cho trace, health
- [x] API contract rõ: `health`, `ready`, trace payload, session/thread context
- [x] Ghi `audit_zone` (execution log) theo contract thống nhất với code hiện tại (`agent_logs`, v.v.)

### Tiêu chí nghiệm thu

- [x] Một luồng end-to-end: UI hoặc REST → graph → response
- [x] `health` / `ready` endpoint và trace format test pass
- [x] Log có thể truy vấn lại để debug phiên

**Phụ thuộc:** Phase 1 (schema + DB).

---

## Phase 3 — MCP, LLM Orchestration & Secure Tooling

**Mục tiêu:** Công cụ chuẩn hóa, router đa model, schema retrieval gọn, policy bảo mật.

### Deliverables

- [x] Lớp tool DB/MCP thống nhất; deny-by-default; audit mọi execution quan trọng
- [x] LiteLLM Router (hoặc tương đương): fallback, tier model
- [x] Semantic schema retrieval — chỉ inject phần schema liên quan câu hỏi
- [x] Security & execution policy: role DB giới hạn, không secrets trong log
- [x] deny-by-default cho tool/SQL access và audit mọi execution quan trọng
- [x] Log redaction secrets và policy ghi log an toàn

### Tiêu chí nghiệm thu

- [x] Agent không gọi SQL “trần” ngoài pipeline tool đã định nghĩa
- [x] Đổi model/provider không phá API contract
- [x] Secrets không xuất trong log; policy audit hoạt động

**Phụ thuộc:** Phase 2.

---

## Phase 4 — Ingest Layer & Context Nexus

**Mục tiêu:** Gatekeeper đầu vào; Context Nexus (checkpoint, thread isolation, replay).

### Deliverables

- [x] IngestAgent: normalize, intent, entity, security (injection / probing)
- [x] Context Nexus: checkpoint state, thread isolation, khả năng resume/replay (theo độ sâu plan)
- [x] Checkpoint persist vào DB/storage và resume/replay flow rõ
- [x] Thread isolation cho nhiều user/session
- [x] AgentState sạch cho downstream

### Tiêu chí nghiệm thu (theo plan Phase 4)

- [x] Input normalize chính xác; intent ổn định; entity đúng
- [x] Prompt injection bị chặn; checkpoint hoạt động; thread isolation hoạt động
- [x] Resume/replay checkpoint validated; reasoning nhận structured state sạch

**Phụ thuộc:** Phase 3.

---

## Phase 5 — Reasoning & Planning Layers

*(Nội dung trong file `phase_5_ingest_agent.md`)*

**Mục tiêu:** ReasoningAgent + PlanningAgent; không sinh SQL ở tầng reasoning; plan có thứ tự & dependency.

**Điểm nối từ Phase 4:** nhận `AgentState` sạch từ Ingest + Context Nexus (intent/entity/security/checkpoint) và chuẩn hóa thành planning graph cho Execution.

### Deliverables

- [x] ReasoningAgent: phân rã bài toán, mapping quan hệ, complexity, output JSON có cấu trúc
- [x] PlanningAgent: task queue BabyAGI-style, dependency, readiness
- [x] Schema validation cho output JSON của ReasoningAgent
- [x] Tích hợp LangGraph; commit state vào Nexus liên tục
- [x] Planning task queue có dependency graph và readiness state rõ
- [x] UI hiển thị reasoning/planning realtime (nếu trong scope UI)
- [x] Định nghĩa contract handoff Phase 5 → Phase 6 (structured plan schema + execution preconditions)

### Tiêu chí nghiệm thu (theo plan Phase 5)

- [ ] Reasoning đúng bài toán; planning tạo task queue rõ; dependency đúng
- [x] Structured plan và reasoning output schema validation pass
- [x] Không sinh SQL ở reasoning layer
- [x] Execution chỉ nhận structured plan
- [x] Có test contract đảm bảo output planner tương thích ExecutionAgent

**Phụ thuộc:** Phase 4.

**Ready cho Phase 6 khi:**
- [ ] JSON schema của reasoning/planning được version hóa và kiểm thử tự động
- [ ] Có ít nhất 1 flow E2E chứng minh handoff plan → execution không cần can thiệp thủ công

---

## Phase 6 — Execution, Reflection & Continuous Learning

**Mục tiêu:** Thực thi SQL an toàn; Reflector; vòng retry; học từ thành công/thất bại; pgvector.

**Điểm nối từ Phase 5:** tiêu thụ plan có dependency/readiness từ planner, thực thi tuần tự theo task queue và phản hồi trạng thái về Nexus.

### Deliverables

- [x] ExecutionAgent: tiêu thụ plan, sinh SQL, gọi tool, bắt lỗi
- [x] ReflectorAgent: logic/data/alignment; quyết định retry / finish
- [x] Retry policy, error classification và backoff giới hạn
- [x] Self-healing loop trong graph (giới hạn retry)
- [x] LearningAgent + lưu pattern / vector (`knowledge_zone`)
- [x] Audit: execution / reflection / learning
- [x] DLQ/failure bucket cho task vượt retry limit để tránh loop vô hạn
- [x] Chuẩn hóa taxonomy lỗi dùng chung giữa Execution/Reflector/Learning

### Tiêu chí nghiệm thu (theo plan Phase 6)

- [ ] Task queue chạy đúng; SQL an toàn; reflector phát hiện lỗi logic
- [x] Retry có kiểm soát; loop-back khi cần
- [x] Retry limit / backoff policy validated
- [ ] Memory thành công/thất bại; pgvector tra cứu pattern
- [ ] Toàn bộ hành vi có audit và trace rõ
- [x] Các lỗi vượt ngưỡng retry được chuyển DLQ và có khả năng replay có kiểm soát

**Phụ thuộc:** Phase 5.

**Ready cho Phase 7 khi:**
- [ ] Có baseline metrics về latency/cost/retry/error-rate cho từng lớp agent
- [ ] Có dữ liệu thực nghiệm đủ để tối ưu routing/cost ở Phase 7

---

## Phase 7 — Lean Optimization & Scalability

**Mục tiêu:** Nén context, cost-aware routing, resilience, observability cockpit, RLS, multi-tenant, DANN/local inference (theo plan).

**Điểm nối từ Phase 6:** dùng baseline hiệu năng + dữ liệu lỗi thực tế để tối ưu cost/routing/resilience mà không phá chất lượng trả lời.

### Deliverables

- [x] Context compression / schema pruning / summarization history
- [x] Metrics / budget tracking cho pipeline và model usage
- [ ] Cost guardrails + routing matrix + budget
- [ ] Resilience: backoff, circuit breaker (nếu trong scope), graceful degradation
- [ ] Observability cockpit: cost, bottleneck, failure analytics, feedback
- [x] PostgreSQL RLS + tenant-aware execution; isolation MCP/agent
- [ ] Validation test cases cho multi-tenant / RLS behavior
- [ ] SLO/SLA mục tiêu (latency, success-rate, cost/query) được định nghĩa và gắn cảnh báo
- [ ] Kịch bản load test tối thiểu cho single-tenant và multi-tenant

### Tiêu chí nghiệm thu (theo plan Phase 7)

- [ ] Context nén hiệu quả; token usage giảm đo được
- [ ] Cost/budget metrics và fallback ổn định
- [ ] Routing theo cost policy; fallback ổn định
- [ ] Dashboard observability; latency đo full pipeline
- [ ] RLS đúng; multi-tenant isolation an toàn
- [ ] Local DANN / lightweight inference đạt latency mục tiêu (khi triển khai)
- [ ] SLO được theo dõi liên tục và có cảnh báo khi vượt ngưỡng

**Phụ thuộc:** Phase 6.

**Ready cho Phase 8 khi:**
- [ ] Các guardrails cost/resilience/tenant được kiểm thử trong môi trường gần production
- [ ] Có dashboard + alert tối thiểu phục vụ vận hành/governance

---

## Phase 8 — Finalization, Governance & Project Closure

**Mục tiêu:** Hardening, bảo mật cuối, RBAC, deploy, backup, tài liệu, handover, đóng dự án vận hành.

**Điểm nối từ Phase 7:** đóng gói các tối ưu và controls thành chuẩn vận hành production (governance + incident readiness + handover).

### Deliverables

- [ ] E2E + regression + multi-tenant validation
- [ ] Security checklist; secret management; tách môi trường
- [ ] RBAC; audit governance; change management
- [ ] Production checklist; infra validation; backup & recovery
- [ ] Monitoring, alerting, incident process
- [ ] Gói tài liệu: kiến trúc, developer, operations, business
- [x] Versioning, release notes, runbooks (`rollback`, `incident_response`, `recovery`)
- [x] Thư mục đích bổ sung: `runbooks/`, `scripts/deploy|backup|monitor`, `docs/deployment`, `data/backups`
- [x] Scripts deploy / backup / monitor và runbooks recovery thực tế
- [x] Tài liệu handover cho developer/operator trong `docs/deployment`
- [x] Phase 8 kickoff: gap analysis, runbook skeleton, and governance checklist draft
- [ ] Kế hoạch UAT + sign-off checklist giữa Engineering / Ops / Business owner

### Tiêu chí nghiệm thu (theo plan Phase 8)

- [ ] Workflow ổn định; retry/fallback đúng; observability đủ
- [ ] RLS hoạt động đúng (đồng bộ Phase 7)
- [ ] Deployment/recovery scripts và docs có; governance checklist pass
- [ ] Documentation hoàn chỉnh; deployment & recovery pass; governance pass; handover pass
- [ ] Có biên bản sign-off cuối cùng và tiêu chí chuyển giao vận hành được chốt

**Phụ thuộc:** Phase 7.

---

## Hạng mục xuyên suốt (ongoing)

- [ ] Đồng bộ `plans/` ↔ `tasks/*.md` phase cũ (nếu có) với master này
- [ ] Mỗi phase có "Ready for next phase" checklist và được tick trước khi mở phase kế tiếp
- [ ] CI bắt buộc chạy test tối thiểu trên PR (unit + smoke E2E + lint)
- [ ] Security review định kỳ trên ingest + SQL path + policy redaction log
- [ ] Validate Docker/dev startup, schema init, migration rollback theo chu kỳ
- [ ] Duy trì API contract cho `health` / `ready` / `trace` / `audit` và test tương thích ngược
- [ ] RBAC / secret management / audit governance explicit và có owner chịu trách nhiệm
- [x] Bổ sung runbooks cơ bản trong `runbooks/` và docs deployment cho Phase 8

---

## Phần mở rộng ngoài `plans/` hiện tại

Trong workspace **chỉ có** các file `phase_1` … `phase_8`. Nếu sau này bổ sung thêm plan (ví dụ phase 9+), nên:

1. Thêm file vào `plans/`
2. Thêm mục tương ứng vào cuối tài liệu này
3. Cập nhật `PROJECT_FINAL_STRUCTURE.md` mục ánh xạ phase

---

*Tài liệu được tạo tự động từ nội dung các plan Phase 1–8; chỉnh sửa trực tiếp trên repo khi scope thay đổi.*
