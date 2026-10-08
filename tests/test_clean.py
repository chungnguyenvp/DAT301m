from lawproc.clean import normalize, strip_part, order_parts, join_wrapped


def test_normalize_nfc_cyrillic_and_spaces():
    decomposed = "Nghị định 168/2024/NĐ-CР  mới"
    assert normalize(decomposed) == "Nghị định 168/2024/NĐ-CP mới"


def test_strip_part_removes_headers_and_detects_continuation():
    lines = [
        "VĂN BẢN QUY PHẠM PHÁP LUẬT",
        "CHÍNH PHỦ",
        "Nghị định số 168/2024/NĐ-CP ngày 26 tháng 12 năm 2024 quy định xử phạt",
        "(Tiếp theo Công báo số 75 + 76)",
        "3. Phạt tiền từ 5.000.000 đồng",
        "2 CÔNG BÁO/Số 77 + 78/Ngày 16-01-2025",
        "17",
        "a) Cơ sở đào tạo lái xe;",
        "(Xem tiếp Công báo số 79 + 80)",
    ]
    out, cont = strip_part(lines)
    assert cont == 75
    assert out == ["3. Phạt tiền từ 5.000.000 đồng", "a) Cơ sở đào tạo lái xe;"]


def test_strip_part_first_part_keeps_body():
    out, cont = strip_part(["VĂN BẢN QUY PHẠM PHÁP LUẬT", "CHÍNH PHỦ", "NGHỊ ĐỊNH", "Điều 1. Phạm vi"])
    assert cont is None
    assert out == ["CHÍNH PHỦ", "NGHỊ ĐỊNH", "Điều 1. Phạm vi"]


def test_order_parts_puts_first_part_then_by_issue():
    parts = [(["c"], 1365), (["a"], None), (["b"], 1361)]
    assert order_parts(parts) == [["a"], ["b"], ["c"]]


def test_join_wrapped_joins_broken_lines_but_not_structure():
    lines = [
        "Điều 7. Xử phạt người điều khiển xe mô tô, xe gắn",
        "máy vi phạm quy tắc giao thông đường bộ",
        "1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với",
        "người điều khiển xe thực hiện hành vi sau đây:",
        "a) Không chấp hành hiệu lệnh;",
        "b) Không có tín hiệu trước khi vượt.",
    ]
    assert join_wrapped(lines) == [
        "Điều 7. Xử phạt người điều khiển xe mô tô, xe gắn máy vi phạm quy tắc giao thông đường bộ",
        "1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với người điều khiển xe thực hiện hành vi sau đây:",
        "a) Không chấp hành hiệu lệnh;",
        "b) Không có tín hiệu trước khi vượt.",
    ]
