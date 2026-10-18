# %% [markdown]
# # G4 — Chạy thử trên Kaggle để chọn mô hình
#
# Notebook này đo xem GPU miễn phí của Kaggle chạy nổi mô hình nào cho G5–G7 của dự án hỏi đáp luật giao thông.
# Với mỗi mô hình trong `MODELS`:
#
# 1. Nạp dạng 4-bit (QLoRA, Unsloth) → đo VRAM.
# 2. Sinh câu trả lời cho 20 câu **dev** theo ba cách: không ngữ cảnh, ngữ cảnh theo Khoản, ngữ cảnh theo Điều
#    → đo tốc độ sinh, VRAM lớn nhất.
# 3. Train QLoRA 1 vòng trên 100 mẫu **chỉ để đo thời gian** → đo thời gian, VRAM.
# 4. Ước tính tổng giờ GPU cho G6 (train) và G7 (sinh A/B/C/D trên 270 câu).
#
# Kết quả: `/kaggle/working/g4_results.json` và `/kaggle/working/g4_answers.jsonl`. Tải hai file này về, đặt vào
# `reports/g4/` của dự án.
#
# **Cài đặt Kaggle:** Settings → Accelerator: *GPU T4 x2* (hoặc P100); Internet: *On*. Add Input → dataset chứa
# `g4_bundle.zip` (đã giải nén). Rồi *Run All*.

# %%
# Cấu hình. Đổi danh sách mô hình ở đây nếu một mô hình không tải được.
MODELS = ["Qwen/Qwen3.5-9B", "Qwen/Qwen3.5-4B"]
MAX_SEQ_LEN = 4096          # ngữ cảnh theo Điều khoảng 2.300 token + prompt + câu trả lời
MAX_NEW_TOKENS = 384
LORA_R, LORA_ALPHA = 16, 16
TRAIN_BATCH, GRAD_ACCUM, LR = 2, 4, 2e-4
SEED = 42
# Giả định để ước tính giờ GPU cho toàn dự án (G6, G7)
EST_TRAIN_SAMPLES, EST_EPOCHS = 2000, 2
EST_EVAL_QUESTIONS = 270     # cả bộ eval_v1
KAGGLE_WEEKLY_GPU_HOURS = 30  # quota thường gặp; Kaggle có thể thay đổi

# %%
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"   # Unsloth dùng 1 GPU; tránh lỗi khi máy có T4 x2
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# %%
# Cài thư viện. Kaggle đã có torch; Unsloth kéo theo transformers, trl, peft, bitsandbytes phù hợp.
!pip install -q unsloth

# %%
import unsloth  # phải nạp trước transformers để Unsloth vá đúng
from unsloth import FastLanguageModel
import gc, glob, json, math, platform, re, subprocess, time, traceback
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
# Dữ liệu: tìm file trong /kaggle/input (dataset đã giải nén), hoặc giải nén g4_bundle.zip nếu chỉ có file zip.
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
SYSTEM_NO_CONTEXT = (
    "Bạn là trợ lý pháp luật giao thông đường bộ Việt Nam. Trả lời theo quy định đang có hiệu lực, nêu căn cứ nếu "
    "biết; nếu không chắc chắn thì nói rõ. Trả lời ngắn gọn bằng tiếng Việt."
)

def messages(question, ngay_hoi, ctx):
    if ctx:
        user = f"Ngày hỏi: {ngay_hoi}\n\nCác đoạn luật:\n{ctx}\n\nCâu hỏi: {question}"
        return [{"role": "system", "content": SYSTEM_WITH_CONTEXT}, {"role": "user", "content": user}]
    return [{"role": "system", "content": SYSTEM_NO_CONTEXT},
            {"role": "user", "content": f"Ngày hỏi: {ngay_hoi}\n\nCâu hỏi: {question}"}]

def chat_text(tokenizer, msgs, generation):
    kwargs = dict(tokenize=False, add_generation_prompt=generation)
    try:
        return tokenizer.apply_chat_template(msgs, enable_thinking=False, **kwargs)  # tắt chế độ suy nghĩ của Qwen3.x
    except TypeError:
        return tokenizer.apply_chat_template(msgs, **kwargs)

def encode(tokenizer, text):
    return tokenizer(text=text, return_tensors="pt").to("cuda")  # text=: tránh bộ xử lý ảnh của mô hình đa phương thức

def gb(x):
    return round(x / 2**30, 2)

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
                fp16=not ENV["bf16"], bf16=ENV["bf16"], seed=SEED, output_dir="/kaggle/working/g4_ckpt",
                save_strategy="no", report_to="none")
    params = inspect.signature(SFTConfig.__init__).parameters
    base["max_seq_length" if "max_seq_length" in params else "max_length"] = MAX_SEQ_LEN
    cfg = SFTConfig(**{k: v for k, v in base.items() if k in params})
    tparams = inspect.signature(SFTTrainer.__init__).parameters
    tok_arg = "processing_class" if "processing_class" in tparams else "tokenizer"
    return SFTTrainer(model=model, train_dataset=dataset, args=cfg, **{tok_arg: tokenizer})

# %%
from datasets import Dataset

RESULTS = {"env": ENV, "bundle": META, "config": {
    "MAX_SEQ_LEN": MAX_SEQ_LEN, "MAX_NEW_TOKENS": MAX_NEW_TOKENS, "LORA_R": LORA_R, "LORA_ALPHA": LORA_ALPHA,
    "TRAIN_BATCH": TRAIN_BATCH, "GRAD_ACCUM": GRAD_ACCUM, "LR": LR}, "models": {}}
ANSWERS = []

for name in MODELS:
    r = {"model": name}
    RESULTS["models"][name] = r
    model = tokenizer = trainer = None
    try:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        t = time.time()
        model, tokenizer = FastLanguageModel.from_pretrained(model_name=name, max_seq_length=MAX_SEQ_LEN,
                                                             dtype=None, load_in_4bit=True)
        r["load_seconds"] = round(time.time() - t, 1)
        r["vram_after_load_gb"] = gb(torch.cuda.memory_allocated())
        print(name, "nạp xong:", r["load_seconds"], "giây,", r["vram_after_load_gb"], "GB")

        # 2. Sinh câu trả lời
        FastLanguageModel.for_inference(model)
        torch.cuda.reset_peak_memory_stats()
        for mode, field in (("khong_ngu_canh", None), ("khoan", "ngu_canh_khoan"), ("dieu", "ngu_canh_dieu")):
            rows = []
            for item in DEV:
                g = generate(model, tokenizer, item, item[field] if field else None)
                rows.append(g)
                ANSWERS.append({"model": name, "che_do": mode, "id": item["id"], "key": item["key"],
                                "nhom_cau": item["nhom_cau"], "cau_hoi": item["cau_hoi"], "dap_an_chuan": item["dap_an"],
                                **g})
            sec, new = sum(x["seconds"] for x in rows), sum(x["new_tokens"] for x in rows)
            r[f"sinh_{mode}"] = {"so_cau": len(rows), "giay_moi_cau": round(sec / len(rows), 2),
                                 "token_moi_giay": round(new / sec, 1) if sec else None,
                                 "prompt_tokens_tb": round(sum(x["prompt_tokens"] for x in rows) / len(rows)),
                                 "new_tokens_tb": round(new / len(rows))}
            print(name, mode, r[f"sinh_{mode}"])
        r["vram_peak_sinh_gb"] = gb(torch.cuda.max_memory_allocated())

        # 3. Train QLoRA trên 100 mẫu đo thời gian
        FastLanguageModel.for_training(model)
        model = FastLanguageModel.get_peft_model(
            model, r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0, bias="none",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            use_gradient_checkpointing="unsloth", random_state=SEED)
        texts = [chat_text(tokenizer, messages(s["cau_hoi"], "2026-10-01", s["ngu_canh"])
                           + [{"role": "assistant", "content": s["dap_an"]}], generation=False) for s in TIMING]
        r["train_tokens_tb"] = round(sum(len(tokenizer(text=x)["input_ids"]) for x in texts) / len(texts))
        trainer = make_trainer(model, tokenizer, Dataset.from_dict({"text": texts}))
        torch.cuda.reset_peak_memory_stats()
        t = time.time()
        stats = trainer.train()
        r["train_100_seconds"] = round(time.time() - t, 1)
        r["train_loss_cuoi"] = round(float(stats.training_loss), 4)
        r["vram_peak_train_gb"] = gb(torch.cuda.max_memory_allocated())
        print(name, "train 100 mẫu:", r["train_100_seconds"], "giây, VRAM", r["vram_peak_train_gb"], "GB")

        # 4. Ước tính giờ GPU cho toàn dự án
        train_h = r["train_100_seconds"] * EST_TRAIN_SAMPLES / 100 * EST_EPOCHS / 3600
        gen_h = EST_EVAL_QUESTIONS * (2 * r["sinh_khong_ngu_canh"]["giay_moi_cau"]  # A, C
                                      + 2 * r["sinh_khoan"]["giay_moi_cau"]) / 3600  # B, D theo Khoản
        gen_dieu_h = EST_EVAL_QUESTIONS * (2 * r["sinh_khong_ngu_canh"]["giay_moi_cau"]
                                           + 2 * r["sinh_dieu"]["giay_moi_cau"]) / 3600
        r["uoc_tinh_gio_gpu"] = {"train_G6": round(train_h, 2), "sinh_G7_ngu_canh_khoan": round(gen_h, 2),
                                 "sinh_G7_ngu_canh_dieu": round(gen_dieu_h, 2),
                                 "tong_khoan": round(train_h + gen_h, 2),
                                 "ty_le_quota_tuan_khoan": round((train_h + gen_h) / KAGGLE_WEEKLY_GPU_HOURS, 2)}
        print(name, "ước tính:", r["uoc_tinh_gio_gpu"])
        r["trang_thai"] = "ok"
    except Exception as e:
        r["trang_thai"] = "loi"
        r["loi"] = f"{type(e).__name__}: {e}"
        r["traceback"] = traceback.format_exc()[-3000:]
        print(name, "LỖI:", r["loi"])
    finally:
        del model, tokenizer, trainer
        gc.collect()
        torch.cuda.empty_cache()
    with open("/kaggle/working/g4_results.json", "w", encoding="utf-8") as fp:  # ghi sau mỗi mô hình
        json.dump(RESULTS, fp, ensure_ascii=False, indent=1)
    with open("/kaggle/working/g4_answers.jsonl", "w", encoding="utf-8") as fp:
        fp.writelines(json.dumps(a, ensure_ascii=False) + "\n" for a in ANSWERS)

# %%
# Tóm tắt
for name, r in RESULTS["models"].items():
    if r.get("trang_thai") != "ok":
        print(f"{name}: LỖI — {r.get('loi')}")
        continue
    print(f"{name}: VRAM nạp {r['vram_after_load_gb']} GB, sinh tối đa {r['vram_peak_sinh_gb']} GB, "
          f"train tối đa {r['vram_peak_train_gb']} GB")
    for mode in ("khong_ngu_canh", "khoan", "dieu"):
        s = r[f"sinh_{mode}"]
        print(f"   sinh {mode:15s}: {s['giay_moi_cau']} giây/câu, {s['token_moi_giay']} token/giây, prompt {s['prompt_tokens_tb']} token")
    print(f"   train 100 mẫu: {r['train_100_seconds']} giây; ước tính G6+G7 (Khoản): {r['uoc_tinh_gio_gpu']['tong_khoan']} giờ GPU "
          f"= {r['uoc_tinh_gio_gpu']['ty_le_quota_tuan_khoan']:.0%} quota tuần")
print("\nTải về: /kaggle/working/g4_results.json và /kaggle/working/g4_answers.jsonl")
