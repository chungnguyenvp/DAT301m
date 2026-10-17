# Kiểm chứng hoàn tất Task 3–4: BM25 và vector — 17/10/2026

**Kết luận: có thể chốt phần kỹ thuật Task 3–4 và chuyển sang hybrid/reranker ở Task 5.** Cả hai chỉ mục thật đã có, nạp và tìm kiếm được; kết quả dev tái hiện hoàn toàn. Không phát hiện lỗi mới chặn phần xây chỉ mục trong phạm vi kiểm tra này. Hạn chế dense-only tìm thiếu Điểm h vẫn tồn tại và đã được công khai, không được tính là đã khắc phục.

Đây chưa phải kết luận hoàn tất G3, hệ thống hỏi đáp, hay đánh giá cuối trên tập test. Không sửa triển khai, không commit/push/merge và không thay file báo cáo dev của Claude.

## Những việc đã kiểm chứng độc lập

| Kiểm tra | Kết quả |
| --- | --- |
| Toàn bộ test mặc định | **380 passed, 2 skipped** trong 25,86 giây |
| Test vector với `RAG_SLOW=1` | **10 passed, 1 xfailed** trong 19,11 giây |
| Script kiểm toán độc lập, có nạp bge-m3 thật | **27/27 điều kiện kiểm tra qua** |
| Chỉ mục theo Khoản | **6.221 vector × 1.024 chiều** |
| Chỉ mục theo Điều | **2.149 vector × 1.024 chiều** |
| Thứ tự ID của cả hai chỉ mục | Khớp từng dòng chunk |
| Toàn bộ vector trong hai FAISS index | Khớp từng phần tử với cache tra theo SHA-256 chữ của chunk |
| Vector hữu hạn và chuẩn hóa | Đạt ở cả hai index |
| Tự tìm vector của chính chunk | Qua 125 mẫu theo Khoản, 43 mẫu theo Điều; chấp nhận trường hợp hòa do vector trùng |
| Danh tính encoder | Cả hai index và mô hình thực nạp cùng revision `5617a9f61b028005a4858fdac845db406aefb181`, max length 8.192, chuẩn hóa, float32, 1.024 chiều |

Ba lỗi kỹ thuật cũ đã được kiểm tra sửa đạt ở review trước: IO Unicode, checkpoint nguyên khối và cache gắn danh tính encoder. Mã `dense.py` không đổi so với trạng thái đó; lần này đã bổ sung kiểm cả index theo Điều và nạp mô hình thật.

## Kết quả dev được chạy lại

Tôi chạy lại logic của `scripts/probe_dev.py`, chỉ dùng 30 câu dev. Output được chuyển vào một file mới trong thư mục review để không ghi đè `reports/retrieval/dev_probe.json`. Cả object JSON khớp **hoàn toàn** bản Claude lưu: điểm từng câu, danh sách chunk, tổng hợp, bootstrap CI, variant gap, bộ lọc và thống kê bỏ lọc.

Bốn câu ngoài phạm vi được mã hóa/truy vấn nhưng không tính vào chỉ số recall theo scorer. Các nhóm được chấm có mẫu số 16 thường, 4 sửa đổi và 6 biến thể. Không chạy 240 câu test để tinh chỉnh.

| Nhóm | Cách cắt | n | BM25 any / all | Vector any / all |
| --- | --- | ---: | --- | --- |
| Thường | Khoản | 16 | 0,6875 / 0,4375 | 0,8125 / 0,5625 |
| Thường | Điều | 16 | 0,8750 / 0,6875 | 0,8750 / 0,8125 |
| Sửa đổi | Khoản | 4 | 0,7500 / 0,7500 | 1,0000 / 1,0000 |
| Sửa đổi | Điều | 4 | 1,0000 / 1,0000 | 0,7500 / 0,7500 |
| Biến thể | Khoản | 6 | 0,3333 / 0,1667 | 0,6667 / 0,3333 |
| Biến thể | Điều | 6 | 0,6667 / 0,5000 | 0,6667 / 0,5000 |

`any` là tìm được ít nhất một nhóm căn cứ; `all` là tìm đủ mọi nhóm bắt buộc. Đây không phải tỷ lệ chatbot trả lời đúng, vì chưa có mô hình sinh câu trả lời trong phép đo.

- Có lọc: **0 đoạn bị lọc ngày loại bỏ lọt vào kết quả**, ở cả bốn cấu hình. Điều này kiểm logic thời gian của kho, không thay thế xét đối tượng/điều kiện pháp lý đi kèm.
- Bỏ lọc: số câu sửa đổi lấy bản cũ trong top-5 là BM25 Khoản **3/4**, BM25 Điều **4/4**, vector Khoản **4/4**, vector Điều **3/4**.
- Không nên suy rộng “vector luôn tốt hơn BM25”: chính nhóm sửa đổi theo Điều có vector 3/4, BM25 4/4. Các mẫu dev nhỏ và chỉ là thăm dò.

Ngoài truy vấn dev, tôi mã hóa lại ba chunk ngắn/vừa bằng encoder thật và so với cache; cosine đều trên 0,99999. Đây là mẫu kiểm độc lập mới, không phải tuyên bố đã tự chạy lại toàn bộ 16 mẫu dài mà Claude kiểm trước khi chuyển cache.

## Ca Điểm h và việc sửa test

Test đã tách đúng mục đích:

- Smoke test chỉ xác nhận index thật nạp được, lọc được và kết quả đầu thuộc Khoản mong đợi; docstring nói rõ không chứng minh đủ Điểm h.
- Ca yêu cầu Điểm h trong top-10 được giữ riêng, đánh dấu `xfail(strict=True)` và ghi rõ đang trượt. Lần chạy với mô hình thật xác nhận đúng trạng thái `xfail`.

Script kiểm độc lập còn tìm top-50 cho đúng câu “đi xe máy mà không đội nón bảo hiểm thì bị phạt bao nhiêu”, ghi hạng thực tế của chunk chứa Điểm h vào file bằng chứng. Việc khớp cùng Khoản không được nâng thành đủ căn cứ.

**Một chỗ cần hiểu đúng cho Task 5:** test hiện tại có tên `test_real_dense_only_finds_point_h_in_top10` và vẫn gọi trực tiếp dense-only. Chỉ nối hybrid/reranker sẽ không làm test dense-only tự đổi kết quả. Cần thêm ca kiểm trên luồng hybrid thực tế. Có thể giữ baseline dense-only trượt như một kết quả thực nghiệm; chỉ bỏ `xfail` của dense-only nếu chính cấu hình dense-only được cải thiện. Không cần đổi cơ chế lưu chỉ mục để giải quyết chỗ này.

## Trạng thái và bước tiếp theo

Task 3–4 đã có cơ sở để chốt kỹ thuật: BM25 và vector hoạt động riêng trên cả hai cách cắt, dữ liệu và kết quả dev đều có thể tái hiện. Chỉ mục/cache là sản phẩm local không commit theo kế hoạch; có script build lại.

Bước tiếp theo là triển khai Task 5: kết hợp kết quả bằng RRF, áp dụng lọc hiệu lực nhất quán, rerank và tạo context. Cần kiểm đúng Điểm h trên chính luồng đó; sau đó chỉnh tham số trên dev và thực hiện đánh giá test cuối ở Task 6. Chưa có bằng chứng hybrid đã được triển khai trong trạng thái đang review.

## File bằng chứng

- [verify.py](verify.py): nạp encoder thật, kiểm hai index/cache và chạy lại dev, không sửa dữ liệu sản phẩm.
- [checks-091726722103Z.json](checks-091726722103Z.json): 27 kết quả kiểm, metadata, hash file, hạng thực tế Điểm h, kết quả mã hóa lại ba mẫu.
- [dev-reproduced-091726722103Z.json](dev-reproduced-091726722103Z.json): kết quả dev do review chạy lại, khớp toàn bộ báo cáo Claude.

Mỗi lần chạy script tạo tên bằng chứng mới, không ghi đè review cũ. Hash của báo cáo dev gốc được kiểm trước/sau và giữ nguyên.
