"""Cải tiến G8: tìm theo Khoản rồi mở rộng mỗi đoạn lên Điều cha, trong một ngân sách token.

G7 cho thấy phần lớn câu sai của hệ thống chính là do ngữ cảnh thiếu căn cứ: tìm đúng một Khoản nhưng thiếu Khoản chế
tài, câu dẫn hay Khoản khác của cùng Điều; và lấy thêm Khoản theo hạng (top 5 → top 20) gần như không giúp. G3 thì cho
thấy cắt theo Điều tìm đủ căn cứ nhiều hơn hẳn, nhưng prompt dài tới gần 20.000 token.

Cách làm: duyệt các Khoản theo thứ tự của retriever (tối đa `rerank_k` đoạn đã xếp hạng). Với mỗi Khoản, thay bằng đoạn
Điều cha có hiệu lực tại ngày hỏi (đoạn nhỏ nhất của `chunks_dieu` chứa mọi đơn vị của Khoản) nếu còn vừa ngân sách;
không vừa thì giữ Khoản. Khoản đã nằm trong một Điều đã chọn thì bỏ qua. Dừng khi đủ `max_pieces` đoạn. Ngân sách 2.500
token được chọn trên dev và 30 câu train (G8), không dùng tập test.
"""

from collections import defaultdict

from rag import chunking

BUDGET = 2500
MAX_PIECES = 5


def parent_index(dieu_chunks: list[dict]) -> dict[tuple[str, str], list[dict]]:
    out: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in dieu_chunks:
        if c.get("dieu"):
            out[(c["doc_id"], c["dieu"])].append(c)
    return out


def parent_of(chunk: dict, index: dict, t: str) -> dict | None:
    """Đoạn Điều nhỏ nhất có hiệu lực tại t chứa mọi đơn vị của đoạn Khoản; None nếu không có (phụ lục...)."""
    if not chunk.get("dieu"):
        return None
    units = set(chunk["units"])
    cands = [p for p in index.get((chunk["doc_id"], chunk["dieu"]), [])
             if chunking.in_force(p, t) and units <= set(p["units"])]
    return min(cands, key=lambda p: (p["so_token"], p["chunk_id"])) if cands else None


def expand_to_dieu(ranked: list[dict], t: str, index: dict, budget: int = BUDGET,
                   max_pieces: int = MAX_PIECES) -> list[dict]:
    """`ranked`: các đoạn Khoản theo thứ tự retriever. Trả tối đa `max_pieces` đoạn (Điều hoặc Khoản), tổng
    `so_token` không quá `budget`."""
    out: list[dict] = []
    seen: set[str] = set()
    used = 0
    for ch in ranked:
        if ch["chunk_id"] in seen:
            continue
        p = parent_of(ch, index, t)
        for cand in ([p, ch] if p else [ch]):
            if cand["chunk_id"] in seen:
                break
            if used + cand["so_token"] <= budget:
                out.append(cand)
                used += cand["so_token"]
                seen.add(cand["chunk_id"])
                if cand is p:
                    seen.add(ch["chunk_id"])
                break
        if len(out) >= max_pieces:
            break
    return out
