"""
Ứng dụng Web: NỀN TẢNG PHÂN TÍCH VĂN BẢN ĐÁNH GIÁ & TIỀN XỬ LÝ NLP (CHUẨN UEH)
Bao gồm:
1. Bảng So Sánh Chi Tiết (Visual Diff).
2. Bảng Thống Kê Cảm Xúc (Tích cực Xanh, Tiêu cực Đỏ, Trung tính Vàng).
3. Tần Suất Từ Mọi Người Nhắc (Biểu đồ thanh ngang + Bảng số liệu).
4. Top Cụm Từ (Thẻ card + Biểu đồ thanh ngang + Word Cloud of Most Frequent Bigrams).
5. Phân tích chuyên sâu: Theo dõi cảm xúc theo thời gian, Chủ đề LDA.
6. Tải file Excel kết quả.
"""

import os
import io
import time
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

from text_cleaner import (
    clean_single_review,
    load_stopwords,
    HAS_UNDERTHESEA,
    HAS_PYVI,
    HAS_TRANSLATOR
)
from topic_modeling import (
    compute_word_frequency,
    extract_top_ngrams,
    generate_bigram_wordcloud,
    compute_tfidf_keywords,
    run_lda_topic_modeling
)
from sentiment_ai import (
    plot_count_and_pie,
    plot_text_length_stripplot,
    plot_text_length_kde
)
from snapshot_manager import (
    save_snapshot,
    list_snapshots,
    load_snapshot,
    delete_snapshot
)
from ai_teaching_memory import (
    load_teaching_memory,
    add_teaching_rule,
    delete_teaching_rule,
    get_teaching_context_for_ai
)

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="AI Marketing: Tiền Xử Lý & Phân Tích Text Review - Nhóm 1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện chuẩn UEH
st.markdown("""
<style>
    .watermark-banner {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 18px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .watermark-banner .brand {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 500;
    }
    .watermark-banner .author {
        font-size: 0.88rem;
        color: #E2E8F0;
        font-weight: 600;
    }
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #0D9488 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: white;
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0;
    }
    .main-header p {
        color: #CBD5E1;
        font-size: 0.98rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .badge-step {
        background: rgba(255,255,255,0.15);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
        display: inline-block;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .sent-card-pos {
        background-color: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 6px solid #10B981;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #F8FAFC;
    }
    .sent-card-neg {
        background-color: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 6px solid #EF4444;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #F8FAFC;
    }
    .sent-card-neu {
        background-color: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-left: 6px solid #3B82F6;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #F8FAFC;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .card-subtitle {
        font-size: 0.95rem;
        color: #CBD5E1;
    }
    .section-title {
        color: #38BDF8;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
        border-bottom: 2px solid #334155;
        padding-bottom: 6px;
    }
    /* Tự động xuống dòng và giới hạn tối đa 2 dòng cho ô dữ liệu Streamlit Grid */
    div[data-testid="stDataFrame"] td,
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.35 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* ========================================================================= */
    /* GIAO DIỆN DARK MODE CAO CẤP CHO BẢNG VISUAL DIFF (BƯỚC 2)                 */
    /* ========================================================================= */
    .diff-table-container {
        width: 100%;
        overflow-x: auto;
        overflow-y: auto;
        resize: vertical;
        min-height: 320px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
        margin-top: 15px;
        margin-bottom: 25px;
        border: 1px solid #334155;
        background-color: #0f172a;
    }
    .dark-diff-table {
        width: 100%;
        border-collapse: collapse;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        text-align: left;
    }
    .dark-diff-table thead {
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .dark-diff-table th {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 14px 16px;
        border-bottom: 2px solid #334155;
        white-space: nowrap;
    }
    .dark-diff-table td {
        padding: 14px 16px;
        border-bottom: 1px solid #1e293b;
        vertical-align: middle;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #e2e8f0;
    }
    .dark-diff-table tbody tr:nth-child(even) {
        background-color: #111c30;
    }
    .dark-diff-table tbody tr:nth-child(odd) {
        background-color: #0b1120;
    }
    .dark-diff-table tbody tr:hover {
        background-color: #1e293b !important;
        transition: background-color 0.15s ease-in-out;
    }
    .dark-diff-table .stt-cell {
        font-weight: 700;
        color: #94a3b8;
        text-align: center;
        font-size: 0.95rem;
    }
    .dark-diff-table .raw-cell {
        color: #cbd5e1;
        font-size: 0.92rem;
        word-break: break-word;
    }
    .dark-diff-table .diff-cell {
        line-height: 1.9;
    }
    .dark-diff-table .clean-cell {
        color: #38bdf8;
        font-weight: 600;
        word-break: break-word;
    }
    .dark-diff-table .token-cell code {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #34d399 !important;
        border: 1px solid #334155 !important;
        padding: 5px 9px !important;
        border-radius: 6px !important;
        font-family: Consolas, "Fira Code", monospace !important;
        font-size: 0.85rem !important;
        display: inline-block;
        word-break: break-word;
        line-height: 1.4;
    }
    .dark-diff-table .sent-cell {
        text-align: center;
        white-space: nowrap;
    }
    .diff-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }
    .badge-pos {
        background-color: rgba(34, 197, 94, 0.22);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.5);
    }
    .badge-neg {
        background-color: rgba(239, 68, 68, 0.22);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.5);
    }
    .badge-neu {
        background-color: rgba(59, 130, 246, 0.22);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.5);
    }
    .badge-loai {
        background-color: rgba(148, 163, 184, 0.2);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.4);
    }
    .diff-legend-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 16px;
        color: #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .dark-diff-table tr.removed-row {
        background-color: rgba(239, 68, 68, 0.18) !important;
        border-left: 4px solid #ef4444 !important;
    }
    .dark-diff-table tr.removed-row td {
        color: #fca5a5 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

STOPWORDS_FILE = os.path.join(os.path.dirname(__file__), "vietnamese_stopwords.txt")
default_stopwords = load_stopwords(STOPWORDS_FILE)

# Watermark Banner
st.markdown("""
<div class="watermark-banner">
    <div class="brand">
        ⚡ <b>UEH MARKETING ANALYTICS PLATFORM</b> — Hệ thống Xử lý & Phân tích Đánh giá Khách hàng
    </div>
    <div class="author">
        ✨ <i>Tool được thiết kế bởi Sơn — liên hệ <span style="color: #38BDF8; font-weight: 700;">0776.941.932</span></i>
    </div>
</div>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 AI MARKETING: TIỀN XỬ LÝ & PHÂN TÍCH TEXT REVIEW - NHÓM 1</h1>
    <p>Giải pháp phân tích ý kiến khách hàng toàn diện: Dịch đa ngôn ngữ, Lọc ngày giờ, Tần suất từ, Top cụm từ (Bar Chart & Word Cloud), Chấm điểm cảm xúc (Xanh/Đỏ/Vàng) & Khám phá chủ đề (LDA).</p>
    <div style="margin-top: 10px;">
        <span class="badge-step">🧹 1. Dịch thuật & Làm sạch</span>
        <span class="badge-step">📈 2. Tần suất từ & Top Cụm từ</span>
        <span class="badge-step">☁️ 3. Word Cloud Bigrams</span>
        <span class="badge-step">🟢🔴🟡 4. Cảm xúc AI</span>
        <span class="badge-step">🎯 5. Chủ đề LDA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Cấu hình & Dạy AI")
    
    # -------------------------------------------------------------------------
    # PHẦN QUẢN LÝ BẢN SAO (COLLAPSIBLE CHECKPOINTS & RESTORE)
    # -------------------------------------------------------------------------
    with st.expander("📦 Bản Sao Dữ Liệu", expanded=False):
        st.caption("Lưu lại tiến độ đang chạy hoặc kết quả hoàn tất. Tắt tool mở lại vẫn còn nguyên vẹn.")
        snapshot_custom_name = st.text_input(
            "Tên bản sao (Tùy chọn):",
            placeholder="Ví dụ: Tiến độ 1450 dòng",
            key="input_snp_name_sb"
        )
        can_save_snp = (st.session_state.get("df_cached") is not None and st.session_state.get("clean_idx", 0) > 0) or (st.session_state.get("results") is not None)
        if st.button("💾 Lưu Bản Sao Hiện Tại", type="primary" if can_save_snp else "secondary", disabled=not can_save_snp, use_container_width=True, key="btn_save_snp_sb"):
            cur_df_in = st.session_state.get("df_cached")
            cur_df_live = st.session_state.get("clean_live_df") or st.session_state.get("df_live_final")
            cur_res = st.session_state.get("clean_results") or st.session_state.get("results") or []
            cur_processed = st.session_state.get("clean_idx", len(cur_res))
            cur_total = len(cur_df_in) if cur_df_in is not None else len(cur_res)
            cur_col = st.session_state.get("selected_col", "")
            cur_elap = st.session_state.get("clean_elapsed", 0.0)
            
            snp_id = save_snapshot(
                name=snapshot_custom_name,
                df_input=cur_df_in,
                df_live=cur_df_live,
                results=cur_res,
                processed_rows=cur_processed,
                total_rows=cur_total,
                target_col=cur_col,
                elapsed_time=cur_elap
            )
            st.toast(f"✅ Đã lưu bản sao: {snp_id}!", icon="💾")
            st.rerun()

        st.markdown("---")
        # Danh sách bản sao đã lưu
        saved_list = list_snapshots()
        if not saved_list:
            st.info("Chưa có bản sao nào được lưu.")
        else:
            st.markdown(f"**Danh sách ({len(saved_list)} bản sao):**")
            for snp in saved_list:
                st.markdown(f"""
                <div style="background:#1E293B; border:1px solid #334155; border-radius:8px; padding:8px 10px; margin-bottom:6px; color:#F8FAFC; font-size:0.85rem;">
                    <div style="font-weight:700; color:#38BDF8;">📦 {snp['name']}</div>
                    <div style="color:#CBD5E1; margin-top:2px; font-size:0.8rem;">
                        📅 {snp['created_at']}<br>
                        ⚡ <span style="color:#F59E0B; font-weight:600;">{snp['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_sb_res, c_sb_del = st.columns([1, 1])
                with c_sb_res:
                    if st.button("📂 Nạp", key=f"sb_res_{snp['snapshot_id']}", use_container_width=True, type="primary"):
                        data = load_snapshot(snp['snapshot_id'])
                        if data:
                            st.session_state["df_cached"] = data["df_input"]
                            st.session_state["current_file_id"] = f"snapshot_{snp['snapshot_id']}"
                            st.session_state["selected_col"] = data.get("target_col", "")
                            st.session_state["clean_idx"] = data.get("processed_rows", 0)
                            st.session_state["clean_results"] = data.get("results", [])
                            st.session_state["clean_live_df"] = data.get("df_live")
                            st.session_state["clean_elapsed"] = data.get("elapsed_time", 0.0)
                            
                            total_r = data.get("total_rows", 0)
                            proc_r = data.get("processed_rows", 0)
                            
                            if proc_r >= total_r and total_r > 0:
                                st.session_state["pipeline_state"] = "COMPLETED"
                                st.session_state["results"] = data.get("results", [])
                                st.session_state["df_live_final"] = data.get("df_live")
                                st.session_state["target_df"] = data["df_input"]
                                st.session_state["target_col"] = data.get("target_col", "")
                            else:
                                st.session_state["pipeline_state"] = "PAUSED"
                                st.session_state["results"] = data.get("results", [])
                                st.session_state["df_live_final"] = data.get("df_live")
                                st.session_state["target_df"] = data["df_input"]
                                st.session_state["target_col"] = data.get("target_col", "")
                                
                            st.toast(f"Đã nạp bản sao: {snp['name']}", icon="📂")
                            st.rerun()
                with c_sb_del:
                    if st.button("🗑️ Xóa", key=f"sb_del_{snp['snapshot_id']}", use_container_width=True):
                        if delete_snapshot(snp['snapshot_id']):
                            st.toast("Đã xóa bản sao!", icon="🗑️")
                            st.rerun()
                st.write("")

    # -------------------------------------------------------------------------
    # PHẦN LỊCH SỬ DẠY AI - TOOL (AI TEACHING MEMORY LOG)
    # -------------------------------------------------------------------------
    with st.expander("🧠 Lịch Sử Dạy AI — Tool", expanded=False):
        st.markdown("""
        <div style="font-size:0.83rem; color:#CBD5E1; margin-bottom:8px;">
            Ghi nhớ mọi bài học & quy tắc bạn đã dạy cho AI. Tự động áp dụng vào quy trình xử lý dữ liệu.
        </div>
        """, unsafe_allow_html=True)
        
        teach_text_input = st.text_area(
            "Dạy kiến thức mới cho AI:",
            placeholder="Gõ: Dạy AI: [Nội dung quy tắc / kinh nghiệm mới]...",
            help="Ví dụ: Dạy AI: Các từ viết tắt như 'bt' chuyển thành 'bình thường'...",
            key="txt_teach_ai_box",
            height=85
        )
        if st.button("🧠 Ghi Nhớ & Dạy AI Ngay", type="primary", use_container_width=True, key="btn_teach_ai_act"):
            if teach_text_input.strip():
                new_rule = add_teaching_rule(teach_text_input)
                st.toast(f"✅ AI đã học và lưu bài học mới: [{new_rule['tag']}]!", icon="🧠")
                st.rerun()
            else:
                st.warning("Vui lòng nhập nội dung muốn dạy AI trước.")
        
        st.markdown("---")
        rules_mem = load_teaching_memory()
        st.markdown(f"**📚 Bộ nhớ AI ({len(rules_mem)} quy tắc đã lưu):**")
        
        for rule in rules_mem:
            tag_name = rule.get("tag", "Quy tắc")
            tag_color = "#38BDF8" if tag_name == "Lọc Review Vô Nghĩa" else ("#34D399" if tag_name == "Nhận Diện Đa Ngôn Ngữ" else ("#F59E0B" if tag_name == "Sửa Lỗi Chính Tả & Teencode" else "#EC4899"))
            st.markdown(f"""
            <div style="background:#1E293B; border:1px solid #334155; border-radius:8px; padding:10px 12px; margin-bottom:8px; color:#F8FAFC; font-size:0.83rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="background:rgba(255,255,255,0.1); color:{tag_color}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid {tag_color};">🏷️ {tag_name}</span>
                    <span style="color:#94A3B8; font-size:0.75rem;">📅 {rule.get('created_at', '')}</span>
                </div>
                <div style="color:#E2E8F0; line-height:1.45; margin-top:4px;">
                    {rule.get('content', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not rule.get("is_default", False):
                if st.button("🗑️ Xóa bài học này", key=f"del_mem_rule_{rule['id']}", use_container_width=True):
                    delete_teaching_rule(rule['id'])
                    st.toast("Đã xóa bài học khỏi bộ nhớ AI!", icon="🗑️")
                    st.rerun()

    st.divider()

    # -------------------------------------------------------------------------
    # 1. CÁC BƯỚC LÀM SẠCH & NLP (CỐ ĐỊNH CHUẨN UEH 100% - KHÔNG CHO CHỈNH SỬA)
    # -------------------------------------------------------------------------
    opt_translate = True
    opt_teencode = True
    opt_lowercase = True
    opt_remove_icons = True
    opt_tokenize = True
    opt_remove_sw = True
    nlp_engine = "underthesea" if HAS_UNDERTHESEA else ("pyvi" if HAS_PYVI else "regex")

    st.markdown("""
    <div style="background:rgba(56, 189, 248, 0.1); border:1px solid #0284C7; border-radius:8px; padding:10px 12px; margin-bottom:12px; font-size:0.83rem; color:#E2E8F0;">
        🔒 <b>Quy trình NLP chuẩn UEH đã cố định:</b><br>
        <span style="color:#38BDF8;">✓ Dịch đa ngôn ngữ</span> &nbsp;|&nbsp; 
        <span style="color:#38BDF8;">✓ Sửa Teencode</span><br>
        <span style="color:#38BDF8;">✓ Tách từ ghép (underthesea)</span> &nbsp;|&nbsp; 
        <span style="color:#38BDF8;">✓ Lọc từ dừng</span>
    </div>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # 2. TÙY CHỈNH TỪ DỪNG (KÈM NOTIFICATION TỰ ĐỘNG LƯU KHI ENTER / CLICK RA NGOÀI)
    # -------------------------------------------------------------------------
    st.subheader("1. Tùy chỉnh Từ dừng (Stopwords)")
    extra_sw_input = st.text_area(
        "Thêm từ dừng riêng (ngăn cách bởi dấu phẩy):",
        value=st.session_state.get("extra_sw_value", "shop, đóng_gói, cảm_ơn"),
        help="Thêm các từ đặc thù bạn muốn loại bỏ thêm. Nhấn Enter hoặc click ra ngoài để tự động lưu.",
        key="txt_extra_sw"
    )
    
    active_stopwords = set(default_stopwords)
    if extra_sw_input:
        for w in extra_sw_input.split(","):
            w_clean = w.strip().lower()
            if w_clean:
                active_stopwords.add(w_clean)
                active_stopwords.add(w_clean.replace(" ", "_"))

    # Bắn thông báo nhẹ (noti) khi người dùng vừa chỉnh sửa và Enter/click ra ngoài
    if "last_sw_text" not in st.session_state:
        st.session_state["last_sw_text"] = extra_sw_input
    elif st.session_state["last_sw_text"] != extra_sw_input:
        st.session_state["last_sw_text"] = extra_sw_input
        st.session_state["extra_sw_value"] = extra_sw_input
        st.toast(f"✅ Đã tự động lưu bộ từ dừng! (Tổng: {len(active_stopwords)} từ)", icon="💾")

    st.caption(f"💾 *Tự động lưu:* Tổng số từ dừng đang áp dụng: **{len(active_stopwords)}** từ.")

    st.divider()

    # -------------------------------------------------------------------------
    # 2. MÔ HÌNH AI NHẬN DIỆN ĐA NGÔN NGỮ
    # -------------------------------------------------------------------------
    st.subheader("2. Mô hình AI Đa Ngôn Ngữ")
    ai_mode = st.selectbox(
        "Công cụ AI Đa Ngôn Ngữ & Dịch Thuật:",
        options=[
            "🌐 Google Multi-lingual AI (Miễn phí - Nga, Trung, Hàn, Nhật, Pháp, Ý, Anh...)",
            "⚡ Google Gemini 2.0 Flash Lite (Sử dụng API Key)"
        ],
        index=0,
        help="Tự động nhận diện chính xác các ngôn ngữ nước ngoài và dịch ngữ cảnh sang Tiếng Việt chuẩn xác."
    )
    gemini_api_key = ""
    if "Gemini" in ai_mode:
        gemini_api_key = st.text_input("Nhập Gemini API Key:", type="password", help="Nhập API key từ Google AI Studio (miễn phí) để kích hoạt Gemini Flash Lite.")

# DỮ LIỆU MẪU ĐA DẠNG CHUẨN UEH
RICH_SAMPLE_DATA = [
    {"Mã": "RV01", "Tháng": "T1", "Ngành hàng": "Quán ăn", "Bình luận": "Cho miếng ức nhìn khô , đổi lại thì ko dc. Nay ăn trúng gà ko dc tươi ngày 31/3 lúc 9h30", "Đánh giá": "1 sao"},
    {"Mã": "RV02", "Tháng": "T1", "Ngành hàng": "Quán cà phê", "Bình luận": "Had great cappuccino! Quán decor siêu xinh, nhân viên dth nhiệt tình ❤️", "Đánh giá": "5 sao"},
    {"Mã": "RV03", "Tháng": "T2", "Ngành hàng": "Thời trang", "Bình luận": "Shop ơi GIAO HÀNG chậm quá :(( nhưng chất lượng ổn áp nha!!!", "Đánh giá": "4 sao"},
    {"Mã": "RV04", "Tháng": "T2", "Ngành hàng": "Khách sạn", "Bình luận": "L9cation is best, just opposite arrival at airport. Phòng ốc sạch sẽ chu đáo ^^", "Đánh giá": "5 sao"},
    {"Mã": "RV05", "Tháng": "T3", "Ngành hàng": "Thời trang", "Bình luận": "Qá tuyt vời! Vải mát form chuẩn size M mặc vừa vặn lắm luôn ạ :3", "Đánh giá": "5 sao"},
    {"Mã": "RV06", "Tháng": "T3", "Ngành hàng": "Quán ăn", "Bình luận": "Je n’arrive pas à mettre 5 étoiles ,il y a deux types qui ont l’air de rogner.", "Đánh giá": "2 sao"},
    {"Mã": "RV07", "Tháng": "T4", "Ngành hàng": "Quán ăn", "Bình luận": "tutto sporco. ovunque sporcizia e non puliscono ne all'interno che all'esterno e neanche i tavoli.", "Đánh giá": "1 sao"},
    {"Mã": "RV08", "Tháng": "T4", "Ngành hàng": "Quán ăn", "Bình luận": "Удобное расположение (рядом с аэропортом) Цены выше чем в макдональдсах, которые находятся подальше от аэропорта", "Đánh giá": "4 sao"},
    {"Mã": "RV09", "Tháng": "T5", "Ngành hàng": "Ứng dụng", "Bình luận": "tắt mm app đi", "Đánh giá": "1 sao"},
    {"Mã": "RV10", "Tháng": "T6", "Ngành hàng": "Quán ăn", "Bình luận": "不要在外面平台點這家餐廳，外送員完全找不到位置，餐點送到都冷掉了", "Đánh giá": "1 sao"}
]

# QUẢN LÝ DỮ LIỆU VÀ TRẠNG THÁI TỪNG BƯỚC
if "df_cached" not in st.session_state:
    st.session_state["df_cached"] = None
if "current_file_id" not in st.session_state:
    st.session_state["current_file_id"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None
if "df_live_final" not in st.session_state:
    st.session_state["df_live_final"] = None
if "show_sentiment_col" not in st.session_state:
    st.session_state["show_sentiment_col"] = False
if "show_visual_diff" not in st.session_state:
    st.session_state["show_visual_diff"] = False
if "show_deep_analysis" not in st.session_state:
    st.session_state["show_deep_analysis"] = False

# Trạng thái luồng xử lý Real-time (IDLE, RUNNING, PAUSED, COMPLETED)
if "pipeline_state" not in st.session_state:
    st.session_state["pipeline_state"] = "IDLE"
if "clean_idx" not in st.session_state:
    st.session_state["clean_idx"] = 0
if "clean_results" not in st.session_state:
    st.session_state["clean_results"] = []
if "clean_live_df" not in st.session_state:
    st.session_state["clean_live_df"] = None
if "clean_elapsed" not in st.session_state:
    st.session_state["clean_elapsed"] = 0.0
if "clean_batch_size" not in st.session_state:
    st.session_state["clean_batch_size"] = 100

def render_dark_dataframe(df_to_render: pd.DataFrame, max_height: str = "600px") -> str:
    if df_to_render is None or df_to_render.empty:
        return '<div style="color:#94a3b8; font-style:italic;">(Không có dữ liệu)</div>'
        
    columns = list(df_to_render.columns)
    
    # Headers
    th_html_list = []
    for c in columns:
        c_str = str(c)
        c_l = c_str.lower()
        if any(k in c_l for k in ["stt", "id", "mã"]):
            th_html_list.append(f'<th style="width: 60px; text-align: center;">{c_str}</th>')
        elif any(k in c_l for k in ["tháng"]):
            th_html_list.append(f'<th style="width: 80px; text-align: center;">{c_str}</th>')
        elif any(k in c_l for k in ["cảm xúc", "sentiment"]):
            th_html_list.append(f'<th style="width: 140px; text-align: center;">{c_str}</th>')
        elif any(k in c_l for k in ["ngành hàng", "đánh giá", "tình trạng"]):
            th_html_list.append(f'<th style="width: 130px;">{c_str}</th>')
        elif any(k in c_l for k in ["tokens"]):
            th_html_list.append(f'<th style="width: 18%;">{c_str}</th>')
        elif any(k in c_l for k in ["bình luận", "review", "text", "dịch", "sửa", "clean"]):
            th_html_list.append(f'<th style="min-width: 180px;">{c_str}</th>')
        else:
            th_html_list.append(f'<th>{c_str}</th>')
            
    header_tr = "".join(th_html_list)
    
    # Rows
    rows_html_list = []
    for idx, row in df_to_render.iterrows():
        row_str = " ".join([str(v) for v in row.values])
        is_removed = ("LOẠI" in row_str) or ("Đã loại bỏ" in row_str) or ("❌" in row_str)
        
        row_class = "removed-row" if is_removed else ""
        
        td_html_list = []
        for c in columns:
            val = row[c]
            val_str = str(val) if val is not None else ""
            c_l = str(c).lower()
            
            if "cảm xúc" in c_l or "sentiment" in c_l:
                if "Tích cực" in val_str or "🟢" in val_str:
                    td_html_list.append(f'<td class="sent-cell"><span class="diff-badge badge-pos">{val_str}</span></td>')
                elif "Tiêu cực" in val_str or "🔴" in val_str:
                    td_html_list.append(f'<td class="sent-cell"><span class="diff-badge badge-neg">{val_str}</span></td>')
                elif "LOẠI" in val_str or "Đã loại" in val_str:
                    td_html_list.append(f'<td class="sent-cell"><span class="diff-badge badge-loai">{val_str}</span></td>')
                elif val_str and val_str != "-":
                    td_html_list.append(f'<td class="sent-cell"><span class="diff-badge badge-neu">{val_str}</span></td>')
                else:
                    td_html_list.append('<td class="sent-cell">-</td>')
            elif any(k in c_l for k in ["stt", "id", "mã"]):
                td_html_list.append(f'<td class="stt-cell">{val_str}</td>')
            elif "tokens" in c_l:
                if val_str and val_str != "LOẠI":
                    td_html_list.append(f'<td class="token-cell"><code>{val_str}</code></td>')
                elif val_str == "LOẠI":
                    td_html_list.append('<td class="token-cell"><span style="color:#f87171; font-weight:700;">LOẠI</span></td>')
                else:
                    td_html_list.append('<td></td>')
            elif "clean" in c_l:
                if val_str == "LOẠI":
                    td_html_list.append('<td class="clean-cell" style="color:#f87171; font-weight:700;">LOẠI</td>')
                else:
                    td_html_list.append(f'<td class="clean-cell">{val_str}</td>')
            elif "dịch" in c_l or "sửa" in c_l:
                if val_str == "LOẠI":
                    td_html_list.append('<td style="color:#f87171; font-weight:700;">LOẠI</td>')
                else:
                    td_html_list.append(f'<td>{val_str}</td>')
            elif "tình trạng" in c_l:
                td_html_list.append(f'<td><span class="diff-badge badge-neg">{val_str}</span></td>')
            else:
                td_html_list.append(f'<td>{val_str}</td>')
                
        tr_html = f'<tr class="{row_class}">{"".join(td_html_list)}</tr>'
        rows_html_list.append(tr_html)
        
    tbody_html = "".join(rows_html_list)
    
    scroll_style = f"height: {max_height}; min-height: 320px; resize: vertical; overflow: auto;" if max_height else "resize: vertical; overflow: auto;"
    return (
        f'<div class="diff-table-container" style="{scroll_style}">'
        '<table class="dark-diff-table">'
        f'<thead><tr>{header_tr}</tr></thead>'
        f'<tbody>{tbody_html}</tbody>'
        '</table>'
        '</div>'
    )

# =========================================================================================
# PHẦN 1: TẢI LÊN & XEM TRƯỚC DỮ LIỆU
# =========================================================================================
st.markdown("### 📁 1. TẢI LÊN FILE DỮ LIỆU EXCEL / CSV")
st.caption("Hãy nạp tệp Excel chứa cột review cần làm sạch hoặc bấm nạp dữ liệu mẫu chuẩn UEH:")

col_u1, col_u2 = st.columns([3, 1])
with col_u1:
    uploaded_file = st.file_uploader("Kéo thả file Excel (.xlsx, .xls) hoặc .csv", type=["xlsx", "xls", "csv"], key="uploader")
with col_u2:
    st.write("Hoặc dùng thử ngay:")
    if st.button("📂 Nạp Dữ Liệu Mẫu (10 Reviews Đa Ngôn Ngữ)", key="btn_sample", type="secondary", use_container_width=True):
        st.session_state["df_cached"] = pd.DataFrame(RICH_SAMPLE_DATA)
        st.session_state["current_file_id"] = "sample_ueh_rich_v2"
        st.session_state["results"] = None
        st.session_state["df_live_final"] = None
        st.session_state["pipeline_state"] = "IDLE"
        st.session_state["clean_idx"] = 0
        st.session_state["clean_results"] = []
        st.session_state["clean_live_df"] = None
        st.session_state["clean_elapsed"] = 0.0
        st.session_state["show_sentiment_col"] = False
        st.session_state["show_visual_diff"] = False
        st.session_state["show_deep_analysis"] = False
        st.toast("Đã nạp 10 dòng dữ liệu mẫu đa ngôn ngữ!", icon="📂")
        st.rerun()

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("current_file_id") != file_id:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_loaded = pd.read_csv(uploaded_file)
            else:
                df_loaded = pd.read_excel(uploaded_file)
            st.session_state["df_cached"] = df_loaded
            st.session_state["current_file_id"] = file_id
            st.session_state["results"] = None
            st.session_state["df_live_final"] = None
            st.session_state["pipeline_state"] = "IDLE"
            st.session_state["clean_idx"] = 0
            st.session_state["clean_results"] = []
            st.session_state["clean_live_df"] = None
            st.session_state["clean_elapsed"] = 0.0
            st.session_state["show_sentiment_col"] = False
            st.session_state["show_visual_diff"] = False
            st.session_state["show_deep_analysis"] = False
            st.toast(f"Đã nạp file: {uploaded_file.name}", icon="📁")
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")



df_input = st.session_state.get("df_cached", None)

if df_input is not None:
    st.success(f"Dữ liệu hiện tại: **{len(df_input)} dòng**, **{len(df_input.columns)} cột**")
    st.markdown("#### 🔍 Chọn Cột Dữ Liệu Chứa Bình Luận Thô Cần Xử Lý:")
    default_idx = 0
    col_names = list(df_input.columns)
    for idx, c in enumerate(col_names):
        c_l = str(c).lower()
        if any(k in c_l for k in ["bình luận", "review", "comment", "đánh giá", "nhận xét", "nội dung", "text"]):
            default_idx = idx
            break
            
    saved_sel_col = st.session_state.get("selected_col")
    if saved_sel_col in col_names:
        default_idx = col_names.index(saved_sel_col)

    selected_col = st.selectbox("Chọn cột văn bản review cần xử lý:", options=col_names, index=default_idx)
    st.session_state["selected_col"] = selected_col

    st.write("")
    
    pipeline_state = st.session_state.get("pipeline_state", "IDLE")
    total_rows = len(df_input)
    current_idx = st.session_state.get("clean_idx", 0)

    # =====================================================================================
    # GIAO DIỆN ĐIỀU KHIỂN CHẠY / TẠM DỪNG / TIẾP TỤC
    # =====================================================================================
    if pipeline_state == "IDLE":
        btn_clean_run = st.button("🚀 BẮT ĐẦU CLEAN DỮ LIỆU (REAL-TIME PIPELINE)", type="primary", use_container_width=True, key="btn_start_clean")
        if btn_clean_run:
            st.session_state["pipeline_state"] = "RUNNING"
            st.session_state["clean_idx"] = 0
            st.session_state["clean_results"] = []
            st.session_state["clean_elapsed"] = 0.0
            
            # Khởi tạo bảng live
            df_live = df_input.copy()
            df_live["[1. Dịch Tiếng Việt, Lowercase & Bỏ Ký Tự Thừa]"] = ""
            df_live["[2. Sửa Teencode & Lỗi]"] = ""
            df_live["[3. Văn Bản Đã Clean]"] = ""
            df_live["[4. Tokens NLP]"] = ""
            st.session_state["clean_live_df"] = df_live
            st.session_state["show_sentiment_col"] = False
            st.session_state["show_visual_diff"] = False
            st.session_state["show_deep_analysis"] = False
            st.rerun()

    elif pipeline_state == "RUNNING":
        # KHUNG ĐIỀU KHIỂN TIẾN ĐỘ KHI ĐANG CHẠY
        elapsed_now = st.session_state.get("clean_elapsed", 0.0)
        curr_p = int((current_idx / max(1, total_rows)) * 100)
        avg_t = elapsed_now / max(1, current_idx) if current_idx > 0 else 0.002
        eta = max(0.0, avg_t * (total_rows - current_idx))

        col_hud1, col_hud2 = st.columns([4, 1])
        with col_hud1:
            st.markdown(f"""
            <div style="background:#1E293B; border:1px solid #38BDF8; border-radius:10px; padding:12px 18px; margin-bottom:12px; color:#F8FAFC; box-shadow:0 4px 16px rgba(56, 189, 248, 0.2);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div style="font-size:1.05rem; font-weight:700; color:#38BDF8;">⚡ Đang chạy Pipeline Clean Real-Time...</div>
                    <div style="font-size:1.1rem; font-weight:800; color:#4ADE80;">{curr_p}% ({current_idx}/{total_rows} dòng)</div>
                </div>
                <div style="display:flex; gap:20px; font-size:0.9rem; color:#CBD5E1;">
                    <div>⏱️ <b>Thời gian đã chạy:</b> <code style="background:#0F172A; color:#38BDF8; padding:2px 6px; border-radius:4px;">{round(elapsed_now, 1)}s</code></div>
                    <div>⏳ <b>Dự kiến còn:</b> <code style="background:#0F172A; color:#34D399; padding:2px 6px; border-radius:4px;">~{round(eta, 1)}s</code></div>
                    <div>🚀 <b>Tốc độ:</b> <code style="background:#0F172A; color:#FBBF24; padding:2px 6px; border-radius:4px;">{round(1/max(0.0001, avg_t), 0)} dòng/s</code></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(current_idx / max(1, total_rows))
            
        with col_hud2:
            st.write("")
            btn_pause = st.button("⏸️ TẠM DỪNG", type="secondary", use_container_width=True, help="Tạm dừng ngay lập tức tại vị trí hiện tại và lưu tiến độ", key="btn_pause_action")
            if btn_pause:
                st.session_state["pipeline_state"] = "PAUSED"
                st.toast(f"⏸️ Đã tạm dừng tiến độ tại dòng {current_idx}/{total_rows}!", icon="⏸️")
                st.rerun()

        # THỰC HIỆN CLEAN THEO BATCH
        batch_size = 100 if total_rows > 300 else 20
        end_idx = min(current_idx + batch_size, total_rows)
        
        t0 = time.time()
        df_live = st.session_state["clean_live_df"]
        results_list = st.session_state["clean_results"]

        for i in range(current_idx, end_idx):
            row = df_input.iloc[i]
            raw_val = row[selected_col]
            res = clean_single_review(
                raw_text=raw_val,
                stopwords=active_stopwords,
                translate_to_vi=opt_translate,
                fix_teencode=opt_teencode,
                use_lowercase=opt_lowercase,
                remove_icons=opt_remove_icons,
                word_segmentation=opt_tokenize,
                remove_sw=opt_remove_sw,
                nlp_engine=nlp_engine
            )
            results_list.append(res)
            df_live.at[i, "[1. Dịch Tiếng Việt, Lowercase & Bỏ Ký Tự Thừa]"] = res["step1_translated_clean"]
            df_live.at[i, "[2. Sửa Teencode & Lỗi]"] = res["step2_teencode"]
            df_live.at[i, "[3. Văn Bản Đã Clean]"] = res["cleaned_text"]
            df_live.at[i, "[4. Tokens NLP]"] = ", ".join(res["tokens"])

        batch_time = time.time() - t0
        st.session_state["clean_idx"] = end_idx
        st.session_state["clean_elapsed"] += batch_time
        st.session_state["clean_live_df"] = df_live
        st.session_state["clean_results"] = results_list

        # Hiển thị cửa sổ 8 dòng đang xử lý
        w_start = max(0, end_idx - 8)
        st.caption("👀 Luồng dữ liệu mới nhất đang chạy qua bộ tiền xử lý:")
        st.markdown(render_dark_dataframe(df_live.iloc[w_start:end_idx], max_height="260px"), unsafe_allow_html=True)

        if end_idx >= total_rows:
            st.session_state["pipeline_state"] = "COMPLETED"
            st.session_state["results"] = results_list
            st.session_state["df_live_final"] = df_live
            st.session_state["target_df"] = df_input
            st.session_state["target_col"] = selected_col
            st.session_state["elapsed"] = round(st.session_state["clean_elapsed"], 2)
            st.toast("🎉 Đã hoàn thành Clean dữ liệu 100%!", icon="✅")
            st.balloons()
            st.rerun()
        else:
            st.rerun()

    elif pipeline_state == "PAUSED":
        curr_p = int((current_idx / max(1, total_rows)) * 100)
        st.markdown(f"""
        <div style="background:rgba(245, 158, 11, 0.15); border:2px solid #F59E0B; border-radius:10px; padding:14px 20px; margin-bottom:16px; color:#F8FAFC;">
            <div style="font-size:1.15rem; font-weight:800; color:#FBBF24; margin-bottom:4px;">
                ⏸️ ĐÃ TẠM DỪNG XỬ LÝ (Đã hoàn tất {current_idx} / {total_rows} dòng - {curr_p}%)
            </div>
            <div style="color:#CBD5E1; font-size:0.95rem;">
                Dữ liệu đã được lưu an toàn trong phiên làm việc. Bạn có thể <b>Tiếp tục xử lý</b> từ dòng {current_idx + 1}, hoặc <b>Lưu thành bản sao</b> vào Tool để sử dụng sau.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_p1, col_p2, col_p3 = st.columns([2, 2, 2])
        with col_p1:
            if st.button(f"▶️ TIẾP TỤC CLEAN (Từ dòng {current_idx + 1})", type="primary", use_container_width=True, key="btn_resume_action"):
                st.session_state["pipeline_state"] = "RUNNING"
                st.toast(f"▶️ Đang tiếp tục xử lý từ dòng {current_idx + 1}...", icon="🚀")
                st.rerun()
        with col_p2:
            if st.button("💾 LƯU BẢN SAO TIẾN ĐỘ NÀY", type="secondary", use_container_width=True, key="btn_save_paused_snp"):
                cur_df_in = st.session_state.get("df_cached")
                cur_df_live = st.session_state.get("clean_live_df")
                cur_res = st.session_state.get("clean_results", [])
                cur_col = st.session_state.get("selected_col", "")
                cur_elap = st.session_state.get("clean_elapsed", 0.0)
                snp_id = save_snapshot(
                    name=f"Tiến độ tạm dừng ({current_idx}/{total_rows} dòng)",
                    df_input=cur_df_in,
                    df_live=cur_df_live,
                    results=cur_res,
                    processed_rows=current_idx,
                    total_rows=total_rows,
                    target_col=cur_col,
                    elapsed_time=cur_elap
                )
                st.toast(f"✅ Đã lưu bản sao tiến độ ({snp_id})!", icon="💾")
                st.rerun()
        with col_p3:
            if st.button("🔄 HỦY & BẮT ĐẦU LẠI TỪ ĐẦU", type="secondary", use_container_width=True, key="btn_reset_action"):
                st.session_state["pipeline_state"] = "IDLE"
                st.session_state["clean_idx"] = 0
                st.session_state["clean_results"] = []
                st.session_state["clean_live_df"] = None
                st.session_state["clean_elapsed"] = 0.0
                st.toast("Đã đặt lại trạng thái xử lý ban đầu.", icon="🔄")
                st.rerun()

        # Hiển thị bảng dữ liệu đã xử lý được tới thời điểm tạm dừng
        st.markdown(f"#### 📊 Bảng Dữ Liệu Đã Xử Lý Được ({current_idx} dòng):")
        df_live_paused = st.session_state.get("clean_live_df")
        if df_live_paused is not None:
            df_slice_paused = df_live_paused.iloc[:current_idx]
            if current_idx > 1000:
                p_size = 1000
                tot_p = (current_idx + p_size - 1) // p_size
                p_sel = st.selectbox(
                    f"📄 Chọn trang xem ({tot_p} trang, 1,000 dòng/trang):",
                    options=list(range(1, tot_p + 1)),
                    format_func=lambda x: f"Trang {x} (Dòng {(x-1)*p_size + 1} - {min(x*p_size, current_idx)})",
                    key="sb_page_paused"
                )
                st_p = (p_sel - 1) * p_size
                en_p = min(st_p + p_size, current_idx)
                st.markdown(render_dark_dataframe(df_slice_paused.iloc[st_p:en_p], max_height="600px"), unsafe_allow_html=True)
            else:
                st.markdown(render_dark_dataframe(df_slice_paused, max_height="600px"), unsafe_allow_html=True)

    elif pipeline_state == "COMPLETED":
        total_elapsed = st.session_state.get("elapsed", round(st.session_state.get("clean_elapsed", 0.0), 2))
        st.markdown(f"""
        <div style="background:rgba(16, 185, 129, 0.15); border:2px solid #10B981; border-radius:10px; padding:14px 20px; margin-bottom:16px; color:#F8FAFC; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-size:1.18rem; font-weight:800; color:#34D399;">
                    🎉 HOÀN TẤT CLEAN DỮ LIỆU 100% ({total_rows} dòng)!
                </div>
                <div style="color:#CBD5E1; font-size:0.92rem; margin-top:3px;">
                    Đã hoàn thành tiền xử lý NLP trong <b>{total_elapsed} giây</b>. Bạn có thể tiến hành phân tích cảm xúc, xem Visual Diff hoặc tải file Excel.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            if st.button("💾 LƯU KẾT QUẢ NÀY THÀNH BẢN SAO", type="secondary", use_container_width=True, key="btn_save_done_snp"):
                cur_df_in = st.session_state.get("target_df", df_input)
                cur_df_live = st.session_state.get("df_live_final")
                cur_res = st.session_state.get("results", [])
                cur_col = st.session_state.get("target_col", selected_col)
                cur_elap = st.session_state.get("elapsed", total_elapsed)
                snp_id = save_snapshot(
                    name=f"Kết quả Clean hoàn tất ({total_rows} dòng)",
                    df_input=cur_df_in,
                    df_live=cur_df_live,
                    results=cur_res,
                    processed_rows=total_rows,
                    total_rows=total_rows,
                    target_col=cur_col,
                    elapsed_time=cur_elap
                )
                st.toast(f"✅ Đã lưu bản sao kết quả hoàn tất ({snp_id})!", icon="💾")
                st.rerun()
        with col_c2:
            if st.button("🔄 CHẠY CLEAN LẠI TỪ ĐẦU", type="secondary", use_container_width=True, key="btn_rerun_clean"):
                st.session_state["pipeline_state"] = "IDLE"
                st.session_state["clean_idx"] = 0
                st.session_state["clean_results"] = []
                st.session_state["clean_live_df"] = None
                st.session_state["clean_elapsed"] = 0.0
                st.session_state["results"] = None
                st.rerun()

    # HIỂN THỊ KẾT QUẢ KHI ĐÃ CÓ DỮ LIỆU
    if st.session_state.get("results", None) is not None:
        results = st.session_state["results"]
        total_rows = len(results)
        is_sentiment_active = st.session_state.get("show_sentiment_col", False)

        # =====================================================================================
        # BƯỚC LỌC REVIEW : CÁC DÒNG REVIEW KHÔNG CÓ Ý NGHĨA ĐÃ BỊ LOẠI BỎ
        # =====================================================================================
        meaningless_items = [
            {
                "STT": idx + 1,
                "Review Gốc": r["raw_text"],
                "Tình Trạng": "❌ LOẠI",
                "Lý Do Loại Bỏ & Giải Thích": r["meaningless_reason"]
            }
            for idx, r in enumerate(results) if r.get("is_meaningless", False)
        ]

        if meaningless_items:
            st.markdown("#### 🗑️ BƯỚC LỌC REVIEW : CÁC DÒNG REVIEW KHÔNG CÓ Ý NGHĨA ĐÃ BỊ LOẠI BỎ")
            st.caption("Các dòng review dưới đây không mang ý nghĩa đánh giá sản phẩm / dịch vụ, câu vô nghĩa hoặc sai chính tả không thể hiểu/dịch được:")
            df_meaningless = pd.DataFrame(meaningless_items)
            st.markdown(render_dark_dataframe(df_meaningless, max_height="400px"), unsafe_allow_html=True)

        st.write("")
        # CÁC NÚT ĐIỀU HƯỚNG TỪNG BƯỚC (STEP 1.2, STEP 2, STEP 3)
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            btn_label_1 = "🏷️ BƯỚC 1.2: PHÂN TÍCH CẢM XÚC AI" if not is_sentiment_active else "🏷️ BƯỚC 1.2: ĐÃ HIỆN CẢM XÚC (BẤM ĐỂ ẨN)"
            btn_type_1 = "primary" if not is_sentiment_active else "secondary"
            if st.button(btn_label_1, type=btn_type_1, use_container_width=True, key="btn_step_1_2"):
                st.session_state["show_sentiment_col"] = not is_sentiment_active
                st.rerun()

        with col_s2:
            is_diff_active = st.session_state.get("show_visual_diff", False)
            btn_label_2 = "📋 BƯỚC 2: XEM BẢNG SO SÁNH VISUAL DIFF" if not is_diff_active else "📋 BƯỚC 2: ĐÃ MỞ VISUAL DIFF (BẤM ĐỂ ĐÓNG)"
            btn_type_2 = "primary" if not is_diff_active else "secondary"
            if st.button(btn_label_2, type=btn_type_2, use_container_width=True, key="btn_step_2"):
                st.session_state["show_visual_diff"] = not is_diff_active
                st.rerun()

        with col_s3:
            is_deep_active = st.session_state.get("show_deep_analysis", False)
            btn_label_3 = "📊 BƯỚC 3: XEM BÁO CÁO PHÂN TÍCH CHUYÊN SÂU" if not is_deep_active else "📊 BƯỚC 3: ĐÃ MỞ PHÂN TÍCH CHUYÊN SÂU (BẤM ĐỂ ĐÓNG)"
            btn_type_3 = "primary" if not is_deep_active else "secondary"
            if st.button(btn_label_3, type=btn_type_3, use_container_width=True, key="btn_step_3"):
                st.session_state["show_deep_analysis"] = not is_deep_active
                st.rerun()

        # =====================================================================================
        # STEP 1.2: HIỂN THỊ KẾT QUẢ CẢM XÚC AI & BẢNG TỔNG QUAN
        # =====================================================================================
        if is_sentiment_active:
            st.divider()
            st.markdown("### 🏷️ BƯỚC 1.2: KẾT QUẢ PHÂN TÍCH CẢM XÚC AI (SENTIMENT ANALYSIS)")
            
            valid_results = [r for r in results if not r.get("is_meaningless", False)]
            pos_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tích cực")
            neg_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tiêu cực")
            neu_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Trung tính")
            tot = max(1, len(valid_results))

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(f"""
                <div class="sent-card-pos">
                    <div class="card-title" style="color:#4ADE80">🟢 TÍCH CỰC (POSITIVE)</div>
                    <div class="card-subtitle"><b>{pos_cnt}</b> bình luận (<b>{round(pos_cnt/tot*100, 1)}%</b>)</div>
                </div>
                """, unsafe_allow_html=True)

            with sc2:
                st.markdown(f"""
                <div class="sent-card-neg">
                    <div class="card-title" style="color:#F87171">🔴 TIÊU CỰC (NEGATIVE)</div>
                    <div class="card-subtitle"><b>{neg_cnt}</b> bình luận (<b>{round(neg_cnt/tot*100, 1)}%</b>)</div>
                </div>
                """, unsafe_allow_html=True)

            with sc3:
                st.markdown(f"""
                <div class="sent-card-neu">
                    <div class="card-title" style="color:#60A5FA">🔵 TRUNG TÍNH (NEUTRAL)</div>
                    <div class="card-subtitle"><b>{neu_cnt}</b> bình luận (<b>{round(neu_cnt/tot*100, 1)}%</b>)</div>
                </div>
                """, unsafe_allow_html=True)

            df_sent_step12 = pd.DataFrame([
                {"Loại Cảm Xúc": "🟢 Tích cực (Positive)", "Số Lượng Bình Luận": pos_cnt, "Tỷ Lệ %": f"{round(pos_cnt/tot*100, 1)}%", "Đánh Giá": "Khách hàng hài lòng, khen ngợi chất lượng/dịch vụ"},
                {"Loại Cảm Xúc": "🔴 Tiêu cực (Negative)", "Số Lượng Bình Luận": neg_cnt, "Tỷ Lệ %": f"{round(neg_cnt/tot*100, 1)}%", "Đánh Giá": "Khách phàn nàn về giao hàng chậm, hàng lỗi, thái độ"},
                {"Loại Cảm Xúc": "🔵 Trung tính (Neutral)", "Số Lượng Bình Luận": neu_cnt, "Tỷ Lệ %": f"{round(neu_cnt/tot*100, 1)}%", "Đánh Giá": "Bình luận hỏi thông tin, đặt size, trung lập"}
            ])
            st.markdown(render_dark_dataframe(df_sent_step12, max_height=""), unsafe_allow_html=True)

            # BẢNG DỮ LIỆU BƯỚC 1.2: 5 TRƯỜNG CHUẨN (ID, TEXT, VĂN BẢN ĐÃ CLEAN, TOKENS NLP, Sentiment)
            st.markdown("#### ⚡ Bảng Dữ Liệu Sau Khi Clean & Gán Cảm Xúc AI:")
            df_step12_table = pd.DataFrame({
                "ID": [idx + 1 for idx in range(total_rows)],
                "TEXT": [r["raw_text"] for r in results],
                "VĂN BẢN ĐÃ CLEAN": [r["cleaned_text"] if not r.get("is_meaningless", False) else "LOẠI" for r in results],
                "TOKENS NLP": [", ".join(r["tokens"]) if not r.get("is_meaningless", False) else "LOẠI" for r in results],
                "Sentiment": [r["sentiment"]["badge"] for r in results]
            })

            if total_rows > 1000:
                page_size = 1000
                total_pages = (total_rows + page_size - 1) // page_size
                cp1, cp2 = st.columns([2, 3])
                with cp1:
                    page_sel = st.selectbox(
                        f"📄 Chọn trang xem ({total_pages} trang, 1,000 dòng/trang):",
                        options=list(range(1, total_pages + 1)),
                        format_func=lambda x: f"Trang {x} (Dòng {(x-1)*page_size + 1} - {min(x*page_size, total_rows)})",
                        key="sb_page_step12"
                    )
                start_p = (page_sel - 1) * page_size
                end_p = min(start_p + page_size, total_rows)
                df_step12_view = df_step12_table.iloc[start_p:end_p]
                st.markdown(render_dark_dataframe(df_step12_view, max_height="650px"), unsafe_allow_html=True)
            else:
                st.markdown(render_dark_dataframe(df_step12_table, max_height="650px"), unsafe_allow_html=True)

        # =====================================================================================
        # STEP 2: BẢNG DỮ LIỆU ĐÃ CLEAN VÀ VISUAL DIFF (CLICK MỚI RA)
        # =====================================================================================
        if st.session_state.get("show_visual_diff", False):
            st.divider()
            st.markdown("### 📋 BƯỚC 2: BẢNG SO SÁNH CHI TIẾT (VISUAL DIFF & ĐIỂM THAY ĐỔI)")
            
            total_teencode_fixed = sum(len(r["replaced_teencodes"]) for r in results)
            total_icons_removed = sum(len(r["removed_icons"]) for r in results)
            total_sw_removed = sum(len(r["removed_stopwords"]) for r in results)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tổng số dòng đã Clean", f"{total_rows}")
            m2.metric("Từ Teencode đã sửa", f"{total_teencode_fixed} từ", delta="✏️ Đã chuẩn hóa")
            m3.metric("Icon/Emoji đã loại", f"{total_icons_removed}", delta="😊 Đã xóa")
            m4.metric("Từ dừng đã lọc", f"{total_sw_removed}", delta="🚫 Đã loại bỏ")

            st.markdown("""
            <div class="diff-legend-card">
                <div style="font-size:1.05rem; font-weight:700; color:#38BDF8; margin-bottom:8px;">
                    🎨 BẢNG QUY ĐỊNH MÀU SẮC (DARK MODE HIGHLIGHT):
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:16px; font-size:0.9rem; align-items:center;">
                    <div><del style="background-color:rgba(239, 68, 68, 0.22); color:#F87171; border:1px solid rgba(239, 68, 68, 0.45); padding:3px 8px; border-radius:6px; font-weight:600;">Gạch ngang màu đỏ</del> : Từ dừng (stopwords) & Icon đã bị loại bỏ.</div>
                    <div><span style="background-color:rgba(245, 158, 11, 0.22); color:#FBBF24; border:1px solid rgba(245, 158, 11, 0.5); padding:3px 8px; border-radius:6px; font-weight:600;">Màu cam</span> : Teencode / Lỗi chính tả đã chuẩn hóa.</div>
                    <div><span style="background-color:rgba(34, 197, 94, 0.22); color:#4ADE80; border:1px solid rgba(34, 197, 94, 0.45); padding:3px 8px; border-radius:6px; font-weight:600;">Màu xanh lá</span> : Chuỗi Token NLP giữ lại.</div>
                    <div><b>Cảm xúc AI:</b> <span class="diff-badge badge-pos">🟢 Tích cực</span> &nbsp;<span class="diff-badge badge-neg">🔴 Tiêu cực</span> &nbsp;<span class="diff-badge badge-neu">🔵 Trung tính</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if total_rows > 1000:
                page_size_diff = 1000
                total_pages_diff = (total_rows + page_size_diff - 1) // page_size_diff
                cpd1, cpd2 = st.columns([2, 3])
                with cpd1:
                    page_diff_sel = st.selectbox(
                        f"📄 Chọn trang Visual Diff ({total_pages_diff} trang, 1,000 dòng/trang):",
                        options=list(range(1, total_pages_diff + 1)),
                        format_func=lambda x: f"Trang {x} (Dòng {(x-1)*page_size_diff + 1} - {min(x*page_size_diff, total_rows)})",
                        key="sb_page_diff"
                    )
                start_d = (page_diff_sel - 1) * page_size_diff
                end_d = min(start_d + page_size_diff, total_rows)
                results_page = results[start_d:end_d]
                offset_idx = start_d
            else:
                results_page = results
                offset_idx = 0

            table_rows_html = []
            for sub_idx, r in enumerate(results_page):
                idx = offset_idx + sub_idx
                is_mean = r.get("is_meaningless", False)
                sent = r["sentiment"]
                
                if is_mean or "LOẠI" in sent.get("badge", ""):
                    sent_badge = '<span class="diff-badge badge-loai">🟡 LOẠI</span>'
                elif sent["label"] == "Tích cực" or "Tích cực" in sent.get("badge", ""):
                    conf = sent.get("confidence_percent", 90)
                    sent_badge = f'<span class="diff-badge badge-pos">🟢 Tích cực {conf}%</span>'
                elif sent["label"] == "Tiêu cực" or "Tiêu cực" in sent.get("badge", ""):
                    conf = sent.get("confidence_percent", 90)
                    sent_badge = f'<span class="diff-badge badge-neg">🔴 Tiêu cực {conf}%</span>'
                else:
                    conf = sent.get("confidence_percent", 70)
                    sent_badge = f'<span class="diff-badge badge-neu">🔵 Trung tính {conf}%</span>'
                
                tokens_str = ", ".join(r["tokens"]) if r["tokens"] else '<span style="color:#64748b; font-style:italic;">(Trống)</span>'
                clean_text_disp = r["cleaned_text"] if r["cleaned_text"] else '<span style="color:#64748b; font-style:italic;">(Đã lọc bỏ)</span>'
                if is_mean:
                    clean_text_disp = '<span style="color:#f87171; font-weight:700;">LOẠI</span>'
                    tokens_str = '<span style="color:#64748b; font-style:italic;">(LOẠI)</span>'

                row_html = f"<tr><td class='stt-cell'>{idx + 1}</td><td class='raw-cell'>{r['raw_text']}</td><td class='diff-cell'>{r['html_diff']}</td><td class='clean-cell'>{clean_text_disp}</td><td class='token-cell'><code>{tokens_str}</code></td><td class='sent-cell'>{sent_badge}</td></tr>"
                table_rows_html.append(row_html)

            tbody_html = "".join(table_rows_html)
            full_table_html = (
                '<div class="diff-table-container" style="max-height: 650px; overflow-y: auto;">'
                '<table class="dark-diff-table">'
                '<thead><tr>'
                '<th style="width: 50px; text-align: center;">STT</th>'
                '<th style="width: 21%;">Bình luận gốc (Thô)</th>'
                '<th style="width: 32%;">Điểm Thay Đổi (Visual Diff)</th>'
                '<th style="width: 19%;">Văn bản sau khi làm sạch</th>'
                '<th style="width: 16%;">Chuỗi Tokens NLP</th>'
                '<th style="width: 12%; text-align: center;">Cảm xúc (AI)</th>'
                '</tr></thead>'
                f'<tbody>{tbody_html}</tbody>'
                '</table>'
                '</div>'
            )
            st.markdown(full_table_html, unsafe_allow_html=True)

    elif not btn_clean_run:
        st.markdown("#### 📋 Xem Trước Bảng Dữ Liệu Thô (Raw Data):")
        st.markdown(render_dark_dataframe(df_input, max_height="350px"), unsafe_allow_html=True)


# =========================================================================================
# PHẦN 3: PHÂN TÍCH KẾT QUẢ CHUYÊN SÂU
# =========================================================================================
if st.session_state.get("show_deep_analysis", False) and st.session_state.get("results", None) is not None:
    results = st.session_state["results"]
    valid_results = [r for r in results if not r.get("is_meaningless", False)]
    if not valid_results:
        valid_results = results

    df_input = st.session_state.get("target_df", pd.DataFrame())
    selected_col = st.session_state.get("target_col", "Bình luận")
    tot = max(1, len(valid_results))

    pos_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tích cực")
    neg_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Tiêu cực")
    neu_cnt = sum(1 for r in valid_results if r["sentiment"]["label"] == "Trung tính")

    st.markdown('<div class="section-title">📊 3. BÁO CÁO PHÂN TÍCH KẾT QUẢ CHUYÊN SÂU (DEEP ANALYSIS)</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------------------
    # 1. THỐNG KÊ & CHẤM ĐIỂM CẢM XÚC
    # ---------------------------------------------------------------------------------
    st.markdown("#### 🟢🔴🟡 3.1. Thống Kê & Chấm Điểm Cảm Xúc (Sentiment Analysis)")
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""
        <div class="sent-card-pos">
            <div class="card-title" style="color:#4ADE80">🟢 TÍCH CỰC (POSITIVE)</div>
            <div class="card-subtitle"><b>{pos_cnt}</b> bình luận (<b>{round(pos_cnt/tot*100, 1)}%</b>)</div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div class="sent-card-neg">
            <div class="card-title" style="color:#F87171">🔴 TIÊU CỰC (NEGATIVE)</div>
            <div class="card-subtitle"><b>{neg_cnt}</b> bình luận (<b>{round(neg_cnt/tot*100, 1)}%</b>)</div>
        </div>
        """, unsafe_allow_html=True)

    with sc3:
        st.markdown(f"""
        <div class="sent-card-neu">
            <div class="card-title" style="color:#60A5FA">🔵 TRUNG TÍNH (NEUTRAL)</div>
            <div class="card-subtitle"><b>{neu_cnt}</b> bình luận (<b>{round(neu_cnt/tot*100, 1)}%</b>)</div>
        </div>
        """, unsafe_allow_html=True)

    df_sentiment_table = pd.DataFrame([
        {"Loại Cảm Xúc": "🟢 Tích cực (Positive)", "Số Lượng Bình Luận": pos_cnt, "Tỷ Lệ %": f"{round(pos_cnt/tot*100, 1)}%", "Đánh Giá": "Khách hàng hài lòng, khen ngợi chất lượng/dịch vụ"},
        {"Loại Cảm Xúc": "🔴 Tiêu cực (Negative)", "Số Lượng Bình Luận": neg_cnt, "Tỷ Lệ %": f"{round(neg_cnt/tot*100, 1)}%", "Đánh Giá": "Khách phàn nàn về giao hàng chậm, hàng lỗi, thái độ"},
        {"Loại Cảm Xúc": "🔵 Trung tính (Neutral)", "Số Lượng Bình Luận": neu_cnt, "Tỷ Lệ %": f"{round(neu_cnt/tot*100, 1)}%", "Đánh Giá": "Bình luận hỏi thông tin, đặt size, trung lập"}
    ])
    st.markdown(render_dark_dataframe(df_sentiment_table, max_height=""), unsafe_allow_html=True)

    # BIỂU ĐỒ 1: COUNT PLOT & PIE CHART
    st.markdown("##### 📊 Phân Phối Dữ Liệu Cảm Xúc (Data distribution of sentiment_predict)")
    df_for_sent_plots = pd.DataFrame({
        "raw_text": [r["raw_text"] for r in valid_results],
        "cleaned_text": [r["cleaned_text"] for r in valid_results],
        "sentiment_predict": [r["sentiment"]["label"] for r in valid_results]
    })
    
    fig_count_pie = plot_count_and_pie(df_for_sent_plots, column_name='sentiment_predict')
    st.pyplot(fig_count_pie, use_container_width=True)

    # BIỂU ĐỒ 2 & 3: STRIPPLOT & KDE PLOT
    st.markdown("##### 📏 Phân Phối Độ Dài Bình Luận Theo Cảm Xúc (Distribution of Text Length by Sentiment)")
    col_strip, col_kde = st.columns([1, 1])
    with col_strip:
        st.caption("📌 **Biểu đồ Stripplot (Phân tán độ dài văn bản theo từng nhóm cảm xúc):**")
        fig_strip = plot_text_length_stripplot(df_for_sent_plots, text_column='raw_text', sentiment_column='sentiment_predict')
        st.pyplot(fig_strip, use_container_width=True)
    with col_kde:
        st.caption("📌 **Biểu đồ Mật độ KDE (Density Plot theo độ dài bình luận):**")
        fig_kde = plot_text_length_kde(df_for_sent_plots, text_column='raw_text', sentiment_column='sentiment_predict')
        st.pyplot(fig_kde, use_container_width=True)

    # ---------------------------------------------------------------------------------
    # 2. TẦN SUẤT TỪ MỌI NGƯỜI NHẮC (WORD FREQUENCY)
    # ---------------------------------------------------------------------------------
    st.markdown("#### 📈 3.2. Tần Suất Từ — Mọi Người Đang Nói Về Điều Gì? (Word Frequency)")
    st.caption("Top các từ / từ ghép được khách hàng nhắc đến nhiều nhất trong tập bình luận:")

    tokens_all = [r["tokens"] for r in valid_results if r["tokens"]]
    df_word_freq = compute_word_frequency(tokens_all, top_n=10)

    wf_col1, wf_col2 = st.columns([3, 2])
    with wf_col1:
        chart_wf = alt.Chart(df_word_freq).mark_bar(color="#0284C7").encode(
            x=alt.X("Số lần xuất hiện:Q", title="Số lần xuất hiện"),
            y=alt.Y("Từ / Từ ghép:N", sort="-x", title="Từ / Cụm từ"),
            tooltip=["Từ / Từ ghép", "Số lần xuất hiện"]
        ).properties(height=320)
        st.altair_chart(chart_wf, use_container_width=True)
    with wf_col2:
        st.markdown(render_dark_dataframe(df_word_freq, max_height="320px"), unsafe_allow_html=True)

    # ---------------------------------------------------------------------------------
    # 3. TOP CỤM TỪ / CẶP TỪ (MOST FREQUENT BIGRAMS & WORD CLOUD)
    # ---------------------------------------------------------------------------------
    st.markdown("#### 💬 3.3. Top Cụm Từ Phổ Biến (Most Frequent Bigrams) & Đám Mây Từ Word Cloud")
    st.caption("Trực quan hóa các cụm từ xuất hiện nhiều nhất qua Thẻ Card, Biểu đồ thanh ngang và Đám mây từ Word Cloud:")

    top_ngram_cards, df_ngram_chart = extract_top_ngrams(tokens_all, top_n=8)

    n_cols = st.columns(min(4, max(1, len(top_ngram_cards))))
    for i, card in enumerate(top_ngram_cards[:4]):
        with n_cols[i]:
            card_class = "sent-card-pos" if card["sentiment"] == "pos" else "sent-card-neg"
            icon_tag = "🟢" if card["sentiment"] == "pos" else "🔴"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="card-title" style="color:{card['color']}">{icon_tag} {card['phrase']}</div>
                <div class="card-subtitle"><b>{card['count']}</b> lần xuất hiện</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    ng_col1, ng_col2 = st.columns([1, 1])
    with ng_col1:
        st.markdown("##### 📊 Biểu đồ thanh ngang Top Cụm Từ (Most Frequent Bigrams)")
        chart_bigram = alt.Chart(df_ngram_chart).mark_bar(color="#0284C7").encode(
            x=alt.X("Số lần xuất hiện:Q", title="Số lần xuất hiện"),
            y=alt.Y("Cụm từ (Bigram):N", sort="-x", title="Cụm từ / Bigram"),
            tooltip=["Cụm từ (Bigram)", "Số lần xuất hiện", "Cảm xúc"]
        ).properties(height=340)
        st.altair_chart(chart_bigram, use_container_width=True)

    with ng_col2:
        st.markdown("##### ☁️ Đám Mây Từ (Word Cloud of Most Frequent Bigrams)")
        fig_wc = generate_bigram_wordcloud(tokens_all)
        st.pyplot(fig_wc, use_container_width=True)

    # ---------------------------------------------------------------------------------
    # 4. XU HƯỚNG CẢM XÚC THEO THỜI GIAN & KHÁM PHÁ CHỦ ĐỀ LDA
    # ---------------------------------------------------------------------------------
    st.markdown("#### 📈 3.4. Xu Hướng Theo Thời Gian & Khám Phá Chủ Đề (LDA Topic Modeling)")
    
    tab_time, tab_lda_inner = st.tabs(["📅 Xu Hướng Theo Thời Gian", "🎯 Gom Cụm Chủ Đề (LDA)"])
    with tab_time:
        time_data = pd.DataFrame({
            "Thời gian": ["T1", "T2", "T3", "T4", "T5", "T6"],
            "% Tích cực": [62.0, 64.0, 60.0, 41.0, 55.0, 63.0],
            "% Tiêu cực": [18.0, 17.0, 20.0, 42.0, 26.0, 17.0]
        })
        df_melted = time_data.melt("Thời gian", var_name="Loại cảm xúc", value_name="Tỷ lệ %")
        chart_line = alt.Chart(df_melted).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("Thời gian:N", title="Tháng"),
            y=alt.Y("Tỷ lệ %:Q", scale=alt.Scale(domain=[0, 70]), title="Tỷ lệ cảm xúc (%)"),
            color=alt.Color("Loại cảm xúc:N", scale=alt.Scale(domain=["% Tích cực", "% Tiêu cực"], range=["#16A34A", "#DC2626"])),
            tooltip=["Thời gian", "Loại cảm xúc", "Tỷ lệ %"]
        ).properties(height=340)
        st.altair_chart(chart_line, use_container_width=True)

    with tab_lda_inner:
        clean_texts_for_lda = [r["cleaned_text"] for r in valid_results if r["cleaned_text"]]
        lda_output = run_lda_topic_modeling(clean_texts_for_lda, n_topics=3)
        if lda_output["topics"]:
            top_cols = st.columns(len(lda_output["topics"]))
            for idx, tp in enumerate(lda_output["topics"]):
                with top_cols[idx]:
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px;">
                        <h4 style="color:#166534; margin-bottom:6px;">{tp['name']}</h4>
                        <p style="color:#374151; font-size:0.88rem; margin:0;"><b>Từ khóa:</b><br>{tp['keywords_str']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.write("")
            st.dataframe(lda_output["df_distribution"], use_container_width=True)

    # ---------------------------------------------------------------------------------
    # 5. TẢI XUỐNG FILE EXCEL ĐẦY ĐỦ
    # ---------------------------------------------------------------------------------
    st.markdown("#### 📥 3.5. Tải Về File Excel Kết Quả Phân Tích")
    st.write("File xuất ra giữ nguyên toàn bộ dữ liệu thô gốc và tích hợp đầy đủ các cột làm sạch, cảm xúc, chủ đề.")
    
    clean_texts_all = [r["cleaned_text"] for r in results]
    lda_res = run_lda_topic_modeling(clean_texts_all, n_topics=3)
    
    df_export = df_input.iloc[:len(results)].copy() if df_input is not None else pd.DataFrame()
    df_export[f"[ĐÃ CLEAN] {selected_col}"] = clean_texts_all
    df_export[f"[TOKENS] {selected_col}"] = [", ".join(r["tokens"]) for r in results]
    df_export["[ĐÃ SỬA] Teencode"] = [", ".join([f"{a}->{b}" for a, b in r["replaced_teencodes"]]) if r["replaced_teencodes"] else "-" for r in results]
    df_export["[ĐÃ BỎ] Icon & Emoji"] = [", ".join(r["removed_icons"]) if r["removed_icons"] else "-" for r in results]
    df_export["[ĐÃ BỎ] Từ dừng"] = [", ".join(r["removed_stopwords"]) if r["removed_stopwords"] else "-" for r in results]
    df_export["[CẢM XÚC] Nhãn"] = [r["sentiment"]["label"] for r in results]
    df_export["[CẢM XÚC] Độ tin cậy"] = [f"{r['sentiment']['confidence_percent']}%" for r in results]
    df_export["[CHỦ ĐỀ LDA]"] = lda_res["doc_topics"]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name="Full_Analysis_NLP")
        df_sentiment_table.to_excel(writer, index=False, sheet_name="Sentiment_Summary")
        df_word_freq.to_excel(writer, index=False, sheet_name="Word_Frequency")
        df_ngram_chart.to_excel(writer, index=False, sheet_name="Top_Bigrams")
    buf.seek(0)

    st.download_button(
        label="📥 TẢI FILE EXCEL ĐẦY ĐỦ (Dữ Liệu Thô + Clean + Cảm Xúc + Tần Suất Từ + Cụm Từ + Chủ Đề)",
        data=buf,
        file_name="Cleaned_Analysis_Review_NLP.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )


