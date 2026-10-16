"""Hàm tính toán cho EDA kho văn bản luật."""

import math
import re
from collections.abc import Sequence
from pathlib import Path


FINE = re.compile(r"phạt\s+tiền\s+từ\s+([\d.]+)\s+đồng\s+đến\s+([\d.]+)\s+đồng", re.IGNORECASE)
POINTS = re.compile(r"trừ\s+điểm\s+giấy\s+phép\s+lái\s+xe\s+(\d{1,2})\s+điểm", re.IGNORECASE)
REF = re.compile(
    r"(?:điểm\s+([a-zđ]{1,2}\d?)\s+)?(?:khoản\s+(\d+[a-zđ]?)\s+)?Điều\s+(\d+[a-zđ]?)"
    r"(?:\s+(?:của\s+)?(Bộ luật|Luật|Nghị định|Thông tư|Quy chuẩn)(\s+này)?)?"
)
WORD = re.compile(r"\w+")

# Từ khóa trong tiêu đề Điều; quy tắc cụ thể đứng trước quy tắc rộng.
VEHICLE_RULES = (
    ("xe ô tô", "Ô tô"),
    ("xe chở người bốn bánh", "Ô tô"),
    ("xe chở hàng bốn bánh", "Ô tô"),
    ("xe cứu hộ giao thông", "Ô tô"),
    ("xe cứu thương", "Ô tô"),
    ("xe mô tô", "Mô tô, xe gắn máy"),
    ("xe gắn máy", "Mô tô, xe gắn máy"),
    ("xe máy chuyên dùng", "Xe máy chuyên dùng"),
    ("xe đạp", "Xe đạp, xe thô sơ"),
    ("xe thô sơ", "Xe đạp, xe thô sơ"),
    ("người đi bộ", "Người đi bộ"),
)

IMPORTANCE = {"Xử phạt": 1.5, "GPLX": 1.5, "Đăng ký xe": 1.5}
LOAI_SPLIT = {
    "Xử phạt": {"mức phạt": 5, "hành vi cấm": 2, "tình huống": 2, "chung": 1},
    "Luật lõi": {"chung": 2, "định nghĩa": 2, "hành vi cấm": 2, "tình huống": 2},
    "Biển báo": {"định nghĩa": 2, "chung": 1, "tình huống": 1},
    "Tốc độ": {"chung": 1, "tình huống": 1},
    "Lệ phí": {"chung": 1, "thủ tục": 1},
    "Tai nạn": {"chung": 1, "tình huống": 2, "mức phạt": 1},
}
DEFAULT_SPLIT = {"chung": 1, "thủ tục": 2, "tình huống": 1}


def money(s: str) -> int:
    return int(s.replace(".", ""))


def extract_fine(text: str) -> tuple[int, int] | None:
    """Lấy khung phạt đầu tiên; đây là heuristic, không phân giải mọi mức phạt."""
    match = FINE.search(text)
    return (money(match.group(1)), money(match.group(2))) if match else None


def extract_points(text: str) -> int | None:
    match = POINTS.search(text)
    return int(match.group(1)) if match else None


def vehicle_group(title: str) -> str:
    title = title.lower()
    return next((group for key, group in VEHICLE_RULES if key in title), "Khác")


def find_references(text: str) -> list[dict]:
    """Nhận diện tham chiếu Điều đơn giản; không dựng đồ thị viện dẫn đầy đủ."""
    out = []
    for match in REF.finditer(text):
        external = bool(match.group(4)) and not match.group(5)
        out.append({"diem": match.group(1), "khoan": match.group(2), "dieu": match.group(3),
                    "loai": "ngoai" if external else "noi_bo"})
    return out


def count_words(text: str) -> int:
    return len(WORD.findall(text))


def count_tokens(texts: Sequence[str], tokenizer_path: Path) -> list[int]:
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    return [len(encoded.ids) for encoded in tokenizer.encode_batch(list(texts), add_special_tokens=False)]


def near_duplicates(texts: Sequence[str], groups: Sequence[str], threshold: float = 0.9,
                    block: int = 500) -> list[tuple[int, int, float]]:
    """Cặp khác nhóm có cosine TF-IDF char 4-gram đạt ngưỡng."""
    if len(texts) != len(groups):
        raise ValueError("texts và groups phải có cùng số phần tử")
    if not isinstance(block, int) or block <= 0:
        raise ValueError("block phải là số nguyên dương")
    if not math.isfinite(threshold) or not 0 < threshold <= 1:
        raise ValueError("threshold phải nằm trong khoảng (0, 1]")
    if len(texts) < 2 or not any(text.strip() for text in texts):
        return []

    from sklearn.feature_extraction.text import TfidfVectorizer

    try:
        matrix = TfidfVectorizer(analyzer="char_wb", ngram_range=(4, 4),
                                 sublinear_tf=True).fit_transform(list(texts))
    except ValueError as error:
        if "empty vocabulary" in str(error):
            return []
        raise
    pairs: list[tuple[int, int, float]] = []
    for start in range(0, matrix.shape[0], block):
        similarity = (matrix[start:start + block] @ matrix.T).tocoo()
        keep = similarity.data >= threshold
        for row, column, value in zip(similarity.row[keep], similarity.col[keep], similarity.data[keep]):
            i, j = start + int(row), int(column)
            if i < j and groups[i] != groups[j]:
                pairs.append((i, j, round(float(value), 4)))
    return sorted(pairs)


def allocate(weights: dict[str, float], total: int, floor: int = 0) -> dict[str, int]:
    """Phân bổ theo phần dư lớn nhất, hòa phần dư thì chọn khóa theo tên."""
    if not isinstance(total, int) or total < 0 or not isinstance(floor, int) or floor < 0:
        raise ValueError("total và floor phải là số nguyên không âm")
    keys = sorted(weights)
    if not keys:
        if total:
            raise ValueError("không thể phân bổ total khi không có nhóm")
        return {}
    if any(not math.isfinite(weight) or weight < 0 for weight in weights.values()):
        raise ValueError("trọng số phải hữu hạn và không âm")
    rest = total - floor * len(keys)
    if rest < 0:
        raise ValueError(f"total {total} nhỏ hơn floor {floor} × {len(keys)} nhóm")
    maximum = max(weights.values())
    # Chuẩn hóa trước khi cộng để tổng của các trọng số hữu hạn không tràn số thực.
    scaled = {key: weights[key] / maximum for key in keys} if maximum else {}
    weight_sum = sum(scaled.values())
    # Khi không có trọng số dương, chia đều phần còn lại để vẫn giữ tổng.
    raw = {key: rest * (scaled[key] / weight_sum if maximum else 1 / len(keys)) for key in keys}
    out = {key: floor + math.floor(raw[key]) for key in keys}
    left = total - sum(out.values())
    for key in sorted(keys, key=lambda k: (-(raw[k] - math.floor(raw[k])), k))[:left]:
        out[key] += 1
    return out


def eval_matrix(group_counts: dict[str, int], docs_by_group: dict[str, list[str]], total: int = 150,
                floor: int = 5) -> list[dict]:
    """Chia câu hỏi theo căn bậc hai số Điều và độ ưu tiên từng chủ đề."""
    weights = {group: math.sqrt(count) * IMPORTANCE.get(group, 1.0)
               for group, count in group_counts.items() if count > 0}
    per_group = allocate(weights, total, floor)
    rows = []
    for group in sorted(per_group):
        split = allocate(LOAI_SPLIT.get(group, DEFAULT_SPLIT), per_group[group])
        for kind, count in split.items():
            if count:
                rows.append({"chu_de": group, "van_ban": " ".join(sorted(docs_by_group.get(group, []))),
                             "loai_cau": kind, "so_cau": count, "ghi_chu": ""})
    return rows
