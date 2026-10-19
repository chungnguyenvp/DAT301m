# G7 — Thực nghiệm A/B/C/D (RQ1, RQ3)

## Thiết lập

- **Bộ eval:** `eval_v1`, kết quả báo trên **240 câu test** (30 câu dev cũng được sinh để dùng ở G8). Đáp án không đưa
  lên Kaggle.
- **Mô hình:** Qwen3.5-9B (commit `c202236…`), nạp 4-bit, fp16 trên Kaggle T4 x2. Adapter LoRA G6 (checkpoint bước
  208). A/B tắt adapter trên cùng mô hình đã nạp, nên bốn cấu hình dùng chung một bản mô hình gốc.
- **Ngữ cảnh:** 5 đoạn theo Khoản của G3 (hybrid + reranker, lọc hiệu lực tại ngày hỏi 2026-10-01). Lượt "bỏ lọc" dùng
  5 đoạn khi tắt lọc, chỉ trên 40 câu sửa đổi.
- **Sinh:** greedy, tối đa 512 token, prompt giống hệt lúc train G6.
- **Chạy:** notebook `notebooks/05_g7_generate`, khoảng 3,5 giờ trên T4 x2, 1.160 câu trả lời, không lỗi
  (`kaggle/g7/out_g7/`).
- **Chấm:** `py -3.13 scripts/score_g7.py` (`src/rag/answer_score.py`, test ở `tests/test_answer_score.py`). Chấm tự
  động theo rubric `data/eval/README.md`:
  - số liệu đọc bằng chính hàm đã tạo `so_lieu`;
  - CI95 bootstrap theo `ho_su_kien` (câu thường + sửa đổi) hoặc `ho_cau`;
  - so sánh hai lượt là bootstrap ghép cặp trên cùng câu.

  Bảng đầy đủ ở [summary.md](summary.md), số liệu ở `scores.json`, từng câu ở `per_item.csv`.

## Kết quả chính (test, câu thường + sửa đổi; % [CI95])

| Chỉ số | n | A: gốc | B: gốc + RAG | C: LoRA | D: LoRA + RAG |
|---|---|---|---|---|---|
| Nêu đúng mọi số liệu ↑ | 95 | 4,2 [1,0–8,7] | **61,1** [51,1–71,3] | 11,6 [5,4–18,5] | **60,0** [49,0–70,8] |
| Đúng khung phạt tiền ↑ | 17 | 5,9 | **88,2** | 17,6 | **88,2** |
| Đúng trừ điểm / không trừ ↑ | 14 | 64,3 | 42,9 | 64,3 | **71,4** |
| Trích đúng văn bản ↑ | 170 | 9,4 | **95,3** | 27,1 | 91,2 |
| Trích đúng Khoản ↑ | 164 | 0,0 | **86,0** | 1,2 | 82,3 |
| Trích văn bản ngoài kho ↓ (cả biến thể) | 214 | 94,4 | 4,7 | 21,0 | **0,5** |
| Từ chối đúng câu ngoài phạm vi ↑ | 26 | 34,6 | **100,0** | 61,5 | 92,3 |
| Từ chối sai câu trong phạm vi ↓ (cả biến thể) | 214 | 3,3 | 6,5 | 0,5 | 7,5 |
| ROUGE-L F1 ↑ (cả biến thể) | 214 | 0,157 | 0,326 | 0,286 | **0,581** |
| Lặp vòng ↓ (mọi câu) | 240 | 11,7 | 10,0 | 8,8 | **0,0** |
| Chạm giới hạn 512 token ↓ | 240 | 15,4 | 13,8 | 7,1 | **0,0** |
| Token trả lời trung bình / giây mỗi câu (cả 270 câu) | | 380 / 31,9 | 312 / 28,5 | 106 / 11,9 | **88 / 12,3** |

## RQ1: RAG và fine-tune đóng góp bao nhiêu?

1. **RAG quyết định độ đúng.**
   - Nêu đúng mọi số liệu: A → B **+56,8 điểm** [+46,2; +67,0]; C → D **+48,4** [+37,6; +59,6].
   - Trích đúng Khoản: từ gần 0% lên 82–86%.
   - Không có ngữ cảnh, mô hình gốc trích **văn bản đã hết hiệu lực ở 94% câu**: NĐ 100/2019, NĐ 123/2021, Luật Giao
     thông đường bộ 2008. Đây đúng là vấn đề dự án đặt ra.
2. **Fine-tune một mình giúp rất ít về độ đúng** (số liệu C − A = +7,4 [+2,1; +13,7]). Thêm nữa, C **bịa số hiệu văn
   bản** không tồn tại (TT 10/2026, TT 15/2024: không có trong kho, cũng không có trong dữ liệu train), và **lặp vòng**
   ở 8,8% câu: 17/270 câu chạm 512 token, đều do lặp một cụm.
3. **Khi đã có RAG, fine-tune không tăng độ đúng số liệu hay trích dẫn.** D − B: số liệu −1,1 [−10,0; +7,6]; Khoản −3,7
   [−9,0; +1,7]; đều không có ý nghĩa thống kê. Fine-tune **thay đổi cách trả lời:**
   - giống đáp án hơn: ROUGE-L +0,255 [+0,228; +0,283];
   - hết lặp vòng và hết bị cắt: −10 và −13,8 điểm, có ý nghĩa;
   - **ngắn hơn 3,5 lần** (88 so với 312 token), **sinh nhanh hơn 2,3 lần** (12,3 so với 28,5 giây/câu);
   - gần như không trích văn bản ngoài kho: 0,5% so với 4,7% (−4,2 [−6,9; −1,8]);
   - trừ điểm đúng hơn: 71,4% so với 42,9%, CI [+0,0; +53,8], n = 14 nên chỉ là dấu hiệu.
4. **Từ chối:**
   - Câu ngoài phạm vi: B từ chối đúng 26/26, D 24/26. B tốt nhờ system prompt và ngữ cảnh không liên quan.
   - Từ chối sai câu trong phạm vi: B và D gần như **chỉ** từ chối khi 5 đoạn đưa vào **không chứa căn cứ**.
     - Có căn cứ: B 1,6%, D 0,5%.
     - Không có căn cứ (n = 31): B 35,5%, D 48,4%.

     Đây là hành vi "không có căn cứ thì không bịa" đúng như được yêu cầu. Nguyên nhân gốc là lỗi tìm kiếm.
5. **Khoản đã gặp hay chưa gặp trong train không tạo ra lợi thế cho D:** số liệu đúng 51,7% (đã gặp, n = 60) và 75,8%
   (chưa gặp, n = 33). Mô hình không học thuộc nội dung luật; độ đúng đến từ ngữ cảnh. Chênh lệch hai nhóm có lẽ do
   khác nhau về loại câu.

**Kết luận RQ1:** với mô hình 9B và kho luật thay đổi nhanh, độ đúng gần như hoàn toàn nhờ RAG. Fine-tune LoRA đem lại
câu trả lời gọn, đúng định dạng, không lặp, nhanh gấp đôi và ít trích văn bản lạ, nhưng không làm số liệu đúng hơn.
Dùng LoRA không có RAG là cấu hình tệ: sai và bịa văn bản.

## RQ3: lọc hiệu lực ở câu trả lời (câu sửa đổi, test)

"Theo bản mới" và "nêu số liệu bản cũ" chỉ đo trên **21/36 câu** có số liệu khác nhau giữa hai bản. 15 câu còn lại khác
nhau về chữ, cần chấm tay.

| Chỉ số | B | B bỏ lọc | D | D bỏ lọc |
|---|---|---|---|---|
| Nêu số liệu của bản cũ ↓ | 4,8 | **61,9** | **0,0** | 33,3 |
| Theo bản mới ↑ | 85,7 | 81,0 | **90,5** | 71,4 |
| Nêu đúng mọi số liệu (n = 28) ↑ | 78,6 | 75,0 | 82,1 | 71,4 |

- **Bỏ lọc hiệu lực làm mô hình trả lời theo luật cũ:**
  - B: từ 4,8% lên 61,9% (−57,1 [−76,2; −33,3]);
  - D: từ 0% lên 33,3% (−33,3 [−52,4; −14,3]).

  Cùng với kết quả tìm kiếm của G3 (bỏ lọc thì 32/36 câu lấy nhầm bản cũ), lọc hiệu lực là thành phần **bắt buộc**.
  Ghi chú hiệu lực trong ngữ cảnh ("hiệu lực từ … đến …") không đủ để mô hình tự loại bản cũ.
- **D chống chịu tốt hơn B khi lẫn bản cũ:** 33% so với 62%. Có thể do được train trên ngữ cảnh có ghi hiệu lực, nhưng
  n = 21 nên cần thận trọng.

## Biến thể đời thường (44 cặp test, so với câu gốc cùng lượt)

| | D: biến thể / gốc | B: biến thể / gốc |
|---|---|---|
| Nêu đúng mọi số liệu (32 cặp) | 40,6 / 59,4 | 37,5 / 56,2 |
| Trích đúng Khoản | 46,5 / 74,4 | 46,5 / 76,7 |
| Từ chối sai | 29,5 / 2,3 | 22,7 / 0,0 |

Hỏi kiểu đời thường, viết tắt, không dấu thì tụt khoảng 19 điểm số liệu và gần 30 điểm trích dẫn. Từ chối sai tăng lên
khoảng một phần tư số câu. Nguyên nhân khớp với G3: tìm đúng căn cứ tụt từ 0,86 xuống 0,52. **Đây là nhóm lỗi lớn nhất
để cải tiến ở G8.**

## Các điểm yếu khác (cho G8)

- **Có căn cứ trong ngữ cảnh mà vẫn sai số liệu:** D đúng 61,3% (n = 93), tức khoảng 39% câu sai ở bước sinh, hoặc
  ngữ cảnh chỉ có một phần căn cứ (G3: tìm đủ mọi nhóm căn cứ chỉ ở 66% câu thường). G8 cần tách hai trường hợp này.
- **Bỏ sót chế tài bổ sung:** cả 3 câu có tước GPLX, không lượt nào nhắc tới tước GPLX. Có lẽ khoản quy định tước
  không nằm trong 5 đoạn.
- **Theo loại câu (D, số liệu đúng):** thủ tục 72,5%, chung 66,7%, tình huống 47,4%, mức phạt 45,5%. Câu tình huống và
  mức phạt cần ghép nhiều khoản.

## Hạn chế

- **Chỉ chấm tự động phần đo được bằng quy tắc:** số liệu, chế tài, trích dẫn, từ chối, lặp. Phần **nội dung** (đủ ý
  chính, không thêm chế tài sai) chưa chấm. Kế hoạch là LLM-Judge cộng chấm tay khoảng 50 câu ở G8.
- **"Nêu đúng mọi số liệu" rất chặt:** thiếu một số là sai. Trích dẫn chấm theo việc câu trả lời có nhắc đúng văn
  bản, Điều, Khoản, chưa kiểm câu trích có đúng nội dung không.
- **Từ chối nhận bằng cụm từ ở 300 ký tự đầu.** Đã đọc mẫu các câu D bị tính từ chối sai: 15/16 câu là từ chối thật khi
  ngữ cảnh không có căn cứ.
- **Một số mẫu số nhỏ:** khung phạt 17, trừ điểm 14, tước GPLX 3, RQ3 21. CI rộng.
- Một lần sinh greedy, một seed, mô hình 4-bit trên T4 (fp16).
