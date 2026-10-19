# Chạy notebook sinh câu trả lời G7 trên Kaggle

Hai file cần tải lên:

- `g7_bundle.zip` (khoảng 112 MB): 270 câu `eval_v1` (không có đáp án) kèm ngữ cảnh RAG của G3, adapter LoRA của G6,
  script `g7_generate.py`. Tạo lại bằng `py -3.13 scripts/build_g7_bundle.py`.
- `g7_generate.ipynb`: notebook.

Notebook sinh 1.160 câu trả lời: A, B, C, D trên 270 câu, cộng B và D với ngữ cảnh bỏ lọc hiệu lực trên 40 câu sửa đổi
(RQ3). Chấm điểm làm sau, trên laptop.

## Các bước

1. **Tạo dataset.** Kaggle → *Datasets* → *New Dataset* → kéo `g7_bundle.zip` vào, đặt tên ví dụ `g7-bundle` →
   *Create*. Kaggle tự giải nén, notebook đọc được cả hai dạng. Để dataset ở chế độ *Private*, vì trong đó có adapter.
2. **Tạo notebook.** *Code* → *New Notebook* → *File* → *Import Notebook* → chọn `g7_generate.ipynb`.
3. **Gắn dataset.** Cột phải → *Add Input* → tìm dataset vừa tạo → *Add*.
4. **Cài đặt.** Cột phải → *Session options*:
   - *Accelerator*: **GPU T4 x2** (2 GPU chạy song song, nhanh gấp đôi; P100 cũng được nhưng chỉ 1 GPU);
   - *Internet*: **On** (để cài Unsloth và tải Qwen3.5-9B khoảng 19 GB).
5. **Chạy.** *Save Version* → *Save & Run All (Commit)* → *Save*. Không cần mở trình duyệt chờ.
   Ước tính **3–4 giờ** với T4 x2: khoảng 15–20 phút cài đặt và tải mô hình, phần còn lại là sinh câu trả lời.
   Lượt A, B (mô hình gốc) chậm hơn vì trả lời dài; C, D nhanh hơn.
6. **Lấy kết quả.** Mở version vừa chạy → tab *Output* → tải thư mục `out_g7`:
   - `g7_answers.jsonl`: 1.160 câu trả lời;
   - `g7_summary.json`: mỗi lượt đủ bao nhiêu câu, lỗi, thời gian, số câu chạm giới hạn 512 token;
   - `worker0.log`, `worker1.log`, `shard*_info.json`: log và thông tin nạp mô hình.

   Gửi `out_g7` (hoặc file zip của tab Output) để chấm điểm.

## Nếu phiên bị ngắt hoặc thiếu câu

Notebook tự dừng sau `MAX_HOURS = 11` giờ để kịp lưu kết quả. Nếu `g7_summary.json` báo `"du": false`:

1. Ở version vừa chạy → tab *Output* → *New Dataset* (tạo dataset từ output), ví dụ `g7-out-1`.
2. Mở lại notebook → *Add Input* cả `g7-out-1` (giữ `g7-bundle`).
3. *Save & Run All* lần nữa. Notebook đọc câu đã có trong `g7-out-1`, chỉ sinh phần còn thiếu, rồi gộp tất cả.

## Nếu có lỗi

- `Không thấy gói G7 trong /kaggle/input`: chưa *Add Input* dataset ở bước 3.
- Lỗi `pip install` hoặc tải mô hình: Internet đang *Off* ở bước 4.
- `bật/tắt adapter cho cùng logit`: adapter không được gắn, nên C/D sẽ giống A/B. Gửi `worker0.log`.
- Một vài câu báo `OutOfMemoryError` trong `g7_summary.json`: câu đó prompt quá dài (dài nhất khoảng 5.500 token).
  Chạy lại theo mục trên, các câu lỗi được thử lại.
- Lỗi khác: tải log của version (nút *Logs*) và `out_g7/worker*.log`, gửi lại.
