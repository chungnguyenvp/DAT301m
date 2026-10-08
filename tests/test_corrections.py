import pytest

from lawproc.corrections import apply_corrections


def row(wrong, right, doc_id="d"):
    return {"doc_id": doc_id, "wrong": wrong, "right": right, "note": ""}


def test_replaces_exactly_once_in_order():
    text = "Điêu 14 và câp phép\nhết"
    out = apply_corrections(text, [row("Điêu 14", "Điều 14"), row("câp phép", "cấp phép")])
    assert out == "Điều 14 và cấp phép\nhết"


def test_zero_matches_raises_with_the_wrong_string():
    with pytest.raises(ValueError, match="không có trong văn bản"):
        apply_corrections("abc", [row("xyz", "q")])


def test_multiple_matches_raises():
    with pytest.raises(ValueError, match="2 lần"):
        apply_corrections("sô 1 và sô 2", [row("sô", "số")])


def test_multiline_wrong_and_right():
    text = "dòng 1\nrác rác\nrác nữa\ndòng 4"
    out = apply_corrections(text, [row("rác rác\nrác nữa", "dòng 2\ndòng 3")])
    assert out == "dòng 1\ndòng 2\ndòng 3\ndòng 4"


def test_empty_right_deletes():
    assert apply_corrections("a\nnhiễu\nb", [row("\nnhiễu", "")]) == "a\nb"
