from pathlib import Path

import pymupdf
import pytest

from lawproc.gplx import chapter_of, parse_cv_lists, parse_questions

ARIAL = Path("C:/Windows/Fonts/arial.ttf")
ARIAL_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")


class _Page:
    """Ghi dòng chữ lần lượt từ trên xuống; dòng đáp án đúng có gạch chân như bản in của Cục CSGT."""

    def __init__(self, doc):
        self.page = doc.new_page()
        self.page.insert_font(fontname="reg", fontfile=str(ARIAL))
        self.page.insert_font(fontname="bold", fontfile=str(ARIAL_BOLD))
        self.y = 60

    def line(self, text, bold=False, underline=False):
        self.page.insert_text((72, self.y), text, fontname="bold" if bold else "reg", fontsize=12)
        if underline:
            self.page.draw_rect(pymupdf.Rect(72, self.y + 2, 300, self.y + 2.6), color=None, fill=(0, 0, 0))
        self.y += 20

    def image(self, height=80):
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40), 0)
        pix.clear_with(200)
        self.page.insert_image(pymupdf.Rect(72, self.y, 272, self.y + height), pixmap=pix)
        self.y += height + 10


@pytest.fixture
def fonts():
    if not (ARIAL.exists() and ARIAL_BOLD.exists()):
        pytest.skip("thiếu font Arial")


def test_parse_questions_reads_options_underlined_answer_and_images(tmp_path, fonts):
    doc = pymupdf.open()
    p = _Page(doc)
    p.line("12")  # số trang
    p.line("Câu 1. Người lái xe phải làm gì khi", bold=True)
    p.line("đến gần đường giao nhau?", bold=True)
    p.line("1. Tăng tốc độ.")
    p.line("2. Giảm tốc độ, quan sát an toàn", underline=True)
    p.line("ở phía trước.", underline=True)
    p.line("Câu 2. Biển nào cấm ô tô?", bold=True)
    p.image()
    p.line("1. Biển 1.", underline=True)
    p.line("2. Biển 2.")
    p.line("3. Biển 3.")
    path = tmp_path / "q.pdf"
    doc.save(path)
    qs = parse_questions(path)
    assert [q["so_cau"] for q in qs] == [1, 2]
    assert qs[0]["cau_hoi"] == "Người lái xe phải làm gì khi đến gần đường giao nhau?"
    assert qs[0]["lua_chon"] == ["Tăng tốc độ.", "Giảm tốc độ, quan sát an toàn ở phía trước."]
    assert qs[0]["dap_an"] == 2 and qs[0]["co_hinh"] is False
    assert qs[1]["lua_chon"] == ["Biển 1.", "Biển 2.", "Biển 3."]
    assert qs[1]["dap_an"] == 1 and qs[1]["co_hinh"] is True


def test_parse_questions_follows_question_across_pages(tmp_path, fonts):
    doc = pymupdf.open()
    p1 = _Page(doc)
    p1.line("Câu 7. Câu hỏi sang trang?", bold=True)
    p1.line("1. Lựa chọn một")
    p2 = _Page(doc)
    p2.line("13")
    p2.line("tiếp tục ở trang sau.")
    p2.line("2. Lựa chọn hai", underline=True)
    path = tmp_path / "q.pdf"
    doc.save(path)
    (q,) = parse_questions(path)
    assert q["lua_chon"] == ["Lựa chọn một tiếp tục ở trang sau.", "Lựa chọn hai"]
    assert q["dap_an"] == 2 and q["co_hinh"] is False


def test_parse_questions_accepts_colon_and_options_on_one_line(tmp_path, fonts):
    doc = pymupdf.open()
    p = _Page(doc)
    p.line("Câu 352. Biển nào báo hiệu cự ly?", bold=True)
    y = p.y
    p.line("1. Biển 1. 2. Biển 2. 3. Cả hai biển.")
    r = p.page.search_for("2. Biển 2.", clip=pymupdf.Rect(0, y - 15, 600, y + 5))[0]
    p.page.draw_rect(pymupdf.Rect(r.x0, r.y1 + 1, r.x1, r.y1 + 1.6), color=None, fill=(0, 0, 0))
    p.line("Câu 507: Hướng nào được đi?", bold=True)
    p.line("1. Cả ba hướng.", underline=True)
    p.line("2. Chỉ hướng 1.")
    path = tmp_path / "q.pdf"
    doc.save(path)
    q352, q507 = parse_questions(path)
    assert q352["lua_chon"] == ["Biển 1.", "Biển 2.", "Cả hai biển."] and q352["dap_an"] == 2
    assert q507["so_cau"] == 507 and q507["cau_hoi"] == "Hướng nào được đi?" and q507["dap_an"] == 1


def test_parse_questions_reads_options_laid_out_in_two_columns(tmp_path, fonts):
    doc = pymupdf.open()
    p = _Page(doc)
    p.line("Câu 301. Biển nào là biển cấm?", bold=True)
    p.line("1. Biển 1. 3. Biển 1 và biển 3.")
    y = p.y
    p.line("2. Biển 2. 4. Cả ba biển.")
    r = p.page.search_for("4. Cả ba biển.", clip=pymupdf.Rect(0, y - 15, 600, y + 5))[0]
    p.page.draw_rect(pymupdf.Rect(r.x0, r.y1 + 1, r.x1, r.y1 + 1.6), color=None, fill=(0, 0, 0))
    path = tmp_path / "q.pdf"
    doc.save(path)
    (q,) = parse_questions(path)
    assert q["lua_chon"] == ["Biển 1.", "Biển 2.", "Biển 1 và biển 3.", "Cả ba biển."]
    assert q["dap_an"] == 4


def test_parse_questions_marks_missing_or_multiple_answers(tmp_path, fonts):
    doc = pymupdf.open()
    p = _Page(doc)
    p.line("Câu 3. Không có gạch chân?", bold=True)
    p.line("1. A")
    p.line("2. B")
    path = tmp_path / "q.pdf"
    doc.save(path)
    (q,) = parse_questions(path)
    assert q["dap_an"] is None


def test_parse_cv_lists_reads_three_annexes():
    lines = ["PHỤ LỤC 1", "NHÓM 250 CÂU", "1.  Nhóm câu hỏi Quy định chung (100 câu trong bộ", "600 câu hỏi)",
             "1", "2", "19", "6. Nhóm 20 câu/60 câu về xử lý tình huống", "19",
             "PHỤ LỤC 2", "300 CÂU HỎI", "1. Nhóm (110 câu trong bộ", "600 câu hỏi)", "1", "3",
             "PHỤ LỤC 3", "60 CÂU HỎI", "(Kèm theo văn bản số  2262/CSGT-P5 ngày 07 tháng 5 năm 2025)", "19", "20"]
    assert parse_cv_lists(lines) == {"hang_A1_A": {1, 2, 19}, "hang_B1": {1, 3}, "diem_liet": {19, 20}}


@pytest.mark.parametrize("n, chuong", [(1, "I"), (180, "I"), (181, "II"), (263, "III"), (300, "IV"),
                                       (301, "V"), (485, "V"), (486, "VI"), (600, "VI")])
def test_chapter_of(n, chuong):
    assert chapter_of(n) == chuong
