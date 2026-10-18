"""Đợt 1g G5: Xử phạt, NĐ 168/2024 Điều 11, 15, 16, 17, 19, 22, 28, 36 và NĐ 336/2025 Điều 5, 10, 11.
Ghi data/train/drafts/xu_phat_07.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
ND336 = "Nghị định 336/2025/NĐ-CP"
NEW = "2026-08-15"
D336 = "2026-03-01"
S = []
START = 369


def v(s, d="2025-01-01"):
    return f"nd_168_2024:{s}@{d}"


def w(s):
    return f"nd_336_2025:{s}@{D336}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, dieu, k, diem=None, nd=ND):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều {dieu} {nd}"
    return f"phạt tiền từ {lo} đồng đến {hi} đồng ({where})"


def org(lo, hi, lo2, hi2, dieu, k, diem=None):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều {dieu} {ND336}"
    return (f"phạt tiền từ {lo} đồng đến {hi} đồng đối với cá nhân, từ {lo2} đồng đến {hi2} đồng đối với tổ chức "
            f"({where})")


# ===== NĐ 168 Điều 11: dẫn dắt vật nuôi, xe vật nuôi kéo
d11 = lambda s: v(f"d11:{s}")  # noqa: E731
add("muc_phat", "Người dắt chó đi dạo không dọn chất thải của vật nuôi thải ra đường, vỉa hè thì bị phạt bao nhiêu?",
    "Người dẫn dắt vật nuôi không đủ dụng cụ đựng chất thải của vật nuôi hoặc không dọn sạch chất thải của vật nuôi thải "
    "ra đường, vỉa hè bị " + fine("150.000", "250.000", 11, 1, "c") + ".", d11("k1:c"), d11("k1"))
add("muc_phat", "Để vật nuôi đi trên đường bộ không bảo đảm an toàn cho người và phương tiện thì bị phạt bao nhiêu?",
    "Để vật nuôi đi trên đường bộ không bảo đảm an toàn cho người, phương tiện đang tham gia giao thông bị "
    + fine("150.000", "250.000", 11, 1, "d") + ".", d11("k1:d"), d11("k1"))
add("tinh_huong", "Tôi vừa đi xe máy vừa dắt chó chạy theo bên cạnh. Như vậy có bị phạt không?",
    "Có. Dẫn dắt vật nuôi chạy theo khi đang điều khiển hoặc ngồi trên phương tiện giao thông đường bộ bị "
    + fine("400.000", "600.000", 11, 2, "b") + ".", d11("k2:b"), d11("k2"))
add("muc_phat", "Dắt trâu bò đi vào phần đường của xe cơ giới hoặc đi vào đường cấm thì bị phạt bao nhiêu?",
    "Điều khiển, dẫn dắt vật nuôi đi không đúng phần đường quy định, đi vào đường cấm, khu vực cấm, đi vào phần đường "
    "của xe cơ giới bị " + fine("400.000", "600.000", 11, 2, "c") + ".", d11("k2:c"), d11("k2"))
add("muc_phat", "Dẫn dắt vật nuôi hoặc điều khiển xe bò kéo đi vào đường cao tốc thì bị phạt bao nhiêu?",
    "Người điều khiển, dẫn dắt vật nuôi, điều khiển xe vật nuôi kéo đi vào đường cao tốc bị "
    + fine("1.000.000", "2.000.000", 11, 3) + ".", d11("k3"))
add("muc_phat", "Để xe ngựa kéo đi mà không có người điều khiển thì bị phạt bao nhiêu?",
    "Để vật nuôi kéo xe mà không có người điều khiển bị " + fine("150.000", "250.000", 11, 1, "e") + ".",
    d11("k1:e"), d11("k1"))

# ===== NĐ 168 Điều 15: điều kiện xe thô sơ
add("doi_thuong", "xe đạp không có chuông với đèn thì có bị phạt ko",
    "Có thể bị phạt. Điều khiển xe thô sơ không có bộ phận phát âm thanh cảnh báo (còi, chuông); không có đèn chiếu sáng "
    "hoặc tấm phản quang phía trước; không có đèn tín hiệu hoặc tấm phản quang phía sau xe (đối với loại xe phải có các "
    "bộ phận này) bị " + fine("100.000", "200.000", 15, 1) + ".", v("d15:k1"))
add("muc_phat", "Điều khiển xe thô sơ không có phanh (bộ phận hãm) hoặc phanh không có hiệu lực thì bị phạt bao nhiêu?",
    "Điều khiển xe không có hệ thống (bộ phận) hãm hoặc có nhưng không có hiệu lực (đối với loại xe phải có) bị "
    + fine("300.000", "400.000", 15, 2) + ".", v("d15:k2"))

# ===== NĐ 168 Điều 16: điều kiện xe máy chuyên dùng
d16 = lambda s: v(f"d16:{s}")  # noqa: E731
add("muc_phat", "Điều khiển xe máy chuyên dùng không gắn biển số thì bị phạt bao nhiêu?",
    "Điều khiển xe máy chuyên dùng không gắn biển số (đối với loại xe phải gắn biển số) bị "
    + fine("800.000", "1.000.000", 16, 1, "a") + ".", d16("k1:a"), d16("k1"))
add("muc_phat", "Xe máy chuyên dùng có phanh hoặc hệ thống lái không bảo đảm tiêu chuẩn kỹ thuật thì bị phạt bao nhiêu?",
    "Điều khiển xe không có hệ thống hãm hoặc có nhưng không bảo đảm tiêu chuẩn kỹ thuật, hoặc có hệ thống chuyển hướng "
    "không bảo đảm tiêu chuẩn kỹ thuật bị " + fine("800.000", "1.000.000", 16, 1, "b") + "; người vi phạm còn buộc lắp "
    "đầy đủ hoặc thay thế thiết bị đủ tiêu chuẩn, khôi phục tính năng kỹ thuật của thiết bị (điểm a khoản 5 Điều 16).",
    d16("k1:b"), d16("k1"), d16("k5:a"))
add("muc_phat", "Xe máy chuyên dùng có tem kiểm định hết hạn dưới 01 tháng thì người điều khiển bị phạt bao nhiêu?",
    "Điều khiển xe máy chuyên dùng có giấy chứng nhận hoặc tem kiểm định an toàn kỹ thuật và bảo vệ môi trường đã hết "
    "hiệu lực dưới 01 tháng bị " + fine("800.000", "1.000.000", 16, 1, "đ") + ".", d16("k1:đ"), d16("k1"))
add("muc_phat", "Xe máy chuyên dùng không có tem kiểm định hoặc tem hết hạn từ 01 tháng trở lên thì bị phạt bao nhiêu?",
    "Điều khiển xe không có giấy chứng nhận hoặc tem kiểm định (đối với loại xe phải kiểm định, trừ xe đăng ký tạm "
    "thời) hoặc có nhưng đã hết hiệu lực từ 01 tháng trở lên bị " + fine("1.000.000", "2.000.000", 16, 2, "b") + ".",
    d16("k2:b"), d16("k2"))
add("muc_phat", "Điều khiển xe máy chuyên dùng hoạt động không đúng phạm vi quy định thì bị phạt bao nhiêu?",
    "Điều khiển xe máy chuyên dùng hoạt động không đúng phạm vi quy định bị " + fine("1.000.000", "2.000.000", 16, 2, "a")
    + ".", d16("k2:a"), d16("k2"))
add("muc_phat", "Xe máy chuyên dùng gắn biển số không do cơ quan có thẩm quyền cấp thì người điều khiển bị xử phạt thế nào?",
    "Điều khiển xe gắn biển số không đúng với chứng nhận đăng ký xe hoặc không do cơ quan có thẩm quyền cấp bị "
    + fine("1.000.000", "2.000.000", 16, 2, "d") + " và bị tịch thu biển số xe (điểm a khoản 4 Điều 16).",
    d16("k2:d"), d16("k2"), d16("k4:a"))
add("muc_phat", "Điều khiển xe máy chuyên dùng sản xuất, lắp ráp hoặc cải tạo trái quy định tham gia giao thông thì bị xử "
    "lý thế nào?",
    "Hành vi này bị tịch thu phương tiện (khoản 3 Điều 16 " + ND + ").", d16("k3"))

# ===== NĐ 168 Điều 17: bảo vệ môi trường
d17 = lambda s, d="2025-01-01": v(f"d17:{s}", d)  # noqa: E731
add("muc_phat", "Lái xe ô tô không đáp ứng yêu cầu về vệ sinh lưu thông trong đô thị thì bị phạt bao nhiêu?",
    "Điều khiển xe không đáp ứng yêu cầu về vệ sinh lưu thông trong đô thị bị " + fine("500.000", "1.000.000", 17, 1)
    + ".", d17("k1"))
add("doi_thuong", "xe tải chở cát ko che bạt làm rơi vãi ra đường thì bị phạt bao nhiêu",
    "Theo điểm a khoản 2 Điều 17 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), người điều khiển xe ô tô chở vật "
    "liệu xây dựng, đất đá, phế thải, hàng rời mà không che đậy, làm rơi vãi xuống đường, bị phạt tiền từ 2.000.000 "
    "đồng đến 4.000.000 đồng.", d17("k2:a", NEW), d17("k2"))
add("muc_phat", "Xe ô tô lôi kéo bùn đất, cát ra đường bộ gây mất an toàn giao thông thì tài xế bị phạt bao nhiêu?",
    "Lôi kéo bùn, đất, cát, nguyên liệu, vật liệu hoặc chất phế thải khác ra đường bộ gây mất an toàn giao thông bị "
    + fine("2.000.000", "4.000.000", 17, 2, "b") + ".", d17("k2:b"), d17("k2"))
add("muc_phat", "Lái ô tô đổ trái phép đất, đá, phế thải trong phạm vi đất dành cho đường bộ ở đoạn ngoài đô thị bị phạt "
    "bao nhiêu?",
    "Người điều khiển xe đổ trái phép rác, đất, cát, đá, vật liệu, chất phế thải trong phạm vi đất dành cho đường bộ ở "
    "đoạn đường ngoài đô thị bị " + fine("4.000.000", "6.000.000", 17, 3) + "; khi điều khiển xe ô tô còn bị trừ điểm "
    "giấy phép lái xe 02 điểm (khoản 5 Điều 17).", d17("k3"), d17("k5"))
add("tinh_huong", "Tôi lái xe tải đổ trộm xà bần ra đường phố vào ban đêm. Tôi có thể bị phạt bao nhiêu?",
    "Người điều khiển xe đổ trái phép rác, đất, cát, đá, vật liệu, chất phế thải ra đường phố bị "
    + fine("10.000.000", "15.000.000", 17, 4) + "; vì điều khiển xe ô tô nên còn bị trừ điểm giấy phép lái xe 02 điểm "
    "(khoản 5 Điều 17).", d17("k4"), d17("k5"))

# ===== NĐ 168 Điều 19: điều kiện người điều khiển xe máy chuyên dùng
add("muc_phat", "Người điều khiển xe máy chuyên dùng không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự bị phạt bao nhiêu?",
    "Người điều khiển xe máy chuyên dùng không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự theo quy định bị "
    + fine("400.000", "600.000", 19, 1) + ".", v("d19:k1"))
add("tinh_huong", "Tôi lái máy xúc ra đường nhưng chưa có bằng hoặc chứng chỉ điều khiển xe máy chuyên dùng. Tôi bị phạt "
    "bao nhiêu?",
    "Máy xúc là xe máy thi công, thuộc nhóm xe máy chuyên dùng (điểm a khoản 3 Điều 34 Luật Trật tự, an toàn giao thông "
    "đường bộ). Người điều khiển xe máy chuyên dùng không có bằng (hoặc chứng chỉ) điều khiển xe máy chuyên dùng, không "
    "có giấy phép lái xe hoặc không có chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ bị "
    + fine("4.000.000", "6.000.000", 19, 2) + ".", v("d19:k2"), "luat_36_2024:d34:k3@2025-01-01")

# ===== NĐ 168 Điều 22: hàng siêu trường, siêu trọng
d22 = lambda s: v(f"d22:{s}")  # noqa: E731
add("muc_phat", "Chở hàng siêu trường, siêu trọng không có báo hiệu kích thước của hàng thì tài xế bị phạt bao nhiêu?",
    "Chở hàng siêu trường, siêu trọng không có báo hiệu kích thước của hàng theo quy định bị "
    + fine("2.000.000", "3.000.000", 22, 1, "a") + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 6 Điều 22).",
    d22("k1:a"), d22("k1"), d22("k6:a"))
add("muc_phat", "Chở hàng siêu trường có giấy phép lưu hành nhưng kích thước bao ngoài của xe vượt quá quy định trong giấy "
    "phép thì bị phạt bao nhiêu?",
    "Chở hàng siêu trường, siêu trọng có giấy phép lưu hành còn giá trị nhưng kích thước bao ngoài của xe (sau khi xếp "
    "hàng) vượt quá quy định trong giấy phép bị " + fine("8.000.000", "10.000.000", 22, 2) + " và bị trừ điểm giấy phép "
    "lái xe 04 điểm (điểm b khoản 6 Điều 22).", d22("k2"), d22("k6:b"))
add("muc_phat", "Chở hàng siêu trường, siêu trọng không có giấy phép lưu hành thì tài xế bị xử phạt thế nào?",
    "Chở hàng siêu trường, siêu trọng không có giấy phép lưu hành, hoặc giấy phép đã hết giá trị, hoặc sử dụng giấy phép "
    "không do cơ quan có thẩm quyền cấp bị " + fine("13.000.000", "15.000.000", 22, 3, "a") + " và bị trừ điểm giấy "
    "phép lái xe 04 điểm (điểm b khoản 6 Điều 22); giấy phép hết giá trị hoặc không do cơ quan có thẩm quyền cấp bị thu "
    "hồi (khoản 5 Điều 22).", d22("k3:a"), d22("k3"), d22("k6:b"), d22("k5"))
add("muc_phat", "Chở hàng siêu trọng có giấy phép lưu hành nhưng đi không đúng tuyến đường ghi trong giấy phép thì bị phạt "
    "bao nhiêu?",
    "Người điều khiển xe bị " + fine("13.000.000", "15.000.000", 22, 3, "c") + " và bị trừ điểm giấy phép lái xe 04 điểm "
    "(điểm b khoản 6 Điều 22). Nếu gây hư hại cầu, đường còn buộc khôi phục lại tình trạng ban đầu (khoản 4 Điều 22).",
    d22("k3:c"), d22("k3"), d22("k6:b"), d22("k4"))
add("muc_phat", "Chở hàng siêu trường, siêu trọng không đúng loại hàng ghi trong giấy phép lưu hành thì bị phạt bao nhiêu?",
    "Chở hàng siêu trường, siêu trọng có giấy phép lưu hành còn giá trị nhưng chở không đúng loại hàng quy định trong "
    "giấy phép bị " + fine("13.000.000", "15.000.000", 22, 3, "d") + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b "
    "khoản 6 Điều 22).", d22("k3:d"), d22("k3"), d22("k6:b"))

# ===== NĐ 168 Điều 28: xe bốn bánh có gắn động cơ
d28 = lambda s: v(f"d28:{s}")  # noqa: E731
add("muc_phat", "Lái xe điện bốn bánh chở khách du lịch chở quá số người quy định thì bị phạt bao nhiêu?",
    "Người điều khiển xe chở người bốn bánh có gắn động cơ chở quá số người quy định được phép chở của phương tiện bị "
    + fine("1.000.000", "2.000.000", 28, 1) + ".", d28("k1"))
add("muc_phat", "Xe chở người bốn bánh có gắn động cơ kinh doanh vận tải không gắn phù hiệu thì người lái bị phạt bao nhiêu?",
    "Điều khiển xe chở người, xe chở hàng bốn bánh có gắn động cơ kinh doanh vận tải không có hoặc không gắn phù hiệu, "
    "hoặc phù hiệu hết giá trị, hoặc không do cơ quan có thẩm quyền cấp, bị " + fine("2.000.000", "3.000.000", 28, 2)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 4 Điều 28).", d28("k2"), d28("k4:a"))
add("tinh_huong", "Tôi lái xe điện bốn bánh chở khách đi ra ngoài tuyến đường được phép hoạt động. Tôi bị phạt bao nhiêu?",
    "Điều khiển xe chở người bốn bánh có gắn động cơ hoạt động không đúng tuyến đường, lịch trình, thời gian hoặc phạm "
    "vi hoạt động được phép bị " + fine("8.000.000", "12.000.000", 28, 3) + " và bị trừ điểm giấy phép lái xe 06 điểm "
    "(điểm b khoản 4 Điều 28).", d28("k3"), d28("k4:b"))

# ===== NĐ 168 Điều 36: xe máy, xe thô sơ chở hàng
d36 = lambda s: v(f"d36:{s}")  # noqa: E731
add("muc_phat", "Đi xe máy chở hàng sắp xếp, chằng buộc không bảo đảm an toàn thì bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô, xe gắn máy, xe thô sơ vận chuyển hàng hóa mà sắp xếp, chằng buộc không bảo đảm an toàn "
    "hoặc gây nguy hiểm cho người, phương tiện tham gia giao thông bị " + fine("300.000", "400.000", 36, 1, "a") + ".",
    d36("k1:a"), d36("k1"))
add("doi_thuong", "chở hàng trên xe máy che mất biển số thì có bị phạt ko",
    "Có. Vận chuyển hàng hóa trên xe gây cản trở tầm nhìn của người lái hoặc che khuất đèn, biển số xe, hoặc để rơi hàng "
    "hóa xuống đường bị " + fine("300.000", "400.000", 36, 1, "b") + ".", d36("k1:b"), d36("k1"))
add("muc_phat", "Xe máy chở hàng vượt quá khối lượng cho phép của xe thì bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô, xe gắn máy, xe thô sơ chở hành lý, hàng hóa vượt quá khối lượng cho phép của xe bị "
    + fine("400.000", "600.000", 36, 2, "a") + ".", d36("k2:a"), d36("k2"))
add("tinh_huong", "Tôi chở hàng cồng kềnh trên xe máy vượt quá khổ giới hạn cho phép của xe. Tôi bị phạt bao nhiêu?",
    "Chở hành lý, hàng hóa vượt quá khổ giới hạn cho phép của xe bị " + fine("400.000", "600.000", 36, 2, "b") + ".",
    d36("k2:b"), d36("k2"))
add("muc_phat", "Đi xe ba gác chở vật liệu xây dựng để rơi vãi xuống đường thì bị phạt bao nhiêu?",
    "Vận chuyển hàng rời, vật liệu xây dựng, phế thải để rơi vãi xuống đường hoặc gây ra tiếng ồn, bụi bẩn khi điều "
    "khiển xe mô tô, xe gắn máy, xe thô sơ bị " + fine("400.000", "600.000", 36, 2, "c") + ".", d36("k2:c"), d36("k2"))
add("muc_phat", "Xe máy chở hàng dài vượt ra phía sau mà ban ngày không có báo hiệu màu đỏ ở cuối hàng thì bị phạt bao nhiêu?",
    "Vận chuyển hàng hóa vượt phía trước, phía sau xe mà không có báo hiệu màu đỏ tại điểm đầu và điểm cuối của hàng hóa "
    "khi xe hoạt động ban ngày (hoặc không có đèn, báo hiệu khi hoạt động ban đêm, trời tối) bị "
    + fine("400.000", "600.000", 36, 2, "d") + ".", d36("k2:d"), d36("k2"))

# ===== NĐ 336/2025 Điều 5: sử dụng đất dành cho kết cấu hạ tầng đường bộ
d5 = lambda s: w(f"d5:{s}")  # noqa: E731
H = "theo " + ND336 + " (có hiệu lực từ ngày 01/3/2026)"
add("muc_phat", "Trồng cây trong hành lang an toàn đường bộ làm che khuất tầm nhìn hoặc che biển báo thì bị phạt bao nhiêu?",
    "Hành vi trồng cây trong phạm vi hành lang an toàn đường bộ làm che khuất tầm nhìn của người điều khiển phương tiện "
    "hoặc che lấp báo hiệu đường bộ bị " + org("500.000", "1.000.000", "1.000.000", "2.000.000", 5, 1) + "; người vi "
    "phạm buộc di dời cây trồng che khuất (điểm a khoản 7 Điều 5).", d5("k1"), d5("k7:a"))
add("muc_phat", "Treo băng rôn trái phép trong phạm vi đất của đường bộ gây ảnh hưởng an toàn giao thông thì bị phạt bao nhiêu?",
    "Treo băng rôn trái phép trong phạm vi đất của đường bộ gây ảnh hưởng đến an toàn giao thông bị "
    + org("1.000.000", "2.000.000", "2.000.000", "4.000.000", 5, 2, "b") + "; người vi phạm buộc thu dọn băng rôn "
    "(điểm c khoản 7 Điều 5).", d5("k2:b"), d5("k2"), d5("k7:c"))
add("tinh_huong", "Nhà tôi tổ chức đám cưới, dựng cổng chào lấn ra đất của đường bộ gây ảnh hưởng giao thông. Có bị phạt không?",
    "Có. " + H[0].upper() + H[1:] + ", dựng cổng chào trái phép trong phạm vi đất dành cho kết cấu hạ tầng đường bộ gây "
    "ảnh hưởng đến an toàn giao thông bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng đối với cá nhân, từ 2.000.000 "
    "đồng đến 4.000.000 đồng đối với tổ chức (điểm a khoản 2 Điều 5); người vi phạm buộc phá dỡ và khôi phục lại tình "
    "trạng ban đầu (điểm b khoản 7 Điều 5).", d5("k2:a"), d5("k2"), d5("k7:b"))
add("muc_phat", "Đặt biển quảng cáo trên đất của đường bộ ở đoạn ngoài đô thị thì bị phạt bao nhiêu?",
    "Đặt, treo biển hiệu, bảng quảng cáo trên đất của đường bộ ở đoạn đường ngoài đô thị (trừ trường hợp đặt tại lòng "
    "đường và hành vi xây dựng biển quảng cáo trong hành lang an toàn mà không có văn bản chấp thuận) bị "
    + org("1.000.000", "2.000.000", "2.000.000", "4.000.000", 5, 2, "c") + "; người vi phạm buộc thu dọn biển hiệu, "
    "bảng quảng cáo (điểm c khoản 7 Điều 5).", d5("k2:c"), d5("k2"), d5("k7:c"))
add("doi_thuong", "vứt rác ra đường không đúng chỗ quy định thì bị phạt bao nhiêu",
    H[0].upper() + H[1:] + ", đổ rác thải ra đường bộ không đúng nơi quy định bị "
    + org("1.000.000", "2.000.000", "2.000.000", "4.000.000", 5, 2, "d") + "; người vi phạm buộc thu dọn rác thải "
    "(điểm d khoản 7 Điều 5).", d5("k2:d"), d5("k2"), d5("k7:d"))
add("muc_phat", "Dựng lều quán trái phép trong phạm vi đất dành cho kết cấu hạ tầng đường bộ thì bị phạt bao nhiêu?",
    "Dựng rạp, lều quán, cổng ra vào, tường rào, công trình khác trái phép trong phạm vi đất dành cho kết cấu hạ tầng "
    "đường bộ bị " + org("3.000.000", "5.000.000", "6.000.000", "10.000.000", 5, 3) + "; người vi phạm buộc phá dỡ công "
    "trình và khôi phục lại tình trạng ban đầu (điểm đ khoản 7 Điều 5).", d5("k3"), d5("k7:đ"))
add("muc_phat", "Đổ vật liệu, chất phế thải trái phép trong hành lang an toàn đường bộ thì bị phạt bao nhiêu?",
    "Đổ, để trái phép vật liệu, chất phế thải trong hành lang an toàn đường bộ bị "
    + org("4.000.000", "6.000.000", "8.000.000", "10.000.000", 5, 4, "a") + "; người vi phạm buộc thu dọn chất phế "
    "thải, vật liệu (điểm d khoản 7 Điều 5).", d5("k4:a"), d5("k4"), d5("k7:d"))
add("muc_phat", "Tự ý đào, đắp, san lấp mặt bằng trong phạm vi đất dành cho kết cấu hạ tầng đường bộ thì bị phạt bao nhiêu?",
    "Hành vi này bị " + org("4.000.000", "6.000.000", "8.000.000", "10.000.000", 5, 4, "b") + "; người vi phạm buộc "
    "khôi phục lại tình trạng ban đầu (điểm e khoản 7 Điều 5).", d5("k4:b"), d5("k4"), d5("k7:e"))
add("tinh_huong", "Cửa hàng tôi treo biển quảng cáo lên cột biển báo giao thông trước cửa. Có bị phạt không?",
    "Có. Tự ý gắn, treo, lắp đặt vào công trình báo hiệu đường bộ nội dung không liên quan tới ý nghĩa, mục đích của "
    "báo hiệu bị " + org("4.000.000", "6.000.000", "8.000.000", "10.000.000", 5, 4, "c") + "; người vi phạm buộc tháo "
    "dỡ vật đã gắn, treo và khôi phục lại tình trạng ban đầu (điểm g khoản 7 Điều 5).",
    d5("k4:c"), d5("k4"), d5("k7:g"))
add("muc_phat", "Dựng lều quán trái phép dưới gầm cầu vượt trong đô thị thì bị phạt bao nhiêu?",
    "Dựng rạp, lều quán, công trình khác trái phép trong khu vực đô thị tại hầm đường bộ, cầu vượt, hầm cho người đi bộ, "
    "gầm cầu vượt bị " + org("4.000.000", "6.000.000", "8.000.000", "10.000.000", 5, 4, "d") + "; người vi phạm buộc phá "
    "dỡ và khôi phục lại tình trạng ban đầu (điểm đ khoản 7 Điều 5).", d5("k4:d"), d5("k4"), d5("k7:đ"))
add("muc_phat", "Chiếm dụng đất hành lang an toàn đường bộ để xây nhà ở thì bị phạt bao nhiêu?",
    "Chiếm dụng đất của đường bộ hoặc đất hành lang an toàn đường bộ để xây dựng nhà ở bị "
    + org("15.000.000", "20.000.000", "30.000.000", "40.000.000", 5, 6, "a") + "; người vi phạm buộc phá dỡ công trình "
    "và khôi phục lại tình trạng ban đầu (điểm đ khoản 7 Điều 5).", d5("k6:a"), d5("k6"), d5("k7:đ"))
add("muc_phat", "Tự ý mở đường đấu nối trái phép vào đường chính thì bị phạt bao nhiêu?",
    "Đấu nối trái phép vào đường chính, đường nhánh bị "
    + org("15.000.000", "20.000.000", "30.000.000", "40.000.000", 5, 6, "b") + "; người vi phạm buộc phá dỡ công trình "
    "và khôi phục lại tình trạng ban đầu (điểm đ khoản 7 Điều 5).", d5("k6:b"), d5("k6"), d5("k7:đ"))
add("muc_phat", "Xây dựng biển quảng cáo trong hành lang an toàn đường cao tốc thì bị phạt bao nhiêu?",
    "Xây dựng, lắp đặt biển quảng cáo trong phạm vi hành lang an toàn đường cao tốc bị "
    + org("15.000.000", "20.000.000", "30.000.000", "40.000.000", 5, 6, "d") + "; người vi phạm buộc phá dỡ và khôi "
    "phục lại tình trạng ban đầu (điểm đ khoản 7 Điều 5).", d5("k6:d"), d5("k6"), d5("k7:đ"))

# ===== NĐ 336/2025 Điều 10: thu phí, thanh toán điện tử
d10 = lambda s: w(f"d10:{s}")  # noqa: E731
add("tinh_huong", "Tôi bóc thẻ thu phí không dừng (thẻ đầu cuối) từ xe này dán sang xe khác. Như vậy có bị phạt không?",
    "Có. " + H[0].upper() + H[1:] + ", tự ý chuyển thẻ đầu cuối từ phương tiện này sang phương tiện khác bị "
    "phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng đối với cá nhân, từ 6.000.000 đồng đến 10.000.000 đồng đối với tổ "
    "chức (điểm a khoản 1 Điều 10).", d10("k1:a"), d10("k1"))
add("muc_phat", "Làm giả, xóa dữ liệu hoặc can thiệp nội dung thẻ đầu cuối thu phí không dừng thì bị phạt bao nhiêu?",
    "Phá hủy, làm giả, xóa dữ liệu hoặc can thiệp nội dung thẻ đầu cuối bị "
    + org("3.000.000", "5.000.000", "6.000.000", "10.000.000", 10, 1, "b") + ".", d10("k1:b"), d10("k1"))
add("muc_phat", "Mở tài khoản giao thông nặc danh hoặc mạo danh người khác thì bị phạt bao nhiêu?",
    "Mở hoặc duy trì tài khoản giao thông nặc danh, mạo danh bị "
    + org("3.000.000", "5.000.000", "6.000.000", "10.000.000", 10, 1, "c") + ".", d10("k1:c"), d10("k1"))
add("muc_phat", "Trạm thu phí nhận tiền mặt mà không giao vé cho người đi đường thì đơn vị vận hành bị phạt bao nhiêu?",
    "Tổ chức nhận tiền mặt của người sử dụng phương tiện mà không giao vé, hoặc giao vé không đúng chủng loại phương "
    "tiện, bị phạt tiền từ 10.000.000 đồng đến 20.000.000 đồng (điểm c khoản 2 Điều 10 " + ND336 + ") và buộc nộp lại "
    "số lợi bất hợp pháp có được (điểm a khoản 7 Điều 10).", d10("k2:c"), d10("k2"), d10("k7:a"))
add("tinh_huong", "Xe ô tô xếp hàng chờ trước trạm thu phí dài từ 750 m trở lên trên một làn do trạm vận hành sai quy trình. "
    "Đơn vị vận hành trạm bị phạt bao nhiêu?",
    "Tổ chức không thực hiện đúng quy trình quản lý, vận hành trạm thu phí để số lượng xe ô tô xếp hàng chờ trên một làn "
    "(tính từ cabin thu phí đến xe cuối cùng) từ 750 m trở lên bị phạt tiền từ 50.000.000 đồng đến 70.000.000 đồng "
    "(điểm a khoản 5 Điều 10 " + ND336 + ").", d10("k5:a"), d10("k5"))

# ===== NĐ 336/2025 Điều 11: lái xe kinh doanh vận tải
d11b = lambda s: w(f"d11:{s}")  # noqa: E731
add("muc_phat", "Tài xế xe kinh doanh vận tải không mặc đồng phục, không đeo thẻ tên theo mẫu của đơn vị thì bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô, xe chở người bốn bánh có gắn động cơ kinh doanh vận tải không mặc đồng phục, không đeo "
    "thẻ tên của lái xe theo đúng mẫu đơn vị kinh doanh vận tải quy định bị " + fine("300.000", "500.000", 11, 1, nd=ND336)
    + ".", d11b("k1"))
add("doi_thuong", "tài xế taxi ko bật đồng hồ tính tiền theo yêu cầu khách thì bị phạt nhiêu",
    "Điều khiển xe taxi không có đồng hồ tính tiền cước (đối với loại xe đăng ký sử dụng đồng hồ), hoặc có nhưng không "
    "đúng quy định, hoặc không sử dụng đồng hồ để tính tiền cước theo yêu cầu của hành khách, hoặc can thiệp điều chỉnh "
    "tiền cước hiển thị bị " + fine("1.000.000", "2.000.000", 11, 2, "a", ND336) + ".", d11b("k2:a"), d11b("k2"))
add("muc_phat", "Tài xế taxi dùng phần mềm tính tiền nhưng trên xe không có thiết bị kết nối trực tiếp với hành khách thì bị "
    "phạt bao nhiêu?",
    "Hành vi này bị " + fine("1.000.000", "2.000.000", 11, 2, "b", ND336) + ".", d11b("k2:b"), d11b("k2"))
add("tinh_huong", "Tôi đi xe khách tuyến cố định, tài xế thu tiền vé cao hơn giá đã niêm yết. Tài xế bị xử phạt thế nào?",
    "Điều khiển xe kinh doanh vận tải hành khách theo tuyến cố định thu tiền vé cao hơn giá vé đã kê khai và niêm yết bị "
    + fine("1.000.000", "2.000.000", 11, 2, "d", ND336) + "; người vi phạm còn buộc nộp lại số lợi bất hợp pháp có được "
    "(khoản 3 Điều 11).", d11b("k2:d"), d11b("k2"), d11b("k3"))

out = ROOT / "data/train/drafts/xu_phat_07.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
