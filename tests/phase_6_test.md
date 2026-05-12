# Phase 6 Test: ReasoningAgent Layer

## Mục tiêu
Kiểm tra khả năng suy luận CoT (Chain-of-Thought) và lập kế hoạch logic.

## Các bước thực hiện
1. **Gửi câu hỏi phức tạp**: "Khách hàng nào có doanh thu cao nhất tại Việt Nam năm 2023?".
2. **Kiểm tra Trace Log**: Xem phần Reasoning có giải thích các bước: "Tìm khách hàng ở VN" -> "Join bảng doanh thu" -> "Sắp xếp và lấy Top 1" hay không.

## Kết quả mong đợi
- [ ] AI hiển thị các bước suy luận logic.
- [ ] Xác định đúng các bảng cần thiết để JOIN.
