"""Gói dữ liệu cho notebook chạy thử trên Kaggle (G4): `kaggle/g4/g4_bundle.zip`.

    py -3.13 scripts/build_g4_bundle.py              # gói dữ liệu và notebook
    py -3.13 scripts/build_g4_bundle.py --notebooks  # chỉ xuất lại notebook cho Kaggle

Nội dung (chỉ dùng tập dev, không đụng tập test):
- `dev_items.jsonl`: 20 câu dev (10 thường, 4 sửa đổi, 3 biến thể, 3 ngoài phạm vi; chọn theo `key`), mỗi câu kèm
  ngữ cảnh theo Khoản và theo Điều lấy từ `data/rag/test_with_context_<cách cắt>.jsonl`.
- `timing_train.jsonl`: 100 mẫu CHỈ ĐỂ ĐO THỜI GIAN train QLoRA, không phải dữ liệu train thật. Dựng từ các đoạn theo
  Khoản đang có hiệu lực mà không chứa căn cứ của bất kỳ câu eval nào; ngữ cảnh gồm đoạn đó và 4 đoạn ngẫu nhiên.
- `meta.json`: mã băm các file nguồn.
"""

import hashlib
import json
import random
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import chunking, context, retrieve  # noqa: E402

OUT = config.ROOT / "kaggle" / "g4"
PICK = {"thuong": 10, "sua_doi": 4, "bien_the": 3, "ngoai_pham_vi": 3}
N_TIMING = 100
SEED = 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dev_items() -> list[dict]:
    files = {cut: config.DATA / "rag" / f"test_with_context_{cut}.jsonl" for cut in ("khoan", "dieu")}
    for path in files.values():
        if not path.exists():
            sys.exit(f"chưa có {path.relative_to(config.ROOT)}: chạy scripts/run_retrieval.py --tap test trước")
    ctx = {cut: {r["id"]: r for r in map(json.loads, path.open(encoding="utf-8"))} for cut, path in files.items()}
    dev = sorted((x for x in evalset.load_eval() if x["tap"] == "dev"), key=lambda x: x["key"])
    out = []
    for group, n in PICK.items():
        for x in [x for x in dev if x["nhom_cau"] == group][:n]:
            out.append({"id": x["id"], "key": x["key"], "nhom_cau": x["nhom_cau"], "cau_hoi": x["cau_hoi"],
                        "ngay_hoi": x["ngay_hoi"], "dap_an": x.get("dap_an"),
                        "ngu_canh_khoan": ctx["khoan"][x["id"]]["ngu_canh"],
                        "ngu_canh_dieu": ctx["dieu"][x["id"]]["ngu_canh"]})
    return out


def timing_samples() -> list[dict]:
    chunks, _ = retrieve.load_chunks("khoan")
    cited = {v for x in evalset.load_eval() for v in (x.get("can_cu") or []) + (x.get("can_cu_cu") or [])}
    live = [c for c in chunks if chunking.in_force(c, config.CUTOFF) and not c["mot_phan"]]
    pool = [c for c in live if 60 <= c["so_token"] <= 400 and not set(c["units"]) & cited]
    rng = random.Random(SEED)
    out = []
    for c in rng.sample(pool, N_TIMING):
        others = rng.sample([d for d in live if d["nhom"] != c["nhom"]], 4)
        shown = others[:]
        shown.insert(rng.randrange(5), c)
        body = "\n".join(c["text"].splitlines()[1:])
        out.append({"cau_hoi": f"Theo {context.source_label(c)}, quy định cụ thể là gì?",
                    "ngu_canh": context.format_context(shown),
                    "dap_an": f"{body}\n(Căn cứ: {context.source_label(c)}.)",
                    "chunk_id": c["chunk_id"], "chi_de_do_thoi_gian": True})
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {"dev_items.jsonl": dev_items(), "timing_train.jsonl": timing_samples()}
    sources = ["data/eval/eval_v1.jsonl", "data/rag/chunks_khoan.jsonl",
               "data/rag/test_with_context_khoan.jsonl", "data/rag/test_with_context_dieu.jsonl"]
    meta = {"mo_ta": "Gói dữ liệu cho notebook G4 (chạy thử Kaggle). Chỉ tập dev; mẫu train chỉ để đo thời gian.",
            "nguon": {p: sha256(config.ROOT / p) for p in sources},
            "so_cau_dev": len(files["dev_items.jsonl"]), "so_mau_do_thoi_gian": len(files["timing_train.jsonl"])}
    data = {name: "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
            for name, rows in files.items()}
    data["meta.json"] = (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    zip_path = OUT / "g4_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in data.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))  # cố định ngày để zip lặp lại được
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, payload)
    print(f"-> {zip_path.relative_to(config.ROOT)}: {meta['so_cau_dev']} câu dev, "
          f"{meta['so_mau_do_thoi_gian']} mẫu đo thời gian, {zip_path.stat().st_size / 1e6:.2f} MB")
    export_notebooks()


NOTEBOOKS = {"02_g4_kaggle.ipynb": "g4_kaggle.ipynb", "03_g4_kaggle_v2.ipynb": "g4_kaggle_v2.ipynb"}


def export_notebooks() -> None:
    """Bản notebook cho Kaggle: dựng từ notebooks/*.ipynb, đổi kernel sang python3 chuẩn của Kaggle."""
    OUT.mkdir(parents=True, exist_ok=True)
    for src, dst in NOTEBOOKS.items():
        nb = json.loads((config.ROOT / "notebooks" / src).read_text(encoding="utf-8"))
        nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nb_out = OUT / dst
        nb_out.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"-> {nb_out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    if "--notebooks" in sys.argv:  # chỉ xuất notebook, giữ nguyên g4_bundle.zip đã tải lên Kaggle
        export_notebooks()
    else:
        main()
