# User Acceptance Testing (UAT) & Sign-Off Plan

Tài liệu này xác định các tiêu chí để hai bên Kỹ thuật (Engineering) và Vận hành/Kinh doanh (Ops/Business) nghiệm thu và đóng dự án Agentic AI.

## 1. Môi trường UAT
- Hệ thống phải được triển khai lên môi trường (Staging/UAT) có cấu hình tương tự như Production.
- Sử dụng mô hình LLM chuẩn (ví dụ: GPT-4o hoặc Gemini-1.5-Pro).

## 2. Các Kịch Bản Kiểm Thử (Test Scenarios)
Người dùng UAT cần thực hiện các bài test thực tế:
- [ ] **Kịch bản 1: Truy vấn đơn giản (Simple Query)**
  - Câu hỏi: "Tổng số khách hàng trong tài khoản là bao nhiêu?"
  - Yêu cầu: Trả về chính xác số liệu, không sinh SQL nguy hiểm.
- [ ] **Kịch bản 2: Truy vấn phức tạp (Complex Query)**
  - Câu hỏi: "Top 5 khách hàng doanh thu cao nhất năm nay là ai?"
  - Yêu cầu: Agent phải tự tìm bảng Accounts, Orders, kết nối chúng và xuất kết quả.
- [ ] **Kịch bản 3: Đa ngôn ngữ (Language Sync)**
  - Câu hỏi: "Give me the list of accounts" và "Cho tôi danh sách tài khoản"
  - Yêu cầu: Câu đầu tiên trả về tiếng Anh, câu thứ hai trả về tiếng Việt.
- [ ] **Kịch bản 4: Phân tách người dùng (Tenant Isolation/RLS)**
  - Yêu cầu: Người dùng đăng nhập với Account A không thể xem được dữ liệu hóa đơn của Account B.

## 3. Checklist An Toàn Bàn Giao
- [ ] Source code hoàn chỉnh trên nhánh `main`.
- [ ] Đã hoàn thiện toàn bộ file tài liệu `ARCHITECTURE.md`, `OPERATIONS.md`.
- [ ] Đã thiết lập cảnh báo ngân sách (Cost Guardrails) thành công.
- [ ] Không có password/secret lộ trong file `.env` commit lên source control.

## 4. Ký Nhận Bàn Giao (Sign-Off)
Khi các bên kiểm tra checklist trên đã pass 100%, tiến hành ký xác nhận:

- **Đại diện Engineering (Dev Lead)**: ___________________ Ngày: ________
- **Đại diện Vận Hành (Ops/DevOps)**: __________________ Ngày: ________
- **Đại diện Nghiệp vụ (Product Owner)**: _______________ Ngày: ________

**KẾT LUẬN**: Hệ thống Agentic AI (v2) đủ điều kiện chạy chính thức (Go-Live).
