# Thiết kế dự án: Hỏi đáp pháp luật cho người tham gia giao thông đường bộ Việt Nam

- **Ngày:** 2026-10-08
- **Trạng thái:** Bản nháp chờ duyệt
- **Môn học:** DAT301m (dự án end-to-end)
- **Repo tham khảo:** `../nlp-traffic-laws` (dự án cũ của môn NLP, chỉ dùng để tham khảo code và kết quả, không sửa)

**Tên đề tài**
- Tiếng Việt: *Xây dựng hệ thống hỏi đáp pháp luật cho người tham gia giao thông đường bộ Việt Nam theo hiệu lực văn bản, kết hợp RAG và fine-tune LoRA*
- Tiếng Anh: *Vietnamese Road-User Law Question Answering with Version-Aware RAG and LoRA Fine-Tuning*

**Loại dự án:** dự án ứng dụng có thực nghiệm. Dùng các phương pháp đã có (RAG, LoRA/QLoRA, BM25, RRF), không đề xuất phương pháp mới. Đóng góp nằm ở dữ liệu có gắn hiệu lực, bộ đánh giá, hệ thống chạy cục bộ và kết quả thực nghiệm.

---

## 1. Bối cảnh và vấn đề

### 1.1 Bối cảnh
- Pháp luật giao thông đường bộ gắn với đời sống hằng ngày: người tham gia giao thông có thể bị xử phạt, phải làm thủ tục giấy tờ, hoặc gặp tai nạn.
- Giai đoạn 2024–2026 hệ thống văn bản thay đổi rất dày:
  - Luật Đường bộ 35/2024/QH15 và Luật Trật tự, an toàn giao thông đường bộ 36/2024/QH15 thay Luật Giao thông đường bộ 2008.
  - NĐ 168/2024/NĐ-CP thay NĐ 100/2019/NĐ-CP về xử phạt (hiệu lực 01/01/2025).
  - Luật 118/2025/QH15 sửa hai luật trên (hiệu lực 01/7/2026).
  - NĐ 238/2026/NĐ-CP sửa NĐ 168 (hiệu lực 15/8/2026).
  - Các văn bản xung quanh cũng thay đổi: lệ phí đăng ký xe (TT 60/2023 bị thay bằng TT 155/2025), đăng kiểm (TT 47/2024 bị thay bằng TT 30/2026/TT-BXD), bảo hiểm bắt buộc (NĐ 67/2023 bị sửa bởi NĐ 220/2026), đăng ký xe (TT 79/2024 bị sửa bởi TT 37/2026), Luật Xử lý vi phạm hành chính (sửa bởi Luật 88/2025).
  - Các mốc trên được tổng hợp từ báo chí và trang tra cứu; phải đối chiếu văn bản gốc ở bước thu thập.

### 1.2 Vấn đề
- Người dân khó biết quy định nào đang áp dụng, vì văn bản mới chỉ sửa một phần văn bản cũ.
- Thông tin trên mạng lẫn cũ và mới; nhiều bài hỏi đáp vẫn dẫn NĐ 100/2019 hoặc NĐ 46/2016.
- Chatbot AI phổ thông có thể trả lời theo luật cũ, bịa mức phạt, không nêu căn cứ; đồng thời cần internet, có thể tốn phí và gửi dữ liệu ra ngoài.

### 1.3 Bằng chứng về vấn đề (tùy chọn)
Khảo sát sơ bộ: hỏi khoảng 30 câu về các quy định vừa sửa đổi với một vài chatbot phổ thông, ghi tỷ lệ trả lời đúng theo luật hiện hành. Kết quả dùng làm số liệu mở đầu cho báo cáo; kết quả nào cũng dùng được.

### 1.4 Giải pháp hiện có và khoảng trống
| Giải pháp | Hạn chế |
|---|---|
| Tự tra trên trang văn bản pháp luật | Phải biết văn bản nào, tự đối chiếu bản gốc với bản sửa đổi |
| Bài tư vấn trên trang luật, báo | Nhiều bài đã cũ, không ghi thời điểm áp dụng |
| Chatbot AI phổ thông | Có thể theo luật cũ, không trích nguồn, cần internet |
| Dự án cũ `nlp-traffic-laws` | 12 văn bản, có lẫn bản dự thảo, thiếu sửa đổi 2025–2026, không lưu hiệu lực, chưa có EDA |

**Khoảng trống thực tiễn:** chưa có hệ thống hỏi đáp mã nguồn mở, chạy cục bộ, miễn phí, trả lời theo văn bản đang có hiệu lực và có trích dẫn căn cứ cho pháp luật giao thông đường bộ Việt Nam.

---

## 2. Định nghĩa bài toán

### 2.1 Mục tiêu
Hệ thống hỏi đáp pháp luật cho người tham gia giao thông đường bộ Việt Nam:
- trả lời câu hỏi tiếng Việt theo văn bản đang có hiệu lực tại thời điểm hỏi;
- trích dẫn căn cứ đến Điều, Khoản, Điểm;
- từ chối khi không có căn cứ;
- chạy cục bộ trên laptop, không cần internet khi demo.

### 2.2 Người dùng
- **Chính:** người dân tham gia giao thông, hỏi bằng ngôn ngữ đời thường, cần câu trả lời ngắn có mức phạt cụ thể.
- **Phụ:** người học thi GPLX, hỏi về quy tắc và biển báo.

### 2.3 Thuật ngữ
| Thuật ngữ | Nghĩa |
|---|---|
| Văn bản | Văn bản quy phạm pháp luật (Luật, Nghị định, Thông tư, Quy chuẩn) hoặc văn bản hợp nhất |
| Đoạn luật | Đơn vị tìm kiếm: một Khoản kèm tiêu đề Điều và tên văn bản (có thể cắt tới Điểm nếu EDA cho thấy Khoản quá dài) |
| Hiệu lực | Khoảng `[valid_from, valid_to)` mà một đoạn luật được áp dụng; `valid_to` rỗng nghĩa là còn hiệu lực |
| Căn cứ | Đoạn luật còn hiệu lực mà câu trả lời dựa vào |
| Luật cũ | Văn bản hoặc đoạn luật đã hết hiệu lực tại thời điểm hỏi |
| Ngày chốt T | Ngày dừng cập nhật dữ liệu: **01/10/2026** |

### 2.4 Phát biểu hình thức
- Đầu vào: câu hỏi `q`, thời điểm hỏi `t` (mặc định là ngày chốt T).
- Kho tri thức `K` gồm các đoạn luật có khoảng hiệu lực; `K_t = { d ∈ K : valid_from(d) ≤ t < valid_to(d) }`.
- Tìm kiếm: chọn `E ⊂ K_t`, `|E| ≤ k`, gồm các đoạn liên quan nhất tới `q`.
- Sinh: từ `(q, E)` sinh câu trả lời `a` kèm trích dẫn `C ⊆ E`.
- Từ chối: nếu `E` không chứa căn cứ cho `q` thì `a` là câu từ chối và `C = ∅`.

### 2.5 Phạm vi

**Chủ đề (khoảng 25–30 văn bản):**
| Tình huống | Nhóm văn bản |
|---|---|
| Quy tắc đi đường, biển báo | Luật 36/2024, QCVN 41:2024, TT 38/2024 (tốc độ) |
| Bằng lái | Luật 36/2024, TT 12/2025/TT-BCA, TT 65/2024/TT-BCA, TT về sức khỏe người lái xe |
| Đăng ký xe, biển số | TT 79/2024/TT-BCA, TT 37/2026/TT-BCA, NĐ 39/2023 |
| Lệ phí | TT 155/2025/TT-BTC, NĐ 10/2022 và các NĐ sửa đổi |
| Đăng kiểm | TT 30/2026/TT-BXD |
| Bảo hiểm | NĐ 67/2023, NĐ 220/2026 |
| Xử phạt | NĐ 168/2024, NĐ 238/2026, NĐ 336/2025 |
| Nộp phạt, giữ xe | Luật Xử lý vi phạm hành chính (VBHN 63/VBHN-VPQH), văn bản về tạm giữ phương tiện |
| Tai nạn | Bộ luật Hình sự (chỉ Điều 260 và Điều liên quan), Bộ luật Dân sự (chỉ các Điều về bồi thường thiệt hại do nguồn nguy hiểm cao độ) |
| Hạ tầng đường bộ | Luật 35/2024, NĐ 165/2024 |

**Chiều thời gian:**
| Mức | Nội dung |
|---|---|
| Yêu cầu chính | Trả lời theo luật hiện hành tại ngày chốt T |
| Lưu trữ | Giữ cả bản cũ và bản mới của các đoạn bị sửa, kèm `valid_from`/`valid_to` và quan hệ sửa đổi |
| Mở rộng (nếu còn sức) | Hỏi theo mốc thời gian từ 01/01/2025, lấy `t` từ câu hỏi |
| Không hỗ trợ | Luật trước 2025 (NĐ 100/2019, Luật GTĐB 2008…); không trích các văn bản này |

**Hình thức:** câu hỏi tiếng Việt dạng chữ (kể cả viết tắt, không dấu); mỗi câu trả lời độc lập; câu trả lời có trích dẫn, kèm đoạn luật gốc và cảnh báo "chỉ mang tính tham khảo".

### 2.6 Ngoài phạm vi
| Không làm | Hệ thống xử lý khi bị hỏi |
|---|---|
| Đường thủy, đường sắt, hàng không | Từ chối, nói rõ ngoài phạm vi |
| Tư vấn vụ việc cụ thể | Đưa căn cứ chung, khuyên liên hệ cơ quan chức năng hoặc luật sư |
| Quy định riêng của địa phương | Từ chối |
| Luật trước 2025, bản dự thảo | Không trích; nói rõ chỉ hỗ trợ luật hiện hành |
| Câu hỏi bằng ảnh, giọng nói | Không hỗ trợ |
| Hỏi đáp nhiều lượt | Không hỗ trợ |

### 2.7 Yêu cầu chức năng
| Mã | Hệ thống phải |
|---|---|
| F1 | Nhận câu hỏi tiếng Việt, kể cả viết tắt và không dấu |
| F2 | Chỉ dùng đoạn luật còn hiệu lực tại thời điểm hỏi |
| F3 | Trả lời kèm trích dẫn (văn bản, Điều, Khoản, Điểm) |
| F4 | Hiển thị đoạn luật gốc |
| F5 | Từ chối khi không có căn cứ hoặc câu hỏi ngoài phạm vi |
| F6 | Hiển thị cảnh báo "Thông tin chỉ mang tính tham khảo" |

### 2.8 Yêu cầu phi chức năng
| Mã | Yêu cầu |
|---|---|
| N1 | Demo chạy trên laptop không có GPU NVIDIA (Ryzen 7 8845H, 31 GB RAM), không cần internet |
| N2 | Thời gian trả lời dưới 40 giây với mô hình 9B, dưới 10 giây với mô hình nhỏ (mục tiêu, đo thực tế khi demo) |
| N3 | Cập nhật luật mới không cần train lại mô hình |
| N4 | Tái lập được: cố định seed, ghi phiên bản thư viện, công khai dữ liệu đã xử lý và adapter |

---

## 3. Câu hỏi nghiên cứu, giả thuyết, đóng góp

| Mã | Câu hỏi nghiên cứu | Giả thuyết |
|---|---|---|
| RQ1 | RAG và fine-tune LoRA đóng góp bao nhiêu vào chất lượng câu trả lời; kết hợp có tốt hơn không? (cấu hình A/B/C/D) | H1: RAG tăng độ đúng nhiều hơn fine-tune; fine-tune tăng độ giống văn phong đáp án nhiều hơn; D tốt nhất |
| RQ2 | Cách cắt đoạn và cách tìm kiếm nào cho Recall@k cao nhất? | H2: cắt theo Khoản tốt hơn theo Điều; hybrid + reranker tốt nhất, chênh rõ nhất ở câu hỏi đời thường |
| RQ3 | Khi một quy định bị sửa đổi, hệ thống có trả lời theo quy định mới không; lọc hiệu lực giúp bao nhiêu? | H3: không RAG (A, C) phần lớn trả lời theo luật cũ; D có lọc hiệu lực phần lớn trả lời theo luật mới |
| RQ4 | Mô hình 9B hơn mô hình nhỏ (2–4B) bao nhiêu, có đáng với chi phí chạy chậm hơn không? | H4: có RAG thì khoảng cách thu hẹp; mô hình nhỏ kém rõ nhất ở câu cần phân biệt các Khoản gần giống nhau |

Căn cứ giả thuyết từ dự án cũ: RAG +0,21 LLM-Judge, fine-tune +0,04; ROUGE-L thì fine-tune hơn; cắt theo Khoản đạt recall 0,81 so với 0,525 khi cắt theo Điều.

**Cấu hình E (tùy chọn):** một mô hình thương mại trả lời cùng bộ eval, chỉ làm mốc đối chiếu trong RQ1, không phải sản phẩm.

**Đóng góp:**
1. Bộ dữ liệu pháp luật cho người tham gia giao thông đường bộ (25–30 văn bản), tách tới Điều/Khoản/Điểm, có ngày hiệu lực và quan hệ sửa đổi.
2. Bộ đánh giá có nhãn tới Điều/Khoản/mức phạt, gồm câu viết tay, biến thể đời thường, câu về quy định đã sửa, câu ngoài phạm vi, và đề GPLX.
3. Hệ thống hỏi đáp chạy cục bộ: RAG lọc theo hiệu lực, kết hợp mô hình fine-tune LoRA.
4. Đánh giá thực nghiệm trả lời RQ1–RQ4, kèm phân tích lỗi.

---

## 4. Hướng tiếp cận kỹ thuật

### 4.1 Kiến trúc
```
Câu hỏi ─► Tìm kiếm (BM25 + vector, gộp RRF, reranker, lọc hiệu lực) ─► top-k đoạn luật
        ─► Ghép prompt (cùng định dạng lúc fine-tune) ─► LLM đã fine-tune ─► câu trả lời + trích dẫn
```

### 4.2 Thành phần
| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| Lưu trữ | PostgreSQL + pgvector | Bảng `van_ban`, `doan_luat`, `sua_doi` (thêm `tham_chieu` nếu làm đồ thị tham chiếu) |
| Cắt đoạn | Theo Khoản, gắn tiêu đề Điều và tên văn bản vào đầu đoạn | Cắt tới Điểm nếu EDA cho thấy cần |
| Embedding | bge-m3 hoặc tương đương đa ngôn ngữ | Chạy CPU được |
| Tìm kiếm | BM25 (rank-bm25, tách từ tiếng Việt) + vector, gộp RRF, reranker cross-encoder | Lọc theo `valid_from`/`valid_to` |
| LLM chính | Qwen3.5-9B, QLoRA bằng Unsloth | Train trên Kaggle (chính) hoặc Colab |
| LLM phụ | Bản nhỏ cùng họ Qwen3.5 (2–4B) | Dùng để phát triển nhanh, cho RQ4, demo dự phòng |
| Demo | Xuất GGUF, chạy bằng Ollama; giao diện Gradio tại `localhost:7860` | Dự phòng: Gradio trên Colab với `share=True`; quay video trước |

### 4.3 Nâng cấp RAG (chỉ thêm khi phân tích lỗi cho thấy cần)
1. Viết lại câu hỏi (đời thường → ngôn ngữ luật).
2. Đồ thị tham chiếu và quan hệ sửa đổi giữa các đoạn luật.

### 4.4 Quy trình chạy giữa laptop và Kaggle
- Laptop: thu thập, xử lý, EDA, xây kho tra cứu, chạy tìm kiếm cho bộ eval và xuất `test_with_context.jsonl`, chấm điểm, demo.
- Kaggle: sinh dữ liệu train (nếu dùng LLM cục bộ), fine-tune, sinh câu trả lời cho các cấu hình.

---

## 5. Dữ liệu

### 5.1 Các loại dữ liệu
| # | Dữ liệu | Nguồn | Cách có |
|---|---|---|---|
| ① | Văn bản luật (~25–30, giữ bản cũ và bản mới) | vbpl.vn (chính), congbao.chinhphu.vn, văn bản hợp nhất; thuvienphapluat/luatvietnam chỉ để đối chiếu | Thu thập |
| ② | Đề GPLX 600 câu (2025, căn cứ TT 12/2025/TT-BCA), chỉ dùng câu thuần chữ | Bản PDF chính thức của Cục CSGT | Thu thập |
| ③ | Bộ eval | Nhóm tự viết từ ① | Xây dựng sau EDA |
| ④ | Dữ liệu train (~2.000 cặp hỏi đáp) | LLM sinh từ ① | Xây dựng sau ③ |

Không thu thập câu hỏi thật của người dân. Thay bằng bộ biến thể đời thường do nhóm viết (mục 5.6).

### 5.2 Danh sách văn bản cần thu thập
Ký hiệu ⚠️: số hiệu hoặc phạm vi phải xác minh khi thu thập.

| # | doc_id | Văn bản | Ghi chú |
|---|---|---|---|
| 1 | `luat_35_2024` | Luật Đường bộ 35/2024/QH15 | |
| 2 | `luat_36_2024` | Luật Trật tự, ATGT đường bộ 36/2024/QH15 | |
| 3 | `luat_118_2025` | Luật 118/2025/QH15 | Chỉ các Điều sửa Luật 35 và 36 |
| 4 | `nd_168_2024` | NĐ 168/2024/NĐ-CP | Bản gốc |
| 5 | `nd_238_2026` | NĐ 238/2026/NĐ-CP | Sửa NĐ 168, hiệu lực 15/8/2026 |
| 6 | `nd_336_2025` | NĐ 336/2025/NĐ-CP | Kiểm tra sửa đổi |
| 7 | `nd_165_2024` | NĐ 165/2024/NĐ-CP | Kiểm tra sửa đổi |
| 8 | `nd_158_2024` | NĐ 158/2024/NĐ-CP | Kiểm tra sửa đổi |
| 9 | `tt_38_2024_bgtvt` | TT 38/2024/TT-BGTVT (tốc độ, khoảng cách) | |
| 10 | `qcvn_41_2024` | QCVN 41:2024/BGTVT | |
| 11 | `tt_12_2025_bca` | TT 12/2025/TT-BCA (sát hạch, cấp GPLX) | |
| 12 | `tt_65_2024_bca` | TT 65/2024/TT-BCA | |
| 13 | `tt_suckhoe_byt` ⚠️ | TT của Bộ Y tế về sức khỏe người lái xe | Bản chính thức, không lấy dự thảo |
| 14 | `tt_79_2024_bca` | TT 79/2024/TT-BCA (đăng ký xe) | |
| 15 | `tt_37_2026_bca` | TT 37/2026/TT-BCA | Sửa TT 79, hiệu lực 08/6/2026 |
| 16 | `nd_39_2023` | NĐ 39/2023/NĐ-CP (đấu giá biển số) | |
| 17 | `tt_155_2025_btc` | TT 155/2025/TT-BTC (lệ phí đăng ký, cấp biển) | Thay TT 60/2023 |
| 18 | `nd_10_2022` | NĐ 10/2022/NĐ-CP (lệ phí trước bạ) | |
| 19 | `nd_51_2025` ⚠️ | NĐ sửa NĐ 10/2022 | Kiểm tra thêm NĐ 175/2025 |
| 20 | `tt_30_2026_bxd` | TT 30/2026/TT-BXD (kiểm định xe cơ giới) | Hiệu lực 01/7/2026 |
| 21 | `nd_67_2023` | NĐ 67/2023/NĐ-CP (bảo hiểm bắt buộc) | Phần xe cơ giới |
| 22 | `nd_220_2026` | NĐ 220/2026/NĐ-CP | Sửa NĐ 67, hiệu lực 01/7/2026 |
| 23 | `vbhn_63_2025_xlvphc` | VBHN 63/VBHN-VPQH Luật Xử lý vi phạm hành chính | |
| 24 | ⚠️ | Văn bản về tạm giữ tang vật, phương tiện vi phạm hành chính | Tra số hiệu hiện hành |
| 25 | `blhs_2015` ⚠️ | Bộ luật Hình sự (bản hợp nhất mới nhất) | Chỉ Điều 260 và Điều liên quan |
| 26 | `blds_2015` ⚠️ | Bộ luật Dân sự | Chỉ các Điều về bồi thường do nguồn nguy hiểm cao độ |
| 27 | `gplx_600_2025` | Bộ 600 câu hỏi sát hạch (Cục CSGT, 2025) | PDF kèm đáp án |

Với mỗi văn bản, xem mục văn bản liên quan trên vbpl.vn để phát hiện văn bản sửa đổi hoặc thay thế chưa có trong danh sách.

### 5.3 Thu thập và lưu dữ liệu thô
- Tải thủ công (hoặc agent tải sau khi người dùng duyệt danh sách file, nguồn, dung lượng). Ưu tiên `.docx`, không có thì `.pdf`; có cả hai thì giữ cả hai.
- Kiểm tra mỗi file: đúng số hiệu; là bản chính thức (không có số hiệu hoặc ngày bỏ trống, không có chữ "DỰ THẢO"); tình trạng hiệu lực; toàn văn đủ phụ lục; ghi văn bản sửa đổi và bị sửa đổi.
- Đặt tên `<loại>_<số>_<năm>[_<cơ quan>].<đuôi>`, viết thường, không dấu.
- Cấu trúc:
```
data/
├── raw/            # file gốc, không bao giờ sửa
│   ├── legal/
│   └── gplx/
├── interim/
├── processed/
├── manifest.csv
└── COLLECTION_LOG.md   # nhật ký thu thập
```
- Cột `manifest.csv`: `doc_id, so_hieu, ten, loai, co_quan, ngay_ban_hanh, ngay_hieu_luc, tinh_trang, sua_doi_van_ban, bi_sua_doi_boi, pham_vi_lay, chu_de, nguon_url, file, sha256, ngay_tai, nguoi_tai, ghi_chu`.
- Git: commit `manifest.csv` và `.docx` nếu tổng dung lượng nhỏ (dưới khoảng 50 MB); PDF lớn để trên Google Drive hoặc Hugging Face Datasets, ghi link trong README.

### 5.4 Xử lý văn bản luật
1. Trích chữ: `.docx` bằng python-docx, `.html` bằng BeautifulSoup, PDF có lớp chữ bằng pymupdf; tránh OCR nếu có định dạng khác.
2. Làm sạch: xóa header Công báo và số trang, nối dòng bị ngắt, chuẩn hóa Unicode NFC, bỏ phần nơi nhận và chữ ký, chuyển bảng thành câu chữ, giữ phụ lục có nội dung pháp lý. Ghi số liệu trước/sau từng bước.
3. Tách cấu trúc Phần → Chương → Mục → Điều → Khoản → Điểm.
4. Gắn hiệu lực và sửa đổi: tìm chỉ dẫn "Sửa đổi…", "Bổ sung…", "Bãi bỏ…" bằng regex để gợi ý, người kiểm tra từng chỉ dẫn; đoạn cũ nhận `valid_to`, đoạn mới nhận `valid_from`; ghi bảng `sua_doi`. Đối chiếu với văn bản hợp nhất nếu có.
5. Kiểm tra: số Điều liên tục, không sót header, mọi đoạn có ngày hiệu lực, so ngẫu nhiên khoảng 30 đoạn với bản gốc.
6. Nạp PostgreSQL.

### 5.5 Xử lý đề GPLX
Đọc PDF thành câu hỏi, lựa chọn, đáp án; loại câu có hình; đánh dấu câu không còn khớp luật hiện hành (đề ban hành 2025, một số quy định đã sửa năm 2026).

### 5.6 Bộ eval (xây trước dữ liệu train, sau đó đóng băng)
| Bộ | Số lượng | Nguồn |
|---|---|---|
| Thủ công (chính) | ~150 | Nhóm viết theo ma trận đề lập từ EDA |
| Biến thể đời thường | ~150 | Nhóm viết lại câu thủ công theo kiểu viết tắt, không dấu, kể chuyện; dùng chung đáp án và nhãn |
| Luật sửa đổi (RQ3) | 40–50 | Nhóm viết về các đoạn đã bị sửa; mỗi câu có đáp án theo bản cũ và bản mới |
| Giả định cũ | nằm trong hai bộ trên | Câu chứa con số hoặc khái niệm của luật cũ; đáp án phải đính chính |
| Ngoài phạm vi | 20–30 | Nhóm viết; đáp án là từ chối |
| GPLX trắc nghiệm | các câu thuần chữ | Đề chính thức |

Nhãn mỗi câu tự luận: `cau_hoi, dap_an, van_ban, dieu, khoan, diem, muc_phat_min, muc_phat_max, diem_tru, chu_de, loai_bo (thu_cong/doi_thuong/sua_doi/ngoai_pham_vi), id_cau_goc, gia_dinh_cu, ngay_dung`.

Quy trình: ma trận đề → viết → kiểm tra chéo bởi người thứ hai → đóng băng `eval_v1` kèm ngày. Sửa sau khi đóng băng phải tạo phiên bản mới và chấm lại mọi cấu hình.

### 5.7 Dữ liệu train
1. Chỉ sinh từ đoạn luật còn hiệu lực.
2. LLM sinh 1–3 cặp hỏi đáp mỗi đoạn, 7 loại câu (chung, định nghĩa, mức phạt, thủ tục, hành vi cấm, tình huống, đời thường).
3. Thêm mẫu từ chối và mẫu ngữ cảnh gây nhiễu (đoạn gần giống nhưng sai).
4. Lọc: câu trả lời trùng ít với đoạn luật, nhắc luật cũ, quá dài, câu hỏi theo mẫu, trùng lặp.
5. Kiểm tra tay ngẫu nhiên khoảng 100 câu.
6. Loại câu gần giống câu trong bộ eval.

### 5.8 Chia dữ liệu
| Dữ liệu | Chia | Dùng cho |
|---|---|---|
| ① Văn bản luật | Không chia | Kho tra cứu |
| ④ Dữ liệu train | train ~80% / dev ~10% / test-gen ~10%, chia theo nhóm (văn bản, Điều) | Fine-tune; test-gen chỉ để kiểm tra nhanh |
| ③ Bộ eval | Không chia, đóng băng | Chấm điểm cuối |

- Không loại các Điều có trong bộ eval khỏi dữ liệu train; gắn nhãn mỗi câu eval là Điều đã gặp hay chưa gặp trong train, và báo cáo kết quả tách hai nhóm.
- train dùng để học; dev dùng để chỉnh (checkpoint, tham số, prompt); eval chỉ dùng để chấm cuối.

---

## 6. EDA
Nguyên tắc: mỗi phân tích phải dẫn tới phát hiện và quyết định; ghi bảng "phát hiện → hành động".

**A. Kho văn bản luật:** quy mô theo văn bản và chủ đề; độ dài đoạn theo số từ và số token của tokenizer Qwen; đoạn dài hoặc ngắn bất thường; phân bố mức phạt theo loại xe và hành vi, điểm GPLX bị trừ; số đoạn bị sửa, bổ sung, bãi bỏ; dòng thời gian hiệu lực; từ vựng sau khi tách từ (underthesea hoặc pyvi); đoạn gần trùng giữa các văn bản; số tham chiếu chéo; kiểm tra chất lượng.

**B. Đề GPLX:** số câu theo chương và số câu có hình bị loại; số lựa chọn mỗi câu để tính mức đoán mò; câu không còn khớp luật hiện hành.

**C. Dữ liệu train (sau khi sinh):** số câu bị loại theo lý do; phân bố loại câu, chủ đề, văn bản so với ma trận đề; độ dài câu hỏi và câu trả lời; mức trùng từ giữa câu hỏi và đoạn luật; mức gần giống giữa câu train và câu eval.

Phát hiện sơ bộ trên 12 văn bản cũ (cách cắt đơn giản, chỉ minh họa): 2.701 đoạn, trung vị 85 từ, 95% đoạn ≤ 394 từ, 16 đoạn trên 1.000 từ (dài nhất 5.928 từ, trong QCVN 41); NĐ 168 có 187 khung phạt tiền từ 100.000đ tới 75.000.000đ.

Đầu ra: notebook EDA, bảng phát hiện → hành động, ma trận đề cho bộ eval.

---

## 7. Đánh giá

### 7.1 Chỉ số và tiêu chí thành công
| Đo | Chỉ số | Mục tiêu |
|---|---|---|
| Tìm kiếm (RQ2) | Recall@5 đúng văn bản | ≥ 0,90 |
| | Recall@5 đúng Khoản | ≥ 0,75 |
| Câu trả lời (RQ1) | LLM-Judge thang 1–5 chuẩn hóa [0,1]; ROUGE-L; BERTScore; chấm tay 50 câu | D cao hơn A ít nhất 0,25 LLM-Judge |
| Mức phạt | Độ đúng khoảng mức phạt trên câu hỏi về phạt | ≥ 80% |
| Luật cũ | Tỷ lệ câu trả lời trích luật cũ hoặc dự thảo | ≤ 2% |
| Từ chối | Tỷ lệ từ chối đúng trên bộ ngoài phạm vi; tỷ lệ từ chối sai trên câu trong phạm vi | Báo cáo cả hai |
| RQ3 | Tỷ lệ trả lời theo bản mới trên bộ luật sửa đổi | D ≥ 80% |
| RQ4 | Chênh lệch chỉ số và thời gian trả lời giữa 9B và bản nhỏ | Báo cáo |
| GPLX | Độ chính xác trắc nghiệm, so với mức đoán mò | Báo cáo |

Các mục tiêu là đề xuất ban đầu, đặt trước khi chạy thực nghiệm.

### 7.2 Quy trình đánh giá
- Mọi cấu hình chấm trên cùng `eval_v1`; B và D dùng cùng một file ngữ cảnh đã tìm sẵn.
- Sinh bằng greedy decoding; cố định seed.
- LLM-Judge dùng một mô hình bên ngoài cố định; chấm tay bởi hai người độc lập để đối chiếu.
- Báo cáo kết quả tách theo: loại câu, chủ đề, câu chuẩn so với biến thể đời thường, Điều đã gặp so với chưa gặp trong train.

### 7.3 Ablation
Bỏ BM25; bỏ vector; bỏ reranker; bỏ lọc hiệu lực; cắt theo Điều thay vì theo Khoản; bỏ gắn tiêu đề đoạn.

---

## 8. Giả định, ràng buộc, rủi ro

**Giả định:** văn bản từ nguồn chính thức là chính xác; câu hỏi do LLM sinh đủ đa dạng để huấn luyện; người dùng hỏi tiếng Việt, mỗi lần một câu.

**Ràng buộc:** chỉ có GPU T4 miễn phí (Kaggle, Colab); laptop không có GPU NVIDIA; chỉ dùng dữ liệu công khai.

**Rủi ro dự án:**
| Rủi ro | Xử lý |
|---|---|
| Luật bị sửa trong lúc làm | Chốt ngày T, ghi rõ trong báo cáo |
| LLM sinh dữ liệu train sai | Lọc tự động, kiểm tra tay ngẫu nhiên |
| Hết quota GPU | Colab dự phòng; phát triển bằng mô hình nhỏ trước |
| Mô hình 9B quá chậm trên laptop | Demo bằng bản nhỏ hoặc trên Colab; video quay trước |
| Gắn quan hệ sửa đổi sai | Gợi ý bằng regex, người kiểm tra, đối chiếu văn bản hợp nhất |

**Rủi ro với tính đúng đắn của kết quả:** lộ đề (xử lý: chia theo Điều, kiểm tra gần trùng, báo cáo đã gặp/chưa gặp); bộ eval nhỏ (xử lý: khoảng tin cậy bootstrap); LLM-Judge thiên vị (xử lý: chấm tay đối chiếu); câu đời thường do nhóm viết chưa hẳn giống người thật (ghi vào hạn chế); đáp án chuẩn do nhóm viết có thể sai (xử lý: trích dẫn bắt buộc, kiểm tra chéo).

**Pháp lý và đạo đức:** văn bản quy phạm pháp luật không thuộc đối tượng bảo hộ quyền tác giả; câu trả lời luôn kèm trích dẫn, đoạn luật gốc và cảnh báo "chỉ mang tính tham khảo"; hệ thống từ chối khi không có căn cứ; báo cáo ghi rõ phần có AI hỗ trợ.

---

## 9. Tái lập và duy trì
- Cố định seed; ghi phiên bản thư viện; lưu dữ liệu đã xử lý, bộ eval và adapter trên Hugging Face; README hướng dẫn chạy từng bước.
- Khi luật thay đổi: thêm văn bản, cập nhật bảng `sua_doi`, xây lại kho tra cứu; không cần train lại mô hình.

---

## 10. Các giai đoạn và sản phẩm

| Giai đoạn | Bước | Sản phẩm | Báo cáo |
|---|---|---|---|
| 1. Khởi động | Chuẩn bị nhóm; xác định bài toán (tài liệu này) | Đề xuất | Report 1 |
| 2. Dữ liệu | Thu thập → xử lý → EDA → bộ eval → dữ liệu train → chia tập | Dữ liệu sạch, ERD, notebook EDA, `eval_v1` | Report 2 |
| 3. Xây hệ thống | RAG + RQ2 (laptop); fine-tune (Kaggle) | Kho tra cứu, adapter LoRA | |
| 4. Đánh giá | RQ1, RQ3, RQ4; phân tích lỗi; cải tiến nếu cần | Bảng kết quả, phân tích lỗi | Report 3 |
| 5. Demo | GGUF + Ollama + Gradio | Chatbot cục bộ, video | |
| 6. Bàn giao | Báo cáo cuối, slide, code, dữ liệu, adapter | | Report 4 |

---

## 11. Quyết định đã chốt và câu hỏi còn mở

**Đã chốt:** người dùng chính là người dân, phụ là người học GPLX; phạm vi mở rộng 25–30 văn bản; ngày chốt T = 01/10/2026; yêu cầu chính là luật hiện hành, mở rộng hỏi theo mốc từ 2025; giữ bản cũ và mới; không thu thập câu hỏi người dân, thay bằng biến thể đời thường; PostgreSQL + pgvector; Qwen3.5-9B làm chính, bản nhỏ làm phụ; fine-tune trên Kaggle; demo cục bộ; repo mới tại `DAT301_NEW/traffic-law-qa`.

**Còn mở:**
1. Giữ đủ RQ1–RQ4 hay bỏ RQ4.
2. Có làm cấu hình E và khảo sát sơ bộ (mục 1.3) không.
3. Kích thước cụ thể của mô hình phụ (chọn khi bắt đầu fine-tune, tùy bản có trên Hugging Face và được Unsloth hỗ trợ).
4. Số hiệu cụ thể của các mục ⚠️ trong danh sách văn bản (xác minh khi thu thập).
5. Mẫu báo cáo của giảng viên (nếu có thì theo mẫu đó).
