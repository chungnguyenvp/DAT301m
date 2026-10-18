"""Dữ liệu train cho fine-tune (G5): nguồn, chia train/dev theo Điều, kiểm tự động, lọc gần trùng với eval.

Mẫu nháp: `key`, `chu_de`, `loai`, `cau_hoi`, `dap_an`, `can_cu` (danh sách `version_id`), tùy chọn `ngay_hoi`.
Quy ước: `can_cu[0]` là đơn vị chính (Điểm hoặc Khoản mô tả hành vi/quy định được hỏi); các căn cứ sau là câu dẫn
của Khoản, khoản chế tài trừ điểm/tước GPLX, hoặc quy định liên quan khác. Mẫu `tu_choi` không có căn cứ.

Kiểm tự động dùng lại `evalset.check_items`: mỗi mẫu được đổi sang dạng câu eval và gắn nhãn chế tài theo luật.
"""

import csv
import functools
import hashlib

from lawproc import config, evalset

LOAI = {"muc_phat", "thu_tuc", "quy_tac", "tinh_huong", "doi_thuong", "tu_choi"}
REQUIRED = ("key", "chu_de", "loai", "cau_hoi", "dap_an", "can_cu")
DEV_RATIO = 0.1


def article_of(unit_id: str) -> str:
    return ":".join(unit_id.split("@")[0].split(":")[:2])


def split_of(unit_id: str, dev_ratio: float = DEV_RATIO) -> str:
    """'dev' hoặc 'train' theo SHA-256 của `doc:Điều`: cùng Điều thì cùng tập, không phụ thuộc thứ tự."""
    h = int(hashlib.sha256(article_of(unit_id).encode("utf-8")).hexdigest()[:8], 16)
    return "dev" if h % 10_000 < dev_ratio * 10_000 else "train"


@functools.cache
def _groups() -> dict[str, str]:
    out: dict[str, str] = {}
    with config.MANIFEST.open(encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            out.setdefault(row["doc_id"], row["nhom"])
    for doc, info in config.DERIVED_DOCS.items():
        out[doc] = info["nhom"]
    return out


def topic_of(doc_id: str) -> str | None:
    return _groups().get(doc_id)


def source_chunks(chunks: list[dict], day: str = config.CUTOFF) -> list[dict]:
    """Đoạn theo Khoản có hiệu lực tại `day`, bỏ mẩu phụ lục (chỉ chứa một phần đơn vị)."""
    from rag import chunking

    return [c for c in chunks if chunking.in_force(c, day) and not c["mot_phan"]]


def _address(vid: str) -> dict:
    doc, *rest = vid.split("@")[0].split(":")
    out = {"van_ban": doc, "dieu": None, "khoan": None, "diem": None}
    if rest and rest[0].startswith("d"):
        out["dieu"] = rest[0][1:]
        if len(rest) > 1 and rest[1].startswith("k") and rest[1][1:2].isdigit():
            out["khoan"] = rest[1][1:]
            out["diem"] = rest[2] if len(rest) > 2 else None
        elif len(rest) > 1:
            out["diem"] = rest[1]
    return out


def as_eval_items(samples: list[dict], records: list[dict]) -> list[dict]:
    """Đổi mẫu train sang dạng câu eval để chạy `evalset.check_items`; nhãn chế tài suy từ luật."""
    live_cache: dict[str, dict] = {}
    items = []
    for s in samples:
        day = s.get("ngay_hoi") or config.CUTOFF
        item = {"id": s["key"], "tap": "test",  # `tap` chỉ để qua bước kiểm trường của check_items
                "chu_de": s["chu_de"], "loai_cau": s["loai"], "cau_hoi": s["cau_hoi"], "dap_an": s["dap_an"],
                "ngay_hoi": day, "can_cu": list(s["can_cu"])}
        if s["loai"] == "tu_choi":
            item.update(nhom_cau="ngoai_pham_vi", hanh_vi="tu_choi")
        else:
            item["nhom_cau"] = "thuong"
            if item["can_cu"]:
                item.update(_address(item["can_cu"][0]))
            uid = evalset.primary_unit(item)
            if day not in live_cache:
                live_cache[day] = evalset.live_versions(records, day)
            law = (evalset.sanctions(uid, live_cache[day]) if uid
                   else {"diem_tru": None, "tuoc_gplx_thang": None, "co_khoan_che_tai": False})
            item["diem_tru"] = law["diem_tru"]
            item["tuoc_gplx_thang"] = law["tuoc_gplx_thang"]
            item["trang_thai_diem_tru"] = ("co" if law["diem_tru"] is not None
                                           else "khong_tru" if law["co_khoan_che_tai"] else "khong_ap_dung")
        items.append(item)
    return items


def check_samples(samples: list[dict], records: list[dict]) -> list[str]:
    """Danh sách lỗi; rỗng nghĩa là mọi mẫu qua bộ kiểm."""
    problems = []
    seen: dict[str, int] = {}
    for s in samples:
        missing = [k for k in REQUIRED if k not in s]
        if missing:
            problems.append(f"{s.get('key', '?')}: thiếu trường {missing}")
        seen[s.get("key")] = seen.get(s.get("key"), 0) + 1
        if s.get("loai") not in LOAI:
            problems.append(f"{s.get('key', '?')}: loai lạ {s.get('loai')!r}")
    problems += [f"key trùng: {k}" for k, n in seen.items() if n > 1]
    good = [s for s in samples if all(k in s for k in REQUIRED) and s["loai"] in LOAI]
    return problems + evalset.check_items(as_eval_items(good, records), records)


def gplx_items(path=None) -> list[dict]:
    """281 câu sát hạch GPLX dùng làm bộ eval trắc nghiệm phụ (thuần chữ, đáp án còn khớp luật), dạng để lọc gần trùng.

    Bộ này do Cục CSGT soạn, độc lập với Claude, nên dữ liệu train không được chép lại câu đề.
    """
    import json

    path = path or config.PROCESSED / "gplx_600.jsonl"
    rows = [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]
    return [{"id": f"GPLX{r['so_cau']:03d}", "cau_hoi": r["cau_hoi"], "can_cu": []}
            for r in rows if not r["co_hinh"] and not r.get("can_xem_phap_ly")]


def _facts(vids: list[str]) -> list[str]:
    """unit_id của căn cứ, bỏ câu dẫn của Khoản/Điều khi đã có đơn vị con của nó (giữ thứ tự)."""
    uids = [v.split("@")[0] for v in vids]
    return [u for u in uids if not any(w.startswith(u + ":") for w in uids)]


def _same_fact(a: list[str], b: list[str]) -> bool:
    """Hai câu cùng hỏi một quy định: đơn vị nội dung đầu tiên của bên này nằm trong căn cứ của bên kia."""
    fa, fb = _facts(a), _facts(b)
    return bool(fa and fb) and (fa[0] in fb or fb[0] in fa)


def near_eval(samples: list[dict], eval_items: list[dict], threshold: float,
              same_unit_threshold: float | None = None) -> list[tuple[dict, str, float]]:
    """(mẫu, id câu eval, cosine) với các mẫu có câu hỏi gần trùng một câu eval (TF-IDF ký tự 4-gram).

    Gần trùng khi cosine ≥ `threshold`, hoặc khi mẫu và câu eval cùng hỏi một quy định (`_same_fact`) và cosine
    ≥ `same_unit_threshold`: đó là cùng một câu hỏi về cùng một quy định, chỉ diễn đạt khác.
    """
    from lawproc.eda import near_duplicates

    low = min(threshold, same_unit_threshold or threshold)
    texts = [x["cau_hoi"] for x in eval_items] + [s["cau_hoi"] for s in samples]
    groups = ["eval"] * len(eval_items) + ["train"] * len(samples)
    best: dict[int, tuple[str, float]] = {}
    for i, j, sim in near_duplicates(texts, groups, threshold=low):
        e, t = (i, j) if i < len(eval_items) else (j, i)
        k = t - len(eval_items)
        same = _same_fact(eval_items[e].get("can_cu") or [], samples[k].get("can_cu") or [])
        if sim >= threshold or (same and same_unit_threshold is not None and sim >= same_unit_threshold):
            if k not in best or sim > best[k][1]:
                best[k] = (eval_items[e]["id"], sim)
    return [(samples[k], eid, sim) for k, (eid, sim) in sorted(best.items())]
