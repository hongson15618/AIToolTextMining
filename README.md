# 📊 AI MARKETING: TIỀN XỬ LÝ & PHÂN TÍCH TEXT REVIEW - NHÓM 1

Hệ thống Web App AI Marketing chuyên sâu tiền xử lý văn bản đánh giá (Review Text Mining & NLP) chuẩn UEH.

---

## 🌟 Tính Năng Nổi Bật

1. **🧹 Pipeline Tiền Xử Lý Real-Time (Tối Ưu Hiệu Năng Cao)**:
   - Dịch đa ngôn ngữ thông minh (Nga, Pháp, Ý, Hàn, Trung, Nhật, Anh... sang Tiếng Việt).
   - Lọc bỏ đánh giá vô nghĩa, sai chính tả không thể dịch.
   - Sửa Teencode & Lỗi chính tả tiếng Việt.
   - Tách từ ghép chuyên sâu với thư viện NLP `underthesea`.
   - Lọc từ dừng (Stopwords) thông minh kèm tính năng tự động lưu.
   - **Tạm dừng (Pause)** & **Tiếp tục (Resume)** tiến độ bất cứ lúc nào đối với tập dữ liệu lớn (>8,000 dòng).
   - **Lưu bản sao (Snapshots Checkpoint)** vĩnh viễn vào hệ thống, quản lý nạp lại và xóa dễ dàng.

2. **🟢🔴🟡 Phân Tích Cảm Xúc AI (Sentiment Analysis)**:
   - Chấm điểm & gán nhãn Tích cực (Xanh), Tiêu cực (Đỏ), Trung tính (Xanh dương).
   - Bảng phân phối và trực quan hóa Stripplot & KDE Plot theo độ dài văn bản.

3. **📋 Bảng So Sánh Chi Tiết (Visual Diff)**:
   - Hiển thị trực quan điểm khác biệt giữa văn bản thô gốc và văn bản sau khi làm sạch.
   - Hỗ trợ phân trang 1,000 dòng/trang và kéo giãn chiều cao bảng tùy ý.

4. **📈 Tần Suất Từ, Top Cụm Từ (Bigrams) & Word Cloud**:
   - Biểu đồ tần suất từ & Top cụm từ thường gặp.
   - Đám mây từ khóa (Word Cloud) trực quan.

5. **🎯 Khám Phá Chủ Đề Tiềm Ẩn (LDA Topic Modeling)** & **Xu Hướng Cảm Xúc Theo Thời Gian**.

6. **📥 Xuất File Excel Đầy Đủ**:
   - Tải file Excel đa sheet tích hợp trọn bộ kết quả phân tích.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng Web:
```bash
streamlit run app.py
```
Hoặc nhấp đúp vào file `run_tool.bat` trên Windows.

---

## 📁 Cấu Trúc Dự Án
- `app.py`: Giao diện Web Streamlit chuẩn Dark Mode & bộ điều khiển Pipeline.
- `text_cleaner.py`: Module NLP tiếng Việt, dịch thuật đa ngôn ngữ, sửa teencode & lọc từ dừng.
- `sentiment_ai.py`: Phân tích cảm xúc & trực quan hóa biểu đồ Matplotlib / Seaborn.
- `topic_modeling.py`: Tần suất từ, N-grams, Word Cloud & LDA Topic Modeling.
- `snapshot_manager.py`: Quản lý lưu trữ bản sao tiến độ vĩnh viễn trên máy.
- `teencode_dict.py`: Từ điển chuẩn hóa Teencode tiếng Việt.
- `vietnamese_stopwords.txt`: Danh mục từ dừng tiếng Việt tùy biến.
- `run_tool.bat`: File chạy 1-click tiện lợi trên Windows.
