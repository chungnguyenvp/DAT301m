"""G8: LLM-Judge chấm nội dung câu trả lời G7 (rubric mục 3 và 5 của `data/eval/README.md`) qua Message Batches API.

    py -3.13 scripts/g8_judge.py prepare     # dựng yêu cầu, in một prompt mẫu và ước tính số token; không gọi API
    py -3.13 scripts/g8_judge.py submit      # gửi batch (cần `pip install anthropic` và ANTHROPIC_API_KEY)
    py -3.13 scripts/g8_judge.py collect     # đợi batch xong, ghi reports/g8/judge.jsonl
    py -3.13 scripts/g8_judge.py score       # tổng hợp: tỷ lệ đạt theo lượt/nhóm, CI95, so với bảng chấm tay

Chấm các câu **test** của lượt A, B, C, D và hai lượt bỏ lọc (khoảng 1.030 câu). Giám khảo: `claude-opus-5-5`
(thinking luôn bật, effort `medium`), đầu ra JSON theo schema cố định. Batch rẻ hơn 50% so với gọi thường; tham số
`fallbacks` không dùng được trên Batches API, nên câu bị từ chối (`stop_reason = refusal`) được ghi lại để chấm tay.

Giám khảo chỉ thấy câu hỏi, ngày hỏi, đáp án chuẩn (kèm đáp án cũ với câu sửa đổi) và câu trả lời; không biết câu
trả lời đến từ lượt nào.
"""

import csv
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402

OUT = config.ROOT / "reports" / "g8"
MODEL = "claude-opus-5-5"
RUNS = ["A", "B", "C", "D", "B_boloc", "D_boloc"]
MAX_TOKENS = 4000          # thinking tính vào max_tokens
SYSTEM = """Bạn là giám khảo chấm câu trả lời hỏi đáp pháp luật giao thông đường bộ Việt Nam.

Bạn nhận: câu hỏi, ngày hỏi, ĐÁP ÁN CHUẨN (đúng theo luật có hiệu lực tại ngày hỏi) và CÂU TRẢ LỜI cần chấm. Chỉ dựa
vào đáp án chuẩn để chấm, không dùng hiểu biết riêng về luật để thêm hay bớt yêu cầu.

Câu hỏi trong phạm vi (có đáp án chuẩn nêu quy định):
- ĐẠT khi câu trả lời nêu đủ các ý chính của đáp án chuẩn: hành vi hoặc thủ tục được hỏi, mọi số liệu (số tiền, số
  điểm trừ, thời hạn, ngưỡng, đơn vị như "ngày làm việc"), chủ thể và điều kiện quan trọng; và không thêm chế tài hay
  quy định trái với đáp án chuẩn. Diễn đạt khác, thứ tự khác, trích dẫn điều khoản ít hơn đều không làm mất điểm. Phần
  "ghi chú" nếu có chỉ là lưu ý cho giám khảo, không phải ý bắt buộc.
- KHÔNG ĐẠT khi thiếu một ý chính, sai một số liệu, nêu chế tài sai (ví dụ nói có trừ điểm khi đáp án nói không),
  trả lời theo quy định cũ, hoặc từ chối trả lời.

Câu hỏi ngoài phạm vi (đáp án chuẩn nói hệ thống phải từ chối):
- ĐẠT khi câu trả lời nói rõ không có căn cứ hoặc ngoài phạm vi và không bịa quy định. Nếu đáp án chuẩn nói văn bản đã
  hết hiệu lực, nêu điều đó (kèm quy định hiện hành) cũng đạt.
- KHÔNG ĐẠT khi câu trả lời đưa ra quy định, mức phạt hay thủ tục như thể có căn cứ.

Câu sửa đổi có thêm ĐÁP ÁN CŨ (quy định trước khi sửa): đánh dấu `theo_luat_cu` = true nếu câu trả lời nêu nội dung
của đáp án cũ thay cho đáp án chuẩn.

Trả lời đúng theo schema JSON: `dat` (true/false), `y_thieu_hoac_sai` (danh sách ngắn các ý thiếu hoặc sai, rỗng nếu
đạt), `che_tai_sai` (true nếu nêu chế tài trái đáp án), `theo_luat_cu` (true/false), `ly_do` (một hai câu tiếng Việt)."""
SCHEMA = {
    "type": "object",
    "properties": {
        "dat": {"type": "boolean"},
        "y_thieu_hoac_sai": {"type": "array", "items": {"type": "string"}},
        "che_tai_sai": {"type": "boolean"},
        "theo_luat_cu": {"type": "boolean"},
        "ly_do": {"type": "string"},
    },
    "required": ["dat", "y_thieu_hoac_sai", "che_tai_sai", "theo_luat_cu", "ly_do"],
    "additionalProperties": False,
}


def uid(x: dict) -> str:
    return f"{x['nhom_cau']}/{x['key']}"


def user_text(item: dict, answer: str) -> str:
    parts = [f"Câu hỏi: {item['cau_hoi']}", f"Ngày hỏi: {item['ngay_hoi']}",
             f"Loại: {'ngoài phạm vi (phải từ chối)' if item['nhom_cau'] == 'ngoai_pham_vi' else 'trong phạm vi'}",
             f"ĐÁP ÁN CHUẨN:\n{item['dap_an']}"]
    if item.get("ghi_chu"):
        parts.append(f"Ghi chú cho giám khảo: {item['ghi_chu']}")
    if item.get("dap_an_cu"):
        parts.append(f"ĐÁP ÁN CŨ (trước ngày {item['ngay_hoi']}, không còn đúng):\n{item['dap_an_cu']}")
    parts.append(f"CÂU TRẢ LỜI CẦN CHẤM:\n{answer.strip() or '(trống)'}")
    return "\n\n".join(parts)


def jobs() -> list[tuple[str, dict, str]]:
    items = {uid(x): x for x in evalset.load_eval()}
    answers = [json.loads(line) for line in open(config.ROOT / "kaggle" / "g7" / "out_g7" / "g7_answers.jsonl",
                                                 encoding="utf-8")]
    out = [(f"{r['run']}|{r['uid']}", items[r["uid"]], r["tra_loi"]) for r in answers
           if r["run"] in RUNS and items[r["uid"]]["tap"] == "test"]
    return sorted(out, key=lambda j: j[0])


def params(item: dict, answer: str) -> dict:
    return {"model": MODEL, "max_tokens": MAX_TOKENS, "system": SYSTEM,
            "output_config": {"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            "messages": [{"role": "user", "content": user_text(item, answer)}]}


def custom_id(job_id: str, i: int) -> str:
    return f"j{i:05d}"   # custom_id chỉ cho chữ, số, -, _; ánh xạ ngược ghi trong judge_batch.json


def cmd_prepare() -> None:
    js = jobs()
    chars = sum(len(SYSTEM) + len(user_text(it, a)) for _, it, a in js)
    print(f"{len(js)} yêu cầu; khoảng {chars / 1e6:.2f} triệu ký tự đầu vào (tiếng Việt ~ 3–4 ký tự/token)")
    print("=" * 80)
    print(user_text(js[0][1], js[0][2])[:1500])


def cmd_submit() -> None:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    state = OUT / "judge_batch.json"
    if state.exists():
        sys.exit(f"{state.relative_to(config.ROOT)} đã có: batch đã gửi, chạy `collect`")
    js = jobs()
    ids = {custom_id(j, i): j for i, (j, _, _) in enumerate(js)}
    reqs = [Request(custom_id=cid, params=MessageCreateParamsNonStreaming(**params(it, a)))
            for cid, (j, it, a) in zip(ids, js)]
    batch = anthropic.Anthropic().messages.batches.create(requests=reqs)
    OUT.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"batch_id": batch.id, "model": MODEL, "ids": ids}, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(f"batch {batch.id}: {len(reqs)} yêu cầu")


def cmd_collect() -> None:
    import anthropic
    client = anthropic.Anthropic()
    st = json.loads((OUT / "judge_batch.json").read_text(encoding="utf-8"))
    while True:
        b = client.messages.batches.retrieve(st["batch_id"])
        if b.processing_status == "ended":
            break
        print(f"{time.strftime('%H:%M:%S')} {b.processing_status}, đang xử lý {b.request_counts.processing}", flush=True)
        time.sleep(60)
    rows, usage = [], defaultdict(int)
    for res in client.messages.batches.results(st["batch_id"]):
        run, u = st["ids"][res.custom_id].split("|", 1)
        row = {"run": run, "uid": u, "trang_thai": res.result.type}
        if res.result.type == "succeeded":
            msg = res.result.message
            row["stop_reason"] = msg.stop_reason
            for k in ("input_tokens", "output_tokens"):
                usage[k] += getattr(msg.usage, k) or 0
            text = next((blk.text for blk in msg.content if blk.type == "text"), "")
            if msg.stop_reason == "refusal" or not text:
                row["loi"] = f"không có kết quả chấm (stop_reason={msg.stop_reason})"
            else:
                row.update(json.loads(text))
        else:
            row["loi"] = res.result.type
        rows.append(row)
    rows.sort(key=lambda r: (RUNS.index(r["run"]), r["uid"]))
    with open(OUT / "judge.jsonl", "w", encoding="utf-8", newline="\n") as fp:
        fp.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    print(f"-> reports/g8/judge.jsonl: {len(rows)} dòng, lỗi {sum('loi' in r for r in rows)}; token {dict(usage)}")


def _ci(vals: list[float], keys: list[str], rng: random.Random, n_boot: int = 2000) -> list[float]:
    by = defaultdict(list)
    for k, v in zip(keys, vals):
        by[k].append(v)
    ks = sorted(by)
    boot = []
    for _ in range(n_boot):
        picked = [v for k in rng.choices(ks, k=len(ks)) for v in by[k]]
        boot.append(sum(picked) / len(picked))
    boot.sort()
    return [boot[int(0.025 * (n_boot - 1))], boot[int(0.975 * (n_boot - 1))]]


def cmd_score() -> None:
    items = {uid(x): x for x in evalset.load_eval()}
    rows = [json.loads(line) for line in open(OUT / "judge.jsonl", encoding="utf-8")]
    rng = random.Random(0)
    rep = {"model": MODEL, "luot": {}}
    for run in RUNS:
        rep["luot"][run] = {}
        for grp in ("trong_pham_vi", "thuong", "sua_doi", "bien_the", "ngoai_pham_vi"):
            sel = [r for r in rows if r["run"] == run and "dat" in r and
                   (items[r["uid"]]["nhom_cau"] in ("thuong", "sua_doi") if grp == "trong_pham_vi"
                    else items[r["uid"]]["nhom_cau"] == grp)]
            if not sel:
                continue
            vals = [float(r["dat"]) for r in sel]
            keys = [items[r["uid"]].get("ho_su_kien") or items[r["uid"]]["id"] for r in sel]
            rep["luot"][run][grp] = {"dat": sum(vals) / len(vals), "ci95": _ci(vals, keys, rng), "n": len(vals),
                                     "theo_luat_cu": sum(bool(r.get("theo_luat_cu")) for r in sel)}
    manual = OUT / "cham_tay_50.csv"
    if manual.exists():
        judged = {(r["run"], r["uid"]): r.get("dat") for r in rows}
        pairs = []
        for m in csv.DictReader(open(manual, encoding="utf-8-sig")):
            for run in ("D", "B"):
                v = (m.get(f"dat_{run}") or "").strip()
                if v in ("0", "1") and judged.get((run, m["uid"])) is not None:
                    pairs.append((int(v), int(judged[(run, m["uid"])])))
        if pairs:
            n = len(pairs)
            po = sum(a == b for a, b in pairs) / n
            p1, p2 = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
            pe = p1 * p2 + (1 - p1) * (1 - p2)
            rep["so_voi_cham_tay"] = {"n": n, "dong_y": po, "kappa": (po - pe) / (1 - pe) if pe < 1 else None}
    (OUT / "judge_scores.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    {"prepare": cmd_prepare, "submit": cmd_submit, "collect": cmd_collect, "score": cmd_score}[sys.argv[1]]()
