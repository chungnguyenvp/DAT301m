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

- **Đối chiếu đáp án với luật tại ngày chốt 01/10/2026.** Bộ câu áp dụng từ 01/6/2025 theo TT 12/2025; sau đó TT 108/2026, Luật 118/2025, NĐ 238/2026 có hiệu lực. Câu nêu con số hoặc quy định đã sửa (mức phạt, tốc độ, điểm GPLX, hạng xe) cần rà và gắn nhãn `khop_luat_hien_hanh` trước khi dùng để chấm.
- Câu thuần chữ chương IV hỏi về cấu tạo xe, không có căn cứ trong kho văn bản luật; khi báo cáo nên tách kết quả theo chương.
