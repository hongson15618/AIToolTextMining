import sys
import os
import pandas as pd
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_cleaner
from topic_modeling import compute_word_frequency, extract_top_ngrams, run_lda_topic_modeling

input_file = os.path.join(os.path.dirname(__file__), "sample_reviews.xlsx")
if os.path.exists(input_file):
    df_raw = pd.read_excel(input_file)
else:
    from generate_sample_excel import sample_data
    df_raw = pd.DataFrame(sample_data)

stopwords_path = os.path.join(os.path.dirname(__file__), "vietnamese_stopwords.txt")
stopwords = text_cleaner.load_stopwords(stopwords_path)

col_name = "Bình Luận Đánh Giá" if "Bình Luận Đánh Giá" in df_raw.columns else df_raw.columns[-1]

results = []
for idx, row in df_raw.iterrows():
    raw_text = row[col_name]
    res = text_cleaner.clean_single_review(
        raw_text=raw_text,
        stopwords=stopwords,
        translate_to_vi=True,
        fix_teencode=True,
        use_lowercase=True,
        remove_icons=True,
        word_segmentation=True,
        remove_sw=True,
        nlp_engine="underthesea" if text_cleaner.HAS_UNDERTHESEA else "regex"
    )
    results.append(res)

total_rows = len(results)
valid_results = [r for r in results if not r.get("is_meaningless", False)]

# Sheet 1: Full Cleaned Data
df_full = df_raw.copy()
df_full["[1. DỊCH TIẾNG VIỆT, LOWERCASE & BỎ KÝ TỰ THỪA]"] = [r["step1_translated_clean"] if not r.get("is_meaningless", False) else "LOẠI" for r in results]
df_full["[2. SỬA TEENCODE & LỖI - AI TÓM TẮT Ý CHÍNH]"] = [r["step2_teencode"] if not r.get("is_meaningless", False) else "LOẠI" for r in results]
df_full["[3. VĂN BẢN ĐÃ CLEAN]"] = [r["cleaned_text"] if not r.get("is_meaningless", False) else "LOẠI" for r in results]
df_full["[4. TOKENS NLP]"] = [", ".join(r["tokens"]) if not r.get("is_meaningless", False) else "LOẠI" for r in results]
df_full["[CẢM XÚC AI]"] = [r["sentiment"]["label"] for r in results]
df_full["[ĐỘ TIN CẬY]"] = [f"{r['sentiment']['confidence_percent']}%" for r in results]

# Sheet 2: Sentiment Summary
tot = max(1, len(valid_results))
pos_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tích cực")
neg_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tiêu cực")
neu_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Trung tính")

df_sent = pd.DataFrame([
    {"Loại Cảm Xúc": "🟢 Tích cực (Positive)", "Số Lượng Bình Luận": pos_cnt, "Tỷ Lệ %": f"{round(pos_cnt/tot*100, 1)}%", "Đánh Giá": "Khách hàng hài lòng, khen ngợi chất lượng/dịch vụ"},
    {"Loại Cảm Xúc": "🔴 Tiêu cực (Negative)", "Số Lượng Bình Luận": neg_cnt, "Tỷ Lệ %": f"{round(neg_cnt/tot*100, 1)}%", "Đánh Giá": "Khách phàn nàn về giao hàng chậm, hàng lỗi, thái độ"},
    {"Loại Cảm Xúc": "🔵 Trung tính (Neutral)", "Số Lượng Bình Luận": neu_cnt, "Tỷ Lệ %": f"{round(neu_cnt/tot*100, 1)}%", "Đánh Giá": "Bình luận hỏi thông tin, đặt size, trung lập"}
])

# Sheet 3: Word Frequency
tokens_all = [r["tokens"] for r in valid_results if r["tokens"]]
df_wf = compute_word_frequency(tokens_all, top_n=20)

# Sheet 4: Top Bigrams
_, df_bg = extract_top_ngrams(tokens_all, top_n=20)

output_excel = os.path.join(os.path.dirname(__file__), "Cleaned_sample_reviews.xlsx")
with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
    df_full.to_excel(writer, index=False, sheet_name="Full_Cleaned_NLP")
    df_sent.to_excel(writer, index=False, sheet_name="Sentiment_Summary")
    df_wf.to_excel(writer, index=False, sheet_name="Word_Frequency")
    df_bg.to_excel(writer, index=False, sheet_name="Top_Bigrams")

print(f"[*] Da xuat file Excel thanh cong tai: {output_excel}")
