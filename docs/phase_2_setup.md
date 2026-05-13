# Phase 2 — UI, API Gateway & Observability

## Mục tiêu

Phase 2 triển khai Flask API gateway và Streamlit UI để tương tác với Agent. Phase này cũng bổ sung observability và audit logging cơ bản.

## 1. Flask API

Endpoints hiện tại:

- `GET /health` — kiểm tra service
- `GET /ready` — kiểm tra kết nối DB
- `POST /v1/agent/chat` — gửi prompt đến Agent
- `GET /v1/agent/trace/<thread_id>` — xem trace/audit log của request

### Chạy API

```bash
python apps/api/app.py
```

Mặc định API chạy trên `http://0.0.0.0:8000`.

## 2. Streamlit UI

Streamlit UI gọi trực tiếp API Flask để gửi prompt và hiển thị kết quả.

### Chạy UI

```bash
streamlit run apps/web/streamlit_app.py
```

### Tính năng

- Nhập prompt và gửi đến API
- Hiển thị conversation history
- Hiển thị trace/audit logs theo `thread_id`
- Kiểm tra `health` endpoint

## 3. Audit

Mọi request và response được ghi vào `audit_zone.agent_logs` bằng trường `thread_id`.

## 4. Notes

- LangGraph runtime hiện tại là stub và chỉ mô phỏng trace tiếp theo Phase 3.
- SQL debug vẫn là placeholder, phù hợp với Phase 2 scope.
