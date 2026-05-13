# Phase 4 — Ingest Layer & Context Nexus

## Mục tiêu

Phase 4 xây dựng lớp Ingest Gateway và Context Nexus để:

- chuẩn hóa input đầu vào
- phát hiện intent và entity
- checkpoint trạng thái cho mỗi thread
- cho phép resume/replay theo thread isolation
- bảo vệ hệ thống khỏi prompt injection và payload xấu

## 1. IngestAgent

Module `core.agents.ingest_agent` là lớp gatekeeper đầu tiên.

Chức năng chính:

- chuẩn hóa prompt
- phân loại intent nhanh
- trích xuất entity cơ bản (email, phone, date, labels)
- tạo state có cấu trúc
- commit checkpoint vào DB bằng `CheckpointStore`

IngestAgent không:

- không gọi SQL
- không truy vấn dữ liệu thực
- không sinh kết quả cuối

## 2. Context Nexus

Module `core.utils.infra.checkpoint` lưu checkpoint trong schema `audit_zone.checkpoints`.

Các supported flow:

- lưu checkpoint theo `thread_id`
- truy vấn checkpoint history với `/v1/agent/checkpoints/<thread_id>`
- lấy latest checkpoint với `/v1/agent/replay/<thread_id>`
- resume từ thread khác khi cần

## 3. Schema và DB

Đã mở rộng `data/schema/init.sql` để thêm bảng:

- `audit_zone.checkpoints`

Trường lưu trữ:

- `thread_id`
- `session_id`
- `checkpoint_data`
- `previous_checkpoint_id`
- `created_at`

## 4. API integration

Endpoint chính:

- `POST /v1/agent/chat`

Payload mới hỗ trợ:

- `prompt`: bắt buộc
- `thread_id`: tùy chọn, nếu không có sẽ tạo mới
- `session_id`: tùy chọn
- `resume_thread_id`: tùy chọn để lấy state từ thread cũ

Response trả về thêm:

- `ingest_state`
- `result`
- `trace`

API trace mới:

- `GET /v1/agent/checkpoints/<thread_id>`
- `GET /v1/agent/replay/<thread_id>`

## 5. Runtime và trace

`core.graph.langgraph_runtime.LangGraphRuntime` hiện nhận thêm `ingest_state`.

Hiệu quả:

- sử dụng prompt đã normalize
- đưa `intent`/`entities` vào trace
- giữ flow Phase 3 nhưng có state sạch từ Phase 4

## 6. Cách chạy

Giữ nguyên cách khởi chạy như Phase 2/3:

```bash
python run.py api
python run.py ui
```

Endpoint kiểm thử:

```bash
curl -X POST http://localhost:8000/v1/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Update account revenue for Acme","session_id":"s1"}'
```

## 7. Tính trạng hiện tại

Đã triển khai:

- `IngestAgent`
- `CheckpointStore`
- API resume/replay
- Phase 4 doc xong

Tiếp theo có thể mở rộng:

- validation prompt injection sâu hơn
- entity extraction chính xác hơn
- audit check cho resume thread
