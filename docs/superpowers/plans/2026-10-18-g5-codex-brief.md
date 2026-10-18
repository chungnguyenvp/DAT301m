# G5: giao Codex soạn tiếp dữ liệu train lên khoảng 1.500 mẫu

Tài liệu này dành cho người (hoặc agent) soạn tiếp mẫu train G5 mà không có ngữ cảnh hội thoại trước. Đọc hết trước khi
viết dòng mã đầu tiên. Kế hoạch gốc: `docs/superpowers/plans/2026-10-18-g5-train-data.md`.

## 1. Mục tiêu

- Hiện có (sau đợt 11): **1.189 mẫu nháp, giữ 1.118** sau khi lọc (train 969, dev 149).
- Đích: **khoảng 1.500 mẫu giữ lại**, tức cần thêm khoảng **380 mẫu giữ lại**, soạn khoảng **410 mẫu** (mỗi đợt thường có
  3–8% mẫu bị loại vì quá giống câu eval).
- Ưu tiên chất lượng hơn số lượng: một mẫu sai ý luật làm mô hình học sai; thiếu vài chục mẫu thì không sao.

## 2. Phạm vi được sửa

**Được tạo mới:**
- `scripts/g5_drafts/g5_<tên>_cx.py`: mỗi script sinh một file nháp.
- `data/train/drafts/<tên>_cx.jsonl`: file nháp do script sinh ra.

**Được sửa:**
- `scripts/g5_drafts/README.md`: thêm script mới vào lệnh chạy lại.
- Mục "Task 3" (nhật ký đợt) trong `docs/superpowers/plans/2026-10-18-g5-train-data.md`.
- `data/train/{train,dev}.jsonl`, `data/train/MANIFEST.json`: chỉ ghi lại bằng `scripts/build_trainset.py`, không sửa tay.

**Không được sửa:**
- Các file nháp và script đã có (không có hậu tố `_cx`).
- `src/`, `tests/`, `data/eval/`, `data/processed/`, `data/rag/`.
- Hai thư mục tham khảo `nlp-traffic-laws/`, `traffic-law-assistant/` ở thư mục cha.
- `docs/reviews/`, và file `data/processed/PROCESSING_REPORT.md` đang có sửa đổi chưa commit.

**Không cài thư viện, không tải mô hình.** Mọi thứ cần dùng đã có sẵn.

## 3. Định dạng mẫu

Mỗi dòng của file nháp là một JSON:

```json
{"key": "xp-1001", "chu_de": "Xử phạt", "loai": "muc_phat",
 "cau_hoi": "Ô tô đi vào đường có biển cấm ô tô bị phạt bao nhiêu?",
 "dap_an": "Đi vào khu vực cấm, đường có biển báo hiệu có nội dung cấm đi vào đối với loại phương tiện đang điều khiển bị phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng (điểm i khoản 5 Điều 6 Nghị định 168/2024/NĐ-CP), ...; người vi phạm còn bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 16 Điều 6).",
 "can_cu": ["nd_168_2024:d6:k5:i@2026-08-15", "nd_168_2024:d6:k5@2025-01-01", "nd_168_2024:d6:k16:a@2025-01-01"]}
```

- `key`: `<tiền tố>-<4 chữ số>`. **Codex dùng số từ 1001 trở lên cho mọi tiền tố** (ví dụ `bb-1001`, `tn-1001`). Mẫu cũ đều
  dưới 1000, nên không trùng, và sau này vẫn biết mẫu nào do Codex soạn.
- `chu_de` và tiền tố đi theo cặp:

  | Tiền tố | `chu_de` | Tiền tố | `chu_de` |
  |---|---|---|---|
  | xp | Xử phạt | lu | Luật lõi |
  | gp | GPLX | tn | Tai nạn |
  | dk | Đăng ký xe | hd | Hướng dẫn |
  | dkm | Đăng kiểm | td | Tốc độ |
  | np | Nộp phạt, giữ xe | bb | Biển báo |
  | lp | Lệ phí | bh | Bảo hiểm |
  | tc | Từ chối | | |

- `loai` là một trong sáu giá trị:
  - `muc_phat`: hỏi mức phạt.
  - `thu_tuc`: hồ sơ, trình tự, thời hạn, nơi nộp, cách làm.
  - `quy_tac`: hỏi quy định là gì.
  - `tinh_huong`: người dùng kể một chuyện cụ thể.
  - `doi_thuong`: viết kiểu chat, không dấu câu, viết tắt (ví dụ "ko", "dc", "csgt").
  - `tu_choi`: ngoài phạm vi hoặc đề nghị giúp vi phạm.

  Gán đúng bản chất câu hỏi, đừng gán `thu_tuc` cho câu hỏi về quyền hay quy tắc để tăng tỷ lệ.
- `can_cu`: danh sách `version_id` **chép đúng từng ký tự** từ kết quả của `g5_dump.py`, kể cả phần `@ngày`.
  - Phần tử đầu tiên là đơn vị chính (khoản hoặc điểm quy định hành vi, thủ tục đang hỏi).
  - `tu_choi` thì `can_cu` là `[]`.
- Không thêm trường nào khác.

Mẫu từ chối viết theo hai kiểu đã có:
- **Ngoài phạm vi:** "Câu hỏi này nằm ngoài phạm vi của tôi. Tôi chỉ hỗ trợ tra cứu pháp luật về trật tự, an toàn giao thông
  đường bộ Việt Nam (…) và không có căn cứ trong tài liệu để trả lời. Bạn nên …"
- **Đề nghị giúp vi phạm:** "Tôi không thể hướng dẫn việc này vì đây là hành vi vi phạm pháp luật hoặc nhằm trốn tránh trách
  nhiệm. …" (câu sau không được nêu con số).

## 4. Quy trình cho mỗi đợt

```bash
export PYTHONIOENCODING=utf-8                                   # Windows cần để in tiếng Việt
py -3.13 scripts/g5_drafts/g5_list.py --keys                    # key lớn nhất, đếm theo chủ đề và loại
py -3.13 scripts/g5_drafts/g5_list.py --chu-de "Biển báo"       # các câu đã có của chủ đề, để không hỏi lại
py -3.13 scripts/g5_drafts/g5_list.py --doc qcvn_41_2024        # Điều nào đang có hiệu lực, đã được dẫn bao nhiêu lần
py -3.13 scripts/g5_drafts/g5_dump.py qcvn_41_2024 d21 d22 d23  # in nguyên văn các đơn vị đang có hiệu lực
py -3.13 scripts/g5_drafts/g5_dump.py qcvn_41_2024 --titles     # chỉ in danh sách Điều
```

1. Chọn các Điều chưa dẫn hoặc dẫn ít (cột `đã dẫn` của `--doc`), đọc nguyên văn bằng `g5_dump.py`.
2. Viết `scripts/g5_drafts/g5_<tên>_cx.py` theo khuôn của `g5_dk03.py` hoặc `g5_tt02.py`:
   - các hàm `t()`, `add()`;
   - đặt `ROOT = Path(__file__).resolve().parents[2]`;
   - ghi file bằng `json.dumps(s, ensure_ascii=False)`, mỗi mẫu một dòng.
3. Chạy script, rồi chạy bộ kiểm:
   ```bash
   py -3.13 scripts/g5_drafts/g5_<tên>_cx.py
   py -3.13 scripts/build_trainset.py --check 2>&1 | grep -E "<tiền tố>-1|mẫu; lỗi|theo loại|key trùng"
   ```
   Phải ra `lỗi 0`. Dòng `GẦN EVAL: …` nghĩa là mẫu đó bị loại vì giống câu eval. Không cần sửa, nhưng đừng viết lại câu
   đó bằng lời khác để lách bộ lọc.
4. Tự rà lại từng mẫu theo mục 6.
5. Ghi một dòng vào nhật ký đợt trong kế hoạch G5, gồm: nguồn (văn bản, Điều), số mẫu soạn, số lỗi, mẫu bị loại vì gần eval
   (key và câu eval tương ứng).
6. Khi xong toàn bộ:
   ```bash
   py -3.13 scripts/build_trainset.py      # ghi train.jsonl, dev.jsonl, MANIFEST.json
   py -3.13 -m pytest -q                   # phải 404 passed, 4 skipped như hiện tại
   ```
   Kiểm thêm: chạy lại mọi script trong `scripts/g5_drafts/` (lệnh ở README, kể cả `g5_fix_owner.py`) phải cho ra các file nháp
   giống từng byte.

## 5. Bộ kiểm bắt được gì (đọc `src/lawproc/evalset.py: check_items`, `src/lawproc/trainset.py`)

- Mỗi `version_id` trong `can_cu` phải tồn tại và có hiệu lực tại `2026-10-01`.
  - Với BLDS chỉ dùng Điều 584–608; với BLHS (`vbhn_135_2025_blhs`) chỉ dùng Điều 260–266.
  - Không dẫn `gplx_600_2025`, `cv_2262_2025_csgt` (tài liệu đề thi, không phải văn bản luật).
- **Mọi số liệu có đơn vị** trong đáp án phải xuất hiện trong văn bản các đơn vị đã dẫn (hoặc trong câu hỏi). Đơn vị gồm: đồng,
  điểm, km/h, m, tấn, chỗ, %, ngày, tháng, năm, giờ… Khung "từ X đến Y" cũng vậy. Viết số **đúng như văn bản**:
  - Văn bản viết "từ 8.000.000 đến 12.000.000 đồng" thì không viết "8.000.000 đồng đến".
  - Văn bản viết "5 (năm) triệu đồng" thì chép nguyên, không rút thành "5 triệu đồng".
  - Văn bản viết "09 chỗ" thì viết "09 chỗ".
- Mỗi trích dẫn dạng "điểm x khoản y Điều z" trong đáp án phải trỏ tới đơn vị đang có hiệu lực của văn bản trong `can_cu`
  (nếu ghi rõ tên văn bản khác không có trong `can_cu` thì bộ kiểm bỏ qua trích dẫn đó).
  - Lỗi hay gặp: "Bảng 3 điểm a" bị đọc thành "3 điểm". Hãy viết "điểm a khoản 2 Điều 11 (Bảng 3)".
- Nếu đơn vị chính là hành vi xử phạt của NĐ 168 mà luật có trừ điểm hoặc tước bằng, đáp án **phải** có chữ "trừ … điểm"
  hoặc "tước", kèm căn cứ khoản chế tài (ví dụ `nd_168_2024:d6:k16:a`).
- Không có hai câu hỏi trùng nhau từng chữ; không trùng `key`.
- Lọc gần trùng: loại mẫu có cosine TF-IDF ký tự 4-gram ≥ 0,85 với câu eval hoặc GPLX, hoặc ≥ 0,6 khi cùng hỏi một quy
  định. Bộ lọc **không** so giữa các mẫu train với nhau, nên phải tự tránh hỏi lại câu đã có (dùng `g5_list.py`).

**Bộ kiểm không bắt được ý nghĩa.** Câu trả lời có thể đúng hết số mà vẫn sai luật. Mục 6 là phần quan trọng nhất.

## 6. Quy tắc nội dung và các lỗi đã từng gặp

1. **Chỉ viết điều văn bản nói.** Đã phải gỡ những lỗi sau:
   - nêu "VNeID" ở chỗ văn bản không nói;
   - tự thêm so sánh "nhẹ hơn";
   - tự thêm "trong thời gian xác minh", "dưới 50 cm3";
   - tự đặt tên biển báo không có trong văn bản;
   - thêm câu "phần vượt quá … tự chi trả";
   - nhắc hạng B2 (hạng đã bỏ) trong câu hỏi.

   Không chắc thì bỏ câu đó đi.
2. **Dẫn đúng phiên bản.** Một số khoản có nhiều phiên bản (ví dụ NĐ 168 bản 15/8/2026, TT 79 bản 18/5/2026). `g5_dump.py`
   chỉ in bản đang có hiệu lực; chép đúng `@ngày` của bản đó. Nếu đáp án nói "được sửa đổi, có hiệu lực từ …" thì ngày phải
   khớp.
3. **Người lái đồng thời là chủ xe (NĐ 168).** Câu hỏi về người lái mà hành vi đó có hành vi tương ứng của chủ xe ở Điều 32,
   khoản 3 Điều 47 quy định thì đáp án phải thêm câu: "Trường hợp người điều khiển đồng thời là chủ phương tiện thì bị xử phạt
   theo điểm, khoản tương ứng của Điều 32 Nghị định 168/2024/NĐ-CP (điểm … khoản 3 Điều 47)", và thêm đơn vị
   `nd_168_2024:d47:k3:<điểm>` vào `can_cu`. Danh sách đơn vị nằm ở `RULES` trong `g5_fix_owner.py`. Mẫu `_cx` tự viết câu
   này, không sửa `g5_fix_owner.py`.
4. **Văn bản thay thế.** Đừng dẫn văn bản đã hết hiệu lực:
   - TT 12/2025 (đã thay bằng TT 108/2026; chỉ còn vài phần chuyển tiếp);
   - NĐ 160/2024 (đã thay bằng NĐ 94/2026);
   - VBHN 63/2025 (đã thay bằng VBHN 90/2026).

   Nếu tự viết mã thống kê, nhớ `validity.in_force_at(rec, ngày)` trả về **cặp** `(bool, điều_kiện)`, phải lấy `[0]`.
5. **Đúng văn bản cho đúng câu hỏi.**
   - NĐ 336/2025 xử phạt trong *hoạt động đường bộ* (kết cấu hạ tầng, vận tải theo Luật Đường bộ). Lỗi của người lái về trật
     tự an toàn giao thông thuộc NĐ 168.
   - Phụ lục và bảng bị mất cột khi xử lý (ví dụ bảng chu kỳ kiểm định ô tô ở Phụ lục V TT 30) thì không dùng.
6. **Không lặp câu đã có.** Mỗi đợt chạy `g5_list.py --chu-de …` trước. Có thể hỏi cùng một quy định theo góc khác (thủ tục
   thay vì định nghĩa, tình huống thay vì câu chung), nhưng không đổi vài chữ của câu cũ.
7. **Câu hỏi tự nhiên.** Có cả câu chuẩn lẫn câu kiểu chat (`doi_thuong`, khoảng 10%). Câu `tinh_huong` kể một chuyện cụ thể ở
   ngôi thứ nhất.
8. **Đáp án:** trả lời thẳng trước ("Có.", "Không.", mức phạt…), rồi giải thích. Ghi căn cứ trong ngoặc theo dạng "(điểm a
   khoản 2 Điều 33 Luật Trật tự, an toàn giao thông đường bộ)". Ngắn gọn, không chép nguyên cả Điều.

## 7. Định mức và nguồn cho từng chủ đề (khoảng 410 mẫu soạn)

Dùng `g5_list.py --doc <doc_id>` để xem Điều nào còn trống. Các số dưới đây là gợi ý, lệch ±20% không sao.

| Đợt | Chủ đề (tiền tố) | Nguồn chính (`doc_id`: Điều) | Soạn | Ghi chú |
|---|---|---|---|---|
| C1 | Biển báo (bb) | `qcvn_41_2024`: Phụ lục `pl2` (biển cấm), `pl3` (nguy hiểm), `pl4` (hiệu lệnh), `pl5` (chỉ dẫn), `pl6` (biển phụ), `pl7` (vạch kẻ); Điều 9, 15, 16, 21–24, 27, 31, 34, 41, 42, 48–51, 54, 72–79 | 80 | Phụ lục là một đơn vị dài (`qcvn_41_2024:pl2@2025-01-01`…). Câu hỏi kiểu "biển P.124a cấm gì, có cấm rẽ trái không". Chỉ nêu tên, số hiệu biển có trong văn bản. |
| C2 | Luật lõi (lu) | `luat_36_2024`: Điều 11, 32, 41–55, 63–65, 67, 70, 73–79, 82–85; `luat_35_2024` (Luật Đường bộ, chưa có mẫu nào): phần người dân hay hỏi (phí sử dụng đường bộ, đường cao tốc, trạm dừng nghỉ, bến xe, hành lang an toàn) | 60 | Luật 35 có nhiều phần về quản lý hạ tầng, chỉ chọn phần liên quan người tham gia giao thông. |
| C3 | Xử phạt (xp) | `nd_168_2024` | 60 | **Tình huống ghép 2–3 lỗi** (ví dụ "vừa không đội mũ vừa vượt đèn đỏ"), mỗi lỗi một căn cứ và mức phạt riêng. Kèm nguyên tắc nhiều hành vi thì xử phạt từng hành vi (tìm trong `vbhn_90_2026_xlvphc` Điều 3, kiểm nguyên văn trước khi dùng). Đơn vị chính là hành vi đầu tiên; nhớ quy tắc 3 ở mục 6. |
| C4 | Nộp phạt, giữ xe (np) | `vbhn_90_2026_xlvphc`: Điều 2–5, 9, 10 (tình tiết giảm nhẹ, tăng nặng), 21–26, 28 (hình thức xử phạt, biện pháp khắc phục), 134–138 (người chưa thành niên); `nd_138_2021` phần còn lại | 35 | Bỏ các Điều về giáo dục bắt buộc, cai nghiện. |
| C5 | Tai nạn (tn) | `vbhn_135_2025_blhs` Điều 261–266 (chỉ trong khoảng 260–266); `blds_2015` Điều 586–589, 592–593, 596, 599, 600, 603–605 (năng lực bồi thường, nhiều người cùng gây ra, thời hiệu khởi kiện, tài sản bị xâm phạm, thời hạn hưởng bồi thường, người dùng chất kích thích, người dưới 15 tuổi, người làm công, súc vật, cây cối, công trình gây thiệt hại) | 40 | Đã có mẫu ở Điều 260, 264, 584, 585, 590, 591, 601 và Luật 36 Điều 80, 81. Chỉ dùng BLDS trong 584–608. |
| C6 | Hướng dẫn (hd) | `nd_158_2024`: Điều 4–5, 8–10, 12–18, 24–28 (tuyến cố định, xe buýt, vận tải hàng hóa, xe bốn bánh có gắn động cơ, hợp đồng vận tải, vận tải nội bộ); `nd_218_2026` (sửa đổi NĐ 158) | 40 | Dẫn bản đang có hiệu lực (nhiều khoản có bản 10/8/2026). |
| C7 | Tốc độ (td), Bảo hiểm (bh), Lệ phí (lp) | `tt_38_2024_bgtvt` Điều 3, 5, 10, 11; `nd_67_2023` Điều 4–13 phần còn lại và `nd_220_2026` (sửa đổi NĐ 67); `nd_10_2022` Điều 3, 6–8, 10; `tt_155_2025_btc` Điều 5, 6 | 45 | Bảng phí ghi số không kèm "đồng" thì viết "tính bằng đồng: 55.000". |
| C8 | GPLX (gp), Đăng ký xe (dk), Đăng kiểm (dkm) | `tt_108_2026_bca` Điều 3, 18, 25, 30; `tt_79_2024_bca` các khoản còn ít mẫu; `tt_30_2026_bxd` Điều 3, 18, 28–30; `luat_36_2024` Điều 57–62 | 30 | |
| C9 | Từ chối (tc) | không có căn cứ | 20 | 15 câu ngoài phạm vi (đường sắt, hàng không, hàng hải, đất đai, hôn nhân…), 5 câu đề nghị giúp vi phạm. Không trùng 60 câu đã có. |

Tỷ lệ loại nên giữ gần như hiện tại; nếu có thể thì tăng `thu_tuc` và `doi_thuong`. `muc_phat` đang nhiều (347), nên đợt C3 thiên
về `tinh_huong`.

## 8. Bàn giao

- Làm trên nhánh `feat/g5-codex-1500` cắt từ `main` mới nhất, mỗi đợt (C1…C9) một commit. **Không merge, không gắn tag.**
- Báo cáo cuối gồm:
  - bảng các đợt (nguồn, số soạn, lỗi, số bị loại);
  - kết quả `build_trainset.py` (tổng giữ lại, theo loại, theo chủ đề, train/dev);
  - kết quả `pytest`;
  - danh sách những chỗ chưa chắc về nội dung, để người duyệt đọc kỹ.
- Sau đó Claude đọc lại toàn bộ mẫu `_cx` trước khi merge; người dùng duyệt tay một mẫu ngẫu nhiên (Task 5 của kế hoạch G5).
