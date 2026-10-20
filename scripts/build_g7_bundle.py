"""Gói cho notebook sinh câu trả lời G7 trên Kaggle: `kaggle/g7/g7_bundle.zip` và `g7_generate.ipynb`.

    py -3.13 scripts/build_g7_bundle.py                 # gói và notebook
    py -3.13 scripts/build_g7_bundle.py --notebooks     # chỉ xuất lại notebook
    py -3.13 scripts/build_g7_bundle.py --g8            # gói G8: `kaggle/g8/g8_bundle.zip`, lượt D_g8 và B_g8 với
                                                        # ngữ cảnh mở rộng lên Điều (data/rag/test_with_context_g8.jsonl)

Trong gói:
- `data/g7/items.jsonl`: 270 câu `eval_v1` với câu hỏi, ngày hỏi và ngữ cảnh của G3 (`test_with_context_khoan.jsonl`,
  câu sửa đổi có thêm bản bỏ lọc hiệu lực). Mỗi câu định danh bằng `uid = nhom_cau/key` (`key` trùng giữa các nhóm).
  **Không có đáp án**: chấm điểm làm trên laptop.
- `data/g7/prompts.json`: system và mẫu user lấy từ dữ liệu train `train-v1`; đã kiểm từng mẫu train dựng lại đúng.
- `adapter/`: adapter LoRA của G6 (checkpoint tốt nhất), kèm tokenizer và khuôn chat.
- `scripts/g7_generate.py`, `scripts/g6_train.py` (hàm dựng prompt dùng chung với lúc train).
- `meta.json`: mã băm từng file, số câu, độ dài prompt ước tính theo từng lượt.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lawproc import config  # noqa: E402

import g6_train as g6  # noqa: E402
import g7_generate as g7  # noqa: E402

OUT = config.ROOT / "kaggle" / "g7"
ADAPTER = config.ROOT / "remote" / "g6" / "ketqua" / "out_g6" / "adapter"
G6_RESULTS = ADAPTER.parent / "g6_results.json"
CHAT = config.ROOT / "data" / "train" / "chat" / "train_chat.jsonl"
NOTEBOOK_SRC = config.ROOT / "notebooks" / "05_g7_generate.py"
USER_CTX = "Ngày hỏi: {ngay_hoi}\n\nCác đoạn luật:\n{ngu_canh}\n\nCâu hỏi: {cau_hoi}"
USER_NO_CTX = "Ngày hỏi: {ngay_hoi}\n\nCâu hỏi: {cau_hoi}"
PAT_CTX = re.compile(r"Ngày hỏi: (.*?)\n\nCác đoạn luật:\n(.*)\n\nCâu hỏi: (.*)", re.DOTALL)
PAT_NO_CTX = re.compile(r"Ngày hỏi: (.*?)\n\nCâu hỏi: (.*)", re.DOTALL)
ITEM_FIELDS = ("key", "id", "tap", "nhom_cau", "loai_cau", "chu_de", "cau_hoi", "ngay_hoi")


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def prompts_from_train() -> dict:
    """System của dạng có/không ngữ cảnh và kiểm mẫu user dựng lại đúng từng mẫu train."""
    systems = {"co": set(), "khong": set()}
    for r in read_jsonl(CHAT):
        sys_msg, user = r["messages"][0]["content"], r["messages"][1]["content"]
        if r["dang"] == "khong_ngu_canh":
            m = PAT_NO_CTX.fullmatch(user)
            assert m and USER_NO_CTX.format(ngay_hoi=m[1], cau_hoi=m[2]) == user, r["key"]
            systems["khong"].add(sys_msg)
        else:   # có ngữ cảnh và từ chối đều có 5 đoạn
            m = PAT_CTX.fullmatch(user)
            assert m and USER_CTX.format(ngay_hoi=m[1], ngu_canh=m[2], cau_hoi=m[3]) == user, r["key"]
            systems["co"].add(sys_msg)
    assert len(systems["co"]) == 1 and len(systems["khong"]) == 1, "dữ liệu train có hơn một system prompt"
    return {"system_with_context": systems["co"].pop(), "system_no_context": systems["khong"].pop(),
            "user_with_context": USER_CTX, "user_no_context": USER_NO_CTX}


def build_items(g8: bool = False) -> list[dict]:
    uid = lambda x: f"{x['nhom_cau']}/{x['key']}"   # noqa: E731  `key` trùng giữa các nhóm (thuong/np01, ngoai_pham_vi/np01)
    ev = {uid(x): x for x in read_jsonl(config.DATA / "eval" / "eval_v1.jsonl")}
    ctx = read_jsonl(config.DATA / "rag" / "test_with_context_khoan.jsonl")
    assert len(ctx) == len(ev) == 270 and {uid(c) for c in ctx} == set(ev)
    g8ctx = ({c["uid"]: c for c in read_jsonl(config.DATA / "rag" / "test_with_context_g8.jsonl")} if g8 else {})
    assert not g8 or set(g8ctx) == set(ev)
    items = []
    for c in ctx:
        x = ev[uid(c)]
        assert c["cau_hoi"] == x["cau_hoi"] and c["ngay_hoi"] == x["ngay_hoi"] and c["id"] == x["id"], uid(c)
        it = {"uid": uid(x), **{f: x[f] for f in ITEM_FIELDS}}
        it["ngu_canh"] = c["ngu_canh"]
        it["ngu_canh_bo_loc"] = c.get("ngu_canh_bo_loc")
        assert (it["ngu_canh_bo_loc"] is not None) == (x["nhom_cau"] == "sua_doi"), uid(c)
        if g8:
            it["ngu_canh_g8"] = g8ctx[uid(x)]["ngu_canh_g8"]
        items.append(it)
    return items


def prompt_lengths(items: list[dict], prompts: dict, runs: list[str]) -> dict:
    """Số token prompt theo từng lượt, dựng đúng như notebook (tokenizer + khuôn chat của adapter)."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(ADAPTER))
    by = {}
    for run, x in g7.all_jobs(items, runs=runs):
        n = len(g6.encode(tok, g6.chat_text(tok, g7.messages(prompts, x, g7.RUNS[run]["ngu_canh"]), generation=True)))
        by.setdefault(run, []).append(n)
    sample = g6.chat_text(tok, g7.messages(prompts, items[0], "ngu_canh"), generation=True)
    assert sample.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), sample[-80:]
    return {run: {"tb": round(sum(v) / len(v)), "max": max(v), "n": len(v)} for run, v in by.items()}


def build_notebook(out: Path = OUT, name: str = "g7_generate.ipynb") -> None:
    import build_notebook as bn
    import nbformat
    nb = nbformat.v4.new_notebook(cells=bn.cells_from_source(NOTEBOOK_SRC.read_text(encoding="utf-8")),
                                  metadata={"kernelspec": {"name": "python3", "display_name": "Python 3",
                                                           "language": "python"}})
    nbformat.write(nb, NOTEBOOK_SRC.with_suffix(".ipynb"))
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(NOTEBOOK_SRC.with_suffix(".ipynb"), out / name)
    print(f"-> {NOTEBOOK_SRC.with_suffix('.ipynb').relative_to(config.ROOT)}, {(out / name).relative_to(config.ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebooks", action="store_true")
    ap.add_argument("--g8", action="store_true")
    a = ap.parse_args()
    out, stem = (config.ROOT / "kaggle" / "g8", "g8") if a.g8 else (OUT, "g7")
    runs = ["D_g8", "B_g8"] if a.g8 else list(g7.G7_RUNS)
    build_notebook(out, f"{stem}_generate.ipynb")
    if a.notebooks:
        return

    g6r = json.loads(G6_RESULTS.read_text(encoding="utf-8"))
    acfg = json.loads((ADAPTER / "adapter_config.json").read_text(encoding="utf-8"))
    assert acfg["base_model_name_or_path"] == g7.MODEL == g6r["mo_hinh"]["ten"]
    assert g6r["mo_hinh"]["commit"] == g7.MODEL_REVISION, "commit mô hình gốc khác bản đã train ở G6"
    prompts = prompts_from_train()
    items = build_items(a.g8)
    lengths = prompt_lengths(items, prompts, runs)

    data = {"data/g7/items.jsonl": "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items).encode(),
            "data/g7/prompts.json": (json.dumps(prompts, ensure_ascii=False, indent=1) + "\n").encode()}
    for name in ("scripts/g7_generate.py", "scripts/g6_train.py"):
        data[name] = lf_bytes(config.ROOT / name)
    for p in sorted(ADAPTER.iterdir()):
        data[f"adapter/{p.name}"] = p.read_bytes()
    meta = {"mo_ta": ("Gói G8: 270 câu eval_v1 (không đáp án) + ngữ cảnh mở rộng lên Điều + adapter G6, sinh lại B và D."
                      if a.g8 else "Gói G7: 270 câu eval_v1 (không đáp án) + ngữ cảnh G3 + adapter G6, sinh câu trả lời A/B/C/D."),
            "luot_chay": runs,
            "mo_hinh": g7.MODEL, "revision": g7.MODEL_REVISION, "max_new_tokens": g7.MAX_NEW_TOKENS,
            "g6": {"checkpoint": g6r["train"]["checkpoint_tot_nhat"], "eval_loss": g6r["train"]["eval_loss_tot_nhat"]},
            "so_cau": dict(Counter(x["tap"] for x in items)), "nhom_cau": dict(Counter(x["nhom_cau"] for x in items)),
            "so_viec": dict(Counter(run for run, _ in g7.all_jobs(items, runs=runs))), "token_prompt": lengths,
            "nguon": {n: hashlib.sha256(lf_bytes(config.ROOT / n)).hexdigest()
                      for n in ("data/eval/eval_v1.jsonl", "data/rag/test_with_context_khoan.jsonl",
                                "data/train/chat/train_chat.jsonl", *(["data/rag/test_with_context_g8.jsonl"] if a.g8 else []))},
            "file": {n: hashlib.sha256(b).hexdigest() for n, b in data.items()}}
    zip_path = out / f"{stem}_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, b in [*data.items(), ("meta.json", (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode())]:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, b)
    print(f"-> {zip_path.relative_to(config.ROOT)}: {len(data)} file, {zip_path.stat().st_size / 1e6:.1f} MB")
    print(json.dumps({k: meta[k] for k in ("so_cau", "nhom_cau", "so_viec", "token_prompt", "g6")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
