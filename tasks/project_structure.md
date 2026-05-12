# Sơ đồ Cấu trúc Dự án (Project Structure Diagram)

Dưới đây là sơ đồ phân cấp thư mục và vai trò của từng thành phần trong dự án:

```mermaid
graph LR
    Root[agentic_v2]
    
    Root --> Plans[plans/]
    Root --> Tasks[tasks/]
    Root --> Apps[apps/]
    Root --> Core[core/]
    Root --> Data[data/]
    Root --> Memory[memory/]
    Root --> Tests[tests/]
    
    subgraph "Tài liệu & Kế hoạch"
        Plans --- PlansFiles[db.json, phase_1-9.md]
        Tasks --- TasksFiles[system_*.md, phase_todo.md]
    end
    
    subgraph "Ứng dụng (Interface)"
        Apps --> API[api/ - Flask Backend]
        Apps --> Web[web/ - Streamlit Frontend]
    end
    
    subgraph "Logic cốt lõi (Agents)"
        Core --> Agents[agents/ - 5 Layers]
        Core --> Graph[graph/ - LangGraph State]
        Core --> Tools[tools/ - MCP & SQL]
    end
    
    subgraph "Dữ liệu & Di chuyển"
        Data --> Migration[migration/ - Scripts]
        Data --> Schema[schema/ - SQL Definitions]
    end
    
    subgraph "Bộ nhớ & Trạng thái"
        Memory --> Embed[embeddings/ - Vector]
        Memory --> Check[checkpoints/ - State]
    end
    
    Root --- RootFiles[.env, requirements.txt, README.md]
```

## Chi tiết các thư mục chính
- **`plans/`**: Lưu trữ các file kế hoạch chi tiết và thông số kỹ thuật cho từng giai đoạn phát triển.
- **`tasks/`**: Chứa các file mô tả hệ thống, kiến trúc và danh sách công việc (to-do) đã được chuẩn hóa.
- **`apps/`**: Nơi chứa mã nguồn của giao diện người dùng và API server.
- **`core/`**: Trái tim của hệ thống, nơi định nghĩa các Agent, luồng xử lý LangGraph và các công cụ thực thi.
- **`data/`**: Quản lý việc di chuyển dữ liệu từ hệ thống cũ và định nghĩa cấu trúc database mới.
- **`memory/`**: Xử lý các hoạt động liên quan đến bộ nhớ vector và lưu trữ trạng thái phiên làm việc.
- **`tests/`**: Chứa các kịch bản kiểm thử cho từng thành phần của hệ thống.
