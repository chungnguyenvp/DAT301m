# Review Task 5: hybrid, reranker và context — 17/10/2026

**Kết luận tại thời điểm review: đã có triển khai Task 5 và bảy test cơ bản qua, nhưng chưa có đủ kết quả để chốt Task 5 hoàn tất.** Phép thử dev đang chạy; báo cáo dev được lưu vẫn chỉ có bốn cấu hình BM25/vector của Task 3–4. Review tìm thêm hai thiếu sót P2 ở khâu nạp retriever cần bổ sung để giữ tính nhất quán dữ liệu/mô hình.

Không sửa triển khai, không commit/push/merge, không ghi cache sản phẩm, không dừng tiến trình của Claude. Các phép thử thay dữ liệu và encoder dùng thư mục tạm/mô hình giả.

## Những gì Claude đã làm đúng

- Git HEAD là `3c53520`, merge PR #10 cho Task 3–4; nhánh hiện tại `feat/rag-retrieve`.
- `retrieve.py` có BM25 và dense, gộp thứ hạng bằng RRF, cấu hình bật/tắt từng cách, rerank top-20 rồi chọn top-5.
- Mask hiệu lực được áp ngay trong hai lượt tìm trước gộp RRF và trước reranker. Cách này giữ ứng viên hợp lệ thay vì để các bản hết hiệu lực chiếm top-k rồi mới loại.
- Reranker nạp snapshot offline, ghi model/revision/max length vào identity. Điểm cache theo identity và cặp query–text; đổi chữ hoặc câu hỏi không dùng lại nhầm điểm cũ.
- Cache JSON ghi qua file tạm rồi thay file. Phép thử độc lập xác nhận khử trùng chữ giống nhau, dùng lại điểm sau khi nạp từ đĩa, đổi query/text tính lại, và đổi revision dùng cache riêng.
- `context.py` ghi nguồn, khoảng ngày hiệu lực và toàn bộ chữ chunk. Ngày kết thúc hiển thị được trừ một ngày đúng với cận trên loại trừ.
- Có test hybrid với mô hình thật, yêu cầu tìm được **Điểm h trong top-5**, không `xfail`. Ca dense-only vẫn được giữ riêng là hạn chế đã biết; lý do `xfail` đã được sửa để không còn nói nối hybrid sẽ làm test dense-only tự qua.

## 1. [P2] Bộ nạp không kiểm hash của file chunk thực tế

Vị trí: `src/rag/retrieve.py:157–163`.

`load()` lấy SHA từ manifest và đưa SHA đó cho hai index loader, nhưng không băm file chunk vừa đọc để so sánh. So thứ tự ID chỉ bắt đổi/xóa/chèn ID, không bắt thay nội dung, hiệu lực hoặc metadata mà giữ nguyên ID.

**Phép thử:** chép nguyên manifest và hai chỉ mục thật sang thư mục tạm. Sửa duy nhất chữ và `valid_from` của một chunk trong bản sao, giữ nguyên toàn bộ ID và thứ tự. Dùng encoder giả có identity đúng để tránh tải mô hình; hai index loader vẫn là code thật, không mock.

Kết quả: file có SHA khác SHA nguồn của chỉ mục, nhưng `retrieve.load` vẫn thành công và lấy nội dung/ngày đã sửa. Retriever sau đó có thể xếp hạng bằng vector/từ khóa cũ, trong khi context và mask sử dụng thông tin mới.

**Cách sửa:** tính SHA-256 trên chính bytes được đọc để parse chunk, so manifest và index trước khi trả retriever. Có thể tái sử dụng cơ chế kiểm của `scripts/build_index.py:load_chunks` sau khi tách thành hàm dùng chung. Test thay riêng text và ngày nhưng giữ ID phải báo lỗi; file hiện tại hợp lệ phải nạp bình thường.

**Phạm vi:** file sản phẩm hiện tại vẫn khớp hash nguồn index. Đây là thiếu kiểm tra ở luồng nạp khi file thay đổi, không phải kết luận dữ liệu thật đang bị sửa sai.

## 2. [P2] Không đối chiếu encoder câu hỏi với encoder tạo dense index

Vị trí: `src/rag/retrieve.py:161–165`.

`DenseIndex.load` kiểm hash chunk nhưng `retrieve.load` sau đó nạp encoder theo mặc định/cache hiện tại mà không đối chiếu `bo_ma_hoa` trong meta của dense index. Nếu cache model đổi revision hoặc cấu hình mã hóa, vector câu hỏi có thể không cùng không gian với vector tài liệu mà retriever vẫn được tạo thành công.

**Phép thử:** giữ index thật; thay riêng `dense.load_encoder` bằng encoder giả có cùng số chiều, cùng model label nhưng revision khác. `retrieve.load(..., reranker=False)` vẫn trả retriever. Không có cảnh báo/báo lỗi.

**Cách sửa:** nạp/pin encoder theo identity được ghi trong meta, hoặc so identity thực tải với meta và từ chối khi khác. Kiểm model, revision, max sequence length, chuẩn hóa, số chiều và kiểu số theo hợp đồng đã chốt. Cache embedding được phân vùng đúng chưa tự bảo vệ được luồng truy vấn này, vì câu hỏi không đi qua cache embedding của tài liệu.

**Phạm vi:** snapshot đang dùng trong các lần build/review trước vẫn là `5617a9f61b028005a4858fdac845db406aefb181`. Phép thử chứng minh thiếu guard khi encoder thay đổi, không nói mô hình thực hiện tại đã khác.

## Trạng thái kiểm tra và những gì chưa thể kết luận

- `pytest -q tests/test_rag_retrieve.py`: **7 passed, 1 skipped**. Test bỏ qua là phép thử hybrid với bge-m3 và reranker thật.
- `pytest -q` toàn dự án: **387 passed, 3 skipped** trong 66,64 giây. Ba test bỏ qua cần mô hình thật; do đó số test mặc định qua chưa chứng minh chất lượng hybrid với mô hình thật.
- Script kiểm độc lập: **9/9 kiểm tra hành vi cơ bản qua**, cộng hai phép thử sai xác nhận các thiếu sót P2 trên.
- Tại lần chụp bằng chứng, tiến trình `scripts/probe_dev.py` PID 55280 vẫn chạy, reranker cache đã có điểm và tiếp tục cập nhật.
- `reports/retrieval/dev_probe.json` hiện vẫn chứa **bm25/khoan, vector/khoan, bm25/dieu, vector/dieu** của vòng trước. Chưa có bảng hybrid/hybrid+rerank mới hoàn chỉnh để đối chiếu.
- Không nạp thêm hai mô hình để tranh RAM/CPU với tiến trình đang chạy (RAM vật lý trống từng được đọc dưới 1 GiB). Review này chưa độc lập xác nhận test hybrid thật đã qua hoặc con số 0,46 giây/cặp.

Việc những đoạn xe đạp máy, chở người không đội mũ và người điều khiển không đội mũ giống nhau về chữ hoặc khung tiền là lý do chúng có thể trở thành ứng viên gây nhầm. Điều đó không chứng minh reranker đã xếp đúng cho câu hỏi cụ thể. Cần dùng đúng căn cứ/đối tượng để chấm và kiểm ca Điểm h trong top-5. Cùng mức phạt không tự làm hai hành vi thành bằng chứng thay thế tương đương.

## Điều kiện chốt Task 5

1. Bổ sung hai guard ở loader, kèm test sai tương ứng.
2. Để phép thử dev hoàn tất; xác nhận file kết quả có đủ bốn cấu hình cho cả hai cách cắt, cùng metadata và chỉ số từng câu.
3. Chạy test hybrid thật và xác nhận Điểm h có trong top-5, không đổi sang tiêu chí chỉ cùng Khoản.
4. Chạy lại toàn bộ test. Chỉ chỉnh tham số trên dev; đánh giá test cuối vẫn để Task 6.

Không cần làm lại BM25/dense index hoặc viết lại RRF để sửa hai thiếu sót này.

## Bằng chứng

- [verify.py](verify.py): phép thử RRF, cache, mốc hiệu lực, context và hai trường hợp nạp sai.
- [checks-094633724954Z.json](checks-094633724954Z.json): chín điều kiện kiểm, kết quả nạp encoder khác, nạp file chunk sai hash, hash trạng thái mã và các cấu hình trong báo cáo dev lúc kiểm.

Mỗi lần chạy tạo bằng chứng mới, không ghi đè file cũ. Vì Claude còn đang chạy, tình trạng báo cáo/cache ở thời điểm sau có thể đã khác ảnh chụp này.
