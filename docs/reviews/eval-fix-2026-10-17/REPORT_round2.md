# Sửa bộ eval theo review vòng 2 — 17/10/2026

Phản hồi [review vòng 2 của Codex](../eval-rereview-2026-10-17/REPORT.md). Làm theo đề nghị của review: giữ bản sửa vòng 1, chỉ sửa các điểm được nêu, không viết lại 270 câu.

Sau khi sửa, bộ eval vẫn là `data/eval/eval_v1.jsonl`, 270 câu, dev 30, test 240. Thành phần giữ nguyên: 150 thường, 40 sửa đổi, 30 ngoài phạm vi, 50 biến thể.

Thư mục `eval-rereview-2026-10-17/` của Codex không bị sửa hay chạy lại. Mọi thay đổi chỉ nằm trong `data/eval/`, `scripts/build_eval.py`, `src/lawproc/evalset.py`, `tests/test_evalset.py` và thư mục này.

**Lưu ý về id:** id lại đổi vì đã thay câu RQ3; đối chiếu bằng `key`. Id mới của các câu nhắc trong báo cáo này:

| Key | Id mới | Id Codex dùng |
|---|---|---|
| gp01 | TH049 | TH049 |
| gp06 | TH054 | TH054 |
| gp13 | TH061 | TH061 |
| ll05 | TH093 | TH093 |
| gp17 | TH065 | TH065 |
| xp01 | TH135 | TH135 |
| sd24 | SD010 | — |
| sd34 | SD020 | SD023 |
| sd47 | SD030 | SD035 |
| sd53–sd59 | SD034–SD040 | (câu mới) |

## 1. [P1] `sd49` và các câu RQ3 cùng dạng — đã thay 7 câu

**Đồng ý với Codex.** TT 47/2024 đã quy định cơ sở đăng kiểm chứng nhận xe cải tạo trước 01/7/2026, nhưng văn bản này không có trong kho. Đáp án cũ của `sd49` chỉ đúng với riêng câu chữ khoản 1 Điều 43 Luật 36, không đúng với thực tế áp dụng.

Codex đề nghị kiểm thêm các đáp án cũ dạng "chưa được quy định". Tôi rà lại cả 40 câu. Ngoài `sd49` có 6 câu cùng dạng: đáp án cũ dựa trên việc **bản cũ chưa có** một quy định, nên dễ bị một văn bản ngoài kho phủ mất. Tôi chưa chứng minh từng câu này sai. Nhưng tôi không chứng minh được câu nào đúng chắc chắn, nên thay cả 7 câu thay vì giữ lại câu còn nghi.

| Key bỏ | Nội dung | Rủi ro |
|---|---|---|
| sd49 | Cơ sở đăng kiểm chứng nhận xe cải tạo | TT 47/2024 đã quy định (Codex chỉ ra) |
| sd09 | Chở vật liệu xây dựng trên xe không có thành thùng | Hành vi có thể đã bị phạt theo điểm khác về chở hàng rời, không che phủ |
| sd11 | Thu hồi GPLX khi gian dối để được cấp, đổi | Việc thu hồi GPLX cấp sai có thể đã có ở thông tư về GPLX |
| sd23 | Xe máy chuyên dùng, xe bốn bánh có gắn động cơ chịu lệ phí trước bạ | Đối tượng có thể đã được nêu ở văn bản lệ phí khác |
| sd39 | Xe bán tải cabin kép tổ chức giao thông như xe con | Cách phân loại có thể đã có trong quy chuẩn kỹ thuật |
| sd42 | Chở thiết bị hình dạng như công-ten-nơ vượt chiều dài | Có thể đã bị phạt theo hành vi chở hàng vượt kích thước |
| sd50 | Dữ liệu điện tử chuyển quyền sở hữu thay bản giấy | Luật Giao dịch điện tử 2023 đã cho dữ liệu điện tử giá trị pháp lý |

**7 câu thay thế:** cả 7 đều là cặp **thời hạn bằng số**, cùng một câu hỏi có hai đáp án khác nhau ở hai ngày. Mỗi cặp đã đọc cả hai phiên bản trong kho. Thời hạn giải quyết thủ tục không phụ thuộc thẩm quyền hay bộ máy, nên không vướng NĐ 189/2025 hay việc bỏ cấp huyện.

| Id | Key | Thủ tục | Cũ → mới | Căn cứ mới (hiệu lực) |
|---|---|---|---|---|
| SD034 | sd53 | Chấp thuận biển quảng cáo trong phạm vi bảo vệ kết cấu hạ tầng đường bộ | 07 → 05 ngày làm việc | điểm c khoản 3 Điều 18 NĐ 165/2024 (01/7/2026) |
| SD035 | sd54 | Thẩm định, phê duyệt phương án tổ chức giao thông cao tốc | 15 → 12 ngày làm việc | điểm c khoản 4 Điều 26 NĐ 165/2024 (01/7/2026) |
| SD036 | sd55 | Chấp thuận đấu nối tạm thời vào quốc lộ | 07 → 05 ngày làm việc | điểm c khoản 5 Điều 31 NĐ 165/2024 (01/7/2026) |
| SD037 | sd56 | Gia hạn lưu hành phương tiện ASEAN | 02 → 01 ngày làm việc | điểm b khoản 4 Điều 34 NĐ 158/2024 (10/8/2026) |
| SD038 | sd57 | Cấp Giấy phép vận tải quốc tế Việt Nam – Lào | 02 → 01 ngày làm việc | điểm c khoản 4 Điều 51 NĐ 158/2024 (10/8/2026) |
| SD039 | sd58 | Cấp Giấy phép liên vận GMS hoặc sổ TAD | 02 → 01 ngày làm việc | điểm c khoản 4 Điều 37 NĐ 158/2024 (10/8/2026) |
| SD040 | sd59 | Cấp bản sao chứng nhận thu hồi đăng ký, biển số xe | 30 ngày xác minh + 02 ngày làm việc → 02 ngày làm việc | điểm d khoản 3 Điều 7 TT 79/2024 (18/5/2026) |

Sau khi thay, câu sửa đổi lấy từ 10 văn bản (trước là 11; TT 37/2026 không còn câu nào). README đã cập nhật bảng này và thêm quy tắc chọn: ưu tiên cặp khác số, tránh đáp án cũ dạng "bản cũ chưa quy định".

## 2. [P1] `so_lieu` bỏ mất ngưỡng đạt và loại ngày — đã sửa

| Lỗi Codex nêu | Sửa | Kết quả |
|---|---|---|
| `gp13`: "27/30 điểm" chỉ ghi 30 điểm | Thêm mẫu tỷ lệ (`RATIO`): "27/30 điểm" là một số liệu riêng, giữ cả tử số và mẫu số. Hai số trong tỷ lệ không bị tách thành số liệu lẻ | `gp13`: `["27/30", "điểm"]`; `gp06`: `["23/25", "điểm"]` |
| Đổi 27/30 → 26/30 vẫn pass | Tỷ lệ phải xuất hiện nguyên dạng trong căn cứ | Bị bắt: "26/30 điểm" không có trong căn cứ |
| "ngày làm việc" gộp thành "ngày" | "ngày làm việc", "giờ làm việc" là đơn vị riêng | `sd24`: `[2, "ngày làm việc"]` |
| Đổi "02 ngày làm việc" → "02 ngày" vẫn pass | Số liệu "02 ngày" phải có dạng "ngày" (không kèm "làm việc") trong căn cứ | Bị bắt |

Về đề nghị gắn vai trò (`diem_dat`, `tong_diem`, `thoi_han`…): **chưa làm**, đã ghi vào hạn chế trong README. Lý do: cách giữ nguyên tỷ lệ và tách loại ngày đã đủ bắt cả hai lỗi Codex nêu. Gắn vai trò cho mọi số liệu phải thêm một tầng nhãn tay cho 106 câu.

## 3. [P1] Nhóm căn cứ OR thay cho AND — đã sửa

**Đồng ý với Codex.** Các Điểm trong một Khoản bổ sung nội dung cho nhau, không thay thế được cho nhau.

- **Mã:** `build_eval.py` không còn gom theo Khoản. Mỗi căn cứ thành một nhóm riêng: `nhom_can_cu = [[vid] for vid in can_cu]`. Các nhóm là ý bắt buộc (AND). Trong một nhóm vẫn có thể liệt kê nhiều phiên bản thay thế được cho nhau (OR), nhưng hiện chưa có câu nào cần.
- **Rubric (README):**
  - Một chunk chỉ đạt các đơn vị mà nó **thực sự chứa**.
  - Chunk theo Khoản hoặc Điều đạt mọi Điểm có trong nó.
  - Chunk chỉ có câu dẫn, hoặc chỉ có một Điểm, không đại diện cho cả Khoản.
- **Ví dụ Codex nêu:**
  - `gp01` nay có 5 nhóm. Chỉ tìm được điểm a thì `all` = sai.
  - `ll05` nay có 8 nhóm: câu dẫn và 7 Điểm. Câu dẫn chỉ đạt nhóm của chính nó.
- **Mẫu số mới:** 108 câu cần từ 2 nhóm trở lên (104 thường + 4 sửa đổi). Trước đây là 74 câu, vì một Khoản nhiều Điểm từng chỉ tính là 1 nhóm. README có bảng phân phối số nhóm (tối đa 8).
- **Test:** `test_each_citation_is_a_required_group` kiểm `gp01` có 5 nhóm và câu dẫn của `ll05` là một nhóm riêng.

**Chưa làm:** test "chỉ tìm một Điểm" và "tìm chunk đầy đủ" ở mức scorer, vì repo chưa có scorer retrieval. Việc này để sang bước G3, đã ghi vào hạn chế.

## 4. [P2] Ngoại lệ của `sd47` và kiểm khoảng phạt — đã sửa

**`sd47` (SD030):**
- Đáp án nay nêu đủ ba trường hợp không áp dụng hạn chế cấp lại phù hiệu:
  - chuyển quyền sử dụng hoặc sở hữu xe;
  - điểm đ khoản 10 Điều 23: xe đã chuyển nhượng hoặc cho đơn vị khác thuê;
  - điểm e khoản 10 Điều 23: đơn vị báo cáo không tiếp tục dùng xe để kinh doanh vận tải.
- Căn cứ thêm hai phiên bản: `nd_158_2024:d23:k10:đ@2025-01-01` và `nd_158_2024:d23:k10:e@2026-08-10`.

**Kiểm khoảng phạt:** thêm hai quy tắc.
- Nếu câu có `muc_phat_min`, `muc_phat_max` thì đáp án phải chứa đúng khoảng "từ `min` đồng đến `max` đồng".
- Mọi khoảng "từ X đến Y" trong đáp án và đáp án cũ phải có trong căn cứ.

Phép thử của Codex (`xp01`: "từ 400.000" → "từ 600.000") nay bị bắt.

## 5. Các điểm giới hạn

| Điểm | Xử lý |
|---|---|
| Họ sự kiện cho bootstrap | Thêm trường `ho_su_kien` = Khoản chính (`dia_chi_chinh`). Câu thường và câu sửa đổi cùng hỏi một Khoản thì chung một họ. Biến thể chép họ từ câu gốc. Ví dụ `gp17` (TH065) và `sd34` (SD020) cùng họ `tt_108_2026_bca:d19:k1`. Có 171 họ cho 190 câu, 16 họ có từ 2 câu trở lên. Test: `test_event_family_links_regular_and_amended_questions` |
| Hash khi đóng băng | Thêm `data/eval/MANIFEST.json`, ghi lại mỗi lần build. Nội dung: SHA-256 của eval, split, từng file nháp, dữ liệu nguồn, và git blob của dữ liệu trong tag `data-v1`. Test: `test_manifest_hash_matches_eval_file` |
| Câu ngoài phạm vi khó hơn | Vẫn **chưa làm**, giữ trong hạn chế |
| Chưa có chuyên gia duyệt | Giữ trong hạn chế |
| Không ghi đè bằng chứng review | Đã tuân thủ: không chạy lại `audit_eval.py`, không sửa file nào trong `eval-rereview-2026-10-17/` |

## 6. Phép thử của vòng 2 thành test cố định

`test_round_two_mutations_are_rejected` chạy theo `key` trên bản sao trong bộ nhớ, và kiểm phép sửa thực sự làm thay đổi dữ liệu:

| Key | Phép sửa | Bị bắt bởi |
|---|---|---|
| gp13 | 27/30 → 26/30 điểm | Tỷ lệ không có trong căn cứ |
| sd24 | 02 ngày làm việc → 02 ngày | Số liệu "02 ngày" không có trong căn cứ |
| xp01 | từ 400.000 → từ 600.000 đồng | Đáp án thiếu khoảng phạt của nhãn, và khoảng mới không có trong căn cứ |

Sáu phép thử của vòng 1 vẫn là test (`test_review_mutations_are_rejected`).

## Kiểm tra

- `py -3.13 scripts/build_eval.py`: hợp lệ, 270 câu; đã ghi `split_v1.json`, `eval_v1.jsonl`, `MANIFEST.json`.
- `py -3.13 -m pytest -q tests/test_evalset.py`: 31 test qua.
- Toàn dự án `py -3.13 -m pytest -q`: 306 test qua.
