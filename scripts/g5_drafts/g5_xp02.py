"""Đợt 1b G5: Xử phạt, Điều 6 NĐ 168/2024 (xe ô tô). Ghi data/train/drafts/xu_phat_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
NEW = "2026-08-15"


def v(s, d="2025-01-01"):
    return f"nd_168_2024:d6:{s}@{d}"


def lead(k):
    return v(f"k{k}")


T2, T4, T6, T10 = v("k16:a"), v("k16:b"), v("k16:c"), v("k16:d")
TUOC1, TUOC2 = v("k15:b"), v("k15:c")
S = []
START = 61


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def fine(lo, hi, diem, k):
    where = f"điểm {diem} khoản {k}" if diem else f"khoản {k}"
    return f"phạt tiền từ {lo} đồng đến {hi} đồng ({where} Điều 6 {ND})"


def pts(n, d):
    return f"bị trừ điểm giấy phép lái xe {n} điểm (điểm {d} khoản 16 Điều 6)"


# ---- Khoản 1, 1a, 2
add("muc_phat", "Lái ô tô bấm còi lúc 23 giờ trong khu dân cư bị phạt bao nhiêu?",
    "Sử dụng còi trong thời gian từ 22 giờ ngày hôm trước đến 05 giờ ngày hôm sau trong khu đông dân cư, khu vực cơ sở "
    "khám bệnh, chữa bệnh (trừ xe ưu tiên đang làm nhiệm vụ) bị " + fine("400.000", "600.000", "đ", 1) + ".",
    v("k1:đ"), lead(1))
add("muc_phat", "Ô tô hỏng phải đỗ chiếm một phần đường mà không bật đèn khẩn cấp, không đặt biển “Chú ý xe đỗ” thì bị phạt bao nhiêu?",
    "Không báo hiệu bằng đèn khẩn cấp hoặc không đặt biển cảnh báo “Chú ý xe đỗ” khi gặp sự cố kỹ thuật buộc phải đỗ xe "
    "chiếm một phần đường xe chạy hoặc tại nơi không được phép đỗ bị " + fine("400.000", "600.000", "c", 1)
    + ". Trường hợp này xảy ra trên đường cao tốc thì xử phạt theo điểm c khoản 7 Điều 6.", v("k1:c"), lead(1),
    v("k7:c", NEW))
add("muc_phat", "Ô tô ra, vào chỗ đỗ mà không bật tín hiệu báo cho xe khác bị phạt bao nhiêu?",
    "Khi ra, vào vị trí dừng xe, đỗ xe không có tín hiệu báo cho người điều khiển phương tiện khác biết bị "
    + fine("400.000", "600.000", "b", 1) + ".", v("k1:b"), lead(1))
add("muc_phat", "Chở bé 6 tuổi cao 1,2 mét trên ô tô gia đình mà không dùng ghế an toàn cho trẻ em thì bị xử phạt thế nào?",
    "Người điều khiển xe ô tô chở trẻ em dưới 10 tuổi và chiều cao dưới 1,35 mét mà không sử dụng thiết bị an toàn phù "
    "hợp cho trẻ em theo quy định bị phạt cảnh cáo (khoản 1a Điều 6 " + ND + ", có hiệu lực từ ngày 15/8/2026). Quy "
    "định này không áp dụng với xe ô tô kinh doanh vận tải hành khách.", v("k1a", NEW))
add("muc_phat", "Ô tô chuyển làn không bật xi nhan trên đường thường (không phải cao tốc) bị phạt bao nhiêu?",
    "Chuyển làn đường không đúng nơi cho phép, không có tín hiệu báo trước, hoặc không đúng quy định “mỗi lần chuyển làn "
    "đường chỉ được phép chuyển sang một làn đường liền kề” bị " + fine("600.000", "800.000", "a", 2)
    + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026. Nếu vi phạm khi chạy trên đường cao tốc thì áp dụng điểm g "
    "khoản 5 Điều 6.", v("k2:a", NEW), lead(2), v("k5:g", NEW))
add("muc_phat", "Ô tô chở người ngồi trên buồng lái quá số lượng quy định bị phạt bao nhiêu?",
    "Chở người trên buồng lái quá số lượng quy định bị " + fine("600.000", "800.000", "b", 2) + ".", v("k2:b"), lead(2))
add("muc_phat", "Dừng ô tô cách vỉa hè hơn 0,25 mét bị phạt bao nhiêu?",
    "Dừng xe không sát theo lề đường, vỉa hè phía bên phải theo chiều đi, hoặc bánh xe gần nhất cách lề đường, vỉa hè quá "
    "0,25 mét, bị " + fine("600.000", "800.000", "đ", 2)
    + ". Nếu là đỗ xe (không phải dừng xe) cách vỉa hè quá 0,25 mét thì xử phạt theo điểm e khoản 3 Điều 6.",
    v("k2:đ"), lead(2), v("k3:e"))
add("tinh_huong", "Tôi dừng ô tô bên đường rồi xuống xe, tắt máy đi mua đồ thì có bị phạt không?",
    "Có thể bị phạt. Rời vị trí lái, tắt máy khi dừng xe (trừ khi rời vị trí lái để đóng, mở cửa xe, xếp dỡ hàng hóa, "
    "kiểm tra kỹ thuật xe) bị " + fine("600.000", "800.000", "đ", 2) + ".", v("k2:đ"), lead(2))
add("muc_phat", "Đỗ ô tô trên dốc mà không chèn bánh bị phạt bao nhiêu?",
    "Đỗ xe trên dốc không chèn bánh bị " + fine("600.000", "800.000", "d", 2) + ".", v("k2:d"), lead(2))

# ---- Khoản 3: 800.000–1.000.000 đồng
add("muc_phat", "Lái ô tô không thắt dây đai an toàn bị phạt bao nhiêu?",
    "Không thắt dây đai an toàn khi điều khiển xe chạy trên đường bị " + fine("800.000", "1.000.000", "k", 3) + ".",
    v("k3:k"), lead(3))
add("muc_phat", "Người ngồi sau trên ô tô không thắt dây an toàn thì tài xế có bị phạt không?",
    "Có. Chở người trên xe ô tô không thắt dây đai an toàn (tại vị trí có trang bị dây đai an toàn) khi xe đang chạy bị "
    + fine("800.000", "1.000.000", "l", 3) + ".", v("k3:l"), lead(3))
add("muc_phat", "Chở trẻ em dưới 10 tuổi ngồi ghế trước cạnh tài xế ô tô có bị phạt không?",
    "Có, nếu trẻ dưới 10 tuổi và chiều cao dưới 1,35 mét. Chở trẻ như vậy ngồi cùng hàng ghế với người lái xe (trừ xe "
    "ô tô chỉ có một hàng ghế) bị " + fine("800.000", "1.000.000", "m", 3) + ", điểm này có hiệu lực từ ngày 15/8/2026.",
    v("k3:m", NEW), lead(3))
add("muc_phat", "Ô tô chạy quá tốc độ 8 km/h bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h bị " + fine("800.000", "1.000.000", "a", 3) + ".",
    v("k3:a"), lead(3))
add("muc_phat", "Lái ô tô dùng còi hơi hoặc bấm còi, rú ga liên tục bị phạt bao nhiêu?",
    "Sử dụng còi, rú ga liên tục, sử dụng còi hơi (trừ xe ưu tiên đang làm nhiệm vụ) bị "
    + fine("800.000", "1.000.000", "b", 3) + ".", v("k3:b"), lead(3))
add("muc_phat", "Ô tô bật đèn pha (đèn chiếu xa) khi gặp xe đi ngược chiều bị phạt bao nhiêu?",
    "Sử dụng đèn chiếu xa khi gặp xe đi ngược chiều (trừ trường hợp dải phân cách có khả năng chống chói), khi gặp người "
    "đi bộ qua đường, khi đi trên đoạn đường qua khu dân cư có hệ thống chiếu sáng đang hoạt động hoặc khi chuyển hướng "
    "tại nơi đường giao nhau bị " + fine("800.000", "1.000.000", "b", 3) + ".", v("k3:b"), lead(3))
add("muc_phat", "Ô tô rẽ mà không bật tín hiệu báo hướng rẽ bị phạt bao nhiêu?",
    "Chuyển hướng không có tín hiệu báo hướng rẽ, hoặc có tín hiệu nhưng không sử dụng liên tục trong quá trình chuyển "
    "hướng, hoặc không quan sát, không giảm tốc độ, không bảo đảm khoảng cách an toàn với xe phía sau, bị "
    + fine("800.000", "1.000.000", "c", 3) + ".", v("k3:c"), lead(3))
add("quy_tac", "Ô tô không được dừng, đỗ trong phạm vi bao nhiêu mét tính từ mép đường giao nhau? Vi phạm bị phạt bao nhiêu?",
    "Dừng xe, đỗ xe tại nơi đường bộ giao nhau hoặc trong phạm vi 05 mét tính từ mép đường giao nhau bị "
    + fine("800.000", "1.000.000", "đ", 3) + ". Cùng mức phạt áp dụng khi dừng, đỗ trong phạm vi 05 mét hai bên cổng trụ "
    "sở cơ quan, tổ chức có bố trí đường cho xe ra, vào, hoặc tại điểm đón, trả khách.", v("k3:đ"), lead(3))
add("muc_phat", "Đỗ ô tô ở nơi có biển “Cấm đỗ xe” bị phạt bao nhiêu?",
    "Đỗ xe nơi có biển “Cấm đỗ xe” hoặc biển “Cấm dừng xe và đỗ xe” bị " + fine("800.000", "1.000.000", "e", 3) + ".",
    v("k3:e"), lead(3))
add("muc_phat", "Đỗ ô tô trên vỉa hè trái phép bị phạt bao nhiêu?",
    "Đỗ, để xe ở vỉa hè trái quy định của pháp luật bị " + fine("800.000", "1.000.000", "e", 3) + ".", v("k3:e"), lead(3))
add("muc_phat", "Ô tô chạy buổi tối không bật đèn chiếu sáng bị phạt bao nhiêu?",
    "Không sử dụng hoặc sử dụng không đủ đèn chiếu sáng trong thời gian từ 18 giờ ngày hôm trước đến 06 giờ ngày hôm sau, "
    "hoặc khi có sương mù, khói, bụi, trời mưa, thời tiết xấu làm hạn chế tầm nhìn, bị "
    + fine("800.000", "1.000.000", "g", 3) + ".", v("k3:g"), lead(3))
add("muc_phat", "Ô tô kéo theo một xe khác không tự chạy được nhưng không nối chắc chắn thì bị xử phạt thế nào?",
    "Không nối chắc chắn, an toàn giữa xe kéo và xe được kéo khi kéo nhau bị " + fine("800.000", "1.000.000", "h", 3)
    + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026; người vi phạm còn " + pts("02", "a") + ".",
    v("k3:h", NEW), lead(3), T2)
add("muc_phat", "Ô tô đang kéo xe hỏng mà vẫn chở người ngồi trên xe được kéo thì bị phạt gì?",
    "Chở người trên xe được kéo (trừ người điều khiển) bị " + fine("800.000", "1.000.000", "i", 3) + " và "
    + pts("02", "a") + ".", v("k3:i"), lead(3), T2)
add("doi_thuong", "lái xe hơi chạy chậm mà cứ đi làn trái có bị phạt k",
    "Có thể bị phạt. Điều khiển xe chạy tốc độ thấp hơn các xe khác đi cùng chiều mà không đi về làn đường bên phải chiều "
    "đi của mình (trừ khi các xe khác chạy quá tốc độ quy định) bị " + fine("800.000", "1.000.000", "p", 3) + ".",
    v("k3:p"), lead(3))
add("doi_thuong", "đi ô tô ko cài dây an toàn bị phạt bn tiền v",
    "Người lái không thắt dây đai an toàn khi điều khiển xe chạy trên đường bị " + fine("800.000", "1.000.000", "k", 3)
    + ". Chở người không thắt dây đai an toàn (tại vị trí có trang bị) cũng bị phạt cùng mức theo điểm l khoản 3 Điều 6.",
    v("k3:k"), lead(3), v("k3:l"))

# ---- Khoản 4: 2.000.000–3.000.000 đồng
add("muc_phat", "Ô tô không dán thẻ thu phí tự động mà đi vào làn thu phí không dừng (ETC) bị phạt bao nhiêu?",
    "Điều khiển xe không đủ điều kiện để thu phí theo hình thức điện tử tự động không dừng (xe không gắn thẻ đầu cuối) đi "
    "vào làn đường dành riêng thu phí không dừng tại trạm thu phí bị " + fine("2.000.000", "3.000.000", "a", 4) + " và "
    + pts("02", "a") + ".", v("k4:a"), lead(4), T2)
add("muc_phat", "Đỗ ô tô trên cầu hoặc dưới gầm cầu vượt bị phạt bao nhiêu?",
    "Dừng xe, đỗ xe trên cầu (trừ trường hợp tổ chức giao thông cho phép) hoặc gầm cầu vượt (trừ nơi cho phép dừng, đỗ) bị "
    + fine("2.000.000", "3.000.000", "b", 4) + " và " + pts("02", "a") + ".", v("k4:b"), lead(4), T2)
add("muc_phat", "Ô tô không nhường đường cho xe phía sau xin vượt khi đủ điều kiện an toàn bị phạt bao nhiêu?",
    "Không nhường đường cho xe xin vượt khi có đủ điều kiện an toàn bị " + fine("2.000.000", "3.000.000", "d", 4) + " và "
    + pts("02", "a") + ".", v("k4:d"), lead(4), T2)
add("muc_phat", "Lùi ô tô trên đường một chiều bị phạt bao nhiêu?",
    "Lùi xe ở đường một chiều, đường có biển “Cấm đi ngược chiều”, khu vực cấm dừng, trên phần đường dành cho người đi bộ "
    "qua đường, nơi đường bộ giao nhau hoặc nơi tầm nhìn bị che khuất bị " + fine("2.000.000", "3.000.000", "e", 4)
    + ". Lùi xe trên đường cao tốc bị xử phạt nặng hơn theo điểm đ khoản 11 Điều 6.", v("k4:e"), lead(4), v("k11:đ"))
add("muc_phat", "Quay đầu ô tô trên cầu hoặc ở phần đường dành cho người đi bộ qua đường bị phạt bao nhiêu?",
    "Quay đầu xe ở phần đường dành cho người đi bộ qua đường, trên cầu, đầu cầu, gầm cầu vượt, đường hẹp, đường dốc, đoạn "
    "đường cong tầm nhìn bị che khuất, trên đường một chiều (trừ khi có hiệu lệnh, chỉ dẫn hoặc có bố trí nơi quay đầu) bị "
    + fine("2.000.000", "3.000.000", "i", 4) + ".", v("k4:i"), lead(4))
add("muc_phat", "Ô tô rẽ trái ở nơi có biển cấm rẽ trái bị phạt bao nhiêu?",
    "Điều khiển xe rẽ trái tại nơi có biển báo hiệu có nội dung cấm rẽ trái đối với loại phương tiện đang điều khiển bị "
    + fine("2.000.000", "3.000.000", "k", 4) + ".", v("k4:k"), lead(4))
add("muc_phat", "Ô tô quay đầu ở nơi có biển cấm quay đầu bị phạt bao nhiêu?",
    "Quay đầu xe tại nơi có biển báo hiệu có nội dung cấm quay đầu đối với loại phương tiện đang điều khiển bị "
    + fine("2.000.000", "3.000.000", "k", 4) + ".", v("k4:k"), lead(4))
add("tinh_huong", "Ô tô của tôi có liên quan trực tiếp đến một vụ va chạm, tôi không dừng lại giúp người bị nạn thì bị phạt thế nào?",
    "Điều khiển xe có liên quan trực tiếp đến vụ tai nạn giao thông mà không dừng ngay phương tiện, không giữ nguyên hiện "
    "trường, không trợ giúp người bị nạn bị " + fine("2.000.000", "3.000.000", "g", 4) + " và " + pts("02", "a")
    + ". Nếu chính người đó gây tai nạn rồi bỏ đi thì xử phạt theo khoản 8 Điều 6 với mức nặng hơn.",
    v("k4:g"), lead(4), T2, v("k8"))
add("muc_phat", "Lái ô tô không giữ khoảng cách an toàn để xảy ra va chạm với xe phía trước bị phạt bao nhiêu?",
    "Không giữ khoảng cách an toàn để xảy ra va chạm với xe chạy liền trước, hoặc không giữ khoảng cách theo biển "
    "“Cự ly tối thiểu giữa hai xe”, bị " + fine("2.000.000", "3.000.000", "l", 4) + ".", v("k4:l"), lead(4))
add("muc_phat", "Quay đầu ô tô trong hầm đường bộ bị phạt bao nhiêu?",
    "Lùi xe, quay đầu xe trong hầm đường bộ bị " + fine("2.000.000", "3.000.000", "đ", 4) + " và " + pts("02", "a") + ".",
    v("k4:đ"), lead(4), T2)

# ---- Khoản 5: 4.000.000–6.000.000 đồng
add("muc_phat", "Lái ô tô vừa đi vừa cầm điện thoại bị phạt bao nhiêu, trừ mấy điểm?",
    "Dùng tay cầm và sử dụng điện thoại hoặc thiết bị điện tử khác khi điều khiển xe đang di chuyển trên đường bộ bị "
    + fine("4.000.000", "6.000.000", "h", 5) + " và " + pts("04", "b") + ".", v("k5:h"), lead(5), T4)
add("muc_phat", "Ô tô chạy quá tốc độ 15 km/h bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định từ 10 km/h đến 20 km/h bị " + fine("4.000.000", "6.000.000", "đ", 5) + " và "
    + pts("02", "a") + ".", v("k5:đ"), lead(5), T2)
add("muc_phat", "Ô tô vượt xe ở đoạn có biển cấm vượt bị phạt bao nhiêu?",
    "Vượt xe trong trường hợp không được vượt, vượt tại đoạn đường có biển báo cấm vượt, không có tín hiệu trước khi vượt "
    "hoặc vượt bên phải xe khác khi không được phép bị " + fine("4.000.000", "6.000.000", "a", 5) + " và "
    + pts("02", "a") + ".", v("k5:a"), lead(5), T2)
add("muc_phat", "Ô tô đi sai làn đường hoặc lấn sang phần đường ngược chiều bị phạt bao nhiêu?",
    "Điều khiển xe không đi bên phải theo chiều đi của mình, đi không đúng phần đường hoặc làn đường quy định (làn cùng "
    "chiều hoặc làn ngược chiều), hoặc đi qua dải phân cách cố định bị " + fine("4.000.000", "6.000.000", "b", 5)
    + " và " + pts("02", "a") + ".", v("k5:b"), lead(5), T2)
add("muc_phat", "Ô tô chạy vào làn dừng xe khẩn cấp trên đường cao tốc bị phạt bao nhiêu?",
    "Điều khiển xe chạy ở làn dừng xe khẩn cấp hoặc phần lề đường của đường cao tốc, hoặc không tuân thủ quy định khi vào, "
    "ra đường cao tốc, bị " + fine("4.000.000", "6.000.000", "d", 5) + " và " + pts("02", "a") + ".",
    v("k5:d"), lead(5), T2)
add("muc_phat", "Ô tô chuyển làn sai quy định trên đường cao tốc bị phạt bao nhiêu?",
    "Chuyển làn đường không đúng nơi cho phép, không có tín hiệu báo trước, hoặc không đúng quy định chuyển sang làn liền "
    "kề khi chạy trên đường cao tốc bị " + fine("4.000.000", "6.000.000", "g", 5)
    + ", điểm này có hiệu lực từ ngày 15/8/2026; người vi phạm còn " + pts("02", "a") + ".",
    v("k5:g", NEW), lead(5), T2)
add("muc_phat", "Ô tô đi vào đường có biển cấm ô tô bị phạt bao nhiêu?",
    "Đi vào khu vực cấm, đường có biển báo hiệu có nội dung cấm đi vào đối với loại phương tiện đang điều khiển bị "
    + fine("4.000.000", "6.000.000", "i", 5) + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026; người vi phạm còn "
    + pts("02", "a") + ".", v("k5:i", NEW), lead(5), T2)
add("muc_phat", "Ô tô rẽ không nhường đường cho người đi bộ đang qua vạch kẻ đường bị phạt bao nhiêu?",
    "Chuyển hướng không nhường quyền đi trước cho người đi bộ, xe lăn của người khuyết tật qua đường tại nơi có vạch kẻ "
    "đường dành cho người đi bộ bị " + fine("4.000.000", "6.000.000", "l", 5) + ".", v("k5:l"), lead(5))
add("muc_phat", "Ô tô từ đường nhánh ra đường chính mà không giảm tốc độ, không nhường đường bị phạt bao nhiêu?",
    "Không giảm tốc độ (hoặc dừng lại) và nhường đường khi điều khiển xe đi từ đường không ưu tiên ra đường ưu tiên, từ "
    "đường nhánh ra đường chính bị " + fine("4.000.000", "6.000.000", "n", 5) + " và " + pts("02", "a") + ".",
    v("k5:n"), lead(5), T2)
add("tinh_huong", "Tôi mở cửa ô tô bất ngờ làm người đi xe máy phía sau phải tránh gấp thì có bị phạt không?",
    "Có. Mở cửa xe, để cửa xe mở không bảo đảm an toàn bị " + fine("4.000.000", "6.000.000", "q", 5)
    + ". Nếu hành vi này gây tai nạn giao thông thì xử phạt theo điểm b khoản 10 Điều 6 với mức nặng hơn.",
    v("k5:q"), lead(5), v("k10:b"))
add("muc_phat", "Chở người trên thùng xe tải trái quy định bị phạt bao nhiêu?",
    "Chở người trên thùng xe trái quy định, hoặc để người nằm, ngồi, đu bám bên ngoài xe khi xe đang chạy, bị "
    + fine("4.000.000", "6.000.000", "p", 5) + ", điểm này được sửa đổi, có hiệu lực từ ngày 15/8/2026; người vi phạm còn "
    + pts("06", "c") + ".", v("k5:p", NEW), lead(5), T6)
add("muc_phat", "Ô tô thường lắp còi ưu tiên như xe cứu thương thì bị xử lý thế nào?",
    "Xe không được quyền ưu tiên lắp đặt, sử dụng thiết bị phát tín hiệu của xe được quyền ưu tiên bị "
    + fine("4.000.000", "6.000.000", "e", 5) + ", " + pts("02", "a") + ", và bị tịch thu thiết bị phát tín hiệu ưu tiên "
    "lắp đặt, sử dụng trái quy định (điểm a khoản 15 Điều 6).", v("k5:e"), lead(5), T2, v("k15:a"))
add("muc_phat", "Dừng, đỗ, quay đầu ô tô trái quy định gây ùn tắc giao thông bị phạt bao nhiêu?",
    "Dừng xe, đỗ xe, quay đầu xe trái quy định gây ùn tắc giao thông bị " + fine("4.000.000", "6.000.000", "k", 5) + " và "
    + pts("02", "a") + ".", v("k5:k"), lead(5), T2)

# ---- Khoản 6, 7, 8
add("muc_phat", "Ô tô chạy quá tốc độ 30 km/h bị phạt bao nhiêu?",
    "Điều khiển xe chạy quá tốc độ quy định trên 20 km/h đến 35 km/h bị " + fine("6.000.000", "8.000.000", "a", 6) + " và "
    + pts("04", "b") + ".", v("k6:a"), lead(6), T4)
add("muc_phat", "Lái ô tô có nồng độ cồn nhưng chưa vượt quá 50 miligam/100 mililít máu bị phạt thế nào?",
    "Điều khiển xe mà trong máu hoặc hơi thở có nồng độ cồn nhưng chưa vượt quá 50 miligam/100 mililít máu hoặc chưa vượt "
    "quá 0,25 miligam/1 lít khí thở bị " + fine("6.000.000", "8.000.000", "c", 6) + " và " + pts("04", "b") + ".",
    v("k6:c"), lead(6), T4)
add("doi_thuong", "lái xe hơi uống 1 cốc bia bị thổi nồng độ cồn mức thấp nhất thì phạt bao nhiêu",
    "Nồng độ cồn chưa vượt quá 0,25 miligam/1 lít khí thở (hoặc chưa vượt quá 50 miligam/100 mililít máu) khi lái ô tô bị "
    + fine("6.000.000", "8.000.000", "c", 6) + " và " + pts("04", "b") + ".", v("k6:c"), lead(6), T4)
add("muc_phat", "Ô tô không nhường đường cho xe cứu hỏa đang phát tín hiệu ưu tiên bị phạt bao nhiêu?",
    "Không nhường đường hoặc gây cản trở xe được quyền ưu tiên đang phát tín hiệu ưu tiên đi làm nhiệm vụ bị "
    + fine("6.000.000", "8.000.000", "b", 6) + " và " + pts("04", "b") + ".", v("k6:b"), lead(6), T4)
add("muc_phat", "Lái ô tô đi trên vỉa hè bị phạt bao nhiêu?",
    "Điều khiển xe đi trên vỉa hè (trừ trường hợp đi qua vỉa hè để vào nhà, cơ quan) bị "
    + fine("6.000.000", "8.000.000", "d", 6) + " và " + pts("04", "b") + ".", v("k6:d"), lead(6), T4)
add("muc_phat", "Ô tô chạy quá tốc độ trên 35 km/h bị phạt bao nhiêu và trừ mấy điểm?",
    "Điều khiển xe chạy quá tốc độ quy định trên 35 km/h bị " + fine("12.000.000", "14.000.000", "a", 7) + " và "
    + pts("06", "c") + ".", v("k7:a"), lead(7), T6)
add("muc_phat", "Ô tô dừng, đỗ trên đường cao tốc không đúng nơi quy định bị phạt bao nhiêu?",
    "Dừng xe, đỗ xe trên đường cao tốc không đúng nơi quy định, hoặc khi gặp sự cố phải dừng trên cao tốc mà không có báo "
    "hiệu bằng đèn khẩn cấp, không đặt biển cảnh báo “Chú ý xe đỗ” cách phía sau xe tối thiểu 150 mét, bị "
    + fine("12.000.000", "14.000.000", "c", 7) + ", điểm này có hiệu lực từ ngày 15/8/2026; người vi phạm còn "
    + pts("06", "c") + ".", v("k7:c", NEW), lead(7), T6)
add("muc_phat", "Xe chở người bốn bánh có gắn động cơ đi vào đường cao tốc bị phạt bao nhiêu?",
    "Điều khiển xe chở người bốn bánh có gắn động cơ, xe chở hàng bốn bánh có gắn động cơ đi vào đường cao tốc bị "
    + fine("12.000.000", "14.000.000", "b", 7) + " và " + pts("04", "b") + ".", v("k7:b"), lead(7), T4)
add("muc_phat", "Lái ô tô gây tai nạn rồi bỏ chạy, không trình báo bị phạt bao nhiêu?",
    "Gây tai nạn giao thông mà không dừng ngay phương tiện, không giữ nguyên hiện trường, không trợ giúp người bị nạn, "
    "không ở lại hiện trường hoặc không đến trình báo ngay với cơ quan công an, Ủy ban nhân dân nơi gần nhất bị "
    + fine("16.000.000", "18.000.000", None, 8) + " và " + pts("06", "c") + ".", v("k8"), T6)

# ---- Khoản 9, 10, 11
add("muc_phat", "Lái ô tô vượt đèn đỏ bị phạt bao nhiêu?",
    "Không chấp hành hiệu lệnh của đèn tín hiệu giao thông bị " + fine("18.000.000", "20.000.000", "b", 9) + " và "
    + pts("04", "b") + ".", v("k9:b"), lead(9), T4)
add("muc_phat", "Ô tô đi ngược chiều trên đường một chiều bị phạt bao nhiêu?",
    "Đi ngược chiều của đường một chiều, hoặc đi ngược chiều trên đường có biển “Cấm đi ngược chiều” (trừ xe ưu tiên đang "
    "làm nhiệm vụ khẩn cấp) bị " + fine("18.000.000", "20.000.000", "d", 9) + " và " + pts("04", "b")
    + ". Đi ngược chiều trên đường cao tốc bị xử phạt nặng hơn theo điểm đ khoản 11 Điều 6.",
    v("k9:d"), lead(9), T4, v("k11:đ"))
add("muc_phat", "Lái ô tô với nồng độ cồn vượt quá 0,25 đến 0,4 miligam/1 lít khí thở bị phạt thế nào?",
    "Điều khiển xe mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 50 miligam đến 80 miligam/100 mililít máu hoặc vượt "
    "quá 0,25 miligam đến 0,4 miligam/1 lít khí thở bị " + fine("18.000.000", "20.000.000", "a", 9) + " và "
    + pts("10", "d") + ".", v("k9:a"), lead(9), T10)
add("muc_phat", "Lái ô tô với nồng độ cồn vượt quá 80 miligam/100 mililít máu bị xử phạt thế nào?",
    "Điều khiển xe mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá "
    "0,4 miligam/1 lít khí thở bị " + fine("30.000.000", "40.000.000", "a", 11)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 15 Điều 6).",
    v("k11:a"), lead(11), TUOC2)
add("muc_phat", "Tài xế ô tô từ chối thổi nồng độ cồn khi cảnh sát yêu cầu thì bị phạt gì?",
    "Không chấp hành yêu cầu kiểm tra về nồng độ cồn của người thi hành công vụ bị "
    + fine("30.000.000", "40.000.000", "b", 11)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 15 Điều 6).",
    v("k11:b"), lead(11), TUOC2)
add("muc_phat", "Lái ô tô mà trong cơ thể có chất ma túy bị xử phạt thế nào?",
    "Điều khiển xe trên đường mà trong cơ thể có chất ma túy hoặc chất kích thích khác mà pháp luật cấm sử dụng bị "
    + fine("30.000.000", "40.000.000", "c", 11)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng (điểm c khoản 15 Điều 6).",
    v("k11:c"), lead(11), TUOC2)
add("muc_phat", "Lùi xe hoặc quay đầu xe ô tô trên đường cao tốc bị phạt bao nhiêu?",
    "Điều khiển xe đi ngược chiều, lùi xe hoặc quay đầu xe trên đường cao tốc (trừ xe ưu tiên đang làm nhiệm vụ khẩn cấp) "
    "bị " + fine("30.000.000", "40.000.000", "đ", 11) + " và " + pts("10", "d") + ".", v("k11:đ"), lead(11), T10)
add("muc_phat", "Ô tô đi sai làn đường mà gây tai nạn giao thông thì bị phạt bao nhiêu?",
    "Không đi đúng phần đường, làn đường gây tai nạn giao thông bị " + fine("20.000.000", "22.000.000", "a", 10) + " và "
    + pts("10", "d") + ".", v("k10:a"), lead(10), T10)

# ---- Khoản 12–14
add("muc_phat", "Lái ô tô lạng lách, đánh võng hoặc chạy quá tốc độ đuổi nhau trên đường bị xử phạt thế nào?",
    "Điều khiển xe lạng lách, đánh võng, chạy quá tốc độ đuổi nhau hoặc dùng chân điều khiển vô lăng khi xe đang chạy bị "
    + fine("40.000.000", "50.000.000", None, 12)
    + " và bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng (điểm b khoản 15 Điều 6). Gây tai nạn thì bị "
    "phạt từ 50.000.000 đồng đến 70.000.000 đồng (khoản 13 Điều 6); tái phạm lạng lách, đánh võng thì bị tịch thu phương "
    "tiện (khoản 14 Điều 6).", v("k12"), TUOC1, v("k13"), v("k14"))

add("tinh_huong", "Tôi mở cửa ô tô không quan sát làm người đi xe máy ngã (gây tai nạn) thì bị phạt thế nào?",
    "Mở cửa xe, để cửa xe mở không bảo đảm an toàn mà gây tai nạn giao thông bị "
    + fine("20.000.000", "22.000.000", "b", 10) + " và " + pts("10", "d") + ".", v("k10:b"), lead(10), v("k5:q"), T10)

out = ROOT / "data" / "train" / "drafts" / "xu_phat_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
print(len(S), "mẫu ->", out)
