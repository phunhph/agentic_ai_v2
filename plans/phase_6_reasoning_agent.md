# Phase 6 — Execution, Reflection & Continuous Learning
## Agentic CRM System

---

# 1. Tổng quan Phase 6

Phase 6 là giai đoạn hệ thống chuyển từ:

- hiểu vấn đề
- lập kế hoạch
- chuẩn bị task

sang:

- thực thi thật
- kiểm tra thật
- sửa lỗi thật
- học từ kinh nghiệm thật

Nếu Phase 4 là cửa ngõ tiếp nhận, Phase 5 là tư duy và lập kế hoạch, thì Phase 6 là nơi Agentic CRM bắt đầu **hành động có kiểm soát**.

Đây là một phase cực kỳ quan trọng vì nó quyết định:

- câu lệnh SQL có chạy đúng không
- kết quả có đúng nghiệp vụ không
- lỗi có được phát hiện sớm không
- hệ thống có tự phục hồi được không
- hệ thống có tiến hóa theo thời gian không

Nói ngắn gọn:

```text
Phase 6 = Do → Verify → Recover → Learn
```

---

# 2. Mục tiêu (Objectives)

## 2.1 Xây dựng ExecutionAgent

ExecutionAgent là lớp “The Doer”.

Nó nhận:

- `task_queue`
- `mini_schema`
- `execution_context`
- `thread_id`

và thực hiện:

- sinh SQL động
- gọi MCP Server
- chạy query an toàn
- lấy kết quả
- ghi trạng thái execution vào Nexus

ExecutionAgent không phải là nơi suy luận sâu.  
Nó chỉ tập trung vào việc **làm đúng kế hoạch đã được chuẩn bị ở Phase 5**.

---

## 2.2 Xây dựng ReflectorAgent

ReflectorAgent là lớp kiểm soát chất lượng.

Nó không chạy query mới ngay lập tức.  
Nó làm nhiệm vụ:

- kiểm tra kết quả có hợp logic không
- so khớp với câu hỏi gốc
- phát hiện kết quả rỗng bất thường
- phát hiện query đúng cú pháp nhưng sai nghiệp vụ
- quyết định pass hay retry

Nói cách khác:

```text
ExecutionAgent = làm
ReflectorAgent = kiểm tra đã làm đúng chưa
```

---

## 2.3 Xây dựng Self-Healing Loop

Nếu execution lỗi hoặc kết quả đáng ngờ, LangGraph phải có khả năng:

- quay lại PlanningAgent
- hoặc quay lại ReasoningAgent nếu cần
- tái lập kế hoạch
- sinh SQL mới
- chạy lại trong giới hạn retry

Mục tiêu là tránh việc người dùng phải can thiệp thủ công quá nhiều.

---

## 2.4 Xây dựng LearningAgent

LearningAgent là lớp lưu kinh nghiệm dài hạn.

Nó lưu:

- thành công
- thất bại
- pattern query
- pattern lỗi
- context hữu ích cho lần sau

Dữ liệu này được vectorize và lưu vào `pgvector` để hỗ trợ tra cứu về sau.

---

# 3. Vai trò của Phase 6 trong pipeline

```text
User Query
   ↓
Phase 4 — Ingest
   ↓
Phase 5 — Reasoning & Planning
   ↓
Phase 6 — Execution
   ↓
Phase 6 — Reflection
   ↓
Phase 6 — Learning
```

Phase 6 là nơi hệ thống bắt đầu tạo ra giá trị thực.

Nếu Phase 5 trả lời:

```text
Cần làm gì và làm theo thứ tự nào?
```

thì Phase 6 trả lời:

```text
Tôi đã làm xong chưa, có đúng không, và tôi sẽ học gì từ lần này?
```

---

# 4. Kiến trúc tổng thể của Phase 6

```text
Task Queue
   ↓
ExecutionAgent
   ↓
safe_executor (MCP)
   ↓
PostgreSQL / Result Set
   ↓
ReflectorAgent
   ↓
PASS → Format Response
FAIL → Replan / Retry
   ↓
LearningAgent
   ↓
Vector Memory Store
```

---

# 5. ExecutionAgent — Lớp thực thi

## 5.1 Định nghĩa

ExecutionAgent là lớp chịu trách nhiệm thực thi task queue.

Nó phải:

- đọc từng task một cách tuần tự hoặc theo dependency
- sinh SQL phù hợp với mini-schema
- gọi công cụ an toàn thông qua MCP
- bắt lỗi kỹ thuật
- ghi trace và audit
- lưu kết quả trung gian vào state

ExecutionAgent **không được tự ý suy luận lại toàn bộ bài toán**.  
Nó chỉ làm đúng phần đã được lên kế hoạch.

---

## 5.2 Nguyên tắc thiết kế

ExecutionAgent phải tuân thủ các nguyên tắc sau:

- **Plan-driven**: chỉ chạy theo task queue
- **Safe execution**: chỉ qua safe_executor
- **Small context**: chỉ dùng mini-schema liên quan
- **Deterministic behavior**: giảm hành vi mơ hồ
- **Traceable output**: mọi bước đều có log
- **Retry-aware**: có thể retry khi cần nhưng có giới hạn

---

## 5.3 Nhiệm vụ cốt lõi

### 5.3.1 Task Consumption

ExecutionAgent đọc lần lượt từng task trong `task_queue`.

Ví dụ:

- task 1: lấy dữ liệu
- task 2: join entity
- task 3: aggregate
- task 4: rank
- task 5: format

---

### 5.3.2 Dynamic SQL Generation

Dựa trên:

- task description
- mini-schema
- context của reasoning
- semantic view metadata

ExecutionAgent sinh SQL động.

Mục tiêu là:

- không hardcode query
- không dùng toàn bộ schema thô
- không viết SQL vượt ngoài phạm vi task
- có thể điều chỉnh khi schema thay đổi

---

### 5.3.3 Tool Calling

ExecutionAgent gọi công cụ `safe_executor` thông qua MCP Server.

Điều này đảm bảo:

- query được kiểm soát
- chỉ `SELECT`
- có limit/timeout/validation
- không có lệnh phá hoại
- lỗi kỹ thuật được chặn ở lớp thực thi

---

### 5.3.4 Execution Error Capture

ExecutionAgent phải bắt các lỗi như:

- `column does not exist`
- `relation does not exist`
- join sai key
- syntax error
- timeout
- empty result bất thường
- permission denied

Các lỗi này không được đẩy thẳng cho người dùng.  
Chúng phải được ghi vào state để ReflectorAgent xử lý.

---

# 6. Output của ExecutionAgent

ExecutionAgent cần ghi kết quả mỗi task vào Nexus.

Ví dụ:

```json
{
  "task_id": 1,
  "sql_executed": "SELECT SUM(total_amount) FROM v_hbl_contract WHERE country_label = 'Vietnam'",
  "execution_status": "success",
  "raw_results": [
    {
      "sum": 1500000
    }
  ],
  "duration_ms": 182,
  "error_message": null
}
```

---

# 7. ReflectorAgent — Lớp phản biện và QA

## 7.1 Định nghĩa

ReflectorAgent là “hệ miễn dịch” của hệ thống.

Nó kiểm tra xem:

- query có đúng mục tiêu không
- kết quả có hợp lý không
- có bị sai logic nghiệp vụ không
- có phải kết quả rỗng thật hay do join sai
- có nên chấp nhận kết quả hay phải retry

---

## 7.2 Vai trò

Không có ReflectorAgent, hệ thống có thể sinh ra SQL:

- chạy được
- không lỗi cú pháp
- nhưng trả kết quả sai nghiệp vụ

Đây là lỗi nguy hiểm nhất vì rất khó phát hiện nếu chỉ nhìn câu lệnh.

---

## 7.3 Quy trình kiểm duyệt

### 7.3.1 Logic Verification

ReflectorAgent kiểm tra:

- câu trả lời có khớp intent ban đầu không
- aggregation có đúng loại không
- COUNT hay SUM có bị nhầm không
- filter có thiếu không
- grouping có đúng dimension không

Ví dụ:

- hỏi doanh thu mà dùng `COUNT(*)` → sai
- hỏi top khách hàng mà không order by revenue → sai
- hỏi theo quý nhưng lọc sai tháng → sai

---

### 7.3.2 Data Verification

ReflectorAgent kiểm tra:

- kết quả 0 dòng có thật hay không
- số lượng bản ghi có hợp lý không
- output có quá nhỏ hoặc quá lớn bất thường không
- dữ liệu có bị lệch do join sai không

Phân biệt:

| Trạng thái | Ý nghĩa |
|---|---|
| Legit Empty | thật sự không có dữ liệu |
| Suspicious Empty | query có vấn đề |
| Partial Result | có dữ liệu nhưng thiếu phần quan trọng |

---

### 7.3.3 Response Alignment

ReflectorAgent kiểm tra kết quả có trả lời đúng câu hỏi gốc không.

Ví dụ:

User hỏi:

```text
Top khách hàng doanh thu cao nhất quý 1
```

thì kết quả phải có:

- ranking
- doanh thu
- khoảng thời gian đúng
- entity đúng
- không trả sang một metric khác

---

# 8. Quyết định của ReflectorAgent

ReflectorAgent chỉ đưa ra một trong các trạng thái sau:

## 8.1 FINISH

Kết quả đạt yêu cầu:

- đúng logic
- đúng dữ liệu
- đúng intent
- đủ thông tin để format và trả user

---

## 8.2 RETRY

Kết quả có vấn đề:

- SQL sai
- logic lệch
- dữ liệu bất thường
- thiếu cột
- join sai

→ cần quay lại planning hoặc reasoning để sửa.

---

## 8.3 ESCALATE

Nếu retry nhiều lần mà vẫn lỗi:

- dừng tự động
- ghi lỗi rõ ràng
- trả phản hồi an toàn
- có thể yêu cầu người dùng làm rõ hoặc báo lỗi hệ thống

---

# 9. Self-Healing Loop

## 9.1 Khái niệm

Self-Healing là khả năng tự sửa sai của graph khi execution không thành công.

Đây là điểm rất quan trọng vì thực tế:

- SQL có thể sai
- schema có thể thay đổi
- dữ liệu có thể thiếu
- query có thể join sai
- intent ban đầu có thể chưa đủ rõ

Hệ thống phải biết quay xe đúng lúc.

---

## 9.2 Flow self-healing

```text
ExecutionAgent
   ↓
Fail / Suspicious Result
   ↓
ReflectorAgent
   ↓
Retry Required
   ↓
PlanningAgent / ReasoningAgent
   ↓
New Task Queue
   ↓
ExecutionAgent (retry)
```

---

## 9.3 Loop-back rules

### Quay lại PlanningAgent khi:

- task order sai
- dependency sai
- cần đổi chiến lược thực thi
- cần chia task nhỏ hơn

---

### Quay lại ReasoningAgent khi:

- logic gốc sai
- entity sai
- bảng chọn sai
- nghiệp vụ hiểu sai
- plan đúng nhưng suy luận đầu vào sai

---

## 9.4 Retry limit

Không cho retry vô hạn.

Khuyến nghị:

```text
Max Retry = 3
```

Nếu vượt quá:

- dừng loop
- log rõ lý do
- báo thất bại có kiểm soát

Mục tiêu là tránh AI bị mắc kẹt trong vòng lặp vô tận.

---

# 10. LearningAgent — Trí nhớ dài hạn

## 10.1 Định nghĩa

LearningAgent là lớp ghi nhận kinh nghiệm sau mỗi lần chạy.

Nó không thay đổi model ngay lập tức, mà lưu lại:

- query pattern
- failure pattern
- correction pattern
- execution metadata
- quality signals

Dữ liệu này được dùng cho retrieval và cải tiến về sau.

---

## 10.2 Dual-Memory Architecture

LearningAgent nên chia thành hai loại memory:

### Positive Memory

Lưu lại các mẫu thành công:

- câu hỏi
- reasoning summary
- task plan
- SQL cuối
- kết quả đúng
- model được dùng
- điều kiện thành công

Mục tiêu là lần sau gặp câu tương tự, hệ thống có thể tham chiếu lại.

---

### Negative Memory

Lưu lại các mẫu lỗi:

- SQL sai
- join sai
- filter sai
- column không tồn tại
- query trả kết quả bất thường
- reasoning lệch nghiệp vụ

Mục tiêu là lần sau hệ thống được cảnh báo trước.

---

## 10.3 Lưu vào pgvector

Các memory này cần được vectorize và lưu vào `pgvector`.

Cách này cho phép:

- semantic retrieval
- tìm pattern tương tự
- gợi ý caution note cho ExecutionAgent
- giảm lặp lại lỗi cũ

---

## 10.4 Ví dụ Positive Memory

```json
{
  "type": "positive",
  "question": "Top khách hàng doanh thu cao nhất quý 1",
  "pattern": "contract -> account -> revenue ranking",
  "sql_template": "SELECT ...",
  "result_quality": "correct",
  "notes": "Use v_hbl_contract and v_hbl_account, aggregate by customer"
}
```

---

## 10.5 Ví dụ Negative Memory

```json
{
  "type": "negative",
  "question": "Doanh thu theo khách hàng",
  "pattern": "wrong join between contract_id and account_id",
  "error_type": "join_mismatch",
  "notes": "Never join account_id directly to contract_id"
}
```

---

# 11. AgentState mở rộng cho Phase 6

```python
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    thread_id: str

    # Phase 4
    user_input: str
    normalized_input: str
    intent: str
    entities: List[Dict[str, Any]]
    security_check: str

    # Phase 5
    reasoning_summary: str
    required_tables: List[str]
    required_entities: List[str]
    complexity: str
    logic_plan: List[str]
    task_queue: List[Dict[str, Any]]

    # Phase 6 - Execution
    executed_tasks: List[Dict[str, Any]]
    sql_queries: List[str]
    raw_results: List[Dict[str, Any]]
    execution_status: str

    # Phase 6 - Reflection
    reflection_notes: List[str]
    qa_decision: str  # "finish" | "retry" | "escalate"

    # Phase 6 - Learning
    memory_signals: List[Dict[str, Any]]
    learning_tags: List[str]

    # Nexus / Trace
    trace_logs: List[str]
    checkpoints: List[Dict[str, Any]]

    # Output
    final_response: Optional[str]
    error_message: Optional[str]
```

---

# 12. Audit & Logging

## 12.1 Những gì cần log

Mỗi execution cycle cần log:

- thread_id
- task_id
- SQL sinh ra
- model dùng để sinh SQL
- duration
- raw result summary
- error details
- reflection decision
- retry count

---

## 12.2 Audit policy

Không log:

- API key
- secret
- raw sensitive payload không cần thiết

Log phải vừa đủ để:

- debug
- replay
- audit
- cải tiến

---

# 13. Gợi ý schema lưu trữ

## 13.1 Execution logs

```sql
CREATE SCHEMA IF NOT EXISTS audit_zone;

CREATE TABLE audit_zone.execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL,
    task_id INTEGER,
    sql_executed TEXT,
    execution_status TEXT NOT NULL,
    raw_results JSONB,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 13.2 Reflection logs

```sql
CREATE TABLE audit_zone.reflection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL,
    task_id INTEGER,
    reflection_notes TEXT,
    qa_decision TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 13.3 Learning memory

```sql
CREATE SCHEMA IF NOT EXISTS knowledge_zone;

CREATE TABLE knowledge_zone.query_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type TEXT NOT NULL,
    question_text TEXT,
    pattern_summary TEXT,
    sql_template TEXT,
    embedding VECTOR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

```sql
CREATE TABLE knowledge_zone.failed_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type TEXT NOT NULL,
    question_text TEXT,
    error_summary TEXT,
    correction_note TEXT,
    embedding VECTOR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 14. LangGraph loop design

```text
PlanningAgent
   ↓
ExecutionAgent
   ↓
ReflectorAgent
   ├── FINISH → Format Response
   ├── RETRY  → PlanningAgent / ReasoningAgent
   └── ESCALATE → Error Response
```

---

# 15. UI impact

Phase 6 phải phản ánh rõ trên sidebar và debug panel:

- task nào đang chạy
- SQL nào đang được sinh
- kết quả có bao nhiêu dòng
- reflector có chấp nhận không
- có retry hay không
- có memory được lưu không

Người dùng không nên chỉ thấy “AI trả lời”, mà còn thấy:

- nó đã làm gì
- nó có kiểm tra lại không
- nó có tự sửa không
- nó có học gì không

---

# 16. Failure Handling

## 16.1 SQL lỗi cú pháp

- ghi execution log
- chuyển ReflectorAgent
- đề xuất retry

---

## 16.2 Column not found

- ghi lỗi rõ ràng
- nếu có thể, quay lại planning/reasoning
- sinh SQL mới

---

## 16.3 Empty result bất thường

- kiểm tra logic
- xác định legit empty hay suspicious empty
- quyết định retry hoặc finish

---

## 16.4 Retry vượt ngưỡng

- dừng loop
- báo lỗi an toàn
- không retry vô hạn

---

# 17. Suggested folder structure

```plaintext
/project-root
├── core/
│   ├── agents/
│   │   ├── execution_agent.py
│   │   ├── reflector_agent.py
│   │   └── learning_agent.py
│   │
│   ├── graph/
│   │   ├── workflow.py
│   │   └── nodes/
│   │       ├── execution_node.py
│   │       ├── reflection_node.py
│   │       └── learning_node.py
│   │
│   ├── execution/
│   │   ├── sql_generator.py
│   │   ├── task_runner.py
│   │   └── result_collector.py
│   │
│   ├── reflection/
│   │   ├── logic_checker.py
│   │   ├── empty_result_checker.py
│   │   └── decision_engine.py
│   │
│   ├── learning/
│   │   ├── memory_writer.py
│   │   ├── memory_retriever.py
│   │   └── pattern_vectorizer.py
│   │
│   └── audit/
│       ├── execution_logger.py
│       ├── reflection_logger.py
│       └── learning_logger.py
```

---

# 18. Success Criteria

Phase 6 được xem là hoàn thành khi:

- ExecutionAgent chạy đúng task queue
- SQL được sinh và chạy an toàn
- ReflectorAgent phát hiện được lỗi logic
- hệ thống retry có kiểm soát
- loop-back hoạt động khi cần
- memory thành công và thất bại được lưu
- pgvector được dùng để tra cứu pattern
- toàn bộ hành vi có audit và trace rõ ràng

---

# 19. Kết luận

Phase 6 là giai đoạn biến hệ thống từ:

- biết phân tích
- biết lập kế hoạch

thành:

- biết thực thi
- biết kiểm tra
- biết sửa lỗi
- biết học từ kinh nghiệm

Đây là phase tạo ra sự khác biệt giữa một AI chỉ “trả lời được” và một AI có thể **vận hành bền vững trong môi trường thực tế**.

Nếu Phase 4 là đầu vào sạch, Phase 5 là tư duy có cấu trúc, thì Phase 6 chính là:

```text
Hành động có kiểm soát + Phản biện + Tiến hóa
```

Và chính ba lớp này là nền để Agentic CRM trở thành một hệ thống thật sự sống được trong production.