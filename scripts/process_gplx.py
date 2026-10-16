"""Tách bộ 600 câu hỏi sát hạch lái xe: python scripts/process_gplx.py

Đọc data/raw/gplx/gplx_600_2025__p1.pdf và Công văn 2262/CSGT-P5, ghi data/processed/gplx_600.jsonl
(mọi câu, kèm nhãn) và in bảng kiểm tra. Bộ eval trắc nghiệm phụ dùng các câu co_hinh = false.
"""
import collections
import csv
import json
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from lawproc.corrections import apply_corrections  # noqa: E402
from lawproc.gplx import CHAPTERS, chapter_of, parse_cv_lists, parse_questions  # noqa: E402

QUESTIONS_PDF = config.RAW / "gplx" / "gplx_600_2025__p1.pdf"
CV_PDF = config.RAW / "gplx" / "cv_2262_2025_csgt__p1.pdf"
OUT = config.PROCESSED / "gplx_600.jsonl"
CORRECTIONS = config.DATA / "ocr_corrections.csv"
FLAGS = config.DATA / "gplx_flags.csv"  # câu có đáp án không còn khớp luật tại config.CUTOFF, đã rà soát
SEP = "\x00"  # ngăn cách các trường khi áp sửa lỗi trên toàn bộ câu hỏi


def correct(questions: list[dict]) -> None:
    """Áp các dòng doc_id = gplx_600_2025 của ocr_corrections.csv; mỗi chuỗi sai phải có đúng một lần trong cả bộ."""
    with CORRECTIONS.open(newline="", encoding="utf-8-sig") as fp:
        rows = [r for r in csv.DictReader(fp) if r["doc_id"] == "gplx_600_2025"]
    if not rows:
        return
    fields = [(q, None) for q in questions] + [(q, i) for q in questions for i in range(len(q["lua_chon"]))]
    text = SEP.join(q["cau_hoi"] if i is None else q["lua_chon"][i] for q, i in fields)
    for (q, i), value in zip(fields, apply_corrections(text, rows).split(SEP), strict=True):
        if i is None:
            q["cau_hoi"] = value
        else:
            q["lua_chon"][i] = value
    print(f"sửa lỗi chữ: {len(rows)} dòng")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    questions = parse_questions(QUESTIONS_PDF)
    correct(questions)
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
    with FLAGS.open(newline="", encoding="utf-8-sig") as fp:
        flags = {int(r["so_cau"]): r["ly_do"] for r in csv.DictReader(fp)}
    for q in questions:
        q["can_xem_phap_ly"] = flags.get(q["so_cau"])
    keys = ["so_cau", "chuong", "cau_hoi", "lua_chon", "dap_an", "co_hinh", "diem_liet", "hang_A1_A", "hang_B1",
            "can_xem_phap_ly"]
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
    print(f"gắn cờ pháp lý: {sorted(n for n in flags)}")
    print("số lựa chọn:", dict(collections.Counter(len(q["lua_chon"]) for q in questions)))
    print("vấn đề:", problems or "không")


if __name__ == "__main__":
    main()
