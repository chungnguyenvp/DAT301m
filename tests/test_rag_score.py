import pytest

from lawproc import evalset
from rag import score


def _chunk(*units, doc="nd_x"):
    return {"chunk_id": "|".join(units) or "rong", "doc_id": doc, "units": list(units)}


def _item(id_="TH001", nhom_cau="thuong", can_cu=("nd_x:d7:k2:a@v", "nd_x:d7:k2:b@v"), **kw):
    item = {"id": id_, "key": id_.lower(), "tap": "test", "nhom_cau": nhom_cau, "van_ban": "nd_x",
            "can_cu": list(can_cu), "nhom_can_cu": [[v] for v in can_cu], "ho_su_kien": id_, "ho_cau": id_}
    item.update(kw)
    return item


@pytest.fixture(scope="module")
def by_key():
    return {x["key"]: x for x in evalset.load_eval()}


def test_full_clause_chunk_satisfies_every_point():
    row = score.score_item(_item(), [_chunk("nd_x:d7:k2@v", "nd_x:d7:k2:a@v", "nd_x:d7:k2:b@v")])
    assert (row["any"], row["all"], row["ty_le_nhom"], row["van_ban"], row["rr"]) == (True, True, 1.0, True, 1.0)
    assert row["nhom_thieu"] == [] and row["so_nhom"] == 2


def test_gp01_one_point_only_is_one_of_five(by_key):
    item = by_key["gp01"]
    assert len(item["nhom_can_cu"]) == 5
    row = score.score_item(item, [_chunk(item["can_cu"][0], doc=item["van_ban"])])
    assert (row["any"], row["all"], row["ty_le_nhom"]) == (True, False, 0.2)
    assert row["nhom_thieu"] == [[v] for v in item["can_cu"][1:]]


def test_ll05_lead_sentence_alone_is_one_of_eight(by_key):
    item = by_key["ll05"]
    lead = "luat_36_2024:d33:k3@2025-01-01"
    assert item["nhom_can_cu"][0] == [lead] and len(item["nhom_can_cu"]) == 8
    row = score.score_item(item, [_chunk(lead, doc="luat_36_2024")])
    assert (row["all"], row["ty_le_nhom"]) == (False, 1 / 8)


def test_rank_and_cutoff():
    ranked = [_chunk("nd_x:d9:k1@v"), _chunk("nd_x:d7:k2:b@v")]
    row = score.score_item(_item(), ranked)
    assert (row["rr"], row["hang_dau_dung"], row["any"], row["all"]) == (0.5, 2, True, False)
    row = score.score_item(_item(), [_chunk("nd_x:d9:k1@v")] * 5 + [_chunk("nd_x:d7:k2:a@v")], k=5)
    assert (row["rr"], row["hang_dau_dung"], row["any"]) == (0.0, None, False)


def test_wrong_document_and_out_of_scope():
    row = score.score_item(_item(), [_chunk("tt_y:d1:k1@v", doc="tt_y")])
    assert (row["van_ban"], row["any"]) == (False, False)
    assert score.score_item(_item(nhom_cau="ngoai_pham_vi", can_cu=()), [_chunk("nd_x:d7:k2:a@v")]) is None


def test_old_version_in_results_is_flagged_for_amended_questions():
    item = _item("SD001", "sua_doi", can_cu=("nd_x:d34:k4:b@new",), can_cu_cu=["nd_x:d34:k4:b@old"])
    assert score.score_item(item, [_chunk("nd_x:d34:k4:b@old")])["nham_ban_cu"] is True
    assert score.score_item(item, [_chunk("nd_x:d34:k4:b@new")])["nham_ban_cu"] is False
    assert score.score_item(_item(), [_chunk("nd_x:d7:k2:a@v")])["nham_ban_cu"] is None


def _rows_and_items():
    items = [_item(f"TH00{i}", ho_su_kien="nd_x:d7:k2" if i < 3 else f"TH00{i}") for i in range(1, 5)]
    items += [_item("SD001", "sua_doi", can_cu=("nd_x:d34:k4:b@new",), can_cu_cu=["nd_x:d34:k4:b@old"])]
    hits = {"TH001": ["nd_x:d7:k2:a@v", "nd_x:d7:k2:b@v"], "TH002": ["nd_x:d7:k2:a@v"], "TH003": [],
            "TH004": ["nd_x:d7:k2:b@v"], "SD001": ["nd_x:d34:k4:b@new"]}
    rows = [score.score_item(x, [_chunk(*hits[x["id"]])] if hits[x["id"]] else []) for x in items]
    return rows, items


def test_summary_reports_denominators_per_question_group():
    rows, items = _rows_and_items()
    out = score.summarize(rows, items, n_boot=200, seed=1)
    assert out["thuong"]["n"] == 4 and out["sua_doi"]["n"] == 1
    assert out["thuong"]["all"]["gia_tri"] == 0.25 and out["thuong"]["any"]["gia_tri"] == 0.75
    assert out["thuong"]["ty_le_nhom"]["gia_tri"] == pytest.approx((1 + 0.5 + 0 + 0.5) / 4)
    assert out["thuong"]["mrr"]["gia_tri"] == 0.75
    assert "nham_ban_cu" not in out["thuong"] and out["sua_doi"]["nham_ban_cu"]["gia_tri"] == 0.0
    lo, hi = out["thuong"]["any"]["ci95"]
    assert 0.0 <= lo <= 0.75 <= hi <= 1.0


def test_bootstrap_resamples_whole_event_families_and_is_reproducible():
    rows, items = _rows_and_items()
    a = score.summarize(rows, items, n_boot=300, seed=7)
    assert a == score.summarize(rows, items, n_boot=300, seed=7)
    assert a["thuong"]["so_ho"] == 3  # TH001–TH002 chung họ nd_x:d7:k2


VID = "tt_x:pl1@v"


def _piece(text, a, b, n=10):
    return {"chunk_id": f"pl1#{a}", "doc_id": "tt_x", "units": [VID], "phan_dong": {VID: [a, b, n]}, "text": text}


def test_annex_piece_counts_only_when_it_holds_the_needed_lines():
    item = _item(can_cu=(VID,), key="x", van_ban="tt_x")
    evidence = {"x": {VID: ["II.2. Cấp đổi không kèm biển số: 35.000 đồng."]}}
    wrong = _piece("Phụ lục\nI.1. Cấp mới: 350.000 đồng.", 0, 4)
    right = _piece("Phụ lục\nII.2. Cấp đổi không kèm biển số: 35.000 đồng.", 5, 9)
    row = score.score_item(item, [wrong], evidence=evidence)
    assert (row["any"], row["all"], row["rr"], row["nhom_thieu"]) == (False, False, 0.0, [[VID]])
    assert row["van_ban"] is True
    row = score.score_item(item, [wrong, right], evidence=evidence)
    assert (row["all"], row["rr"], row["hang_dau_dung"]) == (True, 0.5, 2)


def test_annex_without_annotation_needs_every_piece():
    item = _item(can_cu=(VID,), key="x")
    first, second = _piece("a", 0, 4), _piece("b", 5, 9)
    assert score.score_item(item, [first], evidence={})["all"] is False
    assert score.score_item(item, [second, first], evidence={})["all"] is True


def test_whole_unit_chunk_still_counts_without_annotation():
    item = _item(can_cu=(VID,), key="x")
    row = score.score_item(item, [{"chunk_id": "c", "doc_id": "tt_x", "units": [VID], "phan_dong": {}, "text": ""}],
                           evidence={"x": {VID: ["dòng không có trong chữ"]}})
    assert row["all"] is True


def test_rank_is_where_the_first_group_is_satisfied():
    item = _item(can_cu=(VID, "nd_x:d5:k2@v"), key="x")
    evidence = {"x": {VID: ["dòng A", "dòng B"]}}
    ranked = [_piece("dòng A", 0, 4), {"chunk_id": "k", "doc_id": "nd_x", "units": ["nd_x:d5:k2@v"], "text": ""},
              _piece("dòng B", 5, 9)]
    row = score.score_item(item, ranked, evidence=evidence)
    assert (row["rr"], row["all"]) == (0.5, True)
    assert score.score_item(item, [ranked[0], ranked[2]], evidence=evidence)["rr"] == 0.5


# ---- File bằng chứng và chunk thật ----

@pytest.fixture(scope="module")
def saved_chunks():
    import json

    from lawproc import config

    out = {}
    for cut in ("khoan", "dieu"):
        path = config.DATA / "rag" / f"chunks_{cut}.jsonl"
        if not path.exists():
            pytest.skip("chưa build data/rag")
        out[cut] = [json.loads(line) for line in path.open(encoding="utf-8")]
    return out


def _live(chunks, t):
    from rag import chunking

    return [c for c in chunks if chunking.in_force(c, t)]


def test_evidence_lines_are_real_lines_and_cover_the_answer_amounts(by_key):
    from lawproc import evalset

    texts = {r["version_id"]: r["text"] for r in evalset.load_versions()}
    for key, units in score.load_evidence().items():
        item = by_key[key]
        support = [item["cau_hoi"]] + [texts[v] for v in item["can_cu"] if v not in units]
        for vid, lines in units.items():
            assert vid in item["can_cu"]
            assert all(line in texts[vid].split("\n") for line in lines), (key, vid)
            support += lines
        assert evalset.money_values(item["dap_an"]) <= evalset.money_values("\n".join(support)), key


@pytest.mark.parametrize("cut", ["khoan", "dieu"])
def test_every_citation_split_into_pieces_has_evidence_lines(saved_chunks, by_key, cut):
    evidence = score.load_evidence()
    missing = []
    for item in by_key.values():
        live = _live(saved_chunks[cut], item.get("ngay_hoi") or "2026-10-01")
        for vid in item.get("can_cu") or []:
            if any(vid in c.get("phan_dong", {}) for c in live) and vid not in evidence.get(item["key"], {}):
                missing.append((item["key"], vid))
    assert missing == []


@pytest.mark.parametrize("cut", ["khoan", "dieu"])
@pytest.mark.parametrize("key", ["lp06", "lp07", "lp08", "bt04"])
def test_wrong_annex_piece_is_not_full_evidence(saved_chunks, by_key, cut, key):
    item = by_key[key]
    live = _live(saved_chunks[cut], item["ngay_hoi"])
    annex = "tt_155_2025_btc:pl1@2026-01-01"
    needed = score.load_evidence()[key][annex]
    pieces = [c for c in live if annex in c.get("phan_dong", {})]
    right = [c for c in pieces if all(line in c["text"] for line in needed)]
    wrong = [c for c in pieces if c not in right]
    support = [c for c in live if set(c["units"]) & (set(item["can_cu"]) - {annex}) and not c.get("phan_dong")]
    support = list({c["chunk_id"]: c for c in support}.values())
    assert right and wrong
    assert score.score_item(item, wrong + support, k=20)["all"] is False
    assert score.score_item(item, right + support, k=20)["all"] is True
    if key == "lp08":
        only_first = score.score_item(item, [pieces[0]])
        assert (only_first["all"], only_first["rr"]) == (False, 0.0)


def test_variant_gap_pairs_each_variant_with_its_base():
    base = _item("TH001")
    variant = _item("BT001", "bien_the", goc_id="TH001", ho_cau="TH001")
    rows = [score.score_item(base, [_chunk("nd_x:d7:k2:a@v", "nd_x:d7:k2:b@v")]),
            score.score_item(variant, [_chunk("nd_x:d7:k2:a@v")])]
    gap = score.variant_gap(rows, [base, variant])
    assert gap["n"] == 1
    assert gap["all"] == {"bien_the": 0.0, "goc": 1.0, "chenh": -1.0}
    assert gap["ty_le_nhom"]["chenh"] == -0.5
