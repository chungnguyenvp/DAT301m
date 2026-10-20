"""G8: bảng chấm tay nội dung cho 50 câu test của cấu hình D (và B để so), dùng để kiểm LLM-Judge.

    py -3.13 scripts/g8_manual_sheet.py

Chọn 50 câu test theo tỷ lệ nhóm câu (thường 28, sửa đổi 8, biến thể 8, ngoài phạm vi 6), mỗi nhóm lấy ngẫu nhiên với
seed cố định, cân bằng câu G7 chấm đúng và sai trong nhóm. Ghi `reports/g8/cham_tay_50.csv` (UTF-8 có BOM, mở bằng
Excel). Người chấm điền cột `dat_D`, `dat_B`: 1 nếu câu trả lời nêu đủ các ý chính của đáp án chuẩn và không thêm chế
tài sai (rubric mục 3 của `data/eval/README.md`; câu ngoài phạm vi: đạt khi nói rõ không có căn cứ và không bịa), 0
nếu không; `ghi_chu` tùy ý. Không sửa file này sau khi chấm: G8 đọc lại để so với LLM-Judge.
"""

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402

QUOTA = {"thuong": 28, "sua_doi": 8, "bien_the": 8, "ngoai_pham_vi": 6}
SEED = 2026
OUT = config.ROOT / "reports" / "g8" / "cham_tay_50.csv"


def main() -> None:
    if OUT.exists():
        sys.exit(f"{OUT.relative_to(config.ROOT)} đã có: không ghi đè bảng có thể đã chấm")
    items = {f"{x['nhom_cau']}/{x['key']}": x for x in evalset.load_eval()}
    per = [json.loads(line) for line in open(config.ROOT / "reports" / "g7" / "per_item.jsonl", encoding="utf-8")]
    ans = {(r["run"], r["uid"]): r for r in per}
    rng = random.Random(SEED)
    picked = []
    for nhom, n in QUOTA.items():
        uids = sorted(u for u, x in items.items() if x["tap"] == "test" and x["nhom_cau"] == nhom)

        def ok(u):
            r = ans[("D", u)]
            return bool(r["tu_choi_dung"]) if nhom == "ngoai_pham_vi" else bool(r["so_lieu"] and r["so_lieu"]["du"])
        good, bad = [u for u in uids if ok(u)], [u for u in uids if not ok(u)]
        rng.shuffle(good)
        rng.shuffle(bad)
        k = min(len(bad), n // 2)
        picked += sorted(bad[:k] + good[:n - k])
    rng.shuffle(picked)   # trộn thứ tự để người chấm không đoán được nhóm
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["stt", "uid", "cau_hoi", "dap_an_chuan", "tra_loi_D", "tra_loi_B", "dat_D", "dat_B", "ghi_chu"])
        for i, u in enumerate(picked, 1):
            x = items[u]
            w.writerow([i, u, x["cau_hoi"], x["dap_an"], ans[("D", u)]["tra_loi"], ans[("B", u)]["tra_loi"], "", "", ""])
    print(f"-> {OUT.relative_to(config.ROOT)}: {len(picked)} câu")


if __name__ == "__main__":
    main()
