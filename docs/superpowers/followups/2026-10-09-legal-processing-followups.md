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
- **Tham chiếu điểm có chữ số trong sửa đổi tương lai:** `amendments.py` còn mẫu địa chỉ điểm chỉ nhận chữ; mở rộng để chỉ dẫn nhắm vào điểm `k1` hiện có và thêm test phân giải địa chỉ. Việc bổ sung `k1` trong tập đã duyệt hiện nay vẫn đúng.
- **Bổ sung khoản có dấu chấm trong QCVN:** kiểm tra câu dẫn của `apply.py` chưa nhận dạng `3.2.` theo cấu hình văn bản đích; thêm mẫu riêng theo đích và test trước khi xử lý sửa đổi loại này.
- **Phát hiện phần kết quá sớm:** chữ ký giống mẫu ở giữa văn bản có thể làm Điều sau bị đưa vào `ket_thuc`; ràng buộc với Điều cuối và thêm test hồi quy cho nguồn tương lai.
- **Word và cấu trúc bảng tương lai:** extractor chưa bảo toàn nội dung bọc trong `w:sdt`/`w:customXml` hoặc ranh giới mạnh giữa bảng lồng và bảng ngoài. Kiểm tra corpus hiện tại không thấy mất chữ do wrapper; bổ sung xử lý hoặc từ chối rõ nguồn có wrapper khi mở rộng đầu vào.
- **Hồi quy còn nên ghi thành test lâu dài:** khối trích dẫn nhiều dòng có dòng chữ ký đứng riêng, bảng gộp ô theo chiều dọc và tối đa một `ket_thuc` mỗi văn bản. Các phép kiểm tra độc lập với corpus hiện tại đều qua.
- `effective_dates_auto.csv` có thể lệch `effective_dates.csv` sau khi chạy lại; cần bước so sánh.
- Kiểm thử còn thiếu: `load_corrections` và CLI; `step_parse` nên duyệt theo manifest; `doc_id` trong sửa OCR không thuộc manifest nên báo lỗi.
- **Cache OCR SHA-256 + dpi và stderr Tesseract:** đã xử lý ở đợt làm sạch 2, xem `PROCESSING_REPORT.md`.
- Phạm vi mô hình: mỗi dòng sửa đổi chỉ có một ngày hiệu lực; thay thế phụ lục/mẫu không áp được; trường hợp bổ sung khoản rồi sửa cùng ngày còn gác lại.

## Phát hiện ngày 2026-10-16 (đổi nguồn chữ TT 108, TT 155)

- **Đã xử lý:** TT 108 và TT 155 đọc bản Word từ Công báo thay OCR; `tt_108_2026_bca:pl12` nay có bảng chuyển đổi; hết lỗi dấu OCR ở hai văn bản này. Xem mục 1a `PROCESSING_REPORT.md`.
- **Đã xử lý:** nhãn đánh số tự động của Word được dựng từ `numbering.xml` (mục 1b `PROCESSING_REPORT.md`); TT 38 từ 18 lên 57 đơn vị. Còn lệch nhãn trong phụ lục TT 12, TT 79, TT 108 giữa tệp Word và bản in, không ảnh hưởng cấu trúc Khoản/Điểm.
- **Đã xử lý:** TT 36 đọc bản chữ thuần (thuvienphapluat.vn, đã đối chiếu với PDF chính thức); bảng Phụ lục I dựng lại có nhãn Nhóm 1/2/3 theo ảnh PDF. Không còn văn bản nào OCR. Nếu sau này có bản từ nguồn nhà nước (Công báo, vbpl.vn) thì nên thay file chữ này.
- **Đã xử lý:** bảng phí TT 155 viết lại thành câu có tên khu vực ở từng dòng (mục 1c `PROCESSING_REPORT.md`); 19 đơn vị `chat_luong=kem` đã rà tay, đều là báo nhầm của chỉ số (tiếng Anh trên mẫu song ngữ, tên nước, đơn vị đo).

