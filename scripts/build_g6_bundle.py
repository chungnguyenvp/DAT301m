"""Gói cho G6 trên máy thuê: `remote/g6/g6_bundle.zip`.

    py -3.13 scripts/build_g6_bundle.py

Gói giữ bố cục repo để `scripts/g6_train.py` tìm thấy dữ liệu: `data/train/chat/{train,dev}_chat.jsonl`, `MANIFEST.json`
và script train, kèm `meta.json` ghi mã băm từng file (`setup_g6.sh` kiểm lại sau khi giải nén). `setup_g6.sh` nằm
sẵn ở `remote/g6/` và không nằm trong zip, vì nó phải chạy trước khi giải nén.
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402

OUT = config.ROOT / "remote" / "g6"
FILES = ["data/train/chat/train_chat.jsonl", "data/train/chat/dev_chat.jsonl", "data/train/chat/MANIFEST.json",
         "scripts/g6_train.py"]


def lf_bytes(name: str) -> bytes:
    """Nội dung như trong git (LF), để mã băm khớp `data/train/chat/MANIFEST.json` dù checkout trên Windows là CRLF."""
    return (config.ROOT / name).read_bytes().replace(b"\r\n", b"\n")


def main() -> None:
    data = {n: lf_bytes(n) for n in FILES}
    manifest = json.loads(data["data/train/chat/MANIFEST.json"])
    for n in ("train_chat.jsonl", "dev_chat.jsonl"):
        key = f"data/train/chat/{n}"
        assert hashlib.sha256(data[key]).hexdigest() == manifest["files"][key]["sha256"], f"{key} khác MANIFEST"
    meta = {"mo_ta": "Gói G6: dữ liệu chat train-v1 và script train QLoRA.",
            "file": {n: hashlib.sha256(b).hexdigest() for n, b in data.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path = OUT / "g6_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, b in [*data.items(), ("meta.json", (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode())]:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))  # cố định ngày để zip lặp lại được
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, b)
    print(f"-> {zip_path.relative_to(config.ROOT)}: {len(data)} file, {zip_path.stat().st_size / 1e6:.1f} MB")
    for n, h in meta["file"].items():
        print(f"   {h[:12]}  {n}")


if __name__ == "__main__":
    main()
