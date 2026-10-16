# Nhật ký thu thập dữ liệu

Ngày chốt dữ liệu: **01/10/2026**. Thu thập có hỗ trợ của AI (Claude Code), nhóm duyệt danh sách trước khi tải.

## 2026-10-08: Đợt 1, Công báo Chính phủ

**Nguồn:** congbao.chinhphu.vn (API tìm kiếm `api-searchcongbao.chinhphu.vn/search/all`, file trên `congbaocdn.chinhphu.vn`).

**Vì sao không dùng vbpl.vn:** ngày 08/10/2026 trang vbpl.vn (giao diện mới) trả lỗi 500 cho mọi lượt tìm kiếm.

**Cách làm**
1. Tra số hiệu từng văn bản trong bản thiết kế qua API Công báo, lấy ngày ban hành, ngày hiệu lực và link file.
2. Dò văn bản sửa đổi: tìm "sửa đổi <số hiệu>", "thay thế <số hiệu>" và giữ kết quả có số hiệu gốc trong tiêu đề hoặc trích yếu.
3. Lập `data/download_plan.csv` (link, dung lượng lấy bằng HEAD), nhóm duyệt phương án tải cả Word và PDF.
4. Tải bằng `scripts/download_raw.py`; kiểm tra định dạng bằng chữ ký file và dung lượng so với HEAD; ghi `data/manifest.csv` kèm sha256.

**Kết quả:** 28 văn bản, 87 file, 243 MB, tất cả đạt kiểm tra; không có file trùng sha256.

Một văn bản có nhiều file vì được đăng trên nhiều số Công báo; hậu tố `__pN` theo thứ tự API trả về. Phải ghép đủ các phần khi xử lý.

**Văn bản mới phát hiện (chưa có trong bản thiết kế ban đầu)**
| Văn bản | Nội dung | Hiệu lực |
|---|---|---|
| NĐ 241/2026/NĐ-CP | Sửa NĐ 165/2024 | 01/7/2026 |
| NĐ 218/2026/NĐ-CP | Sửa NĐ 158/2024 | 10/8/2026 |
| TT 51/2025/TT-BCA | Trích yếu có nhắc TT 79/2024; cần đọc để xác nhận quan hệ | |
| NĐ 160/2024/NĐ-CP | Đào tạo lái xe | |
| TT 108/2026/TT-BCA | Thay TT 12/2025/TT-BCA (giữ một số phụ lục của TT 12 đến 28/02/2027) | 01/7/2026 |

**Không lấy**
- NĐ 202/2026/NĐ-CP sửa NĐ 10/2022: hiệu lực 01/3/2027, sau ngày chốt.
- NĐ 110/2022/NĐ-CP: xuất hiện khi dò sửa đổi NĐ 10/2022, chưa xác nhận liên quan.

**Giới hạn của cách dò sửa đổi:** chỉ bắt được văn bản ghi số hiệu gốc trong tiêu đề hoặc trích yếu. Ví dụ Luật 118/2025/QH15 sửa Luật 35 và 36 nhưng không bị dò ra theo cách này. Khi xử lý phải đọc phần căn cứ và điều khoản thi hành của từng văn bản để xác nhận quan hệ sửa đổi.

**Còn thiếu sau đợt 1 (không có trên Công báo; đã lấy ở đợt 2)**
| Văn bản | Nguồn dự kiến |
|---|---|
| TT 108/2026/TT-BCA (sát hạch, cấp GPLX) | Cổng thông tin Bộ Công an |
| TT 36/2024/TT-BYT (sức khỏe người lái xe) | Cổng thông tin Bộ Y tế |
| TT 155/2025/TT-BTC (lệ phí đăng ký, cấp biển) | Cổng thông tin Bộ Tài chính |
| TT 30/2026/TT-BXD (kiểm định xe cơ giới) | moc.gov.vn |
| Bộ 600 câu hỏi sát hạch GPLX (2025) | Cục CSGT; bản PDF trên lawnet.vn để đối chiếu |

## 2026-10-08: Đợt 2, năm văn bản không có trên Công báo

**Nguồn và cách tìm**
- Hệ thống văn bản của Cổng TTĐT Chính phủ (vanban.chinhphu.vn, file trên `datafiles.chinhphu.vn`): tra theo số ký hiệu, lấy file trong mục "Tài liệu đính kèm".
- Bộ 600 câu hỏi: trang cũ của Cục CSGT (`csgt.vn/m/vanbanphapluat/319/...`) nay chuyển về trang chủ, không còn file. Lấy bản đăng lại trên trang Công an TP Cần Thơ (đăng 02/04/2026). Công văn 2262/CSGT-P5 lấy từ thuvienphapluat.vn vì chưa tìm thấy trên trang nhà nước.
- Kế hoạch: `data/download_plan_batch2.csv`; nhóm duyệt, không lấy bản "signed" của TT 108/2026 (bản đó không được liệt kê trên vanban.chinhphu.vn).

**Kết quả:** 6 file, 51 MB, tất cả đạt kiểm tra.
| doc_id | Văn bản | Nguồn |
|---|---|---|
| tt_108_2026_bca | TT 108/2026/TT-BCA (bản đầy đủ) | vanban.chinhphu.vn |
| tt_36_2024_byt | TT 36/2024/TT-BYT | vanban.chinhphu.vn |
| tt_155_2025_btc | TT 155/2025/TT-BTC (bản có chữ ký số) | vanban.chinhphu.vn |
| tt_30_2026_bxd | TT 30/2026/TT-BXD | vanban.chinhphu.vn (cùng dung lượng với bản trên moc.gov.vn) |
| gplx_600_2025 | Bộ 600 câu hỏi sát hạch | congan.cantho.gov.vn (bản đăng lại) |
| cv_2262_2025_csgt | Công văn 2262/CSGT-P5 | thuvienphapluat.vn (không phải nguồn nhà nước) |

**Ghi chú kỹ thuật:** congan.cantho.gov.vn trả 403 khi User-Agent quá ngắn; script dùng User-Agent trình duyệt đầy đủ.

**Việc cần kiểm tra khi xử lý**
- Bộ 600 câu ban hành theo TT 12/2025/TT-BCA, mà TT 12/2025 đã bị TT 108/2026 thay thế. Phải đọc TT 108 để biết bộ câu hỏi có được thay hay không.
- Đối chiếu bộ 600 câu bản đăng lại với Công văn 2262 (số chương, số câu, câu điểm liệt).

## 2026-10-08: Sửa lỗi sau khi mở file kiểm tra

**Bộ luật Dân sự tải nhầm.** Đợt 1 khớp số ký hiệu `91/2015/QH13` và lấy nhầm Nghị quyết ngày 18/6/2015 "về chương trình hoạt động giám sát của Quốc hội năm 2016" (trùng số). Đã xóa file sai, sửa `download_plan.csv` và tải lại Bộ luật Dân sự ban hành 24/11/2015 (Công báo số 1243–1246 ngày 28/12/2015, 2 file PDF, phần 2 chứa Điều 601).

**Bài học:** khớp số ký hiệu chưa đủ vì số có thể trùng giữa các loại văn bản; phải kiểm tra cả trích yếu và tiêu đề trong nội dung file. Bước xử lý sẽ kiểm tra tự động số hiệu và trích yếu ở trang đầu của mọi văn bản.

**TT 36/2024/TT-BYT không phải dự thảo.** Lớp chữ trong file trống ở số hiệu và ngày ký, nhưng ảnh trang đầu có dấu "SAO Y" và chữ ký số của Bộ Y tế ngày 16/11/2024; số "36" và ngày "16" được điền tay trước khi scan. Giữ file, OCR lại khi xử lý vì lớp chữ có sẵn nhiều lỗi.

**PDF dạng ảnh scan cần OCR:** TT 108/2026/TT-BCA (134 trang, không có lớp chữ), TT 155/2025/TT-BTC (6 trang), TT 36/2024/TT-BYT (lớp chữ chất lượng kém). Công cụ: Tesseract 5.4 (cài qua winget) với `vie.traineddata` từ `tesseract-ocr/tessdata_best`, đặt tại `tools/tessdata/` (không đưa lên Git).

## Tổng sau hai đợt
34 văn bản, 94 file, 294 MB. Danh sách đầy đủ trong `data/manifest.csv`.

## 2026-10-16: Đợt 3, bản Word của hai thông tư trước đây chỉ có ảnh

**Nguồn:** Công báo Chính phủ, nhóm tự tải bản Word từ trang văn bản:
| doc_id | File | Trang Công báo |
|---|---|---|
| tt_108_2026_bca | `tt_108_2026_bca__p2.docx` (3,8 MB) | https://congbao.chinhphu.vn/van-ban/thong-tu-so-108-2026-tt-bca-470055/67051.htm |
| tt_155_2025_btc | `tt_155_2025_btc__p2.docx` (50 KB) | https://congbao.chinhphu.vn/van-ban/thong-tu-so-155-2025-tt-btc-468559.htm |

Đợt 1 ghi hai văn bản này không có trên Công báo; khi đó chưa tìm thấy, nay đã có trang văn bản.

**Kiểm tra:** đúng số hiệu, trích yếu và ngày ký ở đầu văn bản; số Điều và số phụ lục khớp bản PDF ảnh (TT 108: 43 Điều, 14 phụ lục; TT 155: 8 Điều, 1 phụ lục); `data/manifest.csv` ghi sha256, cột `url` là trang văn bản trên Công báo (không phải link file trực tiếp nên `scripts/download_raw.py` không tải lại được hai file này). Bản PDF ảnh từ vanban.chinhphu.vn vẫn giữ để đối chiếu.

**TT 36/2024/TT-BYT:** không có bản Word; bản PDF nhóm có trùng sha256 với file đã tải ở đợt 2. Lớp chữ sẵn có trong PDF đọc dấu tốt hơn Tesseract ở phần thân nhưng làm mất nội dung bảng Phụ lục I. Nhóm lấy bản chữ thuần từ thuvienphapluat.vn (https://thuvienphapluat.vn/van-ban/The-thao-Y-te/Thong-tu-36-2024-TT-BYT-tieu-chuan-suc-khoe-nguoi-dieu-khien-xe-may-chuyen-dung-622478.aspx), lưu thành `tt_36_2024_byt__p2.txt`. Đây **không phải nguồn nhà nước**: chỉ dùng làm nguồn chữ sau khi so từng từ phần thân với PDF chính thức (không có khác biệt nội dung) và dựng lại bảng Phụ lục I theo ảnh PDF. PDF chính thức vẫn là bản gốc để tra.

## Tổng sau ba đợt
34 văn bản, 97 file. Danh sách đầy đủ trong `data/manifest.csv`.

**Lưu ý lưu trữ:** `data/raw/` không đưa lên Git (xem `.gitignore`). Tái tạo bằng `python scripts/download_raw.py` và đối chiếu sha256 trong `data/manifest.csv`; hai file Word và file chữ TT 36 của đợt 3 phải tải tay từ các trang ở trên.

## 2026-10-17: Đợt 4, văn bản thay thế và sửa đổi bị sót

**Lý do:** hai bản kiểm toán pháp lý độc lập cho thấy kho thiếu văn bản thay thế hoặc sửa đổi. Đợt 1–3 chỉ tìm văn bản sửa đổi theo cụm "sửa đổi <số hiệu>" trong trích yếu, nên bỏ sót văn bản thay thế cả văn bản (NĐ 156, NĐ 94), văn bản sửa nhiều thông tư một lúc (TT 13/2025, TT 62/2026) và bản hợp nhất mới (VBHN 90).

**Nguồn:** Công báo Chính phủ, tải cả PDF và Word của từng số Công báo bằng `scripts/download_raw.py data/download_plan_batch4.csv`. Cột `url` là liên kết tải của Công báo (g7.cdnchinhphu.vn); trang văn bản ghi dưới đây.

| doc_id | Số Công báo | Trang Công báo |
|---|---|---|
| nd_156_2024 | 1491 + 1492 (25/12/2024) | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-156-2024-nd-cp-43494/53418.htm |
| nd_94_2026 | 212 (14/4/2026) | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-94-2026-nd-cp-469245/63953.htm |
| nd_47_2026 | 108 (14/02/2026) | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-47-2026-nd-cp-468906/62343.htm |
| tt_105_2026_bca | 428 (22/7/2026) | https://congbao.chinhphu.vn/van-ban/thong-tu-so-105-2026-tt-bca-470053/67041.htm |
| vbhn_90_2026_xlvphc | 222 (16/4/2026) | https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-90-vbhn-vpqh-469265/64066.htm |
| tt_62_2026_bca | 324 (11/6/2026) | https://congbao.chinhphu.vn/van-ban/thong-tu-so-62-2026-tt-bca-469658/65510.htm |
| tt_13_2025_bca | 475 + 476 và 477 + 478 (15/3/2025) | https://congbao.chinhphu.vn/van-ban/thong-tu-so-13-2025-tt-bca-44372/55293.htm |

**Kiểm tra:** đúng số hiệu, trích yếu, ngày ký và điều khoản hiệu lực ở bản PDF; `identity_report.csv` 40/40 `ok`; Điều liên tục, không thiếu Điều.

**Đã biết nhưng chưa đưa vào kho:** VBHN 171/2026/VBHN-LQ-VPQH (Luật XLVPHC, ký 30/9/2026) chỉ thêm Luật 11/2026/QH16 có hiệu lực 01/3/2027, sau mốc 01/10/2026.

## Tổng sau bốn đợt
40 văn bản pháp luật (kể cả QCVN 41 tách từ TT 51/2024) cùng bộ 600 câu GPLX và Công văn 2262; 113 file. Danh sách đầy đủ trong `data/manifest.csv`; tình trạng pháp lý trong `data/legal_status.csv`.
