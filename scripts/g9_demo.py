"""G9 — demo hỏi đáp luật giao thông theo ngày hỏi, giao diện Gradio.

    python -u scripts/g9_demo.py --share --work /kaggle/working/g9      # Kaggle/Colab có GPU: in link gradio.live
    py -3.13 scripts/g9_demo.py --backend dry                            # laptop: thử giao diện, không sinh thật
    py -3.13 scripts/g9_demo.py --backend dry --selftest                 # laptop: chạy các câu mẫu, không mở giao diện

Luồng: câu hỏi + ngày hỏi → retriever của G3 (BM25 + bge-m3 → RRF → bge-reranker-v2-m3, lọc hiệu lực tại ngày hỏi,
tham số `reports/retrieval/params.json`) → 5 đoạn theo Khoản, hoặc mở rộng lên Điều như G8 (`rag.expand`) → prompt
dựng giống hệt lúc train G6 (`data/g9/prompts.json`) → Qwen3.5-9B 4-bit, bật adapter LoRA (D) hoặc tắt (B), sinh greedy
tối đa 512 token, hiện chữ dần.

Tìm kiếm chạy trong một tiến trình con, sinh chữ ở tiến trình chính. Mỗi tiến trình chỉ thấy một GPU, như G7: máy 2 GPU
(Kaggle T4 x2) thì tìm kiếm ở GPU 1, mô hình ở GPU 0; máy 1 GPU thì dùng chung; không GPU thì tìm kiếm trên CPU.
Giao diện cho chọn: chế độ (D, B, hay so sánh B và D), cách dựng ngữ cảnh (Khoản / Điều), bật/tắt lọc hiệu lực (RQ3).
"""

import argparse
import contextlib
import html
import json
import multiprocessing as mp
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import g6_train as g6  # noqa: E402  chỉ dùng thư viện chuẩn ở mức module
import g7_generate as g7  # noqa: E402

ADAPTER = next(p for p in (ROOT / "adapter", ROOT / "remote" / "g6" / "ketqua" / "out_g6" / "adapter") if p.exists())
PROMPTS = ROOT / "data" / "g9" / "prompts.json"
EXAMPLES = ROOT / "data" / "g9" / "examples.json"
PARAMS = ROOT / "reports" / "retrieval" / "params.json"
RERANK_REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"   # bản reranker đã chấm ở G3 (rerank_cache)
DEFAULT_DATE = "2026-10-01"
CUTOFF = "2026-10-01"   # kho luật cập nhật đến ngày này
POOL = 20               # số đoạn Khoản đã xếp hạng đưa vào bước mở rộng lên Điều (như G8)
CHE_DO = {"D: LoRA + RAG (hệ thống chính)": [("D", True)],
          "B: mô hình gốc + RAG": [("B", False)],
          "So sánh B và D": [("D", True), ("B", False)]}
NGU_CANH = {"5 đoạn theo Khoản (G3)": "khoan", "Mở rộng lên Điều (G8)": "dieu"}
CANH_BAO = ("*Câu trả lời do mô hình sinh ra, chỉ mang tính tham khảo, không thay thế văn bản pháp luật chính thức. "
            f"Kho văn bản cập nhật đến {date.fromisoformat(CUTOFF):%d/%m/%Y}.*")


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def parse_date(s: str) -> str:
    s = (s or "").strip() or DEFAULT_DATE
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        with contextlib.suppress(ValueError):
            return datetime.strptime(s, fmt).date().isoformat()
    raise ValueError(f"ngày hỏi '{s}' không đọc được, hãy ghi dạng dd/mm/yyyy")


# ---------------------------------------------------------------- tìm kiếm (tiến trình con)

class Search:
    """Retriever G3 trên chỉ mục theo Khoản, bge-m3 và reranker ghim đúng bản đã tạo chỉ mục và đã chấm ở G3."""

    def __init__(self, device: str, work: Path):
        from rag import bm25, dense, expand, retrieve

        t = time.time()
        chunks, sha = retrieve.load_chunks("khoan")
        try:
            b = bm25.BM25Index.load(ROOT / "data" / "rag" / "index" / "khoan" / "bm25.pkl", sha)
        except Exception as e:  # pickle tạo bằng numpy/rank_bm25 khác phiên bản: build lại từ đúng file đoạn
            log(f"không nạp được bm25.pkl ({type(e).__name__}: {e}); build lại BM25 từ chunks_khoan.jsonl")
            b = bm25.BM25Index.build(chunks)
        d = dense.DenseIndex.load(ROOT / "data" / "rag" / "index" / "khoan", sha)
        if not (b.ids == d.ids == [c["chunk_id"] for c in chunks]):
            raise ValueError("thứ tự đoạn trong chỉ mục không khớp file đoạn")
        ident = d.meta["bo_ma_hoa"]
        enc = dense.SentenceEncoder(ident["model"], ident["max_seq_length"], device=device, revision=ident["revision"])
        if enc.identity != ident:
            raise ValueError(f"bộ mã hóa câu hỏi {enc.identity} khác bộ mã hóa đã tạo chỉ mục {ident}")
        rr = retrieve.Reranker(retrieve.CrossReranker(device=device, revision=RERANK_REVISION), work / "rerank_cache")
        self.r = retrieve.Retriever(chunks, b, d, enc, rr)
        self.cfg = retrieve.Config(**json.loads(PARAMS.read_text(encoding="utf-8"))["chon"])
        self.expand = expand
        self.parents = expand.parent_index(retrieve.load_chunks("dieu")[0])
        self.info = {"thiet_bi": device, "so_doan": len(chunks), "nap_giay": round(time.time() - t, 1),
                     "tham_so": self.cfg.__dict__}

    def __call__(self, query: str, t: str, loc: bool, cach: str) -> tuple[list[dict], float]:
        t0 = time.time()
        cfg = replace(self.cfg, loc_hieu_luc=loc, top_k=POOL if cach == "dieu" else self.cfg.top_k)
        ranked = [h.chunk for h in self.r.search(query, t, cfg)]
        chunks = self.expand.expand_to_dieu(ranked, t, self.parents) if cach == "dieu" else ranked
        return chunks, round(time.time() - t0, 2)


def _search_worker(conn, gpu: str | None, work: str) -> None:
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu if gpu is not None else ""   # trước khi nạp torch
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        s = Search("cuda" if gpu is not None else "cpu", Path(work))
        conn.send(("ok", s.info))
    except Exception as e:
        import traceback
        conn.send(("err", f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}"))
        return
    while (msg := conn.recv()) is not None:
        try:
            conn.send(("ok", s(*msg)))
        except Exception as e:
            conn.send(("err", f"{type(e).__name__}: {e}"))


class SearchClient:
    def __init__(self, gpu: str | None, work: Path):
        ctx = mp.get_context("spawn")
        self.conn, child = ctx.Pipe()
        self.proc = ctx.Process(target=_search_worker, args=(child, gpu, str(work)), daemon=True)
        self.proc.start()
        self.lock = threading.Lock()

    def ready(self) -> dict:
        status, val = self.conn.recv()
        if status != "ok":
            raise RuntimeError(f"tiến trình tìm kiếm lỗi khi nạp: {val}")
        return val

    def __call__(self, query: str, t: str, loc: bool, cach: str) -> tuple[list[dict], float]:
        with self.lock:
            self.conn.send((query, t, loc, cach))
            status, val = self.conn.recv()
        if status != "ok":
            raise RuntimeError(f"tìm kiếm lỗi: {val}")
        return val


# ---------------------------------------------------------------- sinh chữ (tiến trình chính)

class Generator:
    def __init__(self, backend: str):
        self.backend = backend
        self.prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
        if backend == "dry":
            from transformers import AutoTokenizer
            self.model, self.tok, self.info = None, AutoTokenizer.from_pretrained(str(ADAPTER)), {"backend": "dry"}
        else:
            self.model, self.tok, self.info = g7.load_model(ADAPTER)

    def prompt_ids(self, query: str, t: str, chunks: list[dict]) -> list[int]:
        from rag import context
        item = {"ngay_hoi": t, "cau_hoi": query, "ngu_canh": context.format_context(chunks)}
        return g6.encode(self.tok, g6.chat_text(self.tok, g7.messages(self.prompts, item, "ngu_canh"), generation=True))

    def check_adapter(self, ids: list[int]) -> None:
        if self.model is not None:
            self.info["chenh_logit_bat_tat_adapter"] = round(g7.check_adapter_active(self.model, self.tok, ids), 4)

    def stream(self, ids: list[int], adapter: bool):
        """Chuỗi chữ đã sinh tới lúc đó (cộng dồn), rồi số token mới ở phần tử cuối dạng int."""
        if self.model is None:
            yield f"(chạy thử, không có mô hình) prompt {len(ids)} token, {'bật' if adapter else 'tắt'} adapter."
            yield 0
            return
        import torch
        from transformers import TextIteratorStreamer

        streamer = TextIteratorStreamer(g6.text_tokenizer(self.tok), skip_prompt=True, skip_special_tokens=True)
        x = torch.tensor([ids], device="cuda")
        box: dict = {}

        def work():
            try:
                with (contextlib.nullcontext() if adapter else self.model.disable_adapter()), torch.inference_mode():
                    out = self.model.generate(input_ids=x, attention_mask=torch.ones_like(x), streamer=streamer,
                                              max_new_tokens=g7.MAX_NEW_TOKENS, do_sample=False, use_cache=True)
                box["n"] = out.shape[1] - x.shape[1]
            except Exception as e:
                box["err"] = e
                streamer.end()

        th = threading.Thread(target=work, daemon=True)
        th.start()
        text = ""
        for piece in streamer:
            text += piece
            yield re.sub(r"<think>.*?(</think>|$)", "", text, flags=re.DOTALL).strip()
        th.join()
        if "err" in box:
            raise box["err"]
        yield int(box.get("n", 0))


# ---------------------------------------------------------------- hiển thị

def sources_markdown(chunks: list[dict], t: str, loc: bool) -> str:
    from rag import chunking, context
    if not chunks:
        return "_Không tìm được đoạn luật nào._"
    lines = [f"**{len(chunks)} đoạn luật đưa vào prompt** (ngày hỏi {date.fromisoformat(t):%d/%m/%Y}, "
             f"{'có' if loc else '**không**'} lọc hiệu lực):"]
    for n, c in enumerate(chunks, 1):
        flag = "" if chunking.in_force(c, t) else " — ⚠️ <b>không còn/chưa có hiệu lực tại ngày hỏi</b>"
        body = html.escape(c["text"]).replace("\n", "<br>")
        lines.append(f"<details><summary><b>[{n}] {html.escape(context.source_label(c))}</b> — "
                     f"{context.validity_label(c)}{flag}</summary><p>{body}</p></details>")
    return "\n\n".join(lines)


def user_error(msg: str) -> Exception:
    """Lỗi hiện thành thông báo trên giao diện; khi chạy --selftest không cần Gradio."""
    try:
        import gradio as gr
        return gr.Error(msg)
    except ImportError:
        return ValueError(msg)


def answer_block(name: str, text: str, done: bool) -> str:
    title = {"D": "D: LoRA + RAG", "B": "B: mô hình gốc + RAG"}[name]
    return f"### {title}\n\n{text or '_đang sinh..._'}" + (f"\n\n---\n{CANH_BAO}" if done else "")


class App:
    def __init__(self, gen: Generator, search: SearchClient):
        self.gen, self.search = gen, search

    def ask(self, query: str, ngay: str, che_do: str, ngu_canh: str, loc: bool):
        """Generator cho Gradio: trả (khung D, khung B, thông tin, nguồn) nhiều lần khi chữ được sinh dần."""
        query = (query or "").strip()
        if not query:
            raise user_error("Hãy nhập câu hỏi.")
        try:
            t = parse_date(ngay)
        except ValueError as e:
            raise user_error(str(e))
        runs = CHE_DO[che_do]
        out = {"D": "", "B": ""}
        for name, _ in runs:
            out[name] = answer_block(name, "_đang tìm đoạn luật..._", False)
        info = [f"Ngày hỏi **{date.fromisoformat(t):%d/%m/%Y}**" +
                (f" (sau ngày kho cập nhật {date.fromisoformat(CUTOFF):%d/%m/%Y}: có thể thiếu văn bản mới)"
                 if t > CUTOFF else "")]
        yield out["D"], out["B"], " · ".join(info), ""

        chunks, secs = self.search(query, t, loc, NGU_CANH[ngu_canh])
        ids = self.gen.prompt_ids(query, t, chunks)
        info.append(f"tìm kiếm {secs:.1f} giây, prompt {len(ids)} token")
        src = sources_markdown(chunks, t, loc)
        yield out["D"], out["B"], " · ".join(info), src

        for name, adapter in runs:
            t0, text = time.time(), ""
            for piece in self.gen.stream(ids, adapter):
                if isinstance(piece, int):
                    info.append(f"{name}: {time.time() - t0:.1f} giây, {piece} token")
                    break
                text = piece
                out[name] = answer_block(name, text, False)
                yield out["D"], out["B"], " · ".join(info), src
            out[name] = answer_block(name, text, True)
            yield out["D"], out["B"], " · ".join(info), src

    def ui(self, examples: list[dict]):
        import gradio as gr
        with gr.Blocks(title="Hỏi đáp luật giao thông theo ngày hỏi") as demo:
            gr.Markdown("# Hỏi đáp luật giao thông đường bộ theo ngày hỏi\n"
                        "Qwen3.5-9B + LoRA (G6) + RAG có lọc hiệu lực (G3). Câu trả lời dựa trên các đoạn luật "
                        "**có hiệu lực tại ngày hỏi**; đổi ngày hỏi để xem đáp án thay đổi theo văn bản sửa đổi.")
            with gr.Row():
                with gr.Column(scale=3):
                    q = gr.Textbox(label="Câu hỏi (Enter để hỏi)", lines=1,   # nhiều dòng thì Enter chỉ xuống dòng
                                   placeholder="Ví dụ: Xe máy vượt đèn đỏ bị phạt bao nhiêu?")
                with gr.Column(scale=1):
                    ngay = gr.Textbox(label="Ngày hỏi (dd/mm/yyyy)", value=f"{date.fromisoformat(DEFAULT_DATE):%d/%m/%Y}")
                    btn = gr.Button("Hỏi", variant="primary")
            with gr.Row():
                che_do = gr.Radio(list(CHE_DO), value=next(iter(CHE_DO)), label="Chế độ")
                ngu_canh = gr.Radio(list(NGU_CANH), value=next(iter(NGU_CANH)), label="Ngữ cảnh")
                loc = gr.Checkbox(value=True, label="Lọc hiệu lực theo ngày hỏi (tắt để xem lỗi lấy nhầm bản cũ)")
            info = gr.Markdown()
            with gr.Row():
                ans_d = gr.Markdown()
                ans_b = gr.Markdown()
            with gr.Accordion("Đoạn luật đã dùng (bấm từng đoạn để xem nguyên văn)", open=False):
                src = gr.Markdown()
            if examples:
                gr.Markdown("**Câu mẫu.** Câu sửa đổi có hai ngày: ngày mặc định (bản mới) và một ngày trước khi "
                            "văn bản sửa đổi có hiệu lực (bản cũ).")
                gr.Examples([[x["cau_hoi"], f"{date.fromisoformat(x['ngay_hoi']):%d/%m/%Y}"] for x in examples],
                            inputs=[q, ngay], examples_per_page=12)
            args = dict(fn=self.ask, inputs=[q, ngay, che_do, ngu_canh, loc], outputs=[ans_d, ans_b, info, src])
            btn.click(**args)
            q.submit(**args)
        return demo


# ---------------------------------------------------------------- chạy

def gpu_count() -> int:
    try:
        return subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.count("GPU ")
    except FileNotFoundError:
        return 0


def selftest(app: App, examples: list[dict], n: int) -> None:
    for x in examples[:n]:
        for che_do in (next(iter(CHE_DO)),):
            last = None
            for last in app.ask(x["cau_hoi"], x["ngay_hoi"], che_do, next(iter(NGU_CANH)), True):
                pass
            print("=" * 100, "\n", x["cau_hoi"], "|", x["ngay_hoi"], "|", last[2])
            print(re.sub(r"<[^>]+>", " ", last[3])[:700])
            print(last[0][:800])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["unsloth", "dry"], default="unsloth")
    ap.add_argument("--share", action="store_true", help="tạo link công khai gradio.live")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--work", default=str(ROOT / "data" / "rag" / "index"), help="thư mục ghi cache điểm reranker")
    ap.add_argument("--selftest", type=int, nargs="?", const=4, default=0, help="chạy n câu mẫu rồi thoát")
    a = ap.parse_args()

    n_gpu = gpu_count()
    gpu_search = None if n_gpu == 0 else ("1" if n_gpu > 1 else "0")
    os.environ["CUDA_VISIBLE_DEVICES"] = "0" if n_gpu else ""   # tiến trình chính chỉ thấy GPU 0, trước khi nạp torch
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    log(f"{n_gpu} GPU; tìm kiếm trên {'GPU ' + gpu_search if gpu_search else 'CPU'}, mô hình trên "
        f"{'GPU 0' if n_gpu else 'không có (chạy thử)' if a.backend == 'dry' else 'GPU 0'}")
    search = SearchClient(gpu_search, work)   # nạp song song với mô hình
    gen = Generator(a.backend)
    log(f"nạp xong mô hình {json.dumps(gen.info, ensure_ascii=False)}")
    log(f"nạp xong tìm kiếm {json.dumps(search.ready(), ensure_ascii=False)}")

    examples = json.loads(EXAMPLES.read_text(encoding="utf-8")) if EXAMPLES.exists() else []
    app = App(gen, search)
    x0 = examples[0] if examples else {"cau_hoi": "Xe máy vượt đèn đỏ bị phạt bao nhiêu?", "ngay_hoi": DEFAULT_DATE}
    chunks, secs = search(x0["cau_hoi"], x0["ngay_hoi"], True, "khoan")
    gen.check_adapter(gen.prompt_ids(x0["cau_hoi"], x0["ngay_hoi"], chunks))
    log(f"chạy thử tìm kiếm {secs} giây; kiểm adapter {gen.info.get('chenh_logit_bat_tat_adapter', '-')}")
    if a.selftest:
        selftest(app, examples, a.selftest)
        search.conn.send(None)
        return
    demo = app.ui(examples)
    log("SẴN SÀNG: mở link bên dưới" + (" (link công khai gradio.live)" if a.share else ""))
    demo.queue(default_concurrency_limit=1).launch(share=a.share, server_name="0.0.0.0", server_port=a.port)


if __name__ == "__main__":
    main()
