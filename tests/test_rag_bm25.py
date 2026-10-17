import json

import numpy as np
import pytest

from lawproc import config
from rag import bm25, chunking


def _chunk(cid, text):
    return {"chunk_id": cid, "text": text}


CHUNKS = [
    _chunk("a", "Phạt tiền từ 400.000 đồng đến 600.000 đồng đối với người không đội mũ bảo hiểm khi điều khiển xe mô tô"),
    _chunk("b", "Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe ô tô chạy quá tốc độ"),
    _chunk("c", "Giấy phép lái xe hạng A1 cấp cho người lái xe mô tô hai bánh"),
    _chunk("d", "Lệ phí cấp đổi chứng nhận đăng ký xe kèm theo biển số"),
]


def test_tokenize_lowercases_joins_words_and_keeps_numbers():
    toks = bm25.tokenize("Không đội mũ bảo hiểm, phạt 400.000 đồng (Nghị định 168/2024/NĐ-CP)")
    assert "bảo_hiểm" in toks and "nghị_định" in toks
    assert "400.000" in toks and "168" in toks
    assert all(t == t.lower() for t in toks) and "," not in toks and "(" not in toks


def test_search_ranks_the_matching_chunk_first():
    index = bm25.BM25Index.build(CHUNKS)
    hits = index.search("không đội mũ bảo hiểm phạt bao nhiêu", k=3)
    assert hits[0][0] == 0 and hits[0][1] > 0
    assert len(hits) <= 3 and all(s > 0 for _, s in hits)
    assert [i for i, _ in hits] == sorted([i for i, _ in hits], key=lambda i: -dict(hits)[i])


def test_mask_removes_chunks_before_ranking():
    index = bm25.BM25Index.build(CHUNKS)
    mask = np.array([False, True, True, True])
    assert 0 not in [i for i, _ in index.search("mũ bảo hiểm xe mô tô", k=4, mask=mask)]


def test_save_and_load_give_the_same_results(tmp_path):
    index = bm25.BM25Index.build(CHUNKS)
    index.save(tmp_path / "bm25.pkl", chunks_sha256="abc")
    again = bm25.BM25Index.load(tmp_path / "bm25.pkl", chunks_sha256="abc")
    assert again.ids == ["a", "b", "c", "d"]
    assert again.search("giấy phép lái xe hạng A1", k=2) == index.search("giấy phép lái xe hạng A1", k=2)
    with pytest.raises(ValueError, match="đoạn"):
        bm25.BM25Index.load(tmp_path / "bm25.pkl", chunks_sha256="khac")


def test_query_with_no_known_word_returns_nothing():
    assert bm25.BM25Index.build(CHUNKS).search("zzzz qqqq", k=3) == []


# ---- Chỉ mục thật (cần chạy scripts/build_index.py trước) ----

@pytest.fixture(scope="module")
def real():
    path = config.DATA / "rag" / "index" / "khoan" / "bm25.pkl"
    manifest = json.loads((config.DATA / "rag" / "MANIFEST.json").read_text(encoding="utf-8"))
    if not path.exists():
        pytest.skip("chưa build chỉ mục BM25")
    chunks = [json.loads(line) for line in (config.DATA / "rag" / "chunks_khoan.jsonl").open(encoding="utf-8")]
    index = bm25.BM25Index.load(path, manifest["files"]["data/rag/chunks_khoan.jsonl"]["sha256"])
    return chunks, index


def test_real_helmet_question_finds_the_fine(real):
    chunks, index = real
    mask = np.array([chunking.in_force(c, config.CUTOFF) for c in chunks])
    hits = index.search("Người điều khiển xe máy không đội mũ bảo hiểm bị phạt bao nhiêu tiền?", k=10, mask=mask)
    found = [chunks[i] for i, _ in hits]
    assert any("nd_168_2024:d7:k2:h@2025-01-01" in c["units"] for c in found)
    assert all(chunking.in_force(c, config.CUTOFF) for c in found)
