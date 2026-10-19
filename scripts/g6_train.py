"""G6 — Fine-tune QLoRA Qwen3.5-9B trên dữ liệu chat của G5 (`data/train/chat/`, tag train-v1), chạy trên máy có GPU.

    G6_SMOKE=1 python scripts/g6_train.py   # chạy thử 12 bước trên 96 mẫu, in ước tính thời gian chạy đầy đủ
    python scripts/g6_train.py              # chạy đầy đủ (2 vòng)
    G6_RESUME=1 python scripts/g6_train.py  # chạy tiếp từ checkpoint cuối nếu bị ngắt

Mỗi mẫu = prompt do khuôn chat của Qwen sinh (`add_generation_prompt=True`, `enable_thinking=False`, giống hệt prompt
lúc sinh ở G7) + đáp án + `<|im_end|>`; chỉ phần đáp án có nhãn. Đánh giá loss trên dev mỗi 1/4 vòng, giữ checkpoint có
loss dev thấp nhất. Sau khi train: lưu adapter, loss dev theo loại câu (mô hình gốc so với đã train), sinh 12 câu dev,
vẽ biểu đồ, ghi `g6_results.json`. Kết quả ở `out_g6/` (chạy thử: `out_g6_smoke/`).

Unsloth phải được nạp trước transformers, nên phần đầu file chỉ dùng thư viện chuẩn; thư viện nặng nạp trong `main()`.
"""

import contextlib
import hashlib
import inspect
import json
import math
import os
import platform
import random
import re
import sys
import time
import traceback
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMOKE = os.environ.get("G6_SMOKE") == "1"
RESUME = os.environ.get("G6_RESUME") == "1"
OUT = ROOT / ("out_g6_smoke" if SMOKE else "out_g6")

# Cấu hình (giữ như G4 v2; docs/superpowers/plans/2026-10-19-g6-finetune.md)
MODEL = os.environ.get("G6_MODEL", "Qwen/Qwen3.5-9B")
MODEL_REVISION = os.environ.get("G6_MODEL_REVISION") or None
MAX_SEQ_LEN = 4096
LORA_R, LORA_ALPHA = 16, 16
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
LR, EPOCHS, BATCH, GRAD_ACCUM = 2e-4, 2, 1, 8
WARMUP_FRAC, WEIGHT_DECAY = 0.05, 0.01
EVALS_PER_EPOCH = 4
SEED = 42
GEN_PER_LOAI, MAX_NEW_TOKENS = 2, 384
SMOKE_STEPS, SMOKE_DEV = 12, 16
END = "<|im_end|>"


# ---------------------------------------------------------------- dữ liệu

def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def chat_text(tok, msgs: list[dict], generation: bool) -> str:
    kwargs = dict(tokenize=False, add_generation_prompt=generation)
    try:
        return tok.apply_chat_template(msgs, enable_thinking=False, **kwargs)  # tắt chế độ suy nghĩ của Qwen3.x
    except TypeError:
        return tok.apply_chat_template(msgs, **kwargs)


def text_tokenizer(tok):
    """Bộ xử lý đa phương thức của Qwen3.5 bọc tokenizer văn bản trong `.tokenizer`."""
    return getattr(tok, "tokenizer", tok)


def encode(tok, text: str) -> list[int]:
    return list(text_tokenizer(tok).encode(text, add_special_tokens=False))


def build_examples(tok, rows: list[dict], max_len: int) -> tuple[list[dict], list[str], dict]:
    """Ghép prompt sinh + đáp án + END; nhãn -100 cho prompt. Trả về mẫu, key bị bỏ vì quá dài, và thông tin khuôn."""
    out, dropped, info = [], [], {}
    for r in rows:
        msgs = r["messages"]
        assert [m["role"] for m in msgs] == ["system", "user", "assistant"], r["key"]
        answer = msgs[2]["content"]
        prompt = chat_text(tok, msgs[:2], generation=True)
        full = chat_text(tok, msgs, generation=False)
        i = full.rfind(answer)
        assert i >= 0, f"{r['key']}: khuôn chat không chứa nguyên đáp án"
        tail = full[i + len(answer):]
        assert tail.lstrip().startswith(END), f"{r['key']}: sau đáp án không phải {END}: {tail[:40]!r}"
        if not info:
            info = {"prompt_cuoi": prompt[-120:], "full_bat_dau_bang_prompt": full.startswith(prompt),
                    "sau_dap_an": tail}
        p_ids, c_ids = encode(tok, prompt), encode(tok, answer + END)
        ids = p_ids + c_ids
        if len(ids) > max_len:
            dropped.append(r["key"])
            continue
        out.append({"input_ids": ids, "labels": [-100] * len(p_ids) + c_ids, "key": r["key"], "ban": r["ban"],
                    "loai": r["loai"], "dang": r["dang"], "n_prompt": len(p_ids), "n_answer": len(c_ids)})
    return out, dropped, info


def check_labels(tok, examples: list[dict], rows_by_key: dict) -> None:
    """Phần có nhãn phải giải mã ra đúng đáp án + END (kiểm 20 mẫu đầu)."""
    t = text_tokenizer(tok)
    for ex in examples[:20]:
        got = t.decode([x for x in ex["labels"] if x != -100], skip_special_tokens=False,
                       clean_up_tokenization_spaces=False)
        want = rows_by_key[(ex["key"], ex["ban"])]["messages"][2]["content"] + END
        assert got == want, f"{ex['key']}: nhãn giải mã khác đáp án:\n{got[:200]!r}\n{want[:200]!r}"


class Collator:
    """Đệm phải; nhãn đệm -100. Với lô 1 mẫu thì không có đệm."""

    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch: list[dict]) -> dict:
        import torch
        n = max(len(b["input_ids"]) for b in batch)
        ids = [b["input_ids"] + [self.pad_id] * (n - len(b["input_ids"])) for b in batch]
        att = [[1] * len(b["input_ids"]) + [0] * (n - len(b["input_ids"])) for b in batch]
        lab = [b["labels"] + [-100] * (n - len(b["labels"])) for b in batch]
        return {"input_ids": torch.tensor(ids), "attention_mask": torch.tensor(att), "labels": torch.tensor(lab)}


class ListDataset:
    def __init__(self, examples: list[dict]):
        self.rows = [{"input_ids": e["input_ids"], "labels": e["labels"]} for e in examples]

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


# ---------------------------------------------------------------- đánh giá sau train

def per_sample_loss(model, examples: list[dict], collator, device: str) -> list[dict]:
    """Loss trung bình trên token đáp án của từng mẫu."""
    import torch
    model.eval()
    res = []
    with torch.no_grad():
        for ex in examples:
            batch = {k: v.to(device) for k, v in collator([ex]).items()}
            loss = model(**batch).loss
            res.append({"key": ex["key"], "loai": ex["loai"], "dang": ex["dang"], "loss": float(loss),
                        "n_token": ex["n_answer"]})
    return res


def group_loss(rows: list[dict], field: str) -> dict:
    acc = defaultdict(lambda: [0.0, 0])
    for r in rows:
        for k in (r[field], "tat_ca"):
            acc[k][0] += r["loss"] * r["n_token"]
            acc[k][1] += r["n_token"]
    return {k: round(s / n, 4) for k, (s, n) in sorted(acc.items())}


def adapter_off(model):
    return model.disable_adapter() if hasattr(model, "disable_adapter") else contextlib.nullcontext()


def pick_gen_rows(dev_rows: list[dict]) -> list[dict]:
    by = defaultdict(list)
    for r in dev_rows:
        by[r["loai"]].append(r)
    rng = random.Random(SEED)
    picked = []
    for loai in sorted(by):
        picked += rng.sample(by[loai], min(GEN_PER_LOAI, len(by[loai])))
    return picked


def generate(model, tok, row: dict, device: str) -> dict:
    import torch
    prompt = chat_text(tok, row["messages"][:2], generation=True)
    ids = torch.tensor([encode(tok, prompt)], device=device)
    t = time.time()
    with torch.inference_mode():
        out = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=MAX_NEW_TOKENS,
                             do_sample=False, use_cache=True)
    new = out[0][ids.shape[1]:]
    text = text_tokenizer(tok).decode(new, skip_special_tokens=True)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return {"tra_loi": text, "so_token": int(len(new)), "giay": round(time.time() - t, 1)}


# ---------------------------------------------------------------- biểu đồ

def plots(log_history: list[dict], lengths: list[int], dev_loss: dict | None, out_dir: Path) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out_dir.mkdir(parents=True, exist_ok=True)
    train = [h for h in log_history if "loss" in h and "step" in h]
    ev = [h for h in log_history if "eval_loss" in h]
    files = []

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(out_dir / name, dpi=130)
        plt.close(fig)
        files.append(name)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([h["step"] for h in train], [h["loss"] for h in train], label="train", lw=1)
    ax.plot([h["step"] for h in ev], [h["eval_loss"] for h in ev], "o-", label="dev")
    ax.set(xlabel="bước", ylabel="loss (token đáp án)", title="Loss train và dev")
    ax.legend()
    save(fig, "loss_train_dev.png")
    for key, name, title in (("learning_rate", "learning_rate.png", "Learning rate"),
                             ("grad_norm", "grad_norm.png", "Grad norm")):
        pts = [h for h in train if key in h]
        if pts:
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.plot([h["step"] for h in pts], [h[key] for h in pts], lw=1)
            ax.set(xlabel="bước", title=title)
            save(fig, name)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.hist(lengths, bins=40)
    ax.axvline(MAX_SEQ_LEN, color="red", ls="--", label=f"giới hạn {MAX_SEQ_LEN}")
    ax.set(xlabel="token mỗi mẫu", ylabel="số mẫu", title="Độ dài mẫu train")
    ax.legend()
    save(fig, "token_length_hist.png")
    if dev_loss:
        keys = [k for k in dev_loss["da_train"]["theo_loai"] if k != "tat_ca"] + ["tat_ca"]
        x = range(len(keys))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar([i - 0.2 for i in x], [dev_loss["goc"]["theo_loai"][k] for k in keys], 0.4, label="mô hình gốc")
        ax.bar([i + 0.2 for i in x], [dev_loss["da_train"]["theo_loai"][k] for k in keys], 0.4, label="đã train")
        ax.set_xticks(list(x), keys, rotation=20)
        ax.set(ylabel="loss dev", title="Loss dev theo loại câu")
        ax.legend()
        save(fig, "dev_loss_by_type.png")
    return files


# ---------------------------------------------------------------- train

def training_args(n_train: int, bf16: bool):
    from transformers import TrainingArguments
    steps_per_epoch = math.ceil(n_train / (BATCH * GRAD_ACCUM))
    total = SMOKE_STEPS if SMOKE else steps_per_epoch * EPOCHS
    every = max(1, (SMOKE_STEPS // 2) if SMOKE else steps_per_epoch // EVALS_PER_EPOCH)
    kw = dict(output_dir=str(OUT / "checkpoints"), per_device_train_batch_size=BATCH, per_device_eval_batch_size=1,
              gradient_accumulation_steps=GRAD_ACCUM, num_train_epochs=EPOCHS, max_steps=total if SMOKE else -1,
              learning_rate=LR, lr_scheduler_type="cosine", warmup_steps=max(1, round(WARMUP_FRAC * total)),
              weight_decay=WEIGHT_DECAY, max_grad_norm=1.0, optim="adamw_8bit", bf16=bf16, fp16=not bf16,
              logging_steps=1 if SMOKE else 5, eval_strategy="steps", eval_steps=every, save_strategy="steps",
              save_steps=every, save_total_limit=3, load_best_model_at_end=True, metric_for_best_model="eval_loss",
              greater_is_better=False, prediction_loss_only=True, label_names=["labels"],
              remove_unused_columns=False, report_to="none", seed=SEED, data_seed=SEED, dataloader_num_workers=0)
    params = inspect.signature(TrainingArguments.__init__).parameters
    if "eval_strategy" not in params:
        kw["evaluation_strategy"] = kw.pop("eval_strategy")
    missing = [k for k in kw if k not in params]
    assert not missing, f"TrainingArguments của transformers {version('transformers')} không có: {missing}"
    return TrainingArguments(**kw), {"buoc_moi_vong": steps_per_epoch, "tong_buoc": total, "danh_gia_moi": every}


def pkg(name):
    try:
        return version(name)
    except Exception:
        return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import unsloth  # noqa: F401  phải nạp trước transformers
    from unsloth import FastLanguageModel
    import torch
    from transformers import Trainer, TrainerCallback, set_seed

    OUT.mkdir(parents=True, exist_ok=True)
    set_seed(SEED)
    R = {"che_do": "chay_thu" if SMOKE else "day_du", "bat_dau": time.strftime("%Y-%m-%d %H:%M:%S")}

    def save_results():
        (OUT / "g6_results.json").write_text(json.dumps(R, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    assert torch.cuda.is_available(), "torch không thấy GPU"
    bf16 = torch.cuda.is_bf16_supported()
    R["moi_truong"] = {"python": platform.python_version(), "torch": torch.__version__, "cuda": torch.version.cuda,
                       **{p: pkg(p) for p in ("unsloth", "unsloth_zoo", "transformers", "peft", "bitsandbytes",
                                              "accelerate", "tokenizers")},
                       "gpu": torch.cuda.get_device_name(0),
                       "vram_gb": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2),
                       "compute_capability": ".".join(map(str, torch.cuda.get_device_capability(0))), "bf16": bf16}
    print(json.dumps(R["moi_truong"], indent=1))

    chat = ROOT / "data" / "train" / "chat"
    R["du_lieu"] = {n: sha256(chat / n) for n in ("train_chat.jsonl", "dev_chat.jsonl")}
    manifest = json.loads((chat / "MANIFEST.json").read_text(encoding="utf-8"))
    for n, h in R["du_lieu"].items():
        assert manifest["files"][f"data/train/chat/{n}"]["sha256"] == h, f"{n} khác MANIFEST"
    train_rows, dev_rows = read_jsonl(chat / "train_chat.jsonl"), read_jsonl(chat / "dev_chat.jsonl")
    rows_by_key = {(r["key"], r["ban"]): r for r in train_rows + dev_rows}

    # nạp mô hình
    t = time.time()
    torch.cuda.reset_peak_memory_stats()
    kwargs = {"revision": MODEL_REVISION} if MODEL_REVISION else {}
    model, tok = FastLanguageModel.from_pretrained(model_name=MODEL, max_seq_length=MAX_SEQ_LEN, dtype=None,
                                                   load_in_4bit=True, **kwargs)
    R["mo_hinh"] = {"ten": MODEL, "revision": MODEL_REVISION, "nap_giay": round(time.time() - t, 1),
                    "vram_sau_nap_gb": round(torch.cuda.memory_allocated() / 2**30, 2)}
    try:
        from huggingface_hub import model_info
        R["mo_hinh"]["commit"] = model_info(MODEL, revision=MODEL_REVISION).sha
    except Exception as e:
        R["mo_hinh"]["commit"] = f"không lấy được: {type(e).__name__}"
    model = FastLanguageModel.get_peft_model(model, r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0, bias="none",
                                             target_modules=TARGET_MODULES, use_gradient_checkpointing="unsloth",
                                             random_state=SEED)
    n_train_p = sum(p.numel() for p in model.parameters() if p.requires_grad)
    R["mo_hinh"]["tham_so_lora"] = n_train_p
    print(R["mo_hinh"])

    # ghép mẫu
    train_ex, drop_tr, R["khuon_chat"] = build_examples(tok, train_rows, MAX_SEQ_LEN)
    dev_ex, drop_dev, _ = build_examples(tok, dev_rows, MAX_SEQ_LEN)
    check_labels(tok, train_ex, rows_by_key)
    check_labels(tok, dev_ex, rows_by_key)
    lengths = [len(e["input_ids"]) for e in train_ex]
    full_tokens = sum(lengths)
    if SMOKE:
        train_ex = random.Random(SEED).sample(train_ex, SMOKE_STEPS * BATCH * GRAD_ACCUM)
        dev_ex = random.Random(SEED).sample(dev_ex, SMOKE_DEV)
    R["mau"] = {"train": len(train_ex), "dev": len(dev_ex), "bo_vi_dai": drop_tr + drop_dev,
                "token_train": {"tb": round(full_tokens / len(lengths)), "max": max(lengths),
                                "p95": sorted(lengths)[int(0.95 * len(lengths))]},
                "token_dap_an_train_tb": round(sum(e["n_answer"] for e in train_ex) / len(train_ex))}
    print(R["mau"], R["khuon_chat"])
    save_results()

    args, R["lich"] = training_args(len(train_ex), bf16)
    R["cau_hinh"] = {"MAX_SEQ_LEN": MAX_SEQ_LEN, "LORA_R": LORA_R, "LORA_ALPHA": LORA_ALPHA, "TARGET": TARGET_MODULES,
                     "LR": LR, "EPOCHS": EPOCHS, "BATCH": BATCH, "GRAD_ACCUM": GRAD_ACCUM, "WARMUP": WARMUP_FRAC,
                     "WEIGHT_DECAY": WEIGHT_DECAY, "SEED": SEED, "bf16": bf16}
    print(R["lich"])

    log_path = OUT / "train_log.jsonl"
    t0 = time.time()

    class Log(TrainerCallback):
        def on_log(self, a, state, control, logs=None, **kw):
            logs = {**(logs or {}), "step": state.global_step, "giay": round(time.time() - t0, 1)}
            with open(log_path, "a", encoding="utf-8") as fp:
                fp.write(json.dumps(logs, ensure_ascii=False) + "\n")
            if state.global_step:
                left = (state.max_steps - state.global_step) * (time.time() - t0) / state.global_step
                msg = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in logs.items()}
                print(f"[{state.global_step}/{state.max_steps}] {msg} | còn khoảng {left / 60:.0f} phút", flush=True)

    collator = Collator(text_tokenizer(tok).pad_token_id or text_tokenizer(tok).eos_token_id)
    trainer = Trainer(model=model, args=args, train_dataset=ListDataset(train_ex), eval_dataset=ListDataset(dev_ex),
                      data_collator=collator, callbacks=[Log()])
    torch.cuda.reset_peak_memory_stats()
    stats = trainer.train(resume_from_checkpoint=True if RESUME else None)
    train_s = time.time() - t0
    R["train"] = {"giay": round(train_s, 1), "gio": round(train_s / 3600, 2),
                  "giay_moi_buoc": round(train_s / max(1, trainer.state.global_step), 2),
                  "vram_dinh_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                  "loss_train_tb": round(float(stats.training_loss), 4), "so_buoc": trainer.state.global_step,
                  "checkpoint_tot_nhat": trainer.state.best_model_checkpoint,
                  "eval_loss_tot_nhat": trainer.state.best_metric,
                  "eval_loss": [{"step": h["step"], "eval_loss": round(h["eval_loss"], 4)}
                                for h in trainer.state.log_history if "eval_loss" in h]}
    R["log_history"] = trainer.state.log_history
    model.save_pretrained(str(OUT / "adapter"))   # adapter tốt nhất (load_best_model_at_end)
    tok.save_pretrained(str(OUT / "adapter"))
    print("-> adapter:", OUT / "adapter", R["train"])
    if SMOKE:
        tokens_seen = sum(len(e["input_ids"]) for e in train_ex)
        ev = [h for h in trainer.state.log_history if "eval_runtime" in h]
        eval_s = sum(h["eval_runtime"] for h in ev)
        eval_s_per_sample = eval_s / len(ev) / len(dev_ex) if ev else 0
        n_eval_full = EVALS_PER_EPOCH * EPOCHS + 1
        # tốc độ train tính trên thời gian trừ phần đánh giá; còn gồm khởi động bước đầu nên ước tính hơi dư
        est = full_tokens * EPOCHS * (train_s - eval_s) / tokens_seen + n_eval_full * eval_s_per_sample * len(dev_rows)
        R["uoc_tinh_chay_day_du_gio"] = round(est / 3600, 2)
        print(f"\n>> ƯỚC TÍNH chạy đầy đủ: khoảng {est / 3600:.1f} giờ (train {EPOCHS} vòng + {n_eval_full} lần đánh giá dev)")
    save_results()

    # loss dev theo loại câu: mô hình gốc (tắt adapter) và đã train
    try:
        t = time.time()
        ft = per_sample_loss(model, dev_ex, collator, "cuda")
        with adapter_off(model):
            base = per_sample_loss(model, dev_ex, collator, "cuda")
        R["loss_dev"] = {name: {"theo_loai": group_loss(rows, "loai"), "theo_dang": group_loss(rows, "dang")}
                         for name, rows in (("goc", base), ("da_train", ft))}
        R["loss_dev"]["giay"] = round(time.time() - t, 1)
        with open(OUT / "dev_loss_per_sample.jsonl", "w", encoding="utf-8") as fp:
            for b, f in zip(base, ft):
                fp.write(json.dumps({**f, "loss_goc": b["loss"]}, ensure_ascii=False) + "\n")
        print("loss dev:", json.dumps(R["loss_dev"], ensure_ascii=False))
    except Exception as e:
        R["loss_dev_loi"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}"
        print("loss dev LỖI:", R["loss_dev_loi"])
    save_results()

    # sinh câu trả lời cho vài câu dev
    try:
        FastLanguageModel.for_inference(model)
        rows = pick_gen_rows(dev_rows)[: 2 if SMOKE else None]
        with open(OUT / "dev_answers.jsonl", "w", encoding="utf-8") as fp:
            for r in rows:
                rec = {"key": r["key"], "loai": r["loai"], "dang": r["dang"],
                       "cau_hoi": r["messages"][1]["content"].split("Câu hỏi:")[-1].strip(),
                       "dap_an_chuan": r["messages"][2]["content"]}
                rec["da_train"] = generate(model, tok, r, "cuda")
                with adapter_off(model):
                    rec["goc"] = generate(model, tok, r, "cuda")
                fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print(r["key"], r["loai"], rec["da_train"]["giay"], "giây:", rec["da_train"]["tra_loi"][:160])
        R["sinh_dev"] = {"so_cau": len(rows), "file": "dev_answers.jsonl"}
    except Exception as e:
        R["sinh_dev_loi"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}"
        print("sinh LỖI:", R["sinh_dev_loi"])
    save_results()

    try:
        R["bieu_do"] = plots(trainer.state.log_history, lengths, R.get("loss_dev"), OUT / "plots")
    except Exception as e:
        R["bieu_do_loi"] = f"{type(e).__name__}: {e}"
    R["ket_thuc"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_results()
    print("\n>> XONG. Kết quả:", OUT)


if __name__ == "__main__":
    sys.exit(main())
