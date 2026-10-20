# G8 — Chấm nội dung (LLM-Judge) trên tập test

Nguồn: `reports/g8/judge_claude.jsonl`. Giám khảo: claude-opus-5-5 (trong phiên). Giá trị % [CI95 bootstrap theo cụm]; hiệu số đánh dấu `*` khi CI95 không chứa 0. **Đạt** = đủ ý chính và kết luận đúng so với đáp án chuẩn (câu ngoài phạm vi: từ chối đúng).

## Tỷ lệ đạt

| Nhóm | n | D | B | D_g8 | B_g8 |
|---|---|---|---|---|---|
| Trong phạm vi (thường + sửa đổi) | 170 | 85.9 [80.3–91.0] | 82.4 [76.0–87.9] | 87.1 [81.7–92.1] | 85.3 [79.9–90.4] |
| Thường | 134 | 83.6 [76.9–89.6] | 82.1 [75.4–88.8] | 85.8 [79.9–91.0] | 85.1 [79.1–91.0] |
| Sửa đổi | 36 | 94.4 [86.1–100.0] | 83.3 [69.4–94.4] | 91.7 [83.3–100.0] | 86.1 [75.0–97.2] |
| Biến thể | 44 | 36.4 [22.7–50.0] | 38.6 [25.0–52.3] | 40.9 [27.3–56.8] | 40.9 [27.3–54.5] |
| Ngoài phạm vi | 26 | 92.3 [80.8–100.0] | 92.3 [80.8–100.0] | 92.3 [80.8–100.0] | 88.5 [73.1–100.0] |

## Hiệu số ghép cặp (điểm %)

| Cặp | Trong phạm vi | Thường | Sửa đổi | Biến thể | Ngoài phạm vi |
|---|---|---|---|---|---|
| D-B | +3.5 [-1.8, +8.8] | +1.5 [-5.2, +7.5] | +11.1 [+2.8, +22.2] * | -2.3 [-13.6, +6.8] | +0.0 [-11.5, +11.5] |
| D_g8-D | +1.2 [-2.4, +4.8] | +2.2 [-1.5, +6.7] | -2.8 [-8.3, +0.0] | +4.5 [+0.0, +11.4] | +0.0 [+0.0, +0.0] |
| B_g8-B | +2.9 [-2.4, +8.4] | +3.0 [-2.2, +9.0] | +2.8 [-8.3, +13.9] | +2.3 [-11.4, +15.9] | -3.8 [-15.4, +7.7] |
| D_g8-B_g8 | +1.8 [-3.6, +7.4] | +0.7 [-5.2, +6.7] | +5.6 [-8.3, +19.4] | +0.0 [-9.1, +9.1] | +3.8 [-7.7, +15.4] |

D-B, trong phạm vi: chỉ D đạt 15 câu, chỉ B đạt 9 câu (trên 170).

D_g8-D, trong phạm vi: chỉ D_g8 đạt 6 câu, chỉ D đạt 4 câu (trên 170).

B_g8-B, trong phạm vi: chỉ B_g8 đạt 13 câu, chỉ B đạt 8 câu (trên 170).

D_g8-B_g8, trong phạm vi: chỉ D_g8 đạt 13 câu, chỉ B_g8 đạt 10 câu (trên 170).

## Câu đổi kết quả D->D_g8 (cả tập test)

- Sai thành đúng: 8 câu; theo nhóm lỗi tự động ở G7: dung 3, khong_co_can_cu 1, loi_sinh 2, thieu_mot_phan 2
- Đúng thành sai: 4 câu: `sua_doi/sd58` (Trả lời thời hạn hiệu lực của giấy phép thay vì thời hạn cấp (01 ngày làm việc).); `thuong/dk04` (Chỉ dẫn chiếu thủ tục, không liệt kê giấy tờ (chứng từ chuyển quyền, lệ phí trước bạ, chứng nhận thu hồi).); `thuong/ll08` (Kết luận "không đúng" trái đáp án (được chở trẻ dưới 12 tuổi).); `thuong/np06` (Nêu trường hợp nộp tại chỗ thay vì nguyên tắc nộp tại Kho bạc Nhà nước.)

## Câu đổi kết quả B->B_g8 (cả tập test)

- Sai thành đúng: 19 câu; theo nhóm lỗi tự động ở G7: dung 9, khong_co_can_cu 3, loi_sinh 3, ngoai_pham_vi 1, thieu_mot_phan 2, tu_choi_sai 1
- Đúng thành sai: 14 câu: `bien_the/bt16` (Kết luận có bị phạt đúng nhưng mức phạt 100-200 nghìn sai (đúng 800.000-1.000.000 đồng).); `bien_the/bt17` (Nói không có căn cứ, rồi nêu mức phạt theo NĐ 100/2019 đã hết hiệu lực.); `bien_the/bt18` (Từ chối sai và nêu ngưỡng cồn sai.); `bien_the/bt26` (Nêu xe gắn máy 50 km/h; đáp án 40 km/h cho cả hai loại.); `ngoai_pham_vi/np04` (Không từ chối, áp quy định đường bộ cho đường sắt.); `ngoai_pham_vi/np05` (Từ chối nhưng kèm thông tin bịa (lái tàu do quân đội, công an quản lý theo khoản 9 Điều 60).); `sua_doi/sd08` (Sai đối tượng (ô tô) và sai mức phạt (4-6 triệu).); `sua_doi/sd28` (Kết luận "không" theo bản cũ (Công an xã chỉ đăng ký mô tô).); `thuong/bh10` (Kết luận "vẫn bồi thường" trái đáp án (không lái xe không GPLX là loại trừ).); `thuong/dk03` (Trộn hồ sơ sang tên (lệ phí trước bạ, chứng nhận thu hồi) vào hồ sơ thu hồi; thiếu bản chà và nộp lại đăng ký, biển số.); `thuong/hd13` (Nói không có căn cứ, cho rằng dựng rạp tang lễ không phải mục đích hợp pháp.); `thuong/ll04` (Nêu có ngưỡng cồn cho phép (0,02 và 0,25 mg/l); luật cấm mọi nồng độ cồn.); `thuong/lp07` (Xếp TP. Hồ Chí Minh vào khu vực II, kết luận 105.000 đồng (đúng là 1.400.000 đồng).); `thuong/td08` (Nêu 80 km/h cho đường hai chiều (đúng là 70 km/h).)

## Lỗi nghiêm trọng

| Chỉ số | D | B | D_g8 | B_g8 |
|---|---|---|---|---|
| Nêu sai chế tài (trong phạm vi) | 1.2 [0.0–3.0] | 10.0 [6.0–14.6] | 0.0 [0.0–0.0] | 5.9 [2.4–10.1] |
| Trả lời theo luật cũ (câu sửa đổi) | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 2.8 [0.0–8.3] |

## Theo loại câu (trong phạm vi)

| Loại câu | n | D | B | D_g8 | B_g8 |
|---|---|---|---|---|---|
| chung | 40 | 95.0 [87.5–100.0] | 90.0 [80.0–97.6] | 97.5 [92.3–100.0] | 95.0 [87.2–100.0] |
| hành vi cấm | 8 | 75.0 [37.5–100.0] | 87.5 [62.5–100.0] | 75.0 [37.5–100.0] | 75.0 [37.5–100.0] |
| mức phạt | 11 | 63.6 [36.4–90.9] | 45.5 [18.2–72.7] | 63.6 [36.4–90.9] | 45.5 [18.2–72.7] |
| thủ tục | 63 | 88.9 [80.6–95.3] | 88.9 [79.4–96.8] | 90.5 [82.3–96.9] | 90.5 [83.1–96.8] |
| tình huống | 39 | 79.5 [65.8–90.2] | 69.2 [53.7–84.2] | 76.9 [63.2–89.7] | 76.9 [63.2–89.5] |
| định nghĩa | 9 | 88.9 [66.7–100.0] | 100.0 [100.0–100.0] | 100.0 [100.0–100.0] | 100.0 [100.0–100.0] |

## So với nhóm lỗi tự động (`loi_*.csv`, thường + sửa đổi + biến thể)

| Lượt | Nhóm lỗi tự động | Judge đạt | Judge không đạt |
|---|---|---|---|
| D | dung | 116 | 8 |
| D | khong_co_can_cu | 5 | 9 |
| D | loi_sinh | 27 | 6 |
| D | thieu_mot_phan | 14 | 13 |
| D | tu_choi_sai | 0 | 16 |
| B | dung | 121 | 12 |
| B | khong_co_can_cu | 8 | 12 |
| B | loi_sinh | 21 | 6 |
| B | thieu_mot_phan | 6 | 14 |
| B | tu_choi_sai | 1 | 13 |

## Khớp với chỉ số tự động (trong phạm vi)

| Lượt | Số liệu đủ & đạt | Số liệu đủ & không đạt | Số liệu thiếu & đạt | Số liệu thiếu & không đạt |
|---|---|---|---|---|
| D | 56 | 1 | 27 | 11 |
| B | 52 | 6 | 21 | 16 |

Chưa có chấm tay: điền cột `dat_D`, `dat_B` (0/1) trong `cham_tay_50.csv` rồi chạy lại script.
