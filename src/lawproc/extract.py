import hashlib
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from collections.abc import Iterable

import docx
import pymupdf
from docx.oxml.ns import qn

from lawproc import config
from lawproc.quality import syllable_error_rate


_SPACE_TAGS = {qn("w:br"), qn("w:cr"), qn("w:tab")}


def _text_of(el) -> str:
    parts: list[str] = []
    for n in el.iter(qn("w:t"), *_SPACE_TAGS):
        parts.append(n.text or "" if n.tag == qn("w:t") else " ")
    return re.sub(r"[ \t\r\n]+", " ", "".join(parts)).strip()


def _roman(n: int) -> str:
    out = ""
    for value, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                       (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= value:
            out, n = out + sym, n - value
    return out


def _format_number(n: int, fmt: str) -> str:
    """Số thứ tự theo numFmt của Word (chữ cái theo bảng a–z của Word, không phải trình tự điểm tiếng Việt)."""
    if fmt in ("lowerLetter", "upperLetter"):
        s = chr(ord("a") + (n - 1) % 26) * ((n - 1) // 26 + 1)
        return s if fmt == "lowerLetter" else s.upper()
    if fmt in ("lowerRoman", "upperRoman"):
        return _roman(n).lower() if fmt == "lowerRoman" else _roman(n)
    return str(n)


class _Numbering:
    """Dựng nhãn đánh số tự động (w:numPr) mà Word chỉ vẽ khi hiển thị, không nằm trong w:t.

    Như Word: các w:num dùng chung một abstractNum là cùng một danh sách và đếm nối tiếp; w:num có
    startOverride (nút "Restart numbering") đếm lại từ giá trị đó ở lần dùng đầu tiên. Đếm theo thứ tự
    đoạn trong văn bản (kể cả đoạn trong bảng và đoạn rỗng); cấp sâu hơn bắt đầu lại khi cấp nông hơn tăng.
    """

    def __init__(self, numbering_el) -> None:
        self.levels: dict[str, dict[int, tuple[str, str, int]]] = {}
        self.nums: dict[str, tuple[str, dict[int, int]]] = {}
        self.counters: dict[str, dict[int, int]] = {}
        self.seen: set[str] = set()
        if numbering_el is None:
            return
        for a in numbering_el.iterchildren(qn("w:abstractNum")):
            lv = {}
            for lvl in a.iterchildren(qn("w:lvl")):
                fmt, txt, start = lvl.find(qn("w:numFmt")), lvl.find(qn("w:lvlText")), lvl.find(qn("w:start"))
                lv[int(lvl.get(qn("w:ilvl")))] = (
                    fmt.get(qn("w:val")) if fmt is not None else "decimal",
                    txt.get(qn("w:val")) if txt is not None else "",
                    int(start.get(qn("w:val"))) if start is not None else 1)
            self.levels[a.get(qn("w:abstractNumId"))] = lv
        for n in numbering_el.iterchildren(qn("w:num")):
            overrides = {}
            for ov in n.iterchildren(qn("w:lvlOverride")):
                so = ov.find(qn("w:startOverride"))
                if so is not None:
                    overrides[int(ov.get(qn("w:ilvl")))] = int(so.get(qn("w:val")))
            self.nums[n.get(qn("w:numId"))] = (n.find(qn("w:abstractNumId")).get(qn("w:val")), overrides)

    def label(self, p) -> str:
        num_pr = p.find(f"{qn('w:pPr')}/{qn('w:numPr')}")
        if num_pr is None:
            return ""
        nid_el, ilvl_el = num_pr.find(qn("w:numId")), num_pr.find(qn("w:ilvl"))
        nid = nid_el.get(qn("w:val")) if nid_el is not None else None
        if nid not in self.nums:  # gồm numId "0": bỏ đánh số
            return ""
        ilvl = int(ilvl_el.get(qn("w:val"))) if ilvl_el is not None else 0
        aid, overrides = self.nums[nid]
        levels = self.levels.get(aid, {})
        if ilvl not in levels:
            return ""

        def start(i: int) -> int:
            return overrides.get(i, levels.get(i, ("", "", 1))[2])

        count = self.counters.setdefault(aid, {})
        if nid not in self.seen:
            self.seen.add(nid)
            if overrides:
                for i in [i for i in count if i >= min(overrides)]:
                    del count[i]
        count[ilvl] = count[ilvl] + 1 if ilvl in count else start(ilvl)
        for deeper in [i for i in count if i > ilvl]:
            del count[deeper]
        fmt, text, _ = levels[ilvl]
        if fmt == "bullet":
            return "-"
        return re.sub(r"%(\d)", lambda m: _format_number(count.get(int(m.group(1)) - 1, start(int(m.group(1)) - 1)),
                                                          levels.get(int(m.group(1)) - 1, ("decimal",))[0]),
                      text).strip()


# Nhãn gõ tay ở đầu đoạn ("1.", "2.1.", "a)", "đ)", "(1)", "-"): khi đã có thì không chèn nhãn tự động,
# vì bản PDF chính thức chỉ in nhãn gõ tay (đoạn vừa có chữ "1. Nhiệm vụ" vừa gắn numPr trong TT 12).
_TYPED_LABEL = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s|[a-zđ]\d?\)\s|\(\d+\)|[-–+•]\s)")


def _para_text(p, numbering: _Numbering) -> str:
    """Chữ của đoạn kèm nhãn đánh số tự động; đoạn rỗng vẫn tăng bộ đếm như Word hiển thị."""
    label, t = numbering.label(p), _text_of(p)
    return f"{label} {t}" if label and t and not _TYPED_LABEL.match(t) else t


def _cell_text(tc, numbering: _Numbering) -> str:
    """Chữ của một ô: các đoạn trực tiếp trong ô, bảng lồng được đọc đúng một lần tại chỗ."""
    parts: list[str] = []
    for el in tc.iterchildren():
        if el.tag == qn("w:p"):
            t = _para_text(el, numbering)
            if t:
                parts.append(t)
        elif el.tag == qn("w:tbl"):
            parts.extend(_table_rows(el, numbering))
    return " ".join(parts)


def _table_rows(tbl, numbering: _Numbering) -> list[str]:
    """Mỗi hàng trực tiếp của bảng thành một dòng "ô | ô"; ô gộp chỉ có một w:tc nên không lặp."""
    rows: list[str] = []
    for tr in tbl.iterchildren(qn("w:tr")):
        cells: list[str] = []
        for tc in tr.iterchildren(qn("w:tc")):
            c = _cell_text(tc, numbering)
            if c and (not cells or cells[-1] != c):
                cells.append(c)
        if cells:
            rows.append(" | ".join(cells))
    return rows


def docx_lines(path: Path) -> list[str]:
    document = docx.Document(str(path))
    try:
        numbering = _Numbering(document.part.numbering_part.element)
    except (KeyError, NotImplementedError):
        numbering = _Numbering(None)
    out: list[str] = []
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            t = _para_text(child, numbering)
            if t:
                out.append(t)
        elif tag == "tbl":
            out.extend(_table_rows(child, numbering))
    return out


def text_lines(path: Path) -> list[str]:
    """Văn bản chữ thuần UTF-8 (có thể có BOM): mỗi dòng không rỗng là một đoạn, chuẩn hóa NFC."""
    text = unicodedata.normalize("NFC", path.read_text(encoding="utf-8-sig"))
    return [s for s in (ln.strip() for ln in text.splitlines()) if s]


def pdf_lines(path: Path) -> list[str]:
    with pymupdf.open(str(path)) as doc:
        return [ln for page in doc for ln in page.get_text().splitlines()]


def is_scanned(path: Path, sample_pages: int = 5, min_chars: int = 200) -> bool:
    with pymupdf.open(str(path)) as doc:
        n = min(sample_pages, doc.page_count)
        chars = sum(len(doc[i].get_text().strip()) for i in range(n))
    return n == 0 or chars / n < min_chars


def _check_source(path: Path, cache_dir: Path) -> None:
    """Chỉ dùng cache đã gắn với đúng nguồn; cache cũ cần được xác minh trước."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    marker = cache_dir / "source.sha256"
    if marker.exists():
        if marker.read_text(encoding="utf-8").strip() != sha:
            raise ValueError(f"Cache OCR {cache_dir} có sha256 khác {path.name}")
    else:
        if any(cache_dir.iterdir()):
            raise ValueError(f"Cache OCR {cache_dir} thiếu source.sha256; cần xác minh nguồn trước khi dùng")
        marker.write_text(sha + "\n", encoding="utf-8")


def _ocr_page(page, i: int, cache_dir: Path, dpi: int, tmp: str) -> str:
    cached = cache_dir / f"dpi{dpi}" / f"p{i:04d}.txt"
    if not cached.exists():
        cached.parent.mkdir(parents=True, exist_ok=True)
        png = Path(tmp) / f"p{i:04d}_{dpi}.png"
        try:
            page.get_pixmap(dpi=dpi).save(str(png))
            r = subprocess.run(
                [str(config.TESSERACT), "--tessdata-dir", config.TESSDATA_REL, str(png), "-",
                 "-l", "vie", "--psm", "6"],
                cwd=config.ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            if r.returncode != 0:
                raise RuntimeError(f"Tesseract lỗi ở trang {i} ({cache_dir.name}, dpi {dpi}): {r.stderr.strip()}")
            staged = cached.with_suffix(".tmp")
            staged.write_text(r.stdout, encoding="utf-8")
            staged.replace(cached)
        finally:
            png.unlink(missing_ok=True)
    try:
        return cached.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise ValueError(f"Cache OCR không phải UTF-8: {cached}") from exc


def ocr_pdf_lines(path: Path, cache_dir: Path, dpi: int = 300, retry_pages: Iterable[int] = (),
                  retry_dpi: int = 400) -> list[str]:
    """OCR tuần tự; thử lại trang được chỉ định và giữ bản có ít nhiễu chữ hơn."""
    for value in (dpi, retry_dpi):
        if type(value) is not int or value <= 0:
            raise ValueError("DPI phải là số nguyên dương")
    retry_list = list(retry_pages)
    lines: list[str] = []
    with pymupdf.open(str(path)) as doc, tempfile.TemporaryDirectory() as tmp:
        if any(type(i) is not int or not 0 <= i < len(doc) for i in retry_list):
            raise ValueError("Trang OCR lại phải là số nguyên trong phạm vi PDF (từ 0)")
        retry = set(retry_list)
        _check_source(path, cache_dir)
        for i, page in enumerate(doc):
            text = _ocr_page(page, i, cache_dir, dpi, tmp)
            if i in retry:
                other = _ocr_page(page, i, cache_dir, retry_dpi, tmp)
                # OCR rỗng không phải bản tốt hơn của một trang đang có chữ.
                if other.strip() and syllable_error_rate(other) < syllable_error_rate(text):
                    text = other
            lines.extend(text.splitlines())
    return lines
