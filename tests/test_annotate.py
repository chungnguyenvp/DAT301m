import csv

import pytest

from lawproc.annotate import annex_type, annotate_records, load_annex_overrides, mark_content_change


def _rec(uid, vf, text, level="khoan", title=""):
    return {"unit_id": uid, "doc_id": uid.split(":")[0], "level": level,
            "title": title, "text": text, "valid_from": vf, "valid_to": None}


def test_mark_content_change():
    recs = [_rec("a:d1:k1", "2026-01-01", "mới"), _rec("a:d1:k1", "2025-01-01", "cũ"),
            _rec("a:d1:k1", "2026-08-15", "mới"), _rec("a:d1:k2", "2025-01-01", "x")]
    mark_content_change(recs)
    by = {r["valid_from"] + r["unit_id"]: r["noi_dung_doi"] for r in recs}
    assert by == {"2025-01-01a:d1:k1": True, "2026-01-01a:d1:k1": True,
                  "2026-08-15a:d1:k1": False, "2025-01-01a:d1:k2": True}


def test_annex_type_form_by_title_or_fill_lines():
    assert annex_type("Phụ lục XVI", "MẪU ĐỀ NGHỊ CẤP GIẤY PHÉP LÁI XE QUỐC TẾ\n...")[0] == "mau_bieu"
    assert annex_type("PHỤ LỤC H MAU GIAY KHAM SỨC KHỎE", "")[0] == "mau_bieu"
    assert annex_type("Phụ lục I", "mẫu đơn xin cấp lại")[0] == "mau_bieu"
    fill = "\n".join(["Họ và tên: ......................"] * 4 + ["Ghi chú"])
    assert annex_type("Phụ lục I", fill)[0] == "mau_bieu"
    assert annex_type("Phụ lục BIỂU MỨC THU LỆ PHÍ", "1. Xe ô tô | 500.000 đồng\n2. Xe mô tô | 50.000 đồng")[0] == "noi_dung"


def test_annotate_records_sets_fields_and_overrides():
    recs = [_rec("a:pl1", "2025-01-01", "Họ và tên: .........\nNgày sinh: .........", "phu_luc", "Phụ lục I"),
            _rec("a:pl2", "2025-01-01", "Trình tự sát hạch lái xe hạng B", "phu_luc", "Phụ lục II"),
            _rec("a:d1:k1", "2025-01-01", "Người điều khiển xe")]
    rows = annotate_records(recs, {"a:pl2": "mau_bieu"})
    by = {r["unit_id"]: r for r in recs}
    assert by["a:pl1"]["loai_phu_luc"] == "mau_bieu"
    assert by["a:pl2"]["loai_phu_luc"] == "mau_bieu"
    assert by["a:d1:k1"]["loai_phu_luc"] is None
    assert by["a:d1:k1"]["chat_luong"] == "ok" and by["a:d1:k1"]["noi_dung_doi"] is True
    assert [r["unit_id"] for r in rows] == ["a:pl1", "a:pl2"]
    assert rows[1]["ly_do"] == "ghi đè"


@pytest.mark.parametrize("uid,kind", [("a:pl2", "invalid"), ("a:missing", "mau_bieu"),
                                      ("a:d1:k1", "mau_bieu")])
def test_invalid_override_rejected(tmp_path, uid, kind):
    path = tmp_path / "overrides.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["unit_id", "loai_phu_luc", "ghi_chu"])
        writer.writeheader()
        writer.writerow({"unit_id": uid, "loai_phu_luc": kind, "ghi_chu": ""})
    with pytest.raises(ValueError):
        load_annex_overrides(path, [_rec("a:pl2", "2025-01-01", "", "phu_luc"),
                                    _rec("a:d1:k1", "2025-01-01", "")])


def test_duplicate_override_rejected(tmp_path):
    path = tmp_path / "overrides.csv"
    path.write_text("unit_id,loai_phu_luc,ghi_chu\na:pl2,mau_bieu,\na:pl2,noi_dung,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="trùng"):
        load_annex_overrides(path, [_rec("a:pl2", "2025-01-01", "", "phu_luc")])


def test_annex_type_does_not_take_ca_mau_for_a_form():
    table = "KÝ HIỆU BIỂN SỐ XE Ô TÔ\n1 | An Giang | 67, 68\n3 | Cà Mau | 69, 94\n4 | TỈNH CÀ MAU | 69"
    assert annex_type("Phụ lục số 02", table)[0] == "noi_dung"
