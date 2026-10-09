# Làm sạch bổ sung (đợt 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sửa các lỗi làm sạch còn lại (L1–L8 trong spec) để giai đoạn dữ liệu văn bản luật có thể coi là xong.

**Architecture:** Mọi sửa nằm trong `src/lawproc` (trích chữ, tách cấu trúc, OCR) và hai module mới: `quality.py` (chỉ số chữ), `annotate.py` (gắn nhãn bản ghi), `validity.py` (ngoại lệ hiệu lực và hàm lọc theo thời điểm). `scripts/process_legal.py` chạy lại toàn bộ; đầu ra trong `data/processed/` được tạo lại và commit. Bộ test toàn vẹn `tests/test_processed_invariants.py` được mở rộng cho từng lỗi.

**Tech Stack:** Python 3.13, python-docx, PyMuPDF, Tesseract 5.4 (`tools/tessdata/vie.traineddata`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-09-cleanup-and-eda-design.md` (mục 2, 3, 5, 6).

## Global Constraints

- Mọi lệnh chạy từ thư mục gốc repo `D:\Dowload\1.Chuyên Ngành\kì 7\DAT301_NEW\traffic-law-qa`. Test: `python -m pytest -q`.
- Không sửa `data/raw/`. Không vá tay `data/processed/documents/*.txt`, `legal_units*.jsonl`; mọi thay đổi đầu ra phải đến từ code hoặc từ các file dữ liệu duyệt (`data/ocr_corrections.csv`, `data/processed/effective_dates.csv`, `data/processed/amendments_reviewed.csv`, `data/effective_exceptions.csv`, `data/annex_type_overrides.csv`).
- Commit không ghi Claude là tác giả hay đồng tác giả: không thêm dòng `Co-Authored-By` nào vào nội dung commit.
- Chạy lại đầu ra sau khi sửa code: `python scripts/process_legal.py assemble`, rồi lần lượt `parse`, `effective`, `amendments`, `apply`. Không chạy `convert` (cần Word; file docx đã có trong `data/interim/docx`). Không dùng `all` (không gồm `apply`).
- Sau mỗi task: toàn bộ test qua; chạy lại hai lần liên tiếp cho ra đầu ra giống hệt (`git status --short data/processed` không đổi giữa hai lần).
- Một bản ghi có hiệu lực tại t khi `valid_from <= t < valid_to` (valid_to rỗng là vô hạn), trừ khi ngoại lệ trong `hl_ngoai_le` nói khác (Task 7). Ngày kết thúc luôn là ngày đầu tiên hết hiệu lực (loại trừ): "đến hết ngày 28/02/2027" ghi là `2027-03-01`.
- Ngày chốt `config.CUTOFF = "2026-10-01"`.
- Comment và thông báo trong code viết tiếng Việt, theo phong cách code hiện có.

## File Structure

| File | Việc |
|---|---|
| `src/lawproc/extract.py` | Sửa duyệt bảng docx (Task 1); cache OCR theo sha256 và dpi, OCR lại trang chọn lọc (Task 5) |
| `src/lawproc/structure.py` | Nhãn điểm có số (Task 2); phần kết (Task 3); heading Phần, trường `phan`, khoản dạng `3.1.` (Task 4) |
| `src/lawproc/clean.py` | `STRUCT_START` nhận nhãn điểm có số (Task 2) |
| `src/lawproc/assemble.py` | Bỏ dòng mục lục, tách văn bản suy ra (Task 4) |
| `src/lawproc/apply.py` | Chép `phan` cho đơn vị sinh từ sửa đổi (Task 4) |
| `src/lawproc/config.py` | `DERIVED_DOCS`, `DOTTED_KHOAN_DOCS` (Task 4); `REOCR_PAGES`, `REOCR_DPI` (Task 5); `QUALITY_BAD`, `QUALITY_MIN_WORDS` (Task 6) |
| `src/lawproc/quality.py` (mới) | `syllable_error_rate` (Task 5) |
| `src/lawproc/annotate.py` (mới) | `mark_content_change`, `annex_type`, `annotate_records` (Task 6) |
| `src/lawproc/validity.py` (mới) | `load_exceptions`, `attach_exceptions`, `in_force_at` (Task 7) |
| `scripts/process_legal.py` | Gọi các bước mới; meta cho văn bản suy ra |
| `data/effective_exceptions.csv` (mới) | Ngoại lệ hiệu lực đã duyệt (Task 7) |
| `data/processed/annex_types.csv` (mới, sinh ra) | Danh sách phân loại phụ lục để người dùng xem (Task 6) |
| `tests/…` | Test cho từng task; `tests/test_processed_invariants.py` mở rộng |

---

### Task 1: Đọc bảng Word đúng một lần (L3)

**Files:**
- Modify: `src/lawproc/extract.py` (hàm `docx_lines`)
- Test: `tests/test_extract.py`
- Regenerate: `data/processed/*`

**Interfaces:**
- Produces: `docx_lines(path: Path) -> list[str]` giữ nguyên chữ ký; bảng lồng nằm trong dòng của ô chứa nó, mỗi ô (`w:tc`) lấy một lần.

Hiện `docx_lines` dùng `child.iter(qn("w:tr"))` và `tr.iter(qn("w:tc"))`, nên hàng và ô của bảng lồng bị duyệt cả ở bảng ngoài lẫn bảng trong. Kiểm tra thực tế cho thấy 5 văn bản bị lặp chữ (nd_158_2024, nd_160_2024, tt_12_2025_bca, tt_37_2026_bca, tt_79_2024_bca); các văn bản khác chỉ đổi khoảng trắng kép trong ô.

- [ ] **Step 1: Ghi danh sách dòng sửa đổi đã duyệt không khớp văn bản (trước khi sửa)**

Lưu script sau vào scratchpad (không commit) với tên `check_reviewed.py`:

```python
"""Liệt kê dòng duyet trong amendments_reviewed.csv có dòng new_text không xuất hiện trong văn bản sửa đổi."""
import csv
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
docs = {p.stem: re.sub(r"\s+", " ", p.read_text(encoding="utf-8"))
        for p in (root / "data/processed/documents").glob("*.txt")}
rows = csv.DictReader((root / "data/processed/amendments_reviewed.csv").open(encoding="utf-8-sig"))
for i, r in enumerate(rows):
    if r["status"] != "duyet":
        continue
    for line in r["new_text"].splitlines():
        s = re.sub(r"\s+", " ", line).strip().strip("“”\"")
        if s and s not in docs[r["amend_doc_id"]]:
            print(i, r["amend_unit_id"], s[:80])
            break
```

Run: `python -X utf8 <scratchpad>/check_reviewed.py . > <scratchpad>/reviewed_before.txt`

- [ ] **Step 2: Viết test thất bại**

Thêm vào `tests/test_extract.py`:

```python
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
```

- [ ] **Step 3: Chạy để thấy thất bại**

Run: `python -m pytest tests/test_extract.py -q`
Expected: 3 test mới FAIL (bảng lồng sinh thêm dòng; ô có đoạn rỗng sinh khoảng trắng kép).

- [ ] **Step 4: Sửa `extract.py`**

Thêm hai hàm sau `_text_of` và thay nhánh `tbl` trong `docx_lines`:

```python
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
```

Trong `docx_lines`, thay toàn bộ nhánh `elif tag == "tbl": ...` bằng:

```python
        elif tag == "tbl":
            out.extend(_table_rows(child))
```

- [ ] **Step 5: Chạy test**

Run: `python -m pytest tests/test_extract.py -q`
Expected: PASS.

- [ ] **Step 6: Chạy lại đầu ra và so sánh**

Run lần lượt: `python scripts/process_legal.py assemble`, `... parse`, `... effective`, `... amendments`, `... apply`.
Run: `git diff --stat data/processed/documents` — các văn bản đổi nhiều phải là 5 văn bản nêu trên; các văn bản khác chỉ đổi vài ký tự (khoảng trắng).
Run: `python -X utf8 <scratchpad>/check_reviewed.py . > <scratchpad>/reviewed_after.txt` rồi so với `reviewed_before.txt`. Dòng nào chỉ có ở bản after là dòng duyet có `new_text` chứa chữ bị lặp do lỗi cũ: sửa `new_text` của dòng đó trong `amendments_reviewed.csv` bằng đúng đoạn tương ứng trong `amendments_candidates.csv` mới (cùng `amend_unit_id`), thêm vào `ghi_chu` câu "new_text cập nhật sau khi sửa lỗi lặp bảng (L3)". Chạy lại `apply`.

- [ ] **Step 7: Toàn bộ test, kiểm tra tái lập, commit**

Run: `python -m pytest -q` → PASS. Chạy lại 5 bước một lần nữa, `git status --short data/processed` không đổi so với lần trước.

```bash
git add src/lawproc/extract.py tests/test_extract.py data/processed
git commit -m "Read each Word table cell once, including nested tables"
```

---

### Task 2: Nhãn điểm có chữ số, ví dụ `k1)` (L4)

**Files:**
- Modify: `src/lawproc/structure.py` (`DIEM`), `src/lawproc/clean.py` (`STRUCT_START`)
- Modify: `data/processed/amendments_reviewed.csv` (dòng `nd_238_2026:d12:k2`)
- Test: `tests/test_structure.py`, `tests/test_apply.py`

**Interfaces:**
- Produces: `DIEM = re.compile(r"^([a-zđ]{1,2}\d?)\)\s+(.*)$")`; địa chỉ điểm dạng `…:k4:k1`.

Văn bản gốc không có nhãn kiểu này ở đầu dòng; nhãn chỉ xuất hiện trong `new_text` của sửa đổi (NĐ 238 bổ sung điểm k1 khoản 4 Điều 41 NĐ 168). Dòng đó từng bị người duyệt chuyển thành `sua_doi` điểm k với `k1)` là dòng thứ hai, nên khi parser nhận `k1)` thì dòng đó sẽ báo lỗi "creates … outside". Phải đổi dòng về đúng chỉ dẫn gốc: bổ sung điểm k1.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `tests/test_structure.py`:

```python
def test_point_label_with_digit():
    lines = ["Điều 41. Trừ điểm", "4. Các hành vi sau:", "k) Điểm b khoản 3 Điều 20;", "k1) Điểm a khoản 3 Điều 32;"]
    units = {u.unit_id: u for u in parse_units("nd", lines)}
    assert units["nd:d41:k4:k"].text == "Điểm b khoản 3 Điều 20;"
    assert units["nd:d41:k4:k1"].text == "Điểm a khoản 3 Điều 32;"
```

Thêm vào `tests/test_apply.py` (dùng các helper đã có trong file; nếu file có hàm dựng dòng sửa đổi thì dùng hàm đó, không thì dựng dict đủ cột như dưới):

```python
def test_bo_sung_point_with_digit_label():
    units = [
        {"unit_id": "nd:d41", "doc_id": "nd", "level": "dieu", "chuong": None, "muc": None, "dieu": "41",
         "khoan": None, "diem": None, "title": "Trừ điểm", "text": "", "line_start": 0},
        {"unit_id": "nd:d41:k4", "doc_id": "nd", "level": "khoan", "chuong": None, "muc": None, "dieu": "41",
         "khoan": "4", "diem": None, "title": "", "text": "Các hành vi sau:", "line_start": 1},
        {"unit_id": "nd:d41:k4:k", "doc_id": "nd", "level": "diem", "chuong": None, "muc": None, "dieu": "41",
         "khoan": "4", "diem": "k", "title": "", "text": "Điểm b khoản 3 Điều 20;", "line_start": 2},
    ]
    row = {"amend_doc_id": "sd", "amend_unit_id": "sd:d12:k2", "action": "bo_sung", "target_doc_id": "nd",
           "target_dieu": "41", "target_khoan": "4", "target_diem": "", "new_label": "điểm k1",
           "instruction": "Bổ sung điểm k1 vào sau điểm k khoản 4 Điều 41",
           "new_text": "k1) Điểm a khoản 3 Điều 32;", "status": "duyet", "hl_rieng": "", "ghi_chu": ""}
    recs = apply_amendments(units, {"nd": "2025-01-01", "sd": "2026-08-15"}, [row])
    live = {r["unit_id"]: r for r in recs if r["valid_to"] is None}
    assert live["nd:d41:k4:k1"]["text"] == "Điểm a khoản 3 Điều 32;"
    assert live["nd:d41:k4:k"]["valid_from"] == "2025-01-01"  # điểm k không bị sửa
```

- [ ] **Step 2: Chạy để thấy thất bại**

Run: `python -m pytest tests/test_structure.py tests/test_apply.py -q`
Expected: 2 test mới FAIL.

- [ ] **Step 3: Sửa mẫu**

`src/lawproc/structure.py`:

```python
DIEM = re.compile(r"^([a-zđ]{1,2}\d?)\)\s+(.*)$")
```

`src/lawproc/clean.py`, trong `STRUCT_START` đổi `[a-zđ]{1,2}\)\s` thành `[a-zđ]{1,2}\d?\)\s`.

- [ ] **Step 4: Chạy test**

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Sửa dòng đã duyệt**

Trong `data/processed/amendments_reviewed.csv`, dòng `amend_unit_id = nd_238_2026:d12:k2` (instruction "Bổ sung điểm k1 vào sau điểm k khoản 4 Điều 41"): đặt `action = bo_sung`, `target_diem` rỗng, `new_label = điểm k1`, `new_text` chỉ còn dòng bắt đầu bằng `k1)` (bỏ dòng `k) Điểm b khoản 3 Điều 20;`), `ghi_chu = "bổ sung điểm k1 (parser nhận nhãn có chữ số từ L4)"`. Sửa bằng một script Python nhỏ dùng `csv.DictReader`/`DictWriter` với `encoding="utf-8-sig"` để giữ nguyên các dòng khác.

- [ ] **Step 6: Chạy lại đầu ra, kiểm tra**

Chạy 5 bước. Kiểm tra:
`python -X utf8 -c "import json;[print(r['version_id'],r['valid_to']) for r in map(json.loads,open('data/processed/legal_units_versioned.jsonl',encoding='utf-8')) if r['unit_id'].startswith('nd_168_2024:d41:k4:k')]"`
Expected: `nd_168_2024:d41:k4:k@2025-01-01 None` và `nd_168_2024:d41:k4:k1@2026-08-15 None`.
`git diff --stat data/processed/legal_units.jsonl` — số đơn vị của văn bản gốc không đổi (nhãn kiểu này không có ở đầu dòng văn bản gốc).

- [ ] **Step 7: Test, tái lập, commit**

```bash
git add src/lawproc/structure.py src/lawproc/clean.py tests/test_structure.py tests/test_apply.py data/processed
git commit -m "Recognise point labels with a digit such as k1)"
```

---

### Task 3: Phần kết văn bản thành đơn vị `ket_thuc` (L1)

**Files:**
- Modify: `src/lawproc/structure.py`
- Test: `tests/test_structure.py`, `tests/test_processed_invariants.py`

**Interfaces:**
- Produces: `is_closing_line(line: str) -> bool` (public, dùng lại ở test toàn vẹn và EDA). Đơn vị `"{doc_id}:ket_thuc"` bắt đầu từ dòng phần kết đầu tiên; "Nơi nhận:" sau đó được nối vào cùng đơn vị, không tạo `ket_thuc#2`.

Thực tế trong kho: "Luật này được Quốc hội … thông qua ngày …", "Bộ luật này đã được Quốc hội …", "CHỦ TỊCH QUỐC HỘI …", "TM. CHÍNH PHỦ KT. THỦ TƯỚNG PHÓ THỦ TƯỚNG …", "KT. BỘ TRƯỞNG THỨ TRƯỞNG …", "BỘ TRƯỞNG Đại tướng …", "BỘ TRƯỞNG", và khối xác thực VBHN "VĂN PHÒNG QUỐC HỘI Số: 135/VBHN-VPQH . | XÁC THỰC VĂN BẢN HỢP NHẤT …".

- [ ] **Step 1: Viết test thất bại**

Thêm vào `tests/test_structure.py`:

```python
from lawproc.structure import is_closing_line


def test_is_closing_line_patterns():
    assert is_closing_line("Luật này được Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam khóa XV, kỳ họp thứ 7 thông qua ngày 27 tháng 6 năm 2024.")
    assert is_closing_line("Bộ luật này đã được Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam khóa XIII, kỳ họp thứ 10 thông qua ngày 24 tháng 11 năm 2015.")
    assert is_closing_line("CHỦ TỊCH QUỐC HỘI")
    assert is_closing_line("TM. CHÍNH PHỦ KT. THỦ TƯỚNG PHÓ THỦ TƯỚNG daky] Phạm Gia Túc")
    assert is_closing_line("KT. BỘ TRƯỞNG THỨ TRƯỞNG Lê Anh Tuấn")
    assert is_closing_line("BỘ TRƯỞNG Đại tướng Lương Tam Quang")
    assert is_closing_line("VĂN PHÒNG QUỐC HỘI Số: 63/VBHN-VPQH | XÁC THỰC VĂN BẢN HỢP NHẤT Hà Nội, ngày 15 tháng 8 năm 2025")
    assert not is_closing_line("Bộ trưởng Bộ Công an quy định chi tiết khoản này.")
    assert not is_closing_line("Luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2025.")


def test_closing_block_goes_to_ket_thuc():
    lines = ["Điều 89. Hiệu lực thi hành", "1. Luật này có hiệu lực từ ngày 01 tháng 01 năm 2025.",
             "Luật này được Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam khóa XV, kỳ họp thứ 7 thông qua ngày 27 tháng 6 năm 2024.",
             "CHỦ TỊCH QUỐC HỘI", "Trần Thanh Mẫn"]
    units = {u.unit_id: u for u in parse_units("luat", lines)}
    assert units["luat:d89:k1"].text == "Luật này có hiệu lực từ ngày 01 tháng 01 năm 2025."
    assert units["luat:ket_thuc"].text.startswith("Luật này được Quốc hội")
    assert units["luat:ket_thuc"].text.endswith("Trần Thanh Mẫn")


def test_signature_then_noi_nhan_is_one_ket_thuc():
    lines = ["Điều 21. Trách nhiệm thi hành", "Các Bộ trưởng chịu trách nhiệm thi hành Nghị định này./.",
             "TM. CHÍNH PHỦ KT. THỦ TƯỚNG PHÓ THỦ TƯỚNG Phạm Gia Túc", "Nơi nhận:", "- Lưu: VT",
             "PHỤ LỤC I", "Mẫu tờ khai"]
    units = parse_units("nd", lines)
    assert [u.unit_id for u in units if u.level == "ket_thuc"] == ["nd:ket_thuc"]
    by_id = {u.unit_id: u for u in units}
    assert "TM. CHÍNH PHỦ" not in by_id["nd:d21"].text
    assert by_id["nd:ket_thuc"].text.endswith("- Lưu: VT")
    assert by_id["nd:pl1"].text == "Mẫu tờ khai"


def test_closing_words_inside_quote_or_before_first_dieu_are_not_ket_thuc():
    lines = ["BỘ TRƯỞNG BỘ CÔNG AN", "Điều 1. Sửa đổi", "1. Sửa đổi khoản 2 Điều 5 như sau:",
             "“2. BỘ TRƯỞNG Bộ Xây dựng quy định chi tiết.”", "Điều 2. Hiệu lực"]
    ids = [u.unit_id for u in parse_units("tt", lines)]
    assert "tt:ket_thuc" not in ids and "tt:d2" in ids
```

- [ ] **Step 2: Chạy để thấy thất bại**

Run: `python -m pytest tests/test_structure.py -q`
Expected: FAIL (`is_closing_line` chưa có).

- [ ] **Step 3: Cài đặt trong `structure.py`**

Thêm sau `KET_THUC`:

```python
# Phần kết sau Điều cuối: câu thông qua của Quốc hội, khối chữ ký, khối xác thực văn bản hợp nhất.
PASSED = re.compile(r"^(?:Bộ luật|Luật) này (?:đã )?được Quốc hội\b.*\bthông qua\b")
SIGNATURE = re.compile(
    r"^(?:(?:TM|KT|Q|TL|PP)\.\s*[A-ZĐ]"
    r"|(?:CHỦ TỊCH QUỐC HỘI|PHÓ THỦ TƯỚNG|THỦ TƯỚNG|BỘ TRƯỞNG|THỨ TRƯỞNG)(?:$|\s+\S))"
)
VBHN_SEAL = re.compile(r"^VĂN PHÒNG QUỐC HỘI\b.*XÁC THỰC VĂN BẢN HỢP NHẤT")


def is_closing_line(line: str) -> bool:
    return bool(PASSED.match(line) or SIGNATURE.match(line) or VBHN_SEAL.match(line))
```

Trong `parse_units`, thay khối:

```python
        if not fragment and not in_annex and KET_THUC.match(line):
            cur = add(Unit(f"{doc_id}:ket_thuc", doc_id, "ket_thuc", text=line, line_start=i))
            heading = None
            continue
```

bằng:

```python
        if not fragment and not in_annex and (
            KET_THUC.match(line) or (seen_dieu and is_closing_line(line))
        ):
            if cur is not None and cur.level == "ket_thuc":
                _append(cur, line)  # "Nơi nhận" sau khối chữ ký: cùng một phần kết
            else:
                cur = add(Unit(f"{doc_id}:ket_thuc", doc_id, "ket_thuc", text=line, line_start=i))
            heading = None
            continue
```

- [ ] **Step 4: Chạy test**

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Thêm test toàn vẹn**

Thêm vào `tests/test_processed_invariants.py`:

```python
from lawproc.structure import is_closing_line


def test_no_closing_lines_outside_ket_thuc(units):
    bad = [u["unit_id"] for u in units if u["level"] not in ("ket_thuc", "phu_luc", "mo_dau")
           and any(is_closing_line(x) for x in u["text"].splitlines())]
    assert bad == [], bad[:10]
```

- [ ] **Step 6: Chạy lại đầu ra và kiểm tra không mất Điều**

Trước khi chạy lại, lưu `cp data/processed/assembly_report.csv <scratchpad>/assembly_before.csv`.
Chạy 5 bước. Run: `diff <scratchpad>/assembly_before.csv data/processed/assembly_report.csv` → không khác (số Điều, Điều đầu, Điều cuối của mọi văn bản giữ nguyên; nếu khác, một dòng bị nhận nhầm là phần kết và nuốt các Điều sau: sửa mẫu, không nới test).
Run: `python -X utf8 -c "import json,collections;print(collections.Counter(u['level'] for u in map(json.loads,open('data/processed/legal_units.jsonl',encoding='utf-8'))))"` — `ket_thuc` tăng từ 2 lên khoảng 30. In dòng đầu của mọi `ket_thuc` và đọc qua: mỗi dòng phải là phần kết thật.

- [ ] **Step 7: Test, tái lập, commit**

```bash
git add src/lawproc/structure.py tests/test_structure.py tests/test_processed_invariants.py data/processed
git commit -m "Move passing clauses and signature blocks into ket_thuc"
```

---

### Task 4: QCVN 41:2024/BGTVT thành văn bản riêng `qcvn_41_2024` (L2)

**Files:**
- Modify: `src/lawproc/config.py`, `src/lawproc/assemble.py`, `src/lawproc/structure.py`, `src/lawproc/apply.py`, `scripts/process_legal.py`
- Modify: `data/processed/effective_dates.csv` (thêm dòng `qcvn_41_2024`)
- Test: `tests/test_assemble.py`, `tests/test_structure.py`, `tests/test_processed_invariants.py`

**Interfaces:**
- Produces:
  - `config.DERIVED_DOCS: dict[str, dict]` khóa là doc_id suy ra, giá trị có `parent`, `so_ky_hieu`, `tieu_de`, `nhom`, `start`.
  - `config.DOTTED_KHOAN_DOCS = {"qcvn_41_2024"}`.
  - `assemble.drop_toc_lines(lines: list[str]) -> list[str]`; `assemble.split_derived(doc_id: str, lines: list[str]) -> dict[str, list[str]]`.
  - `Unit.phan: str | None` (trường cuối của dataclass, mặc định None); có trong `legal_units.jsonl` và bản có phiên bản.
  - `process_legal.doc_meta() -> dict[str, dict]`: meta mọi văn bản, gồm văn bản suy ra (lấy dòng manifest của văn bản cha, ghi đè `doc_id`, `so_ky_hieu`, `tieu_de`, `nhom`).

Thực tế: `data/processed/documents/tt_51_2024_bgtvt_qcvn41.txt` dòng 1–23 là Thông tư 51 (Điều 1, Điều 2, chữ ký); dòng 24 "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM QCVN 41:2024/BGTVT QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ BÁO HIỆU ĐƯỜNG BỘ …" mở đầu quy chuẩn; dòng 29–60 là mục lục (có chấm dẫn); dòng 61 "PHẦN 1: QUY ĐỊNH CHUNG"; Điều 1 đến Điều 84; khoản đánh số "3.1.", "3.2." (số Điều.số khoản), mục sâu hơn "6.2.3." nằm trong khoản; sau đó các phụ lục A, B, C… Hiệu lực Thông tư 51: 2025-01-01.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `tests/test_assemble.py`:

```python
from lawproc import config
from lawproc.assemble import drop_toc_lines, split_derived


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
```

(Thêm `import pytest` ở đầu file nếu chưa có.)

Thêm vào `tests/test_structure.py`:

```python
def test_phan_heading_and_dotted_khoan_for_qcvn():
    lines = ["CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM QCVN 41:2024/BGTVT", "PHẦN 1: QUY ĐỊNH CHUNG",
             "Điều 3. Giải thích từ ngữ", "Trong Quy chuẩn này, các từ ngữ dưới đây được hiểu như sau:",
             "3.1. Đường đô thị là đường trong phạm vi nội thành.", "3.1.1. Chi tiết của 3.1.",
             "3.2. Đường qua khu đông dân cư là đoạn đường bộ.", "PHẦN 2: QUY ĐỊNH KỸ THUẬT", "CHƯƠNG 1",
             "THỨ TỰ HIỆU LỰC", "Điều 4. Thứ tự hiệu lực của hệ thống báo hiệu", "4.1. Khi ở một khu vực."]
    units = {u.unit_id: u for u in parse_units("qcvn_41_2024", lines)}
    d3 = units["qcvn_41_2024:d3"]
    assert (d3.phan, d3.chuong) == ("1 QUY ĐỊNH CHUNG", None)
    assert units["qcvn_41_2024:d3:k1"].text == "Đường đô thị là đường trong phạm vi nội thành.\n3.1.1. Chi tiết của 3.1."
    assert units["qcvn_41_2024:d3:k2"].level == "khoan"
    d4 = units["qcvn_41_2024:d4"]
    assert (d4.phan, d4.chuong) == ("2 QUY ĐỊNH KỸ THUẬT", "1 THỨ TỰ HIỆU LỰC")
    assert units["qcvn_41_2024:d4:k1"].text == "Khi ở một khu vực."


def test_dotted_khoan_only_for_listed_docs():
    lines = ["Điều 3. Giải thích", "3.1. Không phải khoản ở văn bản thường."]
    units = {u.unit_id: u for u in parse_units("nd", lines)}
    assert "nd:d3:k1" not in units
    assert units["nd:d3"].text == "3.1. Không phải khoản ở văn bản thường."
```

- [ ] **Step 2: Chạy để thấy thất bại**

Run: `python -m pytest tests/test_assemble.py tests/test_structure.py -q`
Expected: FAIL (hàm và trường chưa có).

- [ ] **Step 3: `config.py`**

Thêm cuối file:

```python
# Văn bản suy ra: tách từ văn bản cha khi ghép, không có dòng riêng trong manifest.
# start: chuỗi nằm trong dòng mở đầu văn bản suy ra (dòng đó và mọi dòng sau thuộc văn bản suy ra).
DERIVED_DOCS = {
    "qcvn_41_2024": {
        "parent": "tt_51_2024_bgtvt_qcvn41",
        "so_ky_hieu": "QCVN 41:2024/BGTVT",
        "tieu_de": "Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ",
        "nhom": "Biển báo",
        "start": "QCVN 41:2024/BGTVT QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ BÁO HIỆU ĐƯỜNG BỘ",
    },
}
# Văn bản đánh số khoản dạng "3.1." (số Điều.số khoản)
DOTTED_KHOAN_DOCS = {"qcvn_41_2024"}
```

- [ ] **Step 4: `assemble.py`**

Thêm:

```python
# Dòng mục lục: tiêu đề Phần/Chương/Mục/Phụ lục kèm số hiệu, kết thúc bằng chấm dẫn (có thể kèm số trang).
TOC_LINE = re.compile(
    r"^(?:Phần|PHẦN|Chương|CHƯƠNG|Mục|MỤC|Phụ lục|PHỤ LỤC)\s+[\dIVXLCA-Z]+\b.*[.…]{5,}\s*\d*\s*$"
)


def drop_toc_lines(lines: list[str]) -> list[str]:
    return [x for x in lines if not TOC_LINE.match(x)]


def split_derived(doc_id: str, lines: list[str]) -> dict[str, list[str]]:
    """Tách văn bản suy ra (config.DERIVED_DOCS) khỏi văn bản cha; văn bản khác trả nguyên."""
    out = {doc_id: lines}
    for child, spec in config.DERIVED_DOCS.items():
        if spec["parent"] != doc_id:
            continue
        idx = next((i for i, x in enumerate(lines) if spec["start"] in x), None)
        if idx is None:
            raise ValueError(f"{doc_id}: không thấy dòng mở đầu {child}: {spec['start']!r}")
        out = {doc_id: lines[:idx], child: lines[idx:]}
    return out
```

- [ ] **Step 5: `structure.py`**

Thêm import và mẫu:

```python
from lawproc import config
```

```python
PHAN = re.compile(r"^(?:PHẦN|Phần)\s+(\d+|[IVXLC]+)\b\s*[:.\-–]?\s*(.*)$")
DOTTED_KHOAN = re.compile(r"^(\d+)\.(\d+)\.\s+(.*)$")
```

Đổi `STRUCTURAL = (DIEU, KHOAN, DIEM, CHUONG, MUC, PHULUC, KET_THUC)` thành `STRUCTURAL = (DIEU, KHOAN, DIEM, PHAN, CHUONG, MUC, PHULUC, KET_THUC)`.

Thêm trường cuối vào `Unit` (sau `line_start`):

```python
    phan: str | None = None
```

Trong `parse_units`: khởi tạo `phan = None` cạnh `chuong = muc = None`; `heading` nhận thêm giá trị `"phan"`. Thay khối nối tiêu đề:

```python
        if heading is not None and not _is_structural(line):
            if heading == "phan":
                phan = f"{phan} {line}"
            elif heading == "chuong":
                chuong = f"{chuong} {line}"
            else:
                muc = f"{muc} {line}"
            continue
```

Thêm trước nhánh `CHUONG`:

```python
        if m := PHAN.match(line):
            phan, chuong, muc = m.group(1), None, None
            heading = "phan"
            if m.group(2):
                phan = f"{phan} {m.group(2)}"
            continue
```

Thêm trước nhánh `KHOAN`:

```python
        if (dieu is not None and doc_id in config.DOTTED_KHOAN_DOCS and (m := DOTTED_KHOAN.match(line))
                and m.group(1) == dieu):
            khoan = m.group(2)
            cur = add(Unit(unit_address(doc_id, dieu, khoan, None), doc_id, "khoan", chuong, muc, dieu, khoan,
                           text=m.group(3), line_start=i, phan=phan))
            continue
```

Thêm `phan=phan` vào ba lời gọi `Unit(...)` tạo đơn vị `dieu`, `khoan`, `diem`.

- [ ] **Step 6: `apply.py`**

Trong vòng chép bối cảnh cho đơn vị sinh từ sửa đổi, thêm:

```python
            if u.phan is None:
                u.phan = src.get("phan")
```

- [ ] **Step 7: `scripts/process_legal.py`**

Import `drop_toc_lines, split_derived` từ `lawproc.assemble`. Thêm:

```python
def doc_meta() -> dict[str, dict]:
    """Meta theo doc_id (dòng đầu của manifest), gồm văn bản suy ra (config.DERIVED_DOCS)."""
    meta: dict[str, dict] = {}
    for r in manifest():
        meta.setdefault(r["doc_id"], r)
    for child, spec in config.DERIVED_DOCS.items():
        meta[child] = dict(meta[spec["parent"]], doc_id=child, so_ky_hieu=spec["so_ky_hieu"],
                           tieu_de=spec["tieu_de"], nhom=spec["nhom"])
    return meta
```

Trong `step_assemble`, sau khối áp sửa lỗi OCR, thay phần ghi file và báo cáo bằng:

```python
        lines = drop_toc_lines(lines)
        for out_id, part in split_derived(doc_id, lines).items():
            (DOCS_DIR / f"{out_id}.txt").write_text("\n".join(part) + "\n", encoding="utf-8")
            reports.append(article_report(out_id, part, method, len(chosen)))
            m = meta[out_id]
            idents.append(check_identity(out_id, m["so_ky_hieu"], m["tieu_de"], "\n".join(part)))
```

với `meta = doc_meta()` đặt đầu hàm. Trong `step_effective`, thay `meta = {r["doc_id"]: r for r in manifest()}` bằng `meta = doc_meta()`.

- [ ] **Step 8: Chạy test**

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 9: Thêm ngày hiệu lực đã duyệt cho `qcvn_41_2024`**

Chạy `python scripts/process_legal.py assemble`, `parse`, `effective`. Thêm vào `data/processed/effective_dates.csv` một dòng (dùng script csv như Task 2):
`doc_id=qcvn_41_2024, so_ky_hieu=QCVN 41:2024/BGTVT, ngay_ban_hanh=2024-11-15, hl_congbao=, hl_van_ban=` (lấy từ dòng `qcvn_41_2024` của `effective_dates_auto.csv` nếu có), `tu_dieu_hieu_luc=` (như trên), `trich_dan=` (như trên), `hl_chot=2025-01-01, nguon=van_ban_cha, can_duyet=False, ghi_chu="Ban hành kèm theo TT 51/2024/TT-BGTVT; hiệu lực theo khoản 1 Điều 2 của Thông tư: 01/01/2025."`
Chạy tiếp `amendments`, `apply`.

- [ ] **Step 10: Thêm test toàn vẹn**

Thêm vào `tests/test_processed_invariants.py`:

```python
def test_qcvn41_is_its_own_document(units):
    dieu = sorted(int(u["dieu"]) for u in units if u["doc_id"] == "qcvn_41_2024" and u["level"] == "dieu")
    assert dieu == list(range(1, 85))
    assert not [u for u in units if u["doc_id"] == "tt_51_2024_bgtvt_qcvn41" and u["level"] == "phu_luc"]
    assert any(u["doc_id"] == "qcvn_41_2024" and u["level"] == "khoan" for u in units)


def test_no_empty_annex(units):
    assert [u["unit_id"] for u in units if u["level"] == "phu_luc" and not u["text"].strip()] == []
```

- [ ] **Step 11: Kiểm tra đầu ra**

- `data/processed/identity_report.csv` có dòng `qcvn_41_2024` với `status=ok`; dòng `tt_51_2024_bgtvt_qcvn41` vẫn `ok`.
- `data/processed/assembly_report.csv`: `qcvn_41_2024` có `n_dieu=84`, `missing_dieu` rỗng; `tt_51_2024_bgtvt_qcvn41` có `n_dieu=2`.
- In số dòng bị `drop_toc_lines` bỏ ở mỗi văn bản (so `wc -l` documents trước và sau, hoặc in trong một lần chạy thử). Chỉ `qcvn_41_2024` được phép mất dòng; nếu văn bản khác mất dòng, đọc từng dòng: chỉ chấp nhận nếu đúng là mục lục, nếu không thì siết mẫu.
- Test toàn vẹn cũ `test_tt_155_fee_table_is_a_live_annex`, `test_every_document_has_unit_in_force` vẫn qua.
- Heading Phần không được làm hỏng bối cảnh văn bản khác: so `(unit_id, chuong, muc)` của mọi đơn vị ngoài `qcvn_41_2024` và `tt_51_2024_bgtvt_qcvn41` giữa `git show HEAD:data/processed/legal_units.jsonl` và file mới; phải giống hệt. Nếu khác, chỉ nhận `PHAN` khi `doc_id in config.DOTTED_KHOAN_DOCS` (thêm test) thay vì nới kiểm tra.

- [ ] **Step 12: Test, tái lập, commit**

```bash
git add src/lawproc scripts/process_legal.py tests data/processed
git commit -m "Split QCVN 41:2024 into its own document with parts and dotted clauses"
```

---

### Task 5: Chỉ số chất lượng chữ và OCR lại phụ lục (L7, phần OCR)

**Files:**
- Create: `src/lawproc/quality.py`, `tests/test_quality.py`
- Modify: `src/lawproc/extract.py` (`ocr_pdf_lines`), `src/lawproc/config.py`, `scripts/process_legal.py` (`load_part`)
- Modify: `data/ocr_corrections.csv`
- Test: `tests/test_extract.py`

**Interfaces:**
- Produces:
  - `quality.syllable_error_rate(text: str) -> float` (0–1, làm tròn 4 chữ số).
  - `extract.ocr_pdf_lines(path: Path, cache_dir: Path, dpi: int = 300, retry_pages: Iterable[int] = (), retry_dpi: int = 400) -> list[str]`. Cache: `cache_dir/source.sha256` và `cache_dir/dpi{dpi}/p{i:04d}.txt`. Với trang trong `retry_pages`, OCR thêm ở `retry_dpi` và giữ bản có `syllable_error_rate` thấp hơn (bằng nhau thì giữ bản `dpi`).
  - `config.REOCR_PAGES: dict[str, range]` theo tên file (stem); `config.REOCR_DPI = 400`.

Đo trên dữ liệu hiện tại: văn bản Word sạch có tỷ lệ trung bình ≤ 0,01; phụ lục `tt_108_2026_bca:pl13` 0,39, `pl11` 0,13. Chỉ số không bắt được lỗi dấu (ví dụ "Bé trí"), chỉ bắt chữ vô nghĩa; báo cáo phải nói rõ giới hạn này. Trang phụ lục: `tt_108_2026_bca__p1` trang 38–133 (đánh số từ 0, phụ lục I bắt đầu ở `p0038`), `tt_36_2024_byt__p1` trang 8–13 (`p0008`). Tiêu đề phụ lục TT 108 bị OCR sai số La Mã: "PHỤ LỤC H" (II), "LHI" (III), "VH" (VII), "VIH" (VIII), "XH" (XII), "XIH" (XIII). TT 108 còn lỗi cấu trúc do OCR: "9, Cấp thẻ sát hạch viên" (khoản 9 Điều 8 bị nối vào khoản 8), "Chương VỊ ĐIỀU KHOẢN THI HÀNH" (Chương VI bị nối vào khoản 14 Điều 40).

- [ ] **Step 1: Viết test thất bại cho `quality`**

`tests/test_quality.py`:

```python
from lawproc.quality import syllable_error_rate


def test_clean_vietnamese_has_zero_rate():
    assert syllable_error_rate("Người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông") == 0.0


def test_abbreviations_numbers_and_single_letters_are_ignored():
    assert syllable_error_rate("GPLX hạng B1 theo Nghị định số 168/2024/NĐ-CP, điểm a") == 0.0


def test_ocr_junk_has_high_rate():
    assert syllable_error_rate("la Xeôtô wW0W0W ốơúó lbXxemt To000 Câpđôibiênsôxe Sa Xeono lbFemôo") > 0.5


def test_empty_text_is_zero():
    assert syllable_error_rate("12/2025 —") == 0.0
```

- [ ] **Step 2: Chạy để thấy thất bại**

Run: `python -m pytest tests/test_quality.py -q` → FAIL (module chưa có).

- [ ] **Step 3: Viết `src/lawproc/quality.py`**

```python
"""Chỉ số chất lượng chữ: tỷ lệ từ không phải âm tiết tiếng Việt hợp lệ (phụ âm đầu + vần), sau khi bỏ dấu thanh.

Bỏ qua chữ số, từ một chữ cái và từ viết hoa toàn bộ (viết tắt như GPLX, NĐ). Chỉ bắt chữ vô nghĩa do OCR;
không bắt lỗi dấu (ví dụ "Bé trí" thay cho "Bố trí").
"""
import re
import unicodedata

TONE_MARKS = {"\u0300", "\u0301", "\u0303", "\u0309", "\u0323"}  # huyền, sắc, ngã, hỏi, nặng
ONSET = r"(?:ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdđghklmnprstvx])?"
NUCLEUS = r"[aăâeêioôơuưy]{1,3}"
CODA = r"(?:ch|nh|ng|[cmnpt])?"
SYLLABLE = re.compile(rf"^{ONSET}{NUCLEUS}{CODA}$")
WORD = re.compile(r"[^\W\d_]+")


def _strip_tone(word: str) -> str:
    d = unicodedata.normalize("NFD", word.lower())
    return unicodedata.normalize("NFC", "".join(c for c in d if c not in TONE_MARKS))


def syllable_error_rate(text: str) -> float:
    words = [w for w in WORD.findall(text) if len(w) > 1 and not w.isupper()]
    if not words:
        return 0.0
    bad = sum(1 for w in words if not SYLLABLE.match(_strip_tone(w)))
    return round(bad / len(words), 4)
```

- [ ] **Step 4: Chạy test**

Run: `python -m pytest tests/test_quality.py -q` → PASS.

- [ ] **Step 5: Test thất bại cho cache OCR**

Trong `tests/test_extract.py`, sửa test OCR hiện có và thêm test mới:

```python
@pytest.mark.skipif(not config.TESSERACT.exists(), reason="Tesseract chưa cài")
def test_ocr_pdf_lines_reads_vietnamese_and_caches(tmp_path):
    p = tmp_path / "scan.pdf"
    _pdf_with_lines(p, ["Điều 2. Người nộp lệ phí"])
    cache = tmp_path / "cache"
    lines = ocr_pdf_lines(p, cache, dpi=200)
    assert any("Người nộp lệ phí" in x for x in lines)
    assert (cache / "dpi200" / "p0000.txt").exists()
    assert (cache / "source.sha256").read_text().strip()


def test_ocr_cache_from_other_file_is_refused(tmp_path):
    p = tmp_path / "scan.pdf"
    _pdf_with_lines(p, ["Điều 2."])
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "source.sha256").write_text("0" * 64 + "\n")
    with pytest.raises(ValueError, match="sha256"):
        ocr_pdf_lines(p, cache, dpi=200)


def test_ocr_retry_pages_keep_better_text(tmp_path, monkeypatch):
    p = tmp_path / "scan.pdf"
    _pdf_with_lines(p, ["Điều 2."])
    cache = tmp_path / "cache"
    texts = {200: "la Xeôtô wW0W0W lbXxemt\n", 400: "Người nộp lệ phí\n"}

    def fake_page(page, i, cache_dir, dpi, tmp):
        return texts[dpi]

    monkeypatch.setattr("lawproc.extract._ocr_page", fake_page)
    assert ocr_pdf_lines(p, cache, dpi=200, retry_pages=[0], retry_dpi=400) == ["Người nộp lệ phí"]
    assert ocr_pdf_lines(p, cache, dpi=200) == ["la Xeôtô wW0W0W lbXxemt"]
```

Run: `python -m pytest tests/test_extract.py -q` → các test mới FAIL.

- [ ] **Step 6: Sửa `extract.py`**

Thêm import `hashlib`, `from collections.abc import Iterable`, `from lawproc.quality import syllable_error_rate`. Thay `ocr_pdf_lines` bằng:

```python
def _check_source(path: Path, cache_dir: Path) -> None:
    """Cache OCR gắn với sha256 của file nguồn; cache của file khác thì báo lỗi thay vì dùng nhầm."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    marker = cache_dir / "source.sha256"
    if marker.exists() and marker.read_text().strip() != sha:
        raise ValueError(f"cache OCR {cache_dir} có sha256 khác {path.name}; xóa thư mục cache rồi chạy lại")
    marker.write_text(sha + "\n")


def _ocr_page(page, i: int, cache_dir: Path, dpi: int, tmp: str) -> str:
    cached = cache_dir / f"dpi{dpi}" / f"p{i:04d}.txt"
    if not cached.exists():
        cached.parent.mkdir(parents=True, exist_ok=True)
        png = Path(tmp) / f"p{i:04d}_{dpi}.png"
        page.get_pixmap(dpi=dpi).save(str(png))
        r = subprocess.run(
            [str(config.TESSERACT), "--tessdata-dir", config.TESSDATA_REL, str(png), "-",
             "-l", "vie", "--psm", "6"],
            cwd=config.ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        png.unlink()
        if r.returncode != 0:
            raise RuntimeError(f"Tesseract lỗi ở trang {i} ({cache_dir.name}, dpi {dpi}): {r.stderr.strip()}")
        cached.write_text(r.stdout, encoding="utf-8")
    return cached.read_text(encoding="utf-8")


def ocr_pdf_lines(path: Path, cache_dir: Path, dpi: int = 300, retry_pages: Iterable[int] = (),
                  retry_dpi: int = 400) -> list[str]:
    _check_source(path, cache_dir)
    retry = set(retry_pages)
    lines: list[str] = []
    with pymupdf.open(str(path)) as doc, tempfile.TemporaryDirectory() as tmp:
        for i, page in enumerate(doc):
            text = _ocr_page(page, i, cache_dir, dpi, tmp)
            if i in retry:
                other = _ocr_page(page, i, cache_dir, retry_dpi, tmp)
                if syllable_error_rate(other) < syllable_error_rate(text):
                    text = other
            lines.extend(text.splitlines())
    return lines
```

Run: `python -m pytest tests/test_extract.py -q` → PASS.

- [ ] **Step 7: Cấu hình và chuyển cache cũ**

`config.py`, thêm:

```python
# Trang (đánh số từ 0) OCR thêm ở REOCR_DPI, giữ bản tốt hơn theo quality.syllable_error_rate; khóa là tên file
REOCR_PAGES = {"tt_108_2026_bca__p1": range(38, 134), "tt_36_2024_byt__p1": range(8, 14)}
REOCR_DPI = 400
```

`scripts/process_legal.py`, trong `load_part` nhánh `ocr`:

```python
        return ocr_pdf_lines(path, OCR_DIR / path.stem, retry_pages=config.REOCR_PAGES.get(path.stem, ()),
                             retry_dpi=config.REOCR_DPI)
```

Chuyển cache 300 dpi hiện có sang bố cục mới (thư mục `data/interim/` không lên Git), để không phải OCR lại trang đã có:

```bash
for d in data/interim/ocr/*/; do mkdir -p "$d/dpi300" && mv "$d"/p*.txt "$d/dpi300/"; done
```

(`source.sha256` sẽ được ghi ở lần chạy đầu.)

- [ ] **Step 8: Chạy OCR lại**

Run (chạy nền, có thể mất 30–60 phút cho khoảng 100 trang ở 400 dpi): `python scripts/process_legal.py assemble`.
Nếu bước này dừng với `ValueError` từ `apply_corrections`, đó là dòng sửa lỗi OCR mà chuỗi sai không còn (trang đã được OCR lại). Xử lý từng dòng: (a) chuỗi đúng `right` đã có trong văn bản mới → xóa dòng; (b) không → tìm đoạn tương ứng trong văn bản mới, viết lại `wrong` theo chữ mới (đủ dài để xuất hiện đúng một lần) và giữ `right`. Để thấy toàn bộ trạng thái một lần, tạm chạy một script trong scratchpad gọi `assemble_doc` + đếm `text.count(wrong)` cho mọi dòng của `tt_108_2026_bca` và `tt_36_2024_byt`.

- [ ] **Step 9: Sửa lỗi cấu trúc do OCR trong TT 108**

Thêm dòng vào `data/ocr_corrections.csv` (cột `doc_id,wrong,right,note`), `wrong` lấy đúng chuỗi trong văn bản sau Step 8, đủ dài để duy nhất:
- Tiêu đề phụ lục số La Mã: "PHỤ LỤC H (" → "PHỤ LỤC II (", "PHỤ LỤC LHI" → "PHỤ LỤC III", "PHỤ LỤC VH" → "PHỤ LỤC VII", "PHỤ LỤC VIH" → "PHỤ LỤC VIII", "PHỤ LỤC XH" → "PHỤ LỤC XII", "PHỤ LỤC XIH" → "PHỤ LỤC XIII" (chỉ những dòng còn sai sau Step 8; ghi note "L7 số phụ lục"). TT 36: "PHỤ LỤC H" → "PHỤ LỤC II" nếu trang 8 vẫn sai.
- "9, Cấp thẻ sát hạch viên" → "9. Cấp thẻ sát hạch viên" (note "L7 khoản 9 Điều 8").
- "Chương VỊ" → "Chương VI" (note "L7 Chương VI").
- Tìm thêm khoản bị mất do "N," hoặc "N:" thay cho "N." trong ba văn bản OCR: chạy script liệt kê, với mỗi Điều của `tt_108_2026_bca`, `tt_36_2024_byt`, `tt_155_2025_btc`, các số khoản bị nhảy (ví dụ có k8 và k10 mà không có k9). Với mỗi chỗ nhảy, mở văn bản, nếu đúng là lỗi OCR thì thêm dòng sửa; nếu văn bản gốc thật sự nhảy số thì ghi vào báo cáo Task 8.

Chạy lại `assemble`, `parse`, `effective`, `amendments`, `apply`.

- [ ] **Step 10: Ghi số liệu cho báo cáo**

In và lưu vào `<scratchpad>/ocr_quality.txt` (Task 8 dùng): tỷ lệ âm tiết lỗi trung bình theo văn bản OCR trước (từ bản đã commit, `git show HEAD:data/processed/legal_units.jsonl`) và sau; số trang mà bản 400 dpi được chọn; số dòng sửa OCR đã xóa, đã viết lại, đã thêm.

- [ ] **Step 11: Test, tái lập, commit**

Run: `python -m pytest -q` → PASS. Chạy lại 5 bước (lần này dùng cache, nhanh), đầu ra không đổi.

```bash
git add src/lawproc/quality.py src/lawproc/extract.py src/lawproc/config.py scripts/process_legal.py tests data/ocr_corrections.csv data/processed
git commit -m "Re-OCR annex pages at 400 dpi when text is cleaner, key OCR cache by file hash"
```

---

### Task 6: Gắn nhãn bản ghi: nội dung đổi, loại phụ lục, chất lượng (L6, L7 phần phân loại)

**Files:**
- Create: `src/lawproc/annotate.py`, `tests/test_annotate.py`
- Modify: `src/lawproc/config.py`, `scripts/process_legal.py` (`step_apply`)
- Create (sinh ra): `data/processed/annex_types.csv`
- Test: `tests/test_processed_invariants.py`

**Interfaces:**
- Consumes: `quality.syllable_error_rate`.
- Produces (trường mới trên mọi bản ghi của `legal_units_versioned.jsonl`):
  - `noi_dung_doi: bool` — True nếu là phiên bản đầu của `unit_id` hoặc (title, text) khác phiên bản liền trước theo `valid_from`.
  - `loai_phu_luc: str | None` — `"mau_bieu"` hoặc `"noi_dung"` cho cấp `phu_luc`, None cho cấp khác.
  - `ty_le_am_tiet_loi: float`; `chat_luong: str` — `"kem"` nếu `ty_le_am_tiet_loi > config.QUALITY_BAD` và văn bản có ít nhất `config.QUALITY_MIN_WORDS` từ, ngược lại `"ok"`.
  - `annotate.mark_content_change(records: list[dict]) -> None`, `annotate.annex_type(title: str, text: str) -> tuple[str, str]` (loại, lý do), `annotate.annotate_records(records: list[dict], overrides: dict[str, str]) -> list[dict]` (gắn mọi trường trên, trả về các dòng cho `annex_types.csv`).
  - File tùy chọn `data/annex_type_overrides.csv` (cột `unit_id,loai_phu_luc,ghi_chu`) ghi đè phân loại tự động.

- [ ] **Step 1: Viết test thất bại**

`tests/test_annotate.py`:

```python
from lawproc.annotate import annex_type, annotate_records, mark_content_change


def _rec(uid, vf, text, level="khoan", title=""):
    return {"unit_id": uid, "doc_id": uid.split(":")[0], "level": level, "title": title, "text": text,
            "valid_from": vf, "valid_to": None}


def test_mark_content_change():
    recs = [_rec("a:d1:k1", "2026-01-01", "mới"), _rec("a:d1:k1", "2025-01-01", "cũ"),
            _rec("a:d1:k1", "2026-08-15", "mới"), _rec("a:d1:k2", "2025-01-01", "x")]
    mark_content_change(recs)
    by = {r["valid_from"] + r["unit_id"]: r["noi_dung_doi"] for r in recs}
    assert by["2025-01-01a:d1:k1"] is True
    assert by["2026-01-01a:d1:k1"] is True
    assert by["2026-08-15a:d1:k1"] is False
    assert by["2025-01-01a:d1:k2"] is True


def test_annex_type_form_by_title_or_fill_lines():
    assert annex_type("Phụ lục XVI", "MẪU ĐỀ NGHỊ CẤP GIẤY PHÉP LÁI XE QUỐC TẾ\n...")[0] == "mau_bieu"
    assert annex_type("PHỤ LỤC H MAU GIAY KHAM SỨC KHỎE", "")[0] == "mau_bieu"
    fill = "\n".join(["Họ và tên: ......................"] * 4 + ["Ghi chú"])
    assert annex_type("Phụ lục I", fill)[0] == "mau_bieu"
    assert annex_type("Phụ lục BIỂU MỨC THU LỆ PHÍ", "1. Xe ô tô | 500.000 đồng\n2. Xe mô tô | 50.000 đồng")[0] == "noi_dung"


def test_annotate_records_sets_fields_and_overrides():
    recs = [_rec("a:pl1", "2025-01-01", "Họ và tên: .........\nNgày sinh: .........", level="phu_luc", title="Phụ lục I"),
            _rec("a:pl2", "2025-01-01", "Trình tự sát hạch lái xe hạng B", level="phu_luc", title="Phụ lục II"),
            _rec("a:d1:k1", "2025-01-01", "Người điều khiển xe")]
    rows = annotate_records(recs, {"a:pl2": "mau_bieu"})
    by = {r["unit_id"]: r for r in recs}
    assert by["a:pl1"]["loai_phu_luc"] == "mau_bieu"
    assert by["a:pl2"]["loai_phu_luc"] == "mau_bieu"  # ghi đè
    assert by["a:d1:k1"]["loai_phu_luc"] is None
    assert by["a:d1:k1"]["chat_luong"] == "ok" and by["a:d1:k1"]["noi_dung_doi"] is True
    assert [r["unit_id"] for r in rows] == ["a:pl1", "a:pl2"]
    assert rows[1]["ly_do"] == "ghi đè"
```

Run: `python -m pytest tests/test_annotate.py -q` → FAIL.

- [ ] **Step 2: `config.py`**

```python
# Đơn vị có tỷ lệ âm tiết lỗi vượt ngưỡng (và đủ dài) bị gắn chat_luong = "kem"
QUALITY_BAD = 0.1
QUALITY_MIN_WORDS = 50
```

- [ ] **Step 3: Viết `src/lawproc/annotate.py`**

```python
"""Gắn nhãn cho bản ghi có phiên bản: nội dung có đổi không, loại phụ lục, chất lượng chữ."""
import re
from collections import defaultdict

from lawproc import config
from lawproc.quality import syllable_error_rate

FORM_WORD = re.compile(r"\b(?:MẪU|Mẫu|MAU)\b")
FILL_LINE = re.compile(r"[.…]{4,}")
FILL_SHARE = 0.3
HEAD_CHARS = 300


def mark_content_change(records: list[dict]) -> None:
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_unit[r["unit_id"]].append(r)
    for recs in by_unit.values():
        recs.sort(key=lambda r: r["valid_from"])
        prev = None
        for r in recs:
            r["noi_dung_doi"] = prev is None or (r["title"], r["text"]) != (prev["title"], prev["text"])
            prev = r


def annex_type(title: str, text: str) -> tuple[str, str]:
    """Mẫu biểu: tiêu đề/đầu nội dung có chữ "Mẫu", hoặc từ 30% dòng là dòng điền "……"."""
    head = f"{title}\n{text[:HEAD_CHARS]}"
    if FORM_WORD.search(head):
        return "mau_bieu", "tiêu đề có chữ Mẫu"
    lines = [x for x in text.splitlines() if x.strip()]
    if lines and sum(bool(FILL_LINE.search(x)) for x in lines) / len(lines) >= FILL_SHARE:
        return "mau_bieu", "nhiều dòng điền"
    return "noi_dung", ""


def annotate_records(records: list[dict], overrides: dict[str, str]) -> list[dict]:
    mark_content_change(records)
    rows: dict[str, dict] = {}
    for r in records:
        rate = syllable_error_rate(r["text"])
        r["ty_le_am_tiet_loi"] = rate
        words = len(re.findall(r"\w+", r["text"]))
        r["chat_luong"] = "kem" if rate > config.QUALITY_BAD and words >= config.QUALITY_MIN_WORDS else "ok"
        if r["level"] != "phu_luc":
            r["loai_phu_luc"] = None
            continue
        if r["unit_id"] in overrides:
            loai, ly_do = overrides[r["unit_id"]], "ghi đè"
        else:
            loai, ly_do = annex_type(r["title"], r["text"])
        r["loai_phu_luc"] = loai
        rows.setdefault(r["unit_id"], {"unit_id": r["unit_id"], "doc_id": r["doc_id"], "title": r["title"][:120],
                                       "loai_phu_luc": loai, "ly_do": ly_do, "ty_le_am_tiet_loi": rate,
                                       "chat_luong": r["chat_luong"]})
    return list(rows.values())
```

Run: `python -m pytest tests/test_annotate.py -q` → PASS.

- [ ] **Step 4: Gọi trong `step_apply`**

`scripts/process_legal.py`: import `annotate_records`; thêm hằng `ANNEX_TYPES = config.PROCESSED / "annex_types.csv"`, `ANNEX_OVERRIDES = config.DATA / "annex_type_overrides.csv"`. Trong `step_apply`, ngay sau `recs = apply_amendments(...)`:

```python
    overrides = {}
    if ANNEX_OVERRIDES.exists():
        overrides = {r["unit_id"]: r["loai_phu_luc"]
                     for r in csv.DictReader(ANNEX_OVERRIDES.open(encoding="utf-8-sig"))}
    write_csv(ANNEX_TYPES, annotate_records(recs, overrides))
```

- [ ] **Step 5: Test toàn vẹn**

Thêm vào `tests/test_processed_invariants.py`:

```python
def test_records_have_annotations(versioned):
    assert all(isinstance(r["noi_dung_doi"], bool) and r["chat_luong"] in ("ok", "kem") for r in versioned)
    assert all((r["loai_phu_luc"] in ("mau_bieu", "noi_dung")) == (r["level"] == "phu_luc") for r in versioned)
```

- [ ] **Step 6: Chạy lại, kiểm tra**

Chạy `apply` (các bước trước không đổi). Run: `python -m pytest -q` → PASS.
In: số bản ghi `noi_dung_doi = false` (trước đợt này là 184; ghi số mới), số phụ lục mỗi loại theo văn bản, danh sách bản ghi `chat_luong = kem` (unit_id, tỷ lệ). Lưu vào `<scratchpad>/annotate_summary.txt` cho Task 8.

- [ ] **Step 7: Commit**

```bash
git add src/lawproc/annotate.py src/lawproc/config.py scripts/process_legal.py tests data/processed
git commit -m "Annotate versions with content change, annex type and text quality"
```

- [ ] **Step 8: ĐIỂM DỪNG DUYỆT (controller)**

Controller đưa người dùng xem tóm tắt `data/processed/annex_types.csv`: số phụ lục `mau_bieu`/`noi_dung` theo văn bản, các phụ lục `mau_bieu` có lý do "nhiều dòng điền" và mọi phụ lục `chat_luong = kem`. Phụ lục nào người dùng muốn đổi loại thì ghi vào `data/annex_type_overrides.csv`, chạy lại `apply`, commit "Apply reviewed annex type overrides". Không sang Task 7 trước khi người dùng trả lời.

---

### Task 7: Ngoại lệ hiệu lực và hàm lọc theo thời điểm (L5)

**Files:**
- Create: `src/lawproc/validity.py`, `tests/test_validity.py`, `data/effective_exceptions.csv`
- Modify: `scripts/process_legal.py` (`step_apply`), `tests/test_processed_invariants.py`

**Interfaces:**
- Produces:
  - `validity.load_exceptions(path: Path) -> list[dict]`.
  - `validity.attach_exceptions(records: list[dict], rows: list[dict]) -> None` — thêm trường `hl_ngoai_le: list[dict]` cho mọi bản ghi (rỗng nếu không có). Mỗi phần tử: `{"loai", "vai_tro", "tu_ngay", "den_ngay", "dieu_kien", "can_cu"}`, `vai_tro` ∈ `gia_han`, `moi`, `cu`, `moc`. Lỗi (loại lạ, ngày sai, thiếu ngày bắt buộc, `unit_id` không khớp bản ghi nào) được gom và raise một `ValueError`.
  - `validity.in_force_at(rec: dict, t: str) -> tuple[bool, str | None]` — có hiệu lực tại t không, và điều kiện kèm theo (các `dieu_kien` nối bằng "; ", None nếu không có).

**Ngữ nghĩa từng loại** (mỗi dòng áp cho bản ghi của `unit_id` và mọi đơn vị con, tức `unit_id` bằng hoặc bắt đầu bằng `unit_id + ":"`):
- `gia_han` (cần `den_ngay`): áp cho phiên bản cuối của mỗi đơn vị nếu phiên bản đó đã bị đóng (`valid_to` có giá trị); vai trò `gia_han`. Bản ghi được coi là còn hiệu lực từ `valid_to` đến trước `den_ngay`.
- `hoan_ap_dung` (cần `tu_ngay`): với mỗi đơn vị, bản "mới" là phiên bản có `valid_from < tu_ngay` muộn nhất; vai trò `moi`. Bản "cũ" là phiên bản có `valid_to == valid_from` của bản mới (nếu có); vai trò `cu`. Trước `tu_ngay`: bản mới chỉ áp dụng kèm `dieu_kien`; nếu `dieu_kien` rỗng thì bản mới chưa áp dụng. Bản cũ còn áp dụng đến trước `tu_ngay`, kèm `dieu_kien`.
- `moc_trong_noi_dung` (cần `tu_ngay`): áp cho mọi phiên bản; vai trò `moc`. Không đổi hiệu lực; trước `tu_ngay`, khi bản ghi có hiệu lực thì trả kèm `dieu_kien`.

**Nội dung `data/effective_exceptions.csv`** (trợ lý soạn từ văn bản; người dùng duyệt khi duyệt kế hoạch này). Cột: `unit_id,loai,tu_ngay,den_ngay,dieu_kien,can_cu,ghi_chu`.

| unit_id | loai | tu_ngay | den_ngay | dieu_kien | can_cu |
|---|---|---|---|---|---|
| tt_12_2025_bca:d4:k1 | gia_han | | 2027-03-01 | | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:d4:k2 | gia_han | | 2027-03-01 | | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:d4:k3 | gia_han | | 2027-03-01 | | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:pl2 | gia_han | | 2027-03-01 | | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:pl3 | gia_han | | 2027-03-01 | | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:pl4 | gia_han | | 2027-03-01 | Chỉ mục A, mục C và mẫu số 01, 02, 03 mục D của phụ lục này còn hiệu lực | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:pl5 | gia_han | | 2027-03-01 | Chỉ mục A, mục C và mẫu số 01, 02, 03 mục D của phụ lục này còn hiệu lực | tt_108_2026_bca:d41:k6 |
| tt_12_2025_bca:pl6 | gia_han | | 2027-03-01 | Chỉ mục A, mục C và mẫu số 01, 02, 03 mục D của phụ lục này còn hiệu lực | tt_108_2026_bca:d41:k6 |
| nd_168_2024:d20:k5:l | hoan_ap_dung | 2028-01-01 | | Đến hết 31/12/2027, quy định về thiết bị ghi nhận hình ảnh người lái xe chỉ áp dụng với xe ô tô chở người từ 08 chỗ trở lên kinh doanh vận tải hành khách (như bản trước); với xe kinh doanh vận tải hành khách dưới 08 chỗ và xe vận tải nội bộ áp dụng từ 01/01/2028 | nd_168_2024:d53:k3 |
| nd_168_2024:d21:k3:b | hoan_ap_dung | 2028-01-01 | | Đến hết 31/12/2027, chỉ áp dụng với xe ô tô đầu kéo (như bản trước); với xe ô tô kinh doanh vận tải hàng hóa (trừ xe đầu kéo) và xe vận tải nội bộ áp dụng từ 01/01/2028 | nd_168_2024:d53:k3 |
| nd_168_2024:d32:k9a:b | hoan_ap_dung | 2028-01-01 | | Đến hết 31/12/2027, điểm này áp dụng với chủ xe ô tô đầu kéo; với chủ xe vận tải nội bộ áp dụng từ 01/01/2028 | nd_168_2024:d53:k3 |
| luat_36_2024:d35:k2 | hoan_ap_dung | 2028-01-01 | | Đến hết 31/12/2027, yêu cầu lắp thiết bị ghi nhận hình ảnh người lái xe chưa áp dụng với xe ô tô kinh doanh vận tải hành khách dưới 08 chỗ, xe ô tô kinh doanh vận tải hàng hóa (trừ xe đầu kéo), xe vận tải nội bộ; các xe còn lại áp dụng như bản trước | luat_36_2024:d88:k2a |
| luat_36_2024:d35:k2 | moc_trong_noi_dung | 2029-01-01 | | Yêu cầu lắp thiết bị ghi nhận hình ảnh khoang chở khách đối với xe ô tô kinh doanh vận tải hành khách từ 08 chỗ trở lên áp dụng từ 01/01/2029 theo lộ trình của Chính phủ | luat_36_2024:d88:k2a |
| tt_108_2026_bca:d4:k4 | hoan_ap_dung | 2027-03-01 | | | tt_108_2026_bca:d41:k2 |
| tt_108_2026_bca:d4:k4 | moc_trong_noi_dung | 2028-01-01 | | Nội dung bài sát hạch số 2 (Phụ lục I) áp dụng từ 01/01/2028 | tt_108_2026_bca:d41:k2 |
| tt_108_2026_bca:pl1 | moc_trong_noi_dung | 2028-01-01 | | Bài sát hạch số 2 và hình, thiết bị, phần mềm sát hạch tình huống giả định trên đường hạng A1, A áp dụng từ 01/01/2028 | tt_108_2026_bca:d41:k2; tt_108_2026_bca:d41:k3 |
| tt_108_2026_bca:pl1 | moc_trong_noi_dung | 2027-01-01 | | Nội dung nhận diện thí sinh qua thiết bị, phần mềm định danh và xác thực điện tử áp dụng từ 01/01/2027 | tt_108_2026_bca:d41:k5 |
| tt_108_2026_bca:pl2 | moc_trong_noi_dung | 2027-01-01 | | (như dòng trên) | tt_108_2026_bca:d41:k5 |
| tt_108_2026_bca:pl3 | moc_trong_noi_dung | 2027-01-01 | | (như dòng trên) | tt_108_2026_bca:d41:k5 |
| tt_108_2026_bca:pl4 | moc_trong_noi_dung | 2027-01-01 | | (như dòng trên) | tt_108_2026_bca:d41:k5 |
| tt_108_2026_bca:pl5 | moc_trong_noi_dung | 2027-01-01 | | (như dòng trên) | tt_108_2026_bca:d41:k5 |
| tt_108_2026_bca:d3:k4 | moc_trong_noi_dung | 2027-07-01 | | Cấp thẻ sát hạch viên điện tử áp dụng từ 01/7/2027 | tt_108_2026_bca:d41:k4 |

Trong file CSV, "(như dòng trên)" được thay bằng đầy đủ câu "Nội dung nhận diện thí sinh qua thiết bị, phần mềm định danh và xác thực điện tử áp dụng từ 01/01/2027". Cột `ghi_chu` ghi trích dẫn ngắn của căn cứ. Dòng `tt_108_2026_bca:pl1`–`pl5` chỉ đúng nếu sau Task 5 các phụ lục này có tiêu đề "PHỤ LỤC I" đến "PHỤ LỤC V" theo thứ tự; implementer kiểm tra và báo nếu khác.

- [ ] **Step 1: Viết test thất bại**

`tests/test_validity.py`:

```python
import pytest

from lawproc.validity import attach_exceptions, in_force_at


def _r(uid, vf, vt):
    return {"unit_id": uid, "valid_from": vf, "valid_to": vt}


def _row(uid, loai, tu="", den="", dk=""):
    return {"unit_id": uid, "loai": loai, "tu_ngay": tu, "den_ngay": den, "dieu_kien": dk, "can_cu": "x:d1",
            "ghi_chu": ""}


def test_plain_record_follows_valid_dates():
    attach_exceptions([r := _r("a:d1", "2025-01-01", "2026-07-01")], [])
    assert r["hl_ngoai_le"] == []
    assert in_force_at(r, "2026-06-30") == (True, None)
    assert in_force_at(r, "2026-07-01") == (False, None)


def test_gia_han_extends_last_closed_version_and_children():
    recs = [_r("t:d4:k1", "2025-03-01", "2026-07-01"), _r("t:d4:k1:a", "2025-03-01", "2026-07-01"),
            _r("t:d4:k5", "2025-03-01", "2026-07-01")]
    attach_exceptions(recs, [_row("t:d4:k1", "gia_han", den="2027-03-01")])
    assert in_force_at(recs[0], "2026-10-01") == (True, None)
    assert in_force_at(recs[1], "2027-02-28") == (True, None)
    assert in_force_at(recs[1], "2027-03-01") == (False, None)
    assert in_force_at(recs[2], "2026-10-01") == (False, None)


def test_hoan_ap_dung_with_condition_keeps_old_and_new():
    old, new = _r("n:d20:k5:l", "2025-01-01", "2026-08-15"), _r("n:d20:k5:l", "2026-08-15", None)
    attach_exceptions([old, new], [_row("n:d20:k5:l", "hoan_ap_dung", tu="2028-01-01", dk="Đến 2027 chỉ xe X")])
    assert in_force_at(new, "2026-10-01") == (True, "Đến 2027 chỉ xe X")
    assert in_force_at(old, "2026-10-01") == (True, "Đến 2027 chỉ xe X")
    assert in_force_at(old, "2028-01-01") == (False, None)
    assert in_force_at(new, "2028-01-01") == (True, None)


def test_hoan_ap_dung_without_condition_means_not_yet_applied():
    r = _r("t:d4:k4", "2026-07-01", None)
    attach_exceptions([r], [_row("t:d4:k4", "hoan_ap_dung", tu="2027-03-01")])
    assert in_force_at(r, "2026-10-01") == (False, None)
    assert in_force_at(r, "2027-03-01") == (True, None)


def test_moc_adds_note_only_before_date():
    r = _r("l:d35:k2", "2026-07-01", None)
    attach_exceptions([r], [_row("l:d35:k2", "moc_trong_noi_dung", tu="2029-01-01", dk="Khoang chở khách từ 2029")])
    assert in_force_at(r, "2026-10-01") == (True, "Khoang chở khách từ 2029")
    assert in_force_at(r, "2029-01-01") == (True, None)
    assert in_force_at(r, "2026-06-30") == (False, None)


def test_bad_rows_are_all_reported():
    recs = [_r("a:d1", "2025-01-01", None)]
    rows = [_row("khong:co", "gia_han", den="2027-03-01"), _row("a:d1", "loai_la", tu="2027-01-01"),
            _row("a:d1", "hoan_ap_dung", tu="2027-13-01"), _row("a:d1", "gia_han")]
    with pytest.raises(ValueError) as exc:
        attach_exceptions(recs, rows)
    msg = str(exc.value)
    assert "khong:co" in msg and "loai_la" in msg and "2027-13-01" in msg and "den_ngay" in msg
```

Run: `python -m pytest tests/test_validity.py -q` → FAIL.

- [ ] **Step 2: Viết `src/lawproc/validity.py`**

```python
"""Ngoại lệ về hiệu lực (data/effective_exceptions.csv) và hàm lọc bản ghi theo thời điểm.

Một bản ghi có hiệu lực tại t khi valid_from <= t < valid_to (valid_to None là vô hạn), trừ khi hl_ngoai_le nói khác.
"""
import csv
from datetime import date
from pathlib import Path

TYPES = {"gia_han", "hoan_ap_dung", "moc_trong_noi_dung"}


def load_exceptions(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))


def _valid_date(value: str) -> bool:
    try:
        return len(value) == 10 and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _under(uid: str, prefix: str) -> bool:
    return uid == prefix or uid.startswith(prefix + ":")


def attach_exceptions(records: list[dict], rows: list[dict]) -> None:
    for r in records:
        r["hl_ngoai_le"] = []
    by_unit: dict[str, list[dict]] = {}
    for r in records:
        by_unit.setdefault(r["unit_id"], []).append(r)
    for recs in by_unit.values():
        recs.sort(key=lambda r: r["valid_from"])
    problems: list[str] = []
    for i, row in enumerate(rows):
        uid, loai = row["unit_id"], row["loai"]
        need = "den_ngay" if loai == "gia_han" else "tu_ngay"
        if loai not in TYPES:
            problems.append(f"dòng {i} ({uid}): loại lạ {loai!r}")
            continue
        if not row[need]:
            problems.append(f"dòng {i} ({uid}): {loai} cần {need}")
            continue
        if not _valid_date(row[need]):
            problems.append(f"dòng {i} ({uid}): {need} {row[need]!r} không phải ngày YYYY-MM-DD")
            continue
        units = [u for u in by_unit if _under(u, uid)]
        if not units:
            problems.append(f"dòng {i}: không có bản ghi nào cho {uid}")
            continue
        base = {"loai": loai, "tu_ngay": row["tu_ngay"], "den_ngay": row["den_ngay"],
                "dieu_kien": row["dieu_kien"], "can_cu": row["can_cu"]}
        hit = 0
        for u in units:
            recs = by_unit[u]
            if loai == "gia_han":
                if recs[-1]["valid_to"] is not None:
                    recs[-1]["hl_ngoai_le"].append(dict(base, vai_tro="gia_han"))
                    hit += 1
            elif loai == "hoan_ap_dung":
                before = [r for r in recs if r["valid_from"] < row["tu_ngay"]]
                if not before:
                    continue
                new = before[-1]
                new["hl_ngoai_le"].append(dict(base, vai_tro="moi"))
                hit += 1
                for old in recs:
                    if old["valid_to"] == new["valid_from"]:
                        old["hl_ngoai_le"].append(dict(base, vai_tro="cu"))
            else:
                for r in recs:
                    r["hl_ngoai_le"].append(dict(base, vai_tro="moc"))
                hit += 1
        if not hit:
            problems.append(f"dòng {i} ({uid}): {loai} không áp được vào bản ghi nào")
    if problems:
        raise ValueError(f"{len(problems)} lỗi trong ngoại lệ hiệu lực:\n" + "\n".join(f"  - {p}" for p in problems))


def in_force_at(rec: dict, t: str) -> tuple[bool, str | None]:
    exs = rec.get("hl_ngoai_le") or []
    closed = rec["valid_to"] is not None and rec["valid_to"] <= t
    live = rec["valid_from"] <= t and not closed
    notes: list[str] = []
    for ex in exs:
        if closed and ex["vai_tro"] == "gia_han" and t < ex["den_ngay"]:
            live = True
            notes.append(ex["dieu_kien"])
        elif closed and ex["vai_tro"] == "cu" and t < ex["tu_ngay"]:
            live = True
            notes.append(ex["dieu_kien"])
    if not live:
        return False, None
    for ex in exs:
        if ex["vai_tro"] in ("moi", "moc") and rec["valid_from"] <= t < ex["tu_ngay"]:
            if ex["vai_tro"] == "moi" and not ex["dieu_kien"]:
                return False, None
            notes.append(ex["dieu_kien"])
    text = "; ".join(n for n in notes if n)
    return True, text or None
```

Run: `python -m pytest tests/test_validity.py -q` → PASS.

- [ ] **Step 3: Tạo `data/effective_exceptions.csv`**

Ghi đúng các dòng trong bảng trên (thứ tự giữ nguyên), `encoding="utf-8-sig"`, dùng `csv.DictWriter`. `ghi_chu` mỗi dòng: trích dẫn ngắn (≤ 200 ký tự) của đơn vị căn cứ, lấy từ `legal_units_versioned.jsonl`.

- [ ] **Step 4: Gọi trong `step_apply`**

Import `attach_exceptions, in_force_at, load_exceptions`. Thêm `EXCEPTIONS = config.DATA / "effective_exceptions.csv"`. Sau `annotate_records`:

```python
    attach_exceptions(recs, load_exceptions(EXCEPTIONS))
```

Thay dòng đếm `live`:

```python
    live = sum(in_force_at(r, config.CUTOFF)[0] for r in recs)
    print(f"-> {VERSIONED.relative_to(config.ROOT)} ({len(recs)} bản ghi, {live} có hiệu lực tại {config.CUTOFF})")
```

- [ ] **Step 5: Cập nhật test toàn vẹn**

Trong `tests/test_processed_invariants.py`:
- Thay `_in_force` bằng `from lawproc.validity import in_force_at` và `def _in_force(r, t=T): return in_force_at(r, t)[0]`.
- Bỏ `FULLY_REPLACED`; trong `test_every_document_has_unit_in_force` bỏ phần xử lý riêng `tt_12_2025_bca` và thêm test:

```python
def test_tt12_in_force_only_through_extension(versioned):
    live = [r for r in versioned if r["doc_id"] == "tt_12_2025_bca" and _in_force(r)]
    assert live and all(any(e["vai_tro"] == "gia_han" for e in r["hl_ngoai_le"]) for r in live)


def test_exception_rows_give_expected_status_at_cutoff(versioned):
    for r in versioned:
        for e in r["hl_ngoai_le"]:
            ok, note = in_force_at(r, T)
            if e["vai_tro"] in ("gia_han", "cu") and T < (e["den_ngay"] or e["tu_ngay"]):
                assert ok, r["version_id"]
            if e["vai_tro"] == "moi" and T < e["tu_ngay"]:
                assert ok == bool(e["dieu_kien"]), r["version_id"]
            if e["vai_tro"] == "moc" and ok and r["valid_from"] <= T < e["tu_ngay"]:
                assert e["dieu_kien"] in note, r["version_id"]  # ok có thể False do một dòng hoan_ap_dung không điều kiện
```

- [ ] **Step 6: Chạy lại, kiểm tra**

Chạy `apply`. Run: `python -m pytest -q` → PASS.
In tại `2026-10-01`, với mọi `unit_id` trong `effective_exceptions.csv`: các phiên bản, `in_force_at` và điều kiện. Kiểm tra bằng mắt: TT 12 Điều 4 khoản 1–3 và Phụ lục II–VI có hiệu lực; `nd_168_2024:d20:k5:l` có hai bản cùng có hiệu lực kèm điều kiện; `tt_108_2026_bca:d4:k4` chưa có hiệu lực. Lưu bảng vào `<scratchpad>/exceptions_check.txt` cho Task 8.

- [ ] **Step 7: Commit**

```bash
git add src/lawproc/validity.py scripts/process_legal.py tests data/effective_exceptions.csv data/processed
git commit -m "Add reviewed effective-date exceptions and a shared in-force filter"
```

---

### Task 8: Báo cáo xử lý và bảng kiểm tra chất lượng (L8)

**Files:**
- Modify: `data/processed/PROCESSING_REPORT.md`, `docs/superpowers/followups/2026-10-09-legal-processing-followups.md`

**Interfaces:**
- Consumes: số liệu từ `data/processed/*` và các file tóm tắt trong scratchpad của Task 5, 6, 7.

- [ ] **Step 1: Cập nhật số liệu trong `PROCESSING_REPORT.md`**

Mọi con số lấy bằng lệnh từ file đầu ra (không ước lượng). Cập nhật: số văn bản (33, gồm `qcvn_41_2024`), bảng cách trích, bảng số đơn vị theo cấp, số bản ghi có phiên bản, số bản ghi có hiệu lực tại 2026-10-01 (theo `in_force_at`). Sửa đoạn về QCVN 41 thành: đã tách thành văn bản riêng, 84 Điều, khoản dạng "3.1."; phụ lục A–… thuộc `qcvn_41_2024`. Thêm mục "Trường mới trên bản ghi có phiên bản": `phan`, `noi_dung_doi`, `loai_phu_luc`, `ty_le_am_tiet_loi`, `chat_luong`, `hl_ngoai_le`, và cách dùng `lawproc.validity.in_force_at`.

- [ ] **Step 2: Thêm mục "Kiểm tra chất lượng"**

Bảng Markdown với cột `Kiểm tra | Phát hiện | Cách xử lý | Kết quả`, đủ các dòng sau (điền số thật):

| Kiểm tra | Nguồn số liệu |
|---|---|
| Danh tính văn bản (số hiệu, trích yếu) | `identity_report.csv`: số văn bản ok / tổng |
| Văn bản tải nhầm do trùng số hiệu | `data/COLLECTION_LOG.md` (Bộ luật Dân sự) |
| Điều bị thiếu khi ghép | `assembly_report.csv` (`missing_dieu`; VBHN BLHS thiếu Điều 90–107 là phần đã bãi bỏ) |
| Lỗi OCR đã sửa tay | số dòng `data/ocr_corrections.csv` theo văn bản |
| OCR lại ở 400 dpi | số trang được thay, tỷ lệ âm tiết lỗi trước/sau (Task 5) |
| Chữ lặp do bảng lồng | 5 văn bản (Task 1) |
| Phần kết lẫn vào Điều cuối | số đơn vị `ket_thuc` trước (2) và sau |
| Mục lục bị nhận là phụ lục | 12 phụ lục rỗng QCVN 41 → 0 phụ lục rỗng |
| Nhãn điểm có chữ số | 1 dòng sửa đổi (điểm k1 khoản 4 Điều 41 NĐ 168) |
| Ngày hiệu lực ngoại lệ | số dòng `effective_exceptions.csv` theo loại |
| Phiên bản không đổi nội dung | số bản ghi `noi_dung_doi = false` |
| Phụ lục mẫu biểu | số phụ lục `mau_bieu` / tổng phụ lục |
| Chất lượng chữ kém còn lại | số bản ghi `chat_luong = kem`, liệt kê đơn vị |
| Trùng mã đơn vị | 0 `unit_id` có hậu tố `#` trong bản ghi có hiệu lực |
| Chồng phiên bản | 0 (test `test_no_overlapping_versions_per_unit`) |

Thêm mục "Hạn chế" ngắn: chỉ số âm tiết lỗi không bắt lỗi dấu; các đơn vị `chat_luong = kem`; phụ lục chỉ còn hiệu lực một phần (TT 12 Phụ lục IV–VI) được gia hạn cả đơn vị kèm điều kiện; mỗi dòng sửa đổi chỉ có một ngày hiệu lực.

- [ ] **Step 3: Cập nhật file việc tồn đọng**

Trong `docs/superpowers/followups/2026-10-09-legal-processing-followups.md`, đánh dấu "(đã xử lý ở đợt làm sạch 2, xem PROCESSING_REPORT.md)" cho: ngoại lệ ngày hiệu lực; 12 phụ lục rỗng QCVN 41 (phần chia nhỏ phụ lục dài vẫn còn, để bước cắt đoạn); dòng chữ ký; bảng lồng; OCR phụ lục (ghi phần còn lại); 184 phiên bản giống hệt; nhãn `k1)`; cache OCR theo sha256 và dpi; lỗi Tesseract kèm stderr. Giữ nguyên các mục chưa làm.

- [ ] **Step 4: Kiểm tra cuối và commit**

Run: `python -m pytest -q` → PASS. Chạy lại `assemble`, `parse`, `effective`, `amendments`, `apply`; `git status --short data/processed` chỉ còn `PROCESSING_REPORT.md` (đã sửa tay ở Step 1–2).

```bash
git add data/processed/PROCESSING_REPORT.md docs/superpowers/followups/2026-10-09-legal-processing-followups.md
git commit -m "Report cleanup round 2 with a data quality table"
```
