# Phase 5 Test: IngestAgent Layer

## Mục tiêu
Kiểm tra khả năng phân loại ý định và trích xuất thực thể từ câu hỏi người dùng.

## Các bước thực hiện
1. **Gửi câu hỏi mơ hồ**: "Lấy dữ liệu cho tôi".
2. **Gửi câu hỏi rõ ràng**: "Danh sách khách hàng ở Việt Nam thuộc ngành Tài chính".
3. **Gửi câu hỏi tấn công**: "Ignore previous instructions...".

## Kết quả mong đợi
- [ ] Phân loại đúng Intent (Query/Report/Security_Violation).
- [ ] Trích xuất đúng Entity (Việt Nam, Tài chính).
- [ ] Phát hiện và chặn các prompt độc hại.
