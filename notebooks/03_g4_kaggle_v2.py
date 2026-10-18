# %% [markdown]
# # G4 bản 2 — Đo thời gian train và sinh với ngữ cảnh theo Điều đã giới hạn
#
# Lần chạy 1 (`02_g4_kaggle`, kết quả ở `reports/g4/g4_results.json`) đo được Qwen3.5-9B nạp 4-bit trên T4 (7,98 GB),
# sinh không ngữ cảnh 27,8 giây/câu và theo Khoản 26,1 giây/câu. Lần đó hết bộ nhớ ở phép attention khi prompt theo
# Điều dài 8.223 token, nên chưa đo được bước train.
#
# Bản 2 chỉ đo phần còn thiếu, với Qwen3.5-9B:
#
# 1. Train QLoRA 1 vòng trên 100 mẫu **chỉ để đo thời gian** → thời gian, VRAM. Chạy trước để luôn có số liệu.
# 2. Nạp lại mô hình gốc (bỏ adapter vừa train), sinh câu trả lời cho 20 câu **dev** với ngữ cảnh theo Điều, giữ
#    nguyên từng Điều theo thứ hạng cho tới khi đủ `DIEU_CTX_TOKENS` token. Câu nào vẫn hết bộ nhớ thì ghi lỗi và
#    chạy câu tiếp.
# 3. Ước tính giờ GPU cho G6 (train) và G7 (sinh), dùng số đo sinh của lần 1 cho cách không ngữ cảnh và theo Khoản.
#
# Kết quả: `/kaggle/working/g4v2_results.json` và `/kaggle/working/g4v2_answers.jsonl`.
#
# **Lần chạy 2 (đã có kết quả):** train 100 mẫu mất 811 giây, VRAM tối đa 9,16 GB. Bước sinh theo Điều hỏng vì hàm đếm
# token trả về 1 (bộ xử lý của Qwen3.5 trả `input_ids` dạng lô) nên không cắt ngữ cảnh. Đã sửa bằng `token_ids`. Lần
# chạy 3 đặt `RUN_TRAIN = False` để chỉ chạy bước sinh trên mô hình nạp một lần, không còn bộ nhớ thừa của bước train.
#
# **Cài đặt Kaggle:** Accelerator *GPU T4 x2* (hoặc P100); Internet *On*; Add Input → dataset `g4-bundle` đã dùng ở
# lần 1. Rồi *Run All*, chạy xong bấm *Save Version* để giữ file kết quả.

# %%
# Cấu hình
MODEL = "Qwen/Qwen3.5-9B"
MAX_SEQ_LEN = 4096
MAX_NEW_TOKENS = 384
DIEU_CTX_TOKENS = 4000      # lần 1: 9B chạy được prompt 5.573 token, hết bộ nhớ ở 8.223 token
RUN_TRAIN = False           # lần 2 đã đo train (811 giây/100 mẫu); False: chỉ chạy bước sinh để còn đủ bộ nhớ
LORA_R, LORA_ALPHA = 16, 16
TRAIN_BATCH, GRAD_ACCUM, LR = 2, 4, 2e-4
SEED = 42
EST_TRAIN_SAMPLES, EST_EPOCHS = 2000, 2
EST_EVAL_QUESTIONS = 270
KAGGLE_WEEKLY_GPU_HOURS = 30
# Số đo sinh của lần 1 với Qwen3.5-9B (reports/g4/g4_results.json), dùng cho ước tính
LAN_2_TRAIN_100_SECONDS = 811.2  # lần 2 (reports/g4/g4v2_results.json): train 100 mẫu, VRAM tối đa 9,16 GB
LAN_1 = {"sinh_khong_ngu_canh": {"giay_moi_cau": 27.83, "token_moi_giay": 11.9, "prompt_tokens_tb": 104},
         "sinh_khoan": {"giay_moi_cau": 26.09, "token_moi_giay": 10.9, "prompt_tokens_tb": 1800}}

# %%
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"   # Unsloth dùng 1 GPU; tránh lỗi khi máy có T4 x2
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"  # phải đặt trước khi nạp torch

# %%
!pip install -q unsloth

# %%
import unsloth  # phải nạp trước transformers để Unsloth vá đúng
from unsloth import FastLanguageModel
import gc, glob, json, platform, re, subprocess, time, traceback
from importlib.metadata import version
import torch

def pkg(name):
    try:
        return version(name)
    except Exception:
        return None

ENV = {
    "python": platform.python_version(),
    "torch": torch.__version__,
    **{p: pkg(p) for p in ("unsloth", "transformers", "trl", "peft", "bitsandbytes", "accelerate", "datasets")},
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    "gpu_vram_gb": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2) if torch.cuda.is_available() else None,
    "bf16": torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
}
print(json.dumps(ENV, indent=1))
print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout)

# %%
def find(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True) + glob.glob(name)
    return hits[0] if hits else None

if not find("dev_items.jsonl"):
    import zipfile
    z = find("g4_bundle.zip")
    assert z, "Không thấy dev_items.jsonl hay g4_bundle.zip trong /kaggle/input: hãy Add Input dataset G4"
    zipfile.ZipFile(z).extractall("/kaggle/working/g4_bundle")
    os.chdir("/kaggle/working/g4_bundle")

def read_jsonl(name):
    with open(find(name), encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]

DEV = read_jsonl("dev_items.jsonl")
TIMING = read_jsonl("timing_train.jsonl")
META = json.load(open(find("meta.json"), encoding="utf-8"))
print(len(DEV), "câu dev;", len(TIMING), "mẫu đo thời gian;", META["mo_ta"])

# %%
SYSTEM_WITH_CONTEXT = (
    "Bạn là trợ lý pháp luật giao thông đường bộ Việt Nam. Trả lời dựa trên các đoạn luật được cung cấp, "
    "theo quy định có hiệu lực tại ngày hỏi. Nêu rõ căn cứ (điểm, khoản, Điều, văn bản) và nêu đúng số tiền, "
    "số điểm trừ, thời hạn nếu có. Nếu các đoạn luật không có căn cứ cho câu hỏi, nói rõ là không có căn cứ trong "
    "tài liệu, không tự bịa quy định. Trả lời ngắn gọn bằng tiếng Việt."
)

def messages(question, ngay_hoi, ctx):
    user = f"Ngày hỏi: {ngay_hoi}\n\nCác đoạn luật:\n{ctx}\n\nCâu hỏi: {question}"
    return [{"role": "system", "content": SYSTEM_WITH_CONTEXT}, {"role": "user", "content": user}]

def chat_text(tokenizer, msgs, generation):
    kwargs = dict(tokenize=False, add_generation_prompt=generation)
    try:
        return tokenizer.apply_chat_template(msgs, enable_thinking=False, **kwargs)  # tắt chế độ suy nghĩ của Qwen3.x
    except TypeError:
        return tokenizer.apply_chat_template(msgs, **kwargs)

def token_ids(tokenizer, text):
    """Danh sách id phẳng. Bộ xử lý của Qwen3.5 (đa phương thức) trả input_ids dạng lô [[...]] cả khi chỉ có một chuỗi."""
    ids = tokenizer(text=text)["input_ids"]
    return list(ids[0]) if ids and isinstance(ids[0], (list, tuple)) else list(ids)

def n_tokens(tokenizer, text):
    return len(token_ids(tokenizer, text))

def encode(tokenizer, text):
    return tokenizer(text=text, return_tensors="pt").to("cuda")  # text=: tránh bộ xử lý ảnh của mô hình đa phương thức

def gb(x):
    return round(x / 2**30, 2)

def free_memory():
    gc.collect()
    torch.cuda.empty_cache()

# %%
BLOCK = re.compile(r"(?m)^\[\d+\] ")

def cap_context(tokenizer, ctx, budget):
    """Giữ nguyên từng đoạn "[n] ..." theo thứ hạng cho tới khi đủ `budget` token; dừng ở đoạn đầu tiên không vừa.
    Nếu ngay đoạn thứ nhất đã quá dài thì cắt đoạn đó theo token."""
    starts = [m.start() for m in BLOCK.finditer(ctx)] or [0]
    blocks = [ctx[a:b].strip("\n") for a, b in zip(starts, starts[1:] + [len(ctx)])]
    kept, used, cut_first = [], 0, False
    for block in blocks:
        n = n_tokens(tokenizer, block)
        if used + n > budget:
            if not kept:
                ids = token_ids(tokenizer, block)[:budget]
                kept.append(tokenizer.decode(ids, skip_special_tokens=True) + "\n[...đoạn này đã bị cắt bớt...]")
                used, cut_first = budget, True
            break
        kept.append(block)
        used += n
    info = {"so_doan_goc": len(blocks), "so_doan_giu": len(kept), "token_ngu_canh": used,
            "bi_cat": cut_first or len(kept) < len(blocks), "cat_doan_dau": cut_first}
    return "\n\n".join(kept), info

# %%
def generate(model, tokenizer, item, ctx):
    prompt = chat_text(tokenizer, messages(item["cau_hoi"], item["ngay_hoi"], ctx), generation=True)
    inputs = encode(tokenizer, prompt)
    n_in = inputs["input_ids"].shape[1]
    torch.cuda.synchronize()
    t = time.time()
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False, use_cache=True)
    torch.cuda.synchronize()
    dt = time.time() - t
    new = out[0][n_in:]
    text = tokenizer.decode(new, skip_special_tokens=True)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return {"prompt_tokens": int(n_in), "new_tokens": int(len(new)), "seconds": round(dt, 2), "answer": text}


def make_trainer(model, tokenizer, dataset):
    """SFTTrainer với vài cách gọi khác nhau giữa các phiên bản TRL."""
    from trl import SFTConfig, SFTTrainer
    import inspect
    base = dict(dataset_text_field="text", per_device_train_batch_size=TRAIN_BATCH,
                gradient_accumulation_steps=GRAD_ACCUM, num_train_epochs=1, learning_rate=LR,
                warmup_steps=2, logging_steps=5, optim="adamw_8bit", lr_scheduler_type="linear",
                fp16=not ENV["bf16"], bf16=ENV["bf16"], seed=SEED, output_dir="/kaggle/working/g4v2_ckpt",
                save_strategy="no", report_to="none")
    params = inspect.signature(SFTConfig.__init__).parameters
    base["max_seq_length" if "max_seq_length" in params else "max_length"] = MAX_SEQ_LEN
    cfg = SFTConfig(**{k: v for k, v in base.items() if k in params})
    tparams = inspect.signature(SFTTrainer.__init__).parameters
    tok_arg = "processing_class" if "processing_class" in tparams else "tokenizer"
    return SFTTrainer(model=model, train_dataset=dataset, args=cfg, **{tok_arg: tokenizer})


def load():
    free_memory()
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    model, tokenizer = FastLanguageModel.from_pretrained(model_name=MODEL, max_seq_length=MAX_SEQ_LEN,
                                                         dtype=None, load_in_4bit=True)
    return model, tokenizer, round(time.time() - t, 1), gb(torch.cuda.memory_allocated())

# %%
from datasets import Dataset

RESULTS = {"env": ENV, "bundle": META, "model": MODEL, "lan_1": LAN_1, "config": {
    "MAX_SEQ_LEN": MAX_SEQ_LEN, "MAX_NEW_TOKENS": MAX_NEW_TOKENS, "DIEU_CTX_TOKENS": DIEU_CTX_TOKENS,
    "LORA_R": LORA_R, "LORA_ALPHA": LORA_ALPHA, "TRAIN_BATCH": TRAIN_BATCH, "GRAD_ACCUM": GRAD_ACCUM, "LR": LR}}
ANSWERS = []

def save():
    with open("/kaggle/working/g4v2_results.json", "w", encoding="utf-8") as fp:
        json.dump(RESULTS, fp, ensure_ascii=False, indent=1)
    with open("/kaggle/working/g4v2_answers.jsonl", "w", encoding="utf-8") as fp:
        fp.writelines(json.dumps(a, ensure_ascii=False) + "\n" for a in ANSWERS)

# %%
# 1. Train QLoRA trên 100 mẫu đo thời gian
r = RESULTS["train"] = {}
model = tokenizer = trainer = None
try:
    if not RUN_TRAIN:
        raise RuntimeError("bỏ qua: RUN_TRAIN = False (số đo train ở reports/g4/g4v2_results.json)")
    model, tokenizer, r["load_seconds"], r["vram_after_load_gb"] = load()
    print("nạp xong:", r["load_seconds"], "giây,", r["vram_after_load_gb"], "GB")
    model = FastLanguageModel.get_peft_model(
        model, r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=SEED)
    texts = [chat_text(tokenizer, messages(s["cau_hoi"], "2026-10-01", s["ngu_canh"])
                       + [{"role": "assistant", "content": s["dap_an"]}], generation=False) for s in TIMING]
    lengths = [n_tokens(tokenizer, x) for x in texts]
    r["train_tokens_tb"], r["train_tokens_max"] = round(sum(lengths) / len(lengths)), max(lengths)
    trainer = make_trainer(model, tokenizer, Dataset.from_dict({"text": texts}))
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    stats = trainer.train()
    r["train_100_seconds"] = round(time.time() - t, 1)
    r["train_loss_cuoi"] = round(float(stats.training_loss), 4)
    r["vram_peak_train_gb"] = gb(torch.cuda.max_memory_allocated())
    r["trang_thai"] = "ok"
    print("train 100 mẫu:", r["train_100_seconds"], "giây, VRAM tối đa", r["vram_peak_train_gb"], "GB,",
          "token/mẫu tb", r["train_tokens_tb"], "max", r["train_tokens_max"])
except Exception as e:
    r["trang_thai"] = "loi"
    r["loi"] = f"{type(e).__name__}: {e}"
    r["traceback"] = traceback.format_exc()[-3000:]
    print("train:", r["loi"])
finally:
    del model, tokenizer, trainer
    free_memory()
save()

# %%
# 2. Sinh với ngữ cảnh theo Điều đã giới hạn, trên mô hình gốc nạp lại (không có adapter vừa train)
r = RESULTS["sinh_dieu"] = {"budget_token": DIEU_CTX_TOKENS}
model = tokenizer = None
try:
    model, tokenizer, r["load_seconds"], r["vram_after_load_gb"] = load()
    FastLanguageModel.for_inference(model)
    torch.cuda.reset_peak_memory_stats()
    rows = []
    for item in DEV:
        ctx, cap = cap_context(tokenizer, item["ngu_canh_dieu"], DIEU_CTX_TOKENS)
        cap["token_ngu_canh_goc"] = n_tokens(tokenizer, item["ngu_canh_dieu"])
        row = {"model": MODEL, "che_do": "dieu_gioi_han", "id": item["id"], "key": item["key"],
               "nhom_cau": item["nhom_cau"], "cau_hoi": item["cau_hoi"], "dap_an_chuan": item["dap_an"], **cap}
        try:
            row.update(generate(model, tokenizer, item, ctx))
        except torch.cuda.OutOfMemoryError as e:
            row["loi"] = f"OutOfMemoryError: {str(e)[:200]}"
            free_memory()
        rows.append(row)
        ANSWERS.append(row)
        print(item["id"], "ngữ cảnh", cap["token_ngu_canh_goc"], "->", cap["token_ngu_canh"], "token,",
              f"giữ {cap['so_doan_giu']}/{cap['so_doan_goc']} đoạn,", row.get("seconds", row.get("loi")))
        save()
    ok = [x for x in rows if "loi" not in x]
    sec, new = sum(x["seconds"] for x in ok), sum(x["new_tokens"] for x in ok)
    r.update({"so_cau": len(rows), "so_cau_ok": len(ok), "so_cau_loi": len(rows) - len(ok),
              "so_cau_bi_cat": sum(x["bi_cat"] for x in rows),
              "giay_moi_cau": round(sec / len(ok), 2) if ok else None,
              "token_moi_giay": round(new / sec, 1) if sec else None,
              "prompt_tokens_tb": round(sum(x["prompt_tokens"] for x in ok) / len(ok)) if ok else None,
              "prompt_tokens_max": max((x["prompt_tokens"] for x in ok), default=None),
              "new_tokens_tb": round(new / len(ok)) if ok else None,
              "so_cau_cham_tran": sum(x["new_tokens"] >= MAX_NEW_TOKENS for x in ok),
              "vram_peak_sinh_gb": gb(torch.cuda.max_memory_allocated()), "trang_thai": "ok"})
    print({k: v for k, v in r.items()})
except Exception as e:
    r["trang_thai"] = "loi"
    r["loi"] = f"{type(e).__name__}: {e}"
    r["traceback"] = traceback.format_exc()[-3000:]
    print("sinh LỖI:", r["loi"])
finally:
    del model, tokenizer
    free_memory()
save()

# %%
# 3. Ước tính giờ GPU cho toàn dự án
tr, sd = RESULTS["train"], RESULTS["sinh_dieu"]
est = RESULTS["uoc_tinh_gio_gpu"] = {}
a, b = LAN_1["sinh_khong_ngu_canh"]["giay_moi_cau"], LAN_1["sinh_khoan"]["giay_moi_cau"]
est["sinh_G7_ngu_canh_khoan"] = round(EST_EVAL_QUESTIONS * (2 * a + 2 * b) / 3600, 2)  # A, C không ngữ cảnh; B, D theo Khoản
if sd.get("giay_moi_cau"):
    est["sinh_G7_ngu_canh_dieu"] = round(EST_EVAL_QUESTIONS * (2 * a + 2 * sd["giay_moi_cau"]) / 3600, 2)
train_100 = tr.get("train_100_seconds") or LAN_2_TRAIN_100_SECONDS
if train_100:
    est["train_G6"] = round(train_100 * EST_TRAIN_SAMPLES / 100 * EST_EPOCHS / 3600, 2)
    est["tong_khoan"] = round(est["train_G6"] + est["sinh_G7_ngu_canh_khoan"], 2)
    est["ty_le_quota_tuan_khoan"] = round(est["tong_khoan"] / KAGGLE_WEEKLY_GPU_HOURS, 2)
save()
print(json.dumps(est, ensure_ascii=False, indent=1))
print("\nTải về: /kaggle/working/g4v2_results.json và /kaggle/working/g4v2_answers.jsonl (hoặc Save Version)")
