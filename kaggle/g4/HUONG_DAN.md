# Chạy notebook G4 trên Kaggle

Mục đích: đo xem GPU miễn phí của Kaggle chạy nổi mô hình nào (Qwen3.5-9B hay bản nhỏ 4B) để chọn mô hình cho G5–G7.
Notebook chỉ dùng câu **dev**, không đụng tập test. 100 mẫu train trong gói **chỉ để đo thời gian**.

## File cần

Trong thư mục này (`kaggle/g4/`):

| File | Dùng làm gì |
|---|---|
| `g4_bundle.zip` | Dữ liệu: 20 câu dev kèm ngữ cảnh theo Khoản và theo Điều, 100 mẫu đo thời gian |
| `g4_kaggle.ipynb` | Notebook để import lên Kaggle |

Hai file được tạo bằng `py -3.13 scripts/build_g4_bundle.py`. Mã nguồn notebook nằm ở `notebooks/02_g4_kaggle.py`.

## Một lần duy nhất

1. Tạo tài khoản ở https://www.kaggle.com nếu chưa có.
2. Vào **Settings** của tài khoản, **xác minh số điện thoại**. Chưa xác minh thì notebook không bật được GPU và Internet.

## Mỗi lần chạy

1. **Tạo Dataset:** *Datasets → New Dataset*, kéo `g4_bundle.zip` vào, đặt tên (ví dụ `g4-bundle`), chọn **Private**,
   bấm *Create*. Kaggle tự giải nén file zip; notebook xử lý được cả hai trường hợp, đã hay chưa giải nén.
2. **Tạo Notebook:** *Code → New Notebook*, rồi *File → Import Notebook*, chọn `g4_kaggle.ipynb`.
3. **Gắn dữ liệu:** ở cột bên phải bấm *Add Input*, tìm dataset vừa tạo, bấm dấu cộng.
4. **Bật GPU và Internet:** cột bên phải, mục *Session options* (hoặc *Settings*):
   - *Accelerator*: **GPU T4 x2**, hoặc **GPU P100** nếu có;
   - *Internet*: **On**.
5. Bấm **Run All**. Dự kiến 1–1,5 giờ cho cả hai mô hình. Có thể đóng tab trình duyệt; phiên vẫn chạy trong giới hạn
   thời gian của Kaggle.
6. Chạy xong: mở tab **Output** (hoặc thư mục `/kaggle/working`), tải về `g4_results.json` và `g4_answers.jsonl`,
   đặt vào thư mục `reports/g4/` của dự án.

## Nếu có lỗi

- Notebook ghi kết quả **sau mỗi mô hình**, nên nếu mô hình thứ hai lỗi thì kết quả mô hình thứ nhất vẫn còn.
- Một mô hình lỗi khi nạp (ví dụ không có trên Hugging Face, hoặc hết bộ nhớ): lỗi được ghi vào `g4_results.json`
  ở mục `loi`, rồi notebook chạy tiếp mô hình kế tiếp.
- Ô `pip install` hoặc ô `import unsloth` lỗi: chụp hoặc chép thông báo lỗi trong ô bị đỏ, gửi lại để sửa notebook.
- Muốn đổi mô hình: sửa dòng `MODELS = [...]` ở ô cấu hình đầu tiên.

## Quota

Một lần chạy tốn khoảng 1–1,5 giờ GPU, trên quota thường khoảng 30 giờ mỗi tuần (Kaggle có thể thay đổi). Xem số giờ
còn lại ở trang *Settings* của tài khoản Kaggle.

## Lần chạy 2 (`g4_kaggle_v2.ipynb`)

Lần 1 đo được Qwen3.5-9B nạp và sinh câu trả lời được trên T4, nhưng hết bộ nhớ ở bước sinh với ngữ cảnh theo Điều
(prompt 8.223 token) nên chưa đo được thời gian train. Kết quả lần 1 nằm ở `reports/g4/`.

Bản 2 chỉ chạy Qwen3.5-9B và chỉ đo phần còn thiếu:

1. Train 100 mẫu trước, để luôn có số đo thời gian và VRAM khi train.
2. Nạp lại mô hình gốc, sinh 20 câu dev với ngữ cảnh theo Điều giới hạn 4.000 token (giữ nguyên từng Điều theo thứ
   hạng cho tới khi đủ). Câu nào vẫn hết bộ nhớ thì ghi lỗi và chạy câu tiếp.
3. Ước tính giờ GPU cho G6 và G7.

Cách chạy:

1. *Code → New Notebook* → *File → Import Notebook*, chọn `g4_kaggle_v2.ipynb`.
2. *Add Input*: chọn lại dataset `g4-bundle` đã tạo ở lần 1 (không cần tải lại dữ liệu).
3. *Accelerator*: **GPU T4 x2**; *Internet*: **On**.
4. Bấm **Save Version** (chọn *Save & Run All*), hoặc *Run All* rồi *Save Version* khi chạy xong. Dự kiến 30–45 phút.
5. Tải kết quả (file zip của version hoặc tab *Output*), gồm `g4v2_results.json` và `g4v2_answers.jsonl`; đặt vào
   `reports/g4/` hoặc gửi file zip lại.

## Lần chạy 3 (cùng file `g4_kaggle_v2.ipynb`, đã sửa)

Lần 2 đo được thời gian train (811 giây/100 mẫu, kết quả ở `reports/g4/`), nhưng bước sinh theo Điều chưa cắt ngữ cảnh do
lỗi đếm token. Notebook đã sửa và mặc định `RUN_TRAIN = False`: chỉ chạy bước sinh theo Điều (khoảng 20 phút). Cách chạy
giống lần 2: import lại `g4_kaggle_v2.ipynb` (bản mới), gắn dataset `g4-bundle`, GPU T4, Internet On, *Save & Run All*.
Lần chạy này không bắt buộc: chỉ cần nếu muốn so sánh cách cắt theo Điều với theo Khoản khi sinh câu trả lời.
