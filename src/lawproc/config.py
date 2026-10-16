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
# Đơn vị đủ dài có tỷ lệ âm tiết lỗi vượt ngưỡng được gắn nhãn kém.
QUALITY_BAD = 0.1
QUALITY_MIN_WORDS = 50
# PDF ảnh cần OCR khi không có nguồn khác. Nay TT 108, TT 155 có bản Word và TT 36 có bản chữ thuần
# đã đối chiếu, nên pick_sources chọn các nguồn đó và không OCR nữa.
SCANNED_DOCS = {"tt_108_2026_bca", "tt_155_2025_btc", "tt_36_2024_byt"}
# Trang từ 0, khóa theo tên file; chỉ giữ OCR lại khi chỉ số nhiễu chữ thấp hơn.
REOCR_PAGES = {"tt_108_2026_bca__p1": range(38, 134), "tt_36_2024_byt__p1": range(8, 14)}
REOCR_DPI = 400
NON_LEGAL = {"gplx_600_2025", "cv_2262_2025_csgt"}

# Văn bản có chứa chỉ dẫn sửa đổi văn bản khác
AMENDING_DOCS = {
    "luat_118_2025", "nd_238_2026", "nd_241_2026", "nd_218_2026", "nd_220_2026",
    "tt_37_2026_bca", "tt_51_2025_bca", "nd_51_2025", "nd_175_2025",
    "nd_47_2026", "tt_13_2025_bca", "tt_105_2026_bca", "tt_62_2026_bca",
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
    "65/2024/TT-BCA": "tt_65_2024_bca",
    "138/2021/NĐ-CP": "nd_138_2021",
    "Luật Trật tự, an toàn giao thông đường bộ": "luat_36_2024",
    "Luật Đường bộ": "luat_35_2024",
}

# Văn bản suy ra: tách từ văn bản cha khi ghép, không có dòng riêng trong manifest.
# start: chuỗi nằm trong dòng mở đầu văn bản suy ra (dòng đó và mọi dòng sau thuộc văn bản suy ra).
DERIVED_DOCS = {
    "qcvn_41_2024": {
        "parent": "tt_51_2024_bgtvt_qcvn41",
        "so_ky_hieu": "QCVN 41:2024/BGTVT",
        "tieu_de": "Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ",
        "nhom": "Biển báo",
        "start": "QCVN 41:2024/BGTVT QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ BÁO HIỆU ĐƯỜNG BỘ",
    },
}
# Văn bản đánh số khoản dạng "3.1." (số Điều.số khoản)
DOTTED_KHOAN_DOCS = {"qcvn_41_2024"}
