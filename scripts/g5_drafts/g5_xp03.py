"""Đợt 1c G5: Xử phạt, Điều 9 (xe đạp, xe thô sơ), Điều 10 (người đi bộ), Điều 12 (vi phạm khác) NĐ 168/2024.
Ghi data/train/drafts/xu_phat_03.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
S = []
START = 127


def v(s, d="2025-01-01"):
    return f"nd_168_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, dieu, k, diem=None, ai=""):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều {dieu} {ND}"
    return f"phạt tiền từ {lo} đồng đến {hi} đồng{ai} ({where})"


# ===== Điều 9: xe đạp, xe đạp máy, xe thô sơ (không có trừ điểm, tước GPLX)
d9 = lambda s: v(f"d9:{s}")  # noqa: E731
add("muc_phat", "Đi xe đạp vượt đèn đỏ bị phạt bao nhiêu?",
    "Người điều khiển xe đạp không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị "
    + fine("150.000", "250.000", 9, 2, "đ") + ".", d9("k2:đ"), d9("k2"))
add("doi_thuong", "đạp xe mà vừa đi vừa nghe điện thoại có bị phạt ko",
    "Có. Người điều khiển xe đạp, xe đạp máy dùng tay cầm và sử dụng điện thoại hoặc thiết bị điện tử khác bị "
    + fine("100.000", "200.000", 9, 1, "h") + ".", d9("k1:h"), d9("k1"))
add("muc_phat", "Đi xe đạp dàn hàng ngang ba xe trên đường bị phạt bao nhiêu?",
    "Điều khiển xe đạp, xe đạp máy đi dàn hàng ngang từ 03 xe trở lên bị " + fine("100.000", "200.000", 9, 1, "g")
    + ". Với xe thô sơ khác, đi dàn hàng ngang từ 02 xe trở lên đã bị phạt.", d9("k1:g"), d9("k1"))
add("muc_phat", "Đi xe đạp buông cả hai tay bị phạt bao nhiêu?",
    "Điều khiển xe đạp, xe đạp máy buông cả hai tay, dùng chân điều khiển xe, hoặc chuyển hướng đột ngột trước đầu xe cơ "
    "giới đang chạy bị " + fine("150.000", "250.000", 9, 2, "a") + ".", d9("k2:a"), d9("k2"))
add("muc_phat", "Đi xe đạp lạng lách, đánh võng hoặc đuổi nhau trên đường bị phạt bao nhiêu?",
    "Điều khiển xe lạng lách, đánh võng, đuổi nhau trên đường bị " + fine("300.000", "400.000", 9, 3, "a") + ".",
    d9("k3:a"), d9("k3"))
add("muc_phat", "Đi xe đạp ngược chiều trên đường một chiều bị phạt bao nhiêu?",
    "Đi ngược chiều của đường một chiều hoặc đường có biển “Cấm đi ngược chiều”, hoặc đi vào khu vực cấm, đường có biển "
    "cấm đi vào đối với loại phương tiện đang điều khiển bị " + fine("300.000", "400.000", 9, 3, "c") + ".",
    d9("k3:c"), d9("k3"))
add("muc_phat", "Người đi xe đạp uống rượu bia có bị phạt không? Mức thấp nhất là bao nhiêu?",
    "Có. Người điều khiển xe đạp, xe đạp máy, xe thô sơ có nồng độ cồn nhưng chưa vượt quá 50 miligam/100 mililít máu "
    "hoặc chưa vượt quá 0,25 miligam/1 lít khí thở bị " + fine("100.000", "200.000", 9, 1, "p")
    + ". Mức cao hơn: vượt quá 0,25 đến 0,4 miligam/1 lít khí thở bị phạt từ 300.000 đồng đến 400.000 đồng (điểm d khoản 3 "
    "Điều 9); vượt quá 0,4 miligam/1 lít khí thở bị phạt từ 400.000 đồng đến 600.000 đồng (điểm b khoản 4 Điều 9).",
    d9("k1:p"), d9("k1"), d9("k3:d"), d9("k3"), d9("k4:b"), d9("k4"))
add("muc_phat", "Người đi xe đạp không chấp hành yêu cầu kiểm tra nồng độ cồn bị phạt bao nhiêu?",
    "Không chấp hành yêu cầu kiểm tra về nồng độ cồn của người thi hành công vụ bị " + fine("400.000", "600.000", 9, 4, "c")
    + ".", d9("k4:c"), d9("k4"))
add("muc_phat", "Đi xe đạp máy (xe đạp điện) không đội mũ bảo hiểm có bị phạt không?",
    "Có. Người điều khiển xe đạp máy không đội “mũ bảo hiểm cho người đi mô tô, xe máy” hoặc đội nhưng không cài quai "
    "đúng quy cách bị " + fine("400.000", "600.000", 9, 4, "d") + ".", d9("k4:d"), d9("k4"))
add("tinh_huong", "Tôi chở con 8 tuổi ngồi sau xe đạp máy nhưng cháu không đội mũ bảo hiểm thì có bị phạt không?",
    "Có. Chở người ngồi trên xe đạp máy không đội mũ bảo hiểm (hoặc đội không cài quai đúng quy cách) bị "
    + fine("400.000", "600.000", 9, 4, "đ")
    + ". Ngoại lệ chỉ áp dụng khi chở người bệnh đi cấp cứu, trẻ em dưới 06 tuổi hoặc áp giải người vi phạm pháp luật; "
    "trẻ 8 tuổi không thuộc ngoại lệ này.", d9("k4:đ"), d9("k4"))
add("muc_phat", "Đi xe đạp vào đường cao tốc bị phạt bao nhiêu?",
    "Người điều khiển xe đạp, xe đạp máy, xe thô sơ đi vào đường cao tốc (trừ phương tiện phục vụ quản lý, bảo trì đường "
    "cao tốc) bị " + fine("800.000", "1.200.000", 9, 5) + ".", d9("k5"))
add("muc_phat", "Người đi xe đạp gây tai nạn rồi bỏ đi, không trình báo thì bị phạt bao nhiêu?",
    "Gây tai nạn giao thông không dừng ngay phương tiện, không giữ nguyên hiện trường, không trợ giúp người bị nạn, không "
    "ở lại hiện trường hoặc không đến trình báo ngay với cơ quan công an, Ủy ban nhân dân nơi gần nhất bị "
    + fine("400.000", "600.000", 9, 4, "a") + ".", d9("k4:a"), d9("k4"))
add("muc_phat", "Xe đạp chở quá số người quy định bị phạt bao nhiêu?",
    "Xe đạp, xe đạp máy, xe xích lô chở quá số người quy định (trừ trường hợp chở người bệnh đi cấp cứu) bị "
    + fine("100.000", "200.000", 9, 1, "o") + ".", d9("k1:o"), d9("k1"))
add("muc_phat", "Xe ba gác, xe thô sơ đi buổi tối không có đèn hoặc báo hiệu bị phạt bao nhiêu?",
    "Điều khiển xe thô sơ trong thời gian từ 18 giờ ngày hôm trước đến 06 giờ ngày hôm sau không sử dụng đèn hoặc không "
    "có báo hiệu ở phía trước và phía sau xe bị " + fine("100.000", "200.000", 9, 1, "i") + ".", d9("k1:i"), d9("k1"))
add("muc_phat", "Dùng xe đẩy làm quầy hàng lưu động trên đường gây cản trở giao thông bị phạt bao nhiêu?",
    "Dùng xe đẩy làm quầy hàng lưu động trên đường gây cản trở giao thông bị " + fine("100.000", "200.000", 9, 1, "m")
    + ".", d9("k1:m"), d9("k1"))
add("tinh_huong", "Tôi đạp xe mà kéo theo một chiếc xe đạp hỏng của bạn thì có bị phạt không?",
    "Có. Người đang điều khiển xe đạp bám, kéo, đẩy xe khác, vật khác, mang vác vật cồng kềnh, hoặc điều khiển xe kéo "
    "theo xe khác, vật khác bị " + fine("150.000", "250.000", 9, 2, "c") + ".", d9("k2:c"), d9("k2"))
add("quy_tac", "Đi xe đạp chuyển hướng mà không ra tín hiệu báo trước có bị phạt không?",
    "Có. Dừng xe đột ngột hoặc chuyển hướng không báo hiệu trước khi điều khiển xe đạp, xe thô sơ bị "
    + fine("100.000", "200.000", 9, 1, "b") + ".", d9("k1:b"), d9("k1"))

# ===== Điều 10: người đi bộ
d10 = lambda s: v(f"d10:{s}")  # noqa: E731
add("muc_phat", "Người đi bộ vượt qua dải phân cách để sang đường bị phạt bao nhiêu?",
    "Người đi bộ vượt qua dải phân cách, đi qua đường không đúng nơi quy định, không đi đúng phần đường quy định bị "
    + fine("150.000", "250.000", 10, 1, "a") + ".", d10("k1:a"), d10("k1"))
add("muc_phat", "Người đi bộ sang đường khi đèn dành cho người đi bộ đang đỏ bị phạt bao nhiêu?",
    "Người đi bộ không chấp hành hiệu lệnh hoặc chỉ dẫn của đèn tín hiệu, biển báo hiệu, vạch kẻ đường bị "
    + fine("150.000", "250.000", 10, 1, "b") + ".", d10("k1:b"), d10("k1"))
add("muc_phat", "Đi bộ vào đường cao tốc bị phạt bao nhiêu?",
    "Người đi bộ đi vào đường cao tốc (trừ người phục vụ việc quản lý, bảo trì đường cao tốc) bị "
    + fine("400.000", "600.000", 10, 2, "a") + ".", d10("k2:a"), d10("k2"))
add("muc_phat", "Người đi bộ đu bám vào xe đang chạy bị phạt bao nhiêu?",
    "Người đi bộ đu, bám vào phương tiện giao thông đang chạy bị " + fine("400.000", "600.000", 10, 2, "c") + ".",
    d10("k2:c"), d10("k2"))
add("doi_thuong", "đi bộ qua đường ko đúng chỗ có bị phạt ko",
    "Có. Người đi bộ đi qua đường không đúng nơi quy định, hoặc qua đường không có tín hiệu bằng tay theo quy định, bị "
    + fine("150.000", "250.000", 10, 1, "a") + ".", d10("k1:a"), d10("k1"))
add("muc_phat", "Người đi bộ mang vác vật cồng kềnh gây cản trở giao thông bị phạt bao nhiêu?",
    "Người đi bộ mang, vác vật cồng kềnh gây cản trở giao thông bị " + fine("400.000", "600.000", 10, 2, "b") + ".",
    d10("k2:b"), d10("k2"))
add("muc_phat", "Người đi bộ không chấp hành hiệu lệnh của cảnh sát giao thông bị phạt bao nhiêu?",
    "Người đi bộ không chấp hành hiệu lệnh, hướng dẫn của người điều khiển giao thông hoặc người kiểm soát giao thông bị "
    + fine("150.000", "250.000", 10, 1, "c") + ".", d10("k1:c"), d10("k1"))

# ===== Điều 12: vi phạm khác
d12 = lambda s: v(f"d12:{s}")  # noqa: E731
add("tinh_huong", "Người ngồi sau xe máy không đội mũ bảo hiểm thì ai bị phạt, phạt bao nhiêu?",
    "Cả hai người đều bị phạt. Người ngồi sau không đội mũ bảo hiểm (hoặc đội không cài quai đúng quy cách) bị "
    + fine("400.000", "600.000", 12, 5, "b")
    + "; người điều khiển xe chở người không đội mũ bảo hiểm cũng bị phạt tiền từ 400.000 đồng đến 600.000 đồng (điểm i "
    "khoản 2 Điều 7), trừ khi chở người bệnh đi cấp cứu, trẻ em dưới 06 tuổi hoặc áp giải người vi phạm pháp luật.",
    d12("k5:b"), d12("k5"), v("d7:k2:i"), v("d7:k2"))
add("tinh_huong", "Người ngồi ghế sau ô tô không thắt dây an toàn thì bị phạt bao nhiêu?",
    "Người được chở trên xe ô tô không thắt dây đai an toàn (tại vị trí có trang bị dây đai an toàn) khi xe đang chạy bị "
    + fine("350.000", "400.000", 12, 4)
    + ". Người lái chở người không thắt dây đai an toàn cũng bị phạt tiền từ 800.000 đồng đến 1.000.000 đồng (điểm l "
    "khoản 3 Điều 6).", d12("k4"), v("d6:k3:l"), v("d6:k3"))
add("muc_phat", "Người ngồi sau xe máy cầm ô (dù) bị phạt bao nhiêu?",
    "Người được chở trên xe mô tô, xe gắn máy sử dụng ô (dù) bị " + fine("200.000", "250.000", 12, 2, "d") + ".",
    d12("k2:d"), d12("k2"))
add("muc_phat", "Người ngồi sau xe đạp cầm ô (dù) bị phạt bao nhiêu?",
    "Người được chở trên xe đạp, xe đạp máy sử dụng ô (dù) bị " + fine("100.000", "200.000", 12, 1) + ".", d12("k1"))
add("muc_phat", "Đá bóng trên đường hoặc trượt pa-tanh trên phần đường xe chạy bị phạt bao nhiêu?",
    "Đá bóng, đá cầu, chơi cầu lông hoặc các hoạt động thể thao khác trái phép trên đường bộ, hoặc sử dụng bàn trượt, "
    "pa-tanh, thiết bị tương tự trên phần đường xe chạy bị " + fine("200.000", "250.000", 12, 2, "b", " đối với cá nhân")
    + ".", d12("k2:b"), d12("k2"))
add("muc_phat", "Phơi lúa, rơm rạ trên đường bộ bị phạt bao nhiêu?",
    "Phơi thóc, lúa, rơm, rạ, nông, lâm, hải sản trên đường bộ, hoặc đặt máy tuốt lúa trên đường bộ bị "
    + fine("200.000", "250.000", 12, 2, "g", " đối với cá nhân") + ".", d12("k2:g"), d12("k2"))
add("muc_phat", "Thả flycam (tàu bay không người lái) sát mặt đường gây nguy hiểm cho xe cộ bị phạt bao nhiêu?",
    "Điều khiển vật thể bay, tàu bay không người lái, phương tiện bay siêu nhẹ trong phạm vi khổ giới hạn đường bộ gây cản "
    "trở hoặc nguy cơ mất an toàn cho người, phương tiện tham gia giao thông (trừ loại được cấp phép bay) bị "
    + fine("200.000", "250.000", 12, 2, "c", " đối với cá nhân") + ".", d12("k2:c"), d12("k2"))
add("muc_phat", "Để cây, biển quảng cáo che khuất biển báo hiệu đường bộ bị phạt bao nhiêu?",
    "Để vật che khuất biển báo hiệu đường bộ, đèn tín hiệu giao thông bị phạt tiền từ 250.000 đồng đến 350.000 đồng đối "
    "với cá nhân, từ 500.000 đồng đến 700.000 đồng đối với tổ chức (khoản 3 Điều 12 " + ND + "), và buộc phá dỡ các vật "
    "che khuất (điểm a khoản 16 Điều 12).", d12("k3"), d12("k16:a"))
add("muc_phat", "Có điều kiện mà cố ý không cứu giúp người bị tai nạn giao thông thì bị phạt bao nhiêu?",
    "Khi có điều kiện mà cố ý không cứu giúp người bị tai nạn giao thông đường bộ bị "
    + fine("500.000", "1.000.000", 12, 6, "a", " đối với cá nhân") + ".", d12("k6:a"), d12("k6"))
add("muc_phat", "Ném đá vào xe đang chạy trên đường bị phạt bao nhiêu?",
    "Ném gạch, đất, đá, cát hoặc vật thể khác vào người, phương tiện đang tham gia giao thông trên đường bộ bị "
    + fine("500.000", "1.000.000", 12, 6, "c", " đối với cá nhân") + ".", d12("k6:c"), d12("k6"))
add("muc_phat", "Bày bán hàng ăn uống trên vỉa hè trái phép bị phạt bao nhiêu?",
    "Sử dụng trái phép lòng đường, vỉa hè để kinh doanh dịch vụ ăn uống, bày, bán hàng hóa, họp chợ, sửa chữa phương tiện, "
    "rửa xe hoặc đặt, treo biển hiệu, biển quảng cáo bị phạt tiền từ 2.000.000 đồng đến 3.000.000 đồng đối với cá nhân, "
    "từ 4.000.000 đồng đến 6.000.000 đồng đối với tổ chức (khoản 7 Điều 12 " + ND + ").", d12("k7"))
add("doi_thuong", "mở tiệm rửa xe trên vỉa hè có bị phạt k",
    "Có. Sử dụng trái phép lòng đường, vỉa hè để rửa xe bị phạt tiền từ 2.000.000 đồng đến 3.000.000 đồng đối với cá "
    "nhân, từ 4.000.000 đồng đến 6.000.000 đồng đối với tổ chức (khoản 7 Điều 12 " + ND + ").", d12("k7"))
add("muc_phat", "Cố ý xóa dấu vết hiện trường vụ tai nạn giao thông bị phạt bao nhiêu?",
    "Cố ý thay đổi, xóa dấu vết hiện trường vụ tai nạn giao thông bị phạt tiền từ 2.000.000 đồng đến 4.000.000 đồng đối "
    "với cá nhân, từ 4.000.000 đồng đến 8.000.000 đồng đối với tổ chức (khoản 8 Điều 12 " + ND + ").", d12("k8"))
add("muc_phat", "Không chấp hành yêu cầu kiểm tra, kiểm soát của cảnh sát giao thông bị phạt bao nhiêu?",
    "Không chấp hành yêu cầu kiểm tra, kiểm soát của người thi hành công vụ về bảo đảm trật tự, an toàn giao thông đường "
    "bộ bị phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng đối với cá nhân, từ 8.000.000 đồng đến 12.000.000 đồng đối với "
    "tổ chức (khoản 10 Điều 12 " + ND + "). Riêng không chấp hành kiểm tra nồng độ cồn, ma túy thì xử phạt theo các điểm "
    "riêng tại Điều 6, Điều 7, Điều 8, Điều 9.", d12("k10"))
add("muc_phat", "Đổ dầu nhớt, chất trơn trượt ra đường gây mất an toàn giao thông bị xử phạt thế nào?",
    "Đổ chất gây trơn trượt trên đường bộ, đặt, để chướng ngại vật trái phép hoặc làm rơi vãi hóa chất, chất thải gây mất "
    "an toàn giao thông bị phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với cá nhân (điểm a khoản 11 Điều 12 " + ND
    + "); nếu người vi phạm là người điều khiển phương tiện thì còn bị trừ điểm giấy phép lái xe 02 điểm (khoản 17 "
    "Điều 12).", d12("k11:a"), d12("k11"), d12("k17"))
add("muc_phat", "Phá hỏng camera giám sát giao thông bị phạt bao nhiêu?",
    "Hủy hoại, làm hư hỏng, làm mất tác dụng thiết bị điều khiển, giám sát giao thông đường bộ, thiết bị thông minh hỗ trợ "
    "chỉ huy, điều khiển giao thông bị phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với cá nhân (điểm c khoản 11 "
    "Điều 12 " + ND + ").", d12("k11:c"), d12("k11"))
add("muc_phat", "Khai báo gian dối để trốn tránh trách nhiệm khi bị phát hiện vi phạm giao thông bị phạt bao nhiêu?",
    "Không khai báo, khai báo gian dối hoặc cung cấp thông tin, tài liệu không đúng sự thật để trốn tránh trách nhiệm khi "
    "bị phát hiện vi phạm pháp luật về trật tự, an toàn giao thông đường bộ bị phạt tiền từ 30.000.000 đồng đến "
    "32.000.000 đồng đối với cá nhân, từ 60.000.000 đồng đến 64.000.000 đồng đối với tổ chức (khoản 13 Điều 12 " + ND + ").",
    d12("k13"))
add("muc_phat", "Chống đối, xúc phạt cảnh sát giao thông đang làm nhiệm vụ bị xử phạt thế nào?",
    "Xúc phạt, đe dọa, cản trở, chống đối người thi hành công vụ về bảo đảm trật tự, an toàn giao thông đường bộ bị phạt "
    "tiền từ 35.000.000 đồng đến 37.000.000 đồng đối với cá nhân (điểm a khoản 14 Điều 12 " + ND + "); nếu là người điều "
    "khiển phương tiện thì còn bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (khoản 15 Điều 12).",
    d12("k14:a"), d12("k14"), d12("k15"))
add("muc_phat", "Rải đinh, vật sắc nhọn trên đường bị phạt bao nhiêu?",
    "Rải vật sắc nhọn trên đường bộ bị phạt tiền từ 35.000.000 đồng đến 37.000.000 đồng đối với cá nhân (điểm b khoản 14 "
    "Điều 12 " + ND + "); nếu là người điều khiển phương tiện thì còn bị tước quyền sử dụng giấy phép lái xe từ 22 tháng "
    "đến 24 tháng (khoản 15 Điều 12).", d12("k14:b"), d12("k14"), d12("k15"))
add("muc_phat", "Sử dụng tạm thời lòng đường làm đám cưới mà không có giấy phép bị phạt bao nhiêu?",
    "Sử dụng tạm thời lòng đường, vỉa hè vào mục đích khác (theo quy định phải có giấy phép) mà không có giấy phép, giấy "
    "phép đã hết giá trị hoặc thực hiện không đúng nội dung giấy phép bị phạt tiền từ 10.000.000 đồng đến 15.000.000 đồng "
    "đối với cá nhân, từ 20.000.000 đồng đến 30.000.000 đồng đối với tổ chức (khoản 12 Điều 12 " + ND + "), và buộc khôi "
    "phục lại tình trạng ban đầu (điểm b khoản 16 Điều 12).", d12("k12"), d12("k16:b"))
add("muc_phat", "Bán hàng rong trên vỉa hè tuyến phố có quy định cấm bán hàng bị phạt bao nhiêu?",
    "Bán hàng rong hoặc bán hàng hóa nhỏ lẻ khác trên lòng đường, trên vỉa hè các tuyến phố có quy định cấm bán hàng bị "
    + fine("200.000", "250.000", 12, 2, "e", " đối với cá nhân") + ".", d12("k2:e"), d12("k2"))

out = ROOT / "data" / "train" / "drafts" / "xu_phat_03.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
print(len(S), "mẫu ->", out)
