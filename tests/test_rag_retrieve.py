import os

import numpy as np
import pytest

from lawproc import config
from rag import context, retrieve


def _chunk(cid, vf="2025-01-01", vt=None, text=None, doc="nd_168_2024", dieu="7", khoan="2"):
    return {"chunk_id": cid, "doc_id": doc, "dieu": dieu, "khoan": khoan, "valid_from": vf, "valid_to": vt,
            "units": [cid], "text": text or f"Nghị định 168/2024/NĐ-CP — Điều {dieu}. Tiêu đề\nchữ {cid}"}


CHUNKS = [_chunk("a"), _chunk("b"), _chunk("old", vt="2026-08-10"), _chunk("c"), _chunk("d")]


class FakeIndex:
    """Trả danh sách xếp hạng cố định, tôn trọng `mask` như chỉ mục thật."""

    def __init__(self, order):
        self.order = order
        self.masks = []

    def search(self, query, k, mask=None):
        self.masks.append(mask)
        return [(i, 1.0 / (r + 1)) for r, i in enumerate(o for o in self.order if mask is None or mask[o])][:k]


class FakeScorer:
    identity = {"model": "fake-reranker", "revision": "r1", "max_length": 16}

    def __init__(self, scores):
        self.scores = scores
        self.calls = 0

    def __call__(self, pairs):
        self.calls += len(pairs)
        return np.array([self.scores[t.rsplit(" ", 1)[1]] for _, t in pairs])


def _retriever(tmp_path, bm25_order=(0, 2, 1, 3), dense_order=(2, 3, 0, 4), scores=None):
    scorer = FakeScorer(scores or {"a": 0.1, "b": 0.2, "old": 0.9, "c": 0.8, "d": 0.3})
    rr = retrieve.Reranker(scorer, tmp_path / "rerank")
    r = retrieve.Retriever(CHUNKS, FakeIndex(list(bm25_order)), FakeIndex(list(dense_order)),
                           encode_query=lambda texts: np.zeros((len(texts), 4), dtype=np.float32), reranker=rr)
    return r, scorer


def test_rrf_sums_reciprocal_ranks_and_breaks_ties_by_index():
    fused = retrieve.fuse_rrf([[0, 2, 1], [2, 3]], rrf_k=60)
    assert [i for i, _ in fused] == [2, 0, 3, 1]
    assert fused[0][1] == pytest.approx(1 / 62 + 1 / 61)
    assert fused[1][1] == pytest.approx(1 / 61) and fused[2][1] == pytest.approx(1 / 62)
    assert [i for i, _ in retrieve.fuse_rrf([[5], [4]], rrf_k=60)] == [4, 5]


def test_filter_is_applied_inside_both_searches_before_ranking(tmp_path):
    r, _ = _retriever(tmp_path)
    cfg = retrieve.Config(rerank_k=0, top_k=4)
    hits = r.search("câu hỏi", "2026-10-01", cfg)
    assert "old" not in [h.chunk["chunk_id"] for h in hits]
    for index in (r.bm25, r.dense):
        assert index.masks[-1].tolist() == [True, True, False, True, True]


def test_without_filter_the_old_version_can_come_back(tmp_path):
    r, _ = _retriever(tmp_path)
    hits = r.search("câu hỏi", "2026-10-01", retrieve.Config(loc_hieu_luc=False, rerank_k=0, top_k=2))
    assert [h.chunk["chunk_id"] for h in hits] == ["old", "a"]


def test_rrf_order_without_reranker_and_single_method_configs(tmp_path):
    r, _ = _retriever(tmp_path)
    ids = lambda cfg: [h.chunk["chunk_id"] for h in r.search("q", "2026-10-01", cfg)]  # noqa: E731
    assert ids(retrieve.Config(rerank_k=0, top_k=4)) == ["a", "c", "b", "d"]
    assert ids(retrieve.Config(dung_vector=False, rerank_k=0, top_k=3)) == ["a", "b", "c"]
    assert ids(retrieve.Config(dung_bm25=False, rerank_k=0, top_k=3)) == ["c", "a", "d"]


def test_reranker_reorders_the_pool_and_reports_scores(tmp_path):
    r, scorer = _retriever(tmp_path)
    hits = r.search("q", "2026-10-01", retrieve.Config(rerank_k=3, top_k=2))
    assert [h.chunk["chunk_id"] for h in hits] == ["c", "b"]  # pool RRF = a, c, b
    assert hits[0].rerank == pytest.approx(0.8) and hits[0].rrf_rank == 2
    assert scorer.calls == 3


def test_rerank_scores_are_cached_on_disk_by_encoder_identity(tmp_path):
    r, scorer = _retriever(tmp_path)
    cfg = retrieve.Config(rerank_k=3, top_k=2)
    r.search("q", "2026-10-01", cfg)
    r.search("q", "2026-10-01", cfg)
    assert scorer.calls == 3
    again, scorer2 = _retriever(tmp_path)
    again.search("q", "2026-10-01", cfg)
    assert scorer2.calls == 0
    other = FakeScorer({"a": 0, "b": 0, "old": 0, "c": 0, "d": 0})
    other.identity = dict(other.identity, revision="r2")
    retrieve.Reranker(other, tmp_path / "rerank").score("q", CHUNKS[:2])
    assert other.calls == 2


def test_context_lists_source_and_validity_of_each_chunk():
    chunks = [_chunk("x", text="Nghị định 168/2024/NĐ-CP — Điều 7. Xử phạt\n2. Phạt tiền từ 400.000 đồng"),
              _chunk("y", vf="2025-01-01", vt="2026-08-10", doc="nd_158_2024", dieu="34", khoan="4",
                     text="Nghị định 158/2024/NĐ-CP — Điều 34. Gia hạn\n4. Trình tự"),
              _chunk("z", doc="tt_155_2025_btc", dieu=None, khoan=None, text="Thông tư 155/2025/TT-BTC — Phụ lục\nI.2. …")]
    out = context.format_context(chunks)
    blocks = out.split("\n\n")
    assert blocks[0].splitlines()[0] == "[1] Nghị định 168/2024/NĐ-CP, khoản 2 Điều 7 — hiệu lực từ 01/01/2025"
    assert blocks[1].splitlines()[0] == "[2] Nghị định 158/2024/NĐ-CP, khoản 4 Điều 34 — hiệu lực từ 01/01/2025 đến 09/08/2026"
    assert blocks[2].splitlines()[0] == "[3] Thông tư 155/2025/TT-BTC, phụ lục — hiệu lực từ 01/01/2025"
    assert blocks[0].splitlines()[1:] == ["Nghị định 168/2024/NĐ-CP — Điều 7. Xử phạt", "2. Phạt tiền từ 400.000 đồng"]


class FakeQueryEncoder:
    def __init__(self, revision="r1"):
        self.identity = {"model": "fake", "revision": revision, "max_seq_length": 8, "normalize": True,
                         "dtype": "float32", "dim": 4}

    def __call__(self, texts):
        return np.ones((len(texts), 4), dtype=np.float32) / 2


def _rag_dir(tmp_path):
    """Thư mục data/rag nhỏ: 3 đoạn, manifest, chỉ mục BM25 và vector thật dựng từ vector giả."""
    import hashlib
    import json

    from rag import bm25, dense

    rag = tmp_path / "rag"
    chunks = [_chunk(c, text=f"Nghị định 168/2024/NĐ-CP — Điều 7. Tiêu đề\nmũ bảo hiểm {c}") for c in "abc"]
    data = "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks).encode("utf-8")
    (rag / "index" / "khoan").mkdir(parents=True)
    (rag / "chunks_khoan.jsonl").write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    (rag / "MANIFEST.json").write_text(json.dumps({"files": {"data/rag/chunks_khoan.jsonl": {"sha256": sha}}}),
                                       encoding="utf-8")
    bm25.BM25Index.build(chunks).save(rag / "index" / "khoan" / "bm25.pkl", sha)
    dense.DenseIndex.build([c["chunk_id"] for c in chunks], np.eye(3, 4, dtype=np.float32)).save(
        rag / "index" / "khoan", sha, {"bo_ma_hoa": FakeQueryEncoder().identity})
    return rag


def test_load_accepts_matching_files_and_encoder(tmp_path):
    r = retrieve.load("khoan", reranker=False, rag_dir=_rag_dir(tmp_path), encoder=FakeQueryEncoder())
    assert [c["chunk_id"] for c in r.chunks] == ["a", "b", "c"]
    assert r.search("mũ bảo hiểm", "2026-10-01", retrieve.Config(rerank_k=0, top_k=2))


def test_load_rejects_a_chunk_file_edited_in_place(tmp_path):
    rag = _rag_dir(tmp_path)
    path = rag / "chunks_khoan.jsonl"
    path.write_bytes(path.read_bytes().replace("2025-01-01".encode(), "2025-02-01".encode(), 1))
    with pytest.raises(ValueError, match="MANIFEST"):
        retrieve.load("khoan", reranker=False, rag_dir=rag, encoder=FakeQueryEncoder())


def test_load_rejects_a_query_encoder_other_than_the_index_encoder(tmp_path):
    with pytest.raises(ValueError, match="bộ mã hóa"):
        retrieve.load("khoan", reranker=False, rag_dir=_rag_dir(tmp_path), encoder=FakeQueryEncoder(revision="r2"))


# ---- Chỉ mục và mô hình thật: chậm, chỉ chạy khi đặt RAG_SLOW=1 ----

SLOW = pytest.mark.skipif(os.environ.get("RAG_SLOW") != "1", reason="đặt RAG_SLOW=1 để chạy với bge-m3 và reranker thật")
POINT_H = "nd_168_2024:d7:k2:h@2025-01-01"


@pytest.fixture(scope="module")
def real():
    return retrieve.load("khoan")


def _top5(r, query):
    hits = r.search(query, config.CUTOFF, retrieve.Config())
    assert len(hits) == 5
    assert all(h.chunk["valid_from"] <= config.CUTOFF and (h.chunk["valid_to"] is None
                                                            or config.CUTOFF < h.chunk["valid_to"]) for h in hits)
    return hits


@SLOW
def test_real_hybrid_with_reranker_finds_point_h(real):
    # Câu không có trong bộ eval. Vector đơn thuần xếp mẩu chứa điểm h hạng 26; RRF đưa lên 7, reranker lên 3.
    hits = _top5(real, "không đội mũ bảo hiểm khi điều khiển xe mô tô bị phạt bao nhiêu")
    assert any(POINT_H in h.chunk["units"] for h in hits)


@SLOW
@pytest.mark.xfail(strict=True, reason="Đã biết, chưa sửa: với cách nói đời thường 'nón bảo hiểm', RRF đưa mẩu chứa "
                                        "điểm h lên hạng 5 nhưng reranker chấm 0,65 và đẩy xuống hạng 6. Xử lý ở G8 "
                                        "(ánh xạ từ đời thường sang thuật ngữ luật, E7) hoặc bằng cách cắt nhỏ hơn.")
def test_real_hybrid_with_reranker_finds_point_h_for_everyday_wording(real):
    hits = _top5(real, "đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu")
    assert any(POINT_H in h.chunk["units"] for h in hits)
