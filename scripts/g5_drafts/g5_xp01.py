"""Đợt 1 G5: Xử phạt, Điều 7 NĐ 168/2024 (xe mô tô, xe gắn máy). Ghi data/train/drafts/xu_phat_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"


def v(s, d="2025-01-01"):
    return f"nd_168_2024:d7:{s}@{d}"


def lead(k):
    return v(f"k{k}")


T2, T4, T6, T10 = v("k13:a"), v("k13:b"), v("k13:c"), v("k13:d")
TUOC1, TUOC2 = v("k12:b"), v("k12:c")
S = []


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{len(S) + 1:04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, diem, k):
    return f"phạt tiền từ {lo} đồng đến {hi} đồng (điểm {diem} khoản {k} Điều 7 {ND})"


# ---- Khoản 1: 200.000–400.000 đồng
add("muc_phat", "Đi xe máy vào ban đêm mà không bật đèn chiếu sáng thì bị phạt bao nhiêu?",
    "Người điều khiển xe mô tô, xe gắn máy không sử dụng đèn chiếu sáng trong thời gian từ 18 giờ ngày hôm trước "
    "đến 06 giờ ngày hôm sau, hoặc khi có sương mù, khói, bụi, trời mưa, thời tiết xấu làm hạn chế tầm nhìn, bị "
    + fine("200.000", "400.000", "g", 1) + ".", v("k1:g"), lead(1))
add("muc_phat", "Bấm còi xe máy lúc 23 giờ trong khu dân cư bị xử phạt thế nào?",
    "Sử dụng còi trong thời gian từ 22 giờ ngày hôm trước đến 05 giờ ngày hôm sau trong khu đông dân cư, khu vực cơ "
    "sở khám bệnh, chữa bệnh (trừ xe ưu tiên đang đi làm nhiệm vụ) bị " + fine("200.000", "400.000", "i", 1) + ".",
    v("k1:i"), lead(1))
add("muc_phat", "Chở người ngồi sau xe máy mà người đó cầm ô (dù) thì người lái bị phạt bao nhiêu?",
    "Chở người ngồi trên xe sử dụng ô (dù) bị " + fine("200.000", "400.000", "d", 1) + ".", v("k1:d"), lead(1))
add("muc_phat", "Vượt xe máy khác mà không bật xi nhan (tín hiệu) thì bị phạt bao nhiêu?",
    "Không có tín hiệu trước khi vượt, hoặc có tín hiệu vượt xe nhưng không sử dụng trong suốt quá trình vượt, bị "
    + fine("200.000", "400.000", "b", 1) + ".", v("k1:b"), lead(1))
add("muc_phat", "Chuyển làn đường mà không có tín hiệu báo trước khi đi xe máy bị phạt bao nhiêu?",
    "Chuyển làn đường không đúng nơi cho phép, không có tín hiệu báo trước, hoặc không đúng quy định "
    "“mỗi lần chuyển làn đường chỉ được phép chuyển sang một làn đường liền kề”, hoặc không bảo đảm khoảng cách an "
    "toàn với xe phía trước, phía sau, hai bên, bị " + fine("200.000", "400.000", "e", 1)
    + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026.", v("k1:e", "2026-08-15"), lead(1))
add("muc_phat", "Đi xe máy chậm dưới tốc độ tối thiểu trên đoạn đường có quy định tốc độ tối thiểu bị phạt bao nhiêu?",
    "Điều khiển xe chạy dưới tốc độ tối thiểu trên đoạn đường bộ có quy định tốc độ tối thiểu cho phép bị "
    + fine("200.000", "400.000", "k", 1) + ".", v("k1:k"), lead(1))
add("muc_phat", "Dùng đèn chiếu xa (đèn pha) khi gặp xe đi ngược chiều trên xe máy bị phạt thế nào?",
    "Sử dụng đèn chiếu xa khi gặp xe đi ngược chiều (trừ trường hợp dải phân cách có khả năng chống chói), khi gặp "
    "người đi bộ qua đường, khi đi trên đoạn đường qua khu dân cư có hệ thống chiếu sáng đang hoạt động hoặc khi chuyển "
    "hướng tại nơi đường giao nhau bị " + fine("200.000", "400.000", "h", 1) + ".", v("k1:h"), lead(1))
add("doi_thuong", "đi xe máy tối ko bật đèn bị phạt bn",
    "Không sử dụng đèn chiếu sáng trong thời gian từ 18 giờ ngày hôm trước đến 06 giờ ngày hôm sau bị "
    + fine("200.000", "400.000", "g", 1) + ".", v("k1:g"), lead(1))

# ---- Khoản 2: 400.000–600.000 đồng
add("muc_phat", "Không đội mũ bảo hiểm khi điều khiển xe máy bị phạt bao nhiêu?",
    "Không đội “mũ bảo hiểm cho người đi mô tô, xe máy”, hoặc đội nhưng không cài quai đúng quy cách khi điều khiển xe "
    "tham gia giao thông, bị " + fine("400.000", "600.000", "h", 2) + ".", v("k2:h"), lead(2))
add("doi_thuong", "đội nón bảo hiểm mà ko cài quai thì có bị phạt k, bao nhiêu tiền",
    "Có. Đội “mũ bảo hiểm cho người đi mô tô, xe máy” nhưng không cài quai đúng quy cách khi điều khiển xe bị xử phạt "
    "như không đội mũ: " + fine("400.000", "600.000", "h", 2) + ".", v("k2:h"), lead(2))
add("muc_phat", "Chở người ngồi sau không đội mũ bảo hiểm thì người lái xe máy bị phạt bao nhiêu? Có trường hợp nào được miễn không?",
    "Chở người ngồi trên xe không đội mũ bảo hiểm, hoặc đội nhưng không cài quai đúng quy cách, bị "
    + fine("400.000", "600.000", "i", 2) + ". Không bị phạt khi chở người bệnh đi cấp cứu, trẻ em dưới 06 tuổi, "
    "hoặc áp giải người có hành vi vi phạm pháp luật.", v("k2:i"), lead(2))
add("muc_phat", "Chạy xe máy quá tốc độ 7 km/h bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h bị " + fine("400.000", "600.000", "b", 2) + ".",
    v("k2:b"), lead(2))
add("tinh_huong", "Tôi chở theo 2 người lớn trên xe máy (tổng cộng 3 người) thì bị phạt bao nhiêu?",
    "Chở theo 02 người trên xe bị " + fine("400.000", "600.000", "g", 2) + ". Không bị phạt nếu người được chở là "
    "người bệnh đi cấp cứu, trẻ em dưới 12 tuổi, người già yếu hoặc người khuyết tật, hoặc khi áp giải người có hành "
    "vi vi phạm pháp luật.", v("k2:g"), lead(2))
add("muc_phat", "Đỗ xe máy trên vỉa hè trái phép bị phạt bao nhiêu?",
    "Đỗ, để xe ở lòng đường, vỉa hè trái phép bị " + fine("400.000", "600.000", "d", 2)
    + ". Cùng mức phạt áp dụng cho dừng, đỗ xe ở lòng đường gây cản trở giao thông và tụ tập từ 03 xe trở lên ở lòng "
    "đường, trong hầm đường bộ.", v("k2:d"), lead(2))
add("muc_phat", "Quay đầu xe máy ở nơi không được quay đầu bị phạt bao nhiêu?",
    "Quay đầu xe tại nơi không được quay đầu xe bị " + fine("400.000", "600.000", "k", 2)
    + ". Riêng quay đầu xe trong hầm đường bộ bị xử phạt nặng hơn theo điểm d khoản 4 Điều 7.",
    v("k2:k"), lead(2), v("k4:d"))
add("muc_phat", "Đỗ xe máy ở nơi có biển “Cấm đỗ xe” bị phạt bao nhiêu?",
    "Đỗ xe tại nơi có biển “Cấm đỗ xe” hoặc biển “Cấm dừng xe và đỗ xe” bị " + fine("400.000", "600.000", "e", 2) + ".",
    v("k2:e"), lead(2))
add("muc_phat", "Xe máy thường lắp còi ưu tiên (còi hụ) như xe cứu thương thì bị xử lý thế nào?",
    "Xe không được quyền ưu tiên lắp đặt, sử dụng thiết bị phát tín hiệu của xe được quyền ưu tiên bị "
    + fine("400.000", "600.000", "đ", 2) + "; ngoài ra còn bị tịch thu thiết bị phát tín hiệu ưu tiên lắp đặt, sử dụng "
    "trái quy định (điểm a khoản 12 Điều 7).", v("k2:đ"), lead(2), v("k12:a"))

# ---- Khoản 3: 600.000–800.000 đồng
add("muc_phat", "Đi xe máy chở 3 người phía sau (tổng 4 người) bị phạt thế nào, có bị trừ điểm không?",
    "Chở theo từ 03 người trở lên trên xe bị " + fine("600.000", "800.000", "b", 3)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k3:b"), lead(3), T2)
add("muc_phat", "Rẽ trái ở nơi có biển cấm rẽ trái khi đi xe máy bị phạt bao nhiêu?",
    "Điều khiển xe rẽ trái tại nơi có biển báo hiệu có nội dung cấm rẽ trái đối với loại phương tiện đang điều khiển bị "
    + fine("600.000", "800.000", "a", 3) + ".", v("k3:a"), lead(3))
add("muc_phat", "Chuyển hướng xe máy mà không bật tín hiệu báo rẽ thì bị phạt bao nhiêu?",
    "Chuyển hướng không có tín hiệu báo hướng rẽ, hoặc có tín hiệu nhưng không sử dụng liên tục trong quá trình chuyển "
    "hướng, bị " + fine("600.000", "800.000", "a", 3) + ".", v("k3:a"), lead(3))
add("muc_phat", "Dừng xe máy trên cầu để chụp ảnh có bị phạt không?",
    "Có. Dừng xe, đỗ xe trên cầu bị " + fine("600.000", "800.000", "c", 3) + ".", v("k3:c"), lead(3))
add("muc_phat", "Đi xe máy sai làn đường hoặc đi qua dải phân cách cố định bị phạt bao nhiêu?",
    "Đi không đúng phần đường, làn đường quy định (làn cùng chiều hoặc làn ngược chiều), không đi bên phải theo chiều đi "
    "của mình, hoặc điều khiển xe đi qua dải phân cách cố định ở giữa hai phần đường xe chạy bị "
    + fine("600.000", "800.000", "d", 3) + ".", v("k3:d"), lead(3))
add("muc_phat", "Vượt bên phải bằng xe máy khi không được phép bị phạt bao nhiêu?",
    "Vượt bên phải trong trường hợp không được phép bị " + fine("600.000", "800.000", "đ", 3) + ".", v("k3:đ"), lead(3))
add("tinh_huong", "Người ngồi sau xe máy vừa đi vừa kéo theo một xe đạp hỏng thì người lái bị phạt gì?",
    "Người đang điều khiển xe hoặc người ngồi trên xe bám, kéo, đẩy xe khác, vật khác bị "
    + fine("600.000", "800.000", "e", 3) + ".", v("k3:e"), lead(3))
add("muc_phat", "Ba xe máy chạy dàn hàng ngang trên đường bị phạt bao nhiêu?",
    "Điều khiển xe chạy dàn hàng ngang từ 03 xe trở lên bị " + fine("600.000", "800.000", "k", 3)
    + ", áp dụng với mỗi người điều khiển xe vi phạm.", v("k3:k"), lead(3))
add("muc_phat", "Chạy xe máy trong hầm đường bộ mà không bật đèn chiếu sáng gần bị phạt bao nhiêu?",
    "Chạy trong hầm đường bộ không sử dụng đèn chiếu sáng gần bị " + fine("600.000", "800.000", "h", 3) + ".",
    v("k3:h"), lead(3))
add("muc_phat", "Không giữ khoảng cách an toàn để xảy ra va chạm với xe phía trước khi đi xe máy bị phạt bao nhiêu?",
    "Không giữ khoảng cách an toàn để xảy ra va chạm với xe chạy liền trước, hoặc không giữ khoảng cách theo biển "
    "“Cự ly tối thiểu giữa hai xe”, bị " + fine("600.000", "800.000", "i", 3) + ".", v("k3:i"), lead(3))
add("muc_phat", "Đi xe máy mang vác vật cồng kềnh bị phạt bao nhiêu?",
    "Người đang điều khiển xe hoặc người ngồi trên xe mang vác vật cồng kềnh bị "
    + fine("600.000", "800.000", "e", 3) + ".", v("k3:e"), lead(3))

# ---- Khoản 4: 800.000–1.000.000 đồng
add("muc_phat", "Vừa lái xe máy vừa dùng điện thoại cầm tay thì bị phạt bao nhiêu, có bị trừ điểm không?",
    "Người đang điều khiển xe dùng tay cầm và sử dụng điện thoại hoặc thiết bị điện tử khác bị "
    + fine("800.000", "1.000.000", "đ", 4) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).",
    v("k4:đ"), lead(4), T4)
add("doi_thuong", "vừa chạy xe máy vừa nghe tai nghe có bị phạt ko",
    "Có. Người đang điều khiển xe sử dụng thiết bị âm thanh (trừ thiết bị trợ thính) bị "
    + fine("800.000", "1.000.000", "đ", 4) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).",
    v("k4:đ"), lead(4), T4)
add("muc_phat", "Chạy xe máy quá tốc độ 15 km/h bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định từ 10 km/h đến 20 km/h bị " + fine("800.000", "1.000.000", "a", 4) + ".",
    v("k4:a"), lead(4))
add("muc_phat", "Vượt xe máy ở đoạn có biển cấm vượt bị phạt bao nhiêu?",
    "Vượt xe trong những trường hợp không được vượt, hoặc tại đoạn đường có biển báo hiệu có nội dung cấm vượt đối với "
    "loại phương tiện đang điều khiển, bị " + fine("800.000", "1.000.000", "c", 4) + ".", v("k4:c"), lead(4))
add("muc_phat", "Quay đầu xe máy trong hầm đường bộ bị phạt bao nhiêu?",
    "Quay đầu xe trong hầm đường bộ bị " + fine("800.000", "1.000.000", "d", 4) + ".", v("k4:d"), lead(4))

# ---- Khoản 5: 1.000.000–2.000.000 đồng
add("muc_phat", "Đi xe máy rẽ mà không nhường đường cho người đi bộ đang qua vạch kẻ đường thì bị phạt thế nào?",
    "Chuyển hướng không nhường quyền đi trước cho người đi bộ, xe lăn của người khuyết tật qua đường tại nơi có vạch kẻ "
    "đường dành cho người đi bộ bị " + fine("1.000.000", "2.000.000", "b", 5)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k5:b"), lead(5), T2)
add("tinh_huong", "Xe máy của tôi liên quan trực tiếp đến một vụ va chạm nhưng tôi không dừng lại trợ giúp người bị nạn thì bị phạt gì?",
    "Điều khiển xe có liên quan trực tiếp đến vụ tai nạn giao thông mà không dừng ngay phương tiện, không giữ nguyên hiện "
    "trường, không trợ giúp người bị nạn bị " + fine("1.000.000", "2.000.000", "a", 5)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7). Nếu chính người đó gây tai nạn thì áp dụng "
    "điểm c khoản 9 Điều 7 với mức phạt nặng hơn.", v("k5:a"), lead(5), T2, v("k9:c"))
add("muc_phat", "Xe máy chuyển hướng không nhường đường cho xe đi ngược chiều bị phạt bao nhiêu?",
    "Chuyển hướng không nhường đường cho các xe đi ngược chiều, hoặc cho người đi bộ, xe thô sơ đang qua đường tại nơi "
    "không có vạch kẻ đường cho người đi bộ, bị " + fine("1.000.000", "2.000.000", "c", 5)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k5:c"), lead(5), T2)

# ---- Khoản 6: 2.000.000–3.000.000 đồng
add("muc_phat", "Uống rượu bia rồi đi xe máy, nồng độ cồn dưới 50 miligam/100 mililít máu thì bị phạt bao nhiêu?",
    "Điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn nhưng chưa vượt quá 50 miligam/100 mililít máu "
    "hoặc chưa vượt quá 0,25 miligam/1 lít khí thở bị " + fine("2.000.000", "3.000.000", "a", 6)
    + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).", v("k6:a"), lead(6), T4)
add("doi_thuong", "uống 1 lon bia rồi chạy xe máy bị thổi nồng độ cồn mức thấp nhất thì phạt bn, có bị giữ bằng ko",
    "Nồng độ cồn chưa vượt quá 0,25 miligam/1 lít khí thở (hoặc chưa vượt quá 50 miligam/100 mililít máu) bị "
    + fine("2.000.000", "3.000.000", "a", 6) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7). "
    "Ở mức này Điều 7 không quy định tước quyền sử dụng giấy phép lái xe.", v("k6:a"), lead(6), T4)
add("muc_phat", "Đi xe máy từ đường nhánh ra đường chính mà không giảm tốc độ nhường đường bị phạt thế nào?",
    "Không giảm tốc độ (hoặc dừng lại) và nhường đường khi điều khiển xe đi từ đường không ưu tiên ra đường ưu tiên, từ "
    "đường nhánh ra đường chính bị " + fine("2.000.000", "3.000.000", "c", 6)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k6:c"), lead(6), T2)
add("muc_phat", "Đi xe máy vào đường có biển cấm xe máy bị phạt bao nhiêu?",
    "Đi vào khu vực cấm, đường có biển báo hiệu có nội dung cấm đi vào đối với loại phương tiện đang điều khiển bị "
    + fine("2.000.000", "3.000.000", "b", 6) + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026; người vi phạm "
    "còn bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k6:b", "2026-08-15"), lead(6), T2)
add("quy_tac", "Tại vòng xuyến, xe máy phải nhường đường cho xe đi từ bên nào? Không nhường thì bị phạt bao nhiêu?",
    "Tại nơi đường giao nhau có báo hiệu đi theo vòng xuyến phải giảm tốc độ và nhường đường cho xe đi đến từ bên trái; "
    "nơi giao nhau không có báo hiệu đi theo vòng xuyến thì nhường cho xe đi đến từ bên phải. Không thực hiện bị "
    + fine("2.000.000", "3.000.000", "d", 6) + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).",
    v("k6:d"), lead(6), T2)

# ---- Khoản 7: 4.000.000–6.000.000 đồng
add("muc_phat", "Đi xe máy vượt đèn đỏ bị phạt bao nhiêu tiền và trừ mấy điểm giấy phép lái xe?",
    "Không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị " + fine("4.000.000", "6.000.000", "c", 7)
    + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).", v("k7:c"), lead(7), T4)
add("muc_phat", "Đi xe máy ngược chiều trên đường một chiều bị phạt bao nhiêu?",
    "Đi ngược chiều của đường một chiều, hoặc đi ngược chiều trên đường có biển “Cấm đi ngược chiều” (trừ xe ưu tiên "
    "đang đi làm nhiệm vụ khẩn cấp) bị " + fine("4.000.000", "6.000.000", "a", 7)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7).", v("k7:a"), lead(7), T2)
add("muc_phat", "Điều khiển xe máy đi trên vỉa hè bị phạt bao nhiêu?",
    "Điều khiển xe đi trên vỉa hè bị " + fine("4.000.000", "6.000.000", "a", 7)
    + " và bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 13 Điều 7); không bị phạt khi đi qua vỉa hè để vào nhà, "
    "cơ quan.", v("k7:a"), lead(7), T2)
add("muc_phat", "Xe máy đi vào đường cao tốc bị phạt bao nhiêu?",
    "Điều khiển xe đi vào đường cao tốc (trừ xe phục vụ quản lý, bảo trì đường cao tốc) bị "
    + fine("4.000.000", "6.000.000", "b", 7) + " và bị trừ điểm giấy phép lái xe 06 điểm (điểm c khoản 13 Điều 7).",
    v("k7:b"), lead(7), T6)
add("muc_phat", "Không chấp hành hiệu lệnh của cảnh sát giao thông đang điều khiển giao thông khi đi xe máy bị phạt thế nào?",
    "Không chấp hành hiệu lệnh, hướng dẫn của người điều khiển giao thông hoặc người kiểm soát giao thông bị "
    + fine("4.000.000", "6.000.000", "d", 7) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).",
    v("k7:d"), lead(7), T4)
add("muc_phat", "Đi xe máy không nhường đường cho xe cứu thương đang phát tín hiệu ưu tiên bị phạt bao nhiêu?",
    "Không nhường đường hoặc gây cản trở xe được quyền ưu tiên đang phát tín hiệu ưu tiên đi làm nhiệm vụ bị "
    + fine("4.000.000", "6.000.000", "đ", 7) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).",
    v("k7:đ"), lead(7), T4)
add("doi_thuong", "vượt đèn đỏ xe máy bây giờ phạt bao nhiêu thế",
    "Không chấp hành hiệu lệnh của đèn tín hiệu giao thông khi điều khiển xe mô tô, xe gắn máy bị "
    + fine("4.000.000", "6.000.000", "c", 7) + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).",
    v("k7:c"), lead(7), T4)

# ---- Khoản 8: 6.000.000–8.000.000 đồng
add("muc_phat", "Chạy xe máy quá tốc độ trên 20 km/h bị phạt bao nhiêu và trừ mấy điểm?",
    "Điều khiển xe chạy quá tốc độ quy định trên 20 km/h bị " + fine("6.000.000", "8.000.000", "a", 8)
    + " và bị trừ điểm giấy phép lái xe 04 điểm (điểm b khoản 13 Điều 7).", v("k8:a"), lead(8), T4)
add("muc_phat", "Đi xe máy với nồng độ cồn từ trên 0,25 đến 0,4 miligam/1 lít khí thở bị phạt thế nào?",
    "Điều khiển xe mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam đến 80 miligam/100 mililít máu hoặc "
    "vượt quá 0,25 miligam đến 0,4 miligam/1 lít khí thở bị " + fine("6.000.000", "8.000.000", "b", 8)
    + " và bị trừ điểm giấy phép lái xe 10 điểm (điểm d khoản 13 Điều 7).", v("k8:b"), lead(8), T10)

# ---- Khoản 9: 8.000.000–10.000.000 đồng
add("muc_phat", "Đi xe máy với nồng độ cồn vượt quá 0,4 miligam/1 lít khí thở bị xử phạt thế nào?",
    "Điều khiển xe mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá "
    "0,4 miligam/1 lít khí thở bị " + fine("8.000.000", "10.000.000", "d", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 12 Điều 7).",
    v("k9:d"), lead(9), TUOC2)
add("muc_phat", "Đi xe máy mà không chấp hành yêu cầu kiểm tra nồng độ cồn của cảnh sát thì bị phạt gì?",
    "Không chấp hành yêu cầu kiểm tra về nồng độ cồn của người thi hành công vụ bị "
    + fine("8.000.000", "10.000.000", "đ", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 12 Điều 7).",
    v("k9:đ"), lead(9), TUOC2)
add("muc_phat", "Lạng lách, đánh võng bằng xe máy trên đường bị phạt như thế nào?",
    "Điều khiển xe lạng lách, đánh võng trên đường bộ, hoặc sử dụng chân chống hay vật khác quệt xuống đường khi xe "
    "đang chạy, bị " + fine("8.000.000", "10.000.000", "a", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng (điểm b khoản 12 Điều 7). Tái phạm lạng "
    "lách, đánh võng thì bị tịch thu phương tiện (điểm c khoản 11 Điều 7).", v("k9:a"), lead(9), TUOC1, v("k11:c"))
add("muc_phat", "Rú ga, nẹt pô liên tục trong khu dân cư bị phạt bao nhiêu?",
    "Sử dụng còi, rú ga (nẹt pô) liên tục trong khu đông dân cư, khu vực cơ sở khám bệnh, chữa bệnh (trừ xe ưu tiên "
    "đang làm nhiệm vụ) bị " + fine("8.000.000", "10.000.000", "k", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng (điểm b khoản 12 Điều 7).",
    v("k9:k"), lead(9), TUOC1)
add("muc_phat", "Gây tai nạn giao thông bằng xe máy rồi bỏ chạy, không trình báo thì bị phạt bao nhiêu?",
    "Gây tai nạn giao thông không dừng ngay phương tiện, không giữ nguyên hiện trường, không trợ giúp người bị nạn, "
    "không ở lại hiện trường hoặc không đến trình báo ngay với cơ quan công an, Ủy ban nhân dân nơi gần nhất bị "
    + fine("8.000.000", "10.000.000", "c", 9) + " và bị trừ điểm giấy phép lái xe 06 điểm (điểm c khoản 13 Điều 7).",
    v("k9:c"), lead(9), T6)
add("muc_phat", "Đi xe máy mà trong cơ thể có chất ma túy bị xử phạt thế nào?",
    "Điều khiển xe trên đường mà trong cơ thể có chất ma túy hoặc chất kích thích khác mà pháp luật cấm sử dụng bị "
    + fine("8.000.000", "10.000.000", "e", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 12 Điều 7).",
    v("k9:e"), lead(9), TUOC2)
add("tinh_huong", "Người ngồi sau vòng tay qua người ngồi trước để cầm lái xe máy thì bị phạt gì?",
    "Ngồi phía sau vòng tay qua người ngồi trước để điều khiển xe bị " + fine("8.000.000", "10.000.000", "h", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng (điểm b khoản 12 Điều 7). Không bị phạt "
    "khi chở trẻ em dưới 06 tuổi ngồi phía trước.", v("k9:h"), lead(9), TUOC1)
add("muc_phat", "Đi xe máy thành đoàn gây cản trở giao thông bị phạt bao nhiêu?",
    "Điều khiển xe thành đoàn gây cản trở giao thông (trừ khi được cơ quan có thẩm quyền cấp phép) bị "
    + fine("8.000.000", "10.000.000", "i", 9)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng (điểm b khoản 12 Điều 7).",
    v("k9:i"), lead(9), TUOC1)

# ---- Khoản 10, 11
add("muc_phat", "Đi xe máy quá tốc độ mà gây tai nạn giao thông thì bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định gây tai nạn giao thông bị " + fine("10.000.000", "14.000.000", "a", 10)
    + " và bị trừ điểm giấy phép lái xe 10 điểm (điểm d khoản 13 Điều 7).", v("k10:a"), lead(10), T10)
add("muc_phat", "Những hành vi nào khi đi xe máy bị tịch thu phương tiện?",
    "Theo khoản 11 Điều 7 " + ND + ", bị tịch thu phương tiện khi: buông cả hai tay khi đang điều khiển xe, dùng chân "
    "điều khiển xe, ngồi về một bên hoặc nằm trên yên xe điều khiển xe, thay người điều khiển khi xe đang chạy, quay "
    "người về phía sau hoặc bịt mắt điều khiển xe (điểm a); chạy bằng một bánh đối với xe hai bánh, bằng hai bánh đối với "
    "xe ba bánh (điểm b); tái phạm lạng lách, đánh võng (điểm c). Người vi phạm còn bị tước quyền sử dụng giấy phép lái "
    "xe từ 22 tháng đến 24 tháng (điểm c khoản 12 Điều 7).",
    v("k11:a"), lead(11), v("k11:b"), v("k11:c"), TUOC2)

out = ROOT / "data" / "train" / "drafts" / "xu_phat_01.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
print(len(S), "mẫu ->", out)
