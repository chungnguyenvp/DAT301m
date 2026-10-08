from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
MANIFEST = DATA / "manifest.csv"

TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_REL = "tools/tessdata"  # tương đối với ROOT

CUTOFF = "2026-10-01"
SCANNED_DOCS = {"tt_108_2026_bca", "tt_155_2025_btc", "tt_36_2024_byt"}
NON_LEGAL = {"gplx_600_2025", "cv_2262_2025_csgt"}

# Văn bản có chứa chỉ dẫn sửa đổi văn bản khác
AMENDING_DOCS = {
    "luat_118_2025", "nd_238_2026", "nd_241_2026", "nd_218_2026", "nd_220_2026",
    "tt_37_2026_bca", "tt_51_2025_bca", "nd_51_2025", "nd_175_2025",
}

# Chuỗi nhận diện văn bản bị sửa → doc_id (so khớp sau normalize, không phân biệt hoa thường)
TARGET_ALIASES = {
    "168/2024/NĐ-CP": "nd_168_2024",
    "165/2024/NĐ-CP": "nd_165_2024",
    "158/2024/NĐ-CP": "nd_158_2024",
    "67/2023/NĐ-CP": "nd_67_2023",
    "10/2022/NĐ-CP": "nd_10_2022",
    "79/2024/TT-BCA": "tt_79_2024_bca",
    "12/2025/TT-BCA": "tt_12_2025_bca",
    "Luật Trật tự, an toàn giao thông đường bộ": "luat_36_2024",
    "Luật Đường bộ": "luat_35_2024",
}
