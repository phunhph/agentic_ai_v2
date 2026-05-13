# Phase 6 — Execution, Reflection & Continuous Learning

## Mục tiêu

Phase 6 đưa hệ thống từ kế hoạch sang hành động thực tế.

Mục tiêu chính:

- thực thi task queue một cách an toàn
- kiểm tra kết quả và phát hiện lỗi
- thực hiện retry hoặc replan khi cần
- lưu kinh nghiệm học được thành bộ nhớ dài hạn
- duy trì audit/tracing đầy đủ để dễ debug và cải tiến

## 1. ExecutionAgent

Module `core.agents.execution_agent` sẽ là lớp thực thi chính.

Chức năng:

- nhận `task_queue`, `mini_schema`, `execution_context`, `thread_id`
- sinh SQL động từ kế hoạch Phase 5
- gọi MCP tool an toàn để chạy truy vấn
- bắt lỗi kỹ thuật và nghiệp vụ
- lưu execution state vào Nexus

Nguyên tắc:

- chỉ chạy theo task queue
- không tự động suy luận lại toàn bộ vấn đề
- không chạy query ngoài phạm vi task
- chỉ thực thi qua MCP safe executor

## 2. ReflectorAgent

Module `core.agents.reflector_agent` là lớp kiểm tra.

Chức năng:

- kiểm tra kết quả có hợp lý với yêu cầu không
- tìm lỗi rỗng bất thường
- đối chiếu output với câu hỏi gốc
- xác định xem cần retry hay replan
- tạo feedback cho loop tự sửa chữa

## 3. Self-Healing Loop

Phase 6 cần một vòng tự phục hồi như sau:

1. ExecutionAgent chạy task
2. ReflectorAgent đánh giá kết quả
3. Nếu PASS: hoàn tất và trả về
4. Nếu FAIL: quay lại PlanningAgent hoặc ReasoningAgent
5. Thực hiện retry trong giới hạn an toàn

Mục tiêu:

- giảm sự can thiệp thủ công
- tránh repeat failure
- cải thiện độ chính xác qua mỗi lần retry

## 4. LearningAgent

Module `core.agents.learning_agent` sẽ lưu kinh nghiệm.

Nó tập trung vào:

- success/failure pattern
- query pattern
- lỗi execution
- context hữu ích

Dữ liệu này sẽ được vectorize và lưu vào `knowledge_zone.agent_embeddings` để hỗ trợ tra cứu và cải thiện hành vi sau này.

## 5. Schema và công cụ an toàn

Phase 6 vẫn tiếp tục dùng:

- `audit_zone.agent_logs` cho audit event
- `audit_zone.checkpoints` cho trạng thái Nexus
- `MCPTool` để kiểm soát SQL execution

Grace rules:

- chỉ cho phép `SELECT`
- chặn DDL/DML/điều lệnh nguy hiểm
- log có redaction secrets
- các query phức tạp phải được review bởi reflector

## 6. Runtime integration

`core.graph.langgraph_runtime` nên mở rộng để hỗ trợ:

- ExecutionAgent
- ReflectorAgent
- LearningAgent
- retry/replan loop

Flow dự kiến:

1. IngestAgent
2. ReasoningAgent
3. PlanningAgent
4. ExecutionAgent
5. ReflectorAgent
6. LearningAgent

## 7. Cách chạy

Giữ nguyên như các phase trước:

```bash
python run.py api
python run.py ui
```

## 8. Tình trạng hiện tại

Tài liệu này bổ sung Phase 6 dưới dạng setup doc.

Các thư mục/điểm cần bổ sung tiếp theo:

- `core/agents/execution_agent.py`
- `core/agents/reflector_agent.py`
- `core/agents/learning_agent.py`
- Mở rộng `core/graph/langgraph_runtime.py` để điều phối execution/reflection/learning
- Validation cho loop retry và self-healing
