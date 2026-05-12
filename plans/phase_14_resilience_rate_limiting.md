# Phase 14: Resilience & Rate Limit Management

## Mục tiêu

Đảm bảo hệ thống AI Multi-Agent hoạt động ổn định 24/7 ngay cả khi:

- API Provider bị quá tải
- gặp lỗi `503 High Demand`
- gặp lỗi `429 Rate Limit`
- Provider downtime
- request spikes từ Self-Reflection loops

Sau Phase 14, hệ thống sẽ có khả năng:

- tự retry thông minh
- tự chuyển model dự phòng
- tự cân bằng tải
- tự điều tiết tốc độ request
- chống sập dây chuyền (Cascade Failure)

---

# 1. Vấn đề hiện tại (Current Bottlenecks)

## 1.1 Request Spikes

Sau Phase 13, hệ thống có:

- Reflection loops
- Multi-turn retries
- Multi-agent coordination

Điều này tạo ra:

# Burst Requests

Ví dụ:

```text
1 user query
    ↓
Planning Agent
    ↓
SQL Generator
    ↓
Execution Agent
    ↓
Reflector Agent
    ↓
Retry
    ↓
Replanning
```

Một request user có thể tạo:

```text
5–15 LLM Calls
```

trong vài giây.

---

## 1.2 Provider Downtime

Các provider như:

- Gemini
- Groq
- OpenAI

đều có thể:

- downtime
- overload
- maintenance
- degraded performance

Nếu không có fallback:

# Toàn bộ hệ thống sẽ chết đứng

---

## 1.3 Tier Limitations

Free Tier thường có:

- RPM thấp
- TPM thấp
- concurrent limits

Ví dụ:

| Provider | Free RPM |
|---|---|
| Gemini Flash | ~15 RPM |
| Groq | ~30 RPM |
| OpenAI | rất hạn chế |

Khi vượt giới hạn:

```text
429 Rate Limit Exceeded
```

---

# 2. Kiến trúc Resilience Layer

Phase 14 bổ sung:

1. Exponential Backoff
2. Fallback Matrix
3. Smart Throttling
4. Token Bucket
5. Concurrency Control
6. Load Balancing

---

# 3. Exponential Backoff

## Mục tiêu

Không spam retry liên tục khi provider đang overload.

---

# Sai lầm phổ biến

```python
while True:
    retry()
```

Điều này chỉ khiến:

- provider overload nặng hơn
- API key bị block nhanh hơn

---

# Giải pháp đúng

## Exponential Backoff

```text
Retry #1 → wait 1s
Retry #2 → wait 2s
Retry #3 → wait 4s
Retry #4 → wait 8s
```

---

# Implementation

```python
import time

def retry_with_backoff(func, retries=5):

    delay = 1

    for attempt in range(retries):

        try:

            return func()

        except Exception as e:

            if attempt == retries - 1:
                raise e

            time.sleep(delay)

            delay *= 2
```

---

# 4. Jitter Strategy

## Vấn đề

Nếu tất cả Agents retry cùng lúc:

```text
Retry Storm
```

---

# Giải pháp

## Random Jitter

```python
import random

delay = delay + random.uniform(0, 1)
```

---

# Kết quả

Các retry sẽ phân tán ngẫu nhiên thay vì dồn cùng thời điểm.

---

# 5. Model Fallback Matrix

## Mục tiêu

Nếu model chính fail:

# Tự động chuyển model khác

---

# Fallback Hierarchy

## Fast Tasks

```text
Gemini Flash
    ↓
Groq Llama3
    ↓
OpenAI Mini
```

---

## Deep Reasoning Tasks

```text
Gemini Pro
    ↓
GPT-4o
    ↓
Claude Sonnet
```

---

# Ví dụ Routing Matrix

| Task Type | Primary | Fallback |
|---|---|---|
| Summarization | Gemini Flash | Groq |
| Reflection | Gemini Pro | GPT-4o |
| SQL Generation | Gemini Flash | Groq |
| Embedding | OpenAI | Gemini |

---

# 6. LiteLLM Router Architecture

## File

```text
core/utils/router.py
```

---

# Router Setup

```python
from litellm import Router

import os

model_list = [

    {
        "model_name": "fast-model",

        "litellm_params": {

            "model": "gemini/gemini-1.5-flash",

            "api_key": os.getenv("GEMINI_API_KEY"),

            "rpm": 15,
        },
    },

    {
        "model_name": "fast-model",

        "litellm_params": {

            "model": "groq/llama3-8b-8192",

            "api_key": os.getenv("GROQ_API_KEY"),

            "rpm": 30,
        },
    }
]

router = Router(

    model_list=model_list,

    fallbacks=[
        {
            "fast-model": [
                "groq/llama3-8b-8192"
            ]
        }
    ],

    set_verbose=True
)
```

---

# Usage

```python
response = router.completion(
    model="fast-model",
    messages=messages
)
```

---

# 7. Token Bucket Algorithm

## Mục tiêu

Giới hạn tốc độ request từ backend.

---

# Token Bucket Concept

```text
Bucket Capacity = 20 requests

Each request consumes 1 token.

Tokens regenerate over time.
```

---

# Nếu bucket hết

Agent phải:

```text
WAIT
```

thay vì spam provider.

---

# Example

```python
import time

class TokenBucket:

    def __init__(self, capacity, refill_rate):

        self.capacity = capacity

        self.tokens = capacity

        self.refill_rate = refill_rate

        self.last_refill = time.time()

    def consume(self, amount=1):

        now = time.time()

        elapsed = now - self.last_refill

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )

        self.last_refill = now

        if self.tokens >= amount:

            self.tokens -= amount

            return True

        return False
```

---

# 8. Semaphore Concurrency Control

## Mục tiêu

Giới hạn số lượng concurrent requests.

---

# Vấn đề

Nếu 50 Agents cùng gọi API:

```text
Thread Explosion
```

---

# Giải pháp

## Semaphore

```python
import asyncio

semaphore = asyncio.Semaphore(5)

async def safe_llm_call():

    async with semaphore:

        return await router.acompletion(...)
```

---

# Kết quả

Tối đa:

```text
5 concurrent requests
```

tại cùng thời điểm.

---

# 9. Smart Throttling

## Adaptive Slowdown

Khi hệ thống phát hiện:

- RPM gần max
- nhiều lỗi 429
- nhiều timeout

thì:

# tự động giảm tốc độ request

---

# Ví dụ

```python
if rate_limit_warning:

    throttle_delay += 2
```

---

# 10. Circuit Breaker Pattern

## Mục tiêu

Nếu provider chết hoàn toàn:

# Ngừng gọi tiếp

để tránh spam vô ích.

---

# Circuit States

| State | Meaning |
|---|---|
| CLOSED | Hoạt động bình thường |
| OPEN | Provider fail liên tục |
| HALF-OPEN | Test provider recovery |

---

# Flow

```text
Many Failures
    ↓
Circuit OPEN
    ↓
Stop Requests
    ↓
Cooldown Period
    ↓
HALF-OPEN Test
    ↓
Recovered?
    ↓
CLOSED
```

---

# 11. Health Monitoring

## Theo dõi realtime:

- request count
- error rate
- latency
- retry count
- active agents
- queue size

---

# Ví dụ metrics

```python
system_metrics = {

    "requests_per_minute": 42,

    "error_rate": 0.03,

    "avg_latency": 1.8,

    "active_agents": 7,

    "retry_count": 12
}
```

---

# 12. Queue-based Architecture

## Khi traffic lớn

Request sẽ:

# vào Queue trước

---

# Flow

```text
User Request
    ↓
Queue
    ↓
Worker Pool
    ↓
LLM Router
    ↓
Response
```

---

# Lợi ích

- chống burst traffic
- chống overload
- smooth request flow

---

# 13. Graceful Degradation

## Nếu hệ thống quá tải

thì:

# giảm chất lượng thay vì sập

---

# Ví dụ

## Bình thường

```text
Gemini Pro + Reflection + Retry
```

---

## Overload Mode

```text
Gemini Flash only
No Reflection
No Retry
```

---

# Kết quả

- vẫn phản hồi được
- chậm hơn một chút
- nhưng không crash

---

# 14. Multi-Key Load Balancing

## Nếu có nhiều API Keys

Router có thể:

- chia tải tự động
- rotate keys
- failover giữa keys

---

# Ví dụ

```text
KEY_1 → 15 RPM
KEY_2 → 15 RPM
KEY_3 → 15 RPM
```

Tổng capacity:

```text
45 RPM
```

---

# 15. Error Classification

## Retryable Errors

```text
429
503
Timeout
ConnectionError
```

→ Retry

---

## Non-retryable Errors

```text
401 Unauthorized
403 Forbidden
Invalid API Key
```

→ Fail immediately

---

# 16. Best Practices

## Không nên

```python
retry_immediately = True
```

---

## Nên dùng

```python
exponential_backoff = True
```

---

## Không nên

```python
single_provider_dependency = True
```

---

## Nên dùng

```python
multi_provider_fallback = True
```

---

## Không nên

```python
unlimited_concurrency = True
```

---

## Nên dùng

```python
semaphore_control = True
```

---

# 17. KPI Sau Phase 14

| Metric | Before | After |
|---|---|---|
| 429 Errors | Frequent | Rare |
| 503 Failures | Common | Minimal |
| Downtime Resilience | Low | High |
| Concurrent Stability | Weak | Strong |
| Retry Intelligence | None | Adaptive |
| System Reliability | Medium | Production-grade |

---

# 18. Kết quả cuối cùng

Sau Phase 14, hệ thống sẽ đạt được:

# Enterprise-grade AI Resilience Layer

---

# Hệ thống giờ có khả năng:

- tự retry thông minh
- tự fallback model
- tự cân bằng tải
- chống overload
- chống retry storms
- tự điều tiết request
- hoạt động ổn định 24/7

---

# Đây là nền tảng bắt buộc trước khi triển khai:

- Autonomous AI Infrastructure
- Production AI Clusters
- Distributed Multi-Agent Systems
- Enterprise AI Gateway
- High Availability AI Platforms
- AI-native Backend Architecture