"""G7 — sinh câu trả lời cho 270 câu `eval_v1` ở các cấu hình A/B/C/D, chạy trên máy có GPU (Kaggle T4).

    python scripts/g7_generate.py --out OUT                         # một GPU, chạy hết
    python scripts/g7_generate.py --out OUT --shard 0 --nshards 2   # phần việc của GPU 0 khi chạy song song 2 GPU
    python scripts/g7_generate.py --out OUT --merge                 # gộp kết quả các phần thành g7_answers.jsonl
    python scripts/g7_generate.py --out OUT --backend dry           # chạy thử trên máy không GPU (không sinh thật)

Các lượt sinh (`RUNS`):

| Lượt | Mô hình | Ngữ cảnh | Câu |
|---|---|---|---|
| A | Qwen3.5-9B gốc (tắt adapter) | không | 270 |
| B | gốc | 5 đoạn theo Khoản, có lọc hiệu lực tại ngày hỏi (G3) | 270 |
| C | gốc + adapter LoRA của G6 | không | 270 |
| D | gốc + adapter | như B | 270 |
| B_boloc, D_boloc | như B, D | 5 đoạn khi bỏ lọc hiệu lực (RQ3) | 40 câu sửa đổi |

Mô hình nạp một lần (4-bit, đúng commit đã train ở G6) rồi gắn adapter; lượt A, B, B_boloc chạy trong
`model.disable_adapter()`, nên cả bốn cấu hình dùng chung một bản mô hình gốc đã nén. Prompt dựng bằng chính các hàm
`chat_text`/`encode` của `g6_train.py` (`enable_thinking=False`), và system/user lấy từ dữ liệu train
(`data/g7/prompts.json`, `build_g7_bundle.py` đã kiểm khớp từng mẫu train). Sinh greedy, tối đa `MAX_NEW_TOKENS` token.

Mỗi câu trả lời ghi ngay một dòng vào `OUT/answers_shard<i>.jsonl`; chạy lại thì bỏ qua (lượt, key) đã có, kể cả trong
các thư mục `--prev` (kết quả phiên trước), nên phiên bị ngắt có thể chạy tiếp. `--max-hours` dừng sạch trước giới hạn
phiên. Bộ eval trong gói không có đáp án: chấm điểm làm trên laptop.
"""

import argparse
import contextlib
import json
import os
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g6_train as g6  # noqa: E402  chỉ dùng thư viện chuẩn ở mức module; dựng prompt đúng như lúc train

MODEL = "Qwen/Qwen3.5-9B"
MODEL_REVISION = "c202236235762e1c871ad0ccb60c8ee5ba337b9a"   # commit đã train ở G6 (out_g6/g6_results.json)
MAX_SEQ_LEN = 8192
MAX_NEW_TOKENS = 512
RUNS = {  # thứ tự chạy: hệ thống chính trước
    "D": {"adapter": True, "ngu_canh": "ngu_canh"},
    "C": {"adapter": True, "ngu_canh": None},
    "B": {"adapter": False, "ngu_canh": "ngu_canh"},
    "A": {"adapter": False, "ngu_canh": None},
    "D_boloc": {"adapter": True, "ngu_canh": "ngu_canh_bo_loc", "chi_nhom": "sua_doi"},
    "B_boloc": {"adapter": False, "ngu_canh": "ngu_canh_bo_loc", "chi_nhom": "sua_doi"},
}


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def messages(prompts: dict, item: dict, ctx_field: str | None) -> list[dict]:
    if ctx_field:
        system = prompts["system_with_context"]
        user = prompts["user_with_context"].format(ngay_hoi=item["ngay_hoi"], ngu_canh=item[ctx_field],
                                                   cau_hoi=item["cau_hoi"])
    else:
        system = prompts["system_no_context"]
        user = prompts["user_no_context"].format(ngay_hoi=item["ngay_hoi"], cau_hoi=item["cau_hoi"])
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def all_jobs(items: list[dict], limit: int = 0) -> list[tuple[str, dict]]:
    jobs = []
    for run, cfg in RUNS.items():
        rows = [x for x in items if cfg.get("chi_nhom") in (None, x["nhom_cau"])]
        jobs += [(run, x) for x in (rows[:limit] if limit else rows)]
    return jobs


def answer_files(dirs: list[Path]) -> list[Path]:
    return sorted({p for d in dirs if d.exists()
                   for p in [*d.rglob("answers_shard*.jsonl"), *d.rglob("g7_answers.jsonl")]})


def done_jobs(paths: list[Path]) -> set[tuple[str, str]]:
    """(lượt, uid) đã sinh xong không lỗi. `uid = nhom_cau/key` vì `key` trùng giữa các nhóm câu."""
    return {(r["run"], r["uid"]) for p in paths for r in read_jsonl(p) if not r.get("loi")}


# ---------------------------------------------------------------- mô hình

def load_model(adapter_dir: Path):
    import unsloth  # noqa: F401  phải nạp trước transformers
    from unsloth import FastLanguageModel
    import torch
    from peft import PeftModel

    t = time.time()
    kw = dict(max_seq_length=MAX_SEQ_LEN, dtype=None, load_in_4bit=True)
    try:
        model, tok = FastLanguageModel.from_pretrained(model_name=MODEL, revision=MODEL_REVISION, **kw)
        revision = MODEL_REVISION
    except TypeError:   # bản Unsloth không nhận revision: ghi lại để biết
        model, tok = FastLanguageModel.from_pretrained(model_name=MODEL, **kw)
        revision = "khong_ghim"
    try:
        model = PeftModel.from_pretrained(model, str(adapter_dir))
        cach_gan = "peft"
    except Exception as e:  # dự phòng: để Unsloth tự nạp gốc + adapter từ thư mục adapter
        log(f"PeftModel không gắn được adapter ({type(e).__name__}: {e}); thử nạp thẳng thư mục adapter bằng Unsloth")
        del model
        torch.cuda.empty_cache()
        model, tok = FastLanguageModel.from_pretrained(model_name=str(adapter_dir), **kw)
        cach_gan = "unsloth_adapter_dir"
    FastLanguageModel.for_inference(model)
    assert hasattr(model, "disable_adapter"), "không gắn được adapter: lượt A/B sẽ không phải mô hình gốc"
    info = {"model": MODEL, "revision": revision, "cach_gan_adapter": cach_gan, "nap_giay": round(time.time() - t, 1),
            "vram_sau_nap_gb": round(torch.cuda.memory_allocated() / 2**30, 2), "gpu": torch.cuda.get_device_name(0),
            "fp": "bf16" if torch.cuda.is_bf16_supported() else "fp16"}
    return model, tok, info


def check_adapter_active(model, tok, prompt_ids: list[int]) -> float:
    """Logit bước đầu khi bật và tắt adapter phải khác nhau, nếu không thì C/D chính là A/B."""
    import torch
    ids = torch.tensor([prompt_ids[-512:]], device="cuda")
    with torch.inference_mode():
        on = model(input_ids=ids).logits[0, -1].float()
        with model.disable_adapter():
            off = model(input_ids=ids).logits[0, -1].float()
    diff = float((on - off).abs().max())
    assert diff > 1e-3, f"bật/tắt adapter cho cùng logit (chênh {diff}): adapter không có tác dụng"
    return diff


def generate(model, tok, prompt_ids: list[int]) -> dict:
    import torch
    ids = torch.tensor([prompt_ids], device="cuda")
    t = time.time()
    with torch.inference_mode():
        out = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=MAX_NEW_TOKENS,
                             do_sample=False, use_cache=True)
    new = out[0][ids.shape[1]:].tolist()
    raw = g6.text_tokenizer(tok).decode(new, skip_special_tokens=True)
    return {"tra_loi": re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip(), "so_token_moi": len(new),
            "cham_gioi_han": len(new) >= MAX_NEW_TOKENS, "giay": round(time.time() - t, 2)}


class DryModel:
    """Thay mô hình khi chạy thử không GPU: trả câu cố định, để kiểm luồng chia việc, chạy tiếp và gộp."""

    @contextlib.contextmanager
    def disable_adapter(self):
        yield


def dry_generate(prompt_ids: list[int]) -> dict:
    return {"tra_loi": f"(chạy thử) prompt {len(prompt_ids)} token", "so_token_moi": 0, "cham_gioi_han": False,
            "giay": 0.0}


# ---------------------------------------------------------------- sinh

def run_shard(a) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    items = read_jsonl(ROOT / "data" / "g7" / "items.jsonl")
    prompts = json.loads((ROOT / "data" / "g7" / "prompts.json").read_text(encoding="utf-8"))
    jobs = [j for i, j in enumerate(all_jobs(items, a.limit)) if i % a.nshards == a.shard]
    done = done_jobs(answer_files([out, *map(Path, a.prev)]))
    todo = [(run, x) for run, x in jobs if (run, x["uid"]) not in done]
    log(f"[phần {a.shard}/{a.nshards}] {len(jobs)} việc, đã có {len(jobs) - len(todo)}, còn {len(todo)}")
    if not todo:
        return

    adapter_dir = ROOT / "adapter"
    if a.backend == "dry":
        from transformers import AutoTokenizer
        model, tok, info = DryModel(), AutoTokenizer.from_pretrained(str(adapter_dir)), {"backend": "dry"}
    else:
        model, tok, info = load_model(adapter_dir)
    run0, x0 = todo[0]
    first_ids = g6.encode(tok, g6.chat_text(tok, messages(prompts, x0, RUNS[run0]["ngu_canh"]), generation=True))
    if a.backend != "dry":
        info["chenh_logit_bat_tat_adapter"] = round(check_adapter_active(model, tok, first_ids), 4)
    log(f"nạp xong {json.dumps(info, ensure_ascii=False)}")
    (out / f"shard{a.shard}_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")

    t0, n = time.time(), 0
    path = out / f"answers_shard{a.shard}.jsonl"
    with open(path, "a", encoding="utf-8") as fp:
        for run, x in todo:
            if a.max_hours and time.time() - t0 > a.max_hours * 3600:
                log(f"dừng vì quá {a.max_hours} giờ; còn {len(todo) - n} việc, chạy lại để làm tiếp")
                break
            cfg = RUNS[run]
            rec = {"run": run, "uid": x["uid"], "key": x["key"], "id": x["id"], "tap": x["tap"], "nhom_cau": x["nhom_cau"],
                   "loai_cau": x["loai_cau"], "adapter": cfg["adapter"], "ngu_canh": cfg["ngu_canh"], "shard": a.shard}
            try:
                ids = g6.encode(tok, g6.chat_text(tok, messages(prompts, x, cfg["ngu_canh"]), generation=True))
                rec["so_token_prompt"] = len(ids)
                if a.backend == "dry":
                    rec.update(dry_generate(ids))
                elif cfg["adapter"]:
                    rec.update(generate(model, tok, ids))
                else:
                    with model.disable_adapter():
                        rec.update(generate(model, tok, ids))
                rec["loi"] = None
            except Exception as e:  # hết bộ nhớ ở một câu: ghi lỗi, chạy câu tiếp
                rec["loi"] = f"{type(e).__name__}: {e}"[:500]
                log(f"LỖI {run} {x['uid']}: {rec['loi']}\n{traceback.format_exc()[-800:]}")
                if a.backend != "dry":
                    import torch
                    torch.cuda.empty_cache()
            fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fp.flush()
            n += 1
            if n == 1 or n % 10 == 0 or n == len(todo):
                left = (len(todo) - n) * (time.time() - t0) / n
                log(f"[phần {a.shard}] {n}/{len(todo)} | {run} {x['uid']} {rec.get('giay')} giây, "
                    f"{rec.get('so_token_moi')} token | còn khoảng {left / 60:.0f} phút")
    log(f"[phần {a.shard}] XONG {n} việc trong {(time.time() - t0) / 60:.1f} phút -> {path}")


# ---------------------------------------------------------------- gộp

def merge(a) -> dict:
    out = Path(a.out)
    items = read_jsonl(ROOT / "data" / "g7" / "items.jsonl")
    order = {x["uid"]: i for i, x in enumerate(items)}
    best = {}
    for p in answer_files([out, *map(Path, a.prev)]):
        if p.name == "g7_answers.jsonl" and p.parent == out:
            continue   # bản gộp cũ của chính thư mục này: gộp lại từ các phần
        for r in read_jsonl(p):
            k = (r["run"], r["uid"])
            if k not in best or (best[k].get("loi") and not r.get("loi")):
                best[k] = r
    run_idx = {r: i for i, r in enumerate(RUNS)}
    rows = sorted(best.values(), key=lambda r: (run_idx[r["run"]], order[r["uid"]]))
    with open(out / "g7_answers.jsonl", "w", encoding="utf-8", newline="\n") as fp:
        fp.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    expected = Counter(run for run, _ in all_jobs(items))
    by = defaultdict(list)
    for r in rows:
        by[r["run"]].append(r)
    summary = {"model": MODEL, "revision": MODEL_REVISION, "max_new_tokens": MAX_NEW_TOKENS, "luot": {}}
    for run in RUNS:
        rs = by[run]
        ok = [r for r in rs if not r.get("loi")]
        summary["luot"][run] = {
            "can": expected[run], "co": len(ok), "loi": len(rs) - len(ok),
            "thieu": sorted({x["uid"] for r2, x in all_jobs(items) if r2 == run} - {r["uid"] for r in ok},
                            key=order.get)[:20],
            "giay_tb": round(sum(r["giay"] for r in ok) / len(ok), 1) if ok else None,
            "token_moi_tb": round(sum(r["so_token_moi"] for r in ok) / len(ok)) if ok else None,
            "token_prompt_max": max((r["so_token_prompt"] for r in ok), default=None),
            "cham_gioi_han": sum(r["cham_gioi_han"] for r in ok)}
    summary["du"] = all(v["co"] == v["can"] for v in summary["luot"].values())
    (out / "g7_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--prev", nargs="*", default=[], help="thư mục kết quả phiên trước (bỏ qua câu đã có)")
    ap.add_argument("--limit", type=int, default=int(os.environ.get("G7_LIMIT", "0")),
                    help=">0: chỉ lấy bấy nhiêu câu đầu mỗi lượt (chạy thử)")
    ap.add_argument("--max-hours", type=float, default=0)
    ap.add_argument("--backend", choices=["unsloth", "dry"], default="unsloth")
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    if a.merge:
        print(json.dumps(merge(a), ensure_ascii=False, indent=1))
    else:
        run_shard(a)


if __name__ == "__main__":
    main()
