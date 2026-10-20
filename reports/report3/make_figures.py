"""Vẽ hình cho Report 3 từ các file kết quả đã có trong repo.

    py -3.13 reports/report3/make_figures.py
"""

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def pipeline() -> None:
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    boxes = [
        (0.1, 2.2, "Câu hỏi\n+ ngày hỏi t"),
        (1.9, 2.2, "BM25 (pyvi)\n+ bge-m3 (FAISS)"),
        (3.7, 2.2, "Gộp RRF\n(k = 60)"),
        (5.5, 2.2, "Lọc hiệu lực\nin_force_at(t)"),
        (7.3, 2.2, "Rerank\nbge-reranker-v2-m3"),
        (7.3, 0.4, "5 đoạn theo Khoản\n(G8: mở rộng lên Điều)"),
        (5.5, 0.4, "Qwen3.5-9B 4-bit\n+ adapter LoRA (G6)"),
        (3.7, 0.4, "Câu trả lời\n+ căn cứ, hiệu lực"),
    ]
    for x, y, text in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 1.6, 1.0, boxstyle="round,pad=0.05", fc="#EAF2FB", ec="#245B85"))
        ax.text(x + 0.8, y + 0.5, text, ha="center", va="center", fontsize=9)
    arrows = [((1.7, 2.7), (1.9, 2.7)), ((3.5, 2.7), (3.7, 2.7)), ((5.3, 2.7), (5.5, 2.7)), ((7.1, 2.7), (7.3, 2.7)),
              ((8.1, 2.2), (8.1, 1.4)), ((7.3, 0.9), (7.1, 0.9)), ((5.5, 0.9), (5.3, 0.9))]
    for a, b in arrows:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color="#245B85"))
    ax.text(0.1, 0.6, "Kho: 40 văn bản,\n6.221 đoạn Khoản,\n2.149 đoạn Điều,\nmỗi đoạn có\nvalid_from / valid_to", fontsize=8.5,
            va="center")
    fig.tight_layout()
    fig.savefig(FIG / "h1_pipeline.png", dpi=200)
    plt.close(fig)


def rq1() -> None:
    s = json.loads((ROOT / "reports/g7/scores.json").read_text(encoding="utf-8"))
    names = [("so_lieu_du", "Nêu đúng mọi\nsố liệu ↑"), ("trich_khoan", "Trích đúng\nKhoản ↑"),
             ("ngoai_kho", "Trích văn bản\nngoài kho ↓"), ("lap_vong", "Lặp vòng ↓")]
    runs = [("A", "A: gốc"), ("B", "B: gốc + RAG"), ("C", "C: LoRA"), ("D", "D: LoRA + RAG")]
    colors = ["#BBBBBB", "#7FA7CC", "#E8B27A", "#245B85"]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    w = 0.2
    for j, (run, lab) in enumerate(runs):
        vals = [100 * s["chi_so"][n]["luot"][run]["gop"]["gia_tri"] for n, _ in names]
        bars = ax.bar([i + (j - 1.5) * w for i in range(len(names))], vals, w, label=lab, color=colors[j])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", fontsize=7.5)
    ax.set_xticks(range(len(names)), [lab for _, lab in names])
    ax.set_ylabel("% câu (test)")
    ax.set_ylim(0, 105)
    ax.legend(ncol=4, fontsize=8.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "h3_rq1.png", dpi=200)
    plt.close(fig)


def rq3() -> None:
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    labels = ["Tìm kiếm:\nlấy nhầm bản cũ\n(36 câu)", "B: nêu số liệu\nbản cũ (21 câu)", "D: nêu số liệu\nbản cũ (21 câu)"]
    co = [0, 4.8, 0.0]
    bo = [32 / 36 * 100, 61.9, 33.3]
    x = range(3)
    b1 = ax.bar([i - 0.18 for i in x], co, 0.36, label="Có lọc hiệu lực", color="#245B85")
    b2 = ax.bar([i + 0.18 for i in x], bo, 0.36, label="Bỏ lọc hiệu lực", color="#E8B27A")
    for b, v in list(zip(b1, co)) + list(zip(b2, bo)):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%", ha="center", fontsize=8.5)
    ax.set_xticks(list(x), labels, fontsize=8.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("%")
    ax.legend(fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "h4_rq3.png", dpi=200)
    plt.close(fig)


def g8() -> None:
    j = json.loads((ROOT / "reports/g8/judge_scores.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(7.5, 3.3))
    labels = ["Tìm đủ căn cứ\n(câu thường)", "D: đạt nội dung\n(trong phạm vi)", "B: đạt nội dung\n(trong phạm vi)",
              "D: đạt nội dung\n(biến thể)"]
    truoc = [65.7, 100 * j["dat"]["D"]["trong_pham_vi"]["gia_tri"], 100 * j["dat"]["B"]["trong_pham_vi"]["gia_tri"],
             100 * j["dat"]["D"]["bien_the"]["gia_tri"]]
    sau = [82.8, 100 * j["dat"]["D_g8"]["trong_pham_vi"]["gia_tri"], 100 * j["dat"]["B_g8"]["trong_pham_vi"]["gia_tri"],
           100 * j["dat"]["D_g8"]["bien_the"]["gia_tri"]]
    x = range(4)
    b1 = ax.bar([i - 0.18 for i in x], truoc, 0.36, label="5 đoạn theo Khoản (G7)", color="#7FA7CC")
    b2 = ax.bar([i + 0.18 for i in x], sau, 0.36, label="Mở rộng lên Điều (G8)", color="#245B85")
    for b, v in list(zip(b1, truoc)) + list(zip(b2, sau)):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}", ha="center", fontsize=8)
    ax.set_xticks(list(x), labels, fontsize=8.5)
    ax.set_ylim(0, 105)
    ax.set_ylabel("%")
    ax.legend(fontsize=8.5, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "h5_g8.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    pipeline()
    rq1()
    rq3()
    g8()
    shutil.copy(ROOT / "reports/g6/plots/loss_train_dev.png", FIG / "h2_loss_g6.png")
    print("->", ", ".join(sorted(p.name for p in FIG.iterdir())))
