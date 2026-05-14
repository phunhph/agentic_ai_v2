# Production Deployment & Security Checklist

Tài liệu này cung cấp danh sách kiểm tra (checklist) bắt buộc trước khi đưa hệ thống Agentic AI lên môi trường Production.

## 1. Môi trường & Secret Management (Environment & Secrets)
- [ ] **Tách biệt môi trường**: Đảm bảo các biến môi trường của `development`, `staging` và `production` được lưu trữ riêng biệt. Không dùng file `.env` cho production, thay vào đó sử dụng Secret Manager (AWS Secrets Manager, HashiCorp Vault, hoặc GitHub Secrets).
- [ ] **API Keys**: Đảm bảo `OPENAI_API_KEY`, `GEMINI_API_KEY`, và `OPENROUTER_API_KEY` được cấp quyền tối thiểu (least privilege). Cấu hình giới hạn chi phí (hard cap) trên OpenAI / OpenRouter dashboard.
- [ ] **DB Credentials**: Thay đổi mật khẩu `postgres` mặc định. Sử dụng role riêng biệt cho Agent (`agent_role`) chỉ có quyền `SELECT` trên `business_zone` và không có quyền xóa (DROP/DELETE).

## 2. Infrastructure & Database
- [ ] **Postgres RLS**: Kiểm tra lại `RLSManager` đã kích hoạt và hoạt động đúng trên tất cả các bảng nhạy cảm (VD: `v_hbl_accounts`).
- [ ] **Backup & Recovery**: Đảm bảo cron job chạy `scripts/backup_db.sh` hàng ngày.
- [ ] **Connection Pooling**: Sử dụng PgBouncer hoặc cấu hình Connection Pool của SQLAlchemy để xử lý tải cao.

## 3. Observability & Monitoring
- [ ] **Cost Guardrails**: Kiểm tra `daily_budget` trong `CostRouter` đã được cấu hình phù hợp với thực tế.
- [ ] **Circuit Breaker**: Chắc chắn rằng biến `max_failures` và `reset_timeout` được tinh chỉnh tùy theo SLI (Service Level Indicator) của công ty.
- [ ] **Log Redaction**: Mọi PII (Personal Identifiable Information) hoặc dữ liệu thẻ tín dụng phải được che khuất (redact) trước khi ghi vào `audit_zone.agent_logs`.

## 4. RBAC (Role-Based Access Control)
- [ ] **Tenant Isolation**: Bắt buộc mọi yêu cầu API qua cổng `/v1/agent/chat` phải đính kèm `session_id` đã được xác thực (thông qua JWT hoặc SSO).
- [ ] **Change Management**: Mọi thay đổi schema hoặc policy RLS phải được review qua PR (Pull Request) và áp dụng bằng công cụ Migration (VD: Alembic), tuyệt đối không sửa tay trên Production DB.

## 5. Kế hoạch ứng phó sự cố (Incident Response)
- [ ] Có Runbook khôi phục dữ liệu từ bản backup gần nhất (tham khảo `scripts/restore_db.sh`).
- [ ] Cài đặt cảnh báo (Alert) vào Slack/Teams khi hệ thống chạm mốc 80% Budget hoặc khi Circuit Breaker bị TRIPPED.

---
**Ký nhận (Sign-off) trước khi Deploy:**
- [ ] DevOps Engineer: ___________________
- [ ] Security Officer: ___________________
- [ ] Tech Lead: ________________________
