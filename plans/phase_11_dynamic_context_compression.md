# Phase 11: Dynamic Context & Semantic Compression

## Mục tiêu

Chuyển hệ thống từ cơ chế **"nhồi toàn bộ context"** sang mô hình **"truy xuất và nén ngữ cảnh thông minh"** nhằm:

- Giảm 60–80% token usage
- Hạn chế lỗi:
  - `Context Window Exceeded`
  - `503 High Demand`
- Tăng tốc độ phản hồi (Latency)
- Giảm chi phí API
- Tăng độ chính xác khi sinh SQL và reasoning

---

# 1. Vấn đề hiện tại (Current Bottleneck)

## 1.1 Context Overload

Hiện tại hệ thống đang gửi toàn bộ:

- Database Schema
- Prompt logic
- Chat history 10–20 messages
- Metadata nội bộ

trong **mọi request**.

Điều này khiến context bị phình to cực nhanh.

---

## 1.2 Semantic Noise

AI bị nhiễu bởi các thông tin không liên quan.

Ví dụ:

- User hỏi về:
  - nhân sự
  - hợp đồng

Nhưng context vẫn chứa:

- schema kho hàng
- inventory tables
- logistics rules

Kết quả:

- SQL sinh sai bảng
- Model reasoning lệch hướng
- Tăng token vô ích

---

## 1.3 Hard-coded Context Limits

Hiện tại việc cắt context đang dùng kiểu:

```python
messages[-5:]
```

Cách này có vấn đề:

- Mất short-term memory quan trọng
- Không dựa trên semantic relevance
- Không ưu tiên thông tin đang được hỏi

---

# 2. Giải pháp: Kiến trúc “Nén 3 lớp”

---

# Layer 1 — Semantic History Truncation

## Mục tiêu

Giữ lại lịch sử hội thoại **theo ý nghĩa**, không theo số lượng message.

---

## Cơ chế hoạt động

### 2.1 Conversation Summarization

Khi tổng token vượt ngưỡng:

```python
MAX_HISTORY_TOKENS = 2000
```

hệ thống sẽ:

- Gọi lightweight model:
  - `gemini-2.0-flash`
- Tóm tắt:
  - decisions
  - entities
  - pending tasks
  - important user intents

và lưu vào:

```python
state["conversation_summary"]
```

---

### 2.2 Relevance Filtering

Chỉ giữ lại các message liên quan đến:

- entity hiện tại
- intent hiện tại
- task hiện tại

Ví dụ user hỏi:

```text
"Cho tôi danh sách hợp đồng sắp hết hạn"
```

Hệ thống chỉ giữ các messages chứa:

- hợp đồng
- khách hàng
- expiry
- contract
- CRM

Các message unrelated sẽ bị loại bỏ.

---

## Kết quả

### Trước

```python
messages[-10:]
```

### Sau

```python
relevant_messages + compressed_summary
```

---

# Layer 2 — Prompt Compression

## Mục tiêu

Chỉ nạp instruction cần thiết cho từng tác vụ.

---

## Small-to-Big Prompting

Thay vì dùng một mega-prompt duy nhất:

```text
SYSTEM_PROMPT = 5000 lines
```

Ta chia thành các module nhỏ.

---

## Instruction Blocks

Ví dụ:

```python
SQL_BLOCK
REASONING_BLOCK
CRM_BLOCK
RAG_BLOCK
GENERAL_CHAT_BLOCK
ANALYTICS_BLOCK
```

---

## Dynamic Prompt Loading

### Nếu user hỏi SQL

Load:

```python
SQL_BLOCK
SCHEMA_BLOCK
SAFETY_RULES
```

---

### Nếu user chỉ chat

Load:

```python
GENERAL_CHAT_BLOCK
```

Không cần:

- schema
- SQL rules
- DB metadata

---

## Lợi ích

- Prompt ngắn hơn
- Model tập trung hơn
- Giảm hallucination
- Giảm latency

---

# Layer 3 — Token Budget & Adaptive Compression

## Mục tiêu

Quản lý token chủ động trước khi gửi request.

---

# Token Budget Manager

## Luồng xử lý

### Step 1 — Estimate Token

```python
current_tokens = (
    count_tokens(messages)
    + count_tokens(context)
    + count_tokens(system_prompt)
)
```

---

### Step 2 — Budget Check

```python
MAX_CONTEXT = 8000
WARNING_THRESHOLD = 0.8
```

---

### Step 3 — Adaptive Compression

Nếu:

```python
current_tokens > MAX_CONTEXT * WARNING_THRESHOLD
```

thì kích hoạt:

# Extreme Compression Mode

---

## Extreme Compression Strategy

### Schema Compression

Chỉ giữ:

- bảng liên quan
- columns quan trọng
- foreign keys chính

Ví dụ:

### Before

```sql
employees(
  id,
  full_name,
  phone,
  birthday,
  address,
  tax_code,
  ...
)
```

### After

```sql
employees(id, full_name, department_id)
```

---

### History Compression

Thay vì giữ raw messages:

```text
User asked about employee contracts.
Assistant generated SQL for expiring contracts.
User requested department filtering.
```

---

### Prompt Compression

Disable:

- verbose examples
- chain-of-thought hints
- debug instructions

---

# 3. Kiến trúc LangGraph mới

## Updated Agent Flow

```text
User Input
    ↓
Intent Detection
    ↓
Context Compressor Node
    ↓
Prompt Builder
    ↓
Reasoning Agent
    ↓
Tool Execution
    ↓
Final Response
```

---

# 4. Core Compression Node

```python
def context_compressor_node(state: AgentState):

    """
    Dynamic context compression layer
    """

    messages = state["messages"]
    full_context = state["context"]
    system_prompt = state["system_prompt"]

    current_tokens = (
        count_tokens(messages)
        + count_tokens(full_context)
        + count_tokens(system_prompt)
    )

    MAX_CONTEXT = 8000
    WARNING_THRESHOLD = 0.8

    # =====================================================
    # EXTREME COMPRESSION MODE
    # =====================================================

    if current_tokens > MAX_CONTEXT * WARNING_THRESHOLD:

        latest_query = messages[-1].content

        # -------------------------------------------------
        # 1. Compress Schema
        # -------------------------------------------------

        compressed_schema = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Extract only relevant schema information.

            User query:
            {latest_query}

            Full schema:
            {full_context}

            Rules:
            - Keep only relevant tables
            - Keep critical columns
            - Remove unrelated entities
            - Preserve relationships
            """
        )

        state["context"] = compressed_schema.text

        # -------------------------------------------------
        # 2. Summarize Old History
        # -------------------------------------------------

        old_messages = messages[:-3]

        summary = summarize_old_history(old_messages)

        compressed_history = [
            HumanMessage(
                content=f"""
                Conversation Summary:

                {summary}
                """
            )
        ]

        state["messages"] = (
            compressed_history
            + messages[-3:]
        )

        # -------------------------------------------------
        # 3. Prompt Compression
        # -------------------------------------------------

        state["system_prompt"] = build_minimal_prompt(
            user_query=latest_query
        )

        state["compression_mode"] = "extreme"

    else:
        state["compression_mode"] = "normal"

    return state
```

---

# 5. Semantic Relevance Filtering

## Ví dụ implementation

```python
def filter_relevant_messages(messages, query):

    keywords = extract_keywords(query)

    filtered = []

    for msg in messages:

        if contains_relevant_entity(msg.content, keywords):
            filtered.append(msg)

    return filtered
```

---

# 6. Dynamic Schema Retrieval

## Khuyến nghị nâng cấp tiếp theo

Thay vì hard-code schema trong memory:

### Chuyển sang:

# Vector Schema Retrieval

---

## Flow

```text
User Query
    ↓
Embed Query
    ↓
Search Relevant Tables
    ↓
Retrieve Top-K Schema
    ↓
Inject into Prompt
```

---

## Lợi ích

- Scale được database lớn
- Không cần gửi full schema
- Token cực thấp
- Chính xác hơn

---

# 7. Best Practices

## Không nên

```python
full_schema_every_request = True
```

---

## Nên dùng

```python
relevant_schema_only = True
```

---

## Không nên

```python
messages[-20:]
```

---

## Nên dùng

```python
semantic_history_selection()
```

---

## Không nên

```python
one_giant_prompt.txt
```

---

## Nên dùng

```python
modular_prompt_blocks()
```

---

# 8. KPI Sau Phase 11

| Metric | Before | After |
|---|---|---|
| Avg Tokens / Request | 12k–20k | 3k–6k |
| API Cost | High | Reduced 60–80% |
| Latency | Slow | Faster |
| SQL Accuracy | Medium | Higher |
| Context Overflow | Frequent | Rare |
| 503 Errors | Common | Significantly Reduced |

---

# 9. Kết luận

Phase 11 là bước chuyển đổi quan trọng từ:

```text
Static Prompt Engineering
```

sang:

```text
Dynamic Context Orchestration
```

Sau phase này, hệ thống sẽ có khả năng:

- hiểu ngữ cảnh theo semantic
- tự tối ưu token
- nén dữ liệu động
- scale context thông minh
- hoạt động ổn định với multi-agent workflows

Đây là nền tảng bắt buộc trước khi triển khai:

- Long-term Memory
- Multi-Agent Planning
- Autonomous SQL Agents
- Self-Reflective Reasoning
- Enterprise-scale RAG Systems