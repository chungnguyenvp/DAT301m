"""Independent Task 5 re-review; temporary negative tests and isolated reranker cache."""
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import config, evalset
from rag import chunking, dense, retrieve, score


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FakeEncoder:
    def __init__(self, identity):
        self.identity = identity

    def __call__(self, texts):
        return np.zeros((len(texts), self.identity["dim"]), dtype=np.float32)


def main():
    stamp = datetime.now(timezone.utc).strftime("%H%M%S%fZ")
    folder = Path(__file__).parent
    checks = []

    def check(name, passed, details=None):
        checks.append({"name": name, "pass": bool(passed), "details": details})

    saved_path = ROOT / "reports/retrieval/dev_probe.json"
    saved_hash = sha(saved_path)
    saved = json.loads(saved_path.read_text(encoding="utf-8"))
    manifest_path = ROOT / "data/rag/MANIFEST.json"
    identity = json.loads((ROOT / "data/rag/index/khoan/meta.json").read_text(encoding="utf-8"))["bo_ma_hoa"]
    for cut in ("khoan", "dieu"):
        r = retrieve.load(cut, reranker=False, encoder=FakeEncoder(identity))
        check(f"{cut}:matching_load_accepted", r.dense.ids == [c["chunk_id"] for c in r.chunks])
        for key, value in (("revision", "review-other"), ("max_seq_length", 512), ("normalize", False)):
            rejected = False
            try:
                retrieve.load(cut, reranker=False, encoder=FakeEncoder(dict(identity, **{key: value})))
            except ValueError as ex:
                rejected = "bộ mã hóa" in str(ex)
            check(f"{cut}:different_encoder_{key}_rejected", rejected)

    for field, value in (("text", "review-modified-text"), ("valid_from", "2099-01-01")):
        with tempfile.TemporaryDirectory(prefix="task5-hash-") as temp:
            rag = Path(temp)
            shutil.copyfile(manifest_path, rag / "MANIFEST.json")
            rows = [json.loads(s) for s in (ROOT / "data/rag/chunks_khoan.jsonl").read_text(encoding="utf-8").splitlines()]
            rows[0][field] = value
            (rag / "chunks_khoan.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in rows), encoding="utf-8")
            rejected = False
            try:
                retrieve.load("khoan", reranker=False, rag_dir=rag, encoder=FakeEncoder(identity))
            except ValueError as ex:
                rejected = "MANIFEST" in str(ex)
            check(f"altered_chunk_{field}_rejected_before_index_load", rejected)

    print("Guards verified; loading real encoder and reranker.", flush=True)
    enc = dense.load_encoder()
    scorer = retrieve.CrossReranker()
    check("encoder_identity_matches_dev", enc.identity == saved["bo_ma_hoa"])
    check("reranker_identity_matches_dev", scorer.identity == saved["reranker"])
    spec = importlib.util.spec_from_file_location("review_probe_dev", ROOT / "scripts/probe_dev.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check("configs_match_saved_report", {k: v.__dict__ for k, v in module.CONFIGS.items()} == saved["cau_hinh"])
    items = [x for x in evalset.load_eval() if x["tap"] == "dev"]
    check("only_30_dev_questions", len(items) == 30 and all(x["tap"] == "dev" for x in items))
    qvectors = dict(zip([x["id"] for x in items], enc([x["cau_hoi"] for x in items])))
    cache_files = list((ROOT / "data/rag/index/rerank_cache").glob("*.json"))
    product_hashes = {str(p): sha(p) for p in cache_files}
    rerank_dir = folder / f"rerank-cache-{stamp}"
    rerank_dir.mkdir(exist_ok=False)
    for path in cache_files:
        shutil.copyfile(path, rerank_dir / path.name)
    rr = retrieve.Reranker(scorer, rerank_dir)
    reproduced = dict(saved, ket_qua={})
    retrievers = {}
    for cut in ("khoan", "dieu"):
        r = retrieve.load(cut, reranker=False, encoder=enc)
        r.reranker = rr
        retrievers[cut] = r
        for name, cfg in module.CONFIGS.items():
            rows, leaked, old_raw = [], 0, 0
            for item in items:
                chunks = [h.chunk for h in r.search(item["cau_hoi"], item["ngay_hoi"], cfg, qvec=qvectors[item["id"]])]
                leaked += sum(not chunking.in_force(c, item["ngay_hoi"]) for c in chunks)
                rows.append(score.score_item(item, chunks, cfg.top_k))
                if item["nhom_cau"] == "sua_doi":
                    raw = r.search(item["cau_hoi"], item["ngay_hoi"], replace(cfg, loc_hieu_luc=False), qvec=qvectors[item["id"]])
                    old_raw += any(set(item["can_cu_cu"]) & set(h.chunk["units"]) for h in raw)
            data = {"tong_hop": score.summarize(rows, items, n_boot=1000, seed=0),
                    "variant_gap": score.variant_gap(rows, items), "doan_het_hieu_luc_lot_vao": leaked,
                    "sua_doi_lay_ban_cu_khi_bo_loc": old_raw, "tung_cau": [row for row in rows if row is not None]}
            reproduced["ket_qua"][f"{name}/{cut}"] = data
            check(f"{name}/{cut}:full_report_matches", data == saved["ket_qua"][f"{name}/{cut}"])
            check(f"{name}/{cut}:no_expired_hits", leaked == 0)
            print(f"Verified {name}/{cut}", flush=True)

    r = retrievers["khoan"]
    point_h = "nd_168_2024:d7:k2:h@2025-01-01"
    queries = {"everyday": "đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu",
               "formal": "không đội mũ bảo hiểm khi điều khiển xe mô tô bị phạt bao nhiêu"}
    qvec = enc(list(queries.values()))
    query_details = {}
    for (label, query), q in zip(queries.items(), qvec):
        configs = {"dense_only": retrieve.Config(dung_bm25=False, rerank_k=0, top_k=50),
                   "hybrid": retrieve.Config(rerank_k=0, top_k=50),
                   "hybrid_rerank": retrieve.Config(top_k=20)}
        stages = {}
        final_hits = None
        for stage, cfg in configs.items():
            hits = r.search(query, config.CUTOFF, cfg, qvec=q)
            rank = next((i for i, h in enumerate(hits, 1) if point_h in h.chunk["units"]), None)
            stages[stage] = {"point_h_rank": rank, "top": [{"id": h.chunk["chunk_id"], "rrf_rank": h.rrf_rank,
                                "rerank": h.rerank} for h in hits[:10]]}
            if stage == "hybrid_rerank":
                final_hits = hits
        check(f"{label}:all_final_chunks_live", all(chunking.in_force(h.chunk, config.CUTOFF) for h in final_hits))
        query_details[label] = {"query": query, "stages": stages}
    check("reported_everyday_limitation_reproduced", query_details["everyday"]["stages"]["hybrid_rerank"]["point_h_rank"] == 6)
    check("formal_query_point_h_in_top5", 0 < query_details["formal"]["stages"]["hybrid_rerank"]["point_h_rank"] <= 5)

    target = next(c for c in r.chunks if point_h in c["units"] and chunking.in_force(c, config.CUTOFF))
    pairs = [(queries["everyday"], target["text"]), (queries["formal"], target["text"])]
    fresh_scores = scorer(pairs)
    cached_scores = [rr.score(q, [target])[0] for q in queries.values()]
    check("fresh_reranker_scores_match_cached_pair_scores", np.allclose(fresh_scores, cached_scores, atol=1e-5),
          {"fresh": fresh_scores.tolist(), "cached": cached_scores})
    check("saved_dev_report_not_overwritten", sha(saved_path) == saved_hash)
    check("product_rerank_caches_unchanged", all(sha(Path(p)) == h for p, h in product_hashes.items()))
    out_dev = folder / f"dev-reproduced-{stamp}.json"
    with out_dev.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(reproduced, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    paths = ["src/rag/retrieve.py", "src/rag/context.py", "src/rag/dense.py", "scripts/build_index.py",
             "scripts/probe_dev.py", "tests/test_rag_retrieve.py", "tests/test_rag_dense.py", "reports/retrieval/dev_probe.json",
             "data/eval/eval_v1.jsonl", "data/eval/bang_chung_v1.json", "data/rag/MANIFEST.json"]
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "queries": query_details,
              "encoder": enc.identity, "reranker": scorer.identity, "dev_reproduced": out_dev.name,
              "hashes": {p: sha(ROOT / p) for p in paths}}
    output = folder / f"checks-{stamp}.json"
    with output.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(output), "passed": sum(c["pass"] for c in checks), "total": len(checks),
                      "failures": [c for c in checks if not c["pass"]]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
