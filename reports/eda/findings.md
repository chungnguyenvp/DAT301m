# Phát hiện từ EDA kho văn bản luật

Phân tích dữ liệu `data/processed/legal_units_versioned.jsonl` bản chốt `data-v1` (sau PR #6 kiểm tra dữ liệu cuối), tại thời điểm T = **2026-10-01**, từ notebook đã chạy `notebooks/01_eda_kho_luat.ipynb` (nguồn `notebooks/01_eda_kho_luat.py`). Ngày chạy: **2026-10-17**. Số liệu đối chiếu tại `reports/eda/summary.json`; ma trận đề lấy từ `data/eval/eval_matrix.csv`.

“Có hiệu lực” được tính bằng `in_force_at(record, T)[0]`, có xét ngoại lệ. Tập đang có hiệu lực gồm **17.674 phiên bản**, tương ứng **17.671 `unit_id`**. Các thống kê theo đơn vị có hiệu lực tại T dùng bản đại diện mới nhất của mỗi địa chỉ để mô tả; cách chọn này không xác nhận bản mới nhất áp dụng cho mọi đối tượng. E5 phân tích các dòng trong CSV sửa đổi đã duyệt và toàn bộ phiên bản lưu để thống kê lịch sử sửa đổi. E6 dựng dòng thời gian và đếm lượt sự kiện tương lai từ toàn bộ bản ghi lưu, kể cả phiên bản không có hiệu lực tại T. Kiểm tra khoảng trống nguồn E10 cũng xét toàn bộ phiên bản lưu, độc lập với T. Có **6 phiên bản thuộc 3 địa chỉ nhiều nhánh** và **16 phiên bản kèm điều kiện**: phải giữ metadata điều kiện và đối chiếu đối tượng, thời điểm, tình huống trước khi kết luận áp dụng. Thống kê và metadata không tự động giải quyết khả năng áp dụng pháp lý.

## Phát hiện → hành động

| Mã | Phát hiện (kèm số liệu) | Hành động | Giai đoạn |
| --- | --- | --- | --- |
| E1 | Kho có 20.500 phiên bản của 40 văn bản; tập đại diện tại T có 2.216 Điều, 7.118 Khoản, 8.185 Điểm và 152 phụ lục. | Tách địa chỉ đơn vị khỏi phiên bản; lưu ngày hiệu lực và nguồn trích dẫn khi lập chỉ mục. | Cắt đoạn và xây kho tra cứu |
| E1 | 6 phiên bản thuộc 3 địa chỉ nhiều nhánh; 16 phiên bản có điều kiện. | Giữ mọi nhánh có hiệu lực và điều kiện; lọc theo đối tượng, không suy áp dụng chung từ bản mới nhất. | Cắt đoạn và xây kho tra cứu |
| E1 | Tai nạn có 6.985 đơn vị, Tốc độ có 55; 13 văn bản sửa đổi chứa 1.285 đơn vị. | Dùng phạm vi E2 đã chốt, tách chỉ dẫn sửa đổi khỏi nội dung đích đã áp sửa đổi; phân bổ eval theo căn bậc hai thay vì tỷ lệ thô. | Bộ eval |
| E2 | BLDS và BLHS có 6.985/17.671 đơn vị (39,5%); phạm vi đã chốt giữ 213 và để ngoài 6.772 đơn vị. | Dùng cờ `trong_pham_vi` có sẵn trong dữ liệu thay vì xóa; kho tra cứu, bộ eval và dữ liệu train chỉ lấy 213 đơn vị trong phạm vi. | Cắt đoạn và xây kho tra cứu |
| E2 | Phạm vi đã chốt gồm 25 Điều BLDS 584–608 và 7 Điều BLHS 260–266; Điều 267 BLHS chuyển sang đường sắt. | Giữ hai khoảng đã chốt (`config.SCOPE_DIEU`); dùng BLDS làm nguồn hỗ trợ bồi thường dân sự, không gán toàn bộ Chương XX là luật giao thông. | Cắt đoạn và xây kho tra cứu |
| E3 | 7.118 ứng viên Khoản kèm Điểm và tiêu đề Điều có trung vị 77, P95 344 token bge-m3; 123 vượt 512 token. | Thử trần 512 token; tách theo Điểm hoặc ranh giới câu khi dài, giữ địa chỉ và nguồn. | Cắt đoạn và xây kho tra cứu |
| E3 | Phạm vi RAG đã chốt còn 3.880 ứng viên, P95 389 token; 93 vượt 512. | Rà 93 ứng viên dài; đo lại chuỗi có metadata, điều kiện và prompt trước khi chốt ngân sách token. | Cắt đoạn và xây kho tra cứu |
| E3 | Có 2.298 đơn vị dưới 5 từ; sáu phiên bản thuộc ba địa chỉ có điều kiện được đo riêng. | Ghép đơn vị ngắn với ngữ cảnh cha; chỉ ghép nhánh tương thích sau kiểm tra, chưa triển khai phép ghép bản đại diện thành chunk pháp lý. | Cắt đoạn và xây kho tra cứu |
| E3 | Text Khoản–Điểm không có tiêu đề Điều: trung vị 62, P95 321 token, 108 vượt 512; thêm tiêu đề làm tăng trung vị chênh token 11 và P95 chênh 37. | Đo chunk hoàn chỉnh bằng tokenizer, không cộng token từng phần; dành chỗ cho địa chỉ, điều kiện và prompt chưa được đo. | Cắt đoạn và xây kho tra cứu |
| E4 | Regex lấy khung tiền đầu tiên trong 190 Khoản NĐ168, từ 100.000 đến 75.000.000 đồng; bên dưới có 574 Điểm cấu trúc. | Đối chiếu Khoản, Điểm, đối tượng và điều kiện; không coi 574 Điểm là số hành vi pháp lý duy nhất hoặc khung đầu tiên là toàn bộ biểu phạt. | Cắt đoạn và xây kho tra cứu |
| E4 | Mức trừ điểm đầu tiên khớp 48 bản đại diện: 2 điểm (18), 3 (2), 4 (9), 6 (9), 8 (2), 10 (8). | Kiểm tra câu dẫn bổ sung và phạm vi áp dụng trong eval mức phạt/tình huống; bổ sung parser nhiều mức trước khi lập bảng đầy đủ. | Bộ eval |
| E5 | 568 dòng sửa đổi đã duyệt: 481 sửa đổi, 55 bổ sung, 28 bãi bỏ và 4 thay thế văn bản. | Dùng trạng thái đã duyệt cùng ngày hiệu lực từng dòng khi truy hồi theo thời gian; không áp mọi dòng ứng viên. | Cắt đoạn và xây kho tra cứu |
| E5 | Có 1.128 phiên bản sinh từ sửa đổi; 731 địa chỉ Khoản/Điểm có cả bản gốc và bản sửa khác nội dung. | Chọn cặp trước/sau từ các địa chỉ này cho eval RQ3, kiểm tra điều kiện hiệu lực rồi duyệt câu hỏi thủ công; chưa sinh câu hỏi. | Bộ eval |
| E6 | TT12 có ngoại lệ gia hạn đến mốc kết thúc loại trừ 01/03/2027, còn áp dụng đến hết 28/02/2027 cho đơn vị đủ điều kiện. | Gọi `in_force_at` trên từng phiên bản; không suy trạng thái quy định từ đoạn tổng quan văn bản. | Cắt đoạn và xây kho tra cứu |
| E6 | Có 48 lượt sự kiện tương lai theo bản ghi: 5 tại 01/01/2027, 20 tại 01/03/2027, 6 tại 01/07/2027, 12 tại 01/01/2028 và 5 tại 01/01/2029. | Kiểm thử ngày ngay trước và đúng mốc; khử trùng khi lập lịch vì đây không phải số sự kiện pháp lý độc lập. | Đánh giá |
| E7 | Trong tập text đã lọc, “giấy phép lái xe” có 885 lần, “bằng lái” 1; “xe ô tô” 863, “xe hơi” 0; “mũ bảo hiểm” 28, “nón bảo hiểm” 0. | Thêm ánh xạ đời thường → thuật ngữ và kiểm thử các cách diễn đạt; không suy cùng phạm vi pháp lý từ đồng nghĩa. | Cắt đoạn và xây kho tra cứu |
| E7 | “Xe mô tô” có 275 lần, mẫu “xe máy” 121; “đèn tín hiệu” 130, mẫu “đèn đỏ/đèn xanh” 44. | Dùng biến thể ngôn ngữ làm nhóm kiểm tra truy hồi riêng, đối chiếu phương tiện/tình huống trước khi mở rộng truy vấn. | Bộ eval |
| E7 | TF-IDF tính trên 12 tài liệu gộp theo nhóm; top 5 Biển báo có “w”, “ie”, Bảo hiểm có “khớp”, “gẫy”. | Rà mã biển, nhiễu OCR và nội dung bảng chuyên ngành; không diễn giải thứ hạng là nhu cầu người dùng hay tần suất từng văn bản. | Báo cáo |
| E8 | Trong 5.166 đơn vị đủ điều kiện có 92 cặp khác văn bản đạt cosine TF-IDF ký tự ≥ 0,9; NĐ168–NĐ336 chiếm 48/92 cặp; ví dụ Luật36 Điều 27 Khoản 2 và QCVN Điều 7 Khoản 1 đạt 1,0. | Gắn nhóm gần trùng để giảm kết quả lặp, duyệt nguồn thích hợp khi xếp hạng; giữ mọi nguồn, ngày hiệu lực và điều kiện. Không xóa tự động hoặc suy tương đương pháp lý từ similarity. | Cắt đoạn và xây kho tra cứu |
| E9 | Regex khớp 1.557 tham chiếu đánh số trong 1.060/16.271 đơn vị (6,5%): 1.389 nội bộ và 168 bên ngoài. | Thử mở rộng ngữ cảnh theo Điều/Khoản đích; kiểm tra đúng văn bản và phiên bản trước khi đưa vào câu trả lời. | Cắt đoạn và xây kho tra cứu |
| E9 | 168 kết quả được parser gắn nhãn bên ngoài; phép đếm chỉ bao phủ mẫu đánh số đã hỗ trợ. | Duyệt ví dụ và mở rộng nhận diện tên văn bản; không coi kết quả regex là liên kết đã giải quyết, hoặc đơn vị không khớp là không có tham chiếu. | Cắt đoạn và xây kho tra cứu |
| E10 | Tập đại diện có 0 đơn vị rỗng cả tiêu đề/nội dung, 0 đơn vị Điều/Khoản/Điểm lẫn dòng phần kết, 0 địa chỉ có hậu tố `#`. | Giữ các kiểm tra làm cổng kiểm định khi nhập lại dữ liệu; số 0 không chứng minh nguồn đầy đủ. | Cắt đoạn và xây kho tra cứu |
| E10 | Có 17 bản đại diện nhãn `kem` và 634 lượt ký tự ngoài tập cho phép; “♦” 280, “□” 160, “” 77. | Rà ngữ cảnh và đối chiếu nguồn trước khi sửa; nhãn chất lượng là heuristic tỷ lệ âm tiết lạ, không phải độ chính xác OCR. Ký hiệu toán/ô chọn có thể hợp lệ. | Cắt đoạn và xây kho tra cứu |
| E10 | 152 phụ lục tại T gồm 105 mẫu biểu, 47 nội dung; kiểm tra toàn bộ phiên bản không thấy phụ lục QCVN M/N/O/P; NĐ39 `pl1` có 76 ký tự và mang cờ `thieu_noi_dung` (phụ lục là ảnh); TT108 `pl12` đã có đủ chữ (486 ký tự). | Tách mẫu biểu khi dựng kho; bổ sung nguồn ảnh/bảng và thân phụ lục đã được đối chiếu tại báo cáo làm sạch trước khi dùng những phần này cho eval hoặc trả lời đầy đủ. | Cắt đoạn và xây kho tra cứu |

“Từ” ở E3 là kết quả regex `\w+`, gần với đơn vị chữ/số hoặc âm tiết viết cách, không phải từ được tách bằng Pyvi. Khoản–Điểm ghép ở E3 chỉ là ứng viên đo độ dài. Kiểm tra khoảng trống nguồn ở E10 xét mọi phiên bản lưu, độc lập với T, theo danh sách đã đối chiếu trong `data/processed/PROCESSING_REPORT.md`; đây là khoảng trống đã biết, không phải kiểm kê đầy đủ. Độ ngắn hoặc thiếu đơn vị là bằng chứng về text hiện lưu; kết luận thiếu nội dung dựa vào đối chiếu nguồn trong báo cáo làm sạch. Phụ lục NĐ39 `pl1` vẫn có nhãn `ok`, nên nhãn chất lượng không chứng minh đầy đủ ảnh/bảng.

## Ma trận đề cho bộ eval

Bảng dưới là pivot **12 chủ đề × 6 loại câu** từ `data/eval/eval_matrix.csv` (36 dòng phân bổ khác 0), tổng **150 suất câu hỏi**. Số 0 biểu thị chưa phân bổ suất cho tổ hợp đó.

| Chủ đề | chung | hành vi cấm | mức phạt | thủ tục | tình huống | định nghĩa | Tổng |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Biển báo | 3 | 0 | 0 | 0 | 3 | 6 | 12 |
| Bảo hiểm | 3 | 0 | 0 | 6 | 3 | 0 | 12 |
| GPLX | 4 | 0 | 0 | 9 | 4 | 0 | 17 |
| Hướng dẫn | 4 | 0 | 0 | 7 | 3 | 0 | 14 |
| Luật lõi | 4 | 4 | 0 | 0 | 4 | 3 | 15 |
| Lệ phí | 5 | 0 | 0 | 4 | 0 | 0 | 9 |
| Nộp phạt, giữ xe | 4 | 0 | 0 | 7 | 3 | 0 | 14 |
| Tai nạn | 2 | 0 | 2 | 0 | 5 | 0 | 9 |
| Tốc độ | 4 | 0 | 0 | 0 | 4 | 0 | 8 |
| Xử phạt | 2 | 3 | 8 | 0 | 3 | 0 | 16 |
| Đăng kiểm | 2 | 0 | 0 | 5 | 2 | 0 | 9 |
| Đăng ký xe | 4 | 0 | 0 | 7 | 4 | 0 | 15 |
| **Tổng** | **41** | **7** | **10** | **45** | **38** | **9** | **150** |

Quy tắc phân bổ ban đầu trong notebook và `src/lawproc/eda.py`:

1. Đếm số **Điều** có hiệu lực theo chủ đề, trong phạm vi E2 đã chốt, không tính văn bản sửa đổi và đề thi. Trọng số mỗi nhóm là căn bậc hai số Điều; nhân **1,5** cho **Xử phạt, GPLX, Đăng ký xe**, các nhóm khác dùng trọng số 1.
2. Cấp trước tối thiểu **5 suất mỗi nhóm**, rồi chia phần còn lại theo trọng số. Lấy phần nguyên và phân bổ suất dư theo **phần dư lớn nhất**; nếu hòa phần dư, chọn theo tên khóa được sắp xếp. Cách xử lý hòa bảo đảm kết quả xác định khi chạy lại.
3. Chia số suất của mỗi nhóm theo `eda.LOAI_SPLIT`, cũng dùng phần dư lớn nhất với cùng cách xử lý hòa; bước chia loại câu không áp sàn 5. CSV chỉ lưu tổ hợp có số suất khác 0.

**Đề xuất ban đầu, duyệt và chốt trước khi viết.** Đây là phân bổ chưa được duyệt, chưa phải các câu hỏi eval thực tế và không phải dữ liệu train. Nếu điều chỉnh, sửa trực tiếp `data/eval/eval_matrix.csv` và ghi `ghi_chu` ở dòng đã đổi; không sinh lại để ghi đè quyết định đã duyệt.

## Hình

Các hình dưới đây nằm trong `reports/eda/figures/`; mô tả có thể dùng làm chú thích báo cáo.

- `e1_quy_mo_nhom.png`: Quy mô đơn vị đại diện có hiệu lực tại T theo nhóm chủ đề, cho thấy chênh lệch quy mô trước khi giới hạn phạm vi.
- `e2_pham_vi_blds_blhs.png`: Số đơn vị BLDS và BLHS trong và ngoài hai khoảng Điều đã chốt làm phạm vi hỗ trợ.
- `e3_do_dai_khoan.png`: Phân bố token bge-m3 của ứng viên Khoản ghép Điểm và tiêu đề Điều trên trục log, chưa gồm metadata, điều kiện và prompt.
- `e4_muc_phat.png`: Phân bố mức tối đa của khung tiền đầu tiên khớp regex trong Khoản NĐ168 theo nhóm phương tiện, dùng thang log.
- `e4_tru_diem.png`: Số bản đại diện NĐ168 khớp từng mức trừ điểm GPLX đầu tiên, chưa phải kiểm kê toàn bộ các mức áp dụng.
- `e5_sua_doi.png`: Số dòng sửa đổi đã duyệt theo văn bản đích và loại hành động sửa đổi, bổ sung, bãi bỏ hoặc thay thế văn bản.
- `e6_dong_thoi_gian.png`: Dòng thời gian tổng quan văn bản, mốc sửa đổi và ngoại lệ, với đường đánh dấu T; trạng thái từng đơn vị phải kiểm tra riêng.
- `e7_tu_vung.png`: Năm thuật ngữ TF-IDF nổi bật của mỗi nhóm trong tập text đã lọc và tách từ bằng Pyvi, mỗi nhóm là một tài liệu gộp.
- `e9_tham_chieu.png`: Các địa chỉ Điều/Khoản nội bộ được dẫn nhiều nhất theo mẫu regex, chưa xác nhận liên kết đích và phiên bản.
- `e10_chat_luong.png`: Phân bố heuristic tỷ lệ âm tiết lạ theo cách trích trên khoảng 0–1, không biểu diễn độ chính xác OCR.
