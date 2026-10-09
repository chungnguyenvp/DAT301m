import re
from pathlib import Path

from lawproc import config
from lawproc.clean import join_wrapped, order_parts, strip_part
from lawproc.extract import is_scanned
from lawproc.structure import parse_units

OCR_LEADING_BORDER = re.compile(r"^\|+\s*")  # viền bảng bị OCR đọc thành "|" đầu dòng, che mất tiêu đề "Điều N."


def group_rows(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        if r["doc_id"] not in config.NON_LEGAL:
            groups.setdefault(r["doc_id"], []).append(r)
    return groups


def pick_sources(rows: list[dict]) -> tuple[list[dict], str]:
    word = [r for r in rows if r["dinh_dang"] in ("doc", "docx")]
    if word:
        return word, "docx"
    pdfs = [r for r in rows if r["dinh_dang"] == "pdf"]
    doc_id = rows[0]["doc_id"]
    scanned = doc_id in config.SCANNED_DOCS or any(
        is_scanned(config.ROOT / r["file"]) for r in pdfs if (config.ROOT / r["file"]).exists()
    )
    return pdfs, "ocr" if scanned else "pdf"


def assemble_doc(doc_id: str, part_lines: list[list[str]], method: str) -> list[str]:
    ordered = order_parts([strip_part(p) for p in part_lines])
    lines = [x for part in ordered for x in part]
    if method == "ocr":
        lines = [OCR_LEADING_BORDER.sub("", x) for x in lines]
    return join_wrapped(lines) if method in ("pdf", "ocr") else lines


def article_report(doc_id: str, lines: list[str], method: str, n_parts: int) -> dict:
    # Dùng parser (nhận biết trích dẫn “…” và phụ lục) để báo cáo khớp với đơn vị thật sự được tách ra.
    nums = sorted({int(re.match(r"\d+", u.dieu).group()) for u in parse_units(doc_id, lines) if u.level == "dieu"})
    missing = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)] if nums else []
    return {
        "doc_id": doc_id, "method": method, "n_parts": n_parts, "n_lines": len(lines),
        "n_dieu": len(nums), "first_dieu": nums[0] if nums else None,
        "last_dieu": nums[-1] if nums else None, "missing_dieu": " ".join(map(str, missing)),
    }


# Dòng mục lục: tiêu đề Phần/Chương/Mục/Phụ lục kèm số hiệu, kết thúc bằng chấm dẫn (có thể kèm số trang).
TOC_LINE = re.compile(
    r"^(?:Phần|PHẦN|Chương|CHƯƠNG|Mục|MỤC|Phụ lục|PHỤ LỤC)\s+[\dIVXLCA-Z]+\b.*[.…]{4,}\s*\d*\s*$"
)


def drop_toc_lines(lines: list[str]) -> list[str]:
    return [x for x in lines if not TOC_LINE.match(x)]


def split_derived(doc_id: str, lines: list[str]) -> dict[str, list[str]]:
    """Tách văn bản suy ra (config.DERIVED_DOCS) khỏi văn bản cha; văn bản khác trả nguyên."""
    out = {doc_id: lines}
    for child, spec in config.DERIVED_DOCS.items():
        if spec["parent"] != doc_id:
            continue
        idx = next((i for i, x in enumerate(lines) if spec["start"] in x), None)
        if idx is None:
            raise ValueError(f"{doc_id}: không thấy dòng mở đầu {child}: {spec['start']!r}")
        out = {doc_id: lines[:idx], child: lines[idx:]}
    return out
