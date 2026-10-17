"""Independent read-only re-review. Never overwrites previous evidence."""
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import evalset
from rag import chunking, score


def read(path):
    return [json.loads(s) for s in (ROOT / path).read_text(encoding="utf-8").splitlines()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def check(name, ok, details=None):
        checks.append({"name": name, "pass": bool(ok), "details": details})

    items = {x["key"]: x for x in read("data/eval/eval_v1.jsonl")}
    evidence = score.load_evidence()
    source = {r["version_id"]: r for r in evalset.load_versions()}
    all_chunks = {cut: read(f"data/rag/chunks_{cut}.jsonl") for cut in ("khoan", "dieu")}
    annex = "tt_155_2025_btc:pl1@2026-01-01"
    sizes = {}
    for cut, chunks in all_chunks.items():
        live = [c for c in chunks if chunking.in_force(c, "2026-10-01")]
        sizes[cut] = {"total": len(chunks), "live": len(live), "over": sum(c["vuot_gioi_han"] for c in chunks)}
        for key in ("lp06", "lp07", "lp08", "bt04"):
            item = items[key]
            lines = evidence[key][annex]
            check(f"{cut}:{key}:verbatim_evidence", all(s in source[annex]["text"].splitlines() for s in lines))
            pieces = [c for c in live if annex in c.get("phan_dong", {})]
            good = [c for c in pieces if all(s in c["text"] for s in lines)]
            wrong = [c for c in pieces if c not in good]
            support = []
            for vid in sorted(set(item["can_cu"]) - {annex}):
                if not any(vid in c["units"] for c in support):
                    support.append(next(c for c in live if vid in c["units"] and vid not in c.get("phan_dong", {})))
            negative = score.score_item(item, wrong + support)
            positive = score.score_item(item, good + support)
            check(f"{cut}:{key}:wrong_piece_rejected", bool(wrong) and not negative["all"], negative)
            check(f"{cut}:{key}:right_piece_accepted", bool(good) and positive["all"], positive)
            if key == "lp08":
                check(f"{cut}:{key}:wrong_MRR_zero", score.score_item(item, wrong)["rr"] == 0)
                check(f"{cut}:{key}:right_at_rank_2", score.score_item(item, wrong + good)["rr"] == 0.5)
                for i, line in enumerate(lines):
                    broken = [dict(c, text=c["text"].replace(line, "")) for c in good]
                    check(f"{cut}:{key}:missing_line_{i}_rejected", not score.score_item(item, broken)["all"])
                check(f"{cut}:unannotated_partial_rejected", not score.score_item(item, wrong, evidence={})["all"])
                check(f"{cut}:unannotated_complete_accepted", score.score_item(item, pieces, evidence={})["all"])
        missing = [(c["chunk_id"], n) for c in chunks for n in c["ghi_chu_hieu_luc"] if n not in c["text"]]
        check(f"{cut}:all_conditions_in_text", not missing, missing)
        spans = defaultdict(set)
        totals = defaultdict(set)
        bad_spans = []
        for c in chunks:
            for vid, (a, b, n) in c["phan_dong"].items():
                if not 0 <= a <= b < n:
                    bad_spans.append((c["chunk_id"], vid, a, b, n))
                spans[vid].update(range(a, b + 1))
                totals[vid].add(n)
        check(f"{cut}:valid_line_spans", not bad_spans, bad_spans)
        check(f"{cut}:all_partial_units_fully_covered", all(len(totals[v]) == 1 and spans[v] == set(range(next(iter(totals[v])))) for v in spans))
        if cut == "khoan":
            table = [c for c in chunks if c["nhom"] == "qcvn_41_2024:d46:k3"]
            check("QCVN46.3:all_table_pieces_keep_columns", len(table) > 1 and all("Màu chữ, số | Màu nền | Màu viền" in c["text"] for c in table))
            invalid = []
            for c in chunks:
                if c["so_token"] <= 512:
                    continue
                if c["phan_dong"]:
                    indivisible = sum(b - a + 1 for a, b, _ in c["phan_dong"].values()) == 1 and set(c["units"]) == set(c["phan_dong"])
                else:
                    indivisible = sum(source[v]["level"] == "diem" for v in c["units"]) == 1
                if not c["vuot_gioi_han"] or not indivisible:
                    invalid.append(c["chunk_id"])
            check("khoan:oversize_is_single_point_or_single_row", not invalid, invalid)

    manifest = json.loads((ROOT / "data/rag/MANIFEST.json").read_text(encoding="utf-8"))
    hash_entries = [manifest["nguon"], manifest["nguon"]["amendments_reviewed"], manifest["nguon"]["ten_van_ban"], manifest["tokenizer"], manifest["bang_chung"]]
    for entry in hash_entries:
        p = Path(entry["path"]).expanduser()
        if not p.is_absolute():
            p = ROOT / p
        check("manifest:" + entry["path"], sha(p) == entry["sha256"])
    for path, entry in manifest["files"].items():
        check("manifest:" + path, sha(ROOT / path) == entry["sha256"])
    ev = json.loads(score.EVIDENCE.read_text(encoding="utf-8"))
    check("frozen_eval_hash", sha(ROOT / "data/eval/eval_v1.jsonl") == ev["eval_sha256"] == "5a1b72038ae79755f5df7c53ed46447ac1516bb04e8e1330fd81cfc43fc0e252")

    # Exercise the actual --check branch against a temporary output directory.
    # Chunk construction is replaced with already independently rebuilt/saved rows;
    # product files are never edited, including during this negative test.
    spec = importlib.util.spec_from_file_location("review_build_chunks", ROOT / "scripts/build_chunks.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    tok_path = Path(manifest["tokenizer"]["path"]).expanduser()
    if not tok_path.is_absolute():
        tok_path = ROOT / tok_path
    with tempfile.TemporaryDirectory(prefix="g3-review-") as temp:
        out = Path(temp)
        for cut in all_chunks:
            (out / f"chunks_{cut}.jsonl").write_bytes((ROOT / f"data/rag/chunks_{cut}.jsonl").read_bytes())
        altered = dict(manifest, max_tokens=manifest["max_tokens"] + 1)
        (out / "MANIFEST.json").write_bytes(builder.dump_manifest(altered))
        capture = io.StringIO()
        with patch.object(builder, "OUT", out), patch.object(builder.chunking, "load_tokenizer", return_value=SimpleNamespace(path=tok_path)), patch.object(builder.chunking, "build_chunks", side_effect=lambda records, cut, count: all_chunks[cut]), patch.object(sys, "argv", ["build_chunks.py", "--check"]), contextlib.redirect_stdout(capture):
            try:
                builder.main()
                status = 0
            except SystemExit as ex:
                status = ex.code
        check("altered_manifest_rejected_by_check", status == 1 and "MANIFEST.json" in capture.getvalue(), {"exit": status, "output": capture.getvalue().strip()})

    files = ["src/rag/chunking.py", "src/rag/score.py", "scripts/build_chunks.py", "data/eval/bang_chung_v1.json", "data/eval/eval_v1.jsonl", "data/rag/MANIFEST.json"]
    result = {"utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "sizes": sizes,
              "hashes": {p: sha(ROOT / p) for p in files}}
    dest = Path(__file__).parent / ("checks-" + datetime.now(timezone.utc).strftime("%H%M%S%fZ") + ".json")
    with dest.open("x", encoding="utf-8", newline="\n") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(json.dumps({"evidence": str(dest), "passed": sum(c["pass"] for c in checks), "total": len(checks), "failures": [c for c in checks if not c["pass"]]}, ensure_ascii=False))
    return 0 if all(c["pass"] for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
