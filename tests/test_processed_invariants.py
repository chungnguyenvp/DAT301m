"""Kiểm tra bất biến của đầu ra đã commit trong data/processed/ (bỏ qua nếu thiếu file)."""
import json
from collections import defaultdict
from pathlib import Path

import pytest

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
UNITS = PROCESSED / "legal_units.jsonl"
VERSIONED = PROCESSED / "legal_units_versioned.jsonl"
DOCS = PROCESSED / "documents"
T = "2026-10-01"
# TT 108/2026/TT-BCA thay thế toàn bộ TT 12/2025/TT-BCA từ 2026-07-01
FULLY_REPLACED = {"tt_12_2025_bca": "thay thế toàn bộ bởi tt_108_2026_bca từ 2026-07-01"}


def _read(path: Path) -> list[dict]:
    if not path.exists():
        pytest.skip(f"{path.name} chưa có")
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _in_force(r: dict, t: str = T) -> bool:
    return r["valid_from"] <= t and (r["valid_to"] is None or t < r["valid_to"])


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


def test_every_document_has_unit_in_force(versioned):
    if not DOCS.exists():
        pytest.skip("documents/ chưa có")
    live_docs = {r["doc_id"] for r in versioned if _in_force(r)}
    missing = sorted(p.stem for p in DOCS.glob("*.txt") if p.stem not in live_docs and p.stem not in FULLY_REPLACED)
    assert missing == []
    # văn bản được phép không còn đơn vị hiệu lực phải thật sự bị đóng hết
    for doc in FULLY_REPLACED:
        assert not any(r["doc_id"] == doc and _in_force(r) for r in versioned), doc
