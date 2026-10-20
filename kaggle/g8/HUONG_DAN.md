# Chạy notebook sinh lại câu trả lời G8 trên Kaggle

G8 thử một cải tiến cho bước tìm kiếm: lấy 5 đoạn theo Khoản như cũ, rồi mở rộng mỗi đoạn lên **cả Điều** chứa nó,
trong giới hạn 2.500 token (`src/rag/expand.py`). Trên test, câu thường tìm đủ căn cứ từ 65,7% lên 82,8%. Notebook này
sinh lại câu trả lời với ngữ cảnh mới để đo câu trả lời có đúng hơn không. **Không train lại**: vẫn mô hình và adapter
của G6.

Hai file cần tải lên:

- `g8_bundle.zip` (khoảng 112 MB): giống gói G7 nhưng có thêm ngữ cảnh mới `ngu_canh_g8`, và `meta.json` chọn hai lượt
  `D_g8` (LoRA + RAG mới) và `B_g8` (gốc + RAG mới). Tạo lại bằng `py -3.13 scripts/build_g7_bundle.py --g8`.
- `g8_generate.ipynb`: cùng notebook với G7.

## Các bước (giống G7)

1. Kaggle → *Datasets* → *New Dataset* → kéo `g8_bundle.zip` vào, đặt tên ví dụ `g8-bundle`, chế độ *Private* →
   *Create*.
2. *Code* → *New Notebook* → *File* → *Import Notebook* → chọn `g8_generate.ipynb`.
3. *Add Input* → chọn **chỉ** dataset `g8-bundle`. Không thêm dataset G7: notebook sẽ đọc nhầm gói đầu tiên tìm được.
4. *Session options*: **GPU T4 x2**, **Internet On**.
5. Chạy. Nên dùng *Save Version → Save & Run All (Commit)*. Nếu Commit xếp hàng quá lâu thì chạy tương tác như lần G7
   và giữ tab mở.
6. Ước tính khoảng **2 giờ** với T4 x2: D_g8 khoảng 14 giây/câu, B_g8 khoảng 30 giây/câu, mỗi lượt 270 câu.
7. Khi ô gộp in `ĐỦ`, tải thư mục `out_g7` (tên thư mục giữ như G7) gồm `g7_answers.jsonl` (540 câu), `g7_summary.json`,
   log. Chép vào `du_an_hien_tai/kaggle/g8/out_g8/`.

Nếu thiếu thời gian, có thể dừng sau khi xong D_g8 (lượt chạy trước, khoảng 40 phút với 2 GPU). Tải
`answers_shard*.jsonl` về: D_g8 là phần chính để đo cải tiến.
