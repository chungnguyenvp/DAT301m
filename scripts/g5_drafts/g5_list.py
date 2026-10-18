"""Xem các mẫu nháp đã có, để soạn mẫu mới không hỏi lại câu cũ.
    py -3.13 scripts/g5_drafts/g5_list.py --keys                 # số key lớn nhất theo tiền tố, đếm theo chủ đề và loại
    py -3.13 scripts/g5_drafts/g5_list.py --prefix bb            # các mẫu có key bắt đầu bằng "bb-"
    py -3.13 scripts/g5_drafts/g5_list.py --chu-de "Tai nạn"     # các mẫu thuộc một chủ đề
    py -3.13 scripts/g5_drafts/g5_list.py --doc qcvn_41_2024     # các Điều đang có hiệu lực của văn bản và số mẫu đã dẫn"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from lawproc import config, validity  # noqa: E402

DRAFTS = ROOT / "data" / "train" / "drafts"


def samples():
    for f in sorted(DRAFTS.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield f.name, json.loads(line)


def short(vid):
    return vid.split("@")[0]


def show(rows):
    for name, s in rows:
        print(f"{s['key']} [{s['loai']}] {s['cau_hoi']}  | {' '.join(short(v) for v in s['can_cu'])}  ({name})")


ap = argparse.ArgumentParser()
ap.add_argument("--keys", action="store_true")
ap.add_argument("--prefix")
ap.add_argument("--chu-de")
ap.add_argument("--doc")
args = ap.parse_args()

if args.keys:
    top = collections.Counter()
    topic = collections.Counter()
    kind = collections.Counter()
    for _, s in samples():
        p, n = s["key"].rsplit("-", 1)
        top[p] = max(top[p], int(n))
        topic[s["chu_de"]] += 1
        kind[s["loai"]] += 1
    print("key lớn nhất:", dict(sorted(top.items())))
    print("theo chủ đề (bản nháp, chưa lọc):", dict(topic.most_common()))
    print("theo loại (bản nháp, chưa lọc):", dict(kind.most_common()))
if args.prefix:
    show([(n, s) for n, s in samples() if s["key"].startswith(args.prefix + "-")])
if args.chu_de:
    show([(n, s) for n, s in samples() if s["chu_de"] == args.chu_de])
if args.doc:
    used = collections.Counter()
    for _, s in samples():
        for v in s["can_cu"]:
            doc, unit = short(v).split(":", 1)
            if doc == args.doc:
                used[unit.split(":")[0]] += 1
    titles, units = {}, collections.Counter()
    for line in (ROOT / "data/processed/legal_units_versioned.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        if r["doc_id"] != args.doc or not validity.in_force_at(r, config.CUTOFF)[0]:
            continue
        art = r["unit_id"].split(":")[1]
        units[art] += 1
        if r["level"] == "dieu":
            titles[art] = r.get("title") or ""
    for art in sorted(units, key=lambda a: (a[:2] == "pl", int("".join(c for c in a if c.isdigit()) or 0), a)):
        print(f"{art:6s} đơn vị={units[art]:3d} đã dẫn={used[art]:3d}  {titles.get(art, '')[:70]}")
