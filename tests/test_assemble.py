import pytest

from lawproc import config
from lawproc.assemble import (article_report, assemble_doc, drop_toc_lines, group_rows, pick_sources,
                              split_derived)


def _row(doc_id, file, fmt):
    return {"doc_id": doc_id, "file": file, "dinh_dang": fmt}


def test_group_rows_skips_non_legal():
    rows = [_row("a", "x__p1.pdf", "pdf"), _row("gplx_600_2025", "g.pdf", "pdf"), _row("a", "x__p2.doc", "doc")]
    assert list(group_rows(rows)) == ["a"]
    assert len(group_rows(rows)["a"]) == 2


def test_pick_sources_prefers_word():
    rows = [_row("a", "a__p1.pdf", "pdf"), _row("a", "a__p2.doc", "doc"), _row("a", "a__p3.docx", "docx")]
    chosen, method = pick_sources(rows)
    assert method == "docx"
    assert [r["file"] for r in chosen] == ["a__p2.doc", "a__p3.docx"]


def test_pick_sources_scanned_doc_uses_ocr():
    chosen, method = pick_sources([_row("tt_155_2025_btc", "t__p1.pdf", "pdf")])
    assert method == "ocr"


def test_pick_sources_scanned_doc_with_word_skips_ocr():
    rows = [_row("tt_108_2026_bca", "t__p1.pdf", "pdf"), _row("tt_108_2026_bca", "t__p2.docx", "docx")]
    chosen, method = pick_sources(rows)
    assert method == "docx"
    assert [r["file"] for r in chosen] == ["t__p2.docx"]


def test_pick_sources_text_before_pdf_after_word():
    rows = [_row("tt_36_2024_byt", "t__p1.pdf", "pdf"), _row("tt_36_2024_byt", "t__p2.txt", "txt")]
    chosen, method = pick_sources(rows)
    assert method == "txt"
    assert [r["file"] for r in chosen] == ["t__p2.txt"]
    chosen, method = pick_sources(rows + [_row("tt_36_2024_byt", "t__p3.docx", "docx")])
    assert method == "docx"


def test_assemble_keeps_text_lines_unjoined():
    assert assemble_doc("x", [["Điều 1. A", "1. Khoản một", "a) Điểm"]], "txt") == \
        ["Điều 1. A", "1. Khoản một", "a) Điểm"]


def test_assemble_orders_parts_and_joins_pdf_lines():
    part2 = ["Nghị định số 1/2024/NĐ-CP", "(Tiếp theo Công báo số 10 + 11)", "Điều 3. Hiệu lực", "thi hành"]
    part1 = ["CÔNG BÁO/Số 10 + 11/Ngày 01-01-2025 3", "Điều 1. Phạm vi", "Điều 2. Đối tượng",
             "(Xem tiếp Công báo số 12 + 13)"]
    lines = assemble_doc("x", [part2, part1], "pdf")
    assert lines == ["Điều 1. Phạm vi", "Điều 2. Đối tượng", "Điều 3. Hiệu lực thi hành"]


def test_article_report_finds_gaps():
    rep = article_report("x", ["Điều 1. A", "Điều 2. B", "Điều 4. D", "“Điều 9. trong ngoặc”"], "docx", 2)
    assert rep["n_dieu"] == 3
    assert (rep["first_dieu"], rep["last_dieu"]) == (1, 4)
    assert rep["missing_dieu"] == "3"


def test_article_report_ignores_headings_inside_multiline_quotes_and_annexes():
    lines = [
        "Điều 1. Sửa đổi luật khác",
        "1. Bổ sung Điều 31a vào sau Điều 31 như sau:",
        "“Điều 31a. Nội dung",
        "Điều 31b. Nội dung khác”",
        "Điều 2. Hiệu lực",
        "PHỤ LỤC I",
        "Điều 7. mẫu trong phụ lục",
    ]
    rep = article_report("x", lines, "docx", 1)
    assert (rep["n_dieu"], rep["first_dieu"], rep["last_dieu"], rep["missing_dieu"]) == (2, 1, 2, "")


def test_ocr_table_border_pipe_before_heading_is_removed():
    lines = assemble_doc("x", [["Điều 2. Người nộp", "| Điều 3. Tổ chức thu lệ phí", "Điều 4. Giải thích"]], "ocr")
    assert lines == ["Điều 2. Người nộp", "Điều 3. Tổ chức thu lệ phí", "Điều 4. Giải thích"]


def test_drop_toc_lines_only_drops_headings_with_leaders():
    lines = ["Phần 1: Quy định chung……………...........", "Chương 9 - Biển chỉ dẫn trên đường cao tốc……………….…",
             "Phụ lục A - Đèn tín hiệu .................... 12", "Chương trình đào tạo: ......................",
             "Họ và tên: ..........................", "PHẦN 1: QUY ĐỊNH CHUNG", "Điều 1. Phạm vi điều chỉnh"]
    assert drop_toc_lines(lines) == ["Chương trình đào tạo: ......................",
                                     "Họ và tên: ..........................", "PHẦN 1: QUY ĐỊNH CHUNG",
                                     "Điều 1. Phạm vi điều chỉnh"]


def test_split_derived_cuts_at_start_line(monkeypatch):
    monkeypatch.setattr(config, "DERIVED_DOCS", {"qc": {"parent": "tt", "so_ky_hieu": "QC 1", "tieu_de": "Quy chuẩn",
                                                       "nhom": "X", "start": "QC 1 QUY CHUẨN"}})
    lines = ["Điều 1. Ban hành", "BỘ TRƯỞNG", "CỘNG HÒA QC 1 QUY CHUẨN KỸ THUẬT", "Điều 1. Phạm vi"]
    assert split_derived("tt", lines) == {"tt": lines[:2], "qc": lines[2:]}
    assert split_derived("khac", lines) == {"khac": lines}


def test_split_derived_missing_start_line_raises(monkeypatch):
    monkeypatch.setattr(config, "DERIVED_DOCS", {"qc": {"parent": "tt", "so_ky_hieu": "QC 1", "tieu_de": "Quy chuẩn",
                                                       "nhom": "X", "start": "QC 1 QUY CHUẨN"}})
    with pytest.raises(ValueError, match="qc"):
        split_derived("tt", ["Điều 1. Ban hành"])
