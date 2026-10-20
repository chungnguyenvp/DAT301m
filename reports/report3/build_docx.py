"""Chuyển `report_3_mo_hinh_ket_qua.md` thành `Report_3_Mo_hinh_va_ket_qua.docx`.

    py -3.13 reports/report3/make_figures.py
    py -3.13 reports/report3/build_docx.py

Hỗ trợ đúng phần Markdown mà báo cáo dùng: tiêu đề #, ##, ###; đoạn văn; danh sách gạch đầu dòng (2 cấp) và đánh số;
bảng; hình `![chú thích](đường dẫn)`; **đậm** và `mã` trong dòng; `---` là ngắt trang sau phần thông tin đầu.
"""

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
SRC = HERE / "report_3_mo_hinh_ket_qua.md"
OUT = HERE / "Report_3_Mo_hinh_va_ket_qua.docx"
FONT = "Calibri"
BLUE = RGBColor(0x24, 0x5B, 0x85)
TEXT_WIDTH_CM = 16.4

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2)
sec.left_margin = sec.right_margin = Cm(2.3)

for name in ("Normal", "Title", "Heading 1", "Heading 2", "List Bullet", "List Bullet 2", "Caption"):
    st = doc.styles[name]
    st.font.name = FONT
    st.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    if name.startswith("Heading") or name == "Title":
        st.font.color.rgb = BLUE
normal = doc.styles["Normal"]
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.1
doc.styles["Title"].font.size = Pt(24)
for name, size, before in (("Heading 1", 15, 16), ("Heading 2", 12.5, 10)):
    st = doc.styles[name]
    st.font.size = Pt(size)
    st.font.bold = True
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.keep_with_next = True

# Số trang ở chân trang
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
    run = fp.add_run()
    if kind:
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
    else:
        el = OxmlElement("w:instrText")
        el.set(qn("xml:space"), "preserve")
        el.text = text
    run._r.append(el)

INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def inline(p, text: str, size: float | None = None, bold: bool = False) -> None:
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            r = p.add_run(piece[2:-2])
            r.bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = p.add_run(piece[1:-1])
            r.font.name = "Consolas"
            r._r.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Consolas")
            r.font.size = Pt((size or 11) - 1.5)
        else:
            r = p.add_run(piece)
            r.bold = bold or None
        if size and not piece.startswith("`"):
            r.font.size = Pt(size)


def shade(cell, color: str) -> None:
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(sh)


def plain(text: str) -> str:
    return re.sub(r"\*\*|`", "", text)


def add_table(lines: list[str]) -> None:
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
    ncol = len(rows[0])
    t = doc.add_table(rows=0, cols=ncol)
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    # Độ rộng cột theo độ dài chữ, cột đầu được ưu tiên
    lens = [max(max(min(len(plain(r[j])), 60) for r in rows) + 4, 10) for j in range(ncol)]
    widths = [TEXT_WIDTH_CM * x / sum(lens) for x in lens]
    numeric = [all(re.fullmatch(r"[\d\s,.%/+−\-–\[\];*↑↓()a-zA-Z_]*", plain(r[j])) and any(ch.isdigit() for ch in r[j])
                   for r in rows[1:]) for j in range(ncol)]
    for i, vals in enumerate(rows):
        row = t.add_row()
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        for j, val in enumerate(vals):
            cell = row.cells[j]
            cell.width = Cm(widths[j])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            if j > 0 and numeric[j]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            inline(p, val, size=9.5, bold=(i == 0))
            if i == 0:
                shade(cell, "DCE8F3")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_image(caption: str, path: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(HERE / path), width=Cm(15.5))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption)
    r.italic = True
    r.font.size = Pt(9.5)


def add_item(text: str, level: int, number: str | None) -> None:
    if number:
        p = doc.add_paragraph()
        indent = 0.63 + 0.63 * level
        p.paragraph_format.left_indent = Cm(indent)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        p.paragraph_format.space_after = Pt(3)
        p.add_run(f"{number}\t")
        p.paragraph_format.tab_stops.add_tab_stop(Cm(indent))
    else:
        p = doc.add_paragraph(style="List Bullet 2" if level else "List Bullet")
        p.paragraph_format.space_after = Pt(3)
    inline(p, text)


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    i, header = 0, True
    para: list[str] = []

    def flush() -> None:
        if para:
            p = doc.add_paragraph()
            if header:
                p.paragraph_format.space_after = Pt(2)
            inline(p, " ".join(s.strip() for s in para))
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush()
            i += 1
            continue
        if s == "---":
            flush()
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            header = False
            i += 1
            continue
        if s.startswith("# "):
            flush()
            doc.add_paragraph(s[2:], style="Title")
            i += 1
            continue
        if s.startswith("## "):
            flush()
            doc.add_heading(s[3:], level=1)
            i += 1
            continue
        if s.startswith("### "):
            flush()
            doc.add_heading(s[4:], level=2)
            i += 1
            continue
        if s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(block)
            continue
        m = re.fullmatch(r"!\[(.+)\]\((.+)\)", s)
        if m:
            flush()
            add_image(m.group(1), m.group(2))
            i += 1
            continue
        m = re.match(r"^( *)(- |(\d+)\. )(.*)$", ln)
        if m:
            flush()
            indent, number, text = len(m.group(1)), m.group(3), m.group(4)
            level = 1 if indent >= 2 else 0
            i += 1
            # dòng tiếp theo thụt vào (không phải mục mới) là phần nối của mục này
            base = indent + len(m.group(2))
            while i < len(lines) and lines[i].strip() and not re.match(r"^ *(- |\d+\. )", lines[i]) \
                    and len(lines[i]) - len(lines[i].lstrip()) >= base:
                text += " " + lines[i].strip()
                i += 1
            add_item(text, level, f"{number}." if number else None)
            continue
        para.append(s)
        if header and s.startswith("**"):  # mỗi dòng thông tin đầu là một đoạn riêng
            flush()
        i += 1
    flush()
    doc.core_properties.title = "Report 3 — Mô hình và kết quả"
    doc.core_properties.subject = "DAT301m — Hỏi đáp pháp luật giao thông đường bộ theo hiệu lực văn bản"
    doc.save(OUT)
    print("->", OUT.name)


if __name__ == "__main__":
    main()
