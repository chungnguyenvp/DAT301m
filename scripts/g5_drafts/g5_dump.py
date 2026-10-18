"""In các đơn vị đang có hiệu lực tại CUTOFF của một văn bản.
    py -3.13 scripts/g5_drafts/g5_dump.py <doc_id> [d1 d2 ...] [--titles] [--max N]
--titles: chỉ in tên Điều (câu dẫn) và số đơn vị mỗi Điều."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from lawproc import config, evalset, trainset, validity  # noqa: E402

args = sys.argv[1:]
doc = args[0]
titles = "--titles" in args
mx = int(args[args.index("--max") + 1]) if "--max" in args else 700
arts = {a for a in args[1:] if a.startswith("d") and a[1:2].isdigit()}
recs = [r for r in evalset.load_versions() if r["unit_id"].split(":")[0] == doc
        and validity.in_force_at(r, config.CUTOFF)[0]]


def art_key(uid):
    p = uid.split(":")
    if len(p) < 2:
        return (0, "")
    a = p[1]
    num = "".join(ch for ch in a[1:] if ch.isdigit())
    return (int(num) if num else 0, a)


recs.sort(key=lambda r: (art_key(r["unit_id"]), r["unit_id"]))
if titles:
    cnt = collections.Counter(r["unit_id"].split(":")[1] for r in recs if ":" in r["unit_id"])
    for a, c in sorted(cnt.items(), key=lambda x: art_key(f"x:{x[0]}")):
        print(a, c, trainset.split_of(f"{doc}:{a}:k1"))
else:
    for r in recs:
        p = r["unit_id"].split(":")
        if arts and (len(p) < 2 or p[1] not in arts):
            continue
        print(r["version_id"].split(":", 1)[1], "|", r["text"].replace("\n", " ")[:mx])
