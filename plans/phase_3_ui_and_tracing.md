# Phase 3 — MCP, LLM Orchestration & Secure Tooling
## Agentic CRM System

---

# 1. Tổng quan Phase 3

Phase 3 là giai đoạn biến hệ thống từ “có thể chat và truy vấn” thành một **nền tảng Agent có kiểm soát, có công cụ chuẩn hóa, có routing LLM thông minh và có lớp bảo mật rõ ràng**.

Mục tiêu của phase này không chỉ là “kết nối được MCP” hay “gọi được nhiều model”, mà là xây dựng một kiến trúc đủ sạch để:

- code dễ quản lý
- tool dễ mở rộng
- LLM dễ thay thế
- truy vấn database an toàn
- secrets không bị lộ
- mọi hành động đều audit được

Nói ngắn gọn, Phase 3 là **lớp thần kinh trung tâm của hệ thống Agentic CRM**.

---

# 2. Objectives (Mục tiêu)

## 2.1 Chuẩn hóa cách Agent làm việc với Database

Triển khai **Postgres-native MCP Server** để Agent không gọi SQL rời rạc theo kiểu thủ công, mà đi qua một lớp công cụ chuẩn hóa, có kiểm soát và có thể audit.

Mục tiêu:

- tách logic AI khỏi logic truy vấn
- giảm code lặp
- chặn query nguy hiểm
- dễ mở rộng công cụ sau này
- dễ thay đổi schema mà không phá toàn hệ thống

---

## 2.2 Xây dựng LLM Orchestration Layer

Thiết lập **LiteLLM Router** để điều phối model theo từng loại nhiệm vụ.

Mục tiêu:

- tối ưu chi phí
- tăng độ ổn định
- có fallback khi model chính lỗi
- chọn model phù hợp theo task tier
- tránh phụ thuộc vào một nhà cung cấp duy nhất

---

## 2.3 Xây dựng Semantic Schema Retrieval

Thay vì nạp toàn bộ schema vào prompt, hệ thống sẽ chỉ lấy đúng phần schema liên quan đến câu hỏi.

Mục tiêu:

- cắt giảm context
- giảm nhiễu logic
- giảm token cost
- tăng accuracy khi sinh SQL
- giúp LLM tập trung vào đúng bảng, đúng quan hệ, đúng semantic view

---

## 2.4 Thiết lập Security & Execution Policy

Mọi tool call, query execution và model routing phải tuân theo nguyên tắc:

- deny by default
- allow by explicit definition
- restricted tool access
- database role giới hạn quyền
- audit đầy đủ
- secrets quản lý bằng `.env` và cơ chế config tách biệt

---

# 3. Nguyên tắc kiến trúc

Phase 3 cần được thiết kế theo 5 nguyên tắc sau:

## 3.1 Single Responsibility

Mỗi lớp chỉ làm một việc:

- MCP server: expose tool chuẩn hóa
- router LLM: chọn model
- schema retriever: lấy context cần thiết
- executor: chạy query an toàn
- audit logger: ghi lịch sử thực thi

---

## 3.2 Deny by Default

Không có tool nào được Agent sử dụng nếu chưa được khai báo rõ ràng.

Không có SQL nào được thực thi nếu chưa qua kiểm duyệt.

Không có model nào được gọi nếu chưa có policy routing.

---

## 3.3 Config-driven

Toàn bộ hành vi quan trọng phải điều khiển bằng config, không hardcode:

- model name
- fallback rules
- timeouts
- max tokens
- allowed tools
- db role
- audit schema
- env key names

---

## 3.4 Least Privilege

Agent chỉ được dùng role DB ở mức tối thiểu:

- chỉ SELECT trên schema nghiệp vụ
- không có quyền DDL
- không có quyền DML
- không được truy cập schema hệ thống nếu không cần thiết

---

## 3.5 Observable by Design

Mọi thao tác đều phải để lại dấu vết:

- tool name
- input summary
- output summary
- SQL sinh ra
- model được dùng
- fallback đã xảy ra hay chưa
- thời gian thực thi
- lỗi nếu có

---

# 4. Kiến trúc tổng thể

```text
User Question
    ↓
Phase 2 UI / API
    ↓
Agent Planner
    ↓
LLM Router (LiteLLM)
    ↓
Semantic Schema Retriever
    ↓
MCP Server
    ↓
Safe Executor / Tool Layer
    ↓
PostgreSQL (agentic_ai)
    ↓
Audit Logs + Trace + Result