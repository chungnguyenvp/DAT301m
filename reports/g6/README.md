# G6 — Kết quả fine-tune QLoRA (máy thuê RTX 5060 Ti 16 GB)

Kế hoạch: [docs/superpowers/plans/2026-10-19-g6-finetune.md](../../docs/superpowers/plans/2026-10-19-g6-finetune.md).
Script: `scripts/g6_train.py`. Gói và hướng dẫn chạy: `remote/g6/` (`setup_g6.sh`, `HUONG_DAN.md`).

- **Môi trường:** Python 3.12.3, torch 2.14.1 + CUDA 13.0, Unsloth 2026.10.6, transformers 5.17.0, peft 0.21.2, bf16.
- **Mô hình gốc:** `Qwen/Qwen3.5-9B` commit `c202236235762e1c871ad0ccb60c8ee5ba337b9a`, nạp 4-bit (8,0 GB).
- **Dữ liệu:** `train-v1`, 1.662 mẫu train, 192 mẫu dev. Không mẫu nào bị bỏ vì quá dài (dài nhất 3.712 token).
- **Train:** 2 vòng, 416 bước, mất **2,37 giờ** (20,5 giây/bước). VRAM đỉnh 9,17 GB. Loss train trung bình 0,254.

## Loss dev

| Bước | 52 | 104 | 156 | **208** | 260 | 312 | 364 | 416 |
|---|---|---|---|---|---|---|---|---|
| Loss dev | 0,354 | 0,329 | 0,316 | **0,313** | 0,338 | 0,336 | 0,343 | 0,344 |

Adapter được giữ là checkpoint **bước 208** (hết vòng 1), có loss dev thấp nhất. Vòng 2 quá khớp nhẹ: loss train còn
khoảng 0,15, còn loss dev tăng lại. Lần sau train 1 vòng là đủ, khoảng 1,2 giờ.

| Loại câu | Loss dev, mô hình gốc | Đã train |
|---|---|---|
| Tất cả | 0,804 | 0,316 |
| Mức phạt | 0,567 | 0,245 |
| Thủ tục | 0,905 | 0,453 |
| Quy tắc | 0,842 | 0,350 |
| Đời thường | 0,812 | 0,370 |
| Tình huống | 0,712 | 0,320 |
| Từ chối | 2,117 | 0,244 |

Theo dạng mẫu: có ngữ cảnh 0,656 → 0,267; không ngữ cảnh 1,594 → 0,947; từ chối 2,150 → 0,235.

## File

- `g6_results.json`: môi trường, cấu hình, thời gian, loss dev theo loại câu.
- `train_log.jsonl`, `train.log`, `smoke.log`: log từng bước, log đầy đủ, log chạy thử 12 bước.
- `plots/`: loss train/dev, learning rate, grad norm, độ dài mẫu, loss dev theo loại câu.
- `dev_answers.jsonl`: 12 câu dev, câu trả lời của mô hình gốc và mô hình đã train.
- `dev_loss_per_sample.jsonl`: loss từng câu dev.
- `log_may_thue/`: log cài đặt trên máy thuê (G5 Task 4 và G6).

**Adapter** (116 MB) không nằm trong git. Bản trên máy ở `remote/g6/ketqua/out_g6/adapter/`, và có trong gói G7
(`kaggle/g7/g7_bundle.zip`, tạo lại bằng `scripts/build_g7_bundle.py`). Cần sao lưu riêng, ví dụ đẩy lên Hugging
Face như kế hoạch tổng thể.
