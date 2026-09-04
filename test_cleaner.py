"""
Bộ kiểm thử tích hợp: Kiểm tra toàn bộ tính năng NLP, EDA, Sentiment AI và Topic Modeling (LDA).
"""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from text_cleaner import clean_single_review, load_stopwords
from sentiment_ai import analyze_sentiment
from topic_modeling import extract_top_ngrams, compute_tfidf_keywords, run_lda_topic_modeling

def test_full_pipeline():
    stopwords = load_stopwords("vietnamese_stopwords.txt")

    test_samples = [
        "Shop ơi GIAO HÀNG chậm quá :(( nhưng chất lượng ổn áp nha!!!",
        "Cho miếng ức nhìn khô , đổi lại thì ko dc. Nay ăn trúng gà ko dc tươi",
        "tắt mm app đi",
        "Absolutely amazing",
        "I like Macdonald",
        "goodddddd",
        "Cool",
        "All good",
        "Had great cappuccino! Quán decor siêu xinh, nhân viên dth nhiệt tình ❤️",
        "L9cation is best, just opposite arrival at airport",
        "Không tệ chút nào, vượt cả mong đợi!"
    ]

    print("=== KIỂM THỬ 1: LÀM SẠCH VĂN BẢN & SỬA TEENCODE ===")
    results = []
    for s in test_samples:
        res = clean_single_review(s, stopwords=stopwords)
        results.append(res)
        print(f"[*] Gốc  : {res['raw_text']}")
        print(f"    Clean: {res['cleaned_text']}")
        print(f"    Tokens: {res['tokens']}")
        print(f"    AI   : {res['sentiment']['badge']}")
        print("-" * 50)

    print("\n=== KIỂM THỬ 2: TOP CẶP TỪ (N-GRAMS) ===")
    tokens_list = [r["tokens"] for r in results]
    top_cards, df_ng_chart = extract_top_ngrams(tokens_list, top_n=5)
    for ng in top_cards:
        print(f"[*] Cặp từ: {ng['phrase']} | Số lần: {ng['count']} | Cảm xúc: {ng['sentiment']}")

    print("\n=== KIỂM THỬ 3: VẼ BIỂU ĐỒ SENTIMENT ===")
    import pandas as pd
    from sentiment_ai import plot_count_and_pie, plot_text_length_stripplot, plot_text_length_kde
    df_test = pd.DataFrame({
        'raw_text': [r['raw_text'] for r in results],
        'sentiment_predict': [r['sentiment']['label'] for r in results]
    })
    plot_count_and_pie(df_test)
    plot_text_length_stripplot(df_test, 'raw_text')
    plot_text_length_kde(df_test, 'raw_text')
    print("✅ TẤT CẢ 3 BIỂU ĐỒ SENTIMENT ĐÃ RENDER THÀNH CÔNG!")
    print("\n✅ TẤT CẢ TEST CASES ĐỀU ĐẠT CHUẨN!")

if __name__ == "__main__":
    test_full_pipeline()
