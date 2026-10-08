import re
from pathlib import Path

from lawproc import config
from lawproc.clean import join_wrapped, order_parts, strip_part
from lawproc.extract import is_scanned

DIEU_LINE = re.compile(r"^Điều\s+(\d+)[a-zđ]?\.")


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
    return join_wrapped(lines) if method in ("pdf", "ocr") else lines


def article_report(doc_id: str, lines: list[str], method: str, n_parts: int) -> dict:
    nums = sorted({int(m.group(1)) for x in lines if (m := DIEU_LINE.match(x))})
    missing = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)] if nums else []
    return {
        "doc_id": doc_id, "method": method, "n_parts": n_parts, "n_lines": len(lines),
        "n_dieu": len(nums), "first_dieu": nums[0] if nums else None,
        "last_dieu": nums[-1] if nums else None, "missing_dieu": " ".join(map(str, missing)),
    }
