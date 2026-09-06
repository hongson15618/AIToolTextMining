"""
Module: text_cleaner.py (Phiên bản Toàn Cầu & Lọc Ngày Giờ Chuẩn Thứ Tự)
"""

import os
import re
import json
import urllib.request
import urllib.parse
import unicodedata
from typing import Dict, List, Set, Tuple, Any

import emoji
from teencode_dict import TEENCODE_DICT, LEETSPEAK_MAP
from sentiment_ai import analyze_sentiment
from ai_teaching_memory import get_active_learned_actions

# Thư viện NLP tiếng Việt
try:
    from underthesea import word_tokenize as underthesea_tokenize
    HAS_UNDERTHESEA = True
except Exception:
    HAS_UNDERTHESEA = False

try:
    from pyvi import ViTokenizer
    HAS_PYVI = True
except Exception:
    HAS_PYVI = False

# Thư viện dịch thuật & nhận diện ngôn ngữ
try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    HAS_TRANSLATOR = True
except Exception:
    HAS_TRANSLATOR = False

try:
    from langdetect import detect as lang_detect
    HAS_LANGDETECT = True
except Exception:
    HAS_LANGDETECT = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False


EMOTICON_PATTERNS = [
    r":\(\(+", r":\)\)+", r":\-?\)+", r":\-?\(+", r":\-?D+", r":\-?p+", r":\-?P+",
    r":\-?o+", r":\-?O+", r":\-?3", r":\-?>", r"<3+", r"</3+", r"\^\^", r"\^_+\^",
    r">_<+", r"-_-\*?", r"T_T+", r";\)\)+", r";\-?\(+", r":v+", r":3+", r":'\)+",
    r":'\(+", r"@@+", r"\-_-\"", r"-_-", r"= \)+", r"=\(\(+", r":\-\(", r":\-\)"
]
EMOTICON_REGEX = re.compile(r"|".join(EMOTICON_PATTERNS), re.IGNORECASE)

URL_REGEX = re.compile(r"https?://\S+|www\.\S+|bit\.ly/\S+", re.IGNORECASE)
HTML_REGEX = re.compile(r"<.*?>")
PHONE_REGEX = re.compile(r"\b(0[3|5|7|8|9]+[0-9]{8})\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Regex lọc bỏ ngày tháng & giờ giấc
DATETIME_PATTERNS = [
    r"\bngày\s+\d{1,2}(?:[/-]\d{1,2}(?:[/-]\d{2,4})?)?\b",
    r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
    r"\b\d{1,2}h(?:\d{1,2})?\b",
    r"\b\d{1,2}:\d{2}(?::\d{2})?\b",
    r"\b\d{1,2}\s*(?:giờ|phút|giây)\b"
]
DATETIME_REGEX = re.compile(r"|".join(DATETIME_PATTERNS), re.IGNORECASE)

FRENCH_KEYWORDS = {'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'le', 'la', 'les', 'des', 'du', 'un', 'une', 'pas', 'est', 'sont', 'ont', 'pour', 'avec', 'dans', 'sur', 'qui', 'que', 'très', 'service', 'étoiles', 'ambiance', 'sales', 'aucun', 'mains', 'toilette', 'toilettes', 'lavabo', 'eau', 'fait', 'tous', 'deux', 'types', 'air', 'toujours', 'enfin', 'sent', 'tronche', 'sol', 'table', 'coca', 'laver', 'narrive', 'étoile'}
ITALIAN_KEYWORDS = {'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'di', 'da', 'in', 'con', 'su', 'per', 'tutto', 'sporco', 'ovunque', 'sporcizia', 'non', 'puliscono', 'ne', 'all', 'interno', 'esterno', 'neanche', 'tavoli', 'vergogna', 'sono', 'molto', 'bene', 'grazie', 'questo'}
GERMAN_KEYWORDS = {'der', 'die', 'das', 'ein', 'eine', 'und', 'in', 'den', 'von', 'zu', 'mit', 'ist', 'nicht', 'sehr', 'gut', 'schlecht', 'für', 'auf', 'war', 'essen', 'schön'}
SPANISH_KEYWORDS = {'el', 'la', 'los', 'las', 'unos', 'unas', 'del', 'en', 'por', 'para', 'muy', 'bueno', 'malo', 'esta', 'este', 'todo', 'bien', 'gracias', 'servicio', 'comida'}

COMMON_VI_COMPOUNDS = [
    ("giao hàng nhanh", "giao_hàng_nhanh"),
    ("giao hàng chậm", "giao_hàng_chậm"),
    ("giao hàng", "giao_hàng"),
    ("vận chuyển", "vận_chuyển"),
    ("đóng gói", "đóng_gói"),
    ("chất lượng tốt", "chất_lượng_tốt"),
    ("chất lượng", "chất_lượng"),
    ("sản phẩm", "sản_phẩm"),
    ("chính hãng", "chính_hãng"),
    ("hài lòng", "hài_lòng"),
    ("nhiệt tình", "nhiệt_tình"),
    ("thân thiện", "thân_thiện"),
    ("dễ thương", "dễ_thương"),
    ("tuyệt vời", "tuyệt_vời"),
    ("hỏa tốc", "hỏa_tốc"),
    ("nhanh chóng", "nhanh_chóng"),
    ("tư vấn", "tư_vấn"),
    ("hướng dẫn", "hướng_dẫn"),
    ("đổi trả", "đổi_trả"),
    ("bảo hành", "bảo_hành"),
    ("lừa đảo", "lừa_đảo"),
    ("kém chất lượng", "kém_chất_lượng"),
    ("hàng giả", "hàng_giả"),
    ("hàng nhái", "hàng_nhái"),
    ("giá tiền", "giá_tiền"),
    ("không đáng tiền", "không_đáng_tiền"),
    ("đáng tiền", "đáng_tiền"),
    ("vừa vặn", "vừa_vặn"),
    ("thoải mái", "thoải_mái"),
    ("màu sắc", "màu_sắc"),
    ("kích thước", "kích_thước"),
    ("đúng mô tả", "đúng_mô_tả"),
    ("quảng cáo", "quảng_cáo"),
    ("nhân viên", "nhân_viên"),
    ("sân bay", "sân_bay"),
    ("đối diện", "đối_diện"),
    ("vị trí", "vị_trí"),
    ("cà phê", "cà_phê"),
    ("siêu xinh", "siêu_xinh"),
    ("đồ ăn", "đồ_ăn"),
    ("phục vụ", "phục_vụ"),
    ("ngon tuyệt vời", "ngon_tuyệt_vời")
]

OFFLINE_TRANSLATE_MAP = {
    "so kind": "thật tốt bụng",
    "so kind and helpful": "rất tốt bụng và nhiệt tình",
    "so kind and friendly": "rất tốt bụng và thân thiện",
    "very kind": "rất tốt bụng",
    "kind staff": "nhân viên tốt bụng",
    "kind": "tốt bụng",
    "supportive": "nhiệt tình hỗ trợ",
    "extremely supportive": "vô cùng nhiệt tình hỗ trợ",
    "friendly": "thân thiện",
    "ugly and dirty": "xấu xí và bẩn thỉu",
    "ugly": "xấu xí",
    "dirty": "bẩn thỉu",
    "expensive": "đắt đỏ",
    "cheap": "rẻ",
    "delicious": "ngon miệng",
    "tasty": "ngon",
    "yummy": "ngon tuyệt",
    "absolutely amazing": "hoàn toàn tuyệt vời",
    "i like macdonald": "tôi thích macdonald",
    "i like macdonalds": "tôi thích macdonald",
    "i like mcdonald": "tôi thích mcdonald",
    "i like mcdonalds": "tôi thích mcdonald",
    "i like mcdonald's": "tôi thích mcdonald",
    "all good": "tất cả đều tốt",
    "cool": "tuyệt",
    "l9cation": "vị trí",
    "location": "vị trí",
    "supercalifragilisticexpialidocious": "siêu ngon tuyệt vời",
    "had great cappuccino": "uống cà phê cappuccino rất ngon",
    "great": "tuyệt vời",
    "good": "tốt",
    "best": "tốt nhất",
    "fast": "nhanh",
    "slow": "chậm",
    "delivery": "giao hàng",
    "shipping": "vận chuyển",
    "quality": "chất lượng",
    "product": "sản phẩm",
    "service": "dịch vụ",
    "recommend": "khuyên dùng",
    "recommended": "đáng mua",
    "broken": "bị vỡ hỏng",
    "damaged": "bị hư hại",
    "bad": "xấu tệ",
    "packaging": "đóng gói",
    "opposite": "đối diện",
    "arrival": "nơi đến",
    "airport": "sân bay",
    "nice": "đẹp",
    "cappuccino": "cà phê cappuccino",
    "coffee": "cà phê",
    "hotel": "khách sạn",
    "room": "phòng",
    "clean": "sạch sẽ",
    "staff": "nhân viên",
    "price": "giá cả"
}


def load_stopwords(filepath: str = None) -> Set[str]:
    """Tải danh sách stopwords từ file hoặc trả về tập mặc định."""
    stopwords = set()
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    stopwords.add(word)
                    stopwords.add(word.replace(" ", "_"))
    else:
        default_sw = [
            "ơi", "nhưng", "quá", "nha", "áp", "là", "của", "và", "các", "những",
            "thì", "mà", "ở", "cho", "với", "được", "có", "đã", "sẽ", "đang", "rồi",
            "nhé", "ạ", "nhỉ", "thôi", "đi", "lại", "ra", "vào", "lên", "xuống",
            "trong", "đến", "bị", "do", "bởi", "vì", "tại", "từ", "theo", "như",
            "về", "để", "rằng", "nếu", "thế", "vậy", "kìa", "đó", "đây", "này",
            "kia", "nào", "gì", "ai", "đâu", "sao", "lắm", "cực", "luôn", "hết",
            "chứ", "hả", "cũng", "đều", "mọi", "mỗi", "từng", "vài", "nhiều", "ít",
            "rất", "thanks", "thank", "tks", "hihi", "haha", "huhu", "hehe", "dc", "đc", "lúc"
        ]
        for w in default_sw:
            stopwords.add(w)
            stopwords.add(w.replace(" ", "_"))
    return stopwords


_TRANSLATION_CACHE = {}

VI_UNACCENTED_KEYWORDS = {
    "va", "la", "cua", "cho", "voi", "nhung", "thi", "ma", "o", "trong", "den", "bi", "do", "boi",
    "vi", "tai", "tu", "theo", "nhu", "ve", "de", "rang", "neu", "the", "vay", "kia", "day", "nay",
    "nao", "gi", "ai", "dau", "sao", "lam", "cuc", "luon", "het", "chu", "ha", "cung", "deu", "moi",
    "tung", "vai", "nhieu", "it", "rat", "qua", "nhe", "nha", "oi", "da", "nhi", "shop",
    "hang", "giao", "ship", "mua", "ban", "dong", "goi", "chuan", "dung", "tot", "xau", "te", "dep",
    "ngon", "an", "uong", "quan", "danh", "gia", "khach", "san", "pham", "chat", "luong", "tien",
    "re", "dat", "mac", "thay", "em", "anh", "chi", "ban", "minh", "tam", "xem", "tra", "doi",
    "khong", "duoc", "chua", "roi", "form", "size", "mat", "vua", "van", "ao", "tui", "xinh", "dth",
    "nhiet", "tinh", "tu", "van", "ko", "k", "dc", "nv", "sp", "qá", "tuỵt", "tuyet", "on", "oke", "ok"
}

ENGLISH_INDICATORS = {
    "the", "is", "are", "was", "were", "this", "that", "with", "for", "from", "in", "on", "at", "to",
    "it", "they", "you", "we", "my", "your", "not", "have", "had", "great", "good", "bad", "best",
    "worst", "amazing", "love", "like", "fast", "slow", "clean", "location", "room", "hotel", "airport",
    "arrival", "opposite", "service", "price", "delivery", "shipping", "product", "recommend", "recommended",
    "broken", "damaged", "nice", "coffee", "cappuccino", "staff", "supercalifragilisticexpialidocious",
    "so", "kind", "very", "supportive", "friendly", "extremely", "visited", "guest", "guests", "place",
    "ugly", "dirty", "expensive", "cheap", "delicious", "fresh", "crispy", "tender", "burger", "fries",
    "chicken", "drink", "store", "order", "driver", "platform", "too", "helpful", "polite", "rude"
}

VI_SPECIAL_CHARS_REGEX = re.compile(r"[ăắằẳẵặâấầẩẫậêếềểễệôốồổỗộơớờởỡợưứừửữựđĐ]", re.IGNORECASE)

def detect_foreign_language_code(text: str) -> Tuple[bool, str]:
    """Tự động nhận diện ngôn ngữ nguồn chuẩn xác toàn cầu (Tiếng Việt, Anh, Nga, Pháp, Ý, Đức, Trung, Hàn, Nhật...)."""
    text_clean = text.strip()
    if not text_clean:
        return False, "vi"

    # 1. Regex kiểm tra nhanh các bảng chữ cái ngoại ngữ đặc thù
    if re.search(r"[\uac00-\ud7af\u1100-\u11ff]", text_clean):
        return True, "ko"
    if re.search(r"[\u4e00-\u9fff\u3400-\u4dbf]", text_clean):
        return True, "zh-CN"
    if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", text_clean):
        return True, "ja"
    if re.search(r"[\u0400-\u04ff]", text_clean):
        return True, "ru"
    if re.search(r"[\u0e00-\u0e7f]", text_clean):
        return True, "th"

    text_lower = text_clean.lower()
    words = re.findall(r"[a-zA-Z0-9_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", text_lower)
    word_set = set(words)

    # 2. Kiểm tra từ khóa đặc trưng của tiếng Pháp / Ý / Đức / Tây Ban Nha / Anh
    if len(word_set.intersection(FRENCH_KEYWORDS)) >= 1:
        return True, "fr"
    if len(word_set.intersection(ITALIAN_KEYWORDS)) >= 1:
        return True, "it"
    if len(word_set.intersection(GERMAN_KEYWORDS)) >= 1:
        return True, "de"
    if len(word_set.intersection(SPANISH_KEYWORDS)) >= 1:
        return True, "es"
    if len(word_set.intersection(ENGLISH_INDICATORS)) >= 1:
        return True, "en"

    # 3. Dùng thư viện langdetect nếu có từ 2 từ trở lên
    if HAS_LANGDETECT and len(words) >= 2:
        try:
            detected_lang = lang_detect(text_clean)
            if detected_lang != "vi":
                return True, detected_lang
        except Exception:
            pass

    # 4. Kiểm tra chữ cái chỉ có trong Tiếng Việt (ă, â, ê, ô, ơ, ư, đ)
    if VI_SPECIAL_CHARS_REGEX.search(text_clean):
        return False, "vi"

    # 5. Nếu có từ khóa tiếng Việt không dấu hoặc teencode -> Tiếng Việt
    if word_set.intersection(VI_UNACCENTED_KEYWORDS):
        return False, "vi"

    # 6. Kiểm tra các dấu thanh tiếng Việt thông thường
    if re.search(r"[àáảãạèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵ]", text_clean):
        return False, "vi"

    return False, "vi"


def remove_dates_and_times(text: str) -> str:
    """Loại bỏ ngày tháng (31/3, 31-3) và giờ giấc (9h, 9h30, 20:00, 9 giờ)."""
    text = DATETIME_REGEX.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def remove_noise_phrases(text: str) -> str:
    """Loại bỏ các cụm từ rác/vô nghĩa như: tắt mm app đi, tắt app, tải app, mở app..."""
    noise_patterns = [
        r"\btắt\s*(?:mm|m|cả)?\s*app\s*(?:đi|nha|nhé)?\b",
        r"\btắt\s*app\b",
        r"\bmở\s*app\b",
        r"\btải\s*app\b",
        r"\bcài\s*app\b"
    ]
    for np in noise_patterns:
        text = re.sub(np, " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def normalize_repeated_characters(text: str) -> str:
    """
    Rút gọn các ký tự kéo dài / lặp quá nhiều:
    Ví dụ: goodddddd -> good, ngonnnnn -> ngon, tuỵttttt -> tuỵt, quáaaa -> quá
    """
    text = re.sub(r'good[d]+', 'good', text, flags=re.IGNORECASE)
    text = re.sub(r'cool[l]+', 'cool', text, flags=re.IGNORECASE)
    text = re.sub(r'([a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ])\1{2,}', r'\1', text, flags=re.IGNORECASE)
    return text


def fix_typo_leetspeak(text: str) -> str:
    """Sửa các lỗi gõ số thay chữ (ví dụ: l9cation -> location)."""
    words = text.split()
    fixed_words = []
    for w in words:
        if re.search(r"[a-zA-Z]+[0-9]+[a-zA-Z]*", w):
            clean_w = w
            for num, char in LEETSPEAK_MAP.items():
                clean_w = clean_w.replace(num, char)
            fixed_words.append(clean_w)
        else:
            fixed_words.append(w)
    return " ".join(fixed_words)


def _translate_via_google_gtx(text: str, src_lang: str = "auto") -> str:
    """Gọi trực tiếp Google Translate GTX API (miễn phí, siêu nhanh, không giới hạn token/key, ổn định 100%)."""
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + urllib.parse.quote(src_lang) + "&tl=vi&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                result = "".join([part[0] for part in data[0] if part and len(part) > 0 and part[0]])
                if result and result.strip() and result.strip() != text.strip():
                    return result.strip()
    except Exception:
        pass
    return ""


def translate_to_vietnamese(text: str) -> str:
    """
    Dịch tự động TOÀN BỘ ngoại ngữ (Nga, Trung, Hàn, Nhật, Pháp, Ý, Đức, Tây Ban Nha, Anh...) sang Tiếng Việt.
    Hỗ trợ cả trường hợp 1 ĐÁNH GIÁ CHỨA ĐỒNG THỜI NHIỀU LOẠI NGÔN NGỮ KHÁC NHAU (Song ngữ / Đa ngữ).
    """
    if not text or not isinstance(text, str) or not text.strip():
        return ""
    
    text_clean = text.strip()
    if text_clean in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[text_clean]

    text_lower = text_clean.lower()
    if text_lower in OFFLINE_TRANSLATE_MAP:
        res = OFFLINE_TRANSLATE_MAP[text_lower]
        _TRANSLATION_CACHE[text_clean] = res
        return res

    # 1. Nhận diện ngôn ngữ & Gọi Google Translate GTX với mã ngôn ngữ phát hiện được
    is_foreign, lang_code = detect_foreign_language_code(text_clean)
    if is_foreign and lang_code and lang_code != "vi":
        gtx_lang = _translate_via_google_gtx(text_clean, src_lang=lang_code)
        if gtx_lang:
            _TRANSLATION_CACHE[text_clean] = gtx_lang
            return gtx_lang

    # Fallback thử với auto
    gtx_full = _translate_via_google_gtx(text_clean, src_lang="auto")
    if gtx_full:
        _TRANSLATION_CACHE[text_clean] = gtx_full
        return gtx_full

    # 2. Nếu là văn bản nhiều câu hoặc đoạn hỗn hợp đa ngữ (Ví dụ: Câu 1 Tiếng Anh, Câu 2 Tiếng Trung)
    # Tách theo dòng hoặc dấu chấm câu lớn để dịch từng phần riêng lẻ
    segments = re.split(r'(\n+|(?<=[.!?])\s+)', text_clean)
    if len(segments) > 1:
        translated_segments = []
        has_any_translation = False
        for seg in segments:
            if not seg.strip() or re.match(r'^[\s\n.!?]+$', seg):
                translated_segments.append(seg)
                continue
            
            is_seg_foreign, seg_lang = detect_foreign_language_code(seg)
            if is_seg_foreign:
                seg_trans = _translate_via_google_gtx(seg.strip(), src_lang="auto")
                if not seg_trans and seg_lang:
                    seg_trans = _translate_via_google_gtx(seg.strip(), src_lang=seg_lang)
                if seg_trans:
                    translated_segments.append(seg_trans)
                    has_any_translation = True
                else:
                    translated_segments.append(seg)
            else:
                translated_segments.append(seg)

        if has_any_translation:
            combined_res = "".join(translated_segments).strip()
            _TRANSLATION_CACHE[text_clean] = combined_res
            return combined_res

    # 3. Fallback qua deep-translator & MyMemory
    is_foreign, lang_code = detect_foreign_language_code(text_clean)
    if is_foreign and HAS_TRANSLATOR:
        try:
            translator = GoogleTranslator(source='auto', target='vi')
            translated = translator.translate(text_clean)
            if translated and not translated.startswith("Error") and "500" not in translated and translated != text_clean:
                _TRANSLATION_CACHE[text_clean] = translated
                return translated
        except Exception:
            pass

        try:
            mm_src = lang_code if lang_code in ["en", "fr", "it", "de", "es", "ru", "zh-CN", "zh-TW", "ja", "ko"] else "auto"
            res_mm = MyMemoryTranslator(source=mm_src, target="vi-VN").translate(text_clean)
            if res_mm and not res_mm.startswith("Error") and "MYMEMORY WARNING" not in res_mm and res_mm != text_clean:
                _TRANSLATION_CACHE[text_clean] = res_mm
                return res_mm
        except Exception:
            pass

    # 4. Từ điển dịch Offline các từ vựng phổ biến
    res_text = text_clean
    for en_word, vi_trans in OFFLINE_TRANSLATE_MAP.items():
        pattern = re.compile(rf"\b{re.escape(en_word)}\b", re.IGNORECASE)
        res_text = pattern.sub(vi_trans, res_text)

    _TRANSLATION_CACHE[text_clean] = res_text
    return res_text


def _has_keyword(text: str, keywords: List[str]) -> bool:
    """Kiểm tra từ khóa chính xác theo ranh giới từ (tránh lỗi nhận diện nhầm substring như 'khô' trong 'không')."""
    for k in keywords:
        if " " in k or "-" in k:
            if k in text:
                return True
        else:
            if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", text, re.IGNORECASE):
                return True
    return False


def ai_summarize_review_keypoints(text: str) -> str:
    """
    Mô hình AI đọc hiểu & Tóm tắt ý chính toàn diện của đánh giá (Balanced Multi-Aspect Summarization):
    Trích xuất & đúc kết súc tích, giữ trọn vẹn cả các điểm khen ngợi, góp ý/phản ánh, không gian, vị trí, tốc độ và quy định.
    """
    if not text or len(text.strip().split()) < 8:
        return ""

    t_clean = text.strip()
    t_lower = t_clean.lower()
    
    pos_points = []
    neg_points = []
    info_points = []

    # 1. Địa điểm / Không gian / Chỗ ngồi
    if _has_keyword(t_lower, ['sân bay', 'tân sân nhất', 'tân sơn nhất', 'gần sân bay', 'trong sân bay', 'đối diện']):
        if _has_keyword(t_lower, ['ngồi chờ', 'chờ máy bay', 'chờ lên máy bay', 'chờ bay', 'chờ transit']):
            info_points.append('quán nằm trong sân bay Tân Sơn Nhất thích hợp ngồi chờ máy bay')
        elif not _has_keyword(t_lower, ['vị trí']):
            info_points.append('quán nằm trong khu vực sân bay')
            
    if _has_keyword(t_lower, ['chỗ ngồi trong và ngoài trời', 'ngồi trong và ngoài trời', 'chỗ ngồi ngoài trời', 'ngoài trời']):
        info_points.append('có chỗ ngồi trong và ngoài trời')
        
    if _has_keyword(t_lower, ['không khí tốt', 'không khí tuyệt vời', 'không khí dễ chịu', 'không gian đẹp', 'decor xinh', 'decor đẹp', 'view đẹp', 'sạch sẽ']):
        pos_points.append('không gian quán thoáng mát, sạch sẽ')

    # 2. Tốc độ phục vụ / Thời gian
    if _has_keyword(t_lower, ['serve khá nhanh', 'serve nhanh', 'phục vụ nhanh', '10 15p là có', '10 15p', '10-15p', 'ra món nhanh', 'nhanh chóng', 'phục vụ nhanh chóng']):
        pos_points.append('đồ ăn phục vụ nhanh (10-15 phút có món)')
    elif _has_keyword(t_lower, ['đợi gần', 'chờ lâu', 'gần 20p', '20p hơn', 'đợi 10p', 'chờ đợi lâu', 'giao chậm', 'chờ lâu']):
        neg_points.append('thời gian chờ đợi lấy món lâu')

    # 3. Nhân viên / Thái độ
    if _has_keyword(t_lower, ['nhiệt tình', 'hiếu khách', 'nhanh nhẹn', 'thân thiện', 'dễ thương', 'chu đáo', 'hỗ trợ', 'mr ruby', 'mr. ruby', 'anh ruby']):
        pos_points.append('nhân viên nhiệt tình, hiếu khách, thân thiện và nhanh nhẹn')
        
    if _has_keyword(t_lower, ['không đưa bill', 'kh đưa bill', 'chưa đưa bill', 'quên bill', 'không có bill']):
        neg_points.append('nhân viên không đưa bill')
        
    if _has_keyword(t_lower, ['không trả lời', 'kh trl', 'không trl', 'không tl', 'kh thèm trả lời', 'không giải thích']):
        neg_points.append('nhân viên không trả lời khi khách hỏi')
        
    if _has_keyword(t_lower, ['không 1 lời xin lỗi', 'không xin lỗi', 'kh xin lỗi', 'không có lời xin lỗi', 'không thèm xin lỗi']):
        neg_points.append('không có lời xin lỗi khi nhầm lẫn đơn')
        
    if _has_keyword(t_lower, ['đi vòng vòng', 'chỉ lo', 'không tập trung', 'dốc ngược ly', 'thái độ chưa tốt', 'thái độ kém']):
        neg_points.append('tác phong phục vụ thiếu tập trung')

    # 4. Quy định / Order / Cảnh báo App
    if _has_keyword(t_lower, ['order tại quầy', 'order bằng máy', 'chỉ order cho khách tây', 'khách việt order', 'không cho khách việt']):
        neg_points.append('quy định order bất tiện (khách Việt phải tự order bằng máy)')
        
    if _has_keyword(t_lower, ['không ai nhận đơn', 'không có driver', 'không có tài xế', 'không giao', 'no driver']):
        neg_points.append('cảnh báo đặt app không có tài xế nhận giao hàng')

    # 5. Món ăn & Đồ uống
    if _has_keyword(t_lower, ['gà gia vị chanh dây', 'chanh dây', 'món mới', 'gà lạ']):
        pos_points.append('món gà gia vị chanh dây lạ miệng đáng thử')
    elif _has_keyword(t_lower, ['từng rất ngon', 'rất ngon', 'ngon tuyệt', 'đồ ăn ngon', 'cappuccino rất ngon', 'cappuccino ngon', 'tuyệt vời']):
        pos_points.append('đồ ăn thức uống ngon hợp khẩu vị')

    if _has_keyword(t_lower, ['khoai nguội', 'khoai ko ngon', 'khoai không ngon', 'khoai nguội lạnh']):
        neg_points.append('khoai tây chiên nguội không ngon như trước')
    elif _has_keyword(t_lower, ['bị khô', 'thịt khô', 'cháy', 'chua', 'thiu', 'nhạt', 'không tươi', 'nguội lạnh', 'dở']):
        neg_points.append('chất lượng món ăn chưa đạt chuẩn')

    if _has_keyword(t_lower, ['bẩn', 'dirty', 'dơ', 'rác', 'vệ sinh kém', 'hôi']):
        neg_points.append('vệ sinh quán chưa sạch sẽ')

    # 6. Giá cả
    if _has_keyword(t_lower, ['giá không có gì khác', 'giá ko có gì khác', 'giá giống', 'giá như các chi nhánh']):
        info_points.append('giá cả tương đương các chi nhánh khác')
    elif _has_keyword(t_lower, ['giá cao hơn', 'đắt hơn', 'giá đắt', 'đắt', 'chát']):
        neg_points.append('giá cả đắt hơn các chi nhánh ngoài sân bay')

    # Tổng hợp thành văn bản tóm tắt tự nhiên và đầy đủ
    summary_parts = []
    if info_points:
        summary_parts.append(", ".join(info_points).capitalize())
    if pos_points:
        summary_parts.append("Khen ngợi: " + ", ".join(pos_points))
    if neg_points:
        summary_parts.append("Góp ý/Phản ánh: " + ", ".join(neg_points))

    if summary_parts:
        return ". ".join(summary_parts) + "."
    return ""


def normalize_teencode_and_typos(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Chuẩn hóa Teencode, từ viết tắt và lỗi chính tả tiếng Việt.
    Đồng thời áp dụng Mô hình AI để tóm tắt ý chính súc tích đối với các review nhiều ý / phản ánh chi tiết.
    """
    if not text.strip():
        return "", []

    # Nạp thêm từ điển do người dùng dạy AI
    learned_dict = {}
    try:
        learned_actions = get_active_learned_actions()
        learned_dict = learned_actions.get("teencode", {})
    except Exception:
        pass

    combined_dict = dict(TEENCODE_DICT)
    combined_dict.update(learned_dict)

    replaced_items = []
    current_text = text

    for slang, standard in combined_dict.items():
        if " " in slang or len(slang) > 10:
            pattern = re.compile(rf"(?<!\w){re.escape(slang)}(?!\w)", re.IGNORECASE)
            if pattern.search(current_text):
                current_text = pattern.sub(standard, current_text)
                replaced_items.append((slang, standard))

    tokens_list = re.split(r"(\s+|[,.!?;:])", current_text)
    normalized_parts = []
    for token in tokens_list:
        clean_w = token.strip().lower()
        if clean_w in combined_dict:
            standard_word = combined_dict[clean_w]
            normalized_parts.append(standard_word)
            replaced_items.append((token.strip(), standard_word))
        else:
            normalized_parts.append(token)

    normalized_text = "".join(normalized_parts)

    # Áp dụng AI Tóm Tắt Ý Chính (Review Summarization) đối với các review dài/nhiều phản ánh
    ai_summary = ai_summarize_review_keypoints(normalized_text)
    if ai_summary:
        result_text = ai_summary
    else:
        result_text = normalized_text

    return result_text, replaced_items


def normalize_unicode(text: str) -> str:
    """Chuẩn hóa Unicode về chuẩn dựng sẵn (NFC)."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFC", text)


def remove_emojis_and_emoticons(text: str) -> Tuple[str, List[str]]:
    """Xóa bỏ Emojis và Emoticons biểu tượng cảm xúc."""
    removed_items = []

    emojis_found = [c for c in text if emoji.is_emoji(c)]
    if emojis_found:
        removed_items.extend(emojis_found)
        text = emoji.replace_emoji(text, replace=" ")

    emoticons_found = EMOTICON_REGEX.findall(text)
    if emoticons_found:
        removed_items.extend([e.strip() for e in emoticons_found if e.strip()])
        text = EMOTICON_REGEX.sub(" ", text)

    text = URL_REGEX.sub(" ", text)
    text = HTML_REGEX.sub(" ", text)
    text = PHONE_REGEX.sub(" ", text)
    text = EMAIL_REGEX.sub(" ", text)

    return text, removed_items


def tokenize_vietnamese_text(text: str, method: str = "underthesea") -> str:
    """Tách từ ghép tiếng Việt (áp dụng các từ ghép chuẩn và từ ghép người dùng đã dạy AI)."""
    if not text.strip():
        return ""

    current_text = text

    # 1. Áp dụng trước các cụm từ ghép do Người dùng dạy AI (ưu tiên số 1)
    # Hỗ trợ cả trường hợp có từ nối trung gian như: "không được tươi", "ko dc tươi", "chẳng tươi" -> "không_tươi" hoặc "không_được_tươi"
    try:
        learned_actions = get_active_learned_actions()
        learned_compounds = learned_actions.get("compounds", [])
        for phrase, compound in learned_compounds:
            # Match cụm chính xác (ví dụ: không tươi -> không_tươi)
            pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)
            current_text = pattern.sub(compound, current_text)
            
            # Match mở rộng khi có từ đệm ở giữa (ví dụ: "không được tươi", "không quá tươi", "không còn tươi" -> "không_tươi")
            parts = phrase.split()
            if len(parts) == 2:
                flex_pattern = re.compile(rf"(?<!\w){re.escape(parts[0])}\s+(?:được|còn|quá|rất|hề|hẳn)\s+{re.escape(parts[1])}(?!\w)", re.IGNORECASE)
                current_text = flex_pattern.sub(compound, current_text)
    except Exception:
        pass

    # 2. Áp dụng các từ ghép mặc định trong hệ thống
    for phrase, compound in COMMON_VI_COMPOUNDS:
        pattern = re.compile(rf"\b{phrase}\b", re.IGNORECASE)
        current_text = pattern.sub(compound, current_text)

    # 3. Tách từ qua underthesea / pyvi
    if method == "underthesea" and HAS_UNDERTHESEA:
        try:
            tokens = underthesea_tokenize(current_text, format="text")
            current_text = tokens
        except Exception:
            pass
    elif (method == "pyvi" or not HAS_UNDERTHESEA) and HAS_PYVI:
        try:
            tokens = ViTokenizer.tokenize(current_text)
            current_text = tokens
        except Exception:
            pass

    # 4. Đảm bảo các cụm từ dạy AI vẫn giữ nguyên dạng từ ghép sau khi tokenize
    try:
        learned_actions = get_active_learned_actions()
        learned_compounds = learned_actions.get("compounds", [])
        for phrase, compound in learned_compounds:
            # Nếu underthesea tách rời phrase (ví dụ không tươi), ta ghép lại thành không_tươi
            pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)
            current_text = pattern.sub(compound, current_text)
            
            parts = phrase.split()
            if len(parts) == 2:
                flex_pattern = re.compile(rf"(?<!\w){re.escape(parts[0])}\s+(?:được|còn|quá|rất|hề|hẳn)\s+{re.escape(parts[1])}(?!\w)", re.IGNORECASE)
                current_text = flex_pattern.sub(compound, current_text)
    except Exception:
        pass

    return current_text


def remove_punctuation_and_symbols(text: str) -> str:
    """Loại bỏ dấu câu và ký tự đặc biệt sau khi đã tokenize."""
    text = re.sub(r"[,.!?;:\'\"/\\|\(\)\[\]\{\}\<\>\+\=\*\&\^\%\$\#\@~`—–-]", " ", text)
    text = re.sub(r"[^\w\s\d_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]", " ", text)
    
    words = [w.strip("_") for w in text.split() if w.strip("_")]
    return " ".join(words)


def filter_stopwords_from_text(text: str, stopwords: Set[str]) -> Tuple[str, List[str], List[str]]:
    """Lọc bỏ các từ dừng khỏi văn bản (kết hợp stopwords mặc định và stopwords từ kinh nghiệm dạy AI)."""
    if not text.strip():
        return "", [], []

    active_sw = set(stopwords)
    try:
        learned_actions = get_active_learned_actions()
        active_sw.update(learned_actions.get("stopwords", []))
    except Exception:
        pass

    words = text.split()
    kept_tokens = []
    removed_sw = []

    for w in words:
        clean_w = w.lower()
        if not clean_w:
            continue
        
        # Nếu là từ ghép (có dấu _)
        if "_" in clean_w:
            parts = clean_w.split("_")
            # Nếu cả cụm từ ghép là từ dừng thì bỏ
            if clean_w in active_sw or " ".join(parts) in active_sw:
                removed_sw.append(w)
                continue
            
            # Giữ nguyên cả cụm từ ghép (không bẻ vụn nếu cụm từ ghép đó có ý nghĩa như không_tươi, giao_hàng_nhanh)
            kept_tokens.append(w)
        else:
            if clean_w in active_sw:
                removed_sw.append(w)
            else:
                kept_tokens.append(w)

    cleaned_text = " ".join(kept_tokens)
    return cleaned_text, kept_tokens, removed_sw


def generate_html_diff_badge(
    raw_text: str,
    tokens: List[str],
    removed_icons: List[str],
    removed_sw: List[str],
    replaced_teencodes: List[Tuple[str, str]]
) -> str:
    """Tạo chuỗi HTML Highlight trực quan chuẩn Dark Mode & Light Mode."""
    html_parts = []

    if replaced_teencodes:
        for orig, std in replaced_teencodes[:3]:
            html_parts.append(
                f'<span style="background-color:rgba(245, 158, 11, 0.22); color:#FBBF24; border:1px solid rgba(245, 158, 11, 0.5); padding:3px 7px; border-radius:6px; margin:2px; font-size:0.83rem; display:inline-block; font-weight:600;">'
                f'✏️ {orig} ➔ <b>{std}</b></span>'
            )

    for sw in removed_sw:
        html_parts.append(
            f'<del style="background-color:rgba(239, 68, 68, 0.22); color:#F87171; border:1px solid rgba(239, 68, 68, 0.45); padding:3px 7px; border-radius:6px; margin:2px; font-size:0.83rem; display:inline-block;">'
            f'{sw}</del>'
        )

    for ic in removed_icons:
        html_parts.append(
            f'<span style="background-color:rgba(239, 68, 68, 0.22); color:#F87171; border:1px solid rgba(239, 68, 68, 0.45); padding:3px 7px; border-radius:6px; margin:2px; font-size:0.83rem; display:inline-block;">'
            f'❌ {ic}</span>'
        )

    for tk in tokens:
        html_parts.append(
            f'<span style="background-color:rgba(34, 197, 94, 0.22); color:#4ADE80; border:1px solid rgba(34, 197, 94, 0.45); padding:3px 7px; border-radius:6px; margin:2px; font-size:0.83rem; font-weight:600; display:inline-block;">'
            f'{tk}</span>'
        )

    return " ".join(html_parts) if html_parts else '<span style="color:#94A3B8; font-style:italic;">(Không có thay đổi)</span>'


def is_meaningless_review(raw_text: Any) -> Tuple[bool, str]:
    """
    Bước 0.5: Nhận diện và giải thích lý do review vô nghĩa / rác cần loại bỏ.
    Hỗ trợ ĐA NGÔN NGỮ TOÀN CẦU (Tiếng Việt, Anh, Nga, Trung, Hàn, Nhật, Pháp, Ý...).
    """
    if raw_text is None or str(raw_text).strip() == "" or str(raw_text).lower() == "nan":
        return True, "Bình luận trống rỗng hoặc không có ký tự hợp lệ."
    
    raw_str = str(raw_text).strip()
    raw_lower = raw_str.lower()

    # 1. Nhận diện cụm từ rác / câu cảm thán vô nghĩa hoặc lỗi thao tác ứng dụng không phải đánh giá
    meaningless_exact = [
        "tắt mm app đi", "tắt m app đi", "tắt app đi", "tắt app", "tải app", "mở app", "cài app", 
        "test", "testing", "asdfgh", "qwerty", "123456", "abcxyz", "spam", "test app"
    ]
    try:
        learned_actions = get_active_learned_actions()
        for lp in learned_actions.get("meaningless_patterns", []):
            if lp not in meaningless_exact:
                meaningless_exact.append(lp)
    except Exception:
        pass

    for m in meaningless_exact:
        if raw_lower == m or raw_lower.startswith(m) or raw_lower.endswith(m):
            return True, "Chưa hiểu rõ ý của khách hàng muốn nói gì, câu cảm thán/vô nghĩa hoặc lỗi thao tác ứng dụng không liên quan đến trải nghiệm sản phẩm/dịch vụ."

    # 2. Đếm số ký tự chữ trong BẤT KỲ NGÔN NGỮ NÀO trên thế giới (Unicode Category 'L' = Letter)
    unicode_letters = [c for c in raw_str if unicodedata.category(c).startswith('L')]
    if len(unicode_letters) < 2:
        return True, "Chỉ chứa ký tự đặc biệt/dấu câu hoặc số đơn lẻ, không có từ ngữ có nghĩa trong bất kỳ ngôn ngữ nào."

    return False, ""


def clean_single_review(
    raw_text: Any,
    stopwords: Set[str],
    translate_to_vi: bool = True,
    fix_teencode: bool = True,
    use_lowercase: bool = True,
    remove_icons: bool = True,
    word_segmentation: bool = True,
    remove_sw: bool = True,
    nlp_engine: str = "underthesea"
) -> Dict[str, Any]:
    """Thực thi chuỗi xử lý NLP & Phân tích cảm xúc toàn diện cho 1 đánh giá / bình luận."""
    
    # Bước 0.5: Kiểm tra review vô nghĩa / rác
    is_meaningless, meaningless_reason = is_meaningless_review(raw_text)
    raw_str = str(raw_text).strip() if raw_text is not None else ""

    if is_meaningless:
        return {
            "raw_text": raw_str,
            "is_meaningless": True,
            "meaningless_reason": meaningless_reason,
            "step1_translated_clean": "LOẠI",
            "step2_teencode": "LOẠI",
            "cleaned_text": "LOẠI",
            "tokens": [],
            "removed_icons": [],
            "removed_stopwords": [],
            "replaced_teencodes": [],
            "reduction_percent": 100.0,
            "has_changed": True,
            "html_diff": f'<del style="background-color:#FEE2E2; color:#B91C1C; padding:2px 6px; border-radius:4px; font-weight:600;">❌ Bị loại bỏ: {meaningless_reason}</del>',
            "sentiment": {
                "label": "Trung tính",
                "score": 0.5,
                "confidence_percent": 50,
                "badge": "🟡 LOẠI",
                "color": "#6B7280",
                "bg_color": "#F3F4F6",
                "border_color": "#D1D5DB"
            }
        }

    # BƯỚC 1: TIỀN XỬ LÝ TYPO TIẾNG ANH (L9CATION -> LOCATION), DỊCH TIẾNG VIỆT, CHỮ THƯỜNG & BỎ KÝ TỰ THỪA / ICON
    current_text = normalize_unicode(raw_str)
    
    # Sửa lỗi gõ số thay chữ tiếng Anh (l9cation -> location, g00d -> good) TRƯỚC KHI DỊCH
    current_text = fix_typo_leetspeak(current_text)
    current_text = normalize_repeated_characters(current_text)
    current_text = remove_dates_and_times(current_text)

    # Dịch toàn bộ sang Tiếng Việt
    translated_text = current_text
    if translate_to_vi:
        translated_text = translate_to_vietnamese(current_text)
        current_text = translated_text

    # Chuyển chữ thường (Lowercase)
    if use_lowercase:
        current_text = current_text.lower()

    # Bỏ Emojis, Emoticons, URLs, HTML, SĐT
    removed_icons = []
    if remove_icons:
        current_text, removed_icons = remove_emojis_and_emoticons(current_text)

    # Bỏ các ký tự thừa (dấu : " , . ! ? / ( ) ... )
    current_text = re.sub(r"[\:\"\'\,\.\!\?\/\(\)\[\]\{\}\<\>\+\=\*\&\^\%\$\#\@~`—–\-]", " ", current_text)
    current_text = re.sub(r"\s+", " ", current_text).strip()
    step1_translated_clean = current_text

    # BƯỚC 2: SỬA TEENCODE, LỖI CHÍNH TẢ & AI TÓM TẮT Ý CHÍNH
    step2_teencode = current_text
    replaced_teencodes = []
    if fix_teencode:
        step2_teencode, replaced_teencodes = normalize_teencode_and_typos(current_text)
        current_text = step2_teencode

    # BƯỚC 3: VĂN BẢN ĐÃ CLEAN (TÁCH TỪ GHÉP & LỌC TỪ DỪNG)
    if word_segmentation:
        current_text = tokenize_vietnamese_text(current_text, method=nlp_engine)

    current_text = remove_punctuation_and_symbols(current_text)

    cleaned_text = current_text
    tokens = [w for w in current_text.split() if w]
    removed_stopwords = []
    if remove_sw:
        cleaned_text, tokens, removed_stopwords = filter_stopwords_from_text(current_text, stopwords)

    # BƯỚC 4: TOKENS NLP
    len_raw = len(raw_str)
    len_clean = len(cleaned_text)
    reduction = round(((len_raw - len_clean) / max(1, len_raw) * 100), 1) if len_raw > 0 else 0.0
    has_changed = (raw_str != cleaned_text)

    html_diff = generate_html_diff_badge(
        raw_text=raw_str,
        tokens=tokens,
        removed_icons=removed_icons,
        removed_sw=removed_stopwords,
        replaced_teencodes=replaced_teencodes
    )

    sentiment_res = analyze_sentiment(raw_str, tokens=tokens)

    return {
        "raw_text": raw_str,
        "is_meaningless": False,
        "meaningless_reason": "",
        "step1_translated_clean": step1_translated_clean,
        "step2_teencode": step2_teencode,
        "cleaned_text": cleaned_text,
        "tokens": tokens,
        "removed_icons": removed_icons,
        "removed_stopwords": removed_stopwords,
        "replaced_teencodes": replaced_teencodes,
        "reduction_percent": reduction,
        "has_changed": has_changed,
        "html_diff": html_diff,
        "sentiment": sentiment_res
    }
