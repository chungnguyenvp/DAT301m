# EDA kho văn bản luật Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Làm EDA phần A (E1–E10 trong spec) trên dữ liệu đã làm sạch, ra notebook đã chạy, bảng "phát hiện → hành động" và ma trận đề cho bộ eval.

**Architecture:** Phần tính toán có logic (rút mức phạt, điểm trừ, tham chiếu, đếm token, gần trùng, phân bổ ma trận đề) nằm trong `src/lawproc/eda.py`, có test. Notebook viết dạng nguồn `# %%` (`notebooks/01_eda_kho_luat.py`, dễ xem diff), đổi thành `.ipynb` bằng `scripts/build_notebook.py`, chạy bằng `jupyter nbconvert --execute` và commit kèm kết quả. Hình lưu ở `reports/eda/figures/`.

**Tech Stack:** Python 3.13, pandas 3, matplotlib, scikit-learn (TF-IDF), tokenizers (Hugging Face), pyvi (tách từ), nbformat/nbconvert.

**Spec:** `docs/superpowers/specs/2026-10-09-cleanup-and-eda-design.md` (mục 4, 5).

**Điều kiện bắt đầu:** kế hoạch `docs/superpowers/plans/2026-10-09-cleanup-round2.md` đã xong và gộp vào `main`. Kế hoạch này dùng `lawproc.validity.in_force_at`, `lawproc.structure.is_closing_line`, `config.DERIVED_DOCS` và các trường `noi_dung_doi`, `loai_phu_luc`, `ty_le_am_tiet_loi`, `chat_luong`, `hl_ngoai_le` của `legal_units_versioned.jsonl`.

## Global Constraints

- Mọi lệnh chạy từ thư mục gốc repo `D:\Dowload\1.Chuyên Ngành\kì 7\DAT301_NEW\traffic-law-qa`. Test: `python -m pytest -q`.
- Không sửa `data/raw/` và không sửa đầu ra trong `data/processed/` (EDA chỉ đọc).
- Commit không ghi Claude là tác giả hay đồng tác giả: không thêm dòng `Co-Authored-By` nào vào nội dung commit.
- Thời điểm phân tích T = `config.CUTOFF` ("2026-10-01"); "có hiệu lực" luôn tính bằng `in_force_at(record, T)[0]`.
- Cài thư viện và tải tokenizer chỉ sau khi người dùng đồng ý danh sách (tên, nguồn, dung lượng). Tokenizer lưu trong `tools/tokenizers/` (đã nằm trong `.gitignore` qua `tools/`).
- Nhận xét trong notebook và `findings.md` viết tiếng Việt; mọi con số trong nhận xét lấy từ kết quả notebook, không ước lượng.
- Notebook chạy lại từ đầu không lỗi và cho cùng số liệu.

## File Structure

| File | Việc |
|---|---|
| `requirements.txt` (mới) | Phiên bản thư viện |
| `src/lawproc/config.py` | `TOKENIZERS` |
| `src/lawproc/eda.py` (mới) | Hàm tính toán cho EDA |
| `tests/test_eda.py` (mới) | Test cho `eda.py` |
| `scripts/build_notebook.py` (mới), `tests/test_build_notebook.py` (mới) | Đổi nguồn `# %%` thành `.ipynb` |
| `notebooks/01_eda_kho_luat.py` (mới), `notebooks/01_eda_kho_luat.ipynb` (sinh ra, commit kèm kết quả) | Notebook EDA |
| `reports/eda/figures/*.png` (sinh ra) | Hình |
| `reports/eda/findings.md` (mới) | Bảng phát hiện → hành động |
| `data/eval/eval_matrix.csv` (sinh ra) | Ma trận đề |

---

### Task 1: Môi trường và tokenizer (controller tự làm, có điểm dừng duyệt)

Task này cần người dùng đồng ý nên controller làm trực tiếp, không giao subagent.

**Files:**
- Create: `requirements.txt`
- Modify: `src/lawproc/config.py`

**Interfaces:**
- Produces: `config.TOKENIZERS = {"qwen": ROOT / "tools/tokenizers/qwen3.5-9b/tokenizer.json", "bge_m3": ROOT / "tools/tokenizers/bge-m3/tokenizer.json"}`.

- [ ] **Step 1: Xác minh nguồn tokenizer**

Gửi HEAD (theo chuyển hướng) để lấy dung lượng:
- `https://huggingface.co/BAAI/bge-m3/resolve/main/tokenizer.json`
- `https://huggingface.co/Qwen/Qwen3.5-9B/resolve/main/tokenizer.json`

Nếu repo Qwen trả 404, tìm repo chính thức của Qwen3.5-9B trên huggingface.co (tổ chức `Qwen`) và dùng `tokenizer.json` của repo đó. Không dùng bản của bên thứ ba.

- [ ] **Step 2: ĐIỂM DỪNG DUYỆT**

Đưa người dùng: (a) lệnh cài `python -m pip install matplotlib nbconvert nbclient scikit-learn tokenizers pyvi` từ PyPI; (b) hai file tokenizer kèm URL và dung lượng từ Step 1. Chờ đồng ý.

- [ ] **Step 3: Cài và tải**

Chạy lệnh cài. Tải hai file vào `tools/tokenizers/qwen3.5-9b/tokenizer.json` và `tools/tokenizers/bge-m3/tokenizer.json`. Ghi sha256 của hai file (dùng ở notebook, mục E3).
Kiểm tra: `python -c "import matplotlib, nbconvert, sklearn, tokenizers, pyvi; from pyvi import ViTokenizer; print(ViTokenizer.tokenize('người điều khiển xe mô tô'))"` in ra chuỗi có dấu `_` nối từ ghép.

- [ ] **Step 4: `requirements.txt` và `config.py`**

`requirements.txt`: mỗi dòng `ten==phien_ban` cho `pandas`, `numpy`, `python-docx`, `pymupdf`, `pywin32`, `pytest`, `ipykernel`, `matplotlib`, `nbconvert`, `nbclient`, `nbformat`, `scikit-learn`, `tokenizers`, `pyvi`, phiên bản lấy bằng `python -m pip show <ten>`. Dòng đầu là comment `# Python 3.13; Tesseract 5.4 cài riêng (xem data/COLLECTION_LOG.md)`.

`config.py`, thêm:

```python
# Tokenizer (chỉ file tokenizer.json, không có trọng số mô hình) để đếm token; tải về tools/tokenizers/
TOKENIZERS = {
    "qwen": ROOT / "tools/tokenizers/qwen3.5-9b/tokenizer.json",
    "bge_m3": ROOT / "tools/tokenizers/bge-m3/tokenizer.json",
}
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt src/lawproc/config.py
git commit -m "Pin library versions and add tokenizer paths for EDA"
```

---

### Task 2: Hàm tính toán `eda.py`

**Files:**
- Create: `src/lawproc/eda.py`, `tests/test_eda.py`

**Interfaces:**
- Consumes: `config.TOKENIZERS`.
- Produces:
  - `money(s: str) -> int` ("1.000.000" → 1000000)
  - `extract_fine(text: str) -> tuple[int, int] | None` — khung phạt đầu tiên "Phạt tiền từ X đồng đến Y đồng" (mức cho cá nhân khi văn bản ghi cả cá nhân và tổ chức).
  - `extract_points(text: str) -> int | None` — số điểm trong "trừ điểm giấy phép lái xe N điểm".
  - `vehicle_group(title: str) -> str` — nhóm phương tiện suy từ tiêu đề Điều.
  - `find_references(text: str) -> list[dict]` — mỗi phần tử `{"diem", "khoan", "dieu", "loai"}`, `loai` ∈ `noi_bo`, `ngoai`.
  - `count_words(text: str) -> int`
  - `count_tokens(texts: Sequence[str], tokenizer_path: Path) -> list[int]`
  - `near_duplicates(texts: Sequence[str], groups: Sequence[str], threshold: float = 0.9, block: int = 500) -> list[tuple[int, int, float]]` — cặp (i, j, cosine) với i < j, khác nhóm.
  - `allocate(weights: dict[str, float], total: int, floor: int = 0) -> dict[str, int]` — chia theo phần dư lớn nhất, mỗi khóa tối thiểu `floor`.
  - `eval_matrix(group_counts: dict[str, int], docs_by_group: dict[str, list[str]], total: int = 150, floor: int = 5) -> list[dict]` — dòng `{"chu_de", "van_ban", "loai_cau", "so_cau", "ghi_chu"}`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_eda.py`:

```python
import pytest

from lawproc import config, eda


def test_money_and_fine():
    assert eda.money("1.000.000") == 1_000_000
    text = ("Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe thực hiện "
            "một trong các hành vi vi phạm sau đây:")
    assert eda.extract_fine(text) == (800_000, 1_000_000)
    both = ("Phạt tiền từ 5.000.000 đồng đến 6.000.000 đồng đối với cá nhân, từ 10.000.000 đồng đến "
            "12.000.000 đồng đối với tổ chức là chủ xe")
    assert eda.extract_fine(both) == (5_000_000, 6_000_000)
    assert eda.extract_fine("Tịch thu phương tiện") is None


def test_extract_points():
    text = "Thực hiện hành vi quy định tại điểm a khoản 9 Điều này bị trừ điểm giấy phép lái xe 04 điểm;"
    assert eda.extract_points(text) == 4
    assert eda.extract_points("bị tước quyền sử dụng giấy phép lái xe") is None


def test_vehicle_group():
    assert eda.vehicle_group("Xử phạt người điều khiển xe ô tô, xe chở người bốn bánh có gắn động cơ vi phạm "
                             "quy tắc giao thông đường bộ") == "Ô tô"
    assert eda.vehicle_group("Xử phạt người điều khiển xe mô tô, xe gắn máy, các loại xe tương tự xe mô tô") \
        == "Mô tô, xe gắn máy"
    assert eda.vehicle_group("Xử phạt người điều khiển xe máy chuyên dùng vi phạm quy tắc") == "Xe máy chuyên dùng"
    assert eda.vehicle_group("Xử phạt người điều khiển xe đạp, xe đạp máy, xe thô sơ") == "Xe đạp, xe thô sơ"
    assert eda.vehicle_group("Xử phạt người đi bộ vi phạm quy tắc giao thông đường bộ") == "Người đi bộ"
    assert eda.vehicle_group("Xử phạt các hành vi vi phạm khác") == "Khác"


def test_find_references():
    refs = eda.find_references("theo quy định tại điểm a khoản 2 Điều 6 của Nghị định này và Điều 260 của Bộ luật Hình sự")
    assert refs == [{"diem": "a", "khoan": "2", "dieu": "6", "loai": "noi_bo"},
                    {"diem": None, "khoan": None, "dieu": "260", "loai": "ngoai"}]
    assert eda.find_references("khoản 3 Điều 10") == [{"diem": None, "khoan": "3", "dieu": "10", "loai": "noi_bo"}]


def test_count_words():
    assert eda.count_words("Người điều khiển xe") == 4


@pytest.mark.skipif(not config.TOKENIZERS["bge_m3"].exists(), reason="chưa tải tokenizer bge-m3")
def test_count_tokens():
    n = eda.count_tokens(["Người điều khiển xe mô tô", ""], config.TOKENIZERS["bge_m3"])
    assert n[0] > 0 and n[1] == 0


def test_near_duplicates_only_across_groups():
    texts = ["người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông",
             "người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông.",
             "quy định về lệ phí đăng ký xe và cấp biển số"]
    pairs = eda.near_duplicates(texts, ["a", "b", "c"], threshold=0.9)
    assert [(i, j) for i, j, _ in pairs] == [(0, 1)]
    assert eda.near_duplicates(texts, ["a", "a", "c"], threshold=0.9) == []


def test_allocate_largest_remainder_with_floor():
    assert eda.allocate({"a": 1, "b": 1, "c": 2}, 10, floor=1) == {"a": 3, "b": 3, "c": 4}
    with pytest.raises(ValueError):
        eda.allocate({"a": 1, "b": 1}, 3, floor=2)


def test_eval_matrix_totals():
    rows = eda.eval_matrix({"Xử phạt": 400, "Lệ phí": 10, "GPLX": 100},
                           {"Xử phạt": ["nd_168_2024"], "Lệ phí": ["nd_10_2022"], "GPLX": ["tt_108_2026_bca"]})
    assert sum(r["so_cau"] for r in rows) == 150
    per = {}
    for r in rows:
        per[r["chu_de"]] = per.get(r["chu_de"], 0) + r["so_cau"]
    assert min(per.values()) >= 5
    assert any(r["chu_de"] == "Xử phạt" and r["loai_cau"] == "mức phạt" for r in rows)
    assert all(r["so_cau"] > 0 for r in rows)
```

Run: `python -m pytest tests/test_eda.py -q` → FAIL (module chưa có).

- [ ] **Step 2: Viết `src/lawproc/eda.py`**

```python
"""Hàm tính toán cho EDA kho văn bản luật (notebooks/01_eda_kho_luat.py)."""
import math
import re
from collections.abc import Sequence
from pathlib import Path

FINE = re.compile(r"[Pp]hạt tiền từ ([\d.]+) đồng đến ([\d.]+) đồng")
POINTS = re.compile(r"trừ điểm giấy phép lái xe (\d{1,2}) điểm")
REF = re.compile(
    r"(?:điểm\s+([a-zđ]{1,2}\d?)\s+)?(?:khoản\s+(\d+[a-zđ]?)\s+)?Điều\s+(\d+[a-zđ]?)"
    r"(?:\s+(?:của\s+)?(Bộ luật|Luật|Nghị định|Thông tư|Quy chuẩn)(\s+này)?)?"
)
WORD = re.compile(r"\w+")
# (từ khóa trong tiêu đề Điều, nhóm phương tiện), xét theo thứ tự
VEHICLE_RULES = (
    ("xe ô tô", "Ô tô"),
    ("xe mô tô", "Mô tô, xe gắn máy"),
    ("xe gắn máy", "Mô tô, xe gắn máy"),
    ("xe máy chuyên dùng", "Xe máy chuyên dùng"),
    ("xe đạp", "Xe đạp, xe thô sơ"),
    ("xe thô sơ", "Xe đạp, xe thô sơ"),
    ("người đi bộ", "Người đi bộ"),
)
# Ma trận đề: trọng số nhóm người dân hỏi nhiều; tỷ lệ loại câu theo nhóm
IMPORTANCE = {"Xử phạt": 1.5, "GPLX": 1.5, "Đăng ký xe": 1.5}
LOAI_SPLIT = {
    "Xử phạt": {"mức phạt": 5, "hành vi cấm": 2, "tình huống": 2, "chung": 1},
    "Luật lõi": {"chung": 2, "định nghĩa": 2, "hành vi cấm": 2, "tình huống": 2},
    "Biển báo": {"định nghĩa": 2, "chung": 1, "tình huống": 1},
    "Tốc độ": {"chung": 1, "tình huống": 1},
    "Lệ phí": {"chung": 1, "thủ tục": 1},
    "Tai nạn": {"chung": 1, "tình huống": 2, "mức phạt": 1},
}
DEFAULT_SPLIT = {"chung": 1, "thủ tục": 2, "tình huống": 1}


def money(s: str) -> int:
    return int(s.replace(".", ""))


def extract_fine(text: str) -> tuple[int, int] | None:
    m = FINE.search(text)
    return (money(m.group(1)), money(m.group(2))) if m else None


def extract_points(text: str) -> int | None:
    m = POINTS.search(text)
    return int(m.group(1)) if m else None


def vehicle_group(title: str) -> str:
    t = title.lower()
    return next((g for key, g in VEHICLE_RULES if key in t), "Khác")


def find_references(text: str) -> list[dict]:
    out = []
    for m in REF.finditer(text):
        external = bool(m.group(4)) and not m.group(5)
        out.append({"diem": m.group(1), "khoan": m.group(2), "dieu": m.group(3),
                    "loai": "ngoai" if external else "noi_bo"})
    return out


def count_words(text: str) -> int:
    return len(WORD.findall(text))


def count_tokens(texts: Sequence[str], tokenizer_path: Path) -> list[int]:
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(tokenizer_path))
    return [len(e.ids) for e in tok.encode_batch(list(texts), add_special_tokens=False)]


def near_duplicates(texts: Sequence[str], groups: Sequence[str], threshold: float = 0.9,
                    block: int = 500) -> list[tuple[int, int, float]]:
    """Cặp đơn vị gần trùng (cosine TF-IDF n-gram 4 ký tự >= threshold) thuộc hai nhóm khác nhau."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    x = TfidfVectorizer(analyzer="char_wb", ngram_range=(4, 4), sublinear_tf=True).fit_transform(list(texts))
    pairs: list[tuple[int, int, float]] = []
    for start in range(0, x.shape[0], block):
        sim = (x[start:start + block] @ x.T).tocoo()
        keep = sim.data >= threshold
        for bi, j, s in zip(sim.row[keep], sim.col[keep], sim.data[keep]):
            i = start + int(bi)
            if i < j and groups[i] != groups[j]:
                pairs.append((i, int(j), round(float(s), 4)))
    return sorted(pairs)


def allocate(weights: dict[str, float], total: int, floor: int = 0) -> dict[str, int]:
    keys = sorted(weights)
    rest = total - floor * len(keys)
    if rest < 0:
        raise ValueError(f"total {total} nhỏ hơn floor {floor} × {len(keys)} nhóm")
    s = sum(weights.values())
    raw = {k: rest * weights[k] / s for k in keys}
    out = {k: floor + math.floor(raw[k]) for k in keys}
    left = total - sum(out.values())
    for k in sorted(keys, key=lambda k: (-(raw[k] - math.floor(raw[k])), k))[:left]:
        out[k] += 1
    return out


def eval_matrix(group_counts: dict[str, int], docs_by_group: dict[str, list[str]], total: int = 150,
                floor: int = 5) -> list[dict]:
    """Phân bổ câu hỏi thủ công: theo √(số Điều trong phạm vi) × trọng số nhóm, mỗi nhóm tối thiểu floor câu."""
    weights = {g: math.sqrt(n) * IMPORTANCE.get(g, 1.0) for g, n in group_counts.items() if n > 0}
    per_group = allocate(weights, total, floor)
    rows = []
    for g in sorted(per_group):
        for loai, n in allocate(LOAI_SPLIT.get(g, DEFAULT_SPLIT), per_group[g]).items():
            if n:
                rows.append({"chu_de": g, "van_ban": " ".join(sorted(docs_by_group.get(g, []))),
                             "loai_cau": loai, "so_cau": n, "ghi_chu": ""})
    return rows
```

- [ ] **Step 3: Chạy test**

Run: `python -m pytest tests/test_eda.py -q` → PASS (test tokenizer chạy khi đã có file).

- [ ] **Step 4: Kiểm tra trên dữ liệu thật**

Chạy nhanh trong scratchpad: `extract_fine` trên mọi khoản có hiệu lực của `nd_168_2024` (in số khoản có mức phạt; phải trên 150); `vehicle_group` trên mọi tiêu đề Điều của `nd_168_2024` có mức phạt (in bảng tiêu đề → nhóm, đọc qua để chắc từ khóa khớp; nếu một Điều về ô tô rơi vào "Khác" vì tiêu đề viết khác, thêm từ khóa vào `VEHICLE_RULES` kèm test).

- [ ] **Step 5: Commit**

```bash
git add src/lawproc/eda.py tests/test_eda.py
git commit -m "Add EDA helpers: fines, points, references, tokens, near-duplicates, eval matrix"
```

---

### Task 3: Notebook EDA

**Files:**
- Create: `scripts/build_notebook.py`, `tests/test_build_notebook.py`, `notebooks/01_eda_kho_luat.py`
- Create (sinh ra): `notebooks/01_eda_kho_luat.ipynb`, `reports/eda/figures/*.png`, `data/eval/eval_matrix.csv`

**Interfaces:**
- Consumes: mọi hàm của `eda.py`; `validity.in_force_at`; `structure.is_closing_line`; `config.DERIVED_DOCS`, `config.AMENDING_DOCS`, `config.TOKENIZERS`, `config.CUTOFF`.
- Produces: `scripts/build_notebook.py SRC` ghi `SRC` với đuôi `.ipynb`; hàm `cells_from_source(src: str) -> list` (cell nbformat v4).

- [ ] **Step 1: Test thất bại cho bộ đổi notebook**

`tests/test_build_notebook.py`:

```python
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_notebook.py"


def _mod():
    spec = importlib.util.spec_from_file_location("build_notebook", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cells_from_source():
    src = "# %% [markdown]\n# # Tiêu đề\n# Đoạn văn\n\n# %%\nx = 1\n\n# %%\n\n"
    cells = _mod().cells_from_source(src)
    assert [c.cell_type for c in cells] == ["markdown", "code"]
    assert cells[0].source == "# Tiêu đề\nĐoạn văn"
    assert cells[1].source == "x = 1"
```

Run: `python -m pytest tests/test_build_notebook.py -q` → FAIL.

- [ ] **Step 2: Viết `scripts/build_notebook.py`**

```python
"""Đổi nguồn notebook dạng "# %%" thành .ipynb: python scripts/build_notebook.py notebooks/01_eda_kho_luat.py"""
import sys
from pathlib import Path

import nbformat


def cells_from_source(src: str) -> list:
    blocks: list[tuple[str, list[str]]] = []
    for line in src.splitlines():
        if line.startswith("# %%"):
            blocks.append(("md" if "[markdown]" in line else "code", []))
        elif blocks:
            blocks[-1][1].append(line)
    cells = []
    for kind, lines in blocks:
        body = "\n".join(lines).strip("\n")
        if kind == "md":
            text = "\n".join(x[2:] if x.startswith("# ") else x.lstrip("#") for x in body.splitlines())
            cells.append(nbformat.v4.new_markdown_cell(text))
        elif body.strip():
            cells.append(nbformat.v4.new_code_cell(body))
    return cells


if __name__ == "__main__":
    src = Path(sys.argv[1])
    nb = nbformat.v4.new_notebook(cells=cells_from_source(src.read_text(encoding="utf-8")),
                                  metadata={"kernelspec": {"name": "python3", "display_name": "Python 3",
                                                           "language": "python"}})
    nbformat.write(nb, src.with_suffix(".ipynb"))
    print(f"-> {src.with_suffix('.ipynb')}")
```

Run: `python -m pytest tests/test_build_notebook.py -q` → PASS.

- [ ] **Step 3: Viết `notebooks/01_eda_kho_luat.py`**

Viết đúng các ô dưới đây. Ô "Phát hiện → hành động" để trống nội dung ở lần chạy đầu (chỉ có tiêu đề), điền ở Step 5.

````python
# %% [markdown]
# # EDA kho văn bản luật giao thông đường bộ
#
# Phần A của mục 6 bản thiết kế dự án. Dữ liệu: `data/processed/legal_units_versioned.jsonl` (sau đợt làm sạch 2).
# Thời điểm phân tích T = 01/10/2026; "có hiệu lực" tính bằng `lawproc.validity.in_force_at` (có xét ngoại lệ).
# Mỗi phân tích kết thúc bằng **Phát hiện → hành động**; bảng tổng hợp ở `reports/eda/findings.md`.

# %%
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

import hashlib

import matplotlib.pyplot as plt
import pandas as pd

from lawproc import config, eda
from lawproc.structure import is_closing_line
from lawproc.validity import in_force_at

T = config.CUTOFF
FIG = ROOT / "reports" / "eda" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
pd.set_option("display.max_colwidth", 120)
pd.set_option("display.max_rows", 80)


def save(fig, name):
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.show()


def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))

# %%
recs = [json.loads(x) for x in (config.PROCESSED / "legal_units_versioned.jsonl").open(encoding="utf-8")]
nhom = {r["doc_id"]: r["nhom"] for r in read_csv(config.MANIFEST)}
nhom.update({k: v["nhom"] for k, v in config.DERIVED_DOCS.items()})
method = {r["doc_id"]: r["method"] for r in read_csv(config.PROCESSED / "assembly_report.csv")}
for r in recs:
    r["in_force"], r["dieu_kien_hl"] = in_force_at(r, T)
    r["nhom"] = nhom[r["doc_id"]]
    r["van_ban_sua_doi"] = r["doc_id"] in config.AMENDING_DOCS
df = pd.DataFrame(recs)
live = df[df["in_force"]].reset_index(drop=True)
print(f"{len(df)} bản ghi, {df['doc_id'].nunique()} văn bản; {len(live)} bản ghi có hiệu lực tại {T}; "
      f"{int(live['dieu_kien_hl'].notna().sum())} bản ghi có hiệu lực kèm điều kiện")

# %% [markdown]
# ## E1. Quy mô kho

# %%
e1_doc = (live.groupby(["nhom", "doc_id"])["level"].value_counts().unstack(fill_value=0)
          .reindex(columns=["dieu", "khoan", "diem", "phu_luc"], fill_value=0))
e1_doc["tong"] = e1_doc.sum(axis=1)
e1_doc.sort_values("tong", ascending=False)

# %%
e1_nhom = live.groupby("nhom").agg(van_ban=("doc_id", "nunique"), don_vi=("unit_id", "size")).sort_values("don_vi")
fig, ax = plt.subplots(figsize=(8, 5))
e1_nhom["don_vi"].plot.barh(ax=ax)
ax.set_xlabel(f"Số đơn vị có hiệu lực tại {T}")
ax.set_ylabel("")
ax.set_title("E1. Quy mô theo nhóm chủ đề")
save(fig, "e1_quy_mo_nhom.png")
e1_nhom

# %%
sd = live[live["van_ban_sua_doi"]]
print(f"Văn bản sửa đổi: {sd['doc_id'].nunique()} văn bản, {len(sd)} đơn vị của chính văn bản đó "
      f"(phần lớn là câu chỉ dẫn 'sửa đổi, bổ sung…'; nội dung mới đã được áp vào văn bản gốc)")

# %% [markdown]
# **Phát hiện → hành động (E1):**

# %% [markdown]
# ## E2. Phạm vi thực của BLDS 2015 và BLHS (VBHN 135)
#
# Đề xuất phạm vi: BLDS Chương XX (Điều 584–608, bồi thường thiệt hại ngoài hợp đồng, có Điều 601 nguồn nguy hiểm cao độ);
# BLHS Điều 260–266 (các tội về giao thông đường bộ). Bảng tiêu đề bên dưới để kiểm tra lại khoảng Điều.

# %%
SCOPE = {"blds_2015": (584, 608), "vbhn_135_2025_blhs": (260, 266)}


def in_scope(doc_id, dieu):
    rng = SCOPE.get(doc_id)
    if not rng:
        return True
    m = re.match(r"\d+", dieu or "")
    return bool(m) and rng[0] <= int(m.group()) <= rng[1]


live["trong_pham_vi"] = [in_scope(d, x) for d, x in zip(live["doc_id"], live["dieu"])]
big = live[live["doc_id"].isin(SCOPE)]
print(f"BLDS + BLHS: {len(big)} / {len(live)} đơn vị có hiệu lực ({len(big) / len(live):.1%}); "
      f"trong phạm vi đề xuất: {int(big['trong_pham_vi'].sum())}")
e2 = big.groupby(["doc_id", "trong_pham_vi"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(7, 3))
e2.plot.barh(stacked=True, ax=ax)
ax.set_title("E2. Đơn vị BLDS, BLHS trong và ngoài phạm vi đề xuất")
save(fig, "e2_pham_vi_blds_blhs.png")
e2

# %%
check = big[(big["level"] == "dieu")]
check = check[[(SCOPE[d][0] - 5) <= int(re.match(r"\d+", x).group()) <= (SCOPE[d][1] + 5)
               for d, x in zip(check["doc_id"], check["dieu"])]]
check[["doc_id", "dieu", "title", "trong_pham_vi"]]

# %% [markdown]
# **Phát hiện → hành động (E2):**

# %% [markdown]
# ## E3. Độ dài đơn vị (từ, token Qwen3.5-9B, token bge-m3)

# %%
for k, p in config.TOKENIZERS.items():
    print(k, p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
texts = live["text"].tolist()
live["so_tu"] = [eda.count_words(t) for t in texts]
live["tok_qwen"] = eda.count_tokens(texts, config.TOKENIZERS["qwen"])
live["tok_bge"] = eda.count_tokens(texts, config.TOKENIZERS["bge_m3"])
lv = live[live["level"].isin(["dieu", "khoan", "diem", "phu_luc"])]
cols = ["so_tu", "tok_qwen", "tok_bge"]
e3 = lv.groupby("level")[cols].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0)
e3

# %%
# Ứng viên cắt đoạn theo Khoản: nội dung khoản + mọi điểm của khoản đó
diem = live[live["level"] == "diem"].copy()
diem["khoan_id"] = diem["unit_id"].str.rsplit(":", n=1).str[0]
extra = diem.groupby("khoan_id")["text"].agg("\n".join)
kh = live[live["level"] == "khoan"].set_index("unit_id")
kh_text = (kh["text"] + "\n" + extra.reindex(kh.index).fillna("")).str.strip()
kh_tok = pd.Series(eda.count_tokens(kh_text.tolist(), config.TOKENIZERS["bge_m3"]), index=kh.index)
print(kh_tok.describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0))
for lim in (256, 512, 1024, 8192):
    print(f"khoản + điểm > {lim} token bge-m3: {int((kh_tok > lim).sum())}")
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(kh_tok.clip(lower=1), bins=[2 ** i for i in range(0, 15)])
ax.set_xscale("log", base=2)
ax.set_xlabel("Số token bge-m3 (khoản kèm các điểm)")
ax.set_ylabel("Số khoản")
ax.set_title("E3. Độ dài ứng viên đoạn theo Khoản")
save(fig, "e3_do_dai_khoan.png")

# %%
print("Đơn vị dài nhất (token bge-m3):")
display(live.nlargest(15, "tok_bge")[["unit_id", "level", "loai_phu_luc", "so_tu", "tok_bge"]])
short = lv[lv["so_tu"] < 5]
print(f"Đơn vị dưới 5 từ: {len(short)}")
short["level"].value_counts()

# %% [markdown]
# **Phát hiện → hành động (E3):**

# %% [markdown]
# ## E4. Mức phạt NĐ 168/2024 (bản có hiệu lực tại T)

# %%
n168 = live[live["doc_id"] == "nd_168_2024"]
dieu_title = dict(zip(n168.loc[n168["level"] == "dieu", "dieu"], n168.loc[n168["level"] == "dieu", "title"]))
rows = []
for uid, dieu, text in zip(n168["unit_id"], n168["dieu"], n168["text"]):
    if ":k" not in uid or uid.count(":") != 2:
        continue
    f = eda.extract_fine(text)
    if f:
        n_hv = int(n168["unit_id"].str.startswith(uid + ":").sum())
        rows.append({"unit_id": uid, "dieu": dieu, "phuong_tien": eda.vehicle_group(dieu_title.get(dieu, "")),
                     "min": f[0], "max": f[1], "so_hanh_vi": max(n_hv, 1)})
fines = pd.DataFrame(rows)
e4 = fines.groupby("phuong_tien").agg(khung=("unit_id", "size"), hanh_vi=("so_hanh_vi", "sum"),
                                       min_thap_nhat=("min", "min"), max_cao_nhat=("max", "max"),
                                       max_trung_vi=("max", "median"))
print(f"{len(fines)} khung phạt, {int(fines['so_hanh_vi'].sum())} hành vi; mức từ {fines['min'].min():,} "
      f"đến {fines['max'].max():,} đồng")
e4

# %%
fig, ax = plt.subplots(figsize=(8, 4))
groups = sorted(fines["phuong_tien"].unique())
ax.boxplot([fines.loc[fines["phuong_tien"] == g, "max"] for g in groups], tick_labels=groups, vert=False)
ax.set_xscale("log")
ax.set_xlabel("Mức phạt tối đa của khung (đồng, thang log)")
ax.set_title("E4. Khung phạt NĐ 168 theo nhóm phương tiện")
save(fig, "e4_muc_phat.png")

# %%
pts = Counter(p for p in (eda.extract_points(t) for t in n168["text"]) if p)
fig, ax = plt.subplots(figsize=(5, 3))
ax.bar([str(k) for k in sorted(pts)], [pts[k] for k in sorted(pts)])
ax.set_xlabel("Số điểm GPLX bị trừ")
ax.set_ylabel("Số quy định")
ax.set_title("E4. Điểm trừ GPLX")
save(fig, "e4_tru_diem.png")
dict(sorted(pts.items()))

# %% [markdown]
# **Phát hiện → hành động (E4):**

# %% [markdown]
# ## E5. Sửa đổi, bổ sung, bãi bỏ

# %%
hl = {r["doc_id"]: r["hl_chot"] for r in read_csv(config.PROCESSED / "effective_dates.csv")}
ok = pd.DataFrame([r for r in read_csv(config.PROCESSED / "amendments_reviewed.csv") if r["status"] == "duyet"])
ok["ngay"] = [h or hl[a] for h, a in zip(ok["hl_rieng"], ok["amend_doc_id"])]
e5 = pd.crosstab(ok["target_doc_id"], ok["action"], margins=True)
fig, ax = plt.subplots(figsize=(8, 4))
e5.drop(index="All", columns="All").plot.barh(stacked=True, ax=ax)
ax.set_title("E5. Dòng sửa đổi đã duyệt theo văn bản đích")
save(fig, "e5_sua_doi.png")
e5

# %%
pd.crosstab(ok["amend_doc_id"], ok["ngay"])

# %%
amended = df[df["source_doc_id"] != df["doc_id"]]
print(f"{len(amended)} bản ghi sinh từ sửa đổi; {int((~amended['noi_dung_doi']).sum())} không đổi nội dung")
base_units = set(df.loc[df["source_doc_id"] == df["doc_id"], "unit_id"])
rq3 = amended[amended["noi_dung_doi"] & amended["level"].isin(["khoan", "diem"]) & amended["unit_id"].isin(base_units)]
print(f"Khoản/điểm có cả bản gốc và bản sửa khác nội dung (nguồn câu hỏi RQ3): {rq3['unit_id'].nunique()}")
rq3.groupby("doc_id")["unit_id"].nunique()

# %% [markdown]
# **Phát hiện → hành động (E5):**

# %% [markdown]
# ## E6. Dòng thời gian hiệu lực 2024–2029

# %%
docs = sorted(df["doc_id"].unique(), key=lambda d: hl[d])
end = {d: (None if df.loc[df["doc_id"] == d, "valid_to"].isna().any() else df.loc[df["doc_id"] == d, "valid_to"].max())
       for d in docs}
x0, x1 = pd.Timestamp("2024-01-01"), pd.Timestamp("2030-01-01")
fig, ax = plt.subplots(figsize=(10, 9))
for y, d in enumerate(docs):
    s = max(pd.Timestamp(hl[d]), x0)
    e = pd.Timestamp(end[d]) if end[d] else x1
    ax.plot([s, e], [y, y], lw=4, color="tab:blue" if end[d] is None else "tab:gray")
    for day in sorted(set(ok.loc[ok["target_doc_id"] == d, "ngay"])):
        ax.plot(pd.Timestamp(day), y, "o", color="tab:orange", ms=5)
    for day in sorted({ex["tu_ngay"] or ex["den_ngay"] for r in recs if r["doc_id"] == d
                       for ex in r["hl_ngoai_le"]}):
        ax.plot(pd.Timestamp(day), y, "D", color="tab:red", ms=5)
ax.axvline(pd.Timestamp(T), color="black", ls="--")
ax.set_yticks(range(len(docs)), docs, fontsize=7)
ax.set_xlim(x0, x1)
ax.set_title("E6. Hiệu lực văn bản (xanh: còn hiệu lực, xám: đã hết); cam: ngày sửa đổi; đỏ: mốc ngoại lệ; nét đứt: T")
save(fig, "e6_dong_thoi_gian.png")

# %%
fut = []
for r in recs:
    if r["valid_from"] > T:
        fut.append((r["valid_from"], r["doc_id"], "bắt đầu hiệu lực"))
    for ex in r["hl_ngoai_le"]:
        day = ex["tu_ngay"] or ex["den_ngay"]
        if day > T:
            fut.append((day, r["doc_id"], ex["loai"]))
pd.DataFrame(fut, columns=["ngay", "doc_id", "su_kien"]).value_counts().sort_index()

# %% [markdown]
# **Phát hiện → hành động (E6):**

# %% [markdown]
# ## E7. Từ vựng (tách từ bằng pyvi)

# %%
from pyvi import ViTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

STOP = ["của", "và", "các", "về", "đối_với", "với", "trong", "theo", "quy_định", "việc", "được", "này", "có", "là",
        "cho", "tại", "khi", "hoặc", "không", "phải", "từ", "đến", "những", "một", "do", "trường_hợp", "điều",
        "khoản", "điểm", "sau", "đây", "như", "thì", "trên", "người", "bằng"]
body = live[live["trong_pham_vi"] & (live["loai_phu_luc"] != "mau_bieu") & ~live["van_ban_sua_doi"]]
seg = {g: ViTokenizer.tokenize(" ".join(t)).lower() for g, t in body.groupby("nhom")["text"]}
vec = TfidfVectorizer(token_pattern=r"(?u)\b\w*[^\W\d_]\w*\b", stop_words=STOP, sublinear_tf=True)
X = vec.fit_transform(list(seg.values()))
terms = vec.get_feature_names_out()
top = {g: [terms[j].replace("_", " ") for j in X[i].toarray()[0].argsort()[::-1][:15]] for i, g in enumerate(seg)}
pd.DataFrame(top)

# %%
PAIRS = [("xe mô tô", r"xe máy(?! chuyên dùng)"), ("giấy phép lái xe", r"bằng lái"), ("nồng độ cồn", r"rượu bia|rượu, bia"),
         ("xe ô tô", r"xe hơi"), ("cảnh sát giao thông", r"\bcsgt\b"), ("đèn tín hiệu", r"đèn đỏ|đèn xanh"),
         ("tạm giữ phương tiện", r"giam xe|giữ xe"), ("mũ bảo hiểm", r"nón bảo hiểm")]
corpus = "\n".join(body["text"]).lower()
pd.DataFrame([{"phap_ly": a, "so_lan": corpus.count(a), "doi_thuong": b, "so_lan_doi_thuong": len(re.findall(b, corpus))}
              for a, b in PAIRS])

# %% [markdown]
# **Phát hiện → hành động (E7):**

# %% [markdown]
# ## E8. Đơn vị gần trùng giữa các văn bản

# %%
cand = live[(live["so_tu"] >= 30) & (live["loai_phu_luc"] != "mau_bieu") & live["trong_pham_vi"]
            & ~live["van_ban_sua_doi"]].reset_index(drop=True)
pairs = eda.near_duplicates(cand["text"].tolist(), cand["doc_id"].tolist(), threshold=0.9)
print(f"{len(cand)} đơn vị xét; {len(pairs)} cặp gần trùng (cosine ≥ 0,9) khác văn bản")
if pairs:
    e8 = pd.DataFrame([{"a": cand["unit_id"][i], "b": cand["unit_id"][j], "cos": s} for i, j, s in pairs])
    e8["cap"] = e8["a"].str.split(":").str[0] + " ~ " + e8["b"].str.split(":").str[0]
    display(e8["cap"].value_counts())
    display(e8.head(20))

# %% [markdown]
# **Phát hiện → hành động (E8):**

# %% [markdown]
# ## E9. Tham chiếu chéo

# %%
body9 = live[live["level"].isin(["dieu", "khoan", "diem"]) & ~live["van_ban_sua_doi"]]
refs = pd.DataFrame([{"unit_id": u, "doc_id": d, **ref} for u, d, t in zip(body9["unit_id"], body9["doc_id"], body9["text"])
                     for ref in eda.find_references(t)])
print(f"{len(refs)} tham chiếu; {refs['unit_id'].nunique()} / {len(body9)} đơn vị "
      f"({refs['unit_id'].nunique() / len(body9):.1%}) có ít nhất một tham chiếu")
display(refs["loai"].value_counts())
inner = refs[refs["loai"] == "noi_bo"]
target = inner["doc_id"] + ":d" + inner["dieu"] + inner["khoan"].fillna("").map(lambda k: f":k{k}" if k else "")
fig, ax = plt.subplots(figsize=(8, 5))
target.value_counts().head(15).sort_values().plot.barh(ax=ax)
ax.set_title("E9. Điều/khoản được dẫn nhiều nhất (trong cùng văn bản)")
save(fig, "e9_tham_chieu.png")

# %% [markdown]
# **Phát hiện → hành động (E9):**

# %% [markdown]
# ## E10. Chất lượng sau làm sạch

# %%
PUNCT = set(".,;:!?()[]{}\"'“”‘’/\\%&+-–—…|*#°§<>=_~^@$€₫·•")
odd = Counter(c for t in live["text"] for c in t if not (c.isalnum() or c.isspace() or c in PUNCT))
live["method"] = live["doc_id"].map(method)
e10 = {
    "Đơn vị rỗng (không tiêu đề, không nội dung)": int(((live["text"].str.strip() == "")
                                                       & (live["title"].str.strip() == "")).sum()),
    "Đơn vị có dòng phần kết": int(sum(any(is_closing_line(x) for x in t.splitlines())
                                        for t, lvl in zip(live["text"], live["level"]) if lvl in ("dieu", "khoan", "diem"))),
    "unit_id có hậu tố #": int(live["unit_id"].str.contains("#").sum()),
    "Bản ghi chat_luong = kem": int((live["chat_luong"] == "kem").sum()),
    "Ký tự lạ (tổng số lần)": sum(odd.values()),
}
display(pd.Series(e10))
display(live.groupby("method")["ty_le_am_tiet_loi"].describe(percentiles=[0.5, 0.9, 0.99]).round(4))
print("Ký tự lạ hay gặp:", odd.most_common(20))
fig, ax = plt.subplots(figsize=(7, 3))
for m, g in live.groupby("method"):
    ax.hist(g["ty_le_am_tiet_loi"], bins=50, range=(0, 0.5), histtype="step", label=m, density=True)
ax.set_yscale("log")
ax.set_xlabel("Tỷ lệ âm tiết lỗi")
ax.legend()
ax.set_title("E10. Chất lượng chữ theo cách trích")
save(fig, "e10_chat_luong.png")

# %% [markdown]
# **Phát hiện → hành động (E10):**

# %% [markdown]
# ## Ma trận đề cho bộ eval thủ công (~150 câu)
#
# Quy tắc: số câu mỗi nhóm tỷ lệ với √(số Điều có hiệu lực trong phạm vi, không tính văn bản sửa đổi và đề thi),
# nhân trọng số 1,5 cho Xử phạt, GPLX, Đăng ký xe; mỗi nhóm tối thiểu 5 câu; chia loại câu theo `eda.LOAI_SPLIT`.
# Đây là đề xuất ban đầu; nhóm điều chỉnh rồi chốt trước khi viết bộ eval.

# %%
core = live[live["trong_pham_vi"] & ~live["van_ban_sua_doi"] & ~live["doc_id"].isin(config.NON_LEGAL)]
cnt = core[core["level"] == "dieu"].groupby("nhom").size()
docs_by = core.groupby("nhom")["doc_id"].agg(lambda s: sorted(set(s)))
matrix = pd.DataFrame(eda.eval_matrix(cnt.to_dict(), docs_by.to_dict(), total=150, floor=5))
out = ROOT / "data" / "eval" / "eval_matrix.csv"
out.parent.mkdir(parents=True, exist_ok=True)
matrix.to_csv(out, index=False, encoding="utf-8-sig")
print(f"-> {out.relative_to(ROOT)}: {int(matrix['so_cau'].sum())} câu")
matrix.pivot_table(index="chu_de", columns="loai_cau", values="so_cau", aggfunc="sum", fill_value=0, margins=True)
````

- [ ] **Step 4: Tạo và chạy notebook**

```bash
python scripts/build_notebook.py notebooks/01_eda_kho_luat.py
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/01_eda_kho_luat.ipynb
```

Expected: chạy hết không lỗi; `reports/eda/figures/` có 10 file PNG (`e1_quy_mo_nhom`, `e2_pham_vi_blds_blhs`, `e3_do_dai_khoan`, `e4_muc_phat`, `e4_tru_diem`, `e5_sua_doi`, `e6_dong_thoi_gian`, `e9_tham_chieu`, `e10_chat_luong` và không thiếu hình nào được gọi `save`); `data/eval/eval_matrix.csv` tổng 150 câu. Nếu một ô lỗi do tên cột hay kiểu dữ liệu pandas 3, sửa trong file `.py` rồi tạo lại notebook; không sửa trực tiếp `.ipynb`.

Kiểm tra bảng E2 (tiêu đề Điều quanh khoảng đề xuất): nếu khoảng Điều 260–266 hoặc 584–608 không khớp tiêu đề (ví dụ tội giao thông kéo dài đến Điều khác), sửa `SCOPE` và ghi lý do trong ô markdown E2.

- [ ] **Step 5: Viết nhận xét**

Đọc kết quả từng phân tích trong notebook, điền ô "Phát hiện → hành động" của E1–E10 trong `notebooks/01_eda_kho_luat.py`: mỗi ô 2–5 gạch đầu dòng dạng "**Phát hiện:** … (số liệu) → **Hành động:** … (giai đoạn)". Hành động phải cụ thể, ví dụ "cắt đoạn theo Khoản, trần 512 token bge-m3; khoản dài hơn chia theo điểm" thay vì "cân nhắc cách cắt". Tạo và chạy lại notebook (Step 4).

- [ ] **Step 6: Test và commit**

Run: `python -m pytest -q` → PASS.

```bash
git add scripts/build_notebook.py tests/test_build_notebook.py notebooks reports/eda/figures data/eval/eval_matrix.csv
git commit -m "Add corpus EDA notebook with figures and initial eval matrix"
```

---

### Task 4: Bảng phát hiện → hành động

**Files:**
- Create: `reports/eda/findings.md`

**Interfaces:**
- Consumes: notebook đã chạy và `data/eval/eval_matrix.csv` từ Task 3.

- [ ] **Step 1: Viết `reports/eda/findings.md`**

Cấu trúc:
1. Tiêu đề "Phát hiện từ EDA kho văn bản luật", một đoạn ngắn: dữ liệu, thời điểm T, notebook nguồn, ngày chạy.
2. Bảng chính, cột `Mã | Phát hiện (kèm số liệu) | Hành động | Giai đoạn`, mỗi phân tích E1–E10 ít nhất một dòng, nội dung khớp các ô "Phát hiện → hành động" trong notebook. Cột "Giai đoạn" dùng một trong: `Cắt đoạn và xây kho tra cứu`, `Bộ eval`, `Dữ liệu train`, `Đánh giá`, `Báo cáo`.
3. Mục "Ma trận đề cho bộ eval": bảng tổng theo chủ đề × loại câu (từ `eval_matrix.csv`), quy tắc phân bổ, ghi chú "đề xuất ban đầu, nhóm chốt trước khi viết".
4. Mục "Hình": danh sách file trong `reports/eda/figures/` kèm một câu mô tả mỗi hình (để dán vào báo cáo).

Mọi con số lấy từ notebook. Không thêm phát hiện không có trong notebook.

- [ ] **Step 2: Commit**

```bash
git add reports/eda/findings.md
git commit -m "Summarise EDA findings and actions"
```

- [ ] **Step 3: ĐIỂM DỪNG DUYỆT (controller)**

Đưa người dùng: bảng phát hiện → hành động và ma trận đề (tổng theo chủ đề và loại câu). Người dùng điều chỉnh số câu thì sửa `data/eval/eval_matrix.csv` trực tiếp (đây là file chốt của nhóm, không sinh lại), ghi `ghi_chu` cho dòng đã đổi, commit "Adjust eval matrix after team review".
