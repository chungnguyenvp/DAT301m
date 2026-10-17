# Kiểm tra bản sửa BM25/vector — 17/10/2026

**Kết luận:** ba lỗi kỹ thuật của review trước đã được sửa đúng trong phạm vi kiểm chứng. Chỉ mục theo Khoản đã được lưu và nạp trên đường dẫn thật của dự án; toàn bộ 6.221 vector khớp cache theo đúng chữ của từng chunk. Tuy nhiên, Task 4 vẫn đang thực hiện: chưa có chỉ mục theo Điều ở thời điểm kiểm tra, và phép thử chất lượng tìm đúng Điểm h đã được thay bằng một tiêu chí yếu hơn.

Không sửa code triển khai, không ghi cache/chỉ mục sản phẩm, không cài thư viện, không dừng tiến trình nền. Chỉ thêm thư mục review này; các phép gây lỗi dùng thư mục tạm và vector giả.

## Kết quả chạy

- Toàn bộ test: **380 passed, 1 skipped**, 41,66 giây.
- Script kiểm tra độc lập: **19/19 điều kiện kiểm tra qua**, bao gồm xác nhận sự khác biệt giữa tiêu chí cùng Khoản và đủ Điểm cần tìm.
- Test chậm bge-m3 vẫn bị bỏ qua trong lần chạy mặc định này.
- Quan sát tiến trình `scripts/build_index.py --chi dense` PID 46280 đang chạy. Không chờ hoặc khởi chạy lại mã hóa toàn kho.

## Ba lỗi đã sửa

### 1. IO FAISS với đường dẫn có dấu — đạt

Triển khai đã chuyển sang `serialize_index`/`deserialize_index` và Python đọc/ghi byte. Tôi tạo một index nhỏ, lưu và nạp trong thư mục có dấu nằm ngay bên trong workspace; kết quả truy vấn giữ nguyên.

Ngoài phép thử nhỏ, đã nạp thành công file thật `data/rag/index/khoan/dense.faiss` từ chính đường dẫn tiếng Việt. Có 6.221 vector, mỗi vector 1.024 chiều; danh sách ID khớp thứ tự của file chunk. Như vậy đây không chỉ là sửa mã nhưng chưa chạy được trên máy.

### 2. Checkpoint cache khi bị ngắt — đạt

Khóa, vector và metadata nay nằm chung trong một `.npz`; ghi file tạm rồi thay bằng một `os.replace`.

Phép thử độc lập tạo cache của `a`, gây lỗi ngay trước lần thay checkpoint khi thêm `b`, rồi chạy tiếp `a, b, c`. File checkpoint cũ giữ nguyên từng byte; chỉ mã hóa lại `b, c`; kết quả của cả ba chữ đúng, không còn lệch hàng như lần review trước.

Tôi còn tạo năm loại cache sai để xác nhận bị từ chối: thừa hàng vector, trùng khóa, sai số chiều, có NaN và metadata encoder không khớp. Cả năm đều báo lỗi.

### 3. Phân biệt encoder/config trong cache — đạt

Đường dẫn cache phụ thuộc danh tính encoder, gồm model, revision thực tải, độ dài tối đa, chuẩn hóa, kiểu số và số chiều. Metadata bên trong cũng được kiểm khi nạp. `SentenceEncoder` xác định snapshot bằng đường dẫn thực tải offline, rồi nạp chính đường dẫn đó.

Thử đổi riêng revision hoặc độ dài tối đa: đều mã hóa lại đúng các chữ yêu cầu trong cache riêng. Không tái sử dụng vector khác danh tính.

Danh tính trong chỉ mục thật:

```text
model: BAAI/bge-m3
revision: 5617a9f61b028005a4858fdac845db406aefb181
max_seq_length: 8192
normalize: true
dtype: float32
dim: 1024
```

## Chỉ mục thật đã kiểm được gì

- Nguồn chunk khớp hash mà chỉ mục ghi nhận.
- Tất cả 6.221 ID đúng thứ tự trong `chunks_khoan.jsonl`.
- Tất cả đoạn chữ có khóa tương ứng trong cache của đúng encoder.
- **So cả 6.221 vector** được lấy từ FAISS với vector trong cache theo hash chữ: bằng nhau từng phần tử.
- Vector hữu hạn và norm xấp xỉ 1.
- Ba truy vấn dùng vector có sẵn trong index: điểm top-5 khớp phép nhân NumPy khi có mask hiệu lực; không trả đoạn bị mask loại bỏ. Đây là kiểm toán học và ánh xạ, không thay thế kiểm ý nghĩa của câu hỏi bằng mô hình thật.

Tôi không nạp thêm một bản bge-m3 trong lúc tiến trình nền đang mã hóa và máy chỉ còn khoảng 2,7 GiB RAM vật lý trống ở lần đọc. Vì vậy chưa độc lập tái hiện tuyên bố mã hóa lại 16 mẫu với cosine ≥ 0,9999998, cũng chưa chạy lại kết quả vector trên 30 câu dev. Việc index khớp cache không tự chứng minh mọi vector trong cache được tạo đúng về ngữ nghĩa; phạm vi kiểm chứng được phân biệt rõ ở đây.

## Điểm cần giữ lại: test Điểm h đã bị hạ tiêu chí

Vị trí: `tests/test_rag_dense.py`, hàm `test_real_index_finds_the_helmet_fine`.

Tiêu chí cũ yêu cầu trong top-10 có chunk chứa:

```text
nd_168_2024:d7:k2:h@2025-01-01
```

Tiêu chí mới chỉ yêu cầu kết quả đầu có:

```text
nhom == nd_168_2024:d7:k2
```

**Hai tiêu chí không tương đương.** Tôi lấy chính mẩu `khoan:nd_168_2024:d7:k2@2025-01-01#2`: nó cùng Khoản nhưng chứa Điểm i, k, không chứa Điểm h. Mẩu này vượt qua assertion mới; scorer yêu cầu Điểm h cho `any=false`, `all=false`, `rr=0` khi chỉ đưa mẩu này vào.

Claude đã công khai trong kế hoạch rằng Điểm h chỉ đứng khoảng hạng 20–23 với vector đơn thuần; review này chưa tự xác nhận thứ hạng đó bằng mô hình. Đây có thể là hạn chế chất lượng của dense-only để hybrid cải thiện, không nhất thiết là lỗi phép tính FAISS. Tuy nhiên, việc đổi test thực sự đã giảm điều kiện đạt, dù bản tường thuật nói “không nới tiêu chí”. Test mới chỉ là smoke test tìm đúng Khoản, không chứng minh đủ căn cứ trả lời hoặc đúng hành vi.

**Đề nghị:** đổi tên/tách smoke test cho đúng điều đang đo; giữ riêng ca tìm đúng Điểm h như phép đo dev hoặc ca hồi quy có trạng thái thất bại được công bố. Sau khi nối hybrid/reranker, dùng lại tiêu chí đủ căn cứ và đo trên cùng query/cutoff. Không dùng việc smoke test qua để kết luận lỗi truy hồi Điểm h đã được xử lý, cũng chưa thể bảo đảm hybrid chắc chắn sẽ khắc phục.

## Trạng thái và việc còn lại

| Phần | Trạng thái được kiểm chứng |
| --- | --- |
| Ba lỗi kỹ thuật review trước | Đã sửa, phép thử độc lập qua |
| BM25 | Có từ vòng trước |
| Vector theo Khoản | Có file thật, nạp và tìm được; khớp cache và chunk |
| Vector theo Điều | Chưa có `dense.faiss` lúc chụp; đang mã hóa nền theo thông tin tiến trình/kế hoạch |
| Chất lượng dense-only trên dev | Có số liệu Claude ghi trong kế hoạch, chưa tự chạy lại trong vòng này |
| Tìm đúng Điểm h trong top-10 | Chưa đạt theo tường thuật Claude; assertion hiện tại không kiểm điều này |
| Hybrid, reranker, thực nghiệm cuối | Chưa có cơ sở để coi là hoàn tất |

Tiếp theo: để build theo Điều hoàn tất, kiểm lưu/nạp thật; chạy test có mô hình và lưu kết quả dev có thể tái hiện; giữ rõ ca Điểm h còn trượt; rồi nối hybrid/reranker ở Task 5. Không cần viết lại ba phần đã sửa đạt.

## Bằng chứng

- [verify.py](verify.py): kiểm cấu trúc cache, ngắt checkpoint, encoder identity, đường dẫn Unicode và chỉ mục thật.
- [checks-084529227208Z.json](checks-084529227208Z.json): 19 kết quả kiểm, hash mã/chỉ mục, metadata encoder và phản ví dụ cùng Khoản nhưng thiếu Điểm h.

File bằng chứng được tạo mới theo timestamp, không ghi đè review trước. Mốc thời gian và sự tồn tại file chỉ phản ánh trạng thái được chụp, vì mã hóa nền còn tiếp diễn.
