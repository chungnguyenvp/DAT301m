"""Chấm tìm kiếm theo rubric của `data/eval/README.md`.

Một nhóm trong `nhom_can_cu` đạt khi top-k cung cấp đủ một `version_id` của nhóm:
- có đoạn chứa trọn đơn vị đó (đơn vị nằm trong `units` và không nằm trong `phan_dong`); hoặc
- đơn vị bị tách thành nhiều mẩu (`phan_dong`): các mẩu lấy về phải chứa mọi dòng bằng chứng ghi cho câu đó
  trong `data/eval/bang_chung_v1.json`. Câu không có dòng bằng chứng thì các mẩu phải phủ đủ mọi dòng của đơn vị.

Đoạn chỉ được tính cho đơn vị mà nó thực sự chứa: không suy từ quan hệ cha/con của mã địa chỉ.
`rr` là 1 / hạng nhỏ nhất mà tại đó top-hạng đã thỏa ít nhất một nhóm.
"""

import functools
import json
import random
from collections import defaultdict
from pathlib import Path

from lawproc import config

METRICS = ("van_ban", "any", "all", "ty_le_nhom", "mrr")
EVIDENCE = config.DATA / "eval" / "bang_chung_v1.json"


@functools.cache
def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["cau"]


def load_evidence(path: Path | None = None) -> dict[str, dict[str, list[str]]]:
    """{key câu eval: {version_id: [dòng bắt buộc]}}"""
    return _load(path or EVIDENCE)


def _provides(vid: str, chunks: list[dict], lines: list[str] | None) -> bool:
    if any(vid in c["units"] and vid not in (c.get("phan_dong") or {}) for c in chunks):
        return True
    parts = [c for c in chunks if vid in (c.get("phan_dong") or {})]
    if not parts:
        return False
    if lines:
        text = "\n".join(c["text"] for c in parts)
        return all(line in text for line in lines)
    covered: set[int] = set()
    for c in parts:
        a, b, _ = c["phan_dong"][vid]
        covered |= set(range(a, b + 1))
    return len(covered) == parts[0]["phan_dong"][vid][2]


def _hits(groups: list[list[str]], chunks: list[dict], needed: dict[str, list[str]]) -> list[bool]:
    return [any(_provides(v, chunks, needed.get(v)) for v in g) for g in groups]


def score_item(item: dict, ranked_chunks: list[dict], k: int = 5, evidence: dict | None = None) -> dict | None:
    """Kết quả của một câu; None với câu không có căn cứ (ngoài phạm vi)."""
    if item["nhom_cau"] == "ngoai_pham_vi" or not item.get("can_cu"):
        return None
    needed = (load_evidence() if evidence is None else evidence).get(item.get("key"), {})
    top = ranked_chunks[:k]
    groups = item["nhom_can_cu"]
    hits = _hits(groups, top, needed)
    rank = next((r for r in range(1, len(top) + 1) if any(_hits(groups, top[:r], needed))), None) if any(hits) else None
    old = set(item.get("can_cu_cu") or [])
    return {
        "id": item["id"],
        "key": item.get("key"),
        "nhom_cau": item["nhom_cau"],
        "tap": item.get("tap"),
        "so_nhom": len(groups),
        "van_ban": any(c["doc_id"] == item.get("van_ban") for c in top),
        "any": any(hits),
        "all": all(hits),
        "ty_le_nhom": sum(hits) / len(groups),
        "rr": 1 / rank if rank else 0.0,
        "hang_dau_dung": rank,
        "nhom_thieu": [g for g, hit in zip(groups, hits) if not hit],
        "nham_ban_cu": any(old & set(c["units"]) for c in top) if item["nhom_cau"] == "sua_doi" else None,
        "top": [c["chunk_id"] for c in top],
    }


def _value(row: dict, metric: str) -> float:
    return float(row["rr"] if metric == "mrr" else row[metric])


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def summarize(rows: list[dict | None], items: list[dict], n_boot: int = 1000, seed: int = 0) -> dict:
    """Trung bình và CI95 theo nhóm câu; bootstrap lấy lại cả họ sự kiện (`ho_su_kien`)."""
    family = {x["id"]: x.get("ho_su_kien") or x["id"] for x in items}
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row is not None:
            by_group[row["nhom_cau"]].append(row)
    rng = random.Random(seed)
    out = {}
    for group in sorted(by_group):
        group_rows = by_group[group]
        metrics = METRICS + (("nham_ban_cu",) if group == "sua_doi" else ())
        clusters: dict[str, list[dict]] = defaultdict(list)
        for row in group_rows:
            clusters[family[row["id"]]].append(row)
        keys = sorted(clusters)
        samples = {m: [] for m in metrics}
        for _ in range(n_boot):
            picked = [row for key in rng.choices(keys, k=len(keys)) for row in clusters[key]]
            for m in metrics:
                samples[m].append(_mean([_value(row, m) for row in picked]))
        out[group] = {"n": len(group_rows), "so_ho": len(keys)}
        for m in metrics:
            s = sorted(samples[m])
            ci = [s[int(0.025 * (n_boot - 1))], s[int(0.975 * (n_boot - 1))]] if n_boot else [None, None]
            out[group][m] = {"gia_tri": _mean([_value(row, m) for row in group_rows]), "ci95": ci}
    return out


def variant_gap(rows: list[dict | None], items: list[dict]) -> dict:
    """Điểm của biến thể so với câu gốc cùng `ho_cau`, chỉ trên các cặp có cả hai kết quả."""
    by_id = {row["id"]: row for row in rows if row is not None}
    pairs = [(by_id[x["id"]], by_id[x["goc_id"]]) for x in items
             if x["nhom_cau"] == "bien_the" and x["id"] in by_id and x.get("goc_id") in by_id]
    out: dict = {"n": len(pairs)}
    for m in ("any", "all", "ty_le_nhom", "mrr"):
        v = _mean([_value(a, m) for a, _ in pairs]) if pairs else None
        b = _mean([_value(g, m) for _, g in pairs]) if pairs else None
        out[m] = {"bien_the": v, "goc": b, "chenh": v - b if pairs else None}
    return out
