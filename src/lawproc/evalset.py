"""Đọc đơn vị luật theo thời điểm, suy nhãn chế tài và kiểm tra bộ eval `data/eval/eval_v1.jsonl`."""

import json
import re
from collections import Counter
from pathlib import Path

from lawproc import config
from lawproc.validity import in_force_at

EVAL = config.DATA / "eval"
NHOM_CAU = {"thuong", "sua_doi", "ngoai_pham_vi", "bien_the"}
TAP = {"dev", "test"}
KIEU_BIEN_THE = {"viet_tat", "khong_dau", "ke_chuyen", "tu_doi_thuong"}
TRANG_THAI_DIEM_TRU = {"co", "khong_tru", "khong_ap_dung"}
REQUIRED = ("id", "tap", "nhom_cau", "cau_hoi", "dap_an", "chu_de", "loai_cau", "ngay_hoi", "can_cu")

NUM = r"(\d+(?:[.,]\d+)*)"
_PAREN = r"(?:\s*\([^)\d]*\))?"  # "40 (bốn mươi) triệu đồng"
MONEY = re.compile(NUM + _PAREN + r"\s*(triệu|nghìn|tỷ)?\s*đồng")
UNITS = {
    "ngày làm việc": "ngày làm việc", "ngày": "ngày", "giờ làm việc": "giờ làm việc", "giờ": "giờ", "tháng": "tháng", "năm": "năm",
    "phút": "phút", "câu": "câu", "điểm": "điểm", "%": "%", "km/h": "km/h", "mét": "m", "m": "m", "tuổi": "tuổi",
    "chỗ": "chỗ", "lần": "lần", "tấn": "tấn", "kg": "kg", "mm": "mm", "cm": "cm", "kv": "kv",
}
UNIT = re.compile(NUM + r"\s*(" + "|".join(sorted(map(re.escape, UNITS), key=len, reverse=True)) + r")(?![\wÀ-ỹ])",
                  re.IGNORECASE)
RATIO = re.compile(r"(?<![\d/])(\d+)/(\d+)\s*(điểm|câu)(?![\wÀ-ỹ])")  # "27/30 điểm": giữ cả ngưỡng
_RANGE_UNIT = r"(đồng|tháng|năm|ngày làm việc|ngày|giờ|km/h|tuổi)"
RANGE = re.compile(r"từ\s+" + NUM + _PAREN + r"\s*(triệu|nghìn|tỷ)?\s*" + _RANGE_UNIT + r"\s+đến\s+(?:dưới\s+)?"
                   + NUM + _PAREN + r"\s*(triệu|nghìn|tỷ)?\s*" + _RANGE_UNIT)
BARE = re.compile(r"(?<![\w/])" + NUM + r"(?![\w/])")
LOOSE_UNITS = {"km/h", "m", "%"}  # bảng biểu thường ghi đơn vị ở tiêu đề cột
MULT = {None: 1, "nghìn": 1_000, "triệu": 1_000_000, "tỷ": 1_000_000_000}

DEDUCT = re.compile(r"trừ điểm giấy phép lái xe (\d+) điểm")
SUSPEND = re.compile(r"tước quyền sử dụng giấy phép lái xe từ (\d+) tháng đến (\d+) tháng")
FINE = re.compile(r"[Pp]hạt tiền từ (\d{1,3}(?:\.\d{3})+) đồng đến (\d{1,3}(?:\.\d{3})+) đồng")
CITE = re.compile(r"(?:điểm ([a-zđ]) )?(?:khoản (\d+[a-z]?) )?Điều (\d+[a-z]?)")
LAW_NAMES = (
    ("Luật Trật tự, an toàn giao thông đường bộ", "luat_36_2024"), ("Luật Đường bộ", "luat_35_2024"),
    ("Bộ luật Dân sự", "blds_2015"), ("Bộ luật Hình sự", "vbhn_135_2025_blhs"),
    ("Luật Xử lý vi phạm hành chính", "vbhn_90_2026_xlvphc"),
)
DOC_NO = re.compile(r"^\s*(?:của\s+)?(Nghị định|Thông tư)\s+(?:số\s+)?(\d+)/(\d{4})")


def load_versions(path: Path | None = None) -> list[dict]:
    path = path or config.PROCESSED / "legal_units_versioned.jsonl"
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def load_eval(path: Path | None = None) -> list[dict]:
    path = path or EVAL / "eval_v1.jsonl"
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def by_version(records: list[dict]) -> dict[str, dict]:
    return {r["version_id"]: r for r in records}


def live_versions(records: list[dict], day: str) -> dict[str, list[dict]]:
    """Mọi phiên bản có hiệu lực tại `day`, nhóm theo unit_id (có thể nhiều nhánh có điều kiện)."""
    out: dict[str, list[dict]] = {}
    for r in records:
        if in_force_at(r, day)[0]:
            out.setdefault(r["unit_id"], []).append(r)
    return out


def ancestors(unit_id: str) -> list[str]:
    """`doc:d7:k2:h` -> [`doc:d7`, `doc:d7:k2`]; phụ lục và Điều không có cha trong cùng văn bản."""
    parts = unit_id.split(":")
    return [":".join(parts[:i]) for i in range(2, len(parts))]


def number(raw: str) -> float | None:
    """`1.400.000` -> 1400000; `7,5` -> 7.5; `02` -> 2; số mục kiểu `41.3.1` -> None."""
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        return float(raw.replace(".", ""))
    if re.fullmatch(r"\d+(?:,\d+)?", raw):
        return float(raw.replace(",", "."))
    return None


def money_values(text: str) -> set[int]:
    return {round(v * MULT[m.lower() if m else None]) for n, m in MONEY.findall(text) if (v := number(n)) is not None}


def facts(text: str) -> set[tuple]:
    """Các cặp (giá trị, đơn vị) trong văn bản; tiền quy về đồng; tỷ số "27/30 điểm" giữ nguyên dạng "27/30"."""
    out: set[tuple] = {(float(v), "đồng") for v in money_values(text)}
    spans = []
    for m in RATIO.finditer(text):
        out.add((f"{int(m.group(1))}/{int(m.group(2))}", m.group(3)))
        spans.append(m.span())
    for m in UNIT.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        if (v := number(m.group(1))) is not None:
            out.add((v, UNITS[m.group(2).lower()]))
    return out


def ranges(text: str) -> set[tuple[float, float, str]]:
    """Khung "từ X đến Y" cùng đơn vị (tiền quy về đồng)."""
    out = set()
    for n1, m1, u1, n2, m2, u2 in RANGE.findall(text):
        a, b = number(n1), number(n2)
        if a is None or b is None or u1 != u2:
            continue
        if u1 == "đồng":
            a, b = a * MULT[m1 or None], b * MULT[m2 or None]
        out.add((a, b, u1))
    return out


def bare_numbers(text: str) -> set[float]:
    return {v for n in BARE.findall(text) if (v := number(n)) is not None}


def ref_list(text: str) -> set[tuple[str, str | None]]:
    """Danh sách viện dẫn kiểu "điểm b khoản 3; khoản 5; điểm b, điểm c khoản 6 Điều này" -> {(khoản, điểm)}."""
    out: set[tuple[str, str | None]] = set()
    for seg in text.split(";"):
        points: list[str] = []
        for kind, value in re.findall(r"(điểm|khoản)\s+([0-9a-zđ]+)", seg):
            if kind == "điểm":
                points.append(value)
            else:
                out |= {(value, p) for p in points} if points else {(value, None)}
                points = []
    return out


def is_sanction_clause(text: str) -> bool:
    return text.startswith("Thực hiện hành vi") and bool(DEDUCT.search(text) or SUSPEND.search(text))


def primary_unit(item: dict) -> str | None:
    if not (item.get("van_ban") and item.get("dieu")):
        return None
    uid = f"{item['van_ban']}:d{item['dieu']}"
    if item.get("khoan"):
        uid += f":k{item['khoan']}"
        if item.get("diem"):
            uid += f":{item['diem']}"
    return uid


def covers(refs: set[tuple[str, str | None]], uid: str) -> bool:
    parts = uid.split(":")
    if len(parts) < 3:
        return False
    khoan = parts[2][1:]
    diem = parts[3] if len(parts) > 3 else None
    return (khoan, None) in refs or (diem is not None and (khoan, diem) in refs)


def sanctions(uid: str, live: dict[str, list[dict]]) -> dict:
    """Trừ điểm, tước GPLX mà các khoản "Thực hiện hành vi…" của cùng Điều gắn cho đơn vị `uid`."""
    prefix = ":".join(uid.split(":")[:2]) + ":"
    out: dict = {"diem_tru": None, "tuoc_gplx_thang": None, "co_khoan_che_tai": False, "nguon": []}
    for unit, versions in live.items():
        if not unit.startswith(prefix):
            continue
        for r in versions:
            if not is_sanction_clause(r["text"]):
                continue
            if DEDUCT.search(r["text"]):
                out["co_khoan_che_tai"] = True
            if not covers(ref_list(r["text"].split("Điều này")[0]), uid):
                continue
            if m := DEDUCT.search(r["text"]):
                out["diem_tru"] = int(m.group(1))
                out["nguon"].append(r["version_id"])
            if m := SUSPEND.search(r["text"]):
                out["tuoc_gplx_thang"] = [int(m.group(1)), int(m.group(2))]
                out["nguon"].append(r["version_id"])
    return out


def lead_fine(uid: str, live: dict[str, list[dict]]) -> tuple[int, int] | None:
    """Khung phạt cá nhân ở câu dẫn của Khoản chứa đơn vị `uid` (lấy khung đầu tiên)."""
    for parent in [uid] + ancestors(uid)[::-1]:
        for r in live.get(parent, []):
            if m := FINE.search(r["text"]):
                return int(m.group(1).replace(".", "")), int(m.group(2).replace(".", ""))
    return None


def _cited_texts(vids: list[str], versions: dict[str, dict], index: dict[str, list[dict]], day: str) -> str:
    texts = []
    for vid in vids:
        rec = versions.get(vid)
        if rec is None:
            continue
        texts.append(rec["text"])
        for parent in ancestors(rec["unit_id"]):
            texts += [r["text"] for r in index.get(parent, []) if in_force_at(r, day)[0]]
    return "\n".join(texts)


def _number_problems(iid: str, field: str, answer: str, cited: str, question: str) -> list[str]:
    known = facts(cited)
    bare = bare_numbers(cited)
    asked = bare_numbers(question)
    out = []
    known_ranges = ranges(cited) | ranges(question)
    for lo, hi, unit in sorted(ranges(answer)):
        if (lo, hi, unit) not in known_ranges:
            out.append(f"{iid}: {field} có khung từ {lo:,.0f} đến {hi:,.0f} {unit} không có trong căn cứ")
    for value, unit in sorted(facts(answer), key=str):
        if (value, unit) in known or value in asked or (unit in LOOSE_UNITS and value in bare):
            continue
        shown = value if isinstance(value, str) else f"{value:,.0f}" if unit == "đồng" else f"{value:g}"
        out.append(f"{iid}: {field} có số liệu {shown} {unit} không có trong căn cứ")
    return out


def _citation_problems(iid: str, field: str, answer: str, docs: set[str], live_units: set[str]) -> list[str]:
    out = []
    for m in CITE.finditer(answer):
        diem, khoan, dieu = m.groups()
        tail = answer[m.end():m.end() + 80]
        target = docs
        named = next((doc for name, doc in LAW_NAMES if tail.lstrip(" (").startswith(name)), None)
        if dn := DOC_NO.match(tail):
            kind = "nd" if dn.group(1) == "Nghị định" else "tt"
            named = next((d for d in docs if d.startswith(f"{kind}_{dn.group(2)}_{dn.group(3)}")), "khac")
        if named:
            if named not in docs:
                continue  # viện dẫn sang văn bản không nằm trong căn cứ của câu
            target = {named}
        parts = [f"d{dieu}"] + ([f"k{khoan}"] if khoan else []) + ([diem] if diem else [])
        if not any(f"{doc}:{':'.join(parts)}" in live_units for doc in target):
            out.append(f"{iid}: {field} trích dẫn \"{m.group(0)}\" không trỏ tới đơn vị có hiệu lực trong căn cứ")
    return out


def check_items(items: list[dict], records: list[dict]) -> list[str]:
    """Trả danh sách lỗi; rỗng nghĩa là bộ eval khớp dữ liệu `data-v1`."""
    problems: list[str] = []
    versions = by_version(records)
    index: dict[str, list[dict]] = {}
    for r in records:
        index.setdefault(r["unit_id"], []).append(r)
    live_cache: dict[str, dict[str, list[dict]]] = {}

    def live_at(day: str) -> dict[str, list[dict]]:
        if day not in live_cache:
            live_cache[day] = live_versions(records, day)
        return live_cache[day]

    ids = Counter(item.get("id") for item in items)
    problems += [f"id trùng: {k}" for k, n in ids.items() if n > 1]
    questions = Counter(re.sub(r"\s+", " ", item.get("cau_hoi", "")).strip().lower() for item in items)
    problems += [f"câu hỏi trùng: {k[:60]}" for k, n in questions.items() if n > 1]
    by_id = {item.get("id"): item for item in items}
    for item in items:
        iid = item.get("id", "?")
        missing = [k for k in REQUIRED if k not in item]
        if missing:
            problems.append(f"{iid}: thiếu trường {missing}")
            continue
        if item["tap"] not in TAP:
            problems.append(f"{iid}: tap lạ {item['tap']!r}")
        if item["nhom_cau"] not in NHOM_CAU:
            problems.append(f"{iid}: nhom_cau lạ {item['nhom_cau']!r}")
            continue
        day = item["ngay_hoi"]
        if item["nhom_cau"] == "ngoai_pham_vi":
            if item["can_cu"]:
                problems.append(f"{iid}: câu ngoài phạm vi không được có căn cứ")
            if item.get("hanh_vi") != "tu_choi":
                problems.append(f"{iid}: câu ngoài phạm vi phải có hanh_vi = tu_choi")
            continue
        if not item["can_cu"]:
            problems.append(f"{iid}: thiếu căn cứ")
        for vid in item["can_cu"]:
            rec = versions.get(vid)
            if rec is None:
                problems.append(f"{iid}: không có phiên bản {vid}")
                continue
            if not in_force_at(rec, day)[0]:
                problems.append(f"{iid}: {vid} không có hiệu lực tại {day}")
            if not rec["trong_pham_vi"]:
                problems.append(f"{iid}: {vid} nằm ngoài phạm vi BLDS/BLHS")
            if rec["doc_id"] in config.NON_LEGAL:
                problems.append(f"{iid}: {vid} thuộc tài liệu đề thi, không phải văn bản luật")
        first = versions.get(item["can_cu"][0]) if item["can_cu"] else None
        if first is not None and item.get("van_ban") and item["van_ban"] != first["doc_id"]:
            problems.append(f"{iid}: van_ban {item['van_ban']} khác căn cứ đầu {first['doc_id']}")
        live = live_at(day)
        cited = _cited_texts(item["can_cu"], versions, index, day)
        amounts = money_values(cited)
        lo, hi = item.get("muc_phat_min"), item.get("muc_phat_max")
        if lo is not None and hi is not None and lo > hi:
            problems.append(f"{iid}: muc_phat_min {lo} lớn hơn muc_phat_max {hi}")
        for key in ("muc_phat_min", "muc_phat_max"):
            value = item.get(key)
            if value is not None and value not in amounts:
                problems.append(f"{iid}: {key} {value} không xuất hiện trong căn cứ")
        if lo is not None and hi is not None and (float(lo), float(hi), "đồng") not in ranges(item["dap_an"]):
            problems.append(f"{iid}: đáp án không nêu khung phạt {lo:,}–{hi:,} đồng như nhãn")
        if item.get("diem_tru") is not None and (float(item["diem_tru"]), "điểm") not in facts(cited):
            problems.append(f"{iid}: diem_tru {item['diem_tru']} không xuất hiện trong căn cứ")
        if item["nhom_cau"] != "bien_the":
            problems += _number_problems(iid, "dap_an", item["dap_an"], cited, item["cau_hoi"])
            docs = {v.split(":")[0] for v in item["can_cu"]}
            problems += _citation_problems(iid, "dap_an", item["dap_an"], docs, set(live))
        # Chế tài bổ sung phải dẫn chiếu đúng hành vi đang hỏi và khớp nhãn.
        uid = primary_unit(item)
        if uid and item["nhom_cau"] in ("thuong", "sua_doi"):
            for vid in item["can_cu"]:
                rec = versions.get(vid)
                if rec and is_sanction_clause(rec["text"]) and rec["unit_id"].startswith(":".join(uid.split(":")[:2]) + ":") \
                        and not covers(ref_list(rec["text"].split("Điều này")[0]), uid):
                    problems.append(f"{iid}: căn cứ {vid} quy định chế tài cho hành vi khác, không phải {uid}")
            law = sanctions(uid, live)
            if law["diem_tru"] != item.get("diem_tru") and (law["diem_tru"] is not None or law["co_khoan_che_tai"]):
                problems.append(f"{iid}: diem_tru {item.get('diem_tru')} khác luật ({law['diem_tru']})")
            if law["diem_tru"] is not None and "trừ" not in item["dap_an"]:
                problems.append(f"{iid}: đáp án thiếu chế tài trừ {law['diem_tru']} điểm")
            if law["tuoc_gplx_thang"] != item.get("tuoc_gplx_thang"):
                problems.append(f"{iid}: tuoc_gplx_thang {item.get('tuoc_gplx_thang')} khác luật ({law['tuoc_gplx_thang']})")
            if law["tuoc_gplx_thang"] is not None and "tước" not in item["dap_an"]:
                problems.append(f"{iid}: đáp án thiếu chế tài tước giấy phép lái xe")
            if item.get("trang_thai_diem_tru") not in TRANG_THAI_DIEM_TRU:
                problems.append(f"{iid}: trang_thai_diem_tru lạ {item.get('trang_thai_diem_tru')!r}")
        if item["nhom_cau"] == "sua_doi":
            for key in ("dap_an_cu", "can_cu_cu", "ngay_cu"):
                if not item.get(key):
                    problems.append(f"{iid}: câu sửa đổi thiếu {key}")
            old_day = item.get("ngay_cu", "")
            for vid in item.get("can_cu_cu", []):
                rec = versions.get(vid)
                if rec is None:
                    problems.append(f"{iid}: không có phiên bản cũ {vid}")
                    continue
                if not in_force_at(rec, old_day)[0]:
                    problems.append(f"{iid}: {vid} không có hiệu lực tại ngày cũ {old_day}")
                if in_force_at(rec, day)[0]:
                    problems.append(f"{iid}: phiên bản cũ {vid} vẫn còn hiệu lực tại {day}")
            old_cited = _cited_texts(item.get("can_cu_cu", []), versions, index, old_day)
            problems += _number_problems(iid, "dap_an_cu", item.get("dap_an_cu", ""), old_cited, item["cau_hoi"])
            old_docs = {v.split(":")[0] for v in item.get("can_cu_cu", [])}
            problems += _citation_problems(iid, "dap_an_cu", item.get("dap_an_cu", ""), old_docs, set(live_at(old_day)))
        if item["nhom_cau"] == "bien_the":
            base = by_id.get(item.get("goc_id"))
            if base is None or base["nhom_cau"] != "thuong":
                problems.append(f"{iid}: goc_id phải trỏ tới câu thường")
            else:
                if base["can_cu"] != item["can_cu"]:
                    problems.append(f"{iid}: căn cứ khác câu gốc {base['id']}")
                if base["tap"] != item["tap"]:
                    problems.append(f"{iid}: khác tập với câu gốc {base['id']}")
            if item.get("kieu_bien_the") not in KIEU_BIEN_THE:
                problems.append(f"{iid}: kieu_bien_the lạ {item.get('kieu_bien_the')!r}")
    return problems
