# %% [markdown]
# # G9 — Demo hỏi đáp luật giao thông theo ngày hỏi (Gradio)
#
# Notebook chạy `scripts/g9_demo.py` trong gói `g9_bundle.zip`: retriever của G3 (BM25 + bge-m3 → RRF → reranker, lọc
# hiệu lực tại ngày hỏi), tùy chọn mở rộng lên Điều của G8, và Qwen3.5-9B 4-bit với adapter LoRA của G6. Giao diện cho
# nhập câu hỏi và ngày hỏi, chọn D (LoRA + RAG), B (mô hình gốc + RAG) hoặc so sánh cả hai, bật/tắt lọc hiệu lực, và
# hiện các đoạn luật đã dùng cùng ngày hiệu lực.
#
# **Cài đặt Kaggle:** Accelerator *GPU T4 x2*; Internet *On*; Add Input → dataset tạo từ `g9_bundle.zip`.
#
# **Cách chạy:** đây là notebook **tương tác**. Bấm *Run All* ngay trong trình soạn (KHÔNG dùng *Save Version*). Ô cuối
# in ra link `https://....gradio.live`: mở link đó trên trình duyệt hoặc điện thoại để hỏi. Ô cuối chạy mãi để giữ demo
# sống; muốn tắt thì bấm dừng ô (Interrupt). Giữ tab Kaggle mở trong lúc demo.
#
# **Thời gian:** cài đặt + tải mô hình khoảng 15–20 phút lần đầu, nạp mô hình khoảng 1–2 phút. Sau đó mỗi câu: tìm kiếm
# vài giây, D khoảng 10–15 giây, B khoảng 30 giây (số liệu G7 trên T4).

# %%
SHARE = True   # True: tạo link công khai gradio.live (link sống tới khi dừng ô cuối, tối đa khoảng 72 giờ)

# %%
import glob, hashlib, json, os, re, subprocess, sys, time, zipfile
from pathlib import Path

ON_KAGGLE = os.path.exists("/kaggle/input")
ON_COLAB = "google.colab" in sys.modules
INPUT = Path("/kaggle/input") if ON_KAGGLE else Path("/content") if ON_COLAB else Path.cwd()
WORK = Path("/kaggle/working") if ON_KAGGLE else Path("/content") if ON_COLAB else Path.cwd()
T0 = time.time()
if ON_KAGGLE or ON_COLAB:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "unsloth"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gradio", "pyvi", "rank_bm25", "faiss-cpu"], check=True)
print(subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout)
# Kiểm các thư viện nạp được cùng nhau (gradio không làm hỏng bản transformers/unsloth vừa cài).
print(subprocess.run([sys.executable, "-c", "import unsloth, transformers, gradio, faiss, pyvi, rank_bm25, sentence_transformers;"
                      "print('unsloth', unsloth.__version__, '| transformers', transformers.__version__,"
                      "'| gradio', gradio.__version__, '| faiss', faiss.__version__)"],
                     capture_output=True, text=True).stdout[-500:])

# %%
def find_root():
    """Thư mục gốc của gói: dataset Kaggle đã giải nén, hoặc giải nén file zip."""
    for p in glob.glob(f"{INPUT}/**/scripts/g9_demo.py", recursive=True):
        root = Path(p).parents[1]
        if (root / "meta.json").exists() and (root / "data" / "g9" / "prompts.json").exists():
            return root
    z = glob.glob(f"{INPUT}/**/g9_bundle.zip", recursive=True)
    assert z, f"Không thấy gói G9 trong {INPUT}: hãy Add Input dataset tạo từ g9_bundle.zip"
    zipfile.ZipFile(z[0]).extractall(WORK / "g9_bundle")
    return WORK / "g9_bundle"

ROOT = find_root()
META = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
bad = [n for n, h in META["file"].items() if hashlib.sha256((ROOT / n).read_bytes()).hexdigest() != h]
assert not bad, f"file trong gói bị hỏng: {bad}"
print("gói:", ROOT, "| mã băm khớp", len(META["file"]), "file | mô hình:", json.dumps(META["mo_hinh"], ensure_ascii=False))

# %%
# Tải trước ba mô hình đúng revision (Qwen khoảng 19 GB, bge-m3 khoảng 4,5 GB, reranker khoảng 2,3 GB). Tải đủ mọi file:
# tiến trình tìm kiếm nạp offline (`local_files_only`), và huggingface_hub coi bản thiếu file (ví dụ bỏ onnx/) là tải dở.
from huggingface_hub import snapshot_download
for name, rev in META["mo_hinh"].items():
    t = time.time()
    path = snapshot_download(name, revision=rev)
    print(f"{name}@{rev[:8]}: {path} ({time.time() - t:.0f} giây)")

# %%
# Chạy demo ở một tiến trình riêng và đợi đến khi có link.
G9_WORK = WORK / "g9"
G9_WORK.mkdir(parents=True, exist_ok=True)
LOG = G9_WORK / "demo.log"
env = {**os.environ, "TOKENIZERS_PARALLELISM": "false", "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}
cmd = [sys.executable, "-u", str(ROOT / "scripts" / "g9_demo.py"), "--work", str(G9_WORK), *(["--share"] if SHARE else [])]
PROC = subprocess.Popen(cmd, stdout=open(LOG, "w", encoding="utf-8"), stderr=subprocess.STDOUT, env=env, cwd=str(WORK))

def log_text():
    return LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""

URL, shown, t = None, 0, time.time()
while PROC.poll() is None and time.time() - t < 1800:
    text = log_text()
    lines = text.splitlines()
    for line in lines[shown:]:
        if not line.startswith(("Loading", "\r")) and "it/s]" not in line:
            print(line[:300])
    shown = len(lines)
    m = re.search(r"https://[\w.-]+\.gradio\.live", text) or (None if SHARE else re.search(r"http://[\d.:]+", text))
    if m:
        URL = m.group(0)
        break
    time.sleep(5)
if URL:
    print("\n" + "=" * 80 + f"\nDEMO SẴN SÀNG: {URL}\n" + "=" * 80 + f"\n(sau {(time.time() - T0) / 60:.1f} phút từ đầu notebook)")
else:
    print("CHƯA CÓ LINK. Mã thoát:", PROC.poll(), "\n--- cuối log ---\n" + "\n".join(log_text().splitlines()[-40:]))

# %%
# Giữ demo sống. Mỗi 10 phút in lại link và dòng log cuối. Bấm dừng ô này để tắt demo.
try:
    n = 0
    while PROC.poll() is None:
        time.sleep(60)
        n += 1
        if n % 10 == 0:
            last = (log_text().strip().splitlines() or [""])[-1][:200]
            print(f"{time.strftime('%H:%M')} vẫn chạy | {URL} | {last}", flush=True)
    print("Demo đã dừng, mã thoát", PROC.returncode, "\n" + "\n".join(log_text().splitlines()[-40:]))
except KeyboardInterrupt:
    PROC.terminate()
    print("Đã tắt demo.")
