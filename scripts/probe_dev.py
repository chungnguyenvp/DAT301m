"""Thăm dò các cấu hình tìm kiếm trên 30 câu dev; chỉ dùng tập dev.

    py -3.13 scripts/probe_dev.py            # ghi reports/retrieval/dev_probe.json và in bảng

Cấu hình: chỉ BM25, chỉ vector, hybrid (RRF), hybrid + reranker; cho cả hai cách cắt. Mỗi câu: lọc hiệu lực tại
`ngay_hoi`, lấy top-5, chấm bằng `rag.score`. Ghi thêm số đoạn hết hiệu lực lọt vào kết quả có lọc (phải bằng 0)
và số câu sửa đổi lấy phải bản cũ khi bỏ lọc. Không dùng tập test.
"""

import hashlib
import json
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import chunking, retrieve, score  # noqa: E402

OUT = config.ROOT / "reports" / "retrieval" / "dev_probe.json"
BASE = retrieve.Config()
CONFIGS = {
    "bm25": replace(BASE, dung_vector=False, rerank_k=0),
    "vector": replace(BASE, dung_bm25=False, rerank_k=0),
    "hybrid": replace(BASE, rerank_k=0),
    "hybrid+rerank": BASE,
}


def main() -> None:
    items = [x for x in evalset.load_eval() if x["tap"] == "dev"]
    report = {"tap": "dev", "so_cau": len(items), "cau_hinh": {k: asdict(v) for k, v in CONFIGS.items()},
              "eval_sha256": hashlib.sha256((config.DATA / "eval" / "eval_v1.jsonl").read_bytes()).hexdigest(),
              "ket_qua": {}}
    for cut in ("khoan", "dieu"):
        r = retrieve.load(cut)
        report["bo_ma_hoa"] = r.encode_query.identity
        report["reranker"] = r.reranker.scorer.identity
        qvec = dict(zip([x["id"] for x in items], r.encode_query([x["cau_hoi"] for x in items])))
        for name, cfg in CONFIGS.items():
            t = time.time()
            rows, leaked, old_unfiltered = [], 0, 0
            for x in items:
                hits = [h.chunk for h in r.search(x["cau_hoi"], x["ngay_hoi"], cfg, qvec=qvec[x["id"]])]
                leaked += sum(not chunking.in_force(c, x["ngay_hoi"]) for c in hits)
                rows.append(score.score_item(x, hits, k=cfg.top_k))
                if x["nhom_cau"] == "sua_doi":
                    raw = [h.chunk for h in r.search(x["cau_hoi"], x["ngay_hoi"], replace(cfg, loc_hieu_luc=False),
                                                     qvec=qvec[x["id"]])]
                    old_unfiltered += any(set(x["can_cu_cu"]) & set(c["units"]) for c in raw)
            summary = score.summarize(rows, items, n_boot=1000, seed=0)
            report["ket_qua"][f"{name}/{cut}"] = {
                "tong_hop": summary, "variant_gap": score.variant_gap(rows, items),
                "doan_het_hieu_luc_lot_vao": leaked, "sua_doi_lay_ban_cu_khi_bo_loc": old_unfiltered,
                "tung_cau": [row for row in rows if row is not None]}
            for g in ("thuong", "sua_doi", "bien_the"):
                m = summary[g]
                print(f"{name:13s} {cut:5s} {g:9s} n={m['n']:2d} van_ban {m['van_ban']['gia_tri']:.2f} "
                      f"any {m['any']['gia_tri']:.2f} all {m['all']['gia_tri']:.2f} "
                      f"ty_le {m['ty_le_nhom']['gia_tri']:.2f} mrr {m['mrr']['gia_tri']:.2f}", flush=True)
            print(f"              {cut}: lọt hết hiệu lực {leaked}; sửa đổi lấy bản cũ khi bỏ lọc {old_unfiltered}; "
                  f"{time.time() - t:.0f} giây", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"-> {OUT.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
