import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import g9_demo as g9  # noqa: E402


@pytest.mark.parametrize("s, iso", [("01/03/2026", "2026-03-01"), ("2026-03-01", "2026-03-01"),
                                    ("1/3/2026", "2026-03-01"), ("01-03-2026", "2026-03-01"), ("", g9.DEFAULT_DATE)])
def test_parse_date(s, iso):
    assert g9.parse_date(s) == iso


def test_parse_date_rejects_garbage():
    with pytest.raises(ValueError):
        g9.parse_date("hôm qua")


def chunk(valid_from, valid_to=None, text="Phạt tiền <b> & co"):
    return {"doc_id": "nd_168_2024", "dieu": "6", "khoan": "9", "valid_from": valid_from, "valid_to": valid_to,
            "text": text}


def test_sources_markdown_flags_out_of_force_and_escapes():
    md = g9.sources_markdown([chunk("2025-01-01"), chunk("2025-01-01", "2026-01-01")], "2026-03-01", loc=False)
    assert "**không** lọc hiệu lực" in md
    assert md.count("không còn/chưa có hiệu lực") == 1   # chỉ đoạn thứ hai hết hiệu lực tại ngày hỏi
    assert "khoản 9 Điều 6" in md and "&lt;b&gt; &amp; co" in md


def test_answer_block_adds_disclaimer_only_when_done():
    assert g9.CANH_BAO not in g9.answer_block("D", "Phạt 1 triệu.", done=False)
    assert g9.answer_block("B", "", done=True).endswith(g9.CANH_BAO)
