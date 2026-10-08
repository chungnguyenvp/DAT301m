from lawproc.verify import check_identity

HEAD = "QUỐC HỘI | Luật số: 91/2015/QH13\nBỘ LUẬT DÂN SỰ\nCăn cứ Hiến pháp"


def test_number_and_title_match():
    r = check_identity("blds_2015", "91/2015/QH13", "Bộ luật dân sự", HEAD)
    assert r["so_hieu_found"] is True
    assert r["title_ratio"] == 1.0
    assert r["status"] == "ok"


def test_wrong_document_with_same_number_is_flagged():
    head = "Nghị quyết số: 91/2015/QH13 về chương trình hoạt động giám sát của Quốc hội năm 2016"
    r = check_identity("blds_2015", "91/2015/QH13", "Bộ luật dân sự", head)
    assert r["status"] == "kiem_tra_tay"


def test_title_equal_to_code_only_checks_number():
    r = check_identity("nd_168_2024", "168/2024/NĐ-CP", "168/2024/NĐ-CP", "Số: 168/2024/NĐ-CP | Hà Nội")
    assert r["status"] == "ok"


def test_handwritten_number_missing_is_flagged():
    r = check_identity("tt_36_2024_byt", "36/2024/TT-BYT", "Tiêu chuẩn sức khỏe người lái xe",
                       "Số: /2024/TT-BYT\nTiêu chuẩn sức khỏe, việc khám sức khỏe đối với người lái xe")
    assert r["so_hieu_found"] is False
    assert r["status"] == "kiem_tra_tay"


def test_number_inside_longer_number_is_not_found():
    r = check_identity("tt_36_2024_byt", "36/2024/TT-BYT", "36/2024/TT-BYT", "Số: 136/2024/TT-BYT")
    assert r["so_hieu_found"] is False
    assert r["status"] == "kiem_tra_tay"


def test_number_followed_by_pipe_is_found():
    r = check_identity("tt_36_2024_byt", "36/2024/TT-BYT", "36/2024/TT-BYT", "Số: 36/2024/TT-BYT | Hà Nội")
    assert r["so_hieu_found"] is True


def test_number_followed_by_title_on_same_line_is_found():
    r = check_identity("blds_2015", "91/2015/QH13", "Bộ luật dân sự", "Luật số: 91/2015/QH13 CỘNG HÒA")
    assert r["so_hieu_found"] is True


def test_stray_space_inside_number_is_found():
    r = check_identity("tt_36_2024_byt", "36/2024/TT-BYT", "36/2024/TT-BYT", "Số: 36 /2024/TT-BYT")
    assert r["so_hieu_found"] is True


def test_consolidated_number_in_closing_authentication_block_is_found():
    text = "LUẬT XỬ LÝ VI PHẠM HÀNH CHÍNH\n" + "Điều 1. Nội dung\n" * 800 + "VĂN PHÒNG QUỐC HỘI Số: 63/VBHN-VPQH | XÁC THỰC VĂN BẢN HỢP NHẤT"
    r = check_identity("vbhn_63_2025_xlvphc", "63/VBHN-VPQH", "63/VBHN-VPQH", text)
    assert r["so_hieu_found"] is True
    assert r["status"] == "ok"
