import os
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
        "created_at": "05/09/2026 00:30:00",
        "timestamp": 1788540000.0,
        "is_default": True
    },
    {
        "id": "RULE_002",
        "tag": "Nhận Diện Đa Ngôn Ngữ",
        "content": "Đối với review tiếng Hàn (như '별로', '그냥'), tiếng Nga, Trung, Pháp, Ý, Nhật, Anh... không được nhầm lẫn là ký tự đặc biệt vô nghĩa. Phải tự động nhận diện ngôn ngữ và dịch sang Tiếng Việt trước khi xử lý.",
        "created_at": "05/09/2026 00:35:00",
        "timestamp": 1788540300.0,
        "is_default": True
    },
    {
        "id": "RULE_003",
        "tag": "Sửa Teencode & Lỗi Chính Tả",
        "content": "Nhận diện các từ viết sai phổ biến nhưng dễ đoán (Ví dụ: 'L9cation' là 'Location' -> chuẩn hóa thành 'vị trí', 'tuỵt' -> 'tuyệt', 'qá' -> 'quá') trước khi tách từ NLP.",
        "created_at": "05/09/2026 00:40:00",
        "timestamp": 1788540600.0,
        "is_default": True
    }
]

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
    Tự động xử lý cú pháp tiền tố 'Dạy AI:' nếu người dùng gõ vào.
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
    elif any(k in c_lower for k in ["dịch", "tiếng", "hàn", "nga", "pháp", "ngôn ngữ"]):
        inferred_tag = "Nhận Diện Đa Ngôn Ngữ"
    elif any(k in c_lower for k in ["teencode", "chính tả", "viết sai", "sửa"]):
        inferred_tag = "Sửa Lỗi Chính Tả & Teencode"
    elif any(k in c_lower for k in ["cảm xúc", "tích cực", "tiêu cực", "trung tính"]):
        inferred_tag = "Phân Tích Cảm Xúc AI"

    new_rule = {
        "id": rule_id,
        "tag": inferred_tag,
        "content": cleaned_content,
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

def get_teaching_context_for_ai() -> str:
    """
    Tổng hợp toàn bộ kiến thức đã dạy thành chuỗi hướng dẫn để nhúng vào AI Context.
    """
    rules = load_teaching_memory()
    lines = ["Các quy tắc và kinh nghiệm mà người dùng đã dạy cho AI:"]
    for idx, r in enumerate(rules, 1):
        lines.append(f"{idx}. [{r.get('tag', 'Kinh nghiệm')}]: {r.get('content', '')}")
    return "\n".join(lines)
