"""Chấm tự động câu trả lời của G7 theo rubric trong `data/eval/README.md`.

Số liệu đọc bằng chính `lawproc.evalset.facts`, hàm đã tạo `so_lieu` của bộ eval, nên câu trả lời và đáp án được đọc
theo cùng một quy tắc (tiền quy về đồng, "ngày làm việc" khác "ngày", tỷ số "27/30 điểm" giữ nguyên). Trước khi đọc,
câu trả lời được bỏ định dạng markdown và chuẩn hóa cách viết tiền ("VNĐ", "4.000.000đ").

Mỗi hàm chấm một tiêu chí và trả `None` khi câu không thuộc tiêu chí đó, để phần tổng hợp tự lấy đúng mẫu số. Phần
"nội dung" (đủ ý chính) cần LLM-Judge hoặc chấm tay, không nằm ở đây.
"""

import re
from collections import Counter

from lawproc import evalset
from rag.chunking import doc_name

_MD = re.compile(r"\*\*|__|`|^#+\s*|^\s*[-*•]\s+", re.MULTILINE)
_VND = re.compile(r"(\d|triệu|nghìn|tỷ)\s*(?:VNĐ|VND|vnđ|vnd|đ)(?![\wÀ-ỹ])")
_TOKEN = re.compile(r"[0-9a-zà-ỹđ]+(?:[.,/][0-9]+)*", re.IGNORECASE)

REFUSAL = re.compile(
    r"không có căn cứ|ngoài phạm vi|không thuộc phạm vi|nằm ngoài|không có (?:quy định|thông tin|đoạn luật)"
    r"|không (?:được )?(?:đề cập|quy định) trong|không có trong (?:tài liệu|các đoạn)|tài liệu không có"
    r"|không thể (?:cung cấp|trả lời|hướng dẫn|xác định)|không tìm thấy",
    re.IGNORECASE)
EXPIRED = re.compile(r"hết hiệu lực|không còn hiệu lực|đã bị thay thế|được thay thế bởi", re.IGNORECASE)
REFUSAL_HEAD = 300   # câu từ chối nói ngay ở đầu; câu trả lời thật chỉ nhắc "không có quy định..." ở giữa thì không tính

DEDUCT_CLAIM = re.compile(r"trừ(?:\s+điểm)?(?:\s+giấy phép lái xe)?\s*[:\-–]?\s*(\d+)\s*điểm", re.IGNORECASE)
DEDUCT_ANY = re.compile(r"trừ\s+(?:\d+\s+)?điểm", re.IGNORECASE)
SUSPEND = re.compile(r"tước[^.;\n]{0,120}?từ\s+(\d+)\s*tháng\s+đến\s+(\d+)\s*tháng", re.IGNORECASE)
DOC_NO = re.compile(r"(?<![\d/])(\d{1,4})/(\d{4})/(?:NĐ|TT|QH|QĐ|NQ|CT|VBHN|L)")
QCVN = re.compile(r"QCVN\s*(\d+)\s*:\s*(\d{4})")
OLD_LAW = re.compile(r"(?<!pháp )Luật Giao thông đường bộ")   # Luật 23/2008/QH12, đã thay bằng Luật 35, 36/2024


def clean(text: str) -> str:
    """Bỏ markdown, chuẩn hóa tiền và chữ hoa đầu câu ("Từ X đồng đến Y đồng") để các mẫu của `evalset` bắt được."""
    text = _MD.sub("", text or "")
    text = re.sub(r"(?<=\d)\s*ngàn(?![\wÀ-ỹ])", " nghìn", text)
    text = _VND.sub(r"\1 đồng", text)
    text = re.sub(r"(?<![\wÀ-ỹ])Từ(?=\s+\d)", "từ", text.replace("Đồng", "đồng"))
    text = re.sub(r"(?<![\wÀ-ỹ])Đến(?=\s+\d)", "đến", text)
    return re.sub(r"[ \t]+", " ", text)


def _key(v) -> tuple:
    return ("s", v) if isinstance(v, str) else ("f", round(float(v), 6))


def facts(text: str) -> set[tuple]:
    return {(_key(v), u) for v, u in evalset.facts(clean(text))}


def gold_facts(text: str) -> set[tuple]:
    return {(_key(v), u) for v, u in evalset.facts(text)}


# ---------------------------------------------------------------- số liệu, chế tài

def so_lieu(item: dict, answer: str) -> dict | None:
    pairs = item.get("so_lieu") or []
    if not pairs:
        return None
    got = facts(answer)
    hit = [(_key(v), u) in got for v, u in pairs]
    return {"n": len(hit), "dung": sum(hit), "ty_le": sum(hit) / len(hit), "du": all(hit)}


def muc_phat(item: dict, answer: str) -> dict | None:
    lo, hi = item.get("muc_phat_min"), item.get("muc_phat_max")
    if lo is None:
        return None
    text = clean(answer)
    strict = (float(lo), float(hi), "đồng") in evalset.ranges(text)
    money = evalset.money_values(text)
    return {"dung_khung": strict, "co_ca_hai_muc": int(lo) in money and int(hi) in money}


def deduct_claims(answer: str) -> tuple[set[int], bool]:
    """(các số điểm bị trừ được nêu, có khẳng định trừ điểm không bị phủ định)."""
    text = clean(answer)
    nums = {int(m.group(1)) for m in DEDUCT_CLAIM.finditer(text) if "không" not in text[max(0, m.start() - 12):m.start()]}
    claim = any("không" not in text[max(0, m.start() - 12):m.start()] for m in DEDUCT_ANY.finditer(text))
    return nums, claim or bool(nums)


def diem_tru(item: dict, answer: str) -> bool | None:
    state = item.get("trang_thai_diem_tru")
    if state not in ("co", "khong_tru"):
        return None
    nums, claim = deduct_claims(answer)
    return int(item["diem_tru"]) in nums if state == "co" else not claim


def tuoc_gplx(item: dict, answer: str) -> bool | None:
    want = item.get("tuoc_gplx_thang")
    if not want:
        return None
    got = {(int(a), int(b)) for a, b in SUSPEND.findall(clean(answer))}
    return (int(want[0]), int(want[1])) in got


# ---------------------------------------------------------------- trích dẫn

def doc_aliases(doc_id: str) -> list[str]:
    """Cách văn bản được gọi trong câu trả lời: số hiệu "168/2024", "QCVN 41:2024", hoặc tên luật."""
    name = doc_name(doc_id)
    out = re.findall(r"\d+/\d{4}", name) + [f"QCVN {a}:{b}" for a, b in re.findall(r"QCVN (\d+):(\d{4})", name)]
    law = re.match(r"((?:Bộ )?[Ll]uật [^\d(]+?)\s*(?:\d|\(|$)", name)
    if law:
        out.append(law.group(1).strip())
    return out


def corpus_numbers(doc_ids) -> set[str]:
    out = set()
    for d in doc_ids:
        name = doc_name(d)
        out |= set(re.findall(r"\d+/\d{4}", name))
        out |= {f"QCVN{a}:{b}" for a, b in re.findall(r"QCVN (\d+):(\d{4})", name)}
    return out


def trich_dan(item: dict, answer: str) -> dict | None:
    doc = item.get("van_ban")
    if not doc:
        return None
    text = clean(answer)
    doc_ok = any(a.lower() in text.lower() for a in doc_aliases(doc))
    out = {"van_ban": doc_ok}
    dieu, khoan = item.get("dieu"), item.get("khoan")
    if dieu:
        d = re.escape(str(dieu))
        out["dieu"] = doc_ok and bool(re.search(rf"Điều\s+{d}(?![\wÀ-ỹ])", text, re.IGNORECASE))
        if khoan:
            k = re.escape(str(khoan))
            out["khoan"] = doc_ok and bool(
                re.search(rf"khoản\s+{k}\s*,?\s*Điều\s+{d}(?![\wÀ-ỹ])", text, re.IGNORECASE)
                or re.search(rf"Điều\s+{d}\s*,?\s*khoản\s+{k}(?![\wÀ-ỹ])", text, re.IGNORECASE))
    return out


def van_ban_ngoai_kho(answer: str, corpus: set[str]) -> list[str]:
    """Văn bản được trích mà không có trong kho 40 văn bản (thường là văn bản cũ đã hết hiệu lực hoặc bịa)."""
    text = clean(answer)
    out = [f"{n}/{y}" for n, y in DOC_NO.findall(text) if f"{n}/{y}" not in corpus]
    out += [f"QCVN {a}:{b}" for a, b in QCVN.findall(text) if f"QCVN{a}:{b}" not in corpus]
    if OLD_LAW.search(text):
        out.append("Luật Giao thông đường bộ (2008)")
    return sorted(set(out))


# ---------------------------------------------------------------- từ chối, RQ3, chất lượng sinh

def tu_choi(answer: str) -> bool:
    return bool(REFUSAL.search(clean(answer)[:REFUSAL_HEAD]))


def tu_choi_dung(item: dict, answer: str) -> bool | None:
    """Câu ngoài phạm vi: nói rõ không có căn cứ; câu về văn bản cũ thì nói văn bản đã hết hiệu lực cũng đạt."""
    if item["nhom_cau"] != "ngoai_pham_vi":
        return None
    return tu_choi(answer) or (item.get("kieu_ngoai") == "luat_cu" and bool(EXPIRED.search(clean(answer))))


def rq3(item: dict, answer: str) -> dict | None:
    """Câu sửa đổi: nêu số liệu riêng của bản mới, hay số liệu riêng của bản cũ (`dap_an_cu`)."""
    if item["nhom_cau"] != "sua_doi":
        return None
    new, old = gold_facts(item["dap_an"]), gold_facts(item.get("dap_an_cu") or "")
    got = facts(answer)
    only_new, only_old = new - old, old - new
    return {"do_duoc_moi": bool(only_new), "do_duoc_cu": bool(only_old),
            "theo_ban_moi": bool(only_new) and only_new <= got,
            "trich_ban_cu": bool(only_old) and bool(only_old & got)}


def tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(clean(text))]


def lap_vong(answer: str, n: int = 8, times: int = 3) -> bool:
    """Câu trả lời lặp một cụm n âm tiết từ `times` lần trở lên (lỗi lặp khi sinh greedy)."""
    t = tokens(answer)
    grams = Counter(tuple(t[i:i + n]) for i in range(len(t) - n + 1))
    return bool(grams) and max(grams.values()) >= times


def rouge_l(answer: str, reference: str) -> float:
    """ROUGE-L F1 trên âm tiết (chữ thường, bỏ dấu câu)."""
    a, b = tokens(answer), tokens(reference)
    if not a or not b:
        return 0.0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    lcs = prev[-1]
    if not lcs:
        return 0.0
    p, r = lcs / len(a), lcs / len(b)
    return 2 * p * r / (p + r)


def score_answer(item: dict, answer: str, corpus: set[str]) -> dict:
    """Mọi tiêu chí tự động cho một câu trả lời. Tiêu chí không áp dụng cho câu này có giá trị None."""
    return {"so_lieu": so_lieu(item, answer), "muc_phat": muc_phat(item, answer), "diem_tru": diem_tru(item, answer),
            "tuoc_gplx": tuoc_gplx(item, answer), "trich_dan": trich_dan(item, answer),
            "van_ban_ngoai_kho": van_ban_ngoai_kho(answer, corpus), "tu_choi": tu_choi(answer),
            "tu_choi_dung": tu_choi_dung(item, answer), "rq3": rq3(item, answer), "lap_vong": lap_vong(answer),
            "rouge_l": rouge_l(answer, item["dap_an"]) if item["nhom_cau"] != "ngoai_pham_vi" else None}
