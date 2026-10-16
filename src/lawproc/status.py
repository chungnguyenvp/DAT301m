"""Trạng thái bản ghi ngoài ngày hiệu lực: Điều đã bãi bỏ, phụ lục thiếu nội dung, phụ lục bị thay thế.

- `trang_thai = "bai_bo"`: Điều chỉ còn dòng "(được bãi bỏ)" trong văn bản hợp nhất; `in_force_at` coi là hết hiệu lực.
- `thieu_noi_dung`: lý do (từ `data/content_gaps.csv` đã duyệt) khi phần nguồn là ảnh chưa có chữ.
- `pl_thay_the`: danh sách lần phụ lục này bị thay bởi phụ lục của văn bản khác (`data/annex_replacements.csv`, chỉ
  dòng `duyet = duyet`). Thay toàn bộ thì đóng bản cũ tại `tu_ngay`; thay một phần mẫu thì chỉ ghi chú.
"""
import csv
import re
from datetime import date
from pathlib import Path

ABOLISHED = re.compile(r"^\(?\s*(?:được|đã được|đã bị|bị)\s+bãi bỏ\s*\)?\.?$", re.IGNORECASE)
SCOPES = {"toan_bo", "mot_phan"}


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def mark_status(records: list[dict], gaps: list[dict]) -> None:
    ids = {r["unit_id"] for r in records}
    unknown = [g["unit_id"] for g in gaps if g["unit_id"] not in ids]
    if unknown:
        raise ValueError(f"content_gaps: đơn vị không có trong dữ liệu: {unknown}")
    reason = {g["unit_id"]: g["ly_do"].strip() for g in gaps}
    for r in records:
        placeholder = not (r["text"] or "").strip() and ABOLISHED.match((r["title"] or "").strip())
        r["trang_thai"] = "bai_bo" if r["level"] == "dieu" and placeholder else None
        r["thieu_noi_dung"] = reason.get(r["unit_id"])


def _valid_date(value: str) -> bool:
    try:
        return len(value) == 10 and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def check_annex_replacements(rows: list[dict], records: list[dict]) -> list[dict]:
    """Kiểm tra mọi dòng (kể cả chưa duyệt) và trả các dòng đã duyệt."""
    annex = {r["unit_id"] for r in records if r["level"] == "phu_luc"}
    ids = {r["unit_id"] for r in records}
    problems = []
    for i, row in enumerate(rows, 2):
        for key in ("pl_cu", "pl_moi"):
            uid = row[key].strip()
            if uid not in ids:
                problems.append(f"dòng {i}: {key} {uid!r} không có trong dữ liệu")
            elif uid not in annex:
                problems.append(f"dòng {i}: {key} {uid!r} không phải phụ lục")
        if row["pham_vi"].strip() not in SCOPES:
            problems.append(f"dòng {i}: pham_vi {row['pham_vi']!r} phải là {sorted(SCOPES)}")
        if not _valid_date(row["tu_ngay"].strip()):
            problems.append(f"dòng {i}: tu_ngay {row['tu_ngay']!r} không phải YYYY-MM-DD")
        if row["duyet"].strip() not in ("", "duyet"):
            problems.append(f"dòng {i}: duyet {row['duyet']!r} chỉ được để trống hoặc 'duyet'")
    if problems:
        raise ValueError("annex_replacements:\n" + "\n".join(problems))
    return [row for row in rows if row["duyet"].strip() == "duyet"]


def apply_annex_replacements(records: list[dict], approved: list[dict]) -> None:
    by_unit: dict[str, list[dict]] = {}
    for r in records:
        r.setdefault("pl_thay_the", [])
        by_unit.setdefault(r["unit_id"], []).append(r)
    for row in approved:
        tu = row["tu_ngay"].strip()
        link = {"bang": row["pl_moi"].strip(), "tu_ngay": tu, "pham_vi": row["pham_vi"].strip(),
                "chi_tiet": row["chi_tiet"].strip(), "can_cu": row["can_cu"].strip()}
        for r in by_unit[row["pl_cu"].strip()]:
            if r["valid_from"] >= tu or (r["valid_to"] is not None and r["valid_to"] <= tu):
                continue  # phiên bản không còn sống tại mốc thay thế
            r["pl_thay_the"].append(link)
            if link["pham_vi"] == "toan_bo":
                r["valid_to"] = tu
