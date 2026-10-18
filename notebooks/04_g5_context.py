# %% [markdown]
# # G5 Task 4 — Gắn ngữ cảnh RAG cho dữ liệu train (cách C)
#
# Với mỗi mẫu trong `data/train/train.jsonl` và `dev.jsonl`:
#
# 1. Tìm 5 đoạn luật bằng đúng retriever của G3 (BM25 50 + bge-m3 50 → RRF → bge-reranker giữ 5 trong 20, lọc hiệu
#    lực tại ngày hỏi). Notebook chỉ thêm lớp chạy bge-m3 và reranker trên GPU; mã `src/rag` giữ nguyên.
# 2. Đối chiếu với `can_cu`: đoạn đúng đã có trong 5 đoạn thì giữ nguyên; thiếu thì thay vào chỗ đoạn nhiễu xếp cuối
#    và đặt ở vị trí ngẫu nhiên theo seed. Khoản hoặc phụ lục bị cắt nhiều đoạn thì chỉ lấy đoạn chứa căn cứ.
# 3. Chia dạng mẫu theo seed: khoảng 10% không ngữ cảnh; mẫu từ chối dùng nguyên 5 đoạn retriever trả về.
# 4. Tập train: nhân đôi mẫu thủ tục và mẫu thuộc Hướng dẫn, Bảo hiểm, Lệ phí, Tốc độ; bản thứ hai lấy đoạn nhiễu ở
#    hạng 6–10.
# 5. Ghép hội thoại system / user / assistant giống notebook G4, ghi `train_chat.jsonl`, `dev_chat.jsonl` và thống
#    kê `g5ctx_stats.json`.
#
# **Cài đặt Kaggle:** Accelerator *GPU T4 x2* (hoặc P100); Internet *On*; Add Input → dataset tạo từ
# `g5ctx_bundle.zip`. Rồi *Save Version → Save & Run All*. Chạy xong, tải 3 file ở tab Output.
#
# Chạy thử trên máy (không cần Kaggle): `G5CTX_LIMIT=10 py -3.13 notebooks/04_g5_context.py`.

# %%
# Cấu hình
SEED = 42
NGAY_HOI = "2026-10-01"
NO_CTX_RATE = 0.10                     # tỷ lệ mẫu không ngữ cảnh (cấu hình C ở G7)
TOP_K = 5                              # số đoạn đưa vào ngữ cảnh, như G3 và G7
ALT_K = 10                             # bản nhân đôi lấy đoạn nhiễu ở hạng TOP_K+1..ALT_K
BOOST_LOAI = {"thu_tuc"}               # nhân đôi trong tập train
BOOST_CHU_DE = {"Hướng dẫn", "Bảo hiểm", "Lệ phí", "Tốc độ"}
MAX_TOKENS = 4096                      # giới hạn độ dài khi train ở G6
import os
MAX_TOKENS = int(os.environ.get("G5CTX_MAX_TOKENS", MAX_TOKENS))   # chỉ để thử trên máy
BGE_M3 = ("BAAI/bge-m3", "5617a9f61b028005a4858fdac845db406aefb181")              # đúng bản đã dựng chỉ mục
RERANKER = ("BAAI/bge-reranker-v2-m3", "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e")  # đúng bản đã dùng ở G3

SYSTEM_WITH_CONTEXT = (
    "Bạn là trợ lý pháp luật giao thông đường bộ Việt Nam. Trả lời dựa trên các đoạn luật được cung cấp, "
    "theo quy định có hiệu lực tại ngày hỏi. Nêu rõ căn cứ (điểm, khoản, Điều, văn bản) và nêu đúng số tiền, "
    "số điểm trừ, thời hạn nếu có. Nếu các đoạn luật không có căn cứ cho câu hỏi, nói rõ là không có căn cứ trong "
    "tài liệu, không tự bịa quy định. Trả lời ngắn gọn bằng tiếng Việt."
)
SYSTEM_NO_CONTEXT = (
    "Bạn là trợ lý pháp luật giao thông đường bộ Việt Nam. Trả lời theo quy định đang có hiệu lực, nêu căn cứ nếu "
    "biết; nếu không chắc chắn thì nói rõ. Trả lời ngắn gọn bằng tiếng Việt."
)

# %%
import glob, json, os, random, re, subprocess, sys, time, zipfile
from pathlib import Path

ON_KAGGLE = os.path.exists("/kaggle")
LIMIT = int(os.environ.get("G5CTX_LIMIT", "0"))   # >0: chỉ chạy bấy nhiêu mẫu mỗi tập (để thử)
if ON_KAGGLE:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyvi", "rank_bm25", "faiss-cpu"], check=True)

# %%
def find_root():
    """Thư mục gốc của gói (có src/rag/retrieve.py): dataset đã giải nén, file zip, hoặc repo khi chạy trên máy."""
    if not ON_KAGGLE:
        return Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd().parent
    hits = glob.glob("/kaggle/input/**/src/rag/retrieve.py", recursive=True)
    if hits:
        return Path(hits[0]).parents[2]
    z = glob.glob("/kaggle/input/**/g5ctx_bundle.zip", recursive=True)
    assert z, "Không thấy gói g5ctx trong /kaggle/input: hãy Add Input dataset tạo từ g5ctx_bundle.zip"
    zipfile.ZipFile(z[0]).extractall("/kaggle/working/g5ctx")
    return Path("/kaggle/working/g5ctx")

ROOT = find_root()
OUT = Path("/kaggle/working") if ON_KAGGLE else ROOT / "kaggle" / "g5ctx" / "out_local"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
os.environ["TOKENIZERS_PARALLELISM"] = "false"
print("gốc:", ROOT, "| đầu ra:", OUT, "| giới hạn:", LIMIT or "không")

import numpy as np
import torch
from rag import chunking, context, retrieve

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
ENV = {"device": DEVICE, "torch": torch.__version__,
       "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
print(ENV)

# %%
from huggingface_hub import snapshot_download

def model_path(name, revision):
    return Path(snapshot_download(name, revision=revision, local_files_only=not ON_KAGGLE))

class GPUEncoder:
    """bge-m3 như `rag.dense.SentenceEncoder` nhưng chạy được trên GPU; danh tính phải khớp chỉ mục."""

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        path = model_path(*BGE_M3)
        self.st = SentenceTransformer(str(path), device=DEVICE)
        self.st.max_seq_length = 8192
        self.identity = {"model": BGE_M3[0], "revision": path.name, "max_seq_length": 8192, "normalize": True,
                         "dtype": "float32", "dim": self.st.get_embedding_dimension()}

    def __call__(self, texts):
        return self.st.encode(texts, batch_size=64, normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False).astype(np.float32)

class GPUReranker:
    """bge-reranker-v2-m3 như `rag.retrieve.CrossReranker` nhưng chạy được trên GPU."""

    def __init__(self):
        from sentence_transformers import CrossEncoder
        path = model_path(*RERANKER)
        self.ce = CrossEncoder(str(path), device=DEVICE, max_length=retrieve.RERANK_MAX_LENGTH)
        self.identity = {"model": RERANKER[0], "revision": path.name, "max_length": retrieve.RERANK_MAX_LENGTH}

    def __call__(self, pairs):
        return np.asarray(self.ce.predict(pairs, batch_size=32, show_progress_bar=False), dtype=float)

t0 = time.time()
ENC = GPUEncoder()
R = retrieve.load("khoan", reranker=False, rag_dir=ROOT / "data" / "rag", encoder=ENC)  # kiểm đúng bản mô hình
R.reranker = retrieve.Reranker(GPUReranker(), OUT / "rerank_cache")
R.reranker._save = lambda: None        # giữ điểm trong bộ nhớ, không ghi file sau mỗi câu
PARAMS = json.loads((ROOT / "reports" / "retrieval" / "params.json").read_text(encoding="utf-8"))["chon"]
CFG = retrieve.Config(**{**PARAMS, "top_k": ALT_K})
assert PARAMS["top_k"] == TOP_K and CFG.rerank_k >= ALT_K
print(f"nạp retriever: {time.time() - t0:.0f} giây; tham số G3: {PARAMS}")

# %%
LIVE = {c["chunk_id"]: c for c in R.chunks if chunking.in_force(c, NGAY_HOI)}
UNIT_CHUNKS = {}
for c in LIVE.values():
    for u in c["units"]:
        UNIT_CHUNKS.setdefault(u, []).append(c["chunk_id"])
NUM = re.compile(r"\d[\d.,]*\d|\d")

def needed_chunks(sample):
    """Đoạn đang có hiệu lực chứa các căn cứ. Một căn cứ nằm ở nhiều đoạn (khoản, phụ lục bị cắt) thì dùng đoạn đã
    chọn cho căn cứ khác nếu có, không thì lấy đoạn trùng nhiều số liệu của đáp án nhất."""
    numbers = set(NUM.findall(sample["dap_an"]))
    single, multi, missing = [], [], []
    for u in sample["can_cu"]:
        cands = UNIT_CHUNKS.get(u, [])
        (single if len(cands) == 1 else multi if cands else missing).append((u, cands))
    need = list(dict.fromkeys(c for _, cands in single for c in cands))
    for u, cands in multi:
        if set(cands) & set(need):
            continue
        best = max(cands, key=lambda c: (len(numbers & set(NUM.findall(LIVE[c]["text"]))), -cands.index(c)))
        need.append(best)
    return need[:TOP_K], [u for u, _ in missing]

def assemble(ranked, need, rng):
    """5 đoạn: lấy theo hạng, đoạn cần có mà thiếu thì thay vào chỗ đoạn nhiễu xếp cuối, đặt ở vị trí ngẫu nhiên."""
    shown = list(ranked[:TOP_K])
    missing = [c for c in need if c not in shown]
    for c in missing:
        drop = max(i for i, x in enumerate(shown) if x not in need)
        shown.pop(drop)
        shown.insert(rng.randrange(len(shown) + 1), c)
    return shown, missing

def assemble_alt(ranked, need, rng):
    """Bản nhân đôi: đoạn cần có + đoạn nhiễu hạng TOP_K+1..ALT_K (thiếu thì lấy nhiễu trong top-5), rồi xáo."""
    noise = [c for c in ranked[TOP_K:ALT_K] if c not in need] + [c for c in ranked[:TOP_K] if c not in need]
    shown = list(need) + noise[:TOP_K - len(need)]
    rng.shuffle(shown)
    return shown

def messages(question, dap_an, ctx):
    if ctx:
        system, user = SYSTEM_WITH_CONTEXT, f"Ngày hỏi: {NGAY_HOI}\n\nCác đoạn luật:\n{ctx}\n\nCâu hỏi: {question}"
    else:
        system, user = SYSTEM_NO_CONTEXT, f"Ngày hỏi: {NGAY_HOI}\n\nCâu hỏi: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user},
            {"role": "assistant", "content": dap_an}]

TOKENIZER = None
tok_path = ROOT / "tools" / "tokenizers" / "qwen3.5-9b" / "tokenizer.json"
if tok_path.exists():
    from tokenizers import Tokenizer
    TOKENIZER = Tokenizer.from_file(str(tok_path))

def n_tokens(msgs):
    """Ước lượng: token của ba lượt cộng 10 token mỗi lượt cho thẻ của chat template."""
    if TOKENIZER is None:
        return None
    return sum(len(TOKENIZER.encode(m["content"]).ids) + 10 for m in msgs)

# %%
def read_jsonl(path):
    with open(path, encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]

TAPS = {tap: read_jsonl(ROOT / "data" / "train" / f"{tap}.jsonl") for tap in ("train", "dev")}
if LIMIT:
    TAPS = {tap: rows[:LIMIT] for tap, rows in TAPS.items()}

t1 = time.time()
QUESTIONS = [s["cau_hoi"] for rows in TAPS.values() for s in rows]
QVEC = dict(zip(QUESTIONS, ENC(QUESTIONS)))
RANKED = {}
for i, q in enumerate(dict.fromkeys(QUESTIONS), 1):
    RANKED[q] = [h.chunk["chunk_id"] for h in R.search(q, NGAY_HOI, CFG, qvec=QVEC[q])]
    if i % 200 == 0:
        print(f"{i}/{len(set(QUESTIONS))} câu, {time.time() - t1:.0f} giây")
SEARCH_SECONDS = round(time.time() - t1, 1)
print(f"tìm kiếm {len(RANKED)} câu: {SEARCH_SECONDS} giây")

# %%
def chunk_info(cid, ranked, inserted, need):
    return {"chunk_id": cid, "hang": ranked.index(cid) + 1 if cid in ranked else None,
            "chen": cid in inserted, "can_co": cid in need}

def build(tap, rows):
    out, notes = [], []
    for s in rows:
        ranked = RANKED[s["cau_hoi"]]
        need, missing_units = (needed_chunks(s) if s["loai"] != "tu_choi" else ([], []))
        if missing_units:
            notes.append({"key": s["key"], "can_cu_khong_co_doan": missing_units})
        no_basis = s["loai"] != "tu_choi" and not need   # căn cứ không nằm trong đoạn nào: chỉ dùng dạng không ngữ cảnh
        boost = tap == "train" and not no_basis and (s["loai"] in BOOST_LOAI or s["chu_de"] in BOOST_CHU_DE)
        for ban in [0] + ([1] if boost else []):
            rng = random.Random(f"{SEED}:{s['key']}:{ban}")
            no_ctx = ban == 0 and (rng.random() < NO_CTX_RATE or no_basis)
            if no_ctx:
                shown, inserted = [], []
            elif ban == 0:
                shown, inserted = assemble(ranked, need, rng)
            else:
                shown = assemble_alt(ranked, need, rng)
                inserted = [c for c in need if c not in ranked[:TOP_K]]
            ctx = context.format_context([LIVE[c] for c in shown]) if shown else ""
            msgs = messages(s["cau_hoi"], s["dap_an"], ctx)
            dropped = 0
            while TOKENIZER is not None and n_tokens(msgs) > MAX_TOKENS and any(c not in need for c in shown):
                # Quá dài (thường do phụ lục lớn): bỏ đoạn nhiễu dài nhất, không bao giờ bỏ đoạn cần có.
                shown.remove(max((c for c in shown if c not in need), key=lambda c: LIVE[c]["so_token"]))
                dropped += 1
                ctx = context.format_context([LIVE[c] for c in shown])
                msgs = messages(s["cau_hoi"], s["dap_an"], ctx)
            out.append({"key": s["key"], "ban": ban, "tap": tap, "chu_de": s["chu_de"], "loai": s["loai"],
                        "dang": "khong_ngu_canh" if no_ctx else ("tu_choi" if s["loai"] == "tu_choi" else "co_ngu_canh"),
                        "doan": [chunk_info(c, ranked, inserted, need) for c in shown],
                        "retriever_tim_du": bool(need) and all(c in ranked[:TOP_K] for c in need),
                        "retriever_tim_mot_phan": bool(need) and any(c in ranked[:TOP_K] for c in need),
                        "so_doan_can_co": len(need), "so_doan_chen": len(inserted), "so_doan_bo_vi_dai": dropped,
                        "messages": msgs, "so_token": n_tokens(msgs)})
    return out, notes

RESULT = {}
NOTES = []
for tap, rows in TAPS.items():
    RESULT[tap], notes = build(tap, rows)
    NOTES += notes

# Mọi mẫu có ngữ cảnh (không phải từ chối) phải chứa đủ đoạn cần có.
for tap, recs in RESULT.items():
    for r in recs:
        if r["dang"] == "co_ngu_canh":
            shown = {d["chunk_id"] for d in r["doan"]}
            need = {d["chunk_id"] for d in r["doan"] if d["can_co"]}
            assert len(r["doan"]) + r["so_doan_bo_vi_dai"] == TOP_K and need and need <= shown, r["key"]
print({tap: len(recs) for tap, recs in RESULT.items()})

# %%
from collections import Counter

def stats(recs):
    base = [r for r in recs if r["ban"] == 0 and r["loai"] != "tu_choi"]
    with_need = [r for r in base if r["so_doan_can_co"]]
    tokens = sorted(r["so_token"] for r in recs if r["so_token"] is not None)
    pct = lambda p: tokens[min(len(tokens) - 1, int(p * len(tokens)))] if tokens else None
    by_loai = {}
    for loai in sorted({r["loai"] for r in with_need}):
        rs = [r for r in with_need if r["loai"] == loai]
        by_loai[loai] = {"n": len(rs), "tim_du": round(sum(r["retriever_tim_du"] for r in rs) / len(rs), 3),
                         "tim_mot_phan_tro_len": round(sum(r["retriever_tim_mot_phan"] for r in rs) / len(rs), 3)}
    return {"so_mau": len(recs), "theo_dang": dict(Counter(r["dang"] for r in recs)),
            "theo_ban": dict(Counter(r["ban"] for r in recs)),
            "theo_loai": dict(Counter(r["loai"] for r in recs)), "theo_chu_de": dict(Counter(r["chu_de"] for r in recs)),
            "retriever_tren_mau_goc": {
                "n": len(with_need),
                "tim_du": round(sum(r["retriever_tim_du"] for r in with_need) / max(1, len(with_need)), 3),
                "tim_mot_phan_tro_len": round(sum(r["retriever_tim_mot_phan"] for r in with_need) / max(1, len(with_need)), 3),
                "phai_chen": sum(r["so_doan_chen"] > 0 for r in with_need), "theo_loai": by_loai},
            "token": {"tb": round(sum(tokens) / len(tokens)) if tokens else None, "p50": pct(0.5), "p95": pct(0.95),
                      "max": tokens[-1] if tokens else None, "vuot_gioi_han": sum(t > MAX_TOKENS for t in tokens),
                      "mau_bo_bot_doan_vi_dai": sum(r["so_doan_bo_vi_dai"] > 0 for r in recs)}}

STATS = {"cau_hinh": {"seed": SEED, "ngay_hoi": NGAY_HOI, "no_ctx_rate": NO_CTX_RATE, "top_k": TOP_K, "alt_k": ALT_K,
                      "boost_loai": sorted(BOOST_LOAI), "boost_chu_de": sorted(BOOST_CHU_DE), "tham_so_g3": PARAMS,
                      "bge_m3": BGE_M3, "reranker": RERANKER, "gioi_han_thu": LIMIT},
         "moi_truong": ENV, "giay_tim_kiem": SEARCH_SECONDS,
         "train": stats(RESULT["train"]), "dev": stats(RESULT["dev"]), "can_cu_khong_co_doan": NOTES}
meta_path = ROOT / "meta.json"
if meta_path.exists():
    STATS["goi_du_lieu"] = json.loads(meta_path.read_text(encoding="utf-8"))
print(json.dumps({k: STATS[k] for k in ("train", "dev")}, ensure_ascii=False, indent=1))

# %%
for tap, recs in RESULT.items():
    path = OUT / f"{tap}_chat.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    print("->", path, len(recs), "dòng")
(OUT / "g5ctx_stats.json").write_text(json.dumps(STATS, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("->", OUT / "g5ctx_stats.json")

# %%
# Xem nhanh 3 mẫu: một mẫu retriever tìm đủ, một mẫu phải chèn, một mẫu từ chối.
def show(r):
    print("=" * 100)
    print(r["key"], "| bản", r["ban"], "|", r["dang"], "| đoạn:", [(d["hang"], d["chen"], d["can_co"]) for d in r["doan"]])
    for m in r["messages"]:
        print(f"--- {m['role']}:\n{m['content'][:1200]}")

recs = RESULT["train"]
for pick in (lambda r: r["dang"] == "co_ngu_canh" and r["retriever_tim_du"],
             lambda r: r["dang"] == "co_ngu_canh" and r["so_doan_chen"] > 0,
             lambda r: r["dang"] == "tu_choi"):
    hit = next((r for r in recs if pick(r)), None)
    if hit:
        show(hit)
