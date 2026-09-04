"""
Module: sentiment_ai.py
Chức năng: Phân tích cảm xúc (Sentiment Analysis) sử dụng mô hình Local AI & Rule-based Lexicon tiếng Việt.
Quy định màu sắc:
- 🟢 Tích cực: Màu Xanh lá (Green)
- 🔴 Tiêu cực: Màu Đỏ (Red)
- 🟡 Trung tính: Màu Vàng (Yellow / Amber)
"""

import re
from typing import Dict, Any

POSITIVE_WORDS = {
    "tốt", "tuyệt", "tuyệt_vời", "xuất_sắc", "hài_lòng", "thích", "ưng_ý", "đẹp",
    "ổn", "ngon", "nhanh", "chuẩn", "chất_lượng", "dễ_thương", "thân_thiện", "nhiệt_tình",
    "cẩn_thận", "uy_tín", "chính_hãng", "mượt", "êm", "mát", "rẻ", "đáng_tiền", "khuyên_dùng",
    "đúng_mô_tả", "chu_đáo", "đỉnh", "quá_đẹp", "xịn", "ok", "oke", "tuyệt_hảo",
    "xịn_sò", "đáng_mua", "yêu_thích", "hài_lòng_nhất", "ủng_hộ", "thơm", "bền", "siêu_xinh",
    "xinh", "dth", "best", "tốt_nhất", "sạch_sẽ"
}

NEGATIVE_WORDS = {
    "tệ", "xấu", "kém", "kém_chất_lượng", "dở", "chậm", "thất_vọng", "lừa_đảo", "hàng_giả",
    "hàng_nhái", "hỏng", "vỡ", "nát", "rách", "bẩn", "hôi", "đắt", "chát", "phí_tiền",
    "không_đáng", "khó_chịu", "thái_độ", "bực_mình", "lởm", "dỏm", "chán", "nhạt_nhẽo",
    "lỗi", "sai_màu", "thiếu_hàng", "gian_lận", "ức_chế", "bực_bội", "tồi_tệ", "cực_tệ",
    "không_dùng_được", "vứt_đi", "khô", "cháy", "chua", "thiu", "nhạt", "hư_hỏng"
}

NEGATION_WORDS = {"không", "chẳng", "chưa", "đâu_có", "hổng", "k", "ko", "khong"}

SPECIAL_POSITIVE_PHRASES = [
    r"không\s+tệ", r"k\s+tệ", r"ko\s+tệ", r"không\s+chê", r"vượt\s+cả?\s*mong\s+đợi",
    r"không\s+thất\s+vọng", r"hơn\s+cả?\s*mong\s+đợi", r"ngoài\s+sức\s+tưởng\s+tượng"
]
SPECIAL_POSITIVE_REGEX = re.compile(r"|".join(SPECIAL_POSITIVE_PHRASES), re.IGNORECASE)

SPECIAL_NEGATIVE_PHRASES = [
    r"không\s+(tốt|đẹp|nhanh|ngon|ổn|thích|hài\s*lòng|đáng|xịn|mượt|chuẩn)",
    r"chẳng\s+(tốt|đẹp|nhanh|ngon|ổn|thích|hài\s*lòng|đáng)",
    r"chưa\s+(tốt|hài\s*lòng|ổn|đạt)"
]
SPECIAL_NEGATIVE_REGEX = re.compile(r"|".join(SPECIAL_NEGATIVE_PHRASES), re.IGNORECASE)


def analyze_sentiment(text: str, tokens: list = None) -> Dict[str, Any]:
    """
    Phân tích cảm xúc:
    - 🟢 Tích cực (Green)
    - 🔴 Tiêu cực (Red)
    - 🟡 Trung tính (Yellow)
    """
    if not text or not str(text).strip():
        return {
            "label": "Trung tính",
            "score": 0.50,
            "confidence_percent": 50,
            "color": "#D97706",
            "bg_color": "#FEF3C7",
            "border_color": "#FCD34D",
            "badge": "🟡 Trung tính - 50%"
        }

    text_lower = str(text).lower()

    if SPECIAL_POSITIVE_REGEX.search(text_lower):
        return {
            "label": "Tích cực",
            "score": 0.88,
            "confidence_percent": 88,
            "color": "#15803D",
            "bg_color": "#DCFCE7",
            "border_color": "#86EFAC",
            "badge": "🟢 Tích cực - 88%"
        }

    if SPECIAL_NEGATIVE_REGEX.search(text_lower):
        return {
            "label": "Tiêu cực",
            "score": 0.90,
            "confidence_percent": 90,
            "color": "#B91C1C",
            "bg_color": "#FEE2E2",
            "border_color": "#FCA5A5",
            "badge": "🔴 Tiêu cực - 90%"
        }

    all_words = text_lower.replace(",", " ").replace(".", " ").replace("!", " ").replace("?", " ").split()
    if tokens:
        all_words += [t.lower() for t in tokens]

    pos_score = 0
    neg_score = 0
    
    i = 0
    while i < len(all_words):
        w = all_words[i].strip("_")
        is_negated = False
        if i > 0 and all_words[i-1] in NEGATION_WORDS:
            is_negated = True
        
        if w in POSITIVE_WORDS or w.replace("_", " ") in POSITIVE_WORDS:
            if is_negated:
                neg_score += 1.5
            else:
                pos_score += 1.3
        elif w in NEGATIVE_WORDS or w.replace("_", " ") in NEGATIVE_WORDS:
            if is_negated:
                pos_score += 1.1
            else:
                neg_score += 1.5
        i += 1

    total = pos_score + neg_score
    if total == 0:
        return {
            "label": "Trung tính",
            "score": 0.85,
            "confidence_percent": 85,
            "color": "#D97706",
            "bg_color": "#FEF3C7",
            "border_color": "#FCD34D",
            "badge": "🟡 Trung tính - 85%"
        }

    if pos_score > neg_score:
        confidence = min(98, int(75 + (pos_score / (total + 0.1)) * 23))
        return {
            "label": "Tích cực",
            "score": round(confidence / 100, 2),
            "confidence_percent": confidence,
            "color": "#15803D",
            "bg_color": "#DCFCE7",
            "border_color": "#86EFAC",
            "badge": f"🟢 Tích cực - {confidence}%"
        }
    elif neg_score > pos_score:
        confidence = min(98, int(75 + (neg_score / (total + 0.1)) * 23))
        return {
            "label": "Tiêu cực",
            "score": round(confidence / 100, 2),
            "confidence_percent": confidence,
            "color": "#B91C1C",
            "bg_color": "#FEE2E2",
            "border_color": "#FCA5A5",
            "badge": f"🔴 Tiêu cực - {confidence}%"
        }
    else:
        return {
            "label": "Trung tính",
            "score": 0.70,
            "confidence_percent": 70,
            "color": "#D97706",
            "bg_color": "#FEF3C7",
            "border_color": "#FCD34D",
            "badge": "🟡 Trung tính - 70%"
        }


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_count_and_pie(df: pd.DataFrame, column_name: str = 'sentiment_predict', classes: list = None):
    """
    Vẽ 2 biểu đồ phân phối cảm xúc side-by-side chuẩn Dark Theme:
    - Count Plot: Bar chart thể hiện số lượng theo từng nhóm cảm xúc (Negative, Neutral, Positive)
    - Pie Chart: Biểu đồ tròn thể hiện tỷ lệ % (Positive, Negative, Neutral)
    Màu sắc: Negative (Đỏ), Positive (Xanh lá), Neutral (Xanh dương)
    """
    if classes is None:
        classes = ['Negative', 'Neutral', 'Positive']
    
    col_data = df[column_name].copy()
    label_map = {
        'Tích cực': 'Positive',
        'Tiêu cực': 'Negative',
        'Trung tính': 'Neutral',
        '🟢 Tích cực': 'Positive',
        '🔴 Tiêu cực': 'Negative',
        '🟡 Trung tính': 'Neutral'
    }
    col_data = col_data.replace(label_map)
    
    counts = col_data.value_counts()
    for c in classes:
        if c not in counts:
            counts[c] = 0
            
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='#0f172a')
    fig.suptitle('Data distribution of sentiment_predict', fontsize=14, fontweight='bold', color='#f8fafc', y=0.98)
    
    # Subplot 1: Count Plot
    x_labels = [c for c in ['Negative', 'Neutral', 'Positive'] if c in classes]
    if not x_labels:
        x_labels = list(counts.index)
    y_values = [counts.get(c, 0) for c in x_labels]
    
    color_map = {'Negative': '#DC2626', 'Positive': '#16A34A', 'Neutral': '#2563EB'}
    bar_colors = [color_map.get(c, '#2563EB') for c in x_labels]
    
    ax1.set_facecolor('#0f172a')
    ax1.bar(x_labels, y_values, color=bar_colors, width=0.6, edgecolor='#334155')
    ax1.set_title('Count Plot', fontsize=12, color='#38bdf8', fontweight='bold')
    ax1.set_xlabel('sentiment_predict', fontsize=10, color='#94a3b8')
    ax1.set_ylabel('Count', fontsize=10, color='#94a3b8')
    ax1.tick_params(colors='#e2e8f0')
    ax1.grid(axis='y', linestyle='--', alpha=0.25, color='#475569')
    for spine in ax1.spines.values():
        spine.set_color('#334155')
    
    # Subplot 2: Pie Chart
    pie_labels = ['Positive', 'Negative', 'Neutral']
    pie_counts = [counts.get(c, 0) for c in pie_labels]
    
    total_val = sum(pie_counts)
    if total_val == 0:
        pie_counts = [1, 1, 1]
    
    # Positive (Xanh lá), Negative (Đỏ), Neutral (Xanh dương)
    colors_pie = ['#16A34A', '#DC2626', '#2563EB']
    ax2.set_facecolor('#0f172a')
    wedges, texts, autotexts = ax2.pie(
        pie_counts, 
        labels=pie_labels, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors_pie,
        textprops={'fontsize': 10, 'color': '#f8fafc'},
        wedgeprops={'edgecolor': '#0f172a', 'linewidth': 2}
    )
    for at in autotexts:
        at.set_color('#ffffff')
        at.set_fontweight('bold')
    ax2.set_title('Pie Chart', fontsize=12, color='#38bdf8', fontweight='bold')
    legend = ax2.legend(pie_labels, loc="upper left", bbox_to_anchor=(-0.15, 1.0), facecolor='#1e293b', edgecolor='#334155')
    for text in legend.get_texts():
        text.set_color('#f8fafc')
    
    plt.tight_layout()
    return fig


def plot_text_length_stripplot(df: pd.DataFrame, text_column: str, sentiment_column: str = 'sentiment_predict'):
    """
    Biểu đồ Stripplot chuẩn Dark Theme:
    - Negative: Màu đỏ (#DC2626)
    - Positive: Màu xanh lá (#16A34A)
    - Neutral: Màu xanh dương (#2563EB)
    """
    df_plot = df.copy()
    label_map = {
        'Tích cực': 'Positive',
        'Tiêu cực': 'Negative',
        'Trung tính': 'Neutral',
        '🟢 Tích cực': 'Positive',
        '🔴 Tiêu cực': 'Negative',
        '🟡 Trung tính': 'Neutral'
    }
    df_plot[sentiment_column] = df_plot[sentiment_column].replace(label_map)
    df_plot['text_length'] = df_plot[text_column].apply(lambda x: len(str(x).split()))
    
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    order = ['Negative', 'Positive', 'Neutral']
    palette = {'Negative': '#DC2626', 'Positive': '#16A34A', 'Neutral': '#2563EB'}
    
    sns.stripplot(
        data=df_plot, 
        x=sentiment_column, 
        y='text_length', 
        hue=sentiment_column,
        legend=False,
        order=[o for o in order if o in df_plot[sentiment_column].unique()] or None,
        palette=palette, 
        alpha=0.65, 
        jitter=0.2, 
        size=7, 
        ax=ax
    )
    ax.set_title('Distribution of Text Length by Sentiment', fontsize=13, fontweight='bold', color='#f8fafc')
    ax.set_xlabel('sentiment_predict', fontsize=11, color='#94a3b8')
    ax.set_ylabel('text_length', fontsize=11, color='#94a3b8')
    ax.tick_params(colors='#e2e8f0')
    ax.grid(axis='y', linestyle='--', alpha=0.25, color='#475569')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    
    plt.tight_layout()
    return fig


def plot_text_length_kde(df: pd.DataFrame, text_column: str, sentiment_column: str = 'sentiment_predict'):
    """
    Biểu đồ phân phối mật độ KDE chuẩn Dark Theme:
    - Negative: Màu đỏ (#DC2626)
    - Positive: Màu xanh lá (#16A34A)
    - Neutral: Màu xanh dương (#2563EB)
    """
    df_plot = df.copy()
    label_map = {
        'Tích cực': 'Positive',
        'Tiêu cực': 'Negative',
        'Trung tính': 'Neutral',
        '🟢 Tích cực': 'Positive',
        '🔴 Tiêu cực': 'Negative',
        '🟡 Trung tính': 'Neutral'
    }
    df_plot[sentiment_column] = df_plot[sentiment_column].replace(label_map)
    df_plot['text_length'] = df_plot[text_column].apply(lambda x: len(str(x).split()))
    
    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    palette = {'Negative': '#DC2626', 'Positive': '#16A34A', 'Neutral': '#2563EB'}
    
    try:
        sns.kdeplot(
            data=df_plot, 
            x='text_length', 
            hue=sentiment_column, 
            fill=True, 
            common_norm=False, 
            palette=palette,
            ax=ax,
            warn_singular=False
        )
    except Exception:
        sns.histplot(
            data=df_plot, 
            x='text_length', 
            hue=sentiment_column, 
            kde=True, 
            fill=True, 
            palette=palette,
            ax=ax
        )
        
    ax.set_title('Distribution of Text Length by Sentiment', fontsize=13, fontweight='bold', color='#f8fafc')
    ax.set_xlabel('text_length', fontsize=11, color='#94a3b8')
    ax.set_ylabel('Density', fontsize=11, color='#94a3b8')
    ax.tick_params(colors='#e2e8f0')
    ax.grid(axis='y', linestyle='--', alpha=0.25, color='#475569')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    
    plt.tight_layout()
    return fig
