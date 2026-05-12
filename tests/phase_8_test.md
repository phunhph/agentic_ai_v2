# Phase 8 Test: ExecutionAgent Layer

## Mục tiêu
Kiểm tra khả năng sinh SQL chính xác và cơ chế tự sửa lỗi (Self-healing).

## Các bước thực hiện
1. **Gửi câu hỏi yêu cầu dữ liệu thực tế**.
2. **Giả lập lỗi**: Cố tình đổi tên cột trong Database và xem AI có tự phát hiện lỗi và sửa query không.

## Kết quả mong đợi
- [ ] SQL được sinh ra hợp lệ và chạy được trên Postgres.
- [ ] Nếu gặp lỗi cột không tồn tại, AI phải tự đọc schema và sửa lại SQL.
