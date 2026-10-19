#!/usr/bin/env bash
# G6: cài đặt và train QLoRA Qwen3.5-9B trên máy Linux thuê có GPU. Cần trong thư mục home (~):
#   g6_bundle.zip, setup_g6.sh
# Dùng:
#   bash ~/setup_g6.sh           cài đặt, tải Qwen3.5-9B (~19 GB), chạy thử 12 bước, in ước tính thời gian
#   bash ~/setup_g6.sh full      train đầy đủ ở nền (log: ~/g6/train.log); tắt SSH vẫn chạy
#   bash ~/setup_g6.sh resume    chạy tiếp từ checkpoint cuối nếu tiến trình bị ngắt
#   bash ~/setup_g6.sh status    xem tiến độ, GPU
#   bash ~/setup_g6.sh pack      nén kết quả thành ~/g6_ketqua.zip để tải về
set -euo pipefail

G6="$HOME/g6"
MODE="${1:-setup}"
MODEL="${G6_MODEL:-Qwen/Qwen3.5-9B}"

activate() { cd "$G6"; source .venv/bin/activate; }   # shellcheck disable=SC1091

case "$MODE" in
full|resume)
    activate
    if pgrep -f "scripts/g6_train.py" >/dev/null; then echo "Đang có tiến trình train chạy rồi"; exit 1; fi
    if [ "$MODE" = resume ]; then export G6_RESUME=1; fi
    nohup python scripts/g6_train.py >> train.log 2>&1 &
    echo ">> đã chạy nền, pid $!"
    echo ">> xem tiến độ:  bash ~/setup_g6.sh status   (hoặc: tail -f $G6/train.log)"
    exit 0 ;;
status)
    cd "$G6"
    pgrep -f "scripts/g6_train.py" >/dev/null && echo ">> ĐANG CHẠY" || echo ">> không có tiến trình train"
    grep -E "^\[[0-9]+/[0-9]+\]|eval_loss|XONG|Error|LỖI" train.log 2>/dev/null | tail -n 8 || true
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv
    exit 0 ;;
pack)
    activate
    python - <<'EOF'
import zipfile
from pathlib import Path
out = Path("out_g6")
assert (out / "adapter").exists(), "chưa có out_g6/adapter: train chưa xong"
dst = Path.home() / "g6_ketqua.zip"
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(out.rglob("*")):
        if p.is_file() and "checkpoints" not in p.parts:
            zf.write(p, p.as_posix())
    for extra in ("train.log", "smoke.log"):
        if Path(extra).exists():
            zf.write(extra, f"out_g6/{extra}")
print("->", dst, round(dst.stat().st_size / 1e6, 1), "MB")
EOF
    exit 0 ;;
setup) ;;
*) echo "Không hiểu '$MODE'. Dùng: setup | full | resume | status | pack"; exit 1 ;;
esac

echo "== 1. Kiểm tra máy =="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || { echo "Không thấy GPU (nvidia-smi lỗi)"; exit 1; }
df -h "$HOME" | tail -1
free -g | head -2
python3 --version
[ -f "$HOME/g6_bundle.zip" ] || { echo "Thiếu $HOME/g6_bundle.zip — hãy scp lên trước"; exit 1; }

echo "== 2. Giải nén =="
mkdir -p "$G6"
cd "$G6"
python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('.')" "$HOME/g6_bundle.zip"
test -f scripts/g6_train.py || { echo "Giải nén sai: không thấy scripts/g6_train.py"; exit 1; }
python3 - <<'EOF'
import hashlib, json
meta = json.load(open("meta.json", encoding="utf-8"))
bad = [n for n, h in meta["file"].items() if hashlib.sha256(open(n, "rb").read()).hexdigest() != h]
assert not bad, f"file hỏng khi chép: {bad}"
print("mã băm gói: khớp", len(meta["file"]), "file")
EOF

echo "== 3. Môi trường Python (Unsloth kéo theo torch, transformers, peft, bitsandbytes) =="
python3 -m venv .venv || { echo "Thiếu python3-venv: chạy 'sudo apt install -y python3-venv' rồi chạy lại"; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q unsloth matplotlib
python - <<'EOF'
import torch
cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None
print("torch", torch.__version__, "| CUDA", torch.version.cuda, "| GPU:", torch.cuda.is_available(), cap)
assert torch.cuda.is_available(), "torch không thấy GPU"
arch = torch.cuda.get_arch_list()
need = f"sm_{cap[0]}{cap[1]}"
assert need in arch or any(a.startswith(f"sm_{cap[0]}") for a in arch), \
    f"bản torch này không có mã cho {need} (có {arch}): cài lại torch bản CUDA mới hơn, xem HUONG_DAN.md"
x = torch.randn(256, 256, device="cuda", dtype=torch.bfloat16)
print("phép nhân bf16 trên GPU:", float((x @ x).float().abs().mean()) > 0, "| bf16:", torch.cuda.is_bf16_supported())
import bitsandbytes as bnb, unsloth  # noqa: F401
print("bitsandbytes", bnb.__version__, "| unsloth", unsloth.__version__)
EOF

echo "== 4. Tải mô hình $MODEL (khoảng 19 GB) =="
G6_MODEL="$MODEL" python - <<'EOF'
import os
from huggingface_hub import snapshot_download
path = snapshot_download(os.environ["G6_MODEL"])
print("tải xong:", path)
EOF

echo "== 5. Chạy thử 12 bước (khoảng 10–15 phút: nạp mô hình, train, đánh giá, sinh 2 câu) =="
G6_SMOKE=1 python scripts/g6_train.py 2>&1 | tee smoke.log || true
grep -q "XONG" smoke.log || { echo ">> CHẠY THỬ LỖI: gửi file ~/g6/smoke.log để kiểm"; exit 1; }
echo
grep "ƯỚC TÍNH" smoke.log || true
echo ">> Chạy thử xong. Train đầy đủ:  bash ~/setup_g6.sh full"
