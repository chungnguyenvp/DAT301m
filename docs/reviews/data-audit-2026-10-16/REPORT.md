# Kiểm tra sâu dữ liệu luật giao thông — 16/10/2026

## Kết luận

**Chưa nên gắn nhãn “data sạch” hoặc đóng băng để dùng toàn bộ cho RAG/train/eval.** Nguồn được quản lý tốt, pipeline tái lập được và cấu trúc cơ bản nhất quán. Tuy nhiên, kiểm tra trực tiếp xác nhận mất giá trị trong bảng, mất ký hiệu điều kiện, phân loại nhầm một phụ lục quan trọng và chưa đóng hiệu lực các phụ lục đã bị thay thế. Các lỗi này có thể làm câu trả lời sai ngay cả khi tìm đúng văn bản.

Kết luận áp dụng cho snapshot `fix/data-audit`, nội dung tương ứng commit `a33e52f` và hash tại `input_hashes.json`. Không sửa nguồn, pipeline hoặc `data/` trong lần kiểm tra này. Các thay đổi dữ liệu đã có trước khi audit được giữ nguyên. Số liệu vì vậy khác lượt xem tổng quan trước đó: hiện có thêm một Khoản sau bản sửa nguồn gần nhất.

## 1. Phạm vi và mức độ kiểm chứng

- Đọc toàn bộ **97 dòng manifest và 97 file raw**: tồn tại, kích thước, SHA-256, file dư/thiếu và trùng đường dẫn.
- Đọc **100% 17.903 đơn vị gốc, 18.842 phiên bản và 600 câu GPLX**. Kiểm tra schema, địa chỉ, khóa duy nhất, Unicode, rác trích xuất, bản rỗng, bản dài và nội dung lặp.
- Dựng lại **33/33 văn bản trong bộ nhớ** từ nguồn được lựa chọn; áp đủ hai sửa tay hiện có; tách lại đơn vị và áp lại toàn bộ sửa đổi đã duyệt, phân loại phụ lục và ngoại lệ. So sánh từng bản ghi với output, không ghi đè `data/`.
- Kiểm tra cấu trúc XML trên toàn bộ **45 file Word được chọn**: **59.083 đoạn XML**, bảng lồng, text box, ký hiệu đặc biệt và đoạn chữ không được biểu diễn trong kết quả extractor.
- Quét lớp chữ và số trang của toàn bộ PDF, tổng **3.100 trang**; kiểm tra trang ít chữ/ảnh. **10 trang nghi vấn được render để đối chiếu**, và các trang liên quan đến kết luận mất ký hiệu, mất cột bảng, nhảy số gốc, mất nội dung phụ lục đã được xem trực tiếp.
- Kiểm tra khoảng phiên bản và trạng thái tại **21 mốc ngày** trong dữ liệu; duyệt các trường hợp cùng sống có điều kiện và gia hạn. Bộ test sẵn có cũng kiểm tra những ngày ngay trước/đúng một số mốc quan trọng.
- Tách lại toàn bộ 600 câu từ PDF, đối chiếu đáp án gạch chân và các nhãn lấy từ Công văn bằng pipeline; kiểm tra độc lập schema, lựa chọn, trùng văn bản và câu thuần chữ có nhắc hình.
- Chạy bộ test hiện tại: **212 passed**. Test qua không có nghĩa mọi giá trị trong bảng hoặc mọi điều kiện pháp lý đều đúng.

**Giới hạn:** quét toàn bộ bằng chương trình không đồng nghĩa đọc tay từng chữ của 3.100 trang. Chưa kiểm định độc lập mọi con số/mức phạt và mọi quyết định duyệt sửa đổi bằng chuyên gia pháp lý; không xác minh tất cả thay đổi pháp luật ngoài tập nguồn. So sánh lại bằng chính pipeline xác nhận tính tái lập, còn các phép kiểm tra XML và ảnh nguồn cung cấp bằng chứng độc lập về mất nội dung.

## 2. Dữ liệu được xây như thế nào

```text
data/manifest.csv ── mô tả từng file: văn bản, nguồn, URL, bytes, SHA-256
       │
data/raw/legal/     ── DOC/DOCX/PDF/TXT gốc
       │
       ├─ DOC → data/interim/docx/  (Microsoft Word)
       ├─ DOCX: đọc đoạn, numbering và bảng
       ├─ PDF có chữ: trích lớp chữ
       └─ TXT đã đối chiếu: đọc trực tiếp
       │
       └─ chọn nguồn → bỏ header/chữ ký → ghép phần → sửa tay → tách QCVN
                         │
data/processed/documents/*.txt       33 văn bản đã ghép
                         │
data/processed/legal_units.jsonl     đơn vị cấu trúc gốc
                         │
       ├─ effective_dates_auto.csv  đề xuất ngày hiệu lực
       ├─ effective_dates.csv       ngày đã duyệt
       ├─ amendments_candidates.csv đề xuất sửa đổi
       ├─ amendments_reviewed.csv   quyết định đã duyệt
       ├─ effective_exceptions.csv  ngoại lệ, điều kiện và lộ trình
       └─ annex_type_overrides.csv  ghi đè loại phụ lục
                         │
data/processed/legal_units_versioned.jsonl
                         │
                 in_force_at(record, ngày)
```

Nguồn hiện được chọn theo ưu tiên **Word → TXT → PDF**. Báo cáo nguồn hiện có 30 văn bản từ Word, hai từ PDF và một từ TXT; không dùng OCR để dựng corpus hiện tại. QCVN được tách thành văn bản con; hai nguồn GPLX/Công văn không nhập vào kho luật nên 34 `doc_id` trong manifest tạo thành 33 văn bản pháp luật sau khi loại hai nguồn phi luật và thêm một văn bản con.

### 2.1. Ba lớp dữ liệu khác nhau

| Lớp | Ý nghĩa | Điều cần lưu ý |
|---|---|---|
| `documents/*.txt` | Toàn văn đã chọn nguồn, ghép và làm sạch | Còn cả mở đầu, phần kết và phụ lục; là đầu vào parser |
| `legal_units.jsonl` | Một dòng là một Điều, Khoản, Điểm hoặc phần phụ | Không phải một chunk RAG hoàn chỉnh; text cha thường không chứa text con |
| `legal_units_versioned.jsonl` | Một dòng là một phiên bản của địa chỉ pháp lý | Cần xét thời điểm, điều kiện, bản cha và nguồn sửa đổi |

`unit_id` mô tả đường dẫn, ví dụ `nd_168_2024:d6:k1:a`: văn bản → Điều 6 → Khoản 1 → điểm a. `version_id` bổ sung ngày bắt đầu. Cùng một `unit_id` có thể có nhiều phiên bản.

Các trường gốc: `unit_id, doc_id, level, chuong, muc, dieu, khoan, diem, title, text, line_start, phan`. Bản có phiên bản thêm `valid_from, valid_to, source_doc_id, version_id, noi_dung_doi, ty_le_am_tiet_loi, chat_luong, loai_phu_luc, hl_ngoai_le`.

`doc_id` là văn bản đích, còn `source_doc_id` có thể là văn bản ban hành sửa đổi. `valid_to = null` chỉ là trạng thái mà pipeline lưu, không phải bằng chứng đủ rằng nội dung chưa bị thay thế. Khoảng gốc là `[valid_from, valid_to)`; các ngoại lệ có thể cho phép giữ bản cũ theo điều kiện.

### 2.2. Số liệu kiểm đếm trực tiếp

| Chỉ số | Kết quả |
|---|---:|
| Văn bản đã ghép | 33 |
| Đơn vị gốc | 17.903 |
| Điều | 2.236 |
| Khoản | 7.088 |
| Điểm | 8.356 |
| Phụ lục | 158 |
| Mở đầu / phần kết | 33 / 32 |
| Phiên bản | 18.842 |
| Phiên bản được `in_force_at` trả True ngày 01/10/2026 | 17.472 |
| Địa chỉ phân biệt trong tập trên | 17.469 |
| Phiên bản không đổi nội dung | 184 |
| Nhãn chữ `kem` | 19 |
| Phụ lục `mau_bieu` / `noi_dung` | 107 / 51 |
| Dòng sửa đổi đã duyệt / loại | 505 / 304 |
| Dòng ngoại lệ hiệu lực | 22 |
| Ghi đè loại phụ lục / sửa chữ hiện hành | 7 / 2 |
| Câu GPLX / thuần chữ / có hình | 600 / 282 / 318 |

**17.472 là số bản được hàm lọc trả về**, không nên diễn giải thành 17.472 quy định chắc chắn áp dụng đúng: bao gồm placeholder đã bãi bỏ, phụ lục cũ chưa được đóng và các nhánh có điều kiện.

## 3. Các lỗi đã xác nhận

### F01 — Cao: mất cột dữ liệu do loại ô có giá trị giống nhau

`src/lawproc/extract.py:163` loại một ô nếu chữ của ô giống ô không rỗng trước đó. Hai ô khác nhau có cùng giá trị vẫn là hai cột độc lập.

Đối chiếu `qcvn_41_2024:d56:k3`, bảng kích thước ở PDF `tt_51_2024_bgtvt_qcvn41__p1.pdf`, trang 74 (trang in 75):

```text
Nguồn:     < 60 km/h | 220 | 400 | 110 | 200 | 10 | 10
Đang lưu:  < 60 km/h | 220 | 400 | 110 | 200 | 10
```

Cột F bị mất. Hai hàng còn lại cũng mất giá trị cuối 15 và 20. Trong `tt_108_2026_bca:pl3`, hàng có ba ô `100` thành `Thang điểm | 100`; ba ô `80` thành `Điểm đạt tối thiểu | 80`. Bảng tương tự của TT12 cũng bị ảnh hưởng.

Quét XML thấy **46 hàng có ô kề nhau trùng nội dung**, phân bố: NĐ158 23; QCVN 5; TT12 3; TT79 4; NĐ67 2; TT108 9. Đây là danh sách hàng chịu quy tắc gộp, không khẳng định cả 46 đều là lỗi pháp lý độc lập: nhiều hàng là mẫu lặp hoặc ô trong bảng lồng. Lỗi mất giá trị của bảng nội dung QCVN và GPLX đã được xác nhận.

Ngoài ra extractor bỏ ô rỗng, nên một hàng ít cột có thể mất vị trí tương ứng với header. Cần giữ số ô/vị trí hoặc chuyển từng hàng thành cấu trúc có tên cột; không khử trùng bằng giá trị ô.

Bằng chứng: `table_adjacent_duplicate_cells.json`, ảnh `tt_51_2024_bgtvt_qcvn41__p1-page-74.png`.

### F02 — Cao: mất ký hiệu toán học và đường kính trong phần chữ

`_text_of` chỉ lấy `w:t` và một số dấu ngắt. Ký hiệu đặt trong `w:sym` bị bỏ. Có **19 phần tử `w:sym`** trong toàn bộ nguồn Word được chọn, trong đó **7 ở QCVN**; những phần còn lại chủ yếu là ô chọn trong biểu mẫu.

Ví dụ đã so với ảnh PDF:

| Địa chỉ | Nguồn | Nội dung đang lưu |
|---|---|---|
| `qcvn_41_2024:d12:k2:b` | Số hàng đơn vị `> 5` | Số hàng đơn vị `5` |
| `qcvn_41_2024:d55:k7` | `30 m < R ≤ 100 m` | `30 m < R 100 m` |
| `qcvn_41_2024:d55:k7` | độ dốc `≥ 3%` | độ dốc `3%` |
| `qcvn_41_2024:d79:k3` | ống thép `Ø40 - Ø50` | ống thép `40 - 50` |

Hai dấu `≤` khác ở Phụ lục G cũng bị mất. Đây là mất điều kiện/đại lượng, không phải lỗi trình bày. Các bản ghi có thể vẫn mang `chat_luong=ok`.

Cần ánh xạ theo font Symbol/Wingdings đúng ngữ nghĩa, bảo toàn ký hiệu và kiểm tra đối chiếu ảnh; không chuyển mã hex thành Unicode trực tiếp một cách máy móc.

Bằng chứng: `word_symbols_context.json`, `rendered_source_pages.json`, ảnh trang 14, 71 và 82 của PDF QCVN phần 1.

### F03 — Cao: phụ lục biển số mới bị coi là biểu mẫu vì “Cà Mau”

`tt_51_2025_bca:pl1@2025-07-01` là **bảng ký hiệu biển số theo địa phương**, nhưng `loai_phu_luc=mau_bieu`.

Nguyên nhân được tái hiện trực tiếp: `FORM_WORD = r"\b(?:mẫu|mau)\b"` tìm trong 300 ký tự đầu; khớp chữ **Mau** ở dòng `3 | Cà Mau | 69, 94`. Hàm trả lý do “tiêu đề có chữ Mẫu” dù đây là tên địa phương trong bảng.

Nếu loại `mau_bieu` khi dựng RAG như kế hoạch, bảng mới sẽ bị loại. Cần sửa điều kiện nhận diện theo ngữ cảnh tiêu đề hoặc ghi đè đã duyệt; bổ sung trường hợp Cà Mau làm hồi quy.

Bằng chứng: `annex_classifier_unaccented_matches.json`. Vị trí: `legal_units_versioned.jsonl:11942`, `src/lawproc/annotate.py:10` và `:30`.

### F04 — Cao: phụ lục cũ đã bị thay nhưng vẫn vượt qua bộ lọc ngày

Đã đối chiếu chỉ dẫn sửa đổi nằm trong corpus với bản ghi đích. **Ít nhất 5 đơn vị phụ lục nội dung cũ** vẫn có `valid_to=null`, trong khi phụ lục thay thế đã vào hiệu lực:

| Bản cũ còn sống | Bản mới trong kho | Chỉ dẫn thay thế |
|---|---|---|
| `tt_79_2024_bca:pl18` | `tt_51_2025_bca:pl1` | `tt_51_2025_bca:d1:k4` |
| `nd_165_2024:pl2` | `nd_241_2026:pl2` | `nd_241_2026:d25:k4:b` |
| `nd_165_2024:pl10` | `nd_241_2026:pl7` | `nd_241_2026:d25:k4:e` |
| `nd_67_2023:pl3` và `:pl4` | `nd_220_2026:pl1` | `nd_220_2026:d8:k1` |

Hai đơn vị NĐ67 cùng mang tiêu đề Phụ lục III: văn bản được chia ở tiêu đề tiếp nối giữa các phần nguồn. Chúng là hai mảnh của phụ lục cần xử lý cùng nhau.

Những dòng thay phụ lục đã bị loại khỏi bảng sửa đổi áp dụng vì bộ áp chỉ hỗ trợ Điều/Khoản/Điểm. Việc giữ chúng trong CSV dưới trạng thái `loai` không làm phụ lục cũ tự hết hiệu lực. Đây là giới hạn đã được tài liệu cũ ghi nhận, nhưng tác động trực tiếp vẫn tồn tại trong dữ liệu.

Lỗi F03 và F04 kết hợp tạo tình huống xấu: **bảng biển số cũ còn là `noi_dung`, bảng mới lại là `mau_bieu`**. Bộ lọc theo ngày và loại phụ lục có thể giữ bảng cũ và bỏ bảng mới.

Cần biểu diễn quan hệ thay thế phụ lục, đóng mọi mảnh của phụ lục cũ ở đúng mốc và giữ lịch sử. Nếu chưa hỗ trợ được, phải loại nhóm này khỏi phạm vi trả lời/eval bằng cờ có căn cứ; không chỉ thêm một câu vào phần “hạn chế”.

Bằng chứng: `confirmed_stale_annexes.json`, `amendments_reviewed.csv`, `checks.json`.

### F05 — Vừa: nội dung phụ lục ảnh chưa được phục hồi, nhãn `ok` gây hiểu lầm

- `nd_39_2023:pl1` chỉ có **76 ký tự**, chủ yếu là dòng ban hành kèm theo. PDF phần 1, trang 12–14 chứa ảnh biểu mẫu; xem trực tiếp trang 13 thấy mẫu tờ khai và hướng dẫn, trong khi output không có phần này.
- QCVN chỉ có phụ lục **A, B, C, D, E, F, G, I, K**. M/N/O/P trong phần ảnh chưa có nội dung tương ứng trong JSONL.
- `tt_108_2026_bca:pl12` hiện có **467 ký tự và bảng chuyển đổi**: không tiếp tục ghi nhận nó là lỗi “chưa có bảng” như tài liệu cũ.

Phần thiếu có thể nằm ngoài phạm vi demo, nhưng dữ liệu cần cờ `completeness`/`excluded_from_qa` hoặc danh sách loại trừ có địa chỉ. `chat_luong=ok` chỉ phản ánh tỷ lệ âm tiết của chữ đã trích, không đo nội dung còn thiếu.

### F06 — Vừa: 20 placeholder “được bãi bỏ” vẫn được đếm là có hiệu lực

20 Điều có tiêu đề `(được bãi bỏ)`, không có text hoặc đơn vị con: BLHS Điều 292 và 19 Điều của VBHN XLVPHC. Đây là thông tin nguyên bản hợp lệ, **không phải parser làm mất thân Điều**. Tuy nhiên, bản ghi được khởi tạo `valid_from=2025-07-01, valid_to=null`, nên `in_force_at` trả True.

Cần phân biệt tombstone/placeholder với quy định có nội dung áp dụng, chẳng hạn `legal_status=abolished`; lọc phù hợp khi thống kê, sinh QA và dựng RAG. Không tự điền ngày bãi bỏ cụ thể nếu chưa có căn cứ. Không xóa dấu vết lịch sử khỏi corpus lưu trữ.

Bằng chứng: `live_abolished_placeholders.json`.

## 4. Những giới hạn cấu trúc và cách dùng cần xử lý trước RAG

1. **Phụ lục không có địa chỉ pháp lý chuẩn trong ID.** `plN` là thứ tự phát hiện, không phải số phụ lục in trên nguồn: `nd_67_2023:pl7` là Phụ lục VI; `tt_79_2024_bca:pl18` là Phụ lục số 02. Cần trường số/tên phụ lục chính thức và số mảnh; không trích dẫn “Phụ lục 18” từ ID.
2. **Ngoại lệ có thể làm con còn hiệu lực nhưng cha hết khoảng gốc.** Ba Khoản TT12 Điều 4 được gia hạn đến hết 28/02/2027; Điều cha không được gia hạn. Audit thấy 18 lượt con thiếu cha đang sống ở sáu mốc, đều là ba Khoản này. Đây là hệ quả gia hạn hợp lệ trong mô hình, không phải đơn vị gốc mồ côi. Khi ghép chunk, phải lấy tiêu đề cha theo quan hệ lịch sử, không làm rơi Khoản chỉ vì lọc cha trước.
3. **Có ba địa chỉ cũ/mới cùng được trả về tại cutoff**, kèm điều kiện: Luật36 Điều35 Khoản2; NĐ168 Điều20 Khoản5 điểm l; NĐ168 Điều21 Khoản3 điểm b. Giữ `hl_ngoai_le` và ghi chú trả về từ hàm; chọn đơn giản bản mới nhất không giải quyết điều kiện áp dụng.
4. **Bản gốc của văn bản sửa đổi có cấu trúc nhập nhằng do trích dẫn.** Ví dụ NĐ238 Điều18 chứa phần trích Khoản3 trong text Điều nhưng Khoản4 thành đơn vị riêng; NĐ241 Điều10 có chỉ dẫn bổ sung Khoản10/11 nhưng nhãn11 được tách thành `nd_241_2026:d10:k11`. Đã đối chiếu nguồn có dấu ngoặc thẳng và cách đóng/mở không nhất quán. Bản đích được tái dựng từ bảng duyệt là lớp khác; không dùng địa chỉ của đoạn trích làm địa chỉ quy định đích. Nhảy số trong văn bản sửa đổi cần phân loại theo ngữ cảnh, không tự renumber.
5. **Chỉ có snapshot của hai VBHN từ 01/07/2025.** Không có lịch sử trước mốc đó cho hai nhóm này. Không quảng bá khả năng trả lời mọi câu theo mọi ngày từ đầu 2025 chỉ dựa vào giao diện chọn ngày. BLHS còn ghi nhận các luật được hợp nhất có lịch trình hiệu lực khác nhau; cần kiểm tra theo đơn vị nếu mở rộng truy vấn lịch sử.
6. **Provenance của đoạn sinh từ sửa đổi chưa định vị được trang nguồn.** `line_start` của đoạn sửa đổi là vị trí trong fragment, không phải dòng tương ứng của văn bản đích. Cần nối thêm dòng sửa đổi/căn cứ, raw file và trang hoặc đoạn để người dùng kiểm chứng.
7. **Corpus lưu trữ chưa phải corpus RAG.** Có văn bản sửa đổi đa chủ đề, nội dung ngoài giao thông trong BLDS/BLHS, mẫu biểu và chỉ dẫn sửa đổi. Ví dụ lọc theo phạm vi dự kiến còn khoảng 9.565 phiên bản, nhưng đây chỉ là phép đếm thử, chưa phải bộ dữ liệu đã duyệt hoặc chunk hợp lệ. Phải tạo một view có tiêu chí rõ ràng.
8. **Phụ lục dài cần cấu trúc riêng.** Có 19 đơn vị gốc trên 20.000 ký tự; lớn nhất `nd_67_2023:pl7` có 73.322 ký tự. Chia theo hàng, tiểu mục và tiêu đề bảng; cắt token mù có thể làm mất tên cột/đối tượng áp dụng.

## 5. Những cảnh báo đã đối chiếu và không coi là lỗi

- **TT12 Điều3 thiếu Khoản4:** bản PDF gốc cũng nhảy từ 3 sang 5. Không phải mất Khoản do pipeline; không tự thêm số4.
- **TT51 phụ lục biển số có STT16 lặp, thiếu17:** ảnh PDF gốc cũng in Khánh Hòa16 và Lai Châu16. Giữ dấu vết nguồn; có thể thêm STT kỹ thuật riêng nếu cần, không âm thầm sửa văn bản pháp lý.
- **20 Điều rỗng:** đều là placeholder đã bãi bỏ, không phải thiếu thân do parser. Vấn đề là trạng thái và cách lọc, đã tách thành F06.
- **10 tiêu đề Điều dài hơn250 ký tự:** không đủ căn cứ gọi là gộp thân bài; nhiều tiêu đề xử phạt hoặc sửa nhiều luật vốn rất dài. Không cắt ngắn tự động.
- **Các nhãn con sâu của QCVN:** giữ trong Khoản là lựa chọn cấu trúc hiện tại; không phải mọi dòng `a)`/`1.` còn bên trong text đều là lỗi bỏ tách.
- **179 nhóm nội dung trùng dài hơn120 ký tự trong cùng văn bản đang được lọc:** nhiều nhóm là điều kiện/hình phạt/câu pháp lý dùng chung tại địa chỉ khác nhau. Không xóa trùng theo text; giữ địa chỉ và ngữ cảnh cha.
- **19 nhãn `kem`:** chỉ số dựa trên âm tiết, có nhiều mẫu song ngữ, tên nước và đơn vị đo. Nó không đo độ đúng số, bảng, thiếu chữ, ký hiệu hay hiệu lực. Không dùng ngưỡng này làm nhãn sạch cuối cùng.
- **Không phát hiện mất toàn bộ đoạn chữ dài trên30 ký tự** khi so 59.083 đoạn XML với output extractor trước các bước làm sạch. Kết quả này không bảo toàn số lần xuất hiện/vị trí/cột và không bao phủ ký hiệu `w:sym`, vì vậy không phủ nhận F01/F02.

## 6. Bộ 600 câu GPLX

Đọc và tách lại cho kết quả khớp từng dòng lưu. Đủ số1–600; 2–4 lựa chọn không rỗng; mọi đáp án là chỉ số hợp lệ và được bộ tách gạch chân xác định; nhãn hạng A1/A, B1 và điểm liệt có kích thước đúng theo Công văn. Có 282 câu không gắn ảnh, không phát hiện câu nào trong nhóm này nhắc rõ hình vẽ/biển trong hình bằng phép quét đã dùng.

Có **7 cặp trùng cả câu hỏi và lựa chọn dạng chữ**, nhưng tất cả đều có hình và đáp án khác nhau: 389/396, 392/393, 395/397, 419/420, 462/463, 480/481, 567/568. Không coi chúng là nhãn mâu thuẫn: ảnh khác nhau là một phần đầu vào mà JSONL hiện chỉ giữ cờ `co_hinh`, chưa giữ đường dẫn ảnh. Không dùng các cặp này cho eval text-only.

Trong 282 câu thuần chữ có hai nhóm trùng riêng câu hỏi nhưng lựa chọn khác nhau; không phải bản sao nguyên mẫu. Chưa chứng nhận toàn bộ 282 đáp án còn phù hợp tại cutoff2026: nguồn đề là2025 và cần rà so với phiên bản quy định tương ứng. Cũng cần tách câu kỹ thuật xe/văn hóa khỏi câu có căn cứ trong corpus luật khi báo cáo kết quả.

## 7. Kết quả kiểm tra kỹ thuật qua

| Kiểm tra | Lỗi |
|---|---:|
| File raw thiếu/dư, sai hash, sai bytes, trùng đường dẫn manifest | 0 |
| Trùng `unit_id` hoặc `version_id`, ID có hậu tố `#` | 0 |
| Địa chỉ cấu trúc sai trường / con gốc thiếu cha | 0 |
| Ngày ISO sai, khoảng rỗng/âm, khoảng gốc chồng lấn | 0 |
| Ngoại lệ dẫn tới địa chỉ căn cứ không có trong toàn bộ phiên bản | 0 |
| Văn bản đã ghép khác kết quả dựng lại | 0/33 |
| Đơn vị gốc khác kết quả parse lại | 0/17.903 |
| Phiên bản khác kết quả áp sửa đổi và gắn nhãn lại | 0/18.842 |
| GPLX khác kết quả trích lại / sai schema | 0/600 |
| Bộ trường không đồng nhất trong mỗi JSONL | 0 |
| NFC, ký tự thay thế, ký tự Kirin/Hy Lạp/điều khiển trong lớp text được quét | 0 |

Các kiểm tra rác trong nội dung luật không phát hiện header/chuyển trang Công báo, dấu ký số, footer web hoặc khối chữ ký/Nơi nhận lạc vào thân theo mẫu đã quét. Phép quét ban đầu có false positive “vận tải về” với chuỗi “Tải về”; đã loại mẫu đó và chạy lại, không tính chúng thành watermark.

Ba khác biệt giữa đề xuất ngày tự động và bản duyệt được giải thích trong bản duyệt: hai VBHN dùng mốc snapshot01/07/2025 thay ngày luật gốc; QCVN dùng ngày văn bản cha. Không ghi đè bản duyệt bằng kết quả tự động.

## 8. Thứ tự xử lý trước khi chốt data

1. Sửa extractor bảo toàn ô bảng và ký hiệu; bổ sung kiểm tra bằng các giá trị nguồn xác nhận ở F01/F02; dựng lại dữ liệu và kiểm tra diff nội dung.
2. Sửa phân loại phụ lục TT51; rà lại những phụ lục bị loại bởi từ không dấu và các phụ lục vừa chứa mẫu vừa có quy cách bắt buộc.
3. Áp đầy đủ quan hệ thay thế phụ lục hoặc loại có căn cứ khỏi phạm vi truy vấn; xử lý đồng thời mọi mảnh của một phụ lục.
4. Gắn trạng thái cho Điều bãi bỏ và cờ thiếu nội dung/ngoài phạm vi. Duy trì corpus lưu trữ, tạo riêng view dùng cho QA/RAG.
5. Chốt cách ghép cha/con và điều kiện theo thời điểm; kiểm thử trực tiếp ba nhánh cùng sống và ba Khoản TT12 gia hạn.
6. Sau các thay đổi trên, chạy lại EDA, số liệu báo cáo, bộ kiểm tra và lưu hash của bản dữ liệu chốt. Chỉ sau đó sinh eval/train từ view đã duyệt.

## 9. Tái chạy và bằng chứng

Chạy từ gốc `du_an_hien_tai`:

```powershell
py -3.13 -X utf8 docs/reviews/data-audit-2026-10-16/audit.py
py -3.13 -X utf8 docs/reviews/data-audit-2026-10-16/forensics.py
py -3.13 -X utf8 docs/reviews/data-audit-2026-10-16/verify_word_cache.py
py -3.13 -m pytest -q
```

Các script ghi bằng chứng cạnh script, không ghi vào `data/`. Script Word mở raw và cache bằng một tiến trình Word riêng, read-only, ẩn giao diện và tắt macro. `audit.py` dựng từ cache Word, còn bước đối chiếu raw Word/cache là kiểm tra bổ sung tách riêng.

- `summary.json`, `checks.json`: số liệu và toàn bộ trường hợp quét cấu trúc.
- `input_hashes.json`: hash dữ liệu/code đầu vào; `summary.json.input_drift` rỗng ở lượt cuối.
- `source_rebuild.json`, `per_document.json`: tái dựng và quy mô từng văn bản.
- `forensic_summary.json`: kiểm tra độc lập XML/schema và các phát hiện xác nhận.
- `table_adjacent_duplicate_cells.json`, `word_symbols_context.json`: hàng bảng, ký hiệu bị ảnh hưởng và địa chỉ liên quan.
- `confirmed_stale_annexes.json`, `annex_classifier_unaccented_matches.json`: ví dụ làm sai hiệu lực/phạm vi tìm kiếm.
- `rendered_source_pages.json` và PNG: file nguồn, trang và nội dung đã render.
- `word_cache_verification.json`: kết quả so raw Word với cache; xem phụ lục cập nhật khi bước chạy hoàn tất.

## 10. Kiểm kê từng văn bản

| Văn bản | Đơn vị gốc | Phiên bản | Bản được lọc tại cutoff |
|---|---:|---:|---:|
| `blds_2015` | 2,421 | 2,419 | 2,419 |
| `luat_118_2025` | 216 | 214 | 214 |
| `luat_35_2024` | 859 | 917 | 851 |
| `luat_36_2024` | 974 | 1,030 | 976 |
| `nd_10_2022` | 127 | 159 | 123 |
| `nd_138_2021` | 140 | 138 | 138 |
| `nd_158_2024` | 937 | 1,255 | 941 |
| `nd_160_2024` | 364 | 362 | 362 |
| `nd_165_2024` | 838 | 1,068 | 869 |
| `nd_168_2024` | 1,298 | 1,470 | 1,306 |
| `nd_175_2025` | 25 | 23 | 23 |
| `nd_218_2026` | 328 | 326 | 326 |
| `nd_220_2026` | 27 | 25 | 25 |
| `nd_238_2026` | 156 | 154 | 154 |
| `nd_241_2026` | 274 | 272 | 272 |
| `nd_336_2025` | 444 | 442 | 442 |
| `nd_39_2023` | 112 | 110 | 110 |
| `nd_51_2025` | 6 | 4 | 4 |
| `nd_67_2023` | 587 | 702 | 593 |
| `qcvn_41_2024` | 400 | 399 | 399 |
| `tt_108_2026_bca` | 481 | 479 | 476 |
| `tt_12_2025_bca` | 427 | 425 | 17 |
| `tt_155_2025_btc` | 41 | 39 | 39 |
| `tt_30_2026_bxd` | 363 | 361 | 361 |
| `tt_36_2024_byt` | 54 | 52 | 52 |
| `tt_37_2026_bca` | 16 | 14 | 14 |
| `tt_38_2024_bgtvt` | 57 | 55 | 55 |
| `tt_51_2024_bgtvt_qcvn41` | 6 | 4 | 4 |
| `tt_51_2025_bca` | 21 | 19 | 19 |
| `tt_65_2024_bca` | 72 | 70 | 70 |
| `tt_79_2024_bca` | 431 | 438 | 421 |
| `vbhn_135_2025_blhs` | 4,569 | 4,567 | 4,567 |
| `vbhn_63_2025_xlvphc` | 832 | 830 | 830 |

Cột cuối là kết quả hàm lọc hiện tại, chịu các giới hạn F03–F06 đã nêu; không phải kiểm định độc lập tình trạng pháp lý từng đơn vị.


## 11. Đối chiếu raw Word với cache và bảo toàn đầu vào

Đã mở read-only cả raw lẫn cache cho **45/45 file Word được chọn**. **44 cặp có main-story text giống hệt**. Cặp còn lại `nd_165_2024__p4.doc` khác đúng một ký tự điều khiển Word U+0015 ở mẫu chứng chỉ; đối chiếu tiền tố/hậu tố cho thấy không mất chữ/số ở vùng này. Không xem đây là lỗi nội dung luật. Kết quả main-story không thay thế kiểm tra riêng text box, bảng và ký hiệu đã nêu. Bằng chứng: `word_cache_verification.json`, `word_cache_difference_linear.json`.

Kiểm tra cuối đối với **627 file dữ liệu/code đã hash**: **0 file đổi hoặc mất** so với snapshot audit. Không có chỉnh sửa data hoặc code pipeline do các script audit.
