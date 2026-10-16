# Duyệt dòng sửa đổi đợt 4 (2026-10-17)

Bản nháp do `draft_batch4.py` soạn. Chạy thử với mọi dòng dưới đây coi như đã duyệt: áp được hết, không lỗi.

## Đã áp (bạn đồng ý đóng văn bản)

| Văn bản cũ | Thay bởi | Đóng từ |
|---|---|---|
| NĐ 39/2023 | NĐ 156/2024 | 2025-01-01 |
| NĐ 160/2024 | NĐ 94/2026 | 2026-07-01 |
| VBHN 63 (Luật XLVPHC) | VBHN 90 | 2026-07-01 |

## Chờ duyệt

Trong `data/processed/amendments_reviewed.csv`, lọc cột `ghi_chu` có "đợt 4 (2026-10-17): chờ duyệt" (61 dòng, `status = chua_duyet`):

| Văn bản sửa | Văn bản đích | Số dòng | Điểm chính |
|---|---|---:|---|
| NĐ 47/2026 | NĐ 138/2021 | 15 | thêm Điều 11a (niêm phong), Điều 17a; sửa Điều 16, 17; bỏ yêu cầu bản sao CMND/CCCD ở điểm a khoản 2 Điều 14; "thị trấn" → "đặc khu" |
| TT 13/2025 | TT 65/2024 | 1 | khoản 1 Điều 6 (bộ câu hỏi do Cục CSGT ban hành) |
| TT 13/2025 | TT 79/2024 | 24 | Công an cấp xã đăng ký xe (Điều 4), bãi bỏ khoản 3 Điều 4 (Công an cấp huyện), bỏ "công ích" ở 13 chỗ |
| TT 105/2026 | TT 65/2024 | 11 | bỏ kiểm tra mô phỏng từ 01/7/2026; Điều 6 mới từ 01/7/2027 (`hl_rieng`); sửa Điều 7, khoản 4 Điều 8 |
| TT 62/2026 | TT 79/2024 | 10 | sửa khoản 6 Điều 3, Điều 7, 14, 16, 17, 20, 21, 26 |

Trong `data/annex_replacements.csv`, 10 dòng có cột `duyet` trống: 9 mẫu ĐKX của TT 79 thay bằng mẫu ĐKX…/79 của TT 13 (từ 2025-03-01), phụ lục biểu mẫu TT 65 thay bằng phụ lục TT 105 (từ 2026-07-01).

Dòng nên xem kỹ:

- `nd_47_2026:d5:k4`: bỏ cả câu về bản sao CMND/CCCD, đồng thời bỏ dấu ";" theo sau và viết hoa "Đối với tổ chức vi phạm…".
- Các dòng `tt_105_2026_bca:d1` có `hl_rieng = 2027-07-01`: Điều 6 mới chỉ áp dụng từ 01/7/2027; tiêu đề Điều 6 giữ chữ cũ.

## Cách duyệt

1. Đổi `status` thành `duyet` (hoặc `loai`) cho dòng đồng ý; ghi cột `duyet = duyet` ở `annex_replacements.csv`.
2. Chạy `py -3.13 -X utf8 scripts/process_legal.py apply`.
3. Chạy `py -3.13 -X utf8 -m pytest -q`. Khi duyệt hết, ba test đánh dấu `xfail` sẽ báo XPASS (lỗi strict): xóa dòng `@pytest.mark.xfail` của chúng.
