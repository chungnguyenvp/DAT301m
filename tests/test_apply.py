import pytest

from lawproc.apply import AmendmentError, apply_amendments
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


def _in_force(recs, uid, t):
    return [r for r in recs if r["unit_id"] == uid and r["valid_from"] <= t
            and (r["valid_to"] is None or t < r["valid_to"])]


def test_sua_doi_closes_old_clause_and_children_and_adds_new_version():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2",
                                          new_text="2. Phạt tiền từ 600.000 đồng đến 800.000 đồng:\na) Không đội mũ;")])
    old = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k2" and r["valid_to"] == "2026-08-15"]
    assert old and old[0]["valid_from"] == "2025-01-01"
    old_child = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k2:a" and r["valid_to"] == "2026-08-15"]
    assert old_child and old_child[0]["text"] == "Không đội mũ bảo hiểm;"
    assert len(_live(recs, "nd_168_2024:d7:k2")) == 1
    new = _live(recs, "nd_168_2024:d7:k2")[0]
    assert new["text"].startswith("Phạt tiền từ 600.000")
    assert (new["valid_from"], new["source_doc_id"], new["version_id"]) == (
        "2026-08-15", "nd_238_2026", "nd_168_2024:d7:k2@2026-08-15")
    assert _live(recs, "nd_168_2024:d7:k2:a")[0]["text"] == "Không đội mũ;"
    assert _live(recs, "nd_168_2024:d7:k3")[0]["valid_from"] == "2025-01-01"


def test_bai_bo_only_closes():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", target_diem="d")])
    assert _live(recs, "nd_168_2024:d7:k3:d") == []
    closed = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k3:d"]
    assert [r["valid_to"] for r in closed] == ["2026-08-15"]


def test_unreviewed_rows_are_ignored():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", status="chua_duyet")])
    assert _live(recs, "nd_168_2024:d7:k3")


def test_replace_whole_document():
    base = [u.as_dict() for u in parse_units("tt_12", ["Điều 1. A"])]
    recs = apply_amendments(base, HL, [_a(amend_doc_id="tt_108", target_doc_id="tt_12", action="thay_the_van_ban",
                                          target_dieu="")])
    assert _live(recs, "tt_12:d1") == []
    assert [r["valid_to"] for r in recs if r["unit_id"] == "tt_12:d1"] == ["2026-07-01"]


def test_future_dated_amendment_is_in_force_only_from_its_date():
    """A record is in force at t iff valid_from <= t and (valid_to is None or t < valid_to).
    Future-dated amendments are recorded with future dates on purpose."""
    hl = dict(HL, nd_238_2026="2027-01-01")
    recs = apply_amendments(BASE, hl, [_a(action="sua_doi", target_khoan="2", new_text="2. Phạt mới:\na) X;")])
    assert [r["text"] for r in _in_force(recs, "nd_168_2024:d7:k2", "2026-06-01")] == [
        "Phạt tiền từ 400.000 đồng đến 600.000 đồng:"]
    assert [r["text"] for r in _in_force(recs, "nd_168_2024:d7:k2", "2027-01-01")] == ["Phạt mới:"]


def test_bad_approved_rows_are_reported_together():
    rows = [
        _a(action="xoa_bo", target_khoan="2"),                                     # 0 unknown action
        _a(action="thay_the_cum_tu", target_khoan="2", new_text="x"),              # 1 approved, not converted
        _a(action="bai_bo", target_dieu="", target_khoan="3"),                     # 2 empty target_dieu
        _a(action="bai_bo", target_khoan="3", amend_doc_id="nd_missing"),          # 3 amending doc not in hl
        _a(action="bai_bo", target_khoan="9"),                                     # 4 no live unit
        _a(action="sua_doi", target_khoan="2", new_text="  "),                     # 5 blank new_text
        _a(action="bo_sung", target_khoan="2", new_text="Không có nhãn"),          # 6 no structural label
    ]
    with pytest.raises(AmendmentError) as e:
        apply_amendments(BASE, HL, rows)
    msg = str(e.value)
    for n, reason in enumerate(["unknown action", "thay_the_cum_tu", "target_dieu", "nd_missing", "no live unit",
                                "blank new_text", "no structural"]):
        assert f"row {n} (" in msg
        assert reason in msg


def test_base_doc_without_date_raises():
    base = [u.as_dict() for u in parse_units("tt_12", ["Điều 1. A"])]
    with pytest.raises(AmendmentError, match="tt_12"):
        apply_amendments(base, {"tt_108": "2026-07-01"}, [])
    with pytest.raises(AmendmentError, match="tt_12"):
        apply_amendments(base, dict(HL, tt_12=""), [])


def test_lead_in_text_is_kept_with_children():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", new_text="Phạt tiền mới:\na) X;")])
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2")] == ["Phạt tiền mới:"]
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2:a")] == ["X;"]


def test_sua_doi_without_lead_or_own_line_raises():
    with pytest.raises(AmendmentError, match="no line for"):
        apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", new_text="a) X;")])


def test_bo_sung_new_label_adds_sibling_and_keeps_anchor_live():
    recs = apply_amendments(BASE, HL, [_a(action="bo_sung", target_khoan="2", new_text="2a. Thêm mới;")])
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2a")] == ["Thêm mới;"]
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2")] == ["Phạt tiền từ 400.000 đồng đến 600.000 đồng:"]


def test_bo_sung_label_collision_raises():
    with pytest.raises(AmendmentError, match="nd_168_2024:d7:k2"):
        apply_amendments(BASE, HL, [_a(action="bo_sung", target_khoan="2", new_text="2. Phạt mới:")])


def test_bo_sung_lead_in_text_raises():
    with pytest.raises(AmendmentError, match="before"):
        apply_amendments(BASE, HL, [_a(action="bo_sung", target_khoan="2", new_text="Thêm khoản sau:\n2a. Mới;")])


def test_sua_doi_creating_sibling_outside_address_raises():
    with pytest.raises(AmendmentError, match="outside"):
        apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", new_text="3. Phạt khác.")])


def test_closing_k2_leaves_sibling_k2a_live():
    base = [u.as_dict() for u in parse_units("nd_168_2024", ["Điều 7. X", "2. A:", "a) A1;", "2a. B;"])]
    recs = apply_amendments(base, HL, [_a(action="bai_bo", target_khoan="2")])
    assert _live(recs, "nd_168_2024:d7:k2") == []
    assert _live(recs, "nd_168_2024:d7:k2:a") == []
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2a")] == ["B;"]


def test_same_day_child_first_resolves_to_one_version():
    rows = [
        _a(action="sua_doi", target_khoan="2", target_diem="a", new_text="a) A2;"),
        _a(action="sua_doi", target_khoan="2", new_text="2. Phạt mới:\na) A1;"),
    ]
    recs = apply_amendments(BASE, HL, rows)
    assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2:a")] == ["A2;"]
    assert len(_live(recs, "nd_168_2024:d7:k2")) == 1
    assert not [r for r in recs if r["valid_to"] is not None and r["valid_to"] == r["valid_from"]]
    vids = [r["version_id"] for r in recs]
    assert len(vids) == len(set(vids))


def test_duplicate_version_ids_raise():
    with pytest.raises(AmendmentError, match="version_id"):
        apply_amendments(BASE + BASE, HL, [])


def test_mo_dau_and_ket_thuc_are_dropped():
    base = [u.as_dict() for u in parse_units("nd_168_2024", [
        "CHÍNH PHỦ", "Điều 7. X", "2. A:", "Nơi nhận: | TM"])]
    recs = apply_amendments(base, HL, [])
    assert {r["level"] for r in recs} == {"dieu", "khoan"}


def test_new_units_inherit_chuong_and_muc():
    base = [u.as_dict() for u in parse_units("nd_168_2024", [
        "Chương II", "XỬ PHẠT VI PHẠM", "Mục 1", "Điều 7. X", "2. A:", "a) A1;"])]
    recs = apply_amendments(base, HL, [
        _a(action="sua_doi", target_khoan="2", new_text="2. Phạt mới:\na) A2;"),
        _a(action="bo_sung", target_khoan="2", new_text="2a. Thêm;"),
    ])
    new_k2 = _live(recs, "nd_168_2024:d7:k2")[0]
    assert (new_k2["chuong"], new_k2["muc"]) == ("II XỬ PHẠT VI PHẠM", "1")
    new_k2a = _live(recs, "nd_168_2024:d7:k2a")[0]
    assert (new_k2a["chuong"], new_k2a["muc"]) == ("II XỬ PHẠT VI PHẠM", "1")


def test_same_day_addition_survives_replacement_in_both_orders():
    add = _a(action="bo_sung", target_khoan="2", new_text="đ) Mới;")
    rep = _a(action="sua_doi", target_khoan="2", new_text="2. Phạt mới:")
    for rows in ([add, rep], [rep, add]):
        recs = apply_amendments(BASE, HL, rows)
        assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2:đ")] == ["Mới;"]
        assert [r["text"] for r in _live(recs, "nd_168_2024:d7:k2")] == ["Phạt mới:"]


def test_thay_the_van_ban_without_live_unit_raises():
    base = [u.as_dict() for u in parse_units("tt_12", ["Điều 1. A"])]
    with pytest.raises(AmendmentError, match="no live unit in target_doc_id tt_99"):
        apply_amendments(base, HL, [_a(amend_doc_id="tt_108", target_doc_id="tt_99", action="thay_the_van_ban",
                                       target_dieu="")])


def test_amendment_dated_before_closed_record_raises():
    hl = dict(HL, nd_238_2026="2024-06-01")
    with pytest.raises(AmendmentError, match="before"):
        apply_amendments(BASE, hl, [_a(action="sua_doi", target_khoan="2", new_text="2. Phạt mới:")])


def test_hl_rieng_overrides_document_date():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", hl_rieng="2027-01-01",
                                          new_text="2. Phạt mới:")])
    old = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k2" and r["valid_to"] is not None]
    assert [(r["valid_from"], r["valid_to"]) for r in old] == [("2025-01-01", "2027-01-01")]
    new = _live(recs, "nd_168_2024:d7:k2")
    assert [(r["valid_from"], r["version_id"]) for r in new] == [
        ("2027-01-01", "nd_168_2024:d7:k2@2027-01-01")]
    assert _in_force(recs, "nd_168_2024:d7:k2", "2026-09-01")[0]["text"].startswith("Phạt tiền từ 400.000")
    assert _in_force(recs, "nd_168_2024:d7:k2", "2027-01-01")[0]["text"] == "Phạt mới:"


def test_empty_hl_rieng_keeps_document_date():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", hl_rieng="",
                                          new_text="2. Phạt mới:")])
    assert _live(recs, "nd_168_2024:d7:k2")[0]["valid_from"] == "2026-08-15"


def test_hl_rieng_is_used_for_ordering_against_other_rows():
    # hàng có hl_rieng muộn hơn phải áp sau hàng theo ngày văn bản, dù đứng trước trong danh sách
    late = _a(action="sua_doi", target_khoan="2", hl_rieng="2028-01-01", new_text="2. Phạt muộn:")
    early = _a(action="sua_doi", target_khoan="2", new_text="2. Phạt sớm:")
    recs = apply_amendments(BASE, HL, [late, early])
    assert [(r["text"], r["valid_from"], r["valid_to"]) for r in recs
            if r["unit_id"] == "nd_168_2024:d7:k2" and r["valid_from"] >= "2026"] == [
        ("Phạt sớm:", "2026-08-15", "2028-01-01"), ("Phạt muộn:", "2028-01-01", None)]


@pytest.mark.parametrize("bad", ["01/01/2027", "2027-1-1", "2027-13-01", "next year"])
def test_malformed_hl_rieng_is_reported(bad):
    with pytest.raises(AmendmentError, match="hl_rieng"):
        apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2", hl_rieng=bad,
                                       new_text="2. Phạt mới:")])


@pytest.mark.parametrize("bad", ["2026-13-01", "2026-8-15", "15/08/2026", "2026-02-30"])
def test_malformed_document_level_date_is_reported(bad):
    hl = dict(HL, nd_238_2026=bad)
    with pytest.raises(AmendmentError, match="nd_238_2026.*not a valid YYYY-MM-DD"):
        apply_amendments(BASE, hl, [_a(action="sua_doi", target_khoan="2", new_text="2. Mới:")])
