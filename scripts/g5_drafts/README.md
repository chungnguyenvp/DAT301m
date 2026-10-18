# Script sinh bản nháp dữ liệu train (G5)

Mỗi script `g5_*.py` ghi một file trong `data/train/drafts/`. Câu hỏi và câu trả lời được viết tay trong script; số
tiền, điểm, `can_cu` lấy từ đơn vị đang có hiệu lực tại `config.CUTOFF`.

Chạy lại toàn bộ (Windows cần `PYTHONIOENCODING=utf-8` để in tiếng Việt):

```bash
export PYTHONIOENCODING=utf-8
for f in scripts/g5_drafts/g5_{xp0?,gp0?,dk0?,np0?,dkiem0?,lephi01,tdbb01,luat0?,tntc01,hd0?,tt0?,tdbh02,tc02}.py; do py -3.13 "$f"; done
py -3.13 scripts/g5_drafts/g5_bb02_cx.py      # C1: biển báo và vạch kẻ đường, QCVN 41:2024
py -3.13 scripts/g5_drafts/g5_lu03_cx.py      # C2: Luật Đường bộ 35 và Luật Trật tự, an toàn giao thông đường bộ 36
py -3.13 scripts/g5_drafts/g5_xp08_cx.py      # C3: tình huống nhiều hành vi, NĐ 168 và nguyên tắc XLVPHC Điều 3
py -3.13 scripts/g5_drafts/g5_np03_cx.py      # C4: nguyên tắc xử phạt, tình tiết và người chưa thành niên
py -3.13 scripts/g5_drafts/g5_tn02_cx.py      # C5: tai nạn, bồi thường dân sự và các tội giao thông đường bộ
py -3.13 scripts/g5_drafts/g5_fix_owner.py   # bắt buộc sau khi chạy lại g5_xp*: thêm ghi chú khoản 3 Điều 47 NĐ 168 cho chủ xe
py -3.13 scripts/build_trainset.py           # kiểm tra, lọc gần eval, chia train/dev, ghi MANIFEST
```

`g5_dump.py <doc_id> [điều ...] [--titles] [--max N]` in các đơn vị đang có hiệu lực của một văn bản để soạn mẫu.
`g5_list.py --keys | --prefix bb | --chu-de "Tai nạn" | --doc qcvn_41_2024` xem mẫu đã có, key lớn nhất, Điều nào chưa dẫn.
Hướng dẫn soạn tiếp cho agent khác: `docs/superpowers/plans/2026-10-18-g5-codex-brief.md` (script mới có hậu tố `_cx`).
Đã kiểm tra ngày 2026-10-18: chạy lại các script cho ra các file nháp giống từng byte với bản đã commit.
