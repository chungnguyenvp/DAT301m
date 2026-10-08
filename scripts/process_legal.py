"""Xử lý văn bản luật: python scripts/process_legal.py {convert|assemble|parse|effective|amendments|apply|all}"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from lawproc.amendments import extract_instructions  # noqa: E402
from lawproc.apply import apply_amendments  # noqa: E402
from lawproc.assemble import article_report, assemble_doc, group_rows, pick_sources  # noqa: E402
from lawproc.convert import convert_doc_files  # noqa: E402
from lawproc.effective import decide_effective, find_effective  # noqa: E402
from lawproc.extract import docx_lines, ocr_pdf_lines, pdf_lines  # noqa: E402
from lawproc.structure import Unit, parse_units  # noqa: E402
from lawproc.verify import check_identity  # noqa: E402

DOCX_DIR = config.INTERIM / "docx"
OCR_DIR = config.INTERIM / "ocr"
DOCS_DIR = config.PROCESSED / "documents"
UNITS = config.PROCESSED / "legal_units.jsonl"
EFFECTIVE = config.PROCESSED / "effective_dates.csv"
CANDIDATES = config.PROCESSED / "amendments_candidates.csv"
REVIEWED = config.PROCESSED / "amendments_reviewed.csv"
VERSIONED = config.PROCESSED / "legal_units_versioned.jsonl"


def manifest() -> list[dict]:
    return list(csv.DictReader(config.MANIFEST.open(encoding="utf-8-sig")))


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
    if method == "ocr":
        return ocr_pdf_lines(path, OCR_DIR / path.stem)
    return pdf_lines(path)


def step_convert() -> None:
    files = convert_doc_files(config.RAW / "legal", DOCX_DIR)
    print(f"docx: {len(files)} file trong {DOCX_DIR.relative_to(config.ROOT)}")


def step_assemble() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    reports, idents = [], []
    for doc_id, rows in group_rows(manifest()).items():
        chosen, method = pick_sources(rows)
        print(f"{doc_id:28} {method:5} {len(chosen)} phần")
        lines = assemble_doc(doc_id, [load_part(r, method) for r in chosen], method)
        (DOCS_DIR / f"{doc_id}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        reports.append(article_report(doc_id, lines, method, len(chosen)))
        idents.append(check_identity(doc_id, rows[0]["so_ky_hieu"], rows[0]["tieu_de"], "\n".join(lines)))
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
    meta = {r["doc_id"]: r for r in manifest()}
    rows = []
    for doc_id, units in load_units().items():
        m = meta[doc_id]
        found = find_effective(units)
        dec = decide_effective(doc_id, m["ngay_ban_hanh"], m["ngay_hieu_luc_congbao"], found)
        rows.append({"doc_id": doc_id, "so_ky_hieu": m["so_ky_hieu"], "ngay_ban_hanh": m["ngay_ban_hanh"],
                     "hl_congbao": m["ngay_hieu_luc_congbao"], "hl_van_ban": " ".join(found["dates"]),
                     "tu_dieu_hieu_luc": found["tu_dieu_hieu_luc"],
                     "trich_dan": found["trich_dan"], **dec, "ghi_chu": ""})
    write_csv(EFFECTIVE, rows)


def step_amendments() -> None:
    units = load_units()
    rows = []
    for doc_id in sorted(config.AMENDING_DOCS & units.keys()):
        title = next((u.text for u in units[doc_id] if u.level == "mo_dau"), "")[:600]
        rows += extract_instructions(doc_id, units[doc_id], title)
    write_csv(CANDIDATES, rows)


def step_apply() -> None:
    hl = {r["doc_id"]: r["hl_chot"] for r in csv.DictReader(EFFECTIVE.open(encoding="utf-8-sig"))}
    missing = [d for d, v in hl.items() if not v]
    if missing:
        sys.exit(f"Thiếu hl_chot trong effective_dates.csv: {missing}")
    amendments = list(csv.DictReader(REVIEWED.open(encoding="utf-8-sig")))
    units = [json.loads(x) for x in UNITS.open(encoding="utf-8")]
    recs = apply_amendments(units, hl, amendments)
    with VERSIONED.open("w", encoding="utf-8") as fp:
        for r in recs:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")
    live = sum(r["valid_to"] is None for r in recs)
    print(f"-> {VERSIONED.relative_to(config.ROOT)} ({len(recs)} bản ghi, {live} còn hiệu lực)")


STEPS = {"convert": step_convert, "assemble": step_assemble, "parse": step_parse,
         "effective": step_effective, "amendments": step_amendments, "apply": step_apply}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name in (["convert", "assemble", "parse", "effective", "amendments"] if arg == "all" else [arg]):
        print(f"\n== {name}")
        STEPS[name]()
