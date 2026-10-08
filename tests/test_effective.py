from lawproc.effective import decide_effective, find_effective
from lawproc.structure import parse_units

UNITS = parse_units("nd", [
    "Điều 1. Phạm vi",
    "Nội dung có hiệu lực từ ngày 01 tháng 3 năm 2020 của văn bản khác.",
    "Điều 9. Hiệu lực thi hành",
    "1. Nghị định này có hiệu lực thi hành kể từ ngày 15 tháng 8 năm 2026.",
    "2. Khoản 3 Điều 5 có hiệu lực từ ngày 01 tháng 01 năm 2027.",
])


def test_find_effective_prefers_effect_article():
    r = find_effective(UNITS)
    assert r["dates"] == ["2026-08-15", "2027-01-01"]
    assert r["ngay_ky"] is False
    assert "15 tháng 8 năm 2026" in r["trich_dan"]


def test_find_effective_signing_date():
    r = find_effective(parse_units("x", ["Điều 2. Hiệu lực thi hành", "1. Nghị định này có hiệu lực thi hành kể từ ngày ký ban hành."]))
    assert r["dates"] == []
    assert r["ngay_ky"] is True


def test_decide_rules():
    f = {"dates": ["2026-08-15"], "ngay_ky": False, "trich_dan": ""}
    assert decide_effective("nd", "2026-06-26", "2026-08-15", f) == {"hl_chot": "2026-08-15", "nguon": "khop", "can_duyet": False}
    assert decide_effective("nd", "2026-06-26", "2026-07-01", f)["can_duyet"] is True
    assert decide_effective("nd", "2026-06-26", "", f)["nguon"] == "van_ban"
    sign = {"dates": [], "ngay_ky": True, "trich_dan": ""}
    assert decide_effective("nd", "2025-03-01", "", sign) == {"hl_chot": "2025-03-01", "nguon": "ngay_ky", "can_duyet": True}
    none = {"dates": [], "ngay_ky": False, "trich_dan": ""}
    assert decide_effective("nd", "2025-03-01", "", none)["nguon"] == "khong_thay"
    assert decide_effective("vbhn_63_2025_xlvphc", "2025-08-15", "", f)["can_duyet"] is True


def test_numeric_dates_are_parsed():
    r = find_effective(parse_units("nd", ["Điều 9. Hiệu lực thi hành", "1. Nghị định này có hiệu lực thi hành kể từ ngày 15/8/2026."]))
    assert r["dates"] == ["2026-08-15"]


def test_signing_clause_with_dated_clause_needs_review():
    found = {"dates": ["2025-07-01"], "ngay_ky": True, "trich_dan": ""}
    assert decide_effective("nd", "2025-06-01", "", found)["can_duyet"] is True


def test_multiple_distinct_dates_need_review():
    found = {"dates": ["2026-08-15", "2027-01-01"], "ngay_ky": False, "trich_dan": ""}
    r = decide_effective("nd", "2026-06-26", "2026-08-15", found)
    assert r["nguon"] == "khop"
    assert r["can_duyet"] is True


def test_quoted_replacement_text_is_not_scanned():
    units = parse_units("am", [
        "Điều 1. Sửa đổi",
        "Khoản 2 Điều 5 được sửa đổi như sau: “Nội dung có hiệu lực từ ngày 01 tháng 01 năm 2021”.",
    ])
    assert find_effective(units)["dates"] == []


def test_thi_hanh_title_counts_as_effect_article():
    units = parse_units("am", [
        "Điều 1. Sửa đổi",
        "Điều 2 được sửa đổi như sau: “Điều 2. Nội dung có hiệu lực từ ngày 01 tháng 01 năm 2021”.",
        "Điều 3. Điều khoản thi hành",
        "1. Luật này có hiệu lực từ ngày 15 tháng 8 năm 2026.",
    ])
    f = find_effective(units)
    assert f["dates"] == ["2026-08-15"]
    assert f["tu_dieu_hieu_luc"] is True


def test_no_effect_article_is_flagged_for_review():
    units = parse_units("nd", [
        "Điều 1. Phạm vi",
        "Nghị định này có hiệu lực từ ngày 01 tháng 03 năm 2020.",
    ])
    f = find_effective(units)
    assert f["dates"] == ["2020-03-01"]
    assert f["tu_dieu_hieu_luc"] is False
    assert decide_effective("nd", "2020-01-01", "", f)["can_duyet"] is True
