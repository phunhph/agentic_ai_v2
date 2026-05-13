# Phase 8 — Finalization, Governance & Project Closure

## Mục tiêu

Phase 8 là giai đoạn hoàn thiện hệ thống để đưa vào vận hành thực tế với các yêu cầu:

- hardening
- production-ready deployment
- backup/recovery
- RBAC và governance
- documentation và handover
- runbooks vận hành

Phase 8 không thiết kế cơ chế mới cho pipeline; nó hoàn thiện, kiểm chứng và đóng gói các phase trước.

## 1. Governance & Security

### 1.1 Security checklist

- Xác thực tất cả endpoint admin/agent
- Đảm bảo API secret được tách khỏi code và log
- Kiểm tra `core/tools/security.py` đã chặn SQL/DML/DDL nguy hiểm
- Kiểm soát quyền truy cập đến database và audit logs
- Có danh sách biến môi trường an toàn và quy trình secret rotation

### 1.2 RBAC & Audit

- Định nghĩa rõ quyền `read-only` và `admin` cho môi trường production
- Tài liệu ai được phép xem logs và ai có quyền deploy
- Audit log phải ghi đủ `thread_id`, `session_id`, `event_type`, `created_at`

## 2. Deployment

### 2.1 Mục tiêu deploy

- Tự động hóa startup API/UI
- Khởi tạo schema và backup database trước khi deploy
- Triển khai nhanh với Docker Compose hoặc Python script
- Xác thực `health` và `ready` sau deploy

### 2.2 Điểm kiểm tra

- Có `scripts/deploy.py` để chạy deploy môi trường dev/staging
- Có `docs/deployment/README.md` mô tả cách deploy
- Kiểm tra `docker-compose.yml` hoặc script khởi tạo DB trước khi chạy
- Có quy trình rollback và recovery

## 3. Backup & Recovery

### 3.1 Backup

- Sao lưu database trước mỗi release
- Lưu trữ backup file theo định dạng `agentic_backup_<timestamp>.sql`
- Kiểm tra restore trên môi trường staging

### 3.2 Recovery

- Khôi phục từ file SQL backup nếu hệ thống lỗi
- Cấu hình quá trình restore rõ ràng trong runbook
- Đảm bảo dữ liệu audit và checkpoints được bảo toàn

## 4. Runbooks vận hành

Runbooks cần bao gồm:

- rollback
- incident response
- recovery

Mỗi runbook chứa:

- dấu hiệu cảnh báo
- hành động khắc phục
- kiểm tra sau khi xử lý
- liên hệ nội bộ

## 5. Observability & Monitoring

Phase 8 cần bổ sung:

- health check định kỳ cho API
- logging/metrics cho deployment và backup
- cảnh báo khi API/DB không sẵn sàng
- tài liệu monitor cơ bản trong `docs/deployment`

## 6. Handover & Documentation

- Tập trung vào docs cho developer và operations
- Cung cấp hướng dẫn khởi chạy, deploy, monitor, rollback
- Đảm bảo repo có runbooks để support vận hành

## 7. Tài liệu liên quan

- `runbooks/rollback.md`
- `runbooks/incident_response.md`
- `runbooks/recovery.md`
- `docs/deployment/README.md`
- `docs/deployment/production_checklist.md`
- `scripts/deploy.py`
- `scripts/backup.py`
- `scripts/monitor.py`
