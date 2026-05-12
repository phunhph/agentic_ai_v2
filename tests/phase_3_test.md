# Phase 3 Test: Project Initialization & Traceable UI

## Mục tiêu
Xác nhận hệ thống có khả năng hiển thị lộ trình tư duy của Agent (Trace Log), quản lý phiên làm việc (Thread) và lưu trữ lịch sử xử lý vào Audit Zone.

## Các bước thực hiện
1. **Khởi động hệ thống**: Chạy `python run.py`.
2. **Kiểm tra API Health**: Truy cập `http://localhost:5000/v1/agent/health`.
3. **Gửi câu hỏi từ UI**: Nhập một câu hỏi nghiệp vụ (vd: "Danh sách khách hàng Finance tại Việt Nam").
4. **Kiểm tra Sidebar**: Quan sát luồng Trace Log (Ingest -> Reasoning -> Planning -> Execution -> Learning).
5. **Kiểm tra Debug Expander**: (Nếu đã có) Xem SQL hoặc dữ liệu thô được hiển thị.
6. **Kiểm tra Database**: Chạy query `SELECT * FROM audit_zone.agent_trace_logs;` để xác nhận trace đã được lưu.

## Kết quả thực tế (Updated 12/05/2026)
- [x] API trả về status `ok`. (Đã test: `http://localhost:5000/v1/agent/health` -> 200 OK)
- [x] UI hiển thị khung chat và lịch sử tin nhắn đúng vai trò (User/Assistant).
- [x] Sidebar hiển thị đầy đủ 5 bước Trace Log với khả năng mở rộng (Expander). (Đã test: Ingest, Reasoning, Planning, Execution, Learning)
- [x] Database `audit_zone` ghi nhận ít nhất 1 dòng log mới sau mỗi câu hỏi. (Đã test: `audit_zone.agent_trace_logs` có dữ liệu mới)
- [x] Thread ID được sinh mới cho mỗi phiên chat và được trả về trong response.
- [x] Trace chi tiết hiển thị rõ ràng Input/Output cho từng bước. (Tính năng mới Phase 10 support)

## Ghi chú
- Phase 3 tập trung vào **hiển thị luồng (flow)**, chưa yêu cầu logic AI thật sự chính xác 100%.
