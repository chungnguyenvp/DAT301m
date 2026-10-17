# Bộ eval `eval_v1`

- **Ngày đóng băng:** 2026-10-17, bản sửa sau hai vòng review độc lập.
  - Vòng 1: [docs/reviews/eval-fix-2026-10-17/REPORT.md](../../docs/reviews/eval-fix-2026-10-17/REPORT.md).
  - Vòng 2: [REPORT_round2.md](../../docs/reviews/eval-fix-2026-10-17/REPORT_round2.md).
- **Dữ liệu gốc:** tag `data-v1` (`data/processed/legal_units_versioned.jsonl`).
- **Ngày hỏi mặc định:** 2026-10-01 (`config.CUTOFF`). Mọi đáp án đúng theo quy định áp dụng tại ngày này.
- **File chính:** `eval_v1.jsonl`, 270 câu. Không sửa tay file này. Sửa ở `drafts/` rồi build lại.
- **Tập dev/test:** đóng băng trong `split_v1.json`, khóa theo `nhom_cau/key`. Câu có `key` mới mặc định vào test; biến thể luôn theo tập của câu gốc. `id` (TH001…) có thể đổi khi chèn câu vào nháp, còn `key` thì không.
- **Mã băm:** `MANIFEST.json` ghi SHA-256 của bộ eval, split, từng file nháp và dữ liệu nguồn (kèm git blob trong tag `data-v1`). Build lại sẽ ghi lại file này. Khi báo cáo kết quả, ghi kèm hash `eval` trong manifest. File trong `data/eval/` luôn checkout với LF (`.gitattributes`) nên hash không đổi theo máy. Riêng hash `source.sha256` tính trên bản trong thư mục làm việc, có thể khác nếu git đổi xuống dòng; mã ổn định của dữ liệu nguồn là `git_blob_in_tag_data_v1`.

## Thành phần

| Nhóm (`nhom_cau`) | Tiền tố id | Số câu | Dev | Test | Dùng cho |
|---|---|---:|---:|---:|---|
| `thuong` | TH | 150 | 16 | 134 | RQ1, RQ2 |
| `sua_doi` | SD | 40 | 4 | 36 | RQ3 |
| `ngoai_pham_vi` | NP | 30 | 4 | 26 | Từ chối đúng / từ chối sai |
| `bien_the` | BT | 50 | 6 | 44 | Độ bền với cách hỏi đời thường |
| **Tổng** | | **270** | **30** | **240** | |

**Câu thường:** khớp đúng từng ô của `eval_matrix.csv`.

**Câu sửa đổi:** lấy từ 10 văn bản sửa đổi hoặc thay thế (trường `van_ban_sua_doi`):

| Văn bản | Số câu |
|---|---:|
| NĐ 218/2026 | 13 |
| Luật 118/2025 | 5 |
| TT 62/2026 | 5 |
| NĐ 238/2026 | 4 |
| TT 108/2026 (thay TT 12/2025) | 4 |
| NĐ 241/2026 | 4 |
| NĐ 175/2025 | 2 |
| TT 51/2025, NĐ 47/2026, TT 105/2026 | mỗi văn bản 1 |

Quy tắc chọn câu sửa đổi:
- Chỉ chọn thay đổi về **nội dung** (hành vi, mức tiền, thời hạn, ngưỡng, thủ tục).
- **Không** chọn thay đổi chỉ do sắp xếp bộ máy: đổi tên bộ, bỏ cấp huyện, chuyển chức năng GPLX sang Bộ Công an, thẩm quyền xử phạt theo NĐ 189/2025. Lý do: các thay đổi đó đã áp dụng thực tế trước khi câu chữ trong kho được sửa.
- **Ưu tiên** cặp mà cùng một câu hỏi có hai đáp án khác nhau rõ ràng ở hai ngày, tốt nhất là khác số (ví dụ 07 → 05 ngày làm việc).
- **Tránh** đáp án cũ dạng "bản cũ chưa quy định". Văn bản khác ngoài kho có thể đã quy định việc đó từ trước (ví dụ TT 47/2024 về xe cải tạo).

**Câu ngoài phạm vi:** chia theo `kieu_ngoai`:
- đường sắt 5, đường thủy 4, hàng không 3, hàng hải 1;
- quy định địa phương hoặc giá cụ thể 4;
- văn bản cũ đã hết hiệu lực 4;
- không liên quan 7;
- thông tin thị trường 2.

**Biến thể:** 50 câu viết lại từ câu thường, chia theo `kieu_bien_the`: từ đời thường 16, viết tắt 12, không dấu 11, kể chuyện 11. Đây là phép đo độ bền của 50 câu gốc, không phải 50 tình huống độc lập. Bảng đối chiếu từng cặp: [bien_the_review.csv](../../docs/reviews/eval-fix-2026-10-17/bien_the_review.csv).

## Các trường

| Trường | Ý nghĩa |
|---|---|
| `id`, `key`, `tap`, `nhom_cau`, `chu_de`, `loai_cau` | Định danh, tập, nhóm, chủ đề, loại câu |
| `cau_hoi`, `dap_an` | Câu hỏi và đáp án chuẩn có trích Điều, Khoản, Điểm |
| `can_cu` | Mọi `version_id` làm căn cứ, có hiệu lực tại `ngay_hoi` |
| `nhom_can_cu` | Danh sách ý bắt buộc (quan hệ AND). Mỗi nhóm là một ý; trong nhóm là các phiên bản thay thế được cho nhau (OR). Hiện mỗi căn cứ là một nhóm riêng, chưa liệt kê phương án thay thế nào |
| `van_ban`, `dieu`, `khoan`, `diem`, `dia_chi_chinh` | Địa chỉ căn cứ chính; `dia_chi_chinh` ở mức Khoản |
| `muc_phat_min`, `muc_phat_max` | Khung phạt tiền cá nhân của hành vi (null nếu câu không hỏi mức phạt tiền) |
| `diem_tru`, `trang_thai_diem_tru` | Số điểm GPLX bị trừ. Trạng thái: `co` (có trừ), `khong_tru` (Điều có quy định trừ điểm nhưng không áp cho hành vi này), `khong_ap_dung` (câu không thuộc loại này) |
| `tuoc_gplx_thang` | `[min, max]` số tháng tước GPLX hoặc null |
| `so_lieu` | Mọi cặp `[giá trị, đơn vị]` trong đáp án; đều đã kiểm có trong căn cứ hoặc trong câu hỏi. Xem chi tiết bên dưới |
| `ngay_hoi` | Ngày hỏi |
| `dap_an_cu`, `can_cu_cu`, `ngay_cu`, `van_ban_sua_doi` | Chỉ có ở câu sửa đổi |
| `hanh_vi`, `ly_do`, `kieu_ngoai` | Chỉ có ở câu ngoài phạm vi (`hanh_vi = tu_choi`) |
| `goc_id`, `kieu_bien_the` | Chỉ có ở biến thể |
| `ho_cau` | Họ câu: biến thể mang id câu gốc, câu khác mang id của chính nó |
| `ho_su_kien` | Họ sự kiện pháp lý: các câu cùng hỏi về một Khoản chung một họ (= `dia_chi_chinh`), kể cả câu thường và câu sửa đổi. Ví dụ `gp17` và `sd34` cùng hỏi thời hạn cấp GPLX. Biến thể chép từ câu gốc; câu ngoài phạm vi mang id của chính nó. Có 171 họ cho 190 câu thường và sửa đổi, 16 họ có từ 2 câu trở lên |
| `trung_dev` | Câu test dùng chung ít nhất một `version_id` với câu dev (13 câu). Bình thường với kho đóng, nhưng nên báo cáo riêng |
| `ghi_chu` | Lưu ý khi chấm |

**Chi tiết `so_lieu`:**
- Đơn vị gồm đồng (mọi cách viết), ngày, ngày làm việc, giờ, giờ làm việc, tháng, năm, %, km/h, mét, tuổi, điểm, câu, phút…
- "Ngày làm việc" là đơn vị riêng, không gộp với "ngày". Đổi "02 ngày làm việc" thành "02 ngày" là sai.
- Ngưỡng dạng tỷ lệ giữ nguyên cả tử số và mẫu số. Ví dụ `["27/30", "điểm"]`: trả lời 26/30 là sai, trả lời 30 điểm cũng không thay được.

`trang_thai_diem_tru`, `tuoc_gplx_thang`, `nhom_can_cu`, `so_lieu`, `dia_chi_chinh`, `ho_cau`, `ho_su_kien`, `trung_dev` đều do `scripts/build_eval.py` tự suy từ dữ liệu. Trừ điểm và tước GPLX lấy từ các khoản "Thực hiện hành vi quy định tại … Điều này bị trừ / bị tước …" có liệt kê đúng hành vi.

## Cách chấm (rubric)

Báo cáo **riêng từng nhóm câu** và luôn ghi mẫu số. Khoảng tin cậy dùng bootstrap theo `ho_cau`. Khi gộp câu thường với câu sửa đổi, dùng `ho_su_kien`.

1. **Tìm kiếm (câu thường và câu sửa đổi):**
   - `Recall@k-any`: tìm được ít nhất một nhóm trong `nhom_can_cu`.
   - `Recall@k-all`: tìm đủ **mọi** nhóm.
   - Recall đúng văn bản: so `van_ban`.

   **Khi nào một nhóm đạt:**
   - Kết quả trả về có một phiên bản trong nhóm; hoặc
   - Kết quả có một chunk **thực sự chứa** đơn vị đó. Chunk theo Điều hoặc Khoản được tính cho mọi Điểm có trong chunk.

   **Khi nào không đạt:** chunk chỉ chứa câu dẫn của Khoản, hoặc chỉ chứa một Điểm, chỉ đạt đúng đơn vị nó chứa. Ví dụ:
   - `gp01` cần đủ 5 Điểm a–đ khoản 1 Điều 21 TT 108. Tìm được riêng điểm a thì đạt 1/5 nhóm, `all` = sai.
   - `ll05` cần câu dẫn và 7 Điểm của khoản 3 Điều 33. Riêng câu dẫn không đạt các Điểm.

   **Phân phối số nhóm:** có 108 câu cần từ 2 nhóm trở lên (104 câu thường + 4 câu sửa đổi). Số câu theo số nhóm:

   | Số nhóm | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
   |---|---:|---:|---:|---:|---:|---:|---:|---:|
   | Số câu | 82 | 49 | 32 | 16 | 5 | 4 | 1 | 1 |

   Với k nhỏ, `all` không thể đạt 100% ở các câu có nhiều hơn k nhóm, nên báo cáo kèm phân phối này hoặc tính thêm tỷ lệ nhóm tìm được trên từng câu.

   **Căn cứ là phụ lục bị tách mẩu:** `bang_chung_v1.json` (lớp bổ trợ, không sửa `eval_v1.jsonl`) ghi các dòng phụ lục mà câu cần, ví dụ `lp08` cần ba dòng mức phí đổi đăng ký xe mô tô ở Mục II Phụ lục I TT 155. Nhóm chỉ đạt khi các mẩu lấy về chứa đủ các dòng đó; mẩu cùng phụ lục nhưng thiếu các dòng này không được tính. Mã băm của file ghi trong `data/rag/MANIFEST.json`.
2. **Số liệu:**
   - Tỷ lệ cặp trong `so_lieu` mà câu trả lời nêu đúng cả giá trị và đơn vị. Tính trên 106 câu có ít nhất một số liệu: 74 câu thường + 32 câu sửa đổi.
   - Mức phạt tiền chấm riêng trên 18 câu có `muc_phat_*`: 14 câu thường + 4 câu sửa đổi.
   - Trừ điểm chấm trên 15 câu có `trang_thai_diem_tru` khác `khong_ap_dung`: 6 câu `co` và 9 câu `khong_tru`. Với `khong_tru`, trả lời có trừ điểm là sai.
   - Tước GPLX chấm trên 3 câu có `tuoc_gplx_thang`.
3. **Nội dung:** đáp án đạt khi nêu đủ các ý chính của `dap_an` và không thêm chế tài sai. LLM-Judge và chấm tay dùng cùng tiêu chí này. Phần ghi trong `ghi_chu` là lưu ý, không phải ý bắt buộc.
4. **RQ3:**
   - "Trả lời theo luật mới": câu trả lời khớp `dap_an` (số liệu, chủ thể, hành vi).
   - "Trích luật cũ": câu trả lời khớp `dap_an_cu` hoặc trích phiên bản trong `can_cu_cu`.
5. **Từ chối:**
   - Câu `ngoai_pham_vi` đạt khi hệ thống nói rõ không có căn cứ và không bịa quy định. Với `luat_cu`, nêu thêm quy định hiện hành có căn cứ vẫn đạt.
   - Từ chối sai: hệ thống từ chối một câu thường, sửa đổi hoặc biến thể.
6. **Biến thể:** so điểm của biến thể với điểm của câu gốc cùng `ho_cau`, không cộng gộp như câu độc lập.

## Cách làm và kiểm tra

- **Soạn câu:** đọc văn bản đang có hiệu lực tại ngày hỏi bằng `scripts/eval_context.py` (lệnh `tree`, thêm `--all-versions` để xem bản cũ), rồi viết câu bám sát chữ.
- **Kiểm tra tự động** (`lawproc.evalset.check_items`, chạy trong build và trong `tests/test_evalset.py`):
  - Căn cứ có thật, có hiệu lực tại `ngay_hoi`, trong phạm vi, không thuộc đề thi GPLX.
  - Về mức phạt:
    - `muc_phat_min ≤ muc_phat_max`, hai mức có trong căn cứ;
    - đáp án phải có đúng khoảng "từ `min` đồng đến `max` đồng" của nhãn.
  - **Mọi số liệu có đơn vị** trong đáp án và đáp án cũ đều có trong căn cứ tương ứng (kể cả câu dẫn của Khoản cha) hoặc trong câu hỏi. Cụ thể:
    - "ngày làm việc" phải khớp "ngày làm việc";
    - tỷ lệ "27/30 điểm" phải khớp cả hai số;
    - mọi khoảng "từ X đến Y" phải có trong căn cứ.
  - Mọi trích dẫn "điểm… khoản… Điều…" trỏ tới đơn vị có hiệu lực trong văn bản được dẫn; viện dẫn sang văn bản ngoài căn cứ thì bỏ qua.
  - Khoản trừ điểm hoặc tước GPLX trong căn cứ phải liệt kê đúng hành vi đang hỏi.
  - `diem_tru`, `tuoc_gplx_thang` khớp với luật; nếu luật có chế tài thì đáp án phải nêu.
  - Câu sửa đổi: bản cũ có hiệu lực tại `ngay_cu`, hết hiệu lực tại `ngay_hoi`.
  - Câu ngoài phạm vi không có căn cứ; biến thể cùng căn cứ và cùng tập với câu gốc; không trùng id hay câu hỏi; câu thường khớp ma trận đề.
  - Chín phép sửa sai trong hai vòng review là test bắt buộc phải bị bắt (6 phép vòng 1, 3 phép vòng 2).
- **Soát ngoài phần tự động:**
  - Đọc lại 40 câu RQ3 theo câu hỏi: thay đổi đó có áp dụng thực tế vào `ngay_cu` không, có văn bản nào ngoài kho đã đổi trước không.
  - Đọc lại cả 50 cặp biến thể.
  - Đối chiếu một số thay đổi mới với nguồn nhà nước và báo chí (xem các báo cáo sửa).

Chạy lại:

```bash
py -3.13 scripts/build_eval.py
py -3.13 -m pytest -q tests/test_evalset.py
```

## Hạn chế (ghi vào báo cáo)

- Câu hỏi do LLM (Claude) soạn từ văn bản, đã qua kiểm tra tự động, hai vòng review độc lập (Codex) và sửa theo review. Chưa có chuyên gia pháp lý duyệt; nên chấm tay một mẫu.
- **Kho `data-v1` chỉ lưu câu chữ văn bản**, không mô hình hóa các văn bản khác làm thay đổi việc áp dụng:
  - NĐ 189/2025 về thẩm quyền;
  - Nghị quyết về bỏ cấp huyện;
  - chuyển chức năng GPLX sang Bộ Công an;
  - TT 47/2024 về chứng nhận xe cải tạo.

  Câu RQ3 đã tránh các trường hợp này. Hệ thống RAG cũng sẽ không biết các văn bản đó.
- Bộ kiểm tra tự động bảo đảm số liệu, trích dẫn và chế tài khớp căn cứ, nhưng không thay thế việc duyệt nghĩa của câu.
- `so_lieu` ghi cặp giá trị–đơn vị, chưa gắn vai trò (ví dụ phân biệt "thời hạn" với "mức phạt"). Tỷ lệ như "27/30" được giữ nguyên dạng nên vẫn chấm được ngưỡng đạt.
- `nhom_can_cu` chưa liệt kê căn cứ thay thế tương đương (OR). Nếu một ý có thể lấy từ hai nơi khác nhau, rubric hiện tại sẽ chấm chặt hơn thực tế.
- Repo chưa có scorer retrieval. Quy tắc "chunk thực sự chứa đơn vị" sẽ cài đặt ở bước G3 và cần test riêng.
- RQ3 nghiêng về thay đổi thời hạn thủ tục (13/40 câu từ NĐ 218/2026). Kết quả RQ3 chỉ nói về tập thay đổi đã chọn, không suy rộng cho mọi loại sửa đổi pháp luật.
- Mọi câu hỏi tại 01/10/2026; chưa có câu đặt ở ngày quá khứ hay tương lai.
- Câu ngoài phạm vi phần lớn dễ nhận ra; chưa có nhóm câu thiếu dữ kiện, tiền đề sai, hoặc pha trộn phần trong và ngoài phạm vi.
- Câu có phần suy luận, đã ghi ở `ghi_chu`:
  - `dk11`: mốc tăng giá khởi điểm đấu giá biển số;
  - `hd13`: thẩm quyền của Ủy ban nhân dân cấp xã;
  - `tn07`: mức bồi thường giảm theo lỗi của người bị thiệt hại.
- Khoản 1–3 Điều 6 TT 65/2024 có bản mới từ 01/7/2027. Câu `gp06`, `gp13` đúng tại 01/10/2026 nhưng sẽ lỗi thời sau mốc này.
