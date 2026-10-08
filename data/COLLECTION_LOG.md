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

**Còn thiếu (không có trên Công báo, đợt sau)**
| Văn bản | Nguồn dự kiến |
|---|---|
| TT 108/2026/TT-BCA (sát hạch, cấp GPLX) | Cổng thông tin Bộ Công an |
| TT 36/2024/TT-BYT (sức khỏe người lái xe) | Cổng thông tin Bộ Y tế |
| TT 155/2025/TT-BTC (lệ phí đăng ký, cấp biển) | Cổng thông tin Bộ Tài chính |
| TT 30/2026/TT-BXD (kiểm định xe cơ giới) | moc.gov.vn |
| Bộ 600 câu hỏi sát hạch GPLX (2025) | Cục CSGT; bản PDF trên lawnet.vn để đối chiếu |

**Lưu ý lưu trữ:** `data/raw/` không đưa lên Git (xem `.gitignore`). Tái tạo bằng `python scripts/download_raw.py` và đối chiếu sha256 trong `data/manifest.csv`.
