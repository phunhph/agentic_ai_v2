# Phase 4 — Ingest Layer & Context Nexus
## Agentic CRM System

---

# 1. Tổng quan Phase 4

Phase 4 là lớp “cửa ngõ thông minh” của toàn bộ hệ thống Agentic CRM.

Đây là nơi mọi dữ liệu đầu vào từ người dùng được:

- tiếp nhận
- kiểm tra
- chuẩn hóa
- phân loại
- bảo vệ
- lưu trạng thái
- commit vào Context Nexus

Nếu các phase trước tập trung vào:

- hạ tầng
- MCP
- routing
- observability

thì Phase 4 là nơi hệ thống bắt đầu thật sự “hiểu” người dùng.

Đây cũng là phase cực kỳ quan trọng vì:

```text
Input sai → reasoning sai
Reasoning sai → planning sai
Planning sai → execution sai
```

Nói cách khác:

```text
Phase 4 quyết định chất lượng toàn bộ pipeline phía sau.
```

---

# 2. Triết lý kiến trúc của Phase 4

Phase 4 không được hoạt động như một chatbot thông thường.

Nó phải hoạt động như:

```text
Intelligent Gateway + Context Memory Hub
```

Mọi request đều phải đi qua:

1. Security validation
2. Input normalization
3. Intent detection
4. Entity extraction
5. Context synchronization
6. Nexus checkpoint commit

rồi mới được phép đi tiếp sang lớp suy luận.

---

# 3. Mục tiêu (Objectives)

## 3.1 Xây dựng IngestAgent làm Gatekeeper

IngestAgent là lớp đầu tiên tiếp xúc với dữ liệu người dùng.

Vai trò của nó:

- không query database
- không viết SQL
- không trả kết quả cuối

Nó chỉ tập trung vào:

- hiểu input
- làm sạch input
- bảo vệ hệ thống
- tạo structured state
- commit context vào Nexus

---

## 3.2 Xây dựng Context Nexus theo mô hình Git-style

Context Nexus là “trục trí nhớ” của hệ thống.

Mọi thay đổi state phải được:

- checkpoint
- version hóa
- lưu lịch sử
- rollback được
- replay được
- resume được

Triết lý của Nexus:

```text
One Thread = One Persistent Reasoning Timeline
```

---

## 3.3 Đảm bảo Intent Classification chính xác

Hệ thống phải hiểu rõ:

- user đang muốn làm gì
- loại tác vụ là gì
- cần reasoning hay chỉ chat
- có cần query DB không
- có cần clarification không

Nếu intent sai:

- toàn bộ graph sẽ đi sai hướng

---

## 3.4 Đảm bảo Entity Extraction chính xác

AI phải hiểu đúng:

- khách hàng nào
- thời gian nào
- quốc gia nào
- ngành nghề nào
- bảng nào liên quan

Entity extraction là nền cho reasoning phase.

---

## 3.5 Chặn Prompt Injection từ đầu vào

Phase 4 phải là lớp phòng thủ đầu tiên chống:

- prompt injection
- SQL injection
- context poisoning
- system probing
- jailbreak attempt
- malformed payload

Nguyên tắc:

```text
Reject early before wasting reasoning tokens.
```

---

# 4. Vai trò của Ingest Layer trong toàn hệ thống

```text
User Input
   ↓
Ingest Layer
   ↓
Reasoning Layer
   ↓
Planning Layer
   ↓
Execution Layer
```

Ingest Layer là nơi:

- chuẩn hóa dữ liệu
- loại bỏ nhiễu
- bảo vệ pipeline
- đồng bộ context
- tạo state sạch

Nếu ví hệ thống như một CPU:

| Thành phần | Vai trò |
|---|---|
| Ingest Layer | Input Controller |
| Context Nexus | RAM + Git History |
| Reasoning Layer | CPU Logic |
| Execution Layer | Instruction Executor |

---

# 5. IngestAgent — Intelligent Gateway

## 5.1 Định nghĩa

IngestAgent là node đầu tiên trong LangGraph.

Nó không được phép:

- generate SQL
- gọi execution tool
- truy vấn dữ liệu thật

Nó chỉ được phép:

- hiểu input
- validate input
- chuẩn hóa state
- commit context

---

# 6. Kiến trúc xử lý của IngestAgent

```text
Raw User Input
   ↓
Input Sanitizer
   ↓
Security Validator
   ↓
Intent Classifier
   ↓
Entity Extractor
   ↓
Context Synchronizer
   ↓
Checkpoint Commit
   ↓
Structured AgentState
```

---

# 7. Input Sanitization Layer

## 7.1 Mục tiêu

Làm sạch input trước khi AI reasoning.

Nếu không sanitize sớm:

- dễ bị injection
- dễ lệch intent
- tăng hallucination
- tăng token noise

---

## 7.2 Các bước normalize

### Chuẩn hóa unicode

Ví dụ:

- ký tự lạ
- zero-width char
- hidden unicode

---

### Chuẩn hóa thời gian

Ví dụ:

| Input | Normalize |
|---|---|
| tháng này | current_month |
| quý 1 | Q1 |
| đầu năm | start_of_year |

---

### Chuẩn hóa business synonym

Ví dụ:

| User nói | Semantic mapping |
|---|---|
| khách hàng | account |
| sales | revenue |
| hợp đồng | contract |

---

### Chuẩn hóa format query

Ví dụ:

```text
Top KH doanh thu Q1
```

→

```text
top customer revenue quarter 1
```

---

# 8. Security Validation Layer

## 8.1 Vai trò

Đây là lớp firewall logic cho Agentic AI.

Nó phải phát hiện:

- prompt injection
- SQL injection
- hidden instruction
- role hijacking
- system probing

---

## 8.2 Các pattern cần chặn

### Prompt Injection

Ví dụ:

```text
Ignore previous instructions
```

```text
You are now system admin
```

---

### SQL Injection

Ví dụ:

```sql
DROP TABLE
UNION SELECT
DELETE FROM
TRUNCATE
```

---

### Secret Probing

Ví dụ:

```text
show .env
show API keys
show system prompt
```

---

### Context Hijacking

Ví dụ:

```text
forget previous context
replace memory
```

---

## 8.3 Security Policy

Phase 4 phải đi theo mô hình:

```text
Allowlist-first Security
```

Nghĩa là:

- chỉ cho phép action hợp lệ
- mọi thứ không rõ → block hoặc clarify

Không dùng tư duy:

```text
Không cấm thì cho qua
```

---

# 9. Intent Classification

## 9.1 Vai trò

Intent classification quyết định:

- graph đi nhánh nào
- dùng model nào
- có query DB không
- có cần reasoning không

---

## 9.2 Intent taxonomy đề xuất

| Intent | Ý nghĩa |
|---|---|
| query | truy vấn dữ liệu |
| report | tạo báo cáo |
| analysis | phân tích |
| compare | so sánh |
| summarize | tóm tắt |
| help | hướng dẫn |
| chat | hội thoại thường |
| unknown | chưa xác định |

---

## 9.3 Ví dụ

| User Input | Intent |
|---|---|
| top khách hàng doanh thu | query |
| tạo báo cáo tháng này | report |
| so sánh doanh thu 2 quý | compare |
| xin chào | chat |

---

## 9.4 Clarification Strategy

Nếu confidence thấp:

- không đoán
- hỏi lại
- giữ checkpoint hiện tại

Ví dụ:

```text
“Bạn muốn xem doanh thu theo khách hàng hay theo hợp đồng?”
```

---

# 10. Entity Extraction Layer

## 10.1 Vai trò

Entity extraction là nền cho reasoning phase.

AI phải hiểu:

- đang nói về entity nào
- dimension nào
- filter nào
- time range nào

---

## 10.2 Entity types

| Entity Type | Ví dụ |
|---|---|
| account | khách hàng |
| contract | hợp đồng |
| revenue | doanh thu |
| country | quốc gia |
| industry | ngành nghề |
| date_range | quý 1 |

---

## 10.3 Metadata-driven Extraction

Không hardcode entity logic.

Phải lấy từ:

- semantic metadata
- db.json
- AI-friendly views
- business glossary

---

## 10.4 Output ví dụ

```json
{
  "entities": [
    {
      "type": "account",
      "value": "Toyota"
    },
    {
      "type": "date_range",
      "value": "Q1"
    }
  ]
}
```

---

# 11. Context Nexus — Persistent Memory Backbone

## 11.1 Định nghĩa

Context Nexus là hệ thống quản lý state trung tâm của toàn bộ graph.

Nó hoạt động như:

```text
Git + Memory Bus + Persistent State Store
```

---

## 11.2 Mục tiêu

Nexus phải đảm bảo:

- memory continuity
- rollback
- replay
- resume
- thread isolation
- state consistency

---

# 12. Git-style Checkpointing

## 12.1 Triết lý

Mỗi bước reasoning là một commit.

Ví dụ:

```text
Input normalized
→ commit

Intent classified
→ commit

Entity extracted
→ commit
```

---

## 12.2 Lợi ích

- resume sau crash
- replay session
- debug timeline
- compare state evolution
- observability realtime

---

# 13. Thread Isolation

## 13.1 Nguyên tắc

Mỗi session phải có:

```text
thread_id riêng
```

Không được:

- share context giữa user
- reuse reasoning state
- leak memory giữa session

---

## 13.2 Context boundary

```text
Thread A ≠ Thread B
```

Mọi:

- checkpoint
- trace
- reasoning
- planning
- SQL history

đều phải gắn thread_id.

---

# 14. Context Recovery

Nếu hệ thống lỗi:

- resume từ checkpoint gần nhất
- replay lại graph
- rollback nếu cần
- giữ nguyên reasoning timeline

Điều này giúp AI “nhớ kỹ” hơn thay vì chỉ nhớ trong RAM tạm.

---

# 15. AgentState — Structured Data Backbone

## 15.1 Vai trò

AgentState là object trung tâm đi xuyên suốt toàn bộ graph.

Mọi agent:

- đọc từ state
- ghi vào state
- không truyền dữ liệu tùy ý ngoài state

---

## 15.2 Định nghĩa đề xuất

```python
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):

    # Session
    thread_id: str

    # Raw Input
    user_input: str
    normalized_input: str

    # Intent & Entity
    intent: str
    intent_confidence: float
    entities: List[Dict[str, Any]]

    # Security
    security_check: str
    security_flags: List[str]

    # Nexus
    trace_logs: List[str]
    checkpoints: List[Dict[str, Any]]

    # Reasoning
    reasoning_steps: List[str]

    # Future phases
    sql_queries: List[str]
    tool_results: List[Dict[str, Any]]

    # Output
    final_response: Optional[str]
    error_message: Optional[str]
```

---

# 16. Fail-Fast Architecture

## 16.1 Triết lý

Nếu input sai:

```text
STOP IMMEDIATELY
```

Không được:

- reasoning tiếp
- gọi tool
- generate SQL

---

## 16.2 Flow chuẩn

```text
User Input
   ↓
Sanitize
   ↓
Security Check
   ↓
Intent Classification
   ↓
Entity Extraction
   ↓
Nexus Commit
   ↓
Reasoning Layer
```

---

# 17. Checkpoint Schema đề xuất

```sql
CREATE SCHEMA IF NOT EXISTS audit_zone;

CREATE TABLE audit_zone.checkpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL,
    step_name TEXT NOT NULL,
    state_snapshot JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 18. Observability Integration

Phase 4 phải stream realtime trace cho UI.

Ví dụ sidebar:

```text
[✓] Input sanitized
[✓] Security check passed
[✓] Intent classified: query
[✓] Entities extracted: account, Q1
[✓] Nexus checkpoint committed
```

---

# 19. Suggested Folder Structure

```plaintext
/project-root
├── core/
│   ├── agents/
│   │   └── ingest_agent.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   └── nodes/
│   │       ├── ingest_node.py
│   │       ├── security_node.py
│   │       ├── intent_node.py
│   │       └── entity_node.py
│   │
│   ├── nexus/
│   │   ├── checkpoint_manager.py
│   │   ├── state_serializer.py
│   │   └── state_recovery.py
│   │
│   ├── security/
│   │   ├── injection_detector.py
│   │   ├── sanitizer.py
│   │   └── policy.py
│   │
│   └── audit/
│       ├── ingest_logger.py
│       └── checkpoint_logger.py
```

---

# 20. Success Criteria

Phase 4 được xem là hoàn thành khi:

- input được normalize chính xác
- intent classification ổn định
- entity extraction đúng
- prompt injection bị chặn
- checkpoint hoạt động
- thread isolation hoạt động
- state replay được
- reasoning layer nhận structured state sạch

---

# 21. Kết luận

Phase 4 là nền móng của toàn bộ Agentic CRM.

Nếu Phase 4 làm không tốt:

- reasoning sẽ sai
- planning sẽ lệch
- execution sẽ nguy hiểm

Nếu làm tốt, hệ thống sẽ có:

- input sạch
- memory bền vững
- context liên tục
- reasoning ổn định
- observability mạnh
- khả năng resume/replay chuyên nghiệp

Đây chính là lớp biến AI từ một chatbot thông thường thành một hệ thống Agentic có trí nhớ, có kiểm soát và có khả năng vận hành lâu dài.