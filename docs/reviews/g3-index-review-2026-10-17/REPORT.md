# Review G3: BM25 và chỉ mục vector — 17/10/2026

**Kết luận: BM25 đã có và các số liệu dev tái hiện đúng. Phần vector đã có mã nhưng chưa hoàn tất tạo chỉ mục; có hai lỗi P1 và một lỗi P2 cần sửa trước khi chốt Task 4.** Chưa có hybrid, reranker hoặc luồng trả lời hoàn chỉnh.

Phạm vi: mã mới `src/rag/bm25.py`, `src/rag/dense.py`, `scripts/build_index.py`, các test, thư viện đã cài, hai chỉ mục BM25 và cache embedding đang được tạo. Không sửa triển khai, không cài thư viện, không chạy lại build toàn kho, không dừng tiến trình của Claude.

## Claude vừa làm được gì

- Phần chunking/scorer trước đó đã được merge qua PR #9, HEAD được quan sát là `bd83078`.
- Có mã BM25 dùng pyvi, chỉ mục đã lưu cho cả cách cắt theo Khoản và theo Điều.
- Có mã nạp bge-m3 trên CPU, cache embedding, dựng/tìm/lưu/nạp FAISS `IndexFlatIP`, lọc bằng mask, kiểm hash file chunk khi nạp.
- Có script build BM25 và vector, cùng các test mới.
- Đã cài đúng các gói ghi trong kế hoạch: `torch 2.14.1+cpu`, `sentence-transformers 6.1.0`, `transformers 5.20.1`, `faiss-cpu 1.15.1`, `rank-bm25 0.2.2`.
- Tiến trình `scripts/build_index.py --chi dense` PID 58460 đang chạy trong lúc review. Ở lần chụp cuối trong file bằng chứng, cache có 2.304 vector 1.024 chiều; đây là ảnh chụp tiến độ, không phải tổng cuối cùng.
- Tại thời điểm kiểm tra chưa có `dense.faiss` cho kho thật. Các file `retrieve.py`, `context.py`, `run_retrieval.py` chưa có.

## 1. [P1] FAISS không lưu/nạp được đường dẫn tiếng Việt hiện tại

Vị trí: `src/rag/dense.py:115` và `src/rag/dense.py:126`.

Mã truyền trực tiếp đường dẫn Python cho `faiss.write_index` và `faiss.read_index`. Với FAISS đang cài trên máy Windows này, hai lời gọi đều thất bại khi đường dẫn chứa ký tự tiếng Việt. Workspace thực tế nằm dưới `D:\Dowload\1.Chuyên Ngành\kì 7\...`, nên lỗi tác động trực tiếp tới đường dẫn output của `build_index.py`.

**Tái hiện độc lập:**

1. Tạo một FAISS index nhỏ bằng vector giả.
2. Lưu/nạp trong thư mục tạm có đường dẫn ASCII: thành công.
3. Lưu trong thư mục tạm nằm bên trong workspace: `RuntimeError`, thông báo không mở được `dense.faiss` để ghi dù thư mục đã tồn tại.
4. Dùng Python chép index hợp lệ từ đường dẫn ASCII vào thư mục đó, rồi nạp: cũng `RuntimeError` khi mở để đọc.

**Hệ quả:** tiến trình mã hóa toàn kho có thể chạy xong nhưng thất bại ở bước lưu chỉ mục. Cache embedding có thể còn, nhưng chưa có file FAISS hoàn chỉnh để tìm kiếm. Các test hiện tại dùng đường dẫn tạm không có dấu nên không bắt lỗi này.

**Hướng sửa:** dùng giao diện tuần tự hóa FAISS thành byte/array và Python `Path.read_bytes`/`write_bytes`, hoặc một cơ chế IO hỗ trợ Unicode đã được kiểm chứng trên máy này. Không cần di chuyển hay đổi tên workspace của người dùng. Thêm test save/load thực tế dưới thư mục có dấu và xác nhận truy vấn sau nạp giữ nguyên.

## 2. [P1] Ngắt giữa hai lần lưu cache có thể gán sai vector khi chạy tiếp

Vị trí: `src/rag/dense.py:46–59`, `src/rag/dense.py:65–76`.

Cache gồm hai file: `vectors.npy` và `keys.json`. `_save_cache` thay file vector trước rồi mới thay file khóa. Từng lần thay file là riêng lẻ; cả cặp file chưa tạo thành một lần cập nhật nhất quán. `_load_cache` không kiểm số khóa bằng số hàng vector.

**Phép thử dùng chính `_save_cache` của triển khai:**

1. Cache hợp lệ ban đầu có chữ `a` và vector `[1, 0]`.
2. Thêm `b`, chủ động gây lỗi IO ngay trước lúc thay `keys.json`, sau khi `vectors.npy` mới đã được thay.
3. Trạng thái trên đĩa: **1 khóa nhưng 2 hàng vector**.
4. Khôi phục IO bình thường và gọi `embed` cho `a, b, c`.
5. Hàm không báo lỗi, trả vector của `c` thành `[0, 1]` của `b`, trong khi vector đúng của `c` là `[-1, 0]`.

Nguyên nhân là `pos` dùng độ dài danh sách khóa để đánh số hàng mới, trong khi ma trận đã có một đuôi vector chưa đi kèm khóa. Việc mã hóa tiếp nối thêm vào ma trận mà không loại bỏ/khôi phục trạng thái lệch này.

**Hệ quả:** tính năng “chạy dở thì tiếp tục” có thể tạo index ánh xạ sai chữ–vector và vẫn vượt qua kiểm tra hash của file chunk. Test dừng giữa chừng hiện có gây lỗi ở encoder sau checkpoint hoàn chỉnh, chưa mô phỏng ngắt trong chính bước lưu checkpoint.

**Hướng sửa:** lưu khóa và vector trong một checkpoint nguyên khối, hoặc dùng các thế hệ checkpoint hoàn chỉnh với một con trỏ được thay nguyên tử. Khi nạp phải kiểm chiều, số khóa/số hàng, tính duy nhất và phục hồi hoặc từ chối cache bất nhất. Kiểm tra chấp nhận: gây lỗi tại mỗi ranh giới lưu rồi chạy tiếp phải trả vector đúng cho mọi chữ, hoặc báo lỗi rõ ràng; không được âm thầm lệch hàng.

Ở ảnh chụp cache thật trong lần review, số khóa và số hàng đang khớp. Không kết luận cache đang chạy đã bị hỏng; lỗi trên được kiểm chứng trong thư mục tạm.

## 3. [P2] Cache chưa gắn với mô hình và cấu hình mã hóa

Vị trí: `src/rag/dense.py:42–50`, `src/rag/dense.py:62–68`; `scripts/build_index.py:61–64`.

Khóa cache chỉ là SHA-256 của chữ, và script dùng chung một thư mục `emb_cache`. Không có định danh mô hình, snapshot, chiều vector hoặc `max_seq_length` trong khóa/metadata của cache. Thông tin mô hình được ghi vào meta của index ở cuối, nhưng không được dùng để xác nhận nguồn gốc các vector đã tái sử dụng.

**Tái hiện:** mã hóa `a` bằng encoder thứ nhất ra `[1, 0]`. Chạy lại cùng thư mục cache cho `a, b` bằng encoder thứ hai, vốn phải cho cả hai ra `[0, 1]`. Encoder mới chỉ được gọi cho `b`; kết quả trộn `[1, 0]` cũ và `[0, 1]` mới, không cảnh báo.

**Hệ quả:** đổi model, snapshot hoặc cấu hình cắt ngắn có thể tái sử dụng vector cũ rồi ghi nhãn toàn index như được tạo bằng cấu hình mới. Đây là nguy cơ ở những lần rebuild sau; chưa có bằng chứng Claude đã đổi encoder trong lần build đang chạy.

**Hướng sửa:** phân vùng cache theo danh tính encoder cố định (model, revision thực tải, cấu hình mã hóa, chiều/chuẩn hóa); xác nhận metadata trước khi tái sử dụng. Revision nên là revision encoder thực sự nạp, không chỉ đọc `refs/main` độc lập sau khi mã hóa.

## Các kiểm chứng đã qua

- **Toàn bộ test: 375 passed, 1 skipped trong 43,83 giây.** Test bị bỏ là phép thử tìm kiếm bằng mô hình bge-m3 thật; mặc định yêu cầu `RAG_SLOW=1` và còn cần index thật đã build xong. Vì vậy, số test qua chưa chứng minh luồng vector toàn kho đã chạy thành công.
- Thứ tự `ids` của hai BM25 index khớp từng chunk; hash đầu vào khớp; lưu/nạp lại giữ kết quả.
- FAISS tìm chính xác trên bộ vector giả so với phép nhân NumPy, cả có và không có mask. Save/load trên đường dẫn ASCII giữ nguyên kết quả. Lỗi nằm ở IO Unicode và cache, không phải phép tìm lân cận cơ bản trong phép thử này.
- Cache thật được chụp có 2.304 khóa khác nhau và ma trận `(2304, 1024)` `float32`, giá trị hữu hạn, norm xấp xỉ 1. Không kiểm chứng ngữ nghĩa của từng embedding bằng việc này.
- `eval_v1.jsonl` giữ hash `5a1b72038ae79755f5df7c53ed46447ac1516bb04e8e1330fd81cfc43fc0e252`.

## BM25 dev được tái hiện

Chỉ chạy 30 câu **dev**, không chạy bộ test để chỉnh tham số. Có lọc hiệu lực, lấy top-5. Bốn câu ngoài phạm vi không được tính recall theo thiết kế scorer. Không thay tham số.

| Nhóm | Cách cắt | n | Đúng văn bản | Any | All | MRR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Thường | Khoản | 16 | 1,0000 | 0,6875 | 0,4375 | 0,60625 |
| Sửa đổi | Khoản | 4 | 1,0000 | 0,7500 | 0,7500 | 0,58333 |
| Biến thể | Khoản | 6 | 0,6667 | 0,3333 | 0,1667 | 0,20833 |
| Thường | Điều | 16 | 1,0000 | 0,8750 | 0,6875 | 0,62500 |
| Sửa đổi | Điều | 4 | 1,0000 | 1,0000 | 1,0000 | 0,67500 |
| Biến thể | Điều | 6 | 0,6667 | 0,6667 | 0,5000 | 0,34722 |

Khớp các hàng được ghi trong kế hoạch G3. Đây là kết quả thăm dò dev với mẫu nhỏ, chưa phải kết quả đánh giá cuối và chưa có kết quả hybrid/vector/reranker.

## Bằng chứng và điều kiện chốt

- [verify.py](verify.py): chỉ đọc dữ liệu sản phẩm; mọi phép gây lỗi dùng bản giả/thư mục tạm.
- [checks-075553555098Z.json](checks-075553555098Z.json): hash mã được kiểm, kết quả BM25 dev, lỗi đọc/ghi Unicode, hai lỗi cache và ảnh chụp tiến độ cache thật.
- Mỗi lần chạy ghi file bằng chứng mới bằng chế độ tạo độc quyền, không ghi đè lần cũ.

**Trước khi chốt Task 4:** sửa ba điểm trên; test đường dẫn có dấu và lỗi checkpoint; cho build chạy xong thành file FAISS thật rồi nạp lại; chạy phép thử với bge-m3 thật. Có thể tái sử dụng những embedding cũ nếu đã xác minh nguồn gốc và tính nhất quán. Sau đó mới nối hybrid và reranker ở Task 5.
