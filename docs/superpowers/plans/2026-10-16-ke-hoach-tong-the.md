# Kế hoạch tổng thể (bản rút gọn)

- **Ngày:** 2026-10-16
- **Người làm:** 1 người
- **Thay cho:** các mục 4.2 (lưu trữ), 5.6 (bộ eval), 7, 10, 11 của `docs/superpowers/specs/2026-10-08-traffic-law-qa-design.md` ở chỗ mâu thuẫn. Phần bối cảnh, bài toán và dữ liệu của bản thiết kế cũ giữ nguyên.
- **Hạn nộp:** chưa có, điền vào bảng mục 6.

## 0. Nguyên tắc

1. Làm xong một vòng từ đầu đến cuối (dữ liệu → RAG → mô hình → điểm số) trước, rồi mới cải tiến.
2. Dừng làm sạch dữ liệu. Lỗi còn lại (phụ lục QCVN M–P, 21 đơn vị OCR kém, TT108 `pl12`, NĐ39 `pl1`) đưa vào mục Hạn chế của báo cáo.
3. Mỗi giai đoạn phải ra file kết quả và bảng số liệu dùng thẳng cho report.
4. Lấy lại code của `../nlp-traffic-laws` (chép sang rồi sửa, không sửa repo cũ), không viết lại từ đầu.
5. Phần không cần GPU làm trên laptop; chỉ fine-tune và sinh câu trả lời mới chạy trên Kaggle.

## 1. Thay đổi so với thiết kế cũ

| Mục | Cũ | Mới | Lý do |
|---|---|---|---|
| Lưu trữ | PostgreSQL + pgvector | FAISS + chỉ mục BM25 lưu file | Không cần server; mang lên Kaggle dễ |
| Câu hỏi nghiên cứu | RQ1–RQ4 | RQ1–RQ3 bắt buộc, RQ4 tùy chọn | Một người, GPU hạn chế |
| Mô hình | 9B chính + bản nhỏ phụ | **Một** mô hình, chọn sau khi chạy thử Kaggle (G4) | Chưa biết GPU có đủ cho 9B không |
| Bộ eval | ~150 + 150 biến thể + 40–50 sửa đổi + 20–30 ngoài phạm vi + GPLX | 150 thường + 40 sửa đổi + 30 ngoài phạm vi + 50 biến thể (xem G2) | Vừa sức một người |
| Viết câu eval | Nhóm viết, người thứ hai kiểm tra chéo | LLM viết nháp từ đoạn luật → tự duyệt, sửa từng câu → đóng băng | Không có người thứ hai; ghi vào hạn chế |
| Đề GPLX trắc nghiệm | Có | Bỏ (làm nếu còn thời gian) | Nhiều câu có hình, xử lý tốn công |
| Chấm tay | 2 người, 50 câu | 1 người, 50 câu | |
| Khảo sát chatbot, cấu hình E | Tùy chọn | Bỏ | |
| BLDS, BLHS | Toàn văn | Chỉ giữ 213 đơn vị theo E2 (BLDS Điều 584–608, BLHS Điều 260–266) | 40% kho là hai bộ luật này, làm nhiễu tìm kiếm |

## 2. Câu hỏi nghiên cứu

| Mã | Câu hỏi | Thực nghiệm | Cần GPU |
|---|---|---|---|
| RQ1 | RAG và fine-tune đóng góp bao nhiêu? | A (gốc), B (gốc + RAG), C (LoRA), D (LoRA + RAG) | Có |
| RQ2 | Cách cắt đoạn và tìm kiếm nào tốt nhất? | BM25 / vector / hybrid / + reranker; cắt theo Điều so với theo Khoản | Không |
| RQ3 | Lọc theo hiệu lực có giúp trả lời theo luật mới không? | 40 câu về quy định đã sửa: có và không lọc `in_force_at`, ở cả tìm kiếm và câu trả lời | Không (tìm kiếm), có (câu trả lời) |
| RQ4 (tùy chọn) | Mô hình lớn hơn mô hình nhỏ bao nhiêu? | Chỉ làm nếu còn quota GPU | Có |

RQ2 và phần tìm kiếm của RQ3 chạy hoàn toàn trên laptop. Nếu fine-tune gặp sự cố, Report 3 vẫn có đủ kết quả thực nghiệm.

## 3. Các giai đoạn

Công là số ngày làm việc ước lượng cho một người.

### G0. Chốt dữ liệu (0,5 ngày) → Report 2
- Gộp nhánh `codex/eda-corpus` vào `main`, chạy lại `pytest`.
- Chốt phạm vi E2 (BLDS, BLHS) và `data/eval/eval_matrix.csv`.
- Gắn tag `data-v1`. Từ đây không sửa `data/processed/` nữa, trừ khi có lỗi chặn.

### G1. Viết Report 1 và Report 2 (1–2 ngày, làm theo hạn nộp)
- Report 1: rút gọn bản thiết kế cũ theo mục 1 và 2 của kế hoạch này.
- Report 2: viết lại từ `COLLECTION_LOG.md`, `PROCESSING_REPORT.md`, `reports/eda/findings.md` và các hình EDA.

### G2. Bộ eval `eval_v1` (2–3 ngày)
- **150 câu thường** theo ma trận đề: chọn đơn vị luật đang có hiệu lực → LLM viết nháp câu hỏi và đáp án → tự duyệt từng câu, ghi nhãn `van_ban, dieu, khoan, diem, muc_phat_min/max, diem_tru, chu_de, loai_cau`.
- **40 câu luật sửa đổi (RQ3):** chọn trong 661 địa chỉ có bản cũ và bản mới khác nội dung (E5); mỗi câu có đáp án theo cả bản cũ và bản mới.
- **30 câu ngoài phạm vi:** đường thủy, đường sắt, luật địa phương, luật cũ, chủ đề không liên quan. Đáp án là từ chối.
- **50 biến thể đời thường:** viết lại 50 câu trong số 150 câu thường theo kiểu viết tắt, không dấu, kể chuyện, dùng từ trong E7 ("bằng lái", "xe máy", "nón bảo hiểm"). Dùng chung nhãn với câu gốc.
- Tách 30 câu làm tập dev để chỉnh tham số; phần còn lại chỉ dùng để chấm điểm cuối.
- Đóng băng và ghi ngày: `data/eval/eval_v1.jsonl`.

### G3. Kho tra cứu và RAG (3–4 ngày, laptop) → RQ2, RQ3
- **Cắt đoạn:** mỗi đoạn là một Khoản kèm các Điểm của nó, có tiêu đề Điều và tên văn bản ở đầu đoạn; đoạn trên 512 token thì tách theo Điểm. Bỏ phụ lục mẫu biểu. Mỗi đoạn mang `version_id, valid_from, valid_to, hl_ngoai_le`. Làm thêm một bản cắt theo Điều để so sánh.
- **Chỉ mục:** bge-m3 trên CPU với FAISS; BM25 dùng pyvi để tách từ.
- **Tìm kiếm:** gộp BM25 và vector bằng RRF → reranker `bge-reranker-v2-m3` → lọc `in_force_at(t)` → lấy top-k.
- **Chấm tìm kiếm:** Recall@5 đúng văn bản, Recall@5 đúng Khoản, MRR; tách kết quả theo câu thường và biến thể đời thường.
- **Ablation:** chỉ BM25 / chỉ vector / hybrid / + reranker / bỏ lọc hiệu lực / cắt theo Điều.
- **Đầu ra:** `src/rag/` có test, `reports/retrieval/*.json`, và `test_with_context.jsonl` (ngữ cảnh đã tìm sẵn để dùng chung cho B và D).
- Lấy lại từ repo cũ: `retrieval_v4.py`, `sparse_bm25.py`, `chunking.py`, `build_kb.py`, `query_utils.py`.

### G4. Chạy thử trên Kaggle (0,5–1 ngày) → chọn mô hình
- Một notebook: tải mô hình 4-bit, QLoRA trên 100 mẫu, sinh câu trả lời cho 20 câu.
- Thử mô hình 9B và một mô hình nhỏ (khoảng 3–4B). Ghi lại: VRAM, thời gian train mỗi 100 mẫu, tốc độ sinh (token/giây).
- **Cách chọn:** ước tính tổng giờ GPU cần cho train ~2.000 mẫu cộng sinh 4 cấu hình × ~270 câu. Nếu 9B nằm gọn trong 1–2 tuần quota Kaggle thì chọn 9B; không thì chọn mô hình nhỏ. Thuê GPU chỉ là phương án cuối.
- Kiểm tra luôn: Unsloth có hỗ trợ mô hình đã chọn trên T4 không (T4 không có bf16, phải dùng fp16).

### G5. Dữ liệu train (2 ngày)
- Sinh ~1.500–2.000 cặp hỏi đáp từ các đơn vị đang có hiệu lực trong phạm vi, 1–3 cặp mỗi đoạn, nhiều loại câu, có cả mẫu từ chối.
- Mỗi mẫu kèm ngữ cảnh đã tìm được, với xác suất khoảng 0,9, giống `CONTEXT_KEEP_PROB` của repo cũ, để mô hình quen định dạng có RAG.
- Lọc: nhắc luật cũ, quá dài, trùng lặp, gần giống câu eval.
- Chia train/dev theo nhóm (văn bản, Điều).
- Tự kiểm tra tay 50–100 mẫu.
- Lấy lại từ repo cũ: `generate_qa.py`, `filter_qa.py`, `make_splits.py`.

### G6. Fine-tune (1–2 ngày, Kaggle)
- QLoRA bằng Unsloth, cố định seed, chọn checkpoint theo loss trên dev. Đẩy adapter lên Hugging Face.
- Lấy lại từ repo cũ: `finetune.py`.

### G7. Thực nghiệm A/B/C/D (2 ngày) → RQ1, RQ3
- Sinh câu trả lời trên Kaggle bằng greedy decoding, dùng `test_with_context.jsonl`.
- Chấm điểm trên laptop:
  - ROUGE-L, BERTScore;
  - độ đúng mức phạt;
  - tỷ lệ trích luật cũ;
  - từ chối đúng và từ chối sai;
  - tỷ lệ trả lời theo bản mới (RQ3);
  - LLM-Judge;
  - tự chấm tay 50 câu.
- Tách kết quả theo loại câu, chủ đề, và theo Điều đã gặp hoặc chưa gặp trong dữ liệu train. Tính khoảng tin cậy bằng bootstrap.
- Lấy lại từ repo cũ: `evaluate.py`, `llm_judge.py`.

### G8. Phân tích lỗi và một vòng cải tiến (2 ngày) → Report 3
- Phân loại khoảng 50 câu sai: lỗi tìm kiếm, lỗi hiệu lực hay lỗi sinh câu trả lời.
- Chọn **một** cải tiến theo nhóm lỗi lớn nhất, ví dụ ánh xạ từ đời thường sang thuật ngữ luật (E7), viết lại câu hỏi, hoặc kéo kèm đoạn được tham chiếu (E9). Chạy lại phần bị ảnh hưởng.
- Viết Report 3.

### G9. Demo (1–2 ngày)
- Xuất GGUF, chạy bằng llama.cpp hoặc Ollama trên laptop, giao diện Gradio. Màn hình hiển thị câu trả lời, trích dẫn Điều/Khoản/Điểm, đoạn luật gốc, ngày hiệu lực và cảnh báo "chỉ mang tính tham khảo".
- Thêm ô chọn ngày hỏi để minh họa RQ3. Có thể thêm chế độ so sánh B và D cạnh nhau, tham khảo `traffic-law-assistant`.
- Quay video trước. Phương án dự phòng: chạy demo trên Colab.

### G10. Report 4 và slide (2–3 ngày)
- Ghép Report 1–3 thành bài hoàn chỉnh theo cấu trúc paper; làm slide; viết README hướng dẫn tái lập.

**Tổng ước lượng:** khoảng 20–25 ngày làm việc.

## 4. Report ↔ phần paper

| Report | Phần paper | Lấy từ giai đoạn |
|---|---|---|
| 1. Đề xuất | Giới thiệu, bài toán, công trình liên quan, RQ | G1 |
| 2. Dữ liệu | Dataset: thu thập, xử lý, EDA, bộ eval | G0, G1, G2 |
| 3. Mô hình và kết quả | Phương pháp, thực nghiệm RQ1–RQ3, ablation, phân tích lỗi | G3–G8 |
| 4. Bản cuối và thuyết trình | Toàn bài, hạn chế, hướng phát triển, demo | G9, G10 |

Nếu Report 2 đến hạn trước khi xong G2, nộp phần bộ eval dưới dạng thiết kế và ma trận đề.

## 5. Rủi ro và phương án dự phòng

| Rủi ro | Dự phòng |
|---|---|
| T4 không đủ cho 9B | Chọn mô hình nhỏ ở G4; thuê GPU 24GB vài giờ nếu thật cần |
| Hết quota Kaggle | Dùng Colab; giảm số câu ở cấu hình A/C; thuê GPU theo giờ |
| Fine-tune không cải thiện | Vẫn báo cáo trung thực (kết quả âm vẫn là kết quả); RQ2, RQ3 không phụ thuộc fine-tune |
| Thiếu thời gian | Bỏ lần lượt: RQ4 → 50 biến thể → LLM-Judge → cải tiến ở G8 |
| Câu eval do LLM viết nháp bị thiên lệch | Tự duyệt từng câu; kiểm tra gần trùng với dữ liệu train; ghi vào hạn chế |
| Reranker trên CPU chậm | Chỉ rerank top-20; tìm sẵn ngữ cảnh một lần rồi lưu file |

## 6. Lịch

| Giai đoạn | Công (ngày) | Bắt đầu | Xong | Hạn report liên quan |
|---|---:|---|---|---|
| G0 Chốt dữ liệu | 0,5 | | | |
| G1 Report 1, 2 | 1–2 | | | Report 1: ____ · Report 2: ____ |
| G2 Bộ eval | 2–3 | | | |
| G3 RAG | 3–4 | | | |
| G4 Chạy thử Kaggle | 0,5–1 | | | |
| G5 Dữ liệu train | 2 | | | |
| G6 Fine-tune | 1–2 | | | |
| G7 A/B/C/D | 2 | | | |
| G8 Phân tích lỗi | 2 | | | Report 3: ____ |
| G9 Demo | 1–2 | | | |
| G10 Report 4, slide | 2–3 | | | Report 4: ____ |

G4 có thể chạy song song với G2 và G3: tranh thủ chạy notebook Kaggle trong lúc làm việc trên laptop.

## 7. Quyết định phạm vi đã chốt (2026-10-16)

| Mục | Quyết định |
|---|---|
| QCVN 41:2024 (biển báo) | Giữ phần chữ (84 Điều, phụ lục A–K). Bỏ hình biển báo và phụ lục M–P dạng ảnh. Hệ thống không nhận diện biển báo qua ảnh |
| BLDS 2015, BLHS (VBHN 135) | Giữ nguyên trong `data/processed`. Kho tra cứu, bộ eval và dữ liệu train chỉ dùng 213 đơn vị liên quan giao thông: BLDS Điều 584–608, BLHS Điều 260–266 |
| Bộ 600 câu sát hạch GPLX | Làm **bộ eval trắc nghiệm phụ**, chỉ lấy câu thuần chữ. Bỏ câu có hình (biển báo, sa hình). Đối chiếu đáp án với luật hiện hành tại ngày chốt; câu không còn khớp thì loại hoặc ghi chú |
| Nguồn chữ TT 108, TT 155, TT 36 | Word từ Công báo (TT 108, TT 155); bản chữ thuvienphapluat đã đối chiếu với PDF chính thức (TT 36) |

## 8. Việc cần quyết định

1. **Dùng LLM nào để viết nháp câu eval và sinh dữ liệu train (G2, G5):** API trả phí rẻ (Gemini Flash hoặc qua OpenRouter, ước khoảng vài USD) hay mô hình mở chạy trên Kaggle (miễn phí, tốn quota GPU). Laptop chỉ có CPU nên chạy cục bộ sẽ rất chậm.
2. **LLM-Judge:** dùng mô hình API nào, có giữ hay không.
3. **Mô hình chính:** quyết định sau G4.
