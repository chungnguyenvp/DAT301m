"""Gói cho notebook gắn ngữ cảnh trên Kaggle (G5 Task 4): `kaggle/g5ctx/g5ctx_bundle.zip` và `g5_context.ipynb`.

    py -3.13 scripts/build_g5ctx_bundle.py              # gói dữ liệu và notebook
    py -3.13 scripts/build_g5ctx_bundle.py --notebooks  # chỉ xuất lại notebook

Gói giữ nguyên bố cục thư mục của repo để `src/rag` chạy được trên Kaggle mà không sửa: mã `src/rag`, `src/lawproc`;
kho đoạn theo Khoản và chỉ mục của G3; `data/manifest.csv` (tên văn bản); tham số G3; `data/train/{train,dev}.jsonl`;
tokenizer Qwen để đếm token; `meta.json` ghi mã băm từng file. Không có bộ eval hay tập test.
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lawproc import config  # noqa: E402

OUT = config.ROOT / "kaggle" / "g5ctx"
FILES = ["data/manifest.csv", "data/rag/MANIFEST.json", "data/rag/chunks_khoan.jsonl",
         "data/rag/index/khoan/bm25.pkl", "data/rag/index/khoan/dense.faiss", "data/rag/index/khoan/dense_ids.json",
         "data/rag/index/khoan/meta.json", "reports/retrieval/params.json",
         "data/train/train.jsonl", "data/train/dev.jsonl", "data/train/MANIFEST.json",
         "tools/tokenizers/qwen3.5-9b/tokenizer.json"]
CODE = sorted(p.relative_to(config.ROOT).as_posix() for d in ("src/rag", "src/lawproc")
              for p in (config.ROOT / d).glob("*.py"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    names = CODE + FILES
    meta = {"mo_ta": "Gói cho notebook G5 Task 4 (gắn ngữ cảnh RAG cho dữ liệu train, cách C). Không có bộ eval.",
            "file": {n: sha256(config.ROOT / n) for n in names}}
    zip_path = OUT / "g5ctx_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))  # cố định ngày để zip lặp lại được
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, (config.ROOT / name).read_bytes())
        info = zipfile.ZipInfo("meta.json", date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(f"-> {zip_path.relative_to(config.ROOT)}: {len(names)} file, {zip_path.stat().st_size / 1e6:.1f} MB")
    export_notebooks()


def export_notebooks() -> None:
    """notebooks/04_g5_context.ipynb (kernel máy) và kaggle/g5ctx/g5_context.ipynb (kernel python3 của Kaggle)."""
    import nbformat
    from build_notebook import cells_from_source

    src = config.ROOT / "notebooks" / "04_g5_context.py"
    cells = cells_from_source(src.read_text(encoding="utf-8"))
    for path, kernel in ((src.with_suffix(".ipynb"), {"name": "python313-traffic-law",
                                                      "display_name": "Python 3.13 (traffic-law)"}),
                         (OUT / "g5_context.ipynb", {"name": "python3", "display_name": "Python 3"})):
        nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {**kernel, "language": "python"}})
        path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, path)
        print(f"-> {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    if "--notebooks" in sys.argv:
        export_notebooks()
    else:
        main()
