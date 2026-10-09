import csv
from pathlib import Path

import pytest

from lawproc.validity import attach_exceptions, in_force_at, load_exceptions


def _r(uid, vf, vt):
    return {"unit_id": uid, "valid_from": vf, "valid_to": vt}


def _row(uid, loai, tu="", den="", dk=""):
    return {"unit_id": uid, "loai": loai, "tu_ngay": tu, "den_ngay": den,
            "dieu_kien": dk, "can_cu": "x:d1", "ghi_chu": ""}


def test_plain_record_follows_exclusive_end():
    rec = _r("a:d1", "2025-01-01", "2026-07-01")
    attach_exceptions([rec], [])
    assert rec["hl_ngoai_le"] == []
    assert in_force_at(rec, "2026-06-30") == (True, None)
    assert in_force_at(rec, "2026-07-01") == (False, None)


def test_extension_applies_to_last_closed_version_and_children():
    old = _r("t:d4:k1", "2025-01-01", "2026-01-01")
    new = _r("t:d4:k1", "2026-01-01", "2026-07-01")
    child = _r("t:d4:k1:a", "2025-01-01", "2026-07-01")
    other = _r("t:d4:k10", "2025-01-01", "2026-07-01")
    attach_exceptions([old, new, child, other], [_row("t:d4:k1", "gia_han", den="2027-03-01", dk="Chỉ phần A")])
    assert in_force_at(old, "2026-10-01") == (False, None)
    assert in_force_at(new, "2027-02-28") == (True, "Chỉ phần A")
    assert in_force_at(child, "2027-02-28") == (True, "Chỉ phần A")
    assert in_force_at(new, "2027-03-01") == (False, None)
    assert in_force_at(other, "2026-10-01") == (False, None)
    assert in_force_at(new, "2025-12-31") == (False, None)


def test_conditional_delay_keeps_old_and_new_until_boundary():
    old = _r("n:d20:k5:l", "2025-01-01", "2026-08-15")
    new = _r("n:d20:k5:l", "2026-08-15", None)
    attach_exceptions([old, new], [_row("n:d20:k5:l", "hoan_ap_dung", tu="2028-01-01", dk="Đến 2027 chỉ xe X")])
    assert in_force_at(old, "2026-10-01") == (True, "Đến 2027 chỉ xe X")
    assert in_force_at(new, "2026-10-01") == (True, "Đến 2027 chỉ xe X")
    assert in_force_at(old, "2028-01-01") == (False, None)
    assert in_force_at(new, "2028-01-01") == (True, None)


def test_unconditional_delay_and_content_milestones():
    rec = _r("t:d4:k4", "2026-07-01", None)
    attach_exceptions([rec], [_row("t:d4:k4", "hoan_ap_dung", tu="2027-03-01"),
                              _row("t:d4:k4", "moc_trong_noi_dung", tu="2028-01-01", dk="Bài số 2 từ 2028")])
    assert in_force_at(rec, "2026-10-01") == (False, None)
    assert in_force_at(rec, "2027-03-01") == (True, "Bài số 2 từ 2028")
    assert in_force_at(rec, "2028-01-01") == (True, None)


def test_aggregate_validation_preserves_records_on_failure():
    rec = _r("a:d1", "2025-01-01", None)
    rows = [_row("khong:co", "gia_han", den="2027-03-01"),
            _row("a:d1", "loai_la", tu="2027-01-01"),
            _row("a:d1", "hoan_ap_dung", tu="2027-13-01"),
            _row("a:d1", "gia_han")]
    with pytest.raises(ValueError) as exc:
        attach_exceptions([rec], rows)
    msg = str(exc.value)
    assert all(x in msg for x in ("khong:co", "loai_la", "2027-13-01", "den_ngay"))
    assert "hl_ngoai_le" not in rec


def test_load_exceptions_reads_bom(tmp_path: Path):
    path = tmp_path / "exceptions.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=["unit_id", "loai", "tu_ngay", "den_ngay", "dieu_kien", "can_cu", "ghi_chu"])
        writer.writeheader()
        writer.writerow(_row("a:d1", "gia_han", den="2027-01-01"))
    assert load_exceptions(path)[0]["unit_id"] == "a:d1"
    assert load_exceptions(tmp_path / "missing.csv") == []
