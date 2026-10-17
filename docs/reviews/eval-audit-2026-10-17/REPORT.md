# Review độc lập bộ eval Claude — 17/10/2026

**Kết luận: bộ khung tốt, dùng được để chạy thử; chưa nên đóng băng làm benchmark chính thức cho Report 3.** Điểm cần xử lý trước là đáp án cũ của một số câu RQ3: phiên bản câu chữ cũ trong kho không đồng nghĩa với quy định thực tế còn áp dụng ở `ngay_cu`.

## Phạm vi và bằng chứng kiểm tra

- Đọc toàn bộ 270 câu, README, ma trận đề, script build, validator và test; đối chiếu căn cứ của các trường hợp rủi ro với kho phiên bản và nguồn nhà nước bên ngoài. Đây không phải chứng nhận pháp lý đầy đủ cho từng câu.
- `py -3.13 -X utf8 -m pytest -q tests/test_evalset.py`: **14 passed**.
- `py -3.13 -X utf8 -m pytest -q`: **289 passed**, 20,83 giây ở lượt kiểm tra có thu đủ kết quả.
- `py -3.13 -X utf8 scripts/build_eval.py --check`: hợp lệ. Lệnh không có `-X utf8` gặp lỗi in tiếng Việt trên môi trường pipe CP1252 này; lỗi console không phải lỗi dữ liệu.
- Build lại trong bộ nhớ khớp hoàn toàn file đã lưu. Đúng 150 thường + 40 sửa đổi + 30 ngoài phạm vi + 50 biến thể; dev 30, test 240; ma trận câu thường khớp.
- Cả 50 biến thể cùng split và căn cứ với câu gốc. Blob Git của `legal_units_versioned.jsonl` hiện tại khớp bản trong tag `data-v1`: `6897e2b44ff3c005fa043ac06ae3e18eef091092`.
- Script tái lập: [audit_eval.py](audit_eval.py); kết quả, SHA-256 đầu vào và bản chụp các bản ghi liên quan: [audit.json](audit.json). Sáu phép sửa sai chỉ thao tác trên bản sao trong bộ nhớ, không sửa bộ eval.

## 1. [P1] Một số cặp RQ3 sai thời điểm áp dụng pháp luật

### Thẩm quyền xử phạt đã đổi trước mốc sửa NĐ 168 trong kho

`SD002` (dòng 152 file eval) gán `ngay_cu = 2026-06-01`, `dap_an_cu` cho chiến sĩ Công an mức tối đa 500.000 đồng và coi mốc 15/8/2026 là thời điểm tăng lên 7.500.000 đồng. Tuy nhiên, **NĐ 189/2025/NĐ-CP có hiệu lực từ 01/7/2025** đã quy định thẩm quyền theo tỷ lệ mức phạt tối đa của lĩnh vực; khoản 2 Điều 21 điều chỉnh việc áp dụng thẩm quyền trong giai đoạn các nghị định chuyên ngành chưa được sửa. Chính Bộ Công an giải thích từ tháng 4/2026 rằng chiến sĩ có mức tương đương 7.500.000 đồng, Trưởng trạm/Đội trưởng 22.500.000 đồng, Trưởng Công an xã 37.500.000 đồng. Bởi vậy, 500.000 đồng không phải đáp án đúng cho ngày cũ đã gán trong câu này. [Thuộc tính văn bản NĐ 189](https://vanban.chinhphu.vn/?classid=1&docid=214510&pageid=27160&typegroupid=4), [toàn văn, Điều 8 và Điều 21](https://vbpl.vn/TW/Pages/ivbpq-toanvan.aspx?ItemID=179347), [giải thích của Bộ Công an ngày 18/4/2026](https://bocongan.gov.vn/chinh-sach-phap-luat/bai-viet/khong-tang-muc-phat-bo-sung-nhieu-quy-dinh-moi-hoan-thien-khung-xu-ly-vi-pham-giao-thong-duong-bo-1776415565).

`SD003`, `SD004` cùng dùng 01/06/2026 nhưng gán thẩm quyền cũ tương ứng 5.000.000 và 2.500.000 đồng. Cần sửa/loại khỏi tập chứng minh thay đổi tại 15/8/2026 sau khi đối chiếu NĐ 189. Rà thêm `SD005`, `SD006` theo cùng nguyên nhân, không suy rộng rằng mọi con số trong các câu đó đã được xác nhận sai.

`SD040` (dòng 190) cũng dùng ngày cũ 01/06/2026 và mô tả Chủ tịch UBND huyện còn thẩm quyền, đến 15/8/2026 mới không còn chức danh. **Cấp huyện đã kết thúc hoạt động từ 01/7/2025**; đây là một đối chứng thời gian không hợp lệ. [Nghị quyết 203/2025/QH15, Điều 2](https://xaydungchinhsach.chinhphu.vn/nghi-quyet-203-2025-qh15-sua-doi-bo-sung-mot-so-dieu-cua-hien-phap-nuoc-cong-hoa-xa-hoi-chu-nghia-viet-nam-119250616181735552.htm).

### Chuyển chức năng sát hạch, cấp GPLX không bắt đầu vào tháng 7/2026

`SD014`, `SD015` (dòng 164–165) dùng `ngay_cu = 2026-03-01` và gán Bộ trưởng Bộ GTVT là chủ thể quy định mẫu/thủ tục GPLX và nội dung/quy trình sát hạch. Bộ Công an đã tiếp nhận chức năng từ 01/3/2025; TT 12/2025/TT-BCA đã quy định những nội dung này, gồm mẫu GPLX. Nghị quyết 190/2025/QH15 xử lý việc tiếp nhận chức năng, thẩm quyền khi tổ chức lại bộ máy. Các câu này đang so sánh câu chữ chưa sửa của Luật 36 với câu chữ đã sửa, rồi diễn giải thành thay đổi thực tế tại 01/7/2026. [Hướng dẫn của Bộ Công an](https://bocongan.gov.vn/bai-viet/huong-dan-thuc-hien-thu-tuc-hanh-chinh-thuoc-tham-quyen-giai-quyet-cua-bo-cong-an-tu-ngay-0132025-d2-t43728), [quy định tiếp nhận thẩm quyền theo NQ 190](https://xaydungchinhsach.chinhphu.vn/quy-dinh-ve-so-luong-cap-pho-thuc-hien-chuc-nang-nhiem-vu-quyen-han-cua-co-quan-chuc-danh-co-tham-quyen-khi-sap-xep-bo-may-119250224113117647.htm), [TT 12 do Bộ Công an ban hành](https://bocongan.gov.vn/KND/vb/vbqp/Lists/VBQP/Attachments/2822/Thong%20tu%2012.2025.TT.BCA.pdf).

Đây không phải lý do loại mọi câu hỏi thẩm quyền: chuyển thẩm quyền thực sự vẫn là đối tượng eval phù hợp. Vấn đề là ngày cũ và quan hệ pháp lý giữa các văn bản.

### Ghế an toàn trẻ em: không thể áp mức phạt cũ tại ngày đã gán

`SD001` (dòng 151) chọn 01/06/2026 làm ngày cũ nhưng gán phạt 800.000–1.000.000 đồng. Kho hiện cho điểm m khoản 3 Điều 6 NĐ 168 `valid_from = 2025-01-01`, không có ngoại lệ, dù chính Điều 53 quy định hiệu lực riêng; Luật 118 còn lùi thời điểm áp dụng nghĩa vụ liên quan đến 01/07/2026. Bản tin chính thức của Cục CSGT được Chính phủ đăng lại giải thích quy định và giai đoạn chuyển tiếp. Ngày 01/06 không phù hợp để gán mức phạt này. Phải đối chiếu đầy đủ điều khoản thi hành rồi chọn lại ngày/cặp đối chứng, không chỉ kiểm ngày trên record. [Giải thích chính thức](https://xaydungchinhsach.chinhphu.vn/hieu-dung-quy-dinh-xu-phat-lien-quan-den-thiet-bi-an-toan-cho-tre-em-tren-xe-o-to-119260702152700723.htm).

**Ảnh hưởng:** tỷ lệ trả lời theo luật mới và tỷ lệ trích luật cũ có thể chấm sai hệ thống trả lời đúng. Kiểm tra bằng chính `data-v1` không phát hiện được phần quy định liên quan chưa được mô hình hóa trong kho. Kết luận này không có nghĩa đáp án hiện hành của toàn bộ 40 câu đều sai.

**Cách xử lý:** rà pháp lý cả 40 đối chứng, ưu tiên các câu trên; thay các cặp không có thay đổi thực chất trong khoảng thời gian đã chọn, hoặc bổ sung phụ thuộc pháp lý vào phiên bản dữ liệu tiếp theo. Mỗi câu cần có sự kiện thay đổi cụ thể, ngày áp dụng thực tế, và tiêu chí phân biệt câu trả lời cũ/mới. `SD017` cũng nên duyệt riêng: việc bản mới nêu rõ camera khoang khách không tự chứng minh bản cũ cho phép làm sai lệch camera đó.

## 2. [P1] Validator pass chưa chứng minh đáp án chuẩn đúng

`src/lawproc/evalset.py:103–135` kiểm tra chủ yếu sự xuất hiện của số tiền/số điểm và hiệu lực theo metadata. Sáu trường hợp cố ý sai dưới đây đều trả `[]`, tức được chấp nhận:

| Bản sao câu | Thay đổi thử | Kết quả |
|---|---|---|
| TH135 | Đảo min/max thành 600.000 / 400.000 | Pass |
| TH135 | Đổi đáp án thành “Phạt 1 đồng.” | Pass |
| TH138 | Đổi tước GPLX 22–24 tháng thành 1–2 tháng | Pass |
| TH135 | Đổi trích dẫn thành điểm z khoản 99 Điều 999 | Pass |
| SD024 | Đổi thời hạn cấp lại từ 2 thành 99 ngày | Pass |
| TH135 | Thêm căn cứ trừ 4 điểm của hành vi khác và kết luận không đội mũ cũng trừ 4 điểm | Pass |

Regex tiền chỉ bắt một số định dạng có dấu chấm phân cách nghìn; không kiểm `min <= max`; số điểm có mặt trong một căn cứ không bảo đảm khoản đó dẫn chiếu đúng hành vi đang hỏi. Không có bước kiểm trích dẫn văn xuôi trong validator được lưu. README nói đã kiểm thêm trước khi chốt, nhưng bước đó chưa được đóng gói thành kiểm tra tái lập.

Các phép thử này chứng minh phạm vi giới hạn của công cụ; không có nghĩa sáu lỗi giả lập đang tồn tại nguyên dạng trong file eval. Cần bổ sung kiểm tra cấu trúc có thể tự động hóa và duyệt nội dung riêng. Không đặt mục tiêu thay thế duyệt pháp lý bằng regex.

## 3. [P2] Một số câu biến thể làm thay đổi điều kiện trả lời

- **BT004, dòng 224:** câu gốc TH085 hỏi lệ phí cấp mới đăng ký/biển số ở Hà Nội; biến thể thành “Mua xe hơi 5 chỗ ở Hà Nội thì tiền làm giấy tờ, bấm biển số mất bao nhiêu?”. Nơi mua xe không xác định nơi cư trú của chủ xe; “tiền làm giấy tờ” còn rộng hơn đúng một khoản lệ phí. Không thể buộc đáp án duy nhất 14 triệu cho cách hỏi này. Mức theo khu vực gắn với trụ sở/nơi cư trú; chính TH088 đã nói đúng điều đó. [Bộ Tài chính](https://mof.gov.vn/bo-tai-chinh/du-lieu-va-thong-ke-tai-chinh/muc-thu-che-do-thu-nop-mien-le-phi-dang-ky-cap-bien-phuong-tien-giao-thong). Nên sửa thành “Tôi cư trú ở Hà Nội, đăng ký lần đầu xe hơi 5 chỗ thì riêng lệ phí đăng ký kèm biển số bao nhiêu?”.
- **BT024, BT026:** tự đồng nhất “xe 50cc” với “xe gắn máy”. Theo điểm g khoản 1 Điều 34 Luật 36, loại xe còn phụ thuộc vận tốc thiết kế không lớn hơn 50 km/h, bên cạnh dung tích không lớn hơn 50 cm³. Chỉ nói dung tích chưa khóa được tất cả điều kiện phân loại. Giữ tên pháp lý hoặc bổ sung điều kiện trong câu hỏi/đáp án.
- **TH010, TH095, BT019, BT045:** cách gọi “xe máy” và việc chưa có GPLX chưa đủ loại trừ mọi trường hợp xe gắn máy được miễn GPLX. Nên chỉ rõ xe mô tô 110/125 cm³ hoặc thêm điều kiện cần GPLX; nhất là khi chấm đáp án “Không” tuyệt đối. Đây là vấn đề câu hỏi thiếu giả định, không phải kết luận rằng đáp án sai với xe mô tô thông thường. [Luật 36, Điều 34 và Điều 56](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-trat-tu-an-toan-giao-thong-duong-bo-119240909105718285.htm).

`build_eval.py:98–100` sao chép nhãn từ câu gốc nên độ khớp nhãn là hiển nhiên về cơ học; bước này không kiểm được tương đương nghĩa. Cần đọc cả 50 cặp theo các điều kiện: loại xe, người vi phạm, tuổi/chiều cao, địa bàn, thời gian, mức độ vi phạm, phạm vi câu hỏi.

## 4. [P2] Cần định nghĩa cách chấm retrieval và độ đúng nội dung trước khi dùng số điểm

- `can_cu` đang trộn phần bắt buộc, phần giải thích thêm, và nhiều cấp cha/con. Chưa nêu đó là những căn cứ phải tìm đủ hay các đáp án thay thế nhau. TH136 cần cả quy định hành vi và quy định trừ điểm; tìm đúng một trong hai chưa đủ trả lời đầy đủ. Ngược lại, câu nhường đường có thể được hỗ trợ bởi Luật 36 hoặc QCVN 41, không nên bác mọi căn cứ hợp lệ ngoài danh sách duy nhất.
- TH004 cần 7 Khoản khác nhau; TH035 và TH094 cần 6. Nếu mỗi kết quả chỉ mang một Khoản và định nghĩa Recall@5 là tỷ lệ tìm đủ căn cứ, ngay cả bộ tìm kiếm tối ưu cũng không đạt 100% từng câu. So sánh cắt theo Điều với cắt theo Khoản cần ánh xạ từ chunk về tập đơn vị nguồn, tránh lợi thế chỉ do kích thước chunk.
- Nên ghi `required_evidence_groups` theo từng ý cần trả lời, mỗi nhóm cho phép các căn cứ tương đương; báo cáo riêng hit ít nhất một căn cứ và tìm đủ căn cứ cần thiết.
- Chỉ 14/150 câu thường có nhãn số tiền phạt. Đây là tập con nhỏ; “độ đúng mức phạt” phải nêu rõ mẫu số. Schema chưa có nhãn thời gian tước GPLX, thời hạn thủ tục, ngưỡng tốc độ, tỷ lệ phí, loại chế tài. TH138/TH144 có thể đúng tiền nhưng sai tước bằng; chỉ chấm tiền không thể hiện đầy đủ độ đúng pháp lý.
- `diem_tru = null` đang có thể hiểu là không áp dụng, không bị trừ hoặc chưa gắn nhãn. Cần tách các trạng thái này và chấm riêng mức trừ điểm khi có.
- Đây là các điều kiện để triển khai G3/G7; việc chưa có scorer hoàn chỉnh ở giai đoạn G2 không tự nó là lỗi triển khai.

## 5. [P2] Độ độc lập và độ khó cần được mô tả trung thực

- 50 biến thể là phép đo độ bền của 50 câu gốc, không phải 50 tình huống pháp lý độc lập mới. TH065 và SD034 cùng hỏi thời hạn cấp GPLX; TH080 và SD021 cùng kiểm quy tắc trước bạ xe máy. Nên báo cáo theo nhóm trước, bootstrap theo họ câu/đơn vị pháp lý khi gộp kết quả.
- Có **12/214 câu test có căn cứ** dùng ít nhất một `version_id` đã xuất hiện ở dev; 8 câu có căn cứ đầu tiên xuất hiện ở dev. Ví dụ TH132 (dev) và TH134 (test) dùng cùng Khoản/bảng tốc độ. Đây là ứng viên cần xem xét, **không tự động là rò rỉ train/test**: dùng chung luật là bình thường trong bài toán closed-corpus. Tuy nhiên phải phân biệt kết quả trên cùng quy tắc với tổng quát hóa sang quy tắc chưa dùng để chỉnh tham số.
- 30 câu ngoài phạm vi khớp phạm vi dự án, nhưng phần lớn khá dễ nhận ra; chưa có nhóm riêng về câu giao thông thiếu dữ kiện, câu có tiền đề sai hoặc câu pha phần trong/ngoài phạm vi. Nên thêm một tập thách thức nhỏ, không nhất thiết tăng tổng số câu.
- Bốn câu `luat_cu` có nhãn từ chối đúng với đặc tả không hỗ trợ luật trước 2025. Không coi chính sách này là lỗi pháp lý. Khi chấm cần chấp nhận câu trả lời giải thích giới hạn và dẫn luật hiện hành như README đã cho phép.
- Tất cả 270 câu dùng 01/10/2026. Điều này phù hợp yêu cầu chính trả lời tại ngày chốt; chỉ chưa đủ chứng minh khả năng trả lời theo ngày bất kỳ hay xử lý các mốc hoãn áp dụng trong tương lai.

## 6. Các việc nhỏ cần sửa khi phát hành lại

- README nói 10 văn bản sửa đổi/thay thế, thực tế `van_ban_sua_doi` có **9** giá trị. Tổng 40 câu vẫn đúng.
- `pick_dev` dùng top-n theo hash: tái lập được với đầu vào cố định, nhưng **không bảo đảm split không đổi khi thêm câu** như docstring mô tả. Audit có ví dụ chèn một key mới đẩy key dev cũ ra. ID TH/SD/NP/BT cũng phụ thuộc thứ tự dòng; giữ `key` và lưu manifest split/family khi đóng băng phiên bản.
- Mốc cấp lại biển số **7 ngày làm việc** của SD025 đã có nguồn nhà nước xác nhận, không cần giữ ghi chú “chỉ có trong kho”: [UBND xã Yên Lãng, Hà Nội](https://yenlang.hanoi.gov.vn/xay-dung-phap-luat/diem-moi-ve-thoi-han-giai-quyet-dang-ky-xe-2844260522135906624.htm). Trang có kết quả tìm kiếm chứa nội dung; lần mở trực tiếp trong lượt audit gặp lỗi máy chủ.

## Thứ tự hoàn thiện đề nghị

1. Rà lại 40 câu RQ3, xử lý các đối chứng sai ngày/thẩm quyền trước; ghi rõ nguồn duyệt cho cả đáp án mới lẫn đáp án cũ. Không lấy “khớp data-v1” làm chuẩn độc lập duy nhất.
2. Sửa các biến thể/giả định nêu trên; duyệt đủ 50 cặp. Giữ lại các câu thường đang tốt, không cần viết lại cả bộ.
3. Chốt rubric: ý bắt buộc, đáp án tương đương, căn cứ thay thế, loại chế tài, ngày/ngày làm việc, cách chấm từ chối. Tăng độ phủ nhãn cấu trúc ở các trường quyết định kết quả.
4. Lưu manifest phiên bản/split/họ câu, lọc gần trùng khi sinh train theo kế hoạch, rồi đóng băng bản tiếp theo. Báo cáo điểm riêng cho câu thường, RQ3, từ chối, biến thể và kèm mẫu số.

**Mức sẵn sàng:** đạt để thử pipeline RAG và phát hiện lỗi; cần sửa các P1 trước khi dùng làm đáp án chuẩn báo cáo kết quả. Review này không huấn luyện hay chấm chất lượng mô hình và không sửa nội dung bộ eval gốc.
