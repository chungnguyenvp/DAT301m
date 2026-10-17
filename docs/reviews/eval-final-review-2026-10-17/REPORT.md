# Xác nhận bản sửa sau hai vòng review — 17/10/2026

**Kết luận: các lỗi chặn đã nêu ở hai vòng review trước đã được xử lý trong phạm vi kiểm tra này. Có thể chốt bộ eval cho bước G2 và chuyển sang xây retrieval/scorer ở G3. Chưa phát hiện lỗi chặn mới trong những thay đổi vừa rà.**

Đối tượng xác nhận là file eval có SHA-256 **`5a1b72038ae79755f5df7c53ed46447ac1516bb04e8e1330fd81cfc43fc0e252`**. Đây là xác nhận về bộ đề và các sửa đổi đã yêu cầu, không phải chứng nhận pháp lý độc lập cho mọi đáp án hay xác nhận điểm chất lượng mô hình.

## Kết quả kiểm chứng

| Nội dung | Kết quả |
|---|---|
| `pytest -q tests/test_evalset.py` | **31/31 pass** |
| `pytest -q` toàn dự án | **306/306 pass**, 16,29 giây |
| Build `--check` | Pass; build trong bộ nhớ khớp hoàn toàn file lưu |
| Thành phần và split | 270 câu; dev 30/test 240; 150 thường, 40 RQ3, 30 ngoài phạm vi, 50 biến thể |
| Sáu phép sửa sai vòng đầu | 6/6 bị bắt, thử theo key và có kiểm tra không phải thao tác rỗng |
| Ba phép sửa sai vòng hai | 3/3 bị bắt: 27/30 thành 26/30; ngày làm việc thành ngày; khung tiền phạt sai |
| Manifest | **18/18 mã băm khớp**: eval, split, nguồn và 15 file nháp |
| Ngưỡng đạt | `gp06` giữ nguyên `23/25`; `gp13` giữ nguyên `27/30` |
| Căn cứ bắt buộc | `gp01`: 5 nhóm, chỉ lấy một Điểm đạt 1/5, `all=false`; `ll05`: 8 nhóm, chỉ lấy câu dẫn đạt 1/8, `all=false` |
| Họ sự kiện | `gp17` và `sd34` cùng họ; 190 câu thường/RQ3 có 171 họ theo Khoản chính |
| 7 key cần thay | sd09, sd11, sd23, sd39, sd42, sd49, sd50 đã bỏ; sd53–sd59 đều có |
| Ngoại lệ `sd47` | Đáp án và căn cứ đã bổ sung điểm đ, e khoản 10 Điều 23 |

Các lệnh shell chạy với `py -3.13 -X utf8` để in tiếng Việt ổn định. Bằng chứng chi tiết: [checks-033039278247Z.json](checks-033039278247Z.json). Script tái lập: [verify.py](verify.py), luôn tạo file bằng chứng mới thay vì ghi đè. Hash đầu vào được kiểm lại sau khi chạy; dữ liệu eval, mã dự án và bằng chứng vòng trước không bị audit sửa.

## Đánh giá 7 cặp RQ3 mới

Đã đọc câu hỏi, đáp án mới/cũ và toàn bộ các record làm căn cứ của từng cặp. Các cặp mới cùng trả lời một câu hỏi bằng thời hạn khác nhau, thay cho suy luận từ việc bản cũ không nhắc đến một nội dung.

| Key | Nội dung kiểm tra | Cũ → mới trong căn cứ |
|---|---|---|
| sd53 | Chấp thuận biển quảng cáo trong phạm vi bảo vệ đường bộ | 7 → 5 ngày làm việc |
| sd54 | Thẩm định, phê duyệt phương án tổ chức giao thông cao tốc | 15 → 12 ngày làm việc |
| sd55 | Chấp thuận đấu nối tạm vào quốc lộ | 7 → 5 ngày làm việc |
| sd56 | Gia hạn lưu hành phương tiện ASEAN | 2 → 1 ngày làm việc |
| sd57 | Cấp giấy phép vận tải quốc tế Việt Nam–Lào | 2 → 1 ngày làm việc |
| sd58 | Cấp giấy phép liên vận GMS/sổ TAD | 2 → 1 ngày làm việc |
| sd59 | Cấp bản sao chứng nhận thu hồi đăng ký/biển số | Xác minh 30 ngày rồi cấp trong 2 ngày làm việc → không quá 2 ngày làm việc |

Mốc hiệu lực văn bản sửa đổi được đối chiếu với nguồn nhà nước: **NĐ 241/2026 từ 01/07/2026**, **NĐ 218/2026 từ 10/08/2026**; thông tin thủ tục của TT 62/2026 cũng xác nhận cấp bản sao không quá 2 ngày làm việc. [NĐ 241](https://chinhphu.vn/?classid=1&docid=218631&pageid=27160), [NĐ 218](https://vanban.chinhphu.vn/?classid=1&docid=218537&pageid=27160), [thủ tục thu hồi và cấp bản sao](https://congan.daklak.gov.vn/thu-tuc-hanh-chinh/detail-tthc/Thu-hoi-chung-nhan-dang-ky-xe-bien-so-xe-337/).

## Những giới hạn cần giữ khi làm thực nghiệm

- **Scorer retrieval chưa có.** Việc sửa dữ liệu nhóm và rubric đã xử lý vấn đề OR/AND; khi cài G3 vẫn phải test chunk đầy đủ, chunk chỉ có một Điểm và chunk chỉ có câu dẫn. Không dùng quan hệ cha/con trong mã địa chỉ làm bằng chứng rằng chunk thực sự chứa đủ nội dung.
- **`so_lieu` chưa có vai trò ngữ nghĩa.** Cặp giá trị–đơn vị và tỷ lệ đã đủ xử lý những lỗi cụ thể vừa nêu; chưa thay thế duyệt nội dung hoặc bảo đảm mọi cách diễn đạt tương đương đều được nhận ra. Không gắn nhãn thời hạn, ngưỡng và chế tài chỉ từ sự xuất hiện của cùng một con số.
- **RQ3 hiện nghiêng về thay đổi thời hạn thủ tục.** 13/40 câu lấy từ NĐ 218/2026. Đây là lựa chọn hợp lý để tránh đối chứng mơ hồ, nhưng kết quả cần mô tả đúng là trên tập thay đổi đã chọn, không suy rộng thành khả năng xử lý mọi loại sửa đổi pháp luật. Báo cáo riêng theo nhóm và dùng họ sự kiện khi bootstrap gộp kết quả.
- Bộ câu ngoài phạm vi khó hơn, duyệt bởi chuyên gia pháp lý và hỗ trợ hỏi ở nhiều ngày vẫn là các giới hạn đã công bố, không phải công việc đã hoàn thành trong lần sửa này.

**Hành động tiếp theo:** lưu/commit đúng phiên bản gắn hash trên, rồi triển khai G3 với test scorer phù hợp. Không cần tiếp tục thay thêm câu chỉ để tăng số test; chỉ sửa lại bộ đã chốt khi có lỗi cụ thể mới, và lưu phiên bản thay đổi để kết quả thực nghiệm có thể đối chiếu.
