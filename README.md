# 📊 AI MARKETING: TIỀN XỬ LÝ & PHÂN TÍCH TEXT REVIEW - NHÓM 1

Hệ thống Nền Tảng AI Marketing chuyên sâu tiền xử lý văn bản đánh giá (Review Text Mining & NLP) chuẩn UEH.

🔗 **GitHub Repository Public Link**: [https://github.com/hongson15618/AIToolTextMining](https://github.com/hongson15618/AIToolTextMining)

---

## 🌟 Tính Năng Nổi Bật

1. **🧹 Pipeline Tiền Xử Lý 4 Bước Real-Time (Tối Ưu Hiệu Năng Cao)**:
   - **Bước 1**: Dịch đa ngôn ngữ toàn cầu thông minh (Anh, Nga, Pháp, Ý, Hàn, Trung, Nhật... sang Tiếng Việt chuẩn xác), chuyển chữ thường, loại bỏ ký tự thừa & icon.
   - **Bước 2**: Sửa Teencode, chuẩn hóa từ viết tắt, lỗi chính tả & lọc chữ thừa — **giữ trọn vẹn từng câu chữ thật ban đầu của review khách hàng**.
   - **Bước 3**: Văn bản đã Clean (Tách từ ghép tiếng Việt với `underthesea` & Lọc từ dừng thông minh).
   - **Bước 4**: Bóc tách Tokens NLP súc tích phản ánh đúng trọng tâm vấn đề.
   - **Bộ điều khiển**: Tạm dừng (**Pause**) & Tiếp tục (**Resume**) tiến độ bất cứ lúc nào đối với tập dữ liệu lớn (>8,000 dòng).
   - **Lưu bản sao (Snapshots Checkpoint)** vĩnh viễn vào hệ thống, nạp lại và quản lý dễ dàng.

2. **🧠 Bộ Nhớ "Dạy AI" Tự Động (AI Teaching Memory)**:
   - Tự động ghi nhớ các cụm từ mới, teencode riêng biệt và từ khóa do người dùng hướng dẫn.
   - Bảng phân tích AI đóng góp của từng bài học giúp nâng cấp tool liên tục.

3. **🟢🔴🟡 Phân Tích Cảm Xúc AI (Sentiment Analysis)**:
   - Chấm điểm & gán nhãn Tích cực (Xanh), Tiêu cực (Đỏ), Trung tính (Xanh dương).
   - Biểu đồ phân phối, Stripplot & KDE Plot theo độ dài văn bản.

4. **📈 Tần Suất Từ, Top Cụm Từ (Bigrams) & Word Cloud**:
   - Biểu đồ tần suất từ & Top cụm từ thường gặp.
   - Đám mây từ khóa (Word Cloud of Most Frequent Bigrams) trực quan.

5. **🎯 Khám Phá Chủ Đề Tiềm Ẩn (LDA Topic Modeling)** & **Xu Hướng Cảm Xúc Theo Thời Gian**.

6. **📥 Xuất File Excel Đầy Đủ Đa Sheet (Multi-Sheet Excel)**:
   - **Sheet 1 (`Full_Cleaned_NLP`)**: Dữ liệu thô gốc + 4 bước làm sạch + Cảm xúc + Tokens.
   - **Sheet 2 (`Sentiment_Summary`)**: Bảng thống kê tỷ lệ % cảm xúc.
   - **Sheet 3 (`Word_Frequency`)**: Bảng tần suất xuất hiện của các từ khóa.
   - **Sheet 4 (`Top_Bigrams`)**: Bảng xếp hạng các cụm 2 từ phổ biến nhất.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Clone dự án từ GitHub:
```bash
git clone https://github.com/hongson15618/AIToolTextMining.git
cd AIToolTextMining
```

### 2. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### 3. Khởi chạy ứng dụng Web:
```bash
streamlit run app.py
```
Hoặc nhấp đúp vào file `run_tool.bat` trên Windows.

---

## 📁 Cấu Trúc Dự Án
- `app.py`: Giao diện Web Streamlit chuẩn Dark Mode & bộ điều khiển Pipeline.
- `text_cleaner.py`: Module NLP tiếng Việt, dịch thuật đa ngôn ngữ toàn cầu, sửa teencode & lọc từ dừng.
- `sentiment_ai.py`: Phân tích cảm xúc & trực quan hóa biểu đồ Matplotlib / Seaborn.
- `ai_teaching_memory.py`: Bộ nhớ tri thức dạy AI & cơ chế phân tích đóng góp.
- `topic_modeling.py`: Tần suất từ, N-grams, Word Cloud & LDA Topic Modeling.
- `snapshot_manager.py`: Quản lý lưu trữ bản sao tiến độ vĩnh viễn trên máy.
- `teencode_dict.py`: Từ điển chuẩn hóa Teencode tiếng Việt.
- `vietnamese_stopwords.txt`: Danh mục từ dừng tiếng Việt tùy biến.
- `Cleaned_sample_reviews.xlsx`: File Excel mẫu kết quả đã qua tiền xử lý hoàn tất.
- `run_tool.bat`: File chạy 1-click tiện lợi trên Windows.
