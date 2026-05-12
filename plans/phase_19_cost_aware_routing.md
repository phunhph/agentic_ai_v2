# Phase 19: Model Orchestration & Cost-Aware Routing

## Mục tiêu

Xây dựng một lớp điều phối thông minh giúp hệ thống:

# chọn đúng model cho đúng nhiệm vụ

với mục tiêu:

- giảm 50–70% chi phí API
- tối ưu latency
- tăng độ ổn định hệ thống
- tránh lãng phí model mạnh cho task đơn giản

---

# 1. Vấn đề hiện tại (Current Issues)

## 1.1 Resource Waste

Hiện tại hệ thống thường:

```text
Gemini Pro → dùng để chào hỏi
Claude Opus → dùng để summarize text ngắn
```

---

# Đây là anti-pattern nghiêm trọng

vì:

- cost cao không cần thiết
- latency tăng
- quota bị cạn nhanh

---

## 1.2 Latency Inconsistency

Một số model:

| Model | Vấn đề |
|---|---|
| Gemini Pro | chậm |
| Claude Opus | rất chậm |
| Groq | nhanh |

---

# Kết quả:

- UI Streamlit bị delay
- user experience không ổn định

---

## 1.3 Single Provider Risk

Nếu chỉ dùng 1 provider:

- outage = hệ thống chết
- rate limit = system stall
- downtime = mất service

---

# 2. Tư duy cốt lõi của Phase 19

## Không phải model nào cũng cần "thông minh nhất"

---

# Mỗi task có mức độ:

```text
Cost ↔ Intelligence tradeoff
```

---

# 3. Model Orchestration Architecture

Phase 19 bổ sung:

1. Task Classification
2. Cost-aware Routing
3. Model Hierarchy
4. Fallback System
5. Budget Control
6. Latency Optimization

---

# 4. Task Classification System

## Mục tiêu

Trước khi gọi LLM:

# xác định độ khó của task

---

# 4.1 LEVEL 1 — Easy Tasks

## Bao gồm:

- chào hỏi
- summarize text
- format output
- schema compression

---

# Yêu cầu:

- rẻ
- nhanh
- không cần reasoning sâu

---

## 4.2 LEVEL 2 — Medium Tasks

## Bao gồm:

- SQL đơn giản
- retrieval
- knowledge lookup
- basic aggregation

---

## 4.3 LEVEL 3 — Hard Tasks

## Bao gồm:

- multi-step reasoning
- financial analysis
- debugging SQL
- reflection correction (Phase 13–18)

---

# 5. Routing Matrix

## Model Selection Table

| Level | Primary Model | Fallback |
|---|---|---|
| Level 1 | gemini-flash-lite | groq-8b |
| Level 2 | groq-70b | gemini-flash |
| Level 3 | gemini-2.5-pro | claude-opus |

---

# 6. Smart Completion Orchestrator

## File

```text
core/utils/orchestrator.py
```

---

# Implementation

```python
def smart_completion(task_type, messages):

    # =====================================================
    # 1. Task Routing Logic
    # =====================================================

    if task_type == "REASONING_HARD":

        selected_model = "gemini/gemini-2.5-pro"

        temperature = 0.1

    elif task_type == "SQL_EXECUTION":

        selected_model = "groq/llama3-70b-8192"

        temperature = 0.0

    else:

        selected_model = "gemini/gemini-2.5-flash-lite"

        temperature = 0.7

    # =====================================================
    # 2. Model Execution via Router
    # =====================================================

    return router.completion(

        model=selected_model,

        messages=messages,

        temperature=temperature
    )
```

---

# 7. Dynamic Task Classifier

## Trước khi gọi LLM

hệ thống sẽ phân loại:

```text
User Query → Task Classifier → Level 1/2/3
```

---

# Ví dụ

```text
"Xin chào" → Level 1
"SELECT revenue FROM contracts" → Level 2
"Forecast revenue next quarter" → Level 3
```

---

# 8. Cost-Aware Routing Engine

## Mục tiêu

# tối ưu chi phí runtime

---

# Cost Awareness Logic

```python
if daily_budget_remaining < threshold:

    downgrade_model_tier()
```

---

# Ví dụ fallback tiết kiệm

```text
Gemini Pro → Flash → Groq
```

---

# 9. Budget Control System

## Phú có thể giới hạn:

```text
Daily AI Spend Limit
```

---

# Example

```python
budget = {

    "daily_limit_usd": 10,

    "current_spend": 6.2
}
```

---

# Khi vượt limit:

```text
force downgrade models
```

---

# 10. High Availability Routing

## Nếu provider fail:

hệ thống tự:

# failover sang provider khác

---

# Example Flow

```text
Gemini Pro FAIL
    ↓
Claude Opus
    ↓
Groq
```

---

# 11. Latency Optimization Strategy

## Mục tiêu

giảm thời gian phản hồi UI Streamlit

---

# Strategy

| Task | Model |
|---|---|
| Fast response | Groq |
| Medium reasoning | Flash |
| Deep reasoning | Pro |

---

# 12. Zero Waste Principle

## Không được phép:

```text
Use expensive model for simple tasks
```

---

# Ví dụ sai

```text
Gemini Pro → "hello"
```

---

# Ví dụ đúng

```text
Flash Lite → "hello"
```

---

# 13. Adaptive Model Scaling

## Hệ thống tự điều chỉnh theo load

---

# Nếu load cao:

```text
downgrade model tier
```

---

# Nếu load thấp:

```text
upgrade model tier
```

---

# 14. Multi-Provider Strategy

## Không phụ thuộc 1 vendor

---

# Providers:

- Google Gemini
- Groq
- OpenRouter
- OpenAI
- Claude

---

# Kết quả:

# Anti single-point-of-failure system

---

# 15. Request Cost Estimation

## Trước khi gọi model:

hệ thống có thể estimate:

```python
estimated_cost = tokens * model_price
```

---

# Nếu vượt budget:

```text
switch to cheaper model
```

---

# 16. Smart Temperature Control

## Theo task type

| Task | Temperature |
|---|---|
| SQL | 0.0 |
| Reasoning | 0.1 |
| Chat | 0.7 |

---

# 17. Observability Integration

## Track theo model

| Metric | Example |
|---|---|
| cost per model | Gemini vs Groq |
| latency per model | ms |
| success rate | % |
| fallback frequency | count |

---

# 18. KPI Dashboard Impact

Sau Phase 19 bạn sẽ thấy:

- model usage distribution
- cost breakdown by task
- fallback frequency
- latency per provider

---

# 19. Best Practices

## Không nên

```python
always_use_gpt4 = True
```

---

## Nên dùng

```python
task_based_model_selection = True
```

---

## Không nên

```python
ignore_cost = True
```

---

## Nên dùng

```python
cost_aware_routing = True
```

---

## Không nên

```python
single_provider_only = True
```

---

## Nên dùng

```python
multi_provider_fallback = True
```

---

# 20. KPI Sau Phase 19

| Metric | Before | After |
|---|---|---|
| Cost Efficiency | Low | High |
| Latency Stability | Medium | High |
| Model Waste | High | Minimal |
| System Reliability | Medium | Very High |
| Budget Control | None | Full |
| Provider Risk | High | Low |

---

# 21. Kết quả cuối cùng

Sau Phase 19, hệ thống đạt:

# Intelligent AI Model Orchestration Layer

---

# Hệ thống giờ có khả năng:

- tự chọn model theo độ khó
- giảm chi phí mạnh
- tối ưu latency realtime
- fallback multi-provider
- budget control theo ngày
- không lãng phí token
- routing thông minh theo task
- scale enterprise-grade AI usage

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- AI Cost Optimization Systems
- Multi-Model Orchestration Platforms
- Enterprise AI Routing Engines
- High-Availability LLM Systems
- Production AI Efficiency Layers