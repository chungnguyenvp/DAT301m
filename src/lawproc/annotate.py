"""Gắn nhãn nội dung thay đổi, loại phụ lục và chất lượng chữ cho bản ghi."""
import csv
import re
from collections import defaultdict
from pathlib import Path

from lawproc import config
from lawproc.quality import syllable_error_rate

# "Mẫu" có dấu (mọi kiểu chữ), hoặc "MAU" in hoa mất dấu do OCR; không khớp tên tỉnh "Cà Mau"/"CÀ MAU".
FORM_WORD = re.compile(r"(?i:\bmẫu\b)|(?<!CÀ )(?<!CA )\bMAU\b")
FILL_LINE = re.compile(r"[.…]{4,}")
FILL_SHARE = 0.3
HEAD_CHARS = 300
ANNEX_TYPES = {"mau_bieu", "noi_dung"}


def mark_content_change(records: list[dict]) -> None:
    """So từng phiên bản với phiên bản liền trước của cùng đơn vị."""
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_unit[r["unit_id"]].append(r)
    for recs in by_unit.values():
        recs.sort(key=lambda r: r["valid_from"])
        prev = None
        for r in recs:
            r["noi_dung_doi"] = prev is None or (r["title"], r["text"]) != (prev["title"], prev["text"])
            prev = r


def annex_type(title: str, text: str) -> tuple[str, str]:
    """Nhận diện mẫu qua tiêu đề, phần đầu hoặc tỷ lệ dòng để điền."""
    head = f"{title}\n{text[:HEAD_CHARS]}"
    if FORM_WORD.search(head):
        return "mau_bieu", "tiêu đề có chữ Mẫu"
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and sum(bool(FILL_LINE.search(line)) for line in lines) / len(lines) >= FILL_SHARE:
        return "mau_bieu", "nhiều dòng điền"
    return "noi_dung", ""


def load_annex_overrides(path: Path, records: list[dict]) -> dict[str, str]:
    """Đọc bản duyệt và báo lỗi ở dòng không khớp, trùng hoặc sai loại."""
    if not path.exists():
        return {}
    annex_ids = {r["unit_id"] for r in records if r["level"] == "phu_luc"}
    overrides: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        if not reader.fieldnames or not {"unit_id", "loai_phu_luc", "ghi_chu"} <= set(reader.fieldnames):
            raise ValueError(f"{path}: thiếu cột unit_id, loai_phu_luc hoặc ghi_chu")
        for line_no, row in enumerate(reader, start=2):
            uid = row["unit_id"].strip()
            kind = row["loai_phu_luc"].strip()
            if uid in overrides:
                raise ValueError(f"{path}:{line_no}: unit_id trùng: {uid}")
            if uid not in annex_ids:
                raise ValueError(f"{path}:{line_no}: unit_id không phải phụ lục: {uid}")
            if kind not in ANNEX_TYPES:
                raise ValueError(f"{path}:{line_no}: loai_phu_luc không hợp lệ: {kind}")
            overrides[uid] = kind
    return overrides


def annotate_records(records: list[dict], overrides: dict[str, str]) -> list[dict]:
    """Gắn nhãn trên mọi bản ghi; trả các phụ lục duy nhất để người dùng duyệt."""
    annex_ids = {r["unit_id"] for r in records if r["level"] == "phu_luc"}
    unknown = set(overrides) - annex_ids
    invalid = {uid: kind for uid, kind in overrides.items() if kind not in ANNEX_TYPES}
    if unknown or invalid:
        raise ValueError(f"Ghi đè loại phụ lục không hợp lệ: unit_id={sorted(unknown)}, loại={invalid}")
    mark_content_change(records)
    rows: dict[str, dict] = {}
    for r in records:
        rate = syllable_error_rate(r["text"])
        r["ty_le_am_tiet_loi"] = rate
        words = len(re.findall(r"\w+", r["text"]))
        r["chat_luong"] = "kem" if rate > config.QUALITY_BAD and words >= config.QUALITY_MIN_WORDS else "ok"
        if r["level"] != "phu_luc":
            r["loai_phu_luc"] = None
            continue
        loai, ly_do = (overrides[r["unit_id"]], "ghi đè") if r["unit_id"] in overrides else annex_type(r["title"], r["text"])
        r["loai_phu_luc"] = loai
        rows.setdefault(r["unit_id"], {
            "unit_id": r["unit_id"], "doc_id": r["doc_id"], "title": r["title"][:120],
            "loai_phu_luc": loai, "ly_do": ly_do,
            "ty_le_am_tiet_loi": rate, "chat_luong": r["chat_luong"],
        })
    return list(rows.values())
