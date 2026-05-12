# Phase 2 Test: Database Migration & Schema

## Mục tiêu
Xác nhận cấu trúc Database đã được khởi tạo đúng và AI có thể đọc được metadata.

## Các bước thực hiện
1. **Chạy init script**: Thực thi file `data/schema/init.sql` trong PostgreSQL.
2. **Kiểm tra Schema**: 
   - `SELECT * FROM information_schema.schemata;` (Kiểm tra business_zone, knowledge_zone, audit_zone).
   - `SELECT * FROM pg_extension;` (Kiểm tra pgvector, uuid-ossp).
3. **Kiểm tra dữ liệu mẫu**: `SELECT * FROM hbl_account;`

## Kết quả mong đợi
- [x] Database được tạo đầy đủ các schema yêu cầu (business_zone, knowledge_zone, audit_zone).
- [x] Extension uuid-ossp đã được cài đặt (pgvector đang ở chế độ chờ/fallback).
- [x] Các bảng metadata sẵn sàng để AI truy vấn.
- [x] Dữ liệu mẫu (1000+ dòng) đã được nạp thành công.

## Kết quả thực tế (2026-05-12)
- **Schemas**: Đã xác nhận tồn tại 3 zone.
- **Tables**: Toàn bộ các bảng nghiệp vụ từ `db.json` đã được khởi tạo.
- **Data Seeding**: Bảng `agentic_ai` có 1000 dòng dữ liệu ngẫu nhiên.
- **AI Views**: Các View `v_hbl_...` đã hoạt động.
- **Đánh giá**: **PASS**
