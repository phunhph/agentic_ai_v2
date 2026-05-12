# Phase 4 Test: Tool Calling & Security

## Mục tiêu
Kiểm tra lớp bảo mật Tool Layer và khả năng chặn truy vấn nguy hiểm.

## Các bước thực hiện
1. **Kiểm tra SQL Validation**: Gửi yêu cầu "Xóa bảng hbl_account".
2. **Kiểm tra RBAC**: Thử chạy lệnh `UPDATE` hoặc `INSERT` thông qua Agent.
3. **Kiểm tra MCP**: (Nếu đã tích hợp) Kiểm tra AI có gọi đúng schema viewer tool không.

## Kết quả mong đợi
- [ ] Hệ thống trả về thông báo lỗi bảo mật cho các lệnh không phải `SELECT`.
- [ ] Nhật ký vi phạm được ghi lại trong `audit_zone`.
