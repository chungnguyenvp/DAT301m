"""Task 6 của G3: chốt tham số trên dev, chạy ablation một lần trên test, xuất ngữ cảnh cho G7.

    py -3.13 scripts/run_retrieval.py --tap dev     # thử lưới tham số trên dev, ghi reports/retrieval/params.json
    py -3.13 scripts/run_retrieval.py --tap test    # chạy test MỘT lần với params.json; từ chối chạy lại nếu không có --force

Quy tắc chọn tham số (ghi trước khi chạy dev, không đổi theo kết quả test):
- Lưới: `rerank_k` ∈ {10, 20, 30} × `rrf_k` ∈ {20, 60}, cấu hình hybrid + reranker, cả hai cách cắt.
- Điểm của một bộ tham số = số câu dev (thường + sửa đổi + biến thể, cộng cả hai cách cắt) tìm đủ căn cứ (`all`);
  hòa thì so tổng MRR.
- Giữ mặc định (`rerank_k = 20`, `rrf_k = 60`) trừ khi bộ khác hơn ít nhất 2 câu `all` mà tổng MRR không giảm.
  Dev chỉ có 26 câu có căn cứ, nên chênh lệch một câu coi là nhiễu.

Test chạy cho mỗi cách cắt (Khoản, Điều): chỉ BM25, chỉ vector, hybrid, hybrid + reranker, hybrid + reranker bỏ lọc
hiệu lực. Ngữ cảnh của hybrid + reranker (có lọc, tại `ngay_hoi`) được ghi cho cả 270 câu eval vào
`data/rag/test_with_context_<cách cắt>.jsonl`; câu sửa đổi có thêm ngữ cảnh khi bỏ lọc (cho RQ3 ở G7).
"""

import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import chunking, context, retrieve, score  # noqa: E402

REPORTS = config.ROOT / "reports" / "retrieval"
PARAMS = REPORTS / "params.json"
CUTS = ("khoan", "dieu")
GRID = [(rk, kk) for rk in (10, 20, 30) for kk in (20, 60)]
DEFAULT = retrieve.Config()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def log(msg: str) -> None:
    print(msg, flush=True)


def ablation(cfg: retrieve.Config) -> dict[str, retrieve.Config]:
    return {"bm25": replace(cfg, dung_vector=False, rerank_k=0),
            "vector": replace(cfg, dung_bm25=False, rerank_k=0),
            "hybrid": replace(cfg, rerank_k=0),
            "hybrid+rerank": cfg,
            "hybrid+rerank_bo_loc": replace(cfg, loc_hieu_luc=False)}


def run(r: retrieve.Retriever, items: list[dict], qvec: dict, cfg: retrieve.Config) -> tuple[list, dict]:
    rows, hits_by_id, leaked = [], {}, 0
    for x in items:
        hits = r.search(x["cau_hoi"], x["ngay_hoi"], cfg, qvec=qvec[x["id"]])
        hits_by_id[x["id"]] = hits
        if cfg.loc_hieu_luc:
            leaked += sum(not chunking.in_force(h.chunk, x["ngay_hoi"]) for h in hits)
        rows.append(score.score_item(x, [h.chunk for h in hits], k=cfg.top_k))
    if leaked:
        raise RuntimeError(f"{leaked} đoạn hết hiệu lực lọt vào kết quả có lọc")
    return rows, hits_by_id


def old_version_count(items: list[dict], rows: list) -> int:
    return sum(bool(row and row["nham_ban_cu"]) for row in rows if row and row["nhom_cau"] == "sua_doi")


def dev_grid() -> None:
    items = [x for x in evalset.load_eval() if x["tap"] == "dev"]
    results = {}
    for cut in CUTS:
        r = retrieve.load(cut)
        qvec = dict(zip([x["id"] for x in items], r.encode_query([x["cau_hoi"] for x in items])))
        for rk, kk in GRID:
            t = time.time()
            rows, _ = run(r, items, qvec, replace(DEFAULT, rerank_k=rk, rrf_k=kk))
            scored = [row for row in rows if row]
            results.setdefault(f"{rk}/{kk}", {})[cut] = {
                "all": sum(row["all"] for row in scored), "mrr": sum(row["rr"] for row in scored), "n": len(scored)}
            log(f"dev {cut} rerank_k={rk} rrf_k={kk}: all {results[f'{rk}/{kk}'][cut]['all']}/{len(scored)}, "
                f"tổng MRR {results[f'{rk}/{kk}'][cut]['mrr']:.2f}, {time.time() - t:.0f} giây")
    total = {k: (sum(v[c]["all"] for c in CUTS), sum(v[c]["mrr"] for c in CUTS)) for k, v in results.items()}
    base = total[f"{DEFAULT.rerank_k}/{DEFAULT.rrf_k}"]
    best = max(total, key=lambda k: total[k])
    chosen = best if total[best][0] >= base[0] + 2 and total[best][1] >= base[1] else f"{DEFAULT.rerank_k}/{DEFAULT.rrf_k}"
    rk, kk = map(int, chosen.split("/"))
    cfg = replace(DEFAULT, rerank_k=rk, rrf_k=kk)
    REPORTS.mkdir(parents=True, exist_ok=True)
    PARAMS.write_text(json.dumps({
        "chon": asdict(cfg), "luoi": results, "tong": {k: {"all": a, "mrr": m} for k, (a, m) in total.items()},
        "quy_tac": "giữ mặc định trừ khi bộ khác hơn ≥ 2 câu all (cộng hai cách cắt) mà tổng MRR không giảm",
        "eval_sha256": sha256(config.DATA / "eval" / "eval_v1.jsonl")}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    log(f"chốt: rerank_k={rk}, rrf_k={kk} (mặc định {DEFAULT.rerank_k}/{DEFAULT.rrf_k}) -> {PARAMS.relative_to(config.ROOT)}")


def context_record(x: dict, cut: str, hits: list, raw_hits: list | None) -> dict:
    rec = {"id": x["id"], "key": x["key"], "tap": x["tap"], "nhom_cau": x["nhom_cau"], "cau_hoi": x["cau_hoi"],
           "ngay_hoi": x["ngay_hoi"], "cach_cat": cut,
           "doan": [{"chunk_id": h.chunk["chunk_id"], "rerank": h.rerank, "rrf_rank": h.rrf_rank} for h in hits],
           "diem_rerank_dau": hits[0].rerank if hits else None,
           "ngu_canh": context.format_context([h.chunk for h in hits])}
    if raw_hits is not None:
        rec["doan_bo_loc"] = [{"chunk_id": h.chunk["chunk_id"], "rerank": h.rerank} for h in raw_hits]
        rec["ngu_canh_bo_loc"] = context.format_context([h.chunk for h in raw_hits])
    return rec


LABELS = {"bm25": "Chỉ BM25", "vector": "Chỉ vector", "hybrid": "Hybrid (RRF)", "hybrid+rerank": "Hybrid + reranker",
          "hybrid+rerank_bo_loc": "Hybrid + reranker, bỏ lọc hiệu lực"}
GROUPS = (("thuong", "Câu thường"), ("sua_doi", "Câu sửa đổi"), ("bien_the", "Biến thể đời thường"))


def _cell(m: dict) -> str:
    lo, hi = m["ci95"]
    return f"{m['gia_tri']:.2f} [{lo:.2f}–{hi:.2f}]"


def write_summary(report: dict) -> Path:
    """Bảng cho Report 3: mỗi nhóm câu một bảng, mỗi dòng một cấu hình × cách cắt, kèm CI95 bootstrap theo họ."""
    lines = ["# Kết quả tìm kiếm trên tập test (G3, Task 6)", "",
             f"- Tập test: {report['so_cau']} câu; top-{report['cau_hinh_chinh']['top_k']}; tham số chốt trên dev "
             f"(`reports/retrieval/params.json`): rerank_k = {report['cau_hinh_chinh']['rerank_k']}, "
             f"rrf_k = {report['cau_hinh_chinh']['rrf_k']}, bm25_k = dense_k = {report['cau_hinh_chinh']['bm25_k']}.",
             "- Ô bảng: giá trị [khoảng tin cậy 95%, bootstrap theo họ sự kiện]. `any`: tìm được ít nhất một nhóm căn cứ; "
             "`all`: tìm đủ mọi nhóm; MRR: nghịch đảo hạng của đoạn đúng đầu tiên.",
             "- Câu ngoài phạm vi không có căn cứ nên không tính các chỉ số này.", ""]
    for g, title in GROUPS:
        any_row = next(iter(report["ket_qua"].values()))["tong_hop"][g]
        lines += [f"## {title} (n = {any_row['n']}, {any_row['so_ho']} họ sự kiện)", "",
                  "| Cấu hình | Cách cắt | Đúng văn bản | any | all | Tỷ lệ nhóm | MRR |", "|---|---|---|---|---|---|---|"]
        for cut in CUTS:
            for name, label in LABELS.items():
                m = report["ket_qua"][f"{name}/{cut}"]["tong_hop"][g]
                lines.append(f"| {label} | {'Khoản' if cut == 'khoan' else 'Điều'} | {_cell(m['van_ban'])} | "
                             f"{_cell(m['any'])} | {_cell(m['all'])} | {_cell(m['ty_le_nhom'])} | {_cell(m['mrr'])} |")
        lines.append("")
    lines += ["## RQ3: lấy nhầm bản cũ (câu sửa đổi)", "",
              "| Cách cắt | Có lọc hiệu lực | Bỏ lọc hiệu lực |", "|---|---|---|"]
    n = report["ket_qua"]["hybrid+rerank/khoan"]["tong_hop"]["sua_doi"]["n"]
    for cut in CUTS:
        a = report["ket_qua"][f"hybrid+rerank/{cut}"]["sua_doi_lay_ban_cu"]
        b = report["ket_qua"][f"hybrid+rerank_bo_loc/{cut}"]["sua_doi_lay_ban_cu"]
        lines.append(f"| {'Khoản' if cut == 'khoan' else 'Điều'} | {a}/{n} | {b}/{n} |")
    lines += ["", "## Biến thể so với câu gốc (hybrid + reranker)", "",
              "| Cách cắt | Số cặp | any: biến thể / gốc | all: biến thể / gốc | MRR: biến thể / gốc |", "|---|---|---|---|---|"]
    for cut in CUTS:
        v = report["ket_qua"][f"hybrid+rerank/{cut}"]["variant_gap"]
        lines.append(f"| {'Khoản' if cut == 'khoan' else 'Điều'} | {v['n']} | "
                     + " | ".join(f"{v[m]['bien_the']:.2f} / {v[m]['goc']:.2f}" for m in ("any", "all", "mrr")) + " |")
    path = REPORTS / "summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def test_run(force: bool) -> None:
    out = REPORTS / "test_results.json"
    if out.exists() and not force:
        sys.exit(f"{out} đã có: tập test chỉ chạy một lần. Thêm --force nếu thật sự cần.")
    if not PARAMS.exists():
        sys.exit("chưa có reports/retrieval/params.json: chạy --tap dev trước")
    cfg = retrieve.Config(**json.loads(PARAMS.read_text(encoding="utf-8"))["chon"])
    all_items = evalset.load_eval()
    items = [x for x in all_items if x["tap"] == "test"]
    report = {"tap": "test", "so_cau": len(items), "cau_hinh_chinh": asdict(cfg), "params_sha256": sha256(PARAMS),
              "eval_sha256": sha256(config.DATA / "eval" / "eval_v1.jsonl"), "ket_qua": {}, "ngu_canh": {}}
    for cut in CUTS:
        r = retrieve.load(cut)
        report.setdefault("nguon", {})[cut] = {"chunks_sha256": retrieve.load_chunks(cut)[1],
                                                "bo_ma_hoa": r.encode_query.identity,
                                                "reranker": r.reranker.scorer.identity}
        qvec = dict(zip([x["id"] for x in all_items], r.encode_query([x["cau_hoi"] for x in all_items])))
        for name, c in ablation(cfg).items():
            t = time.time()
            rows, _ = run(r, items, qvec, c)
            report["ket_qua"][f"{name}/{cut}"] = {
                "cau_hinh": asdict(c), "tong_hop": score.summarize(rows, all_items, n_boot=1000, seed=0),
                "variant_gap": score.variant_gap(rows, all_items),
                "sua_doi_lay_ban_cu": old_version_count(items, rows),
                "tung_cau": [row for row in rows if row is not None]}
            log(f"test {name}/{cut}: {time.time() - t:.0f} giây")
        # Ngữ cảnh cho G7: cả 270 câu, cấu hình chính có lọc; câu sửa đổi thêm bản bỏ lọc.
        path = config.DATA / "rag" / f"test_with_context_{cut}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as fp:
            for x in all_items:
                hits = r.search(x["cau_hoi"], x["ngay_hoi"], cfg, qvec=qvec[x["id"]])
                raw = (r.search(x["cau_hoi"], x["ngay_hoi"], replace(cfg, loc_hieu_luc=False), qvec=qvec[x["id"]])
                       if x["nhom_cau"] == "sua_doi" else None)
                fp.write(json.dumps(context_record(x, cut, hits, raw), ensure_ascii=False) + "\n")
        report["ngu_canh"][cut] = {"path": path.relative_to(config.ROOT).as_posix(), "sha256": sha256(path),
                                   "so_cau": len(all_items)}
        log(f"-> {path.relative_to(config.ROOT)}")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    log(f"-> {out.relative_to(config.ROOT)}")
    log(f"-> {write_summary(report).relative_to(config.ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", choices=["dev", "test"], required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dev_grid() if a.tap == "dev" else test_run(a.force)


if __name__ == "__main__":
    main()
