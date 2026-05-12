# Phase 24: Neural Network Integration (Hybrid AI)

## 🎯 Mục tiêu
Giảm sự phụ thuộc vào các API LLM đắt đỏ và tăng tốc độ xử lý bằng cách tích hợp các mô hình học sâu chuyên biệt (Deep Learning) chạy cục bộ.

## 🛠️ Các thay đổi chính

### 1. Local Intent Classifier
- Triển khai một mô hình phân loại ý định (Intent Classifier) sử dụng Scikit-learn hoặc PyTorch chạy trực tiếp trên server.
- Thay thế bước `Ingest Agent` bằng mô hình này để đạt tốc độ xử lý gần như tức thì (< 50ms) cho các câu hỏi phổ thông.

### 2. Custom Business Embeddings
- Tinh chỉnh (Fine-tuning) mô hình Embedding (như BGE-M3 hoặc các model nhỏ của HuggingFace) để hiểu sâu các mã sản phẩm và thuật ngữ CRM nội bộ.
- Cải thiện độ chính xác của tìm kiếm Vector (Semantic Search) cho dữ liệu đặc thù của doanh nghiệp.

### 3. Neural Context Ranking
- Sử dụng mô hình Cross-Encoder để xếp hạng lại (Re-rank) kết quả tìm kiếm từ tri thức, đảm bảo thông tin đưa vào LLM là chính xác nhất.

## 📈 Kết quả mong đợi
- Giảm 90% số lượng token tiêu thụ cho bước phân loại ý định.
- Tăng tính bảo mật cho các tác vụ phân tích cảm xúc khách hàng (xử lý nội bộ).
