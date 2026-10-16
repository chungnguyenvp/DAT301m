"""Kiểm tra bất biến của đầu ra đã commit trong data/processed/ (bỏ qua nếu thiếu file)."""
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pytest

from lawproc.structure import is_closing_line
from lawproc.validity import in_force_at

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
UNITS = PROCESSED / "legal_units.jsonl"
VERSIONED = PROCESSED / "legal_units_versioned.jsonl"
DOCS = PROCESSED / "documents"
T = "2026-10-01"


def _read(path: Path) -> list[dict]:
    if not path.exists():
        pytest.skip(f"{path.name} chưa có")
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _in_force(r: dict, t: str = T) -> bool:
    return in_force_at(r, t)[0]


@pytest.fixture(scope="module")
def versioned() -> list[dict]:
    return _read(VERSIONED)


@pytest.fixture(scope="module")
def units() -> list[dict]:
    return _read(UNITS)


def test_no_overlapping_versions_per_unit(versioned):
    by_unit = defaultdict(list)
    for r in versioned:
        by_unit[r["unit_id"]].append(r)
    bad = []
    for uid, recs in by_unit.items():
        recs.sort(key=lambda r: (r["valid_from"], r["valid_to"] or "9999-12-31"))
        for a, b in zip(recs, recs[1:]):
            if (a["valid_to"] or "9999-12-31") > b["valid_from"]:
                bad.append(uid)
                break
    assert not bad, bad[:10]


def test_version_ids_are_unique(versioned):
    ids = [r["version_id"] for r in versioned]
    assert len(ids) == len(set(ids))


def test_no_hash_suffix_in_unit_ids_in_force(versioned):
    assert [r["unit_id"] for r in versioned if _in_force(r) and "#" in r["unit_id"]] == []


def test_ket_thuc_units_contain_no_annex_text(units):
    bad = [u["unit_id"] for u in units if u["level"] == "ket_thuc"
           and any(k in u["text"] for k in ("Phụ lục", "PHỤ LỤC", "BIỂU MỨC"))]
    assert bad == []


def test_ket_thuc_is_not_in_versioned_output(versioned):
    assert [r["unit_id"] for r in versioned if r["level"] == "ket_thuc"] == []


def test_tt_155_fee_table_is_a_live_annex(versioned):
    live = [r for r in versioned if r["doc_id"] == "tt_155_2025_btc" and r["level"] == "phu_luc"
            and r["valid_to"] is None and "BIỂU MỨC THU LỆ PHÍ" in (r["title"] + r["text"])]
    assert live, "bảng biểu mức thu lệ phí của TT 155 không có trong đầu ra có phiên bản"


def _live_annex(versioned, unit_id):
    live = [r for r in versioned if r["unit_id"] == unit_id and r["valid_to"] is None]
    assert len(live) == 1, unit_id
    return live[0]["text"]


def test_tt_155_fee_rows_name_their_region(versioned):
    text = _live_annex(versioned, "tt_155_2025_btc:pl1")
    assert ("I.2. Cấp mới chứng nhận đăng ký xe và biển số xe cơ giới - Xe ô tô chở người từ 9 chỗ trở xuống "
            "(bao gồm cả xe con pick-up): Khu vực I 14.000.000 đồng; Khu vực II 140.000 đồng.") in text
    assert "mức thu chung cho Khu vực I và Khu vực II" in text
    assert not re.search(r"(?m)^\w+ \| ", text), "còn dòng bảng thô không có tên khu vực"


def test_tt_36_annex_i_labels_every_group(versioned):
    text = _live_annex(versioned, "tt_36_2024_byt:pl1")
    assert len(re.findall(r"(?m)^Chuyên khoa \d - ", text)) == 9
    # 9 chuyên khoa × 3 nhóm; dòng giới thiệu ba nhóm ở đầu bảng không có ": " sau ngoặc nên không tính
    assert len(re.findall(r"(?m)^Nhóm [123] \(người lái xe hạng[^)]*\): ", text)) == 27


def _replaced_docs() -> set[str]:
    """Văn bản bị thay cả văn bản bởi dòng thay_the_van_ban đã duyệt."""
    import csv

    with (PROCESSED / "amendments_reviewed.csv").open(encoding="utf-8-sig") as fp:
        return {r["target_doc_id"] for r in csv.DictReader(fp)
                if r["action"] == "thay_the_van_ban" and r["status"] == "duyet"}


def test_every_document_has_unit_in_force(versioned):
    if not DOCS.exists():
        pytest.skip("documents/ chưa có")
    live_docs = {r["doc_id"] for r in versioned if _in_force(r)}
    missing = sorted(p.stem for p in DOCS.glob("*.txt") if p.stem not in live_docs)
    # TT 12 bị TT 108 thay nhưng còn phần gia hạn đến 28/02/2027 nên vẫn có đơn vị hiệu lực
    assert missing == sorted(_replaced_docs() - {"tt_12_2025_bca"})


@pytest.mark.parametrize("old, new, day", [
    ("nd_39_2023", "nd_156_2024", "2025-01-01"),  # đấu giá biển số xe: Điều 27 NĐ 156
    ("nd_160_2024", "nd_94_2026", "2026-07-01"),  # đào tạo, sát hạch lái xe: Điều 41 NĐ 94
    ("vbhn_63_2025_xlvphc", "vbhn_90_2026_xlvphc", "2026-07-01"),  # Luật XLVPHC: bản hợp nhất mới
])
def test_replaced_document_hands_over_on_its_date(versioned, old, new, day):
    before = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    assert any(_in_force(r, before) for r in versioned if r["doc_id"] == old)
    assert not any(_in_force(r, before) for r in versioned if r["doc_id"] == new)
    assert not any(_in_force(r, day) for r in versioned if r["doc_id"] == old)
    assert any(_in_force(r, day) for r in versioned if r["doc_id"] == new)


def _live_text(versioned, prefix: str, day: str = T) -> str:
    return "\n".join(r["text"] for r in versioned
                     if (r["unit_id"] == prefix or r["unit_id"].startswith(prefix + ":")) and _in_force(r, day))


# Câu hỏi theo ngày từ đợt rà soát 2026-10-17 (dòng sửa đổi đợt 4 đã duyệt).


def test_plate_auction_at_cutoff_follows_nd_156(versioned):
    assert not any(_in_force(r) for r in versioned if r["doc_id"] == "nd_39_2023")
    assert "đấu giá biển số xe" in _live_text(versioned, "nd_156_2024:d1")


def test_point_restoration_has_no_simulation_test_after_july_2026(versioned):
    assert "mô phỏng" in _live_text(versioned, "tt_65_2024_bca:d6", "2026-06-30")
    assert "mô phỏng" not in _live_text(versioned, "tt_65_2024_bca:d6")


def test_keeping_seized_vehicle_needs_no_id_copy_after_march_2026(versioned):
    copy = "Chứng minh nhân dân hoặc Thẻ căn cước công dân"
    assert copy in _live_text(versioned, "nd_138_2021:d14:k2:a", "2026-03-14")
    assert copy not in _live_text(versioned, "nd_138_2021:d14:k2:a")


def test_vehicle_registration_has_no_district_police(versioned):
    assert "Công an cấp huyện" not in _live_text(versioned, "tt_79_2024_bca")


def test_tt12_in_force_only_through_extension(versioned):
    live = [r for r in versioned if r["doc_id"] == "tt_12_2025_bca" and _in_force(r)]
    assert live and all(any(e["vai_tro"] == "gia_han" for e in r["hl_ngoai_le"]) for r in live)


def test_exception_rows_give_expected_status_at_cutoff(versioned):
    for r in versioned:
        for e in r["hl_ngoai_le"]:
            ok, note = in_force_at(r, T)
            if e["vai_tro"] in ("gia_han", "cu") and r["valid_from"] <= T < (e["den_ngay"] or e["tu_ngay"]):
                assert ok, r["version_id"]
            if e["vai_tro"] == "moi" and r["valid_from"] <= T < e["tu_ngay"]:
                assert ok == bool(e["dieu_kien"]), r["version_id"]
            if e["vai_tro"] == "moc" and ok and r["valid_from"] <= T < e["tu_ngay"]:
                assert e["dieu_kien"] in note, r["version_id"]


def test_effective_overlaps_require_conditional_old_and_new(versioned):
    by_unit = defaultdict(list)
    for r in versioned:
        by_unit[r["unit_id"]].append(r)
    bad = []
    for day in (T, "2027-02-28", "2027-03-01", "2027-12-31", "2028-01-01", "2029-01-01"):
        for uid, recs in by_unit.items():
            live = [(r, in_force_at(r, day)[1]) for r in recs if _in_force(r, day)]
            if len(live) <= 1:
                continue
            roles = [{e["vai_tro"] for e in r["hl_ngoai_le"] if e["loai"] == "hoan_ap_dung"} for r, _ in live]
            if (len(live) != 2 or not any("cu" in x for x in roles) or
                    not any("moi" in x for x in roles) or not all(note for _, note in live)):
                bad.append((uid, day))
    assert not bad, bad[:10]


def test_no_closing_lines_outside_ket_thuc(units):
    bad = [u["unit_id"] for u in units if u["level"] not in ("ket_thuc", "phu_luc", "mo_dau")
           and any(is_closing_line(x) for x in u["text"].splitlines())]
    assert bad == [], bad[:10]


def test_qcvn41_is_its_own_document(units):
    dieu = sorted(int(u["dieu"]) for u in units if u["doc_id"] == "qcvn_41_2024" and u["level"] == "dieu")
    assert dieu == list(range(1, 85))
    assert not [u for u in units if u["doc_id"] == "tt_51_2024_bgtvt_qcvn41" and u["level"] == "phu_luc"]
    assert any(u["doc_id"] == "qcvn_41_2024" and u["level"] == "khoan" for u in units)


def test_no_empty_annex(units):
    assert [u["unit_id"] for u in units if u["level"] == "phu_luc" and not u["text"].strip()] == []


def test_records_have_annotations(versioned):
    assert all(isinstance(r["noi_dung_doi"], bool) and r["chat_luong"] in ("ok", "kem") for r in versioned)
    assert all((r["loai_phu_luc"] in ("mau_bieu", "noi_dung")) == (r["level"] == "phu_luc")
               for r in versioned)


def test_no_digital_signature_stamp_in_legal_units(units):
    bad = [u["unit_id"] for u in units if u["level"] in ("dieu", "khoan", "diem") and "Ký bởi:" in u["text"]]
    assert bad == []


def test_next_clause_is_not_glued_into_previous_clause(units):
    """Khoản N+1 không nằm dính trong chữ khoản N (ngoài văn bản sửa đổi, nơi khoản nằm trong trích dẫn)."""
    from lawproc import config

    ids = {u["unit_id"] for u in units}
    bad = []
    for u in units:
        if u["level"] != "khoan" or u["doc_id"] in config.AMENDING_DOCS or not (u["khoan"] or "").isdigit():
            continue
        nxt = int(u["khoan"]) + 1
        m = re.search(rf"(?:[.;:]|\))\s+{nxt}\.\s+[A-ZĐÂĂÊÔƠƯ]", u["text"])
        if m and f"{u['doc_id']}:d{u['dieu']}:k{nxt}" not in ids and "“" not in u["text"][:m.start()]:
            bad.append(u["unit_id"])
    assert bad == []


def test_qcvn_keeps_symbols_and_equal_table_cells(versioned):
    text = "\n".join(r["text"] for r in versioned if r["unit_id"] in ("qcvn_41_2024:d55:k7", "qcvn_41_2024:d56:k3",
                                                                       "qcvn_41_2024:d79:k3"))
    for expected in ("30 m < R ≤ 100 m", "độ dốc ≥ 3%", "Ø40 - Ø50", "220 | 400 | 110 | 200 | 10 | 10"):
        assert expected in text, expected


def test_new_licence_plate_annex_is_content_not_form(versioned):
    assert {r["loai_phu_luc"] for r in versioned if r["unit_id"] == "tt_51_2025_bca:pl1"} == {"noi_dung"}


def test_repealed_placeholders_are_not_in_force(versioned):
    repealed = [r for r in versioned if r["trang_thai"] == "bai_bo"]
    # VBHN 63: 19 Điều; VBHN 90: 19 Điều đó cộng Điều 96, 103, 104 (Luật 120/2025 bỏ cai nghiện bắt buộc); BLHS: 1
    assert len(repealed) == 42
    assert not any(_in_force(r) for r in repealed)


def test_annex_replacement_table_is_valid(versioned):
    from lawproc.status import check_annex_replacements, read_csv

    check_annex_replacements(read_csv(PROCESSED.parent / "annex_replacements.csv"), versioned)


def test_tt_12_scoring_table_keeps_columns(versioned):
    # TT 12 đã bị thay; Phụ lục IV còn áp dụng có điều kiện nhờ ngoại lệ gia hạn
    (text,) = [r["text"] for r in versioned if r["unit_id"] == "tt_12_2025_bca:pl4" and _in_force(r)]
    assert "\n| 6. Giữ tốc độ động cơ không quá 4000 vòng/phút;" in text


def test_replaced_licence_plate_annex_is_closed(versioned):
    old = [r for r in versioned if r["unit_id"] == "tt_79_2024_bca:pl18"]
    new = [r for r in versioned if r["unit_id"] == "tt_51_2025_bca:pl1"]
    assert not any(_in_force(r) for r in old) and all(_in_force(r) for r in new)
    assert old[-1]["pl_thay_the"][0]["bang"] == "tt_51_2025_bca:pl1"


def test_manual_corrections_reached_outputs(units):
    """Sửa tay trong ocr_corrections.csv có mặt ở đầu ra: chữ ký NĐ 238 và câu 3 bộ GPLX."""
    assert not [u["unit_id"] for u in units if "daky]" in u["text"]]
    gplx = _read(PROCESSED / "gplx_600.jsonl")
    assert "hầm trên đường bộ để các xe" in gplx[2]["lua_chon"][1]
    assert not [q["so_cau"] for q in gplx if re.search(r"\bb ộ\b", " ".join([q["cau_hoi"], *q["lua_chon"]]))]


def test_tt79_result_delivery_uses_later_issued_tt62(versioned):
    """Khoản 6 Điều 3 TT 79: TT 62 (ban hành 18/5/2026) thắng TT 37 (ban hành 24/4/2026, hiệu lực 08/6/2026)."""
    for day in ("2026-05-18", "2026-06-08", T):
        live = [r for r in versioned if r["unit_id"] == "tt_79_2024_bca:d3:k6" and _in_force(r, day)]
        assert [r["source_doc_id"] for r in live] == ["tt_62_2026_bca"], day
        assert "bản vật lý hoặc nhận dữ liệu điện tử" in live[0]["text"]
