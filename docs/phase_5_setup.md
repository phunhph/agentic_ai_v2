# Phase 5 — Reasoning & Planning Layers

## Mục tiêu

Phase 5 xây dựng lớp Reasoning và Planning để hệ thống không còn phản ứng trực tiếp theo prompt nữa.

Mục tiêu chính:

- chuyển input đã làm sạch sang suy luận có cấu trúc
- tạo business intent sâu hơn
- đánh giá độ phức tạp
- bẻ nhỏ yêu cầu thành các bước logic
- tạo kế hoạch task queue có thứ tự và phụ thuộc
- ghi lại reasoning và planning state vào Context Nexus
- bảo đảm không sinh SQL ngay trong luồng này

## 1. ReasoningAgent

Module `core.agents.reasoning_agent` thực hiện:

- nhận input normalized từ Phase 4
- phân tích business intent sâu hơn
- phân loại complexity
- xác định semantic views liên quan
- trích xuất assumptions và bước logic
- lưu reasoning state vào `audit_zone.checkpoints` với `state_type = reasoning`

Nó không được phép:

- gọi execution tool
- sinh SQL
- trả kết quả cuối cùng

## 2. PlanningAgent

Module `core.agents.planning_agent` chuyển output của ReasoningAgent thành kế hoạch.

Chức năng:

- tạo task queue theo độ phức tạp
- xác định phụ thuộc task
- lưu planning state vào `audit_zone.checkpoints` với `state_type = planning`
- chuẩn bị dữ liệu cho ExecutionAgent ở Phase 6

## 3. Context Nexus & state persistence

`audit_zone.checkpoints` được mở rộng để lưu `state_type`.

Các trạng thái hiện lưu:

- `checkpoint` — trạng thái đầu vào từ Phase 4
- `reasoning` — output của ReasoningAgent
- `planning` — output của PlanningAgent

## 4. Runtime integration

`core.graph.langgraph_runtime.LangGraphRuntime` hiện chạy tuần tự:

1. IngestAgent
2. ReasoningAgent
3. PlanningAgent
4. Schema retrieval
5. SQL preview (nếu có) nhưng không thực thi ngay

Response API cung cấp:

- `ingest_state`
- `reasoning_state`
- `planning_state`
- `trace`

## 5. Cách chạy

Không thay đổi so với Phase 2/3:

```bash
python run.py api
python run.py ui
```

## 6. Kiến trúc hiện tại

Các file chính:

- `core/agents/reasoning_agent.py`
- `core/agents/planning_agent.py`
- `core/utils/infra/checkpoint.py`
- `core/graph/langgraph_runtime.py`
- `apps/api/app.py`
- `data/schema/init.sql`

## 7. Next steps

- xây ExecutionAgent cho Phase 6
- mở rộng state store để replay từng bước logic
- bổ sung validation schema cho output reasoning/planning
