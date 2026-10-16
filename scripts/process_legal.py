"""Xử lý văn bản luật: python scripts/process_legal.py {convert|assemble|parse|effective|amendments|apply|all}"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from lawproc.amendments import extract_instructions  # noqa: E402
from lawproc.apply import apply_amendments  # noqa: E402
from lawproc.annotate import annotate_records, load_annex_overrides  # noqa: E402
from lawproc.assemble import (article_report, assemble_doc, drop_toc_lines, group_rows,  # noqa: E402
                              pick_sources, split_derived)
from lawproc.convert import convert_doc_files  # noqa: E402
from lawproc.corrections import apply_corrections  # noqa: E402
from lawproc.effective import decide_effective, find_effective  # noqa: E402
from lawproc.extract import docx_lines, ocr_pdf_lines, pdf_lines, text_lines  # noqa: E402
from lawproc.structure import Unit, parse_units  # noqa: E402
from lawproc.status import apply_annex_replacements, check_annex_replacements, mark_status, read_csv  # noqa: E402
from lawproc.validity import attach_exceptions, in_force_at, load_exceptions  # noqa: E402
from lawproc.verify import check_identity  # noqa: E402

DOCX_DIR = config.INTERIM / "docx"
OCR_DIR = config.INTERIM / "ocr"
DOCS_DIR = config.PROCESSED / "documents"
UNITS = config.PROCESSED / "legal_units.jsonl"
CORRECTIONS = config.DATA / "ocr_corrections.csv"
EFFECTIVE = config.PROCESSED / "effective_dates.csv"  # bản đã được người duyệt, chỉ đọc
EFFECTIVE_AUTO = config.PROCESSED / "effective_dates_auto.csv"  # đề xuất tự động do step_effective ghi
CANDIDATES = config.PROCESSED / "amendments_candidates.csv"
REVIEWED = config.PROCESSED / "amendments_reviewed.csv"
VERSIONED = config.PROCESSED / "legal_units_versioned.jsonl"
ANNEX_TYPES = config.PROCESSED / "annex_types.csv"
ANNEX_OVERRIDES = config.DATA / "annex_type_overrides.csv"
EXCEPTIONS = config.DATA / "effective_exceptions.csv"
CONTENT_GAPS = config.DATA / "content_gaps.csv"  # phần nguồn là ảnh chưa có chữ, đã duyệt
ANNEX_REPLACEMENTS = config.DATA / "annex_replacements.csv"  # chỉ áp dòng duyet = duyet


def manifest() -> list[dict]:
    return list(csv.DictReader(config.MANIFEST.open(encoding="utf-8-sig")))


def doc_meta() -> dict[str, dict]:
    """Meta theo doc_id (dòng đầu của manifest), gồm văn bản suy ra (config.DERIVED_DOCS)."""
    meta: dict[str, dict] = {}
    for r in manifest():
        meta.setdefault(r["doc_id"], r)
    for child, spec in config.DERIVED_DOCS.items():
        meta[child] = dict(meta[spec["parent"]], doc_id=child, so_ky_hieu=spec["so_ky_hieu"],
                           tieu_de=spec["tieu_de"], nhom=spec["nhom"])
    return meta


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"-> {path.relative_to(config.ROOT)} ({len(rows)} dòng)")


def load_part(row: dict, method: str) -> list[str]:
    path = config.ROOT / row["file"]
    if method == "docx":
        return docx_lines(DOCX_DIR / f"{path.stem}.docx")
    if method == "txt":
        return text_lines(path)
    if method == "ocr":
        return ocr_pdf_lines(path, OCR_DIR / path.stem,
                             retry_pages=config.REOCR_PAGES.get(path.stem, ()), retry_dpi=config.REOCR_DPI)
    return pdf_lines(path)


def step_convert() -> None:
    files = convert_doc_files(config.RAW / "legal", DOCX_DIR)
    print(f"docx: {len(files)} file trong {DOCX_DIR.relative_to(config.ROOT)}")


def load_corrections() -> dict[str, list[dict]]:
    """Sửa lỗi OCR đã ghi nhận, nhóm theo doc_id (giữ thứ tự dòng trong file)."""
    by_doc: dict[str, list[dict]] = {}
    if CORRECTIONS.exists():
        with CORRECTIONS.open(newline="", encoding="utf-8-sig") as fp:
            for r in csv.DictReader(fp):
                # git autocrlf co the doi LF trong o nhieu dong thanh CRLF
                r["wrong"] = r["wrong"].replace("\r\n", "\n")
                r["right"] = r["right"].replace("\r\n", "\n")
                by_doc.setdefault(r["doc_id"], []).append(r)
    return by_doc


def step_assemble() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    reports, idents = [], []
    corrections = load_corrections()
    meta = doc_meta()
    for doc_id, rows in group_rows(manifest()).items():
        chosen, method = pick_sources(rows)
        print(f"{doc_id:28} {method:5} {len(chosen)} phần")
        lines = assemble_doc(doc_id, [load_part(r, method) for r in chosen], method)
        if doc_id in corrections:
            lines = apply_corrections("\n".join(lines), corrections[doc_id]).split("\n")
            print(f"{'':28} {len(corrections[doc_id])} sửa lỗi OCR")
        lines = drop_toc_lines(lines)
        for out_id, part in split_derived(doc_id, lines).items():
            (DOCS_DIR / f"{out_id}.txt").write_text("\n".join(part) + "\n", encoding="utf-8")
            reports.append(article_report(out_id, part, method, len(chosen)))
            m = meta[out_id]
            idents.append(check_identity(out_id, m["so_ky_hieu"], m["tieu_de"], "\n".join(part)))
    write_csv(config.PROCESSED / "assembly_report.csv", reports)
    write_csv(config.PROCESSED / "identity_report.csv", idents)


def step_parse() -> None:
    n = 0
    with UNITS.open("w", encoding="utf-8") as fp:
        for path in sorted(DOCS_DIR.glob("*.txt")):
            for u in parse_units(path.stem, path.read_text(encoding="utf-8").splitlines()):
                fp.write(json.dumps(u.as_dict(), ensure_ascii=False) + "\n")
                n += 1
    print(f"-> {UNITS.relative_to(config.ROOT)} ({n} đơn vị)")


def load_units() -> dict[str, list[Unit]]:
    by_doc: dict[str, list[Unit]] = {}
    for line in UNITS.open(encoding="utf-8"):
        d = json.loads(line)
        by_doc.setdefault(d["doc_id"], []).append(Unit(**d))
    return by_doc


def step_effective() -> None:
    meta = doc_meta()
    rows = []
    for doc_id, units in load_units().items():
        m = meta[doc_id]
        found = find_effective(units)
        dec = decide_effective(doc_id, m["ngay_ban_hanh"], m["ngay_hieu_luc_congbao"], found)
        rows.append({"doc_id": doc_id, "so_ky_hieu": m["so_ky_hieu"], "ngay_ban_hanh": m["ngay_ban_hanh"],
                     "hl_congbao": m["ngay_hieu_luc_congbao"], "hl_van_ban": " ".join(found["dates"]),
                     "tu_dieu_hieu_luc": found["tu_dieu_hieu_luc"],
                     "trich_dan": found["trich_dan"], **dec, "ghi_chu": ""})
    write_csv(EFFECTIVE_AUTO, rows)


def step_amendments() -> None:
    units = load_units()
    rows = []
    for doc_id in sorted(config.AMENDING_DOCS & units.keys()):
        title = next((u.text for u in units[doc_id] if u.level == "mo_dau"), "")[:600]
        rows += extract_instructions(doc_id, units[doc_id], title)
    write_csv(CANDIDATES, rows)


def step_apply() -> None:
    if not EFFECTIVE.exists():
        sys.exit(f"Thiếu {EFFECTIVE.name}: hãy xem lại {EFFECTIVE_AUTO.name} (chạy bước effective để tạo), "
                 f"điền hl_chot/ghi_chu rồi lưu bản đã duyệt thành {EFFECTIVE.name} trong {EFFECTIVE.parent.name}/.")
    hl = {r["doc_id"]: r["hl_chot"] for r in csv.DictReader(EFFECTIVE.open(encoding="utf-8-sig"))}
    missing = [d for d, v in hl.items() if not v]
    if missing:
        sys.exit(f"Thiếu hl_chot trong effective_dates.csv: {missing}")
    amendments = list(csv.DictReader(REVIEWED.open(encoding="utf-8-sig")))
    units = [json.loads(x) for x in UNITS.open(encoding="utf-8")]
    recs = apply_amendments(units, hl, amendments)
    overrides = load_annex_overrides(ANNEX_OVERRIDES, recs)
    annex_rows = annotate_records(recs, overrides)
    write_csv(ANNEX_TYPES, annex_rows)
    attach_exceptions(recs, load_exceptions(EXCEPTIONS))
    mark_status(recs, read_csv(CONTENT_GAPS))
    approved = check_annex_replacements(read_csv(ANNEX_REPLACEMENTS), recs)
    apply_annex_replacements(recs, approved)
    print(f"thay thế phụ lục: {len(approved)} dòng đã duyệt được áp")
    with VERSIONED.open("w", encoding="utf-8") as fp:
        for r in recs:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")
    live = sum(in_force_at(r, config.CUTOFF)[0] for r in recs)
    print(f"-> {VERSIONED.relative_to(config.ROOT)} ({len(recs)} bản ghi, {live} có hiệu lực tại {config.CUTOFF})")


STEPS = {"convert": step_convert, "assemble": step_assemble, "parse": step_parse,
         "effective": step_effective, "amendments": step_amendments, "apply": step_apply}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name in (["convert", "assemble", "parse", "effective", "amendments"] if arg == "all" else [arg]):
        print(f"\n== {name}")
        STEPS[name]()
