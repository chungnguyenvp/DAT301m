"""G8: chạy cải tiến "mở rộng Khoản lên Điều cha" (`rag.expand`, ngân sách đã chọn trên dev/train) MỘT lần trên test.

    py -3.13 scripts/g8_context.py           # từ chối chạy lại nếu đã có reports/g8/retrieval_test.json
    py -3.13 scripts/g8_context.py --force

Cho cả 270 câu eval: retriever G3 (tham số `reports/retrieval/params.json`, lọc hiệu lực) lấy 20 đoạn Khoản đã xếp hạng;
top 5 phải trùng ngữ cảnh G3 (`test_with_context_khoan.jsonl`); rồi `expand_to_dieu` dựng ngữ cảnh mới. Ghi:
- `data/rag/test_with_context_g8.jsonl`: `ngu_canh_g8`, `doan_g8` cho từng câu (cho bước sinh lại ở Kaggle);
- `reports/g8/retrieval_test.json`: any/all/tỷ lệ nhóm/MRR trên test, trước và sau, CI95 bootstrap theo họ sự kiện,
  cùng biến thể so với câu gốc và số token ngữ cảnh.
"""

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import context, expand, retrieve, score  # noqa: E402

OUT = config.ROOT / "reports" / "g8"
CTX_OUT = config.DATA / "rag" / "test_with_context_g8.jsonl"
POOL = 20


def uid(x: dict) -> str:
    return f"{x['nhom_cau']}/{x['key']}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    out = OUT / "retrieval_test.json"
    if out.exists() and not a.force:
        sys.exit(f"{out.relative_to(config.ROOT)} đã có: tập test chỉ chạy một lần. Thêm --force nếu thật sự cần.")
    t0 = time.time()
    cfg = retrieve.Config(**json.loads((config.ROOT / "reports" / "retrieval" / "params.json")
                                       .read_text(encoding="utf-8"))["chon"])
    r = retrieve.load("khoan")
    dieu_chunks, dieu_sha = retrieve.load_chunks("dieu")
    index = expand.parent_index(dieu_chunks)
    g3 = {f"{c['nhom_cau']}/{c['key']}": c for c in
          map(json.loads, open(config.DATA / "rag" / "test_with_context_khoan.jsonl", encoding="utf-8"))}
    items = evalset.load_eval()
    ev = score.load_evidence()
    rows_base, rows_new, recs, mismatch = [], [], [], []
    for x in items:
        hits = r.search(x["cau_hoi"], x["ngay_hoi"], replace(cfg, top_k=POOL))
        ranked = [h.chunk for h in hits]
        base = ranked[:cfg.top_k]
        if [c["chunk_id"] for c in base] != [d["chunk_id"] for d in g3[uid(x)]["doan"]]:
            mismatch.append(uid(x))
        new = expand.expand_to_dieu(ranked, x["ngay_hoi"], index)
        recs.append({"uid": uid(x), "id": x["id"], "key": x["key"], "tap": x["tap"], "nhom_cau": x["nhom_cau"],
                     "cau_hoi": x["cau_hoi"], "ngay_hoi": x["ngay_hoi"],
                     "doan_g8": [{"chunk_id": c["chunk_id"], "so_token": c["so_token"]} for c in new],
                     "so_token_g8": sum(c["so_token"] for c in new),
                     "so_token_khoan": sum(c["so_token"] for c in base),
                     "ngu_canh_g8": context.format_context(new)})
        if x["tap"] == "test":
            for rows, chunks in ((rows_base, base), (rows_new, new)):
                s = score.score_item(x, chunks, k=len(chunks), evidence=ev)
                rows.append(s and {**s, "id": x["id"], "nhom_cau": x["nhom_cau"]})
    assert not mismatch, f"top 5 khác ngữ cảnh G3 ở {len(mismatch)} câu: {mismatch[:5]}"
    with open(CTX_OUT, "w", encoding="utf-8", newline="\n") as fp:
        fp.writelines(json.dumps(rec, ensure_ascii=False) + "\n" for rec in recs)
    test = [x for x in items if x["tap"] == "test"]
    tok = {k: sum(rec[k] for rec in recs if rec["tap"] == "test") / len(test) for k in ("so_token_khoan", "so_token_g8")}
    report = {"cach": "mo_rong_dieu", "ngan_sach": expand.BUDGET, "toi_da_doan": expand.MAX_PIECES, "pool": POOL,
              "tham_so_g3": cfg.__dict__, "chunks_dieu_sha256": dieu_sha, "so_cau_test": len(test),
              "token_ngu_canh_tb": tok,
              "truoc": score.summarize(rows_base, items, n_boot=1000, seed=0),
              "sau": score.summarize(rows_new, items, n_boot=1000, seed=0),
              "bien_the_truoc": score.variant_gap(rows_base, items), "bien_the_sau": score.variant_gap(rows_new, items),
              "giay": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for grp in ("thuong", "sua_doi", "bien_the"):
        b, n = report["truoc"].get(grp, {}), report["sau"].get(grp, {})
        print(grp, {m: (round(b[m]["gia_tri"], 3), round(n[m]["gia_tri"], 3)) for m in ("any", "all", "ty_le_nhom", "mrr")
                    if m in b})
    print("token ngữ cảnh tb (test):", {k: round(v) for k, v in tok.items()}, "| giây:", report["giay"])
    print(f"-> {CTX_OUT.relative_to(config.ROOT)}, {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
