# Review G3: cắt đoạn và bộ chấm — 17/10/2026

**Kết luận: phần nền làm đúng hướng, nhưng chưa nên chốt Task 1–2 là hoàn tất.** Có hai lỗi ưu tiên P1 và một lỗi P2 cần sửa trước khi dùng bộ chấm để chỉnh truy hồi hoặc công bố kết quả. Các lỗi được tái hiện trên dữ liệu thật; không dựa riêng vào bản tường thuật của Claude.

Phạm vi: nhánh `feat/rag-g3`, `src/rag/chunking.py`, `src/rag/score.py`, script build, hai file test, dữ liệu chunk và manifest, kế hoạch G3, rubric eval. Đây là review mã và dữ liệu hiện có, chưa phải đánh giá chất lượng BM25/vector/reranker hoặc xác nhận độc lập nội dung pháp luật. Chưa có các phần truy hồi đó để đo.

## Kết quả kiểm tra độc lập

| Kiểm tra | Kết quả |
| --- | --- |
| `pytest -q tests/test_rag_chunking.py tests/test_rag_score.py` | 36/36 qua |
| `scripts/build_chunks.py --check` | Khớp hai file chunk khi dựng lại |
| `pytest -q` | 342/342 qua |
| Hash của hai file chunk so với manifest | Khớp |
| Theo Khoản: tổng / qua lọc ngày tại 01/10/2026 | 6.189 / 4.641 |
| Theo Điều: tổng / qua lọc ngày tại 01/10/2026 | 2.117 / 1.463 |
| Đối chiếu tiêu đề đang hiển thị với phiên bản tiêu đề tại cutoff | Không thấy tiêu đề cũ còn sót ở hai kho |

Con số 341 trong đoạn tường thuật không phải số cuối cùng: trạng thái hiện tại có 342 test. Việc thêm test kiểm file đã lưu có thể giải thích chênh lệch này; không coi đây là lỗi chức năng.

## 1. [P1] Mẩu phụ lục sai nội dung vẫn được điểm căn cứ đầy đủ

Vị trí: `src/rag/score.py:19–23`; nguồn metadata tại `src/rag/chunking.py:272`. Định nghĩa cho phép ngoại lệ này còn được ghi tại đầu `score.py` và trong kế hoạch.

`found` hợp nhất mọi `units` của top-k. Hai mẩu Phụ lục I TT155 đều mang cùng `version_id`, dù mỗi mẩu chỉ có một phần chữ. Scorer không xét `mot_phan` hay phần nội dung thực sự được phủ.

**Tái hiện tối giản:**

- Câu `lp08` / `TH087` hỏi phí đổi đăng ký xe máy; đáp án cần 70.000, 35.000 và 50.000 đồng.
- Chỉ đưa `khoan:tt_155_2025_btc:pl1@2026-01-01#1` vào kết quả. Mẩu này là phần cấp mới, không chứa ba mức phí cần trả lời.
- `score_item` trả `any = true`, `all = true`, `ty_le_nhom = 1`, `rr = 1` và không thiếu nhóm nào.
- Mẩu số 2 mới chứa các mức phí được hỏi.

Lỗi ảnh hưởng cả hai cách cắt. Với `lp06`, `lp07`, `bt04`, chọn mẩu phụ lục sai rồi bổ sung các chunk hỗ trợ còn lại cũng nhận `all = true`, dù toàn bộ top-k không có mức phí chính cần trả lời. Tổng cộng **4 câu khác nhau: 2 dev và 2 test**; script tái hiện 8 trường hợp khi kiểm cả hai cách cắt.

Claude đã ghi nhận lựa chọn này là hạn chế. Tuy nhiên, ghi hạn chế không làm điểm số trở thành phép đo đủ căn cứ: nó đang chấm đúng mã phụ lục thành đủ bằng chứng. Điều này làm lệch cả việc chỉnh trên dev và kết quả test, đồng thời đi ngược mục tiêu của rubric “chunk thực sự chứa đơn vị”. Có thể giữ một chỉ số hit theo mã phụ lục riêng, nhưng không diễn giải nó thành tìm đủ căn cứ trả lời.

**Yêu cầu sửa:** phân biệt địa chỉ nguồn với độ phủ bằng chứng. Dùng annotation bổ trợ cố định về mục/dòng/span cần thiết, hoặc quy tắc bảo thủ chỉ cấp điểm cho toàn đơn vị sau khi các mẩu truy xuất hợp lại phủ đủ đơn vị. Không cần sửa trực tiếp bộ eval đã đóng băng để bổ sung lớp ánh xạ bằng chứng có hash riêng. Kiểm tra cả recall và MRR theo định nghĩa được chốt.

**Kiểm tra chấp nhận:** `lp08` chỉ có mẩu 1 phải trượt; có phần cần thiết của mẩu 2 phải đạt. Với ba câu còn lại, nhầm mẩu phụ lục không được nhận đủ nhóm dù các căn cứ hỗ trợ đã đủ.

## 2. [P1] Điều kiện hiệu lực biến mất khỏi chữ của các mẩu sau khi tách

Vị trí: `_line`, `src/rag/chunking.py:192`, và nhánh tách theo dòng `src/rag/chunking.py:233–242`.

`_line` nối ghi chú hiệu lực vào cuối toàn đơn vị. Khi đơn vị được tách theo dòng, chỉ mẩu chứa dòng cuối giữ ghi chú trong `text`. Các mẩu khác vẫn có `ghi_chu_hieu_luc` trong metadata, nhưng chữ đem đi mã hóa/tìm kiếm không còn điều kiện đó. Test ghi chú hiện tại chỉ kiểm đơn vị ngắn không bị tách.

Kiểm trên mỗi kho:

- 123 mẩu có metadata điều kiện nhưng thiếu ít nhất một ghi chú tương ứng trong `text`.
- **111 mẩu được bộ lọc ngày giữ lại tại 01/10/2026**, thuộc tám nhóm phụ lục của TT108 và TT12.
- Hai cách cắt cùng mắc lỗi này; đây là 111 mẩu ở mỗi kho, không phải 222 nội dung độc lập.

Ví dụ theo chính dữ liệu nguồn của dự án:

`khoan:tt_12_2025_bca:pl4@2026-07-01#1` còn metadata:

> Chỉ mục A, mục C và mẫu số 01, 02, 03 mục D của phụ lục này còn hiệu lực

nhưng phần `text` không có dòng đó. Tương tự, mẩu đầu TT108 Phụ lục I chứa nội dung định danh điện tử nhưng thiếu ghi chú về các mốc áp dụng 2027/2028 đang được lưu trong metadata.

**Hệ quả:** bộ lọc khoảng ngày vẫn làm đúng theo nguồn, nhưng bên tiêu thụ chỉ dùng `text` không được báo phạm vi/điều kiện đi kèm. Chưa có luồng sinh câu trả lời để khẳng định đã trả lời sai; lỗi mất thông tin trong đầu ra chunk đã xảy ra. Một formatter sau này có thể bù bằng metadata, nhưng không sửa được nội dung đang được dùng để mã hóa và cũng chưa có hợp đồng/test bắt buộc bù này.

**Yêu cầu sửa:** dựng mỗi mẩu với ghi chú hiệu lực cần thiết của các đơn vị có mặt, tính cả phần ghi chú khi chia ngân sách token. Nên đặt điều kiện ở vị trí được giữ khi có bước cắt ngắn đầu vào. Bổ sung test một phụ lục dài có điều kiện, cùng kiểm kê toàn kho rằng mọi ghi chú của mẩu xuất hiện trong phần chữ đưa cho các bước tiếp theo.

## 3. [P2] Tách bảng theo dòng làm mất tên cột và ngữ cảnh bảng

Vị trí: `src/rag/chunking.py:233–242`.

Nhánh này giữ tiêu đề văn bản/Điều, nhưng không giữ tiêu đề bảng và tên cột ở các mẩu tiếp theo. Ví dụ QCVN41 khoản 46.3:

- Mẩu `#1` có `Bảng 5` và dòng `TT | Mô tả biển chỉ dẫn | Kiểu chữ | Màu chữ, số | Màu nền | Màu viền`.
- Các mẩu `#2`, `#3`, `#4` chỉ có các hàng dữ liệu; cả ba thiếu dòng tên cột.
- Mẩu `#2` chứa hàng `4 | Biển số IE.451 ... | gt2 | trắng | xanh lam | trắng`. Khi được truy xuất riêng, thứ tự ý nghĩa của các giá trị màu không còn được khai báo trong đoạn.

Đây là dữ liệu kỹ thuật dạng bảng cần giữ quan hệ hàng–cột. Cờ `mot_phan` chỉ báo thiếu một phần đơn vị, không khôi phục ý nghĩa các cột.

**Yêu cầu sửa:** nhận diện bảng, lặp tiêu đề bảng và tên cột ở mỗi mẩu của bảng; giữ câu dẫn/phạm vi áp dụng cần thiết. Tính phần lặp trong ngân sách token. Test lấy riêng một mẩu giữa bảng phải đọc được tên cột và gắn đúng giá trị.

## Những phần có thể giữ

- Giữ các phiên bản cũ để thực hiện phép thử bỏ lọc hiệu lực.
- Dùng `in_force_at` và các mốc ngoại lệ để tạo khoảng hiệu lực của nhóm.
- Ghép câu dẫn và các Điểm, sắp thứ tự chữ cái luật, ghi đúng những `version_id` thực sự được đưa vào phần chunk theo Điểm.
- Phân biệt nhóm căn cứ AND với phương án OR; các test `gp01`, `ll05` đã ngăn kiểu nâng một Điểm/câu dẫn thành đủ Khoản.
- Bootstrap theo họ sự kiện và tách kết quả theo nhóm câu.
- Build lặp lại ổn định và kiểm mã băm file chunk.

Không cần viết lại toàn bộ phần này. Các lỗi tập trung ở cách xử lý đơn vị bị chia nhỏ và việc chấm độ phủ bằng chứng.

## Bổ sung nên làm khi chốt manifest

`scripts/build_chunks.py:60–66` ghi blob của nguồn trong tag `data-v1`, nhưng chưa ghi hash của file nguồn thực tế vừa đọc. Tokenizer có đường nạp dự phòng từ cache, trong khi manifest chỉ hash đường trong config. `--check` hiện so hai file chunk, không kiểm manifest. Với trạng thái được review, hash hai chunk khớp và nguồn thực tế khớp blob đã ghi; đây là khoảng trống bảo đảm tái lập cho những lần chạy sau, chưa phải bằng chứng nguồn hiện tại bị sai.

Nên ghi SHA-256 file nguồn thực tế, đúng file tokenizer được nạp, các đầu vào dựng tiêu đề, và kiểm metadata/hash khi chạy `--check`.

## Bằng chứng và cách chạy lại

- Script độc lập: [verify.py](verify.py).
- Bằng chứng của lần review: [checks-053222213695Z.json](checks-053222213695Z.json), gồm hash các file đã kiểm, 8 phép thử nhầm mẩu, danh sách đoạn thiếu điều kiện, và ba mẩu bảng mất tên cột.
- Chạy từ repo: `py -3.13 -X utf8 docs/reviews/g3-chunking-score-review-2026-10-17/verify.py`.
- Mỗi lần chạy tạo file bằng chứng mới với chế độ tạo độc quyền; không ghi đè lần cũ.

Review chỉ thêm thư mục báo cáo này. Không sửa code triển khai, bộ eval, nguồn luật, file chunk hay manifest; không commit và không cài thư viện.

**Điều kiện chốt Task 1–2:** sửa ba điểm trên, dựng lại chunk/manifest, bổ sung phép thử sai tương ứng và chạy lại kiểm tra. Có thể tiếp tục xây BM25/vector độc lập, nhưng chưa dùng scorer hiện tại để chốt tham số hoặc báo cáo điểm retrieval.
