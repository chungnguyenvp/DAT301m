"""Read product data; write timestamped evidence and use disposable directories for probes."""
import hashlib
import importlib.metadata as metadata
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import evalset
from rag import bm25, chunking, dense, score


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": {}, "findings": {}}
    check = result["checks"]
    check["installed_versions"] = {n: metadata.version(n) for n in (
        "torch", "sentence-transformers", "transformers", "faiss-cpu", "rank-bm25")}
    check["bm25_dev"] = {}
    items = [x for x in evalset.load_eval() if x["tap"] == "dev"]
    for cut in ("khoan", "dieu"):
        path = ROOT / f"data/rag/chunks_{cut}.jsonl"
        chunks = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines()]
        index = bm25.BM25Index.load(ROOT / f"data/rag/index/{cut}/bm25.pkl", sha(path))
        assert index.ids == [c["chunk_id"] for c in chunks]
        mask = np.array([chunking.in_force(c, "2026-10-01") for c in chunks])
        rows = []
        for item in items:
            hits = [chunks[i] for i, _ in index.search(item["cau_hoi"], 5, mask)]
            assert all(chunking.in_force(c, "2026-10-01") for c in hits)
            rows.append(score.score_item(item, hits))
        check["bm25_dev"][cut] = score.summarize(rows, items, n_boot=0)
        with tempfile.TemporaryDirectory(prefix="g3-bm25-") as temp:
            p = Path(temp) / "index.pkl"
            index.save(p, sha(path))
            again = bm25.BM25Index.load(p, sha(path))
            assert again.search("mũ bảo hiểm", 5, mask) == index.search("mũ bảo hiểm", 5, mask)

    # Exact vector search and serialization on an ASCII path.
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(100, 16)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    query = rng.normal(size=16).astype(np.float32)
    query /= np.linalg.norm(query)
    index = dense.DenseIndex.build([str(i) for i in range(100)], vectors)
    for mask in (None, np.arange(100) % 3 == 0):
        expected = vectors @ query
        if mask is not None:
            expected = np.where(mask, expected, -np.inf)
        actual = index.search(query, 7, mask)
        want = np.argsort(-expected)[:7].tolist()
        assert [i for i, _ in actual] == want
        assert np.allclose([s for _, s in actual], expected[want])
    check["faiss_exact_search_matches_numpy_with_and_without_mask"] = True

    with tempfile.TemporaryDirectory(prefix="g3-ascii-") as temp:
        ascii_folder = Path(temp)
        index.save(ascii_folder, "test")
        assert dense.DenseIndex.load(ascii_folder, "test").search(query, 7) == index.search(query, 7)
        check["faiss_ascii_save_load"] = True
        # Actual project path contains Vietnamese characters. Never touch its product indexes.
        with tempfile.TemporaryDirectory(prefix="faiss-path-probe-", dir=Path(__file__).parent) as unicode_temp:
            target = Path(unicode_temp)
            details = {}
            try:
                index.save(target, "test")
            except Exception as ex:
                details["write_error"] = {"type": type(ex).__name__, "message": str(ex)}
            for p in ascii_folder.iterdir():
                shutil.copyfile(p, target / p.name)
            try:
                dense.DenseIndex.load(target, "test")
            except Exception as ex:
                details["read_error"] = {"type": type(ex).__name__, "message": str(ex)}
            result["findings"]["unicode_faiss_io"] = details

    expected_by_text = {"a": [1, 0], "b": [0, 1], "c": [-1, 0]}

    def encode(texts):
        return np.array([expected_by_text[t] for t in texts], dtype=np.float32)

    # Interrupt the actual cache writer after replacing vectors but before replacing keys.
    with tempfile.TemporaryDirectory(prefix="g3-crash-") as temp:
        folder = Path(temp)
        dense.embed(["a"], folder, encode, batch=1, save_every=1)
        original_replace = dense.os.replace
        calls = []

        def crash_between_files(src, dst):
            calls.append(str(dst))
            if len(calls) == 2:
                raise OSError("review: interrupt before keys.json replacement")
            return original_replace(src, dst)

        with patch.object(dense.os, "replace", side_effect=crash_between_files):
            try:
                dense.embed(["a", "b"], folder, encode, batch=1, save_every=1)
            except OSError:
                pass
        before_resume = {"key_count": len(json.loads((folder / "keys.json").read_text())),
                         "vector_rows": int(np.load(folder / "vectors.npy").shape[0])}
        actual = dense.embed(["a", "b", "c"], folder, encode, batch=1, save_every=1)
        expected = encode(["a", "b", "c"])
        result["findings"]["interrupted_cache_save"] = {
            "before_resume": before_resume, "actual": actual.tolist(), "expected": expected.tolist(),
            "silently_wrong": not np.array_equal(actual, expected)}

    # The public encoder API allows a different model/config but cache has no namespace for it.
    with tempfile.TemporaryDirectory(prefix="g3-identity-") as temp:
        folder = Path(temp)
        dense.embed(["a"], folder, lambda texts: np.array([[1, 0] for _ in texts], dtype=np.float32))
        called = []

        def changed_encoder(texts):
            called.extend(texts)
            return np.array([[0, 1] for _ in texts], dtype=np.float32)

        actual = dense.embed(["a", "b"], folder, changed_encoder)
        result["findings"]["cache_encoder_identity"] = {
            "new_encoder_called_for": called, "actual": actual.tolist(),
            "expected": [[0, 1], [0, 1]], "stale_vector_reused": actual[0].tolist() == [1, 0]}

    cache = ROOT / "data/rag/index/emb_cache"
    keys = json.loads((cache / "keys.json").read_text(encoding="utf-8"))
    cached = np.load(cache / "vectors.npy", mmap_mode="r")
    norms = np.linalg.norm(cached, axis=1)
    check["live_cache_snapshot_not_a_completion_claim"] = {
        "keys": len(keys), "shape": list(cached.shape), "unique_keys": len(set(keys)),
        "dtype": str(cached.dtype), "finite": bool(np.isfinite(cached).all()),
        "norm_min": float(norms.min()), "norm_max": float(norms.max())}
    check["dense_artifacts_at_review_time"] = [str(p.relative_to(ROOT)) for p in (ROOT / "data/rag/index").rglob("dense.faiss")]
    check["later_pipeline_files"] = {p: (ROOT / p).exists() for p in (
        "src/rag/retrieve.py", "src/rag/context.py", "scripts/run_retrieval.py")}
    paths = ["src/rag/bm25.py", "src/rag/dense.py", "scripts/build_index.py", "requirements.txt",
             "tests/test_rag_bm25.py", "tests/test_rag_dense.py", "data/eval/eval_v1.jsonl",
             "data/rag/chunks_khoan.jsonl", "data/rag/chunks_dieu.jsonl"]
    result["hashes"] = {p: sha(ROOT / p) for p in paths}
    assert result["hashes"]["data/eval/eval_v1.jsonl"] == "5a1b72038ae79755f5df7c53ed46447ac1516bb04e8e1330fd81cfc43fc0e252"
    dest = Path(__file__).parent / ("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with dest.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(dest), "findings": result["findings"],
                      "cache": check["live_cache_snapshot_not_a_completion_claim"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
