# Báo cáo xử lý văn bản pháp luật giao thông

Tài liệu này tổng hợp đầu ra trong `data/processed/` tại `config.CUTOFF = 2026-10-01`. Số liệu hiện hành được tính từ JSONL/CSV bằng `task8_metrics.py`; các ghi nhận kiểm tra thủ công cũ được ghi rõ thời điểm mẫu. Chạy pipeline: `assemble → parse → effective → amendments → apply`. `effective` và `amendments` tạo bản đề xuất; `apply` dùng `effective_dates.csv`, `amendments_reviewed.csv`, `effective_exceptions.csv` và `annex_type_overrides.csv` đã duyệt.

## 1. Văn bản và đơn vị

Có **33 văn bản**: 28 trích từ docx, 2 từ pdf (`tt_30_2026_bxd`, `blds_2015`), 3 OCR (`tt_108_2026_bca`, `tt_36_2024_byt`, `tt_155_2025_btc`). `legal_units.jsonl` có **17.850 đơn vị**:

| Cấp | Số đơn vị |
|---|---:|
| `dieu` | 2.236 |
| `khoan` | 7.051 |
| `diem` | 8.341 |
| `phu_luc` | 158 |
| `mo_dau` | 33 |
| `ket_thuc` | 31 |

### Ghép và tách văn bản

- `vbhn_135_2025_blhs` thiếu Điều 90–107 theo `assembly_report.csv`; đây là phần đã bãi bỏ trong văn bản hợp nhất, không tự thêm Điều. Đây là văn bản duy nhất được báo `missing_dieu`.
- QCVN 41 đã tách khỏi `tt_51_2024_bgtvt_qcvn41` thành `qcvn_41_2024`: **84 Điều liên tục 1–84**, 270 khoản, 35 điểm, 9 phụ lục và 1 mở đầu. Các khoản dạng `3.1.` được nhận diện. Chỉ trích được phụ lục **A, B, C, D, E, F, G, I, K** vào văn bản QCVN. Phụ lục M/N/O/P ở nguồn ảnh chưa có chữ trích; chữ trong hình/biển báo cũng chưa được khôi phục đầy đủ. Không coi văn bản này đã đủ A–P.
- 12 phụ lục rỗng từng sinh từ mục lục QCVN đã được loại; hiện **0 phụ lục rỗng**. Các phụ lục dài vẫn cần cắt đoạn sau. Nhãn `k1)` ở khoản 4 Điều 41 NĐ 168 đã được tách thành điểm riêng. Khối chữ ký/Nơi nhận nay tách khỏi Điều cuối; `ket_thuc` tăng từ 2 lên 31.
- Bảng lồng ở 5 văn bản docx đã sửa lỗi lặp chữ. Phụ lục biểu mức thu của `tt_155_2025_btc` là `:pl1` và được giữ trong đầu ra có phiên bản. Không có `unit_id` hậu tố `#` trong bản ghi có hiệu lực.

## 2. Danh tính văn bản

`identity_report.csv`: **33/33 `ok`**. Với `tt_36_2024_byt`, số viết tay được OCR thành “36 /2024” và khớp sau chuẩn hóa.

## 3. Ngày hiệu lực

Ngày hiệu lực cuối cùng (`effective_dates.csv` do người duyệt giữ, **không bị `step_effective` ghi đè**; bản đề xuất tự động nằm ở `effective_dates_auto.csv`; `apply` chỉ đọc bản đã duyệt và báo lỗi rõ ràng nếu thiếu; cột `hl_chot`, đã người duyệt xác nhận; `nguon` = nguồn của ngày đó):

| doc_id | hl_chot | nguon | ghi chú |
|---|---|---|---|
| blds_2015 | 2017-01-01 | van_ban | Điều 689: "Bộ luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2017." Xác nhận. |
| luat_118_2025 | 2026-07-01 | khop | Điều 11 khoản 1: "từ ngày 01 tháng 7 năm 2026, trừ quy định tại khoản 2"; khoản 2: điểm a khoản 20 Điều 7 có hiệu lực từ 01/01/2026. Lấy ngày chung 2… |
| luat_35_2024 | 2025-01-01 | van_ban | Điều 85: khoản 1 "từ ngày 01 tháng 01 năm 2025, trừ khoản 2"; khoản 2: điểm a, b khoản 2 Điều 42, Điều 43, Điều 50, khoản 1 Điều 84 có hiệu lực từ 01… |
| luat_36_2024 | 2025-01-01 | van_ban | Điều 88: khoản 1 "từ ngày 01 tháng 01 năm 2025, trừ khoản 2"; khoản 2: khoản 3 Điều 10 có hiệu lực từ 01/01/2026. Ngày chung 2025-01-01; ngày riêng 2… |
| nd_10_2022 | 2022-03-01 | van_ban | Điều 14 khoản 1: "có hiệu lực từ ngày 01 tháng 3 năm 2022". |
| nd_138_2021 | 2022-01-01 | van_ban | Điều 18 khoản 1: "từ ngày 01 tháng 01 năm 2022". |
| nd_158_2024 | 2025-01-01 | van_ban | Điều 77 khoản 1: "từ ngày 01 tháng 01 năm 2025". |
| nd_160_2024 | 2025-01-01 | van_ban | Điều 40 khoản 1: "từ ngày 01 tháng 01 năm 2025". Riêng nghĩa vụ chuyển tiếp trước 01/7/2025 và 01/01/2026 (Điều 41). |
| nd_165_2024 | 2025-01-01 | van_ban | Điều 68 khoản 1: "từ ngày 01 tháng 01 năm 2025". |
| nd_168_2024 | 2025-01-01 | van_ban | Điều 53: khoản 1 "từ ngày 01 tháng 01 năm 2025, trừ khoản 2"; khoản 2: điểm m khoản 3 Điều 6, điểm e khoản 4 Điều 26, điểm b khoản 1 Điều 27 từ 01/01… |
| nd_175_2025 | 2025-07-01 | van_ban | Điều 2 khoản 1: "từ ngày 01 tháng 7 năm 2025". Xác nhận. |
| nd_218_2026 | 2026-08-10 | khop | Điều 39 khoản 1: "từ ngày 10 tháng 8 năm 2026". Xác nhận. |
| nd_220_2026 | 2026-07-01 | khop | Điều 10 khoản 1: "từ ngày 01 tháng 7 năm 2026". Xác nhận. |
| nd_238_2026 | 2026-08-15 | khop | Điều 20 khoản 1: "từ ngày 15 tháng 8 năm 2026". Xác nhận. |
| nd_241_2026 | 2026-07-01 | khop | Điều 26 khoản 1: "từ ngày 01 tháng 7 năm 2026". Xác nhận. |
| nd_336_2025 | 2026-03-01 | van_ban | Điều 26: "từ ngày 01 tháng 3 năm 2026". Xác nhận. |
| nd_39_2023 | 2023-07-01 | van_ban | Điều 25 khoản 1: "kể từ ngày 01 tháng 7 năm 2023"; khoản 2: thí điểm đấu giá biển số đến 01/7/2026. Ngày chung 2023-07-01. |
| nd_51_2025 | 2025-03-01 | ngay_ky | Điều 2: "có hiệu lực thi hành kể từ ngày ký ban hành"; ngày ký đầu văn bản "Hà Nội, ngày 01 tháng 3 năm 2025" -> 2025-03-01. Xác nhận. |
| nd_67_2023 | 2023-09-06 | ngay_ky | Điều 77: "có hiệu lực thi hành kể từ ngày ký ban hành"; ngày ký "Hà Nội, ngày 06 tháng 9 năm 2023" -> 2023-09-06. Xác nhận. |
| tt_108_2026_bca | 2026-07-01 | khop | Điều 41 khoản 1: "từ ngày 01 tháng 7 năm 2026, trừ khoản 2, 3, 4, 5". Ngày riêng: 01/3/2027 (nội dung sát hạch khoản 4 Điều 4), 01/01/2028 (bài sát h… |
| tt_12_2025_bca | 2025-03-01 | van_ban | Điều 38 khoản 1: "từ ngày 01 tháng 3 năm 2025". Xác nhận. |
| tt_155_2025_btc | 2026-01-01 | congbao | Đối chiếu ảnh PDF, Điều 8 khoản 1: "Thông tư này có hiệu lực từ ngày 01 tháng 01 năm 2026" (OCR đọc nhầm "0]"). Khớp công báo 2026-01-01; ngày ký 31/… |
| tt_30_2026_bxd | 2026-07-01 | khop | Điều 32 khoản 1: "kể từ ngày 01 tháng 7 năm 2026". Xác nhận. |
| tt_36_2024_byt | 2025-01-01 | khop | Điều 7 khoản 1: "có hiệu lực kể từ ngày 01 tháng 01 năm 2025". Xác nhận. |
| tt_37_2026_bca | 2026-06-08 | khop | Điều 7 khoản 1: "kể từ ngày 08 tháng 6 năm 2026". Xác nhận. |
| tt_38_2024_bgtvt | 2025-01-01 | van_ban | Điều 12: "kể từ ngày 01 tháng 01 năm 2025". Xác nhận. |
| tt_51_2024_bgtvt_qcvn41 | 2025-01-01 | van_ban | Điều 2 khoản 1: "kể từ ngày 01 tháng 01 năm 2025". Xác nhận. |
| tt_51_2025_bca | 2025-07-01 | van_ban | Điều 3 khoản 1: "từ ngày 01 tháng 7 năm 2025". Xác nhận. |
| tt_65_2024_bca | 2025-01-01 | van_ban | Điều 10: "từ ngày 01 tháng 01 năm 2025". Xác nhận. |
| tt_79_2024_bca | 2025-01-01 | van_ban | Điều 38 khoản 1: "kể từ ngày 01 tháng 01 năm 2025". Xác nhận. |
| vbhn_135_2025_blhs | 2025-07-01 | van_ban | Văn bản hợp nhất: phần mở đầu liệt kê Luật 86/2025/QH15 (25/6/2025) là luật sửa đổi mới nhất, "có hiệu lực kể từ ngày 01 tháng 01 năm 2018" là của BL… |
| vbhn_63_2025_xlvphc | 2025-07-01 | van_ban | Văn bản hợp nhất: phần mở đầu liệt kê Luật 88/2025/QH15 (25/6/2025) là luật sửa đổi mới nhất, "có hiệu lực kể từ ngày 01 tháng 7 năm 2025"; đổi từ ng… |

**Hai thay đổi so với bản đề xuất tự động (cả hai là văn bản hợp nhất):**

- `vbhn_135_2025_blhs`: 2018-01-01 → **2025-07-01** — phần mở đầu nêu Luật 86/2025/QH15 (25/6/2025) là luật sửa đổi mới nhất, có hiệu lực từ 01/7/2025. 2018-01-01 chỉ là ngày của bộ luật gốc.
- `vbhn_63_2025_xlvphc`: 2013-07-01 → **2025-07-01** — phần mở đầu nêu Luật 88/2025/QH15 (25/6/2025) có hiệu lực từ 01/7/2025. 2013-07-01 chỉ là ngày của luật gốc.

Các văn bản có nhiều mốc (tt_108_2026_bca, nd_168_2024, luat_35/36/118, nd_160_2024…) giữ ngày chung trong `hl_chot`; mốc riêng nằm ở `ghi_chu` và, với các điều khoản sửa đổi, ở cột `hl_rieng` (mục 4).

## 4. Sửa đổi (`amendments_reviewed.csv`)

Tổng **809 dòng**: **505 `duyet`** (được áp) và **304 `loai`**. (Bản nháp đã duyệt có 808 dòng; thêm 1 dòng do tách điểm b khoản 9 Điều 21 NĐ 158/2024, xem 4.4.)

### 4.1 Theo văn bản sửa đổi × hành động × trạng thái

| Văn bản sửa đổi | Hành động | duyet | loai | Cộng |
|---|---|---|---|---|
| luat_118_2025 | bai_bo | 3 | 7 | 10 |
| luat_118_2025 | bo_sung | 4 | 11 | 15 |
| luat_118_2025 | sua_doi | 75 | 94 | 169 |
| luat_118_2025 | thay_the_cum_tu | 0 | 53 | 53 |
| nd_175_2025 | sua_doi | 15 | 5 | 20 |
| nd_218_2026 | bai_bo | 15 | 1 | 16 |
| nd_218_2026 | bo_sung | 16 | 1 | 17 |
| nd_218_2026 | sua_doi | 126 | 35 | 161 |
| nd_218_2026 | thay_the_cum_tu | 0 | 15 | 15 |
| nd_220_2026 | bo_sung | 3 | 0 | 3 |
| nd_220_2026 | sua_doi | 45 | 1 | 46 |
| nd_220_2026 | thay_the_cum_tu | 0 | 6 | 6 |
| nd_238_2026 | bai_bo | 4 | 1 | 5 |
| nd_238_2026 | bo_sung | 14 | 0 | 14 |
| nd_238_2026 | sua_doi | 84 | 12 | 96 |
| nd_238_2026 | thay_the_cum_tu | 0 | 16 | 16 |
| nd_241_2026 | bai_bo | 1 | 1 | 2 |
| nd_241_2026 | bo_sung | 16 | 1 | 17 |
| nd_241_2026 | sua_doi | 73 | 23 | 96 |
| nd_241_2026 | thay_the_cum_tu | 0 | 11 | 11 |
| nd_51_2025 | sua_doi | 1 | 0 | 1 |
| tt_108_2026_bca | thay_the_van_ban | 1 | 0 | 1 |
| tt_37_2026_bca | bo_sung | 0 | 1 | 1 |
| tt_37_2026_bca | sua_doi | 2 | 2 | 4 |
| tt_37_2026_bca | thay_the_cum_tu | 0 | 1 | 1 |
| tt_51_2025_bca | sua_doi | 7 | 2 | 9 |
| tt_51_2025_bca | thay_the_cum_tu | 0 | 4 | 4 |
| **Tổng** |  | 505 | 304 | 809 |

### 4.2 Lý do loại

| Lý do | Số dòng |
|---|---|
| Văn bản đích ngoài kho (luật khác không nằm trong 33 văn bản) | 154 |
| Dòng cha, nội dung nằm ở các dòng con | 87 |
| Đã chuyển/gộp thành dòng `sua_doi`/`bai_bo` khác | 43 |
| Thay/bãi bỏ Phụ lục, Mẫu: không phải đơn vị Điều/khoản | 19 |
| Dòng nhiều địa chỉ, đã tách thành các dòng riêng | 1 |

### 4.3 Các dòng CAN_XEM và cách giải quyết

Bảng giữ **35 quyết định đã rà** từ đợt trước; hiện `amendments_reviewed.csv` còn **34 dòng chứa cờ CAN_XEM**, đều `duyet`. Dòng `k1)` số 23 đã được chuyển thành bổ sung điểm riêng và không còn cờ. Cột cuối là ghi chú đã duyệt (rút gọn).

| # | Văn bản sửa | Đích | Hành động | hl_rieng | Quyết định / lý do |
|---|---|---|---|---|---|
| 1 | nd_218_2026 | nd_158_2024 Đ7 | bo_sung | 2028-01-01 | hiệu lực riêng 2028-01-01 / hl_rieng: toàn bộ khoản 11 mới chỉ áp dụng từ 2028-01-01 (văn bản ghi 'Từ ngày 01/01/2028'). |
| 2 | nd_218_2026 | nd_158_2024 Đ12 k6 | sua_doi | - | khoản mới có ít điểm hơn khoản cũ (cũ a-c, mới không có điểm); thay toàn bộ theo văn bản sửa đổi |
| 3 | nd_218_2026 | nd_158_2024 Đ21 k1 | sua_doi | - | văn bản sửa đổi chỉ trích điểm a, b khoản 1; giữ nguyên câu dẫn "Thủ tục cấp Giấy phép kinh doanh" của khoản 1 |
| 4 | nd_218_2026 | nd_158_2024 Đ21 k5 | sua_doi | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống (ngày sớm nhất): đoạn cuối khoản chỉ áp dụng từ 2026-09-15 nhưng nằm trong cùng đơn vị, không tách được. |
| 5 | nd_218_2026 | nd_158_2024 Đ21 k7 b | sua_doi | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống (ngày sớm nhất): đoạn cuối điểm chỉ áp dụng từ 2026-09-15 nhưng nằm trong cùng đơn vị, không tách được. |
| 6 | nd_218_2026 | nd_158_2024 Đ21 k8 | bo_sung | 2026-09-15 | hiệu lực riêng 2026-09-15 / hl_rieng: điểm c mới chỉ áp dụng từ 2026-09-15 (văn bản ghi 'Từ ngày 15/9/2026'). |
| 7 | nd_218_2026 | nd_158_2024 Đ21 | bo_sung | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống: khoản 9 và điểm a áp dụng từ ngày của NĐ 218; điểm b tách thành dòng riêng (hl_rieng 2026-09-15). |
| 8 | nd_218_2026 | nd_158_2024 Đ22 k2 | sua_doi | - | sửa tên khoản kèm thay cụm từ "Sở Giao thông vận tải" -> "Sở Xây dựng" ở các điểm con; new_text gồm câu dẫn mới + các điểm a-d (điểm a theo Điều 9 khoản 2 NĐ 218) |
| 9 | nd_218_2026 | nd_158_2024 Đ23 k6 | sua_doi | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống (ngày sớm nhất): đoạn 'Từ ngày 15/9/2026' nằm trong điểm b của khoản, không tách được. |
| 10 | nd_218_2026 | nd_158_2024 Đ23 k9 | sua_doi | - | khoản mới có ít điểm hơn khoản cũ (cũ a-d, mới a-c); thay toàn bộ theo văn bản sửa đổi |
| 11 | nd_218_2026 | nd_158_2024 Đ23 k11 | sua_doi | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống (ngày sớm nhất): đoạn 'Từ ngày 15/9/2026' nằm trong điểm b của khoản, không tách được. |
| 12 | nd_218_2026 | nd_158_2024 Đ23 k12 | sua_doi | - | hiệu lực riêng 2026-09-15 / hl_rieng để trống (ngày sớm nhất): đoạn 'Từ ngày 15/9/2026' nằm trong điểm a của khoản, không tách được. |
| 13 | nd_218_2026 | nd_158_2024 Đ45 k3 | sua_doi | - | khoản mới có ít điểm hơn khoản cũ (cũ a-d, mới a-c); thay toàn bộ theo văn bản sửa đổi |
| 14 | nd_218_2026 | nd_158_2024 Đ45 k4 | sua_doi | - | khoản mới có ít điểm hơn khoản cũ (cũ a-b, mới không có điểm); thay toàn bộ theo văn bản sửa đổi |
| 15 | nd_218_2026 | nd_158_2024 Đ67 k2 | sua_doi | - | bỏ cụm từ kèm dấu phẩy liền trước để câu liền mạch; đã chuyển từ thay_the_cum_tu (d38:k1, d38:k8) |
| 16 | nd_218_2026 | nd_158_2024 Đ17 k3 | sua_doi | - | bỏ cụm từ kèm dấu phẩy liền trước để câu liền mạch; đã chuyển từ thay_the_cum_tu (d38:k8) |
| 17 | nd_238_2026 | nd_168_2024 Đ20 k5 l | sua_doi | - | hiệu lực hoãn theo Điều 18 NĐ 238 (01/01/2028) đối với xe dưới 08 chỗ, xe hàng, xe nội bộ; điểm l cũ vốn áp dụng xe từ 08 chỗ / hl_rieng để trống (ngày sớm nhất 2026-08-15): từ 2028-01-01 c… |
| 18 | nd_238_2026 | nd_168_2024 Đ20 k5 | bo_sung | 2029-01-01 | hiệu lực hoãn từ 01/01/2029 (Điều 18 khoản 4 NĐ 238); neo ở khoản 5 Điều 20 / hl_rieng: điểm n mới (thiết bị ghi nhận hình ảnh khoang chở khách) áp dụng từ 2029-01-01 theo Điều 18 khoản 4 N… |
| 19 | nd_238_2026 | nd_168_2024 Đ21 k3 b | sua_doi | - | hiệu lực hoãn 01/01/2028 (Điều 18 khoản 3 NĐ 238) đối với xe hàng (trừ đầu kéo) và xe nội bộ / hl_rieng để trống (ngày sớm nhất 2026-08-15): từ 2028-01-01 chỉ với xe hàng (trừ đầu kéo) và x… |
| 20 | nd_238_2026 | nd_168_2024 Đ26 k7 | bo_sung | 2029-01-01 | hiệu lực hoãn 01/01/2029 (Điều 18 khoản 4 NĐ 238); neo ở khoản 7 Điều 26 / hl_rieng: điểm k mới áp dụng từ 2029-01-01 theo Điều 18 khoản 4 NĐ 238. |
| 21 | nd_238_2026 | nd_168_2024 Đ26 k7 | bo_sung | 2029-01-01 | hiệu lực hoãn 01/01/2029 (Điều 18 khoản 4 NĐ 238); neo ở khoản 7 Điều 26 / hl_rieng: điểm l mới áp dụng từ 2029-01-01 theo Điều 18 khoản 4 NĐ 238. |
| 22 | nd_238_2026 | nd_168_2024 Đ32 | bo_sung | - | neo ở Điều 32; cá nhân 5-6 triệu, tổ chức 10-12 triệu; điểm b hiệu lực hoãn 01/01/2028 (xe nội bộ, Điều 18 khoản 3) / hl_rieng để trống (ngày sớm nhất 2026-08-15): điểm b chỉ hoãn đến 2028-… |
| 23 | nd_238_2026 | nd_168_2024 Đ41 k4 k1 | bo_sung | - | parser nhận diện `k1)`; dòng đã duyệt bổ sung điểm k1 riêng |
| 24 | nd_238_2026 | nd_168_2024 Đ53 | bo_sung | - | neo ở Điều 53; nêu hiệu lực hoãn 01/01/2028 cho thiết bị ghi nhận hình ảnh người lái xe với xe dưới 08 chỗ, xe hàng, xe nội bộ / hl_rieng để trống: đây là chính quy định về mốc 2028-01-01,… |
| 25 | nd_238_2026 | nd_168_2024 Đ32 k7 b | sua_doi | - | bỏ cụm từ kèm dấu "; " liền trước để câu liền mạch (kết quả "...biển số xe theo quy định;") |
| 26 | nd_238_2026 | nd_168_2024 Đ32 k7 d | sua_doi | - | bỏ cụm từ kèm dấu ", " liền trước (kết quả "...chứng nhận đăng ký xe nhưng chưa đến mức...") |
| 27 | nd_175_2025 | nd_10_2022 Đ8 k5 | sua_doi | - | sửa khoản 5 để giữ điểm c (bản NĐ 51/2025, hiệu lực 2025-03-01) vì sua_doi khoản sẽ đóng cả điểm con; gộp điểm a,b + tiêu đề + điểm d vào một dòng |
| 28 | nd_175_2025 | nd_10_2022 Đ13 | sua_doi | - | thay cả Điều 13; nguồn chỉ có khoản 1-4, khoản 5 gốc (trách nhiệm thi hành) sẽ bị bỏ; giữ tên Điều gốc |
| 29 | nd_220_2026 | nd_67_2023 Đ3 k5 | sua_doi | - | khoản 5 Điều 3 viết hoa "Người thứ ba" (tiêu đề khoản, đầu câu điểm a,b) cũng được đổi thành "Bên thứ ba" theo nghĩa của chỉ dẫn; từ thay cụm từ Điều 9 NĐ 220/2026 (khoản 1/2) |
| 30 | nd_220_2026 | nd_67_2023 Đ47 | sua_doi | - | từ thay cụm từ Điều 9 NĐ 220/2026 (khoản 1/3/4); viết lại cả d47 (17 đơn vị) vì cụm từ nằm trong tên Điều hoặc nhiều khoản |
| 31 | nd_220_2026 | nd_67_2023 Đ60 | sua_doi | - | từ thay cụm từ Điều 9 NĐ 220/2026 (khoản 1/4); viết lại cả d60 (16 đơn vị) vì cụm từ nằm trong tên Điều hoặc nhiều khoản |
| 32 | luat_118_2025 | luat_36_2024 Đ35 k2 | sua_doi | - | hiệu lực riêng 2028-01-01 (thiết bị ghi nhận hình ảnh người lái xe) và 2029-01-01 (khoang chở khách) theo khoản 2a Điều 88 do chính Luật 118 bổ sung; phần còn lại của khoản có hiệu lực 2026… |
| 33 | luat_118_2025 | luat_36_2024 Đ88 k2 | sua_doi | 2026-01-01 | hiệu lực riêng 2026-01-01 (Điều 11 khoản 2 Luật 118/2025: điểm a khoản 20 Điều 7 có hiệu lực từ 01/01/2026, các quy định khác 01/07/2026); pipeline chỉ dùng một ngày cho cả luật / hl_rieng:… |
| 34 | luat_118_2025 | luat_36_2024 Đ42 k5 | sua_doi | - | thay "Bộ Giao thông vận tải" thành "Bộ Xây dựng" ở khoản 5 Điều 42 và gộp luôn sửa điểm e khoản 5 (Luật 118 Điều 7 khoản 8 điểm b) vào cùng một dòng để không sửa hai lần cùng đơn vị |
| 35 | luat_118_2025 | luat_36_2024 Đ75 k3 | sua_doi | - | văn bản gốc viết "trực thuộc Trung ương" (chữ hoa), chỉ dẫn viết thường |

### 4.4 Dòng có ngày hiệu lực riêng (`hl_rieng`)

**7 dòng** có `hl_rieng`; `apply_amendments` dùng ngày này thay cho `hl[văn bản sửa]` để sắp xếp, đóng bản cũ và đặt `valid_from` của bản mới:

| Văn bản sửa | Đích | Hành động | hl_rieng | Lý do |
|---|---|---|---|---|
| nd_218_2026 | nd_158_2024 Đ7 | bo_sung | 2028-01-01 | hl_rieng: toàn bộ khoản 11 mới chỉ áp dụng từ 2028-01-01 (văn bản ghi 'Từ ngày 01/01/2028'). |
| nd_218_2026 | nd_158_2024 Đ21 k8 | bo_sung | 2026-09-15 | hl_rieng: điểm c mới chỉ áp dụng từ 2026-09-15 (văn bản ghi 'Từ ngày 15/9/2026'). |
| nd_218_2026 | nd_158_2024 Đ21 k9 | bo_sung | 2026-09-15 | Tách từ dòng khoản 9 Điều 21 NĐ 158/2024 (bo_sung khoản 9): điểm b chỉ áp dụng từ 2026-09-15 (văn bản ghi 'Từ ngày 15/9/2026'). |
| nd_238_2026 | nd_168_2024 Đ20 k5 | bo_sung | 2029-01-01 | hl_rieng: điểm n mới (thiết bị ghi nhận hình ảnh khoang chở khách) áp dụng từ 2029-01-01 theo Điều 18 khoản 4 NĐ 238. |
| nd_238_2026 | nd_168_2024 Đ26 k7 | bo_sung | 2029-01-01 | hl_rieng: điểm k mới áp dụng từ 2029-01-01 theo Điều 18 khoản 4 NĐ 238. |
| nd_238_2026 | nd_168_2024 Đ26 k7 | bo_sung | 2029-01-01 | hl_rieng: điểm l mới áp dụng từ 2029-01-01 theo Điều 18 khoản 4 NĐ 238. |
| luat_118_2025 | luat_36_2024 Đ88 k2 | sua_doi | 2026-01-01 | hl_rieng: Điều 11 khoản 2 Luật 118/2025: quy định tại điểm a khoản 20 Điều 7 có hiệu lực từ 2026-01-01 (các quy định khác 2026-07-01). |

Quy ước: nếu một dòng gồm nhiều mốc ngày mà không tách được thành đơn vị riêng (ví dụ khoản 2 Điều 35 Luật 36/2024 với mốc 2028-01-01 và 2029-01-01 nằm trong cùng câu; điểm l khoản 5 Điều 20, điểm b khoản 3 Điều 21, điểm b khoản 9a Điều 32 NĐ 168/2024 với xe nội bộ/xe hàng hoãn đến 2028-01-01; đoạn “Từ ngày 15/9/2026” nằm giữa điểm/khoản của NĐ 158/2024) thì **dùng ngày sớm nhất** (ngày của văn bản), `hl_rieng` để trống và ghi lý do vào `ghi_chu`. Khoản 9 Điều 21 NĐ 158/2024 được tách: khoản 9 + điểm a theo ngày NĐ 218/2026, điểm b là dòng riêng với `hl_rieng` = 2026-09-15.

## 5. Đầu ra có phiên bản (`legal_units_versioned.jsonl`)

| Chỉ số | Giá trị |
|---|---:|
| Tổng bản ghi | 18.790 |
| Có hiệu lực tại 2026-10-01 theo `in_force_at` | 17.423 |
| `valid_to` khác rỗng / rỗng | 1.380 / 17.410 |
| Bản ghi mới do sửa đổi (`source_doc_id` ≠ `doc_id`) | 1.004 |
| Bản ghi bắt đầu sau ngày chốt | 4 |
| Văn bản có đơn vị hiệu lực tại ngày chốt | 33 |

Bản ghi mới theo nguồn sửa đổi: `nd_218_2026` 320, `nd_241_2026` 232, `nd_238_2026` 174, `luat_118_2025` 118, `nd_220_2026` 117, `nd_175_2025` 33, `tt_51_2025_bca` 7, `tt_37_2026_bca` 2, `nd_51_2025` 1. Không có `version_id` trùng. Khoảng ngày gốc `[valid_from, valid_to)` của cùng `unit_id` **không chồng lấn** (0 cặp). Tại ngày chốt, ngoại lệ có điều kiện cho phép **3 cặp phiên bản cũ/mới cùng được trả về**: `luat_36_2024:d35:k2`, `nd_168_2024:d20:k5:l`, `nd_168_2024:d21:k3:b`; phải xét điều kiện theo loại xe và thời điểm trước khi chọn bản áp dụng.

### Trường mới và truy vấn hiệu lực

Mọi bản ghi phiên bản có `phan` (Phần của văn bản, hoặc `null`), `noi_dung_doi` (so tiêu đề và nội dung với phiên bản trước), `ty_le_am_tiet_loi` (heuristic dạng âm tiết), `chat_luong` (`ok`/`kem`), `loai_phu_luc` (`mau_bieu`/`noi_dung` với phụ lục; `null` ở cấp khác) và `hl_ngoai_le` (danh sách ngoại lệ đã duyệt cùng mốc, vai trò, điều kiện, căn cứ). `valid_to` là cận trên loại trừ. Dùng `in_force_at` để xét ngoại lệ, nhận `(có_hiệu_lực, điều_kiện)`:

```python
import json
import sys
from pathlib import Path

root = Path.cwd()  # chạy từ gốc repo
sys.path.insert(0, str(root / "src"))
from lawproc.validity import in_force_at

with (root / "data/processed/legal_units_versioned.jsonl").open(encoding="utf-8") as f:
    records = (json.loads(line) for line in f)
    live = [(r, condition) for r in records
            if (result := in_force_at(r, "2026-10-01"))[0]
            for condition in [result[1]]]
# Giữ condition khi hiển thị/lọc theo người, loại xe và mốc áp dụng.
```

### TT 108/2026 thay TT 12/2025

TT 108 thay TT 12 từ 2026-07-01, nhưng ngoại lệ `gia_han` giữ Điều 4 khoản 1–3 và Phụ lục II–VI của TT 12 đến **hết 28/02/2027** (`den_ngay=2027-03-01`, cận loại trừ). Phụ lục IV–VI chỉ còn hiệu lực ở một phần mục/mẫu; mô hình gia hạn cả đơn vị và gắn điều kiện văn bản. Người gọi phải mang theo ghi chú và điều kiện theo mục/mẫu, không chọn tùy ý một phiên bản sống.

## 6. Kiểm tra chất lượng

| Kiểm tra | Phát hiện | Cách xử lý | Kết quả |
|---|---|---|---|
| Danh tính văn bản | 33/33 `ok` trong `identity_report.csv` | So số hiệu, trích yếu với manifest | 33 văn bản đạt |
| Tải nhầm do trùng số hiệu | Bộ luật Dân sự từng bị nhầm; xem `data/COLLECTION_LOG.md` | Kiểm tra danh tính nguồn | Đã thay nguồn đúng; 33/33 `ok` |
| Điều thiếu khi ghép | 1 văn bản: VBHN BLHS thiếu Điều 90–107 | Đối chiếu phần đã bãi bỏ, giữ nguyên | Không tự sinh 18 Điều |
| OCR sửa tay | 97 dòng: TT 108 42, TT 36 17, TT 155 38 | Áp `ocr_corrections.csv`, báo lỗi nếu chuỗi không khớp duy nhất | 97 dòng được kiểm soát |
| OCR lại 400 dpi | 102 trang thử lại: TT 108 96, TT 36 6 | Chọn bản tốt hơn theo heuristic | 34 trang thay: TT 108 31, TT 36 3; tỷ lệ âm tiết lỗi theo văn bản TT 108 0,0095→0,0079, TT 36 0,0175→0,0139 |
| Chữ lặp do bảng lồng | 5 văn bản docx | Sửa duyệt bảng lồng trong extractor | Không còn lặp do đường duyệt cũ |
| Phần kết trong Điều cuối | Trước: 2 `ket_thuc` | Tách chữ ký/Nơi nhận | Sau: 31 `ket_thuc` |
| Mục lục nhận là phụ lục | 12 phụ lục rỗng QCVN | Bỏ dòng mục lục trước parse | 0 phụ lục rỗng |
| Nhãn điểm có chữ số | 1 dòng sửa đổi `k1)` NĐ 168 Đ41 k4 | Nhận điểm có chữ số, áp `bo_sung` | `:k1` riêng trong cây đơn vị |
| Ngoại lệ ngày hiệu lực | 22 dòng: 8 `gia_han`, 5 `hoan_ap_dung`, 9 `moc_trong_noi_dung` | Gắn `hl_ngoai_le`, lọc bằng `in_force_at` | 17.423 bản ghi sống tại ngày chốt, có điều kiện kèm theo |
| Phiên bản không đổi nội dung | 184 bản ghi `noi_dung_doi=false` | Đánh dấu so với phiên bản liền trước | Giữ cả 184 để truy vết nguồn |
| Phụ lục mẫu biểu | 107/158 `mau_bieu`, 51 `noi_dung` | Phân loại và áp bản đè đã duyệt | 158 phụ lục được gắn nhãn |
| Chất lượng chữ kém | 21 bản ghi, gồm 18 phụ lục | Gắn `chat_luong=kem`, giữ nguyên | Liệt kê dưới bảng; cần kiểm tra theo nguồn |
| Trùng mã đơn vị | 0 `unit_id` hậu tố `#` trong bản ghi sống | Kiểm tra bất biến | 0 |
| Chồng phiên bản | 0 cặp chồng khoảng ngày gốc | Test `test_no_overlapping_versions_per_unit` | 3 cặp cùng sống có điều kiện theo ngoại lệ, phải lọc tiếp |

21 đơn vị `chat_luong=kem`: `nd_158_2024:pl7`, `:pl8`, `:pl9`, `:pl12`; `nd_218_2026:pl2`, `:pl3`, `:pl5`; `qcvn_41_2024:d61:k1`; `tt_108_2026_bca:pl11`, `:pl13`; `tt_12_2025_bca:pl13`, `:pl16`; `tt_37_2026_bca:pl1`; `tt_79_2024_bca:pl1`–`:pl6`; `vbhn_135_2025_blhs:d235:k1:h`, `:d235:k2:đ`. Điểm xấu ở “kilômét” trong QCVN và “milisivơ” trong BLHS có thể là từ hợp lệ không khớp mẫu âm tiết, không mặc nhiên là lỗi OCR.

### Giới hạn đo OCR

Tỷ lệ âm tiết lỗi là **heuristic**, không đo độ đúng pháp lý và không bắt lỗi dấu, nghĩa, số hay bảng. Số mẫu đọc tay cũ dưới đây đo **trước đợt OCR 400 dpi**, chưa đo lại sau thay trang; không dùng chúng làm bằng chứng chất lượng hiện tại:

| Văn bản | Mẫu cũ | Từ sai lúc đo | Tỷ lệ lúc đo |
|---|---:|---:|---:|
| TT 108 | 10 đơn vị / 511 từ | 16 | 3,1% |
| TT 36 | 10 đơn vị / 240 từ | 28 | 11,7% |
| TT 155 | 10 đơn vị / khoảng 923 từ | khoảng 160 | khoảng 17% (mẫu gồm bảng hỏng trước sửa) |

## 7. Hạn chế và việc cần làm tiếp

- Phụ lục QCVN mới trích được A, B, C, D, E, F, G, I, K; M/N/O/P và nhiều hình là nguồn ảnh chưa có chữ. Phải khôi phục trước khi dùng như kho tra cứu đầy đủ.
- `tt_108_2026_bca:pl12` chỉ khoảng 138 ký tự; bảng chuyển đổi chưa có dù nhãn chất lượng `ok`. `nd_39_2023:pl1` chỉ còn dòng “ban hành kèm theo”, thiếu nội dung phụ lục. `tt_108_2026_bca:pl9` và `tt_12_2025_bca:pl10` chứa nội dung quy định trong phụ lục, cần cắt đoạn phù hợp. Các đơn vị `chat_luong=kem` nêu ở trên vẫn giữ và cần đối chiếu nguồn; nhãn `ok` không chứng minh nội dung đủ.
- TT 12 Phụ lục IV–VI chỉ được gia hạn một phần, còn mô hình theo cả đơn vị kèm điều kiện; người gọi phải xét mục/mẫu. Mỗi dòng sửa đổi chỉ có một ngày hiệu lực; phần có nhiều mốc trong cùng câu/đơn vị cần diễn giải điều kiện.
- Các dòng sửa đổi nhắm văn bản ngoài kho hoặc thay/bãi bỏ phụ lục không có địa chỉ Điều/khoản chưa được áp dụng. `line_start` trên bản ghi sinh từ sửa đổi là vị trí ở đoạn trích, không phải văn bản đích. Trường hợp biên bổ sung khoản và sửa chính khoản cùng ngày chưa xử lý.
