# Sửa bộ eval theo review độc lập — 17/10/2026

Phản hồi [review của Codex](../eval-audit-2026-10-17/REPORT.md). Bộ sau sửa vẫn có tên `data/eval/eval_v1.jsonl` (bản trước chưa từng commit), gồm 270 câu: dev 30, test 240. Thành phần không đổi: 150 câu thường, 40 sửa đổi, 30 ngoài phạm vi, 50 biến thể.

**Lưu ý về id:** id trong bản này khác bản Codex đã review, vì đã thay câu RQ3. Đối chiếu bằng `key`. Ví dụ: TH135 cũ = `xp01`, TH138 = `xp04`, SD024 = `sd24`, TH010 = `bh10`, TH095 = `ll07`.

## 1. [P1] RQ3 sai mốc áp dụng — đã sửa

**Đồng ý với nguyên nhân Codex nêu:** kho `data-v1` chỉ lưu câu chữ, nên "phiên bản cũ còn hiệu lực trong kho" không có nghĩa "quy định cũ còn áp dụng thực tế". Tôi đã kiểm trong kho: Luật XLVPHC sửa đổi (khoản 2 Điều 37a, VBHN 63) giao Chính phủ quy định chi tiết thẩm quyền từng chức danh, và NĐ 189/2025 không có trong kho.

**12 câu đã bỏ** (key cũ):

| Key cũ | Lý do bỏ |
|---|---|
| sd01 | Ghế an toàn trẻ em: nghĩa vụ chỉ có từ 01/7/2026; nguồn tin về giai đoạn 1/7–14/8 còn mâu thuẫn |
| sd02–sd06 | Thẩm quyền chiến sĩ, Chủ tịch UBND xã, Trưởng Công an xã, Trưởng đồn, cấp sở: đã đổi từ 01/7/2025 theo NĐ 189/2025 |
| sd40 | Chủ tịch UBND cấp huyện: cấp huyện kết thúc từ 01/7/2025 |
| sd14, sd15 | Bộ quy định mẫu GPLX và sát hạch: Bộ Công an đã đảm nhận từ 01/3/2025 |
| sd17 | Camera khoang khách: bản mới nêu rõ thêm, không chứng minh bản cũ cho phép làm sai lệch |
| sd19, sd20 | Bản thân Codex không nêu. Đường huyện, cơ quan quản lý đường bộ thuộc Bộ GTVT và cấp huyện: cùng lỗi bộ máy đã đổi từ 2025 |

**12 câu thay thế:** đều là thay đổi về nội dung. Đã đọc cả hai phiên bản trong kho và kiểm không phụ thuộc thẩm quyền hay bộ máy.

| Id | Key | Thay đổi | Văn bản |
|---|---|---|---|
| SD029 | sd41 | Chuyển làn sai trên cao tốc không còn trong danh sách được tạm giữ phương tiện ngay (điểm a khoản 1 Điều 48) | NĐ 238/2026 |
| SD030 | sd42 | Hành vi mới: chở thiết bị hình dạng như công-ten-nơ vượt chiều dài, phạt 8–12 triệu, trừ 04 điểm | NĐ 238/2026 |
| SD031 | sd43 | Bỏ hành vi "không làm thủ tục thu hồi giấy chứng nhận kiểm định" khỏi điểm b khoản 7 Điều 32 | NĐ 238/2026 |
| SD032 | sd44 | Cấp Giấy phép liên vận ASEAN: 02 → 01 ngày làm việc | NĐ 218/2026 |
| SD033 | sd45 | Cấp Giấy phép GMS: 02 → 01 ngày làm việc | NĐ 218/2026 |
| SD034 | sd46 | Gia hạn lưu hành xe Lào, Campuchia: 02 → 01 ngày làm việc | NĐ 218/2026 |
| SD035 | sd47 | Không cấp lại phù hiệu trong 30 ngày kể từ ngày ký quyết định thu hồi | NĐ 218/2026 |
| SD036 | sd48 | Nộp hồ sơ kiểm tra phục hồi điểm tại Công an cấp xã | TT 105/2026 |
| SD037 | sd49 | Cơ sở đăng kiểm chứng nhận xe cải tạo | Luật 118/2025 |
| SD038 | sd50 | Dữ liệu điện tử chuyển quyền sở hữu có giá trị như bản giấy | TT 37/2026 |
| SD039 | sd51 | Thu hồi GPKD: mốc 30 ngày tính từ ngày ký quyết định (cũ: từ ngày nộp lại; 45 ngày nếu nộp chậm) | NĐ 218/2026 |
| SD040 | sd52 | Đường ống cấp nước ≤ 200 mm được làm thủ tục đồng thời với giấy phép thi công | NĐ 241/2026 |

**Câu RQ3 còn giữ cũng được sửa thêm:**
- `sd33` (SD022): bỏ tên "Sở Giao thông vận tải" khỏi đáp án cũ.
- `sd10` (SD004): bỏ số "10 giờ, 48 giờ" khỏi đáp án mới, vì đó là số của bản cũ.
- `sd09` (SD003), `sd42`: thêm trừ 04 điểm (điểm b khoản 13 Điều 21). Thiếu sót này do bộ kiểm tra mới phát hiện.

**Phần chưa làm được:** chưa có chuyên gia pháp lý duyệt 28 câu RQ3 giữ lại. Tôi đã đọc lại từng câu theo câu hỏi "văn bản nào ngoài kho có thể đã đổi trước", nhưng đây không phải chứng nhận pháp lý.

## 2. [P1] Bộ kiểm tra bỏ lọt lỗi — đã sửa

Sáu phép sửa sai của Codex nay đều bị bắt và là test cố định (`test_review_mutations_are_rejected`):

| Phép thử | Quy tắc bắt lỗi |
|---|---|
| Đảo min/max | `muc_phat_min ≤ muc_phat_max` |
| "Phạt 1 đồng" | Mọi số liệu có đơn vị trong đáp án phải có trong căn cứ hoặc câu hỏi; tiền nhận mọi cách viết (1 đồng, 7,5 triệu, 40 (bốn mươi) triệu đồng) |
| Tước 1–2 tháng | Cùng quy tắc số liệu, và `tuoc_gplx_thang` phải khớp luật |
| Điều 999 | Trích dẫn "điểm… khoản… Điều…" phải trỏ tới đơn vị có hiệu lực trong văn bản được dẫn |
| 99 ngày | Cùng quy tắc số liệu, áp dụng cả cho `dap_an_cu` |
| Gán trừ điểm của hành vi khác | Khoản "Thực hiện hành vi … bị trừ / bị tước" trong căn cứ phải liệt kê đúng hành vi đang hỏi; `diem_tru` phải bằng số luật quy định cho hành vi đó |

Bộ kiểm tra mới còn yêu cầu: nếu luật có trừ điểm hoặc tước GPLX cho hành vi thì đáp án phải nêu. Nhờ vậy đã tìm ra 3 thiếu sót thật và đã sửa:
- `xp09` (TH143): tịch thu xe còn kèm tước GPLX 22–24 tháng;
- `sd09`, `sd42`: thiếu trừ 04 điểm.

**Giới hạn:** bộ kiểm tra không kiểm được nghĩa của câu. Việc duyệt nghĩa vẫn làm bằng tay.

## 3. [P2] Biến thể đổi nghĩa — đã sửa

| Câu | Sửa |
|---|---|
| BT004 | Thêm nơi cư trú, chỉ hỏi lệ phí đăng ký kèm biển. Câu gốc `lp06` (TH085) cũng thêm nơi cư trú và căn cứ khoản 2 Điều 5 TT 155 |
| BT019 và câu gốc `ll07` (TH095) | Nêu rõ xe mô tô 110 cc |
| BT045 và câu gốc `bh10` (TH010) | Nêu rõ xe mô tô 125 cc; ghi chú trường hợp xe gắn máy |
| BT024, BT026 | Dùng "xe gắn máy" thay "50cc" |
| BT013 | Bỏ "khoảng" để mức quá tốc độ nằm chắc trong khung |

Cả 50 cặp đã đối chiếu theo: loại xe, người vi phạm, tuổi và chiều cao, địa bàn, thời điểm, mức độ, phạm vi câu hỏi. Kết quả: [bien_the_review.csv](bien_the_review.csv).

## 4. [P2] Cách chấm và nhãn — đã bổ sung

Trường mới (tự suy và tự kiểm):

| Trường | Nội dung |
|---|---|
| `nhom_can_cu` | Nhóm căn cứ theo Khoản |
| `trang_thai_diem_tru` | `co` / `khong_tru` / `khong_ap_dung`, thay cho ý nghĩa mơ hồ của `diem_tru = null` |
| `tuoc_gplx_thang` | Số tháng tước GPLX |
| `so_lieu` | Mọi số liệu trong đáp án |
| `dia_chi_chinh` | Địa chỉ căn cứ chính ở mức Khoản |
| `ho_cau` | Họ câu, dùng khi bootstrap |
| `trung_dev` | Câu test dùng chung căn cứ với dev |

README có mục **Cách chấm**: Recall any/all theo nhóm, mẫu số cho từng chỉ số, chấm RQ3, chấm từ chối, so biến thể với câu gốc.

## 5–6. Các điểm còn lại

| Điểm | Xử lý |
|---|---|
| Độ độc lập | Ghi `ho_cau` và `trung_dev` (13 câu test dùng chung căn cứ với dev); README yêu cầu báo cáo riêng |
| Tập câu ngoài phạm vi khó hơn (thiếu dữ kiện, tiền đề sai) | **Chưa làm**, ghi vào hạn chế |
| Số văn bản sửa đổi trong README | Đã sửa; nay là 11 giá trị sau khi thay câu |
| Split không ổn định | Đã đóng băng vào `data/eval/split_v1.json`; câu có key mới mặc định vào test; chú thích của `pick_dev` đã sửa cho đúng |
| Mốc 7 ngày cấp lại biển số | Đã có nguồn của UBND xã Yên Lãng (Hà Nội) như Codex dẫn |

## Kiểm tra

- `py -3.13 scripts/build_eval.py`: hợp lệ, 270 câu.
- `py -3.13 -m pytest -q tests/test_evalset.py`: 24 test qua.
- Toàn dự án: xem kết quả chạy ở cuối phiên sửa.
