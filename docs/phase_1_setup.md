# Phase 1 Setup & Data Foundation

## Mục tiêu

Phase 1 xây dựng nền tảng dữ liệu cho Agentic CRM: PostgreSQL, schema zones, semantic views và môi trường dev.

## Bước 1: Chuẩn bị môi trường

1. Sao chép file cấu hình mẫu:
   ```bash
   copy .env.example .env
   ```
2. Cập nhật `DB_PASSWORD` và các biến AI provider trong `.env`.
3. Cài đặt dependency:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Bước 2: Khởi động PostgreSQL

Sử dụng Docker Compose để chạy PostgreSQL:

```bash
docker compose up -d
```

Docker Compose sử dụng image `ankane/pgvector:pg15`, có sẵn extension `vector`.

> Nếu bạn chạy script với một PostgreSQL cục bộ khác, hãy đảm bảo extension `vector` đã được cài.

## Bước 3: Khởi tạo schema

Nếu database đã tồn tại, chạy script khởi tạo schema:

```bash
python scripts/init_db.py
```

## Schema zones

Phase 1 tạo ba zone chính:

- `business_zone`: bảng nghiệp vụ CRM chính.
- `knowledge_zone`: bảng lưu embeddings và memory.
- `audit_zone`: bảng ghi lại execution trace và agent log.

## Semantic abstraction

Semantic layer được xây dựng bằng các view AI-friendly:

- `business_zone.v_hbl_accounts`
- `business_zone.v_hbl_contacts`

Các view này trừu tượng hóa dữ liệu kỹ thuật của bảng cơ bản, giúp Agent truy vấn theo ngữ cảnh nghiệp vụ mà không cần hiểu chi tiết schema dưới.

## Kết quả mong đợi

- Database `agentic_ai` có các schema và bảng khởi tạo.
- Extensions PostgreSQL `uuid-ossp` và `vector` sẵn sàng sử dụng.
- Semantic views giúp giảm độ phức tạp khi prompt tới LLM.

## Migration strategy

Xem thêm chiến lược Dataverse → PostgreSQL tại:

- `data/migration/README.md`
