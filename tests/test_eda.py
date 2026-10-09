import pytest

from lawproc import config, eda


def test_money_and_fine():
    assert eda.money("1.000.000") == 1_000_000
    text = ("Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe thực hiện "
            "một trong các hành vi vi phạm sau đây:")
    assert eda.extract_fine(text) == (800_000, 1_000_000)
    both = ("Phạt tiền từ 5.000.000 đồng đến 6.000.000 đồng đối với cá nhân, từ 10.000.000 đồng đến "
            "12.000.000 đồng đối với tổ chức là chủ xe")
    assert eda.extract_fine(both) == (5_000_000, 6_000_000)
    assert eda.extract_fine("Tịch thu phương tiện") is None


def test_extract_points():
    text = "Thực hiện hành vi quy định tại điểm a khoản 9 Điều này bị trừ điểm giấy phép lái xe 04 điểm;"
    assert eda.extract_points(text) == 4
    assert eda.extract_points("bị tước quyền sử dụng giấy phép lái xe") is None


@pytest.mark.parametrize(("title", "group"), [
    ("Xử phạt người điều khiển xe ô tô, xe chở người bốn bánh có gắn động cơ vi phạm quy tắc", "Ô tô"),
    ("Xử phạt người điều khiển xe chở người bốn bánh có gắn động cơ", "Ô tô"),
    ("Xử phạt người điều khiển xe chở hàng bốn bánh có gắn động cơ", "Ô tô"),
    ("Xử phạt người điều khiển xe cứu thương", "Ô tô"),
    ("Xử phạt người điều khiển xe mô tô, xe gắn máy, các loại xe tương tự xe mô tô", "Mô tô, xe gắn máy"),
    ("Xử phạt người điều khiển xe máy chuyên dùng vi phạm quy tắc", "Xe máy chuyên dùng"),
    ("Xử phạt người điều khiển xe đạp, xe đạp máy, xe thô sơ", "Xe đạp, xe thô sơ"),
    ("Xử phạt người đi bộ vi phạm quy tắc giao thông đường bộ", "Người đi bộ"),
    ("Xử phạt các hành vi vi phạm khác", "Khác"),
])
def test_vehicle_group(title, group):
    assert eda.vehicle_group(title) == group


def test_find_references():
    refs = eda.find_references("theo quy định tại điểm a khoản 2 Điều 6 của Nghị định này và Điều 260 của Bộ luật Hình sự")
    assert refs == [{"diem": "a", "khoan": "2", "dieu": "6", "loai": "noi_bo"},
                    {"diem": None, "khoan": None, "dieu": "260", "loai": "ngoai"}]
    assert eda.find_references("khoản 3 Điều 10") == [
        {"diem": None, "khoan": "3", "dieu": "10", "loai": "noi_bo"}]


def test_count_words():
    assert eda.count_words("Người điều khiển xe") == 4


@pytest.mark.skipif(not config.TOKENIZERS["bge_m3"].exists(), reason="chưa tải tokenizer bge-m3")
def test_count_tokens():
    n = eda.count_tokens(["Người điều khiển xe mô tô", ""], config.TOKENIZERS["bge_m3"])
    assert n[0] > 0 and n[1] == 0


def test_near_duplicates_only_across_groups():
    texts = ["người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông",
             "người điều khiển xe mô tô phải đội mũ bảo hiểm khi tham gia giao thông.",
             "quy định về lệ phí đăng ký xe và cấp biển số"]
    pairs = eda.near_duplicates(texts, ["a", "b", "c"], threshold=0.9, block=1)
    assert [(i, j) for i, j, _ in pairs] == [(0, 1)]
    assert eda.near_duplicates(texts, ["a", "a", "c"], threshold=0.9) == []


def test_near_duplicates_empty_and_invalid_input():
    assert eda.near_duplicates([], []) == []
    assert eda.near_duplicates(["", ""], ["a", "b"]) == []
    assert eda.near_duplicates(["a", "b"], ["a", "b"]) == []
    with pytest.raises(ValueError):
        eda.near_duplicates(["one"], [])
    with pytest.raises(ValueError):
        eda.near_duplicates(["one"], ["a"], block=0)


def test_allocate_largest_remainder_with_floor():
    assert eda.allocate({"a": 1, "b": 1, "c": 2}, 10, floor=1) == {"a": 3, "b": 3, "c": 4}
    with pytest.raises(ValueError):
        eda.allocate({"a": 1, "b": 1}, 3, floor=2)


def test_allocate_boundary_inputs():
    assert eda.allocate({}, 0) == {}
    assert eda.allocate({"b": 0, "a": 0}, 3) == {"a": 2, "b": 1}
    with pytest.raises(ValueError):
        eda.allocate({}, 1)
    with pytest.raises(ValueError):
        eda.allocate({"a": -1}, 1)
    with pytest.raises(ValueError):
        eda.allocate({"a": float("nan")}, 1)
    with pytest.raises(ValueError):
        eda.allocate({"a": 1}, -1)


def test_allocate_large_finite_weights_preserves_total_and_proportions():
    ordinary = eda.allocate({"a": 2.0, "b": 1.0, "c": 1.0}, 10)
    huge = eda.allocate({"a": 1e308, "b": 5e307, "c": 5e307}, 10)
    assert huge == ordinary == {"a": 5, "b": 3, "c": 2}
    assert sum(eda.allocate({"a": 1e308, "b": 1e308}, 10).values()) == 10


def test_eval_matrix_totals():
    rows = eda.eval_matrix({"Xử phạt": 400, "Lệ phí": 10, "GPLX": 100},
                           {"Xử phạt": ["nd_168_2024"], "Lệ phí": ["nd_10_2022"],
                            "GPLX": ["tt_108_2026_bca"]})
    assert sum(r["so_cau"] for r in rows) == 150
    per = {}
    for r in rows:
        per[r["chu_de"]] = per.get(r["chu_de"], 0) + r["so_cau"]
    assert min(per.values()) >= 5
    assert any(r["chu_de"] == "Xử phạt" and r["loai_cau"] == "mức phạt" for r in rows)
    assert all(r["so_cau"] > 0 for r in rows)
