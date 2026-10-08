"""Tải file văn bản gốc theo data/download_plan.csv vào data/raw/legal/ và ghi data/manifest.csv."""
import csv, hashlib, sys, time, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "download_plan.csv"
OUT = ROOT / "data" / "raw" / "legal"
MANIFEST = ROOT / "data" / "manifest.csv"
MAGIC = {b"%PDF": "pdf", b"\xd0\xcf\x11\xe0": "doc", b"PK\x03\x04": "docx"}


def sniff(head: bytes) -> str:
    return next((ext for sig, ext in MAGIC.items() if head.startswith(sig)), "unknown")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rows = list(csv.DictReader(PLAN.open(encoding="utf-8-sig")))
    part = {}
    out_rows = []
    for r in rows:
        part[r["doc_id"]] = part.get(r["doc_id"], 0) + 1
        ext = r["dinh_dang"] if len(r["dinh_dang"]) <= 4 else "pdf"
        dest = OUT / f"{r['doc_id']}__p{part[r['doc_id']]}.{ext}"
        if not dest.exists():
            req = urllib.request.Request(r["url"], headers={"User-Agent": "Mozilla/5.0"})
            for attempt in range(3):
                try:
                    data = urllib.request.urlopen(req, timeout=120).read()
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  retry {attempt + 1} {dest.name}: {e}")
                    time.sleep(3)
            else:
                print(f"FAIL {dest.name}")
                continue
            dest.write_bytes(data)
            time.sleep(0.5)
        data = dest.read_bytes()
        real = sniff(data[:4])
        ok = real == ext or (ext == "doc" and real == "docx")
        expected = int(r["bytes"] or 0)
        status = "ok" if ok and (expected <= 0 or expected == len(data)) else f"CHECK(type={real},size={len(data)}/{expected})"
        print(f"{status:10} {dest.name:40} {len(data)/1024:9.0f} KB")
        out_rows.append({
            "doc_id": r["doc_id"], "so_ky_hieu": r["so_ky_hieu"], "nhom": r["nhom"], "tieu_de": r["tieu_de"],
            "ngay_ban_hanh": r["ngay_ban_hanh"], "ngay_hieu_luc_congbao": r["ngay_hieu_luc"],
            "file": dest.relative_to(ROOT).as_posix(), "dinh_dang": real, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "nguon": "congbao.chinhphu.vn", "url": r["url"],
            "ngay_tai": date.today().isoformat(), "kiem_tra": status,
        })
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    print(f"\n{len(out_rows)}/{len(rows)} file, {sum(r['bytes'] for r in out_rows)/1048576:.1f} MB -> {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
