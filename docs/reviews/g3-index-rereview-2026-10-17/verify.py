"""Independent structural and adversarial checks. Never rebuilds product embeddings."""
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from rag import dense, chunking, score


class Encoder:
    def __init__(self, revision="a", max_length=8):
        self.identity = {"model": "review", "revision": revision, "max_seq_length": max_length,
                         "normalize": True, "dim": 2, "dtype": "float32"}
        self.called = []

    def __call__(self, texts):
        self.called.extend(texts)
        a = {"a": [1, 0], "b": [0, 1], "c": [-1, 0]}
        arr = np.array([a[t] for t in texts], dtype=np.float32)
        return arr if self.identity["revision"] == "a" else -arr


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def check(name, ok, details=None):
        checks.append({"name": name, "pass": bool(ok), "details": details})

    with tempfile.TemporaryDirectory(prefix="kiểm-tra-", dir=Path(__file__).parent) as temp:
        folder = Path(temp)
        index = dense.DenseIndex.build(["a", "b"], np.eye(2, dtype=np.float32))
        index.save(folder, "abc")
        again = dense.DenseIndex.load(folder, "abc")
        check("unicode_path_save_load", again.search(np.array([1, 0], dtype=np.float32), 2) == index.search(np.array([1, 0], dtype=np.float32), 2))

    with tempfile.TemporaryDirectory(prefix="g3-checkpoint-") as temp:
        folder = Path(temp)
        enc = Encoder()
        dense.embed(["a"], folder, enc)
        original = dense.cache_path(folder, enc.identity).read_bytes()
        with patch.object(dense.os, "replace", side_effect=OSError("injected before replace")):
            try:
                dense.embed(["a", "b"], folder, enc, batch=1, save_every=1)
            except OSError:
                pass
        check("interrupted_save_keeps_old_checkpoint", original == dense.cache_path(folder, enc.identity).read_bytes())
        fresh = Encoder()
        actual = dense.embed(["a", "b", "c"], folder, fresh, batch=1, save_every=1)
        check("resume_has_no_vector_misalignment", np.array_equal(actual, Encoder()(["a", "b", "c"])), {"actual": actual.tolist(), "reencoded": fresh.called})
        for name, alternate in (("revision", Encoder("b")), ("max_length", Encoder(max_length=4))):
            out = dense.embed(["a", "b"], folder, alternate)
            check("cache_separate_" + name, alternate.called == ["a", "b"] and np.array_equal(out, alternate(["a", "b"])))

    malformed = []
    for case in ("extra_rows", "duplicate_keys", "wrong_dim", "nan", "identity"):
        with tempfile.TemporaryDirectory(prefix="g3-invalid-") as temp:
            folder = Path(temp)
            enc = Encoder()
            dense.embed(["a", "b"], folder, enc)
            path = dense.cache_path(folder, enc.identity)
            with np.load(path, allow_pickle=False) as z:
                meta, keys, vecs = z["meta"], z["keys"], z["vectors"]
            if case == "extra_rows":
                vecs = np.vstack([vecs, vecs[:1]])
            elif case == "duplicate_keys":
                keys = np.array([keys[0], keys[0]])
            elif case == "wrong_dim":
                vecs = np.zeros((2, 3), dtype=np.float32)
            elif case == "nan":
                vecs[0, 0] = np.nan
            else:
                meta = np.array(json.dumps(dict(enc.identity, revision="unexpected")))
            with path.open("wb") as fp:
                np.savez(fp, meta=meta, keys=keys, vectors=vecs)
            rejected = False
            try:
                dense.embed(["a"], folder, enc)
            except ValueError:
                rejected = True
            check("malformed_cache_rejected_" + case, rejected)

    cut = "khoan"
    path = ROOT / f"data/rag/chunks_{cut}.jsonl"
    chunks = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    index = dense.DenseIndex.load(ROOT / "data/rag/index/khoan", digest(path))
    meta = json.loads((ROOT / "data/rag/index/khoan/meta.json").read_text(encoding="utf-8"))
    check("real_index_ids_match_chunk_order", index.ids == [c["chunk_id"] for c in chunks])
    check("real_index_size_and_dimension", (index.index.ntotal, index.index.d) == (6221, 1024), {"rows": index.index.ntotal, "dim": index.index.d})
    keys, vectors = dense._load_cache(dense.cache_path(ROOT / "data/rag/index/emb_cache", meta["bo_ma_hoa"]), meta["bo_ma_hoa"])
    pos = {k: i for i, k in enumerate(keys)}
    wanted = [hashlib.sha256(c["text"].encode("utf-8")).hexdigest() for c in chunks]
    check("all_chunk_texts_present_in_cache", all(k in pos for k in wanted))
    cached = np.stack([vectors[pos[k]] for k in wanted])
    reconstructed = index.index.reconstruct_n(0, index.index.ntotal)
    check("all_6221_index_vectors_match_cache_by_text", np.array_equal(cached, reconstructed))
    norms = np.linalg.norm(reconstructed, axis=1)
    check("real_vectors_normalized_and_finite", np.isfinite(reconstructed).all() and np.allclose(norms, 1, atol=1e-5))
    mask = np.array([chunking.in_force(c, "2026-10-01") for c in chunks])
    for i in (0, len(chunks) // 2, len(chunks) - 1):
        q = reconstructed[i]
        values = reconstructed @ q
        values[~mask] = -np.inf
        hits = index.search(q, 5, mask)
        check(f"real_index_exact_search_and_temporal_mask_{i}",
              all(mask[j] for j, _ in hits) and np.allclose([v for _, v in hits], np.sort(values)[-5:][::-1], atol=1e-5))

    wrong = next(c for c in chunks if c["chunk_id"] == "khoan:nd_168_2024:d7:k2@2025-01-01#2")
    needed = "nd_168_2024:d7:k2:h@2025-01-01"
    item = {"id": "audit-helmet", "key": "audit-helmet", "nhom_cau": "thuong", "can_cu": [needed],
            "nhom_can_cu": [[needed]], "van_ban": "nd_168_2024"}
    weak = wrong["nhom"] == "nd_168_2024:d7:k2"
    strict = score.score_item(item, [wrong])
    check("same_clause_assertion_can_pass_without_required_point", weak and not strict["any"],
          {"chunk": wrong["chunk_id"], "same_clause_assertion": weak, "actual_evidence_score": strict})

    artifacts = {c: (ROOT / f"data/rag/index/{c}/dense.faiss").exists() for c in ("khoan", "dieu")}
    files = ["src/rag/dense.py", "scripts/build_index.py", "tests/test_rag_dense.py",
             "data/rag/index/khoan/dense.faiss", "data/rag/index/khoan/meta.json", "data/rag/index/khoan/dense_ids.json",
             "data/eval/eval_v1.jsonl"]
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "artifacts_at_review_time": artifacts,
              "encoder": meta["bo_ma_hoa"], "hashes": {p: digest(ROOT / p) for p in files},
              "scope": "No second bge-m3 model loaded while background build is running with low free RAM. No claim to independently reproduce query semantics or the reported 16-sample re-encoding."}
    dest = Path(__file__).parent / ("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with dest.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(dest), "passed": sum(c["pass"] for c in checks), "total": len(checks),
                      "failures": [c for c in checks if not c["pass"]], "artifacts": artifacts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
