"""G7: chấm tự động 1.160 câu trả lời A/B/C/D (và bản bỏ lọc hiệu lực) theo rubric của `data/eval/README.md`.

    py -3.13 scripts/score_g7.py                      # đọc kaggle/g7/out_g7/g7_answers.jsonl
    py -3.13 scripts/score_g7.py --answers PATH

Kết quả ở `reports/g7/`:
- `per_item.jsonl` (đủ trường) và `per_item.csv` (mở bằng Excel): mọi tiêu chí của từng (lượt, câu), dùng cho G8.
- `scores.json`: tổng hợp trên tập **test** theo nhóm câu, CI95 bootstrap, so sánh từng cặp lượt, biến thể so với câu
  gốc, Khoản đã gặp hay chưa gặp trong dữ liệu train.
- `summary.md`: các bảng chính.

Quy ước (theo README của bộ eval):
- Báo cáo riêng từng nhóm câu, luôn ghi mẫu số. "Trong phạm vi" = câu thường + câu sửa đổi, bootstrap theo
  `ho_su_kien`; một nhóm riêng thì theo `ho_cau`.
- So sánh hai lượt là so sánh **ghép cặp** trên cùng câu: bootstrap hiệu số theo cùng các cụm.
- Biến thể được so với câu gốc cùng `ho_cau`, không cộng gộp như câu độc lập.
- Phần "nội dung" (đủ ý chính) cần LLM-Judge hoặc chấm tay; script này chỉ chấm phần tự động được.
"""

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import answer_score as S  # noqa: E402

OUT = config.ROOT / "reports" / "g7"
ANSWERS = config.ROOT / "kaggle" / "g7" / "out_g7" / "g7_answers.jsonl"
RUNS = ["A", "B", "C", "D", "B_boloc", "D_boloc"]
RUN_LABEL = {"A": "A: gốc", "B": "B: gốc + RAG", "C": "C: LoRA", "D": "D: LoRA + RAG",
             "B_boloc": "B bỏ lọc hiệu lực", "D_boloc": "D bỏ lọc hiệu lực"}
IN_SCOPE = ("thuong", "sua_doi")
N_BOOT, SEED = 2000, 0

# (tên, mô tả, nhóm câu áp dụng, hàm lấy giá trị từ kết quả chấm, cao hơn là tốt?)
METRICS = [
    ("so_lieu_du", "Nêu đúng mọi số liệu", IN_SCOPE, lambda r: r["so_lieu"] and r["so_lieu"]["du"], True),
    ("so_lieu_ty_le", "Tỷ lệ số liệu đúng", IN_SCOPE, lambda r: r["so_lieu"] and r["so_lieu"]["ty_le"], True),
    ("muc_phat", "Đúng khung phạt tiền", IN_SCOPE, lambda r: r["muc_phat"] and r["muc_phat"]["dung_khung"], True),
    ("diem_tru", "Đúng trừ điểm / không trừ", IN_SCOPE, lambda r: r["diem_tru"], True),
    ("tuoc_gplx", "Đúng thời hạn tước GPLX", IN_SCOPE, lambda r: r["tuoc_gplx"], True),
    ("trich_van_ban", "Trích đúng văn bản", IN_SCOPE, lambda r: r["trich_dan"] and r["trich_dan"]["van_ban"], True),
    ("trich_dieu", "Trích đúng Điều", IN_SCOPE, lambda r: r["trich_dan"] and r["trich_dan"].get("dieu"), True),
    ("trich_khoan", "Trích đúng Khoản", IN_SCOPE, lambda r: r["trich_dan"] and r["trich_dan"].get("khoan"), True),
    ("ngoai_kho", "Trích văn bản ngoài kho (cũ/bịa)", (*IN_SCOPE, "bien_the"),
     lambda r: bool(r["van_ban_ngoai_kho"]), False),
    ("tu_choi_sai", "Từ chối sai câu trong phạm vi", (*IN_SCOPE, "bien_the"), lambda r: r["tu_choi"], False),
    ("tu_choi_dung", "Từ chối đúng câu ngoài phạm vi", ("ngoai_pham_vi",), lambda r: r["tu_choi_dung"], True),
    ("rq3_moi", "Theo bản mới (RQ3)", ("sua_doi",),
     lambda r: r["rq3"]["theo_ban_moi"] if r["rq3"]["do_duoc_moi"] else None, True),
    ("rq3_cu", "Nêu số liệu bản cũ (RQ3)", ("sua_doi",),
     lambda r: r["rq3"]["trich_ban_cu"] if r["rq3"]["do_duoc_cu"] else None, False),
    ("rouge_l", "ROUGE-L F1", (*IN_SCOPE, "bien_the"), lambda r: r["rouge_l"], True),
    ("lap_vong", "Lặp vòng", (*IN_SCOPE, "bien_the", "ngoai_pham_vi"), lambda r: r["lap_vong"], False),
    ("cham_gioi_han", "Chạm giới hạn 512 token", (*IN_SCOPE, "bien_the", "ngoai_pham_vi"),
     lambda r: r["cham_gioi_han"], False),
]
MAIN = ["so_lieu_du", "muc_phat", "diem_tru", "trich_van_ban", "trich_khoan", "ngoai_kho", "tu_choi_sai",
        "tu_choi_dung", "rouge_l", "lap_vong", "cham_gioi_han"]
PAIRS = [("D", "B"), ("D", "C"), ("B", "A"), ("C", "A"), ("D", "A")]
RQ3_PAIRS = [("B", "B_boloc"), ("D", "D_boloc")]


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def uid(x: dict) -> str:
    return f"{x['nhom_cau']}/{x['key']}"


def value(metric: tuple, rec: dict):
    v = metric[3](rec)
    return None if v is None else float(v)


# ---------------------------------------------------------------- bootstrap

def _ci(samples: list[float]) -> list[float]:
    s = sorted(samples)
    return [s[int(0.025 * (len(s) - 1))], s[int(0.975 * (len(s) - 1))]]


def cluster_of(item: dict, groups: tuple) -> str:
    if len(groups) > 1 and set(groups) <= set(IN_SCOPE):
        return item.get("ho_su_kien") or item["id"]
    return item.get("ho_cau") or item["id"]


def mean_ci(vals: dict[str, float], items: dict, groups: tuple, rng: random.Random) -> dict | None:
    """vals: uid -> giá trị. Trung bình và CI95 bootstrap theo cụm."""
    if not vals:
        return None
    clusters = defaultdict(list)
    for u, v in vals.items():
        clusters[cluster_of(items[u], groups)].append(v)
    keys = sorted(clusters)
    boot = []
    for _ in range(N_BOOT):
        picked = [v for k in rng.choices(keys, k=len(keys)) for v in clusters[k]]
        boot.append(sum(picked) / len(picked))
    return {"gia_tri": sum(vals.values()) / len(vals), "ci95": _ci(boot), "n": len(vals), "so_cum": len(keys)}


def paired_diff(a: dict[str, float], b: dict[str, float], items: dict, groups: tuple, rng: random.Random) -> dict | None:
    common = sorted(set(a) & set(b))
    if not common:
        return None
    clusters = defaultdict(list)
    for u in common:
        clusters[cluster_of(items[u], groups)].append(a[u] - b[u])
    keys = sorted(clusters)
    boot = []
    for _ in range(N_BOOT):
        picked = [d for k in rng.choices(keys, k=len(keys)) for d in clusters[k]]
        boot.append(sum(picked) / len(picked))
    ci = _ci(boot)
    return {"chenh": sum(a[u] - b[u] for u in common) / len(common), "ci95": ci, "n": len(common),
            "co_y_nghia": ci[0] > 0 or ci[1] < 0}


# ---------------------------------------------------------------- main

def train_khoan_keys() -> set[str]:
    def key(u: str) -> str:
        return ":".join(u.split("@")[0].split(":")[:3])
    rows = read_jsonl(config.DATA / "train" / "train.jsonl")
    return {key(v) for r in rows for v in r.get("can_cu") or []}


def flat(rec: dict) -> dict:
    sl, mp, td, r3 = rec["so_lieu"] or {}, rec["muc_phat"] or {}, rec["trich_dan"] or {}, rec["rq3"] or {}
    return {"run": rec["run"], "uid": rec["uid"], "id": rec["id"], "tap": rec["tap"], "nhom_cau": rec["nhom_cau"],
            "loai_cau": rec["loai_cau"], "so_lieu_dung": sl.get("dung"), "so_lieu_n": sl.get("n"),
            "so_lieu_du": sl.get("du"), "muc_phat_khung": mp.get("dung_khung"), "diem_tru": rec["diem_tru"],
            "tuoc_gplx": rec["tuoc_gplx"], "trich_van_ban": td.get("van_ban"), "trich_dieu": td.get("dieu"),
            "trich_khoan": td.get("khoan"), "van_ban_ngoai_kho": "; ".join(rec["van_ban_ngoai_kho"]),
            "tu_choi": rec["tu_choi"], "tu_choi_dung": rec["tu_choi_dung"], "rq3_moi": r3.get("theo_ban_moi"),
            "rq3_cu": r3.get("trich_ban_cu"), "rouge_l": None if rec["rouge_l"] is None else round(rec["rouge_l"], 3),
            "lap_vong": rec["lap_vong"], "cham_gioi_han": rec["cham_gioi_han"], "so_token_moi": rec["so_token_moi"],
            "khoan_da_gap_khi_train": rec["khoan_da_gap"], "ngu_canh_co_can_cu": rec["ngu_canh_co_can_cu"],
            "tra_loi": rec["tra_loi"]}


def fmt(m: dict | None, pct: bool = True) -> str:
    if not m:
        return "—"
    f = (lambda x: f"{100 * x:.1f}") if pct else (lambda x: f"{x:.3f}")
    return f"{f(m['gia_tri'])} [{f(m['ci95'][0])}–{f(m['ci95'][1])}]"


def fmt_diff(d: dict | None, pct: bool = True) -> str:
    if not d:
        return "—"
    f = (lambda x: f"{100 * x:+.1f}") if pct else (lambda x: f"{x:+.3f}")
    return f"{f(d['chenh'])} [{f(d['ci95'][0])}, {f(d['ci95'][1])}]" + (" *" if d["co_y_nghia"] else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", default=str(ANSWERS))
    a = ap.parse_args()
    answers_path = Path(a.answers)

    items = {uid(x): x for x in evalset.load_eval()}
    with open(config.DATA / "manifest.csv", encoding="utf-8-sig") as fp:   # đủ 40 văn bản của kho
        doc_ids = {r["doc_id"] for r in csv.DictReader(fp)}
    # QCVN 41:2024 nằm trong kho dưới mã của TT 51/2024 nhưng bộ eval gọi là `qcvn_41_2024`: lấy cả hai bộ mã
    corpus = S.corpus_numbers(doc_ids | {x["van_ban"] for x in items.values() if x.get("van_ban")})
    seen_keys = train_khoan_keys()
    g3 = json.loads((config.ROOT / "reports" / "retrieval" / "test_results.json").read_text(encoding="utf-8"))
    found = {r["id"]: r["any"] for r in g3["ket_qua"]["hybrid+rerank/khoan"]["tung_cau"]}   # ngữ cảnh B/D có căn cứ?
    answers = read_jsonl(answers_path)
    assert len(answers) == 1160 and len({(r["run"], r["uid"]) for r in answers}) == 1160, "thiếu hoặc trùng câu trả lời"

    recs = []
    for ans in answers:
        it = items[ans["uid"]]
        rec = {"run": ans["run"], "uid": ans["uid"], "id": it["id"], "tap": it["tap"], "nhom_cau": it["nhom_cau"],
               "loai_cau": it["loai_cau"], "cham_gioi_han": ans["cham_gioi_han"], "so_token_moi": ans["so_token_moi"],
               "khoan_da_gap": (":".join((it.get("dia_chi_chinh") or "").split(":")[:3]) in seen_keys
                                if it.get("dia_chi_chinh") else None),
               "ngu_canh_co_can_cu": found.get(it["id"]),
               "tra_loi": ans["tra_loi"], **S.score_answer(it, ans["tra_loi"], corpus)}
        recs.append(rec)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "per_item.jsonl", "w", encoding="utf-8", newline="\n") as fp:
        fp.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)
    rows = [flat(r) for r in recs]
    with open(OUT / "per_item.csv", "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    test = {u for u, x in items.items() if x["tap"] == "test"}
    by_run = defaultdict(dict)
    for r in recs:
        by_run[r["run"]][r["uid"]] = r
    rng = random.Random(SEED)

    def vals(run: str, metric: tuple, groups: tuple, filt=None) -> dict[str, float]:
        out = {}
        for u, r in by_run[run].items():
            if u in test and r["nhom_cau"] in groups and (filt is None or filt(r)):
                v = value(metric, r)
                if v is not None:
                    out[u] = v
        return out

    M = {m[0]: m for m in METRICS}
    report = {"answers": answers_path.relative_to(config.ROOT).as_posix(),
              "answers_sha256": hashlib.sha256(answers_path.read_bytes()).hexdigest(),
              "eval_sha256": json.loads((config.DATA / "eval" / "MANIFEST.json").read_text(encoding="utf-8"))
              .get("eval", {}).get("sha256"),
              "tap": "test", "n_boot": N_BOOT, "seed": SEED, "chi_so": {}, "so_sanh": {}, "rq3": {}, "bien_the": {},
              "da_gap_khi_train": {}, "theo_loai_cau": {}}

    # 1. Từng chỉ số, từng lượt: gộp nhóm áp dụng và riêng từng nhóm
    for name, label, groups, _, higher in METRICS:
        entry = {"mo_ta": label, "cao_la_tot": higher, "nhom": list(groups), "luot": {}}
        for run in RUNS:
            if run.endswith("_boloc") and name not in ("so_lieu_du", "rq3_moi", "rq3_cu", "trich_van_ban"):
                continue
            g = ("sua_doi",) if run.endswith("_boloc") else groups
            res = {"gop": mean_ci(vals(run, M[name], g), items, g, rng)}
            if len(g) > 1:
                res.update({grp: mean_ci(vals(run, M[name], (grp,)), items, (grp,), rng) for grp in g})
            entry["luot"][run] = res
        report["chi_so"][name] = entry

    # 2. So sánh ghép cặp giữa các lượt
    for name, _, groups, _, _ in METRICS:
        report["so_sanh"][name] = {f"{x}-{y}": paired_diff(vals(x, M[name], groups), vals(y, M[name], groups),
                                                          items, groups, rng) for x, y in PAIRS}

    # 3. RQ3: có lọc so với bỏ lọc hiệu lực, trên câu sửa đổi
    for name in ("so_lieu_du", "rq3_moi", "rq3_cu", "trich_van_ban"):
        report["rq3"][name] = {f"{x}-{y}": paired_diff(vals(x, M[name], ("sua_doi",)), vals(y, M[name], ("sua_doi",)),
                                                      items, ("sua_doi",), rng) for x, y in RQ3_PAIRS}

    # 4. Biến thể so với câu gốc (cùng lượt), trên các cặp thuộc test
    by_id = {x["id"]: u for u, x in items.items()}
    pairs = [(u, by_id[x["goc_id"]]) for u, x in items.items()
             if x["nhom_cau"] == "bien_the" and u in test and x.get("goc_id") in by_id]
    for name in ("so_lieu_du", "trich_van_ban", "trich_khoan", "tu_choi_sai", "rouge_l"):
        report["bien_the"][name] = {}
        for run in RUNS[:4]:
            pv = [(value(M[name], by_run[run][v]), value(M[name], by_run[run][g])) for v, g in pairs]
            pv = [(x, y) for x, y in pv if x is not None and y is not None]
            report["bien_the"][name][run] = ({"n_cap": len(pv), "bien_the": sum(x for x, _ in pv) / len(pv),
                                              "goc": sum(y for _, y in pv) / len(pv)} if pv else None)

    # 5. Khoản chính đã gặp hay chưa gặp trong dữ liệu train
    for name in ("so_lieu_du", "trich_khoan", "rouge_l"):
        report["da_gap_khi_train"][name] = {}
        for run in RUNS[:4]:
            report["da_gap_khi_train"][name][run] = {
                lab: mean_ci(vals(run, M[name], IN_SCOPE, lambda r, s=s: r["khoan_da_gap"] is s), items, IN_SCOPE, rng)
                for lab, s in (("da_gap", True), ("chua_gap", False))}

    # 6. Theo loại câu (số liệu đủ)
    loai = sorted({items[u]["loai_cau"] for u in test if items[u]["nhom_cau"] in IN_SCOPE})
    for run in RUNS[:4]:
        report["theo_loai_cau"][run] = {
            lc: mean_ci(vals(run, M["so_lieu_du"], IN_SCOPE, lambda r, lc=lc: r["loai_cau"] == lc), items, IN_SCOPE, rng)
            for lc in loai}

    # 7. B và D theo việc 5 đoạn đưa vào có chứa căn cứ hay không (retriever G3 `any`)
    report["theo_ngu_canh"] = {}
    for name, groups in (("tu_choi_sai", (*IN_SCOPE, "bien_the")), ("so_lieu_du", IN_SCOPE), ("trich_khoan", IN_SCOPE)):
        report["theo_ngu_canh"][name] = {
            run: {lab: mean_ci(vals(run, M[name], groups, lambda r, s=s: r["ngu_canh_co_can_cu"] is s), items, groups, rng)
                  for lab, s in (("co_can_cu", True), ("khong_co_can_cu", False))} for run in ("B", "D")}

    (OUT / "scores.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                     newline="\n")
    write_summary(report)
    print(f"-> {(OUT / 'per_item.csv').relative_to(config.ROOT)}, scores.json, summary.md")


def write_summary(rep: dict) -> None:
    C = rep["chi_so"]
    L = [f"# G7 — Kết quả chấm tự động trên tập test ({rep['answers']})", "",
         "Giá trị % [CI95 bootstrap]; `n` là mẫu số. Trong phạm vi = câu thường + câu sửa đổi. Hiệu số đánh dấu `*` khi "
         "CI95 không chứa 0. Phần nội dung (đủ ý chính) chưa chấm (cần LLM-Judge hoặc chấm tay).", "",
         "## Bảng chính", "", "| Chỉ số | n | " + " | ".join(RUN_LABEL[r] for r in RUNS[:4]) + " |",
         "|---|---|" + "---|" * 4]
    for name in MAIN:
        e = C[name]
        n = (e["luot"]["D"]["gop"] or {}).get("n")
        pct = name != "rouge_l"
        arrow = "↑" if e["cao_la_tot"] else "↓"
        L.append(f"| {e['mo_ta']} {arrow} | {n} | " + " | ".join(fmt(e["luot"][r]["gop"], pct) for r in RUNS[:4]) + " |")
    L += ["", "## So sánh ghép cặp (điểm %)", "", "| Chỉ số | " + " | ".join(f"{x} − {y}" for x, y in PAIRS) + " |",
          "|---|" + "---|" * len(PAIRS)]
    for name in MAIN:
        pct = name != "rouge_l"
        L.append(f"| {C[name]['mo_ta']} | " + " | ".join(fmt_diff(rep["so_sanh"][name][f"{x}-{y}"], pct)
                                                         for x, y in PAIRS) + " |")
    L += ["", "## Theo nhóm câu: nêu đúng mọi số liệu", "", "| Nhóm | " + " | ".join(RUNS[:4]) + " |", "|---|" + "---|" * 4]
    for grp in IN_SCOPE:
        L.append(f"| {grp} | " + " | ".join(fmt(C["so_lieu_du"]["luot"][r].get(grp)) for r in RUNS[:4]) + " |")
    L += ["", "## RQ3: câu sửa đổi, có lọc so với bỏ lọc hiệu lực", "",
          "| Chỉ số | B | B bỏ lọc | B − B bỏ lọc | D | D bỏ lọc | D − D bỏ lọc |", "|---|---|---|---|---|---|---|"]
    for name in ("so_lieu_du", "rq3_moi", "rq3_cu", "trich_van_ban"):
        e = C[name]["luot"]
        L.append(f"| {C[name]['mo_ta']} | {fmt(e['B'].get('sua_doi') or e['B']['gop'])} | {fmt(e['B_boloc']['gop'])} | "
                 f"{fmt_diff(rep['rq3'][name]['B-B_boloc'])} | {fmt(e['D'].get('sua_doi') or e['D']['gop'])} | "
                 f"{fmt(e['D_boloc']['gop'])} | {fmt_diff(rep['rq3'][name]['D-D_boloc'])} |")
    L += ["", "## Biến thể đời thường so với câu gốc (cùng lượt)", "",
          "| Chỉ số | " + " | ".join(f"{r}: biến thể / gốc" for r in RUNS[:4]) + " |", "|---|" + "---|" * 4]
    for name, e in rep["bien_the"].items():
        pct = name != "rouge_l"
        f = (lambda x: f"{100 * x:.1f}") if pct else (lambda x: f"{x:.3f}")
        L.append(f"| {C[name]['mo_ta']} | " + " | ".join(
            f"{f(e[r]['bien_the'])} / {f(e[r]['goc'])} (n={e[r]['n_cap']})" if e[r] else "—" for r in RUNS[:4]) + " |")
    L += ["", "## Khoản chính đã gặp / chưa gặp trong dữ liệu train (trong phạm vi)", "",
          "| Chỉ số | " + " | ".join(f"{r}: đã gặp / chưa gặp" for r in RUNS[:4]) + " |", "|---|" + "---|" * 4]
    for name, e in rep["da_gap_khi_train"].items():
        pct = name != "rouge_l"
        L.append(f"| {C[name]['mo_ta']} | " + " | ".join(
            f"{fmt(e[r]['da_gap'], pct)} (n={(e[r]['da_gap'] or {}).get('n')}) / {fmt(e[r]['chua_gap'], pct)} "
            f"(n={(e[r]['chua_gap'] or {}).get('n')})" for r in RUNS[:4]) + " |")
    L += ["", "## B và D theo việc ngữ cảnh có chứa căn cứ (retriever G3 tìm được ít nhất một nhóm căn cứ)", "",
          "| Chỉ số | B: có căn cứ / không | D: có căn cứ / không |", "|---|---|---|"]
    for name, e in rep["theo_ngu_canh"].items():
        L.append(f"| {C[name]['mo_ta']} | " + " | ".join(
            f"{fmt(e[r]['co_can_cu'])} (n={(e[r]['co_can_cu'] or {}).get('n')}) / {fmt(e[r]['khong_co_can_cu'])} "
            f"(n={(e[r]['khong_co_can_cu'] or {}).get('n')})" for r in ("B", "D")) + " |")
    L += ["", "## Theo loại câu: nêu đúng mọi số liệu", "", "| Loại câu | " + " | ".join(RUNS[:4]) + " |",
          "|---|" + "---|" * 4]
    for lc in rep["theo_loai_cau"]["D"]:
        L.append(f"| {lc} | " + " | ".join(
            f"{fmt(rep['theo_loai_cau'][r][lc])} (n={(rep['theo_loai_cau'][r][lc] or {}).get('n')})" for r in RUNS[:4])
            + " |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
