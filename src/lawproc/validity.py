"""Ngoại lệ hiệu lực và hàm lọc bản ghi theo thời điểm."""

import csv
from datetime import date
from pathlib import Path


TYPES = {"gia_han", "hoan_ap_dung", "moc_trong_noi_dung"}


def load_exceptions(path: Path) -> list[dict]:
    """Đọc bảng ngoại lệ đã duyệt (có thể có BOM)."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def _valid_date(value: str) -> bool:
    try:
        return len(value) == 10 and date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def _under(uid: str, prefix: str) -> bool:
    return uid == prefix or uid.startswith(prefix + ":")


def attach_exceptions(records: list[dict], rows: list[dict]) -> None:
    """Gắn ngoại lệ vào phiên bản của đơn vị và mọi đơn vị con."""
    by_unit: dict[str, list[dict]] = {}
    for rec in records:
        by_unit.setdefault(rec["unit_id"], []).append(rec)
    for versions in by_unit.values():
        versions.sort(key=lambda rec: rec["valid_from"])

    problems: list[str] = []
    assignments: list[tuple[dict, dict]] = []
    for i, row in enumerate(rows, 1):
        uid = (row.get("unit_id") or "").strip()
        loai = (row.get("loai") or "").strip()
        tu = (row.get("tu_ngay") or "").strip()
        den = (row.get("den_ngay") or "").strip()
        issues = []
        if loai not in TYPES:
            issues.append(f"loại lạ {loai!r}")
        if loai == "gia_han" and not den:
            issues.append("thiếu den_ngay")
        if loai in {"hoan_ap_dung", "moc_trong_noi_dung"} and not tu:
            issues.append("thiếu tu_ngay")
        for field, value in (("tu_ngay", tu), ("den_ngay", den)):
            if value and not _valid_date(value):
                issues.append(f"{field} {value!r} không phải ngày YYYY-MM-DD")
        units = [key for key in by_unit if _under(key, uid)] if uid else []
        if not units:
            issues.append(f"không có bản ghi nào cho {uid!r}")
        if issues:
            problems.append(f"dòng {i} ({uid}): " + "; ".join(issues))
            continue

        base = {"loai": loai, "tu_ngay": tu, "den_ngay": den,
                "dieu_kien": row.get("dieu_kien") or "", "can_cu": row.get("can_cu") or ""}
        hit = 0
        for unit in units:
            versions = by_unit[unit]
            if loai == "gia_han":
                if versions[-1]["valid_to"] is not None:
                    assignments.append((versions[-1], dict(base, vai_tro="gia_han")))
                    hit += 1
            elif loai == "hoan_ap_dung":
                before = [rec for rec in versions if rec["valid_from"] < tu]
                if before:
                    new = before[-1]
                    assignments.append((new, dict(base, vai_tro="moi")))
                    hit += 1
                    for old in versions:
                        if old is not new and old["valid_to"] == new["valid_from"]:
                            assignments.append((old, dict(base, vai_tro="cu")))
            else:
                for rec in versions:
                    assignments.append((rec, dict(base, vai_tro="moc")))
                    hit += 1
        if not hit:
            problems.append(f"dòng {i} ({uid}): {loai} không áp được vào bản ghi nào")
    if problems:
        raise ValueError(f"{len(problems)} lỗi trong ngoại lệ hiệu lực:\n" +
                         "\n".join(f"  - {problem}" for problem in problems))

    for rec in records:
        rec["hl_ngoai_le"] = []
    for rec, ex in assignments:
        rec["hl_ngoai_le"].append(ex)


def in_force_at(rec: dict, t: str) -> tuple[bool, str | None]:
    """Trả trạng thái tại ngày t và điều kiện đi kèm, nếu có."""
    if not _valid_date(t):
        raise ValueError(f"Ngày truy vấn không hợp lệ: {t!r}")
    if rec.get("trang_thai") == "bai_bo":  # Điều chỉ còn dòng "(được bãi bỏ)" trong văn bản hợp nhất
        return False, None
    exs = rec.get("hl_ngoai_le") or []
    closed = rec["valid_to"] is not None and rec["valid_to"] <= t
    live = rec["valid_from"] <= t and not closed
    notes: list[str] = []
    if rec["valid_from"] <= t:
        for ex in exs:
            if closed and ex["vai_tro"] == "gia_han" and t < ex["den_ngay"]:
                live = True
                notes.append(ex["dieu_kien"])
            elif closed and ex["vai_tro"] == "cu" and t < ex["tu_ngay"]:
                live = True
                notes.append(ex["dieu_kien"])
    if not live:
        return False, None
    for ex in exs:
        if ex["vai_tro"] in ("moi", "moc") and t < ex["tu_ngay"]:
            if ex["vai_tro"] == "moi" and not ex["dieu_kien"]:
                return False, None
            notes.append(ex["dieu_kien"])
    condition = "; ".join(note for note in notes if note)
    return True, condition or None
