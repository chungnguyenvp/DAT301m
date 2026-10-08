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


def test_chuong_then_muc_without_titles_does_not_swallow_article():
    units = {u.unit_id: u for u in parse_units("x", ["Điều 1. A", "Chương I", "Mục 1", "Điều 2. B"])}
    assert "x:d2" in units
    assert units["x:d2"].chuong == "I"
    assert units["x:d2"].muc == "1"


def test_wrapped_chuong_title_is_joined_and_does_not_leak():
    lines = ["Điều 1. A", "1. Nội dung.", "Chương II", "QUY ĐỊNH VỀ XỬ PHẠT", "HÀNH VI VI PHẠM", "Điều 2. B"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert units["x:d2"].chuong == "II QUY ĐỊNH VỀ XỬ PHẠT HÀNH VI VI PHẠM"
    assert units["x:d1:k1"].text == "Nội dung."


def test_nơi_nhận_inline_text_does_not_close_document():
    lines = ["Điều 1. A", "1. Thủ tục:", "Nơi nhận hồ sơ: Cục", "Điều 2. B", "1. Khoản"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert "x:d2" in units
    assert "x:d2:k1" in units
    assert not any(u.level == "ket_thuc" for u in units.values())


def test_nơi_nhận_inside_annex_does_not_open_closing_block():
    lines = ["Điều 1. A", "PHỤ LỤC I", "Nơi nhận: mẫu", "1. Mẫu"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert not any(u.level == "ket_thuc" for u in units.values())
    assert units["x:pl1"].text == "Nơi nhận: mẫu\n1. Mẫu"


def test_unclosed_quote_is_resynced_by_closing_block():
    lines = ["Điều 1. Tên có “ngoặc", "1. Khoản", "Nơi nhận: | TM. CHÍNH PHỦ"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert units["x:ket_thuc"].level == "ket_thuc"


def test_unclosed_quote_is_resynced_after_max_quoted_run():
    lines = ["Điều 1. Tên có “ngoặc"] + [f"Dòng {i}" for i in range(201)] + ["Điều 2. B"]
    ids = {u.unit_id for u in parse_units("x", lines)}
    assert "x:d2" in ids


def test_stray_midline_quote_does_not_swallow_following_articles():
    lines = ["Điều 1. A", "1. Kèm theo “Thông tư này và khoản 2.", "2. Khoản hai", "Điều 2. B", "1. Khoản"]
    ids = {u.unit_id for u in parse_units("x", lines)}
    assert {"x:d1:k1", "x:d1:k2", "x:d2", "x:d2:k1"} <= ids


def test_quote_without_closing_mark_ends_at_next_quote_line():
    lines = ["Điều 1. Sửa đổi", "“2. Nội dung thiếu dấu đóng", "tiếp theo", "“4. Nội dung khác”;", "Điều 2. Hiệu lực"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert "x:d2" in units
    assert "tiếp theo" in units["x:d1"].text


def test_long_balanced_quote_is_still_one_block():
    lines = ["Điều 1. Sửa đổi", "1. Sửa đổi như sau:", "“Điều 5. Mới", "1. Khoản mới", "a) Điểm mới", "2. Khoản hai.”", "Điều 2. Hiệu lực"]
    ids = {u.unit_id for u in parse_units("x", lines)}
    assert "x:d5" not in ids and "x:d2" in ids


def test_sentence_starting_with_phu_luc_is_not_an_annex_heading():
    lines = ["Điều 1. A", "4. Việc khám sức khỏe theo mẫu tại", "Phụ lục I ban hành kèm theo Thông tư này để khám sức khỏe.", "Điều 2. B"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert "x:pl1" not in units and "x:d2" in units
    assert "Phụ lục I ban hành" in units["x:d1:k4"].text


def test_annex_heading_variants_open_an_annex():
    for head in ["PHỤ LỤC", "PHỤ LỤC I", "Phụ lục số 02", "PHỤ LỤC LHI (Ban hành kèm theo Thông tư số 1/2026/TT-BCA)",
                 "Phụ lục I: Mẫu giấy", "PHỤ LỤC II TIÊU CHUẨN"]:
        units = {u.unit_id for u in parse_units("x", ["Điều 1. A", head, "nội dung"])}
        assert "x:pl1" in units, head


def test_mau_form_with_ban_hanh_kem_theo_opens_annex_same_line():
    lines = ["Điều 40. Hiệu lực", "1. Có hiệu lực.", "Mẫu ĐKX01 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024",
             "Điều 1. Thu hồi chứng nhận đăng ký xe", "1. Họ và tên"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert units["x:pl1"].level == "phu_luc"
    assert "x:d1" not in units and "x:d1:k1" not in units
    assert "Điều 1. Thu hồi" in units["x:pl1"].text


def test_mau_form_with_ban_hanh_kem_theo_on_next_line_opens_annex():
    lines = ["Điều 40. Hiệu lực", "Mẫu ĐKX01", "(Ban hành kèm theo Thông tư số 79/2024/TT-BCA)", "Điều 2. Mẫu", "Nơi nhận: A"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert "x:pl1" in units and "x:d2" not in units
    assert not any(u.level == "ket_thuc" for u in units.values())


def test_mau_reference_in_body_text_stays_body():
    lines = ["Điều 3. Hồ sơ", "Mẫu đơn theo quy định tại khoản 2 Điều này", "Mẫu số 01 ban hành kèm theo Thông tư này.",
             "Điều 4. B"]
    units = {u.unit_id: u for u in parse_units("x", lines)}
    assert not any(u.level == "phu_luc" for u in units.values())
    assert "x:d4" in units


def test_mau_before_first_dieu_is_not_annex():
    lines = ["Mẫu ĐKX01 Ban hành kèm theo Thông tư số 1", "Điều 1. A"]
    assert not any(u.level == "phu_luc" for u in parse_units("x", lines))


def test_annex_heading_joined_with_its_title_by_ocr_still_opens_annex():
    head = "PHỤ LỤC II MẪU GIẤY KHÁM SỨC KHỎE CỦA NGƯỜI LÁI XE, NGƯỜI ĐIỀU KHIỂN XE MÁY CHUYÊN DÙNG " + "TÊN CƠ QUAN " * 8
    assert 150 < len(head) < 250
    units = {u.unit_id: u for u in parse_units("x", ["Điều 1. A", "1. Khoản", head, "1. Họ và tên", "1. Họ và tên"])}
    assert "x:pl1" in units and "x:d1:k1#2" not in units


def test_mau_form_heading_duplicated_by_docx_text_box_opens_annex():
    head = "Mẫu KĐ23a ban hành kèm theo Thông tư số 37/2026/TT-BCA ngày 24/4/2026 của Bộ Công an" * 2
    assert 150 < len(head) < 250
    units = {u.unit_id for u in parse_units("x", ["Điều 1. A", "2. Khoản", head, "2. Mặt sau"])}
    assert "x:pl1" in units and "x:d1:k2#2" not in units
