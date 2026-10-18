# G4 — Kết quả chạy thử trên Kaggle (GPU Tesla T4, 14,56 GB)

Môi trường: Python 3.13, torch 2.11.0+cu128, unsloth 2026.10.6, transformers 5.16.1, trl 1.15.0; T4 không hỗ trợ bf16.

## Lần 1 (`g4_results.json`, `g4_answers.jsonl`; notebook `02_g4_kaggle`)

| | Qwen3.5-9B | Qwen3.5-4B |
|---|---|---|
| VRAM sau khi nạp 4-bit | 7,98 GB | 3,53 GB |
| Sinh không ngữ cảnh (20 câu dev) | 27,8 giây/câu, 11,9 token/giây | 26,8 giây/câu, 9,6 token/giây |
| Sinh theo Khoản (prompt ~1.800 token) | 26,1 giây/câu | 22,5 giây/câu |
| Sinh theo Điều | 5/20 câu, hết bộ nhớ ở prompt 8.223 token | 14/20 câu, hết bộ nhớ ở câu ~20.000 token |

Hết bộ nhớ ở phép attention (`scaled_dot_product_attention`), bộ nhớ tăng theo bình phương độ dài prompt. 4B không
nhanh hơn 9B. Đọc 4 câu: không ngữ cảnh thì cả hai mô hình dẫn văn bản cũ hoặc không tồn tại; theo Khoản thì 9B trả lời
đúng 3/4 câu (sai ở câu sát hạch hạng B1), 4B bịa số tiền ở câu lệ phí trước bạ.

## Lần 2 (`g4v2_results.json`, `g4v2_answers.jsonl`; notebook `03_g4_kaggle_v2`, chỉ Qwen3.5-9B)

- Train QLoRA 1 vòng, 100 mẫu đo thời gian (batch 2 × tích lũy 4, r = 16): **811 giây**, VRAM tối đa **9,16 GB**,
  loss cuối 1,096.
- Ước tính: train G6 (2.000 mẫu × 2 vòng) **9,0 giờ GPU**; sinh G7 theo Khoản (270 câu × A/B/C/D) **8,1 giờ**;
  tổng **17,1 giờ ≈ 57% quota 30 giờ/tuần**. Số giờ train giả định mẫu thật dài như mẫu đo thời gian (ngữ cảnh 5 đoạn
  theo Khoản); mẫu dài hơn thì lâu hơn.
- Bước sinh theo Điều **không hợp lệ**: hàm đếm token trả về 1 (bộ xử lý Qwen3.5 trả `input_ids` dạng lô) nên ngữ cảnh
  không bị cắt; 9/20 câu hết bộ nhớ. Mô hình nạp lại sau bước train còn chiếm 9,94 GB (thay vì 7,98 GB), nên cả câu
  5.573 token từng chạy được ở lần 1 cũng hỏng. Đã sửa ở notebook (hàm `token_ids`, `RUN_TRAIN = False` cho lần 3).

## Lần 3 (`g4v3_results.json`, `g4v3_answers.jsonl`; notebook `03_g4_kaggle_v2` đã sửa, `RUN_TRAIN = False`)

- Sinh 20 câu dev với ngữ cảnh theo Điều giới hạn 4.000 token: **20/20 câu chạy được**, 11 câu bị cắt bớt Điều (có câu
  từ 19.065 token còn 3.958 token, giữ 1/5 Điều). Prompt trung bình 3.394 token, lớn nhất 4.141 token; 33,7 giây/câu;
  VRAM tối đa 10,97 GB; 5/20 câu chạm giới hạn 384 token.
- Ước tính G7 nếu B, D dùng ngữ cảnh theo Điều: 9,2 giờ GPU (theo Khoản: 8,1 giờ).
- Đọc 3 câu (sơ bộ, chưa chấm cả 20): TH025 trả lời lệch sang kiểm định khí thải xe máy; TH060 nói sai bài sát hạch số 1, 2
  của hạng A1, A là "trong hình và trên đường"; SD009 đúng mức 60% nhưng tự nhân với lệ phí cấp biển (14.000.000 đồng) thành
  số tiền sai. Ngữ cảnh theo Điều dài hơn và lẫn nhiều văn bản nên mô hình dễ ghép nhầm. Cần chấm đủ 20 câu ở G7 trước khi
  kết luận.

## Kết luận G4

Chọn Qwen3.5-9B (4-bit, Unsloth) trên Kaggle T4. Train G6 khoảng 9 giờ, sinh G7 khoảng 8–9 giờ: vừa quota, không cần thuê
GPU. Ngữ cảnh theo Khoản là cấu hình chính; theo Điều chỉ chạy được khi giới hạn khoảng 4.000 token.
