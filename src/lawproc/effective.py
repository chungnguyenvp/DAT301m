import re

from lawproc.structure import Unit

HL_DATE = re.compile(
    r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+"
    r"(?:(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})|(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4}))",
    re.IGNORECASE,
)
HL_SIGN = re.compile(r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+ký", re.IGNORECASE)
QUOTED = re.compile(r"“.*?”", re.DOTALL)  # nội dung được trích dẫn (văn bản sửa đổi), không phải hiệu lực của văn bản này
EFFECT_TITLE_KEYS = ("hiệu lực", "thi hành")


def _scan(text: str) -> dict:
    text = QUOTED.sub(" ", text)
    dates = []
    for m in HL_DATE.finditer(text):
        if m.group(1) is not None:
            d, mo, y = m.group(1), m.group(2), m.group(3)
        else:
            d, mo, y = m.group(4), m.group(5), m.group(6)
        dates.append(f"{y}-{int(mo):02d}-{int(d):02d}")
    sign = bool(HL_SIGN.search(text))
    hit = HL_DATE.search(text) or HL_SIGN.search(text)
    snippet = text[max(0, hit.start() - 80): hit.end() + 20].replace("\n", " ") if hit else ""
    return {"dates": dates, "ngay_ky": sign, "trich_dan": snippet.strip()}


def find_effective(units: list[Unit]) -> dict:
    effect_dieu = [
        u.dieu for u in units
        if u.level == "dieu" and any(k in u.title.lower() for k in EFFECT_TITLE_KEYS)
    ]
    if effect_dieu:
        text = "\n".join(u.text for u in units if u.dieu in effect_dieu and u.level in ("dieu", "khoan", "diem"))
        r = _scan(text)
        if r["dates"] or r["ngay_ky"]:
            return {**r, "tu_dieu_hieu_luc": True}
    r = _scan("\n".join(u.text for u in units if u.level != "phu_luc"))
    return {**r, "tu_dieu_hieu_luc": False}


def _base_decision(doc_id: str, ngay_ban_hanh: str, hl_congbao: str, found: dict) -> dict:
    first = found["dates"][0] if found["dates"] else ""
    vbhn = doc_id.startswith("vbhn_")
    if first and hl_congbao:
        same = first == hl_congbao
        return {"hl_chot": first, "nguon": "khop" if same else "lech", "can_duyet": vbhn or not same}
    if first:
        return {"hl_chot": first, "nguon": "van_ban", "can_duyet": vbhn}
    if hl_congbao:
        return {"hl_chot": hl_congbao, "nguon": "congbao", "can_duyet": vbhn}
    if found["ngay_ky"]:
        return {"hl_chot": ngay_ban_hanh, "nguon": "ngay_ky", "can_duyet": True}
    return {"hl_chot": "", "nguon": "khong_thay", "can_duyet": True}


def decide_effective(doc_id: str, ngay_ban_hanh: str, hl_congbao: str, found: dict) -> dict:
    r = _base_decision(doc_id, ngay_ban_hanh, hl_congbao, found)
    doubtful = (
        (found["ngay_ky"] and bool(found["dates"]))       # có cả điều khoản ngày ký lẫn ngày cụ thể
        or len(set(found["dates"])) > 1                    # nhiều ngày khác nhau trong điều hiệu lực
        or not found.get("tu_dieu_hieu_luc", True)         # không lấy được từ Điều hiệu lực, quét toàn văn
    )
    if doubtful:
        r["can_duyet"] = True
    return r
