# Script sinh bản nháp dữ liệu train (G5)

Mỗi script `g5_*.py` ghi một file trong `data/train/drafts/`. Câu hỏi và câu trả lời được viết tay trong script; số
tiền, điểm, `can_cu` lấy từ đơn vị đang có hiệu lực tại `config.CUTOFF`.

Chạy lại toàn bộ (Windows cần `PYTHONIOENCODING=utf-8` để in tiếng Việt):

```bash
export PYTHONIOENCODING=utf-8
for f in scripts/g5_drafts/g5_{xp0?,gp0?,dk0?,np01,dkiem01,lephi01,tdbb01,luat0?,tntc01,hd01}.py; do py -3.13 "$f"; done
py -3.13 scripts/g5_drafts/g5_fix_owner.py   # bắt buộc sau khi chạy lại g5_xp*: thêm ghi chú khoản 3 Điều 47 NĐ 168 cho chủ xe
py -3.13 scripts/build_trainset.py           # kiểm tra, lọc gần eval, chia train/dev, ghi MANIFEST
```

`g5_dump.py <doc_id> [điều ...] [--titles] [--max N]` in các đơn vị đang có hiệu lực của một văn bản để soạn mẫu.
Đã kiểm tra ngày 2026-10-18: chạy lại các script cho ra các file nháp giống từng byte với bản đã commit.
