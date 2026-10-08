import re
import subprocess
import tempfile
from pathlib import Path

import docx
import pymupdf
from docx.oxml.ns import qn

from lawproc import config


_SPACE_TAGS = {qn("w:br"), qn("w:cr"), qn("w:tab")}


def _text_of(el) -> str:
    parts: list[str] = []
    for n in el.iter(qn("w:t"), *_SPACE_TAGS):
        parts.append(n.text or "" if n.tag == qn("w:t") else " ")
    return re.sub(r"[ \t\r\n]+", " ", "".join(parts)).strip()


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
            for tr in child.iter(qn("w:tr")):
                cells: list[str] = []
                for tc in tr.iter(qn("w:tc")):
                    c = " ".join(_text_of(p) for p in tc.iter(qn("w:p"))).strip()
                    if c and (not cells or cells[-1] != c):
                        cells.append(c)
                if cells:
                    out.append(" | ".join(cells))
    return out


def pdf_lines(path: Path) -> list[str]:
    with pymupdf.open(str(path)) as doc:
        return [ln for page in doc for ln in page.get_text().splitlines()]


def is_scanned(path: Path, sample_pages: int = 5, min_chars: int = 200) -> bool:
    with pymupdf.open(str(path)) as doc:
        n = min(sample_pages, doc.page_count)
        chars = sum(len(doc[i].get_text().strip()) for i in range(n))
    return n == 0 or chars / n < min_chars


def ocr_pdf_lines(path: Path, cache_dir: Path, dpi: int = 300) -> list[str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    with pymupdf.open(str(path)) as doc, tempfile.TemporaryDirectory() as tmp:
        for i, page in enumerate(doc):
            cached = cache_dir / f"p{i:04d}.txt"
            if not cached.exists():
                png = Path(tmp) / f"p{i:04d}.png"
                page.get_pixmap(dpi=dpi).save(str(png))
                r = subprocess.run(
                    [str(config.TESSERACT), "--tessdata-dir", config.TESSDATA_REL, str(png), "-",
                     "-l", "vie", "--psm", "6"],
                    cwd=config.ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
                )
                cached.write_text(r.stdout, encoding="utf-8")
                png.unlink()
            lines.extend(cached.read_text(encoding="utf-8").splitlines())
    return lines
