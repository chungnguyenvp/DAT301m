# G5 — Dữ liệu train cho fine-tune Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** tạo **khoảng 2.000** cặp hỏi đáp có căn cứ (người dùng chốt 18/10/2026), bám câu chữ luật đang có hiệu lực, để fine-tune QLoRA ở G6. Kèm mẫu từ chối, và khoảng 90% mẫu có ngữ cảnh tìm được bằng retriever của G3.

**Architecture:**
- Nguồn là các đoạn theo Khoản đang có hiệu lực tại `config.CUTOFF` (`data/rag/chunks_khoan.jsonl`). Đã bỏ chỉ dẫn sửa đổi và mẫu biểu.
- Chia train/dev **theo Điều** bằng mã băm cố định. Một Điều nằm trọn trong train hoặc trọn trong dev.
- Claude soạn câu hỏi–đáp án theo đợt, mỗi đợt một chủ đề, lưu ở `data/train/drafts/`.
- `scripts/build_trainset.py` ghép các đợt, chạy bộ kiểm tự động (dùng lại `lawproc.evalset.check_items`), lọc trùng và lọc gần trùng với câu eval, chia train/dev, ghi `data/train/` cùng manifest.
- Bước gắn ngữ cảnh chạy riêng, sau khi G3 xong.

**Tech Stack:** Python 3.13; `lawproc.evalset`, `lawproc.eda.near_duplicates`; `rag.retrieve` (bước gắn ngữ cảnh).

**Spec:** `docs/superpowers/plans/2026-10-16-ke-hoach-tong-the.md` mục G5.

**Quyết định đã chốt (18/10/2026, người dùng đồng ý):**
- Claude soạn dữ liệu, theo đợt, có bộ kiểm tự động. Người dùng kiểm tay 50–100 mẫu ở cuối.
- Quy mô và tỷ lệ loại câu như bảng bên dưới.

**Bộ giữ lại để chấm (không train, không chép câu):** `eval_v1` (270 câu) và 281 câu đề GPLX thuần chữ (`trainset.gplx_items`).
- Bộ GPLX do Cục CSGT soạn, độc lập với Claude. Đây là phép kiểm rủi ro "cùng người viết eval và train", nên không dùng để train.
- Mẫu train gần trùng một câu trong hai bộ này bị loại và ghi vào manifest.

**So với repo tham khảo `nlp-traffic-laws`:** repo có 1.762 mẫu train (1.249 mẫu có nội dung, 513 mẫu từ chối), do LLM sinh. Báo cáo của repo ghi dùng Gemini 2.0 Flash qua OpenRouter và có đối chiếu với nguồn; code mặc định gọi Qwen3.5-9B qua Ollama. File dữ liệu không ghi mẫu nào do mô hình nào sinh, nên không khẳng định được mức kiểm tra thực tế.

**Phân bổ mục tiêu khoảng 2.000 mẫu** (trọng số như ma trận eval; soạn theo thứ tự chủ đề nhưng giữ cân đối để nếu dừng sớm vẫn có bộ dùng được):

| Chủ đề | Mẫu | Chủ đề | Mẫu |
|---|---:|---|---:|
| Xử phạt (NĐ 168, NĐ 336…) | ~440 | Nộp phạt, giữ xe | ~140 |
| GPLX | ~220 | Đăng kiểm | ~100 |
| Đăng ký xe | ~180 | Lệ phí, Bảo hiểm | ~80 mỗi chủ đề |
| Luật lõi (Luật 35, 36) | ~180 | Tốc độ, Biển báo, Tai nạn | ~80 mỗi chủ đề |
| Hướng dẫn (NĐ 158, 165…) | ~160 | Từ chối | ~180 |

## Rủi ro đã biết, ghi vào hạn chế

1. **Cùng một LLM (Claude) soạn cả bộ eval lẫn dữ liệu train.** Mô hình fine-tune có thể được lợi một phần vì quen văn phong. Cách giảm rủi ro:
   - lọc gần trùng câu hỏi với eval (TF-IDF ký tự 4-gram);
   - ở G7 báo cáo riêng câu hỏi về Điều đã có và chưa có trong train;
   - ghi rõ trong báo cáo.
2. **Điều khoản sử dụng** của nhà cung cấp mô hình về việc dùng đầu ra để train: người dùng tự kiểm theo gói đang dùng.
3. Bộ kiểm tự động bảo đảm số liệu, trích dẫn và chế tài khớp căn cứ, **không** kiểm được nghĩa của câu. Vì vậy cần bước kiểm tay.

## Loại câu và tỷ lệ (mục tiêu, có thể chỉnh theo nguồn)

| `loai` | Tỷ lệ | Ví dụ |
|---|---:|---|
| `muc_phat`: mức phạt, trừ điểm, tước GPLX | ~30% | "Vượt đèn đỏ bằng xe máy bị phạt bao nhiêu, trừ mấy điểm?" |
| `thu_tuc`: thủ tục, thời hạn, hồ sơ, thẩm quyền | ~25% | "Đổi GPLX cần giấy tờ gì?" |
| `quy_tac`: quy tắc, định nghĩa, điều kiện | ~15% | "Xe máy chuyên dùng là gì?" |
| `tinh_huong`: tình huống thực tế | ~10% | "Tôi chở 2 người lớn trên xe máy thì sao?" |
| `doi_thuong`: cách nói đời thường, viết tắt, không dấu | ~10% | "bằng lái hết hạn có bị phạt k" |
| `tu_choi`: ngoài phạm vi | ~10% | "Luật hàng hải quy định gì về tàu cá?" |

Mỗi đoạn nguồn có 1–3 cặp, khác loại nhau. Câu `doi_thuong` vẫn có đáp án viết chuẩn và qua đủ bộ kiểm số liệu.

## Định dạng nháp (`data/train/drafts/<chu_de>_<đợt>.jsonl`)

```json
{"key": "xp-0001", "chu_de": "Xử phạt", "loai": "muc_phat", "cau_hoi": "...", "dap_an": "...",
 "can_cu": ["nd_168_2024:d7:k2:h@2025-01-01", "nd_168_2024:d7:k2@2025-01-01"]}
```

- `key` là duy nhất và ổn định.
- `can_cu` liệt kê mọi `version_id` làm căn cứ: Điểm, câu dẫn của Khoản, và khoản chế tài nếu đáp án nêu trừ điểm hoặc tước GPLX.
- `ngay_hoi` mặc định là `config.CUTOFF`.
- Mẫu `tu_choi` có `can_cu: []`; đáp án nói rõ câu hỏi nằm ngoài phạm vi tài liệu luật giao thông đường bộ đang có.

## File

| File | Việc |
|---|---|
| `src/lawproc/trainset.py` | Chọn nguồn, chia theo Điều, đổi mẫu sang dạng câu eval để kiểm, lọc gần trùng |
| `tests/test_trainset.py` | Test |
| `scripts/build_trainset.py` | Ghép nháp, kiểm, lọc, chia, ghi `data/train/train.jsonl`, `dev.jsonl`, `MANIFEST.json`; `--check` chỉ kiểm |
| `scripts/attach_context.py` (sau G3) | Gắn ngữ cảnh cho mẫu, ghi `data/train/train_with_context.jsonl` |
| `data/train/drafts/*.jsonl` | Nháp theo đợt |
| `data/train/README.md` | Mô tả bộ dữ liệu, cách tái lập, hạn chế |

## Các bước

### Task 1: Nguồn và chia train/dev
- `source_chunks(chunks, day)`: đoạn theo Khoản có hiệu lực tại `day`, bỏ mẩu phụ lục.
- `topic_of(doc_id)`: chủ đề lấy từ cột `nhom` của `data/manifest.csv`, cùng 12 chủ đề với eval.
- `split_of(unit_id, dev_ratio=0.1)`: theo SHA-256 của `doc:Điều`; ổn định, không phụ thuộc thứ tự.
- Test: cùng Điều thì cùng tập; tỷ lệ dev xấp xỉ 10%; chạy lại cho cùng kết quả.

### Task 2: Bộ kiểm tự động
- `as_eval_items(samples, records)`: đổi mẫu sang dạng câu eval và gắn nhãn chế tài theo luật (như `scripts/build_eval.py:label`). Sau đó `check_samples` gọi `evalset.check_items`.
  - Mẫu thường được kiểm: căn cứ có thật và còn hiệu lực; mọi số liệu trong đáp án có trong căn cứ hoặc câu hỏi; trích dẫn trỏ tới đơn vị có hiệu lực; luật có trừ điểm hoặc tước GPLX thì đáp án phải nêu; không có câu hỏi trùng.
  - Mẫu từ chối được kiểm: không có căn cứ.
- `near_eval(samples, eval_items, threshold)`: các mẫu có câu hỏi gần trùng câu eval. Ngưỡng chốt sau khi xem phân bố, ghi vào manifest.
- Test: mẫu sai số tiền bị bắt; mẫu thiếu trừ điểm bị bắt; câu gần giống câu eval bị lọc.

### Task 3: Soạn theo đợt
Thứ tự đợt: Xử phạt → GPLX → Đăng ký xe → Luật lõi → Hướng dẫn → Nộp phạt, giữ xe → Đăng kiểm → Lệ phí → Bảo hiểm → Tốc độ → Biển báo → Tai nạn → Từ chối.

Mỗi đợt:
- đọc chữ luật bằng `scripts/eval_context.py tree`;
- soạn 100–200 cặp;
- chạy `scripts/build_trainset.py --check`, sửa tới khi sạch;
- báo cáo số mẫu theo loại.

- [x] Đợt 1a: Điều 7 NĐ 168 (xe mô tô, xe gắn máy). 60 mẫu, 0 lỗi; 5 mẫu bị loại vì cùng câu hỏi với câu eval (TH135, TH136, TH141, TH143, TH144); giữ 55.
- [x] Đợt 1b: Điều 6 NĐ 168 (ô tô). 66 mẫu, 0 lỗi; 2 mẫu bị loại vì gần câu eval (TH138, TH142); giữ 64.
- [x] Đợt 1c: Điều 9, 10, 12 NĐ 168 (xe đạp, người đi bộ, xe máy chuyên dùng...). 45 mẫu, 0 lỗi, giữ 45.
- [x] Đợt 1d: Điều 14, 18, 33, 35 NĐ 168 (điều kiện xe máy, điều kiện người lái, hành khách, đua xe). 42 mẫu, 0 lỗi, giữ 42.
- [x] Đợt 1e: Điều 32 NĐ 168 (chủ phương tiện). 55 mẫu, 0 lỗi, giữ 55; cả 55 rơi vào dev vì Điều 32 băm vào dev. Lần chạy đầu có 9 mẫu lỗi vì khoản 8 viết "từ 8.000.000 đến 12.000.000 đồng" (thiếu "đồng" sau số đầu); đã sửa đáp án theo đúng chữ văn bản.
- [x] Đợt 1f: Điều 8, 13, 20, 21, 34 NĐ 168 (xe máy chuyên dùng, điều kiện xe ô tô, xe chở khách, xe chở hàng, quá tải quá khổ). 100 mẫu, 0 lỗi, giữ 100 (đều train). Điều 8 trong văn bản gốc chỉ có khoản 1–9, không có khoản xử phạt bổ sung hay trừ điểm, nên đáp án chỉ nêu tiền phạt.
- [x] Đợt 1g: NĐ 168 Điều 11, 15, 16, 17, 19, 22, 28, 36 và NĐ 336/2025 Điều 5, 10, 11 (hiệu lực 01/3/2026). 58 mẫu, 0 lỗi, giữ 58.
- Lũy kế nhóm Xử phạt sau đợt 1g: 426 soạn, giữ 418 sau khi chạy lại (xp-0359 bị loại khi kho lớn thêm vì cosine TF-IDF với TH141 lên 0,85). Còn thiếu khoảng 20 mẫu so với mục tiêu 440; bổ sung sau từ NĐ 168 Điều 23–27, 29–31, 37–40 nếu cần.
- [x] Đợt 2a: GPLX, Luật 36 Điều 57–62 (hạng, thời hạn, điểm, tuổi, đào tạo, sát hạch, cấp đổi, thu hồi) và TT 108/2026/TT-BCA (hiệu lực 01/7/2026). 75 mẫu, 0 lỗi; 8 mẫu bị loại vì gần câu eval (TH050, TH052, TH056, TH059, TH064, TH100, BT024, BT033); giữ 67.
- [x] Đợt 2b: GPLX, TT 65/2024/TT-BCA sửa bởi TT 105/2026 (kiểm tra để phục hồi điểm; cấu trúc bài kiểm tra hiện hành áp dụng đến hết 30/6/2027) và TT 36/2024/TT-BYT (sức khỏe người lái xe). 28 mẫu, 0 lỗi; 2 mẫu bị loại (TH054, TH057); giữ 26.
- [x] Đợt 2c: NĐ 168 Điều 49–51 (trừ điểm, phục hồi điểm), NĐ 94/2026 (tự học, đào tạo từ xa, trung tâm sát hạch, giáo viên), NĐ 168 Điều 47 (đối tượng xử phạt, phạt nguội) và Điều 48 (không xuất trình giấy tờ, tạm giữ xe). 33 mẫu, 0 lỗi; 1 mẫu bị loại (TH058); giữ 32.
- [x] Sửa sau đợt 2c: khoản 3 Điều 47 NĐ 168 quy định người lái đồng thời là chủ phương tiện thì bị xử phạt theo điều khoản tương ứng của Điều 32 đối với các lỗi về biển số, đăng ký xe, kiểm định, niên hạn, thùng xe, phù hiệu, thời gian lái, thiết bị giám sát, quá tải, quá khổ, quá số người, hàng dạng trụ. 51 mẫu cũ hỏi về người lái theo Điều 13, 14, 16, 20, 21, 22, 34 được bổ sung một câu ghi chú và căn cứ điểm tương ứng của khoản 3 Điều 47. Bước sửa nằm ở script `g5_fix_owner.py` (scratchpad), phải chạy lại sau mỗi lần sinh lại các nháp `xu_phat_*.jsonl`; script không nhân đôi ghi chú.
- Lũy kế sau đợt 2c: 562 soạn, giữ 543 (train 464, dev 79). GPLX đạt 110/220.
- [x] Đợt 3a: Đăng ký xe, TT 79/2024/TT-BCA bản đang có hiệu lực (nguyên tắc, cơ quan đăng ký, trách nhiệm chủ xe, thời hạn giải quyết theo bản 18/5/2026, hồ sơ, đăng ký lần đầu, sang tên, đổi, cấp lại, tạm thời, thu hồi, biển số). 60 mẫu, 0 lỗi; 10 mẫu bị loại vì gần câu eval (TH034, TH035, TH036, TH039, TH040, TH043, TH046, TH047, TH048, SD010); giữ 50. Lũy kế: 622 soạn, giữ 593 (train 509, dev 84).
- [x] Đợt 3b: đấu giá biển số (NĐ 156/2024, Luật 36 Điều 37–38) và hồ sơ chi tiết, trường hợp đặc biệt của TT 79/2024 (Điều 9, 11–13, 28–33). 40 mẫu, 0 lỗi, giữ 40. Lũy kế: 662 soạn, giữ 633 (train 543, dev 90); Đăng ký xe 90/180.
- [ ] Đợt 3c: Đăng ký xe còn lại (Luật 36 Điều 39–41 về đăng ký xe, niên hạn; TT 79 Phụ lục ký hiệu biển số theo địa phương nếu có trong kho), cho tới khoảng 180 mẫu.
- [x] Đợt 4a: Nộp phạt, giữ xe. Luật XLVPHC hợp nhất 90/2026 (Điều 6, 56, 58, 66, 70, 73, 74, 76–79, 125, 126) và NĐ 138/2021 bản 15/3/2026. 47 mẫu, 0 lỗi, giữ 44.
- [x] Đợt 5a: Đăng kiểm, TT 30/2026/TT-BXD (miễn kiểm định, kiểm định ô tô, kiểm định khí thải xe máy, chu kỳ Phụ lục V, cấp lại, tem, cải tạo, phương tiện vi phạm). 47 mẫu, 0 lỗi, giữ 40. Bảng chu kỳ ô tô ở Phụ lục V bị mất cột số khi xử lý văn bản, nên chỉ dùng phần chu kỳ xe máy và các ví dụ có số.
- [x] Đợt 6a: Lệ phí (NĐ 10/2022 bản 01/7/2025; TT 155/2025) và Bảo hiểm (NĐ 67/2023). 48 mẫu; lần đầu 10 lỗi vì bảng phí bảo hiểm ghi số không kèm chữ "đồng" và văn bản viết "09 chỗ", đã sửa; giữ 36.
- [x] Đợt 7a: Tốc độ (TT 38/2024) và Biển báo, đèn tín hiệu (QCVN 41:2024). 44 mẫu, 0 lỗi sau khi sửa "Bảng 3 điểm a" (bộ kiểm hiểu nhầm thành "3 điểm"); giữ 38.
- [x] Đợt 8a, 8b: Luật lõi, Luật 36 Điều 9–33, 35, 40, 56. 66 + 28 mẫu, 0 lỗi, giữ 93.
- [x] Đợt 9a: Tai nạn (BLDS 2015 Điều 584, 585, 590, 591, 601; BLHS hợp nhất 135/2025 Điều 260, 264) và 60 mẫu `tu_choi` (40 câu ngoài phạm vi, 15 đề nghị giúp vi phạm, 5 câu đời thường). 80 mẫu, 0 lỗi, giữ 74.
- [x] Đợt 10a: Hướng dẫn, NĐ 158/2024 (taxi, xe hợp đồng, an toàn vận tải, phù hiệu) và NĐ 165/2024 (hành lang an toàn, sử dụng tạm thời lòng đường, vỉa hè). 36 mẫu, 0 lỗi, giữ 35.
- Lũy kế sau đợt 10a: 1.058 soạn, giữ 993 (train 854, dev 139). Theo loại: mức phạt 347, quy tắc 307, tình huống 130, đời thường 79, thủ tục 70, từ chối 60. Các chủ đề Lệ phí, Bảo hiểm, Tốc độ, Tai nạn, Đăng kiểm còn dưới mục tiêu; câu thủ tục mới 7% so với mục tiêu 25%.
- [x] Đợt 11 (bù câu thủ tục, chủ yếu ở các Điều chưa có mẫu thủ tục):
  - 11a: Đăng ký xe, TT 79/2024 (các bước sang tên, đổi, cấp lại trực tiếp, đăng ký tạm thời và gia hạn, thu hồi khi mất hoặc hư hỏng, xe tịch thu, thanh lý, đóng lại số máy, số khung, biểu mẫu, quy định chuyển tiếp). 37 mẫu, 0 lỗi; loại 1 (dk-0122 gần SD013).
  - 11b: GPLX, TT 108/2026 (nộp hồ sơ sát hạch, thi lại, bằng PET, cấp lại, đổi bằng hỏng, đổi bằng quân sự và trong Công an, IDP, người khuyết tật, người dân tộc thiểu số). 24 mẫu, 0 lỗi; loại 3 (gp-0137 gần SD023, gp-0145 gần TH053, gp-0155 gần SD021).
  - 11c: Đăng kiểm, TT 30/2026 (kiểm định lần đầu, khí thải xe đăng ký tạm thời, cấp lại giấy kiểm định, chứng nhận xe cải tạo và cấp lại). 17 mẫu, 0 lỗi, giữ 17.
  - 11d: Luật XLVPHC 90/2026 Điều 57, 61, 64, 69, 80, 86, 125; NĐ 138/2021 Điều 12, 17; NĐ 158/2024 Điều 19–21, 23 (giấy phép kinh doanh vận tải, phù hiệu). 24 mẫu, 0 lỗi; loại 2 (hd-0038 trùng TH070 với độ giống 1,00; hd-0041 gần SD032).
  - 11e: Luật 36 Điều 39, 66, 69, 72, 80, 81 (tai nạn, dừng xe kiểm tra, di chuyển xe đỗ sai); NĐ 10/2022 Điều 4, 11; TT 155/2025 Điều 2, 3, 7; TT 36/2024/TT-BYT Điều 4, 6; NĐ 156/2024 Điều 7, 16, 18. 21 mẫu, 0 lỗi; loại 1 (dk-0139 gần TH045).
  - 11f: NĐ 94/2026 Điều 11–13, 15–16 (giấy chứng nhận giáo viên dạy thực hành lái xe, giấy phép xe tập lái). 8 mẫu, 0 lỗi, giữ 8.
- Lũy kế sau đợt 11: 1.189 soạn, giữ 1.118 (train 969, dev 149), loại 71 vì gần eval. Theo loại: mức phạt 347, quy tắc 329, thủ tục 164 (15%), tình huống 137, đời thường 81, từ chối 60. Không bù tới 25%: các Điều còn lại có thủ tục chủ yếu là thủ tục của cơ quan (lưu trữ hồ sơ, giám sát kỳ sát hạch, cấp phép trung tâm sát hạch, giấy phép vận tải quốc tế), ít gặp trong câu hỏi của người dân. ND 336/2025 (xử phạt trong hoạt động đường bộ) không dùng cho câu "không mang giấy tờ" của người lái vì câu này thuộc NĐ 168.

- [x] Đợt C1 (Codex): Biển báo, QCVN 41:2024/BGTVT, Phụ lục B–G (`pl2`–`pl7`), Điều 51, 76–78. 80 mẫu (`bb-1001`–`bb-1080`), 0 lỗi, không có mẫu mới bị loại gần eval (không có cặp key–eval); giữ 80. Đã đọc đầy đủ các phụ lục, chỉ dùng nội dung chữ rõ ràng, tự rà ngữ nghĩa từng câu và các ngoại lệ. Kết quả kiểm toàn kho tạm thời: 1.269 soạn, giữ 1.198 (train 1.048, dev 150), loại 71 cũ; không ghi lại train/dev/manifest trong đợt này.
- [x] Đợt C2 (Codex): Luật lõi, Luật 35/2024 Điều 7, 15–16, 18, 21, 39, 43, 45, 47, 50–52, 54, 60, 72–73; Luật 36/2024 Điều 32, 43–47, 49, 51–53, 55, 63–65, 67, 73, 76, 79, 82–85. 60 mẫu (`lu-1001`–`lu-1060`), 0 lỗi; loại mới `lu-1011` gần `TH103` (0,72), giữ 59. Đã tự rà từng mẫu theo toàn văn đơn vị, ngữ cảnh liên quan và ngoại lệ hiệu lực; giữ ngoại lệ bất khả kháng/trở ngại khách quan, điều ước quốc tế và điều kiện hỗ trợ của quỹ. Kết quả toàn kho tạm thời: 1.329 soạn, giữ 1.257 (train 1.096, dev 161), loại 72; không ghi train/dev/manifest.

**Quy tắc lọc gần trùng (chốt sau đợt 1a):** loại mẫu nếu cosine TF-IDF ký tự 4-gram với một câu giữ lại ≥ 0,85, hoặc ≥ 0,6 khi cùng hỏi một quy định. "Cùng quy định" nghĩa là đơn vị nội dung đầu tiên của bên này nằm trong căn cứ của bên kia; bỏ qua câu dẫn đã có đơn vị con. Lý do: các câu trùng thật ở đợt 1a chỉ giống nhau 0,70–0,82 theo chữ.

### Task 4: Gắn ngữ cảnh (sau G3)
- Khoảng 90% mẫu có ngữ cảnh: top-5 của retriever tại `ngay_hoi`. **Đảm bảo có đoạn chứa căn cứ:** nếu retriever bỏ sót thì thay đoạn cuối bằng đoạn đúng, để mô hình học trả lời từ ngữ cảnh.
- Khoảng 10% mẫu không có ngữ cảnh, để mô hình quen cấu hình C.
- Một phần nhỏ mẫu từ chối có ngữ cảnh không liên quan, để mô hình học nói "không có căn cứ".
- Chọn tỷ lệ bằng seed cố định, ghi vào manifest.

### Task 5: Kiểm tay và chốt
- Người dùng đọc 50–100 mẫu ngẫu nhiên (seed cố định); sửa lỗi phát hiện được.
- Ghi `data/train/MANIFEST.json` (mã băm) và `README.md`; gắn tag `train-v1`.
