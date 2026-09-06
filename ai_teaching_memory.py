import os
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Any

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "ai_learned_rules.json")

DEFAULT_RULES = [
    {
        "id": "RULE_001",
        "tag": "Lọc Review Vô Nghĩa",
        "content": "Đối với các dòng review cộc lốc, câu vô nghĩa hoặc sai chính tả nặng không hiểu được (Ví dụ: 'tắt mm app đi') -> Gán nhãn LOẠI và ghi rõ lý do loại bỏ ở Bước Lọc Review.",
        "contribution": "🎯 Lọc sạch dữ liệu rác & lỗi thao tác ứng dụng; ngăn ngừa làm loãng tập dữ liệu phân tích, giúp tỷ lệ cảm xúc và mô hình chủ đề LDA phản ánh chính xác 100% trải nghiệm thực tế.",
        "created_at": "05/09/2026 00:30:00",
        "timestamp": 1788540000.0,
        "is_default": True
    },
    {
        "id": "RULE_002",
        "tag": "Nhận Diện Đa Ngôn Ngữ",
        "content": "Đối với review tiếng Hàn (như '별로', '그냥'), tiếng Nga, Trung, Pháp, Ý, Nhật, Anh... không được nhầm lẫn là ký tự đặc biệt vô nghĩa. Phải tự động nhận diện ngôn ngữ và dịch sang Tiếng Việt trước khi xử lý.",
        "contribution": "🌐 Mở rộng độ phủ quốc tế của Tool; bảo toàn trọn vẹn ý kiến của du khách nước ngoài thay vì loại nhầm, giúp doanh nghiệp nắm bắt toàn diện chân dung khách hàng toàn cầu.",
        "created_at": "05/09/2026 00:35:00",
        "timestamp": 1788540300.0,
        "is_default": True
    },
    {
        "id": "RULE_003",
        "tag": "Sửa Teencode & Lỗi Chính Tả",
        "content": "Nhận diện các từ viết sai phổ biến nhưng dễ đoán (Ví dụ: 'L9cation' là 'Location' -> chuẩn hóa thành 'vị trí', 'tuỵt' -> 'tuyệt', 'qá' -> 'quá') trước khi tách từ NLP.",
        "contribution": "⚡ Chuẩn hóa ngôn ngữ mạng & lỗi gõ phím về từ điển chuẩn tiếng Việt; giúp thư viện underthesea tách chính xác từ ghép (Bi-grams/Tri-grams) và trích xuất đúng tần suất từ khóa.",
        "created_at": "05/09/2026 00:40:00",
        "timestamp": 1788540600.0,
        "is_default": True
    }
]

def analyze_contribution(content: str, tag: str) -> str:
    """
    AI tự động phân tích và đánh giá đóng góp của bài học/quy tắc này vào việc cải tiến Tool.
    """
    c_lower = content.lower()
    
    if tag == "Lọc Review Vô Nghĩa" or any(k in c_lower for k in ["loại", "vô nghĩa", "rác", "spam", "cộc lốc"]):
        return f"🎯 Giúp bộ lọc tiền xử lý loại trừ chính xác các mẫu đánh giá rác/không có ý nghĩa kinh doanh, bảo toàn tính trung thực và độ tin cậy của tập mẫu nghiên cứu."
    
    elif "ghép" in c_lower or "cụm" in c_lower or "_" in content or tag == "Tách Từ Ghép & NLP":
        return f"🧩 Nhận diện cụm từ ghép có nghĩa trong ngữ cảnh đánh giá; gắn kết các từ đơn thành cụm liền mạch (N-Grams), ngăn ngừa tình trạng tách rời làm biến đổi hoặc mất mát ngữ nghĩa gốc."

    elif tag == "Nhận Diện Đa Ngôn Ngữ" or any(k in c_lower for k in ["tiếng", "dịch", "hàn", "nga", "pháp", "trung", "ngoại ngữ"]):
        return f"🌐 Tối ưu hóa pipeline dịch thuật đa ngữ tự động; đảm bảo không bỏ sót ý kiến của khách hàng quốc tế, chuyển hóa trơn tru về ngữ nghĩa Tiếng Việt trước khi chạy NLP."
    
    elif tag == "Sửa Lỗi Chính Tả & Teencode" or any(k in c_lower for k in ["teencode", "chính tả", "viết tắt", "sửa lỗi", "chuẩn hóa"]):
        return f"⚡ Bổ sung tri thức từ vựng mới vào từ điển Teencode; giúp khôi phục đúng ngữ nghĩa gốc của từ ngữ và nâng cao độ chính xác khi trích xuất cụm từ (N-Grams)."
    
    elif tag == "Phân Tích Cảm Xúc AI" or any(k in c_lower for k in ["cảm xúc", "tích cực", "tiêu cực", "trung tính", "khen", "chê"]):
        return f"💡 Tinh chỉnh độ nhạy của bộ chấm điểm cảm xúc (Sentiment AI); nhận diện chính xác các sắc thái đánh giá tinh tế, giảm tỷ lệ phân loại sai giữa Tích cực và Tiêu cực."
    
    elif any(k in c_lower for k in ["stopwords", "từ dừng", "loại bỏ từ"]):
        return f"🚫 Mở rộng danh mục từ dừng ngữ cảnh đặc thù; triệt tiêu các từ vô thưởng vô phạt để tập trung vào các từ khóa mang lại giá trị phân tích marketing cao nhất."
    
    else:
        return f"🚀 Nâng cao khả năng thích ứng linh hoạt của hệ thống; ghi nhớ kinh nghiệm người dùng để liên tục tối ưu hóa quy trình tiền xử lý văn bản theo bài toán thực tế."

def load_teaching_memory() -> List[Dict[str, Any]]:
    """
    Tải danh sách các quy tắc mà người dùng đã dạy cho AI.
    """
    if not os.path.exists(MEMORY_FILE):
        save_all_rules(DEFAULT_RULES)
        return DEFAULT_RULES

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                # Đảm bảo mỗi rule đều có trường contribution
                for r in data:
                    if "contribution" not in r or not r["contribution"]:
                        r["contribution"] = analyze_contribution(r.get("content", ""), r.get("tag", "Tùy Chỉnh"))
                return data
            else:
                save_all_rules(DEFAULT_RULES)
                return DEFAULT_RULES
    except Exception:
        return DEFAULT_RULES

def save_all_rules(rules: List[Dict[str, Any]]) -> None:
    """
    Lưu toàn bộ danh sách quy tắc vào file JSON.
    """
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

def add_teaching_rule(content: str, tag: str = "Tùy Chỉnh") -> Dict[str, Any]:
    """
    Thêm một bài học mới vào bộ nhớ của AI.
    Tự động xử lý cú pháp tiền tố 'Dạy AI:' nếu người dùng gõ vào và phân tích đóng góp.
    """
    cleaned_content = content.strip()
    # Tự động loại bỏ tiền tố Dạy AI: nếu có
    if cleaned_content.lower().startswith("dạy ai:"):
        cleaned_content = cleaned_content[7:].strip()
    elif cleaned_content.lower().startswith("day ai:"):
        cleaned_content = cleaned_content[7:].strip()

    now = datetime.now()
    rule_id = f"RULE_{now.strftime('%Y%m%d_%H%M%S')}"

    # Tự động suy luận Tag nếu chưa có
    inferred_tag = tag
    c_lower = cleaned_content.lower()
    if any(k in c_lower for k in ["loại", "vô nghĩa", "không có ý nghĩa", "cộc lốc"]):
        inferred_tag = "Lọc Review Vô Nghĩa"
    elif any(k in c_lower for k in ["từ ghép", "ghép", "cụm từ", "thành 1 cụm", "thành cụm"]):
        inferred_tag = "Tách Từ Ghép & NLP"
    elif any(k in c_lower for k in ["dịch", "tiếng", "hàn", "nga", "pháp", "ngôn ngữ"]):
        inferred_tag = "Nhận Diện Đa Ngôn Ngữ"
    elif any(k in c_lower for k in ["teencode", "chính tả", "viết sai", "sửa", "viết tắt"]):
        inferred_tag = "Sửa Lỗi Chính Tả & Teencode"
    elif any(k in c_lower for k in ["cảm xúc", "tích cực", "tiêu cực", "trung tính"]):
        inferred_tag = "Phân Tích Cảm Xúc AI"

    # AI Tự động phân tích đóng góp của bài học này
    contribution_text = analyze_contribution(cleaned_content, inferred_tag)

    new_rule = {
        "id": rule_id,
        "tag": inferred_tag,
        "content": cleaned_content,
        "contribution": contribution_text,
        "created_at": now.strftime("%d/%m/%Y %H:%M:%S"),
        "timestamp": time.time(),
        "is_default": False
    }

    rules = load_teaching_memory()
    # Thêm vào đầu danh sách (mới nhất lên trước)
    rules.insert(0, new_rule)
    save_all_rules(rules)
    return new_rule

def delete_teaching_rule(rule_id: str) -> bool:
    """
    Xóa một quy tắc trong bộ nhớ của AI.
    """
    rules = load_teaching_memory()
    filtered = [r for r in rules if r.get("id") != rule_id]
    if len(filtered) < len(rules):
        save_all_rules(filtered)
        return True
    return False

def extract_rule_actions_with_ai(content: str, tag: str) -> Dict[str, Any]:
    """
    Sử dụng AI logic / NLP reasoning để bóc tách tri thức từ văn bản tự nhiên của người dùng
    thành các hành động cụ thể có thể áp dụng trực tiếp vào pipeline:
    - compounds: cụm từ ghép cần nối _ (ví dụ: 'không tươi' -> 'không_tươi', 'gà rán' -> 'gà_rán')
    - teencode_mappings: từ viết tắt / chính tả cần sửa (ví dụ: 'k ngon' -> 'không ngon')
    - custom_stopwords: từ dừng bổ sung
    - meaningless_patterns: mẫu câu rác cần loại bỏ
    - sentiment_overrides: điều chỉnh cảm xúc (tích cực, tiêu cực)
    """
    c_raw = content.strip()
    c_lower = c_raw.lower()
    
    actions = {
        "compounds": [],
        "teencode_mappings": {},
        "custom_stopwords": [],
        "meaningless_patterns": [],
        "sentiment_words": {"positive": [], "negative": []}
    }

    # 1. Trích xuất cụm từ ghép (Compound words)
    # Ví dụ: "các từ như không tươi là từ ghép..." hoặc "...thành 1 cụm Không_tươi"
    # Match các từ ghép được trỏ đích danh sau "từ như...", "từ...", "cụm..."
    direct_compound_matches = re.findall(r'(?:như|từ|cụm|ghép)\s+([a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]{3,25}?)\s+(?:là|thành|phải|đứng)', c_raw, re.IGNORECASE)
    for dm in direct_compound_matches:
        dm_clean = dm.strip().lower()
        if " " in dm_clean and len(dm_clean.split()) <= 4:
            compound_ver = dm_clean.replace(" ", "_")
            if (dm_clean, compound_ver) not in actions["compounds"]:
                actions["compounds"].append((dm_clean, compound_ver))

    quoted_phrases = re.findall(r'["\'„”«»](.*?)["\'„”«»]', c_raw)
    
    # Tìm các cặp từ có _ được đề cập (ví dụ không_tươi, không_ngon, Không_tươi)
    underscore_terms = re.findall(r'\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+_[a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ_]+\b', c_raw, re.IGNORECASE)
    for u in underscore_terms:
        orig_phrase = u.replace("_", " ").lower()
        target_compound = u.lower()
        if (orig_phrase, target_compound) not in actions["compounds"]:
            actions["compounds"].append((orig_phrase, target_compound))

    # Phân tích theo ngữ cảnh nếu người dùng nói từ ghép
    if "từ ghép" in c_lower or "cụm" in c_lower:
        for qp in quoted_phrases:
            qp_clean = qp.strip().lower()
            if " " in qp_clean and len(qp_clean.split()) <= 4:
                compound_ver = qp_clean.replace(" ", "_")
                if (qp_clean, compound_ver) not in actions["compounds"]:
                    actions["compounds"].append((qp_clean, compound_ver))

    # 2. Trích xuất quy tắc Sửa Teencode / Chính Tả (A thành B, A là B, A -> B)
    # Regex tìm: 'a' -> 'b' hoặc 'a' là 'b' hoặc 'a' thành 'b'
    arrow_matches = re.findall(r'["\']?([\w\s]+)["\']?\s*(?:->|➔|=>|thành|là)\s*["\']?([\w\s]+)["\']?', c_raw, re.IGNORECASE)
    for src, dst in arrow_matches:
        src_c = src.strip().lower()
        dst_c = dst.strip().lower()
        if src_c and dst_c and src_c != dst_c and len(src_c.split()) <= 3:
            # Bỏ qua các từ khóa câu
            if not any(k in src_c for k in ["bước", "stt", "đóng góp", "quy tắc", "nội dung"]):
                actions["teencode_mappings"][src_c] = dst_c

    # 3. Trích xuất quy tắc Lọc Review Vô Nghĩa / Rác
    if any(k in c_lower for k in ["loại", "vô nghĩa", "rác", "spam", "cộc lốc"]):
        for qp in quoted_phrases:
            qp_clean = qp.strip().lower()
            if len(qp_clean) >= 2 and not any(k in qp_clean for k in ["loại", "vô nghĩa", "không_tươi"]):
                actions["meaningless_patterns"].append(qp_clean)

    # 4. Trích xuất Cảm xúc
    if any(k in c_lower for k in ["tiêu cực", "chê", "xấu", "tệ"]):
        for qp in quoted_phrases:
            qp_clean = qp.strip().lower()
            if qp_clean and len(qp_clean.split()) <= 3:
                actions["sentiment_words"]["negative"].append(qp_clean)
                actions["sentiment_words"]["negative"].append(qp_clean.replace(" ", "_"))
    if any(k in c_lower for k in ["tích cực", "khen", "tốt", "ngon", "đẹp"]):
        for qp in quoted_phrases:
            qp_clean = qp.strip().lower()
            if qp_clean and len(qp_clean.split()) <= 3:
                actions["sentiment_words"]["positive"].append(qp_clean)
                actions["sentiment_words"]["positive"].append(qp_clean.replace(" ", "_"))

    return actions

def get_active_learned_actions() -> Dict[str, Any]:
    """
    Tổng hợp toàn bộ các hành động thực thi từ mọi quy tắc đã học.
    Được gọi trực tiếp trong text_cleaner.py và sentiment_ai.py để áp dụng ngay lập tức vào Tool!
    """
    rules = load_teaching_memory()
    combined_compounds = []
    combined_teencode = {}
    combined_stopwords = set()
    combined_meaningless = []
    combined_pos = set()
    combined_neg = set()

    for r in rules:
        content = r.get("content", "")
        tag = r.get("tag", "")
        actions = extract_rule_actions_with_ai(content, tag)
        
        for c in actions.get("compounds", []):
            if c not in combined_compounds:
                combined_compounds.append(c)
                
        combined_teencode.update(actions.get("teencode_mappings", {}))
        combined_stopwords.update(actions.get("custom_stopwords", []))
        
        for m in actions.get("meaningless_patterns", []):
            if m not in combined_meaningless:
                combined_meaningless.append(m)
                
        combined_pos.update(actions.get("sentiment_words", {}).get("positive", []))
        combined_neg.update(actions.get("sentiment_words", {}).get("negative", []))

    return {
        "compounds": combined_compounds,
        "teencode": combined_teencode,
        "stopwords": combined_stopwords,
        "meaningless_patterns": combined_meaningless,
        "positive_words": combined_pos,
        "negative_words": combined_neg
    }

def get_teaching_context_for_ai() -> str:
    """
    Tổng hợp toàn bộ kiến thức đã dạy thành chuỗi hướng dẫn để nhúng vào AI Context.
    """
    rules = load_teaching_memory()
    lines = ["Các quy tắc và kinh nghiệm mà người dùng đã dạy cho AI:"]
    for idx, r in enumerate(rules, 1):
        lines.append(f"{idx}. [{r.get('tag', 'Kinh nghiệm')}]: {r.get('content', '')} (Đóng góp: {r.get('contribution', '')})")
    return "\n".join(lines)

