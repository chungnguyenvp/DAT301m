"""Read-only audit of eval inputs; writes evidence only beside this script."""

import copy
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import evalset  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clause(vid):
    return ":".join(vid.split("@")[0].split(":")[:3])


def main():
    items = evalset.load_eval()
    records = evalset.load_versions()
    by_id = {x["id"]: x for x in items}
    by_vid = evalset.by_version(records)
    baseline = evalset.check_items(items, records)
    spec = importlib.util.spec_from_file_location("eval_builder_audit", ROOT / "scripts/build_eval.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    built = builder.build(records)
    matrix = {(r["chu_de"], r["loai_cau"]): int(r["so_cau"])
              for r in csv.DictReader((evalset.EVAL / "eval_matrix.csv").open(encoding="utf-8-sig"))}
    got_matrix = Counter((x["chu_de"], x["loai_cau"]) for x in items if x["nhom_cau"] == "thuong")

    changes = [
        ("reversed_fine_bounds", "TH135", {"muc_phat_min": 600000, "muc_phat_max": 400000}),
        ("unsupported_one_dong", "TH135", {"dap_an": "Phạt 1 đồng."}),
        ("wrong_suspension_duration", "TH138", {"dap_an": by_id["TH138"]["dap_an"].replace(
            "22 tháng đến 24 tháng", "01 tháng đến 02 tháng")}),
        ("nonexistent_answer_citation", "TH135", {"dap_an": by_id["TH135"]["dap_an"].replace(
            "điểm h khoản 2 Điều 7", "điểm z khoản 99 Điều 999")}),
        ("wrong_rq3_duration", "SD024", {"dap_an": by_id["SD024"]["dap_an"].replace("02 ngày", "99 ngày")}),
        ("unrelated_point_deduction", "TH135", {
            "diem_tru": 4,
            "can_cu": by_id["TH135"]["can_cu"] + ["nd_168_2024:d7:k13:b@2025-01-01"],
            "dap_an": by_id["TH135"]["dap_an"] + " Trừ 04 điểm giấy phép lái xe."}),
    ]
    mutation_results = []
    for name, iid, change in changes:
        mutated = copy.deepcopy(by_id[iid])
        mutated.update(change)
        problems = evalset.check_items([mutated], records)
        mutation_results.append({"name": name, "id": iid, "changed_fields": change,
                                 "problems": problems, "incorrect_mutation_accepted": not problems})

    dev_vids = {v for x in items if x["tap"] == "dev" for v in x["can_cu"]}
    answerable_test = [x for x in items if x["tap"] == "test" and x["can_cu"]]
    overlap = [{"id": x["id"], "shared_version_ids": sorted(set(x["can_cu"]) & dev_vids)}
               for x in answerable_test if set(x["can_cu"]) & dev_vids]
    signatures = defaultdict(list)
    for x in items:
        if x["nhom_cau"] in {"thuong", "sua_doi"}:
            signatures[tuple(sorted(x["can_cu"]))].append(x["id"])
    variants = [x for x in items if x["nhom_cau"] == "bien_the"]
    too_many = [{"id": x["id"], "distinct_clauses": len({clause(v) for v in x["can_cu"]})}
                for x in items if x["nhom_cau"] == "thuong" and
                len({clause(v) for v in x["can_cu"]}) > 5]
    selected = ["SD001", "SD002", "SD003", "SD004", "SD005", "SD006", "SD014", "SD015", "SD017",
                "SD020", "SD025", "SD040", "TH010", "TH095", "TH138", "TH141", "BT004", "BT024", "BT026"]
    snapshots = []
    for iid in selected:
        x = by_id[iid]
        refs = x["can_cu"] + x.get("can_cu_cu", [])
        snapshots.append({"line": items.index(x) + 1, "item": x,
                          "source_records": [by_vid[v] for v in dict.fromkeys(refs)]})

    # Demonstrate that top-n hash selection is deterministic, but can displace a dev member on insertion.
    original_dev = builder.pick_dev(items)
    displaced = None
    for n in range(1000):
        added = {"nhom_cau": "sua_doi", "key": f"audit-inserted-{n}"}
        changed_dev = builder.pick_dev(items + [added])
        if original_dev - changed_dev:
            displaced = {"inserted_key": added["key"], "displaced_dev_keys": sorted(original_dev - changed_dev)}
            break

    inputs = [ROOT / "data/eval/eval_v1.jsonl", ROOT / "data/eval/eval_matrix.csv",
              ROOT / "data/processed/legal_units_versioned.jsonl", ROOT / "src/lawproc/evalset.py",
              ROOT / "scripts/build_eval.py", ROOT / "tests/test_evalset.py"]
    result = {
        "review_date": "2026-10-17", "cutoff": "2026-10-01",
        "input_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in inputs},
        "count": len(items), "groups": dict(Counter(x["nhom_cau"] for x in items)),
        "splits": dict(Counter(x["tap"] for x in items)), "matrix_matches": dict(got_matrix) == matrix,
        "baseline_problems": baseline, "rebuild_equals_file": built == items,
        "query_dates": dict(Counter(x["ngay_hoi"] for x in items)),
        "rq3_amending_sources": dict(Counter(x["van_ban_sua_doi"] for x in items if x["nhom_cau"] == "sua_doi")),
        "normal_items_with_fine_labels": sum(x.get("muc_phat_min") is not None for x in items if x["nhom_cau"] == "thuong"),
        "answerable_test_count": len(answerable_test), "test_dev_citation_overlap_candidates": overlap,
        "primary_test_citations_seen_in_dev": sum(x["can_cu"][0] in dev_vids for x in answerable_test),
        "repeated_grounding_candidates": [{"ids": ids, "can_cu": list(key)} for key, ids in signatures.items() if len(ids) > 1],
        "variant_count": len(variants),
        "variants_share_split_and_citations": all(x["tap"] == by_id[x["goc_id"]]["tap"] and
            x["can_cu"] == by_id[x["goc_id"]]["can_cu"] for x in variants),
        "more_than_five_distinct_clauses": too_many, "mutation_probes": mutation_results,
        "dev_selection_insertion_probe": displaced, "selected_evidence": snapshots,
        "interpretation": "Shared citations are review candidates, not proof of train/test leakage. Mutation probes modify in-memory copies only. Legal findings require the official sources cited in REPORT.md."
    }
    out = Path(__file__).with_name("audit.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["count", "groups", "splits", "matrix_matches", "baseline_problems", "rebuild_equals_file", "variants_share_split_and_citations"]}, ensure_ascii=False, indent=2))
    print(f"Citation overlap candidates: {len(overlap)}/{len(answerable_test)}")
    print(f"Incorrect mutations accepted: {sum(x['incorrect_mutation_accepted'] for x in mutation_results)}/{len(mutation_results)}")
    print(f"Evidence: {out}")


if __name__ == "__main__":
    main()
