import hashlib
import json
import os

import numpy as np
import pytest

from lawproc import config
from rag import chunking, dense


class FakeEncoder:
    """Vector giả theo mã băm của chữ, có đếm số chữ đã mã hóa."""

    def __init__(self, fail_after: int | None = None, salt: str = ""):
        self.seen: list[str] = []
        self.fail_after = fail_after
        self.salt = salt
        self.identity = {"model": "fake", "revision": salt or "r1", "max_seq_length": 8, "normalize": True,
                         "dtype": "float32", "dim": 8}

    def vector(self, t: str) -> np.ndarray:
        v = np.frombuffer(hashlib.sha256((self.salt + t).encode()).digest(), dtype=np.uint8).astype(np.float32)[:8]
        v = v - 127
        return v / np.linalg.norm(v)

    def __call__(self, texts: list[str]) -> np.ndarray:
        out = []
        for t in texts:
            if self.fail_after is not None and len(self.seen) >= self.fail_after:
                raise RuntimeError("dừng giữa chừng")
            self.seen.append(t)
            out.append(self.vector(t))
        return np.stack(out)


def test_embed_caches_by_text_and_keeps_order(tmp_path):
    enc = FakeEncoder()
    first = dense.embed(["a", "bb", "a"], tmp_path, enc)
    assert first.shape == (3, 8) and np.allclose(first[0], first[2])
    assert sorted(enc.seen) == ["a", "bb"]
    again = dense.embed(["bb", "ccc", "a"], tmp_path, enc)
    assert enc.seen.count("a") == 1 and enc.seen[-1] == "ccc"
    assert np.allclose(again[0], first[1]) and np.allclose(again[2], first[0])


def test_embed_resumes_after_a_crash(tmp_path):
    with pytest.raises(RuntimeError):
        dense.embed(["x1", "x2", "x3"], tmp_path, FakeEncoder(fail_after=2), batch=1, save_every=1)
    enc = FakeEncoder()
    dense.embed(["x1", "x2", "x3"], tmp_path, enc, batch=1)
    assert enc.seen == ["x3"]


def test_crash_while_saving_a_checkpoint_keeps_the_old_cache(tmp_path, monkeypatch):
    dense.embed(["a"], tmp_path, FakeEncoder())

    def broken(*args, **kwargs):
        raise OSError("mất điện lúc thay file")

    with monkeypatch.context() as m:
        m.setattr(dense.os, "replace", broken)
        with pytest.raises(OSError):
            dense.embed(["a", "b"], tmp_path, FakeEncoder(), batch=1, save_every=1)
    enc = FakeEncoder()
    got = dense.embed(["a", "b", "c"], tmp_path, enc)
    assert np.allclose(got, np.stack([enc.vector(t) for t in "abc"]))
    assert sorted(enc.seen) == ["b", "c"]


def test_inconsistent_cache_is_rejected(tmp_path):
    enc = FakeEncoder()
    dense.embed(["a"], tmp_path, enc)
    (path,) = tmp_path.glob("*.npz")
    with np.load(path) as z:
        meta, keys, vecs = z["meta"], z["keys"], z["vectors"]
    with path.open("wb") as fp:
        np.savez(fp, meta=meta, keys=keys, vectors=np.vstack([vecs, vecs]))
    with pytest.raises(ValueError, match="không nhất quán"):
        dense.embed(["a", "b"], tmp_path, enc)


def test_cache_is_separate_for_each_encoder_identity(tmp_path):
    first = FakeEncoder(salt="m1")
    dense.embed(["a"], tmp_path, first)
    second = FakeEncoder(salt="m2")
    got = dense.embed(["a", "b"], tmp_path, second)
    assert second.seen == ["a", "b"]
    assert np.allclose(got, np.stack([second.vector("a"), second.vector("b")]))
    assert len(list(tmp_path.glob("*.npz"))) == 2


def test_cache_file_of_another_encoder_is_refused(tmp_path):
    first, second = FakeEncoder(salt="m1"), FakeEncoder(salt="m2")
    dense.embed(["a"], tmp_path, first)
    (path,) = tmp_path.glob("*.npz")
    path.replace(dense.cache_path(tmp_path, second.identity))
    with pytest.raises(ValueError, match="mô hình"):
        dense.embed(["a"], tmp_path, second)


def test_save_and_load_under_a_folder_with_vietnamese_accents(tmp_path):
    folder = tmp_path / "1.Chuyên Ngành" / "kì 7"
    index = _index()
    index.save(folder, chunks_sha256="abc", info={"model": "fake"})
    again = dense.DenseIndex.load(folder, chunks_sha256="abc")
    q = np.array([0, 1, 0, 0], dtype=np.float32)
    assert again.index.ntotal == 4 and again.search(q, 2) == index.search(q, 2)


def _index():
    vecs = np.eye(4, dtype=np.float32)
    return dense.DenseIndex.build(["a", "b", "c", "d"], vecs)


def test_search_returns_nearest_and_respects_mask():
    index = _index()
    q = np.array([0.1, 0.9, 0.3, 0], dtype=np.float32)
    assert [i for i, _ in index.search(q, k=2)] == [1, 2]
    mask = np.array([True, False, True, True])
    assert [i for i, _ in index.search(q, k=2, mask=mask)] == [2, 0]
    assert index.search(q, k=3, mask=np.zeros(4, dtype=bool)) == []


def test_save_load_and_reject_other_chunk_file(tmp_path):
    index = _index()
    index.save(tmp_path, chunks_sha256="abc", info={"model": "fake"})
    again = dense.DenseIndex.load(tmp_path, chunks_sha256="abc")
    q = np.array([0, 0, 1, 0], dtype=np.float32)
    assert again.ids == index.ids and again.search(q, 1) == index.search(q, 1)
    assert json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))["model"] == "fake"
    with pytest.raises(ValueError, match="đoạn"):
        dense.DenseIndex.load(tmp_path, chunks_sha256="khac")


# ---- Mô hình thật: chậm (nạp bge-m3 mất gần một phút), chỉ chạy khi đặt RAG_SLOW=1 ----

SLOW = pytest.mark.skipif(os.environ.get("RAG_SLOW") != "1", reason="đặt RAG_SLOW=1 để chạy test với bge-m3 thật")
HELMET = "đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu"


@pytest.fixture(scope="module")
def real_dense():
    folder = config.DATA / "rag" / "index" / "khoan"
    if not (folder / "dense.faiss").exists():
        pytest.skip("chưa build chỉ mục vector")
    manifest = json.loads((config.DATA / "rag" / "MANIFEST.json").read_text(encoding="utf-8"))
    chunks = [json.loads(line) for line in (config.DATA / "rag" / "chunks_khoan.jsonl").open(encoding="utf-8")]
    index = dense.DenseIndex.load(folder, manifest["files"]["data/rag/chunks_khoan.jsonl"]["sha256"])
    q = dense.load_encoder()([HELMET])[0]
    mask = np.array([chunking.in_force(c, config.CUTOFF) for c in chunks])
    return [chunks[i] for i, _ in index.search(q, k=10, mask=mask)]


@SLOW
def test_real_index_smoke_finds_the_right_clause(real_dense):
    """Smoke test: chỉ mục thật nạp được và tìm đúng Khoản. KHÔNG chứng minh tìm đủ căn cứ (Điểm h)."""
    assert all(chunking.in_force(c, config.CUTOFF) for c in real_dense)
    assert real_dense[0]["nhom"] == "nd_168_2024:d7:k2"


@SLOW
@pytest.mark.xfail(strict=True, reason="Đã biết, chưa sửa: với vector đơn thuần, mẩu chứa điểm h (448 token, khoảng 8 "
                                        "hành vi) chỉ đứng hạng 20–23. Task 5 (hybrid + reranker) phải làm test này qua; "
                                        "khi qua thì bỏ xfail.")
def test_real_dense_only_finds_point_h_in_top10(real_dense):
    assert any("nd_168_2024:d7:k2:h@2025-01-01" in c["units"] for c in real_dense)
