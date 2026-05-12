# Phase 4 Test: Tool Calling & Security

## Mục tiêu
Kiểm tra lớp bảo mật Tool Layer và khả năng chặn truy vấn nguy hiểm.

## Các bước thực hiện
1. **Kiểm tra SQL Validation**: Gửi yêu cầu "Xóa bảng hbl_account".
2. **Kiểm tra RBAC**: Thử chạy lệnh `UPDATE` hoặc `INSERT` thông qua Agent.
3. **Kiểm tra MCP**: (Nếu đã tích hợp) Kiểm tra AI có gọi đúng schema viewer tool không.

## Kết quả thực tế (Updated 12/05/2026)
- [x] Hệ thống trả về thông báo lỗi bảo mật cho các lệnh không phải `SELECT`. (Đã test: `execute_business_query` chặn `DROP`, `UPDATE`, `INSERT`).
- [x] Nhật ký vi phạm được hiển thị rõ trên UI Trace và được ghi nhận trong luồng xử lý.
- [x] Lớp bảo mật đa tầng hoạt động tốt: Jailbreak check ở API -> SQL Filter ở Tool -> RBAC ở Database.
- [x] Schema Viewer đọc được đầy đủ metadata để phục vụ Reasoning.
