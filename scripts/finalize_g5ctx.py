"""Chốt kết quả notebook gắn ngữ cảnh G5 (Task 4) vào `data/train/chat/`.

    py -3.13 scripts/finalize_g5ctx.py [thư_mục_kết_quả]   # mặc định kaggle/g5ctx/out_local

Đầu vào là 3 file notebook `04_g5_context` ghi ra (`train_chat.jsonl`, `dev_chat.jsonl`, `g5ctx_stats.json`).
Script kiểm lại mã băm gói dữ liệu với repo, rồi xử lý một trường hợp notebook chưa xử lý: mẫu có ngữ cảnh mà căn cứ
nằm ở nhiều Khoản hơn 5 ô (chỉ 5 đoạn được đưa vào, phần căn cứ còn lại không có trong ngữ cảnh). Để mô hình không học
trả lời ngoài tài liệu, các mẫu này chuyển sang dạng không ngữ cảnh: giữ đáp án, bỏ đoạn luật. Ghi `train_chat.jsonl`,
`dev_chat.jsonl`, bản sao `g5ctx_stats.json` và `MANIFEST.json` (mã băm, số mẫu theo dạng, các mẫu đã chuyển).
"""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config  # noqa: E402
from rag import chunking  # noqa: E402

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else config.ROOT / "kaggle" / "g5ctx" / "out_local"
OUT = config.ROOT / "data" / "train" / "chat"
TAPS = ("train", "dev")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def check_bundle(stats: dict) -> None:
    """Gói đã chạy phải khớp repo (so sau khi đổi CRLF về LF, vì git trên Windows có thể đổi dòng khi checkout)."""
    differ = [name for name, h in stats["goi_du_lieu"]["file"].items()
              if h not in {sha256(b := (config.ROOT / name).read_bytes()), sha256(b.replace(b"\r\n", b"\n"))}]
    assert not differ, f"gói đã chạy khác repo: {differ}"


def main() -> None:
    stats = json.loads((SRC / "g5ctx_stats.json").read_text(encoding="utf-8"))
    check_bundle(stats)
    T = stats["cau_hinh"]["ngay_hoi"]
    chunks = {c["chunk_id"]: c for c in read_jsonl(config.ROOT / "data" / "rag" / "chunks_khoan.jsonl")}
    live_units = {u for c in chunks.values() if chunking.in_force(c, T) for u in c["units"]}

    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(config.ROOT / "tools" / "tokenizers" / "qwen3.5-9b" / "tokenizer.json"))

    def n_tokens(msgs):  # như n_tokens của notebook
        return sum(len(tok.encode(m["content"]).ids) + 10 for m in msgs)

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"mo_ta": "Dữ liệu hội thoại cho G6 (G5 Task 4, cách C), chốt từ kết quả notebook 04_g5_context.",
                "moi_truong_chay": stats["moi_truong"], "giay_tim_kiem": stats["giay_tim_kiem"],
                "dau_vao": {}, "files": {}, "chuyen_khong_ngu_canh": []}
    for tap in TAPS:
        src = {s["key"]: s for s in read_jsonl(config.ROOT / "data" / "train" / f"{tap}.jsonl")}
        raw = (SRC / f"{tap}_chat.jsonl").read_bytes()
        manifest["dau_vao"][f"{tap}_chat.jsonl"] = sha256(raw)
        rows = read_jsonl(SRC / f"{tap}_chat.jsonl")
        no_ctx = next(r["messages"][0]["content"] for r in rows if r["dang"] == "khong_ngu_canh")
        for r in rows:
            if r["dang"] != "co_ngu_canh":
                continue
            shown = {u for d in r["doan"] for u in chunks[d["chunk_id"]]["units"]}
            missing = [u for u in src[r["key"]]["can_cu"] if u in live_units and u not in shown]
            if not missing:
                continue
            r["messages"] = [{"role": "system", "content": no_ctx},
                             {"role": "user", "content": f"Ngày hỏi: {T}\n\nCâu hỏi: {src[r['key']]['cau_hoi']}"},
                             r["messages"][2]]
            r.update(dang="khong_ngu_canh", doan=[], so_doan_can_co=0, so_doan_chen=0, so_doan_bo_vi_dai=0,
                     so_token=n_tokens(r["messages"]))
            manifest["chuyen_khong_ngu_canh"].append(
                {"tap": tap, "key": r["key"], "ban": r["ban"], "ly_do": "căn cứ vượt 5 ô ngữ cảnh",
                 "can_cu_ngoai_ngu_canh": missing})
        path = OUT / f"{tap}_chat.jsonl"
        write_jsonl(path, rows)
        manifest["files"][path.relative_to(config.ROOT).as_posix()] = {
            "so_mau": len(rows), "theo_dang": dict(Counter(r["dang"] for r in rows)),
            "theo_ban": dict(Counter(str(r["ban"]) for r in rows)),
            "token_max": max(r["so_token"] for r in rows), "sha256": sha256(path.read_bytes())}
        print(f"-> {path.relative_to(config.ROOT)}: {len(rows)} dòng {manifest['files'][path.relative_to(config.ROOT).as_posix()]['theo_dang']}")
    (OUT / "g5ctx_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for c in manifest["chuyen_khong_ngu_canh"]:
        print("chuyển không ngữ cảnh:", c["tap"], c["key"], "bản", c["ban"], c["can_cu_ngoai_ngu_canh"])
    print("->", (OUT / "MANIFEST.json").relative_to(config.ROOT))


if __name__ == "__main__":
    main()
