"""Đợt 1f G5: Xử phạt, Điều 8 (xe máy chuyên dùng), 13 (điều kiện xe ô tô), 20 (xe chở khách), 21 (xe chở hàng),
34 (quá tải, quá khổ) NĐ 168/2024. Ghi data/train/drafts/xu_phat_06.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
NEW = "2026-08-15"
S = []
START = 269


def v(s, d="2025-01-01"):
    return f"nd_168_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, dieu, k, diem=None):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều {dieu} {ND}"
    return f"phạt tiền từ {lo} đồng đến {hi} đồng ({where})"


def tru(n, dieu, k, diem):
    return f"bị trừ điểm giấy phép lái xe {n} điểm (điểm {diem} khoản {k} Điều {dieu})"


# ===== Điều 13: điều kiện của xe ô tô (người điều khiển)
d13 = lambda s, d="2025-01-01": v(f"d13:{s}", d)  # noqa: E731
P2, P6, P10 = d13("k13:a"), d13("k13:b"), d13("k13:c")
T2, T6, T10 = tru("02", 13, 13, "a"), tru("06", 13, 13, "b"), tru("10", 13, 13, "c")
FIX = d13("k11:a")
FIXT = ("buộc lắp đầy đủ thiết bị hoặc thay thế thiết bị đủ tiêu chuẩn, quy chuẩn an toàn kỹ thuật hoặc khôi phục lại "
        "tính năng kỹ thuật của thiết bị (điểm a khoản 11 Điều 13)")
add("muc_phat", "Lái ô tô không có kính chắn gió hoặc kính chắn gió bị vỡ không có tác dụng thì bị phạt bao nhiêu?",
    "Điều khiển xe không có kính chắn gió hoặc có nhưng vỡ không có tác dụng (đối với xe có thiết kế lắp kính chắn "
    "gió) bị " + fine("200.000", "400.000", 13, 1) + "; người vi phạm còn " + FIXT + ".", d13("k1"), FIX)
add("muc_phat", "Lái ô tô không có dây đai an toàn hoặc dây đai không có tác dụng thì bị phạt bao nhiêu?",
    "Điều khiển xe không có đủ dây đai an toàn (đối với loại xe phải có) hoặc có nhưng không có tác dụng, không đúng "
    "tiêu chuẩn thiết kế bị " + fine("400.000", "600.000", 13, 2, "a") + "; người vi phạm còn " + FIXT + ".",
    d13("k2:a"), d13("k2"), FIX)
add("doi_thuong", "ô tô bị gãy gương chiếu hậu vẫn lái đi thì có bị phạt ko",
    "Có thể bị phạt. Điều khiển xe ô tô không có đủ gương chiếu hậu, hoặc có nhưng không có tác dụng, bị "
    + fine("400.000", "600.000", 13, 2, "a") + " và buộc lắp đầy đủ hoặc thay thế thiết bị đủ tiêu chuẩn (điểm a "
    "khoản 11 Điều 13).", d13("k2:a"), d13("k2"), FIX)
add("muc_phat", "Ô tô không có còi hoặc còi không kêu thì người lái bị phạt bao nhiêu?",
    "Điều khiển xe không có còi hoặc có nhưng còi không có tác dụng bị " + fine("400.000", "600.000", 13, 2, "b")
    + "; người vi phạm còn " + FIXT + ".", d13("k2:b"), d13("k2"), FIX)
add("muc_phat", "Ô tô xả khói đen, không bảo đảm quy chuẩn môi trường về khí thải thì người lái bị phạt bao nhiêu?",
    "Điều khiển xe không có bộ phận giảm thanh, giảm khói, hoặc có nhưng không có tác dụng, không bảo đảm quy chuẩn môi "
    "trường về khí thải, tiếng ồn bị " + fine("400.000", "600.000", 13, 2, "c") + "; người vi phạm còn " + FIXT + ".",
    d13("k2:c"), d13("k2"), FIX)
add("muc_phat", "Lái ô tô lắp thêm đèn phía trước, trên nóc hoặc dưới gầm xe bị phạt bao nhiêu?",
    "Điều khiển xe lắp thêm đèn phía trước, phía sau, trên nóc, dưới gầm, một hoặc cả hai bên thành xe (trừ đèn sương "
    "mù dạng rời được lắp theo quy định) bị " + fine("1.000.000", "2.000.000", 13, 3, "a") + ", " + T2 + "; đồng thời "
    "buộc tháo bỏ những thiết bị lắp thêm không đúng quy định (điểm b khoản 11 Điều 13).",
    d13("k3:a"), d13("k3"), P2, d13("k11:b"))
add("doi_thuong", "độ thêm đèn trợ sáng trên nóc ô tô có bị phạt ko vậy",
    "Có. Điều khiển xe lắp thêm đèn trên nóc (và các vị trí phía trước, phía sau, dưới gầm, hai bên thành xe), trừ đèn "
    "sương mù dạng rời được lắp theo quy định, bị " + fine("1.000.000", "2.000.000", 13, 3, "a") + " và " + T2
    + "; ngoài ra buộc tháo bỏ đèn lắp thêm (điểm b khoản 11 Điều 13).", d13("k3:a"), d13("k3"), P2, d13("k11:b"))
add("muc_phat", "Lái ô tô có hệ thống lái (chuyển hướng) không đúng tiêu chuẩn an toàn kỹ thuật bị phạt bao nhiêu?",
    "Điều khiển xe có hệ thống chuyển hướng không đúng tiêu chuẩn an toàn kỹ thuật bị "
    + fine("1.000.000", "2.000.000", 13, 3, "b") + ", " + T2 + "; người vi phạm còn " + FIXT + ".",
    d13("k3:b"), d13("k3"), P2, FIX)
add("tinh_huong", "Tôi thay lốp ô tô không đúng kích cỡ của nhà sản xuất rồi lái đi trên đường. Tôi có bị phạt không?",
    "Có. Điều khiển xe không lắp đủ bánh lốp hoặc lắp bánh lốp không đúng kích cỡ, không bảo đảm tiêu chuẩn kỹ thuật bị "
    + fine("1.000.000", "2.000.000", 13, 3, "c") + "; người vi phạm còn " + FIXT + ".", d13("k3:c"), d13("k3"), FIX)
add("muc_phat", "Hiện nay tài xế lái xe khách có lắp thêm hoặc tháo bớt ghế, giường nằm không đúng thông số kiểm định bị "
    "phạt bao nhiêu?",
    "Theo điểm d khoản 3 Điều 13 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), người điều khiển xe ô tô kinh "
    "doanh vận tải hành khách lắp thêm hoặc tháo bớt ghế, giường nằm hoặc có kích thước hầm xe không đúng thông số kỹ "
    "thuật ghi trong chứng nhận kiểm định bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng; người vi phạm còn buộc "
    "khôi phục lại tính năng kỹ thuật, tháo bỏ những thiết bị lắp thêm không đúng quy định (điểm b khoản 11 Điều 13).",
    d13("k3:d", NEW), d13("k3"), d13("k11:b"))
add("muc_phat", "Lái ô tô không mang theo hoặc không có chứng nhận đăng ký xe bị phạt bao nhiêu?",
    "Điều khiển xe không có chứng nhận đăng ký xe, hoặc sử dụng chứng nhận đăng ký đã hết hạn, hết hiệu lực, bị "
    + fine("2.000.000", "3.000.000", 13, 4, "a") + " và " + T2 + ". Nếu không chứng minh được nguồn gốc xuất xứ của "
    "phương tiện thì còn bị tịch thu phương tiện (điểm b khoản 10 Điều 13).", d13("k4:a"), d13("k4"), P2, d13("k10:b"))
add("muc_phat", "Tài xế lái xe tải có kích thước thùng không đúng thông số trong chứng nhận kiểm định bị phạt thế nào?",
    "Theo điểm b khoản 4 Điều 13 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô tải có kích "
    "thước thùng xe không đúng với thông số kỹ thuật ghi trong chứng nhận kiểm định bị phạt tiền từ 2.000.000 đồng đến "
    "3.000.000 đồng và " + T2 + "; người vi phạm còn " + FIXT + ".", d13("k4:b", NEW), d13("k4"), P2, FIX)
add("muc_phat", "Ô tô dán phù hiệu, biểu trưng giống của cơ quan nhà nước thì người lái bị phạt bao nhiêu?",
    "Điều khiển xe dán, lắp phù hiệu, biểu trưng nhận diện tương tự của các cơ quan nhà nước, cơ quan ngoại giao, tổ "
    "chức quốc tế tại Việt Nam bị " + fine("2.000.000", "3.000.000", 13, 4, "c") + ", " + T2 + "; đồng thời buộc khôi "
    "phục lại tình trạng ban đầu (điểm c khoản 11 Điều 13).", d13("k4:c"), d13("k4"), P2, d13("k11:c"))
add("muc_phat", "Lái ô tô có tem kiểm định hết hạn dưới 01 tháng thì người lái bị phạt bao nhiêu?",
    "Điều khiển xe có giấy chứng nhận hoặc tem kiểm định an toàn kỹ thuật và bảo vệ môi trường đã hết hiệu lực dưới 01 "
    "tháng bị " + fine("3.000.000", "4.000.000", 13, 5, "a") + " và " + T2 + ".", d13("k5:a"), d13("k5"), P2)
add("muc_phat", "Lái ô tô có phanh không có tác dụng, không đúng tiêu chuẩn an toàn kỹ thuật bị phạt bao nhiêu?",
    "Điều khiển xe không đủ hệ thống hãm, hoặc có đủ nhưng không có tác dụng, không đúng tiêu chuẩn an toàn kỹ thuật bị "
    + fine("3.000.000", "4.000.000", 13, 5, "b") + ", " + T2 + "; người vi phạm còn " + FIXT + ".",
    d13("k5:b"), d13("k5"), P2, FIX)
add("muc_phat", "Lái xe kinh doanh vận tải có niên hạn sử dụng không bảo đảm điều kiện của hình thức kinh doanh đã đăng ký "
    "bị phạt bao nhiêu?",
    "Người điều khiển xe bị " + fine("3.000.000", "4.000.000", 13, 5, "c") + " và " + T2 + ".",
    d13("k5:c"), d13("k5"), P2)
add("doi_thuong", "ô tô gắn còi quá to vượt âm lượng thì tài xế bị phạt bao nhiêu",
    "Điều khiển xe lắp đặt, sử dụng còi vượt quá âm lượng theo quy định bị "
    + fine("3.000.000", "4.000.000", 13, 5, "d") + ", " + T2 + "; người vi phạm còn " + FIXT + ".",
    d13("k5:d"), d13("k5"), P2, FIX)
add("muc_phat", "Lái ô tô sử dụng chứng nhận đăng ký xe hoặc tem kiểm định không do cơ quan có thẩm quyền cấp bị xử phạt "
    "thế nào?",
    "Sử dụng chứng nhận đăng ký xe, giấy chứng nhận, tem kiểm định không do cơ quan có thẩm quyền cấp hoặc bị tẩy xóa, "
    "hoặc chứng nhận đăng ký không đúng số khung, số máy của xe, bị " + fine("4.000.000", "6.000.000", 13, 6, "a")
    + " và " + T2 + ". Các giấy tờ đó bị thu hồi (khoản 12 Điều 13), người vi phạm buộc nộp lại (điểm d khoản 11 "
    "Điều 13); nếu không chứng minh được nguồn gốc xuất xứ của phương tiện thì còn bị tịch thu phương tiện (điểm b "
    "khoản 10 Điều 13).", d13("k6:a"), d13("k6"), P2, d13("k12"), d13("k11:d"), d13("k10:b"))
add("muc_phat", "Lái ô tô không có tem kiểm định hoặc tem kiểm định hết hạn từ 01 tháng trở lên bị phạt bao nhiêu?",
    "Điều khiển xe không có giấy chứng nhận hoặc tem kiểm định an toàn kỹ thuật và bảo vệ môi trường (đối với loại xe "
    "phải kiểm định, trừ xe đăng ký tạm thời) hoặc có nhưng đã hết hiệu lực từ 01 tháng trở lên bị "
    + fine("4.000.000", "6.000.000", 13, 6, "b") + " và " + T2 + ".", d13("k6:b"), d13("k6"), P2)
add("tinh_huong", "Tôi lái chiếc ô tô của công ty, đăng kiểm của xe đã hết hạn 3 tháng. Tôi bị phạt bao nhiêu?",
    "Người điều khiển xe có tem kiểm định hết hiệu lực từ 01 tháng trở lên bị " + fine("4.000.000", "6.000.000", 13, 6,
                                                                                         "b")
    + " và " + T2 + ". Riêng chủ xe là tổ chức đưa xe hết hạn kiểm định từ 01 tháng trở lên tham gia giao thông còn bị "
    "phạt tiền từ 20.000.000 đồng đến 24.000.000 đồng (điểm a khoản 11 Điều 32).",
    d13("k6:b"), d13("k6"), P2, v("d32:k11:a"), v("d32:k11"))
add("muc_phat", "Lái ô tô đăng ký tạm thời chạy quá phạm vi, tuyến đường, thời hạn cho phép bị phạt bao nhiêu?",
    "Điều khiển xe đăng ký tạm thời, xe có phạm vi hoạt động hạn chế hoạt động quá phạm vi, tuyến đường, thời hạn cho "
    "phép bị " + fine("10.000.000", "12.000.000", 13, 7, "a") + " và " + T2 + ".", d13("k7:a"), d13("k7"), P2)
add("muc_phat", "Lái ô tô không gắn biển số bị phạt bao nhiêu?",
    "Điều khiển xe (kể cả rơ moóc và sơ mi rơ moóc) không gắn biển số (đối với loại xe phải gắn biển số) bị "
    + fine("10.000.000", "12.000.000", 13, 7, "b") + " và " + T6 + ".", d13("k7:b"), d13("k7"), P6)
add("muc_phat", "Lái ô tô gắn biển số giả (không do cơ quan có thẩm quyền cấp) bị xử phạt thế nào?",
    "Điều khiển xe gắn biển số không đúng với chứng nhận đăng ký xe hoặc không do cơ quan có thẩm quyền cấp bị "
    + fine("20.000.000", "26.000.000", 13, 8, "a") + ", " + T10 + "; đồng thời bị tịch thu biển số xe (điểm a khoản 10 "
    "Điều 13).", d13("k8:a"), d13("k8"), P10, d13("k10:a"))
add("muc_phat", "Hiện nay lái ô tô gắn biển số bị bẻ cong, che lấp hoặc làm thay đổi chữ, số bị phạt bao nhiêu?",
    "Theo điểm b khoản 8 Điều 13 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe không gắn đủ biển "
    "số, gắn biển số không đúng vị trí, quy cách, gắn biển số bị bẻ cong, che lấp, làm thay đổi chữ, số, màu sắc, hình "
    "dạng, kích thước bị phạt tiền từ 20.000.000 đồng đến 26.000.000 đồng và " + T6 + "; người vi phạm còn buộc thực "
    "hiện đúng quy định về biển số (điểm a khoản 11 Điều 13).", d13("k8:b", NEW), d13("k8"), P6, FIX)
add("doi_thuong", "dán băng dính che bớt biển số ô tô thì bị phạt bao nhiêu thế",
    "Gắn biển số bị che lấp, làm thay đổi chữ, số hoặc dán lên chữ, số của biển số xe khi điều khiển ô tô bị "
    + fine("20.000.000", "26.000.000", 13, 8, "b") + " và " + T6 + " (quy định có hiệu lực từ ngày 15/8/2026).",
    d13("k8:b", NEW), d13("k8"), P6)
add("muc_phat", "Lái ô tô đã quá niên hạn sử dụng tham gia giao thông thì bị xử lý thế nào?",
    "Người điều khiển xe quá niên hạn sử dụng tham gia giao thông bị tịch thu phương tiện (điểm a khoản 9 Điều 13 " + ND
    + "), trừ hành vi điều khiển xe kinh doanh vận tải có niên hạn không bảo đảm điều kiện của hình thức kinh doanh đã "
    "đăng ký (điểm c khoản 5 Điều 13).", d13("k9:a"), d13("k9"))
add("muc_phat", "Điều khiển xe công nông thuộc diện bị đình chỉ tham gia giao thông thì bị xử lý thế nào?",
    "Điều khiển loại xe sản xuất, lắp ráp trái quy định tham gia giao thông, bao gồm cả xe công nông thuộc diện bị đình "
    "chỉ tham gia giao thông, bị tịch thu phương tiện (điểm b khoản 9 Điều 13 " + ND + ").", d13("k9:b"), d13("k9"))

# ===== Điều 20: xe chở hành khách, chở người
d20 = lambda s, d="2025-01-01": v(f"d20:{s}", d)  # noqa: E731
Q2 = d20("k10:a")
U2 = tru("02", 20, 10, "a")
add("muc_phat", "Tài xế xe khách không hướng dẫn hành khách đứng, nằm, ngồi đúng vị trí trong xe bị phạt bao nhiêu?",
    "Không hướng dẫn hành khách đứng, nằm, ngồi đúng vị trí quy định trong xe bị " + fine("100.000", "200.000", 20, 1)
    + ".", d20("k1"))
add("muc_phat", "Xe khách không đóng cửa lên xuống khi xe đang chạy thì tài xế bị phạt bao nhiêu?",
    "Người điều khiển xe chở hành khách không đóng cửa lên xuống khi xe đang chạy bị "
    + fine("600.000", "800.000", 20, 3, "a") + ".", d20("k3:a"), d20("k3"))
add("muc_phat", "Tài xế xe khách để hành khách ngồi trên xe khi xe xuống phà, đang trên phà thì bị phạt bao nhiêu?",
    "Để người ngồi trên xe khi xe xuống phà, đang trên phà và khi lên bến (trừ người lái xe, trẻ em, phụ nữ mang thai, "
    "người già yếu, người bệnh, người khuyết tật) bị " + fine("600.000", "800.000", 20, 3, "b") + ".",
    d20("k3:b"), d20("k3"))
add("muc_phat", "Xe khách không chạy đúng tuyến đường, lịch trình được phép hoạt động thì tài xế bị phạt bao nhiêu?",
    "Không chạy đúng tuyến đường, lịch trình, hành trình vận tải được phép hoạt động bị "
    + fine("600.000", "800.000", 20, 3, "c") + " và " + U2 + ".", d20("k3:c"), d20("k3"), Q2)
add("muc_phat", "Tài xế xe khách để người mắc võng nằm trên xe khi xe đang chạy bị phạt bao nhiêu?",
    "Để người mắc võng nằm trên xe khi xe đang chạy bị " + fine("600.000", "800.000", 20, 3, "d") + " và " + U2 + ".",
    d20("k3:d"), d20("k3"), Q2)
add("muc_phat", "Xe khách chở hành lý vượt quá kích thước bao ngoài của xe thì tài xế bị phạt bao nhiêu?",
    "Chở hành lý, hàng hóa vượt quá kích thước bao ngoài của xe bị " + fine("600.000", "800.000", 20, 3, "e") + " và "
    + U2 + ".", d20("k3:e"), d20("k3"), Q2)
add("muc_phat", "Xe ô tô kinh doanh vận tải không có dây đai an toàn tại các ghế ngồi, giường nằm thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe ô tô kinh doanh vận tải không có dây đai an toàn tại các vị trí ghế ngồi, giường nằm theo quy định "
    "(trừ xe buýt nội tỉnh) bị " + fine("600.000", "800.000", 20, 3, "h") + ".", d20("k3:h"), d20("k3"))
add("quy_tac", "Tài xế xe khách chở quá số người được phép thì bị xử phạt theo cách tính nào?",
    "Người điều khiển xe ô tô chở hành khách, ô tô chở người (trừ xe buýt) chở quá số người quy định bị phạt tiền từ "
    "400.000 đồng đến 600.000 đồng trên mỗi người vượt quá, nhưng tổng mức phạt tiền tối đa không vượt quá 75.000.000 "
    "đồng (khoản 2 Điều 20 " + ND + "). Nếu chở vượt trên 50% đến 100% số người được phép chở còn bị trừ điểm giấy phép "
    "lái xe 04 điểm (điểm b khoản 10 Điều 20); vượt trên 100% bị trừ 10 điểm (điểm d khoản 10 Điều 20).",
    d20("k2"), d20("k10:b"), d20("k10:d"))
add("muc_phat", "Xe khách tuyến cố định cự ly trên 300 km chở quá số người quy định thì tài xế bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô chở hành khách (kinh doanh vận tải theo tuyến cố định, hợp đồng) chạy tuyến có cự ly lớn "
    "hơn 300 km chở quá số người quy định bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng trên mỗi người vượt quá, "
    "tổng mức phạt tối đa không vượt quá 75.000.000 đồng (khoản 4 Điều 20 " + ND + "). Chở vượt trên 50% đến 100% còn "
    "bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 10 Điều 20); vượt trên 100% bị trừ 10 điểm (điểm d khoản 10 "
    "Điều 20).", d20("k4"), d20("k10:b"), d20("k10:d"))
add("muc_phat", "Tài xế xe khách để người lên, xuống xe khi xe đang chạy bị phạt bao nhiêu?",
    "Để người lên, xuống xe khi xe đang chạy bị " + fine("1.000.000", "2.000.000", 20, 5, "a") + " và " + U2 + ".",
    d20("k5:a"), d20("k5"), Q2)
add("muc_phat", "Xe khách đón, trả khách không đúng nơi quy định thì tài xế bị phạt bao nhiêu?",
    "Đón, trả hành khách không đúng nơi quy định trên những tuyến đường đã xác định nơi đón, trả khách, hoặc dừng đón, "
    "trả khách quá thời gian quy định, bị " + fine("1.000.000", "2.000.000", 20, 5, "c") + " và " + U2 + ".",
    d20("k5:c"), d20("k5"), Q2)
add("tinh_huong", "Tôi lái xe khách dừng lại đón khách ngay ở đoạn đường cong bị che khuất tầm nhìn. Tôi bị phạt bao nhiêu?",
    "Đón, trả hành khách tại nơi cấm dừng, cấm đỗ, nơi đường cong tầm nhìn bị che khuất bị "
    + fine("1.000.000", "2.000.000", 20, 5, "d") + " và " + U2 + ".", d20("k5:d"), d20("k5"), Q2)
add("muc_phat", "Xe khách tuyến cố định không mang theo lệnh vận chuyển thì tài xế bị phạt bao nhiêu?",
    "Vận chuyển hành khách theo tuyến cố định không có hoặc không mang theo lệnh vận chuyển, hoặc lệnh vận chuyển không "
    "ghi đầy đủ thông tin, không có xác nhận của bến xe khách nơi đi, nơi đến, bị "
    + fine("1.000.000", "2.000.000", 20, 5, "e") + " và " + U2 + ".", d20("k5:e"), d20("k5"), Q2)
add("muc_phat", "Hiện nay xe hợp đồng dùng hợp đồng giấy nhưng không có danh sách hành khách thì tài xế bị phạt bao nhiêu?",
    "Theo điểm đ khoản 5 Điều 20 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe vận tải hành khách "
    "theo hợp đồng sử dụng hợp đồng bằng văn bản giấy mà không có hợp đồng vận tải, danh sách hành khách, hoặc đón "
    "khách không có tên trong danh sách, bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng và " + U2 + ".",
    d20("k5:đ", NEW), d20("k5"), Q2)
add("muc_phat", "Xe khách chở hành lý, hàng hóa vượt quá trọng tải thiết kế của xe thì tài xế bị phạt bao nhiêu?",
    "Chở hành lý, hàng hóa vượt quá trọng tải theo thiết kế của xe bị " + fine("1.000.000", "2.000.000", 20, 5, "i")
    + " và " + U2 + ".", d20("k5:i"), d20("k5"), Q2)
add("muc_phat", "Tài xế xe khách không dùng thẻ nhận dạng lái xe hoặc dùng thẻ của người khác để đăng nhập bị phạt bao nhiêu?",
    "Không sử dụng thẻ nhận dạng lái xe để đăng nhập thông tin, hoặc sử dụng thẻ của lái xe khác, khi điều khiển xe ô "
    "tô chở khách bị " + fine("1.000.000", "2.000.000", 20, 5, "k") + " và " + U2 + ".", d20("k5:k"), d20("k5"), Q2)
add("muc_phat", "Xe kinh doanh vận tải hành khách không lắp camera ghi hình người lái thì tài xế bị phạt bao nhiêu?",
    "Theo điểm l khoản 5 Điều 20 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe kinh doanh vận tải "
    "hành khách, xe vận tải nội bộ không lắp thiết bị ghi nhận hình ảnh người lái xe, hoặc có lắp nhưng không có tác "
    "dụng, hoặc làm sai lệch dữ liệu, bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng.", d20("k5:l", NEW), d20("k5"))
add("muc_phat", "Tài xế xe khách chở người trên mui xe hoặc trong khoang chở hành lý bị phạt bao nhiêu?",
    "Chở người trên mui xe, trong khoang chở hành lý của xe bị " + fine("3.000.000", "5.000.000", 20, 6, "b") + " và "
    + U2 + ".", d20("k6:b"), d20("k6"), Q2)
add("muc_phat", "Tài xế xe khách tranh giành, lôi kéo, ép hành khách đi xe bị phạt bao nhiêu?",
    "Đe dọa, xúc phạm, tranh giành, lôi kéo hành khách; đe dọa, cưỡng ép hành khách sử dụng dịch vụ ngoài ý muốn bị "
    + fine("3.000.000", "5.000.000", 20, 6, "c") + " và " + U2 + ".", d20("k6:c"), d20("k6"), Q2)
add("muc_phat", "Xe khách chở hàng dễ cháy, dễ nổ hoặc hàng có mùi hôi thối trên xe thì tài xế bị phạt bao nhiêu?",
    "Vận chuyển hàng hóa nguy hiểm, hàng độc hại, dễ cháy, dễ nổ, động vật, hàng có mùi hôi thối hoặc hàng hóa khác ảnh "
    "hưởng đến sức khỏe của hành khách trên xe bị " + fine("3.000.000", "5.000.000", 20, 6, "a") + " và " + U2 + ".",
    d20("k6:a"), d20("k6"), Q2)
add("tinh_huong", "Tôi lái xe khách liên tục quá thời gian cho phép mà không nghỉ. Tôi bị phạt bao nhiêu?",
    "Theo điểm d khoản 6 Điều 20 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô kinh doanh vận "
    "tải quá thời gian quy định tại khoản 1 Điều 64 Luật Trật tự, an toàn giao thông đường bộ, hoặc không thực hiện "
    "đúng quy định về thời gian nghỉ giữa hai lần lái xe liên tục, bị phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng "
    "và " + U2 + ".", d20("k6:d", NEW), d20("k6"), Q2)
add("muc_phat", "Xe kinh doanh vận tải hành khách không lắp thiết bị giám sát hành trình thì tài xế bị phạt bao nhiêu?",
    "Theo điểm đ khoản 6 Điều 20 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe kinh doanh vận tải "
    "hành khách, xe vận tải nội bộ không lắp thiết bị giám sát hành trình, hoặc thiết bị không hoạt động, hoặc làm sai "
    "lệch dữ liệu, bị phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng và " + U2 + ".", d20("k6:đ", NEW), d20("k6"), Q2)
add("muc_phat", "Xe khách không gắn phù hiệu hoặc phù hiệu hết hạn thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe chở hành khách không có hoặc không gắn phù hiệu theo quy định, hoặc có nhưng đã hết giá trị sử dụng, "
    "hoặc sử dụng phù hiệu không do cơ quan có thẩm quyền cấp bị " + fine("5.000.000", "7.000.000", 20, 7) + " và "
    + U2 + "; phù hiệu hết giá trị hoặc không do cơ quan có thẩm quyền cấp bị thu hồi (khoản 9 Điều 20).",
    d20("k7"), Q2, d20("k9"))
add("muc_phat", "Tài xế xe khách dừng đón, trả khách trên đường cao tốc bị phạt bao nhiêu?",
    "Đón, trả hành khách trên đường cao tốc bị " + fine("10.000.000", "12.000.000", 20, 8) + " và bị trừ điểm giấy phép "
    "lái xe 06 điểm (điểm c khoản 10 Điều 20).", d20("k8"), d20("k10:c", NEW))
add("doi_thuong", "xe nhà không kinh doanh mà chở khách thu tiền (xe dù) thì bị phạt nhiêu",
    "Theo khoản 8a Điều 20 " + ND + " (có hiệu lực từ ngày 15/8/2026), người điều khiển xe ô tô không kinh doanh vận tải "
    "hành khách nhưng chở người có thu tiền, hoặc ký hợp đồng, nhận đặt chỗ để chở người, bị phạt tiền từ 12.000.000 "
    "đồng đến 14.000.000 đồng và bị trừ điểm giấy phép lái xe 06 điểm (điểm c khoản 10 Điều 20).",
    d20("k8a", NEW), d20("k10:c", NEW))

# ===== Điều 21: xe chở hàng
d21 = lambda s, d="2025-01-01": v(f"d21:{s}", d)  # noqa: E731
H2, H4, H6, H8, H10 = d21("k13:a"), d21("k13:b"), d21("k13:c"), d21("k13:d"), d21("k13:đ")
V2 = "bị trừ điểm giấy phép lái xe (khi điều khiển xe ô tô) 02 điểm (điểm a khoản 13 Điều 21)"
V4 = tru("04", 21, 13, "b")
add("muc_phat", "Tài xế xe tải xếp hàng trên nóc buồng lái bị phạt bao nhiêu?",
    "Điều khiển xe xếp hàng trên nóc buồng lái, xếp hàng làm lệch xe bị " + fine("600.000", "800.000", 21, 1, "a") + ".",
    d21("k1:a"), d21("k1"))
add("muc_phat", "Xe tải không chốt, đóng cố định cửa sau thùng xe khi xe đang chạy thì tài xế bị phạt bao nhiêu?",
    "Không chốt, đóng cố định cửa sau, cửa bên thùng xe khi xe đang chạy bị " + fine("600.000", "800.000", 21, 1, "b")
    + ".", d21("k1:b"), d21("k1"))
add("muc_phat", "Hiện nay xe tải chở hàng vượt trọng tải cho phép ghi trong kiểm định trên 10% đến 30% thì tài xế bị phạt "
    "bao nhiêu?",
    "Theo điểm a khoản 2 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe chở hàng vượt trọng "
    "tải cho phép ghi trong chứng nhận kiểm định trên 10% đến 30% (với xe xi téc chở chất lỏng là trên 20% đến 30%) bị "
    "phạt tiền từ 800.000 đồng đến 1.000.000 đồng.", d21("k2:a", NEW), d21("k2"))
add("muc_phat", "Xe tải chở hàng vượt quá bề rộng thùng xe thì tài xế bị phạt bao nhiêu?",
    "Theo điểm b khoản 2 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), chở hàng trên nóc thùng xe, chở "
    "hàng vượt quá bề rộng thùng xe, hoặc vượt phía trước, phía sau thùng xe trên 10% chiều dài toàn bộ của xe theo "
    "thiết kế, bị phạt tiền từ 800.000 đồng đến 1.000.000 đồng và " + V2 + ".", d21("k2:b", NEW), d21("k2"), H2)
add("muc_phat", "Tài xế xe tải chở người trên mui xe bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô tải chở người trên mui xe bị " + fine("800.000", "1.000.000", 21, 2, "c") + " và " + V2
    + ".", d21("k2:c"), d21("k2"), H2)
add("muc_phat", "Xe kinh doanh vận tải hàng hóa không mang theo giấy vận tải thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe kinh doanh vận tải hàng hóa không có hoặc không mang theo giấy vận tải bằng văn bản giấy, hoặc không "
    "có thiết bị truy cập được nội dung giấy vận tải điện tử, hoặc có nhưng không cung cấp khi lực lượng chức năng yêu "
    "cầu, bị " + fine("800.000", "1.000.000", 21, 2, "đ") + " và " + V2 + ".", d21("k2:đ"), d21("k2"), H2)
add("muc_phat", "Tài xế xe tải kinh doanh vận tải không dùng thẻ nhận dạng lái xe để đăng nhập bị phạt bao nhiêu?",
    "Không sử dụng thẻ nhận dạng lái xe để đăng nhập thông tin, hoặc dùng thẻ của lái xe khác, khi điều khiển xe tham "
    "gia kinh doanh vận tải hàng hóa bị " + fine("1.000.000", "2.000.000", 21, 3, "a") + " và " + V2 + ".",
    d21("k3:a"), d21("k3"), H2)
add("muc_phat", "Xe ô tô đầu kéo không lắp thiết bị ghi nhận hình ảnh người lái xe thì tài xế bị phạt bao nhiêu?",
    "Theo điểm b khoản 3 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô kinh doanh vận "
    "tải, xe ô tô đầu kéo, xe vận tải nội bộ không lắp thiết bị ghi nhận hình ảnh người lái xe, hoặc có lắp nhưng không "
    "có tác dụng, hoặc làm sai lệch dữ liệu, bị phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng.",
    d21("k3:b", NEW), d21("k3"))
add("muc_phat", "Xe ô tô tải chở hàng vượt quá chiều cao xếp hàng cho phép thì tài xế bị phạt bao nhiêu?",
    "Người điều khiển xe chở hàng vượt quá chiều cao xếp hàng cho phép đối với xe ô tô tải (kể cả rơ moóc và sơ mi rơ "
    "moóc) bị " + fine("2.000.000", "3.000.000", 21, 4) + " và " + V2 + ".", d21("k4"), H2)
add("muc_phat", "Xe tải chở hàng vượt trọng tải cho phép ghi trong kiểm định trên 30% đến 50% thì tài xế bị phạt bao nhiêu?",
    "Theo điểm a khoản 5 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), tài xế bị phạt tiền từ 3.000.000 "
    "đồng đến 5.000.000 đồng và " + V2 + ".", d21("k5:a", NEW), d21("k5"), H2)
add("muc_phat", "Tài xế xe tải kinh doanh vận tải lái quá thời gian quy định, không nghỉ giữa hai lần lái bị phạt bao nhiêu?",
    "Theo điểm b khoản 5 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô kinh doanh vận "
    "tải, xe vận tải nội bộ quá thời gian quy định tại khoản 1 Điều 64 Luật Trật tự, an toàn giao thông đường bộ, hoặc "
    "không thực hiện đúng quy định về thời gian nghỉ giữa hai lần lái xe liên tục, bị phạt tiền từ 3.000.000 đồng đến "
    "5.000.000 đồng và " + V2 + ".", d21("k5:b", NEW), d21("k5"), H2)
add("muc_phat", "Xe tải kinh doanh vận tải không lắp thiết bị giám sát hành trình thì tài xế bị phạt bao nhiêu?",
    "Theo điểm c khoản 5 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô kinh doanh vận "
    "tải, xe ô tô đầu kéo, xe vận tải nội bộ không lắp thiết bị giám sát hành trình, hoặc có lắp nhưng không có tác "
    "dụng, hoặc làm sai lệch dữ liệu, bị phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng và " + V2 + ".",
    d21("k5:c", NEW), d21("k5"), H2)
add("tinh_huong", "Xe tải của tôi chở hàng vượt trọng tải cho phép ghi trong kiểm định khoảng 60%. Tôi là tài xế thì bị "
    "phạt bao nhiêu?",
    "Mức vượt 60% thuộc khoảng trên 50% đến 100% tại điểm a khoản 6 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày "
    "15/8/2026): người điều khiển xe bị phạt tiền từ 5.000.000 đồng đến 7.000.000 đồng và " + V4 + ".",
    d21("k6:a", NEW), d21("k6"), H4)
add("muc_phat", "Xe tải không gắn phù hiệu hoặc phù hiệu hết hạn thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe không có hoặc không gắn phù hiệu (đối với loại xe phải gắn phù hiệu), hoặc phù hiệu đã hết giá trị "
    "sử dụng, hoặc không do cơ quan có thẩm quyền cấp, bị " + fine("5.000.000", "7.000.000", 21, 6, "c") + " và " + V2
    + "; phù hiệu đó bị thu hồi (khoản 12 Điều 21).", d21("k6:c"), d21("k6"), H2, d21("k12"))
add("muc_phat", "Xe chở hàng trong đô thị không chạy đúng tuyến, phạm vi, thời gian quy định thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe chở hàng trong đô thị không chạy đúng tuyến, phạm vi, thời gian quy định bị "
    + fine("5.000.000", "7.000.000", 21, 6, "d") + " và " + V2 + ".", d21("k6:d"), d21("k6"), H2)
add("muc_phat", "Xe tải chở hàng vượt trọng tải cho phép ghi trong kiểm định trên 100% đến 150% thì tài xế bị phạt bao nhiêu?",
    "Theo điểm a khoản 7 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), tài xế bị phạt tiền từ 7.000.000 "
    "đồng đến 8.000.000 đồng và bị trừ điểm giấy phép lái xe 08 điểm (điểm d khoản 13 Điều 21).",
    d21("k7:a", NEW), d21("k7"), H8)
add("muc_phat", "Xe tải chở hàng vượt trọng tải cho phép ghi trong kiểm định trên 150% thì tài xế bị phạt bao nhiêu?",
    "Theo điểm a khoản 8 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), tài xế bị phạt tiền từ 8.000.000 "
    "đồng đến 12.000.000 đồng và bị trừ điểm giấy phép lái xe 10 điểm (điểm đ khoản 13 Điều 21).",
    d21("k8:a", NEW), d21("k8"), H10)
add("doi_thuong", "xe tải chở cát mà xe ko có thành thùng thì bị phạt bao nhiêu",
    "Theo điểm đ khoản 8 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), vận chuyển hàng rời, vật liệu xây "
    "dựng trên xe mà xe không có thành thùng, hoặc vận chuyển hàng không chằng buộc, chằng buộc không bảo đảm an toàn, "
    "bị phạt tiền từ 8.000.000 đồng đến 12.000.000 đồng và " + V4 + ".", d21("k8:đ", NEW), d21("k8"), H4)
add("muc_phat", "Xe ô tô không kinh doanh vận tải hàng hóa nhưng chở hàng có thu tiền thì tài xế bị phạt bao nhiêu?",
    "Theo điểm e khoản 8 Điều 21 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), điều khiển xe ô tô không kinh "
    "doanh vận tải hàng hóa nhưng chở hàng hóa trên xe có thu tiền bị phạt tiền từ 8.000.000 đồng đến 12.000.000 đồng.",
    d21("k8:e", NEW), d21("k8"))
add("muc_phat", "Chở công-ten-nơ không bảo đảm quy chuẩn, tiêu chuẩn kỹ thuật thì tài xế bị phạt bao nhiêu?",
    "Chở công-ten-nơ trên xe (kể cả sơ mi rơ moóc) không bảo đảm quy chuẩn, tiêu chuẩn kỹ thuật của công-ten-nơ bị "
    + fine("8.000.000", "12.000.000", 21, 8, "c") + " và " + V4 + ".", d21("k8:c"), d21("k8"), H4)
add("muc_phat", "Tài xế xe tải dừng nhận, trả hàng trên đường cao tốc bị phạt bao nhiêu?",
    "Người điều khiển xe thực hiện hành vi nhận, trả hàng trên đường cao tốc bị " + fine("10.000.000", "12.000.000", 21, 9)
    + " và bị trừ điểm giấy phép lái xe 06 điểm (điểm c khoản 13 Điều 21).", d21("k9"), H6)
add("muc_phat", "Chở công-ten-nơ mà không sử dụng cơ cấu khóa hãm thì tài xế bị phạt bao nhiêu?",
    "Chở công-ten-nơ trên xe (kể cả sơ mi rơ moóc) mà không sử dụng cơ cấu khóa hãm công-ten-nơ với xe, hoặc có sử "
    "dụng nhưng công-ten-nơ vẫn bị xê dịch trong quá trình vận chuyển, bị " + fine("18.000.000", "22.000.000", 21, 10, "b")
    + " và " + V4 + ".", d21("k10:b"), d21("k10"), H4)
add("muc_phat", "Chở máy móc, hàng dạng trụ không chằng buộc theo quy định thì tài xế bị phạt bao nhiêu?",
    "Vận chuyển hàng hóa là phương tiện vận tải, máy móc, thiết bị kỹ thuật, hàng dạng trụ không chằng buộc hoặc chằng "
    "buộc không theo quy định bị " + fine("18.000.000", "22.000.000", 21, 10, "a") + " và " + V4 + ".",
    d21("k10:a"), d21("k10"), H4)
add("tinh_huong", "Tôi chở cuộn thép trên xe tải mà không chằng buộc theo quy định, cuộn thép rơi xuống gây tai nạn. Tôi bị "
    "phạt bao nhiêu?",
    "Vi phạm khoản 10 Điều 21 (chở hàng dạng trụ không chằng buộc theo quy định) mà gây tai nạn giao thông thì bị "
    + fine("30.000.000", "35.000.000", 21, 11) + " và bị trừ điểm giấy phép lái xe 10 điểm (điểm đ khoản 13 Điều 21).",
    d21("k11"), d21("k10:a"), H10)

# ===== Điều 34: quá tải trọng, quá khổ giới hạn của đường bộ
d34 = lambda s, d="2025-01-01": v(f"d34:{s}", d)  # noqa: E731
W2 = tru("02", 34, 7, "a")
add("muc_phat", "Tài xế không thực hiện đúng quy định trong giấy phép lưu hành bị phạt bao nhiêu?",
    "Không thực hiện đúng quy định trong giấy phép lưu hành (trừ các hành vi tại điểm a, điểm b khoản 3; điểm b, điểm c "
    "khoản 4 Điều 34) bị " + fine("3.000.000", "5.000.000", 34, 1) + " và " + W2 + ".", d34("k1"), d34("k7:a"))
add("muc_phat", "Xe có tổng trọng lượng vượt quá tải trọng cho phép của đường bộ trên 10% đến 20% thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe mà tổng trọng lượng (khối lượng toàn bộ) vượt quá tải trọng cho phép của đường bộ trên 10% đến 20%, "
    "trừ trường hợp có giấy phép lưu hành còn giá trị sử dụng, bị " + fine("4.000.000", "6.000.000", 34, 2)
    + ". Nếu gây hư hại cầu, đường còn buộc khôi phục lại tình trạng ban đầu (khoản 6 Điều 34).", d34("k2"), d34("k6"))
add("muc_phat", "Chở hàng vượt khổ giới hạn ghi trong giấy phép lưu hành thì tài xế bị phạt bao nhiêu?",
    "Chở hàng vượt khổ giới hạn của xe hoặc của đường bộ ghi trong giấy phép lưu hành bị "
    + fine("8.000.000", "10.000.000", 34, 3, "a") + " và " + W2 + ".", d34("k3:a"), d34("k3"), d34("k7:a"))
add("muc_phat", "Xe bánh xích đi trên đường không có giấy phép lưu hành thì người điều khiển bị phạt bao nhiêu?",
    "Điều khiển xe bánh xích tham gia giao thông không có giấy phép lưu hành, hoặc giấy phép không còn giá trị sử dụng, "
    "hoặc lưu thông trực tiếp trên đường mà không thực hiện biện pháp bảo vệ đường, bị "
    + fine("8.000.000", "10.000.000", 34, 3, "b") + " và " + W2 + ".", d34("k3:b"), d34("k3"), d34("k7:a"))
add("muc_phat", "Xe có kích thước bao ngoài vượt quá khổ giới hạn của đường bộ mà không có giấy phép lưu hành thì bị phạt "
    "bao nhiêu?",
    "Điều khiển xe có kích thước bao ngoài vượt quá khổ giới hạn của đường bộ, hoặc chở hàng vượt khổ giới hạn của "
    "đường bộ, vượt quá kích thước giới hạn xếp hàng của xe, trừ trường hợp có giấy phép lưu hành còn giá trị, bị "
    + fine("8.000.000", "10.000.000", 34, 3, "c") + " và " + W2 + ".", d34("k3:c"), d34("k3"), d34("k7:a"))
add("tinh_huong", "Xe tải của tôi có tổng trọng lượng vượt tải trọng cho phép của cầu đường khoảng 30% và làm hư mặt đường. "
    "Tôi bị xử phạt thế nào?",
    "Mức vượt 30% thuộc khoảng trên 20% đến 50% (điểm a khoản 4 Điều 34 " + ND + "), trừ trường hợp có giấy phép lưu "
    "hành còn giá trị: người điều khiển bị phạt tiền từ 13.000.000 đồng đến 15.000.000 đồng và " + W2 + ". Vì gây hư "
    "hại cầu, đường nên còn buộc khôi phục lại tình trạng ban đầu (khoản 6 Điều 34).",
    d34("k4:a"), d34("k4"), d34("k7:a"), d34("k6"))
add("muc_phat", "Có giấy phép lưu hành nhưng tổng trọng lượng xe vẫn vượt quá quy định trong giấy phép thì bị phạt bao nhiêu?",
    "Điều khiển xe có giấy phép lưu hành còn giá trị nhưng tổng trọng lượng hoặc tải trọng trục xe vượt quá quy định "
    "trong giấy phép bị " + fine("13.000.000", "15.000.000", 34, 4, "b") + " và " + tru("03", 34, 7, "b") + ".",
    d34("k4:b"), d34("k4"), d34("k7:b"))
add("muc_phat", "Có giấy phép lưu hành nhưng đi không đúng tuyến đường ghi trong giấy phép thì bị phạt bao nhiêu?",
    "Điều khiển xe có giấy phép lưu hành còn giá trị nhưng đi không đúng tuyến đường quy định trong giấy phép bị "
    + fine("13.000.000", "15.000.000", 34, 4, "c") + " và " + tru("03", 34, 7, "b") + ".",
    d34("k4:c"), d34("k4"), d34("k7:b"))
add("muc_phat", "Xe vượt quá tải trọng cho phép của đường bộ trên 50% thì tài xế bị phạt bao nhiêu?",
    "Điều khiển xe mà tổng trọng lượng hoặc tải trọng trục xe (bao gồm cả hàng hóa và người được chở) vượt quá tải "
    "trọng cho phép của đường bộ trên 50%, trừ trường hợp có giấy phép lưu hành còn giá trị, bị "
    + fine("40.000.000", "50.000.000", 34, 5, "a") + " và " + tru("04", 34, 7, "c") + ".",
    d34("k5:a"), d34("k5"), d34("k7:c"))
add("muc_phat", "Không chấp hành yêu cầu kiểm tra tải trọng hoặc chuyển tải để trốn trạm cân thì tài xế bị phạt bao nhiêu?",
    "Không chấp hành yêu cầu kiểm tra về trọng tải, tải trọng, khổ giới hạn xe của người thi hành công vụ; chuyển tải "
    "hoặc dùng thủ đoạn khác để trốn tránh việc phát hiện xe chở quá tải, quá khổ bị "
    + fine("40.000.000", "50.000.000", 34, 5, "b") + " và " + tru("10", 34, 7, "d") + ".",
    d34("k5:b"), d34("k5"), d34("k7:d"))
add("quy_tac", "Xe tải chở quá trọng tải ghi trong kiểm định khác gì với xe vượt quá tải trọng cho phép của đường bộ?",
    "Đây là hai hành vi khác nhau. Chở hàng vượt trọng tải (khối lượng hàng chuyên chở) cho phép ghi trong chứng nhận "
    "kiểm định của xe được xử phạt theo Điều 21 " + ND + "; ví dụ vượt trên 10% đến 30% bị phạt tiền từ 800.000 đồng "
    "đến 1.000.000 đồng (điểm a khoản 2 Điều 21, nội dung có hiệu lực từ ngày 15/8/2026). Còn tổng trọng lượng của xe "
    "vượt quá tải trọng cho phép của đường bộ (tức của cầu, đường) được xử phạt theo Điều 34; ví dụ vượt trên 10% đến "
    "20% bị phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng (khoản 2 Điều 34), trừ trường hợp có giấy phép lưu hành còn "
    "giá trị sử dụng.", d21("k2:a", NEW), d34("k2"))

# ===== Điều 8: xe máy chuyên dùng
d8 = lambda s, d="2025-01-01": v(f"d8:{s}", d)  # noqa: E731
M = "người điều khiển xe máy chuyên dùng"
LXMCD = "luat_36_2024:d34:k3@2025-01-01"
add("muc_phat", "Người điều khiển xe máy chuyên dùng không chấp hành biển báo hiệu, vạch kẻ đường bị phạt bao nhiêu?",
    f"Theo Điều 8 {ND}, {M} không chấp hành hiệu lệnh, chỉ dẫn của biển báo hiệu, vạch kẻ đường (trừ các hành vi đã "
    "được quy định riêng ở các khoản khác của Điều 8) bị " + fine("400.000", "600.000", 8, 1, "a") + ".",
    d8("k1:a"), d8("k1"))
add("muc_phat", "Đỗ xe máy chuyên dùng trên vỉa hè trái phép bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} đỗ, để xe ở vỉa hè trái phép bị " + fine("600.000", "800.000", 8, 2, "đ") + ".",
    d8("k2:đ"), d8("k2"))
add("muc_phat", "Xe máy chuyên dùng chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h bị "
    + fine("800.000", "1.000.000", 8, 3, "a") + ".", d8("k3:a"), d8("k3"))
add("muc_phat", "Xe máy chuyên dùng chạy quá tốc độ quy định từ 10 km/h đến 20 km/h bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} chạy quá tốc độ quy định từ 10 km/h đến 20 km/h bị "
    + fine("1.000.000", "2.000.000", 8, 4, "a") + ".", d8("k4:a"), d8("k4"))
add("muc_phat", "Xe máy chuyên dùng chạy quá tốc độ quy định trên 20 km/h bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} chạy quá tốc độ quy định trên 20 km/h bị " + fine("3.000.000", "5.000.000", 8, 6, "a") + ".",
    d8("k6:a"), d8("k6"))
add("doi_thuong", "lái máy xúc ra đường mà có uống bia thì bị phạt bao nhiêu",
    "Máy xúc là xe máy thi công, thuộc nhóm xe máy chuyên dùng (điểm a khoản 3 Điều 34 Luật Trật tự, an toàn giao thông "
    "đường bộ). Theo Điều 8 " + ND + ", mức phạt phụ thuộc nồng độ cồn: chưa vượt quá 50 "
    "miligam/100 mililít máu hoặc chưa vượt quá 0,25 miligam/1 lít khí thở bị phạt tiền từ 3.000.000 đồng đến 5.000.000 "
    "đồng (điểm c khoản 6); vượt quá 50 miligam đến 80 miligam/100 mililít máu hoặc vượt quá 0,25 miligam đến 0,4 "
    "miligam/1 lít khí thở bị phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng (điểm a khoản 7); vượt quá 80 "
    "miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở bị phạt tiền từ 18.000.000 đồng đến 20.000.000 "
    "đồng (điểm a khoản 9).", d8("k6:c"), d8("k7:a"), d8("k9:a"), LXMCD)
add("muc_phat", "Người điều khiển xe máy chuyên dùng không chấp hành yêu cầu kiểm tra nồng độ cồn bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} không chấp hành yêu cầu kiểm tra về nồng độ cồn của người thi hành công vụ bị "
    + fine("18.000.000", "20.000.000", 8, 9, "b") + ".", d8("k9:b"), d8("k9"))
add("muc_phat", "Người điều khiển xe máy chuyên dùng vượt đèn đỏ bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị "
    + fine("6.000.000", "8.000.000", 8, 7, "c") + ".", d8("k7:c"), d8("k7"))
add("muc_phat", "Xe máy chuyên dùng đi ngược chiều của đường một chiều bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} đi ngược chiều của đường một chiều, đi ngược chiều trên đường có biển \u201cCấm đi ngược "
    "chiều\u201d (trừ trường hợp đi ngược chiều trên đường cao tốc và xe ưu tiên đang làm nhiệm vụ khẩn cấp) bị "
    + fine("6.000.000", "8.000.000", 8, 7, "d") + ".", d8("k7:d"), d8("k7"))
add("muc_phat", "Xe máy chuyên dùng có tốc độ thiết kế thấp hơn tốc độ tối thiểu đi vào đường cao tốc thì bị phạt bao nhiêu?",
    "Điều khiển xe máy chuyên dùng có tốc độ thiết kế nhỏ hơn tốc độ tối thiểu quy định đối với đường cao tốc đi vào "
    "đường cao tốc (trừ phương tiện, thiết bị phục vụ quản lý, bảo trì đường cao tốc) bị "
    + fine("14.000.000", "16.000.000", 8, 8, "b") + "; nếu gây tai nạn giao thông thì bị phạt tiền từ 18.000.000 đồng "
    "đến 20.000.000 đồng (điểm e khoản 9 Điều 8).", d8("k8:b"), d8("k8"), d8("k9:e"))
add("tinh_huong", "Tôi lái xe lu gây tai nạn rồi bỏ đi, không dừng lại trợ giúp người bị nạn. Tôi bị phạt bao nhiêu?",
    "Xe lu là xe máy thi công, thuộc nhóm xe máy chuyên dùng (điểm a khoản 3 Điều 34 Luật Trật tự, an toàn giao thông "
    "đường bộ). Người điều khiển gây tai nạn giao thông mà không dừng ngay phương tiện, không "
    "giữ nguyên hiện trường, không trợ giúp người bị nạn, không ở lại hiện trường hoặc không đến trình báo ngay với cơ "
    "quan công an, Ủy ban nhân dân nơi gần nhất bị " + fine("14.000.000", "16.000.000", 8, 8, "c") + ".",
    d8("k8:c"), d8("k8"), LXMCD)
add("muc_phat", "Lùi xe máy chuyên dùng hoặc quay đầu trên đường cao tốc bị phạt bao nhiêu?",
    f"{M[0].upper() + M[1:]} lùi xe, đi ngược chiều hoặc quay đầu xe trên đường cao tốc bị "
    + fine("18.000.000", "20.000.000", 8, 9, "đ") + ".", d8("k9:đ"), d8("k9"))
add("muc_phat", "Xe máy chuyên dùng chuyển hướng không nhường đường cho người đi bộ qua đường tại vạch kẻ đường bị phạt "
    "bao nhiêu?",
    f"{M[0].upper() + M[1:]} chuyển hướng không nhường quyền đi trước cho người đi bộ, xe lăn của người khuyết tật qua "
    "đường tại nơi có vạch kẻ đường dành cho người đi bộ bị " + fine("2.000.000", "3.000.000", 8, 5, "đ") + ".",
    d8("k5:đ"), d8("k5"))

out = ROOT / "data/train/drafts/xu_phat_06.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
