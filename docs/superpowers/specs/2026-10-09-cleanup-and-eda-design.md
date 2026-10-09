# Thiết kế: làm sạch bổ sung và EDA kho văn bản luật

- **Ngày:** 2026-10-09
- **Trạng thái:** Bản nháp chờ duyệt
- **Thuộc dự án:** `docs/superpowers/specs/2026-10-08-traffic-law-qa-design.md` (mục 5.4 và 6A)
- **Đầu vào:** kết quả của kế hoạch `docs/superpowers/plans/2026-10-08-legal-text-processing.md` trong `data/processed/`, danh sách việc tồn đọng `docs/superpowers/followups/2026-10-09-legal-processing-followups.md`

## 1. Mục tiêu và phạm vi

Đợt này gồm hai phần làm theo thứ tự:
1. **Làm sạch bổ sung** (mục 3): sửa các lỗi còn lại ở khâu làm sạch để giai đoạn dữ liệu có thể coi là xong.
2. **EDA kho văn bản luật** (mục 4): phần A của mục 6 bản thiết kế dự án, chạy trên dữ liệu đã sạch.

**Ngoài phạm vi:** xử lý đề GPLX và EDA phần B; EDA dữ liệu train (phần C); cắt đoạn, embedding, nạp PostgreSQL; chia nhỏ phụ lục dài (để sang bước cắt đoạn vì đó là tiền xử lý, không phải lỗi).

## 2. Nguyên tắc chung
- Mọi sửa đổi nằm trong code xử lý `src/lawproc` và chạy lại bằng `scripts/process_legal.py`; không vá tay file đầu ra. Viết test trước khi sửa.
- Không sửa `data/raw/`.
- Dữ liệu cần người duyệt (mốc hiệu lực ngoại lệ, phân loại phụ lục nếu tự động không chắc) nằm trong file CSV riêng, có cột ghi căn cứ; người dùng duyệt trước khi áp.
- Sau đợt làm sạch: toàn bộ test hiện có vẫn qua; bộ test toàn vẹn dữ liệu (`tests/test_processed_invariants.py`) được mở rộng cho từng lỗi đã sửa; chạy lại quy trình hai lần cho ra kết quả giống hệt.
- Commit không ghi Claude là tác giả hay đồng tác giả.

## 3. Phần 1: làm sạch bổ sung

### L1. Phần kết văn bản
**Lỗi:** khoảng 22 đơn vị cuối văn bản chứa dòng thông qua và chữ ký, ví dụ `luat_36_2024:d89:k7` chứa "Luật này được Quốc hội … thông qua ngày …" và "CHỦ TỊCH QUỐC HỘI Trần Thanh Mẫn"; `nd_238_2026:d21` chứa "TM. CHÍNH PHỦ KT. THỦ TƯỚNG PHÓ THỦ TƯỚNG daky] Phạm Gia Túc".

**Sửa:** bộ tách cấu trúc nhận diện điểm bắt đầu phần kết, ngoài đoạn trích dẫn và ngoài phụ lục:
- dòng bắt đầu bằng "Luật này được Quốc hội", "Bộ luật này được Quốc hội" (kèm "thông qua");
- dòng bắt đầu bằng khối chữ ký: `TM.`, `KT.`, `Q.`, `TL.`, `PP.` theo sau là chữ in hoa; hoặc đúng các chức danh in hoa `CHỦ TỊCH QUỐC HỘI`, `THỦ TƯỚNG`, `PHÓ THỦ TƯỚNG`, `BỘ TRƯỞNG`, `THỨ TRƯỞNG`.

Từ dòng đó đến phụ lục hoặc "Nơi nhận" thuộc đơn vị `ket_thuc` (cấp đã có sẵn).

**Kiểm tra:** không đơn vị nào ngoài `ket_thuc` có dòng khớp các mẫu trên.

### L2. QCVN 41:2024/BGTVT thành văn bản riêng
**Lỗi:** mục lục đầu quy chuẩn (dòng có dấu chấm dẫn, ví dụ "Phụ lục A - Đèn tín hiệu ……") bị nhận là 13 phụ lục, 12 cái rỗng; toàn bộ phần thân quy chuẩn (Phần, Chương, Điều) bị gộp vào `tt_51_2024_bgtvt_qcvn41:pl13` dài khoảng 125 nghìn ký tự.

**Sửa:**
1. Bỏ dòng mục lục trước khi tách cấu trúc: dòng kết thúc bằng chuỗi từ 5 dấu chấm hoặc dấu "…" trở lên, có thể kèm số trang. Áp cho mọi văn bản.
2. Tách văn bản `tt_51_2024_bgtvt_qcvn41` tại dòng mở đầu quy chuẩn (dòng chứa "QCVN 41:2024/BGTVT QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ BÁO HIỆU ĐƯỜNG BỘ"). Phần trước dòng đó giữ mã `tt_51_2024_bgtvt_qcvn41` (Thông tư 2 Điều). Phần từ dòng đó trở đi thành văn bản mới `qcvn_41_2024`, ghi ra `data/processed/documents/qcvn_41_2024.txt`.
3. `qcvn_41_2024` là văn bản suy ra, không có dòng riêng trong `data/manifest.csv`. Khai báo trong `config.py` (văn bản cha, số hiệu `QCVN 41:2024/BGTVT`, nhóm "Biển báo"). Ngày hiệu lực lấy theo Thông tư 51, thêm một dòng vào `effective_dates.csv`.
4. Bộ tách cấu trúc nhận heading `PHẦN <số>` và lưu vào trường mới `phan` (các văn bản khác để trống). Chương, Điều, Khoản, Điểm tách như bình thường. Các phụ lục A–P sau phần thân thuộc `qcvn_41_2024`.
5. Kiểm tra danh tính: `qcvn_41_2024` phải chứa số hiệu `QCVN 41:2024/BGTVT` ở đầu văn bản.

**Kiểm tra:** không còn phụ lục rỗng; `qcvn_41_2024` có các Điều đánh số liên tục từ 1; không phụ lục nào của QCVN chứa dòng mở đầu bằng "Điều <số>." của phần thân.

### L3. Chữ lặp trong bảng
**Lỗi:** 5 file Word có bảng lồng nhau hoặc ô gộp; `extract.docx_lines` lấy cùng một ô nhiều lần.

**Sửa:** khi duyệt bảng, mỗi ô (theo phần tử `w:tc`) chỉ lấy một lần; bảng lồng trong ô được duyệt đúng một lần.

**Kiểm tra:** test với file docx mẫu có ô gộp ngang, ô gộp dọc và bảng lồng; chạy lại 5 văn bản bị ảnh hưởng, so số dòng lặp liền nhau trước và sau.

### L4. Nhãn điểm có số
**Lỗi:** nhãn như `k1)` bị ghép vào điểm `k`.

**Sửa:** mẫu nhận diện điểm thành chữ cái (gồm `đ`), một hoặc hai chữ, có thể kèm một chữ số, theo sau là `)`. Địa chỉ dạng `…:k5:k1`.

**Kiểm tra:** test đơn vị; số điểm của các văn bản không có nhãn kiểu này không đổi.

### L5. Ngày hiệu lực ngoại lệ
**Lỗi:** một số quy định có mốc áp dụng khác ngày hiệu lực chung, nên tại 01/10/2026 bị coi sai trạng thái (chi tiết trong file việc tồn đọng).

**Sửa:**
1. Tạo `data/effective_exceptions.csv`, cột: `unit_id`, `loai`, `tu_ngay`, `den_ngay`, `dieu_kien`, `can_cu`, `ghi_chu`. Ba loại:
   - `gia_han`: đơn vị đáng lẽ hết hiệu lực nhưng còn áp dụng đến `den_ngay` (các phần TT 12/2025 còn đến 28/02/2027). Bản ghi cuối của đơn vị được giữ hiệu lực đến `den_ngay`.
   - `hoan_ap_dung`: bản mới chỉ áp dụng cho một số trường hợp đến `tu_ngay`; bản cũ còn áp dụng cho trường hợp còn lại (`dieu_kien`) đến `tu_ngay` (NĐ 238 Điều 18). Cả hai bản ghi được gắn ngoại lệ; trong khoảng đó cả hai cùng được trả về khi lọc theo thời điểm, kèm điều kiện.
   - `moc_trong_noi_dung`: chính nội dung đơn vị ghi mốc áp dụng tương lai (Luật 36 Điều 35 khoản 2; TT 108 Điều 41 khoản 2–5). Không đổi hiệu lực, chỉ gắn cờ để bước sinh câu hỏi và bộ eval biết.
2. Trợ lý soạn file từ nội dung văn bản, mỗi dòng ghi căn cứ (văn bản, Điều, Khoản). **Người dùng duyệt trước khi áp.**
3. Bản ghi trong `legal_units_versioned.jsonl` có thêm trường `hl_ngoai_le`: danh sách ngoại lệ áp vào bản ghi đó (rỗng nếu không có).
4. Hàm lọc theo thời điểm `in_force_at(record, t)` dùng chung cho mọi giai đoạn sau, có xét ngoại lệ, trả về có hiệu lực hay không và điều kiện kèm theo.

**Kiểm tra:** kiểm tra "không chồng phiên bản" chỉ cho phép chồng khi có ngoại lệ `hoan_ap_dung`; tại 01/10/2026 các đơn vị trong file có trạng thái đúng như cột `loai`.

### L6. Phiên bản không đổi nội dung
**Lỗi:** 184 phiên bản mới có tiêu đề và nội dung giống hệt phiên bản liền trước (sinh ra khi văn bản sửa đổi chép lại cả khoản).

**Sửa:** giữ bản ghi, thêm trường `noi_dung_doi` (true nếu khác phiên bản liền trước hoặc là phiên bản đầu).

**Kiểm tra:** đúng 184 bản ghi `noi_dung_doi = false` (hoặc số mới nếu L1–L4 làm thay đổi văn bản, ghi lại trong báo cáo).

### L7. Phụ lục OCR kém và phụ lục mẫu biểu
**Lỗi:** phụ lục của `tt_108_2026_bca` và `tt_36_2024_byt` OCR kém (ví dụ "Bé trí" thay cho "Bố trí"; mẫu giấy khám sức khỏe gần như không đọc được).

**Sửa:**
1. Thêm chỉ số chất lượng chữ: tỷ lệ âm tiết không phải âm tiết tiếng Việt hợp lệ (kiểm tra theo cấu trúc phụ âm đầu, vần, dấu), tính cho từng đơn vị.
2. OCR lại các trang phụ lục của hai văn bản ở 400 dpi (hiện 300 dpi); giữ bản nào có chỉ số tốt hơn theo từng trang. Cache OCR gắn với sha256 file và dpi.
3. Thêm trường `loai_phu_luc` cho đơn vị phụ lục: `mau_bieu` (tiêu đề có "Mẫu", hoặc nội dung chủ yếu là ô điền "……") hoặc `noi_dung`. Trợ lý xuất danh sách phân loại để người dùng xem lại.
4. Phụ lục `noi_dung` còn lỗi: thêm dòng vào `data/ocr_corrections.csv` như đợt trước. Phụ lục `mau_bieu` không sửa chữ; giai đoạn xây kho tra cứu sẽ không đưa chúng vào.
5. Đơn vị nào vẫn vượt ngưỡng lỗi sau khi sửa thì gắn `chat_luong = kem` và ghi vào mục hạn chế của báo cáo.

**Kiểm tra:** chỉ số chất lượng của hai văn bản trước và sau ghi trong báo cáo; mọi phụ lục có `loai_phu_luc`.

### L8. Báo cáo
- Cập nhật `data/processed/PROCESSING_REPORT.md` theo số liệu mới.
- Thêm **bảng kiểm tra chất lượng**: mỗi dòng là một kiểm tra, số trường hợp phát hiện, cách xử lý, kết quả. Gồm cả các kiểm tra của đợt trước (80 dòng sửa OCR, kiểm tra danh tính 32/32…). Dùng trực tiếp cho báo cáo môn.
- Cập nhật file việc tồn đọng: đánh dấu các mục đã xong.

## 4. Phần 2: EDA kho văn bản luật

### 4.1 Tổ chức
- Hàm tính toán trong `src/lawproc/eda.py`, có test: rút mức phạt, rút điểm trừ GPLX, đếm tham chiếu chéo, đếm từ và token, tìm cặp gần trùng, thống kê sửa đổi.
- Notebook `notebooks/01_eda_kho_luat.ipynb` gọi các hàm trên, vẽ biểu đồ, viết nhận xét bằng tiếng Việt. Notebook được chạy bằng `jupyter nbconvert --execute --to notebook --inplace` và lưu kèm kết quả.
- Hình lưu ở `reports/eda/figures/` (PNG, tên file theo mã phân tích, ví dụ `e3_do_dai_khoan.png`).
- Thời điểm phân tích mặc định T = 01/10/2026; dữ liệu "đang hiệu lực" lấy qua `in_force_at` (L5).

### 4.2 Các phân tích
| # | Phân tích | Quyết định mà nó phục vụ |
|---|---|---|
| E1 | Quy mô: số văn bản, số đơn vị theo cấp, theo văn bản và theo nhóm chủ đề (cột `nhom` của manifest); số bản ghi đang hiệu lực tại T | Phân bổ câu hỏi theo chủ đề trong ma trận đề |
| E2 | Phạm vi thực của BLDS 2015 và VBHN BLHS: tỷ lệ đơn vị trong kho; các Chương/Điều liên quan giao thông (bồi thường do nguồn nguy hiểm cao độ, tội vi phạm quy định về tham gia giao thông…) | Giới hạn phần đưa vào kho tra cứu để hai bộ luật không lấn át kết quả tìm kiếm |
| E3 | Độ dài đơn vị (Điều, Khoản, Điểm, Phụ lục) theo số từ, số token tokenizer Qwen3.5-9B và bge-m3: phân vị, đơn vị quá dài và quá ngắn | Cỡ đoạn khi cắt; cắt theo Khoản hay ghép Điểm; danh sách phụ lục phải chia nhỏ |
| E4 | Mức phạt NĐ 168 (bản đang hiệu lực tại T): số khung phạt, phân bố mức tối thiểu và tối đa, theo loại phương tiện (suy từ tiêu đề Điều) và nhóm hành vi; số điểm GPLX bị trừ | Phân bổ câu hỏi về mức phạt; cách chấm con số trong câu trả lời |
| E5 | Sửa đổi: số đơn vị bị sửa, bổ sung, bãi bỏ theo văn bản đích, văn bản sửa và ngày; số sửa đổi có `noi_dung_doi = true` | Số câu hỏi có thể viết cho bộ RQ3 |
| E6 | Dòng thời gian hiệu lực các văn bản và các mốc ngoại lệ, 2024–2029 | Câu hỏi theo mốc thời gian; minh họa rủi ro trả lời theo luật cũ |
| E7 | Từ vựng sau khi tách từ (pyvi): thuật ngữ đặc trưng theo nhóm (TF-IDF theo nhóm), các cặp cách gọi pháp lý và đời thường gặp trong kho (ví dụ "xe mô tô" và "xe máy") | Nguyên liệu viết biến thể đời thường; cân nhắc mở rộng truy vấn |
| E8 | Đơn vị gần trùng giữa các văn bản: cosine TF-IDF n-gram ký tự, ngưỡng 0,9, chỉ trên bản ghi đang hiệu lực | Có cần lọc kết quả gần trùng khi tìm kiếm |
| E9 | Tham chiếu chéo: số lần dẫn "điểm… khoản… Điều…", trong cùng văn bản và sang văn bản khác, đơn vị được dẫn nhiều nhất | Có cần kéo kèm đơn vị được dẫn vào ngữ cảnh RAG |
| E10 | Chất lượng sau làm sạch: đơn vị rỗng, ký tự ngoài bảng chữ tiếng Việt, chỉ số âm tiết lỗi (L7), dòng phần kết còn sót | Bảng kiểm tra chất lượng (L8); mục hạn chế |

Mỗi phân tích kết thúc bằng một ô "Phát hiện → hành động" trong notebook.

### 4.3 Đầu ra
1. Notebook đã chạy kèm hình.
2. `reports/eda/findings.md`: bảng "phát hiện → hành động", mỗi dòng ghi mã phân tích, phát hiện kèm số liệu, hành động, giai đoạn thực hiện.
3. `data/eval/eval_matrix.csv`: ma trận đề cho bộ eval thủ công khoảng 150 câu. Cột: `chu_de`, `van_ban`, `loai_cau`, `so_cau`, `ghi_chu`. `loai_cau` gồm: chung, định nghĩa, mức phạt, thủ tục, hành vi cấm, tình huống. Phân bổ ban đầu theo số đơn vị đang hiệu lực trong phạm vi của mỗi nhóm (sau giới hạn ở E2), mỗi nhóm tối thiểu 5 câu, có thêm trọng số cho nhóm người dân hỏi nhiều (Xử phạt, GPLX, Đăng ký xe); quy tắc phân bổ ghi trong notebook. Nhóm điều chỉnh rồi chốt trước khi viết bộ eval.

### 4.4 Thư viện và file cần tải (xin phép trước khi tải)
- Thư viện Python: `matplotlib`, `nbconvert`, `nbclient`, `scikit-learn`, `tokenizers`, `pyvi`. Ghi phiên bản vào `requirements.txt`.
- File `tokenizer.json` của Qwen3.5-9B và bge-m3 từ Hugging Face (chỉ tokenizer), lưu ở `tools/tokenizers/` (không đưa lên Git), ghi nguồn và sha256 trong notebook.

### 4.5 Kiểm thử
- Test đơn vị cho các hàm trong `eda.py` với câu mẫu thật từ NĐ 168 (mức phạt "từ 800.000 đồng đến 1.000.000 đồng", trừ điểm "trừ điểm giấy phép lái xe 04 điểm"), tham chiếu "điểm a khoản 2 Điều 6 của Nghị định này".
- Notebook chạy lại từ đầu không lỗi và cho cùng số liệu.

## 5. Thứ tự thực hiện và điểm dừng duyệt
1. L3, L4, L1, L2 (sửa trích chữ và tách cấu trúc), chạy lại quy trình.
2. L7 (OCR lại, phân loại phụ lục) → **người dùng xem danh sách phân loại phụ lục**.
3. L5 → **người dùng duyệt `effective_exceptions.csv`** → áp. L6.
4. L8, gộp nhánh làm sạch.
5. Xin phép cài thư viện và tải tokenizer → EDA E1–E10 → findings và ma trận đề → **người dùng duyệt ma trận đề**.

## 6. Rủi ro
- Tách phần kết có thể cắt nhầm câu có chữ in hoa ở đầu dòng trong thân văn bản: chỉ nhận mẫu chức danh cố định và chỉ sau Điều cuối có số lớn nhất; có test với các văn bản sửa đổi (chứa trích dẫn).
- Bỏ dòng mục lục có thể bỏ nhầm dòng bảng có dấu chấm dẫn: chỉ bỏ khi dòng không bắt đầu bằng nhãn Điều/Khoản/Điểm; so số đơn vị của mọi văn bản trước và sau.
- Tách QCVN làm đổi mã đơn vị của TT 51: chưa có giai đoạn nào sau dùng mã cũ nên không ảnh hưởng.
- OCR 400 dpi chậm hơn: chỉ chạy cho trang phụ lục của hai văn bản; có cache.
