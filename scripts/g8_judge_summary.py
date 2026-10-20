"""G8: tổng hợp kết quả chấm nội dung (LLM-Judge) trên tập test.

    py -3.13 scripts/g8_judge_summary.py

Đọc `reports/g8/judge_claude.jsonl`: mỗi dòng là một (lượt, câu) với `dat` (câu trả lời có đủ ý chính và kết luận đúng
so với đáp án chuẩn), `che_tai_sai` (nêu sai mức phạt, điểm trừ, tước GPLX, hình phạt) và `theo_luat_cu` (trả lời theo
phiên bản đã hết hiệu lực). Giám khảo là Claude chấm trực tiếp trong phiên làm việc, đọc câu hỏi, đáp án chuẩn, ghi
chú của bộ eval và câu trả lời; với câu ngoài phạm vi, `dat` = từ chối đúng.

Kết quả ở `reports/g8/`:
- `judge_scores.json`: tỷ lệ đạt theo lượt và nhóm câu (CI95 bootstrap theo cụm như G7), hiệu số ghép cặp, theo loại
  câu, theo nhóm lỗi tự động của `g8_errors.py`, độ khớp với chỉ số tự động, độ khớp với chấm tay (nếu đã điền).
- `judge_summary.md`: các bảng chính.
"""

import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402

G8 = config.ROOT / "reports" / "g8"
JUDGE = G8 / "judge_claude.jsonl"
PER_ITEM = config.ROOT / "reports" / "g7" / "per_item.jsonl"
MANUAL = G8 / "cham_tay_50.csv"
IN_SCOPE = ("thuong", "sua_doi")
GROUPS = ("thuong", "sua_doi", "bien_the", "ngoai_pham_vi")
LABEL = {"thuong": "Thường", "sua_doi": "Sửa đổi", "bien_the": "Biến thể", "ngoai_pham_vi": "Ngoài phạm vi"}
RUN_ORDER = ["D", "B", "D_g8", "B_g8"]
PAIRS = [("D", "B"), ("D_g8", "D"), ("B_g8", "B"), ("D_g8", "B_g8")]
N_BOOT, SEED = 2000, 0


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def uid(x: dict) -> str:
    return f"{x['nhom_cau']}/{x['key']}"


def _ci(s: list[float]) -> list[float]:
    s = sorted(s)
    return [s[int(0.025 * (len(s) - 1))], s[int(0.975 * (len(s) - 1))]]


def cluster_of(item: dict, groups: tuple) -> str:
    if len(groups) > 1 and set(groups) <= set(IN_SCOPE):
        return item.get("ho_su_kien") or item["id"]
    return item.get("ho_cau") or item["id"]


def boot(vals: dict[str, float], items: dict, groups: tuple, rng: random.Random) -> list[float]:
    clusters = defaultdict(list)
    for u, v in vals.items():
        clusters[cluster_of(items[u], groups)].append(v)
    keys = sorted(clusters)
    out = []
    for _ in range(N_BOOT):
        picked = [v for k in rng.choices(keys, k=len(keys)) for v in clusters[k]]
        out.append(sum(picked) / len(picked))
    return out


def mean_ci(vals, items, groups, rng):
    if not vals:
        return None
    return {"gia_tri": sum(vals.values()) / len(vals), "ci95": _ci(boot(vals, items, groups, rng)), "n": len(vals)}


def paired(a, b, items, groups, rng):
    common = sorted(set(a) & set(b))
    if not common:
        return None
    d = {u: a[u] - b[u] for u in common}
    ci = _ci(boot(d, items, groups, rng))
    return {"chenh": sum(d.values()) / len(d), "ci95": ci, "n": len(d), "co_y_nghia": ci[0] > 0 or ci[1] < 0,
            "chi_a_dat": sum(1 for u in common if a[u] > b[u]), "chi_b_dat": sum(1 for u in common if b[u] > a[u])}


def pct(m):
    return "—" if not m else f"{100 * m['gia_tri']:.1f} [{100 * m['ci95'][0]:.1f}–{100 * m['ci95'][1]:.1f}]"


def pdiff(d):
    if not d:
        return "—"
    return (f"{100 * d['chenh']:+.1f} [{100 * d['ci95'][0]:+.1f}, {100 * d['ci95'][1]:+.1f}]"
            + (" *" if d["co_y_nghia"] else ""))


def main() -> None:
    items = {uid(x): x for x in evalset.load_eval()}
    test = {u for u, x in items.items() if x["tap"] == "test"}
    judge = read_jsonl(JUDGE)
    J = defaultdict(dict)
    for r in judge:
        J[r["run"]][r["uid"]] = r
    runs = [r for r in RUN_ORDER if r in J]
    for run in runs:
        missing = test - set(J[run])
        assert not missing, f"{run} còn thiếu {len(missing)} câu test"
    rng = random.Random(SEED)

    def vals(run, field, groups, filt=None):
        return {u: float(r[field]) for u, r in J[run].items()
                if u in test and items[u]["nhom_cau"] in groups and (filt is None or filt(u))}

    rep = {"nguon": JUDGE.relative_to(config.ROOT).as_posix(), "giam_khao": sorted({r["giam_khao"] for r in judge}),
           "tap": "test", "n_boot": N_BOOT, "seed": SEED, "dat": {}, "so_sanh": {}, "che_tai_sai": {},
           "theo_luat_cu": {}, "theo_loai_cau": {}, "theo_nhom_loi_tu_dong": {}, "khop_tu_dong": {}, "khop_cham_tay": {}}

    # 1. Tỷ lệ đạt: trong phạm vi (gộp) và từng nhóm
    for run in runs:
        rep["dat"][run] = {"trong_pham_vi": mean_ci(vals(run, "dat", IN_SCOPE), items, IN_SCOPE, rng),
                           **{g: mean_ci(vals(run, "dat", (g,)), items, (g,), rng) for g in GROUPS}}
        rep["che_tai_sai"][run] = mean_ci(vals(run, "che_tai_sai", IN_SCOPE), items, IN_SCOPE, rng)
        rep["theo_luat_cu"][run] = mean_ci(vals(run, "theo_luat_cu", ("sua_doi",)), items, ("sua_doi",), rng)

    # 2. Hiệu số ghép cặp
    for x, y in PAIRS:
        if x in J and y in J:
            rep["so_sanh"][f"{x}-{y}"] = {
                "trong_pham_vi": paired(vals(x, "dat", IN_SCOPE), vals(y, "dat", IN_SCOPE), items, IN_SCOPE, rng),
                **{g: paired(vals(x, "dat", (g,)), vals(y, "dat", (g,)), items, (g,), rng) for g in GROUPS}}

    # 2b. Câu đổi kết quả giữa ngữ cảnh G7 và ngữ cảnh G8 (cùng mô hình), kèm nhóm lỗi tự động của G7
    rep["doi_ket_qua"] = {}
    for old, new in (("D", "D_g8"), ("B", "B_g8")):
        if old in J and new in J:
            with open(G8 / f"loi_{old}.csv", encoding="utf-8-sig") as fp:
                nhom = {r["uid"]: r["nhom_loi"] for r in csv.DictReader(fp)}
            sang_dung = sorted(u for u in test if not J[old][u]["dat"] and J[new][u]["dat"])
            sang_sai = sorted(u for u in test if J[old][u]["dat"] and not J[new][u]["dat"])
            rep["doi_ket_qua"][f"{old}->{new}"] = {
                "sai_thanh_dung": [{"uid": u, "nhom_loi_g7": nhom.get(u, items[u]["nhom_cau"])} for u in sang_dung],
                "dung_thanh_sai": [{"uid": u, "ly_do": J[new][u]["ly_do"]} for u in sang_sai],
                "sai_thanh_dung_theo_nhom": dict(Counter(nhom.get(u, items[u]["nhom_cau"]) for u in sang_dung))}

    # 3. Theo loại câu (trong phạm vi)
    loai = sorted({items[u]["loai_cau"] for u in test if items[u]["nhom_cau"] in IN_SCOPE})
    for run in runs:
        rep["theo_loai_cau"][run] = {lc: mean_ci(vals(run, "dat", IN_SCOPE, lambda u, lc=lc: items[u]["loai_cau"] == lc),
                                                 items, IN_SCOPE, rng) for lc in loai}

    # 4. So với nhóm lỗi tự động (g8_errors.py) và chỉ số tự động G7 (chỉ có cho các lượt G7)
    auto = {(r["run"], r["uid"]): r for r in read_jsonl(PER_ITEM)}
    for run in [r for r in runs if r in ("B", "D")]:
        with open(G8 / f"loi_{run}.csv", encoding="utf-8-sig") as fp:
            nhom = {r["uid"]: r["nhom_loi"] for r in csv.DictReader(fp)}
        t = defaultdict(Counter)
        for u, g in nhom.items():
            if u in test:
                t[g]["dat" if J[run][u]["dat"] else "khong_dat"] += 1
        rep["theo_nhom_loi_tu_dong"][run] = {g: dict(c) for g, c in sorted(t.items())}

        # Khớp với "nêu đúng mọi số liệu" và với "từ chối" trên câu trong phạm vi
        k = {"so_lieu_du": Counter(), "tu_choi": Counter()}
        lech = []
        for u in test:
            if items[u]["nhom_cau"] not in IN_SCOPE:
                continue
            a, d = auto[(run, u)], J[run][u]["dat"]
            if a["so_lieu"] and a["so_lieu"].get("du") is not None:
                k["so_lieu_du"][f"tu_dong_{int(bool(a['so_lieu']['du']))}/judge_{int(d)}"] += 1
                if bool(a["so_lieu"]["du"]) != d:
                    lech.append({"uid": u, "so_lieu_du": bool(a["so_lieu"]["du"]), "judge_dat": d,
                                 "ly_do": J[run][u]["ly_do"]})
            k["tu_choi"][f"tu_choi_{int(bool(a['tu_choi']))}/judge_{int(d)}"] += 1
        rep["khop_tu_dong"][run] = {**{n: dict(sorted(c.items())) for n, c in k.items()}, "lech_so_lieu": lech}

    # 5. Khớp với chấm tay (nếu đã điền cột dat_D / dat_B)
    if MANUAL.exists():
        with open(MANUAL, encoding="utf-8-sig") as fp:
            rows = list(csv.DictReader(fp))
        for run in ("D", "B"):
            pairs_ = [(r["uid"], r[f"dat_{run}"].strip()) for r in rows if r.get(f"dat_{run}", "").strip() in ("0", "1")]
            if pairs_:
                agree = sum(1 for u, v in pairs_ if J[run][u]["dat"] == (v == "1"))
                rep["khop_cham_tay"][run] = {"n": len(pairs_), "khop": agree, "ty_le": agree / len(pairs_),
                                             "lech": [u for u, v in pairs_ if J[run][u]["dat"] != (v == "1")]}

    (G8 / "judge_scores.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                          newline="\n")
    write_summary(rep, runs, loai)
    print("-> reports/g8/judge_scores.json, judge_summary.md")


def write_summary(rep: dict, runs: list[str], loai: list[str]) -> None:
    D = rep["dat"]
    L = ["# G8 — Chấm nội dung (LLM-Judge) trên tập test", "",
         f"Nguồn: `{rep['nguon']}`. Giám khảo: {', '.join(rep['giam_khao'])}. Giá trị % [CI95 bootstrap theo cụm]; "
         "hiệu số đánh dấu `*` khi CI95 không chứa 0. **Đạt** = đủ ý chính và kết luận đúng so với đáp án chuẩn "
         "(câu ngoài phạm vi: từ chối đúng).", "",
         "## Tỷ lệ đạt", "", "| Nhóm | n | " + " | ".join(runs) + " |", "|---|---|" + "---|" * len(runs)]
    for key, lab in (("trong_pham_vi", "Trong phạm vi (thường + sửa đổi)"), *LABEL.items()):
        n = (D[runs[0]][key] or {}).get("n")
        L.append(f"| {lab} | {n} | " + " | ".join(pct(D[r][key]) for r in runs) + " |")
    L += ["", "## Hiệu số ghép cặp (điểm %)", "", "| Cặp | Trong phạm vi | " + " | ".join(LABEL.values()) + " |",
          "|---|---|" + "---|" * len(LABEL)]
    for name, s in rep["so_sanh"].items():
        L.append(f"| {name} | {pdiff(s['trong_pham_vi'])} | " + " | ".join(pdiff(s[g]) for g in GROUPS) + " |")
    for name, s in rep["so_sanh"].items():
        t = s["trong_pham_vi"]
        L.append(f"\n{name}, trong phạm vi: chỉ {name.split('-')[0]} đạt {t['chi_a_dat']} câu, "
                 f"chỉ {name.split('-')[1]} đạt {t['chi_b_dat']} câu (trên {t['n']}).")
    for name, d in rep.get("doi_ket_qua", {}).items():
        L += ["", f"## Câu đổi kết quả {name} (cả tập test)", "",
              f"- Sai thành đúng: {len(d['sai_thanh_dung'])} câu; theo nhóm lỗi tự động ở G7: "
              + ", ".join(f"{k} {v}" for k, v in sorted(d["sai_thanh_dung_theo_nhom"].items())),
              f"- Đúng thành sai: {len(d['dung_thanh_sai'])} câu: "
              + "; ".join(f"`{x['uid']}` ({x['ly_do']})" for x in d["dung_thanh_sai"])]
    L += ["", "## Lỗi nghiêm trọng", "", "| Chỉ số | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs),
          "| Nêu sai chế tài (trong phạm vi) | " + " | ".join(pct(rep["che_tai_sai"][r]) for r in runs) + " |",
          "| Trả lời theo luật cũ (câu sửa đổi) | " + " | ".join(pct(rep["theo_luat_cu"][r]) for r in runs) + " |",
          "", "## Theo loại câu (trong phạm vi)", "", "| Loại câu | n | " + " | ".join(runs) + " |",
          "|---|---|" + "---|" * len(runs)]
    for lc in loai:
        n = (rep["theo_loai_cau"][runs[0]][lc] or {}).get("n")
        L.append(f"| {lc} | {n} | " + " | ".join(pct(rep["theo_loai_cau"][r][lc]) for r in runs) + " |")
    if rep["theo_nhom_loi_tu_dong"]:
        L += ["", "## So với nhóm lỗi tự động (`loi_*.csv`, thường + sửa đổi + biến thể)", "",
              "| Lượt | Nhóm lỗi tự động | Judge đạt | Judge không đạt |", "|---|---|---|---|"]
        for run, t in rep["theo_nhom_loi_tu_dong"].items():
            for g, c in t.items():
                L.append(f"| {run} | {g} | {c.get('dat', 0)} | {c.get('khong_dat', 0)} |")
        L += ["", "## Khớp với chỉ số tự động (trong phạm vi)", "",
              "| Lượt | Số liệu đủ & đạt | Số liệu đủ & không đạt | Số liệu thiếu & đạt | Số liệu thiếu & không đạt |",
              "|---|---|---|---|---|"]
        for run, k in rep["khop_tu_dong"].items():
            c = k["so_lieu_du"]
            L.append(f"| {run} | {c.get('tu_dong_1/judge_1', 0)} | {c.get('tu_dong_1/judge_0', 0)} | "
                     f"{c.get('tu_dong_0/judge_1', 0)} | {c.get('tu_dong_0/judge_0', 0)} |")
    if rep["khop_cham_tay"]:
        L += ["", "## Khớp với chấm tay", ""]
        for run, k in rep["khop_cham_tay"].items():
            L.append(f"- {run}: khớp {k['khop']}/{k['n']} ({100 * k['ty_le']:.0f}%); lệch: {', '.join(k['lech']) or '—'}")
    else:
        L += ["", "Chưa có chấm tay: điền cột `dat_D`, `dat_B` (0/1) trong `cham_tay_50.csv` rồi chạy lại script."]
    (G8 / "judge_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
