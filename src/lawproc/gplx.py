"""Tách bộ 600 câu hỏi sát hạch lái xe (Cục CSGT, 2025) từ PDF có lớp chữ.

Theo Công văn 2262/CSGT-P5: đáp án đúng là phần gạch chân; câu hỏi in đậm "Câu N."; lựa chọn đánh số
"1.", "2."… Câu có hình (biển báo, sa hình) nhận biết bằng ảnh nằm trong vùng của câu.
"""
import re
import unicodedata
from pathlib import Path

import pymupdf

QUESTION = re.compile(r"^Câu\s+(\d+)\s*[.:]\s*(.*)$")  # câu 507 in "Câu 507:"
OPTION = re.compile(r"^(\d)\.\s+(.*)$")
PAGE_NO = re.compile(r"^\d{1,3}$")
# Khoảng câu của từng chương, theo Công văn 2262/CSGT-P5 mục I.1
CHAPTERS = [("I", 1, 180), ("II", 181, 205), ("III", 206, 263), ("IV", 264, 300), ("V", 301, 485),
            ("VI", 486, 600)]
MIN_IMAGE_SIDE = 20  # pt; bỏ ảnh trang trí nhỏ


def chapter_of(n: int) -> str:
    return next(name for name, lo, hi in CHAPTERS if lo <= n <= hi)


def _lines(page) -> list[dict]:
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = unicodedata.normalize("NFC", "".join(s["text"] for s in line["spans"]))
            text = re.sub(r"\s+", " ", text).strip()
            bold_chars = sum(len(s["text"]) for s in spans if "Bold" in s["font"] or s["flags"] & 16)
            out.append({"text": text, "bbox": line["bbox"],
                        "bold": bold_chars * 2 > sum(len(s["text"]) for s in spans)})
    return sorted(out, key=lambda ln: (round(ln["bbox"][1]), ln["bbox"][0]))


def _underlines(page) -> list[pymupdf.Rect]:
    return [d["rect"] for d in page.get_drawings() if d["rect"].height <= 2 and d["rect"].width >= 15]


def _is_underlined(bbox, underlines) -> bool:
    x0, _, x1, y1 = bbox
    return any(y1 - 4 <= r.y0 <= y1 + 6 and r.x0 < x1 and r.x1 > x0 for r in underlines)


MAX_OPTIONS = 4


def _split_inline(text: str, taken: set[int]) -> list[tuple[int, str, str]]:
    """Tách dòng có nhiều lựa chọn ("1. Biển 1. 2. Biển 2." hoặc lưới "1. Biển 1. 3. Cả ba.") thành
    [(số, đoạn in, nội dung)].

    Chỉ cắt tại nhãn lớn hơn nhãn trước trong dòng và chưa dùng, để số trong nội dung ("Biển 1.") không
    bị nhầm là nhãn; nếu một đoạn cắt ra không phải lựa chọn hợp lệ thì giữ nguyên cả dòng.
    """
    first = int(OPTION.match(text).group(1))
    cuts, last = [0], first
    for m in re.finditer(r"\s(?=(\d)\.\s)", text):
        k = int(m.group(1))
        if last < k <= MAX_OPTIONS and k not in taken:
            cuts.append(m.start() + 1)
            last = k
    segments = [text[a:b].strip() for a, b in zip(cuts, cuts[1:] + [len(text)])]
    matches = [OPTION.match(s) for s in segments]
    if not all(m and m.group(2).strip() for m in matches):
        return [(first, text, OPTION.match(text).group(2))]
    return [(int(m.group(1)), s, m.group(2)) for s, m in zip(segments, matches)]


def parse_questions(path: Path) -> list[dict]:
    """Câu hỏi theo thứ tự: so_cau, cau_hoi, lua_chon, dap_an (1-based; None nếu không đúng một đáp án), co_hinh."""
    questions: list[dict] = []
    starts: list[tuple[int, float]] = []  # (trang, y) đầu mỗi câu, để gán ảnh
    images: list[tuple[int, float]] = []
    cur = None  # câu đang đọc
    part = None  # "q" (nội dung câu hỏi) hoặc chỉ số lựa chọn đang đọc
    with pymupdf.open(str(path)) as doc:
        for pno, page in enumerate(doc):
            underlines = _underlines(page)
            for info in page.get_image_info():
                x0, y0, x1, y1 = info["bbox"]
                if x1 - x0 >= MIN_IMAGE_SIDE and y1 - y0 >= MIN_IMAGE_SIDE:
                    images.append((pno, (y0 + y1) / 2))
            for i, ln in enumerate(_lines(page)):
                text = ln["text"]
                if i == 0 and PAGE_NO.match(text):
                    continue
                m = QUESTION.match(text) if ln["bold"] else None
                if m:
                    cur = {"so_cau": int(m.group(1)), "cau_hoi": m.group(2), "_opts": {}, "_gach": {}}
                    questions.append(cur)
                    starts.append((pno, ln["bbox"][1]))
                    part = "q"
                    continue
                if cur is None:
                    continue
                opts = cur["_opts"]
                o = OPTION.match(text) if not ln["bold"] else None
                # nhãn mới: số kế tiếp, hoặc số nhỏ nhất còn thiếu (cột thứ hai của bố cục lưới)
                missing = min(set(range(1, MAX_OPTIONS + 1)) - set(opts), default=None)
                if o and int(o.group(1)) in (len(opts) + 1, missing) and int(o.group(1)) not in opts:
                    segments = _split_inline(text, set(opts))
                    for num, printed, option in segments:
                        box = ln["bbox"]
                        if len(segments) > 1:  # gạch chân chỉ nằm dưới đoạn của lựa chọn đúng
                            found = page.search_for(printed, clip=pymupdf.Rect(ln["bbox"]) + (-2, -2, 2, 2))
                            box = tuple(found[0]) if found else box
                        opts[num] = option
                        cur["_gach"][num] = _is_underlined(box, underlines)
                    part = segments[-1][0]
                elif part == "q":
                    cur["cau_hoi"] = f"{cur['cau_hoi']} {text}".strip()
                else:
                    opts[part] = f"{opts[part]} {text}"
                    cur["_gach"][part] = cur["_gach"][part] or _is_underlined(ln["bbox"], underlines)
    for k, q in enumerate(questions):
        opts, gach = q.pop("_opts"), q.pop("_gach")
        q["lua_chon"] = [opts[i] for i in sorted(opts)]
        q["nhan_lien_tuc"] = sorted(opts) == list(range(1, len(opts) + 1))
        marked = [i for i in sorted(gach) if gach[i]]
        q["dap_an"] = marked[0] if len(marked) == 1 and q["nhan_lien_tuc"] else None
        end = starts[k + 1] if k + 1 < len(starts) else (float("inf"), 0.0)
        q["co_hinh"] = any(starts[k] <= img < end for img in images)
    return questions


def parse_cv_lists(lines: list[str]) -> dict[str, set[int]]:
    """Số câu trong ba phụ lục của Công văn 2262: hạng A1/A (250), hạng B1 (300), điểm liệt (60).

    Chỉ lấy dòng là một số đứng riêng; dòng tiêu đề nhóm và dòng "(Kèm theo …)" bị bỏ qua.
    """
    keys = {"1": "hang_A1_A", "2": "hang_B1", "3": "diem_liet"}
    out: dict[str, set[int]] = {k: set() for k in keys.values()}
    current = None
    for raw in lines:
        line = raw.strip()
        m = re.match(r"^PHỤ LỤC\s+(\d)\b", line)
        if m:
            current = keys.get(m.group(1))
            continue
        if current and re.fullmatch(r"\d{1,3}", line) and 1 <= int(line) <= 600:
            out[current].add(int(line))
    return out
