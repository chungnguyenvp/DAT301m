"""Build chỉ mục BM25 và vector (bge-m3 + FAISS) cho các file đoạn trong `data/rag/`.

    py -3.13 scripts/build_index.py                     # cả hai cách cắt, cả BM25 và vector
    py -3.13 scripts/build_index.py --cut khoan --chi bm25

Đầu ra trong `data/rag/index/<cách cắt>/` (không commit): `bm25.pkl`, `dense.faiss`, `dense_ids.json`, `meta.json`.
Vector được cache theo chữ trong `data/rag/index/emb_cache/`, dùng chung cho hai cách cắt; chạy dở thì chạy lại
lệnh này là tiếp tục. Mã hóa toàn kho trên CPU mất khoảng 45 phút mỗi cách cắt.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from rag import bm25, dense  # noqa: E402

RAG = config.DATA / "rag"
INDEX = RAG / "index"


def log(msg: str) -> None:
    print(msg, flush=True)


def load_chunks(cut: str) -> tuple[list[dict], str]:
    path = RAG / f"chunks_{cut}.jsonl"
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    manifest = json.loads((RAG / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["files"][f"data/rag/chunks_{cut}.jsonl"]["sha256"] != sha:
        sys.exit(f"{path} không khớp data/rag/MANIFEST.json; chạy scripts/build_chunks.py")
    return [json.loads(line) for line in data.decode("utf-8").splitlines()], sha


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cut", choices=["khoan", "dieu", "all"], default="all")
    ap.add_argument("--chi", choices=["bm25", "dense", "all"], default="all")
    a = ap.parse_args()
    cuts = ["khoan", "dieu"] if a.cut == "all" else [a.cut]
    encode = None
    for cut in cuts:
        chunks, sha = load_chunks(cut)
        folder = INDEX / cut
        if a.chi in ("bm25", "all"):
            t = time.time()
            bm25.BM25Index.build(chunks).save(folder / "bm25.pkl", sha)
            log(f"{cut}: BM25 {len(chunks)} đoạn, {time.time() - t:.0f} giây")
        if a.chi in ("dense", "all"):
            if encode is None:
                t = time.time()
                encode = dense.load_encoder()
                log(f"nạp {dense.MODEL} (revision {encode.identity['revision']}): {time.time() - t:.0f} giây")
            t = time.time()
            vectors = dense.embed([c["text"] for c in chunks], INDEX / "emb_cache", encode, log=log)
            index = dense.DenseIndex.build([c["chunk_id"] for c in chunks], vectors)
            index.save(folder, sha, {"bo_ma_hoa": encode.identity})
            again = dense.DenseIndex.load(folder, sha)  # kiểm lưu–nạp ngay trên chính thư mục đích
            probe = vectors[: min(5, len(vectors))]
            if [again.search(v, 1)[0][0] for v in probe] != list(range(len(probe))):
                sys.exit(f"{folder}: chỉ mục nạp lại không trả đúng đoạn")
            log(f"{cut}: vector {vectors.shape}, {time.time() - t:.0f} giây")


if __name__ == "__main__":
    main()
