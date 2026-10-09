import unicodedata

from lawproc.quality import syllable_error_rate


def test_clean_vietnamese_has_zero_rate():
    assert syllable_error_rate("Người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông") == 0.0


def test_abbreviations_numbers_and_single_letters_are_ignored():
    assert syllable_error_rate("GPLX hạng B1 theo Nghị định số 168/2024/NĐ-CP, điểm a") == 0.0
    assert syllable_error_rate("word123 123word A1 12/2025 —") == 0.0


def test_ocr_junk_has_high_rate():
    assert syllable_error_rate("la Xeôtô wW0W0W ốơúó lbXxemt To000 Câpđôibiênsôxe Sa Xeono lbFemôo") > 0.5


def test_empty_text_is_zero():
    assert syllable_error_rate("12/2025 —") == 0.0
    assert syllable_error_rate("") == 0.0


def test_canonical_unicode_and_tone_limitation():
    text = "Người điều khiển"
    assert syllable_error_rate(unicodedata.normalize("NFD", text)) == syllable_error_rate(text)
    assert syllable_error_rate("Bé trí") == 0.0


def test_rate_is_rounded_fraction():
    assert syllable_error_rate("người xe xyz") == 0.3333
