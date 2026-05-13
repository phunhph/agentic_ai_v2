# Dataverse → PostgreSQL Migration Strategy

Phase 1 focuses on building a reusable migration path from Microsoft Dataverse into PostgreSQL.

## Mục tiêu

- Đồng bộ dữ liệu Dataverse vào PostgreSQL theo dạng bảng nghiệp vụ.
- Chuẩn hóa dữ liệu CRM để hỗ trợ semantic views và AI-friendly access.
- Giữ separation between raw ingest and AI abstraction.

## Chiến lược

1. Extract
   - Export Dataverse entities và lookup relationships.
   - Sử dụng Data Export Service, Power Platform CLI, hoặc Azure Data Factory.

2. Transform
   - Map Dataverse entity fields sang các bảng business_zone phù hợp.
   - Chuẩn hóa định dạng địa chỉ, ngày tháng, tên đối tượng và trạng thái.
   - Loại bỏ metadata không cần thiết, chỉ giữ fields phục vụ AI và audit.

3. Load
   - Tải data vào PostgreSQL bằng batch insert hoặc incremental upsert.
   - Áp dụng kiểm tra tính toàn vẹn dữ liệu trước khi commit.

## Kết quả

- `business_zone` chứa các bảng nghiệp vụ đã làm sạch và liên kết.
- `knowledge_zone` lưu embeddings / memory metadata.
- `audit_zone` lưu lại lịch sử thực thi và trace.

## Gợi ý công cụ

- Azure Data Factory / Power Platform Dataflows
- Python ETL script với `pandas` và `sqlalchemy`
- `pgvector` cho embeddings

