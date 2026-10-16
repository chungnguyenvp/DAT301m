"""Tách bộ 600 câu hỏi sát hạch lái xe: python scripts/process_gplx.py

Đọc data/raw/gplx/gplx_600_2025__p1.pdf và Công văn 2262/CSGT-P5, ghi data/processed/gplx_600.jsonl
(mọi câu, kèm nhãn) và in bảng kiểm tra. Bộ eval trắc nghiệm phụ dùng các câu co_hinh = false.
"""
import collections
import json
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from lawproc.gplx import CHAPTERS, chapter_of, parse_cv_lists, parse_questions  # noqa: E402

QUESTIONS_PDF = config.RAW / "gplx" / "gplx_600_2025__p1.pdf"
CV_PDF = config.RAW / "gplx" / "cv_2262_2025_csgt__p1.pdf"
OUT = config.PROCESSED / "gplx_600.jsonl"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    questions = parse_questions(QUESTIONS_PDF)
    with pymupdf.open(str(CV_PDF)) as cv:
        lists = parse_cv_lists([ln for page in cv for ln in page.get_text().splitlines()])
    problems = []
    numbers = [q["so_cau"] for q in questions]
    if numbers != list(range(1, 601)):
        problems.append(f"số câu không liên tục 1–600: có {len(numbers)} câu")
    for name, size in (("hang_A1_A", 250), ("hang_B1", 300), ("diem_liet", 60)):
        if len(lists[name]) != size:
            problems.append(f"{name}: {len(lists[name])} câu, công văn ghi {size}")
    for q in questions:
        q["chuong"] = chapter_of(q["so_cau"])
        for name, nums in lists.items():
            q[name] = q["so_cau"] in nums
        if q["dap_an"] is None:
            problems.append(f"câu {q['so_cau']}: không xác định được đúng một đáp án gạch chân")
        if not 2 <= len(q["lua_chon"]) <= 4:
            problems.append(f"câu {q['so_cau']}: {len(q['lua_chon'])} lựa chọn")
    keys = ["so_cau", "chuong", "cau_hoi", "lua_chon", "dap_an", "co_hinh", "diem_liet", "hang_A1_A", "hang_B1"]
    with OUT.open("w", encoding="utf-8") as fp:
        for q in questions:
            fp.write(json.dumps({k: q[k] for k in keys}, ensure_ascii=False) + "\n")
    print(f"-> {OUT.relative_to(config.ROOT)} ({len(questions)} câu)")
    by = collections.Counter((q["chuong"], q["co_hinh"]) for q in questions)
    print("chương | số câu | có hình | thuần chữ")
    for name, lo, hi in CHAPTERS:
        print(f"{name:6} | {hi - lo + 1:6} | {by[(name, True)]:7} | {by[(name, False)]:9}")
    text_only = [q for q in questions if not q["co_hinh"]]
    print(f"thuần chữ: {len(text_only)} câu, trong đó điểm liệt {sum(q['diem_liet'] for q in text_only)}")
    print("số lựa chọn:", dict(collections.Counter(len(q["lua_chon"]) for q in questions)))
    print("vấn đề:", problems or "không")


if __name__ == "__main__":
    main()
