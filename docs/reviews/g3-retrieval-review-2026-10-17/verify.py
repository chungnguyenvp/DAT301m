"""Fast Task 5 audit; no real-model load and no writes to product data or caches."""
import hashlib
import json
import shutil
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import config
from rag import context, dense, retrieve


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Encoder:
    def __init__(self, identity):
        self.identity = identity

    def __call__(self, texts):
        return np.zeros((len(texts), 1024), dtype=np.float32)


class Index:
    def __init__(self, order):
        self.order = order
        self.seen = []

    def search(self, query, k, mask=None):
        self.seen.append(None if mask is None else mask.tolist())
        return [(i, float(len(self.order) - j)) for j, i in enumerate(self.order) if mask is None or mask[i]][:k]


class Scorer:
    def __init__(self, revision="a"):
        self.identity = {"model": "audit", "revision": revision, "max_length": 1024}
        self.calls = []

    def __call__(self, pairs):
        self.calls.extend(pairs)
        return np.array([len(t) / 100 for _, t in pairs])


def main():
    checks, findings = [], {}

    def check(name, passed, details=None):
        checks.append({"name": name, "pass": bool(passed), "details": details})

    ranks = [[0, 2, 1], [2, 3]]
    fused = retrieve.fuse_rrf(ranks, 60)
    check("rrf_hand_calculation", [i for i, _ in fused] == [2, 0, 3, 1] and np.isclose(fused[0][1], 1 / 61 + 1 / 62))
    with tempfile.TemporaryDirectory(prefix="task5-cache-") as temp:
        folder = Path(temp)
        scorer = Scorer()
        rr = retrieve.Reranker(scorer, folder)
        chunks = [{"text": "một"}, {"text": "hai dài"}, {"text": "một"}]
        first = rr.score("q", chunks)
        check("reranker_deduplicates_equal_text", len(scorer.calls) == 2 and first[0] == first[2])
        other = Scorer()
        again = retrieve.Reranker(other, folder)
        check("reranker_reuses_saved_scores", again.score("q", chunks) == first and not other.calls)
        again.score("q khác", chunks)
        again.score("q", [{"text": "chữ đã đổi"}])
        check("query_and_text_changes_recomputed", len(other.calls) == 3)
        new = Scorer("b")
        retrieve.Reranker(new, folder).score("q", chunks)
        check("reranker_identity_separates_cache", len(new.calls) == 2)

    chunks = [{"chunk_id": "old", "doc_id": "nd_168_2024", "dieu": "7", "khoan": "2",
               "valid_from": "2025-01-01", "valid_to": "2026-08-10", "text": "old"},
              {"chunk_id": "new", "doc_id": "nd_168_2024", "dieu": "7", "khoan": "2",
               "valid_from": "2026-08-10", "valid_to": None, "text": "new"}]
    with tempfile.TemporaryDirectory(prefix="task5-pipeline-") as temp:
        b, d = Index([0, 1]), Index([0, 1])
        rr = retrieve.Reranker(Scorer(), Path(temp))
        r = retrieve.Retriever(chunks, b, d, lambda texts: np.zeros((len(texts), 2)), rr)
        cfg = retrieve.Config()
        check("before_amendment_only_old", [h.chunk["chunk_id"] for h in r.search("q", "2026-08-09", cfg)] == ["old"])
        check("at_amendment_only_new", [h.chunk["chunk_id"] for h in r.search("q", "2026-08-10", cfg)] == ["new"])
        r.search("q", "2026-08-10", replace(cfg, loc_hieu_luc=False))
        check("unfiltered_search_disables_both_masks", b.seen[-1] is None and d.seen[-1] is None)
    label = context.format_context([chunks[0]])
    check("context_exclusive_end_date", "đến 09/08/2026" in label)

    real_meta = json.loads((ROOT / "data/rag/index/khoan/meta.json").read_text(encoding="utf-8"))
    fake_identity = dict(real_meta["bo_ma_hoa"], revision="review-other-revision")
    with patch.object(dense, "load_encoder", return_value=Encoder(fake_identity)):
        accepted = retrieve.load("khoan", reranker=False)
    findings["different_query_encoder_accepted"] = {
        "index_identity": real_meta["bo_ma_hoa"], "query_identity": accepted.encode_query.identity,
        "reproduced": accepted.encode_query.identity != real_meta["bo_ma_hoa"]}

    # Keep actual saved indexes and all IDs, change only a copied chunk's text and date.
    # No fake index loaders: this exercises real BM25/FAISS load paths.
    with tempfile.TemporaryDirectory(prefix="task5-integrity-") as temp:
        datadir = Path(temp)
        rag = datadir / "rag"
        target = rag / "index/khoan"
        target.mkdir(parents=True)
        shutil.copyfile(ROOT / "data/rag/MANIFEST.json", rag / "MANIFEST.json")
        for name in ("bm25.pkl", "dense.faiss", "dense_ids.json", "meta.json"):
            shutil.copyfile(ROOT / f"data/rag/index/khoan/{name}", target / name)
        source = ROOT / "data/rag/chunks_khoan.jsonl"
        modified = [json.loads(s) for s in source.read_text(encoding="utf-8").splitlines()]
        modified[0]["text"] = "review: changed text, unchanged ID"
        modified[0]["valid_from"] = "2099-01-01"
        path = rag / "chunks_khoan.jsonl"
        path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in modified), encoding="utf-8")
        with patch.object(config, "DATA", datadir), patch.object(dense, "load_encoder", return_value=Encoder(real_meta["bo_ma_hoa"])):
            loaded = retrieve.load("khoan", reranker=False)
        findings["changed_chunk_file_accepted"] = {"expected_sha256": real_meta["chunks_sha256"], "actual_sha256": sha(path),
            "loaded_text": loaded.chunks[0]["text"], "loaded_valid_from": loaded.chunks[0]["valid_from"],
            "reproduced": loaded.chunks[0]["text"] == modified[0]["text"] and sha(path) != real_meta["chunks_sha256"]}

    paths = ["src/rag/retrieve.py", "src/rag/context.py", "scripts/probe_dev.py", "tests/test_rag_retrieve.py", "tests/test_rag_dense.py",
             "reports/retrieval/dev_probe.json", "data/rag/MANIFEST.json", "data/rag/chunks_khoan.jsonl", "data/rag/chunks_dieu.jsonl"]
    saved = json.loads((ROOT / "reports/retrieval/dev_probe.json").read_text(encoding="utf-8"))
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "findings": findings,
              "saved_dev_configurations_at_review_time": list(saved["ket_qua"]),
              "hashes": {p: sha(ROOT / p) for p in paths}}
    dest = Path(__file__).parent / ("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with dest.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(dest), "passed": sum(c["pass"] for c in checks), "total": len(checks), "findings": findings,
                      "saved_dev_configurations": result["saved_dev_configurations_at_review_time"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
