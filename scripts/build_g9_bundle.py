"""Gói cho notebook demo G9 trên Kaggle: `kaggle/g9/g9_bundle.zip` và `g9_demo.ipynb`.

    py -3.13 scripts/build_g9_bundle.py                 # câu mẫu, prompt, gói và notebook
    py -3.13 scripts/build_g9_bundle.py --notebooks     # chỉ xuất lại notebook

Ghi vào repo (để chạy thử demo trên laptop): `data/g9/prompts.json` (system và mẫu user lấy từ dữ liệu train, như G7)
và `data/g9/examples.json` (câu mẫu lấy từ eval_v1; câu sửa đổi có thêm ngày cũ `ngay_cu`).

Trong gói, giữ đúng cấu trúc thư mục của repo để `lawproc.config.ROOT` trỏ về gốc gói:
- `scripts/g9_demo.py`, `scripts/g7_generate.py`, `scripts/g6_train.py`; `src/rag/`, `src/lawproc/` (phần retriever cần);
- `data/rag/`: đoạn theo Khoản và theo Điều, `MANIFEST.json`, chỉ mục theo Khoản (BM25, FAISS);
- `data/manifest.csv` (số ký hiệu văn bản cho nhãn nguồn), `reports/retrieval/params.json` (tham số G3);
- `data/g9/`, `adapter/` (adapter LoRA G6), `meta.json` (mã băm từng file, mô hình và revision cần tải).
"""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lawproc import config  # noqa: E402

import build_g7_bundle as b7  # noqa: E402
import g7_generate as g7  # noqa: E402
import g9_demo as g9  # noqa: E402

OUT = config.ROOT / "kaggle" / "g9"
NOTEBOOK_SRC = config.ROOT / "notebooks" / "06_g9_demo.py"
G9_DATA = config.DATA / "g9"
# Câu mẫu: câu thường D trả lời đúng (theo chấm nội dung G8), câu sửa đổi để đổi ngày hỏi (RQ3), câu ngoài phạm vi.
EXAMPLES = ["thuong/xp03", "thuong/xp07", "thuong/ll08", "thuong/td02", "thuong/ll12",
            "sua_doi/sd10", "sua_doi/sd34", "sua_doi/sd25",
            "ngoai_pham_vi/np01", "ngoai_pham_vi/np18"]
CODE = ["scripts/g9_demo.py", "scripts/g7_generate.py", "scripts/g6_train.py",
        "src/lawproc/__init__.py", "src/lawproc/config.py", "src/lawproc/validity.py",
        *(f"src/rag/{m}.py" for m in ("__init__", "bm25", "chunking", "context", "dense", "expand", "retrieve"))]
DATA = ["data/manifest.csv", "data/rag/MANIFEST.json", "data/rag/chunks_khoan.jsonl", "data/rag/chunks_dieu.jsonl",
        *(f"data/rag/index/khoan/{n}" for n in ("bm25.pkl", "dense.faiss", "dense_ids.json", "meta.json")),
        "reports/retrieval/params.json"]


def build_examples() -> list[dict]:
    ev = {f"{x['nhom_cau']}/{x['key']}": x for x in b7.read_jsonl(config.DATA / "eval" / "eval_v1.jsonl")}
    out = []
    for uid in EXAMPLES:
        x = ev[uid]
        out.append({"uid": uid, "cau_hoi": x["cau_hoi"], "ngay_hoi": x["ngay_hoi"], "nhom_cau": x["nhom_cau"]})
        if x.get("ngay_cu"):
            out.append({"uid": uid, "cau_hoi": x["cau_hoi"], "ngay_hoi": x["ngay_cu"], "nhom_cau": x["nhom_cau"],
                        "ban_cu": True})
    return out


def write_json(path: Path, obj) -> bytes:
    data = (json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebooks", action="store_true")
    a = ap.parse_args()
    b7.NOTEBOOK_SRC = NOTEBOOK_SRC
    b7.build_notebook(OUT, "g9_demo.ipynb")
    if a.notebooks:
        return

    data = {"data/g9/prompts.json": write_json(G9_DATA / "prompts.json", b7.prompts_from_train()),
            "data/g9/examples.json": write_json(G9_DATA / "examples.json", build_examples())}
    for name in CODE:
        data[name] = b7.lf_bytes(config.ROOT / name)
    for name in DATA:   # nguyên byte: mã băm phải khớp MANIFEST.json và meta.json của chỉ mục
        data[name] = (config.ROOT / name).read_bytes()
    for p in sorted(b7.ADAPTER.iterdir()):
        data[f"adapter/{p.name}"] = p.read_bytes()
    dense_meta = json.loads((config.DATA / "rag" / "index" / "khoan" / "meta.json").read_text(encoding="utf-8"))
    meta = {"mo_ta": "Gói demo G9: retriever G3 (chỉ mục theo Khoản) + mở rộng Điều G8 + adapter G6, giao diện Gradio.",
            "mo_hinh": {g7.MODEL: g7.MODEL_REVISION,
                        dense_meta["bo_ma_hoa"]["model"]: dense_meta["bo_ma_hoa"]["revision"],
                        "BAAI/bge-reranker-v2-m3": g9.RERANK_REVISION},
            "so_cau_mau": len(json.loads(data["data/g9/examples.json"])),
            "file": {n: hashlib.sha256(b).hexdigest() for n, b in data.items()}}
    zip_path = OUT / "g9_bundle.zip"
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, b in [*data.items(), ("meta.json", (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode())]:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, b)
    print(f"-> {zip_path.relative_to(config.ROOT)}: {len(data)} file, {zip_path.stat().st_size / 1e6:.1f} MB")
    print(json.dumps({k: meta[k] for k in ("mo_hinh", "so_cau_mau")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
