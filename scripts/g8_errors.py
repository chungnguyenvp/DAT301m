"""G8: phân loại câu trả lời sai của G7 theo khâu gây lỗi, trên tập test.

    py -3.13 scripts/g8_errors.py

Đọc `reports/g7/per_item.jsonl` (chấm tự động G7) và `reports/retrieval/test_results.json` (G3: 5 đoạn đưa vào prompt
có chứa nhóm căn cứ nào). Mỗi câu trong phạm vi (thường, sửa đổi, biến thể) của một lượt có RAG được xếp vào đúng một
nhóm, theo thứ tự ưu tiên:

1. `dung`: nêu đúng mọi số liệu (hoặc, với câu không có số liệu, trích đúng Khoản/Điều chính) và không từ chối.
2. `tu_choi_sai`: từ chối dù câu trong phạm vi.
3. `khong_co_can_cu`: 5 đoạn không chứa nhóm căn cứ nào (lỗi tìm kiếm).
4. `thieu_mot_phan`: 5 đoạn chứa một số nhưng không đủ các nhóm căn cứ (lỗi tìm kiếm).
5. `loi_sinh`: 5 đoạn đủ căn cứ mà vẫn sai (lỗi đọc/ghép của mô hình).

Câu sửa đổi nêu số liệu bản cũ được đánh dấu thêm `trich_ban_cu`. Nhãn là tự động; bảng chấm tay ở G8 dùng để kiểm lại.
Kết quả: `reports/g8/loi_<lượt>.csv` và `reports/g8/loi_tong_hop.json`.
"""

import ast
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402

OUT = config.ROOT / "reports" / "g8"
GROUPS = ("thuong", "sua_doi", "bien_the")
ORDER = ["dung", "tu_choi_sai", "khong_co_can_cu", "thieu_mot_phan", "loi_sinh"]


def _val(x):
    return ast.literal_eval(x) if isinstance(x, str) else x


def correct(r: dict) -> bool:
    if r["tu_choi"]:
        return False
    if r["so_lieu"]:
        return r["so_lieu"]["du"]
    td = r["trich_dan"] or {}
    return bool(td.get("khoan", td.get("dieu", td.get("van_ban"))))


def classify(r: dict, ret: dict | None) -> str:
    if correct(r):
        return "dung"
    if r["tu_choi"]:
        return "tu_choi_sai"
    if ret is None or not _val(ret["any"]):
        return "khong_co_can_cu"
    if not _val(ret["all"]):
        return "thieu_mot_phan"
    return "loi_sinh"


def main() -> None:
    per = [json.loads(line) for line in open(config.ROOT / "reports" / "g7" / "per_item.jsonl", encoding="utf-8")]
    g3 = json.loads((config.ROOT / "reports" / "retrieval" / "test_results.json").read_text(encoding="utf-8"))
    ret = {r["id"]: r for r in g3["ket_qua"]["hybrid+rerank/khoan"]["tung_cau"]}
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"ghi_chu": __doc__.split("\n\n")[2].strip(), "luot": {}}
    for run in ("B", "D"):
        rows = []
        for r in per:
            if r["run"] != run or r["tap"] != "test" or r["nhom_cau"] not in GROUPS:
                continue
            g = ret.get(r["id"])
            nhom = classify(r, g)
            rows.append({"uid": r["uid"], "id": r["id"], "nhom_cau": r["nhom_cau"], "loai_cau": r["loai_cau"],
                         "nhom_loi": nhom, "trich_ban_cu": bool(r["rq3"] and r["rq3"]["trich_ban_cu"]),
                         "so_lieu": f"{r['so_lieu']['dung']}/{r['so_lieu']['n']}" if r["so_lieu"] else "",
                         "nhom_can_cu_thieu": "; ".join(v[0] for v in _val(g["nhom_thieu"]) or []) if g else "",
                         "top5": "; ".join(_val(g["top"]) or []) if g else "", "tra_loi": r["tra_loi"]})
        with open(OUT / f"loi_{run}.csv", "w", encoding="utf-8-sig", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        by = defaultdict(Counter)
        for row in rows:
            by["tat_ca"][row["nhom_loi"]] += 1
            by[row["nhom_cau"]][row["nhom_loi"]] += 1
            by[f"loai/{row['loai_cau']}"][row["nhom_loi"]] += 1
        summary["luot"][run] = {k: {n: c[n] for n in ORDER} | {"n": sum(c.values())} for k, c in by.items()}
        summary["luot"][run]["trich_ban_cu"] = sum(row["trich_ban_cu"] for row in rows)
    (OUT / "loi_tong_hop.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                           newline="\n")
    for run, s in summary["luot"].items():
        print(run, {k: v for k, v in s.items() if k in ("tat_ca", *GROUPS)})


if __name__ == "__main__":
    main()
