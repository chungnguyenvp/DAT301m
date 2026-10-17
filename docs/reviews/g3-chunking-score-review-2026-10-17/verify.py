"""Read-only G3 audit; each run writes a new evidence file beside this script."""

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from rag.chunking import in_force  # noqa: E402
from rag.score import score_item  # noqa: E402


def read_rows(path):
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines()]


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    cutoff = "2026-10-01"
    items = read_rows("data/eval/eval_v1.jsonl")
    chunks = {cut: read_rows(f"data/rag/chunks_{cut}.jsonl") for cut in ("khoan", "dieu")}
    by_key = {x["key"]: x for x in items}
    probe_cases = []
    annex = "tt_155_2025_btc:pl1@2026-01-01"
    for cut, rows in chunks.items():
        by_id = {c["chunk_id"]: c for c in rows}
        for key, wrong_piece, amounts in (
            ("lp06", 2, ["14.000.000"]),
            ("lp07", 2, ["1.400.000"]),
            ("lp08", 1, ["70.000", "35.000", "50.000"]),
            ("bt04", 2, ["14.000.000"]),
        ):
            item = by_key[key]
            wrong = by_id[f"{cut}:tt_155_2025_btc:pl1@2026-01-01#{wrong_piece}"]
            ranked = [wrong]
            needed = set(item["can_cu"]) - {annex}
            for vid in sorted(needed):
                if not any(vid in c["units"] for c in ranked):
                    ranked.append(next(c for c in rows if vid in c["units"] and in_force(c, cutoff)))
            score = score_item(item, ranked)
            text = "\n".join(c["text"] for c in ranked)
            absent = [a for a in amounts if not re.search(r"(?<![\d.])" + re.escape(a) + r"(?![\d.])", text)]
            assert len(ranked) <= 5 and score["all"] and absent == amounts
            probe_cases.append({
                "cut": cut, "key": key, "id": item["id"], "split": item["tap"],
                "query": item["cau_hoi"], "wrong_piece": wrong["chunk_id"],
                "missing_answer_amounts": absent, "score": score,
            })
        correct = by_id[f"{cut}:tt_155_2025_btc:pl1@2026-01-01#2"]
        assert score_item(by_key["lp08"], [correct])["all"]

    notes = {}
    for cut, rows in chunks.items():
        bad = [{"chunk_id": c["chunk_id"], "group": c["nhom"],
                "live_at_cutoff": in_force(c, cutoff),
                "missing_from_text": [n for n in c["ghi_chu_hieu_luc"] if n not in c["text"]]}
               for c in rows if any(n not in c["text"] for n in c["ghi_chu_hieu_luc"])]
        live = [c for c in bad if c["live_at_cutoff"]]
        notes[cut] = {"all_count": len(bad), "live_count": len(live),
                      "live_by_group": dict(Counter(c["group"] for c in live)), "cases": bad}

    by_id = {c["chunk_id"]: c for c in chunks["khoan"]}
    table_header = "TT | Mô tả biển chỉ dẫn | Kiểu chữ | Màu chữ, số | Màu nền | Màu viền"
    first = by_id["khoan:qcvn_41_2024:d46:k3@2025-01-01#1"]
    later = [by_id[f"khoan:qcvn_41_2024:d46:k3@2025-01-01#{i}"] for i in (2, 3, 4)]
    assert table_header in first["text"] and all(table_header not in c["text"] for c in later)

    manifest = json.loads((ROOT / "data/rag/MANIFEST.json").read_text(encoding="utf-8"))
    paths = ["src/rag/chunking.py", "src/rag/score.py", "scripts/build_chunks.py",
             "tests/test_rag_chunking.py", "tests/test_rag_score.py", "data/rag/MANIFEST.json",
             "data/rag/chunks_khoan.jsonl", "data/rag/chunks_dieu.jsonl",
             "data/eval/eval_v1.jsonl", "data/processed/legal_units_versioned.jsonl"]
    hashes = {p: digest(p) for p in paths}
    for cut in chunks:
        p = f"data/rag/chunks_{cut}.jsonl"
        assert hashes[p] == manifest["files"][p]["sha256"]
    source_blob = subprocess.check_output(
        ["git", "hash-object", "data/processed/legal_units_versioned.jsonl"], cwd=ROOT, text=True).strip()
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "cutoff": cutoff,
        "hashes": hashes, "actual_source_git_blob": source_blob,
        "manifest_source_git_blob": manifest["nguon"]["git_blob_in_tag_data_v1"],
        "full_credit_with_wrong_annex_fragment": probe_cases,
        "conditions_missing_from_chunk_text": notes,
        "table_context_loss": {"header_only_in_piece_1": table_header,
                               "later_pieces": [{"chunk_id": c["chunk_id"], "text": c["text"]} for c in later]},
    }
    target = Path(__file__).parent / ("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with target.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(target), "wrong_fragment_cases": len(probe_cases),
                      "missing_conditions": {k: {n: v[n] for n in ("all_count", "live_count")}
                                             for k, v in notes.items()},
                      "table_fragments_without_column_header": len(later)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
