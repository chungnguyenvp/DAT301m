"""Ghép nháp `data/train/drafts/*.jsonl`, kiểm tự động, lọc gần trùng eval, chia train/dev, ghi `data/train/`.

    py -3.13 scripts/build_trainset.py --check     # chỉ kiểm và báo cáo
    py -3.13 scripts/build_trainset.py             # kiểm rồi ghi train.jsonl, dev.jsonl, MANIFEST.json

- Mẫu lỗi làm dừng build (sửa nháp rồi chạy lại).
- Mẫu có câu hỏi gần trùng câu eval (`eval_v1` và 281 câu đề GPLX) bị loại và liệt kê trong manifest: cosine TF-IDF ký tự 4-gram ≥ NEAR, hoặc
  ≥ NEAR_SAME khi cùng căn cứ chính với câu eval.
- Chia theo Điều của `can_cu[0]` (`trainset.split_of`); mẫu từ chối chia theo `key`.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset, trainset  # noqa: E402

TRAIN = config.DATA / "train"
DRAFTS = TRAIN / "drafts"
NEAR = 0.85        # gần trùng bất kỳ câu eval nào
NEAR_SAME = 0.6    # gần trùng câu eval có cùng căn cứ chính (cùng câu hỏi, diễn đạt khác)


def load_drafts() -> list[dict]:
    out = []
    for path in sorted(DRAFTS.glob("*.jsonl")):
        for n, line in enumerate(path.open(encoding="utf-8"), 1):
            if line.strip():
                s = json.loads(line)
                s["nguon_nhap"] = f"{path.name}:{n}"
                out.append(s)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    records = evalset.load_versions()
    samples = load_drafts()
    problems = trainset.check_samples(samples, records)
    for p in problems:
        print("LỖI:", p)
    held_out = evalset.load_eval() + trainset.gplx_items()  # eval_v1 và 281 câu đề GPLX
    near = trainset.near_eval(samples, held_out, NEAR, NEAR_SAME)
    for s, eid, sim in near:
        print(f"GẦN EVAL: {s['key']} ~ {eid} ({sim:.2f}): {s['cau_hoi'][:80]}")
    dropped = {s["key"] for s, _, _ in near}
    kept = [s for s in samples if s["key"] not in dropped]
    for s in kept:
        s["tap"] = trainset.split_of(s["can_cu"][0] if s["can_cu"] else f"tu_choi:{s['key']}")
    print(f"{len(samples)} mẫu; lỗi {len(problems)}; loại vì gần eval {len(dropped)}; giữ {len(kept)}")
    print("theo loại:", dict(Counter(s["loai"] for s in kept)))
    print("theo chủ đề:", dict(Counter(s["chu_de"] for s in kept)))
    print("theo tập:", dict(Counter(s["tap"] for s in kept)))
    if problems:
        sys.exit(1)
    if a.check:
        return
    files = {}
    for tap in ("train", "dev"):
        path = TRAIN / f"{tap}.jsonl"
        rows = [{k: v for k, v in s.items() if k != "tap"} for s in kept if s["tap"] == tap]
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
        files[f"data/train/{tap}.jsonl"] = {"so_mau": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest = {
        "files": files,
        "drafts": {f"data/train/drafts/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(DRAFTS.glob("*.jsonl"))},
        "nguong_gan_eval": NEAR, "nguong_gan_eval_cung_can_cu": NEAR_SAME, "loai_vi_gan_eval": [{"key": s["key"], "eval": eid, "cosine": sim} for s, eid, sim in near],
        "eval_sha256": hashlib.sha256((config.DATA / "eval" / "eval_v1.jsonl").read_bytes()).hexdigest(),
        "gplx_sha256": hashlib.sha256((config.PROCESSED / "gplx_600.jsonl").read_bytes()).hexdigest(),
        "ty_le_dev": trainset.DEV_RATIO, "cutoff": config.CUTOFF,
    }
    (TRAIN / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                         newline="\n")
    print("-> data/train/train.jsonl, dev.jsonl, MANIFEST.json")


if __name__ == "__main__":
    main()
