# Phase 3 — MCP, LLM Orchestration & Secure Tooling

## Mục tiêu

Phase 3 xây dựng lớp điều phối model, lớp trích xuất schema phù hợp và lớp công cụ thực thi SQL an toàn.

## 1. LLM Router

Module `core.tools.llm_router` chọn model dựa trên nội dung prompt:

- `reasoning` cho truy vấn liên quan SQL/schema
- `high_accuracy` cho phân tích/plan
- `default` cho các yêu cầu chung

Model selection giờ đọc từ `.env` để có thể cấu hình các provider và model name ngoài code.

Fallback được cấu hình và theo dõi trong trace.

## 2. Semantic Schema Retrieval

Module `core.tools.semantic_schema` trả về các view semantic liên quan:

- `business_zone.v_hbl_accounts`
- `business_zone.v_hbl_contacts`
- `knowledge_zone.agent_embeddings`
- `audit_zone.agent_logs`

Chỉ nạp những view liên quan, không đưa toàn bộ schema vào prompt.

## 3. MCP Tool & Security

Module `core.tools.mcp_tool` thực hiện:

- kiểm tra công cụ có được phép
- kiểm tra SQL chỉ `SELECT`
- chặn DDL/DML/điều lệnh nguy hiểm
- ghi audit request/response vào `audit_zone.agent_logs`
- redaction secrets và giới hạn output

## 4. Runtime Phase 3

`core.graph.langgraph_runtime.LangGraphRuntime` tích hợp:

- `LLMRouter`
- `SemanticSchemaRetriever`
- `MCPTool`

Nó xây dựng trace bao gồm lựa chọn model, context schema và SQL preview.

## 5. Cách chạy

Giữ nguyên cách chạy Phase 2:

```bash
python run.py api
python run.py ui
```

Phase 3 hiện tại dùng runtime mới để phản hồi prompt với routing và schema-aware trace.
