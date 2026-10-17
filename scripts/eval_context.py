"""Xem đơn vị luật có hiệu lực tại một ngày để soạn và duyệt câu eval.

    py -3.13 scripts/eval_context.py toc nd_168_2024            # danh sách Điều
    py -3.13 scripts/eval_context.py tree nd_168_2024:d7        # cả Điều, kèm version_id
    py -3.13 scripts/eval_context.py tree nd_168_2024:d7:k2 --day 2026-06-30
    py -3.13 scripts/eval_context.py grep "nón bảo hiểm|mũ bảo hiểm" --doc nd_168_2024
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402


def order_key(rec: dict) -> tuple:
    return (rec["line_start"], rec["valid_from"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["toc", "tree", "grep"])
    ap.add_argument("arg")
    ap.add_argument("--day", default=config.CUTOFF)
    ap.add_argument("--doc")
    ap.add_argument("--all-versions", action="store_true", help="tree: in cả phiên bản không còn hiệu lực")
    a = ap.parse_args()
    recs = evalset.load_versions()
    live = evalset.live_versions(recs, a.day)
    if a.cmd == "toc":
        rows = sorted((r for vs in live.values() for r in vs if r["doc_id"] == a.arg and r["level"] == "dieu"),
                      key=order_key)
        for r in rows:
            n = sum(1 for u in live if u.startswith(r["unit_id"] + ":"))
            scope = "" if r["trong_pham_vi"] else "  [ngoài phạm vi]"
            print(f"{r['unit_id']:<28} {n:>4}  {r['title']}{scope}")
        for r in sorted((r for vs in live.values() for r in vs if r["doc_id"] == a.arg and r["level"] == "phu_luc"),
                        key=order_key):
            print(f"{r['unit_id']:<28}  PL  {r['title'][:90]}  ({r.get('loai_phu_luc')}, {len(r['text'])} ký tự)")
    elif a.cmd == "tree":
        pool = recs if a.all_versions else [r for vs in live.values() for r in vs]
        rows = sorted((r for r in pool if r["unit_id"] == a.arg or r["unit_id"].startswith(a.arg + ":")),
                      key=order_key)
        for r in rows:
            mark = "" if r in live.get(r["unit_id"], []) else "  [KHÔNG HIỆU LỰC]"
            cond = f"  [điều kiện: {r['hl_ngoai_le']}]" if r["hl_ngoai_le"] else ""
            print(f"## {r['version_id']}  ({r['valid_from']} → {r['valid_to']}){mark}{cond}")
            if r["title"]:
                print(f"   [tiêu đề] {r['title']}")
            print("   " + r["text"].replace("\n", "\n   "))
    else:
        pat = re.compile(a.arg, re.IGNORECASE)
        for vs in live.values():
            for r in vs:
                if (a.doc is None or r["doc_id"] == a.doc) and r["trong_pham_vi"] and pat.search(r["text"]):
                    print(f"{r['version_id']}: {r['text'][:220].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()
