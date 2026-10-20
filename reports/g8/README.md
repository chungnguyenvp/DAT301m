# G8 — Phân tích lỗi, chấm nội dung và một cải tiến

G8 dùng các câu trả lời G7 (`kaggle/g7/out_g7/g7_answers.jsonl`), kết quả chấm tự động (`reports/g7/per_item.jsonl`)
và hai lượt sinh lại có ngữ cảnh mới (`kaggle/g8/out_g8/g7_answers.jsonl`). Mọi số liệu dưới đây tính trên **tập
test**, 240 câu.

| Bước | Script | Kết quả |
|---|---|---|
| Phân loại lỗi tự động của B, D | `scripts/g8_errors.py` | `loi_B.csv`, `loi_D.csv`, `loi_tong_hop.json` |
| Cải tiến: mở rộng Khoản lên Điều | `src/rag/expand.py`, `scripts/g8_context.py` | `retrieval_test.json`, ngữ cảnh `data/rag/test_with_context_g8.jsonl` |
| Sinh lại D_g8, B_g8 (Kaggle T4 x2, 101 phút) | `kaggle/g8/` | `kaggle/g8/out_g8/g7_answers.jsonl` (540 câu) |
| Chấm tự động D_g8, B_g8 | `scripts/score_g8.py` | `auto/summary.md`, `auto/scores.json`, `auto/per_item.jsonl` |
| Chấm nội dung (LLM-Judge) D, B, D_g8, B_g8 | chấm trong phiên, ghi `judge_claude.jsonl`; tổng hợp bằng `scripts/g8_judge_summary.py` | `judge_summary.md`, `judge_scores.json` |
| Phiếu chấm tay 50 câu (để kiểm giám khảo) | `scripts/g8_manual_sheet.py` | `cham_tay_50.csv` (chờ điền) |

## 1. Chấm nội dung

**Cách chấm.** Với mỗi (lượt, câu), giám khảo đọc câu hỏi, đáp án chuẩn, ghi chú của bộ eval và câu trả lời, rồi ghi ba
nhãn:

- `dat`: đủ ý chính và kết luận đúng so với đáp án chuẩn. Câu hỏi mức phạt phải đúng cả tiền phạt lẫn điểm trừ hoặc
  tước GPLX nếu đáp án có. Câu ngoài phạm vi thì đạt khi từ chối đúng (từ chối mà kèm thông tin bịa thì không đạt). Lỗi
  phụ như trích nhầm số Điều không làm trượt nếu kết luận và số liệu vẫn đúng.
- `che_tai_sai`: nêu sai mức phạt, điểm trừ, tước GPLX hoặc hình phạt, kể cả khi câu hỏi không hỏi đến.
- `theo_luat_cu`: trả lời theo phiên bản đã hết hiệu lực tại ngày hỏi.

Giám khảo là Claude (claude-opus-5-5) chấm trực tiếp trong phiên làm việc, không qua API: 4 lượt × 240 câu = 960 nhãn.
Mô hình sinh câu trả lời là Qwen3.5-9B, nên giám khảo không chấm bài của chính họ mô hình mình. Khi một mức phạt trong câu
trả lời không có trong đáp án, giám khảo tra lại kho văn bản trước khi gắn `che_tai_sai`. Ví dụ mức phạt 5–10 triệu đồng
cho việc mang điện thoại vào phòng thi (`thuong/gp16`) có thật ở điểm k khoản 3 Điều 39 NĐ 168, nên không tính là bịa.

**Hạn chế.** Chỉ có một giám khảo. Giám khảo biết câu trả lời thuộc lượt nào, nên không mù lượt. Sau khi chấm, các ca
giống nhau được rà lại cho cùng một chuẩn giữa các lượt; 5 nhãn của B đã được sửa (`gp16`, `ll06`, `xp05`, `xp06`,
`xp10`). Cần phiếu chấm tay 50 câu `cham_tay_50.csv` để đo độ khớp; điền xong thì chạy lại
`scripts/g8_judge_summary.py`.

### Tỷ lệ đạt (D và B, ngữ cảnh G7)

| Nhóm | n | D: LoRA + RAG | B: gốc + RAG | D − B |
|---|---|---|---|---|
| Trong phạm vi (thường + sửa đổi) | 170 | 85,9 [80,3–91,0] | 82,4 [76,0–87,9] | +3,5 [−1,8; +8,8] |
| Thường | 134 | 83,6 | 82,1 | +1,5 [−5,2; +7,5] |
| Sửa đổi | 36 | 94,4 | 83,3 | **+11,1 [+2,8; +22,2]** |
| Biến thể | 44 | 36,4 | 38,6 | −2,3 [−13,6; +6,8] |
| Ngoài phạm vi (từ chối đúng) | 26 | 92,3 | 92,3 | 0 |

| Lỗi nghiêm trọng | D | B |
|---|---|---|
| Nêu sai chế tài (trong phạm vi) | **1,2%** [0,0–3,0] | **10,0%** [6,0–14,6] |
| Trả lời theo luật cũ (câu sửa đổi, có lọc hiệu lực) | 0% | 0% |

Bảng đầy đủ, theo loại câu: `judge_summary.md`.

### Nhận xét

1. **Về nội dung, LoRA không làm tăng tỷ lệ đúng chung.** D và B chênh +3,5 điểm, CI95 chứa 0. Điều này khớp kết luận
   G7: độ đúng chủ yếu đến từ RAG.
2. **LoRA giảm rõ việc bịa chế tài.** B nêu sai mức phạt, điểm trừ hoặc hình phạt ở 10,0% câu trong phạm vi, D chỉ
   1,2%. Phần lớn lỗi của B là thông tin mô hình tự thêm khi câu hỏi không hỏi đến. Ví dụ `thuong/ll08`: B kết luận chở
   vợ và con 10 tuổi là sai luật, rồi bịa mức phạt 2 triệu đồng và trừ 2 điểm. D trả lời ngắn (khoảng 88 token, B
   khoảng 310) nên ít bịa thêm.
3. **Câu sửa đổi: D tốt hơn B có ý nghĩa thống kê** (+11,1 điểm). B hay trộn hai phiên bản. Ví dụ B dẫn TT 12/2025 thay
   cho TT 65/2024 (`thuong/gp13`), hoặc nêu thêm mức phạt "từ 15/08/2026" không có thật (`thuong/xp08`). Có lọc hiệu
   lực thì cả hai không trả lời theo luật cũ (0%). Bỏ lọc thì tỷ lệ này tăng mạnh: B lên 61,9%, D lên 33,3% (chỉ số tự
   động G7, RQ3).
4. **Biến thể là điểm yếu lớn nhất**, chỉ khoảng 37% đạt. Với D, 13/28 câu trượt là **từ chối sai**: căn cứ có trong kho
   nhưng 5 đoạn lấy về không chứa căn cứ, nên mô hình nói "không có căn cứ". B cũng từ chối sai nhiều, và thêm lỗi trả
   lời theo văn bản đã hết hiệu lực (gợi ý NĐ 100/2019) khi không có căn cứ.
5. **Câu mức phạt khó nhất** (D 63,6%, B 45,5%). Mô hình thường đúng tiền phạt nhưng thiếu hoặc sai điểm trừ, tước GPLX.
   Ví dụ `thuong/xp03`: đúng 18–20 triệu đồng nhưng ghi trừ 9 điểm thay vì 04 điểm. Đoạn trừ điểm (khoản 16 Điều 6,
   khoản 13 Điều 7 NĐ 168) là một Khoản riêng, thường không được lấy về cùng đoạn mức phạt.

### Độ khớp với chấm tự động

- Phân loại lỗi tự động (`g8_errors.py`) **đếm lỗi nhiều hơn thực tế**. Trên 214 câu thường, sửa đổi và biến thể của D,
  phân loại tự động xếp 90 câu là lỗi; giám khảo chỉ cho trượt 52 câu. Chênh lệch chủ yếu ở nhóm "lỗi sinh": 27/33 câu
  D bị xếp vào đây vẫn đạt nội dung. Lý do: chỉ số "nêu đủ số liệu" đòi đủ mọi con số của đáp án, kể cả số phụ.
- Ngược lại, 8 câu D được chấm tự động là "đúng" lại trượt nội dung, vì kết luận sai dù số liệu và trích dẫn khớp. Ví
  dụ `thuong/ll08`: tự động thấy đúng Điều 33, nhưng kết luận ngược đáp án.
- Trong 52 câu D trượt nội dung, 38 câu (73%) thuộc nhóm từ chối sai, ngữ cảnh không có căn cứ, hoặc thiếu một phần căn
  cứ. Như vậy **bước tìm kiếm vẫn là nguyên nhân lỗi chính**, đúng như phân tích lỗi tự động.

## 2. Phân tích lỗi tự động

Xem `loi_tong_hop.json`. Mỗi câu thuộc đúng một nhóm, xét theo thứ tự ưu tiên: từ chối sai; ngữ cảnh không có căn cứ;
thiếu một phần căn cứ; lỗi sinh; đúng. Trên 214 câu của D: 124 đúng, 16 từ chối sai, 14 không có căn cứ, 27 thiếu một
phần, 33 lỗi sinh.

## 3. Cải tiến: mở rộng Khoản lên Điều

**Cách làm.** Vẫn lấy 5 đoạn theo Khoản như G3. Sau đó mỗi đoạn được thay bằng **cả Điều** chứa nó, trong giới hạn 2.500
token; các Điều trùng thì gộp lại; Điều nào dài hơn ngân sách thì giữ Khoản (`src/rag/expand.py`). Ngân sách chọn trên
dev và 30 câu train, không dùng test. Ngữ cảnh trung bình tăng từ khoảng 1.241 lên 2.153 token. Không train lại: vẫn mô
hình và adapter G6, chỉ sinh lại hai lượt D_g8 (LoRA + ngữ cảnh mới) và B_g8 (gốc + ngữ cảnh mới).

Ví dụ `thuong/hd02` hỏi nộp hồ sơ xin dùng tạm vỉa hè ở cơ quan nào và bằng hình thức nào. Trước cải tiến, ngữ cảnh có
khoản 3, 4, 6, 7 Điều 21 NĐ 165 nhưng thiếu khoản 5 (thẩm quyền), nên B trả lời "không nêu rõ cơ quan". Sau cải tiến,
ngữ cảnh có cả Điều 21, và cả D_g8 lẫn B_g8 nêu đúng Khu Quản lý đường bộ, Sở Xây dựng, UBND cấp xã.

### Kết quả

| Chỉ số (test) | D | D_g8 | D_g8 − D | B | B_g8 | B_g8 − B |
|---|---|---|---|---|---|---|
| Tìm đủ mọi nhóm căn cứ, câu thường (G3) | 65,7 | 82,8 | **+17,1** | 65,7 | 82,8 | **+17,1** |
| **Đạt nội dung, trong phạm vi (170)** | 85,9 | 87,1 | +1,2 [−2,4; +4,8] | 82,4 | 85,3 | +2,9 [−2,4; +8,4] |
| Đạt nội dung, biến thể (44) | 36,4 | 40,9 | +4,5 [0,0; +11,4] | 38,6 | 40,9 | +2,3 [−11,4; +15,9] |
| Nêu sai chế tài, trong phạm vi | 1,2 | 0,0 | | 10,0 | 5,9 | |
| Nêu đúng mọi số liệu (tự động, 95) | 60,0 | 61,1 | +1,1 [−4,3; +6,7] | 61,1 | 66,3 | +5,3 [−1,0; +11,7] |
| Trích đúng Khoản (tự động, 164) | 82,3 | 56,1 | **−26,2 [−34,3; −18,8]** | 86,0 | 70,1 | **−15,9 [−22,9; −8,7]** |
| Chạm giới hạn 512 token (240) | 0 | 0 | | 13,8 | 18,8 | **+5,0 [+0,4; +9,8]** |
| Giây/câu trên T4 | — | 13,4 | | — | 30,6 | |

Chi tiết: `auto/summary.md` (chấm tự động), `judge_summary.md` (chấm nội dung, danh sách câu đổi kết quả).

### Nhận xét

1. **Tìm kiếm tốt lên rõ, nhưng câu trả lời chỉ đúng hơn một chút.** D_g8 hơn D +1,2 điểm và B_g8 hơn B +2,9 điểm, cả hai
   đều không có ý nghĩa thống kê. Với D: 8 câu từ sai thành đúng (ví dụ `hd02`, `gp05`, `lp05`, `dk01`, `bt35`), 4 câu từ
   đúng thành sai (`sd58`, `dk04`, `ll08`, `np06`).
2. **Vì sao lợi ích nhỏ.** Các câu được sửa là loại "thiếu một Khoản trong cùng Điều". Ba nhóm lỗi lớn còn lại không đổi:
   - Biến thể từ chối sai: retriever lấy nhầm cả Điều, không phải thiếu một Khoản, nên mở rộng không giúp (D_g8 vẫn từ
     chối sai 14 câu biến thể, D là 13).
   - Câu mức phạt: Điều 6 (khoảng 5.000 token) và Điều 7 (khoảng 3.600 token) NĐ 168 dài hơn ngân sách, nên vẫn chỉ có
     Khoản mức tiền, thiếu Khoản trừ điểm (mức phạt vẫn 63,6% ở D_g8).
   - Lỗi kết luận của mô hình dù ngữ cảnh đủ, ví dụ `ll08`, `bt20` (chở trẻ dưới 12 tuổi).
3. **Ngữ cảnh dài hơn giúp B bớt bịa chế tài** (10,0% còn 5,9%), nhưng làm B dài dòng hơn: tỷ lệ chạm giới hạn 512 token
   tăng có ý nghĩa (13,8% lên 18,8%).
4. **Tác dụng phụ: trích dẫn kém chính xác hơn.** Tỷ lệ trích đúng Khoản giảm mạnh (D 82,3% còn 56,1%). Đoạn Điều chỉ có
   tiêu đề "Điều X", nên mô hình ghi "Điều 10 Nghị định 67" mà không ghi khoản. Nội dung vẫn đúng nhưng trích dẫn kém cụ
   thể. Cách sửa: ghi nhãn từng Khoản trong đoạn Điều, hoặc nhắc trong prompt phải ghi số khoản.

**Kết luận cho Report 3.** Mở rộng lên Điều là cải tiến đúng hướng cho phần tìm kiếm (+17 điểm tìm đủ căn cứ), nhưng
không đủ để tăng độ đúng của câu trả lời một cách có ý nghĩa. Hai hướng tiếp theo nhắm vào các nhóm lỗi còn lại: (1) viết
lại câu hỏi đời thường sang thuật ngữ luật (E7) cho câu biến thể; (2) khi lấy Khoản mức phạt của NĐ 168 thì kéo kèm
Khoản trừ điểm, tước GPLX của cùng Điều.
