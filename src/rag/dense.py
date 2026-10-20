"""Vector bge-m3 và chỉ mục FAISS tìm vét cạn (`IndexFlatIP` trên vector đã chuẩn hóa = cosine).

Cache vector:
- Mỗi bộ mã hóa có một file riêng `<mã>.npz` trong thư mục cache. `<mã>` băm từ danh tính của bộ mã hóa
  (mô hình, revision thực sự nạp, `max_seq_length`, chuẩn hóa, kiểu số, số chiều). Danh tính cũng được ghi trong
  file và được kiểm khi nạp, nên đổi mô hình hay cấu hình không dùng nhầm vector cũ.
- File gồm khóa (SHA-256 của chữ), vector và danh tính, ghi ra file tạm rồi thay bằng một lần `os.replace`:
  bị ngắt lúc lưu thì file cũ còn nguyên. Khi nạp, cache lệch (số khóa khác số hàng, khóa trùng, sai số chiều,
  giá trị không hữu hạn) bị từ chối.
- Lưu dần trong lúc mã hóa, nên chạy dở thì chạy tiếp được.

Chỉ mục FAISS được tuần tự hóa thành byte và đọc/ghi bằng Python: `faiss.write_index`/`read_index` trên Windows không
mở được đường dẫn có dấu tiếng Việt. Chỉ mục khóa theo mã băm của file đoạn.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Callable, Protocol

import faiss
import numpy as np

MODEL = "BAAI/bge-m3"
MAX_SEQ_LENGTH = 8192  # bge-m3 nhận tới 8.192 token; đoạn theo Điều dài nhất khoảng 7.800 token


class Encoder(Protocol):
    identity: dict

    def __call__(self, texts: list[str]) -> np.ndarray: ...


class SentenceEncoder:
    """bge-m3, nạp từ snapshot trong cache Hugging Face (không tải mạng). Mặc định chạy CPU; demo G9 dùng GPU và ghim
    `revision` đúng bản đã tạo chỉ mục."""

    def __init__(self, model: str = MODEL, max_seq_length: int = MAX_SEQ_LENGTH, batch_size: int = 8,
                 device: str = "cpu", revision: str | None = None):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer

        path = Path(snapshot_download(model, revision=revision, local_files_only=True))
        self.st = SentenceTransformer(str(path), device=device)
        self.st.max_seq_length = max_seq_length
        self.batch_size = batch_size
        self.identity = {"model": model, "revision": path.name, "max_seq_length": max_seq_length,
                         "normalize": True, "dtype": "float32", "dim": self.st.get_embedding_dimension()}

    def __call__(self, texts: list[str]) -> np.ndarray:
        return self.st.encode(texts, batch_size=self.batch_size, normalize_embeddings=True,
                              convert_to_numpy=True, show_progress_bar=False).astype(np.float32)


def load_encoder(model: str = MODEL, max_seq_length: int = MAX_SEQ_LENGTH) -> SentenceEncoder:
    return SentenceEncoder(model, max_seq_length)


def _key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _identity_json(identity: dict) -> str:
    return json.dumps(identity, ensure_ascii=False, sort_keys=True)


def cache_path(cache_dir: Path, identity: dict) -> Path:
    return cache_dir / f"{hashlib.sha256(_identity_json(identity).encode()).hexdigest()[:16]}.npz"


def _load_cache(path: Path, identity: dict) -> tuple[list[str], np.ndarray | None]:
    if not path.exists():
        return [], None
    with np.load(path, allow_pickle=False) as z:
        meta, keys, vectors = json.loads(str(z["meta"])), [str(k) for k in z["keys"]], np.array(z["vectors"])
    if meta != identity:
        raise ValueError(f"{path} là cache của mô hình/cấu hình khác: {meta}")
    if (vectors.ndim != 2 or len(keys) != len(vectors) or len(set(keys)) != len(keys)
            or vectors.shape[1] != identity.get("dim", vectors.shape[1]) or not np.isfinite(vectors).all()):
        raise ValueError(f"{path} không nhất quán: {len(keys)} khóa, vector {vectors.shape}; xóa file để mã hóa lại")
    return keys, vectors


def _save_cache(path: Path, identity: dict, keys: list[str], vectors: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.stem + ".tmp.npz")
    with tmp.open("wb") as fp:
        np.savez(fp, meta=np.array(_identity_json(identity)), keys=np.array(keys), vectors=vectors)
    os.replace(tmp, path)


def embed(texts: list[str], cache_dir: Path, encode: Encoder, batch: int = 32, save_every: int = 256,
          log: Callable[[str], None] | None = None) -> np.ndarray:
    """Vector của từng chữ theo đúng thứ tự; chỉ mã hóa chữ chưa có trong cache (chữ ngắn trước)."""
    path = cache_path(cache_dir, encode.identity)
    keys, cached = _load_cache(path, encode.identity)
    blocks = [] if cached is None else [cached]
    pos = {k: i for i, k in enumerate(keys)}
    wanted = [_key(t) for t in texts]
    missing = sorted({k: t for k, t in zip(wanted, texts) if k not in pos}.items(), key=lambda kv: len(kv[1]))
    done, start, unsaved = 0, time.time(), 0
    for i in range(0, len(missing), batch):
        part = missing[i:i + batch]
        new = np.asarray(encode([t for _, t in part]), dtype=np.float32)
        if new.shape != (len(part), new.shape[1]):
            raise ValueError(f"bộ mã hóa trả {new.shape} cho {len(part)} chữ")
        blocks.append(new)
        for k, _ in part:
            pos[k] = len(keys)
            keys.append(k)
        done += len(part)
        unsaved += len(part)
        if unsaved >= save_every:
            blocks = [np.vstack(blocks)]
            _save_cache(path, encode.identity, keys, blocks[0])
            unsaved = 0
            if log:
                log(f"  mã hóa {done}/{len(missing)} đoạn, {time.time() - start:.0f} giây")
    if not blocks:
        return np.zeros((0, encode.identity.get("dim", 0)), dtype=np.float32)
    vectors = np.vstack(blocks)
    if unsaved:
        _save_cache(path, encode.identity, keys, vectors)
    return np.stack([vectors[pos[k]] for k in wanted]) if wanted else vectors[:0]


class DenseIndex:
    def __init__(self, ids: list[str], index: faiss.Index, meta: dict | None = None):
        self.ids = ids
        self.index = index
        self.meta = meta or {}  # nội dung meta.json khi nạp từ đĩa, gồm `bo_ma_hoa` đã tạo chỉ mục

    @classmethod
    def build(cls, ids: list[str], vectors: np.ndarray) -> "DenseIndex":
        if len(ids) != len(vectors):
            raise ValueError(f"{len(ids)} mã đoạn nhưng {len(vectors)} vector")
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(np.ascontiguousarray(vectors, dtype=np.float32))
        return cls(ids, index)

    def search(self, query: np.ndarray, k: int, mask: np.ndarray | None = None) -> list[tuple[int, float]]:
        """(chỉ số đoạn, cosine) của k đoạn gần nhất; `mask` False thì bỏ đoạn đó trước khi xếp hạng."""
        q = np.ascontiguousarray(query.reshape(1, -1), dtype=np.float32)
        params = None
        if mask is not None:
            allowed = np.flatnonzero(mask).astype(np.int64)
            if not len(allowed):
                return []
            params = faiss.SearchParameters(sel=faiss.IDSelectorBatch(allowed))
        scores, idx = self.index.search(q, min(k, self.index.ntotal), params=params)
        return [(int(i), float(s)) for i, s in zip(idx[0], scores[0]) if i >= 0]

    def save(self, folder: Path, chunks_sha256: str, info: dict | None = None) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "dense.faiss").write_bytes(faiss.serialize_index(self.index).tobytes())
        (folder / "dense_ids.json").write_text(json.dumps(self.ids, ensure_ascii=False), encoding="utf-8")
        meta = {"chunks_sha256": chunks_sha256, "so_vector": self.index.ntotal, "so_chieu": self.index.d, **(info or {})}
        (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, folder: Path, chunks_sha256: str) -> "DenseIndex":
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        if meta["chunks_sha256"] != chunks_sha256:
            raise ValueError(f"{folder} được build từ file đoạn khác; chạy lại scripts/build_index.py")
        ids = json.loads((folder / "dense_ids.json").read_text(encoding="utf-8"))
        index = faiss.deserialize_index(np.frombuffer((folder / "dense.faiss").read_bytes(), dtype=np.uint8))
        if index.ntotal != len(ids) or index.ntotal != meta["so_vector"]:
            raise ValueError(f"{folder}: {index.ntotal} vector nhưng {len(ids)} mã đoạn")
        return cls(ids, index, meta)
