"""Áp các sửa lỗi OCR đã ghi nhận (data/ocr_corrections.csv) vào văn bản đã ghép."""


def apply_corrections(text: str, rows: list[dict]) -> str:
    """Thay lần lượt từng `wrong` bằng `right`.

    Mỗi `wrong` phải xuất hiện đúng một lần trong văn bản hiện tại; nếu không (đã hết hạn hoặc
    mơ hồ) thì raise ValueError để sửa lỗi cũ không âm thầm bị bỏ qua.
    """
    for r in rows:
        wrong, right = r["wrong"], r["right"]
        n = text.count(wrong)
        if n == 0:
            raise ValueError(f"{r.get('doc_id', '')}: chuỗi sai không có trong văn bản: {wrong[:80]!r}")
        if n > 1:
            raise ValueError(f"{r.get('doc_id', '')}: chuỗi sai xuất hiện {n} lần (cần đúng 1): {wrong[:80]!r}")
        text = text.replace(wrong, right)
    return text
