# 🚀 Autonomous CRM Intelligence System (Agentic AI)

Chào mừng bạn đến với dự án **Agentic CRM Intelligence System**. Đây là một hệ thống AI Agent đa tầng được thiết kế để cung cấp khả năng truy vấn và phân tích dữ liệu CRM một cách thông minh, an toàn và có khả năng tự học.

---

## 📖 Tài liệu Hướng dẫn (Documentation)

Hệ thống có tài liệu Phase 1 và hướng dẫn khởi tạo cơ sở dữ liệu:

| Tài liệu | Đối tượng | Nội dung chính |
|---|---|---|
| 🌟 [**Phase 1 Setup**](docs/phase_1_setup.md) | Kỹ thuật | Khởi tạo DB, semantic schema, migration strategy, và quick start. |
| 🌟 [**Phase 2 Setup**](docs/phase_2_setup.md) | Kỹ thuật | Flask API, Streamlit UI, observability và audit logging. |
| 🌟 [**Phase 3 Setup**](docs/phase_3_setup.md) | Kỹ thuật | LLM Router, semantic schema retrieval, MCP tool và security policy. |
| 🌟 [**Phase 8 Setup**](docs/phase_8_setup.md) | Vận hành | Deployment, backup, recovery, runbooks và governance documentation. |
| 🌟 [**System Summary**](docs/system_summary.md) | Tổng kết | Tổng quan dự án, cấu trúc, sơ đồ kiến trúc và hướng dẫn chạy. |

---

## 🧩 Quy trình hoạt động (Agent Pipeline)
Hệ thống hoạt động dựa trên 5 tầng Agent phối hợp nhịp nhàng:
```mermaid
graph LR
    User((User)) --> IA[IngestAgent]
    IA --> RA[ReasoningAgent]
    RA --> PA[PlanningAgent]
    PA --> EA[ExecutionAgent]
    EA --> LA[LearningAgent]
    LA --> Memory[(pgvector)]
    Memory -.-> RA
```

---

## 🚀 Tính năng nổi bật
- **Traceable UI**: Xem lộ trình tư duy (Chain-of-Thought) của Agent theo thời gian thực.
- **Context Awareness**: Hiểu ngữ cảnh hội thoại nhiều lượt (giải quyết đại từ "nó", "họ"...).
- **Secure Execution**: Thực thi SQL an toàn thông qua lớp bảo mật RBAC và Tool Layer.
- **Self-Learning**: Ghi nhớ các mẫu thành công để tối ưu hóa chi phí và tốc độ.

---

## 📂 Cấu trúc Dự án (Sơ lược)
- `apps/`: Giao diện người dùng (Streamlit) và API Backend (Flask).
- `core/`: Trái tim của hệ thống (Graph, Agents, Tools).
- `docs/`: Tài liệu hướng dẫn và kiến trúc.
- `plans/`: Kế hoạch chi tiết cho từng giai đoạn (Phase 1-10).
- `tasks/`: Danh sách các công việc cần làm (Checklist).

---

## 📝 Roadmap Phát triển
Hệ thống được phát triển qua 10 Phase chuyên sâu:
- **Phase 1-21**: Đã hoàn thành toàn bộ hệ thống (Hoàn thành ✅).
  - Tích hợp Multi-Agent, Resilience, RAG Nâng cao, MCP Tools và Observability Cockpit.

---
*Phát triển bởi đội ngũ chuyên gia AI Agent.*
