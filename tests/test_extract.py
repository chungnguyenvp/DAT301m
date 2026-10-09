from pathlib import Path

import docx
import pymupdf
import pytest

from lawproc import config
from lawproc.extract import docx_lines, pdf_lines, is_scanned, ocr_pdf_lines

ARIAL = Path("C:/Windows/Fonts/arial.ttf")


def test_docx_lines_keeps_paragraph_and_table_order(tmp_path):
    d = docx.Document()
    d.add_paragraph("CHÍNH PHỦ")
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text = "Số: 168/2024/NĐ-CP"
    t.cell(0, 1).text = "Hà Nội, ngày 26 tháng 12 năm 2024"
    d.add_paragraph("Điều 1. Phạm vi điều chỉnh")
    d.add_paragraph("   ")
    p = tmp_path / "a.docx"
    d.save(p)
    assert docx_lines(p) == [
        "CHÍNH PHỦ",
        "Số: 168/2024/NĐ-CP | Hà Nội, ngày 26 tháng 12 năm 2024",
        "Điều 1. Phạm vi điều chỉnh",
    ]


def test_docx_lines_keeps_breaks_and_tabs_as_spaces(tmp_path):
    d = docx.Document()
    p1 = d.add_paragraph()
    r1 = p1.add_run("VIỆT NAM")
    r1.add_break()
    p1.add_run("Độc lập")
    p2 = d.add_paragraph()
    r2 = p2.add_run("Số:")
    r2.add_tab()
    p2.add_run("168/2024")
    p = tmp_path / "b.docx"
    d.save(p)
    assert docx_lines(p) == ["VIỆT NAM Độc lập", "Số: 168/2024"]


def _pdf_with_lines(path, lines):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_font(fontname="arial", fontfile=str(ARIAL))
    for k, text in enumerate(lines):
        page.insert_text((72, 72 + 22 * k), text, fontname="arial", fontsize=14)
    doc.save(path)


def test_pdf_lines_and_not_scanned(tmp_path):
    p = tmp_path / "t.pdf"
    _pdf_with_lines(p, ["Điều 1. Phạm vi điều chỉnh của Nghị định này"] * 8)
    assert pdf_lines(p)[0].replace("\xa0", " ").startswith("Điều 1.")  # PyMuPDF may emit NBSP; normalize() cleans it later
    assert is_scanned(p) is False


def test_is_scanned_true_for_image_only_pdf(tmp_path):
    p = tmp_path / "img.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(p)
    assert is_scanned(p) is True


@pytest.mark.skipif(not config.TESSERACT.exists(), reason="Tesseract chưa cài")
def test_ocr_pdf_lines_reads_vietnamese_and_caches(tmp_path):
    p = tmp_path / "scan.pdf"
    _pdf_with_lines(p, ["Điều 2. Người nộp lệ phí"])
    cache = tmp_path / "cache"
    lines = ocr_pdf_lines(p, cache, dpi=200)
    assert any("Người nộp lệ phí" in x for x in lines)
    assert (cache / "p0000.txt").exists()


def test_docx_lines_reads_nested_table_once(tmp_path):
    d = docx.Document()
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text = "Mẫu số 01"
    inner = t.cell(0, 1).add_table(rows=1, cols=2)
    inner.cell(0, 0).text = "Họ và tên"
    inner.cell(0, 1).text = "Ngày sinh"
    p = tmp_path / "n.docx"
    d.save(p)
    assert docx_lines(p) == ["Mẫu số 01 | Họ và tên | Ngày sinh"]


def test_docx_lines_merged_cells_once(tmp_path):
    d = docx.Document()
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).merge(t.cell(0, 1)).text = "Tiêu đề gộp"
    t.cell(1, 0).text = "Trái"
    t.cell(1, 1).text = "Phải"
    p = tmp_path / "m.docx"
    d.save(p)
    assert docx_lines(p) == ["Tiêu đề gộp", "Trái | Phải"]


def test_docx_lines_cell_with_empty_paragraph_has_single_spaces(tmp_path):
    d = docx.Document()
    t = d.add_table(rows=1, cols=1)
    c = t.cell(0, 0)
    c.text = "Dòng một"
    c.add_paragraph("")
    c.add_paragraph("Dòng hai")
    p = tmp_path / "s.docx"
    d.save(p)
    assert docx_lines(p) == ["Dòng một Dòng hai"]
