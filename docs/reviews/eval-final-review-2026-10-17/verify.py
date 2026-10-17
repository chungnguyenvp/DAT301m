"""Verify the fixes requested by the previous two reviews without changing eval inputs."""

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


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    xs, rs = evalset.load_eval(), evalset.load_versions()
    by = {x["key"]: x for x in xs}
    versions = evalset.by_version(rs)
    spec = importlib.util.spec_from_file_location("final_review_builder", ROOT / "scripts/build_eval.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    paths = [ROOT / p for p in ["data/eval/eval_v1.jsonl", "data/eval/split_v1.json", "data/eval/MANIFEST.json",
             "data/eval/README.md", "scripts/build_eval.py", "src/lawproc/evalset.py", "tests/test_evalset.py",
             "data/processed/legal_units_versioned.jsonl", "docs/reviews/eval-rereview-2026-10-17/REPORT.md",
             "docs/reviews/eval-rereview-2026-10-17/audit-031317389623Z.json"]]
    fingerprints = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    changes = [
        ("reversed_bounds", "xp01", {"muc_phat_min": 600000, "muc_phat_max": 400000}),
        ("one_dong", "xp01", {"dap_an": "Phạt 1 đồng."}),
        ("suspension", "xp04", {"dap_an": by["xp04"]["dap_an"].replace("22 tháng đến 24 tháng", "01 tháng đến 02 tháng")}),
        ("citation", "xp01", {"dap_an": by["xp01"]["dap_an"].replace("điểm h khoản 2 Điều 7", "điểm z khoản 99 Điều 999")}),
        ("99_days", "sd24", {"dap_an": by["sd24"]["dap_an"].replace("02 ngày", "99 ngày")}),
        ("unrelated_deduction", "xp01", {"diem_tru": 4,
            "can_cu": by["xp01"]["can_cu"] + ["nd_168_2024:d7:k13:b@2025-01-01"],
            "dap_an": by["xp01"]["dap_an"] + " Trừ 04 điểm giấy phép lái xe."}),
        ("ratio", "gp13", {"dap_an": by["gp13"]["dap_an"].replace("27/30", "26/30")}),
        ("working_days", "sd24", {"dap_an": by["sd24"]["dap_an"].replace("02 ngày làm việc", "02 ngày")}),
        ("fine_range", "xp01", {"dap_an": by["xp01"]["dap_an"].replace("400.000 đồng đến 600.000 đồng", "600.000 đồng đến 600.000 đồng")}),
    ]
    probes = []
    for name, key, change in changes:
        changed = copy.deepcopy(by[key])
        changed.update(change)
        assert changed != by[key], f"No-op mutation: {name}"
        problems = evalset.check_items([changed], rs)
        probes.append({"name": name, "key": key, "id": by[key]["id"], "changes": change,
                       "mutation_is_real": True, "rejected": bool(problems), "problems": problems})
        assert problems, name
    retrieval = []
    for key in ["gp01", "ll05"]:
        x = by[key]
        retrieved = {x["nhom_can_cu"][0][0]}
        hits = [bool(retrieved.intersection(g)) for g in x["nhom_can_cu"]]
        retrieval.append({"key": key, "groups": len(hits), "single_piece_hits": sum(hits), "all": all(hits)})
        assert sum(hits) == 1 and not all(hits)
    manifest = json.loads((ROOT / "data/eval/MANIFEST.json").read_text(encoding="utf-8"))
    hashes = []
    for k in ["eval", "split", "source"]:
        d = manifest[k]
        hashes.append({"path": d["path"], "matches": digest(ROOT / d["path"]) == d["sha256"]})
    hashes += [{"path": p, "matches": digest(ROOT / p) == h} for p, h in manifest["drafts"].items()]
    assert all(x["matches"] for x in hashes)
    ordinary = [x for x in xs if x["nhom_cau"] in {"thuong", "sua_doi"}]
    rq3 = [x for x in xs if x["nhom_cau"] == "sua_doi"]
    replaced = ["sd09", "sd11", "sd23", "sd39", "sd42", "sd49", "sd50"]
    assert not any(k in by for k in replaced)
    assert all(f"sd{i}" in by for i in range(53, 60))
    snapshots = []
    for key in ["sd47"] + [f"sd{i}" for i in range(53, 60)]:
        x = by[key]
        snapshots.append({"line": xs.index(x) + 1, "item": x,
                          "records": [versions[v] for v in dict.fromkeys(x["can_cu"] + x["can_cu_cu"])]})
    result = {
        "review_date": "2026-10-17", "input_sha256": fingerprints,
        "count": len(xs), "groups": dict(Counter(x["nhom_cau"] for x in xs)),
        "splits": dict(Counter(x["tap"] for x in xs)), "baseline_problems": evalset.check_items(xs, rs),
        "rebuild_equals_file": builder.build(rs) == xs, "mutation_probes": probes,
        "retrieval_rule_probes": retrieval, "manifest_hash_checks": hashes,
        "rq3_sources": dict(Counter(x["van_ban_sua_doi"] for x in rq3)),
        "evidence_group_distribution": dict(Counter(len(x["nhom_can_cu"]) for x in ordinary)),
        "event_family_count": len({x["ho_su_kien"] for x in ordinary}),
        "shared_event_gp17_sd34": by["gp17"]["ho_su_kien"] == by["sd34"]["ho_su_kien"],
        "passing_threshold_labels": {k: by[k]["so_lieu"] for k in ["gp06", "gp13"]},
        "rq3_replacement_evidence": snapshots,
        "interpretation": "Previous requested fixes verified. Retrieval probes apply the documented rule; no production retrieval scorer is evaluated here. No full independent legal certification of all gold answers is implied."
    }
    assert not result["baseline_problems"] and result["rebuild_equals_file"] and result["shared_event_gp17_sd34"]
    out = Path(__file__).with_name("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with out.open("x", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    for p in paths:
        assert digest(p) == fingerprints[str(p.relative_to(ROOT))]
    print(json.dumps({"evidence": str(out), "previous_error_probes_rejected": len(probes),
                      "manifest_hashes_matched": len(hashes), "rebuild_equals_file": result["rebuild_equals_file"],
                      "input_files_unchanged": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
