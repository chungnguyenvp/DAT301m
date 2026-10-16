# Kiểm tra tay 40 đơn vị (2026-10-17)

**Trạng thái: đã kiểm 40/40 ngày 2026-10-17** (Claude so từng đơn vị với ảnh trang PDF chính thức; cột `nguoi_kiem`). Kết quả: 40/40 khớp chữ và con số; dòng 22 phát hiện lỗi tiêu đề khoản dính câu sau ở TT 30, đã sửa trong pipeline. Người dùng có thể kiểm lại vài dòng bất kỳ để xác nhận.

Năm văn bản không đối chứng tự động được với chữ PDF: TT 108, TT 155 (PDF ảnh), TT 36 (bản chữ thuvienphapluat), BLDS, TT 30 (dữ liệu trích chính từ PDF). Lượt này lấy ngẫu nhiên 40 đơn vị đang có hiệu lực của năm văn bản, khoảng 2/3 có con số; thêm hai bảng đã dựng lại tay (biểu phí TT 155, Phụ lục I TT 36). Danh sách sinh bằng `make_checklist.py` với hạt giống cố định 20261017.

| Văn bản | Số đơn vị |
|---|---:|
| TT 108/2026/TT-BCA | 12 |
| TT 30/2026/TT-BXD | 10 |
| Bộ luật Dân sự 2015 (Điều 584–608) | 8 |
| TT 155/2025/TT-BTC | 5 |
| TT 36/2024/TT-BYT | 5 |

## Cách làm

1. Mở `checklist.csv` bằng Excel.
2. Với mỗi dòng, mở tệp ở cột `file_pdf` (trong `data/raw/legal/`) tới trang ở cột `trang_pdf`. Nếu không thấy, xem trang trước và sau.
3. So chữ ở cột `noi_dung_trong_du_lieu` với bản PDF. Chú ý: **con số** (mức tiền, thời hạn, số Điều/khoản dẫn chiếu), **ngày tháng**, **chữ có dấu**, từ bị thiếu/thừa, câu bị cắt.
4. Cột `ket_qua`: ghi `khop` hoặc `sai`. Nếu `sai`, ghi ngắn vào `ghi_chu_sai` chỗ sai (ví dụ "thiếu chữ 'không' sau 'được'", "PDF ghi 30 ngày, dữ liệu ghi 3 ngày").

Không tính là sai: khác ngắt dòng, khác khoảng trắng, dấu nháy “ ” với ", gạch "-" với "–". Với hai bảng dựng lại (dòng 35, 40), dữ liệu được viết lại thành câu có tên cột; chỉ cần so **giá trị trong từng ô** và **ô thuộc nhóm/khu vực nào**.

## Sau khi kiểm tra

Lưu `checklist.csv` và báo lại. Kết quả sẽ được tổng hợp vào báo cáo xử lý (tỷ lệ khớp, lỗi tìm được) và dùng cho Report 2.
