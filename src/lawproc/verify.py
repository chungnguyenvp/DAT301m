import re

from lawproc.clean import normalize

STOP = {"của", "và", "các", "về", "đối", "với", "trong", "theo", "quy", "định", "việc", "người"}


def _words(s: str) -> list[str]:
    return [w for w in re.findall(r"\w+", normalize(s).lower()) if len(w) >= 3 and w not in STOP]


def check_identity(doc_id: str, so_ky_hieu: str, tieu_de: str, text: str, head_chars: int = 4000) -> dict:
    # Văn bản hợp nhất ghi số "Số: NN/VBHN-VPQH" ở khối xác thực cuối văn bản nên xét cả đầu lẫn đuôi.
    head = normalize(text[:head_chars]).upper()
    tail = normalize(text[-head_chars:]).upper() if len(text) > head_chars else ""
    key = re.sub(r"\s+", "", normalize(so_ky_hieu)).upper()
    pattern = r"\s*".join(re.escape(ch) for ch in key)
    found = any(re.search(rf"(?<![\w/]){pattern}(?![\w/])", part) for part in (head, tail) if part)
    if normalize(tieu_de) == normalize(so_ky_hieu):
        ratio = 1.0
    else:
        words = _words(tieu_de)
        head_words = set(_words(head))
        ratio = round(sum(w in head_words for w in words) / len(words), 2) if words else 1.0
    status = "ok" if found and ratio >= 0.6 else "kiem_tra_tay"
    return {"doc_id": doc_id, "so_hieu_found": found, "title_ratio": ratio, "status": status}
