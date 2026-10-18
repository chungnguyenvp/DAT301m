import pytest

from lawproc import evalset, trainset

HELMET = "nd_168_2024:d7:k2:h@2025-01-01"
HELMET_LEAD = "nd_168_2024:d7:k2@2025-01-01"
RED_LIGHT = "nd_168_2024:d7:k7:c@2025-01-01"
RED_LIGHT_LEAD = "nd_168_2024:d7:k7@2025-01-01"
RED_LIGHT_POINTS = "nd_168_2024:d7:k13:b@2025-01-01"


@pytest.fixture(scope="module")
def records():
    return evalset.load_versions()


def _s(key="xp-0001", loai="muc_phat", cau_hoi="Không đội mũ bảo hiểm khi lái xe máy bị phạt bao nhiêu?",
       dap_an="Phạt tiền từ 400.000 đồng đến 600.000 đồng (điểm h khoản 2 Điều 7 Nghị định 168/2024/NĐ-CP).",
       can_cu=(HELMET, HELMET_LEAD), **kw):
    return {"key": key, "chu_de": "Xử phạt", "loai": loai, "cau_hoi": cau_hoi, "dap_an": dap_an,
            "can_cu": list(can_cu), **kw}


def test_split_keeps_each_article_on_one_side_and_is_stable():
    ids = [f"nd_x:d{i}:k{k}" for i in range(1, 2001) for k in (1, 2)]
    sides = {uid: trainset.split_of(uid) for uid in ids}
    assert all(sides[f"nd_x:d{i}:k1"] == sides[f"nd_x:d{i}:k2"] for i in range(1, 2001))
    share = sum(s == "dev" for s in sides.values()) / len(sides)
    assert 0.07 < share < 0.13
    assert trainset.split_of("nd_x:d5:k1") == trainset.split_of("nd_x:d5:k1:a") == sides["nd_x:d5:k1"]


def test_topic_comes_from_the_manifest_group():
    assert trainset.topic_of("nd_168_2024") == "Xử phạt"
    assert trainset.topic_of("qcvn_41_2024") == "Biển báo"


def test_a_correct_sample_passes(records):
    assert trainset.check_samples([_s()], records) == []


def test_wrong_amount_is_caught(records):
    bad = _s(dap_an="Phạt tiền từ 500.000 đồng đến 600.000 đồng (điểm h khoản 2 Điều 7 Nghị định 168/2024/NĐ-CP).")
    assert any("500" in p for p in trainset.check_samples([bad], records))


def test_missing_point_deduction_is_caught(records):
    no_points = _s(key="xp-0002", cau_hoi="Xe máy vượt đèn đỏ bị phạt bao nhiêu?",
                   dap_an="Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng (điểm c khoản 7 Điều 7 Nghị định 168/2024/NĐ-CP).",
                   can_cu=(RED_LIGHT, RED_LIGHT_LEAD))
    assert any("trừ" in p for p in trainset.check_samples([no_points], records))
    full = dict(no_points, dap_an=no_points["dap_an"] + " Ngoài ra bị trừ điểm giấy phép lái xe 04 điểm "
                                                     "(điểm b khoản 13 Điều 7).",
                can_cu=[RED_LIGHT, RED_LIGHT_LEAD, RED_LIGHT_POINTS])
    assert trainset.check_samples([full], records) == []


def test_refusal_must_have_no_citation(records):
    ok = _s(key="tc-0001", loai="tu_choi", cau_hoi="Luật hàng hải quy định gì về tàu cá?",
            dap_an="Câu hỏi này nằm ngoài phạm vi tài liệu luật giao thông đường bộ hiện có.", can_cu=())
    assert trainset.check_samples([ok], records) == []
    assert trainset.check_samples([dict(ok, can_cu=[HELMET])], records)


def test_duplicate_keys_and_unknown_type_are_caught(records):
    problems = trainset.check_samples([_s(), _s(cau_hoi="Câu khác hẳn về mũ bảo hiểm?"), _s(key="x", loai="la")],
                                      records)
    assert any("key trùng" in p for p in problems) and any("loai lạ" in p for p in problems)


def test_questions_too_close_to_eval_are_flagged():
    eval_items = [{"id": "TH135", "cau_hoi": "Người điều khiển xe máy không đội mũ bảo hiểm khi tham gia giao thông "
                                            "bị phạt bao nhiêu tiền?"}]
    near = _s(key="a", cau_hoi="Người điều khiển xe máy không đội mũ bảo hiểm khi tham gia giao thông bị phạt "
                               "bao nhiêu tiền vậy?")
    far = _s(key="b", cau_hoi="Thủ tục cấp đổi giấy phép lái xe quốc tế gồm những giấy tờ gì?")
    flagged = trainset.near_eval([near, far], eval_items, threshold=0.8)
    assert [s["key"] for s, _, _ in flagged] == ["a"] and flagged[0][1] == "TH135"


def test_same_fact_paraphrase_is_flagged_but_a_different_fact_is_kept():
    eval_items = [{"id": "TH135", "can_cu": [HELMET, HELMET_LEAD],
                   "cau_hoi": "Người điều khiển xe máy không đội mũ bảo hiểm khi tham gia giao thông bị phạt bao nhiêu tiền?"}]
    same_fact = _s(key="a", cau_hoi="Không đội mũ bảo hiểm khi điều khiển xe máy bị phạt bao nhiêu?")
    other_fact = _s(key="b", cau_hoi="Không đội mũ bảo hiểm khi điều khiển xe máy bị phạt bao nhiêu?",
                    can_cu=("nd_168_2024:d9:k4:d@2025-01-01",))
    # Ngưỡng thấp vì TF-IDF trên 3 câu cho cosine khác tập thật; điều cần kiểm là quy tắc "cùng quy định".
    flagged = trainset.near_eval([same_fact, other_fact], eval_items, threshold=0.85, same_unit_threshold=0.2)
    assert [s["key"] for s, _, _ in flagged] == ["a"]


def test_gplx_exam_questions_are_part_of_the_held_out_set():
    items = trainset.gplx_items()
    assert len(items) == 281  # 282 câu thuần chữ trừ câu 172 (đáp án lệch luật từ 01/7/2026)
    assert all(x["id"].startswith("GPLX") and x["can_cu"] == [] for x in items)
    assert "GPLX172" not in {x["id"] for x in items}
    copied = _s(key="g", cau_hoi=items[0]["cau_hoi"])
    assert [eid for _, eid, _ in trainset.near_eval([copied], items, threshold=0.85)] == [items[0]["id"]]


def test_same_fact_ignores_shared_clause_leads_and_sanction_lists():
    assert trainset._same_fact(["nd_x:d7:k11@v", "nd_x:d7:k11:a@v", "nd_x:d7:k12:c@v"],
                               ["nd_x:d7:k11:a@v", "nd_x:d7:k11@v"])
    # Cùng câu dẫn khoản 2 nhưng khác Điểm (mũ bảo hiểm và quá tốc độ): không phải cùng quy định.
    assert not trainset._same_fact(["nd_x:d7:k2:h@v", "nd_x:d7:k2@v"], ["nd_x:d7:k2:b@v", "nd_x:d7:k2@v"])
    # Cùng khoản trừ 04 điểm nhưng khác hành vi (điện thoại và vượt đèn đỏ).
    assert not trainset._same_fact(["nd_x:d7:k4:đ@v", "nd_x:d7:k4@v", "nd_x:d7:k13:b@v"],
                                   ["nd_x:d7:k7:c@v", "nd_x:d7:k7@v", "nd_x:d7:k13:b@v"])
