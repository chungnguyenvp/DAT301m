# %% [markdown]
# # G7 — Sinh câu trả lời A/B/C/D trên 270 câu eval
#
# Notebook chạy `scripts/g7_generate.py` trong gói `g7_bundle.zip`:
#
# | Lượt | Mô hình | Ngữ cảnh | Số câu |
# |---|---|---|---|
# | A | Qwen3.5-9B gốc | không | 270 |
# | B | gốc | 5 đoạn theo Khoản của G3 (lọc hiệu lực tại ngày hỏi) | 270 |
# | C | gốc + adapter LoRA G6 | không | 270 |
# | D | gốc + adapter | như B | 270 |
# | B_boloc, D_boloc | như B, D | 5 đoạn khi **bỏ** lọc hiệu lực (RQ3) | 40 câu sửa đổi |
#
# Mô hình nạp 4-bit một lần, gắn adapter; lượt A/B tắt adapter. Prompt dựng giống hệt lúc train G6. Sinh greedy, tối
# đa 512 token. Máy có 2 GPU (Kaggle *T4 x2*) thì chạy 2 tiến trình song song, mỗi GPU một nửa số việc.
#
# **Cài đặt Kaggle:** Accelerator *GPU T4 x2*; Internet *On*; Add Input → dataset tạo từ `g7_bundle.zip`. Rồi
# *Save Version → Save & Run All (Commit)*. Ước tính khoảng 3–4 giờ với 2 GPU (6–7 giờ với 1 GPU).
#
# **Kết quả** (tab *Output*): `out_g7/g7_answers.jsonl` (mọi câu trả lời), `out_g7/g7_summary.json` (đủ hay thiếu,
# thời gian, số câu chạm giới hạn token), log từng GPU. Nếu `g7_summary.json` báo `"du": false` (phiên bị ngắt), tạo
# dataset từ Output của version này, Add Input cả nó, chạy lại: notebook bỏ qua câu đã có và chỉ làm phần còn thiếu.
#
# **G8:** cùng notebook này chạy được gói `g8_bundle.zip`. Gói ghi các lượt cần chạy trong `meta.json`
# (`luot_chay`: D_g8, B_g8, với ngữ cảnh mở rộng lên Điều), nên chỉ cần Add Input gói G8 thay cho gói G7.

# %%
MAX_HOURS = 11.0   # dừng sạch trước giới hạn 12 giờ của một phiên Kaggle
LIMIT = 0          # >0: chỉ chạy bấy nhiêu câu đầu mỗi lượt, để thử nhanh

# %%
import glob, hashlib, json, os, subprocess, sys, time, zipfile
from pathlib import Path

ON_KAGGLE = os.path.exists("/kaggle/input")
ON_COLAB = "google.colab" in sys.modules
INPUT = Path("/kaggle/input") if ON_KAGGLE else Path("/content") if ON_COLAB else Path.cwd()
WORK = Path("/kaggle/working") if ON_KAGGLE else Path("/content") if ON_COLAB else Path.cwd()
T0 = time.time()
if ON_KAGGLE or ON_COLAB:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "unsloth"], check=True)
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout)

# %%
def find_root():
    """Thư mục gốc của gói: dataset Kaggle đã giải nén, hoặc giải nén file zip."""
    for p in glob.glob(f"{INPUT}/**/scripts/g7_generate.py", recursive=True):
        root = Path(p).parents[1]
        if (root / "data" / "g7" / "items.jsonl").exists():
            return root
    z = glob.glob(f"{INPUT}/**/g7_bundle.zip", recursive=True)
    assert z, f"Không thấy gói G7 trong {INPUT}: hãy Add Input dataset tạo từ g7_bundle.zip"
    zipfile.ZipFile(z[0]).extractall(WORK / "g7")
    return WORK / "g7"

ROOT = find_root()
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
bad = [n for n, h in META["file"].items() if hashlib.sha256((ROOT / n).read_bytes()).hexdigest() != h]
assert not bad, f"file trong gói bị hỏng: {bad}"
OUT = WORK / "out_g7"
OUT.mkdir(parents=True, exist_ok=True)
PREV = sorted({str(Path(p).parent) for pat in ("answers_shard*.jsonl", "g7_answers.jsonl")
               for p in glob.glob(f"{INPUT}/**/{pat}", recursive=True) if not str(p).startswith(str(OUT))})
RUNS_ARG = ["--runs", ",".join(META["luot_chay"])] if META.get("luot_chay") else []   # gói G8 chọn lượt
N_GPU = max(1, subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.count("GPU "))
print("gói:", ROOT, "| mã băm khớp", len(META["file"]), "file | GPU:", N_GPU, "| lượt:", META.get("luot_chay", "G7"))
print("kết quả phiên trước:", PREV or "không có")
print(json.dumps({k: META[k] for k in ("so_viec", "token_prompt", "g6")}, ensure_ascii=False))

# %%
# Tải mô hình gốc trước (khoảng 19 GB), để các tiến trình con không tải chồng lên nhau.
from huggingface_hub import snapshot_download
t = time.time()
print("mô hình:", snapshot_download(META["mo_hinh"], revision=META["revision"]), f"({time.time() - t:.0f} giây)")

# %%
SCRIPT = str(ROOT / "scripts" / "g7_generate.py")

def tail(path, n=1):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip().splitlines()[-n:]
    except FileNotFoundError:
        return []

PROCS = []
for i in range(N_GPU):
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": str(i), "TOKENIZERS_PARALLELISM": "false",
           "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}
    hours = max(0.5, MAX_HOURS - (time.time() - T0) / 3600)
    cmd = [sys.executable, "-u", SCRIPT, "--out", str(OUT), "--shard", str(i), "--nshards", str(N_GPU),
           "--max-hours", f"{hours:.2f}", "--limit", str(LIMIT), *RUNS_ARG, "--prev", *PREV]
    log_path = OUT / f"worker{i}.log"
    p = subprocess.Popen(cmd, stdout=open(log_path, "w", encoding="utf-8"), stderr=subprocess.STDOUT, env=env,
                         cwd=str(WORK))
    PROCS.append((p, log_path))
    print(f"GPU {i}: pid {p.pid}, log {log_path}")
    # Đợi tiến trình này nạp xong mô hình rồi mới chạy tiến trình sau, tránh hai bản 19 GB cùng đọc vào RAM.
    t = time.time()
    while i < N_GPU - 1 and p.poll() is None and time.time() - t < 1200:
        if any("nạp xong" in line for line in tail(log_path, 50)):
            break
        time.sleep(10)
    print("\n".join(tail(log_path, 3)))

# %%
# Theo dõi đến khi các tiến trình xong (in tiến độ mỗi 5 phút).
while any(p.poll() is None for p, _ in PROCS):
    time.sleep(300)
    for i, (p, log_path) in enumerate(PROCS):
        print(f"GPU {i}:", (tail(log_path) or ["(chưa có log)"])[0][:200])
for i, (p, log_path) in enumerate(PROCS):
    print(f"GPU {i}: mã thoát {p.returncode}")
    if p.returncode:
        print("\n".join(tail(log_path, 40)))

# %%
subprocess.run([sys.executable, SCRIPT, "--out", str(OUT), "--merge", *RUNS_ARG, "--prev", *PREV], check=True)
SUMMARY = json.loads((OUT / "g7_summary.json").read_text(encoding="utf-8"))
print("ĐỦ" if SUMMARY["du"] else "CHƯA ĐỦ: Add Input Output của version này rồi chạy lại để làm tiếp",
      f"| tổng thời gian {(time.time() - T0) / 3600:.2f} giờ")

# %%
# Xem nhanh một câu thường và một câu sửa đổi ở mọi lượt.
ANS = [json.loads(line) for line in open(OUT / "g7_answers.jsonl", encoding="utf-8")]
items = {x["uid"]: x for x in map(json.loads, open(ROOT / "data" / "g7" / "items.jsonl", encoding="utf-8"))}
for nhom in ("thuong", "sua_doi"):
    uid = next((r["uid"] for r in ANS if r["nhom_cau"] == nhom and not r.get("loi")), None)
    if uid is None:
        continue
    print("=" * 100, "\n", uid, "|", items[uid]["cau_hoi"])
    for r in ANS:
        if r["uid"] == uid:
            print(f"--- {r['run']} ({r.get('giay')} giây, {r.get('so_token_moi')} token):\n{(r.get('tra_loi') or r.get('loi'))[:600]}")
