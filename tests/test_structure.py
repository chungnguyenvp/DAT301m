from lawproc.structure import parse_units, unit_address

DOC = [
    "CHÍNH PHỦ",
    "Căn cứ Luật Tổ chức Chính phủ;",
    "Chương II",
    "XỬ PHẠT VI PHẠM",
    "Mục 1",
    "VI PHẠM QUY TẮC GIAO THÔNG",
    "Điều 7. Xử phạt người điều khiển xe mô tô",
    "1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với hành vi sau đây:",
    "a) Không chấp hành hiệu lệnh;",
    "b) Không có tín hiệu trước khi vượt;",
    "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng.",
    "Điều 8. Hiệu lực thi hành",
    "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2025.",
    "Nơi nhận: | TM. CHÍNH PHỦ",
    "PHỤ LỤC I",
    "1. Mẫu biên bản",
]


def test_unit_address():
    assert unit_address("nd", "7", "2", "h") == "nd:d7:k2:h"
    assert unit_address("nd", "7", None, None) == "nd:d7"


def test_parse_levels_and_context():
    units = {u.unit_id: u for u in parse_units("nd", DOC)}
    assert units["nd:mo_dau"].text == "CHÍNH PHỦ\nCăn cứ Luật Tổ chức Chính phủ;"
    d7 = units["nd:d7"]
    assert (d7.level, d7.title, d7.chuong, d7.muc) == ("dieu", "Xử phạt người điều khiển xe mô tô",
                                                        "II XỬ PHẠT VI PHẠM", "1 VI PHẠM QUY TẮC GIAO THÔNG")
    assert units["nd:d7:k1"].text.startswith("Phạt tiền từ 200.000")
    assert units["nd:d7:k1:b"].text == "Không có tín hiệu trước khi vượt;"
    assert units["nd:d7:k2"].level == "khoan"
    assert units["nd:d8"].text == "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2025."
    assert units["nd:ket_thuc"].level == "ket_thuc"
    assert units["nd:pl1"].title == "PHỤ LỤC I"
    assert "nd:d1" not in units  # "1. Mẫu biên bản" nằm trong phụ lục, không tách


def test_quoted_amendment_is_not_split():
    lines = [
        "Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
        "1. Sửa đổi, bổ sung khoản 2 Điều 7 như sau:",
        "“2. Phạt tiền từ 600.000 đồng đến 800.000 đồng đối với:",
        "a) Không đội mũ bảo hiểm;",
        "b) Chở quá số người quy định.”",
        "2. Bãi bỏ điểm d khoản 3 Điều 9.",
    ]
    units = {u.unit_id: u for u in parse_units("nd238", lines)}
    k1 = units["nd238:d1:k1"]
    assert k1.text.splitlines()[0] == "Sửa đổi, bổ sung khoản 2 Điều 7 như sau:"
    assert "a) Không đội mũ bảo hiểm;" in k1.text
    assert "nd238:d1:k1:a" not in units
    assert units["nd238:d1:k2"].text == "Bãi bỏ điểm d khoản 3 Điều 9."


def test_fragment_mode_uses_given_context():
    frag = ["2. Phạt tiền từ 600.000 đồng đến 800.000 đồng đối với:", "a) Không đội mũ bảo hiểm;"]
    ids = [u.unit_id for u in parse_units("nd_168_2024", frag, dieu="7")]
    assert ids == ["nd_168_2024:d7:k2", "nd_168_2024:d7:k2:a"]
    ids = [u.unit_id for u in parse_units("nd_10_2022", ["c) Ô tô điện: 0%."], dieu="8", khoan="5")]
    assert ids == ["nd_10_2022:d8:k5:c"]


def test_duplicate_ids_get_suffix():
    ids = [u.unit_id for u in parse_units("x", ["Điều 1. A", "Điều 1. A lặp"])]
    assert ids == ["x:mo_dau", "x:d1", "x:d1#2"]
