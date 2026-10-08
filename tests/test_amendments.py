from lawproc.amendments import extract_instructions
from lawproc.structure import parse_units

LINES = [
    "Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
    "1. Sửa đổi, bổ sung khoản 2 Điều 7 như sau:",
    "“2. Phạt tiền từ 600.000 đồng đến 800.000 đồng.”",
    "2. Bổ sung khoản 2a vào sau khoản 2 Điều 7 như sau:",
    "“2a. Phạt tiền từ 800.000 đồng.”",
    "3. Bãi bỏ điểm d khoản 3 Điều 9.",
    "4. Thay thế cụm từ “Bộ Giao thông vận tải” bằng cụm từ “Bộ Xây dựng” tại Điều 12.",
    "Điều 2. Sửa đổi, bổ sung một số điều của Luật Trật tự, an toàn giao thông đường bộ",
    "1. Sửa đổi, bổ sung điểm c khoản 5 Điều 10 như sau: “c) Trẻ em ngồi ghế sau.”",
]


def _rows():
    return extract_instructions("nd_238_2026", parse_units("nd_238_2026", LINES), "Nghị định sửa đổi")


def test_extracts_actions_targets_and_new_text():
    rows = _rows()
    assert [r["action"] for r in rows] == ["sua_doi", "bo_sung", "bai_bo", "thay_the_cum_tu", "sua_doi"]
    r0 = rows[0]
    assert (r0["target_doc_id"], r0["target_dieu"], r0["target_khoan"], r0["target_diem"]) == ("nd_168_2024", "7", "2", "")
    assert r0["new_text"] == "2. Phạt tiền từ 600.000 đồng đến 800.000 đồng."
    assert rows[1]["new_label"] == "khoản 2a"
    assert (rows[2]["target_dieu"], rows[2]["target_khoan"], rows[2]["target_diem"]) == ("9", "3", "d")
    assert rows[3]["target_dieu"] == "12"
    r4 = rows[4]
    assert (r4["target_doc_id"], r4["target_diem"]) == ("luat_36_2024", "c")
    assert r4["new_text"] == "c) Trẻ em ngồi ghế sau."
    assert all(r["status"] == "chua_duyet" for r in rows)


def test_falls_back_to_doc_title():
    units = parse_units("nd_51_2025", ["Điều 1. Sửa đổi, bổ sung điểm c khoản 5 Điều 8 như sau:", "“c) Ô tô điện: 0%.”"])
    rows = extract_instructions("nd_51_2025", units, "Sửa đổi Nghị định số 10/2022/NĐ-CP về lệ phí trước bạ")
    assert rows[0]["target_doc_id"] == "nd_10_2022"
    assert rows[0]["new_text"] == "c) Ô tô điện: 0%."
