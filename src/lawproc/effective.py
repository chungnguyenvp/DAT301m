import re

from lawproc.structure import Unit

HL_DATE = re.compile(
    r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
    re.IGNORECASE,
)
HL_SIGN = re.compile(r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+ký", re.IGNORECASE)


def _scan(text: str) -> dict:
    dates = [f"{y}-{int(m):02d}-{int(d):02d}" for d, m, y in HL_DATE.findall(text)]
    sign = bool(HL_SIGN.search(text))
    hit = HL_DATE.search(text) or HL_SIGN.search(text)
    snippet = text[max(0, hit.start() - 80): hit.end() + 20].replace("\n", " ") if hit else ""
    return {"dates": dates, "ngay_ky": sign, "trich_dan": snippet.strip()}


def find_effective(units: list[Unit]) -> dict:
    effect_dieu = [u.dieu for u in units if u.level == "dieu" and "hiệu lực" in u.title.lower()]
    if effect_dieu:
        text = "\n".join(u.text for u in units if u.dieu in effect_dieu and u.level in ("dieu", "khoan", "diem"))
        r = _scan(text)
        if r["dates"] or r["ngay_ky"]:
            return r
    return _scan("\n".join(u.text for u in units if u.level != "phu_luc"))


def decide_effective(doc_id: str, ngay_ban_hanh: str, hl_congbao: str, found: dict) -> dict:
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
