"""Audit the revised eval by stable keys. Never overwrite an earlier evidence file."""

import copy
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import evalset  # noqa: E402


def main():
    xs = evalset.load_eval()
    rs = evalset.load_versions()
    by_key = {x["key"]: x for x in xs}
    versions = evalset.by_version(rs)
    spec = importlib.util.spec_from_file_location("rereview_builder", ROOT / "scripts/build_eval.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    probes = []

    def probe(name, key, changes, expected_rejected):
        original = by_key[key]
        changed = copy.deepcopy(original)
        changed.update(changes)
        assert changed != original, f"No-op mutation: {name}/{key}"
        problems = evalset.check_items([changed], rs)
        probes.append({"name": name, "key": key, "id": original["id"],
                       "changed_fields": changes, "mutation_is_real": True,
                       "problems": problems, "rejected": bool(problems),
                       "expected_rejected": expected_rejected,
                       "facts_unchanged": evalset.facts(original["dap_an"]) == evalset.facts(changed["dap_an"])})

    original_six = [
        ("original_reversed_bounds", "xp01", {"muc_phat_min": 600000, "muc_phat_max": 400000}),
        ("original_one_dong", "xp01", {"dap_an": "Phạt 1 đồng."}),
        ("original_wrong_suspension", "xp04", {"dap_an": by_key["xp04"]["dap_an"].replace("22 tháng đến 24 tháng", "01 tháng đến 02 tháng")}),
        ("original_nonexistent_citation", "xp01", {"dap_an": by_key["xp01"]["dap_an"].replace("điểm h khoản 2 Điều 7", "điểm z khoản 99 Điều 999")}),
        ("original_99_days", "sd24", {"dap_an": by_key["sd24"]["dap_an"].replace("02 ngày", "99 ngày")}),
        ("original_unrelated_deduction", "xp01", {"diem_tru": 4,
            "can_cu": by_key["xp01"]["can_cu"] + ["nd_168_2024:d7:k13:b@2025-01-01"],
            "dap_an": by_key["xp01"]["dap_an"] + " Trừ 04 điểm giấy phép lái xe."}),
    ]
    for name, key, changes in original_six:
        probe(name, key, changes, True)
    extra = [
        ("passing_threshold_27_to_26", "gp13", {"dap_an": by_key["gp13"]["dap_an"].replace("27/30", "26/30")}),
        ("working_days_to_calendar_days", "sd24", {"dap_an": by_key["sd24"]["dap_an"].replace("02 ngày làm việc", "02 ngày")}),
        ("wrong_fine_with_existing_value", "xp01", {"dap_an": by_key["xp01"]["dap_an"].replace("400.000 đồng đến 600.000 đồng", "600.000 đồng đến 600.000 đồng")}),
        ("control_hours_to_days_rejected", "gp17", {"dap_an": by_key["gp17"]["dap_an"].replace("02 giờ", "02 ngày")}),
    ]
    for name, key, changes in extra:
        probe(name, key, changes, True)

    retrieval_probes = []
    for key in ["gp01", "ll05"]:
        x = by_key[key]
        retrieved = {x["nhom_can_cu"][0][0]}
        hits = [bool(retrieved.intersection(group)) for group in x["nhom_can_cu"]]
        retrieval_probes.append({"key": key, "id": x["id"], "question": x["cau_hoi"],
            "retrieved": list(retrieved), "retrieved_text": [versions[v]["text"] for v in retrieved],
            "nhom_can_cu": x["nhom_can_cu"], "group_hits": hits,
            "all_groups_hit_under_readme_rule": all(hits),
            "interpretation": "Applies the README rule to simulated retrieval; no production scorer exists in this repo yet."})

    snapshots = []
    keys = ["gp01", "gp06", "gp13", "gp17", "sd34", "sd47", "sd49", "bt04", "bh10", "ll07"]
    keys += [f"sd{i}" for i in range(41, 53)]
    for key in dict.fromkeys(keys):
        x = by_key[key]
        vids = x["can_cu"] + x.get("can_cu_cu", [])
        snapshots.append({"line": xs.index(x) + 1, "item": x,
                          "records": [versions[v] for v in dict.fromkeys(vids)]})

    paths = [ROOT / "src/lawproc/evalset.py", ROOT / "scripts/build_eval.py", ROOT / "tests/test_evalset.py",
             ROOT / "data/eval/eval_v1.jsonl", ROOT / "data/eval/split_v1.json", ROOT / "data/eval/README.md",
             ROOT / "data/processed/legal_units_versioned.jsonl",
             ROOT / "docs/reviews/eval-audit-2026-10-17/audit.json",
             ROOT / "docs/reviews/eval-audit-2026-10-17/REPORT.md"]
    fingerprints = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result = {
        "review_date": "2026-10-17", "input_sha256": fingerprints,
        "count": len(xs), "groups": dict(Counter(x["nhom_cau"] for x in xs)),
        "splits": dict(Counter(x["tap"] for x in xs)),
        "baseline_problems": evalset.check_items(xs, rs), "rebuild_equals_file": builder.build(rs) == xs,
        "removed_problematic_keys_still_present": [k for k in ["sd01", "sd02", "sd03", "sd04", "sd05", "sd06", "sd14", "sd15", "sd17", "sd19", "sd20", "sd40"] if k in by_key],
        "new_rq3_keys_present": [f"sd{i}" for i in range(41, 53) if f"sd{i}" in by_key],
        "original_six_rejected": all(x["rejected"] for x in probes[:6]),
        "mutation_probes": probes, "retrieval_probes": retrieval_probes,
        "normal_or_rq3_with_multiple_citations_in_one_group": sum(any(len(g)>1 for g in x.get("nhom_can_cu", [])) for x in xs if x["nhom_cau"] in {"thuong", "sua_doi"}),
        "duplicate_fact_families_example": {k: {"id": by_key[k]["id"], "family": by_key[k]["ho_cau"]} for k in ["gp17", "sd34"]},
        "selected_evidence": snapshots,
    }
    assert result["original_six_rejected"]
    assert not result["baseline_problems"] and result["rebuild_equals_file"]
    stamp = datetime.now(timezone.utc).strftime("%H%M%S%fZ")
    out = Path(__file__).with_name(f"audit-{stamp}.json")
    with out.open("x", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    for p in paths:
        assert hashlib.sha256(p.read_bytes()).hexdigest() == fingerprints[str(p.relative_to(ROOT))]
    print(json.dumps({"evidence": str(out), "count": len(xs), "rebuild_equals_file": result["rebuild_equals_file"],
                      "original_six_rejected": result["original_six_rejected"],
                      "extra_rejected": {x["name"]: x["rejected"] for x in probes[6:]}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
