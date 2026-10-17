"""Ghép các file nháp `data/eval/drafts/*.jsonl` thành `data/eval/eval_v1.jsonl`, gắn nhãn, chia dev/test, kiểm tra.

    py -3.13 scripts/build_eval.py                  # kiểm tra rồi ghi file
    py -3.13 scripts/build_eval.py --check          # chỉ kiểm tra
    py -3.13 scripts/build_eval.py --freeze-split   # chọn lại dev/test theo quy tắc và ghi split_v1.json

Tên file nháp quyết định nhóm câu: thuong_*.jsonl, sua_doi*.jsonl, ngoai_pham_vi*.jsonl, bien_the*.jsonl.
Câu nháp có `key` ổn định; `id` gán theo thứ tự nhóm rồi thứ tự trong file, nên id có thể đổi khi sửa nháp,
còn `key` thì không. Tập dev/test đọc từ `split_v1.json` (đã đóng băng). Câu có key chưa có trong file này
mặc định vào test; biến thể luôn theo tập của câu gốc. Quy tắc chọn ban đầu (chỉ chạy khi --freeze-split):
16 câu thường chia đều theo chủ đề, 4 câu sửa đổi, 4 câu ngoài phạm vi, chọn theo SHA-256 của key.

Nhãn suy tự động từ dữ liệu (`label`): trừ điểm và tước GPLX theo các khoản "Thực hiện hành vi…" cùng Điều,
khung phạt ở câu dẫn của Khoản, số liệu trong đáp án, nhóm căn cứ theo Khoản, họ câu, câu test dùng chung
căn cứ với dev.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402

DRAFTS = evalset.EVAL / "drafts"
OUT = evalset.EVAL / "eval_v1.jsonl"
SPLIT = evalset.EVAL / "split_v1.json"
MANIFEST = evalset.EVAL / "MANIFEST.json"
ORDER = ("thuong", "sua_doi", "ngoai_pham_vi", "bien_the")
PREFIX = {"thuong": "TH", "sua_doi": "SD", "ngoai_pham_vi": "NP", "bien_the": "BT"}
DEV = {"thuong": 16, "sua_doi": 4, "ngoai_pham_vi": 4}
FIELDS = ("id", "tap", "nhom_cau", "chu_de", "loai_cau", "cau_hoi", "dap_an", "hanh_vi", "can_cu", "nhom_can_cu",
          "van_ban", "dieu", "khoan", "diem", "dia_chi_chinh", "muc_phat_min", "muc_phat_max", "diem_tru",
          "trang_thai_diem_tru", "tuoc_gplx_thang", "so_lieu", "ngay_hoi", "dap_an_cu", "can_cu_cu", "ngay_cu",
          "van_ban_sua_doi", "goc_id", "ho_cau", "ho_su_kien", "kieu_bien_the", "kieu_ngoai", "ly_do", "trung_dev", "ghi_chu",
          "key", "nguon_nhap")
COPIED_FROM_BASE = ("chu_de", "loai_cau", "dap_an", "can_cu", "nhom_can_cu", "van_ban", "dieu", "khoan", "diem",
                    "dia_chi_chinh", "muc_phat_min", "muc_phat_max", "diem_tru", "trang_thai_diem_tru",
                    "tuoc_gplx_thang", "so_lieu", "ngay_hoi", "ho_su_kien")


def group_of(path: Path) -> str:
    return next(g for g in ORDER if path.stem.startswith(g))


def rank(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def pick_dev(items: list[dict]) -> set[str]:
    """Quy tắc chọn dev ban đầu; chỉ dùng khi đóng băng split, không bảo đảm ổn định khi thêm câu."""
    dev: set[str] = set()
    for group, n in DEV.items():
        pool = [x for x in items if x["nhom_cau"] == group]
        if group == "thuong":
            by_topic = defaultdict(list)
            for x in sorted(pool, key=lambda x: rank(x["key"])):
                by_topic[x["chu_de"]].append(x)
            queues = [by_topic[t] for t in sorted(by_topic)]
            chosen = 0
            while chosen < n and any(queues):
                for q in queues:
                    if q and chosen < n:
                        dev.add("thuong/" + q.pop(0)["key"])
                        chosen += 1
        else:
            dev |= {f"{group}/" + x["key"] for x in sorted(pool, key=lambda x: rank(x["key"]))[:n]}
    return dev


def khoan_address(vid: str) -> str:
    unit = vid.split("@")[0]
    parts = unit.split(":")
    return ":".join(parts[:3]) if len(parts) >= 3 and parts[2].startswith("k") else unit


def label(items: list[dict], records: list[dict]) -> None:
    """Gắn nhãn suy từ luật cho câu thường và câu sửa đổi (biến thể chép lại sau)."""
    live = evalset.live_versions(records, config.CUTOFF)
    for x in items:
        if x["nhom_cau"] not in ("thuong", "sua_doi"):
            continue
        # Mỗi căn cứ là một ý bắt buộc (AND). Chưa liệt kê căn cứ thay thế tương đương (OR) nào.
        x["nhom_can_cu"] = [[vid] for vid in x["can_cu"]]
        uid = evalset.primary_unit(x)
        x["dia_chi_chinh"] = khoan_address(uid) if uid else None
        if x["dia_chi_chinh"]:
            x["ho_su_kien"] = x["dia_chi_chinh"]  # câu thường và câu sửa đổi cùng hỏi một Khoản thuộc một họ
        law = evalset.sanctions(uid, live) if uid else {"diem_tru": None, "tuoc_gplx_thang": None,
                                                         "co_khoan_che_tai": False}
        if x.get("diem_tru") is None and law["diem_tru"] is not None:
            x["diem_tru"] = law["diem_tru"]
        x["tuoc_gplx_thang"] = law["tuoc_gplx_thang"]
        if law["diem_tru"] is not None:
            x["trang_thai_diem_tru"] = "co"
        elif law["co_khoan_che_tai"]:
            x["trang_thai_diem_tru"] = "khong_tru"
        else:
            x["trang_thai_diem_tru"] = "khong_ap_dung"
        if uid and x.get("muc_phat_min") is None and x.get("muc_phat_max") is None:
            fine = evalset.lead_fine(uid, live)
            if fine and set(fine) <= evalset.money_values(x["dap_an"]):
                x["muc_phat_min"], x["muc_phat_max"] = fine
        x["so_lieu"] = [[v, u] for v, u in sorted(evalset.facts(x["dap_an"]), key=str)]


def build(records: list[dict] | None = None, freeze: bool = False) -> list[dict]:
    items = []
    for group in ORDER:
        for path in sorted(DRAFTS.glob(f"{group}*.jsonl")):
            if group_of(path) != group:
                continue
            for n, line in enumerate(path.open(encoding="utf-8"), 1):
                if line.strip():
                    item = json.loads(line)
                    item["nhom_cau"] = group
                    item.setdefault("ngay_hoi", config.CUTOFF)
                    item["nguon_nhap"] = f"{path.name}:{n}"
                    items.append(item)
    keys = Counter(f"{x['nhom_cau']}/{x['key']}" for x in items)
    dup = [k for k, v in keys.items() if v > 1]
    if dup:
        sys.exit(f"key trùng: {dup}")
    if freeze or not SPLIT.exists():
        dev = pick_dev(items)
        split = {k: ("dev" if k in dev else "test") for k in keys if not k.startswith("bien_the/")}
    else:
        split = json.loads(SPLIT.read_text(encoding="utf-8"))
    counters = Counter()
    key_to_id = {}
    for x in items:
        counters[x["nhom_cau"]] += 1
        x["id"] = f"{PREFIX[x['nhom_cau']]}{counters[x['nhom_cau']]:03d}"
        key_to_id[f"{x['nhom_cau']}/{x['key']}"] = x["id"]
        x["tap"] = split.get(f"{x['nhom_cau']}/{x['key']}", "test")
        x["ho_cau"] = x["id"]
        x["ho_su_kien"] = x["id"]
    if records:
        label(items, records)
    by_id = {x["id"]: x for x in items}
    source = {r["version_id"]: r["source_doc_id"] for r in records or []}
    owner = {r["version_id"]: r["doc_id"] for r in records or []}
    for x in items:
        if x["nhom_cau"] == "sua_doi" and source:
            # Văn bản tạo ra phiên bản mới: ưu tiên căn cứ do văn bản sửa đổi sinh ra; văn bản thay thế thì là chính nó.
            amended = [source[v] for v in x["can_cu"] if v in source and source[v] != owner[v]]
            x["van_ban_sua_doi"] = amended[0] if amended else source.get(x["can_cu"][0], "")
        if x["nhom_cau"] == "bien_the":
            x["goc_id"] = key_to_id.get(f"thuong/{x.pop('goc_key', '')}", "")
            base = by_id.get(x["goc_id"])
            if base:
                x["tap"] = base["tap"]
                x["ho_cau"] = base["id"]
                for k in COPIED_FROM_BASE:
                    if k in base:
                        x[k] = base[k]
    dev_versions = {v for x in items if x["tap"] == "dev" for v in x["can_cu"]}
    for x in items:
        x["trung_dev"] = x["tap"] == "test" and any(v in dev_versions for v in x["can_cu"])
    return [{k: x[k] for k in FIELDS if k in x} for x in items]


def save_split(items: list[dict]) -> None:
    """Ghi split hiện tại: key cũ giữ nguyên tập, key mới đã được gán test, key bị xóa thì bỏ khỏi file."""
    SPLIT.write_text(json.dumps({f"{x['nhom_cau']}/{x['key']}": x["tap"] for x in items
                                 if x["nhom_cau"] != "bien_the"}, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--freeze-split", action="store_true")
    a = ap.parse_args()
    records = evalset.load_versions()
    items = build(records, freeze=a.freeze_split)
    problems = evalset.check_items(items, records)
    for p in problems:
        print("LỖI:", p)
    print(Counter((x["nhom_cau"], x["tap"]) for x in items))
    print("theo chủ đề (thường):", dict(Counter(x["chu_de"] for x in items if x["nhom_cau"] == "thuong")))
    if problems:
        sys.exit(1)
    if not a.check:
        save_split(items)
        with OUT.open("w", encoding="utf-8", newline="\n") as fp:
            for x in items:
                fp.write(json.dumps(x, ensure_ascii=False) + "\n")
        write_manifest(items)
        print(f"-> {OUT.relative_to(config.ROOT)}: {len(items)} câu")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(items: list[dict]) -> None:
    """Mã băm của bộ eval, split, nháp và dữ liệu nguồn để đối chiếu khi đóng băng."""
    data = config.PROCESSED / "legal_units_versioned.jsonl"
    blob = subprocess.run(["git", "rev-parse", "data-v1:data/processed/legal_units_versioned.jsonl"],
                          cwd=config.ROOT, capture_output=True, text=True).stdout.strip()
    manifest = {
        "eval": {"path": "data/eval/eval_v1.jsonl", "sha256": sha256(OUT), "items": len(items),
                 "groups": dict(Counter(x["nhom_cau"] for x in items)),
                 "splits": dict(Counter(x["tap"] for x in items))},
        "split": {"path": "data/eval/split_v1.json", "sha256": sha256(SPLIT)},
        "drafts": {f"data/eval/drafts/{p.name}": sha256(p) for p in sorted(DRAFTS.glob("*.jsonl"))},
        "source": {"path": "data/processed/legal_units_versioned.jsonl", "sha256": sha256(data),
                   "git_blob_in_tag_data_v1": blob},
        "cutoff": config.CUTOFF,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
