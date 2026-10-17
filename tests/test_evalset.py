import json
from collections import Counter

import pytest

from lawproc import evalset


def _rec(uid, text, vf="2025-01-01", vt=None, doc="nd_x"):
    return {"unit_id": uid, "doc_id": doc, "version_id": f"{uid}@{vf}", "text": text, "valid_from": vf,
            "valid_to": vt, "hl_ngoai_le": [], "trong_pham_vi": True, "level": "diem"}


RECS = [
    _rec("nd_x:d7:k2", "Phạt tiền từ 400.000 đồng đến 600.000 đồng đối với người điều khiển xe:"),
    _rec("nd_x:d7:k2:h", "Không đội mũ bảo hiểm;"),
    _rec("nd_x:d7:k13:b", "Thực hiện hành vi quy định tại khoản 2 bị trừ điểm giấy phép lái xe 04 điểm;"),
    _rec("nd_x:d43:k1:b", "Phạt tiền đến 500.000 đồng.", vt="2026-08-15"),
    _rec("nd_x:d43:k1:b", "Phạt tiền đến 7.500.000 đồng;", vf="2026-08-15"),
]


def _item(**kw):
    base = {"id": "TH001", "tap": "test", "nhom_cau": "thuong", "cau_hoi": "Không đội mũ bảo hiểm phạt bao nhiêu?",
            "dap_an": "Phạt tiền từ 400.000 đồng đến 600.000 đồng.", "chu_de": "Xử phạt", "loai_cau": "mức phạt",
            "ngay_hoi": "2026-10-01", "can_cu": ["nd_x:d7:k2:h@2025-01-01"], "van_ban": "nd_x",
            "muc_phat_min": 400000, "muc_phat_max": 600000, "diem_tru": None}
    base.update(kw)
    return base


def test_valid_item_passes_and_fine_comes_from_parent_clause():
    assert evalset.check_items([_item()], RECS) == []


@pytest.mark.parametrize(("change", "message"), [
    ({"can_cu": ["nd_x:d7:k2:h@2024-01-01"]}, "không có phiên bản"),
    ({"muc_phat_max": 700000}, "muc_phat_max 700000"),
    ({"dap_an": "Phạt tiền từ 400.000 đồng đến 6.000.000 đồng."}, "6,000,000"),
    ({"diem_tru": 6, "can_cu": ["nd_x:d7:k2:h@2025-01-01", "nd_x:d7:k13:b@2025-01-01"]}, "diem_tru 6"),
    ({"can_cu": ["nd_x:d43:k1:b@2025-01-01"], "muc_phat_min": None, "muc_phat_max": None,
      "dap_an": "Phạt tiền đến 500.000 đồng."}, "không có hiệu lực"),
    ({"van_ban": "nd_y"}, "van_ban nd_y"),
])
def test_problems_are_reported(change, message):
    problems = evalset.check_items([_item(**change)], RECS)
    assert any(message in p for p in problems), problems


def test_point_deduction_found_in_cited_clause():
    item = _item(diem_tru=4, can_cu=["nd_x:d7:k2:h@2025-01-01", "nd_x:d7:k13:b@2025-01-01"])
    assert evalset.check_items([item], RECS) == []


def test_amended_item_needs_old_version_out_of_force():
    item = _item(id="SD001", nhom_cau="sua_doi", can_cu=["nd_x:d43:k1:b@2026-08-15"], muc_phat_min=None,
                 muc_phat_max=None, dap_an="Phạt tiền đến 7.500.000 đồng.", dap_an_cu="Phạt tiền đến 500.000 đồng.",
                 can_cu_cu=["nd_x:d43:k1:b@2025-01-01"], ngay_cu="2026-06-01")
    assert evalset.check_items([item], RECS) == []
    stale = dict(item, can_cu_cu=["nd_x:d43:k1:b@2026-08-15"], ngay_cu="2026-09-01")
    assert any("vẫn còn hiệu lực" in p for p in evalset.check_items([stale], RECS))
    wrong_old_money = dict(item, dap_an_cu="Phạt tiền đến 5.000.000 đồng.")
    assert any("dap_an_cu có số liệu" in p for p in evalset.check_items([wrong_old_money], RECS))


def test_refusal_and_variant_rules():
    refusal = _item(id="NP001", nhom_cau="ngoai_pham_vi", can_cu=[], hanh_vi="tu_choi", dap_an="Từ chối.")
    assert evalset.check_items([refusal], RECS) == []
    with_citation = dict(refusal, can_cu=["nd_x:d7:k2:h@2025-01-01"])
    assert any("không được có căn cứ" in p for p in evalset.check_items([with_citation], RECS))
    base = _item()
    variant = _item(id="BT001", nhom_cau="bien_the", goc_id="TH001", kieu_bien_the="khong_dau",
                    cau_hoi="khong doi mu bao hiem phat bao nhieu")
    assert evalset.check_items([base, variant], RECS) == []
    other_split = dict(variant, tap="dev")
    assert any("khác tập" in p for p in evalset.check_items([base, other_split], RECS))


def test_duplicate_questions_are_reported():
    problems = evalset.check_items([_item(), _item(id="TH002")], RECS)
    assert any("câu hỏi trùng" in p for p in problems)


@pytest.fixture(scope="module")
def eval_v1():
    path = evalset.EVAL / "eval_v1.jsonl"
    if not path.exists():
        pytest.skip("chưa có data/eval/eval_v1.jsonl")
    return evalset.load_eval(path)


def test_eval_v1_matches_data(eval_v1):
    assert evalset.check_items(eval_v1, evalset.load_versions()) == []


def test_eval_v1_composition(eval_v1):
    groups = Counter(x["nhom_cau"] for x in eval_v1)
    assert groups == {"thuong": 150, "sua_doi": 40, "ngoai_pham_vi": 30, "bien_the": 50}
    assert Counter(x["tap"] for x in eval_v1) == {"dev": 30, "test": 240}
    matrix = {(r["chu_de"], r["loai_cau"]): int(r["so_cau"])
              for r in __import__("csv").DictReader((evalset.EVAL / "eval_matrix.csv").open(encoding="utf-8-sig"))}
    got = Counter((x["chu_de"], x["loai_cau"]) for x in eval_v1 if x["nhom_cau"] == "thuong")
    assert dict(got) == matrix


def test_eval_v1_is_plain_jsonl(eval_v1):
    raw = (evalset.EVAL / "eval_v1.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(raw) == len(eval_v1) and all(json.loads(line)["id"] for line in raw)


def test_ref_list_parses_sanction_clauses():
    text = "Thực hiện hành vi quy định tại điểm b khoản 3; khoản 5; điểm b, điểm c, điểm d khoản 6; điểm a khoản 7 Điều này"
    refs = evalset.ref_list(text)
    assert ("3", "b") in refs and ("5", None) in refs and ("6", "d") in refs and ("7", "a") in refs
    assert evalset.covers(refs, "nd_x:d7:k5:c") and not evalset.covers(refs, "nd_x:d7:k3:a")


def test_number_facts_normalise_units():
    found = evalset.facts("phạt từ 1.400.000 đồng, giá 40 (bốn mươi) triệu đồng, trong 02 ngày làm việc, 7,5 tháng")
    assert {(1_400_000.0, "đồng"), (40_000_000.0, "đồng"), (2.0, "ngày làm việc"), (7.5, "tháng")} <= found


@pytest.fixture(scope="module")
def records():
    return evalset.load_versions()


# Sáu phép sửa sai của bản review độc lập 2026-10-17 (docs/reviews/eval-audit-2026-10-17): đều phải bị bắt.
MUTATIONS = [
    ("xp01", lambda x: {"muc_phat_min": 600000, "muc_phat_max": 400000}, "lớn hơn"),
    ("xp01", lambda x: {"dap_an": "Phạt 1 đồng."}, "số liệu 1 đồng"),
    ("xp04", lambda x: {"dap_an": x["dap_an"].replace("22 tháng đến 24 tháng", "01 tháng đến 02 tháng")}, "tháng"),
    ("xp01", lambda x: {"dap_an": x["dap_an"].replace("điểm h khoản 2 Điều 7", "điểm z khoản 99 Điều 999")},
     "trích dẫn"),
    ("sd24", lambda x: {"dap_an": x["dap_an"].replace("02 ngày", "99 ngày")}, "99 ngày"),
    ("xp01", lambda x: {"diem_tru": 4, "can_cu": x["can_cu"] + ["nd_168_2024:d7:k13:b@2025-01-01"],
                        "dap_an": x["dap_an"] + " Trừ 04 điểm giấy phép lái xe."}, "hành vi khác"),
]


@pytest.mark.parametrize(("key", "change", "message"), MUTATIONS)
def test_review_mutations_are_rejected(eval_v1, records, key, change, message):
    item = next(x for x in eval_v1 if x["key"] == key)
    mutated = dict(item, **change(item))
    assert mutated != item
    problems = evalset.check_items([mutated], records)
    assert any(message in p for p in problems), problems


def test_missing_sanction_in_answer_is_rejected(eval_v1, records):
    item = next(x for x in eval_v1 if x["key"] == "xp04")
    cut = dict(item, dap_an=item["dap_an"].split(" và bị tước")[0] + ".")
    assert any("thiếu chế tài tước" in p for p in evalset.check_items([cut], records))


def test_split_manifest_covers_all_non_variant_keys(eval_v1):
    split = json.loads((evalset.EVAL / "split_v1.json").read_text(encoding="utf-8"))
    for x in eval_v1:
        if x["nhom_cau"] != "bien_the":
            assert split[f"{x['nhom_cau']}/{x['key']}"] == x["tap"]


# Phép sửa sai của review vòng hai (docs/reviews/eval-rereview-2026-10-17).
ROUND2 = [
    ("gp13", lambda x: {"dap_an": x["dap_an"].replace("27/30", "26/30")}, "26/30"),
    ("sd24", lambda x: {"dap_an": x["dap_an"].replace("02 ngày làm việc", "02 ngày")}, "2 ngày"),
    ("xp01", lambda x: {"dap_an": x["dap_an"].replace("từ 400.000 đồng", "từ 600.000 đồng")}, "khung"),
]


@pytest.mark.parametrize(("key", "change", "message"), ROUND2)
def test_round_two_mutations_are_rejected(eval_v1, records, key, change, message):
    item = next(x for x in eval_v1 if x["key"] == key)
    mutated = dict(item, **change(item))
    assert mutated != item
    assert any(message in p for p in evalset.check_items([mutated], records))


def test_ratio_keeps_pass_mark():
    assert ("27/30", "điểm") in evalset.facts("đạt từ 27/30 điểm trở lên")
    assert (2.0, "ngày làm việc") in evalset.facts("trong 02 ngày làm việc")
    assert (2.0, "ngày") not in evalset.facts("trong 02 ngày làm việc")


def test_each_citation_is_a_required_group(eval_v1):
    gp01 = next(x for x in eval_v1 if x["key"] == "gp01")
    assert len(gp01["nhom_can_cu"]) == 5 and all(len(g) == 1 for g in gp01["nhom_can_cu"])
    ll05 = next(x for x in eval_v1 if x["key"] == "ll05")
    lead = "luat_36_2024:d33:k3@2025-01-01"
    assert [lead] in ll05["nhom_can_cu"] and len(ll05["nhom_can_cu"]) == len(ll05["can_cu"])


def test_event_family_links_regular_and_amended_questions(eval_v1):
    by_key = {x["key"]: x for x in eval_v1}
    assert by_key["gp17"]["ho_su_kien"] == by_key["sd34"]["ho_su_kien"]


def test_manifest_hash_matches_eval_file(eval_v1):
    import hashlib
    manifest = json.loads((evalset.EVAL / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["eval"]["sha256"] == hashlib.sha256((evalset.EVAL / "eval_v1.jsonl").read_bytes()).hexdigest()
