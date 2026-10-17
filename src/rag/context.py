"""Dựng ngữ cảnh cho mô hình từ các đoạn đã tìm: mỗi đoạn ghi số thứ tự, nguồn và khoảng hiệu lực."""

from datetime import date, timedelta

from rag.chunking import doc_name


def _vn(d: str) -> str:
    return date.fromisoformat(d).strftime("%d/%m/%Y")


def source_label(chunk: dict) -> str:
    """Ví dụ "Nghị định 168/2024/NĐ-CP, khoản 2 Điều 7"."""
    if chunk.get("dieu") is None:
        where = "phụ lục"
    elif chunk.get("khoan"):
        where = f"khoản {chunk['khoan']} Điều {chunk['dieu']}"
    else:
        where = f"Điều {chunk['dieu']}"
    return f"{doc_name(chunk['doc_id'])}, {where}"


def validity_label(chunk: dict) -> str:
    """`valid_to` là ngày đầu tiên hết hiệu lực, nên ngày cuối còn hiệu lực là ngày liền trước."""
    text = f"hiệu lực từ {_vn(chunk['valid_from'])}"
    if chunk.get("valid_to"):
        text += f" đến {(date.fromisoformat(chunk['valid_to']) - timedelta(days=1)).strftime('%d/%m/%Y')}"
    return text


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{n}] {source_label(c)} — {validity_label(c)}\n{c['text']}" for n, c in enumerate(chunks, 1))
