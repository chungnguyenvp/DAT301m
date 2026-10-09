# Duyệt phân loại phụ lục — Task 6, ngày 09/10/2026

Trạng thái: **đã được người dùng duyệt và áp dụng 7 dòng ghi đè** ngày 09/10/2026. Đầu ra hiện có **107 mẫu biểu / 51 nội dung**. Các bảng phía dưới lưu kết quả phân loại tự động trước khi duyệt để đối chiếu.

Đã giữ đủ **18.790 bản ghi**, không thay đổi trường cũ so với commit `a163a01`. Review độc lập đạt; 170 test qua. Hai lần chạy assemble → parse → effective → amendments → apply cho cùng SHA256 trên 43 file đầu ra.

Phân loại hiện tại: **158 đơn vị phụ lục**, gồm **104 mẫu biểu**, **54 nội dung**. Đếm theo `unit_id`, không khẳng định có 158 phụ lục khác nhau trong nguồn: một phụ lục có thể được trích thành nhiều đơn vị. Có **21 bản ghi** bị gắn chất lượng `kem`, trong đó **18 phụ lục**.

Nhãn phục vụ bước chọn dữ liệu về sau; hiện không xóa hay loại bản ghi nào. `ok` chỉ nghĩa là không vượt ngưỡng nhiễu âm tiết (10%, ít nhất 50 từ); không chứng nhận đúng nội dung, số liệu, dấu tiếng Việt, cấu trúc bảng hay đủ hình ảnh. Tiếng Anh trong mẫu song ngữ có thể bị gắn `kem`.

## Đề xuất 7 dòng ghi đè

Đề xuất giữ các phân loại khác và áp dụng 7 dòng dưới đây sau khi được duyệt. Khi đó tổng sẽ là **107 mẫu biểu / 51 nội dung**, không đổi số bản ghi.

| unit_id | Hiện tại → đề xuất | Căn cứ đọc nội dung |
|---|---|---|
| `nd_67_2023:pl9` (Phụ lục VIII) | noi_dung → **mau_bieu** | Đơn đề nghị thành lập Hội đồng quản lý Quỹ; có trường để điền và chữ ký. |
| `nd_67_2023:pl10` (Phụ lục IX) | noi_dung → **mau_bieu** | Đơn đề nghị thay đổi thành viên Hội đồng quản lý Quỹ; có trường để điền và chữ ký. |
| `tt_108_2026_bca:pl9` | mau_bieu → **noi_dung** | Biểu mẫu GPLX kèm quy cách phôi, kích thước, màu chữ và cách in. |
| `tt_108_2026_bca:pl13` | noi_dung → **mau_bieu** | Các mẫu báo cáo kết quả sát hạch; ảnh PDF trang 131–133 có ô trống, ngày tháng và chữ ký. |
| `tt_12_2025_bca:pl10` | mau_bieu → **noi_dung** | Biểu mẫu GPLX kèm quy cách phôi và cách in; giữ để tra cứu phiên bản lịch sử. |
| `tt_12_2025_bca:pl14` | noi_dung → **mau_bieu** | Các trang mẫu giấy phép lái xe quốc tế (IDP), cùng mô tả vị trí thông tin. |
| `tt_30_2026_bxd:pl13` | noi_dung → **mau_bieu** | Mẫu thông báo sai khác dữ liệu xe; có chỗ điền, nơi nhận, ký tên và hướng dẫn ghi. |

Bản CSV đề xuất: [2026-10-09-annex-overrides-proposed.csv](2026-10-09-annex-overrides-proposed.csv). Bảy dòng đã được đưa vào `data/annex_type_overrides.csv`. Hai lượt chạy pipeline sau ghi đè cho SHA256 giống nhau trên 43 file, 170 test qua. CLI nạp file ghi đè trong bước `apply`.

Phụ lục vừa có mẫu vừa có quy định được giữ là `noi_dung` để tránh bỏ mất quy định; cần tách đoạn khi xây kho tra cứu. Task 6 chưa tạo dữ liệu fine-tune.

## Khoảng trống dữ liệu cần xử lý trước khi sinh câu hỏi

| Đơn vị | Tình trạng quan sát được | Hành động tiếp theo |
|---|---|---|
| `tt_108_2026_bca:pl12` | Chỉ còn khoảng 138 ký tự; không có các hàng của bảng chuyển đổi GPLX quốc tế. Nhãn hiện tại vẫn là `ok`. | Giữ loại nội dung; phục hồi bảng và đối chiếu PDF trước khi sử dụng. Không sinh QA từ đoạn thiếu này. |
| `nd_39_2023:pl1` | Đầu ra chỉ có dòng ban hành kèm, chưa có nội dung phụ lục. | Đối chiếu nguồn để xác định phần thiếu, trích lại; chưa dùng để sinh QA. |
| QCVN 41 | Đã tách đủ 84 Điều; phụ lục trích được A, B, C, D, E, F, G, I, K. Chưa có M/N/O/P dạng ảnh và chưa bảo toàn đầy đủ hình minh họa. | Ghi rõ phạm vi; bổ sung xử lý ảnh nếu cần câu hỏi về phần thiếu. |

Đây là các khoảng trống được phát hiện, không phải kết quả kiểm chứng toàn bộ corpus. Task 5 đã OCR lại 102 trang và chọn 34 trang tốt hơn; hoàn thành các bước này không đồng nghĩa dữ liệu sạch hoàn toàn.

## Số lượng trước khi duyệt theo văn bản

| doc_id | Mẫu biểu | Nội dung | Tổng |
|---|---:|---:|---:|
| `nd_158_2024` | 13 | 0 | 13 |
| `nd_160_2024` | 20 | 1 | 21 |
| `nd_165_2024` | 6 | 4 | 10 |
| `nd_218_2026` | 7 | 0 | 7 |
| `nd_220_2026` | 1 | 1 | 2 |
| `nd_241_2026` | 5 | 2 | 7 |
| `nd_39_2023` | 0 | 1 | 1 |
| `nd_67_2023` | 1 | 10 | 11 |
| `qcvn_41_2024` | 0 | 9 | 9 |
| `tt_108_2026_bca` | 6 | 8 | 14 |
| `tt_12_2025_bca` | 9 | 8 | 17 |
| `tt_155_2025_btc` | 0 | 1 | 1 |
| `tt_30_2026_bxd` | 16 | 4 | 20 |
| `tt_36_2024_byt` | 1 | 1 | 2 |
| `tt_37_2026_bca` | 1 | 0 | 1 |
| `tt_51_2025_bca` | 1 | 0 | 1 |
| `tt_65_2024_bca` | 1 | 0 | 1 |
| `tt_79_2024_bca` | 16 | 4 | 20 |
| **Tổng** | **104** | **54** | **158** |

## Bốn mẫu nhận diện bằng tỷ lệ dòng điền

Đọc nội dung cho thấy cả bốn là biểu mẫu để điền; đề xuất giữ nhãn hiện tại.

| unit_id | Tiêu đề | Tỷ lệ dòng điền |
|---|---|---:|
| `nd_160_2024:pl13` | Phụ lục XIII | 60.0% |
| `tt_12_2025_bca:pl1` | Phụ lục I | 52.4% |
| `tt_12_2025_bca:pl12` | Phụ lục XII | 47.6% |
| `tt_12_2025_bca:pl13` | Phụ lục XIII | 41.4% |

## Toàn bộ bản ghi có nhãn chất lượng kém

Tỷ lệ là chỉ báo âm tiết, không phải tỷ lệ lỗi OCR đối chiếu bản chuẩn. Không xóa các bản ghi này.

| version_id | Loại phụ lục hiện tại | Chỉ báo âm tiết lỗi |
|---|---|---:|
| `nd_158_2024:pl7@2025-01-01` | mau_bieu | 0.2864 |
| `nd_158_2024:pl8@2025-01-01` | mau_bieu | 0.4204 |
| `nd_158_2024:pl9@2025-01-01` | mau_bieu | 0.1379 |
| `nd_158_2024:pl12@2025-01-01` | mau_bieu | 0.1409 |
| `nd_218_2026:pl2@2026-08-10` | mau_bieu | 0.1930 |
| `nd_218_2026:pl3@2026-08-10` | mau_bieu | 0.1879 |
| `nd_218_2026:pl5@2026-08-10` | mau_bieu | 0.1005 |
| `qcvn_41_2024:d61:k1@2025-01-01` | không phải phụ lục | 0.1176 |
| `tt_108_2026_bca:pl11@2026-07-01` | mau_bieu | 0.1265 |
| `tt_108_2026_bca:pl13@2026-07-01` | noi_dung | 0.3600 |
| `tt_12_2025_bca:pl13@2025-03-01` | mau_bieu | 0.3477 |
| `tt_12_2025_bca:pl16@2025-03-01` | mau_bieu | 0.3456 |
| `tt_37_2026_bca:pl1@2026-06-08` | mau_bieu | 0.3138 |
| `tt_79_2024_bca:pl1@2025-01-01` | mau_bieu | 0.2318 |
| `tt_79_2024_bca:pl2@2025-01-01` | mau_bieu | 0.2311 |
| `tt_79_2024_bca:pl3@2025-01-01` | mau_bieu | 0.2969 |
| `tt_79_2024_bca:pl4@2025-01-01` | mau_bieu | 0.3333 |
| `tt_79_2024_bca:pl5@2025-01-01` | mau_bieu | 0.1992 |
| `tt_79_2024_bca:pl6@2025-01-01` | mau_bieu | 0.2467 |
| `vbhn_135_2025_blhs:d235:k1:h@2025-07-01` | không phải phụ lục | 0.1379 |
| `vbhn_135_2025_blhs:d235:k2:đ@2025-07-01` | không phải phụ lục | 0.1379 |

## Danh sách đủ 158 đơn vị phụ lục trước khi duyệt

CSV có trích đầu/cuối nội dung, tỷ lệ dòng điền và cờ cần xem: [2026-10-09-annex-review.csv](2026-10-09-annex-review.csv). Đầu ra CLI gốc: `data/processed/annex_types.csv`.

| unit_id | Tiêu đề | Loại hiện tại | Chất lượng | Cờ cần xem |
|---|---|---|---|---|
| `nd_158_2024:pl1` | Phụ lục I | mau_bieu | ok |  |
| `nd_158_2024:pl2` | Phụ lục II | mau_bieu | ok |  |
| `nd_158_2024:pl3` | Phụ lục III | mau_bieu | ok |  |
| `nd_158_2024:pl4` | Phụ lục IV | mau_bieu | ok |  |
| `nd_158_2024:pl5` | Phụ lục V | mau_bieu | ok |  |
| `nd_158_2024:pl6` | Phụ lục VI | mau_bieu | ok |  |
| `nd_158_2024:pl7` | Phụ lục VII | mau_bieu | kem | chữ kém |
| `nd_158_2024:pl8` | Phụ lục VIII | mau_bieu | kem | chữ kém |
| `nd_158_2024:pl9` | Phụ lục IX | mau_bieu | kem | chữ kém |
| `nd_158_2024:pl10` | Phụ lục X | mau_bieu | ok |  |
| `nd_158_2024:pl11` | Phụ lục XI | mau_bieu | ok |  |
| `nd_158_2024:pl12` | Phụ lục XII | mau_bieu | kem | chữ kém |
| `nd_158_2024:pl13` | Phụ lục XIII | mau_bieu | ok |  |
| `nd_160_2024:pl1` | Phụ lục I | mau_bieu | ok |  |
| `nd_160_2024:pl2` | Phụ lục II | noi_dung | ok |  |
| `nd_160_2024:pl3` | Phụ lục III | mau_bieu | ok |  |
| `nd_160_2024:pl4` | Phụ lục IV | mau_bieu | ok |  |
| `nd_160_2024:pl5` | Phụ lục V | mau_bieu | ok |  |
| `nd_160_2024:pl6` | Phụ lục VI | mau_bieu | ok |  |
| `nd_160_2024:pl7` | Phụ lục VII | mau_bieu | ok |  |
| `nd_160_2024:pl8` | Phụ lục VIII | mau_bieu | ok |  |
| `nd_160_2024:pl9` | Phụ lục IX | mau_bieu | ok |  |
| `nd_160_2024:pl10` | Phụ lục X | mau_bieu | ok |  |
| `nd_160_2024:pl11` | Phụ lục XI | mau_bieu | ok |  |
| `nd_160_2024:pl12` | Phụ lục XII | mau_bieu | ok |  |
| `nd_160_2024:pl13` | Phụ lục XIII | mau_bieu | ok |  |
| `nd_160_2024:pl14` | Phụ lục XIV | mau_bieu | ok |  |
| `nd_160_2024:pl15` | Phụ lục XV | mau_bieu | ok |  |
| `nd_160_2024:pl16` | Phụ lục XVI | mau_bieu | ok |  |
| `nd_160_2024:pl17` | Phụ lục XVII | mau_bieu | ok |  |
| `nd_160_2024:pl18` | Phụ lục XVIII | mau_bieu | ok |  |
| `nd_160_2024:pl19` | Phụ lục XIX | mau_bieu | ok |  |
| `nd_160_2024:pl20` | Phụ lục XX | mau_bieu | ok |  |
| `nd_160_2024:pl21` | Phụ lục XXI | mau_bieu | ok |  |
| `nd_165_2024:pl1` | Phụ lục I | mau_bieu | ok |  |
| `nd_165_2024:pl2` | Phụ lục II | noi_dung | ok |  |
| `nd_165_2024:pl3` | Phụ lục III | mau_bieu | ok |  |
| `nd_165_2024:pl4` | Phụ lục IV | mau_bieu | ok |  |
| `nd_165_2024:pl5` | Phụ lục V MẪU TỜ TRÌNH VÀ QUYẾT ĐỊNH PHÊ DUYỆT PHƯƠNG ÁN TỔ CHỨC GIAO THÔNG ĐƯỜNG CAO TỐC, PHÊ DUYỆT ĐIỀU CHỈNH PHƯƠNG Á | mau_bieu | ok |  |
| `nd_165_2024:pl6` | Phụ lục VI MẪU ĐƠN ĐỀ NGHỊ VÀ VĂN BẢN CHẤP THUẬN VỊ TRÍ NÚT GIAO ĐẤU NỐI, ĐẤU NỐI TẠM VÀO ĐƯỜNG BỘ ĐANG KHAI THÁC (Kèm t | mau_bieu | ok |  |
| `nd_165_2024:pl7` | Phụ lục VII | noi_dung | ok |  |
| `nd_165_2024:pl8` | Phụ lục VIII | mau_bieu | ok |  |
| `nd_165_2024:pl9` | Phụ lục IX | noi_dung | ok | có dòng điền dưới ngưỡng |
| `nd_165_2024:pl10` | Phụ lục X | noi_dung | ok |  |
| `nd_218_2026:pl1` | Phụ lục I | mau_bieu | ok |  |
| `nd_218_2026:pl2` | Phụ lục II | mau_bieu | kem | chữ kém |
| `nd_218_2026:pl3` | Phụ lục III | mau_bieu | kem | chữ kém |
| `nd_218_2026:pl4` | Phụ lục IV | mau_bieu | ok |  |
| `nd_218_2026:pl5` | Phụ lục V | mau_bieu | kem | chữ kém |
| `nd_218_2026:pl6` | Phụ lục VI | mau_bieu | ok |  |
| `nd_218_2026:pl7` | Phụ lục VII | mau_bieu | ok |  |
| `nd_220_2026:pl1` | Phụ lục III | noi_dung | ok |  |
| `nd_220_2026:pl2` | Phụ lục X | mau_bieu | ok |  |
| `nd_241_2026:pl1` | Phụ lục I | mau_bieu | ok |  |
| `nd_241_2026:pl2` | Phụ lục II | noi_dung | ok |  |
| `nd_241_2026:pl3` | Phụ lục III | mau_bieu | ok |  |
| `nd_241_2026:pl4` | Phụ lục IV | mau_bieu | ok |  |
| `nd_241_2026:pl5` | Phụ lục V | mau_bieu | ok |  |
| `nd_241_2026:pl6` | Phụ lục VI | mau_bieu | ok |  |
| `nd_241_2026:pl7` | Phụ lục VII | noi_dung | ok |  |
| `nd_39_2023:pl1` | Phụ lục | noi_dung | ok | ngắn; xem đủ nội dung |
| `nd_67_2023:pl1` | Phụ lục I | noi_dung | ok |  |
| `nd_67_2023:pl2` | Phụ lục II | noi_dung | ok |  |
| `nd_67_2023:pl3` | Phụ lục III | noi_dung | ok |  |
| `nd_67_2023:pl4` | Phụ lục III | noi_dung | ok |  |
| `nd_67_2023:pl5` | Phụ lục IV | noi_dung | ok |  |
| `nd_67_2023:pl6` | Phụ lục V | noi_dung | ok |  |
| `nd_67_2023:pl7` | Phụ lục VI | noi_dung | ok | có dòng điền dưới ngưỡng |
| `nd_67_2023:pl8` | Phụ lục VII | noi_dung | ok |  |
| `nd_67_2023:pl9` | Phụ lục VIII | noi_dung | ok | có dòng điền dưới ngưỡng |
| `nd_67_2023:pl10` | Phụ lục IX | noi_dung | ok | có dòng điền dưới ngưỡng |
| `nd_67_2023:pl11` | Phụ lục X | mau_bieu | ok |  |
| `qcvn_41_2024:pl1` | Phụ lục A | noi_dung | ok |  |
| `qcvn_41_2024:pl2` | Phụ lục B | noi_dung | ok |  |
| `qcvn_41_2024:pl3` | Phụ lục C | noi_dung | ok |  |
| `qcvn_41_2024:pl4` | Phụ lục D | noi_dung | ok |  |
| `qcvn_41_2024:pl5` | Phụ lục E | noi_dung | ok |  |
| `qcvn_41_2024:pl6` | Phụ lục F | noi_dung | ok |  |
| `qcvn_41_2024:pl7` | Phụ lục G | noi_dung | ok | có dòng điền dưới ngưỡng |
| `qcvn_41_2024:pl8` | Phụ lục I | noi_dung | ok |  |
| `qcvn_41_2024:pl9` | Phụ lục K | noi_dung | ok |  |
| `tt_108_2026_bca:pl1` | PHỤ LỤC I (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok |  |
| `tt_108_2026_bca:pl2` | PHỤ LỤC II (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok |  |
| `tt_108_2026_bca:pl3` | PHỤ LỤC III (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok |  |
| `tt_108_2026_bca:pl4` | PHỤ LỤC IV (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok |  |
| `tt_108_2026_bca:pl5` | PHỤ LỤC V (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok | có dòng điền dưới ngưỡng |
| `tt_108_2026_bca:pl6` | PHỤ LỤC VI (Ban hành kèm theo Thông tư số 108/2026/T7-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok | có dòng điền dưới ngưỡng; chữ mẫu ngoài phần đầu |
| `tt_108_2026_bca:pl7` | PHỤ LỤC VII (Ban hành kèm theo Thông tư sô 108/2026/77-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | ok |  |
| `tt_108_2026_bca:pl8` | PHỤ LỤC VIII (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | ok |  |
| `tt_108_2026_bca:pl9` | PHỤ LỤC IX (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | ok | mẫu có nội dung quy định |
| `tt_108_2026_bca:pl10` | PHỤ LỤC X (Ban hành kèm theo Thông tư số 108/2026/T7-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | ok |  |
| `tt_108_2026_bca:pl11` | PHỤ LỤC XI (Ban hành kèm theo Thông tư sô 108/2026/71-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | kem | chữ kém |
| `tt_108_2026_bca:pl12` | PHỤ LỤC XII (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | ok | ngắn; xem đủ nội dung |
| `tt_108_2026_bca:pl13` | PHỤ LỤC XIII (Ban hành kèm theo Thông tư số 108/2026/TT-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | noi_dung | kem | chữ kém |
| `tt_108_2026_bca:pl14` | PHỤ LỤC XIV (Ban hành kèm theo Thông tư sô 108/2026/71-BCA ngày 29 tháng 6 năm 2026 của Bộ trưởng Bộ Công an) | mau_bieu | ok |  |
| `tt_12_2025_bca:pl1` | Phụ lục I | mau_bieu | ok |  |
| `tt_12_2025_bca:pl2` | Phụ lục II | noi_dung | ok |  |
| `tt_12_2025_bca:pl3` | Phụ lục III | noi_dung | ok |  |
| `tt_12_2025_bca:pl4` | Phụ lục IV | noi_dung | ok |  |
| `tt_12_2025_bca:pl5` | Phụ lục V | noi_dung | ok |  |
| `tt_12_2025_bca:pl6` | Phụ lục VI | noi_dung | ok |  |
| `tt_12_2025_bca:pl7` | Phụ lục VII | noi_dung | ok | có dòng điền dưới ngưỡng; chữ mẫu ngoài phần đầu |
| `tt_12_2025_bca:pl8` | PHỤ LỤC VIII | mau_bieu | ok |  |
| `tt_12_2025_bca:pl9` | Phụ lục IX | mau_bieu | ok |  |
| `tt_12_2025_bca:pl10` | Phụ lục X | mau_bieu | ok | mẫu có nội dung quy định |
| `tt_12_2025_bca:pl11` | Phụ lục XI | mau_bieu | ok |  |
| `tt_12_2025_bca:pl12` | Phụ lục XII | mau_bieu | ok |  |
| `tt_12_2025_bca:pl13` | Phụ lục XIII | mau_bieu | kem | chữ kém |
| `tt_12_2025_bca:pl14` | Phụ lục XIV | noi_dung | ok | mẫu IDP nhận thành nội dung; đề xuất ghi đè |
| `tt_12_2025_bca:pl15` | Phụ lục XV | noi_dung | ok |  |
| `tt_12_2025_bca:pl16` | Phụ lục XVI | mau_bieu | kem | chữ kém |
| `tt_12_2025_bca:pl17` | Phụ lục XVII | mau_bieu | ok |  |
| `tt_155_2025_btc:pl1` | Phụ lục BIỂU MỨC THU LỆ PHÍ ĐĂNG KÝ, CẤP BIỂN PHƯƠNG TIỆN GIAO THÔNG (Kèm theo Thông tư số 155/2025/TT-BTC ngày 31 tháng | noi_dung | ok |  |
| `tt_30_2026_bxd:pl1` | Phụ lục I MẪU THÔNG BÁO KẾT QUẢ KIỂM TRA, ĐÁNH GIÁ (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 202 | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl2` | Phụ lục II MẪU PHIẾU HỒ SƠ PHƯƠNG TIỆN (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ trư | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl3` | Phụ lục III BẢN XÁC NHẬN THÔNG SỐ KỸ THUẬT CỦA XE (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl4` | Phụ lục IV MẪU PHIẾU KIỂM SOÁT (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ trưởng Bộ X | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl5` | Phụ lục V CHU KỲ KIỂM ĐỊNH (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ trưởng Bộ Xây d | noi_dung | ok |  |
| `tt_30_2026_bxd:pl6` | Phụ lục VI MẪU GIẤY HẸN CẤP GIẤY CHỨNG NHẬN KIỂM ĐỊNH; GIẤY TIẾP NHẬN THÔNG TIN BÁO MẤT GIẤY CHỨNG NHẬN KIỂM ĐỊNH, TEM K | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl7` | Phụ lục VII MẪU VĂN BẢN ĐỀ NGHỊ KIỂM ĐỊNH (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ  | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl8` | Phụ lục VIII PHIẾU KIỂM ĐỊNH (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ trưởng Bộ Xây | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl9` | Phụ lục IX MẪU ĐƠN ĐỀ NGHỊ CẤP LẠI GIẤY CHỨNG NHẬN KIỂM ĐỊNH, TEM KIỂM ĐỊNH; GIẤY CHỨNG NHẬN CẢI TẠO (Ban hành kèm theo  | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl10` | Phụ lục X MẪU SỔ THEO DÕI CẤP GIẤY CHỨNG NHẬN KIỂM ĐỊNH, TEM KIỂM ĐỊNH, GIẤY CHỨNG NHẬN CẢI TẠO, SỐ QUẢN LÝ HỒ SƠ PHƯƠNG | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl11` | Phụ lục XI NGUYÊN TẮC XÁC ĐỊNH XE CẢI TẠO (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ  | noi_dung | ok |  |
| `tt_30_2026_bxd:pl12` | Phụ lục XII MẪU PHIẾU TIẾP NHẬN HỒ SƠ (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ trưở | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl13` | Phụ lục XIII THÔNG BÁO THÔNG TIN DỮ LIỆU CỦA XE SẢN XUẤT, LẮP RÁP HOẶC XE NHẬP KHẨU HOẶC XE CẢI TẠO CÓ SỰ SAI KHÁC VỚI X | noi_dung | ok | có dòng điền dưới ngưỡng |
| `tt_30_2026_bxd:pl14` | Phụ lục XIV NỘI DUNG HỒ SƠ THIẾT KẾ CẢI TẠO (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của B | noi_dung | ok |  |
| `tt_30_2026_bxd:pl15` | Phụ lục XV MẪU BIÊN BẢN KIỂM TRA, ĐÁNH GIÁ XE CẢI TẠO (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm  | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl16` | Phụ lục XVI MẪU BẢNG KÊ CÁC HỆ THỐNG, TỔNG THÀNH, PHỤ TÙNG THAY THẾ (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 1 | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl17` | Phụ lục XVII MẪU VĂN BẢN ĐỀ NGHỊ CHỨNG NHẬN XE CẢI TẠO (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl18` | Phụ lục XVIII MẪU GIẤY CHỨNG NHẬN CẢI TẠO (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 2026 của Bộ  | mau_bieu | ok |  |
| `tt_30_2026_bxd:pl19` | Phụ lục XIX MẪU VĂN BẢN CHẤP THUẬN SỬ DỤNG CHUNG HỒ SƠ THIẾT KẾ (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 th | mau_bieu | ok | mẫu có nội dung quy định |
| `tt_30_2026_bxd:pl20` | Phụ lục XX MẪU TEM KIỂM ĐỊNH, CHỨNG NHẬN KIỂM ĐỊNH (Ban hành kèm theo Thông tư số 30/2026/TT-BXD ngày 15 tháng 6 năm 202 | mau_bieu | ok |  |
| `tt_36_2024_byt:pl1` | PHỤ LỤC I BẢNG TIÊU CHUẨN SỨC KHỎE CỦA NGƯỜI LÁI XE, NGƯỜI ĐIỀU KHIỂN XE MÁY CHUYÊN DÙNG (Ban hành kèm theo Thông tư số  | noi_dung | ok |  |
| `tt_36_2024_byt:pl2` | PHỤ LỤC II MAU GIAY KHAM SỨC KHỎE CUỦA NGUỜI LAI XE, NGƯỜI ĐIỀU KHIỂN XE MAY CHUYEN DỰNG (Ban hành kèm theo Thôngtưsô. 3 | mau_bieu | ok |  |
| `tt_37_2026_bca:pl1` | Mẫu KĐ23a ban hành kèm theo Thông tư số 37/2026/TT-BCA ngày 24/4/2026 của Bộ Công anMẫu KĐ23a ban hành kèm theo Thông tư | mau_bieu | kem | chữ kém |
| `tt_51_2025_bca:pl1` | Phụ lục số 02 | mau_bieu | ok |  |
| `tt_65_2024_bca:pl1` | PHỤ LỤC | mau_bieu | ok | mẫu có nội dung quy định |
| `tt_79_2024_bca:pl1` | Mẫu ĐKX01 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl2` | Mẫu ĐKX02 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl3` | Mẫu ĐKX03 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl4` | Mẫu ĐKX04 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl5` | Mẫu ĐKX05 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl6` | Mẫu ĐKX06 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | kem | chữ kém |
| `tt_79_2024_bca:pl7` | Mẫu ĐKX07 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl8` | Mẫu ĐKX08 Ban hành kèm theo Thông tư số 79/2024/TT-BCA Ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl9` | Mẫu ĐKX09 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok | mẫu có nội dung quy định |
| `tt_79_2024_bca:pl10` | Mẫu ĐKX10 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl11` | Mẫu ĐKX11 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl12` | Mẫu ĐKX12 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl13` | Mẫu ĐKX13 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl14` | Mẫu ĐKX14 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl15` | Mẫu ĐKX15 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl16` | Mẫu ĐKX16 Ban hành kèm theo Thông tư số 79/2024/TT-BCA ngày 15/11/2024 của Bộ trưởng Bộ Công an | mau_bieu | ok |  |
| `tt_79_2024_bca:pl17` | PHỤ LỤC 01 | noi_dung | ok |  |
| `tt_79_2024_bca:pl18` | Phụ lục số 02 | noi_dung | ok | chữ mẫu ngoài phần đầu |
| `tt_79_2024_bca:pl19` | Phụ lục số 03 | noi_dung | ok |  |
| `tt_79_2024_bca:pl20` | Phụ lục số 04 | noi_dung | ok |  |

Điểm dừng quy định tại `docs/superpowers/plans/2026-10-09-cleanup-round2.md`, Task 6, Step 8: **“Không sang Task 7 trước khi người dùng trả lời.”**
