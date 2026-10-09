# Việc chuyển sang giai đoạn sau (đợt làm sạch 2)

Nguồn: review `feat/legal-processing` và báo cáo hiện hành [`PROCESSING_REPORT.md`](../../../data/processed/PROCESSING_REPORT.md). Các mục dưới đây phân biệt việc đã xử lý với phần nguồn còn thiếu.

## Bắt buộc trước khi sinh dữ liệu hỏi đáp hoặc bộ eval

- **Ngoại lệ ngày hiệu lực:** đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`. `hl_ngoai_le` và `in_force_at` xử lý 22 dòng đã duyệt. TT 12 Phụ lục IV–VI được gia hạn cả đơn vị **kèm điều kiện** dù chỉ một phần mục/mẫu còn hiệu lực; truy hồi phải giữ điều kiện và không chọn tùy ý một bản trong ba cặp cũ/mới cùng sống có điều kiện.
- **Nguồn chữ còn thiếu:** QCVN 41 chỉ trích A, B, C, D, E, F, G, I, K; phụ lục M/N/O/P là ảnh, hình/biển báo chưa đủ. `tt_108_2026_bca:pl12` thiếu bảng chuyển đổi dù được gắn `ok`; `nd_39_2023:pl1` chỉ có dòng ban hành kèm theo. Cần khôi phục từ nguồn trước khi xem corpus là đầy đủ.

## Trước khi cắt đoạn và xây kho tra cứu

- **QCVN 41:** 12 phụ lục rỗng mục lục đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`. QCVN đã thành `qcvn_41_2024` với 84 Điều; phụ lục dài vẫn cần cắt đoạn. `nd_67_2023:pl7` khoảng 73 nghìn ký tự cũng cần chia nhỏ.
- **Dòng chữ ký/Nơi nhận:** đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`; số `ket_thuc` hiện 31.
- **Bảng lồng:** lỗi lặp chữ trong 5 file docx đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`.
- **OCR phụ lục:** đã xử lý một phần ở đợt làm sạch 2 (TT 108: 96 trang thử, 31 trang chọn; TT 36: 6/3; 97 dòng sửa tay), xem `PROCESSING_REPORT.md`. Còn phụ lục/chữ ảnh nêu trên, 21 đơn vị `chat_luong=kem`, và các nhãn `ok` nhưng thiếu nội dung. Cần kiểm tra thủ công theo ảnh nguồn. `tt_108_2026_bca:pl9` và `tt_12_2025_bca:pl10` có nội dung cần chia chunk theo quy định.

## Chất lượng dữ liệu và code

- **184 phiên bản giống hệt:** đã xử lý ở đợt làm sạch 2 bằng `noi_dung_doi=false`, xem `PROCESSING_REPORT.md`; bộ eval RQ3 nên xét trường này.
- `line_start` trên bản ghi sinh từ sửa đổi là vị trí trong đoạn trích, không phải văn bản đích.
- **Nhãn `k1)`:** đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`.
- `effective_dates_auto.csv` có thể lệch `effective_dates.csv` sau khi chạy lại; cần bước so sánh.
- Kiểm thử còn thiếu: `load_corrections` và CLI; `step_parse` nên duyệt theo manifest; `doc_id` trong sửa OCR không thuộc manifest nên báo lỗi.
- **Cache OCR SHA-256 + dpi và stderr Tesseract:** đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`.
- Phạm vi mô hình: mỗi dòng sửa đổi chỉ có một ngày hiệu lực; thay thế phụ lục/mẫu không áp được; trường hợp bổ sung khoản rồi sửa cùng ngày còn gác lại.
