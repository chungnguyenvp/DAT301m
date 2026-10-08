# Việc chuyển sang giai đoạn sau (từ kế hoạch xử lý văn bản luật)

Nguồn: review từng task và review toàn nhánh của `feat/legal-processing` (kế hoạch `docs/superpowers/plans/2026-10-08-legal-text-processing.md`). Kết quả xử lý: `data/processed/PROCESSING_REPORT.md`.

## Bắt buộc trước khi sinh dữ liệu hỏi đáp hoặc bộ eval
- **Ngoại lệ về ngày hiệu lực chưa có cờ trong `legal_units_versioned.jsonl`.** Tại 2026-10-01 các đơn vị sau bị coi sai trạng thái:
  - Đang được coi là có hiệu lực nhưng thực ra chưa: NĐ 238/2026 Điều 18 hoãn áp dụng theo hạng xe đến 2028 (`nd_168_2024:d20:k5:l`, `d21:k3:b`, `d32:k9a`); Luật 36/2024 Điều 35 khoản 2 (mốc 2028, 2029); TT 108/2026 Điều 41 khoản 2–5 (mốc 2027, 2028).
  - Đang được coi là hết hiệu lực nhưng thực ra còn đến 28/02/2027: một phần TT 12/2025/TT-BCA (Điều 4 khoản 1–3, Phụ lục II, III và một phần Phụ lục IV), do TT 108/2026 thay thế cả văn bản từ 01/7/2026.
  - Việc cần làm: thêm trường máy đọc được (ví dụ `hl_canh_bao` hoặc danh sách mốc ngoại lệ) cho các bản ghi này và dùng nó khi lọc theo thời điểm.

## Trước khi cắt đoạn và xây kho tra cứu
- QCVN 41 (`tt_51_2024_bgtvt_qcvn41`): phần thân nằm trong một đơn vị phụ lục khoảng 125 nghìn ký tự (`pl13`), cùng 12 đơn vị phụ lục rỗng (mục lục). Cần lọc và chia nhỏ.
- `nd_67_2023:pl7` khoảng 73 nghìn ký tự: chia nhỏ.
- Dòng chữ ký (`TM. CHÍNH PHỦ`, `KT. BỘ TRƯỞNG`, `CHỦ TỊCH QUỐC HỘI`…) lọt vào đơn vị cuối của nhiều văn bản (ví dụ `nd_168_2024:d55`, `nd_238_2026:d21`, `nd_218_2026:d39:k5:d`); 30/32 văn bản không có đơn vị `ket_thuc`. Nên coi các dòng này là phần kết.
- Bảng lồng nhau trong 5 file docx bị lặp chữ khi trích (`extract.docx_lines`).
- Phụ lục của `tt_108_2026_bca` và `tt_36_2024_byt` OCR kém: cần OCR lại hoặc chép tay.

## Chất lượng dữ liệu và code (không chặn)
- 184 phiên bản mới có nội dung giống hệt phiên bản cũ (sinh ra khi chép lại cả khoản); bộ eval luật sửa đổi (RQ3) nên so sánh nội dung chứ không chỉ dựa vào `source_doc_id`.
- `line_start` trên bản ghi sinh ra từ sửa đổi là vị trí trong đoạn trích dẫn, không phải trong văn bản đích.
- Nhãn điểm dạng `k1)` chưa được nhận diện (đang được ghép vào điểm k): mở rộng mẫu điểm thành `[a-zđ]{1,2}\d?`.
- `effective_dates_auto.csv` (đề xuất tự động) có thể lệch khỏi `effective_dates.csv` (đã duyệt) nếu chạy lại bước `effective`; nên có bước so sánh.
- Kiểm thử còn thiếu: `load_corrections` và các bước CLI; `step_parse` nên duyệt theo `doc_id` trong manifest thay vì mọi file `.txt`; dòng sửa OCR có `doc_id` không có trong manifest nên báo lỗi.
- Cache OCR chỉ theo số trang: nên gắn với sha256 file và dpi; hiện lỗi Tesseract không kèm stderr.
- Phạm vi mô hình hóa: mỗi dòng sửa đổi chỉ có một ngày hiệu lực; thay thế Phụ lục/Mẫu không áp được (không phải đơn vị có địa chỉ); trường hợp biên (đã gác lại) bổ sung khoản mới kèm điểm con và sửa chính khoản đó trong cùng ngày.
