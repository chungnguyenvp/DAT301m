# Dữ liệu train cho fine-tune QLoRA (G5, tag `train-v1`)

## File

| File | Nội dung |
|---|---|
| `drafts/*.jsonl` | Nháp theo đợt, sinh bằng `scripts/g5_drafts/g5_*.py` |
| `train.jsonl`, `dev.jsonl` | 1.375 / 192 cặp hỏi đáp có căn cứ (`key, chu_de, loai, cau_hoi, dap_an, can_cu, nguon_nhap`), chia theo Điều |
| `MANIFEST.json` | Mã băm nháp, `train.jsonl`, `dev.jsonl` |
| `chat/train_chat.jsonl`, `chat/dev_chat.jsonl` | 1.662 / 192 hội thoại system / user / assistant đã gắn ngữ cảnh, dùng trực tiếp ở G6 |
| `chat/MANIFEST.json`, `chat/g5ctx_stats.json` | Mã băm, máy chạy, mẫu đã chuyển dạng; thống kê retriever và token |

Mỗi dòng `chat/*_chat.jsonl` có `key, ban, tap, chu_de, loai, dang, doan, retriever_tim_du, retriever_tim_mot_phan,
so_doan_can_co, so_doan_chen, so_doan_bo_vi_dai, messages, so_token`. `dang` là `co_ngu_canh` (5 đoạn luật, luôn có
đoạn chứa căn cứ), `khong_ngu_canh` (khoảng 10%, chỉ câu hỏi) hoặc `tu_choi` (5 đoạn retriever trả về, không chèn).
`doan[].chen = true` là đoạn đúng được chèn vì retriever bỏ sót. `ban = 1` là bản nhân đôi của tập train cho thủ tục và
các chủ đề Hướng dẫn, Bảo hiểm, Lệ phí, Tốc độ, với đoạn nhiễu ở hạng 6–10.

## Tái lập

1. Nháp và chia train/dev: xem `scripts/g5_drafts/README.md`.
2. Gắn ngữ cảnh (cần GPU): `py -3.13 scripts/build_g5ctx_bundle.py` tạo `kaggle/g5ctx/g5ctx_bundle.zip` và
   `g5_context.ipynb`. Chạy notebook trên Kaggle (`kaggle/g5ctx/HUONG_DAN.md`) hoặc máy có GPU, đặt 3 file kết quả vào
   `kaggle/g5ctx/out_local/`. Seed 42, ngày hỏi 2026-10-01; bge-m3 và bge-reranker-v2-m3 ghim theo revision.
3. `py -3.13 scripts/finalize_g5ctx.py` kiểm mã băm gói với repo và ghi `chat/`.

Bản `train-v1` chạy bước 2 trên RTX 5060 Ti (torch 2.14.1+cu130), tìm 1.567 câu trong 1.125 giây.

## Hạn chế

- Câu hỏi và đáp án do Claude và Codex soạn từ câu chữ luật, qua bộ kiểm tự động của G5 (số liệu, trích dẫn, chế tài,
  gần trùng với eval). **Người dùng chưa đọc tay mẫu nào** (bỏ qua Task 5 theo quyết định ngày 2026-10-19).
- Phân bố lệch so với eval: thủ tục ít hơn, Xử phạt nhiều hơn; chỉ cân bằng một phần bằng nhân đôi ở tập train.
- Retriever tìm đủ mọi đoạn căn cứ ở 67% mẫu train (mức phạt 44%); phần còn lại được chèn, nên ngữ cảnh train dễ
  hơn ngữ cảnh lúc chạy thật ở G7.
- Hai mẫu (`xp-0286`, `xp-1050`) có căn cứ ở nhiều Khoản hơn 5 ô nên được chuyển sang dạng không ngữ cảnh.
