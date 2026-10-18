# Chạy notebook gắn ngữ cảnh (G5 Task 4) trên Kaggle

Hai file cần tải lên:

- `g5ctx_bundle.zip` (khoảng 29 MB): kho đoạn luật, chỉ mục BM25 và FAISS của G3, mã `src/rag` và `src/lawproc`,
  `train.jsonl`, `dev.jsonl`, tokenizer Qwen. Không có bộ eval.
- `g5_context.ipynb`: notebook.

## Các bước

1. **Tạo dataset.** Kaggle → *Datasets* → *New Dataset* → kéo `g5ctx_bundle.zip` vào. Đặt tên, ví dụ `g5ctx-bundle`
   → *Create*. Kaggle tự giải nén file zip, notebook đọc được cả hai dạng.
2. **Tạo notebook.** *Code* → *New Notebook* → *File* → *Import Notebook* → chọn `g5_context.ipynb`.
3. **Gắn dataset.** Cột phải → *Add Input* → tìm dataset vừa tạo → *Add*.
4. **Cài đặt.** Cột phải → *Session options*:
   - *Accelerator*: **GPU T4 x2** (hoặc P100);
   - *Internet*: **On** (để tải bge-m3, bge-reranker-v2-m3 và cài `pyvi`, `rank_bm25`, `faiss-cpu`).
5. **Chạy.** *Save Version* → *Save & Run All (Commit)* → *Save*. Không cần mở trình duyệt chờ.
   Ước tính 20–30 phút: tải mô hình khoảng 6,5 GB, tìm kiếm khoảng 1.570 câu.
6. **Lấy kết quả.** Mở version vừa chạy → tab *Output* → tải 3 file:
   - `train_chat.jsonl` (khoảng 1.700 dòng),
   - `dev_chat.jsonl` (192 dòng),
   - `g5ctx_stats.json`.

   Gửi 3 file này (hoặc file zip của tab Output) để kiểm tra trước khi làm notebook train G6.

## Nếu có lỗi

- `Không thấy gói g5ctx trong /kaggle/input`: chưa *Add Input* dataset ở bước 3.
- Lỗi tải mô hình hoặc `pip install`: Internet đang *Off* ở bước 4.
- `bộ mã hóa câu hỏi … khác bộ mã hóa đã tạo chỉ mục`: Hugging Face trả về bản bge-m3 khác. Gửi lại log để kiểm.
- Lỗi khác: tải log của version (nút *Logs*) và gửi lại.
