"""G8: chấm tự động câu trả lời D_g8, B_g8 (ngữ cảnh mở rộng lên Điều) và so với D, B của G7.

    py -3.13 scripts/score_g8.py          # đọc kaggle/g8/out_g8/g7_answers.jsonl (540 câu)

Dùng đúng các tiêu chí và cách bootstrap của `score_g7.py`. Kết quả ở `reports/g8/auto/`:
- `per_item.jsonl`: chấm từng (lượt, câu) của D_g8, B_g8.
- `scores.json`: chỉ số từng lượt trên test, hiệu số ghép cặp D_g8 − D, B_g8 − B, D_g8 − B_g8, và với mỗi nhóm lỗi tự
  động của D (`reports/g8/loi_D.csv`) bao nhiêu câu đã thành "đúng" ở D_g8.
- `summary.md`: các bảng chính.
"""

import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import g8_errors  # noqa: E402
import score_g7 as G  # noqa: E402
from lawproc import config, evalset  # noqa: E402
from rag import answer_score as S  # noqa: E402

ANSWERS = config.ROOT / "kaggle" / "g8" / "out_g8" / "g7_answers.jsonl"
OUT = config.ROOT / "reports" / "g8" / "auto"
RUNS = ["D", "B", "D_g8", "B_g8"]
PAIRS = [("D_g8", "D"), ("B_g8", "B"), ("D_g8", "B_g8")]


def main() -> None:
    items = {G.uid(x): x for x in evalset.load_eval()}
    with open(config.DATA / "manifest.csv", encoding="utf-8-sig") as fp:
        doc_ids = {r["doc_id"] for r in csv.DictReader(fp)}
    corpus = S.corpus_numbers(doc_ids | {x["van_ban"] for x in items.values() if x.get("van_ban")})
    answers = G.read_jsonl(ANSWERS)
    assert len(answers) == 540 and len({(r["run"], r["uid"]) for r in answers}) == 540, "thiếu hoặc trùng câu trả lời"

    recs = []
    for ans in answers:
        it = items[ans["uid"]]
        recs.append({"run": ans["run"], "uid": ans["uid"], "id": it["id"], "tap": it["tap"], "nhom_cau": it["nhom_cau"],
                     "loai_cau": it["loai_cau"], "cham_gioi_han": ans["cham_gioi_han"],
                     "so_token_moi": ans["so_token_moi"], "giay": ans["giay"], "tra_loi": ans["tra_loi"],
                     **S.score_answer(it, ans["tra_loi"], corpus)})
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "per_item.jsonl", "w", encoding="utf-8", newline="\n") as fp:
        fp.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)

    by_run = defaultdict(dict)
    for r in G.read_jsonl(G.OUT / "per_item.jsonl"):
        if r["run"] in ("D", "B"):
            by_run[r["run"]][r["uid"]] = r
    for r in recs:
        by_run[r["run"]][r["uid"]] = r
    test = {u for u, x in items.items() if x["tap"] == "test"}
    rng = random.Random(G.SEED)

    def vals(run, metric, groups):
        out = {}
        for u, r in by_run[run].items():
            if u in test and r["nhom_cau"] in groups:
                v = G.value(metric, r)
                if v is not None:
                    out[u] = v
        return out

    M = {m[0]: m for m in G.METRICS}
    rep = {"answers": ANSWERS.relative_to(config.ROOT).as_posix(),
           "answers_sha256": hashlib.sha256(ANSWERS.read_bytes()).hexdigest(), "tap": "test", "n_boot": G.N_BOOT,
           "seed": G.SEED, "chi_so": {}, "so_sanh": {}, "nhom_loi_D": {}, "toc_do": {}}
    for name, label, groups, _, higher in G.METRICS:
        entry = {"mo_ta": label, "cao_la_tot": higher, "nhom": list(groups), "luot": {}}
        for run in RUNS:
            res = {"gop": G.mean_ci(vals(run, M[name], groups), items, groups, rng)}
            if len(groups) > 1:
                res.update({g: G.mean_ci(vals(run, M[name], (g,)), items, (g,), rng) for g in groups})
            entry["luot"][run] = res
        rep["chi_so"][name] = entry
        rep["so_sanh"][name] = {f"{x}-{y}": G.paired_diff(vals(x, M[name], groups), vals(y, M[name], groups),
                                                          items, groups, rng) for x, y in PAIRS}

    # Nhóm lỗi tự động của D (G7) → D_g8 có thành "đúng" không (cùng hàm `correct` của g8_errors)
    for run, new in (("D", "D_g8"), ("B", "B_g8")):
        with open(config.ROOT / "reports" / "g8" / f"loi_{run}.csv", encoding="utf-8-sig") as fp:
            nhom = {r["uid"]: r["nhom_loi"] for r in csv.DictReader(fp) if r["uid"] in test}
        t = defaultdict(Counter)
        for u, g in nhom.items():
            t[g]["dung_sau" if g8_errors.correct(by_run[new][u]) else "sai_sau"] += 1
        rep["nhom_loi_D" if run == "D" else "nhom_loi_B"] = {g: dict(c) for g, c in sorted(t.items())}

    for run in RUNS:
        rs = [r for u, r in by_run[run].items() if u in test]
        rep["toc_do"][run] = {"token_moi_tb": sum(r["so_token_moi"] for r in rs) / len(rs),
                              "cham_gioi_han": sum(1 for r in rs if r["cham_gioi_han"]),
                              **({"giay_tb": sum(r["giay"] for r in rs) / len(rs)} if "giay" in rs[0] else {})}

    (OUT / "scores.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                     newline="\n")
    write_summary(rep)
    print("-> reports/g8/auto/per_item.jsonl, scores.json, summary.md")


def write_summary(rep: dict) -> None:
    C, P = rep["chi_so"], rep["so_sanh"]
    L = ["# G8 — Chấm tự động D_g8, B_g8 (ngữ cảnh mở rộng lên Điều) so với D, B", "",
         "Tập test. Giá trị % [CI95 bootstrap theo cụm, như G7]; hiệu số ghép cặp, `*` khi CI95 không chứa 0.", "",
         "| Chỉ số | n | D | D_g8 | D_g8 − D | B | B_g8 | B_g8 − B |", "|---|---|---|---|---|---|---|---|"]
    for name in G.MAIN:
        e = C[name]
        n = (e["luot"]["D"]["gop"] or {}).get("n")
        pct = name != "rouge_l"
        L.append(f"| {e['mo_ta']} | {n} | " + " | ".join(
            [G.fmt(e["luot"]["D"]["gop"], pct), G.fmt(e["luot"]["D_g8"]["gop"], pct),
             G.fmt_diff(P[name]["D_g8-D"], pct), G.fmt(e["luot"]["B"]["gop"], pct),
             G.fmt(e["luot"]["B_g8"]["gop"], pct), G.fmt_diff(P[name]["B_g8-B"], pct)]) + " |")
    L += ["", "## Theo nhóm câu: nêu đúng mọi số liệu và từ chối sai", "",
          "| Chỉ số | Nhóm | D | D_g8 | B | B_g8 |", "|---|---|---|---|---|---|"]
    for name in ("so_lieu_du", "trich_khoan", "tu_choi_sai"):
        e = C[name]
        for g in e["nhom"]:
            L.append(f"| {e['mo_ta']} | {g} | " + " | ".join(G.fmt(e["luot"][r].get(g)) for r in ("D", "D_g8", "B", "B_g8"))
                     + " |")
    for run, key in (("D", "nhom_loi_D"), ("B", "nhom_loi_B")):
        L += ["", f"## Nhóm lỗi tự động của {run} (G7) → {run}_g8", "", "| Nhóm ở G7 | Đúng ở G8 | Sai ở G8 |", "|---|---|---|"]
        for g, c in rep[key].items():
            L.append(f"| {g} | {c.get('dung_sau', 0)} | {c.get('sai_sau', 0)} |")
    L += ["", "## Độ dài và tốc độ (test)", "", "| Lượt | Token sinh TB | Chạm giới hạn 512 | Giây/câu TB |", "|---|---|---|---|"]
    for run, t in rep["toc_do"].items():
        L.append(f"| {run} | {t['token_moi_tb']:.0f} | {t['cham_gioi_han']} | "
                 + (f"{t['giay_tb']:.1f}" if "giay_tb" in t else "—") + " |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
