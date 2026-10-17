# Kiểm tra tiếp Task 5: bộ nạp và hybrid — 18/10/2026

**Kết luận:** hai lỗi P2 ở bộ nạp đã được sửa và kiểm chứng độc lập. Luồng BM25 + dense + RRF + lọc hiệu lực + reranker đã chạy được; toàn bộ kết quả dev của tám cấu hình tái hiện đúng. Tuy nhiên, điều kiện chất lượng của ca “nón bảo hiểm” ban đầu **vẫn chưa đạt**: căn cứ đúng ở hạng 6 sau rerank, ngoài top-5. Việc chuyển ca này sang `xfail` và thêm một câu dùng thuật ngữ chuẩn không làm ca cũ được giải quyết.

Không phát hiện lỗi triển khai mới chặn luồng cơ bản trong phạm vi review. Có thể coi đây là baseline hybrid hoạt động với hạn chế công khai; không được báo cáo rằng mọi điều kiện chốt Task 5 của review trước đều đã qua.

Chỉ thêm thư mục báo cáo này. Không sửa triển khai, không ghi file dev/caches sản phẩm, không commit/push/merge, không chạy tập test cuối để tinh chỉnh.

## Kết quả kiểm tra

| Kiểm tra | Kết quả |
| --- | --- |
| Toàn bộ test mặc định | **390 passed, 4 skipped**, 45,77 giây |
| Test retrieval với `RAG_SLOW=1` | **11 passed, 1 xfailed**, 43,93 giây |
| Script kiểm chứng độc lập, có mô hình thật | **37/37 điều kiện kiểm qua**, bao gồm kiểm chứng trung thực ca trượt đã biết |
| Tái hiện dev | Khớp từng câu và toàn bộ tổng hợp của **8 cấu hình** |
| Hash file dev và cache reranker sản phẩm trước/sau review | Giữ nguyên |

Mô hình embedding và reranker đều được nạp từ snapshot local. Để tránh ghi vào cache sản phẩm, review chép cache reranker sang thư mục riêng rồi thực hiện truy vấn. Hai cặp query–Điểm h còn được chấm lại trực tiếp bằng reranker thật để đối chiếu điểm cache.

## Hai lỗi P2 đã sửa đạt

### Hash của file chunk thực tế

`retrieve.load_chunks` đọc byte, tính SHA-256 trên chính dữ liệu đó và so manifest trước khi parse/nạp index. `build_index.py` tái sử dụng cùng hàm.

Phép thử độc lập thay riêng text, rồi thay riêng `valid_from`, trong các bản sao vẫn giữ ID và thứ tự. Cả hai đều bị từ chối ngay vì không khớp manifest. File thực tế của cả hai cách cắt nạp bình thường.

### Danh tính encoder truy vấn so với dense index

`DenseIndex.load` nay giữ metadata trong `d.meta`; `retrieve.load` đối chiếu `enc.identity` với `bo_ma_hoa` đã ghi khi build.

Tôi thử thay riêng revision, `max_seq_length`, normalize trên cả hai index: cả sáu trường hợp đều bị từ chối. Encoder có identity đúng được chấp nhận. Các phép thử này không cần sửa mô hình hay dữ liệu sản phẩm.

## Kết quả dev xác nhận bằng mô hình thật

Đã chạy đúng 30 câu dev, bốn cấu hình trên hai cách cắt. 26 câu có căn cứ được chấm recall (16 thường, 4 sửa đổi, 6 biến thể); bốn câu ngoài phạm vi không được tính các chỉ số này theo thiết kế scorer. Dùng tham số hiện tại, không chỉnh.

Từng object kết quả của mỗi cấu hình khớp file Claude lưu: các chunk top-5 theo từng câu, any/all, nhóm thiếu, MRR, tổng hợp, CI bootstrap, variant gap, số đoạn hết hiệu lực lọt vào, và số câu lấy bản cũ khi bỏ lọc.

| Cấu hình | Cách cắt | Thường: any / all / MRR | Sửa đổi: any / all / MRR | Biến thể: any / all / MRR |
| --- | --- | --- | --- | --- |
| BM25 | Khoản | 0,6875 / 0,4375 / 0,6063 | 0,75 / 0,75 / 0,5833 | 0,3333 / 0,1667 / 0,2083 |
| Vector | Khoản | 0,8125 / 0,5625 / 0,6615 | 1 / 1 / 0,7083 | 0,6667 / 0,3333 / 0,6667 |
| Hybrid | Khoản | 0,9375 / 0,625 / 0,6948 | 1 / 1 / 0,7083 | 0,6667 / 0,3333 / 0,5 |
| Hybrid + rerank | Khoản | 0,9375 / 0,625 / 0,8333 | 1 / 1 / 0,875 | 0,8333 / 0,5 / 0,6667 |
| BM25 | Điều | 0,875 / 0,6875 / 0,625 | 1 / 1 / 0,675 | 0,6667 / 0,5 / 0,3472 |
| Vector | Điều | 0,875 / 0,8125 / 0,8125 | 0,75 / 0,75 / 0,75 | 0,6667 / 0,5 / 0,5 |
| Hybrid | Điều | 1 / 0,8125 / 0,8125 | 0,75 / 0,75 / 0,75 | 0,6667 / 0,5 / 0,5833 |
| Hybrid + rerank | Điều | 1 / 0,8125 / 0,8688 | 1 / 1 / 0,875 | 0,6667 / 0,5 / 0,4722 |

Có cải thiện ở nhiều chỉ số, nhưng không phải mọi trường hợp: reranker làm MRR nhóm biến thể theo Điều giảm từ khoảng 0,5833 xuống 0,4722. Không kết luận reranker luôn giúp hoặc mô hình trả lời đã đạt các tỷ lệ này. Đây chỉ là tìm kiếm trên dev nhỏ, chưa phải kết quả test cuối.

Tám cấu hình đều không có chunk bị mask ngày loại bỏ lọt vào top-5. Điều này kiểm logic hiệu lực của kho; không thay thế xét điều kiện pháp lý theo người/xe/mục của phụ lục.

## Ca “nón bảo hiểm” vẫn trượt — kiểm chứng trực tiếp

Căn cứ cần tìm: `nd_168_2024:d7:k2:h@2025-01-01`, trong mẩu `#1` của Khoản 2 Điều 7 NĐ168.

| Câu hỏi | Dense-only | Sau RRF | Sau reranker |
| --- | ---: | ---: | ---: |
| “đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu” | 20 | **5** | **6** |
| “không đội mũ bảo hiểm khi điều khiển xe mô tô bị phạt bao nhiêu” | 26 | 7 | **3** |

Tôi tìm tới top-50 trước rerank và tới hết pool 20 sau rerank để xác định hạng, không chỉ đọc assertion. Các hạng khớp diễn giải của Claude, trừ việc câu chuẩn là test bổ sung sau đó, không thay thế được câu gốc.

Hai cặp query–chunk cần thiết được chấm mới bằng `CrossReranker`, đối chiếu với điểm đã cache và khớp trong sai số kiểm tra. Vì vậy, ca cũ tụt từ hạng 5 xuống 6 không phải do điểm cache sai hay lỗi loader vừa sửa; đó là hạn chế xếp hạng hiện tại được tái hiện với mô hình thật.

`tests/test_rag_retrieve.py` hiện tách:

- Câu thuật ngữ chuẩn: test bắt buộc qua — thực tế qua.
- Câu đời thường ban đầu: `xfail(strict=True)` — thực tế xfail.

Đánh dấu `xfail` công khai tốt hơn việc loại mất ca lỗi, nhưng không đồng nghĩa đã đạt điều kiện “câu nón bảo hiểm có Điểm h trong top-5”. Kế hoạch hiện cũng đã ghi rõ điều kiện này chưa đạt hoàn toàn và dời xử lý về G8. Đó là quyết định phạm vi/cải tiến cần trình bày minh bạch, không phải bằng chứng kỹ thuật rằng ca đã được sửa.

## Việc tiếp theo

- Giữ ca lỗi và bộ câu hỏi cố định để so sánh; không đổi câu hỏi hoặc tăng top-k chỉ để chuyển trạng thái đạt.
- Dùng kết quả dev và phân tích lỗi để quyết định cải tiến chung (ví dụ ánh xạ từ đời thường đã có trong EDA hoặc thay đổi cách cắt đoạn); đo lại trên toàn nhóm dev liên quan thay vì chỉ một câu.
- Nếu giữ cấu hình hiện tại làm baseline trước khi cải tiến, ghi rõ hạn chế trên. Task 6 vẫn cần chốt tham số trên dev, chạy các cấu hình ablation cuối và xuất context; chưa được báo G3 hay chatbot hoàn tất.

Review này không tự triển khai cải tiến hoặc thay đổi tiêu chí đã chốt. Hai lỗi bộ nạp đã được xác nhận sửa đạt, không cần sửa lại.

## Bằng chứng

- [verify.py](verify.py): test hai guard, nạp hai mô hình thật, chạy tám cấu hình dev, đo hạng của hai câu và chấm mới hai điểm reranker.
- [checks-182406627491Z.json](checks-182406627491Z.json): 37 điều kiện kiểm, metadata, hash mã, các hạng và điểm chấm mới.
- [dev-reproduced-182406627491Z.json](dev-reproduced-182406627491Z.json): kết quả dev được review tái hiện.
- `rerank-cache-182406627491Z/`: cache riêng của review, sản phẩm gốc không bị ghi thêm.

Tên file bằng chứng có timestamp và được tạo độc quyền, không ghi đè các vòng review trước.
