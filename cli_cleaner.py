"""
CLI Tool: Làm sạch dữ liệu văn bản Excel từ Command Line
Sử dụng:
    python cli_cleaner.py input.xlsx -o output.xlsx --column "Bình luận"
"""

import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import os
import pandas as pd
from text_cleaner import clean_single_review, load_stopwords

def main():
    parser = argparse.ArgumentParser(description="Tool lọc và làm sạch dữ liệu review Excel tiếng Việt (NLP)")
    parser.add_argument("input_file", help="Đường dẫn đến file Excel (.xlsx, .xls) hoặc CSV cần xử lý")
    parser.add_argument("-o", "--output", help="Đường dẫn lưu file Excel kết quả (mặc định: Cleaned_<tên_file>.xlsx)")
    parser.add_argument("-c", "--column", help="Tên cột chứa bình luận cần làm sạch (nếu bỏ trống sẽ tự động nhận diện)")
    parser.add_argument("--no-translate", action="store_true", help="Không dịch tiếng nước ngoài sang tiếng Việt")
    parser.add_argument("--no-icons", action="store_true", help="Không xóa icons/emojis")
    parser.add_argument("--no-stopwords", action="store_true", help="Không lọc stopwords")
    parser.add_argument("--stopwords-file", help="Đường dẫn file stopwords tùy chỉnh", default="vietnamese_stopwords.txt")
    
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"[-] Loi: Khong tim thay file {args.input_file}")
        sys.exit(1)

    print(f"[*] Dang doc file: {args.input_file}...")
    if args.input_file.endswith(".csv"):
        df = pd.read_csv(args.input_file)
    else:
        df = pd.read_excel(args.input_file)

    target_col = args.column
    if not target_col:
        for col in df.columns:
            c_low = str(col).lower()
            if any(k in c_low for k in ["bình luận", "review", "comment", "đánh giá", "nhận xét", "nội dung", "text"]):
                target_col = col
                break
        if not target_col:
            target_col = df.columns[0]
            print(f"[*] Tu dong chon cot: '{target_col}'")

    print(f"[*] Cot duoc chon de lam sach: '{target_col}' (Tong {len(df)} dong)")

    stopwords_path = args.stopwords_file
    stopwords = load_stopwords(stopwords_path)

    results = []
    print("[*] Dang tien hanh lam sach...")
    for idx, row in df.iterrows():
        val = row[target_col]
        res = clean_single_review(
            raw_text=val,
            stopwords=stopwords,
            translate_to_vi=not args.no_translate,
            use_lowercase=True,
            remove_icons=not args.no_icons,
            word_segmentation=True,
            remove_sw=not args.no_stopwords
        )
        results.append(res)

    df_result = df.copy()
    df_result[f"[ĐÃ CLEAN] {target_col}"] = [r["cleaned_text"] for r in results]
    df_result[f"[TOKENS] {target_col}"] = [", ".join(r["tokens"]) for r in results]
    df_result["[ĐÃ BỎ] Icon & Emoji"] = [", ".join(r["removed_icons"]) if r["removed_icons"] else "-" for r in results]
    df_result["[ĐÃ BỎ] Từ dừng"] = [", ".join(r["removed_stopwords"]) if r["removed_stopwords"] else "-" for r in results]
    df_result["% Rút gọn"] = [f"{r['reduction_percent']}%" for r in results]

    output_path = args.output
    if not output_path:
        base_name = os.path.basename(args.input_file)
        dir_name = os.path.dirname(args.input_file)
        output_path = os.path.join(dir_name, f"Cleaned_{base_name}")
        if not output_path.endswith(".xlsx"):
            output_path = os.path.splitext(output_path)[0] + ".xlsx"

    df_result.to_excel(output_path, index=False)
    print(f"[*] Da luu ket qua thanh cong tai: {output_path}")

if __name__ == "__main__":
    main()
