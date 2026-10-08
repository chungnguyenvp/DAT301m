# Xử lý văn bản luật — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Biến 94 file gốc trong `data/raw/` thành văn bản sạch và bảng đơn vị Điều/Khoản/Điểm có ngày hiệu lực và quan hệ sửa đổi.

**Architecture:** Gói Python `lawproc` trong `src/`, mỗi module một việc: chuyển `.doc`→`.docx` (Word COM), trích chữ (docx, PDF có lớp chữ, OCR Tesseract), làm sạch và ghép các phần Công báo, kiểm tra danh tính văn bản, tách cấu trúc, tìm ngày hiệu lực, trích chỉ dẫn sửa đổi, áp sửa đổi thành các phiên bản có `valid_from`/`valid_to`. Script `scripts/process_legal.py` chạy từng bước. Hai bước cần người duyệt (ngày hiệu lực, chỉ dẫn sửa đổi) xuất CSV để duyệt rồi mới áp.

**Tech Stack:** Python 3.13, python-docx 1.2, PyMuPDF 1.28 (`import pymupdf`), pywin32 (Word COM), Tesseract 5.4 + `tools/tessdata/vie.traineddata`, pytest 9.

**Ngoài phạm vi kế hoạch này:** nạp PostgreSQL/pgvector (chuyển sang kế hoạch xây kho tra cứu, vì cần thông tin đăng nhập database), tách đề GPLX 600 câu (kế hoạch riêng), EDA.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-10-08-traffic-law-qa-design.md` mục 5.4–5.5.
- `data/raw/` không bao giờ bị sửa; mọi đầu ra ghi vào `data/interim/` (gitignored) hoặc `data/processed/` (commit).
- Ngày chốt dữ liệu: `2026-10-01`.
- Chuẩn hóa Unicode NFC; đổi ký tự Kirin `Р`/`р` (U+0420/U+0440) thành `P`/`p` (Công báo có tiêu đề ghi "NĐ-CР").
- Tesseract: `C:\Program Files\Tesseract-OCR\tesseract.exe`; gọi với `cwd=ROOT` và `--tessdata-dir tools/tessdata` (đường dẫn tương đối, vì Tesseract trên Windows lỗi với đường dẫn có dấu); ảnh trang để trong thư mục tạm của hệ thống.
- Văn bản dạng scan phải OCR: `tt_108_2026_bca`, `tt_155_2025_btc`, `tt_36_2024_byt`.
- Không phải văn bản luật (bỏ qua trong kế hoạch này): `gplx_600_2025`, `cv_2262_2025_csgt`.
- Chạy test: `python -m pytest -q` từ thư mục gốc repo.
- Commit kết thúc bằng dòng `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File Structure

| File | Trách nhiệm |
|---|---|
| `pytest.ini` | `pythonpath = src`, `testpaths = tests` |
| `src/lawproc/__init__.py` | Gói rỗng |
| `src/lawproc/config.py` | Đường dẫn, hằng số, bảng tên văn bản → `doc_id` |
| `src/lawproc/clean.py` | `normalize`, `strip_part`, `order_parts`, `join_wrapped` |
| `src/lawproc/extract.py` | `docx_lines`, `pdf_lines`, `is_scanned`, `ocr_pdf_lines` |
| `src/lawproc/convert.py` | `convert_doc_files` (Word COM) |
| `src/lawproc/assemble.py` | `group_rows`, `assemble_doc`, `article_report` |
| `src/lawproc/verify.py` | `check_identity` |
| `src/lawproc/structure.py` | `Unit`, `parse_units` |
| `src/lawproc/effective.py` | `find_effective`, `decide_effective` |
| `src/lawproc/amendments.py` | `extract_instructions` |
| `src/lawproc/apply.py` | `apply_amendments` |
| `scripts/process_legal.py` | CLI chạy từng bước, ghi đầu ra và báo cáo |
| `tests/test_*.py` | Test từng module |

Đầu ra:
- `data/interim/docx/` (docx đã chuyển), `data/interim/ocr/<file>/pNNNN.txt` (cache OCR) — gitignored.
- `data/processed/documents/<doc_id>.txt` — văn bản sạch.
- `data/processed/assembly_report.csv`, `identity_report.csv`.
- `data/processed/legal_units.jsonl` — đơn vị chưa áp sửa đổi.
- `data/processed/effective_dates.csv` — ngày hiệu lực (có cột duyệt).
- `data/processed/amendments_candidates.csv` → người duyệt lưu thành `amendments_reviewed.csv`.
- `data/processed/legal_units_versioned.jsonl` — đơn vị có `valid_from`/`valid_to`.
- `data/processed/PROCESSING_REPORT.md`.

---

### Task 1: Khung dự án và làm sạch văn bản

**Files:**
- Create: `pytest.ini`, `src/lawproc/__init__.py`, `src/lawproc/config.py`, `src/lawproc/clean.py`
- Test: `tests/test_clean.py`

**Interfaces:**
- Produces:
  - `config`: `ROOT: Path`, `DATA`, `RAW`, `INTERIM`, `PROCESSED`, `MANIFEST: Path`, `TESSERACT: Path`, `TESSDATA_REL: str`, `CUTOFF: str`, `SCANNED_DOCS: set[str]`, `NON_LEGAL: set[str]`, `TARGET_ALIASES: dict[str, str]`, `AMENDING_DOCS: set[str]`
  - `normalize(s: str) -> str`
  - `strip_part(lines: list[str]) -> tuple[list[str], int | None]` — trả dòng đã bỏ rác và số Công báo trong "(Tiếp theo Công báo số N …)" nếu có
  - `order_parts(parts: list[tuple[list[str], int | None]]) -> list[list[str]]`
  - `join_wrapped(lines: list[str]) -> list[str]` — nối dòng bị ngắt (dùng cho PDF/OCR)

- [ ] **Step 1: Tạo `pytest.ini` và gói rỗng**

`pytest.ini`:
```ini
[pytest]
pythonpath = src
testpaths = tests
```
`src/lawproc/__init__.py`: file rỗng.

- [ ] **Step 2: Viết `src/lawproc/config.py`**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
MANIFEST = DATA / "manifest.csv"

TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_REL = "tools/tessdata"  # tương đối với ROOT

CUTOFF = "2026-10-01"
SCANNED_DOCS = {"tt_108_2026_bca", "tt_155_2025_btc", "tt_36_2024_byt"}
NON_LEGAL = {"gplx_600_2025", "cv_2262_2025_csgt"}

# Văn bản có chứa chỉ dẫn sửa đổi văn bản khác
AMENDING_DOCS = {
    "luat_118_2025", "nd_238_2026", "nd_241_2026", "nd_218_2026", "nd_220_2026",
    "tt_37_2026_bca", "tt_51_2025_bca", "nd_51_2025", "nd_175_2025",
}

# Chuỗi nhận diện văn bản bị sửa → doc_id (so khớp sau normalize, không phân biệt hoa thường)
TARGET_ALIASES = {
    "168/2024/NĐ-CP": "nd_168_2024",
    "165/2024/NĐ-CP": "nd_165_2024",
    "158/2024/NĐ-CP": "nd_158_2024",
    "67/2023/NĐ-CP": "nd_67_2023",
    "10/2022/NĐ-CP": "nd_10_2022",
    "79/2024/TT-BCA": "tt_79_2024_bca",
    "12/2025/TT-BCA": "tt_12_2025_bca",
    "Luật Trật tự, an toàn giao thông đường bộ": "luat_36_2024",
    "Luật Đường bộ": "luat_35_2024",
}
```

- [ ] **Step 3: Viết test thất bại `tests/test_clean.py`**

```python
from lawproc.clean import normalize, strip_part, order_parts, join_wrapped


def test_normalize_nfc_cyrillic_and_spaces():
    decomposed = "Nghi\u0323 đi\u0323nh 168/2024/NĐ-C\u0420\u00a0 mới"
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
```

- [ ] **Step 4: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_clean.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.clean'`

- [ ] **Step 5: Viết `src/lawproc/clean.py`**

```python
import re
import unicodedata

CONGBAO_HEADER = re.compile(
    r"^(?:\d{1,4}\s+)?CÔNG BÁO\s*/\s*Số\s*[\d\s+]+/\s*Ngày\s*\d{1,2}-\d{1,2}-\d{4}(?:\s+\d{1,4})?$",
    re.IGNORECASE,
)
PAGE_NO = re.compile(r"^\d{1,4}$")
BANNERS = {
    "VĂN BẢN QUY PHẠM PHÁP LUẬT", "PHẦN VĂN BẢN QUY PHẠM PHÁP LUẬT", "VĂN BẢN KHÁC",
    "VĂN BẢN PHÁP LUẬT KHÁC", "VĂN BẢN HỢP NHẤT - VĂN PHÒNG QUỐC HỘI",
}
XEM_TIEP = re.compile(r"^\(\s*Xem tiếp Công báo số[^)]*\)\.?$", re.IGNORECASE)
TIEP_THEO = re.compile(r"^\(\s*Tiếp theo Công báo số\s*(\d+)", re.IGNORECASE)
STRUCT_START = re.compile(
    r"^(?:Phần|PHẦN|Chương|CHƯƠNG|Mục|MỤC|PHỤ LỤC|Phụ lục|Điều\s+\d+|\d+[a-zđ]?\.\s|[a-zđ]{1,2}\)\s|[“\"])"
)
END_PUNCT = (".", ":", ";", "!", "?", "”", "\"", ")")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ").replace("\u0420", "P").replace("\u0440", "p")
    return re.sub(r"[ \t]+", " ", s).strip()


def strip_part(lines: list[str]) -> tuple[list[str], int | None]:
    lines = [normalize(x) for x in lines]
    cont = None
    for i, line in enumerate(lines[:20]):
        m = TIEP_THEO.match(line)
        if m:
            cont = int(m.group(1))
            lines = lines[i + 1:]
            break
    out = [
        x for x in lines
        if x and not CONGBAO_HEADER.match(x) and not PAGE_NO.match(x)
        and x.upper() not in BANNERS and not XEM_TIEP.match(x)
    ]
    return out, cont


def order_parts(parts: list[tuple[list[str], int | None]]) -> list[list[str]]:
    return [p for p, _ in sorted(parts, key=lambda pc: -1 if pc[1] is None else pc[1])]


def join_wrapped(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in (normalize(x) for x in lines):
        if not line:
            continue
        if out and not STRUCT_START.match(line) and not out[-1].endswith(END_PUNCT):
            out[-1] = f"{out[-1]} {line}"
        else:
            out.append(line)
    return out
```

- [ ] **Step 6: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_clean.py -q`
Expected: `5 passed`

- [ ] **Step 7: Commit**

```bash
git add pytest.ini src/lawproc/__init__.py src/lawproc/config.py src/lawproc/clean.py tests/test_clean.py
git commit -m "Add lawproc package with text cleaning helpers"
```

---

### Task 2: Trích chữ từ docx, PDF và OCR

**Files:**
- Create: `src/lawproc/extract.py`
- Test: `tests/test_extract.py`

**Interfaces:**
- Consumes: `config.TESSERACT`, `config.TESSDATA_REL`, `config.ROOT`
- Produces:
  - `docx_lines(path: Path) -> list[str]` — đoạn văn và hàng bảng theo đúng thứ tự trong tài liệu; ô bảng nối bằng `" | "`
  - `pdf_lines(path: Path) -> list[str]`
  - `is_scanned(path: Path, sample_pages: int = 5, min_chars: int = 200) -> bool`
  - `ocr_pdf_lines(path: Path, cache_dir: Path, dpi: int = 300) -> list[str]` — cache mỗi trang vào `cache_dir/pNNNN.txt`

- [ ] **Step 1: Viết test thất bại `tests/test_extract.py`**

```python
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
    assert pdf_lines(p)[0].startswith("Điều 1.")
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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_extract.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.extract'`

- [ ] **Step 3: Viết `src/lawproc/extract.py`**

```python
import subprocess
import tempfile
from pathlib import Path

import docx
import pymupdf
from docx.oxml.ns import qn

from lawproc import config


def _text_of(el) -> str:
    return "".join(n.text or "" for n in el.iter(qn("w:t"))).strip()


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
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_extract.py -q`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/extract.py tests/test_extract.py
git commit -m "Add docx, PDF and Tesseract OCR text extraction"
```

---

### Task 3: Chuyển `.doc` sang `.docx` bằng Word

**Files:**
- Create: `src/lawproc/convert.py`
- Test: `tests/test_convert.py`

**Interfaces:**
- Consumes: `config.RAW`, `config.INTERIM`
- Produces: `convert_doc_files(src_dir: Path, out_dir: Path) -> list[Path]` — chuyển mọi `*.doc`, sao chép mọi `*.docx` có sẵn sang `out_dir`; bỏ qua file đã có; trả danh sách file `.docx` trong `out_dir`

- [ ] **Step 1: Viết test thất bại `tests/test_convert.py`**

```python
import shutil

import docx
import pytest

from lawproc import config
from lawproc.convert import convert_doc_files

SAMPLE = config.RAW / "legal" / "nd_51_2025__p2.doc"


def test_copies_existing_docx(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    d = docx.Document()
    d.add_paragraph("Điều 1.")
    d.save(src / "a__p1.docx")
    assert [p.name for p in convert_doc_files(src, out)] == ["a__p1.docx"]


@pytest.mark.skipif(not SAMPLE.exists(), reason="chưa có dữ liệu thô")
def test_converts_real_doc_with_word(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    shutil.copy(SAMPLE, src / SAMPLE.name)
    result = convert_doc_files(src, out)
    assert [p.name for p in result] == ["nd_51_2025__p2.docx"]
    text = "\n".join(p.text for p in docx.Document(result[0]).paragraphs)
    assert "10/2022/NĐ-CP" in text
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_convert.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.convert'`

- [ ] **Step 3: Viết `src/lawproc/convert.py`**

```python
import shutil
from pathlib import Path

WD_FORMAT_DOCX = 16


def convert_doc_files(src_dir: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(src_dir.glob("*.docx")):
        if not (out_dir / p.name).exists():
            shutil.copy2(p, out_dir / p.name)
    todo = [p for p in sorted(src_dir.glob("*.doc")) if not (out_dir / f"{p.stem}.docx").exists()]
    if todo:
        import win32com.client

        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        try:
            for p in todo:
                d = word.Documents.Open(str(p), False, True)
                d.SaveAs2(str(out_dir / f"{p.stem}.docx"), WD_FORMAT_DOCX)
                d.Close(False)
        finally:
            word.Quit()
    return sorted(out_dir.glob("*.docx"))
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_convert.py -q`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/convert.py tests/test_convert.py
git commit -m "Convert legacy .doc files to .docx via Word COM"
```

---

### Task 4: Ghép các phần Công báo thành một văn bản

**Files:**
- Create: `src/lawproc/assemble.py`
- Test: `tests/test_assemble.py`

**Interfaces:**
- Consumes: `clean.strip_part`, `clean.order_parts`, `clean.join_wrapped`, `clean.normalize`; `extract.docx_lines`, `extract.pdf_lines`, `extract.is_scanned`, `extract.ocr_pdf_lines`; `config.SCANNED_DOCS`, `config.NON_LEGAL`
- Produces:
  - `group_rows(rows: list[dict]) -> dict[str, list[dict]]` — nhóm dòng manifest theo `doc_id`, giữ thứ tự, bỏ `NON_LEGAL`
  - `pick_sources(rows: list[dict]) -> tuple[list[dict], str]` — ưu tiên file Word (`"docx"`); không có thì PDF, trả `"ocr"` nếu thuộc `SCANNED_DOCS` hoặc scan, ngược lại `"pdf"`
  - `assemble_doc(doc_id: str, part_lines: list[list[str]], method: str) -> list[str]`
  - `article_report(doc_id: str, lines: list[str], method: str, n_parts: int) -> dict` — khóa `doc_id, method, n_parts, n_lines, n_dieu, first_dieu, last_dieu, missing_dieu`

- [ ] **Step 1: Viết test thất bại `tests/test_assemble.py`**

```python
from lawproc.assemble import group_rows, pick_sources, assemble_doc, article_report


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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_assemble.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.assemble'`

- [ ] **Step 3: Viết `src/lawproc/assemble.py`**

```python
import re
from pathlib import Path

from lawproc import config
from lawproc.clean import join_wrapped, order_parts, strip_part
from lawproc.extract import is_scanned

DIEU_LINE = re.compile(r"^Điều\s+(\d+)[a-zđ]?\.")


def group_rows(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        if r["doc_id"] not in config.NON_LEGAL:
            groups.setdefault(r["doc_id"], []).append(r)
    return groups


def pick_sources(rows: list[dict]) -> tuple[list[dict], str]:
    word = [r for r in rows if r["dinh_dang"] in ("doc", "docx")]
    if word:
        return word, "docx"
    pdfs = [r for r in rows if r["dinh_dang"] == "pdf"]
    doc_id = rows[0]["doc_id"]
    scanned = doc_id in config.SCANNED_DOCS or any(
        is_scanned(config.ROOT / r["file"]) for r in pdfs if (config.ROOT / r["file"]).exists()
    )
    return pdfs, "ocr" if scanned else "pdf"


def assemble_doc(doc_id: str, part_lines: list[list[str]], method: str) -> list[str]:
    ordered = order_parts([strip_part(p) for p in part_lines])
    lines = [x for part in ordered for x in part]
    return join_wrapped(lines) if method in ("pdf", "ocr") else lines


def article_report(doc_id: str, lines: list[str], method: str, n_parts: int) -> dict:
    nums = sorted({int(m.group(1)) for x in lines if (m := DIEU_LINE.match(x))})
    missing = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)] if nums else []
    return {
        "doc_id": doc_id, "method": method, "n_parts": n_parts, "n_lines": len(lines),
        "n_dieu": len(nums), "first_dieu": nums[0] if nums else None,
        "last_dieu": nums[-1] if nums else None, "missing_dieu": " ".join(map(str, missing)),
    }
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_assemble.py -q`
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/assemble.py tests/test_assemble.py
git commit -m "Assemble multi-issue Công báo parts into one document"
```

---

### Task 5: Kiểm tra danh tính văn bản

Sinh ra từ lỗi đã gặp: số ký hiệu `91/2015/QH13` trùng giữa Bộ luật Dân sự và một Nghị quyết.

**Files:**
- Create: `src/lawproc/verify.py`
- Test: `tests/test_verify.py`

**Interfaces:**
- Consumes: `clean.normalize`
- Produces: `check_identity(doc_id: str, so_ky_hieu: str, tieu_de: str, text: str, head_chars: int = 4000) -> dict` — khóa `doc_id, so_hieu_found, title_ratio, status` với `status ∈ {"ok", "kiem_tra_tay"}`

- [ ] **Step 1: Viết test thất bại `tests/test_verify.py`**

```python
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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_verify.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.verify'`

- [ ] **Step 3: Viết `src/lawproc/verify.py`**

```python
import re

from lawproc.clean import normalize

STOP = {"của", "và", "các", "về", "đối", "với", "trong", "theo", "quy", "định", "việc", "người"}


def _words(s: str) -> list[str]:
    return [w for w in re.findall(r"\w+", normalize(s).lower()) if len(w) >= 3 and w not in STOP]


def check_identity(doc_id: str, so_ky_hieu: str, tieu_de: str, text: str, head_chars: int = 4000) -> dict:
    head = normalize(text[:head_chars])
    compact = re.sub(r"\s+", "", head).upper()
    key = re.sub(r"\s+", "", so_ky_hieu).upper()
    found = key in compact
    if normalize(tieu_de) == normalize(so_ky_hieu):
        ratio = 1.0
    else:
        words = _words(tieu_de)
        head_words = set(_words(head))
        ratio = round(sum(w in head_words for w in words) / len(words), 2) if words else 1.0
    status = "ok" if found and ratio >= 0.6 else "kiem_tra_tay"
    return {"doc_id": doc_id, "so_hieu_found": found, "title_ratio": ratio, "status": status}
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_verify.py -q`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/verify.py tests/test_verify.py
git commit -m "Check document identity by number and title words"
```

---

### Task 6: Tách cấu trúc Chương/Mục/Điều/Khoản/Điểm

**Files:**
- Create: `src/lawproc/structure.py`
- Test: `tests/test_structure.py`

**Interfaces:**
- Produces:
  - `@dataclass Unit(unit_id, doc_id, level, chuong=None, muc=None, dieu=None, khoan=None, diem=None, title="", text="", line_start=0)` với `level ∈ {"mo_dau","dieu","khoan","diem","phu_luc","ket_thuc"}` và `as_dict() -> dict`
  - `unit_address(doc_id: str, dieu: str | None, khoan: str | None, diem: str | None) -> str` — ví dụ `nd_168_2024:d7:k2:h`
  - `parse_units(doc_id: str, lines: list[str], dieu: str | None = None, khoan: str | None = None) -> list[Unit]` — khi truyền `dieu`, chạy ở chế độ "đoạn trích" (dùng cho nội dung sửa đổi): không tạo `mo_dau`, bắt đầu với ngữ cảnh Điều/Khoản cho trước

Quy tắc:
- Dòng nằm trong ngoặc kép “…” (nội dung sửa đổi được trích dẫn) không được tách cấu trúc, mà nối vào đơn vị đang mở.
- Dòng tiêu đề sau "Chương I"/"Mục 1" được ghép vào tên Chương/Mục, không nối vào đơn vị trước.
- "PHỤ LỤC"/"Phụ lục" (dòng ngắn, sau khi đã gặp Điều) mở đơn vị `phu_luc`; bên trong phụ lục không tách Điều/Khoản.
- Dòng bắt đầu "Nơi nhận" mở đơn vị `ket_thuc`.
- `unit_id` trùng thì thêm hậu tố `#2`, `#3`.

- [ ] **Step 1: Viết test thất bại `tests/test_structure.py`**

```python
from lawproc.structure import parse_units, unit_address

DOC = [
    "CHÍNH PHỦ",
    "Căn cứ Luật Tổ chức Chính phủ;",
    "Chương II",
    "XỬ PHẠT VI PHẠM",
    "Mục 1",
    "VI PHẠM QUY TẮC GIAO THÔNG",
    "Điều 7. Xử phạt người điều khiển xe mô tô",
    "1. Phạt tiền từ 200.000 đồng đến 400.000 đồng đối với hành vi sau đây:",
    "a) Không chấp hành hiệu lệnh;",
    "b) Không có tín hiệu trước khi vượt;",
    "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng.",
    "Điều 8. Hiệu lực thi hành",
    "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2025.",
    "Nơi nhận: | TM. CHÍNH PHỦ",
    "PHỤ LỤC I",
    "1. Mẫu biên bản",
]


def test_unit_address():
    assert unit_address("nd", "7", "2", "h") == "nd:d7:k2:h"
    assert unit_address("nd", "7", None, None) == "nd:d7"


def test_parse_levels_and_context():
    units = {u.unit_id: u for u in parse_units("nd", DOC)}
    assert units["nd:mo_dau"].text == "CHÍNH PHỦ\nCăn cứ Luật Tổ chức Chính phủ;"
    d7 = units["nd:d7"]
    assert (d7.level, d7.title, d7.chuong, d7.muc) == ("dieu", "Xử phạt người điều khiển xe mô tô",
                                                        "II XỬ PHẠT VI PHẠM", "1 VI PHẠM QUY TẮC GIAO THÔNG")
    assert units["nd:d7:k1"].text.startswith("Phạt tiền từ 200.000")
    assert units["nd:d7:k1:b"].text == "Không có tín hiệu trước khi vượt;"
    assert units["nd:d7:k2"].level == "khoan"
    assert units["nd:d8"].text == "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2025."
    assert units["nd:ket_thuc"].level == "ket_thuc"
    assert units["nd:pl1"].title == "PHỤ LỤC I"
    assert "nd:d1" not in units  # "1. Mẫu biên bản" nằm trong phụ lục, không tách


def test_quoted_amendment_is_not_split():
    lines = [
        "Điều 1. Sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
        "1. Sửa đổi, bổ sung khoản 2 Điều 7 như sau:",
        "“2. Phạt tiền từ 600.000 đồng đến 800.000 đồng đối với:",
        "a) Không đội mũ bảo hiểm;",
        "b) Chở quá số người quy định.”",
        "2. Bãi bỏ điểm d khoản 3 Điều 9.",
    ]
    units = {u.unit_id: u for u in parse_units("nd238", lines)}
    k1 = units["nd238:d1:k1"]
    assert k1.text.splitlines()[0] == "Sửa đổi, bổ sung khoản 2 Điều 7 như sau:"
    assert "a) Không đội mũ bảo hiểm;" in k1.text
    assert "nd238:d1:k1:a" not in units
    assert units["nd238:d1:k2"].text == "Bãi bỏ điểm d khoản 3 Điều 9."


def test_fragment_mode_uses_given_context():
    frag = ["2. Phạt tiền từ 600.000 đồng đến 800.000 đồng đối với:", "a) Không đội mũ bảo hiểm;"]
    ids = [u.unit_id for u in parse_units("nd_168_2024", frag, dieu="7")]
    assert ids == ["nd_168_2024:d7:k2", "nd_168_2024:d7:k2:a"]
    ids = [u.unit_id for u in parse_units("nd_10_2022", ["c) Ô tô điện: 0%."], dieu="8", khoan="5")]
    assert ids == ["nd_10_2022:d8:k5:c"]


def test_duplicate_ids_get_suffix():
    ids = [u.unit_id for u in parse_units("x", ["Điều 1. A", "Điều 1. A lặp"])]
    assert ids == ["x:mo_dau", "x:d1", "x:d1#2"]
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_structure.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.structure'`

- [ ] **Step 3: Viết `src/lawproc/structure.py`**

```python
import re
from dataclasses import asdict, dataclass

CHUONG = re.compile(r"^(?:Chương|CHƯƠNG)\s+([IVXLC]+|\d+)\b\.?\s*(.*)$")
MUC = re.compile(r"^(?:Mục|MỤC)\s+(\d+)\b\.?\s*(.*)$")
DIEU = re.compile(r"^Điều\s+(\d+[a-zđ]?)\.\s*(.*)$")
KHOAN = re.compile(r"^(\d+[a-zđ]?)\.\s+(.*)$")
DIEM = re.compile(r"^([a-zđ]{1,2})\)\s+(.*)$")
PHULUC = re.compile(r"^(?:PHỤ LỤC|Phụ lục)\b")
KET_THUC = re.compile(r"^Nơi nhận")


@dataclass
class Unit:
    unit_id: str
    doc_id: str
    level: str
    chuong: str | None = None
    muc: str | None = None
    dieu: str | None = None
    khoan: str | None = None
    diem: str | None = None
    title: str = ""
    text: str = ""
    line_start: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


def unit_address(doc_id: str, dieu: str | None, khoan: str | None, diem: str | None) -> str:
    s = f"{doc_id}:d{dieu}"
    if khoan:
        s += f":k{khoan}"
    if diem:
        s += f":{diem}"
    return s


def _append(unit: "Unit | None", line: str) -> None:
    if unit is not None:
        unit.text = f"{unit.text}\n{line}" if unit.text else line


def parse_units(doc_id: str, lines: list[str], dieu: str | None = None, khoan: str | None = None) -> list[Unit]:
    fragment = dieu is not None
    units: list[Unit] = []
    seen: dict[str, int] = {}
    chuong = muc = None
    pending = None  # "chuong" | "muc": dòng kế tiếp là tên Chương/Mục
    in_annex = False
    annex_n = 0
    depth = 0
    seen_dieu = fragment
    cur: Unit | None = None

    def add(unit: Unit) -> Unit:
        n = seen.get(unit.unit_id, 0) + 1
        seen[unit.unit_id] = n
        if n > 1:
            unit.unit_id = f"{unit.unit_id}#{n}"
        units.append(unit)
        return unit

    if not fragment:
        cur = add(Unit(f"{doc_id}:mo_dau", doc_id, "mo_dau"))

    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        quoted = depth > 0 or line.startswith(("“", "\""))
        depth = max(0, depth + line.count("“") - line.count("”"))
        if quoted:
            _append(cur, line)
            continue
        if not fragment and KET_THUC.match(line):
            cur = add(Unit(f"{doc_id}:ket_thuc", doc_id, "ket_thuc", text=line, line_start=i))
            continue
        if seen_dieu and not fragment and PHULUC.match(line) and len(line) < 150:
            in_annex = True
            annex_n += 1
            cur = add(Unit(f"{doc_id}:pl{annex_n}", doc_id, "phu_luc", title=line, line_start=i))
            continue
        if in_annex or (cur is not None and cur.level == "ket_thuc"):
            _append(cur, line)
            continue
        if pending:
            if pending == "chuong":
                chuong = f"{chuong} {line}"
            else:
                muc = f"{muc} {line}"
            pending = None
            continue
        if m := CHUONG.match(line):
            chuong, muc = m.group(1), None
            pending = None if m.group(2) else "chuong"
            if m.group(2):
                chuong = f"{chuong} {m.group(2)}"
            continue
        if m := MUC.match(line):
            muc = m.group(1)
            pending = None if m.group(2) else "muc"
            if m.group(2):
                muc = f"{muc} {m.group(2)}"
            continue
        if m := DIEU.match(line):
            dieu, khoan, seen_dieu = m.group(1), None, True
            cur = add(Unit(unit_address(doc_id, dieu, None, None), doc_id, "dieu", chuong, muc, dieu,
                           title=m.group(2), line_start=i))
            continue
        if dieu is not None and (m := KHOAN.match(line)):
            khoan = m.group(1)
            cur = add(Unit(unit_address(doc_id, dieu, khoan, None), doc_id, "khoan", chuong, muc, dieu, khoan,
                           text=m.group(2), line_start=i))
            continue
        if dieu is not None and (m := DIEM.match(line)):
            cur = add(Unit(unit_address(doc_id, dieu, khoan, m.group(1)), doc_id, "diem", chuong, muc, dieu,
                           khoan, m.group(1), text=m.group(2), line_start=i))
            continue
        _append(cur, line)
    return units
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_structure.py -q`
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/structure.py tests/test_structure.py
git commit -m "Parse chapters, articles, clauses and points with quote awareness"
```

---

### Task 7: Tìm ngày hiệu lực

**Files:**
- Create: `src/lawproc/effective.py`
- Test: `tests/test_effective.py`

**Interfaces:**
- Consumes: `structure.Unit`
- Produces:
  - `find_effective(units: list[Unit]) -> dict` — khóa `dates: list[str]` (ISO), `ngay_ky: bool`, `trich_dan: str`; ưu tiên Điều có tiêu đề chứa "hiệu lực", sau đó toàn văn bản
  - `decide_effective(doc_id: str, ngay_ban_hanh: str, hl_congbao: str, found: dict) -> dict` — khóa `hl_chot, nguon, can_duyet`; `nguon ∈ {"khop","lech","van_ban","congbao","ngay_ky","khong_thay"}`; văn bản hợp nhất (`doc_id` bắt đầu `vbhn_`) luôn `can_duyet=True`

- [ ] **Step 1: Viết test thất bại `tests/test_effective.py`**

```python
from lawproc.effective import decide_effective, find_effective
from lawproc.structure import parse_units

UNITS = parse_units("nd", [
    "Điều 1. Phạm vi",
    "Nội dung có hiệu lực từ ngày 01 tháng 3 năm 2020 của văn bản khác.",
    "Điều 9. Hiệu lực thi hành",
    "1. Nghị định này có hiệu lực thi hành kể từ ngày 15 tháng 8 năm 2026.",
    "2. Khoản 3 Điều 5 có hiệu lực từ ngày 01 tháng 01 năm 2027.",
])


def test_find_effective_prefers_effect_article():
    r = find_effective(UNITS)
    assert r["dates"] == ["2026-08-15", "2027-01-01"]
    assert r["ngay_ky"] is False
    assert "15 tháng 8 năm 2026" in r["trich_dan"]


def test_find_effective_signing_date():
    r = find_effective(parse_units("x", ["Điều 2. Hiệu lực thi hành", "1. Nghị định này có hiệu lực thi hành kể từ ngày ký ban hành."]))
    assert r["dates"] == []
    assert r["ngay_ky"] is True


def test_decide_rules():
    f = {"dates": ["2026-08-15"], "ngay_ky": False, "trich_dan": ""}
    assert decide_effective("nd", "2026-06-26", "2026-08-15", f) == {"hl_chot": "2026-08-15", "nguon": "khop", "can_duyet": False}
    assert decide_effective("nd", "2026-06-26", "2026-07-01", f)["can_duyet"] is True
    assert decide_effective("nd", "2026-06-26", "", f)["nguon"] == "van_ban"
    sign = {"dates": [], "ngay_ky": True, "trich_dan": ""}
    assert decide_effective("nd", "2025-03-01", "", sign) == {"hl_chot": "2025-03-01", "nguon": "ngay_ky", "can_duyet": True}
    none = {"dates": [], "ngay_ky": False, "trich_dan": ""}
    assert decide_effective("nd", "2025-03-01", "", none)["nguon"] == "khong_thay"
    assert decide_effective("vbhn_63_2025_xlvphc", "2025-08-15", "", f)["can_duyet"] is True
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_effective.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.effective'`

- [ ] **Step 3: Viết `src/lawproc/effective.py`**

```python
import re

from lawproc.structure import Unit

HL_DATE = re.compile(
    r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
    re.IGNORECASE,
)
HL_SIGN = re.compile(r"có hiệu lực(?:\s+thi hành)?(?:\s+kể)?\s+từ\s+ngày\s+ký", re.IGNORECASE)


def _scan(text: str) -> dict:
    dates = [f"{y}-{int(m):02d}-{int(d):02d}" for d, m, y in HL_DATE.findall(text)]
    sign = bool(HL_SIGN.search(text))
    hit = HL_DATE.search(text) or HL_SIGN.search(text)
    snippet = text[max(0, hit.start() - 80): hit.end() + 20].replace("\n", " ") if hit else ""
    return {"dates": dates, "ngay_ky": sign, "trich_dan": snippet.strip()}


def find_effective(units: list[Unit]) -> dict:
    effect_dieu = [u.dieu for u in units if u.level == "dieu" and "hiệu lực" in u.title.lower()]
    if effect_dieu:
        text = "\n".join(u.text for u in units if u.dieu in effect_dieu and u.level in ("dieu", "khoan", "diem"))
        r = _scan(text)
        if r["dates"] or r["ngay_ky"]:
            return r
    return _scan("\n".join(u.text for u in units if u.level != "phu_luc"))


def decide_effective(doc_id: str, ngay_ban_hanh: str, hl_congbao: str, found: dict) -> dict:
    first = found["dates"][0] if found["dates"] else ""
    vbhn = doc_id.startswith("vbhn_")
    if first and hl_congbao:
        same = first == hl_congbao
        return {"hl_chot": first, "nguon": "khop" if same else "lech", "can_duyet": vbhn or not same}
    if first:
        return {"hl_chot": first, "nguon": "van_ban", "can_duyet": vbhn}
    if hl_congbao:
        return {"hl_chot": hl_congbao, "nguon": "congbao", "can_duyet": vbhn}
    if found["ngay_ky"]:
        return {"hl_chot": ngay_ban_hanh, "nguon": "ngay_ky", "can_duyet": True}
    return {"hl_chot": "", "nguon": "khong_thay", "can_duyet": True}
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_effective.py -q`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/effective.py tests/test_effective.py
git commit -m "Find effective dates from the effect article"
```

---

### Task 8: Trích chỉ dẫn sửa đổi

**Files:**
- Create: `src/lawproc/amendments.py`
- Test: `tests/test_amendments.py`

**Interfaces:**
- Consumes: `structure.Unit`, `config.TARGET_ALIASES`, `clean.normalize`
- Produces: `extract_instructions(doc_id: str, units: list[Unit], doc_title: str) -> list[dict]` — mỗi dòng có khóa `amend_doc_id, amend_unit_id, action, target_doc_id, target_dieu, target_khoan, target_diem, new_label, instruction, new_text, status, ghi_chu`; `action ∈ {"sua_doi","bo_sung","bai_bo","thay_the_cum_tu"}`; `status = "chua_duyet"`

Thứ tự xác định văn bản bị sửa: tham chiếu trong chính câu chỉ dẫn → tiêu đề Điều chứa câu chỉ dẫn → `doc_title` của văn bản sửa đổi.

- [ ] **Step 1: Viết test thất bại `tests/test_amendments.py`**

```python
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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_amendments.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.amendments'`

- [ ] **Step 3: Viết `src/lawproc/amendments.py`**

```python
import re

from lawproc import config
from lawproc.clean import normalize
from lawproc.structure import Unit

ACTION = re.compile(r"^(Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Thay thế|Thay cụm từ)\b", re.IGNORECASE)
ADDR = re.compile(
    r"(?:điểm\s+([a-zđ]{1,2})\s+)?(?:khoản\s+(\d+[a-zđ]?)\s+)?Điều\s+(\d+[a-zđ]?)(?!\s*\.\s*\S)",
    re.IGNORECASE,
)
NEW_LABEL = re.compile(r"Bổ sung\s+((?:điểm|khoản|Điều)\s+[\wđ]+)\s+vào", re.IGNORECASE)
ACTION_MAP = {"sửa đổi, bổ sung": "sua_doi", "sửa đổi": "sua_doi", "bổ sung": "bo_sung",
              "bãi bỏ": "bai_bo", "thay thế": "thay_the_cum_tu", "thay cụm từ": "thay_the_cum_tu"}


def _target_from(text: str) -> str:
    t = normalize(text).lower()
    for alias, doc_id in config.TARGET_ALIASES.items():
        if normalize(alias).lower() in t:
            return doc_id
    return ""


def _new_text(full: str, first_line: str) -> str:
    rest = full[len(first_line):].strip() if full.startswith(first_line) else ""
    if not rest and "“" in first_line and ACTION.match(first_line).group(1).lower() != "thay thế":
        rest = first_line[first_line.index("“"):]
    rest = rest.strip()
    if rest.startswith("“"):
        rest = rest[1:]
    rest = re.sub(r"”\s*[.;]?\s*$", "", rest)
    return rest.strip()


def extract_instructions(doc_id: str, units: list[Unit], doc_title: str) -> list[dict]:
    titles = {u.dieu: u.title for u in units if u.level == "dieu"}
    rows: list[dict] = []
    for u in units:
        if u.level not in ("dieu", "khoan", "diem"):
            continue
        body = u.title if u.level == "dieu" and not u.text else u.text
        first = body.split("\n")[0]
        if u.level == "dieu" and u.text:
            first, body = u.title, f"{u.title}\n{u.text}"
        m = ACTION.match(first)
        if not m:
            continue
        action = ACTION_MAP[m.group(1).lower()]
        head = first.split("“")[0] if action != "thay_the_cum_tu" else re.sub(r"“[^”]*”", "", first)
        addrs = list(ADDR.finditer(head))
        if not addrs:
            continue  # tiêu đề kiểu "Sửa đổi, bổ sung một số điều của ..." chỉ là ngữ cảnh
        target = _target_from(head) or _target_from(titles.get(u.dieu, "")) or _target_from(doc_title)
        label = NEW_LABEL.search(head)
        a = addrs[-1] if action == "bo_sung" else addrs[0]
        rows.append({
            "amend_doc_id": doc_id, "amend_unit_id": u.unit_id, "action": action, "target_doc_id": target,
            "target_dieu": a.group(3), "target_khoan": a.group(2) or "", "target_diem": a.group(1) or "",
            "new_label": label.group(1) if label else "", "instruction": first,
            "new_text": "" if action in ("bai_bo", "thay_the_cum_tu") else _new_text(body, first),
            "status": "chua_duyet", "ghi_chu": "nhiều địa chỉ" if len(addrs) > 1 and action != "bo_sung" else "",
        })
    return rows
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_amendments.py -q`
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/amendments.py tests/test_amendments.py
git commit -m "Extract amendment instructions as review candidates"
```

---

### Task 9: Áp sửa đổi thành các phiên bản có hiệu lực

**Files:**
- Create: `src/lawproc/apply.py`
- Test: `tests/test_apply.py`

**Interfaces:**
- Consumes: `structure.parse_units`, `structure.Unit`, `structure.unit_address`
- Produces: `apply_amendments(units: list[dict], hl: dict[str, str], amendments: list[dict]) -> list[dict]` — trả các bản ghi đơn vị (bỏ `mo_dau`, `ket_thuc`) có thêm khóa `valid_from, valid_to, source_doc_id, version_id`; chỉ áp dòng `status == "duyet"`; `action == "thay_the_van_ban"` đóng hiệu lực mọi đơn vị còn hiệu lực của `target_doc_id`; `thay_the_cum_tu` không áp tự động (người duyệt chuyển thành `sua_doi` kèm `new_text` đầy đủ)

- [ ] **Step 1: Viết test thất bại `tests/test_apply.py`**

```python
from lawproc.apply import apply_amendments
from lawproc.structure import parse_units

BASE = [u.as_dict() for u in parse_units("nd_168_2024", [
    "Điều 7. Xử phạt xe mô tô",
    "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng:",
    "a) Không đội mũ bảo hiểm;",
    "3. Phạt tiền khác.",
    "d) Hành vi d;",
])]
HL = {"nd_168_2024": "2025-01-01", "nd_238_2026": "2026-08-15", "tt_108": "2026-07-01", "tt_12": "2025-03-01"}


def _a(**kw):
    row = {"amend_doc_id": "nd_238_2026", "target_doc_id": "nd_168_2024", "target_dieu": "7", "target_khoan": "",
           "target_diem": "", "new_text": "", "status": "duyet"}
    row.update(kw)
    return row


def _live(recs, uid):
    return [r for r in recs if r["unit_id"] == uid and r["valid_to"] is None]


def test_sua_doi_closes_old_clause_and_children_and_adds_new_version():
    recs = apply_amendments(BASE, HL, [_a(action="sua_doi", target_khoan="2",
                                          new_text="2. Phạt tiền từ 600.000 đồng đến 800.000 đồng:\na) Không đội mũ;")])
    old = [r for r in recs if r["unit_id"] == "nd_168_2024:d7:k2" and r["valid_to"] == "2026-08-15"]
    assert old and old[0]["valid_from"] == "2025-01-01"
    new = _live(recs, "nd_168_2024:d7:k2")[0]
    assert new["text"].startswith("Phạt tiền từ 600.000")
    assert (new["valid_from"], new["source_doc_id"], new["version_id"]) == (
        "2026-08-15", "nd_238_2026", "nd_168_2024:d7:k2@2026-08-15")
    assert _live(recs, "nd_168_2024:d7:k2:a")[0]["text"] == "Không đội mũ;"
    assert _live(recs, "nd_168_2024:d7:k3")[0]["valid_from"] == "2025-01-01"


def test_bai_bo_only_closes():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", target_diem="d")])
    assert _live(recs, "nd_168_2024:d7:k3:d") == []


def test_unreviewed_rows_are_ignored():
    recs = apply_amendments(BASE, HL, [_a(action="bai_bo", target_khoan="3", status="chua_duyet")])
    assert _live(recs, "nd_168_2024:d7:k3")


def test_replace_whole_document():
    base = [u.as_dict() for u in parse_units("tt_12", ["Điều 1. A"])]
    recs = apply_amendments(base, HL, [_a(amend_doc_id="tt_108", target_doc_id="tt_12", action="thay_the_van_ban",
                                          target_dieu="")])
    assert _live(recs, "tt_12:d1") == []
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest tests/test_apply.py -q`
Expected: FAIL với `ModuleNotFoundError: No module named 'lawproc.apply'`

- [ ] **Step 3: Viết `src/lawproc/apply.py`**

```python
from lawproc.structure import Unit, parse_units, unit_address

SKIP_LEVELS = {"mo_dau", "ket_thuc"}


def _version(rec: dict) -> dict:
    rec["version_id"] = f"{rec['unit_id']}@{rec['valid_from']}"
    return rec


def apply_amendments(units: list[dict], hl: dict[str, str], amendments: list[dict]) -> list[dict]:
    out = [
        _version(dict(u, valid_from=hl.get(u["doc_id"], ""), valid_to=None, source_doc_id=u["doc_id"]))
        for u in units if u["level"] not in SKIP_LEVELS
    ]
    rows = sorted((a for a in amendments if a["status"] == "duyet"), key=lambda a: hl.get(a["amend_doc_id"], ""))
    for a in rows:
        when = hl[a["amend_doc_id"]]
        target, action = a["target_doc_id"], a["action"]
        if action == "thay_the_van_ban":
            for r in out:
                if r["doc_id"] == target and r["valid_to"] is None:
                    r["valid_to"] = when
            continue
        addr = unit_address(target, a["target_dieu"], a["target_khoan"] or None, a["target_diem"] or None)
        if action in ("sua_doi", "bai_bo"):
            for r in out:
                if r["doc_id"] == target and r["valid_to"] is None and (
                        r["unit_id"] == addr or r["unit_id"].startswith(addr + ":")):
                    r["valid_to"] = when
        if action in ("sua_doi", "bo_sung") and a["new_text"].strip():
            frag = [x for x in a["new_text"].splitlines() if x.strip()]
            new = parse_units(target, frag, dieu=a["target_dieu"], khoan=a["target_khoan"] or None)
            if not new:
                level = "diem" if a["target_diem"] else "khoan" if a["target_khoan"] else "dieu"
                new = [Unit(addr, target, level, dieu=a["target_dieu"], khoan=a["target_khoan"] or None,
                            diem=a["target_diem"] or None, text="\n".join(frag))]
            for u in new:
                out.append(_version(dict(u.as_dict(), valid_from=when, valid_to=None,
                                         source_doc_id=a["amend_doc_id"])))
    return out
```

- [ ] **Step 4: Chạy test, xác nhận qua**

Run: `python -m pytest tests/test_apply.py -q`
Expected: `4 passed`

- [ ] **Step 5: Chạy toàn bộ test**

Run: `python -m pytest -q`
Expected: tất cả qua (khoảng 30 test)

- [ ] **Step 6: Commit**

```bash
git add src/lawproc/apply.py tests/test_apply.py
git commit -m "Apply reviewed amendments into dated unit versions"
```

---

### Task 10: Chạy toàn bộ trên dữ liệu thật

**Files:**
- Create: `scripts/process_legal.py`
- Modify: `.gitignore` (không cần sửa: `data/interim/` đã bị bỏ qua)

**Interfaces:**
- Consumes: mọi module ở Task 1–9
- Produces: CLI `python scripts/process_legal.py <step>` với `step ∈ {convert, assemble, parse, effective, amendments, apply, all}`; `all` chạy `convert → assemble → parse → effective → amendments` (dừng trước `apply`, vì `apply` cần file đã duyệt)

- [ ] **Step 1: Viết `scripts/process_legal.py`**

```python
"""Xử lý văn bản luật: python scripts/process_legal.py {convert|assemble|parse|effective|amendments|apply|all}"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from lawproc.amendments import extract_instructions  # noqa: E402
from lawproc.apply import apply_amendments  # noqa: E402
from lawproc.assemble import article_report, assemble_doc, group_rows, pick_sources  # noqa: E402
from lawproc.convert import convert_doc_files  # noqa: E402
from lawproc.effective import decide_effective, find_effective  # noqa: E402
from lawproc.extract import docx_lines, ocr_pdf_lines, pdf_lines  # noqa: E402
from lawproc.structure import Unit, parse_units  # noqa: E402
from lawproc.verify import check_identity  # noqa: E402

DOCX_DIR = config.INTERIM / "docx"
OCR_DIR = config.INTERIM / "ocr"
DOCS_DIR = config.PROCESSED / "documents"
UNITS = config.PROCESSED / "legal_units.jsonl"
EFFECTIVE = config.PROCESSED / "effective_dates.csv"
CANDIDATES = config.PROCESSED / "amendments_candidates.csv"
REVIEWED = config.PROCESSED / "amendments_reviewed.csv"
VERSIONED = config.PROCESSED / "legal_units_versioned.jsonl"


def manifest() -> list[dict]:
    return list(csv.DictReader(config.MANIFEST.open(encoding="utf-8-sig")))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"-> {path.relative_to(config.ROOT)} ({len(rows)} dòng)")


def load_part(row: dict, method: str) -> list[str]:
    path = config.ROOT / row["file"]
    if method == "docx":
        return docx_lines(DOCX_DIR / f"{path.stem}.docx")
    if method == "ocr":
        return ocr_pdf_lines(path, OCR_DIR / path.stem)
    return pdf_lines(path)


def step_convert() -> None:
    files = convert_doc_files(config.RAW / "legal", DOCX_DIR)
    print(f"docx: {len(files)} file trong {DOCX_DIR.relative_to(config.ROOT)}")


def step_assemble() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    reports, idents = [], []
    for doc_id, rows in group_rows(manifest()).items():
        chosen, method = pick_sources(rows)
        print(f"{doc_id:28} {method:5} {len(chosen)} phần")
        lines = assemble_doc(doc_id, [load_part(r, method) for r in chosen], method)
        (DOCS_DIR / f"{doc_id}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        reports.append(article_report(doc_id, lines, method, len(chosen)))
        idents.append(check_identity(doc_id, rows[0]["so_ky_hieu"], rows[0]["tieu_de"], "\n".join(lines)))
    write_csv(config.PROCESSED / "assembly_report.csv", reports)
    write_csv(config.PROCESSED / "identity_report.csv", idents)


def step_parse() -> None:
    n = 0
    with UNITS.open("w", encoding="utf-8") as fp:
        for path in sorted(DOCS_DIR.glob("*.txt")):
            for u in parse_units(path.stem, path.read_text(encoding="utf-8").splitlines()):
                fp.write(json.dumps(u.as_dict(), ensure_ascii=False) + "\n")
                n += 1
    print(f"-> {UNITS.relative_to(config.ROOT)} ({n} đơn vị)")


def load_units() -> dict[str, list[Unit]]:
    by_doc: dict[str, list[Unit]] = {}
    for line in UNITS.open(encoding="utf-8"):
        d = json.loads(line)
        by_doc.setdefault(d["doc_id"], []).append(Unit(**d))
    return by_doc


def step_effective() -> None:
    meta = {r["doc_id"]: r for r in manifest()}
    rows = []
    for doc_id, units in load_units().items():
        m = meta[doc_id]
        found = find_effective(units)
        dec = decide_effective(doc_id, m["ngay_ban_hanh"], m["ngay_hieu_luc_congbao"], found)
        rows.append({"doc_id": doc_id, "so_ky_hieu": m["so_ky_hieu"], "ngay_ban_hanh": m["ngay_ban_hanh"],
                     "hl_congbao": m["ngay_hieu_luc_congbao"], "hl_van_ban": " ".join(found["dates"]),
                     "trich_dan": found["trich_dan"], **dec, "ghi_chu": ""})
    write_csv(EFFECTIVE, rows)


def step_amendments() -> None:
    units = load_units()
    rows = []
    for doc_id in sorted(config.AMENDING_DOCS & units.keys()):
        title = next((u.text for u in units[doc_id] if u.level == "mo_dau"), "")[:600]
        rows += extract_instructions(doc_id, units[doc_id], title)
    write_csv(CANDIDATES, rows)


def step_apply() -> None:
    hl = {r["doc_id"]: r["hl_chot"] for r in csv.DictReader(EFFECTIVE.open(encoding="utf-8-sig"))}
    missing = [d for d, v in hl.items() if not v]
    if missing:
        sys.exit(f"Thiếu hl_chot trong effective_dates.csv: {missing}")
    amendments = list(csv.DictReader(REVIEWED.open(encoding="utf-8-sig")))
    units = [json.loads(x) for x in UNITS.open(encoding="utf-8")]
    recs = apply_amendments(units, hl, amendments)
    with VERSIONED.open("w", encoding="utf-8") as fp:
        for r in recs:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")
    live = sum(r["valid_to"] is None for r in recs)
    print(f"-> {VERSIONED.relative_to(config.ROOT)} ({len(recs)} bản ghi, {live} còn hiệu lực)")


STEPS = {"convert": step_convert, "assemble": step_assemble, "parse": step_parse,
         "effective": step_effective, "amendments": step_amendments, "apply": step_apply}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name in (["convert", "assemble", "parse", "effective", "amendments"] if arg == "all" else [arg]):
        print(f"\n== {name}")
        STEPS[name]()
```

- [ ] **Step 2: Chạy các bước đến trước `apply`**

Run: `python scripts/process_legal.py all`
Expected: in tên 32 văn bản với phương pháp (`docx`/`pdf`/`ocr`); tạo `data/processed/documents/*.txt` (32 file), `assembly_report.csv`, `identity_report.csv`, `legal_units.jsonl`, `effective_dates.csv`, `amendments_candidates.csv`. Bước OCR TT 108/2026 (134 trang) mất vài phút; chạy lại sẽ dùng cache.

- [ ] **Step 3: Đọc báo cáo và xử lý bất thường**

Run:
```bash
python -c "import csv;[print(r) for r in csv.DictReader(open('data/processed/identity_report.csv',encoding='utf-8-sig')) if r['status']!='ok']"
python -c "import csv;[print(r['doc_id'],r['method'],r['n_dieu'],r['first_dieu'],r['last_dieu'],r['missing_dieu']) for r in csv.DictReader(open('data/processed/assembly_report.csv',encoding='utf-8-sig'))]"
```
Expected: `tt_36_2024_byt` bị gắn `kiem_tra_tay` (số hiệu viết tay, đã biết). Văn bản nào khác bị `kiem_tra_tay`, hoặc có `missing_dieu` không rỗng, hoặc `first_dieu != 1`: mở `data/processed/documents/<doc_id>.txt`, tìm nguyên nhân (thứ tự phần sai, dòng rác chưa lọc, OCR đọc sai "Điều"), sửa quy tắc trong `clean.py`/`assemble.py` kèm một test tái hiện lỗi, chạy lại `python -m pytest -q` và `python scripts/process_legal.py all`. Ghi những trường hợp chấp nhận được (ví dụ văn bản hợp nhất có Điều bị bãi bỏ) vào `PROCESSING_REPORT.md` ở Task 11.

- [ ] **Step 4: Commit mã và đầu ra tự động**

```bash
git add scripts/process_legal.py data/processed/documents data/processed/assembly_report.csv data/processed/identity_report.csv data/processed/legal_units.jsonl data/processed/effective_dates.csv data/processed/amendments_candidates.csv
git commit -m "Run legal text processing on collected sources"
```

---

### Task 11: Duyệt ngày hiệu lực, chỉ dẫn sửa đổi, OCR và áp sửa đổi

Task này cần người duyệt. Agent làm bản duyệt đầu, người dùng xác nhận trước khi chạy `apply`.

**Files:**
- Modify: `data/processed/effective_dates.csv` (cột `hl_chot`, `ghi_chu`)
- Create: `data/processed/amendments_reviewed.csv`, `data/processed/PROCESSING_REPORT.md`, `data/processed/legal_units_versioned.jsonl`

**Interfaces:**
- Consumes: đầu ra Task 10; `scripts/process_legal.py apply`
- Produces: `legal_units_versioned.jsonl` dùng cho giai đoạn xây kho tra cứu

- [ ] **Step 1: Duyệt ngày hiệu lực**

Với mọi dòng `can_duyet = True` trong `effective_dates.csv`: mở văn bản trong `data/processed/documents/`, đọc Điều "Hiệu lực thi hành", điền `hl_chot` (ISO `YYYY-MM-DD`) và lý do vào `ghi_chu`. Quy tắc: văn bản có nhiều mốc lấy mốc chung của văn bản, ghi các mốc riêng vào `ghi_chu`; văn bản hợp nhất lấy ngày hiệu lực của văn bản sửa đổi gần nhất được hợp nhất (ghi trong phần đầu văn bản hợp nhất). Không để trống `hl_chot`.

- [ ] **Step 2: Duyệt chỉ dẫn sửa đổi**

Sao `amendments_candidates.csv` thành `amendments_reviewed.csv`. Với từng dòng: mở văn bản sửa đổi tại `amend_unit_id`, kiểm tra `target_doc_id`, `target_dieu/khoan/diem`, `new_text`; sửa sai rồi đặt `status = duyet` (hoặc `loai` nếu không phải chỉ dẫn sửa đổi). Dòng `ghi_chu = nhiều địa chỉ`: tách thành nhiều dòng, mỗi dòng một địa chỉ. Dòng `thay_the_cum_tu`: chuyển thành `sua_doi` cho từng đơn vị bị ảnh hưởng, `new_text` là nội dung sau khi thay. Thêm thủ công các quan hệ mà regex không bắt được:
- Luật 118/2025/QH15 sửa Luật 35/2024 và Luật 36/2024: kiểm tra `target_doc_id` của mọi dòng `amend_doc_id = luat_118_2025`.
- TT 108/2026/TT-BCA thay TT 12/2025/TT-BCA: thêm dòng `action = thay_the_van_ban`, `amend_doc_id = tt_108_2026_bca`, `target_doc_id = tt_12_2025_bca`, `target_dieu` để trống, `status = duyet`, `ghi_chu` ghi các phụ lục của TT 12 còn hiệu lực đến 28/02/2027.
- TT 51/2025/TT-BCA: xác nhận văn bản này có sửa TT 79/2024/TT-BCA hay không; nếu không, đặt `loai`.

Người dùng xem lại hai file đã duyệt trước khi sang bước 4.

- [ ] **Step 3: Kiểm tra mẫu OCR**

Với mỗi văn bản OCR (`tt_108_2026_bca`, `tt_155_2025_btc`, `tt_36_2024_byt`): chọn ngẫu nhiên 10 đơn vị trong `legal_units.jsonl`, so với ảnh PDF gốc, đếm số từ sai. Ghi tỷ lệ lỗi và các lỗi điển hình vào `PROCESSING_REPORT.md`. Nếu mức phạt hoặc số liệu bị đọc sai ở đơn vị nào, sửa trực tiếp trong `data/processed/documents/<doc_id>.txt`, ghi lại từng chỗ sửa trong báo cáo, rồi chạy lại `python scripts/process_legal.py parse`.

- [ ] **Step 4: Áp sửa đổi**

Run: `python scripts/process_legal.py apply`
Expected: tạo `legal_units_versioned.jsonl`; dòng in ra cho biết tổng số bản ghi và số bản ghi còn hiệu lực. Kiểm tra nhanh một chỗ đã biết bị NĐ 238/2026 sửa:
```bash
python -c "import json;[print(r['version_id'],r['valid_from'],r['valid_to'],r['text'][:80]) for r in map(json.loads,open('data/processed/legal_units_versioned.jsonl',encoding='utf-8')) if r['doc_id']=='nd_168_2024' and r['source_doc_id']=='nd_238_2026'][:10]"
```
Expected: có bản ghi `source_doc_id = nd_238_2026` với `valid_from = 2026-08-15`, và bản ghi gốc tương ứng có `valid_to = 2026-08-15`.

- [ ] **Step 5: Viết `data/processed/PROCESSING_REPORT.md`**

Gồm: số văn bản theo phương pháp trích (docx/pdf/ocr); số đơn vị theo cấp (dieu/khoan/diem/phu_luc); văn bản có bất thường ở `assembly_report` và cách xử lý; kết quả kiểm tra danh tính; số chỉ dẫn sửa đổi theo hành động và theo văn bản; số đơn vị bị đóng hiệu lực và số phiên bản mới; tỷ lệ lỗi OCR; các quyết định thủ công ở bước 1–3. Số liệu lấy bằng lệnh, không ước lượng.

- [ ] **Step 6: Commit**

```bash
git add data/processed/effective_dates.csv data/processed/amendments_reviewed.csv data/processed/legal_units_versioned.jsonl data/processed/PROCESSING_REPORT.md data/processed/documents
git commit -m "Review effective dates and amendments, build versioned units"
```
