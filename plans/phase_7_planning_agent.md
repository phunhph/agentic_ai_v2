# Phase 7 — Lean Optimization & Scalability
## Agentic CRM System

---

# 1. Tổng quan Phase 7

Phase 7 là giai đoạn đưa hệ thống từ:

- chạy được
- đúng được
- sửa được

sang:

- chạy gọn hơn
- rẻ hơn
- nhanh hơn
- ổn định hơn
- mở rộng được

Nếu các phase trước xây nên:

- bộ não
- lớp suy luận
- execution flow
- self-healing
- long-term memory

thì Phase 7 là lớp tối ưu để toàn bộ hệ thống có thể vận hành thật trong production với:

- chi phí thấp
- tốc độ cao
- khả năng scale
- khả năng chống lỗi
- khả năng giám sát toàn hệ thống

---

# 2. Mục tiêu (Objectives)

## 2.1 Lean Context

Tinh gọn ngữ cảnh để:

- giảm token
- giảm latency
- giảm nhiễu
- tăng độ chính xác

Hệ thống chỉ được nạp đúng phần context cần thiết cho nhiệm vụ hiện tại.

---

## 2.2 Cost Optimization

Tối ưu chi phí bằng:

- routing model theo độ khó
- giảm số lần gọi model mạnh
- hạn chế retry không cần thiết
- ưu tiên local inference cho tác vụ nhỏ

---

## 2.3 Resilience

Tăng khả năng chịu lỗi khi:

- API bị 429
- provider lỗi 503
- timeout
- provider quá tải
- MCP chậm phản hồi

Hệ thống không được “sập dây chuyền”.

---

## 2.4 Observability

Toàn bộ hệ thống phải đo được:

- latency
- token usage
- API cost
- SQL performance
- retry rate
- fallback rate
- bottleneck

---

## 2.5 Scalability

Chuẩn bị cho khả năng:

- multi-tenant
- scale nhiều user
- scale nhiều org
- scale nhiều agent
- scale nhiều workflow

---

# 3. Vai trò của Phase 7 trong kiến trúc

```text
User Query
   ↓
Lean Context Engine
   ↓
Cost-Aware Router
   ↓
Execution Flow
   ↓
Observability & Metrics
   ↓
Learning & Feedback
```

Phase 7 không thay thế các phase trước.

Nó là lớp:

- tối ưu
- bảo vệ
- giám sát
- mở rộng

cho toàn bộ hệ thống.

---

# 4. Lean Context Engine

## 4.1 Triết lý

Không đưa toàn bộ dữ liệu vào model.

Càng nhiều context thừa:

- càng tốn token
- càng chậm
- càng dễ hallucination
- càng giảm accuracy

Mục tiêu là:

```text
Minimum Context → Maximum Accuracy
```

---

# 5. Dynamic Context Compression

## 5.1 Semantic Schema Pruning

Chỉ nạp schema liên quan tới intent hiện tại.

Ví dụ:

User hỏi:

```text
Doanh thu hợp đồng quý 1
```

Chỉ cần:

- `v_hbl_contract`
- `v_hbl_account`
- mapping liên quan

Không cần:

- bảng audit
- bảng user
- bảng permission
- schema không liên quan

---

## 5.2 Metadata-Based Selection

Schema selection phải dựa trên:

- entity extraction
- intent classification
- semantic similarity
- relationship graph

Không hardcode mapping bằng tay.

---

## 5.3 Mini Schema Injection

Thay vì:

```text
10.000+ tokens schema
```

hệ thống chỉ inject:

```text
300–800 tokens schema
```

đủ để model reasoning chính xác.

---

## 5.4 History Truncation

Không gửi toàn bộ chat history.

Hệ thống phải:

- summarize hội thoại cũ
- giữ lại context quan trọng
- loại bỏ đoạn dư thừa
- bỏ reasoning trace không còn giá trị

---

## 5.5 Context Summarization

Các state cũ sẽ được nén thành:

- current intent
- active entities
- last execution
- unresolved issues
- current business objective

---

# 6. Cost Optimization Engine

## 6.1 Triết lý

Không dùng:

```text
DAO MỔ TRÂU → GIẾT GÀ
```

Câu hỏi đơn giản không được đi qua pipeline đắt tiền.

---

# 7. Cost-Aware Routing

## 7.1 Dynamic Model Selection

Hệ thống chọn model theo:

- độ khó
- loại task
- mức độ reasoning
- latency requirement
- cost policy

---

## 7.2 Routing Matrix

| Task Type | Priority | Suggested Model |
|---|---|---|
| Greeting / small talk | tốc độ | Flash / lightweight |
| Intent classification | siêu rẻ | Local classifier |
| Basic SQL reasoning | cân bằng | Flash / Groq |
| Complex reasoning | chính xác | Gemini Pro / Claude |
| Reflection / QA | logic mạnh | Claude / strong reasoning model |

---

## 7.3 Cost Guardrails

Các giới hạn cần có:

- max token input
- max retries
- max reasoning depth
- max tool calls
- max concurrent executions

---

## 7.4 Local First Strategy

Nếu task đủ đơn giản:

- xử lý local
- không gọi API ngoài
- không tốn token

Ví dụ:

- greeting
- intent sơ cấp
- query classification
- routing

---

# 8. Resilience Engine

## 8.1 Mục tiêu

Hệ thống phải sống được khi:

- provider lỗi
- API rate limit
- timeout
- provider mất kết nối
- model unavailable

---

# 9. Exponential Backoff

## 9.1 Retry Policy

Nếu gặp:

```text
429 Rate Limit
```

hệ thống không retry ngay lập tức.

Chu kỳ:

```text
2s → 4s → 8s → 16s
```

Có jitter để tránh request burst.

---

# 10. Multi-Provider Fallback

## 10.1 Fallback Chain

Ví dụ:

```text
Gemini Flash
   ↓ fail
Groq Llama
   ↓ fail
Claude
```

Fallback phải được quản lý tập trung.

Không để agent tự fallback lung tung.

---

# 11. Circuit Breaker Pattern

## 11.1 Mục tiêu

Nếu provider lỗi liên tục:

- tạm khóa provider
- chuyển traffic sang provider khác
- tránh spam request vô ích

---

## 11.2 Circuit States

| State | Ý nghĩa |
|---|---|
| CLOSED | hoạt động bình thường |
| OPEN | provider đang bị chặn |
| HALF_OPEN | thử khôi phục |

---

# 12. Graceful Degradation

## 12.1 Triết lý

Nếu một phần hệ thống lỗi:

- phần còn lại vẫn hoạt động
- không crash toàn bộ pipeline

---

## 12.2 Ví dụ

Nếu:

- Reflection model fail

thì:

- vẫn có thể trả basic response
- gắn warning
- log lại lỗi

---

# 13. Observability Cockpit

## 13.1 Mục tiêu

Admin phải nhìn thấy:

- hệ thống đang làm gì
- tốn bao nhiêu tiền
- nghẽn ở đâu
- lỗi ở đâu
- agent nào đang bất thường

---

# 14. Cost Analytics

## 14.1 Metrics cần theo dõi

- token input
- token output
- cost theo request
- cost theo tenant
- cost theo model
- cost theo agent

---

## 14.2 Dashboard cần có

- Daily API Spend
- Cost by Agent
- Cost by Tenant
- Model Usage
- Token Consumption Trend

---

# 15. Bottleneck Detection

## 15.1 Theo dõi latency

Đo thời gian cho:

- ingest
- reasoning
- planning
- execution
- reflection
- learning

---

## 15.2 Slow SQL Detection

Theo dõi:

- execution time
- row count
- query frequency
- repeated failed queries

---

# 16. Failure Analytics

## 16.1 Theo dõi lỗi

- 429 frequency
- 503 frequency
- timeout rate
- retry success rate
- fallback usage
- reflection failures

---

# 17. Feedback Loop

## 17.1 User Feedback System

UI cần có:

- 👍
- 👎

---

## 17.2 Nếu user bấm 👎

Hệ thống sẽ:

- flag response
- lưu negative memory
- giảm ranking của pattern sai
- cảnh báo future execution

---

# 18. Learning Feedback Integration

## 18.1 Feedback → Learning Flow

```text
User Feedback
   ↓
Memory Signal
   ↓
Vector Embedding
   ↓
pgvector Storage
   ↓
Future Retrieval Optimization
```

---

# 19. Scalability Architecture

## 19.1 Multi-Tenant Support

Một hệ thống phải phục vụ được:

- nhiều công ty
- nhiều workspace
- nhiều user

mà không lẫn dữ liệu.

---

# 20. Row-Level Security (RLS)

## 20.1 PostgreSQL RLS

Dùng:

```sql
ALTER TABLE ... ENABLE ROW LEVEL SECURITY;
```

để:

- cô lập tenant
- chống data leak
- enforce security ở tầng DB

---

## 20.2 Org Isolation

Mọi query phải có:

```text
org_id
```

trong execution context.

---

# 21. Tenant-Aware Execution

## 21.1 MCP Layer

MCP phải inject:

- org_id
- role
- permission scope

vào mọi execution request.

---

## 21.2 Agent Isolation

Agent không được:

- truy cập cross-tenant
- reuse state giữa tenant
- leak memory giữa org

---

# 22. DANN — Dynamic Agentic Neural Network

## 22.1 Mục tiêu

Tạo lớp local inference siêu nhanh để:

- giảm token cost
- giảm latency
- giảm phụ thuộc external API

---

## 22.2 Vai trò

DANN dùng cho:

- intent classification
- lightweight routing
- greeting detection
- low-level gating
- query categorization

---

## 22.3 Latency Target

```text
< 50ms
```

cho các tác vụ gating đơn giản.

---

# 23. DANN Pipeline

```text
User Query
   ↓
Local Intent Model
   ↓
Fast Classification
   ↓
Cost-Aware Router
   ↓
LLM Pipeline
```

---

# 24. Optimization Workflow

```text
User Input
   ↓
Context Compression
   ↓
Schema Pruning
   ↓
Local Intent Classification
   ↓
Cost-Aware Routing
   ↓
Execution Pipeline
   ↓
Metrics Collection
   ↓
Feedback Processing
```

---

# 25. Audit & Metrics Storage

## 25.1 Các bảng cần có

```text
audit_zone.api_cost_logs
audit_zone.latency_logs
audit_zone.retry_logs
audit_zone.fallback_logs
audit_zone.feedback_logs
audit_zone.performance_metrics
```

---

# 26. Logging Requirements

## 26.1 Phải log

- model usage
- token usage
- retries
- fallback events
- execution duration
- reflection duration
- SQL latency

---

## 26.2 Không log

- API keys
- secrets
- raw credentials
- sensitive payloads không cần thiết

---

# 27. Folder Structure đề xuất

```text
/project-root
├── core/
│
├── optimization/
│   ├── context/
│   │   ├── schema_pruner.py
│   │   ├── history_summarizer.py
│   │   ├── context_compressor.py
│   │   └── token_manager.py
│   │
│   ├── routing/
│   │   ├── cost_router.py
│   │   ├── provider_router.py
│   │   ├── fallback_policy.py
│   │   ├── retry_policy.py
│   │   └── circuit_breaker.py
│   │
│   ├── observability/
│   │   ├── metrics_collector.py
│   │   ├── latency_tracker.py
│   │   ├── cost_tracker.py
│   │   ├── feedback_engine.py
│   │   └── dashboard_service.py
│   │
│   ├── scalability/
│   │   ├── tenant_guard.py
│   │   ├── rls_manager.py
│   │   ├── org_context.py
│   │   └── workspace_resolver.py
│   │
│   └── local_ai/
│       ├── intent_classifier.py
│       ├── local_router.py
│       └── dann_engine.py
```

---

# 28. Success Criteria

Phase 7 được xem là hoàn thành khi:

- context được nén hiệu quả
- token usage giảm mạnh
- routing hoạt động theo cost policy
- fallback ổn định
- retry có kiểm soát
- observability dashboard hoạt động
- latency đo được toàn pipeline
- RLS hoạt động đúng
- multi-tenant isolation an toàn
- local DANN inference hoạt động nhanh

---

# 29. Kết luận

Phase 7 là giai đoạn đưa hệ thống từ:

```text
AI hoạt động được
```

thành:

```text
AI production-grade
```

Đây là lớp:

- tối ưu
- chống lỗi
- đo lường
- mở rộng

để Agentic CRM có thể:

- phục vụ nhiều user
- vận hành dài hạn
- tiết kiệm chi phí
- scale enterprise
- hoạt động ổn định trong thực tế

Nếu các phase trước xây dựng trí thông minh, thì Phase 7 là thứ giúp trí thông minh đó:

- sống được
- chạy bền
- scale được
- và tối ưu được theo thời gian