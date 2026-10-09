# %% [markdown]
# # EDA kho văn bản luật giao thông đường bộ
#
# Phần A của mục 6 bản thiết kế dự án. Dữ liệu: `data/processed/legal_units_versioned.jsonl` (sau đợt làm sạch 2).
# Thời điểm phân tích T = 01/10/2026; "có hiệu lực" tính bằng `lawproc.validity.in_force_at` (có xét ngoại lệ).
# Mỗi phân tích kết thúc bằng **Phát hiện → hành động**. Số liệu máy đọc lưu ở `reports/eda/summary.json`.
# Bản ghi có điều kiện cần được đối chiếu với điều kiện áp dụng trước khi trả lời câu hỏi pháp lý.
#
# **Chạy lại từ thư mục gốc:** môi trường Python 3.13 cần các thư viện đã ghim trong `requirements.txt`
# và hai `tokenizer.json` tại đường dẫn `config.TOKENIZERS` (không cần trọng số mô hình).
# Đăng ký kernel cho Python của dự án rồi tạo/chạy notebook bằng các lệnh sau
# (Linux/macOS: thay `py -3.13` bằng Python của môi trường):
#
# ```powershell
# py -3.13 -m ipykernel install --user --name python313-traffic-law --display-name "Python 3.13 (traffic-law)"
# py -3.13 scripts/build_notebook.py notebooks/01_eda_kho_luat.py
# py -3.13 -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=python313-traffic-law --ExecutePreprocessor.timeout=3600 notebooks/01_eda_kho_luat.ipynb
# ```
# Môi trường hiện tại đã có thư viện/kernel/tokenizer; không tải thêm để thực hiện notebook.
#
# **Đơn vị thống kê:** E1–E10 dùng một bản đại diện mới nhất cho mỗi `unit_id` có hiệu lực tại T.
# Đây là thống kê mô tả, không chứng minh nội dung mới nhất áp dụng chung cho mọi đối tượng.
# `live_all` giữ mọi phiên bản có hiệu lực; sáu bản thuộc ba `unit_id` nhiều nhánh được hiển thị riêng bên dưới
# và đo token riêng ở E3. Ghép Khoản–Điểm dưới đây chỉ tạo ứng viên đo độ dài, chưa tạo đoạn pháp lý dùng cho RAG;
# khi triển khai phải ghép các phiên bản tương thích và giữ đầy đủ điều kiện áp dụng.

# %%
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

import hashlib
import math

import matplotlib.pyplot as plt
import pandas as pd

from lawproc import config, eda
from lawproc.structure import is_closing_line
from lawproc.validity import in_force_at

T = config.CUTOFF
FIG = ROOT / "reports" / "eda" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
pd.set_option("display.max_colwidth", 120)
pd.set_option("display.max_rows", 80)


def save(fig, name):
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)


def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))

# %%
recs = [json.loads(x) for x in (config.PROCESSED / "legal_units_versioned.jsonl").open(encoding="utf-8")]
nhom = {r["doc_id"]: r["nhom"] for r in read_csv(config.MANIFEST)}
nhom.update({k: v["nhom"] for k, v in config.DERIVED_DOCS.items()})
method = {r["doc_id"]: r["method"] for r in read_csv(config.PROCESSED / "assembly_report.csv")}
for r in recs:
    r["in_force"], r["dieu_kien_hl"] = in_force_at(r, T)
    r["nhom"] = nhom[r["doc_id"]]
    r["van_ban_sua_doi"] = r["doc_id"] in config.AMENDING_DOCS
df = pd.DataFrame(recs)
live_all = df[df["in_force"]].reset_index(drop=True)
variants = live_all[live_all.duplicated("unit_id", keep=False)].copy()
# Đại diện mới nhất cho số liệu theo đơn vị. Các nhánh cũ có điều kiện vẫn được giữ trong live_all/variants.
live = (live_all.sort_values(["unit_id", "valid_from", "version_id"])
        .drop_duplicates("unit_id", keep="last").reset_index(drop=True))
print(f"{len(df)} bản ghi, {df['doc_id'].nunique()} văn bản; {len(live_all)} phiên bản có hiệu lực tại {T}, "
      f"{len(live)} unit_id phân biệt; {len(variants)} phiên bản thuộc {variants['unit_id'].nunique()} "
      f"unit_id có nhiều nhánh; {int(live_all['dieu_kien_hl'].notna().sum())} phiên bản kèm điều kiện")
with pd.option_context("display.max_colwidth", None):
    display(variants[["unit_id", "version_id", "valid_from", "valid_to", "dieu_kien_hl"]])

# %% [markdown]
# ## E1. Quy mô kho

# %%
e1_doc = (live.groupby(["nhom", "doc_id"])["level"].value_counts().unstack(fill_value=0)
          .reindex(columns=["dieu", "khoan", "diem", "phu_luc"], fill_value=0))
e1_doc["tong"] = e1_doc.sum(axis=1)
e1_doc.sort_values("tong", ascending=False)

# %%
e1_nhom = live.groupby("nhom").agg(van_ban=("doc_id", "nunique"), don_vi=("unit_id", "size")).sort_values("don_vi")
fig, ax = plt.subplots(figsize=(8, 5))
e1_nhom["don_vi"].plot.barh(ax=ax)
ax.set_xlabel(f"Số đơn vị có hiệu lực tại {T}")
ax.set_ylabel("")
ax.set_title("E1. Quy mô theo nhóm chủ đề")
save(fig, "e1_quy_mo_nhom.png")
e1_nhom

# %%
sd = live[live["van_ban_sua_doi"]]
print(f"Văn bản sửa đổi: {sd['doc_id'].nunique()} văn bản, {len(sd)} đơn vị của chính văn bản đó "
      f"(phần lớn là câu chỉ dẫn 'sửa đổi, bổ sung…'; nội dung mới đã được áp vào văn bản gốc)")

# %% [markdown]
# **Phát hiện → hành động (E1):**
#
# - **Phát hiện:** 18.790 phiên bản của 33 văn bản; tại T có 17.423 phiên bản có hiệu lực nhưng chỉ 17.420 `unit_id`, gồm 2.195 Điều, 6.932 Khoản, 8.147 Điểm và 146 phụ lục → **Hành động:** ở bước lập chỉ mục, tách địa chỉ đơn vị khỏi phiên bản và lưu ngày hiệu lực cùng nguồn trích dẫn.
# - **Phát hiện:** 6 phiên bản thuộc 3 địa chỉ nhiều nhánh, tổng cộng 16 phiên bản có ghi chú điều kiện → **Hành động:** ở bước lọc truy hồi, đối chiếu điều kiện và đối tượng; không dùng quy tắc chọn bản mới nhất làm kết luận pháp lý chung.
# - **Phát hiện:** nhóm Tai nạn có 6.986 đơn vị, còn Tốc độ có 16; 9 văn bản sửa đổi chứa 1.051 đơn vị → **Hành động:** ở bước tạo kho RAG, dùng phạm vi đề xuất E2 và tách chỉ dẫn sửa đổi khỏi nội dung đích đã áp sửa đổi; bộ eval lấy phân bổ theo căn bậc hai thay vì tỷ lệ thô.

# %% [markdown]
# ## E2. Phạm vi thực của BLDS 2015 và BLHS (VBHN 135)
#
# Đề xuất phạm vi: BLDS Chương XX (Điều 584–608, bồi thường thiệt hại ngoài hợp đồng, có Điều 601 nguồn nguy hiểm cao độ);
# BLHS Điều 260–266 (các tội về giao thông đường bộ). Đây là phạm vi hỗ trợ đề xuất, cần xác nhận pháp lý
# trước khi dùng làm tiêu chí loại trừ; Chương XX BLDS rộng hơn riêng giao thông đường bộ.

# %%
SCOPE = {"blds_2015": (584, 608), "vbhn_135_2025_blhs": (260, 266)}


def in_scope(doc_id, dieu):
    rng = SCOPE.get(doc_id)
    if not rng:
        return True
    m = re.match(r"\d+", dieu or "")
    return bool(m) and rng[0] <= int(m.group()) <= rng[1]


live["trong_pham_vi"] = [in_scope(d, x) for d, x in zip(live["doc_id"], live["dieu"])]
big = live[live["doc_id"].isin(SCOPE)]
print(f"BLDS + BLHS: {len(big)} / {len(live)} đơn vị có hiệu lực ({len(big) / len(live):.1%}); "
      f"trong phạm vi đề xuất: {int(big['trong_pham_vi'].sum())}")
e2 = big.groupby(["doc_id", "trong_pham_vi"]).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(7, 3))
e2.rename(columns={False: "Ngoài phạm vi", True: "Trong phạm vi"}).plot.barh(stacked=True, ax=ax)
ax.set_xlabel("Số đơn vị đại diện")
ax.set_ylabel("")
ax.set_title("E2. Đơn vị BLDS, BLHS trong và ngoài phạm vi đề xuất")
save(fig, "e2_pham_vi_blds_blhs.png")
e2

# %%
check = big[(big["level"] == "dieu")]
check = check[[(SCOPE[d][0] - 5) <= int(re.match(r"\d+", x).group()) <= (SCOPE[d][1] + 5)
               for d, x in zip(check["doc_id"], check["dieu"])]]
check[["doc_id", "dieu", "title", "trong_pham_vi"]]

# %% [markdown]
# **Phát hiện → hành động (E2):**
#
# - **Phát hiện:** BLDS và BLHS chiếm 6.986/17.420 đơn vị đại diện (40,1%), nhưng khoảng đề xuất chỉ giữ 213 đơn vị và để ngoài phạm vi 6.773 đơn vị → **Hành động:** ở bước xây kho thử nghiệm, gắn cờ phạm vi thay vì xóa dữ liệu; nhóm pháp lý xác nhận phạm vi trước khi chốt.
# - **Phát hiện:** bảng tiêu đề có 25 Điều BLDS 584–608 và 7 Điều BLHS 260–266; Điều 267 BLHS chuyển sang đường sắt → **Hành động:** giữ hai khoảng đang đề xuất; dùng BLDS như nguồn hỗ trợ bồi thường dân sự, không gán toàn bộ Chương XX là luật giao thông.

# %% [markdown]
# ## E3. Độ dài đơn vị (từ, token Qwen3.5-9B, token bge-m3)
#
# `so_tu` dùng regex `\w+`: đếm các đơn vị chữ/số, gần với âm tiết viết cách ở tiếng Việt,
# không phải số từ đã tách bằng Pyvi. Pyvi chỉ dùng cho phân tích từ vựng E7.

# %%
tokenizer_provenance = [
    {"key": "qwen", "name": "Qwen3.5-9B",
     "url": "https://huggingface.co/Qwen/Qwen3.5-9B/resolve/main/tokenizer.json",
     "bytes": 12807982, "sha256": "5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42"},
    {"key": "bge_m3", "name": "bge-m3",
     "url": "https://huggingface.co/BAAI/bge-m3/resolve/main/tokenizer.json",
     "bytes": 17098108, "sha256": "21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08"},
]
for info in tokenizer_provenance:
    p = config.TOKENIZERS[info["key"]]
    assert p.stat().st_size == info["bytes"] and hashlib.sha256(p.read_bytes()).hexdigest() == info["sha256"]
    print(info["name"], info["url"], info["bytes"], info["sha256"])
texts = live["text"].tolist()
live["so_tu"] = [eda.count_words(t) for t in texts]
live["tok_qwen"] = eda.count_tokens(texts, config.TOKENIZERS["qwen"])
live["tok_bge"] = eda.count_tokens(texts, config.TOKENIZERS["bge_m3"])
lv = live[live["level"].isin(["dieu", "khoan", "diem", "phu_luc"])]
cols = ["so_tu", "tok_qwen", "tok_bge"]
e3 = lv.groupby("level")[cols].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0)
display(e3)
variant_lengths = variants[["unit_id", "version_id", "valid_from", "dieu_kien_hl"]].copy()
variant_lengths["tok_qwen_body"] = eda.count_tokens(variants["text"].tolist(), config.TOKENIZERS["qwen"])
variant_lengths["tok_bge_body"] = eda.count_tokens(variants["text"].tolist(), config.TOKENIZERS["bge_m3"])
with pd.option_context("display.max_colwidth", None):
    display(variant_lengths)
print("Bảng theo level đo riêng text nguồn: chưa có title, địa chỉ, điều kiện, metadata hay prompt.")

# %%
# Ứng viên cắt đoạn theo Khoản: tiêu đề Điều + nội dung Khoản + mọi Điểm trực thuộc.
# Các nhánh có điều kiện được đo riêng khi triển khai chunk; bản đại diện ở đây không thay thế điều kiện pháp lý.
diem = live[live["level"] == "diem"].copy()
diem["khoan_id"] = diem["unit_id"].str.rsplit(":", n=1).str[0]
extra = diem.groupby("khoan_id")["text"].agg("\n".join)
kh = live[live["level"] == "khoan"].set_index("unit_id")
dieu_heading = (live[live["level"] == "dieu"].set_index("unit_id")["title"])
kh_heading = dieu_heading.reindex(kh.index.str.rsplit(":", n=1).str[0]).fillna("")
kh_text = (kh_heading.to_numpy() + "\n" + kh["text"] + "\n" + extra.reindex(kh.index).fillna("")).str.strip()
kh_tok = pd.Series(eda.count_tokens(kh_text.tolist(), config.TOKENIZERS["bge_m3"]), index=kh.index)
kh_body_text = (kh["text"] + "\n" + extra.reindex(kh.index).fillna("")).str.strip()
kh_body_tok = pd.Series(eda.count_tokens(kh_body_text.tolist(), config.TOKENIZERS["bge_m3"]), index=kh.index)
print("Khoản + Điểm chỉ text nguồn (chưa có tiêu đề Điều):",
      kh_body_tok.describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0).to_dict(),
      ">512:", int((kh_body_tok > 512).sum()))
print("Chênh token sau khi ghép tiêu đề Điều (không phải phép cộng token độc lập):",
      (kh_tok - kh_body_tok).describe(percentiles=[0.5, 0.95]).round(0).to_dict())
print(kh_tok.describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0))
for lim in (256, 512, 1024, 8192):
    print(f"khoản + điểm > {lim} token bge-m3: {int((kh_tok > lim).sum())}")
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(kh_tok.clip(lower=1), bins=[2 ** i for i in range(0, 15)])
ax.set_xscale("log", base=2)
ax.set_xlabel("Số token bge-m3 (khoản kèm các điểm)")
ax.set_ylabel("Số khoản")
ax.set_title("E3. Độ dài ứng viên đoạn theo Khoản")
save(fig, "e3_do_dai_khoan.png")
core_kh_ids = kh.index[[in_scope(d, a) and d not in config.AMENDING_DOCS and d not in config.NON_LEGAL
                        for d, a in zip(kh["doc_id"], kh["dieu"])]]
core_kh_tok = kh_tok.reindex(core_kh_ids)
print("Khoản kèm Điểm và tiêu đề Điều, trong phạm vi RAG đề xuất:",
      core_kh_tok.describe(percentiles=[0.5, 0.9, 0.95, 0.99]).round(0).to_dict(),
      ">512:", int((core_kh_tok > 512).sum()))

# %%
print("Đơn vị dài nhất (token bge-m3):")
display(live.nlargest(15, "tok_bge")[["unit_id", "level", "loai_phu_luc", "so_tu", "tok_bge"]])
short = lv[lv["so_tu"] < 5]
print(f"Đơn vị dưới 5 từ: {len(short)}")
short["level"].value_counts()

# %% [markdown]
# **Phát hiện → hành động (E3):**
#
# - **Phát hiện:** 6.932 ứng viên Khoản kèm Điểm và tiêu đề Điều có trung vị 76, P95 337 token bge-m3; 111 ứng viên vượt 512 → **Hành động:** ở bước thiết kế chunk, lấy 512 token làm trần thử nghiệm; tách theo Điểm hoặc ranh giới câu đối với ứng viên dài, giữ địa chỉ và nguồn.
# - **Phát hiện:** trong phạm vi RAG đề xuất còn 3.831 ứng viên, P95 390 token và 93 vượt 512 → **Hành động:** ưu tiên rà soát 93 trường hợp này khi xây chunk; đo lại cả metadata, điều kiện và prompt vì thống kê có tiêu đề Điều vẫn chưa bao gồm các phần đó.
# - **Phát hiện:** 2.281 đơn vị có dưới 5 từ; sáu bản thuộc ba địa chỉ có điều kiện đã được đo riêng → **Hành động:** ghép đơn vị ngắn với ngữ cảnh cha; với nhánh điều kiện, chỉ ghép phiên bản tương thích sau kiểm tra, không triển khai trực tiếp phép ghép bản đại diện đang dùng để mô tả độ dài.
# - **Phát hiện:** chỉ text Khoản–Điểm có trung vị 62, P95 318 token bge-m3 và 98 ứng viên vượt 512; thêm tiêu đề Điều làm tăng trung vị chênh token 11 và P95 chênh 34 → **Hành động:** ở bước định ngân sách, đo chuỗi chunk hoàn chỉnh bằng tokenizer thay vì cộng số token từng phần; dành thêm chỗ cho địa chỉ, điều kiện và prompt chưa được đo ở đây.

# %% [markdown]
# ## E4. Mức phạt NĐ 168/2024 (bản có hiệu lực tại T)

# %%
n168 = live[live["doc_id"] == "nd_168_2024"]
dieu_title = dict(zip(n168.loc[n168["level"] == "dieu", "dieu"], n168.loc[n168["level"] == "dieu", "title"]))
rows = []
for uid, dieu, text in zip(n168["unit_id"], n168["dieu"], n168["text"]):
    if ":k" not in uid or uid.count(":") != 2:
        continue
    f = eda.extract_fine(text)
    if f:
        n_hv = n168.loc[n168["unit_id"].str.startswith(uid + ":"), "unit_id"].nunique()
        rows.append({"unit_id": uid, "dieu": dieu, "phuong_tien": eda.vehicle_group(dieu_title.get(dieu, "")),
                     "min": f[0], "max": f[1], "so_diem_cau_truc": n_hv})
fines = pd.DataFrame(rows)
e4 = fines.groupby("phuong_tien").agg(khung=("unit_id", "size"), diem_cau_truc=("so_diem_cau_truc", "sum"),
                                       min_thap_nhat=("min", "min"), max_cao_nhat=("max", "max"),
                                       max_trung_vi=("max", "median"))
print(f"{len(fines)} Khoản có khung phạt đầu tiên khớp regex, {int(fines['so_diem_cau_truc'].sum())} Điểm cấu trúc; "
      f"mức đầu tiên từ {fines['min'].min():,} đến {fines['max'].max():,} đồng. "
      "Không phải kiểm kê đầy đủ mức phạt cá nhân/tổ chức hay số hành vi pháp lý.")
e4

# %%
fig, ax = plt.subplots(figsize=(8, 4))
groups = sorted(fines["phuong_tien"].unique())
ax.boxplot([fines.loc[fines["phuong_tien"] == g, "max"] for g in groups], tick_labels=groups, vert=False)
ax.set_xscale("log")
ax.set_xlabel("Mức phạt tối đa của khung (đồng, thang log)")
ax.set_title("E4. Khung phạt NĐ 168 theo nhóm phương tiện")
save(fig, "e4_muc_phat.png")

# %%
pts = Counter(p for p in (eda.extract_points(t) for t in n168["text"]) if p)
fig, ax = plt.subplots(figsize=(5, 3))
ax.bar([str(k) for k in sorted(pts)], [pts[k] for k in sorted(pts)])
ax.set_xlabel("Số điểm GPLX bị trừ")
ax.set_ylabel("Số bản đại diện khớp mức đầu tiên")
ax.set_title("E4. Điểm trừ GPLX")
save(fig, "e4_tru_diem.png")
dict(sorted(pts.items()))

# %% [markdown]
# **Phát hiện → hành động (E4):**
#
# - **Phát hiện:** regex tìm khung tiền đầu tiên trong 190 Khoản NĐ168, từ 100.000 đến 75.000.000 đồng; bên dưới có 574 Điểm cấu trúc → **Hành động:** ở bước trích thuộc tính, đối chiếu từng Khoản cùng Điểm, đối tượng và điều kiện; không xem 574 Điểm là số hành vi pháp lý duy nhất hoặc khung đầu tiên là toàn bộ biểu phạt.
# - **Phát hiện:** phép lấy mức trừ điểm đầu tiên cho ra 48 bản đại diện: 2 điểm (18), 3 (2), 4 (9), 6 (9), 8 (2), 10 (8) → **Hành động:** trong eval mức phạt/tình huống, kiểm tra câu dẫn bổ sung và phạm vi áp dụng; bổ sung parser nhiều mức trước khi tự động lập bảng đầy đủ.

# %% [markdown]
# ## E5. Sửa đổi, bổ sung, bãi bỏ

# %%
hl = {r["doc_id"]: r["hl_chot"] for r in read_csv(config.PROCESSED / "effective_dates.csv")}
ok = pd.DataFrame([r for r in read_csv(config.PROCESSED / "amendments_reviewed.csv") if r["status"] == "duyet"])
ok["ngay"] = [h or hl[a] for h, a in zip(ok["hl_rieng"], ok["amend_doc_id"])]
e5 = pd.crosstab(ok["target_doc_id"], ok["action"], margins=True)
fig, ax = plt.subplots(figsize=(8, 4))
e5.drop(index="All", columns="All").rename(columns={
    "bai_bo": "Bãi bỏ", "bo_sung": "Bổ sung", "sua_doi": "Sửa đổi",
    "thay_the_van_ban": "Thay thế văn bản",
}).plot.barh(stacked=True, ax=ax)
ax.set_xlabel("Số dòng sửa đổi đã duyệt")
ax.set_ylabel("")
ax.legend(title="")
ax.set_title("E5. Dòng sửa đổi đã duyệt theo văn bản đích")
save(fig, "e5_sua_doi.png")
e5

# %%
pd.crosstab(ok["amend_doc_id"], ok["ngay"])

# %%
amended = df[df["source_doc_id"] != df["doc_id"]]
print(f"{len(amended)} bản ghi sinh từ sửa đổi; {int((~amended['noi_dung_doi']).sum())} không đổi nội dung")
base_units = set(df.loc[df["source_doc_id"] == df["doc_id"], "unit_id"])
rq3 = amended[amended["noi_dung_doi"] & amended["level"].isin(["khoan", "diem"]) & amended["unit_id"].isin(base_units)]
print(f"Khoản/điểm có cả bản gốc và bản sửa khác nội dung (nguồn câu hỏi RQ3): {rq3['unit_id'].nunique()}")
rq3.groupby("doc_id")["unit_id"].nunique()

# %% [markdown]
# **Phát hiện → hành động (E5):**
#
# - **Phát hiện:** 505 dòng sửa đổi được duyệt gồm 428 sửa đổi, 53 bổ sung, 23 bãi bỏ và 1 thay thế văn bản → **Hành động:** ở bước truy hồi theo thời gian, sử dụng trạng thái đã duyệt và ngày hiệu lực của từng dòng, không áp dụng mọi dòng ứng viên.
# - **Phát hiện:** có 1.004 phiên bản sinh từ sửa đổi và 661 địa chỉ Khoản/Điểm có cả bản gốc lẫn bản sửa khác nội dung → **Hành động:** ở bước thiết kế eval RQ3, chọn cặp trước/sau từ 661 địa chỉ này, kiểm tra điều kiện hiệu lực rồi duyệt câu hỏi thủ công; hiện chưa sinh câu hỏi.

# %% [markdown]
# ## E6. Dòng thời gian hiệu lực 2024–2029

# %%
docs = sorted(df["doc_id"].unique(), key=lambda d: hl[d])
end = {d: (None if df.loc[df["doc_id"] == d, "valid_to"].isna().any() else df.loc[df["doc_id"] == d, "valid_to"].max())
       for d in docs}
extensions = {d: max((ex["den_ngay"] for r in recs if r["doc_id"] == d
                      for ex in r["hl_ngoai_le"] if ex["vai_tro"] == "gia_han" and ex["den_ngay"]), default=None)
              for d in docs}
x0, x1 = pd.Timestamp("2024-01-01"), pd.Timestamp("2030-01-01")
fig, ax = plt.subplots(figsize=(10, 9))
for y, d in enumerate(docs):
    s = max(pd.Timestamp(hl[d]), x0)
    e = pd.Timestamp(end[d]) if end[d] else x1
    ax.plot([s, e], [y, y], lw=4, color="tab:blue" if end[d] is None else "tab:gray")
    if extensions[d] and end[d]:
        ax.plot([e, pd.Timestamp(extensions[d])], [y, y], lw=4, color="tab:green")
    for day in sorted(set(ok.loc[ok["target_doc_id"] == d, "ngay"])):
        ax.plot(pd.Timestamp(day), y, "o", color="tab:orange", ms=5)
    for day in sorted({ex["tu_ngay"] or ex["den_ngay"] for r in recs if r["doc_id"] == d
                       for ex in r["hl_ngoai_le"]}):
        ax.plot(pd.Timestamp(day), y, "D", color="tab:red", ms=5)
ax.axvline(pd.Timestamp(T), color="black", ls="--")
ax.set_yticks(range(len(docs)), docs, fontsize=7)
ax.set_xlim(x0, x1)
ax.set_title("E6. Khoảng tổng quan văn bản; lục: gia hạn tới mốc loại trừ; cam: sửa đổi; đỏ: ngoại lệ; nét đứt: T")
save(fig, "e6_dong_thoi_gian.png")

# %%
fut = []
for r in recs:
    if r["valid_from"] > T:
        fut.append((r["valid_from"], r["doc_id"], "bắt đầu hiệu lực"))
    for ex in r["hl_ngoai_le"]:
        day = ex["tu_ngay"] or ex["den_ngay"]
        if day > T:
            fut.append((day, r["doc_id"], ex["loai"]))
display(pd.DataFrame(fut, columns=["ngay", "doc_id", "su_kien"]).value_counts().sort_index())
print("Gia hạn có ngày kết thúc loại trừ:", {d: x for d, x in extensions.items() if x})
print("Đồ thị tổng quan theo văn bản, không chứng minh mọi điều/khoản cùng trạng thái ở mọi ngày.")

# %% [markdown]
# **Phát hiện → hành động (E6):**
#
# - **Phát hiện:** TT12 có ngoại lệ gia hạn tới mốc kết thúc loại trừ 01/03/2027 (còn áp dụng tới hết 28/02/2027 cho đơn vị đủ điều kiện) → **Hành động:** ở bước lọc hiệu lực, gọi `in_force_at` trên từng phiên bản; không suy trạng thái từng quy định từ đoạn tổng quan theo văn bản.
# - **Phát hiện:** có 43 lượt sự kiện tương lai theo bản ghi: 5 tại 01/01/2027, 20 tại 01/03/2027, 1 tại 01/07/2027, 12 tại 01/01/2028 và 5 tại 01/01/2029 → **Hành động:** ở bước kiểm thử thời gian, kiểm tra ngày ngay trước và đúng các mốc này; khử trùng khi lập lịch sự kiện thực vì số lượt không phải số sự kiện pháp lý độc lập.

# %% [markdown]
# ## E7. Từ vựng (tách từ bằng pyvi)

# %%
from pyvi import ViTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

STOP = ["của", "và", "các", "về", "đối_với", "với", "trong", "theo", "quy_định", "việc", "được", "này", "có", "là",
        "cho", "tại", "khi", "hoặc", "không", "phải", "từ", "đến", "những", "một", "do", "trường_hợp", "điều",
        "khoản", "điểm", "sau", "đây", "như", "thì", "trên", "người", "bằng"]
body = live[live["trong_pham_vi"] & (live["loai_phu_luc"] != "mau_bieu") & ~live["van_ban_sua_doi"]]
seg = {g: ViTokenizer.tokenize(" ".join(t)).lower() for g, t in body.groupby("nhom")["text"]}
vec = TfidfVectorizer(token_pattern=r"(?u)\b\w*[^\W\d_]\w*\b", stop_words=STOP, sublinear_tf=True)
X = vec.fit_transform(list(seg.values()))
terms = vec.get_feature_names_out()
top = {g: [terms[j].replace("_", " ") for j in X[i].toarray()[0].argsort()[::-1][:15]] for i, g in enumerate(seg)}
display(pd.DataFrame(top))

# Hình thứ 10: năm thuật ngữ TF-IDF nổi bật nhất mỗi nhóm (mỗi nhóm là một tài liệu phân tích).
fig, axes = plt.subplots(math.ceil(len(seg) / 3), 3,
                         figsize=(16, 3.4 * math.ceil(len(seg) / 3)), layout="constrained")
for i, (g, words) in enumerate(top.items()):
    ax = axes.flat[i]
    ax.barh(words[:5][::-1], [X[i, list(terms).index(w.replace(" ", "_"))] for w in words[:5][::-1]])
    ax.set_title(g)
    ax.tick_params(axis="y", labelsize=8)
for ax in axes.flat[len(seg):]:
    ax.axis("off")
fig.suptitle("E7. Thuật ngữ nổi bật theo nhóm (TF-IDF)")
save(fig, "e7_tu_vung.png")

# %%
PAIRS = [("xe mô tô", r"xe máy(?! chuyên dùng)"), ("giấy phép lái xe", r"bằng lái"), ("nồng độ cồn", r"rượu bia|rượu, bia"),
         ("xe ô tô", r"xe hơi"), ("cảnh sát giao thông", r"\bcsgt\b"), ("đèn tín hiệu", r"đèn đỏ|đèn xanh"),
         ("tạm giữ phương tiện", r"giam xe|giữ xe"), ("mũ bảo hiểm", r"nón bảo hiểm")]
corpus = "\n".join(body["text"]).lower()
pair_counts = pd.DataFrame([{"phap_ly": a, "so_lan": corpus.count(a), "doi_thuong": b,
                             "so_lan_doi_thuong": len(re.findall(b, corpus))} for a, b in PAIRS])
pair_counts

# %% [markdown]
# **Phát hiện → hành động (E7):**
#
# - **Phát hiện:** trong tập text đã lọc, “giấy phép lái xe” xuất hiện 835 lần nhưng “bằng lái” 0 lần; “xe ô tô” 914 lần nhưng “xe hơi” 0 lần; “mũ bảo hiểm” 28 lần nhưng “nón bảo hiểm” 0 lần → **Hành động:** ở bước xử lý truy vấn, thêm ánh xạ từ đời thường sang thuật ngữ và kiểm thử câu diễn đạt khác nhau; không dùng đồng nghĩa để suy cùng phạm vi pháp lý.
# - **Phát hiện:** “xe mô tô” có 253 lần, mẫu “xe máy” có 125; “đèn tín hiệu” có 127, mẫu “đèn đỏ/đèn xanh” có 39 → **Hành động:** ở bước eval truy hồi, lấy biến thể ngôn ngữ làm nhóm kiểm tra riêng và đối chiếu loại phương tiện/tình huống trước khi mở rộng truy vấn.
# - **Phát hiện:** TF-IDF được tính trên 12 tài liệu gộp theo nhóm; top 5 của Biển báo có “w”, “ie”, còn Bảo hiểm có “thần kinh”, “khớp” → **Hành động:** ở bước kiểm tra kho, rà mã biển, nhiễu OCR và nội dung bảng chuyên ngành; không diễn giải thứ hạng này là nhu cầu người dùng hay tần suất trên từng văn bản.

# %% [markdown]
# ## E8. Đơn vị gần trùng giữa các văn bản

# %%
cand = live[(live["so_tu"] >= 30) & (live["loai_phu_luc"] != "mau_bieu") & live["trong_pham_vi"]
            & ~live["van_ban_sua_doi"]].reset_index(drop=True)
pairs = eda.near_duplicates(cand["text"].tolist(), cand["doc_id"].tolist(), threshold=0.9)
print(f"{len(cand)} đơn vị xét; {len(pairs)} cặp gần trùng (cosine TF-IDF ký tự ≥ 0,9) khác văn bản")
if pairs:
    e8 = pd.DataFrame([{"a": cand["unit_id"][i], "b": cand["unit_id"][j], "cos": s} for i, j, s in pairs])
    e8["cap"] = e8["a"].str.split(":").str[0] + " ~ " + e8["b"].str.split(":").str[0]
    display(e8["cap"].value_counts())
    display(e8.head(20))

# %% [markdown]
# **Phát hiện → hành động (E8):**
#
# - **Phát hiện:** 5.146 đơn vị đủ điều kiện có 89 cặp khác văn bản đạt cosine TF-IDF ký tự ≥ 0,9 → **Hành động:** ở bước lập chỉ mục, gắn nhóm gần trùng để tránh kết quả lặp nhưng giữ mọi nguồn, ngày hiệu lực và điều kiện; không tự xóa theo độ giống chữ.
# - **Phát hiện:** cặp NĐ168–NĐ336 chiếm 48/89 cặp; bảng ví dụ có Luật36 Điều 27 Khoản 2 và QCVN Điều 7 Khoản 1 đạt cosine 1,0 → **Hành động:** ở bước xếp hạng truy hồi, duyệt những cặp này để chọn nguồn thích hợp với câu hỏi; similarity không xác nhận hai quy định tương đương pháp lý.

# %% [markdown]
# ## E9. Tham chiếu chéo

# %%
body9 = live[live["level"].isin(["dieu", "khoan", "diem"]) & ~live["van_ban_sua_doi"]]
refs = pd.DataFrame([{"unit_id": u, "doc_id": d, **ref} for u, d, t in zip(body9["unit_id"], body9["doc_id"], body9["text"])
                     for ref in eda.find_references(t)])
print(f"{len(refs)} tham chiếu đánh số khớp regex; {refs['unit_id'].nunique()} / {len(body9)} đơn vị "
      f"({refs['unit_id'].nunique() / len(body9):.1%}) có ít nhất một tham chiếu")
display(refs["loai"].value_counts())
# Ví dụ chỉ để rà mẫu parser; chưa phân giải địa chỉ đích hay khẳng định liên kết đầy đủ.
reference_examples = []
for kind in ("noi_bo", "ngoai"):
    for row in refs[refs["loai"] == kind].head(3).to_dict(orient="records"):
        text = body9.loc[body9["unit_id"] == row["unit_id"], "text"].iloc[0]
        matches = [(match, parsed) for match, parsed in zip(eda.REF.finditer(text), eda.find_references(text))
                   if parsed["loai"] == kind]
        match, parsed = matches[0]
        reference_examples.append({"unit_id": row["unit_id"], **parsed,
                                   "trich_ngu_canh": text[max(0, match.start() - 60):match.end() + 160]})
with pd.option_context("display.max_colwidth", None):
    display(pd.DataFrame(reference_examples))
inner = refs[refs["loai"] == "noi_bo"]
target = inner["doc_id"] + ":d" + inner["dieu"] + inner["khoan"].fillna("").map(lambda k: f":k{k}" if k else "")
fig, ax = plt.subplots(figsize=(8, 5))
target.value_counts().head(15).sort_values().plot.barh(ax=ax)
ax.set_title("E9. Điều/khoản được dẫn nhiều nhất (trong cùng văn bản)")
save(fig, "e9_tham_chieu.png")

# %% [markdown]
# **Phát hiện → hành động (E9):**
#
# - **Phát hiện:** regex khớp 1.540 tham chiếu đánh số trong 1.044/16.241 đơn vị (6,4%), gồm 1.379 nội bộ và 161 bên ngoài → **Hành động:** ở bước truy hồi, thử mở rộng ngữ cảnh theo Điều/Khoản đích và kiểm tra đúng văn bản/phiên bản trước khi đưa vào câu trả lời.
# - **Phát hiện:** 161 kết quả được parser gắn nhãn bên ngoài; phép đếm chỉ bao phủ các mẫu đánh số đã hỗ trợ → **Hành động:** ở bước xây đồ thị tham chiếu, duyệt ví dụ bên ngoài và mở rộng nhận diện tên văn bản; không xem đơn vị không khớp regex là không có tham chiếu hoặc kết quả regex là liên kết đã giải quyết.

# %% [markdown]
# ## E10. Chất lượng sau làm sạch

# %%
PUNCT = set(".,;:!?()[]{}\"'“”‘’/\\%&+-–—…|*#°§<>=_~^@$€₫·•")
odd = Counter(c for t in live["text"] for c in t if not (c.isalnum() or c.isspace() or c in PUNCT))
live["method"] = live["doc_id"].map(method)
e10 = {
    "Đơn vị rỗng (không tiêu đề, không nội dung)": int(((live["text"].str.strip() == "")
                                                       & (live["title"].str.strip() == "")).sum()),
    "Đơn vị có dòng phần kết": int(sum(any(is_closing_line(x) for x in t.splitlines())
                                        for t, lvl in zip(live["text"], live["level"]) if lvl in ("dieu", "khoan", "diem"))),
    "unit_id có hậu tố #": int(live["unit_id"].str.contains("#").sum()),
    "Bản ghi chat_luong = kem": int((live["chat_luong"] == "kem").sum()),
    "Ký tự lạ (tổng số lần)": sum(odd.values()),
}
display(pd.Series(e10))
display(live.groupby("method")["ty_le_am_tiet_loi"].describe(percentiles=[0.5, 0.9, 0.99]).round(4))
print("Ký tự lạ hay gặp:", odd.most_common(20))
print("Nhãn chất lượng là heuristic tỷ lệ âm tiết lạ, không phải độ chính xác OCR. "
      "Ký hiệu Unicode lạ cần kiểm tra ngữ cảnh trước khi sửa.")
annex_all = df[df["level"] == "phu_luc"].drop_duplicates("unit_id", keep="last")
qcvn_annex_titles = annex_all.loc[annex_all["doc_id"] == "qcvn_41_2024", "title"].tolist()
known_qcvn_gap_letters = ["M", "N", "O", "P"]
missing_qcvn_titles = [f"Phụ lục {letter}" for letter in known_qcvn_gap_letters
                      if f"Phụ lục {letter}" not in qcvn_annex_titles]
stub_uids = ["tt_108_2026_bca:pl12", "nd_39_2023:pl1"]
stub_audit = annex_all[annex_all["unit_id"].isin(stub_uids)][["unit_id", "title", "text", "chat_luong"]].copy()
stub_audit["text_characters"] = stub_audit["text"].str.len()
source_gap_audit = {
    "evidence_report": "data/processed/PROCESSING_REPORT.md",
    "scope": "All stored versions, independent of cutoff; known gaps only, not an exhaustive audit",
    "qcvn_annex_titles_present": qcvn_annex_titles,
    "known_qcvn_titles_absent": missing_qcvn_titles,
    "known_stub_units": stub_audit.to_dict(orient="records"),
}
print("Kiểm tra danh sách khoảng trống đã được đối chiếu nguồn tại PROCESSING_REPORT.md:",
      len(missing_qcvn_titles), "phụ lục QCVN không có đơn vị:", missing_qcvn_titles)
with pd.option_context("display.max_colwidth", None):
    display(stub_audit)
print("Độ ngắn/không có đơn vị là bằng chứng văn bản hiện lưu; kết luận thiếu nội dung dựa vào "
      "đối chiếu nguồn ở báo cáo làm sạch, không chỉ từ ngưỡng độ dài. Danh sách không phải kiểm kê đầy đủ.")
fig, ax = plt.subplots(figsize=(7, 3))
for m, g in live.groupby("method"):
    ax.hist(g["ty_le_am_tiet_loi"], bins=100, range=(0, 1), histtype="step", label=m, density=True)
ax.set_yscale("log")
ax.set_xlabel("Tỷ lệ âm tiết lạ theo heuristic (toàn khoảng 0–1)")
ax.legend()
ax.set_title("E10. Chất lượng chữ theo cách trích")
save(fig, "e10_chat_luong.png")

# %% [markdown]
# **Phát hiện → hành động (E10):**
#
# - **Phát hiện:** tập đại diện có 0 đơn vị rỗng cả tiêu đề/nội dung, 0 dòng phần kết lẫn trong Điều/Khoản/Điểm và 0 địa chỉ có hậu tố `#` → **Hành động:** giữ ba kiểm tra này làm cổng kiểm định khi nhập lại dữ liệu; các số 0 không chứng minh nguồn đã đủ.
# - **Phát hiện:** có 19 bản đại diện nhãn `kem` và 733 lượt ký tự ngoài tập cho phép, trong đó “♦” 280, “□” 131, ký hiệu ô chọn riêng “” 77 → **Hành động:** ở bước rà chất lượng, kiểm tra ngữ cảnh và đối chiếu nguồn trước khi sửa; nhãn âm tiết lạ không phải phép đo độ chính xác OCR, ký hiệu toán/ô chọn có thể hợp lệ.
# - **Phát hiện:** 146 phụ lục tại T gồm 98 mẫu biểu và 48 nội dung; kiểm tra toàn bộ phiên bản không tìm thấy 4 phụ lục QCVN M/N/O/P, TT108 `pl12` chỉ có 138 ký tự và NĐ39 `pl1` 76 ký tự → **Hành động:** tách mẫu biểu khi dựng kho RAG; bổ sung nguồn ảnh/bảng và thân phụ lục theo [báo cáo làm sạch](../data/processed/PROCESSING_REPORT.md) trước khi dùng những phần này cho eval hoặc trả lời đầy đủ.

# %% [markdown]
# ## Ma trận đề cho bộ eval thủ công (~150 câu)
#
# Quy tắc: số câu mỗi nhóm tỷ lệ với √(số Điều có hiệu lực trong phạm vi, không tính văn bản sửa đổi và đề thi),
# nhân trọng số 1,5 cho Xử phạt, GPLX, Đăng ký xe; mỗi nhóm tối thiểu 5 câu; chia loại câu theo `eda.LOAI_SPLIT`.
# Đây là đề xuất ban đầu; nhóm điều chỉnh rồi chốt trước khi viết bộ eval.

# %%
core = live[live["trong_pham_vi"] & ~live["van_ban_sua_doi"] & ~live["doc_id"].isin(config.NON_LEGAL)]
cnt = core[core["level"] == "dieu"].groupby("nhom").size()
docs_by = core.groupby("nhom")["doc_id"].agg(lambda s: sorted(set(s)))
matrix = pd.DataFrame(eda.eval_matrix(cnt.to_dict(), docs_by.to_dict(), total=150, floor=5))
out = ROOT / "data" / "eval" / "eval_matrix.csv"
out.parent.mkdir(parents=True, exist_ok=True)
if not out.exists():
    matrix.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Đã tạo bản đề xuất -> {out.relative_to(ROOT)}")
else:
    saved = pd.read_csv(out, encoding="utf-8-sig").fillna("")
    if saved.to_csv(index=False) == matrix.to_csv(index=False):
        print("Ma trận đang lưu khớp bản đề xuất tính lại; giữ nguyên file.")
    else:
        print("Ma trận đang lưu khác bản đề xuất tính lại; giữ nguyên chỉnh sửa thủ công. "
              "Bảng dưới và summary.json chỉ mô tả bản đề xuất tính lại để nhóm đối chiếu.")
print(f"{int(matrix['so_cau'].sum())} suất câu hỏi đề xuất; chưa tạo câu hỏi và chưa duyệt phân bổ")
matrix.pivot_table(index="chu_de", columns="loai_cau", values="so_cau", aggfunc="sum", fill_value=0, margins=True)

# %% [markdown]
# ## Số liệu kiểm chứng và nguồn gốc
#
# `summary.json` được tạo lại từ chính phép tính trong notebook. Không chứa nhận xét viết tay.

# %%
summary = {
    "cutoff": T,
    "inputs": {"processed_versions": len(df), "active_versions": len(live_all),
               "active_distinct_units": len(live), "documents": int(df["doc_id"].nunique()),
               "conditional_active_versions": int(live_all["dieu_kien_hl"].notna().sum()),
               "multi_branch_unit_ids": int(variants["unit_id"].nunique())},
    "tokenizers": [{"name": x["name"], "url": x["url"], "bytes": x["bytes"], "sha256": x["sha256"]}
                   for x in tokenizer_provenance],
    "E1": {"units_by_group": {k: int(v) for k, v in e1_nhom["don_vi"].items()},
           "amending_documents": int(sd["doc_id"].nunique()), "amending_document_units": len(sd),
           "levels": {k: int(v) for k, v in live["level"].value_counts().items()}},
    "E2": {"large_doc_units": len(big), "large_doc_in_scope": int(big["trong_pham_vi"].sum()),
           "large_doc_out_scope": int((~big["trong_pham_vi"]).sum()),
           "scope": {k: list(v) for k, v in SCOPE.items()}},
    "E3": {"clause_candidates": len(kh_tok), "clause_bge_p50": float(kh_tok.quantile(.5)),
           "clause_bge_p95": float(kh_tok.quantile(.95)),
           "clause_over_512": int((kh_tok > 512).sum()),
           "core_clause_candidates": len(core_kh_tok), "core_clause_over_512": int((core_kh_tok > 512).sum()),
           "core_clause_bge_p95": float(core_kh_tok.quantile(.95)),
           "short_under_5_words": len(short),
           "clause_body_only_bge_p50": float(kh_body_tok.quantile(.5)),
           "clause_body_only_bge_p95": float(kh_body_tok.quantile(.95)),
           "clause_body_only_over_512": int((kh_body_tok > 512).sum()),
           "heading_token_delta_p50": float((kh_tok - kh_body_tok).quantile(.5)),
           "heading_token_delta_p95": float((kh_tok - kh_body_tok).quantile(.95)),
           "conditional_branch_body_tokens": variant_lengths.to_dict(orient="records")},
    "E4": {"first_fine_frames": len(fines), "structured_points_under_frames": int(fines["so_diem_cau_truc"].sum()),
           "first_fine_min": int(fines["min"].min()), "first_fine_max": int(fines["max"].max()),
           "points_first_match": {str(k): int(v) for k, v in sorted(pts.items())}},
    "E5": {"reviewed_rows": len(ok), "reviewed_actions": {k: int(v) for k, v in ok["action"].value_counts().items()},
           "amended_versions": len(amended), "content_changed_clause_point_unit_ids": int(rq3["unit_id"].nunique())},
    "E6": {"exception_extensions_exclusive_end": {k: v for k, v in extensions.items() if v},
           "future_events": len(fut), "future_events_by_date": {k: int(v) for k, v in
            pd.DataFrame(fut, columns=["ngay", "doc_id", "su_kien"])["ngay"].value_counts().sort_index().items()}},
    "E7": {"groups": len(seg), "top_terms": {k: v[:5] for k, v in top.items()},
           "legal_colloquial_counts": pair_counts.to_dict(orient="records")},
    "E8": {"candidates": len(cand), "near_duplicate_pairs": len(pairs)},
    "E9": {"units_checked": len(body9), "matched_references": len(refs),
           "units_with_reference": int(refs["unit_id"].nunique()),
           "reference_types": {k: int(v) for k, v in refs["loai"].value_counts().items()}},
    "E10": {"quality_checks": e10, "odd_top20": [[k, v] for k, v in odd.most_common(20)],
            "active_annex_types": {k: int(v) for k, v in live["loai_phu_luc"].value_counts().items()},
            "source_gap_audit": source_gap_audit},
    "eval_proposal": {"rows": len(matrix), "total_slots": int(matrix["so_cau"].sum()),
                      "slots_by_group": {k: int(v) for k, v in matrix.groupby("chu_de")["so_cau"].sum().items()},
                      "slots_by_type": {k: int(v) for k, v in matrix.groupby("loai_cau")["so_cau"].sum().items()}},
}
summary_path = ROOT / "reports/eda/summary.json"
summary_path.parent.mkdir(parents=True, exist_ok=True)
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"-> {summary_path.relative_to(ROOT)}")
