"""Luồng tìm kiếm: BM25 + vector → gộp RRF → reranker → top-k, có lọc hiệu lực tại ngày hỏi.

Lọc hiệu lực được áp bằng `mask` ngay trong BM25 và vector, tức trước khi xếp hạng, trước khi gộp và trước reranker.
Nhờ vậy top-k luôn đủ đoạn có hiệu lực, và reranker không tốn công chấm đoạn đã hết hiệu lực.
Mỗi bước là một hàm riêng (`fuse_rrf`, `live_mask`, `Reranker.score`); G8 có thể chèn thêm bước mở rộng tham chiếu.

Điểm reranker được cache trên đĩa theo (câu hỏi, chữ của đoạn) và theo danh tính mô hình, nên các cấu hình ablation
dùng lại được điểm của nhau.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

import numpy as np

from lawproc import config
from rag import chunking

RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
RERANK_MAX_LENGTH = 1024


@dataclass(frozen=True)
class Config:
    bm25_k: int = 50
    dense_k: int = 50
    rrf_k: int = 60
    dung_bm25: bool = True
    dung_vector: bool = True
    loc_hieu_luc: bool = True
    rerank_k: int = 20  # 0 = không dùng reranker
    top_k: int = 5


@dataclass
class Hit:
    chunk: dict
    rrf: float
    rrf_rank: int
    rerank: float | None = None


def fuse_rrf(rank_lists: list[list[int]], rrf_k: int) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion: điểm = Σ 1 / (rrf_k + hạng), hạng tính từ 1; hòa điểm thì chỉ số nhỏ trước."""
    scores: dict[int, float] = {}
    for ranked in rank_lists:
        for rank, i in enumerate(ranked, 1):
            scores[i] = scores.get(i, 0.0) + 1.0 / (rrf_k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def live_mask(chunks: list[dict], t: str) -> np.ndarray:
    return np.array([chunking.in_force(c, t) for c in chunks], dtype=bool)


class PairScorer(Protocol):
    identity: dict

    def __call__(self, pairs: list[tuple[str, str]]) -> np.ndarray: ...


class CrossReranker:
    """bge-reranker-v2-m3, nạp từ snapshot trong cache Hugging Face (không tải mạng). Mặc định chạy CPU; demo G9 dùng
    GPU và ghim `revision`."""

    def __init__(self, model: str = RERANK_MODEL, max_length: int = RERANK_MAX_LENGTH, batch_size: int = 8,
                 device: str = "cpu", revision: str | None = None):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        from huggingface_hub import snapshot_download
        from sentence_transformers import CrossEncoder

        path = Path(snapshot_download(model, revision=revision, local_files_only=True))
        self.ce = CrossEncoder(str(path), device=device, max_length=max_length)
        self.batch_size = batch_size
        self.identity = {"model": model, "revision": path.name, "max_length": max_length}

    def __call__(self, pairs: list[tuple[str, str]]) -> np.ndarray:
        return np.asarray(self.ce.predict(pairs, batch_size=self.batch_size, show_progress_bar=False), dtype=float)


class Reranker:
    """Chấm (câu hỏi, đoạn) bằng `scorer`, cache điểm trong một file JSON riêng cho mỗi danh tính mô hình."""

    def __init__(self, scorer: PairScorer, cache_dir: Path):
        self.scorer = scorer
        ident = json.dumps(scorer.identity, ensure_ascii=False, sort_keys=True)
        self.path = cache_dir / f"{hashlib.sha256(ident.encode()).hexdigest()[:16]}.json"
        self.cache: dict[str, float] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data["meta"] != scorer.identity:
                raise ValueError(f"{self.path} là cache của reranker khác: {data['meta']}")
            self.cache = data["scores"]

    @staticmethod
    def _key(query: str, text: str) -> str:
        return hashlib.sha256(f"{query}\x00{text}".encode("utf-8")).hexdigest()

    def score(self, query: str, chunks: list[dict]) -> list[float]:
        keys = [self._key(query, c["text"]) for c in chunks]
        todo = [(k, c) for k, c in zip(keys, chunks) if k not in self.cache]
        todo = list({k: c for k, c in todo}.items())
        if todo:
            values = self.scorer([(query, c["text"]) for _, c in todo])
            self.cache.update({k: float(v) for (k, _), v in zip(todo, values)})
            self._save()
        return [self.cache[k] for k in keys]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.stem + ".tmp.json")
        tmp.write_text(json.dumps({"meta": self.scorer.identity, "scores": self.cache}, ensure_ascii=False),
                       encoding="utf-8")
        os.replace(tmp, self.path)


class Retriever:
    def __init__(self, chunks: list[dict], bm25, dense, encode_query: Callable[[list[str]], np.ndarray],
                 reranker: Reranker | None = None):
        self.chunks = chunks
        self.bm25 = bm25
        self.dense = dense
        self.encode_query = encode_query
        self.reranker = reranker
        self._mask_cache: dict[str, np.ndarray] = {}

    def _mask(self, t: str) -> np.ndarray:
        if t not in self._mask_cache:
            self._mask_cache[t] = live_mask(self.chunks, t)
        return self._mask_cache[t]

    def search(self, query: str, ngay_hoi: str, cfg: Config = Config(), qvec: np.ndarray | None = None) -> list[Hit]:
        mask = self._mask(ngay_hoi) if cfg.loc_hieu_luc else None
        lists = []
        if cfg.dung_bm25:
            lists.append([i for i, _ in self.bm25.search(query, cfg.bm25_k, mask=mask)])
        if cfg.dung_vector:
            q = qvec if qvec is not None else self.encode_query([query])[0]
            lists.append([i for i, _ in self.dense.search(q, cfg.dense_k, mask=mask)])
        fused = fuse_rrf(lists, cfg.rrf_k)
        hits = [Hit(self.chunks[i], s, rank) for rank, (i, s) in enumerate(fused, 1)]
        if cfg.rerank_k and self.reranker is not None:
            pool = hits[:cfg.rerank_k]
            for h, s in zip(pool, self.reranker.score(query, [h.chunk for h in pool])):
                h.rerank = s
            hits = sorted(pool, key=lambda h: (-h.rerank, h.rrf_rank))
        return hits[:cfg.top_k]


def load_chunks(cut: str, rag_dir: Path | None = None) -> tuple[list[dict], str]:
    """Đoạn của một cách cắt cùng SHA-256 tính trên chính các byte vừa đọc; báo lỗi nếu khác manifest."""
    rag = rag_dir or config.DATA / "rag"
    path = rag / f"chunks_{cut}.jsonl"
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    manifest = json.loads((rag / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["files"][f"data/rag/chunks_{cut}.jsonl"]["sha256"] != sha:
        raise ValueError(f"{path} không khớp data/rag/MANIFEST.json; chạy scripts/build_chunks.py rồi build lại chỉ mục")
    return [json.loads(line) for line in data.decode("utf-8").splitlines()], sha


def load(cut: str = "khoan", reranker: bool = True, rag_dir: Path | None = None, encoder=None) -> Retriever:
    """Retriever trên chỉ mục đã build trong `data/rag/index/<cách cắt>/`, với bge-m3 và reranker thật.

    Kiểm: file đoạn khớp manifest (băm chính các byte đã đọc), hai chỉ mục được build từ đúng file đó, thứ tự mã đoạn
    khớp, và bộ mã hóa câu hỏi có cùng danh tính với bộ mã hóa đã tạo chỉ mục vector.
    """
    from rag import bm25, dense

    rag = rag_dir or config.DATA / "rag"
    chunks, sha = load_chunks(cut, rag)
    b = bm25.BM25Index.load(rag / "index" / cut / "bm25.pkl", sha)
    d = dense.DenseIndex.load(rag / "index" / cut, sha)
    if not (b.ids == d.ids == [c["chunk_id"] for c in chunks]):
        raise ValueError("thứ tự đoạn trong chỉ mục không khớp file đoạn")
    enc = encoder if encoder is not None else dense.load_encoder()
    if enc.identity != d.meta.get("bo_ma_hoa"):
        raise ValueError(f"bộ mã hóa câu hỏi {enc.identity} khác bộ mã hóa đã tạo chỉ mục {d.meta.get('bo_ma_hoa')}")
    rr = Reranker(CrossReranker(), rag / "index" / "rerank_cache") if reranker else None
    return Retriever(chunks, b, d, enc, rr)
