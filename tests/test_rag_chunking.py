import re
from collections import defaultdict

import pytest

from lawproc import config, evalset, validity
from rag import chunking


def _rec(uid, text="", vf="2025-01-01", vt=None, title="", exc=None, **kw):
    doc, *rest = uid.split(":")
    if rest[0].startswith("pl"):
        level = "phu_luc"
    elif len(rest) == 1:
        level = "dieu"
    else:
        level = "khoan" if len(rest) == 2 and re.fullmatch(r"k\d+\w*", rest[1]) else "diem"
    rec = {"unit_id": uid, "doc_id": doc, "level": level, "dieu": rest[0][1:] if level != "phu_luc" else None,
           "khoan": rest[1][1:] if level in ("khoan", "diem") and len(rest) == 3 or level == "khoan" else None,
           "diem": rest[-1] if level == "diem" else None, "title": title, "text": text,
           "valid_from": vf, "valid_to": vt, "version_id": f"{uid}@{vf}", "hl_ngoai_le": exc or [],
           "trang_thai": None, "trong_pham_vi": True, "loai_phu_luc": None}
    rec.update(kw)
    return rec


def words(text: str) -> int:
    return len(text.split())


def _build(recs, cach_cat="khoan", max_tokens=512, exclude=frozenset()):
    return chunking.build_chunks(recs, cach_cat, words, max_tokens, exclude=exclude)


def _live(chunks, t):
    return [c for c in chunks if chunking.in_force(c, t)]


FINE = [
    _rec("nd_168_2024:d7", title="Xử phạt người điều khiển xe mô tô"),
    _rec("nd_168_2024:d7:k2", "Phạt tiền từ 400.000 đồng đến 600.000 đồng đối với người điều khiển xe:"),
    _rec("nd_168_2024:d7:k2:a", "Dừng xe, đỗ xe trên phần đường xe chạy;"),
    _rec("nd_168_2024:d7:k2:h", "Không đội mũ bảo hiểm;"),
]


def test_khoan_chunk_has_article_title_lead_and_points():
    (chunk,) = _build(FINE)
    assert chunk["text"].splitlines() == [
        "Nghị định 168/2024/NĐ-CP — Điều 7. Xử phạt người điều khiển xe mô tô",
        "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng đối với người điều khiển xe:",
        "a) Dừng xe, đỗ xe trên phần đường xe chạy;",
        "h) Không đội mũ bảo hiểm;",
    ]
    assert chunk["units"] == ["nd_168_2024:d7:k2@2025-01-01", "nd_168_2024:d7:k2:a@2025-01-01",
                              "nd_168_2024:d7:k2:h@2025-01-01"]
    assert (chunk["doc_id"], chunk["dieu"], chunk["khoan"], chunk["nhom"]) == ("nd_168_2024", "7", "2",
                                                                              "nd_168_2024:d7:k2")
    assert chunk["valid_from"] == "2025-01-01" and chunk["valid_to"] is None
    assert not chunk["mot_phan"] and not chunk["vuot_gioi_han"]


def test_points_follow_legal_alphabet_not_python_order():
    recs = FINE[:2] + [_rec(f"nd_168_2024:d7:k2:{p}", p) for p in ("đ", "e", "d", "k1", "k", "a")]
    (chunk,) = _build(recs)
    assert [line.split(")")[0] for line in chunk["text"].splitlines()[2:]] == ["a", "d", "đ", "e", "k", "k1"]


def test_long_khoan_is_split_by_points_and_every_piece_keeps_the_lead():
    # tiêu đề 14 từ + câu dẫn 15 từ + mỗi Điểm 4 từ: tối đa 2 Điểm mỗi mẩu
    recs = FINE[:2] + [_rec(f"nd_168_2024:d7:k2:{p}", f"hành vi {p}") for p in "abcdeg"]
    pieces = _build(recs, max_tokens=40)
    assert len(pieces) > 1
    lead = "nd_168_2024:d7:k2@2025-01-01"
    for piece in pieces:
        assert "2. Phạt tiền từ 400.000 đồng đến 600.000 đồng" in piece["text"]
        assert piece["units"][0] == lead and piece["so_token"] <= 40 and not piece["mot_phan"]
    points = [u for piece in pieces for u in piece["units"] if u != lead]
    assert points == [f"nd_168_2024:d7:k2:{p}@2025-01-01" for p in "abcdeg"]
    assert len({piece["chunk_id"] for piece in pieces}) == len(pieces)


def test_a_point_too_long_on_its_own_is_kept_and_flagged():
    recs = FINE[:2] + [_rec("nd_168_2024:d7:k2:a", "rất dài " * 50)]
    (chunk,) = _build(recs, max_tokens=40)
    assert chunk["so_token"] > 40 and chunk["vuot_gioi_han"]


def test_article_lead_goes_into_each_khoan_chunk():
    recs = [_rec("luat_35_2024:d2", "Trong Luật này, các từ ngữ dưới đây được hiểu như sau:", title="Giải thích từ ngữ"),
            _rec("luat_35_2024:d2:k1", "Đường bộ gồm đường, cầu đường bộ."),
            _rec("luat_35_2024:d2:k2", "Phương tiện là xe cơ giới.")]
    chunks = _build(recs)
    assert len(chunks) == 2
    for chunk in chunks:
        assert chunk["units"][0] == "luat_35_2024:d2@2025-01-01"
        assert chunk["text"].splitlines()[1] == "Trong Luật này, các từ ngữ dưới đây được hiểu như sau:"
    assert chunks[0]["text"].startswith("Luật Đường bộ 35/2024/QH15 — Điều 2. Giải thích từ ngữ")


def test_article_without_clauses_is_one_chunk_with_direct_points():
    recs = [_rec("nd_218_2026:d33", "Bãi bỏ các quy định sau:", title="Bãi bỏ"),
            _rec("nd_218_2026:d33:a", "Điểm a khoản 2 Điều 5;"), _rec("nd_218_2026:d33:b", "Khoản 3 Điều 9.")]
    (chunk,) = _build(recs)
    assert chunk["nhom"] == "nd_218_2026:d33" and chunk["khoan"] is None
    assert chunk["text"].splitlines()[1:] == ["Bãi bỏ các quy định sau:", "a) Điểm a khoản 2 Điều 5;",
                                              "b) Khoản 3 Điều 9."]


def test_amended_point_gives_one_chunk_per_period():
    recs = [_rec("nd_158_2024:d34", title="Gia hạn"), _rec("nd_158_2024:d34:k4", "Trình tự gia hạn:"),
            _rec("nd_158_2024:d34:k4:a", "Nộp hồ sơ;"),
            _rec("nd_158_2024:d34:k4:b", "Trong thời hạn 02 ngày làm việc;", vt="2026-08-10"),
            _rec("nd_158_2024:d34:k4:b", "Trong thời hạn 01 ngày làm việc;", vf="2026-08-10")]
    old, new = _build(recs)
    assert (old["valid_from"], old["valid_to"], new["valid_from"], new["valid_to"]) == (
        "2025-01-01", "2026-08-10", "2026-08-10", None)
    assert "02 ngày làm việc" in old["text"] and "01 ngày làm việc" in new["text"]
    assert "nd_158_2024:d34:k4:b@2025-01-01" in old["units"] and "nd_158_2024:d34:k4:b@2026-08-10" in new["units"]
    assert [c["chunk_id"] for c in _live([old, new], "2026-06-01")] == [old["chunk_id"]]
    assert [c["chunk_id"] for c in _live([old, new], "2026-10-01")] == [new["chunk_id"]]


def test_point_added_later_starts_a_new_period():
    recs = FINE + [_rec("nd_168_2024:d7:k2:i", "Chở quá số người;", vf="2026-07-01")]
    before, after = _build(recs)
    assert before["valid_to"] == "2026-07-01" and "i) Chở quá số người;" not in before["text"]
    assert after["valid_from"] == "2026-07-01" and after["units"][-1] == "nd_168_2024:d7:k2:i@2026-07-01"


def test_repealed_out_of_scope_and_form_annexes_are_left_out():
    recs = FINE + [_rec("nd_168_2024:d9", title="Đã bãi bỏ", trang_thai="bai_bo"),
                   _rec("blds_2015:d1", "Phạm vi điều chỉnh.", title="Phạm vi", trong_pham_vi=False),
                   _rec("nd_168_2024:pl1", "Mẫu biên bản", title="Phụ lục I", loai_phu_luc="mau_bieu")]
    chunks = _build(recs)
    assert [c["nhom"] for c in chunks] == ["nd_168_2024:d7:k2"]


def test_amendment_instructions_and_their_children_are_left_out():
    recs = FINE + [_rec("nd_218_2026:d1", title="Sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP"),
                   _rec("nd_218_2026:d1:k4", "Sửa đổi, bổ sung điểm b khoản 4 Điều 34 như sau:"),
                   _rec("nd_218_2026:d1:k4:b", "“b) Trong thời hạn 01 ngày làm việc;”"),
                   _rec("nd_218_2026:d39", title="Điều khoản thi hành"),
                   _rec("nd_218_2026:d39:k1", "Nghị định này có hiệu lực thi hành từ ngày 10 tháng 8 năm 2026.")]
    chunks = _build(recs, exclude={"nd_218_2026:d1:k4"})
    assert [c["nhom"] for c in chunks] == ["nd_168_2024:d7:k2", "nd_218_2026:d39:k1"]


def test_instruction_list_reads_reviewed_amendments(tmp_path):
    path = tmp_path / "amendments_reviewed.csv"
    path.write_text("amend_doc_id,amend_unit_id,status,ghi_chu\n"
                    "nd_x,nd_x:d7:k2#18,duyet,\n"
                    "nd_x,nd_x:d7:k1,loai,\"dòng cha, nội dung nằm ở dòng con\"\n"
                    "nd_x,nd_x:d6:k3:a,loai,không phải chỉ dẫn sửa đổi: liệt kê\n", encoding="utf-8")
    assert chunking.instruction_units(path) == {"nd_x:d7:k2", "nd_x:d7:k1"}


def test_postponed_version_uses_in_force_at_not_raw_dates():
    old_exc = [{"vai_tro": "cu", "tu_ngay": "2027-01-01", "den_ngay": "", "dieu_kien": "", "loai": "hoan_ap_dung"}]
    new_exc = [{"vai_tro": "moi", "tu_ngay": "2027-01-01", "den_ngay": "", "dieu_kien": "", "loai": "hoan_ap_dung"}]
    recs = FINE[:2] + [_rec("nd_168_2024:d7:k2:b", "Bản cũ;", vt="2026-07-01", exc=old_exc),
                       _rec("nd_168_2024:d7:k2:b", "Bản mới;", vf="2026-07-01", exc=new_exc)]
    old, new = _build(recs)
    assert (old["valid_to"], new["valid_from"]) == ("2027-01-01", "2027-01-01")
    assert "Bản cũ;" in _live([old, new], "2026-10-01")[0]["text"]


def test_conditional_note_is_written_into_the_chunk():
    exc = [{"vai_tro": "moc", "tu_ngay": "2028-01-01", "den_ngay": "", "dieu_kien": "Áp dụng với xe tải từ 01/01/2028",
            "loai": "moc_trong_noi_dung"}]
    recs = FINE[:2] + [_rec("nd_168_2024:d7:k2:c", "Không lắp camera;", exc=exc)]
    now, later = _build(recs)
    assert "c) Không lắp camera; [Hiệu lực: Áp dụng với xe tải từ 01/01/2028]" in now["text"]
    assert now["ghi_chu_hieu_luc"] == ["Áp dụng với xe tải từ 01/01/2028"]
    assert later["valid_from"] == "2028-01-01" and later["ghi_chu_hieu_luc"] == []


def test_dieu_cut_keeps_the_whole_article():
    recs = FINE + [_rec("nd_168_2024:d7:k3", "Phạt tiền từ 800.000 đồng:"),
                   _rec("nd_168_2024:d7:k3:a", "Chạy quá tốc độ " * 20)]
    (chunk,) = _build(recs, cach_cat="dieu", max_tokens=10)
    assert chunk["nhom"] == "nd_168_2024:d7" and chunk["khoan"] is None and not chunk["mot_phan"]
    assert chunk["text"].count("\n") == 5 and chunk["so_token"] > 10
    assert len(chunk["units"]) == 5


def test_annex_is_split_by_lines_and_marked_partial():
    text = "\n".join(f"Dòng {i} của bảng lệ phí" for i in range(12))
    recs = [_rec("tt_155_2025_btc:pl1", text, title="Phụ lục I. Mức thu lệ phí")]
    for cach_cat in ("khoan", "dieu"):
        pieces = _build(recs, cach_cat=cach_cat, max_tokens=30)
        assert len(pieces) > 1 and all(p["mot_phan"] for p in pieces)
        assert all(p["text"].startswith("Thông tư 155/2025/TT-BTC — Phụ lục I. Mức thu lệ phí\n") for p in pieces)
        body = [line for p in pieces for line in p["text"].splitlines()[1:]]
        assert body == text.splitlines()
        assert all(p["units"] == ["tt_155_2025_btc:pl1@2025-01-01"] for p in pieces)


def test_annex_pieces_record_which_lines_they_hold():
    text = "\n".join(f"Dòng {i} của bảng lệ phí" for i in range(12))
    pieces = _build([_rec("tt_155_2025_btc:pl1", text, title="Phụ lục I")], max_tokens=30)
    vid = "tt_155_2025_btc:pl1@2025-01-01"
    spans = [p["phan_dong"][vid] for p in pieces]
    assert spans[0][0] == 0 and spans[-1][1] == 11 and all(s[2] == 12 for s in spans)
    assert all(a[1] + 1 == b[0] for a, b in zip(spans, spans[1:]))
    (whole,) = _build([_rec("tt_155_2025_btc:pl1", text, title="Phụ lục I")], max_tokens=500)
    assert whole["phan_dong"] == {} and not whole["mot_phan"]


def test_condition_note_is_repeated_at_the_top_of_every_annex_piece():
    exc = [{"vai_tro": "moc", "tu_ngay": "2028-01-01", "den_ngay": "", "loai": "moc_trong_noi_dung",
            "dieu_kien": "Chỉ mục A còn hiệu lực"}]
    text = "\n".join(f"Dòng {i} của bảng chấm điểm" for i in range(12))
    pieces = [p for p in _build([_rec("tt_12_2025_bca:pl4", text, title="Phụ lục IV", exc=exc)], max_tokens=40)
              if chunking.in_force(p, "2026-10-01")]
    assert len(pieces) > 1
    for p in pieces:
        assert p["text"].splitlines()[1] == "[Hiệu lực (phụ lục): Chỉ mục A còn hiệu lực]"
        assert p["so_token"] <= 40


def test_table_pieces_repeat_caption_and_column_names():
    rows = [f"{i} | Biển số IE.{450 + i} chỉ dẫn | gt2 | trắng | xanh lam | trắng" for i in range(1, 13)]
    text = "\n".join(["Màu sắc của biển chỉ dẫn", "Bảng 5 - Quy định về màu sắc của biển chỉ dẫn",
                      "TT | Mô tả biển chỉ dẫn | Kiểu chữ | Màu chữ, số | Màu nền | Màu viền", *rows])
    recs = [_rec("qcvn_41_2024:d46", title="Biển chỉ dẫn"), _rec("qcvn_41_2024:d46:k3", text)]
    pieces = _build(recs, max_tokens=60)
    assert len(pieces) > 2
    for p in pieces[1:]:
        lines = p["text"].splitlines()
        assert lines[1:3] == ["Bảng 5 - Quy định về màu sắc của biển chỉ dẫn",
                              "TT | Mô tả biển chỉ dẫn | Kiểu chữ | Màu chữ, số | Màu nền | Màu viền"]
        assert p["so_token"] <= 60
    body = [line for p in pieces for line in p["text"].splitlines()[1:]]
    assert sum(line.startswith("TT | ") for line in body) == len(pieces)
    assert [line for line in body if " | " in line and not line.startswith("TT | ")] == rows


def test_long_article_chunk_lists_conditions_near_the_top():
    exc = [{"vai_tro": "moc", "tu_ngay": "2029-01-01", "den_ngay": "", "loai": "moc_trong_noi_dung",
            "dieu_kien": "Khoang chở khách áp dụng từ 01/01/2029"}]
    recs = FINE + [_rec("nd_168_2024:d7:k3", "Phạt tiền từ 800.000 đồng:"),
                   _rec("nd_168_2024:d7:k3:a", "Không lắp camera " * 20, exc=exc)]
    now = next(c for c in _build(recs, cach_cat="dieu", max_tokens=30) if chunking.in_force(c, "2026-10-01"))
    lines = now["text"].splitlines()
    assert lines[1] == "[Hiệu lực (điểm a khoản 3): Khoang chở khách áp dụng từ 01/01/2029]"
    assert lines[-1].endswith("[Hiệu lực: Khoang chở khách áp dụng từ 01/01/2029]")
    (short,) = [c for c in _build(recs, cach_cat="dieu", max_tokens=5000) if chunking.in_force(c, "2026-10-01")]
    assert short["text"].splitlines()[1].startswith("2. ")


def test_build_is_deterministic():
    assert _build(FINE + FINE[1:2]) == _build(FINE + FINE[1:2])


# ---- Dữ liệu thật (data-v1, eval-v1) ----

@pytest.fixture(scope="module")
def count_tokens():
    try:
        return chunking.load_tokenizer()
    except FileNotFoundError:
        pytest.skip("không có tokenizer bge-m3")


@pytest.fixture(scope="module")
def records():
    return evalset.load_versions()


@pytest.fixture(scope="module")
def eval_items():
    return evalset.load_eval()


@pytest.fixture(scope="module")
def built(records, count_tokens):
    return {cut: chunking.build_chunks(records, cut, count_tokens) for cut in ("khoan", "dieu")}


def _containing(chunks, vid, t):
    return [c for c in chunks if vid in c["units"] and chunking.in_force(c, t)]


def test_helmet_fine_chunk_has_the_amount(built):
    (chunk,) = _containing(built["khoan"], "nd_168_2024:d7:k2:h@2025-01-01", config.CUTOFF)
    assert "400.000 đồng đến 600.000 đồng" in chunk["text"] and "mũ bảo hiểm" in chunk["text"]
    assert chunk["so_token"] <= 512


def test_sd56_old_and_new_deadline(built):
    (old,) = _containing(built["khoan"], "nd_158_2024:d34:k4:b@2025-01-01", "2026-06-01")
    (new,) = _containing(built["khoan"], "nd_158_2024:d34:k4:b@2026-08-10", config.CUTOFF)
    assert "02 ngày làm việc" in old["text"] and "01 ngày làm việc" in new["text"]
    assert not chunking.in_force(old, config.CUTOFF)


@pytest.mark.parametrize("cut", ["khoan", "dieu"])
def test_every_eval_citation_is_in_a_live_chunk(built, eval_items, cut):
    missing = []
    for item in eval_items:
        if item["nhom_cau"] not in ("thuong", "sua_doi"):
            continue
        for vid in item["can_cu"]:
            if not _containing(built[cut], vid, item["ngay_hoi"]):
                missing.append((item["key"], vid))
        for vid in item.get("can_cu_cu") or []:
            if not _containing(built[cut], vid, item["ngay_cu"]):
                missing.append((item["key"], vid, "cu"))
    assert missing == []


@pytest.mark.parametrize("cut", ["khoan", "dieu"])
def test_live_chunks_hold_exactly_the_live_versions(records, built, eval_items, cut):
    dates = {config.CUTOFF} | {x["ngay_cu"] for x in eval_items if x.get("ngay_cu")}
    by_unit = defaultdict(list)
    for rec in chunking.load_scope(records):
        by_unit[rec["unit_id"]].append(rec)
    members = {g.anchor: g.members for g in chunking.groups(chunking.load_scope(records), cut)}
    by_group = defaultdict(list)
    for c in built[cut]:
        by_group[c["nhom"]].append(c)
    bad = []
    for anchor, chunks in by_group.items():
        for t in dates:
            want = {r["version_id"] for u in members[anchor] for r in by_unit[u] if validity.in_force_at(r, t)[0]}
            got = {u for c in chunks if chunking.in_force(c, t) for u in c["units"]}
            if want != got:
                bad.append((anchor, t))
    assert bad == []


def test_real_instructions_are_dropped_but_closing_provisions_kept(built):
    groups = {c["nhom"] for c in built["khoan"]}
    assert not any(g.startswith(("luat_118_2025:d7:", "nd_218_2026:d1:", "nd_175_2025:d1:")) for g in groups)
    assert {"luat_118_2025:d11:k1", "nd_218_2026:d39:k1", "tt_105_2026_bca:d6:k3"} <= groups
    # Nội dung đã áp vào văn bản đích vẫn có: khoản 18a Điều 9 Luật 36 do Luật 118 bổ sung.
    assert "luat_36_2024:d9:k18a" in groups


@pytest.mark.parametrize("cut", ["khoan", "dieu"])
def test_every_condition_note_is_in_the_chunk_text(built, cut):
    missing = [c["chunk_id"] for c in built[cut] for note in c["ghi_chu_hieu_luc"] if note not in c["text"]]
    assert missing == []


def test_real_table_piece_keeps_column_names(built):
    pieces = [c for c in built["khoan"] if c["nhom"] == "qcvn_41_2024:d46:k3"]
    assert len(pieces) > 1
    for p in pieces:
        assert "Màu chữ, số | Màu nền | Màu viền" in p["text"]
    row = next(p for p in pieces if "Biển số IE.451" in p["text"])
    assert "Bảng 5 - Quy định về kiểu chữ, màu sắc của biển chỉ dẫn" in row["text"]


def test_khoan_chunks_respect_the_token_limit(built):
    # Vượt giới hạn chỉ khi mẩu còn một Điểm hoặc một dòng (hàng bảng dài) cộng phần lặp lại ở đầu mẩu.
    over = [c for c in built["khoan"] if c["so_token"] > 512]
    assert all(c["vuot_gioi_han"] for c in over)
    assert len(over) <= 30


def test_dieu_chunks_fit_the_embedding_model(built):
    assert max(c["so_token"] for c in built["dieu"] if not c["mot_phan"]) <= 8192


def test_saved_chunks_match_a_fresh_build_and_the_manifest(built):
    import hashlib
    import json

    folder = config.DATA / "rag"
    manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    for cut, chunks in built.items():
        data = (folder / f"chunks_{cut}.jsonl").read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest["files"][f"data/rag/chunks_{cut}.jsonl"]["sha256"]
        assert data == "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks).encode("utf-8")


def test_chunk_ids_are_unique(built):
    for chunks in built.values():
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))
