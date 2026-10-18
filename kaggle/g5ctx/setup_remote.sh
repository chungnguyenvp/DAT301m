#!/usr/bin/env bash
# Cài đặt và chạy thử G5 Task 4 trên máy Linux thuê. Cần có sẵn trong thư mục home (~):
#   g5ctx_bundle.zip, 04_g5_context.py, setup_remote.sh
# Dùng:  bash ~/setup_remote.sh          (cài đặt + chạy thử 10 mẫu)
#        bash ~/setup_remote.sh full     (chạy đầy đủ, ghi log vào ~/g5/run.log)
set -euo pipefail

G5="$HOME/g5"
MODE="${1:-setup}"

if [ "$MODE" = "full" ]; then
    cd "$G5"
    # shellcheck disable=SC1091
    source .venv/bin/activate
    echo ">> chạy đầy đủ, log: $G5/run.log (Ctrl+C không dừng được tiến trình nền; xem log bằng: tail -f $G5/run.log)"
    nohup python notebooks/04_g5_context.py > run.log 2>&1 &
    echo ">> pid $!  — theo dõi: tail -f $G5/run.log"
    exit 0
fi

echo "== 1. Kiểm tra máy =="
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv || { echo "Không thấy GPU (nvidia-smi lỗi)"; exit 1; }
df -h "$HOME" | tail -1
python3 --version

for f in g5ctx_bundle.zip 04_g5_context.py; do
    [ -f "$HOME/$f" ] || { echo "Thiếu $HOME/$f — hãy scp lên trước"; exit 1; }
done

echo "== 2. Giải nén =="
mkdir -p "$G5/notebooks"
cd "$G5"
if command -v unzip >/dev/null 2>&1; then
    unzip -qo "$HOME/g5ctx_bundle.zip"
else
    python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('.')" "$HOME/g5ctx_bundle.zip"
fi
cp -f "$HOME/04_g5_context.py" notebooks/
test -f src/rag/retrieve.py || { echo "Giải nén sai: không thấy src/rag/retrieve.py"; exit 1; }

echo "== 3. Môi trường Python =="
python3 -m venv .venv || { echo "Thiếu python3-venv: chạy 'sudo apt install -y python3-venv' rồi chạy lại"; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q pyvi rank_bm25 faiss-cpu sentence-transformers huggingface_hub tokenizers numpy
python - <<'EOF'
import torch
print("torch", torch.__version__, "| CUDA:", torch.cuda.is_available())
assert torch.cuda.is_available(), "torch không thấy GPU — gửi kết quả nvidia-smi để chọn bản torch CUDA"
EOF

echo "== 4. Tải model (khoảng 6,5 GB, đúng revision đã dựng chỉ mục) =="
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download("BAAI/bge-m3", revision="5617a9f61b028005a4858fdac845db406aefb181")
snapshot_download("BAAI/bge-reranker-v2-m3", revision="953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e")
print("tải xong 2 model")
EOF

echo "== 5. Chạy thử 10 mẫu =="
G5CTX_LIMIT=10 python notebooks/04_g5_context.py
rm -rf "$G5/kaggle/g5ctx/out_local"   # xoá kết quả chạy thử để bản đầy đủ không lẫn

echo
echo ">> Xong cài đặt và chạy thử. Chạy đầy đủ:  bash ~/setup_remote.sh full"
