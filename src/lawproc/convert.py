import shutil
from pathlib import Path

WD_FORMAT_DOCX = 16


def convert_doc_files(src_dir: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(src_dir.glob("*.docx")):
        if not (out_dir / p.name).exists():
            shutil.copy2(p, out_dir / p.name)
    todo = [p for p in sorted(src_dir.glob("*.doc")) if not (out_dir / f"{p.stem}.docx").exists()]
    if todo:
        import win32com.client

        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        try:
            for p in todo:
                d = word.Documents.Open(str(p), False, True)
                d.SaveAs2(str(out_dir / f"{p.stem}.docx"), WD_FORMAT_DOCX)
                d.Close(False)
        finally:
            word.Quit()
    return sorted(out_dir.glob("*.docx"))
