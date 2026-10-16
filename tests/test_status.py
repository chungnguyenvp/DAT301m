import pytest

from lawproc.status import apply_annex_replacements, check_annex_replacements, mark_scope, mark_status
from lawproc.validity import in_force_at


def _rec(uid, level="phu_luc", title="", text="nội dung", vf="2025-01-01", vt=None):
    return {"unit_id": uid, "doc_id": uid.split(":")[0], "level": level, "title": title, "text": text,
            "valid_from": vf, "valid_to": vt, "version_id": f"{uid}@{vf}", "hl_ngoai_le": []}


def _row(old, new, pham_vi="toan_bo", tu="2026-07-01", duyet="duyet", chi_tiet=""):
    return {"pl_cu": old, "pl_moi": new, "pham_vi": pham_vi, "chi_tiet": chi_tiet, "tu_ngay": tu,
            "can_cu": "x:d1", "chi_dan": "Thay thế", "duyet": duyet, "ghi_chu": ""}


def test_whole_replacement_closes_old_annex_and_records_link():
    recs = [_rec("a:pl2"), _rec("b:pl2", vf="2026-07-01")]
    apply_annex_replacements(recs, check_annex_replacements([_row("a:pl2", "b:pl2")], recs))
    old, new = recs
    assert old["valid_to"] == "2026-07-01"
    assert old["pl_thay_the"] == [{"bang": "b:pl2", "tu_ngay": "2026-07-01", "pham_vi": "toan_bo",
                                   "chi_tiet": "", "can_cu": "x:d1"}]
    assert new["pl_thay_the"] == []
    assert in_force_at(old, "2026-06-30")[0] and not in_force_at(old, "2026-07-01")[0]


def test_partial_replacement_keeps_old_annex_in_force_with_note():
    recs = [_rec("a:pl7"), _rec("b:pl2")]
    apply_annex_replacements(recs, check_annex_replacements(
        [_row("a:pl7", "b:pl2", pham_vi="mot_phan", chi_tiet="Mẫu số 01, 02")], recs))
    assert recs[0]["valid_to"] is None
    assert recs[0]["pl_thay_the"][0]["pham_vi"] == "mot_phan"


def test_unapproved_rows_are_not_applied():
    recs = [_rec("a:pl2"), _rec("b:pl2")]
    apply_annex_replacements(recs, check_annex_replacements([_row("a:pl2", "b:pl2", duyet="")], recs))
    assert recs[0]["valid_to"] is None and recs[0]["pl_thay_the"] == []


@pytest.mark.parametrize("row, msg", [(_row("a:pl9", "b:pl2"), "không có"), (_row("a:d1", "b:pl2"), "không phải phụ lục"),
                                      (_row("a:pl2", "b:pl2", pham_vi="ca_hai"), "pham_vi"),
                                      (_row("a:pl2", "b:pl2", tu="1/7/2026"), "tu_ngay")])
def test_bad_rows_are_refused(row, msg):
    recs = [_rec("a:pl2"), _rec("b:pl2"), _rec("a:d1", level="dieu")]
    with pytest.raises(ValueError, match=msg):
        check_annex_replacements([row], recs)


def test_mark_status_flags_repealed_placeholders_and_content_gaps():
    recs = [_rec("x:d38", level="dieu", title="(được bãi bỏ)", text=""),
            _rec("x:d39", level="dieu", title="Thẩm quyền", text="Được bãi bỏ một phần"),
            _rec("y:pl1", text="(Kèm theo Nghị định)")]
    mark_status(recs, [{"unit_id": "y:pl1", "ly_do": "phụ lục là ảnh", "can_cu": "PDF trang 12–14"}])
    assert [r["trang_thai"] for r in recs] == ["bai_bo", None, None]
    assert [r["thieu_noi_dung"] for r in recs] == [None, None, "phụ lục là ảnh"]
    assert not in_force_at(recs[0], "2026-10-01")[0]
    assert in_force_at(recs[1], "2026-10-01")[0]


def test_mark_status_refuses_unknown_gap_unit():
    with pytest.raises(ValueError, match="không có"):
        mark_status([_rec("y:pl1")], [{"unit_id": "y:pl9", "ly_do": "x", "can_cu": "y"}])


def test_scope_flags_units_outside_the_article_range():
    recs = [dict(_rec("blds:d583", level="dieu"), dieu="583"), dict(_rec("blds:d584:k1", level="khoan"), dieu="584"),
            dict(_rec("blds:d608", level="dieu"), dieu="608"), dict(_rec("blds:pl1"), dieu=None),
            dict(_rec("x:d1", level="dieu"), dieu="1")]
    mark_scope(recs, {"blds": (584, 608)})
    assert [r["trong_pham_vi"] for r in recs] == [False, True, True, False, True]
