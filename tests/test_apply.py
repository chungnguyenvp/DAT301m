from lawproc.apply import apply_amendments
from lawproc.structure import parse_units

BASE = [u.as_dict() for u in parse_units("nd_168_2024", [
    "Điều 7. Xử phạt xe mô tô",
    "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng:",
    "a) Không đội mũ bảo hiểm;",
    "3. Phạt tiền khác.",
    "d) Hành vi d;",
])]
HL = {"nd_168_2024": "2025-01-01", "nd_238_2026": "2026-08-15", "tt_108": "2026-07-01", "tt_12": "2025-03-01"}


def _a(**kw):
    row = {"amend_doc_id": "nd_238_2026", "target_doc_id": "nd_168_2024", "target_dieu": "7", "target_khoan": "",
           "target_diem": "", "new_text": "", "status": "duyet"}
    row.update(kw)
    return row


def _live(recs, uid):
    return [r for r in recs if r["unit_id"] == uid and r["valid_to"] is None]


def test_sua_doi_closes_old_clause_and_children_and_adds_new_version():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2",
                                          new_text="2. Phạt tiền từ 600.000 đồng đến 800.000 đồng:\na) Không đội mũ;")])
    old = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k2" and r["valid_to"] == "2026-08-15"]
    assert old and old[0]["valid_from"] == "2025-01-01"
    new = _live(recs, "nd_168_2024:d7:k2")[0]
    assert new["text"].startswith("Phạt tiền từ 600.000")
    assert (new["valid_from"], new["source_doc_id"], new["version_id"]) == (
        "2026-08-15", "nd_238_2026", "nd_168_2024:d7:k2@2026-08-15")
    assert _live(recs, "nd_168_2024:d7:k2:a")[0]["text"] == "Không đội mũ;"
    assert _live(recs, "nd_168_2024:d7:k3")[0]["valid_from"] == "2025-01-01"


def test_bai_bo_only_closes():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", target_diem="d")])
    assert _live(recs, "nd_168_2024:d7:k3:d") == []


def test_unreviewed_rows_are_ignored():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", status="chua_duyet")])
    assert _live(recs, "nd_168_2024:d7:k3")


def test_replace_whole_document():
    base = [u.as_dict() for u in parse_units("tt_12", ["Điều 1. A"])]
    recs = apply_amendments(base, HL, [_a(amend_doc_id="tt_108", target_doc_id="tt_12", action="thay_the_van_ban",
                                          target_dieu="")])
    assert _live(recs, "tt_12:d1") == []
