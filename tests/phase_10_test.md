# Phase 10 Test: Context Monitoring & Logic Validation

## Mục tiêu
Xác nhận hệ thống có khả năng hiểu ngữ cảnh hội thoại, giải quyết đại từ tham chiếu và kiểm soát tính nhất quán của logic/dữ liệu.

## Các kịch bản kiểm thử

### 1. Kiểm thử Tham chiếu (Coreference Resolution)
- **Bước 1**: Hỏi "Account HBL có bao nhiêu hợp đồng?"
- **Bước 2**: Hỏi tiếp "Hợp đồng của nó tháng 5 thế nào?"
- **Kết quả mong đợi**: `ContextMonitor` phải giải mã được "nó" là "Account HBL" và sinh ra SQL đúng cho HBL.

### 2. Kiểm thử Logic (Consistency Check)
- **Kịch bản**: Reasoning dự kiến có 10 dòng kết quả, nhưng Execution trả về 0 dòng.
- **Kết quả mong đợi**: Hệ thống cảnh báo "Logic inconsistency detected" hoặc tự động kiểm tra lại schema.

### 3. Kiểm thử Hallucination Guard
- **Kịch bản**: Yêu cầu AI lấy dữ liệu từ một trường không tồn tại (vd: `SELECT salary FROM hbl_account`).
- **Kết quả mong đợi**: Hệ thống từ chối thực thi và thông báo lỗi schema thay vì bịa ra dữ liệu.

### 4. Kiểm thử Feedback Loop
- **Bước 1**: Nhấn nút 👎 trên UI.
- **Kết quả mong đợi**: Dữ liệu này không được đưa vào bộ nhớ của `LearningAgent`.

## Kết quả kiểm thử
- [ ] Coreference Resolution: PASSED/FAILED
- [ ] Logic Consistency: PASSED/FAILED
- [ ] Hallucination Guard: PASSED/FAILED
- [ ] Feedback System: PASSED/FAILED
- [ ] Checkpointing: PASSED/FAILED
