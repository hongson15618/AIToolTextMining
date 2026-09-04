"""
Module: text_cleaner.py (Phiên bản Toàn Cầu & Lọc Ngày Giờ Chuẩn Thứ Tự)
"""

import os
import re
import unicodedata
from typing import Dict, List, Set, Tuple, Any

import emoji
from teencode_dict import TEENCODE_DICT, LEETSPEAK_MAP
from sentiment_ai import analyze_sentiment

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
    "broken", "damaged", "nice", "coffee", "cappuccino", "staff", "supercalifragilisticexpialidocious"
}

def detect_foreign_language_code(text: str) -> Tuple[bool, str]:
    """Tự động nhận diện ngôn ngữ nguồn cực nhanh (0ms cho Tiếng Việt & Teencode)."""
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

    # 2. Nếu văn bản có dấu tiếng Việt -> Chắc chắn 100% là Tiếng Việt
    if re.search(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]", text_clean):
        return False, "vi"

    text_lower = text_clean.lower()
    words = re.findall(r"[a-zA-Z0-9_]+", text_lower)
    word_set = set(words)

    # 3. Nếu có từ khóa tiếng Việt không dấu hoặc teencode -> Đích thị là Tiếng Việt
    if word_set.intersection(VI_UNACCENTED_KEYWORDS):
        return False, "vi"

    # 4. Kiểm tra từ khóa tiếng Pháp / Ý / Đức / Tây Ban Nha
    if len(word_set.intersection(FRENCH_KEYWORDS)) >= 1:
        return True, "fr"
    if len(word_set.intersection(ITALIAN_KEYWORDS)) >= 1:
        return True, "it"
    if len(word_set.intersection(GERMAN_KEYWORDS)) >= 1:
        return True, "de"
    if len(word_set.intersection(SPANISH_KEYWORDS)) >= 1:
        return True, "es"

    # 5. Kiểm tra tiếng Anh
    if len(word_set.intersection(ENGLISH_INDICATORS)) >= 1:
        return True, "en"

    # 6. Dùng thư viện langdetect nếu còn nghi ngờ
    if HAS_LANGDETECT and len(words) >= 3:
        try:
            detected_lang = lang_detect(text_clean)
            if detected_lang != "vi":
                return True, detected_lang
        except Exception:
            pass

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


def translate_to_vietnamese(text: str) -> str:
    """Dịch tự động TOÀN BỘ ngoại ngữ (Nga, Trung, Hàn, Nhật, Pháp, Ý, Anh...) sang Tiếng Việt."""
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

    is_foreign, lang_code = detect_foreign_language_code(text_clean)

    if is_foreign and HAS_TRANSLATOR:
        # 1. Thử Google Translator (source='auto')
        try:
            translator = GoogleTranslator(source='auto', target='vi')
            translated = translator.translate(text_clean)
            if translated and not translated.startswith("Error") and "500" not in translated and translated != text_clean:
                _TRANSLATION_CACHE[text_clean] = translated
                return translated
        except Exception:
            pass

        # 2. Thử Google Translator với mã ngôn ngữ cụ thể
        try:
            translator = GoogleTranslator(source=lang_code, target='vi')
            translated = translator.translate(text_clean)
            if translated and not translated.startswith("Error") and "500" not in translated and translated != text_clean:
                _TRANSLATION_CACHE[text_clean] = translated
                return translated
        except Exception:
            pass

        # 3. Thử MyMemory Translator
        try:
            mm_src = lang_code if lang_code in ["en", "fr", "it", "de", "es", "ru", "zh-CN", "zh-TW", "ja", "ko"] else "auto"
            res_mm = MyMemoryTranslator(source=mm_src, target="vi-VN").translate(text_clean)
            if res_mm and not res_mm.startswith("Error") and "MYMEMORY WARNING" not in res_mm and res_mm != text_clean:
                _TRANSLATION_CACHE[text_clean] = res_mm
                return res_mm
        except Exception:
            pass

    res_text = text_clean
    for en_word, vi_trans in OFFLINE_TRANSLATE_MAP.items():
        pattern = re.compile(rf"\b{re.escape(en_word)}\b", re.IGNORECASE)
        res_text = pattern.sub(vi_trans, res_text)

    _TRANSLATION_CACHE[text_clean] = res_text
    return res_text


def normalize_teencode_and_typos(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """Chuẩn hóa Teencode, từ viết tắt và lỗi chính tả tiếng Việt."""
    if not text.strip():
        return "", []

    replaced_items = []
    current_text = text

    for slang, standard in TEENCODE_DICT.items():
        if " " in slang or len(slang) > 10:
            pattern = re.compile(rf"(?<!\w){re.escape(slang)}(?!\w)", re.IGNORECASE)
            if pattern.search(current_text):
                current_text = pattern.sub(standard, current_text)
                replaced_items.append((slang, standard))

    tokens_list = re.split(r"(\s+|[,.!?;:])", current_text)
    normalized_parts = []
    for token in tokens_list:
        clean_w = token.strip().lower()
        if clean_w in TEENCODE_DICT:
            standard_word = TEENCODE_DICT[clean_w]
            normalized_parts.append(standard_word)
            replaced_items.append((token.strip(), standard_word))
        else:
            normalized_parts.append(token)

    return "".join(normalized_parts), replaced_items


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
    """Tách từ ghép tiếng Việt."""
    if not text.strip():
        return ""

    current_text = text
    for phrase, compound in COMMON_VI_COMPOUNDS:
        pattern = re.compile(rf"\b{phrase}\b", re.IGNORECASE)
        current_text = pattern.sub(compound, current_text)

    if method == "underthesea" and HAS_UNDERTHESEA:
        try:
            tokens = underthesea_tokenize(current_text, format="text")
            return tokens
        except Exception:
            pass

    if (method == "pyvi" or not HAS_UNDERTHESEA) and HAS_PYVI:
        try:
            tokens = ViTokenizer.tokenize(current_text)
            return tokens
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
    """Lọc bỏ các từ dừng khỏi văn bản."""
    if not text.strip():
        return "", [], []

    words = text.split()
    kept_tokens = []
    removed_sw = []

    for w in words:
        clean_w = w.strip("_").lower()
        if not clean_w:
            continue
        
        if "_" in clean_w:
            parts = clean_w.split("_")
            if clean_w in stopwords or " ".join(parts) in stopwords:
                removed_sw.append(w)
                continue
            
            sub_kept = []
            for p in parts:
                if p in stopwords:
                    removed_sw.append(p)
                else:
                    sub_kept.append(p)
            
            if len(sub_kept) == len(parts):
                kept_tokens.append(w.strip("_"))
            elif sub_kept:
                kept_tokens.extend([sk.strip("_") for sk in sub_kept])
        else:
            if clean_w in stopwords:
                removed_sw.append(w)
            else:
                kept_tokens.append(w.strip("_"))

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

    # 1. Nhận diện cụm từ rác / câu cảm thán vô nghĩa hoặc từ quá ngắn không mang thông tin
    meaningless_exact = [
        "tắt mm app đi", "tắt m app đi", "tắt app đi", "tắt app", "tải app", "mở app", "cài app", 
        "test", "testing", "asdfgh", "qwerty", "123456", "abcxyz",
        "별로", "그냥", "soso", "so so", "chẳng ra sao", "chả ra sao", "chả có gì", "bình thường thôi"
    ]
    for m in meaningless_exact:
        if raw_lower == m or raw_lower.startswith(m) or raw_lower.endswith(m):
            if m in ["별로", "그냥", "soso", "so so"]:
                return True, f"Đánh giá quá ngắn và cụt lủn ('{raw_str}' - không có nội dung/ngữ cảnh cụ thể), chưa đủ thông tin để đánh giá trải nghiệm sản phẩm/dịch vụ."
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

    # BƯỚC 2: SỬA TEENCODE & LỖI CHÍNH TẢ (tuỵt -> tuyệt, ko -> không, l9cation/location -> vị trí...)
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
    tokens = [w.strip("_") for w in current_text.split() if w.strip("_")]
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
