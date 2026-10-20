from rag import expand


def _k(cid, dieu="7", tok=100, units=None, vf="2025-01-01", vt=None, doc="nd_x"):
    return {"chunk_id": cid, "doc_id": doc, "dieu": dieu, "units": units or [cid], "so_token": tok,
            "valid_from": vf, "valid_to": vt}


D7 = _k("dieu7", units=["k1", "k2", "k3"], tok=600)
D7_OLD = _k("dieu7_old", units=["k1", "k2", "k3"], tok=500, vt="2026-01-01")
D9 = _k("dieu9", dieu="9", units=["k9"], tok=5000)
INDEX = expand.parent_index([D7, D7_OLD, D9])
T = "2026-10-01"


def test_parent_is_in_force_and_contains_units():
    assert expand.parent_of(_k("k1"), INDEX, T)["chunk_id"] == "dieu7"
    assert expand.parent_of(_k("k1"), INDEX, "2025-06-01")["chunk_id"] == "dieu7_old"   # nhỏ nhất còn hiệu lực
    assert expand.parent_of(_k("k4"), INDEX, T) is None          # Điều không chứa đơn vị này
    assert expand.parent_of(_k("pl1", dieu=None), INDEX, T) is None


def test_expand_replaces_by_parent_and_skips_covered_siblings():
    ranked = [_k("k1"), _k("k2"), _k("k9", dieu="9"), _k("x", dieu="11")]
    out = expand.expand_to_dieu(ranked, T, INDEX, budget=2500)
    assert [c["chunk_id"] for c in out] == ["dieu7", "k9", "x"]   # k2 đã nằm trong Điều 7; Điều 9 quá ngân sách


def test_expand_respects_budget_and_max_pieces():
    ranked = [_k(f"z{i}", dieu=str(20 + i), tok=400) for i in range(10)]
    out = expand.expand_to_dieu(ranked, T, INDEX, budget=1000, max_pieces=5)
    assert [c["chunk_id"] for c in out] == ["z0", "z1"]
    out = expand.expand_to_dieu(ranked, T, INDEX, budget=10_000, max_pieces=3)
    assert len(out) == 3
