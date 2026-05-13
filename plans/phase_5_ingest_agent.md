# Phase 5 — Reasoning & Planning Layers
## Agentic CRM System

---

# 1. Tổng quan Phase 5

Phase 5 là giai đoạn biến hệ thống từ “biết nhận input” thành “biết suy nghĩ có cấu trúc”.

Nếu Phase 4 là cửa ngõ tiếp nhận và làm sạch dữ liệu đầu vào, thì Phase 5 là nơi hệ thống bắt đầu:

- phân tích vấn đề nghiệp vụ
- bẻ nhỏ bài toán
- nhận diện quan hệ dữ liệu
- xác định độ phức tạp của truy vấn
- lập kế hoạch thực thi theo thứ tự rõ ràng
- chuẩn bị state sạch cho lớp Execution phía sau

Đây là phase cực kỳ quan trọng vì từ đây trở đi, AI không còn phản ứng trực tiếp theo cảm tính nữa mà phải đi qua:

```text
Reasoning → Planning → Execution
```

Nói ngắn gọn:

- Phase 4 trả lời: “Dữ liệu đầu vào này có hợp lệ không?”
- Phase 5 trả lời: “Bài toán này cần giải thế nào, theo thứ tự nào?”

Nếu làm sai Phase 5, các lớp sau có thể vẫn chạy, nhưng sẽ chạy sai hướng.

---

# 2. Mục tiêu (Objectives)

## 2.1 Xây dựng ReasoningAgent

ReasoningAgent là lớp phân tích logic trung tâm của hệ thống.

Nhiệm vụ của nó là:

- đọc input đã được chuẩn hóa từ Phase 4
- hiểu người dùng đang muốn gì
- suy luận bài toán cần giải theo nghiệp vụ CRM
- xác định bảng/view liên quan
- phân tích các mối quan hệ lookup trong Dataverse
- đánh giá độ phức tạp của yêu cầu
- tạo ra một bản reasoning có cấu trúc để lưu vào Nexus

ReasoningAgent không được nhảy thẳng sang SQL.

Nó phải trả lời được:

- “Bài toán này thực chất là gì?”
- “Cần những thực thể nào?”
- “Cần đi qua những bước logic nào?”
- “Mức độ phức tạp ra sao?”
- “Nên dùng model nào cho bước kế tiếp?”

---

## 2.2 Xây dựng PlanningAgent

PlanningAgent là lớp biến suy luận thành kế hoạch thực thi.

Nếu ReasoningAgent trả lời:

```text
Cần làm gì?
```

thì PlanningAgent trả lời:

```text
Làm theo thứ tự nào?
```

PlanningAgent phải:

- chuyển logic trừu tượng thành task cụ thể
- sắp xếp thứ tự thực thi
- gắn phụ thuộc giữa các task
- chuẩn bị task queue cho ExecutionAgent
- tạo nền cho repair plan nếu bước sau bị lỗi

---

## 2.3 Đảm bảo AI không viết SQL ngay lập tức

Một trong những nguyên tắc cốt lõi của phase này là:

```text
Không được nhảy từ câu hỏi sang SQL ngay.
```

Hệ thống phải đi qua các lớp:

1. hiểu yêu cầu
2. phân tích logic
3. lập kế hoạch
4. rồi mới thực thi

Điều này giúp:

- giảm SQL hallucination
- dễ debug
- dễ audit
- dễ cải tiến prompt
- tối ưu model routing
- tránh execution sai hướng

---

## 2.4 Ghi lại toàn bộ suy luận vào Nexus

Mọi kết quả của ReasoningAgent và PlanningAgent phải được lưu liên tục vào AgentState / Context Nexus để:

- UI có thể hiển thị realtime
- developer có thể debug
- hệ thống có thể resume khi lỗi
- các phase sau đọc được state sạch

---

# 3. Vai trò của Phase 5 trong pipeline

```text
User Input
   ↓
Phase 4 — IngestAgent
   ↓
Phase 5 — ReasoningAgent
   ↓
Phase 5 — PlanningAgent
   ↓
Phase 6 — ExecutionAgent
```

Phase 5 là cầu nối giữa:

- đầu vào đã được lọc sạch
- và lớp thực thi thật sự

Đây là lớp quyết định chất lượng của toàn bộ downstream flow.

---

# 4. ReasoningAgent — Lớp phân tích logic

## 4.1 Định nghĩa

ReasoningAgent là “bộ não phân tích” của hệ thống.

Nó không chạy SQL.  
Nó không gọi tool thực thi.  
Nó không format kết quả cuối cùng.

Nó chỉ tập trung vào việc hiểu bài toán và chuyển nó thành cấu trúc suy luận rõ ràng.

---

## 4.2 Nhiệm vụ cốt lõi

### 4.2.1 Query Decomposition

ReasoningAgent phải bẻ nhỏ câu hỏi nghiệp vụ thành các bước nhỏ có thể xử lý.

Ví dụ:

> “Top khách hàng doanh thu cao nhất quý 1”

Không nên hiểu trực tiếp là “viết SQL trả top khách hàng”.

Phải bẻ thành:

- xác định khoảng thời gian quý 1
- tìm các hợp đồng/giao dịch trong khoảng đó
- nhóm theo khách hàng
- tính tổng doanh thu
- sắp xếp giảm dần
- lấy top N

---

### 4.2.2 Relationship Mapping

Dataverse thường có nhiều lookup và mapping phức tạp.

ReasoningAgent phải dùng metadata và semantic views để xác định:

- bảng nào là entity chính
- bảng nào là bảng phụ trợ
- field nào là lookup key
- field nào là label hiển thị
- quan hệ nào cần join
- quan hệ nào không cần join

Ví dụ:

- `v_hbl_account`
- `v_hbl_contract`
- `cr987_account_am_salesid`

ReasoningAgent cần hiểu:

- cái nào là business field
- cái nào là physical field
- cái nào dùng trực tiếp
- cái nào cần mapping qua semantic layer

---

### 4.2.3 Complexity Classification

ReasoningAgent cần tự đánh giá độ phức tạp của câu hỏi để phục vụ model routing.

Các mức có thể gồm:

- `simple`
- `standard`
- `nested`
- `complex`

Ví dụ:

| Query | Complexity |
|---|---|
| Đếm số khách hàng tháng này | simple |
| Top 10 khách hàng doanh thu quý 1 | standard |
| Doanh thu theo ngành và quốc gia | nested |
| So sánh xu hướng doanh thu 3 quý | complex |

---

### 4.2.4 Semantic Intent Deepening

Intent từ Phase 4 mới chỉ là intent sơ cấp.

ReasoningAgent phải chuyển thành business intent sâu hơn.

Ví dụ:

| Intent sơ cấp | Business Intent |
|---|---|
| query | revenue_ranking |
| report | quarterly_sales_report |
| analysis | trend_comparison |

Điều này giúp PlanningAgent không phải suy luận lại từ đầu.

---

## 4.3 Output của ReasoningAgent

Output phải có cấu trúc rõ ràng và lưu được vào Nexus.

Ví dụ:

```json
{
  "thought_process": "Cần lấy dữ liệu từ v_hbl_contract trong khoảng thời gian quý 1, sau đó nhóm theo khách hàng thông qua v_hbl_account để tính tổng doanh thu và xếp hạng.",
  "required_tables": [
    "v_hbl_contract",
    "v_hbl_account"
  ],
  "required_entities": [
    "account",
    "contract",
    "revenue",
    "date_range"
  ],
  "complexity": "nested",
  "logic_plan": [
    "Xác định phạm vi thời gian quý 1",
    "Lấy dữ liệu hợp đồng",
    "Join khách hàng",
    "Tính tổng doanh thu",
    "Sắp xếp giảm dần"
  ],
  "recommended_model_tier": "medium",
  "risk_flags": []
}
```

---

# 5. PlanningAgent — Lớp lập kế hoạch thực thi

## 5.1 Định nghĩa

PlanningAgent nhận output từ ReasoningAgent và biến nó thành kế hoạch thực thi cụ thể.

Nếu ReasoningAgent trả lời:

```text
Cần làm gì?
```

thì PlanningAgent trả lời:

```text
Làm theo thứ tự nào?
```

---

## 5.2 Vai trò theo mô hình BabyAGI

PlanningAgent hoạt động theo tinh thần BabyAGI:

- tạo danh sách task
- ưu tiên task theo dependency
- cập nhật queue theo trạng thái execution
- chuẩn bị repair plan nếu lỗi

PlanningAgent không suy luận nghiệp vụ sâu, mà chuyển reasoning thành plan có thể chạy.

---

## 5.3 Nhiệm vụ cốt lõi

### 5.3.1 Task Decomposition

Ví dụ:

- Task 1: lấy dữ liệu hợp đồng
- Task 2: join khách hàng
- Task 3: tính doanh thu
- Task 4: sắp xếp
- Task 5: format output

---

### 5.3.2 Dependency Planning

Ví dụ:

```text
Task 2 phụ thuộc Task 1
Task 3 phụ thuộc Task 2
Task 5 phụ thuộc Task 4
```

PlanningAgent phải biểu diễn dependency rõ ràng để ExecutionAgent không chạy sai thứ tự.

---

### 5.3.3 Execution Readiness Check

Trước khi chuyển sang Execution Layer, PlanningAgent cần kiểm tra:

- đủ bảng chưa
- đủ entity chưa
- có ambiguity không
- có cần clarification không
- có risk flag nào không

---

### 5.3.4 Repair Plan Preparation

PlanningAgent phải chuẩn bị sẵn khả năng self-healing.

Nếu execution fail:

- rollback về đâu
- retry thế nào
- đổi strategy ra sao
- có cần replan không

---

# 6. Output của PlanningAgent

```json
{
  "status": "ready_to_execute",
  "execution_strategy": "sequential",
  "task_queue": [
    {
      "task_id": 1,
      "action": "fetch_data",
      "description": "Lấy dữ liệu hợp đồng quý 1",
      "dependencies": []
    },
    {
      "task_id": 2,
      "action": "join_entities",
      "description": "Join khách hàng",
      "dependencies": [1]
    },
    {
      "task_id": 3,
      "action": "aggregate",
      "description": "Tính tổng doanh thu",
      "dependencies": [2]
    },
    {
      "task_id": 4,
      "action": "rank",
      "description": "Xếp hạng giảm dần",
      "dependencies": [3]
    },
    {
      "task_id": 5,
      "action": "format_response",
      "description": "Format bảng Markdown",
      "dependencies": [4]
    }
  ],
  "fallback_plan": {
    "on_failure": "replan_and_retry",
    "max_retries": 2
  }
}
```

---

# 7. Tích hợp vào LangGraph

```text
User Query
   ↓
Ingest Node
   ↓
Reasoning Node
   ↓
Planning Node
   ↓
Execution Node
```

---

## 7.1 Nguyên tắc trong graph

- mỗi node nhận state rõ ràng
- mỗi node trả state rõ ràng
- trace append liên tục
- checkpoint commit liên tục
- không cho reasoning viết SQL trực tiếp

---

# 8. AgentState cập nhật trong Phase 5

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

    # Reasoning
    reasoning_summary: str
    required_tables: List[str]
    required_entities: List[str]
    complexity: str
    logic_plan: List[str]

    # Planning
    planning_status: str
    task_queue: List[Dict[str, Any]]
    fallback_plan: Dict[str, Any]

    # Nexus
    reasoning_steps: List[str]
    trace_logs: List[str]
    checkpoints: List[Dict[str, Any]]

    # Future phases
    sql_queries: List[str]
    tool_results: List[Dict[str, Any]]

    final_response: Optional[str]
    error_message: Optional[str]
```

---

# 9. Checkpointing trong Nexus

Checkpoint nên được commit:

- sau reasoning
- sau planning
- sau task generation
- trước execution
- khi retry/replan

Mục tiêu:

- replay được
- rollback được
- resume được
- debug timeline được

---

# 10. Observability & UI Impact

Sidebar realtime cần hiển thị:

- intent hiện tại
- reasoning summary
- complexity level
- selected model tier
- logic plan
- task queue
- dependency chain
- execution readiness

Người dùng phải nhìn thấy AI đang:

```text
Hiểu → Phân tích → Lập kế hoạch
```

chứ không phải “nhảy kết quả”.

---

# 11. Error Handling

## 11.1 Nếu reasoning mơ hồ

- không cho qua planning
- yêu cầu clarification
- giữ checkpoint hiện tại

---

## 11.2 Nếu planning fail

- log audit
- stop execution
- ghi error state
- không gọi SQL layer

---

## 11.3 Nếu entity không đủ

Ví dụ:

- thiếu khoảng thời gian
- thiếu customer scope
- thiếu dimension

→ phải hỏi lại thay vì đoán.

---

# 12. Suggested Folder Structure

```plaintext
/project-root
├── core/
│   ├── agents/
│   │   ├── reasoning_agent.py
│   │   └── planning_agent.py
│   │
│   ├── graph/
│   │   ├── workflow.py
│   │   ├── state.py
│   │   └── nodes/
│   │       ├── reasoning_node.py
│   │       └── planning_node.py
│   │
│   ├── reasoning/
│   │   ├── decomposition.py
│   │   ├── relationship_mapper.py
│   │   └── complexity_classifier.py
│   │
│   ├── planning/
│   │   ├── task_builder.py
│   │   ├── dependency_resolver.py
│   │   └── repair_planner.py
│   │
│   └── audit/
│       ├── reasoning_logger.py
│       └── planning_logger.py
```

---

# 13. Success Criteria

Phase 5 được xem là hoàn thành khi:

- ReasoningAgent phân tích đúng bài toán
- PlanningAgent tạo task queue rõ ràng
- dependency chain chính xác
- không sinh SQL ở reasoning layer
- state được commit vào Nexus liên tục
- UI hiển thị realtime reasoning/planning
- execution chỉ nhận structured plan

---

# 14. Kết luận

Phase 5 là tầng biến hệ thống từ:

```text
Input Processing
```

thành:

```text
Structured Reasoning & Execution Planning
```

Nếu Phase 4 giúp hệ thống “nhận đúng dữ liệu”, thì Phase 5 giúp hệ thống:

- hiểu đúng vấn đề
- suy luận đúng logic
- lập đúng kế hoạch
- chuẩn bị đúng execution flow

Đây là nền tảng để toàn bộ Agentic CRM hoạt động ổn định, explainable và có khả năng mở rộng lâu dài.