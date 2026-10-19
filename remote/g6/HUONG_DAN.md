# Train G6 (QLoRA Qwen3.5-9B) trên máy thuê

Hai file cần chép lên máy (ở `remote/g6/`):

- `g6_bundle.zip`: dữ liệu chat `train-v1` (1.662 train, 192 dev), `MANIFEST.json`, script `scripts/g6_train.py`.
  Tạo lại bằng `py -3.13 scripts/build_g6_bundle.py`.
- `setup_g6.sh`: cài đặt, chạy thử, chạy thật, xem tiến độ, nén kết quả.

Máy cần: GPU NVIDIA ≥ 16 GB (đã nhắm RTX 5060 Ti 16 GB), Ubuntu, khoảng 40 GB ổ trống, có Internet.

## Các bước

Trong PowerShell trên máy bạn, thay `<IP>`, `<CỔNG>`, `<USER>` bằng thông tin trang thuê cấp.

1. **Chép file lên** (đứng ở thư mục `remote/g6`):
   ```bash
   scp -P <CỔNG> g6_bundle.zip setup_g6.sh <USER>@<IP>:~/
   ```
2. **Vào máy:**
   ```bash
   ssh -p <CỔNG> <USER>@<IP>
   ```
3. **Cài đặt và chạy thử** (khoảng 20–30 phút: cài thư viện, tải mô hình khoảng 19 GB, chạy thử 12 bước):
   ```bash
   bash ~/setup_g6.sh
   ```
   Cuối cùng phải thấy `>> XONG` và dòng `>> ƯỚC TÍNH chạy đầy đủ: khoảng … giờ`. Nếu báo lỗi, gửi file
   `~/g6/smoke.log`, chưa chạy bước 4.
4. **Train thật** (chạy nền, tắt cửa sổ SSH hay mất mạng vẫn chạy tiếp):
   ```bash
   bash ~/setup_g6.sh full
   ```
5. **Xem tiến độ** (SSH vào lại bất cứ lúc nào):
   ```bash
   bash ~/setup_g6.sh status
   ```
   Dòng `[120/416] {...} | còn khoảng 95 phút` cho biết bước hiện tại, tổng số bước và thời gian còn lại.
6. **Nếu tiến trình bị ngắt** (máy khởi động lại, hết điểm…), chạy tiếp từ checkpoint gần nhất:
   ```bash
   bash ~/setup_g6.sh resume
   ```
7. **Xong thì nén kết quả** (khi `status` báo `XONG`):
   ```bash
   bash ~/setup_g6.sh pack
   ```
8. **Tải về máy bạn** (PowerShell trên máy bạn):
   ```bash
   scp -P <CỔNG> <USER>@<IP>:~/g6_ketqua.zip .
   ```
9. **Tắt hoặc trả máy** trên trang thuê, để không bị trừ điểm tiếp.

## Trong `g6_ketqua.zip`

| File | Nội dung |
|---|---|
| `out_g6/adapter/` | Adapter LoRA tốt nhất (loss dev thấp nhất), dùng cho G7 |
| `out_g6/g6_results.json` | Môi trường, cấu hình, thời gian, VRAM, checkpoint tốt nhất, loss dev theo loại câu |
| `out_g6/train_log.jsonl` | Log từng bước: loss, learning rate, grad norm, loss dev |
| `out_g6/plots/*.png` | Biểu đồ loss train/dev, learning rate, grad norm, độ dài mẫu, loss dev theo loại câu |
| `out_g6/dev_answers.jsonl` | 12 câu dev: câu trả lời của mô hình gốc và mô hình đã train |
| `out_g6/dev_loss_per_sample.jsonl` | Loss của từng câu dev, gốc và đã train |
| `out_g6/train.log`, `smoke.log` | Toàn bộ log |

## Nếu có lỗi

- `torch không thấy GPU` hoặc `bản torch này không có mã cho sm_120`: bản torch không hợp card RTX 50. Chạy
  `source ~/g6/.venv/bin/activate && pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128`
  rồi chạy lại `bash ~/setup_g6.sh`.
- `Thiếu python3-venv`: `sudo apt install -y python3-venv`, chạy lại.
- `CUDA out of memory` khi chạy thử: gửi `smoke.log`.
- Lỗi khác: gửi `~/g6/smoke.log` (khi chạy thử) hoặc `~/g6/train.log` (khi train thật).
