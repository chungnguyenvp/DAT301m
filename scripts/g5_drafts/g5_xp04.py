"""Đợt 1d G5: Xử phạt, Điều 14 (điều kiện xe máy), 18 (điều kiện người lái), 33 (hành khách), 35 (đua xe) NĐ 168/2024.
Ghi data/train/drafts/xu_phat_04.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
NEW = "2026-08-15"
S = []
START = 172


def v(s, d="2025-01-01"):
    return f"nd_168_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, dieu, k, diem=None):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều {dieu} {ND}"
    return f"phạt tiền từ {lo} đồng đến {hi} đồng ({where})"


# ===== Điều 14: điều kiện của xe mô tô, xe gắn máy
d14 = lambda s, d="2025-01-01": v(f"d14:{s}", d)  # noqa: E731
P2, P6 = d14("k8:a"), d14("k8:b")
FIX = d14("k6:a", NEW)
add("muc_phat", "Xe máy không có gương chiếu hậu bên trái thì bị phạt bao nhiêu?",
    "Điều khiển xe không có gương chiếu hậu bên trái người điều khiển, hoặc có nhưng không có tác dụng, bị "
    + fine("400.000", "600.000", 14, 1, "a") + "; người vi phạm còn buộc thay thế thiết bị đủ tiêu chuẩn an toàn kỹ "
    "thuật hoặc khôi phục tính năng kỹ thuật của thiết bị (điểm a khoản 6 Điều 14).", d14("k1:a"), d14("k1"), FIX)
add("doi_thuong", "xe máy ko có gương thì bị phạt k ạ",
    "Có. Xe mô tô, xe gắn máy không có gương chiếu hậu bên trái người điều khiển (hoặc có nhưng không có tác dụng) bị "
    + fine("400.000", "600.000", 14, 1, "a") + ".", d14("k1:a"), d14("k1"))
add("muc_phat", "Xe máy không có đèn xi nhan hoặc đèn xi nhan hỏng bị phạt bao nhiêu?",
    "Điều khiển xe không có đèn tín hiệu, hoặc có nhưng không có tác dụng, bị " + fine("400.000", "600.000", 14, 1, "b")
    + ".", d14("k1:b"), d14("k1"))
add("muc_phat", "Xe máy phanh không ăn (hệ thống hãm không có tác dụng) bị phạt bao nhiêu?",
    "Điều khiển xe không có hệ thống hãm, hoặc có nhưng không có tác dụng, không bảo đảm tiêu chuẩn kỹ thuật, bị "
    + fine("400.000", "600.000", 14, 1, "d") + ".", d14("k1:d"), d14("k1"))
add("muc_phat", "Lắp đèn chiếu sáng hướng về phía sau xe máy có bị phạt không?",
    "Có. Điều khiển xe lắp đèn chiếu sáng về phía sau xe bị " + fine("400.000", "600.000", 14, 1, "đ") + ".",
    d14("k1:đ"), d14("k1"))
add("muc_phat", "Đi xe máy không có chứng nhận đăng ký xe (cà vẹt) bị xử phạt thế nào?",
    "Điều khiển xe không có chứng nhận đăng ký xe, hoặc sử dụng chứng nhận đăng ký đã hết hạn, hết hiệu lực, bị "
    + fine("2.000.000", "3.000.000", 14, 2, "a") + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 8 Điều 14). "
    "Nếu không chứng minh được nguồn gốc xuất xứ của phương tiện thì còn bị tịch thu phương tiện (điểm b khoản 5 Điều 14).",
    d14("k2:a"), d14("k2"), P2, d14("k5:b"))
add("muc_phat", "Dùng chứng nhận đăng ký xe máy bị tẩy xóa thì bị xử phạt thế nào?",
    "Sử dụng chứng nhận đăng ký xe bị tẩy xóa bị " + fine("2.000.000", "3.000.000", 14, 2, "b")
    + ", bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 8 Điều 14) và buộc nộp lại chứng nhận đăng ký xe đã bị tẩy "
    "xóa (điểm b khoản 6 Điều 14).", d14("k2:b"), d14("k2"), P2, d14("k6:b"))
add("muc_phat", "Xe máy đăng ký tạm thời chạy quá thời hạn hoặc quá tuyến đường cho phép bị phạt bao nhiêu?",
    "Điều khiển xe đăng ký tạm thời hoạt động quá phạm vi, tuyến đường, thời hạn cho phép bị "
    + fine("2.000.000", "3.000.000", 14, 2, "c") + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 8 Điều 14).",
    d14("k2:c"), d14("k2"), P2)
add("tinh_huong", "Tôi thay ống xả xe máy làm tiếng nổ rất to, không đạt quy chuẩn tiếng ồn thì bị phạt gì?",
    "Điều khiển xe không có bộ phận giảm thanh, giảm khói, hoặc có nhưng không bảo đảm quy chuẩn môi trường về khí thải, "
    "tiếng ồn, bị " + fine("2.000.000", "3.000.000", 14, 2, "d") + " và buộc thay thế thiết bị đủ tiêu chuẩn hoặc khôi "
    "phục tính năng kỹ thuật của thiết bị (điểm a khoản 6 Điều 14).", d14("k2:d"), d14("k2"), FIX)
add("muc_phat", "Xe máy lắp còi không đúng quy chuẩn kỹ thuật (còi quá to) bị phạt bao nhiêu?",
    "Sử dụng còi không đúng quy chuẩn kỹ thuật cho từng loại xe bị " + fine("2.000.000", "3.000.000", 14, 2, "đ")
    + " và buộc thay thế thiết bị đủ tiêu chuẩn hoặc khôi phục tính năng kỹ thuật (điểm a khoản 6 Điều 14).",
    d14("k2:đ"), d14("k2"), FIX)
add("muc_phat", "Đi xe máy không gắn biển số bị phạt bao nhiêu?",
    "Điều khiển xe không gắn biển số (đối với loại xe phải gắn biển số) bị " + fine("4.000.000", "6.000.000", 14, 3, "a")
    + " và bị trừ điểm giấy phép lái xe 06 điểm (điểm b khoản 8 Điều 14).", d14("k3:a"), d14("k3"), P6)
add("muc_phat", "Gắn biển số giả (không do cơ quan có thẩm quyền cấp) cho xe máy bị xử phạt thế nào?",
    "Gắn biển số không đúng với chứng nhận đăng ký xe hoặc không do cơ quan có thẩm quyền cấp bị "
    + fine("4.000.000", "6.000.000", 14, 3, "a") + ", bị trừ điểm giấy phép lái xe 06 điểm (điểm b khoản 8 Điều 14) và bị "
    "tịch thu biển số xe (điểm a khoản 5 Điều 14).", d14("k3:a"), d14("k3"), P6, d14("k5:a"))
add("muc_phat", "Bẻ cong hoặc dán che biển số xe máy để tránh camera bị phạt bao nhiêu?",
    "Gắn biển số bị bẻ cong, che lấp, sơn, dán lên chữ, số, hoặc sử dụng chất liệu, thiết bị làm thay đổi khả năng nhận "
    "diện thông tin biển số bị " + fine("4.000.000", "6.000.000", 14, 3, "b")
    + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026; người vi phạm còn bị trừ điểm giấy phép lái xe 06 điểm "
    "(điểm b khoản 8 Điều 14).", d14("k3:b", NEW), d14("k3"), P6)
add("doi_thuong", "biển số xe máy bị cong mép thì có bị phạt k",
    "Có. Gắn biển số bị bẻ cong, che lấp hoặc làm thay đổi chữ, số, hình dạng, kích thước của biển số bị "
    + fine("4.000.000", "6.000.000", 14, 3, "b") + " và bị trừ điểm giấy phép lái xe 06 điểm (điểm b khoản 8 Điều 14).",
    d14("k3:b", NEW), d14("k3"), P6)
add("muc_phat", "Điều khiển xe máy tự chế, lắp ráp trái quy định tham gia giao thông bị xử lý thế nào?",
    "Điều khiển loại xe sản xuất, lắp ráp trái quy định tham gia giao thông bị tịch thu phương tiện (khoản 4 Điều 14 "
    + ND + ").", d14("k4"))

# ===== Điều 18: điều kiện của người điều khiển
d18 = lambda s, d="2025-01-01": v(f"d18:{s}", d)  # noqa: E731
add("tinh_huong", "Con tôi 15 tuổi lén chạy xe máy ra đường thì bị xử phạt thế nào?",
    "Người từ đủ 14 tuổi đến dưới 16 tuổi điều khiển xe mô tô, xe gắn máy (hoặc xe ô tô) bị phạt cảnh cáo (khoản 1 "
    "Điều 18 " + ND + ").", d18("k1"))
add("muc_phat", "Người 17 tuổi lái ô tô bị phạt bao nhiêu?",
    "Người từ đủ 16 tuổi đến dưới 18 tuổi điều khiển xe ô tô, xe chở người bốn bánh có gắn động cơ, xe chở hàng bốn bánh "
    "có gắn động cơ bị " + fine("4.000.000", "6.000.000", 18, 6) + ".", d18("k6"))
add("muc_phat", "Người 17 tuổi điều khiển xe mô tô bị phạt bao nhiêu?",
    "Người từ đủ 16 tuổi đến dưới 18 tuổi điều khiển xe mô tô và các loại xe tương tự xe mô tô bị "
    + fine("400.000", "600.000", 18, 4, "a") + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026.",
    d18("k4:a", NEW), d18("k4"))
add("muc_phat", "Đi xe máy 110 cc mà không có giấy phép lái xe bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô hai bánh có dung tích xi-lanh đến 125 cm3 (hoặc công suất động cơ điện đến 11 kW) không có "
    "giấy phép lái xe bị " + fine("2.000.000", "4.000.000", 18, 5, "a") + ".", d18("k5:a"), d18("k5"))
add("doi_thuong", "chưa có bằng lái mà chạy xe máy 110 phân khối thì phạt bn",
    "Không có giấy phép lái xe khi điều khiển xe mô tô hai bánh có dung tích xi-lanh đến 125 cm3 bị "
    + fine("2.000.000", "4.000.000", 18, 5, "a") + ".", d18("k5:a"), d18("k5"))
add("muc_phat", "Lái xe mô tô 150 cc mà không có giấy phép lái xe bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô hai bánh có dung tích xi-lanh trên 125 cm3 (hoặc công suất động cơ điện trên 11 kW), xe "
    "mô tô ba bánh không có giấy phép lái xe bị " + fine("6.000.000", "8.000.000", 18, 7, "b") + ".",
    d18("k7:b"), d18("k7"))
add("tinh_huong", "Tôi có bằng lái hạng A1 nhưng điều khiển xe mô tô 175 cc thì có bị phạt không?",
    "Có. Người điều khiển xe mô tô hai bánh có dung tích xi-lanh trên 125 cm3 mà có giấy phép lái xe nhưng không phù hợp "
    "với loại xe đang điều khiển bị " + fine("6.000.000", "8.000.000", 18, 7, "a") + ".", d18("k7:a"), d18("k7"))
add("muc_phat", "Lái ô tô mà không có giấy phép lái xe bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô không có giấy phép lái xe, hoặc sử dụng giấy phép lái xe đã bị trừ hết điểm, không do cơ "
    "quan có thẩm quyền cấp, bị tẩy xóa hoặc không còn hiệu lực, bị " + fine("18.000.000", "20.000.000", 18, 9, "b") + ".",
    d18("k9:b"), d18("k9"))
add("tinh_huong", "Bằng lái ô tô của tôi hết hạn được 3 tháng mà vẫn lái xe thì bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô có giấy phép lái xe nhưng đã hết hạn sử dụng dưới 01 năm bị "
    + fine("8.000.000", "10.000.000", 18, 8, "a") + ".", d18("k8:a"), d18("k8"))
add("muc_phat", "Lái ô tô với giấy phép lái xe đã hết hạn từ 1 năm trở lên bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô có giấy phép lái xe nhưng đã hết hạn sử dụng từ 01 năm trở lên, hoặc giấy phép lái xe không "
    "phù hợp với loại xe đang điều khiển, bị " + fine("18.000.000", "20.000.000", 18, 9, "a") + ".",
    d18("k9:a"), d18("k9"))
add("tinh_huong", "Giấy phép lái xe ô tô của tôi đã bị trừ hết điểm, nếu vẫn lái xe thì bị phạt thế nào?",
    "Sử dụng giấy phép lái xe đã bị trừ hết điểm khi điều khiển xe ô tô bị xử phạt như không có giấy phép lái xe: "
    + fine("18.000.000", "20.000.000", 18, 9, "b") + ".", d18("k9:b"), d18("k9"))
add("muc_phat", "Xe máy không có bảo hiểm bắt buộc trách nhiệm dân sự còn hiệu lực bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô, xe gắn máy không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới "
    "còn hiệu lực bị " + fine("200.000", "300.000", 18, 2, "b") + ".", d18("k2:b"), d18("k2"))
add("muc_phat", "Ô tô không có bảo hiểm bắt buộc trách nhiệm dân sự còn hiệu lực bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới còn hiệu lực bị "
    + fine("400.000", "600.000", 18, 4, "c") + ".", d18("k4:c"), d18("k4"))
add("muc_phat", "Lái ô tô dùng giấy phép lái xe không hợp lệ (số phôi không trùng số phôi mới nhất trong hệ thống) bị xử lý thế nào?",
    "Sử dụng giấy phép lái xe không hợp lệ (số phôi ghi ở mặt sau không trùng với số phôi được cấp mới nhất trong hệ thống "
    "thông tin quản lý giấy phép lái xe) khi điều khiển xe ô tô bị " + fine("8.000.000", "10.000.000", 18, 8, "c")
    + ", bị thu hồi giấy phép lái xe không hợp lệ (khoản 11 Điều 18) và bị trừ điểm giấy phép lái xe được cấp mới nhất "
    "trong hệ thống thông tin quản lý giấy phép lái xe 02 điểm (khoản 12 Điều 18).",
    d18("k8:c"), d18("k8"), d18("k11"), d18("k12"))
add("muc_phat", "Người nước ngoài lái ô tô ở Việt Nam bằng giấy phép lái xe quốc tế nhưng không mang theo giấy phép lái xe quốc gia thì bị phạt bao nhiêu?",
    "Có giấy phép lái xe quốc tế do các nước tham gia Công ước của Liên hợp quốc về Giao thông đường bộ năm 1968 cấp "
    "(trừ giấy phép lái xe quốc tế do Việt Nam cấp) nhưng không mang theo giấy phép lái xe quốc gia phù hợp với loại xe "
    "khi điều khiển ô tô bị " + fine("8.000.000", "10.000.000", 18, 8, "b") + ".", d18("k8:b"), d18("k8"))
add("muc_phat", "Tài xế ô tô kinh doanh vận tải không mang theo giấy phép lái xe bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô kinh doanh vận tải không mang theo giấy phép lái xe bị "
    + fine("300.000", "400.000", 18, 3, "a") + ".", d18("k3:a"), d18("k3"))
add("tinh_huong", "Tôi chạy xe ôm công nghệ bằng xe máy mà quên mang giấy phép lái xe thì bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô kinh doanh vận tải không mang theo giấy phép lái xe bị "
    + fine("200.000", "300.000", 18, 2, "d") + ".", d18("k2:d"), d18("k2"))
add("muc_phat", "Ô tô kinh doanh vận tải không mang theo chứng nhận kiểm định bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô kinh doanh vận tải không mang theo chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi "
    "trường (đối với loại xe phải kiểm định) bị " + fine("300.000", "400.000", 18, 3, "c")
    + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026.", d18("k3:c", NEW), d18("k3"))
add("muc_phat", "Ô tô kinh doanh vận tải không mang theo chứng nhận đăng ký xe bị phạt bao nhiêu?",
    "Người điều khiển xe ô tô kinh doanh vận tải không mang theo chứng nhận đăng ký xe bị "
    + fine("300.000", "400.000", 18, 3, "b") + ".", d18("k3:b"), d18("k3"))

# ===== Điều 33: hành khách
d33 = lambda s: v(f"d33:{s}")  # noqa: E731
add("muc_phat", "Hành khách gây mất trật tự trên xe khách bị phạt bao nhiêu?",
    "Hành khách gây mất trật tự trên xe, hoặc không chấp hành hướng dẫn của lái xe, nhân viên phục vụ về bảo đảm trật tự, "
    "an toàn giao thông, bị " + fine("100.000", "200.000", 33, 1, "b") + ".", d33("k1:b"), d33("k1"))
add("muc_phat", "Hành khách mang xăng, chất dễ cháy nổ lên xe khách bị xử phạt thế nào?",
    "Mang hóa chất độc hại, chất dễ cháy, nổ, hàng nguy hiểm hoặc hàng cấm lưu thông trên xe chở khách bị "
    + fine("1.000.000", "2.000.000", 33, 2, "a") + " và bị tịch thu các hàng hóa đó (khoản 4 Điều 33).",
    d33("k2:a"), d33("k2"), d33("k4"))
add("muc_phat", "Hành khách tự ý mở cửa xe khách khi xe đang chạy bị phạt bao nhiêu?",
    "Tự ý mở cửa xe, đu bám vào thành xe, đứng, ngồi, nằm trên mui xe, nóc xe, trong khoang chở hành lý hoặc có hành vi "
    "khác không bảo đảm an toàn khi xe đang chạy bị " + fine("1.000.000", "2.000.000", 33, 2, "b") + ".",
    d33("k2:b"), d33("k2"))
add("muc_phat", "Hành khách đe dọa, hành hung tài xế xe khách bị phạt bao nhiêu?",
    "Hành vi đe dọa, xâm phạm sức khỏe của người khác đi trên xe, lái xe, nhân viên phục vụ trên xe bị "
    + fine("2.000.000", "3.000.000", 33, 3) + ".", d33("k3"))

# ===== Điều 35: đua xe
d35 = lambda s: v(f"d35:{s}")  # noqa: E731
add("muc_phat", "Tụ tập cổ vũ đua xe trái phép bị phạt bao nhiêu?",
    "Tụ tập để cổ vũ, giúp sức, xúi giục hành vi chạy quá tốc độ, lạng lách, đánh võng, đuổi nhau trên đường hoặc đua xe "
    "trái phép bị " + fine("1.000.000", "2.000.000", 35, 1) + ".", d35("k1"))
add("muc_phat", "Tổ chức đua xe trái phép bị phạt bao nhiêu?",
    "Tổ chức đua xe trái phép bị phạt tiền từ 40.000.000 đồng đến 50.000.000 đồng đối với cá nhân, từ 80.000.000 đồng đến "
    "100.000.000 đồng đối với tổ chức (khoản 2 Điều 35 " + ND + ").", d35("k2"))
add("muc_phat", "Đua xe mô tô hoặc ô tô trái phép trên đường bị xử phạt thế nào?",
    "Đua xe ô tô, mô tô trái phép trên đường giao thông bị tịch thu phương tiện (điểm b khoản 3 Điều 35 " + ND
    + ") và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (khoản 4 Điều 35).",
    d35("k3:b"), d35("k3"), d35("k4"))
add("muc_phat", "Đua xe đạp hoặc xe gắn máy trái phép trên đường bị xử lý thế nào?",
    "Đua xe gắn máy, xe đạp máy, xe đạp trái phép trên đường giao thông bị tịch thu phương tiện (điểm a khoản 3 Điều 35 "
    + ND + ").", d35("k3:a"), d35("k3"))

out = ROOT / "data" / "train" / "drafts" / "xu_phat_04.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
print(len(S), "mẫu ->", out)
