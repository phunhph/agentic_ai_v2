# Phase 2 — UI, API Gateway & Observability Layer
## Agentic CRM System

---

# 1. Mục đích Phase 2

Phase 2 không chỉ là làm giao diện chat hay mở một API đơn giản.  
Đây là giai đoạn xây dựng **lớp tương tác đầu tiên giữa con người và hệ thống Agentic CRM**, đồng thời thiết lập **năng lực quan sát nội bộ** để hệ thống có thể debug, audit, replay và cải tiến trong các phase sau.

Nói cách khác, Phase 2 đóng vai trò tạo ra 3 lớp quan trọng:

- **Interaction Layer**: người dùng nhập câu hỏi và nhận kết quả
- **Gateway Layer**: điều phối request, session và workflow Agent
- **Observability Layer**: quan sát tiến trình suy luận, tool call, SQL sinh ra và các điểm lỗi

Nếu Phase 1 là nền móng dữ liệu và semantic layer, thì Phase 2 là **lớp vận hành đầu tiên của hệ thống Agent**.

---

# 2. Objectives

## 2.1 Xây dựng API Gateway trung tâm

Flask sẽ đóng vai trò là cổng điều phối trung tâm giữa UI, Agent runtime và PostgreSQL.

API Gateway phải đảm nhiệm các chức năng:

- Nhận request từ UI
- Chuẩn hóa payload đầu vào
- Tạo và quản lý thread/session
- Kích hoạt LangGraph workflow
- Stream trạng thái tiến trình của Agent
- Ghi log thực thi và lỗi hệ thống
- Trả response cuối cùng cho frontend

---

## 2.2 Xây dựng giao diện chat cho người dùng cuối

Streamlit được dùng để tạo giao diện tương tác nhanh, nhẹ và dễ iterate.

Giao diện cần hỗ trợ:

- Chat text
- Hiển thị Markdown
- Hiển thị bảng dữ liệu
- Hiển thị trạng thái xử lý theo thời gian thực
- Hiển thị SQL debug
- Hiển thị trace của từng bước Agent

---

## 2.3 Thiết kế hệ thống Observability

Hệ thống cần cho phép người dùng và developer nhìn thấy:

- Agent đang làm gì
- Bước nào đang chạy
- SQL nào đang được sinh ra
- Tool nào đang được gọi
- Node nào bị lỗi
- Tổng thời gian xử lý của từng bước
- Dữ liệu nào đã được truy vấn

Mục tiêu là biến AI từ một “hộp đen” thành một hệ thống có thể kiểm tra và giải thích.

---

## 2.4 Thiết lập audit log và execution log

Mọi request/response quan trọng cần được ghi nhận vào PostgreSQL theo cấu trúc chuẩn để:

- theo dõi lịch sử hội thoại
- debug lỗi
- phân tích hiệu năng
- đánh giá độ chính xác của Agent
- replay lại một phiên làm việc khi cần

---

# 3. Phạm vi của Phase 2

Phase 2 tập trung vào các thành phần sau:

- Flask API Gateway
- Session/Thread Management
- Streamlit UI
- Agent Trace Sidebar
- SQL Debug Viewer
- PostgreSQL Audit Logging
- Realtime status update theo polling hoặc stream
- Basic health monitoring

Phase này **không** đi sâu vào tối ưu model, đa agent phức tạp hay tool orchestration nâng cao.  
Mục tiêu là tạo một **khung vận hành đủ chắc** để các phase sau có thể mở rộng ổn định.

---

# 4. Kiến trúc tổng thể

```text
User
  ↓
Streamlit UI
  ↓
Flask API Gateway
  ↓
LangGraph Runtime
  ↓
Agent Nodes / Tools / SQL Layer
  ↓
PostgreSQL / Audit / Checkpoint / Semantic Views