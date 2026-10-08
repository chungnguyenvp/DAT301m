"""Tải file văn bản gốc theo các file kế hoạch vào data/raw/ và ghi data/manifest.csv.

Chạy: python scripts/download_raw.py [plan.csv ...]
Không truyền tham số thì chạy mọi file data/download_plan*.csv. File đã có sẽ không tải lại.
Cột tùy chọn trong kế hoạch: `nguon` (mặc định congbao.chinhphu.vn), `thu_muc` (mặc định legal).
"""
import csv, hashlib, sys, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "manifest.csv"
MAGIC = {b"%PDF": "pdf", b"\xd0\xcf\x11\xe0": "doc", b"PK\x03\x04": "docx"}
# Một số cổng (ví dụ congan.cantho.gov.vn) trả 403 nếu User-Agent quá ngắn.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def sniff(head: bytes) -> str:
    return next((ext for sig, ext in MAGIC.items() if head.startswith(sig)), "unknown")


def fetch(url: str) -> bytes:
    origin = "{0.scheme}://{0.netloc}/".format(urllib.parse.urlsplit(url))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": origin, "Accept": "*/*"})
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=180).read()
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt + 1}: {e}")
            time.sleep(3)
    raise RuntimeError(f"không tải được {url}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    plans = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "data").glob("download_plan*.csv"))
    existing = {}
    if MANIFEST.exists():
        existing = {r["file"]: r for r in csv.DictReader(MANIFEST.open(encoding="utf-8-sig"))}
    out = dict(existing)
    for plan in plans:
        part = {}
        for r in csv.DictReader(plan.open(encoding="utf-8-sig")):
            part[r["doc_id"]] = part.get(r["doc_id"], 0) + 1
            ext = r["dinh_dang"] if len(r["dinh_dang"]) <= 4 else "pdf"
            dest = RAW / (r.get("thu_muc") or "legal") / f"{r['doc_id']}__p{part[r['doc_id']]}.{ext}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            rel = dest.relative_to(ROOT).as_posix()
            if not dest.exists():
                dest.write_bytes(fetch(r["url"]))
                time.sleep(0.5)
            data = dest.read_bytes()
            real = sniff(data[:4])
            expected = int(r["bytes"] or 0)
            ok = (real == ext or (ext == "doc" and real == "docx")) and (expected <= 0 or expected == len(data))
            status = "ok" if ok else f"CHECK(type={real},size={len(data)}/{expected})"
            print(f"{status:10} {rel:55} {len(data) / 1024:9.0f} KB")
            prev = existing.get(rel, {})
            out[rel] = {
                "doc_id": r["doc_id"], "so_ky_hieu": r["so_ky_hieu"], "nhom": r["nhom"], "tieu_de": r["tieu_de"],
                "ngay_ban_hanh": r["ngay_ban_hanh"], "ngay_hieu_luc_congbao": r["ngay_hieu_luc"],
                "file": rel, "dinh_dang": real, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                "nguon": r.get("nguon") or "congbao.chinhphu.vn", "url": r["url"],
                "ngay_tai": prev.get("ngay_tai") or date.today().isoformat(), "kiem_tra": status,
            }
    rows = list(out.values())
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nmanifest: {len(rows)} file, {sum(int(r['bytes']) for r in rows) / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
