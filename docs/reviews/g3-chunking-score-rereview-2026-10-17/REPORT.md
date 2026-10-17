# Kiểm tra lại bản sửa G3 — 17/10/2026

**Kết luận: ba lỗi của vòng review trước đã được sửa đúng trên trạng thái hiện tại. Có thể chốt phần kỹ thuật Task 1–2 và chuyển sang BM25/vector.** Không thấy lỗi chặn mới trong phạm vi kiểm tra này. Đây chưa phải kết luận hoàn tất G3 hoặc đánh giá chất lượng truy hồi, vì luồng truy hồi và thực nghiệm chưa có.

Đã đọc mã triển khai, test, lớp bằng chứng bổ trợ, manifest, README và báo cáo sửa của Claude; đồng thời kiểm tra độc lập trên dữ liệu thật. Không dựa riêng vào các test mà Claude thêm.

## Kết quả chạy lại

| Kiểm tra | Kết quả |
| --- | --- |
| Toàn bộ test dự án | **364/364 qua**, không có test bị bỏ qua trong kết quả chạy |
| `scripts/build_chunks.py --check` | Khớp chunk và manifest |
| `scripts/build_eval.py --check` | Hợp lệ |
| Script kiểm tra độc lập của đợt này | **55/55 qua** |
| Hash `eval_v1.jsonl` | Giữ nguyên `5a1b72038ae79755f5df7c53ed46447ac1516bb04e8e1330fd81cfc43fc0e252` |

## Ba lỗi cũ

**1. Nhầm mẩu phụ lục — đã sửa.** Kiểm cả `lp06`, `lp07`, `lp08`, `bt04` trên hai cách cắt, sử dụng mặc định `k=5`. Mẩu sai kèm đủ căn cứ hỗ trợ đều trượt `all`; mẩu đúng kèm căn cứ hỗ trợ đều đạt. Chỉ cần tối đa ba chunk cho các phép thử này.

Riêng `lp08`: chỉ mẩu sai cho `rr=0`; mẩu đúng đứng sau mẩu sai cho `rr=0.5`; chỉ mẩu đúng cho `rr=1`. Tôi còn lần lượt xóa từng dòng trong ba dòng phí cần thiết khỏi bản sao mẩu đúng: cả ba trường hợp đều trượt. Không sửa file chunk thật khi thử.

Các dòng trong `bang_chung_v1.json` đúng nguyên văn nguồn. Khi không cung cấp annotation, một mẩu riêng bị từ chối và tập mẩu phủ đủ đơn vị được chấp nhận. Cách tính hạng mới phản ánh thời điểm nhóm căn cứ thực sự đủ.

**2. Mất điều kiện hiệu lực trong chữ — đã sửa.** Kiểm toàn bộ hai kho: số ghi chú trong metadata nhưng thiếu khỏi `text` bằng **0** ở cả hai cách cắt, thay cho 123 trước đây. Phần tách theo dòng đưa ghi chú lên đầu từng mẩu và tính phần này vào ngân sách token.

**3. Mất tên cột bảng — đã sửa cho trường hợp được báo.** Cả bốn mẩu khoản 46.3 QCVN41 trong kho theo Khoản đều có tên cột; mẩu giữa bảng có cả chú thích bảng. Cách cắt theo Điều giữ khoản này trong cả Điều nên không có cùng các mẩu `46.3#…` để so trực tiếp.

## Kiểm tra bổ sung

- Tất cả khoảng `phan_dong` đều hợp lệ; hợp các khoảng của mỗi đơn vị bị chia nhỏ phủ đầy đủ các dòng, không mất phần nguồn trong metadata độ phủ.
- Theo Khoản: **6.221 đoạn / 4.665 qua lọc ngày tại 01/10/2026**. Theo Điều: **2.149 / 1.487**. Khớp báo cáo sửa.
- SHA-256 của nguồn thực tế, bảng sửa đổi, bảng tên văn bản, tokenizer thực tải, lớp bằng chứng và hai file chunk đều khớp manifest.
- Phép thử sai trên thư mục tạm: sửa riêng `max_tokens` trong bản sao manifest, giữ hai file chunk nguyên vẹn. Nhánh `--check` thực tế trả mã lỗi 1 và chỉ ra `MANIFEST.json`. Không chạm manifest trong dự án.
- Kho theo Khoản còn **25 đoạn vượt 512 token**; cả 25 đều được gắn cờ và thực sự chỉ còn một Điểm hoặc một dòng nguồn dài cộng ngữ cảnh lặp. Không thấy trường hợp ghép nhiều Điểm/dòng khiến vượt giới hạn có thể tránh được bằng cách tách hiện tại.

## Giới hạn cần giữ khi làm bước tiếp

512 token vẫn là mục tiêu có ngoại lệ. Độ dài lớn nhất của toàn kho theo Khoản là 3.557 token; con số 626 trong báo cáo Claude nói về nhóm vượt giới hạn phát sinh thêm, không phải toàn kho. Luồng embedding/reranker cần xử lý và công bố việc cắt ngắn đầu vào như kế hoạch đã nêu. Đợt kiểm tra này chưa chạy mô hình để đo tác động đó.

Test giới hạn hiện chủ yếu kiểm cờ và số lượng đoạn vượt. Nên bổ sung điều kiện “chỉ một Điểm hoặc một dòng nguồn” vào test hồi quy; kiểm tra độc lập của đợt này đã xác nhận điều kiện đó trên dữ liệu hiện tại. Đây là đề nghị tăng độ bền test, không phải lỗi đang xảy ra cần chặn Task 1–2.

## Bằng chứng

- [verify.py](verify.py): script độc lập, chỉ đọc dữ liệu sản phẩm; phép thử manifest dùng thư mục tạm.
- [checks-055014147578Z.json](checks-055014147578Z.json): 55 kết quả kiểm tra, hash trạng thái được review và số liệu hai kho.

Mỗi lần chạy script tạo file bằng chứng mới; không ghi đè lần cũ. Đợt này chỉ thêm thư mục review mới, không sửa code triển khai/dữ liệu sản phẩm, không ghi đè review trước, không cài thư viện và không commit.
