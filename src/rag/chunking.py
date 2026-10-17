"""Cắt kho luật có phiên bản thành đoạn cho RAG.

Hai cách cắt:
- `khoan`: mỗi đoạn là một Khoản, gồm tiêu đề Điều, câu dẫn của Điều (nếu có), câu dẫn Khoản và các Điểm.
  Đoạn vượt `max_tokens` thì gom các Điểm liền nhau thành nhiều mẩu, mẩu nào cũng lặp lại tiêu đề và câu dẫn.
  Điều không có Khoản là một đoạn (kèm các Điểm nằm thẳng dưới Điều).
- `dieu`: mỗi Điều là một đoạn, giữ nguyên cả Điều.

Phụ lục nội dung dài (và Điều, Khoản dài không có Điểm) thì tách theo dòng, đánh dấu `mot_phan`; `phan_dong`
ghi mẩu chứa những dòng nào của đơn vị. Mỗi mẩu lặp lại ghi chú hiệu lực và, nếu bắt đầu giữa bảng, dòng chú thích
bảng cùng dòng tên cột; phần lặp được tính vào giới hạn token. Đoạn dài hơn giới hạn (đoạn theo Điều) nêu ghi chú
hiệu lực ngay sau tiêu đề, vì reranker chỉ đọc phần đầu.

Mỗi đoạn mang `units`: các `version_id` mà chữ của đoạn thực sự chứa. Hiệu lực của đoạn suy từ
`in_force_at` của các đơn vị trong nhóm, xét tại mọi mốc ngày của chúng (ngày bắt đầu, ngày hết hiệu lực,
mốc của ngoại lệ). Giữa hai mốc liền nhau tập phiên bản có hiệu lực không đổi, nên mỗi khoảng là một đoạn.
"""

import csv
import functools
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from lawproc import config
from lawproc.validity import in_force_at

MAX_TOKENS = 512
ALPHABET = "a ă â b c d đ e ê g h i k l m n o ô ơ p q r s t u ư v x y".split()
NAMES = {
    "luat_36_2024": "Luật Trật tự, an toàn giao thông đường bộ 36/2024/QH15",
    "luat_35_2024": "Luật Đường bộ 35/2024/QH15",
    "blds_2015": "Bộ luật Dân sự 91/2015/QH13",
    "vbhn_135_2025_blhs": "Bộ luật Hình sự (văn bản hợp nhất 135/VBHN-VPQH)",
    "vbhn_90_2026_xlvphc": "Luật Xử lý vi phạm hành chính (văn bản hợp nhất 90/VBHN-VPQH)",
    "vbhn_63_2025_xlvphc": "Luật Xử lý vi phạm hành chính (văn bản hợp nhất 63/VBHN-VPQH)",
}
KIND = {"luat": "Luật", "nd": "Nghị định", "tt": "Thông tư"}


@dataclass(frozen=True)
class Group:
    anchor: str  # unit_id đặt tên cho đoạn: Khoản, Điều hoặc Phụ lục
    doc_id: str
    members: tuple[str, ...]  # unit_id theo thứ tự hiển thị


@functools.cache
def _numbers() -> dict[str, str]:
    out: dict[str, str] = {}
    with config.MANIFEST.open(encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            out.setdefault(row["doc_id"], row["so_ky_hieu"])
    for doc, info in config.DERIVED_DOCS.items():
        out[doc] = info["so_ky_hieu"]
    return out


def doc_name(doc_id: str) -> str:
    if doc_id in NAMES:
        return NAMES[doc_id]
    number = _numbers().get(doc_id)
    kind = KIND.get(doc_id.split("_")[0])
    if number and kind:
        return f"{kind} {number}"
    return number or doc_id


def load_tokenizer(path: Path | None = None) -> Callable[[str], int]:
    """Bộ đếm token bge-m3: lấy `config.TOKENIZERS`, không có thì lấy trong cache Hugging Face.

    Hàm trả về có thuộc tính `path`: file tokenizer thực sự được nạp.
    """
    from tokenizers import Tokenizer

    hub = Path.home() / ".cache/huggingface/hub/models--BAAI--bge-m3/snapshots"
    candidates = [path] if path else [config.TOKENIZERS["bge_m3"], *sorted(hub.glob("*/tokenizer.json"))]
    for p in candidates:
        if p and Path(p).exists():
            tok = Tokenizer.from_file(str(p))

            def count(text: str) -> int:
                return len(tok.encode(text, add_special_tokens=False).ids)

            count.path = Path(p)
            return count
    raise FileNotFoundError("không tìm thấy tokenizer.json của bge-m3")


def instruction_units(path: Path | None = None) -> set[str]:
    """unit_id của chỉ dẫn sửa đổi trong bảng đã duyệt (bỏ hậu tố `#…`).

    Dòng `duyet` đã được áp vào văn bản đích; dòng `loai` là dòng cha, hoặc chỉ dẫn cho văn bản ngoài kho.
    Chỉ giữ lại dòng mà người duyệt ghi rõ "không phải chỉ dẫn sửa đổi".
    """
    path = path or config.PROCESSED / "amendments_reviewed.csv"
    with path.open(encoding="utf-8-sig", newline="") as fp:
        return {row["amend_unit_id"].split("#")[0] for row in csv.DictReader(fp)
                if "không phải chỉ dẫn sửa đổi" not in (row.get("ghi_chu") or "")}


def load_scope(records: list[dict], exclude: set[str] | frozenset[str] | None = None) -> list[dict]:
    """Bản ghi dùng cho kho tra cứu: trong phạm vi, bỏ phụ lục mẫu biểu, bỏ chỉ dẫn sửa đổi và đơn vị con của nó.

    Nội dung của chỉ dẫn đã nằm trong phiên bản mới của văn bản đích (EDA E1). Bản bãi bỏ do `in_force_at` loại.
    """
    exclude = instruction_units() if exclude is None else exclude

    def dropped(uid: str) -> bool:
        parts = uid.split(":")
        return any(":".join(parts[:i]) in exclude for i in range(2, len(parts) + 1))

    return [r for r in records if r["trong_pham_vi"] and r.get("loai_phu_luc") != "mau_bieu"
            and not dropped(r["unit_id"])]


def in_force(chunk: dict, t: str) -> bool:
    return chunk["valid_from"] <= t and (chunk["valid_to"] is None or t < chunk["valid_to"])


def _number_key(label: str) -> tuple:
    m = re.match(r"(\d+)(.*)", label)
    return (int(m.group(1)), m.group(2)) if m else (10**6, label)


def _point_key(label: str) -> tuple:
    letter, num = re.match(r"(\D+?)(\d*)$", label).groups()
    return (ALPHABET.index(letter) if letter in ALPHABET else len(ALPHABET), letter, int(num or 0))


def _unit_key(uid: str) -> tuple:
    doc, top = uid.split(":")[:2]
    return (doc, top.startswith("pl"), _number_key(top.lstrip("dpl")))


def groups(records: list[dict], cach_cat: str) -> list[Group]:
    if cach_cat not in ("khoan", "dieu"):
        raise ValueError(f"cách cắt lạ: {cach_cat!r}")
    level, doc, has_text = {}, {}, set()
    kids: dict[str, set[str]] = defaultdict(set)
    for r in records:
        uid = r["unit_id"]
        level[uid], doc[uid] = r["level"], r["doc_id"]
        if r["text"].strip():
            has_text.add(uid)
        if r["level"] in ("khoan", "diem"):
            kids[uid.rsplit(":", 1)[0]].add(uid)

    def clauses(parent: str) -> list[str]:
        return sorted((u for u in kids[parent] if level[u] == "khoan"), key=lambda u: _number_key(u.rsplit(":k", 1)[1]))

    def points(parent: str) -> list[str]:
        return sorted((u for u in kids[parent] if level[u] == "diem"), key=lambda u: _point_key(u.rsplit(":", 1)[1]))

    out: list[Group] = []
    for uid in sorted((u for u in level if level[u] in ("dieu", "phu_luc")), key=_unit_key):
        if level[uid] == "phu_luc":
            out.append(Group(uid, doc[uid], (uid,)))
            continue
        lead = (uid,) if uid in has_text else ()
        ks, ps = clauses(uid), points(uid)
        if cach_cat == "dieu":
            out.append(Group(uid, doc[uid], lead + tuple(m for k in ks for m in (k, *points(k))) + tuple(ps)))
            continue
        out.extend(Group(k, doc[uid], lead + (k, *points(k))) for k in ks)
        if ps or not ks:
            out.append(Group(uid, doc[uid], lead + tuple(ps)))
    covered = {m for g in out for m in g.members}
    # Phòng hờ: đơn vị có chữ mà không thuộc nhóm nào (cha không nằm trong phạm vi) thành đoạn riêng.
    out.extend(Group(u, doc[u], (u,)) for u in sorted(has_text - covered, key=_unit_key))
    return [g for g in out if g.members]


def intervals(group: Group, versions: dict[str, list[dict]]) -> list[tuple[str, str | None, list[tuple[str, str]]]]:
    """Các khoảng [từ, đến) cùng danh sách (version_id, ghi chú hiệu lực) có hiệu lực trong khoảng."""
    recs = [r for u in group.members for r in versions[u]]
    marks = sorted({d for r in recs for d in (r["valid_from"], r["valid_to"],
                                               *(ex.get(k) for ex in r.get("hl_ngoai_le") or []
                                                 for k in ("tu_ngay", "den_ngay"))) if d})
    spans: list[list] = []
    current_key: tuple | None = None
    for t in marks:
        key = tuple((r["version_id"], note or "") for r in recs for ok, note in [in_force_at(r, t)] if ok)
        if key == current_key:
            continue
        if spans and spans[-1][1] is None and current_key:
            spans[-1][1] = t
        if key:
            spans.append([t, None, list(key)])
        current_key = key
    return [(a, b, live) for a, b, live in spans]


def _plain(rec: dict) -> str:
    """Chữ của đơn vị kèm nhãn ("2. …", "h) …"), chưa kèm ghi chú hiệu lực."""
    text = rec["text"].strip()
    if rec["level"] == "khoan":
        label = f"{rec['dieu']}.{rec['khoan']}" if rec["doc_id"] in config.DOTTED_KHOAN_DOCS else rec["khoan"]
        text = f"{label}. {text}"
    elif rec["level"] == "diem":
        text = f"{rec['diem']}) {text}"
    return text


def _label(rec: dict) -> str:
    """Tên đơn vị trong dòng ghi chú hiệu lực đặt ở đầu đoạn."""
    if rec["level"] == "diem":
        return f"điểm {rec['diem']} " + (f"khoản {rec['khoan']}" if rec["khoan"] else f"Điều {rec['dieu']}")
    if rec["level"] == "khoan":
        return f"khoản {rec['khoan']}"
    return f"Điều {rec['dieu']}" if rec["level"] == "dieu" else "phụ lục"


def _title_record(uid: str, versions: dict[str, list[dict]], t: str) -> dict | None:
    recs = versions.get(uid) or []
    live = [r for r in recs if in_force_at(r, t)[0]]
    return (live or recs or [None])[-1]


def _header(group: Group, versions: dict[str, list[dict]], t: str) -> str:
    name = doc_name(group.doc_id)
    top = ":".join(group.anchor.split(":")[:2])
    rec = _title_record(top, versions, t)
    if rec is None:
        return name
    if rec["level"] == "phu_luc":
        return f"{name} — {rec['title'] or 'Phụ lục'}"
    return f"{name} — Điều {rec['dieu']}. {rec['title']}".rstrip()


TABLE_CELL = " | "


def _render(header: str, top: list[str], rows: list[dict]) -> str:
    return "\n".join([header, *top, *(row["line"] for row in rows)])


def _note_lines(rows: list[dict]) -> list[str]:
    return list(dict.fromkeys(f"[Hiệu lực ({row['nhan']}): {row['note']}]" for row in rows if row["note"]))


def _table_context(seg: dict) -> list[str]:
    """Mẩu bắt đầu giữa bảng: lặp lại dòng chú thích bảng (nếu có) và dòng tên cột."""
    lines, j = seg["lines"], seg["j"]
    if TABLE_CELL not in lines[j]:
        return []
    h = j
    while h > 0 and TABLE_CELL in lines[h - 1]:
        h -= 1
    if h == j:
        return []
    caption = lines[h - 1] if h > 0 else ""
    if caption and TABLE_CELL not in caption and re.search(r"[^\W_]", caption) and len(caption) <= 200:
        return [caption, lines[h]]
    return [lines[h]]


def _pieces(header: str, rows: list[dict], count, max_tokens: int, split: bool) -> list[dict]:
    """Chia các đơn vị thành mẩu. Mỗi mẩu: `top` (dòng lặp lại), `rows`, `phan_dong` {version_id: [đầu, cuối, tổng]}."""
    whole = [dict(row, line=row["text"] + (f" [Hiệu lực: {row['note']}]" if row["note"] else "")) for row in rows]
    if not split or count(_render(header, [], whole)) <= max_tokens:
        return [{"top": [], "rows": whole, "phan_dong": {}}]
    fixed = [row for row in whole if row["level"] != "diem"]
    pts = [row for row in whole if row["level"] == "diem"]
    if pts:
        packs, current = [], []
        for p in pts:
            if current and count(_render(header, [], fixed + current + [p])) > max_tokens:
                packs.append(current)
                current = [p]
            else:
                current.append(p)
        packs.append(current)
        return [{"top": [], "rows": fixed + pack, "phan_dong": {}} for pack in packs]
    # Không có Điểm (phụ lục, Điều hay Khoản dài): tách theo dòng. Ghi chú hiệu lực và tên cột bảng được lặp lại
    # ở đầu mỗi mẩu, và được tính vào giới hạn token.
    segs = []
    for row in rows:
        lines = [line for line in row["text"].split("\n") if line.strip()]
        segs += [dict(row, line=line, lines=lines, j=j) for j, line in enumerate(lines)]

    def top(piece: list[dict]) -> list[str]:
        return _note_lines(piece) + _table_context(piece[0])

    packs, current = [], []
    for s in segs:
        candidate = current + [s]
        if current and count(_render(header, top(candidate), candidate)) > max_tokens:
            packs.append(current)
            current = [s]
        else:
            current = candidate
    packs.append(current)
    out = []
    for pack in packs:
        held: dict[str, list[int]] = defaultdict(list)
        total = {}
        for s in pack:
            held[s["vid"]].append(s["j"])
            total[s["vid"]] = len(s["lines"])
        partial = {vid: [min(js), max(js), total[vid]] for vid, js in held.items() if len(js) < total[vid]}
        out.append({"top": top(pack), "rows": pack, "phan_dong": partial})
    return out


def build_chunks(records: list[dict], cach_cat: str, count_tokens: Callable[[str], int],
                 max_tokens: int = MAX_TOKENS, exclude: set[str] | frozenset[str] | None = None) -> list[dict]:
    scope = load_scope(records, exclude)
    versions: dict[str, list[dict]] = defaultdict(list)
    for r in scope:
        versions[r["unit_id"]].append(r)
    for vs in versions.values():
        vs.sort(key=lambda r: r["valid_from"])
    by_vid = {r["version_id"]: r for r in scope}
    out = []
    for g in groups(scope, cach_cat):
        anchor = versions[g.anchor][0]
        is_annex = anchor["level"] == "phu_luc"
        for start, end, live in intervals(g, versions):
            header = _header(g, versions, start)
            rows = [{"text": _plain(by_vid[vid]), "vid": vid, "note": note, "level": by_vid[vid]["level"],
                     "nhan": _label(by_vid[vid])} for vid, note in live]
            pieces = _pieces(header, rows, count_tokens, max_tokens, split=cach_cat == "khoan" or is_annex)
            for i, piece in enumerate(pieces, 1):
                text = _render(header, piece["top"], piece["rows"])
                n = count_tokens(text)
                if n > max_tokens and not piece["top"] and _note_lines(piece["rows"]):
                    # Đoạn theo Điều dài: reranker chỉ đọc phần đầu, nên nêu điều kiện hiệu lực ngay sau tiêu đề.
                    piece["top"] = _note_lines(piece["rows"])
                    text = _render(header, piece["top"], piece["rows"])
                    n = count_tokens(text)
                out.append({
                    "chunk_id": f"{cach_cat}:{g.anchor}@{start}" + (f"#{i}" if len(pieces) > 1 else ""),
                    "cach_cat": cach_cat,
                    "nhom": g.anchor,
                    "doc_id": g.doc_id,
                    "dieu": anchor["dieu"] if not is_annex else None,
                    "khoan": anchor["khoan"] if anchor["level"] == "khoan" else None,
                    "units": list(dict.fromkeys(row["vid"] for row in piece["rows"])),
                    "phan_dong": piece["phan_dong"],
                    "valid_from": start,
                    "valid_to": end,
                    "ghi_chu_hieu_luc": list(dict.fromkeys(row["note"] for row in piece["rows"] if row["note"])),
                    "mot_phan": bool(piece["phan_dong"]),
                    "vuot_gioi_han": n > max_tokens and (cach_cat == "khoan" or is_annex),
                    "so_token": n,
                    "text": text,
                })
    return out
