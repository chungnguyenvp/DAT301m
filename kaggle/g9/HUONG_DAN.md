# Chạy demo G9 (Gradio) trên Kaggle

Hai file cần tải lên:

- `g9_bundle.zip` (khoảng 138 MB): adapter LoRA của G6, đoạn luật và chỉ mục tìm kiếm theo Khoản của G3, đoạn theo Điều
  (cho chế độ mở rộng G8), prompt lấy từ dữ liệu train, câu mẫu, và code (`scripts/g9_demo.py` cùng phần `src/` cần
  dùng). Tạo lại bằng `py -3.13 scripts/build_g9_bundle.py`.
- `g9_demo.ipynb`: notebook.

## Các bước

1. **Tạo dataset.** Kaggle → *Datasets* → *New Dataset* → kéo `g9_bundle.zip` vào, đặt tên ví dụ `g9-bundle` →
   *Create*. Để chế độ *Private*, vì trong gói có adapter.
2. **Tạo notebook.** *Code* → *New Notebook* → *File* → *Import Notebook* → chọn `g9_demo.ipynb`.
3. **Gắn dataset.** Cột phải → *Add Input* → tìm `g9-bundle` → *Add*.
4. **Cài đặt.** Cột phải → *Session options*: *Accelerator* **GPU T4 x2**, *Internet* **On**.
5. **Chạy.** Bấm **Run All** ngay trong trình soạn notebook. **Không** dùng *Save Version*: chế độ commit chạy ngầm,
   không thấy link.
   - Cài thư viện và tải mô hình khoảng 15–20 phút (Qwen khoảng 19 GB, bge-m3 khoảng 4,5 GB, reranker khoảng 2,3 GB).
   - Ô gần cuối in khung `DEMO SẴN SÀNG: https://xxxx.gradio.live`. Mở link này trên trình duyệt hoặc điện thoại.
   - Ô cuối chạy mãi để giữ demo sống. Muốn tắt thì bấm dừng ô đó.
6. **Trong lúc demo:** giữ tab Kaggle mở. Phiên Kaggle tắt thì link chết, phải *Run All* lại từ đầu. Lần sau nhanh hơn
   một chút nếu Kaggle còn giữ cache, nhưng đừng trông vào điều đó: **nên bật notebook trước giờ demo khoảng 30 phút.**

Máy 2 GPU: tìm kiếm chạy ở GPU 1, Qwen + LoRA ở GPU 0. Máy 1 GPU (P100, Colab T4) vẫn chạy được, cả hai dùng chung GPU.

## Giao diện

- **Câu hỏi**, **Ngày hỏi** (dd/mm/yyyy, mặc định 01/10/2026). Bấm *Hỏi* hoặc Enter.
- **Chế độ:** D (LoRA + RAG, hệ thống chính), B (mô hình gốc + RAG), hoặc *So sánh B và D* (sinh D trước rồi B).
- **Ngữ cảnh:** 5 đoạn theo Khoản (G3, mặc định), hoặc mở rộng lên Điều (G8).
- **Lọc hiệu lực:** bật mặc định. Tắt để minh họa RQ3: hệ thống lấy cả bản đã hết hiệu lực.
- Dòng thông tin ghi thời gian tìm kiếm, số token prompt, thời gian sinh. Mục *Đoạn luật đã dùng* liệt kê từng đoạn kèm
  văn bản, Điều/Khoản, ngày hiệu lực; đoạn không có hiệu lực tại ngày hỏi được đánh dấu ⚠️.
- Thời gian dự kiến trên T4: D khoảng 10–15 giây/câu, B khoảng 20–40 giây/câu (trả lời dài hơn).

## Kịch bản demo gợi ý (khoảng 5 phút)

Câu mẫu có sẵn ở cuối trang, bấm vào là điền câu hỏi và ngày. Đã kiểm trên laptop: với các câu mẫu, demo lấy đúng các
đoạn luật và dựng đúng prompt như lúc chạy G7/G8 (10/10 câu, cả hai cách dựng ngữ cảnh). Sinh greedy nên câu trả lời D
và B ở ngày 01/10/2026 sẽ trùng (hoặc gần như trùng) với câu trả lời đã chấm trong Report 3, ghi dưới đây.

1. **Câu thường, chế độ D.** "Lái ô tô không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị xử phạt như thế nào?"
   → phạt 18–20 triệu đồng (điểm b khoản 9 Điều 6 NĐ 168/2024), trừ 04 điểm GPLX. Mở *Đoạn luật đã dùng* để chỉ căn cứ.
2. **So sánh B và D.** "Tôi đi xe máy chở vợ và con trai 10 tuổi cùng lúc thì có đúng luật không?"
   → D: *đúng luật*, được chở tối đa hai người khi chở trẻ em dưới 12 tuổi (điểm c khoản 1 Điều 33 Luật 36/2024).
   B: trả lời *không đúng luật*, dài và chậm hơn nhiều. Đây là ví dụ cho kết luận của Report 3: LoRA làm câu trả lời
   gọn, nhanh và ít bịa hơn.
3. **Đổi ngày hỏi (RQ3).** "Tài xế ô tô được lái xe tối đa bao nhiêu giờ một ngày và bao lâu thì phải nghỉ?"
   - Ngày 01/10/2026: lái xe liên tục không quá 04 giờ, thời gian làm việc theo Bộ luật Lao động (khoản 1 Điều 64 Luật
     36/2024, bản sửa đổi có hiệu lực từ 01/7/2026).
   - Đổi ngày thành 01/03/2026: đoạn luật lấy về là bản cũ (không quá 10 giờ/ngày, 48 giờ/tuần). Câu trả lời ở ngày cũ
     chưa sinh trước ở G7, nên nên chạy thử một lần trước khi demo.
   - Về lại 01/10/2026 và **tắt lọc hiệu lực**: ở G7, D khi bỏ lọc đã trả lời theo bản cũ "10 giờ trong một ngày". Đây
     là minh họa vì sao lọc hiệu lực là bắt buộc.
4. **Ngoài phạm vi.** "Đi tàu hỏa mà không mua vé thì bị phạt bao nhiêu tiền?" → D từ chối, nói chỉ hỗ trợ luật giao
   thông đường bộ. "Theo Nghị định 100/2019/NĐ-CP, người đi xe máy vượt đèn đỏ bị phạt bao nhiêu?" → D nói văn bản đã hết
   hiệu lực và chỉ sang NĐ 168/2024.

Câu mẫu khác: thời hạn cấp GPLX sau khi thi đậu (02 giờ theo TT 108/2026; ngày 01/03/2026 lấy TT 12/2025: 07 ngày làm
việc), cấp lại biển số bị mất (07 ngày làm việc; ngày 01/03/2026 lấy bản cũ: xác minh 30 ngày).

**Nên quay video** một lượt chạy tốt để dự phòng nếu mạng hoặc Kaggle trục trặc lúc demo trực tiếp.

## Nếu có lỗi

- Ô cài đặt báo lỗi, hoặc dòng kiểm thư viện không in phiên bản: chụp lại output ô đó. Thường do `gradio` kéo theo bản
  thư viện khác với bản Unsloth cần.
- Ô chạy demo báo `CHƯA CÓ LINK`: ô in 40 dòng cuối của `/kaggle/working/g9/demo.log`. Gửi log đó để sửa.
- Câu đầu tiên chậm hơn các câu sau (khởi động CUDA), đó là bình thường.
- Chạy thử trên laptop (không GPU, không sinh thật, chỉ kiểm tìm kiếm và giao diện):
  `py -3.13 scripts/g9_demo.py --backend dry` (cần `pip install gradio`), hoặc
  `py -3.13 scripts/g9_demo.py --backend dry --selftest 13` (không cần gradio).
