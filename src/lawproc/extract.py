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


def _cell_text(tc) -> str:
    """Chữ của một ô: các đoạn trực tiếp trong ô, bảng lồng được đọc đúng một lần tại chỗ."""
    parts: list[str] = []
    for el in tc.iterchildren():
        if el.tag == qn("w:p"):
            t = _text_of(el)
            if t:
                parts.append(t)
        elif el.tag == qn("w:tbl"):
            parts.extend(_table_rows(el))
    return " ".join(parts)


def _table_rows(tbl) -> list[str]:
    """Mỗi hàng trực tiếp của bảng thành một dòng "ô | ô"; ô gộp chỉ có một w:tc nên không lặp."""
    rows: list[str] = []
    for tr in tbl.iterchildren(qn("w:tr")):
        cells: list[str] = []
        for tc in tr.iterchildren(qn("w:tc")):
            c = _cell_text(tc)
            if c and (not cells or cells[-1] != c):
                cells.append(c)
        if cells:
            rows.append(" | ".join(cells))
    return rows


def docx_lines(path: Path) -> list[str]:
    body = docx.Document(str(path)).element.body
    out: list[str] = []
    for child in body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            t = _text_of(child)
            if t:
                out.append(t)
        elif tag == "tbl":
            out.extend(_table_rows(child))
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
