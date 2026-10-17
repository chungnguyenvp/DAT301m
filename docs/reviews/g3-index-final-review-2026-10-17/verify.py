"""Verify completed indexes and reproduce dev results with the real cached encoder.

Writes only new files inside this review directory; never overwrites Claude's report.
"""
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import evalset
from rag import chunking, dense, score


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    stamp = datetime.now(timezone.utc).strftime("%H%M%S%fZ")
    folder = Path(__file__).parent
    original_path = ROOT / "reports/retrieval/dev_probe.json"
    original_hash = digest(original_path)
    original = json.loads(original_path.read_text(encoding="utf-8"))
    checks = []

    def check(name, ok, details=None):
        checks.append({"name": name, "pass": bool(ok), "details": details})

    enc = dense.load_encoder()
    check("real_encoder_matches_report_identity", enc.identity == original["bo_ma_hoa"], enc.identity)
    chunks_by_cut = {}
    indexes = {}
    index_meta = {}
    manifest = json.loads((ROOT / "data/rag/MANIFEST.json").read_text(encoding="utf-8"))
    keys, cache = dense._load_cache(dense.cache_path(ROOT / "data/rag/index/emb_cache", enc.identity), enc.identity)
    by_key = {k: i for i, k in enumerate(keys)}
    for cut, count in (("khoan", 6221), ("dieu", 2149)):
        path = ROOT / f"data/rag/chunks_{cut}.jsonl"
        sha = digest(path)
        check(f"{cut}:chunk_hash_matches_manifest", sha == manifest["files"][f"data/rag/chunks_{cut}.jsonl"]["sha256"])
        chunks = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines()]
        index = dense.DenseIndex.load(ROOT / f"data/rag/index/{cut}", sha)
        meta = json.loads((ROOT / f"data/rag/index/{cut}/meta.json").read_text(encoding="utf-8"))
        index_meta[cut] = meta
        chunks_by_cut[cut], indexes[cut] = chunks, index
        check(f"{cut}:id_order", index.ids == [c["chunk_id"] for c in chunks])
        check(f"{cut}:count_dim", (index.index.ntotal, index.index.d) == (count, 1024))
        check(f"{cut}:encoder_identity", meta["bo_ma_hoa"] == enc.identity)
        vectors = index.index.reconstruct_n(0, index.index.ntotal)
        norms = np.linalg.norm(vectors, axis=1)
        check(f"{cut}:finite_normalized", np.isfinite(vectors).all() and np.allclose(norms, 1, atol=1e-5))
        wanted = [hashlib.sha256(c["text"].encode("utf-8")).hexdigest() for c in chunks]
        check(f"{cut}:all_vectors_match_cache_by_text", np.array_equal(vectors, np.stack([cache[by_key[k]] for k in wanted])))
        picks = list(range(0, len(chunks), 50))
        hits = [index.search(vectors[i], 1) for i in picks]
        # Accept an equal-vector tie, since duplicated text can have multiple chunk IDs.
        check(f"{cut}:self_search", all(s[0][1] >= 0.99999 and np.allclose(vectors[s[0][0]], vectors[i], atol=1e-6)
                                               for i, s in zip(picks, hits)), {"samples": len(picks)})

    # Re-run the actual probe script while sending its output to a fresh review file.
    # Reuse the encoder already loaded for this audit.
    spec = importlib.util.spec_from_file_location("review_probe_dev", ROOT / "scripts/probe_dev.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = folder / f"dev-reproduced-{stamp}.json"
    if module.OUT.exists():
        raise FileExistsError(module.OUT)
    original_loader = dense.load_encoder
    dense.load_encoder = lambda: enc
    try:
        module.main()
    finally:
        dense.load_encoder = original_loader
    reproduced = json.loads(module.OUT.read_text(encoding="utf-8"))
    check("complete_dev_report_matches_exactly", reproduced == original)
    check("original_dev_report_unchanged", digest(original_path) == original_hash)
    expected_ids = {x["id"] for x in evalset.load_eval() if x["tap"] == "dev" and x["nhom_cau"] != "ngoai_pham_vi"}
    for name, outcome in reproduced["ket_qua"].items():
        check(name + ":only_26_scorable_dev_items", {r["id"] for r in outcome["tung_cau"]} == expected_ids)
        check(name + ":no_expired_hits", outcome["doan_het_hieu_luc_lot_vao"] == 0)

    helmet = "đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu"
    q = enc([helmet])[0]
    chunks, index = chunks_by_cut["khoan"], indexes["khoan"]
    mask = np.array([chunking.in_force(c, "2026-10-01") for c in chunks])
    ranked = index.search(q, 50, mask)
    vid = "nd_168_2024:d7:k2:h@2025-01-01"
    rank = next((i for i, (j, _) in enumerate(ranked, 1) if vid in chunks[j]["units"]), None)
    helmet_details = {"query": helmet, "required_vid": vid, "rank_in_top50": rank,
                      "top_chunk": chunks[ranked[0][0]]["chunk_id"],
                      "top10_contains_required_point": rank is not None and rank <= 10}
    check("known_dense_only_helmet_failure_reproduced", rank is not None and rank > 10, helmet_details)

    # A small independent real-encoder/cache comparison; avoid recoding the entire corpus.
    rows = chunks_by_cut["khoan"]
    selected = [min(rows, key=lambda c: c["so_token"]),
                min(rows, key=lambda c: abs(c["so_token"] - 128)),
                min(rows, key=lambda c: abs(c["so_token"] - 480))]
    fresh = enc([c["text"] for c in selected])
    expected = np.stack([cache[by_key[hashlib.sha256(c["text"].encode("utf-8")).hexdigest()]] for c in selected])
    cosines = (fresh * expected).sum(axis=1)
    check("three_real_reencoded_chunks_match_cache", np.all(cosines > 0.99999), {
        "chunks": [c["chunk_id"] for c in selected], "tokens": [c["so_token"] for c in selected],
        "cosines": cosines.tolist()})

    paths = ["src/rag/dense.py", "src/rag/bm25.py", "scripts/probe_dev.py", "scripts/build_index.py",
             "tests/test_rag_dense.py", "data/eval/eval_v1.jsonl", "data/eval/bang_chung_v1.json",
             "data/rag/MANIFEST.json", "reports/retrieval/dev_probe.json"]
    for cut in indexes:
        paths.extend(f"data/rag/index/{cut}/{name}" for name in ("dense.faiss", "dense_ids.json", "meta.json", "bm25.pkl"))
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "index_meta": index_meta,
              "dev_reproduced_path": module.OUT.name, "helmet": helmet_details,
              "hashes": {p: digest(ROOT / p) for p in paths}}
    output = folder / f"checks-{stamp}.json"
    with output.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(output), "passed": sum(c["pass"] for c in checks), "total": len(checks),
                      "failures": [c for c in checks if not c["pass"]]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
