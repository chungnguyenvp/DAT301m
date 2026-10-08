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

## Tổng sau hai đợt
34 văn bản, 93 file, 294 MB. Danh sách đầy đủ trong `data/manifest.csv`.

**Lưu ý lưu trữ:** `data/raw/` không đưa lên Git (xem `.gitignore`). Tái tạo bằng `python scripts/download_raw.py` và đối chiếu sha256 trong `data/manifest.csv`.
