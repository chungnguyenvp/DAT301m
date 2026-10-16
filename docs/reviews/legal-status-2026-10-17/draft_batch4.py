"""Soạn bản nháp đợt 4 (rà soát tình trạng pháp lý 2026-10-17) vào các bảng duyệt.

Chạy: py -3.13 -X utf8 docs/reviews/legal-status-2026-10-17/draft_batch4.py
Chạy lại được: xóa dòng của đợt 4 rồi ghi lại.

- amendments_reviewed.csv: dòng sửa nội dung của NĐ 47/2026, TT 13/2025, TT 105/2026, TT 62/2026 để `chua_duyet`;
  ba dòng đóng cả văn bản (NĐ 39 bởi NĐ 156, NĐ 160 bởi NĐ 94, VBHN 63 bởi VBHN 90) để `duyet` theo yêu cầu.
- annex_replacements.csv: mẫu ĐKX của TT 79 thay bởi TT 13, phụ lục TT 65 thay bởi TT 105; cột duyet để trống.
- effective_dates.csv: ngày hiệu lực của 7 văn bản mới, trích điều khoản hiệu lực.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "data" / "processed"
REVIEWED = PROCESSED / "amendments_reviewed.csv"
CANDIDATES = PROCESSED / "amendments_candidates.csv"
EFFECTIVE = PROCESSED / "effective_dates.csv"
EFFECTIVE_AUTO = PROCESSED / "effective_dates_auto.csv"
ANNEX = ROOT / "data" / "annex_replacements.csv"
UNITS = PROCESSED / "legal_units.jsonl"

NEW_DOCS = ["nd_156_2024", "nd_94_2026", "nd_47_2026", "tt_105_2026_bca", "vbhn_90_2026_xlvphc",
            "tt_62_2026_bca", "tt_13_2025_bca"]
AMENDING = {"nd_47_2026", "tt_13_2025_bca", "tt_105_2026_bca", "tt_62_2026_bca"}
TAG = "đợt 4 (2026-10-17)"
PENDING = f"{TAG}: chờ duyệt"

units = {u["unit_id"]: u for u in map(json.loads, UNITS.open(encoding="utf-8"))}


def read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def unit_text(uid: str) -> str:
    """Toàn văn đơn vị kèm đơn vị con, có nhãn, để làm new_text của dòng sua_doi."""
    out = []
    for k, u in units.items():
        if k != uid and not k.startswith(uid + ":"):
            continue
        label = {"khoan": f"{u['khoan']}. ", "diem": f"{u['diem']}) "}.get(u["level"], "")
        if u["level"] == "dieu":
            out.append(f"Điều {u['dieu']}. {u['title']}")
            if u["text"]:
                out.append(u["text"])
        else:
            out.append(label + u["text"])
    if not out:
        raise KeyError(uid)
    return "\n".join(out)


def edit(uid: str, changes: list[tuple[str, str]]) -> str:
    """Áp các thay cụm từ (không phân biệt hoa thường); mỗi cụm phải có mặt."""
    text = unit_text(uid)
    for old, new in changes:
        pat = re.compile(re.escape(old), re.IGNORECASE)
        if not pat.search(text):
            raise ValueError(f"{uid}: không thấy cụm {old!r}")
        text = pat.sub(new, text)
    return text


def row(amend_unit: str, action: str, target: str, dieu: str, khoan: str = "", diem: str = "", *,
        text: str = "", label: str = "", status: str = "chua_duyet", hl: str = "", note: str = "",
        instruction: str | None = None) -> dict:
    return {
        "amend_doc_id": amend_unit.split(":")[0], "amend_unit_id": amend_unit, "action": action,
        "target_doc_id": target, "target_dieu": dieu, "target_khoan": khoan, "target_diem": diem,
        "new_label": label,
        "instruction": instruction if instruction is not None else units[amend_unit]["text"].split("\n")[0][:600],
        "new_text": text, "status": status, "hl_rieng": hl,
        "ghi_chu": f"{PENDING}; {note}" if status == "chua_duyet" and note else (PENDING if status == "chua_duyet" else note),
    }


def from_candidates() -> tuple[list[dict], dict[str, dict]]:
    cands = [c for c in read(CANDIDATES) if c["amend_doc_id"] in AMENDING]
    by_id = {c["amend_unit_id"]: c for c in cands}
    return cands, by_id


def drafted() -> list[dict]:
    cands, by_id = from_candidates()
    out: list[dict] = []
    handled: set[str] = set()

    def keep(uid: str, note: str = "") -> None:
        c = dict(by_id[uid])
        c["status"], c["hl_rieng"] = "chua_duyet", ""
        c["ghi_chu"] = "; ".join(x for x in (PENDING, note, c["ghi_chu"]) if x)
        out.append(c)
        handled.add(uid)

    def drop(uid: str, why: str) -> None:
        c = dict(by_id[uid])
        c["status"], c["hl_rieng"], c["ghi_chu"] = "loai", "", f"{TAG}: {why}"
        out.append(c)
        handled.add(uid)

    # NĐ 47/2026 sửa NĐ 138/2021, hiệu lực 15/3/2026
    for uid in ("nd_47_2026:d1", "nd_47_2026:d2:k1", "nd_47_2026:d2:k2", "nd_47_2026:d3:k1",
                "nd_47_2026:d3:k2", "nd_47_2026:d4"):
        keep(uid)
    for uid in ("nd_47_2026:d2", "nd_47_2026:d3", "nd_47_2026:d5"):
        drop(uid, "dòng cha, nội dung nằm ở dòng con")
    t = "nd_138_2021"
    out.append(row("nd_47_2026:d5:k1", "sua_doi", t, "1", "2", note="đã chuyển từ thay_the_cum_tu (d5:k1)",
                   text=edit(f"{t}:d1:k2", [("theo quy định của Luật Xử lý vi phạm hành chính.",
                                             "theo quy định của Luật Xử lý vi phạm hành chính và các quy định của pháp luật có liên quan.")])))
    out.append(row("nd_47_2026:d5:k2", "sua_doi", t, "8", "2", note="đã chuyển từ thay_the_cum_tu (d5:k2)",
                   text=edit(f"{t}:d8:k2", [("khi có quyết định của người có thẩm quyền.",
                                             "khi có quyết định của người có thẩm quyền ra quyết định tạm giữ hoặc quyết định của người có thẩm quyền.")])))
    out.append(row("nd_47_2026:d5:k3", "sua_doi", t, "14", "3", note="đã chuyển từ thay_the_cum_tu (d5:k3)",
                   text=edit(f"{t}:d14:k3", [("Ủy ban nhân dân xã, phường, thị trấn", "Ủy ban nhân dân xã, phường, đặc khu")])))
    cmnd = ("hoặc số chứng minh nhân dân", "")
    sentence = ("Cá nhân vi phạm khi gửi đơn phải gửi bản sao kèm theo bản chính để đối chiếu hoặc bản sao có công chứng, "
                "chứng thực Chứng minh nhân dân hoặc Thẻ căn cước công dân hoặc giấy xác nhận về nơi công tác của cơ quan, "
                "tổ chức nơi cá nhân vi phạm đang công tác; đối với", "Đối với")
    out.append(row("nd_47_2026:d5:k4", "sua_doi", t, "14", "2", "a",
                   note="đã chuyển từ thay_the_cum_tu (d5:k4 và d5:k5 cùng sửa điểm này); bỏ cả dấu “;” sau cụm bị bỏ và viết hoa “Đối với”",
                   text=re.sub(r"  +", " ", edit(f"{t}:d14:k2:a", [sentence, (" " + cmnd[0], "")]))))
    for addr in (("14", "2", "c"), ("15", "3", "a"), ("15", "3", "c"), ("15", "4", ""), ("15", "6", "")):
        uid = f"{t}:d{addr[0]}:k{addr[1]}" + (f":{addr[2]}" if addr[2] else "")
        out.append(row("nd_47_2026:d5:k5", "sua_doi", t, *addr, note="đã chuyển từ thay_the_cum_tu (d5:k5)",
                       text=edit(uid, [(" " + cmnd[0], "")])))
    handled.update({"nd_47_2026:d5:k1", "nd_47_2026:d5:k2", "nd_47_2026:d5:k3", "nd_47_2026:d5:k4", "nd_47_2026:d5:k5"})

    # TT 105/2026 sửa TT 65/2024, hiệu lực 01/7/2026; khoản 1-3 Điều 6 mới từ 01/7/2027 (khoản 6 Điều 6 TT 105)
    t = "tt_65_2024_bca"
    new6 = by_id["tt_105_2026_bca:d1"]["new_text"]
    I6 = "Sửa đổi, bổ sung Điều 6"
    parts = {m.group(1): m.group(0).strip() for m in re.finditer(r"(?ms)^(\d)\. .*?(?=^\d\. |\Z)", new6)}
    parts = {k: re.sub(r"”\.?$", "", v).strip() for k, v in parts.items()}
    for k in ("1", "2", "3"):
        out.append(row("tt_105_2026_bca:d1", "sua_doi", t, "6", k, hl="2027-07-01", text=parts[k], instruction=I6,
                       note="khoản 6 Điều 6 TT 105: khoản 1, 2, 3 Điều 6 mới có hiệu lực từ 01/7/2027; "
                            "đến hết 30/6/2027 vẫn áp dụng phần lý thuyết cũ (khoản 3 Điều 6 TT 105)"))
    out.append(row("tt_105_2026_bca:d1", "sua_doi", t, "6", "4", text=parts["4"], instruction=I6,
                   note="khoản 4 Điều 6 mới (kiểm tra lại sau 07 ngày làm việc) có hiệu lực 01/7/2026; khoản 4 cũ "
                        "(kiểm tra mô phỏng) hết hiệu lực từ 01/7/2026 theo khoản 2 Điều 6 TT 105"))
    out.append(row("tt_105_2026_bca:d1", "bai_bo", t, "6", "5", hl="2027-07-01", instruction=I6,
                   note="Điều 6 mới không còn khoản 5; điểm a khoản 5 tiếp tục đến hết 30/6/2027 (khoản 3 Điều 6 TT 105)"))
    for k, d in (("1", "b"), ("2", "b"), ("5", "b")):
        out.append(row("tt_105_2026_bca:d6:k2", "bai_bo", t, "6", k, d,
                       note="nội dung kiểm tra mô phỏng hết hiệu lực từ 01/7/2026; khoản 5 Điều 6 TT 105 (chuyển tiếp) "
                            "cho người có GPLX ô tô chỉ cần đạt lý thuyết"))
    handled.update({"tt_105_2026_bca:d1", "tt_105_2026_bca:d4:k1"})
    keep("tt_105_2026_bca:d2")
    keep("tt_105_2026_bca:d3")
    out.append(row("tt_105_2026_bca:d4:k1", "sua_doi", t, "4", "2", note="đã chuyển từ thay_the_cum_tu (d4:k1)",
                   text=edit(f"{t}:d4:k2", [("Phòng Cảnh sát giao thông Công an tỉnh, thành phố trực thuộc trung ương",
                                             "Phòng Cảnh sát giao thông Công an tỉnh, thành phố")])))
    drop("tt_105_2026_bca:d4:k2", "bãi bỏ phụ lục: ghi ở data/annex_replacements.csv (tt_65_2024_bca:pl1 -> tt_105_2026_bca:pl1)")
    drop("tt_105_2026_bca:d6:k3:a", "không phải chỉ dẫn sửa đổi: liệt kê nội dung chuyển tiếp trong khoản 3 Điều 6 TT 105")

    # TT 13/2025 sửa TT 65 (Điều 6) và TT 79 (Điều 12), hiệu lực 01/3/2025
    d6 = units["tt_13_2025_bca:d6"]["text"]
    k1 = re.sub(r"”\.?$", "", d6.split("“", 1)[1]).strip()
    out.append(row("tt_13_2025_bca:d6", "sua_doi", "tt_65_2024_bca", "6", "1", text=k1,
                   instruction="Sửa đổi, bổ sung khoản 1 Điều 6 như sau:",
                   note="bộ tách tự động bỏ sót vì chỉ dẫn nằm trong thân Điều 6 TT 13"))
    for k in range(1, 10):
        keep(f"tt_13_2025_bca:d12:k{k}")
    keep("tt_13_2025_bca:d12:k11")
    t = "tt_79_2024_bca"
    out.append(row("tt_13_2025_bca:d12:k10", "sua_doi", t, "10", "1", note="đã chuyển từ thay_the_cum_tu (d12:k10): bỏ “Công an cấp huyện”",
                   text=re.sub(r"  +", " ", edit(f"{t}:d10:k1", [("Công an cấp huyện", "")]))))
    for addr in (("3", "6", ""), ("14", "1", "a"), ("14", "2", "a"), ("14", "2", "d"), ("17", "2", "c"),
                 ("17", "2", "d"), ("20", "2", ""), ("21", "1", "a"), ("21", "1", "b"), ("21", "1", "c"),
                 ("21", "2", "b"), ("26", "1", "a"), ("29", "1", "d")):
        uid = f"{t}:d{addr[0]}:k{addr[1]}" + (f":{addr[2]}" if addr[2] else "")
        out.append(row("tt_13_2025_bca:d12:k10", "sua_doi", t, *addr,
                       note="đã chuyển từ thay_the_cum_tu (d12:k10): bỏ “công ích”",
                       text=edit(uid, [(" công ích", "")])))
    handled.add("tt_13_2025_bca:d12:k10")
    drop("tt_13_2025_bca:d12:k12", "thay mẫu ĐKX: ghi ở data/annex_replacements.csv")

    # TT 62/2026 Điều 7 sửa TT 79, hiệu lực từ ngày ký 18/5/2026
    for uid in ("tt_62_2026_bca:d7:k1", "tt_62_2026_bca:d7:k2", "tt_62_2026_bca:d7:k3:a", "tt_62_2026_bca:d7:k3:b",
                "tt_62_2026_bca:d7:k3:c", "tt_62_2026_bca:d7:k4", "tt_62_2026_bca:d7:k5", "tt_62_2026_bca:d7:k6",
                "tt_62_2026_bca:d7:k7", "tt_62_2026_bca:d7:k8"):
        keep(uid)
    drop("tt_62_2026_bca:d7:k3", "dòng cha, nội dung nằm ở dòng con")

    for c in cands:
        if c["amend_unit_id"] in handled:
            continue
        handled.add(c["amend_unit_id"])
        if c["target_doc_id"] in ("", "luat_36_2024") or c["amend_doc_id"] == "tt_13_2025_bca":
            drop(c["amend_unit_id"], "văn bản đích không có trong kho (đích tự động lấy nhầm từ phần căn cứ nếu có)")
        else:
            raise SystemExit(f"chưa xử lý: {c['amend_unit_id']} -> {c['target_doc_id']}")

    # Đóng cả văn bản: người dùng đã đồng ý (2026-10-17)
    ok = f"{TAG}: người dùng đồng ý đóng văn bản"
    out.append(row("nd_156_2024:d27:k2", "thay_the_van_ban", "nd_39_2023", "", status="duyet",
                   note=f"{ok}; Điều 28 NĐ 156: phiên đấu giá trước 01/01/2025 tiếp tục theo NĐ 39"))
    out.append(row("nd_94_2026:d41:k2", "thay_the_van_ban", "nd_160_2024", "", status="duyet",
                   note=f"{ok}; Điều 42 NĐ 94: hồ sơ nộp trước 01/7/2026 giải quyết theo NĐ 160, giấy phép đã cấp còn giá trị"))
    out.append(row("vbhn_90_2026_xlvphc:mo_dau", "thay_the_van_ban", "vbhn_63_2025_xlvphc", "", status="duyet",
                   instruction="Văn bản hợp nhất 90/VBHN-VPQH (30/3/2026) thay bản hợp nhất 63/VBHN-VPQH: thêm Luật 116/2025/QH15 và 120/2025/QH15 (hiệu lực 01/7/2026)",
                   note=f"{ok}; VBHN 171/2026/VBHN-LQ-VPQH (30/9/2026) chỉ thêm Luật 11/2026/QH16 hiệu lực 01/3/2027, sau mốc 01/10/2026"))
    return out


EFFECTIVE_NOTES = {
    "nd_156_2024": ("2025-01-01", "van_ban", "Điều 27 khoản 1: \"từ ngày 01 tháng 01 năm 2025\"; khoản 2: NĐ 39/2023 hết hiệu lực từ ngày này, trừ Điều 28."),
    "nd_94_2026": ("2026-07-01", "van_ban", "Điều 41 khoản 1: \"từ ngày 01 tháng 7 năm 2026\"; khoản 2: bãi bỏ NĐ 160/2024."),
    "nd_47_2026": ("2026-03-15", "van_ban", "Điều 6 khoản 1: \"từ ngày 15 tháng 3 năm 2026\"."),
    "tt_105_2026_bca": ("2026-07-01", "van_ban", "Điều 6 khoản 1: \"từ ngày 01 tháng 7 năm 2026, trừ khoản 6\"; khoản 6: khoản 1, 2, 3 Điều 6 mới từ 01/7/2027 (ghi ở hl_rieng của dòng sửa đổi)."),
    "vbhn_90_2026_xlvphc": ("2026-07-01", "van_ban", "Văn bản hợp nhất: luật sửa đổi mới nhất trong danh sách là Luật 116/2025/QH15 và 120/2025/QH15, \"có hiệu lực kể từ ngày 01 tháng 7 năm 2026\"; cùng quy ước với vbhn_63. VBHN ký 30/3/2026."),
    "tt_62_2026_bca": ("2026-05-18", "ngay_ky", "Điều 9 khoản 1: \"có hiệu lực thi hành từ ngày ký\" (18/5/2026), trừ khoản 2 (Điều 8 sửa TT 36/2025 về PCCC, ngoài phạm vi, từ 01/7/2026). Điều 7 sửa TT 79 theo ngày ký."),
    "tt_13_2025_bca": ("2025-03-01", "van_ban", "Điều 14 khoản 1: \"kể từ ngày 01 tháng 3 năm 2025\"."),
}


def main() -> None:
    reviewed = read(REVIEWED)
    fields = list(reviewed[0])
    replaced = {"nd_39_2023", "nd_160_2024", "vbhn_63_2025_xlvphc"}
    kept = [r for r in reviewed if r["amend_doc_id"] not in AMENDING
            and not (r["action"] == "thay_the_van_ban" and r["target_doc_id"] in replaced)]
    new = drafted()
    write(REVIEWED, kept + [{k: r.get(k, "") for k in fields} for r in new], fields)

    eff = read(EFFECTIVE)
    efields = list(eff[0])
    auto = {r["doc_id"]: r for r in read(EFFECTIVE_AUTO)}
    eff = [r for r in eff if r["doc_id"] not in EFFECTIVE_NOTES]
    for doc in NEW_DOCS:
        hl, nguon, note = EFFECTIVE_NOTES[doc]
        r = dict(auto[doc])
        r.update(hl_chot=hl, nguon=nguon, can_duyet="False", ghi_chu=f"{note} Xác nhận ({TAG}).")
        eff.append({k: r.get(k, "") for k in efields})
    write(EFFECTIVE, eff, efields)

    annex = read(ANNEX)
    afields = list(annex[0])
    annex = [r for r in annex if not r["pl_moi"].startswith(("tt_13_2025_bca:", "tt_105_2026_bca:"))]
    forms = ["01", "02", "03", "05", "06", "07", "08", "09", "10"]
    old = {"01": 1, "02": 2, "03": 3, "05": 5, "06": 6, "07": 7, "08": 8, "09": 9, "10": 10}
    for i, f in enumerate(forms):
        annex.append({"pl_cu": f"tt_79_2024_bca:pl{old[f]}", "pl_moi": f"tt_13_2025_bca:pl{9 + i}", "pham_vi": "toan_bo",
                      "chi_tiet": "", "tu_ngay": "2025-03-01", "can_cu": "tt_13_2025_bca:d12:k12",
                      "chi_dan": f"Thay thế mẫu số ĐKX{f} ban hành kèm theo Thông tư số 79/2024/TT-BCA bằng mẫu số ĐKX{f}/79 ban hành kèm theo Thông tư số 13/2025/TT-BCA.",
                      "duyet": "", "ghi_chu": PENDING})
    annex.append({"pl_cu": "tt_65_2024_bca:pl1", "pl_moi": "tt_105_2026_bca:pl1", "pham_vi": "toan_bo", "chi_tiet": "",
                  "tu_ngay": "2026-07-01", "can_cu": "tt_105_2026_bca:d4:k2; tt_105_2026_bca:d5",
                  "chi_dan": "Bãi bỏ Phụ lục và Mẫu số 01, Mẫu số 02 Phụ lục biểu mẫu của TT 65/2024; ban hành kèm theo TT 105/2026 Phụ lục biểu mẫu (Mẫu số 01, Mẫu số 02).",
                  "duyet": "", "ghi_chu": PENDING})
    write(ANNEX, annex, afields)

    pending = sum(r["status"] == "chua_duyet" for r in new)
    print(f"amendments: {len(new)} dòng đợt 4 ({pending} chờ duyệt, "
          f"{sum(r['status'] == 'duyet' for r in new)} đã duyệt, {sum(r['status'] == 'loai' for r in new)} loại)")
    print(f"effective_dates: {len(NEW_DOCS)} văn bản; annex_replacements: {len(forms) + 1} dòng chờ duyệt")


if __name__ == "__main__":
    main()
