# Review lại bộ eval sau bản sửa của Claude — 17/10/2026

**Kết luận: bản sửa có cải thiện thực chất và đã xử lý nhiều lỗi cũ. Còn ba điểm cần sửa trước khi chốt benchmark: cặp RQ3 `sd49`, nhãn số liệu bỏ mất ngưỡng đạt, và quy tắc gom căn cứ đang biến quan hệ “cần đủ” thành “chỉ cần một”.** Không cần làm lại toàn bộ 270 câu.

## Những phần đã xác nhận sửa đúng

| Nội dung | Kết quả kiểm tra độc lập |
|---|---|
| Test eval | 24/24 pass |
| Test toàn dự án | 299/299 pass, 11,27 giây |
| Build `--check` | Pass; build trong bộ nhớ khớp hoàn toàn file đã lưu |
| Thành phần | 270 câu, dev 30/test 240; 150 thường, 40 RQ3, 30 ngoài phạm vi, 50 biến thể |
| 12 câu RQ3 cũ cần loại | Các key sd01–sd06, sd14, sd15, sd17, sd19, sd20, sd40 đều đã bỏ; sd41–sd52 đều có |
| Sáu phép thử sai của vòng review trước | Tái chạy theo `key`, xác nhận phép sửa thực sự thay đổi dữ liệu: 6/6 đều bị bắt |
| Những biến thể đã yêu cầu sửa | Đã sửa nơi cư trú/phạm vi lệ phí, xe mô tô 110/125 cc, xe gắn máy thay cho cách nói chỉ dựa trên 50 cc |
| Chế tài thiếu trong `xp09`, `sd09`, `sd42` | Đã bổ sung vào đáp án và căn cứ |
| Split | Có manifest khóa theo `nhom_cau/key`; không còn dựa vào top-n hash mỗi lần build thông thường |
| Mẫu số của rubric | Các số 74+28 câu có số liệu, 14+6 câu có nhãn tiền phạt, 17 câu xét trừ điểm, 3 câu tước GPLX khớp dữ liệu; các mẫu số này loại biến thể |

Giải thích của Claude về lỗi 1/6 trong script audit cũ là đúng: `SD024` nay là `sd35`, không còn chứa chuỗi “02 ngày”, nên phép `.replace()` cũ là thao tác không đổi dữ liệu. Test mới khóa theo `key` và kiểm `mutated != item` xử lý đúng vấn đề này.

Bằng chứng vòng này ở [audit-031317389623Z.json](audit-031317389623Z.json), script [audit_eval.py](audit_eval.py). Script chỉ sửa bản sao trong bộ nhớ và tạo file bằng chứng mới bằng chế độ `x`, tên có thời gian; không ghi lại `audit.json` của vòng trước. Toàn bộ input quan trọng có SHA-256 trước/sau để xác nhận không bị sửa trong audit.

## 1. [P1] Cặp RQ3 mới `sd49` vẫn nhầm bổ sung câu chữ với thay đổi thực tế

**Vị trí:** `data/eval/eval_v1.jsonl:187`, id hiện tại **SD037**, key **sd49**; nguồn nháp `data/eval/drafts/sua_doi.jsonl:37`.

Câu hỏi: “Cơ sở đăng kiểm có được cấp chứng nhận an toàn kỹ thuật cho xe cơ giới cải tạo không?”. Ngày cũ là **01/03/2026**. Đáp án cũ nói khoản 1 Điều 43 Luật 36 chưa giao việc chứng nhận xe cải tạo; đáp án mới nói có, từ 01/07/2026.

Nhưng **TT 47/2024/TT-BGTVT đã quy định thủ tục chứng nhận xe cải tạo và cơ sở đăng kiểm thực hiện cấp chứng nhận trước mốc tháng 7/2026**. Phụ lục XVIII đã có mẫu chứng nhận mang tên cơ sở đăng kiểm; các thủ tục nhà nước công bố từ năm 2025 và trả lời chính thức đầu năm 2026 cũng thể hiện quy trình này. [TT 47 trên trang Bộ Xây dựng](https://moc.gov.vn/Images/FileVanBan/BGTVT_47-2024-TT-BGTVT_15112024.pdf), [thủ tục chứng nhận xe cải tạo theo TT 47](https://dichvucong.laocai.gov.vn/trang-chu/tra-cuu/chi-tiet-thu-tuc?ma-thu-tuc=44827), [trả lời về thủ tục xe cải tạo ngày 16/01/2026](https://cms.baochinhphu.vn/thu-tuc-quy-trinh-dang-kiem-xe-cai-tao-10226011611180279.htm).

Đáp án cũ có thể mô tả đúng chỗ chưa có trong riêng câu chữ khoản 1 Điều 43, nhưng không trả lời đúng câu hỏi về việc cơ sở đăng kiểm có được làm hay không tại ngày cũ. Một câu trả lời “Có” không tự chứng minh mô hình đã cập nhật Luật 118, vì câu trả lời đó đã phù hợp với quy trình trước đó.

**Đề nghị:** thay `sd49` bằng cặp có khác biệt đầu ra thật ở hai ngày; hoặc chuyển câu này sang câu thường và bù một câu RQ3 khác. Không giải quyết bằng cách chỉ đổi ngày trên record. Với các đáp án cũ dùng cụm “chưa được quy định tại điểm/khoản này”, cần kiểm thêm xem quy định liên quan đã có ở nơi khác hay chưa; chưa kết luận mọi câu như vậy đều sai.

## 2. [P1] `so_lieu` không chứa ngưỡng đạt 23/25, 27/30 và làm mất loại ngày

**Vị trí mã:** `src/lawproc/evalset.py:21–27`, `86–92`, `181–190`; `scripts/build_eval.py:107`.

Hai trường hợp đang có trong dữ liệu:

- `gp06` / TH054 có đáp án đạt **23/25 điểm**, nhưng `so_lieu` chỉ ghi 25 điểm, không ghi ngưỡng 23.
- `gp13` / TH061 có đáp án đạt **27/30 điểm**, nhưng `so_lieu` chỉ ghi 30 điểm, không ghi ngưỡng 27.

Thử thay **27/30 thành 26/30** trong đáp án `gp13`: validator vẫn trả `[]`; tập `facts()` trước và sau giống hệt nhau. Theo rubric chấm các cặp trong `so_lieu`, câu trả lời sai ngưỡng đạt có thể giữ nguyên điểm số liệu. Đây là thiếu sót trực tiếp của nhãn chuẩn, không phải yêu cầu regex hiểu mọi ý nghĩa pháp lý.

Thêm nữa, `UNITS` quy “ngày làm việc” thành “ngày”, “giờ làm việc” thành “giờ”. Thử đổi **02 ngày làm việc thành 02 ngày** trong `sd24`: vẫn pass và facts không đổi. Đơn vị này phải được giữ riêng khi chấm thời hạn thủ tục.

**Đề nghị:** gắn số liệu theo vai trò, ví dụ `diem_dat=27`, `tong_diem=30`, `thoi_han={gia_tri:2, don_vi:ngay_lam_viec}`. Parser có thể hỗ trợ dạng phân số, nhưng phải kiểm cả tử số và mẫu số. Thêm regression cho ngưỡng và ngày làm việc; build lại nhãn trước khi tính điểm mô hình.

## 3. [P1] Nhóm căn cứ chưa thể hiện đúng yêu cầu tìm đủ bằng chứng

**Vị trí:** `scripts/build_eval.py:86–89`; rubric `data/eval/README.md`, mục “Tìm kiếm”.

Mã hiện gom mọi `version_id` cùng Khoản vào một nhóm, README coi nhóm đạt nếu tìm được **bất kỳ một** phiên bản trong nhóm. Đây là các Điểm bổ sung nội dung cho nhau, không nhất thiết là căn cứ tương đương có thể thay thế nhau.

Ví dụ **gp01 / TH049**, hỏi tất cả trường hợp được đổi GPLX: nhóm duy nhất gồm điểm a, b, c, d, đ khoản 1 Điều 21 TT 108. Mô phỏng chỉ tìm được **điểm a** về GPLX bị hỏng: quy tắc README vẫn cho `all = True`, dù thiếu những trường hợp còn lại và điều kiện không đổi. Với **ll05 / TH093**, chỉ lấy record câu dẫn của khoản 3 Điều 33 cũng đủ đạt nhóm duy nhất, dù record đó không chứa danh sách các hành vi cấm ở các Điểm.

Có **58 câu thường/RQ3** chứa ít nhất một nhóm nhiều căn cứ; đây là số câu cần phân loại quan hệ, không phải khẳng định cả 58 nhóm đều sai. Repo chưa có scorer retrieval hoàn chỉnh, vì vậy kết quả mô phỏng là áp dụng đúng quy tắc README, không phải kết quả chạy hệ thống RAG.

**Đề nghị:** mỗi ý bắt buộc là một nhóm AND; bên trong nhóm chỉ dùng OR cho các cách cung cấp cùng ý đó. Nếu một chunk Khoản/Điều thật sự chứa đủ các Điểm thì ánh xạ chunk về tất cả đơn vị nguồn mà nó chứa. Một chunk chỉ chứa một Điểm hoặc câu dẫn không được đại diện cho toàn bộ Khoản. Cần test trường hợp chỉ tìm một Điểm và trường hợp tìm chunk đầy đủ, nhất là khi cắt Khoản dài thành các Điểm.

## 4. [P2] Một câu mới thiếu ngoại lệ; kiểm số tiền vẫn chỉ là kiểm sự xuất hiện

**`sd47` / SD035, dòng 185:** đáp án mới nêu ngoại lệ chuyển quyền sử dụng/sở hữu, nhưng bỏ ngoại lệ tại **điểm e khoản 10 Điều 23** được chính điểm b khoản 9 viện dẫn. Điểm e áp dụng khi đơn vị báo cáo không tiếp tục sử dụng phương tiện kinh doanh vận tải. Câu hỏi hiện hỏi mọi trường hợp thu hồi phù hiệu nên cần nêu ngoại lệ này hoặc giới hạn tình huống là bị thu hồi do vi phạm và không thuộc các ngoại lệ.

**Kiểm khung tiền:** thay “400.000 đồng đến 600.000 đồng” của `xp01` thành “600.000 đồng đến 600.000 đồng” vẫn pass dù các trường nhãn còn 400.000/600.000. Cả hai số đều xuất hiện trong nguồn nên quy tắc hiện tại không phát hiện mâu thuẫn đáp án–nhãn. Khác với việc kiểm đúng/sai một câu văn bất kỳ, kiểm khoảng phạt trong đáp án với cặp nhãn sẵn có là việc có thể làm trực tiếp. Kết quả này không phủ nhận sáu regression cũ đều đã được sửa.

## Những điểm còn là giới hạn, không cần làm lại toàn bộ bộ đề

- `ho_cau` mới nhóm biến thể với câu gốc; chưa nhóm các câu thường/RQ3 cùng hỏi một sự kiện. Ví dụ `gp17` / TH065 và `sd34` / SD023 cùng hỏi thời hạn cấp GPLX nhưng mang họ khác nhau. Khi bootstrap gộp nhiều nhóm, nên dùng họ sự kiện pháp lý; hoặc báo cáo riêng như README đã hướng dẫn.
- Bộ ngoài phạm vi chưa có câu thiếu dữ kiện/tiền đề sai: Claude đã ghi nhận đúng là chưa làm, không coi là bước đã hoàn tất.
- Việc chưa có chuyên gia duyệt toàn bộ không ngăn dùng bộ này để thử RAG. Tuy nhiên, sửa đáp án cũ bằng cách bỏ tên cơ quan hoặc chọn đoạn không nhắc đến một quyền không đủ chứng minh thay đổi thực tế. Các cặp RQ3 cần có đáp án cho cùng câu hỏi ở hai ngày.
- Việc giữ nguyên tên `eval_v1` khi bản cũ chưa commit có thể quản lý được, nhưng cần gắn hash/manifest ở lần đóng băng cuối. Không chạy lại script ghi đè lên cùng file bằng chứng của vòng review trước.

## Phạm vi xác nhận và thứ tự xử lý

Đã kiểm mã mới, 24 test eval, toàn bộ test dự án, build, các regression cũ, metadata mới và nội dung 40 câu RQ3; đối chiếu nguồn của 12 cặp mới trong kho và tra nguồn ngoài kho cho trường hợp đăng kiểm có vấn đề. Không xác nhận pháp lý toàn diện cho từng đáp án.

Ưu tiên: **thay/đổi nhóm `sd49` → sửa nhãn số liệu → sửa nhóm căn cứ và rubric → bổ sung ngoại lệ `sd47`, đối chiếu khoảng phạt → chốt hash và chạy lại kiểm tra**. Sau các sửa này có thể dùng bộ đề cho thực nghiệm chính, với phạm vi và hạn chế đã công bố.
