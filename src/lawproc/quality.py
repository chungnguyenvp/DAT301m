"""Tỷ lệ token không có dạng âm tiết tiếng Việt, sau khi bỏ dấu thanh.

Bỏ qua số, mã chứa chữ số, chữ đơn và chữ viết hoa toàn bộ. Đây là chỉ số
nhiễu chữ OCR, không kiểm tra nghĩa, dấu thanh, số liệu hoặc bố cục bảng.
"""
import re
import unicodedata

TONE_MARKS = {"\u0300", "\u0301", "\u0303", "\u0309", "\u0323"}
ONSET = r"(?:ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdđghklmnprstvx])?"
NUCLEUS = r"[aăâeêioôơuưy]{1,3}"
CODA = r"(?:ch|nh|ng|[cmnpt])?"
SYLLABLE = re.compile(rf"{ONSET}{NUCLEUS}{CODA}")
WORD = re.compile(r"[^\W_]+")


def _strip_tone(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower())
    return unicodedata.normalize("NFC", "".join(c for c in decomposed if c not in TONE_MARKS))


def syllable_error_rate(text: str) -> float:
    words = [w for w in WORD.findall(unicodedata.normalize("NFC", text))
             if len(w) > 1 and not w.isupper() and not any(c.isdigit() for c in w)]
    if not words:
        return 0.0
    bad = sum(SYLLABLE.fullmatch(_strip_tone(w)) is None for w in words)
    return round(bad / len(words), 4)
