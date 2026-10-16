"""Chọn ngẫu nhiên 40 đơn vị của 5 văn bản chưa có đối chứng chữ độc lập và tìm trang PDF để kiểm tra tay.

Chạy từ gốc repo: py -3.13 -X utf8 docs/reviews/manual-check-2026-10-17/make_checklist.py
Ghi checklist.csv (mở bằng Excel) cạnh tệp này. Hạt giống cố định nên chạy lại ra cùng danh sách.
"""
import csv
import difflib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lawproc import config  # noqa: E402
from lawproc.validity import in_force_at  # noqa: E402

OUT = Path(__file__).with_name("checklist.csv")
SEED = 20261017
# Số đơn vị mỗi văn bản; BLDS chỉ lấy trong phạm vi giao thông đã chốt (Điều 584–608)
QUOTA = {"tt_108_2026_bca": 12, "tt_30_2026_bxd": 10, "blds_2015": 8, "tt_155_2025_btc": 5, "tt_36_2024_byt": 5}
# Nguồn để tìm trang: lớp chữ PDF, hoặc bộ đệm OCR với PDF ảnh (chỉ dùng để định vị trang, không dùng làm dữ liệu)
PAGE_SOURCES = {
    "tt_108_2026_bca": ("data/raw/legal/tt_108_2026_bca__p1.pdf", "data/interim/ocr/tt_108_2026_bca__p1/dpi300"),
    "tt_155_2025_btc": ("data/raw/legal/tt_155_2025_btc__p1.pdf", "data/interim/ocr/tt_155_2025_btc__p1/dpi300"),
    "tt_36_2024_byt": ("data/raw/legal/tt_36_2024_byt__p1.pdf", None),
    "tt_30_2026_bxd": ("data/raw/legal/tt_30_2026_bxd__p1.pdf", None),
    "blds_2015": (["data/raw/legal/blds_2015__p1.pdf", "data/raw/legal/blds_2015__p2.pdf"], None),
}
# Trang của hai bảng đã dựng lại theo ảnh PDF (đã xem trực tiếp khi dựng bảng)
ANNEX_PAGES = {"tt_155_2025_btc:pl1": "6", "tt_36_2024_byt:pl1": "6–8"}
NAMES = {"tt_108_2026_bca": "TT 108/2026/TT-BCA", "tt_30_2026_bxd": "TT 30/2026/TT-BXD", "blds_2015": "Bộ luật Dân sự 2015",
         "tt_155_2025_btc": "TT 155/2025/TT-BTC", "tt_36_2024_byt": "TT 36/2024/TT-BYT"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w%/.,]", " ", s)).strip()


def pages(doc: str) -> list[tuple[str, int, str]]:
    pdfs, ocr = PAGE_SOURCES[doc]
    out = []
    for pdf in ([pdfs] if isinstance(pdfs, str) else pdfs):
        with pymupdf.open(str(ROOT / pdf)) as d:
            for i, page in enumerate(d):
                text = page.get_text()
                if ocr:
                    text = (ROOT / ocr / f"p{i:04d}.txt").read_text(encoding="utf-8")
                out.append((pdf, i + 1, norm(text)))
    return out


def locate(text: str, doc_pages) -> tuple[str, int, str]:
    probe = norm(text)[:120]
    best = max(doc_pages, key=lambda p: difflib.SequenceMatcher(None, probe, p[2], autojunk=False)
               .find_longest_match(0, len(probe), 0, len(p[2])).size)
    size = difflib.SequenceMatcher(None, probe, best[2], autojunk=False).find_longest_match(
        0, len(probe), 0, len(best[2])).size
    return best[0], best[1], "cao" if size >= 40 else ("vừa" if size >= 20 else "thấp")


def where(r: dict) -> str:
    if r["level"] == "phu_luc":
        return r["title"] or r["unit_id"].split(":")[-1]
    parts = [f"Điều {r['dieu']}"]
    if r["khoan"]:
        parts.append(f"khoản {r['khoan']}")
    if r["diem"]:
        parts.append(f"điểm {r['diem']}")
    return ", ".join(parts)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    vers = [json.loads(l) for l in open(ROOT / "data/processed/legal_units_versioned.jsonl", encoding="utf-8")]
    rng = random.Random(SEED)
    rows = []
    for doc, k in QUOTA.items():
        pool = [r for r in vers if r["doc_id"] == doc and in_force_at(r, config.CUTOFF)[0]
                and r["level"] in ("dieu", "khoan", "diem") and 40 <= len(r["text"]) <= 700]
        if doc == "blds_2015":
            pool = [r for r in pool if 584 <= int(r["dieu"]) <= 608]
        pool.sort(key=lambda r: r["version_id"])
        with_numbers = [r for r in pool if re.search(r"\d", r["text"])]
        others = [r for r in pool if r not in with_numbers]
        n_num = min(len(with_numbers), (k * 2 + 2) // 3)  # khoảng 2/3 là đơn vị có con số
        picked = rng.sample(with_numbers, n_num) + rng.sample(others, k - n_num)
        if doc in ("tt_155_2025_btc", "tt_36_2024_byt"):  # thêm bảng đã dựng lại tay thay cho một đơn vị
            annex = next(r for r in vers if r["unit_id"] == f"{doc}:pl1" and in_force_at(r, config.CUTOFF)[0])
            picked = picked[:-1] + [annex]
        doc_pages = pages(doc)
        for r in sorted(picked, key=lambda r: r["unit_id"]):
            if r["unit_id"] in ANNEX_PAGES:  # bảng đã dựng lại: chữ khác PDF nên dò tự động không được
                pdf, page, conf = PAGE_SOURCES[doc][0], ANNEX_PAGES[r["unit_id"]], "đã xem ảnh"
            else:
                pdf, page, conf = locate(r["text"], doc_pages)
            rows.append({"van_ban": NAMES[doc], "vi_tri": where(r), "file_pdf": pdf, "trang_pdf": page,
                         "do_tin_cay_trang": conf, "noi_dung_trong_du_lieu": (r["title"] + "\n" if r["level"] == "dieu"
                                                                               and r["title"] else "") + r["text"],
                         "ket_qua": "", "ghi_chu_sai": "", "unit_id": r["unit_id"]})
    with OUT.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=["stt"] + list(rows[0]))
        w.writeheader()
        for i, row in enumerate(rows, 1):
            w.writerow({"stt": i, **row})
    print(f"{len(rows)} dòng -> {OUT.relative_to(ROOT)}")
    for i, row in enumerate(rows, 1):
        print(f"{i:2} {row['van_ban']:20} {row['vi_tri'][:30]:30} {Path(row['file_pdf']).name:24} tr.{row['trang_pdf']:<4} "
              f"{row['do_tin_cay_trang']:4} {row['noi_dung_trong_du_lieu'][:50]!r}")


if __name__ == "__main__":
    main()
