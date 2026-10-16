# Bộ 600 câu hỏi sát hạch lái xe (bộ eval trắc nghiệm phụ)

Nguồn: `data/raw/gplx/gplx_600_2025__p1.pdf` (Cục CSGT, 2025; bản đăng lại của Công an TP Cần Thơ) và Công văn 2262/CSGT-P5 ngày 07/5/2025 (`cv_2262_2025_csgt__p1.pdf`, lấy từ thuvienphapluat.vn). Chạy: `py -3.13 scripts/process_gplx.py`, ghi `data/processed/gplx_600.jsonl`.

## Cách tách

- PDF có lớp chữ. Câu hỏi là dòng in đậm "Câu N." (câu 507 in "Câu 507:"); lựa chọn là dòng "1.", "2."…, kể cả khi nhiều lựa chọn in trên một dòng hoặc xếp lưới hai cột (câu 301, 302, 352).
- Đáp án: Công văn 2262 ghi "Phần đáp án đúng là phần gạch chân". Đáp án là lựa chọn có vạch kẻ ngang ngay dưới dòng; câu nào không có đúng một lựa chọn gạch chân thì `dap_an = null` và bị báo lỗi.
- Câu có hình: có ảnh (cạnh ≥ 20 pt) nằm trong vùng từ đầu câu đến đầu câu kế tiếp.
- Nhãn phụ từ ba phụ lục của Công văn 2262: `diem_liet` (60 câu), `hang_A1_A` (250 câu), `hang_B1` (300 câu). Chương theo khoảng số câu trong Công văn.

Trường mỗi dòng: `so_cau, chuong, cau_hoi, lua_chon, dap_an (1-based), co_hinh, diem_liet, hang_A1_A, hang_B1`.

## Kiểm tra

Đủ 600 câu đánh số liên tục 1–600; mỗi câu đúng một đáp án gạch chân; 2–4 lựa chọn mỗi câu; số câu theo chương và kích thước ba danh sách khớp Công văn. Đối chiếu tay với ảnh trang (ví dụ câu 17–22, 215–217) khớp.

| Chương | Nội dung | Số câu | Có hình | Thuần chữ |
|---|---|---:|---:|---:|
| I | Quy định chung, quy tắc giao thông | 180 | 2 | 178 |
| II | Văn hóa giao thông, đạo đức người lái xe | 25 | 0 | 25 |
| III | Kỹ thuật lái xe | 58 | 5 | 53 |
| IV | Cấu tạo và sửa chữa | 37 | 11 | 26 |
| V | Báo hiệu đường bộ | 185 | 185 | 0 |
| VI | Sa hình, xử lý tình huống | 115 | 115 | 0 |
| **Cộng** | | **600** | **318** | **282** |

Bộ eval trắc nghiệm phụ = **282 câu thuần chữ** (`co_hinh = false`), gồm cả 60 câu điểm liệt. Số lựa chọn: 2 lựa chọn 108 câu, 3 lựa chọn 326 câu, 4 lựa chọn 166 câu (tính trên cả 600 câu).

## Việc còn lại

## Đối chiếu đáp án với luật tại 01/10/2026 (2026-10-17)

Bộ câu áp dụng từ 01/6/2025 và vẫn là bộ hiện hành (TT 108/2026 chỉ đổi nội dung sát hạch từ 01/3/2027). Đáp án chỉ có thể lệch luật nếu quy định làm căn cứ bị sửa sau 6/2025, nên đã lập danh sách điều bị sửa (Luật 118/2025 sửa Luật 36: Điều 9, 10, 11, 12, 27, 35, 41, 42, 49, 52, 53, 57, 62, 64…; NĐ 238/2026 sửa NĐ 168) rồi rà mọi câu thuần chữ liên quan (xe ưu tiên, chở trẻ em, thiết bị giám sát hành trình, thời gian lái xe, hạng và độ tuổi GPLX, điểm GPLX, thu hồi GPLX, mũ bảo hiểm, nồng độ cồn).

- **Câu 172** ("thời gian làm việc của người lái xe ô tô kinh doanh vận tải trong một ngày", đáp án "không quá 10 giờ"): căn cứ là khoản 1 Điều 64 Luật 36; từ 01/7/2026 Luật 118 bỏ giới hạn 10 giờ/ngày, 48 giờ/tuần và chuyển sang Bộ luật Lao động. Gắn cờ trong `data/gplx_flags.csv`, trường `can_xem_phap_ly`; **loại khỏi bộ eval**.
- Các câu khác trong nhóm trên vẫn đúng: 171 (lái liên tục không quá 4 giờ vẫn giữ), 42 (chở trẻ em: luật mới chỉ thêm ngoại lệ xe kinh doanh vận tải hành khách), 94–98 và 112 (danh sách xe ưu tiên không đổi, chỉ đổi màu đèn của xe quân sự), 143 (xe kinh doanh vận tải vẫn phải lắp thiết bị giám sát hành trình), 118–135 (độ tuổi, hạng GPLX), 139–141 (thu hồi, phục hồi điểm), 75 (mũ bảo hiểm).

Bộ eval trắc nghiệm phụ dùng được tại 01/10/2026: **281 câu** (282 câu thuần chữ trừ câu 172).

## Việc còn lại

- Câu thuần chữ chương IV hỏi về cấu tạo xe, không có căn cứ trong kho văn bản luật; khi báo cáo nên tách kết quả theo chương.
