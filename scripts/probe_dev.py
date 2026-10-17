"""Thăm dò BM25 và vector (từng cách riêng, chưa hybrid) trên 30 câu dev; chỉ dùng tập dev.

    py -3.13 scripts/probe_dev.py            # ghi reports/retrieval/dev_probe.json và in bảng

Mỗi câu: lọc hiệu lực tại `ngay_hoi`, lấy top-5, chấm bằng `rag.score`. Ghi thêm số đoạn hết hiệu lực lọt vào
kết quả có lọc (phải bằng 0) và số câu sửa đổi lấy phải bản cũ khi bỏ lọc. Không dùng tập test.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from lawproc import config, evalset  # noqa: E402
from rag import bm25, chunking, dense, score  # noqa: E402

RAG = config.DATA / "rag"
OUT = config.ROOT / "reports" / "retrieval" / "dev_probe.json"
K = 5


def main() -> None:
    items = [x for x in evalset.load_eval() if x["tap"] == "dev"]
    manifest = json.loads((RAG / "MANIFEST.json").read_text(encoding="utf-8"))
    enc = dense.load_encoder()
    qvec = dict(zip([x["id"] for x in items], enc([x["cau_hoi"] for x in items])))
    report = {"tap": "dev", "k": K, "so_cau": len(items), "bo_ma_hoa": enc.identity,
              "eval_sha256": hashlib.sha256((config.DATA / "eval" / "eval_v1.jsonl").read_bytes()).hexdigest(),
              "ket_qua": {}}
    for cut in ("khoan", "dieu"):
        sha = manifest["files"][f"data/rag/chunks_{cut}.jsonl"]["sha256"]
        chunks = [json.loads(line) for line in (RAG / f"chunks_{cut}.jsonl").open(encoding="utf-8")]
        searchers = {
            "bm25": (bm25.BM25Index.load(RAG / "index" / cut / "bm25.pkl", sha), lambda ix, x, m: ix.search(x["cau_hoi"], K, mask=m)),
            "vector": (dense.DenseIndex.load(RAG / "index" / cut, sha), lambda ix, x, m: ix.search(qvec[x["id"]], K, mask=m)),
        }
        for name, (index, run) in searchers.items():
            rows, leaked, old_unfiltered = [], 0, 0
            for x in items:
                mask = np.array([chunking.in_force(c, x["ngay_hoi"]) for c in chunks])
                hits = [chunks[i] for i, _ in run(index, x, mask)]
                leaked += sum(not chunking.in_force(c, x["ngay_hoi"]) for c in hits)
                rows.append(score.score_item(x, hits, k=K))
                if x["nhom_cau"] == "sua_doi":
                    raw = [chunks[i] for i, _ in run(index, x, None)]
                    old_unfiltered += any(set(x["can_cu_cu"]) & set(c["units"]) for c in raw)
            summary = score.summarize(rows, items, n_boot=1000, seed=0)
            report["ket_qua"][f"{name}/{cut}"] = {
                "tong_hop": summary, "variant_gap": score.variant_gap(rows, items),
                "doan_het_hieu_luc_lot_vao": leaked, "sua_doi_lay_ban_cu_khi_bo_loc": old_unfiltered,
                "tung_cau": [r for r in rows if r is not None]}
            for g in ("thuong", "sua_doi", "bien_the"):
                m = summary[g]
                print(f"{name:6s} {cut:5s} {g:9s} n={m['n']:2d} van_ban {m['van_ban']['gia_tri']:.2f} "
                      f"any {m['any']['gia_tri']:.2f} all {m['all']['gia_tri']:.2f} mrr {m['mrr']['gia_tri']:.2f}")
            print(f"       {cut}: lọt hết hiệu lực {leaked}; sửa đổi lấy bản cũ khi bỏ lọc {old_unfiltered}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"-> {OUT.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
