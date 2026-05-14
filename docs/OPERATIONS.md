# Operations & Runbooks (Sổ Tay Vận Hành)

Tài liệu này dùng cho DevOps/SysAdmin để quản trị và khắc phục sự cố hệ thống.

## 1. Monitoring & Alerts (Giám sát hệ thống)
- **Truy cập Observability Cockpit**: 
  1. Mở Streamlit web UI.
  2. Truy cập tab `Observability Cockpit`.
  3. Theo dõi "Circuit Breaker Status" và "Total Cost Spent".
- **Cảnh báo (Alerts)**:
  - Khi "Circuit Breaker Status" là `TRIPPED`, có nghĩa là LLM API hoặc kết nối DB đang bị gián đoạn.
  - Vui lòng xem logs trong `audit_zone.system_metrics` thông qua dashboard.

## 2. Backup & Restore (Sao lưu và Phục hồi)
- Chạy backup dữ liệu thủ công: `bash scripts/backup_db.sh`
- Khôi phục dữ liệu từ file backup (LƯU Ý: sẽ ghi đè database hiện tại): `bash scripts/restore_db.sh <path_to_backup_file>`

## 3. Quản trị Người dùng (RBAC)
- **Thay đổi quyền**: Hiện tại Agent sử dụng user `postgres` (mặc định) hoặc role `agent_role` (Khuyến cáo sử dụng trên Production).
- **Tenant Validation**: Việc xác thực tenant được thực hiện thông qua `core.utils.logic.tenant_guard.TenantGuard`. Để cấu hình thêm quyền, hãy cập nhật class này.

## 4. Xử lý sự cố thường gặp (Troubleshooting)
- **Vượt quá ngân sách hàng ngày (Budget Exceeded)**:
  - Triệu chứng: Agent chỉ phản hồi bằng model `default` rất chậm hoặc liên tục báo lỗi suy luận kém.
  - Cách khắc phục: Vào file `.env`, điều chỉnh `OPENAI_API_KEY` mới hoặc tắt tính năng Budget Guardrail trong biến môi trường.
- **Lỗi kết nối DB (Connection Timeout)**:
  - Triệu chứng: `/ready` API trả về 503.
  - Khắc phục: Kiểm tra trạng thái service `docker ps`, restart postgres `docker-compose restart postgres`.
