# Sửa G3 (cắt đoạn và bộ chấm) theo review — 17/10/2026

Phản hồi [review G3](../g3-chunking-score-review-2026-10-17/REPORT.md).
- Đã tự tái hiện cả ba lỗi trên dữ liệu thật trước khi sửa; cả ba đúng như review mô tả.
- Không sửa gì trong thư mục review và không chạy lại `verify.py` của review.
- Bộ eval `eval_v1.jsonl` không đổi (hash `5a1b7203…`).

## 1. [P1] Bộ chấm cho điểm đủ khi lấy nhầm mẩu phụ lục — đã sửa

**Tái hiện:** `lp08` (TH087) chỉ có mẩu `#1` của Phụ lục I TT 155. Mẩu này là phần cấp mới, không có các mức 70.000 / 35.000 / 50.000 đồng, nhưng bộ chấm vẫn cho `all = true`, `rr = 1`. Bốn câu bị ảnh hưởng: `lp06`, `lp07`, `lp08`, `bt04`.

**Sửa:**

| Chỗ | Thay đổi |
|---|---|
| `chunking.py` | Mẩu tách theo dòng có thêm `phan_dong`: `{version_id: [dòng đầu, dòng cuối, tổng số dòng]}`. `units` vẫn liệt kê mọi đơn vị có mặt trong mẩu |
| `data/eval/bang_chung_v1.json` (mới) | Lớp bổ trợ, không sửa `eval_v1.jsonl`. Ghi các dòng phụ lục bắt buộc của từng câu, chép nguyên văn từ dữ liệu: `lp06`, `bt04` dòng I.2; `lp07` dòng I.4.b; `lp08` dòng II.1.b, II.2, II.3.b. Mã băm ghi trong `data/rag/MANIFEST.json` |
| `score.py` | Nhóm có căn cứ bị tách mẩu chỉ đạt khi các mẩu lấy về chứa **mọi** dòng bằng chứng. Câu không có dòng bằng chứng thì các mẩu phải phủ đủ mọi dòng của đơn vị (quy tắc bảo thủ). Đoạn chứa trọn đơn vị vẫn được tính như cũ |
| `rr` | 1 / hạng nhỏ nhất mà top-hạng đã thỏa ít nhất một nhóm. Mẩu sai không còn được tính hạng 1 |

**Test mới:**
- **Ba test kiểm tra chấp nhận, theo đúng yêu cầu của review, chạy trên chunk thật của cả hai cách cắt:**
  - `lp08` chỉ có mẩu `#1` thì `all = false`, `rr = 0`.
  - Cả 4 câu (`lp06`, `lp07`, `lp08`, `bt04`): lấy mẩu sai kèm đủ căn cứ hỗ trợ thì `all = false`; lấy mẩu đúng kèm đủ căn cứ hỗ trợ thì `all = true`.
- **Các dòng bằng chứng:** phải là dòng có thật trong phụ lục, và cùng các căn cứ khác phải chứa đủ mọi mức tiền của đáp án.
- **Không bỏ sót căn cứ:** mọi căn cứ của eval bị tách mẩu đều phải có dòng bằng chứng. Thêm câu mới cần phụ lục dài thì test này sẽ báo.
- **Dữ liệu giả lập:** mẩu sai không được tính; quy tắc phủ đủ khi không có chú thích; hạng tính tại vị trí nhóm đầu tiên được thỏa.

## 2. [P1] Điều kiện hiệu lực mất khỏi chữ — đã sửa

**Tái hiện:** 111 mẩu có hiệu lực tại 01/10/2026 có ghi chú trong metadata nhưng không có trong `text`. Các mẩu này thuộc 8 phụ lục của TT 108 và TT 12.

**Sửa:**
- Mẩu tách theo dòng ghi điều kiện ngay sau tiêu đề, ở **mọi** mẩu, dạng `[Hiệu lực (phụ lục): …]`. Dòng này được tính vào giới hạn token.
- Đoạn dài hơn 512 token (chủ yếu đoạn theo Điều) nêu thêm điều kiện ngay sau tiêu đề, kèm tên đơn vị, ví dụ `[Hiệu lực (điểm a khoản 3): …]`, vì reranker chỉ đọc phần đầu. Ghi chú đặt cạnh Điểm vẫn giữ nguyên.

**Kết quả:** số ghi chú thiếu trong chữ giảm từ 123 xuống **0** ở cả hai cách cắt, có test kiểm toàn kho. Hiện có 151 đoạn theo Khoản và 156 đoạn theo Điều nêu điều kiện ở đầu đoạn.

## 3. [P2] Tách bảng mất tên cột — đã sửa

**Sửa:** mẩu bắt đầu giữa bảng (các dòng có " | ") lặp lại dòng chú thích bảng ngay phía trên bảng (nếu có chữ và không quá 200 ký tự) cùng dòng tên cột. Phần lặp được tính vào giới hạn token.

**Ví dụ:** QCVN 41 khoản 46.3. Mẩu chứa hàng `4 | Biển số IE.451 …` nay có thêm "Bảng 5 - Quy định về kiểu chữ, màu sắc của biển chỉ dẫn" và "TT | Mô tả biển chỉ dẫn | Kiểu chữ | Màu chữ, số | Màu nền | Màu viền". Có test trên dữ liệu thật và trên dữ liệu giả lập; test giả lập kiểm thêm rằng mọi hàng bảng xuất hiện đúng một lần.

**Cái giá:** số đoạn theo Khoản vượt 512 token tăng từ 19 lên 25. Sáu đoạn mới đều là bảng chấm điểm sát hạch của TT 108 và TT 12: mỗi mẩu chỉ còn một hàng bảng dài cộng phần lặp, nên vượt 1–114 token (dài nhất 626). Mức này vẫn dưới giới hạn 8.192 của bge-m3, và các đoạn đều có cờ `vuot_gioi_han`.

## 4. Manifest — đã bổ sung

`data/rag/MANIFEST.json` nay ghi:
- SHA-256 của chính file nguồn vừa đọc (cùng git blob trong tag `data-v1`);
- `amendments_reviewed.csv` và `data/manifest.csv` (dùng để dựng tên văn bản);
- đường dẫn và mã băm của **file tokenizer thực sự được nạp** (`load_tokenizer` trả về hàm có thuộc tính `path`);
- file bằng chứng.

`--check` nay so cả hai file chunk lẫn manifest.

Lưu ý: hash của file nguồn tính trên bản trong thư mục làm việc, nên có thể khác giữa các máy nếu git đổi kiểu xuống dòng. Mã ổn định là git blob.

## Kết quả sau sửa

| | Trước | Sau |
|---|---:|---:|
| Đoạn theo Khoản / có hiệu lực tại 01/10/2026 | 6.189 / 4.641 | 6.221 / 4.665 |
| Đoạn theo Điều / có hiệu lực | 2.117 / 1.463 | 2.149 / 1.487 |
| Ghi chú hiệu lực thiếu trong chữ (mỗi kho) | 123 | 0 |
| Test RAG | 36 | 58 |

Số đoạn tăng vì phần lặp (điều kiện, tên cột) chiếm thêm chỗ trong mẩu.

Kiểm tra:
- `py -3.13 scripts/build_chunks.py --check`: khớp.
- `py -3.13 scripts/build_eval.py --check`: hợp lệ; `eval_v1.jsonl` vẫn có hash `5a1b72038ae7…`.
- `py -3.13 -m pytest -q`: 364 test qua.
