# Đối chiếu chữ PDF với dữ liệu trích Word — 16/10/2026

Đã chạy trên bản làm việc tại commit `891eb675d1b3daa71db661f16421556b669db80e`. Không dùng OCR. Không sửa dữ liệu hoặc pipeline. Kết quả: **chưa thể kết luận dữ liệu sạch hoàn toàn**; phần Điều gần như khớp, phụ lục còn lỗi cấu trúc, nhãn kích thước và nhãn mục.

## Phạm vi và số liệu

| Chỉ tiêu | Kết quả |
|---|---:|
| Văn bản đối chiếu độc lập được | 28/33 |
| Điều ghép được và so từng token | 1.454 |
| Điều khớp sau chuẩn hóa | 1440/1.454 |
| Phần phụ lục ghép được | 121 |
| Phụ lục khớp sau chuẩn hóa | 27/121 |
| Phần đầu văn bản | 28 |
| Tiêu đề phía Word không tìm thấy đối ứng PDF | 0 |
| Khối chênh lệch máy phát hiện | 2,257 |
| Trang PDF đã render và xem trực tiếp | 24 |
| Trang kiểm bảng bằng hình học PDF | 270 |
| Bảng nhận dạng bằng đường kẻ/toạ độ | 318 |
| Cặp hàng được ghép | 2.271 |
| Cặp còn lệch số/ký hiệu ở lượt ghép bảng ban đầu | 47 |
| Hàng ghép độ tin cậy thấp, lưu riêng | 124 |

Các số “khớp” là khớp token sau chuẩn hóa, **không phải tỷ lệ đúng pháp lý**. 2,257 khối lệch không tương đương 2,257 lỗi: bảng nhiều cột, tiêu đề lặp, nhãn mục và dấu ký số tạo nhiều khối lệch. Ảnh hình học không được OCR; chỉ mở ảnh để kiểm bằng mắt.

## Cách chạy

1. Đọc lớp chữ PDF kèm toạ độ trang; đối chiếu với `data/processed/documents/*.txt` được tạo từ Word, dùng đơn vị trong corpus để định vị Điều/phụ lục.
2. Chuẩn hóa NFC, khoảng trắng, ngắt dòng, dấu gạch ngang Unicode và ligature; không phân biệt hoa/thường. Tách token từ, số, mã có dấu chấm/phẩy/gạch và ký hiệu `≤ ≥ < > Ø % ‰ ± × = + °`. Phần lớn dấu câu không nằm trong phép so này; đây không phải phép kiểm đồng nhất từng byte/ký tự.
3. Bỏ header Công báo, số trang lề, chữ trắng ẩn, khối ký số và thông tin xuất bản nhận diện được. Lưu riêng mọi dòng bị bỏ. Với VBHN, tách chú thích cỡ chữ nhỏ và số mũ đánh dấu chú thích; giữ số mũ đơn vị. Chú thích vẫn được lưu làm bằng chứng, **chưa kiểm nội dung chú thích**.
4. Ghép từng Điều và từng phần phụ lục bằng tiêu đề; so SequenceMatcher và đếm chênh tập số/ký hiệu. Không coi tập số bằng nhau là bằng chứng số nằm đúng hàng.
5. Chạy lượt bổ sung `find_tables()` theo toạ độ PDF; ghép hàng có khóa. Lượt này chỉ xét nhóm phụ lục nội dung có bảng, không phủ mọi bảng/hình. Cùng mã hàng lặp ở nhiều bảng có thể ghép nhầm; hàng nối có thể bị cắt. Giữ nguyên kết quả gốc và lưu phân loại sau xem xét riêng.
6. Render bằng Poppler và xem trực tiếp các trang quan trọng; danh sách trong `render_manifest.json`. Các bộ lọc không nhận diện được hết nhiễu; phần chưa duyệt có trạng thái rõ trong `section_triage.csv`.

## Phát hiện đã xác nhận

### F01 — P2 — Ô đầu trống bị bỏ ở hàng tiếp nối, làm nội dung cột Yêu cầu đạt được trượt sang cột Các bước thực hiện.

PDF p1 trang 58: yêu cầu 6–8 nằm cột giữa, lỗi 7–11 nằm cột phải; TXT dòng 791 chỉ còn hai ô. Các con số còn đủ, quan hệ cột bị mất.

Dữ liệu: [data/processed/documents/tt_12_2025_bca.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/tt_12_2025_bca.txt:791). [Ảnh PDF đã xem](renders/tt_12_2025_bca__p1-page-58.png). Phạm vi: `tt_12_2025_bca:pl4`.

### F02 — P2 — Hai nhãn kích thước riêng 64,52 và 10,02 bị nối thành 64,5210,02.

Ảnh PDF p5 trang 38 có ba nhãn riêng 10,02 / 64,52 / 3,57. TXT dòng 2450 ghi 3,57 64,5210,02.

Dữ liệu: [data/processed/documents/qcvn_41_2024.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/qcvn_41_2024.txt:2450). [Ảnh PDF đã xem](renders/tt_51_2024_bgtvt_qcvn41__p5-page-38.png). Phạm vi: `qcvn_41_2024:pl9`.

### F03 — P2 — Kích thước ngang và dọc của mẫu đăng ký xe bị nối thành 53.9885.6.

PDF p1 trang 44 thể hiện ngang 85.6 mm, dọc 53.98 mm; TXT dòng 489 ghi 53.9885.6 mm. Đoạn ghi chú phía sau vẫn có kích thước đúng.

Dữ liệu: [data/processed/documents/tt_79_2024_bca.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/tt_79_2024_bca.txt:489). [Ảnh PDF đã xem](renders/tt_79_2024_bca__p1-page-44.png). Phạm vi: `tt_79_2024_bca:pl1`.

### F04 — P2 — Nhiều số đo và ký hiệu nằm trong hình minh họa chưa có trong văn bản trích xuất.

Mẫu đã xem: PDF p5 trang 27, Hình G.73, có nhiều nhãn 300, 320, 45°… nhưng TXT chỉ giữ phần lời và tên hình. Có chữ thật trong PDF; các nhãn trong Word nằm trong hình. Chưa kiểm tay từng nhãn của toàn phụ lục.

Dữ liệu: [data/processed/documents/qcvn_41_2024.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/qcvn_41_2024.txt). [Ảnh PDF đã xem](renders/tt_51_2024_bgtvt_qcvn41__p5-page-27.png). Phạm vi: `qcvn_41_2024:pl7`.

### F05 — P2 — Nhãn mục của dữ liệu Word khác PDF, có thể làm dẫn chiếu sai.

PDF p3 trang 30: phần xe mô tô bắt đầu mục 2, 2.1…; dữ liệu bắt đầu 1, 1.1…. Chỉ xác nhận hai định dạng khác nhau, chưa quy lỗi cho bộ trích hay tự sửa theo suy đoán.

Dữ liệu: [data/processed/documents/tt_79_2024_bca.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/tt_79_2024_bca.txt). [Ảnh PDF đã xem](renders/tt_79_2024_bca__p3-page-30.png). Phạm vi: `tt_79_2024_bca:pl20`.

### F06 — P3 — Nhãn mục Word khác nhãn in trong PDF; bản PDF cũng có thứ tự bất thường.

PDF p3 trang 29 in tiêu đề 5 rồi 4.1 và 4.1.1.5; dữ liệu có 1 và 5. Không tự coi nhãn in bất thường là nhãn phải sửa lại theo logic.

Dữ liệu: [data/processed/documents/tt_12_2025_bca.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/tt_12_2025_bca.txt). [Ảnh PDF đã xem](renders/tt_12_2025_bca__p3-page-29.png). Phạm vi: `tt_12_2025_bca:pl7`.

### F07 — P3 — Từ bộ bị tách thành b ộ trong dữ liệu.

PDF p1 trang 24 in đường bộ; TXT dòng 288 ghi đường b ộ. Không làm thay đổi con số.

Dữ liệu: [data/processed/documents/nd_165_2024.txt](D:/Dowload/1.Chuyên Ngành/kì 7/DAT301_NEW/thamkhao/du_an_hien_tai/data/processed/documents/nd_165_2024.txt:288). [Ảnh PDF đã xem](renders/nd_165_2024__p1-page-24.png). Phạm vi: `nd_165_2024:d22`.

## Những lệch quan trọng đã loại khỏi danh sách lỗi số liệu

- TT 38 Điều 5: mã QCVN 07-4:2023/BXD bị ngắt dòng ở PDF; ảnh xác nhận cùng mã. Điều 6: bảng tốc độ đọc khác thứ tự cột; mẫu đã xem giữ đúng giá trị.
- NĐ 158 Điều 12: bảng thời gian 02, 16, 02, 02, 02, tổng 24 giữ đủ; khác thứ tự đọc.
- NĐ 220 phụ lục: 5 cặp hàng tưởng lệch mức phí thực ra ghép nhầm hai bảng dùng lại cùng mã. Ví dụ mã 2.4.2 có hàng đúng 3,0/M và hàng khác 2,3/N; dữ liệu có cả hai. Đã xem các trang 12,14,15,16. Một số hàng bị bộ đọc hình học PDF lấy thiếu phần sau; không dùng làm bằng chứng Word thừa số.
- NĐ 220 trang 32: số 4 hiện trên ảnh nhưng lớp chữ PDF không trích được. Không coi số 4 trong Word là thừa.
- NĐ 67: chênh số lần % và ‰ chủ yếu từ tiêu đề bảng lặp qua trang. 825 cặp hàng ở phụ lục tỷ lệ tổn thương đã ghép được, không có chênh bộ số/ký hiệu trong các cặp này; điều đó không chứng nhận mọi hàng của phụ lục. Kết quả gốc vẫn còn chênh thứ tự đọc.
- VBHN BLHS Điều 358: native PDF nối hai từ ở vị trí chú thích; ảnh trang 58 cho thấy Word đặt khoảng trắng hợp lý. Chữ ký, phần bìa và tiền tố quy chuẩn cũng tạo chênh ở một số Điều cuối.

Trong 14 phần Điều không khớp token hoàn toàn, không xác nhận trường hợp thay sai con số quy định ở lượt này. Một phần Điều cuối bao gồm khối chữ ký. Chi tiết từng phần ở `section_triage.csv`; không suy rộng thành bảo đảm mọi số liệu trong toàn bộ corpus đều đúng.

## Phần chưa đủ cơ sở kết luận

| Văn bản | Trạng thái trong lượt này |
|---|---|
| TT 108/2026/BCA | PDF scan; không chạy OCR, chưa được đối chiếu độc lập bằng chữ. |
| TT 155/2025/BTC | PDF scan; không chạy OCR, chưa được đối chiếu độc lập bằng chữ. |
| TT 36/2024/BYT | Dữ liệu TXT/đối chiếu scan; loại khỏi phép so chữ độc lập này. |
| BLDS 2015 | Dữ liệu từ chính PDF; tự so không tạo đối chứng độc lập. Chưa làm lượt lấy mẫu tay mới. |
| TT 30/2026/BXD | Dữ liệu từ chính PDF; chưa làm lượt lấy mẫu tay mới. |

Các phụ lục chỉ có ảnh như NĐ 39 hoặc phần QCVN M–P không có chữ để phép so phát hiện thiếu. Việc tiêu đề ghép đủ và chữ còn lại khớp không chứng minh những phần ảnh đã đầy đủ.

Chưa duyệt mắt từng khối khác trong toàn bộ mẫu biểu, từng nhãn kích thước hoặc từng ô bảng. 124 hàng ghép tin cậy thấp và các ô PDF bị đọc cắt vẫn ở hàng đợi; phần phụ lục có cùng bộ số vẫn có thể sai vị trí. Không tự duyệt bảng thay thế phụ lục và không đóng phụ lục cũ trong lượt này.

## Tệp để kiểm tra lại

- `compare.py`: chạy lại toàn bộ phép so chữ; `check_tables.py`: lượt bảng theo toạ độ; `finish_review.py`: tạo phân loại và báo cáo.
- `coverage.csv`: đủ 33 văn bản, nêu rõ 28 đã so và 5 bị loại.
- `differences.csv` / `differences.json`: mọi khối thiếu, thừa, khác với ngữ cảnh và trang PDF; JSON có toạ độ.
- `section_triage.csv`: trạng thái xét từng phần còn lệch, không đánh dấu đã duyệt toàn phần chỉ vì kiểm một mẫu.
- `reviewed_findings.csv`: 7 nhóm phát hiện có bằng chứng; đây không phải tổng số lỗi đơn lẻ.
- `table_row_pairs.json`, `table_unmatched_rows.json`, `table_numeric_triage.csv`: các cặp bảng, hàng chưa ghép chắc và xử lý cảnh báo số.
- `pdf_footnotes.json`, `removed_pdf_lines.json`, `pdf_symbol_normalizations.json`: các thao tác lọc và chuẩn hóa để kiểm toán lại.
- `input_hashes.json` / `review_summary.json`: dấu vết đầu vào, commit, số liệu và kiểm tra dữ liệu không thay đổi.

## Bao phủ theo văn bản

| Văn bản | Điều khớp / đã so | Phụ lục khớp / đã so | Trạng thái |
|---|---:|---:|---|
| blds_2015 | 0/0 | 0/0 | excluded |
| luat_118_2025 | 11/11 | 0/0 | compared |
| luat_35_2024 | 85/86 | 0/0 | compared |
| luat_36_2024 | 89/89 | 0/0 | compared |
| nd_10_2022 | 13/14 | 0/0 | compared |
| nd_138_2021 | 19/19 | 0/0 | compared |
| nd_158_2024 | 77/78 | 3/13 | compared |
| nd_160_2024 | 42/42 | 5/21 | compared |
| nd_165_2024 | 69/70 | 1/10 | compared |
| nd_168_2024 | 55/55 | 0/0 | compared |
| nd_175_2025 | 2/2 | 0/0 | compared |
| nd_218_2026 | 39/39 | 0/7 | compared |
| nd_220_2026 | 10/10 | 0/2 | compared |
| nd_238_2026 | 20/21 | 0/0 | compared |
| nd_241_2026 | 28/28 | 2/7 | compared |
| nd_336_2025 | 28/28 | 0/0 | compared |
| nd_39_2023 | 25/25 | 1/1 | compared |
| nd_51_2025 | 2/2 | 0/0 | compared |
| nd_67_2023 | 78/78 | 1/11 | compared |
| qcvn_41_2024 | 81/84 | 4/9 | compared |
| tt_108_2026_bca | 0/0 | 0/0 | excluded |
| tt_12_2025_bca | 39/39 | 4/17 | compared |
| tt_155_2025_btc | 0/0 | 0/0 | excluded |
| tt_30_2026_bxd | 0/0 | 0/0 | excluded |
| tt_36_2024_byt | 0/0 | 0/0 | excluded |
| tt_37_2026_bca | 8/8 | 0/1 | compared |
| tt_38_2024_bgtvt | 10/12 | 0/0 | compared |
| tt_51_2024_bgtvt_qcvn41 | 1/2 | 0/0 | compared |
| tt_51_2025_bca | 3/3 | 0/1 | compared |
| tt_65_2024_bca | 11/11 | 0/1 | compared |
| tt_79_2024_bca | 40/40 | 6/20 | compared |
| vbhn_135_2025_blhs | 408/410 | 0/0 | compared |
| vbhn_63_2025_xlvphc | 147/148 | 0/0 | compared |

Kiểm tra SHA-256 sau khi hoàn tất: **0 tệp data/src thay đổi** so với đầu lượt chạy. Báo cáo chỉ xác nhận trạng thái trong workspace, không xác minh tính cập nhật/hiệu lực của văn bản trên Internet.
