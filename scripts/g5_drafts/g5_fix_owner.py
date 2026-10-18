"""Bổ sung khoản 3 Điều 47 NĐ 168 vào các mẫu hỏi về người lái: nếu người lái đồng thời là chủ phương tiện thì bị xử phạt
theo điều khoản tương ứng của Điều 32. Chạy sau các script g5_xp*.py; chạy lại nhiều lần không nhân đôi ghi chú."""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
MARK = "Trường hợp người điều khiển đồng thời là chủ phương tiện"

# Điểm của khoản 3 Điều 47 -> các đơn vị (theo chữ của từng điểm)
RULES = {
    "a": {"d13": ["k4:a", "k6:a", "k7:a", "k7:b", "k8:a"], "d14": ["k2:a", "k2:b", "k2:c", "k3:a"],
          "d16": ["k1:a", "k2:a", "k2:c", "k2:d", "k2:đ"]},                      # biển số, đăng ký xe
    "b": {"d13": ["k5:a", "k6:b"], "d16": ["k1:đ", "k2:b"]},                    # tem kiểm định
    "c": {"d20": ["k6:d", "k7"], "d21": ["k5:b", "k6:c"]},                      # thời gian lái xe, phù hiệu
    "d": {"d13": ["k9:a"]},                                                    # niên hạn
    "e": {"d13": ["k3:d", "k4:b"]},                                            # thùng xe, ghế, giường
    "h": {"d20": ["k5:l", "k6:đ"], "d21": ["k3:b", "k5:c"]},                    # giám sát hành trình, camera
    "o": {"d20": ["k2", "k4"],                                                 # quá tải, quá khổ, quá số người
          "d21": ["k2:a", "k2:b", "k2:d", "k4", "k5:a", "k5:d", "k6:a", "k6:b", "k7:a", "k7:b", "k8:a", "k8:b"],
          "d22": ["k1:a", "k2", "k3:a", "k3:b", "k3:c", "k3:d"],
          "d34": ["k2", "k3:a", "k3:c", "k3:d", "k4:a", "k4:b", "k5:a"]},
    "p": {"d21": ["k10:a"]},                                                   # hàng dạng trụ
}
SINCE = {"h": "2026-08-15"}
INDEX = {f"nd_168_2024:{d}:{u}": p for p, by in RULES.items() for d, units in by.items() for u in units}

changed = 0
for path in sorted(glob.glob(str(ROOT / "data/train/drafts/xu_phat_*.jsonl"))):
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    for r in rows:
        point = INDEX.get(r["can_cu"][0].split("@")[0])
        if not point or MARK in r["dap_an"]:
            continue
        ref = f"nd_168_2024:d47:k3:{point}@{SINCE.get(point, '2025-01-01')}"
        r["dap_an"] = (r["dap_an"].rstrip() + f" {MARK} thì bị xử phạt theo điểm, khoản tương ứng của Điều 32 {ND} "
                       f"(điểm {point} khoản 3 Điều 47).")
        r["can_cu"].append(ref)
        changed += 1
        print(r["key"], point, "|", r["cau_hoi"][:70])
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print("đã bổ sung", changed, "mẫu")
