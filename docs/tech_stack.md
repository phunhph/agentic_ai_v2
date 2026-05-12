# Lộ trình Công nghệ & Thư viện (Tech Stack by Phase)

Dưới đây là danh sách các công nghệ và thư viện chủ chốt được sử dụng xuyên suốt quá trình phát triển hệ thống.

## 🏗️ Nền tảng (Core Stack)
- **Ngôn ngữ**: Python 3.10+
- **Cơ sở dữ liệu**: PostgreSQL 15+ (với `pgvector` cho AI Memory)
- **Điều phối Agent**: [LangGraph](https://www.langchain.com/langgraph) (Quản lý trạng thái và luồng)
- **Mô hình AI (LLMs)**: Google Gemini 1.5 Pro/Flash, Groq (Llama 3), OpenAI GPT-4o.

---

## 📅 Chi tiết theo từng Giai đoạn (Phases)

### Phase 1: Architecture & Foundation
- `python-dotenv`: Quản lý biến môi trường.
- `psycopg2-binary`: Kết nối PostgreSQL.
- `pydantic`: Chuẩn hóa cấu trúc dữ liệu.

### Phase 2: Database Migration & Seeding
- `json`: Xử lý metadata từ `db.json`.
- `uuid`: Sinh mã định danh duy nhất cho dữ liệu mẫu.
- `random`, `datetime`: Giả lập dữ liệu nghiệp vụ thực tế.

### Phase 3: Traceable UI & API Gateway
- `flask`: Xây dựng RESTful API.
- `streamlit`: Giao diện người dùng tương tác thời gian thực.
- `requests`: Kết nối giữa Frontend và Backend.
- `mermaid`: Vẽ sơ đồ luồng trực tiếp trong tài liệu.

### Phase 4: Tools & Security
- `sqlparse`: Phân tích và kiểm tra tính an toàn của câu lệnh SQL.
- `mcp` (Model Context Protocol): Chuẩn hóa giao tiếp với các công cụ bên ngoài.

### Phase 5-8: Specialized Agents (Ingest -> Execution)
- `langchain-google-genai`: Tích hợp Gemini SDK.
- `langchain-groq`: Tích hợp Groq SDK cho suy luận tốc độ cao.
- `litellm`: Thư viện hợp nhất gọi nhiều loại LLM khác nhau.

### Phase 9: Semantic Learning Agent
- `pgvector-python`: Thao tác với Vector Database trong Postgres.
- `sentence-transformers`: Tạo tọa độ vector (embeddings) cho dữ liệu.

### Phase 10: Context & Monitoring
- `langgraph[checkpoint]`: Lưu trữ và khôi phục trạng thái hội thoại.
- `langsmith`: Giám sát, debug và đánh giá hiệu năng Agent.

---

## 🔒 Bảo mật & Vận hành
- **RBAC**: Phân quyền truy cập Database ở mức thấp nhất (`agent_user`).
- **Audit Logging**: Lưu vết mọi hành động vào schema `audit_zone`.
