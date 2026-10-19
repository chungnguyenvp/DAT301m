import pytest

from lawproc import evalset
from rag import answer_score as s


def _item(**kw):
    item = {"nhom_cau": "thuong", "dap_an": "", "van_ban": "nd_168_2024", "dieu": "7", "khoan": "7"}
    item.update(kw)
    return item


@pytest.fixture(scope="module")
def items():
    return {f"{x['nhom_cau']}/{x['key']}": x for x in evalset.load_eval()}


@pytest.fixture(scope="module")
def corpus(items):
    return s.corpus_numbers({x["van_ban"] for x in items.values() if x.get("van_ban")})


def test_so_lieu_reads_markdown_and_vnd():
    item = _item(so_lieu=[[4000000.0, "đồng"], [6000000.0, "đồng"], [4.0, "điểm"]])
    got = s.so_lieu(item, "Phạt **4.000.000đ** đến 6 triệu VNĐ, trừ **04 điểm**.")
    assert got == {"n": 3, "dung": 3, "ty_le": 1.0, "du": True}


def test_so_lieu_keeps_working_days_apart_from_days():
    item = _item(so_lieu=[[5.0, "ngày làm việc"]])
    assert s.so_lieu(item, "Trong 05 ngày làm việc.")["du"]
    assert not s.so_lieu(item, "Trong 05 ngày.")["du"]


def test_so_lieu_none_without_numbers():
    assert s.so_lieu(_item(so_lieu=[]), "bất kỳ") is None


def test_muc_phat_capital_tu_and_markdown():
    item = _item(muc_phat_min=4000000, muc_phat_max=6000000)
    assert s.muc_phat(item, "*   **Phạt tiền:** Từ **4.000.000 đồng đến 6.000.000 đồng**.")["dung_khung"]
    assert not s.muc_phat(item, "phạt từ 400.000 đồng đến 600.000 đồng")["co_ca_hai_muc"]


def test_diem_tru_co_and_khong_tru():
    co = _item(trang_thai_diem_tru="co", diem_tru=4)
    assert s.diem_tru(co, "bị trừ điểm giấy phép lái xe 04 điểm")
    assert s.diem_tru(co, "Trừ điểm giấy phép lái xe: **4 điểm**")
    assert not s.diem_tru(co, "trừ 2 điểm")
    khong = _item(trang_thai_diem_tru="khong_tru", diem_tru=None)
    assert s.diem_tru(khong, "Hành vi này không bị trừ điểm giấy phép lái xe.")
    assert not s.diem_tru(khong, "và bị trừ 06 điểm")
    assert s.diem_tru(_item(trang_thai_diem_tru="khong_ap_dung"), "x") is None


def test_tuoc_gplx():
    item = _item(tuoc_gplx_thang=[22, 24])
    assert s.tuoc_gplx(item, "tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng")
    assert not s.tuoc_gplx(item, "tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng")


def test_trich_dan_levels():
    item = _item()
    full = s.trich_dan(item, "(điểm c khoản 7 Điều 7 Nghị định 168/2024/NĐ-CP)")
    assert full == {"van_ban": True, "dieu": True, "khoan": True}
    reversed_order = s.trich_dan(item, "theo Điều 7, Khoản 7 Nghị định 168/2024/NĐ-CP")
    assert reversed_order["khoan"]
    wrong_doc = s.trich_dan(item, "khoản 7 Điều 7 Nghị định 100/2019/NĐ-CP")
    assert wrong_doc == {"van_ban": False, "dieu": False, "khoan": False}
    assert not s.trich_dan(item, "khoản 7 Điều 70 Nghị định 168/2024/NĐ-CP")["dieu"]


def test_doc_aliases_cover_laws_and_qcvn():
    assert "Luật Đường bộ" in s.doc_aliases("luat_35_2024")
    assert "35/2024" in s.doc_aliases("luat_35_2024")
    assert "QCVN 41:2024" in s.doc_aliases("qcvn_41_2024")


def test_van_ban_ngoai_kho(corpus):
    text = "theo Nghị định 100/2019/NĐ-CP và Nghị định 168/2024/NĐ-CP, QCVN 41:2019/BGTVT"
    assert s.van_ban_ngoai_kho(text, corpus) == ["100/2019", "QCVN 41:2019"]
    assert s.van_ban_ngoai_kho("Luật Giao thông đường bộ 2008 quy định", corpus) == ["Luật Giao thông đường bộ (2008)"]
    assert s.van_ban_ngoai_kho("hỗ trợ tra cứu pháp luật giao thông đường bộ", corpus) == []


def test_tu_choi_only_at_head():
    assert s.tu_choi("Câu hỏi này nằm ngoài phạm vi của tôi.")
    long_answer = "Phạt tiền từ 4.000.000 đồng. " * 20 + "Các đoạn luật không có quy định về xe đạp."
    assert not s.tu_choi(long_answer)


def test_tu_choi_dung_luat_cu():
    item = _item(nhom_cau="ngoai_pham_vi", kieu_ngoai="luat_cu")
    assert s.tu_choi_dung(item, "Thông tư 58/2020/TT-BCA " + "x " * 200 + "đã hết hiệu lực.")
    assert not s.tu_choi_dung(_item(nhom_cau="ngoai_pham_vi", kieu_ngoai="duong_sat"), "Phạt 500.000 đồng.")


def test_rq3_new_vs_old(items):
    sd07 = items["sua_doi/sd07"]
    new = s.rq3(sd07, "vượt phía sau trên 10% chiều dài, phạt từ 800.000 đồng đến 1.000.000 đồng")
    old = s.rq3(sd07, "vượt phía sau trên 1,1 lần chiều dài, phạt từ 800.000 đồng đến 1.000.000 đồng")
    assert new["theo_ban_moi"] and not new["trich_ban_cu"]
    assert old["trich_ban_cu"] and not old["theo_ban_moi"]


def test_lap_vong():
    assert s.lap_vong("cấm đi vào đường dành cho xe đạp, xe máy, xe thô sơ, " * 5)
    assert not s.lap_vong("Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng và trừ 04 điểm.")


def test_rouge_l():
    assert s.rouge_l("phạt 4 triệu đồng", "phạt 4 triệu đồng") == pytest.approx(1.0)
    assert s.rouge_l("", "abc") == 0.0
    assert 0 < s.rouge_l("phạt tiền 4 triệu", "phạt 4 triệu đồng") < 1
