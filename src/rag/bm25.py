"""Chỉ mục BM25 trên chữ đã tách từ bằng pyvi.

Chữ được chuyển về chữ thường, ghép từ bằng `pyvi.ViTokenizer` ("bảo hiểm" → "bảo_hiểm"), giữ số có dấu chấm,
phẩy, gạch chéo ("400.000"), bỏ dấu câu. Chỉ mục khóa theo mã băm của file đoạn: nạp với file đoạn khác thì báo lỗi.
"""

import pickle
import re
import warnings
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

TOKEN = re.compile(r"\d+(?:[.,/]\d+)*|\w+")


def _segment(text: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # pyvi nạp mô hình pickle cũ, numpy 2.4 cảnh báo
        from pyvi import ViTokenizer
        return ViTokenizer.tokenize(text)


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(_segment(text.lower()))


class BM25Index:
    def __init__(self, ids: list[str], model: BM25Okapi):
        self.ids = ids
        self.model = model

    @classmethod
    def build(cls, chunks: list[dict]) -> "BM25Index":
        return cls([c["chunk_id"] for c in chunks], BM25Okapi([tokenize(c["text"]) for c in chunks]))

    def search(self, query: str, k: int, mask: np.ndarray | None = None) -> list[tuple[int, float]]:
        """(chỉ số đoạn, điểm) của tối đa k đoạn có điểm dương, điểm giảm dần. `mask` False thì bỏ đoạn đó."""
        scores = np.asarray(self.model.get_scores(tokenize(query)), dtype=float)
        if mask is not None:
            scores = np.where(mask, scores, -np.inf)
        order = np.argsort(-scores, kind="stable")[:k]
        return [(int(i), float(scores[i])) for i in order if scores[i] > 0]

    def save(self, path: Path, chunks_sha256: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as fp:
            pickle.dump({"chunks_sha256": chunks_sha256, "ids": self.ids, "model": self.model}, fp)

    @classmethod
    def load(cls, path: Path, chunks_sha256: str) -> "BM25Index":
        with path.open("rb") as fp:
            data = pickle.load(fp)
        if data["chunks_sha256"] != chunks_sha256:
            raise ValueError(f"{path} được build từ file đoạn khác; chạy lại scripts/build_index.py")
        return cls(data["ids"], data["model"])
