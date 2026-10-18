"""Đợt 7a G5: Tốc độ (TT 38/2024/TT-BGTVT) và Biển báo, đèn tín hiệu (QCVN 41:2024/BGTVT).
Ghi data/train/drafts/toc_do_bien_bao_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 38/2024/TT-BGTVT"
QC = "QCVN 41:2024/BGTVT"
S = []
N = {"td": 0, "bb": 0}


def t(s):
    return f"tt_38_2024_bgtvt:{s}@2025-01-01"


def q(s):
    return f"qcvn_41_2024:{s}@2025-01-01"


def add(pre, chu_de, loai, qs, ans, *can_cu):
    N[pre] += 1
    S.append({"key": f"{pre}-{N[pre]:04d}", "chu_de": chu_de, "loai": loai, "cau_hoi": qs, "dap_an": ans,
              "can_cu": list(can_cu)})


T, B = "Tốc độ", "Biển báo"

# ===== Tốc độ (TT 38/2024)
add("td", T, "quy_tac", "Trong khu đông dân cư, ô tô và xe máy được chạy tối đa bao nhiêu km/h?",
    "Theo Bảng 1 khoản 1 Điều 6 " + TT + ", tốc độ khai thác tối đa (đơn vị km/h) của các loại xe cơ giới trong khu vực đông "
    "dân cư là: 60 trên đường đôi hoặc đường một chiều có từ hai làn xe cơ giới trở lên; 50 trên đường hai chiều hoặc đường "
    "một chiều có một làn xe cơ giới. Không áp dụng cho xe gắn máy, xe máy chuyên dùng và xe bốn bánh có gắn động cơ (có mức "
    "riêng tại Điều 7, Điều 8).", t("d6:k1"))
add("td", T, "doi_thuong", "trong phố đường 2 chiều không có biển tốc độ thì xe máy chạy max bao nhiêu",
    "Ở đoạn đường không đặt biển báo tốc độ, người lái thực hiện theo Thông tư 38/2024 (khoản 2 Điều 4). Trong khu đông dân "
    "cư, trên đường hai chiều, tốc độ khai thác tối đa (km/h) của xe mô tô và các xe cơ giới khác là 50 (Bảng 1 khoản 1 "
    "Điều 6 " + TT + "). Riêng xe gắn máy tối đa 40 km/h (Điều 7).", t("d4:k2"), t("d6:k1"), t("d7"))
add("td", T, "quy_tac", "Ngoài khu đông dân cư, ô tô con được chạy tối đa bao nhiêu?",
    "Theo Bảng 2 khoản 2 Điều 6 " + TT + ", xe ô tô chở người đến 28 chỗ (trừ xe buýt) và ô tô tải có trọng tải không lớn "
    "hơn 3,5 tấn có tốc độ khai thác tối đa (km/h) là 90 trên đường đôi, đường một chiều từ hai làn xe cơ giới trở lên, và 80 "
    "trên đường hai chiều, đường một chiều có một làn xe cơ giới.", t("d6:k2"))
add("td", T, "quy_tac", "Xe máy chạy ngoài khu dân cư thì tốc độ tối đa là bao nhiêu?",
    "Theo Bảng 2 khoản 2 Điều 6 " + TT + ", xe mô tô (cùng nhóm với xe buýt, ô tô đầu kéo kéo sơ mi rơ moóc, ô tô chuyên "
    "dùng) có tốc độ khai thác tối đa (km/h) ngoài khu vực đông dân cư là 70 trên đường đôi, đường một chiều từ hai làn xe cơ "
    "giới trở lên, và 60 trên đường hai chiều, đường một chiều có một làn xe cơ giới.", t("d6:k2"))
add("td", T, "quy_tac", "Xe tải trên 3,5 tấn chạy ngoài khu dân cư được tối đa bao nhiêu km/h?",
    "Theo Bảng 2 khoản 2 Điều 6 " + TT + ", ô tô tải có trọng tải trên 3,5 tấn (trừ ô tô xi téc) và ô tô chở người trên 28 "
    "chỗ (trừ xe buýt) có tốc độ khai thác tối đa (km/h) là 80 trên đường đôi, đường một chiều từ hai làn xe cơ giới trở lên, "
    "và 70 trên đường hai chiều, đường một chiều có một làn.", t("d6:k2"))
add("td", T, "quy_tac", "Xe kéo rơ moóc, xe xi téc, xe trộn bê tông chạy ngoài khu dân cư được tối đa bao nhiêu?",
    "Theo Bảng 2 khoản 2 Điều 6 " + TT + ", ô tô kéo rơ moóc, ô tô kéo xe khác, ô tô trộn vữa, trộn bê tông lưu động, ô tô "
    "xi téc, ô tô đầu kéo kéo sơ mi rơ moóc xi téc có tốc độ khai thác tối đa (km/h) là 60 trên đường đôi, đường một chiều "
    "từ hai làn xe cơ giới trở lên, và 50 trên đường hai chiều, đường một chiều có một làn.", t("d6:k2"))
add("td", T, "doi_thuong", "xe gắn máy 50cc được chạy tối đa bao nhiêu km/h",
    "Xe gắn máy, xe máy chuyên dùng và các loại xe tương tự khi tham gia giao thông có tốc độ khai thác tối đa là 40 km/h "
    "(Điều 7 " + TT + ").", t("d7"))
add("td", T, "quy_tac", "Xe điện chở khách du lịch (xe chở người bốn bánh có gắn động cơ) được chạy tối đa bao nhiêu?",
    "Xe chở người bốn bánh có gắn động cơ khi tham gia giao thông trong phạm vi và thời gian cho phép hoạt động có tốc độ khai "
    "thác tối đa là 30 km/h; xe chở hàng bốn bánh có gắn động cơ là 50 km/h (Điều 8 " + TT + ").", t("d8:k1"), t("d8:k2"))
add("td", T, "quy_tac", "Tốc độ tối đa và tối thiểu trên đường cao tốc là bao nhiêu?",
    "Tốc độ khai thác tối đa cho phép trên đường cao tốc là 120 km/h; tốc độ khai thác tối thiểu là 60 km/h (trường hợp đường "
    "cao tốc có tốc độ thiết kế 60 km/h thì tốc độ tối thiểu theo phương án tổ chức giao thông được phê duyệt) (khoản 2, khoản "
    "3 Điều 9 " + TT + "). Đường cao tốc phải đặt biển báo tốc độ tối đa, tối thiểu (khoản 1 Điều 9).",
    t("d9:k2"), t("d9:k3"), t("d9:k1"))
add("td", T, "quy_tac", "Khu đông dân cư được xác định như thế nào khi áp dụng tốc độ?",
    "Đường bộ trong khu đông dân cư là đoạn đường nằm trong khu vực nội thành phố, nội thị xã, nội thị trấn và những đoạn "
    "đường có đông dân cư sinh sống sát dọc theo đường, được xác định bằng biển báo \"Bắt đầu khu đông dân cư\" và biển báo "
    "\"Hết khu đông dân cư\" (khoản 1 Điều 3 " + TT + ").", t("d3:k1"))
add("td", T, "quy_tac", "Đường đôi và đường hai chiều khác nhau thế nào khi tính tốc độ tối đa?",
    "Đường đôi là đường có chiều đi và chiều về được phân biệt bằng dải phân cách giữa; đường hai chiều là đường dùng chung "
    "cho cả chiều đi và về trên cùng một phần đường xe chạy mà không có dải phân cách giữa (khoản 2, khoản 4 Điều 3 " + TT
    + "). Theo QCVN 41:2024, trường hợp phân biệt hai chiều bằng vạch sơn thì không phải đường đôi (khoản 10 Điều 3).",
    t("d3:k2"), t("d3:k4"), q("d3:k10"))
add("td", T, "quy_tac", "Chạy 80 km/h thì phải giữ khoảng cách an toàn với xe trước bao nhiêu?",
    "Theo điểm a khoản 2 Điều 11 " + TT + " (Bảng 3), trong điều kiện đường khô ráo, thẳng, tầm nhìn bảo đảm, khoảng cách an "
    "toàn (đơn vị mét) ứng với tốc độ lưu hành là: tốc độ 60: 35; trên 60 đến 80: 55; trên 80 đến 100: 70; trên 100 đến 120: "
    "100. Dưới 60 km/h thì người lái chủ động giữ khoảng cách phù hợp với mật độ phương tiện.", t("d11:k2:a"), t("d11:k2"))
add("td", T, "tinh_huong", "Trời mưa, đường trơn khi chạy trên cao tốc thì khoảng cách an toàn tính thế nào?",
    "Trong điều kiện trời mưa, có sương mù, mặt đường trơn trượt, đường quanh co, đèo dốc, tầm nhìn hạn chế, người lái xe "
    "phải điều chỉnh khoảng cách an toàn lớn hơn trị số ghi trên biển báo hoặc trị số trong Bảng 3 (điểm b khoản 2 Điều 11 "
    + TT + ").", t("d11:k2:b"))
add("td", T, "quy_tac", "Gặp biển 'Cự ly tối thiểu giữa hai xe' thì phải làm gì?",
    "Người lái xe phải giữ một khoảng cách an toàn với xe chạy liền trước cùng làn hoặc cùng phần đường, cùng chiều; ở nơi có "
    "biển báo \"Cự ly tối thiểu giữa hai xe\" phải giữ khoảng cách không nhỏ hơn trị số ghi trên biển (khoản 1 Điều 11 " + TT
    + ").", t("d11:k1"))
add("td", T, "quy_tac", "Khoảng cách an toàn giữa hai xe là gì?",
    "Là cự ly tối thiểu giữa xe phía sau với xe đang di chuyển liền trước, cùng làn đường, bảo đảm tránh va chạm khi xe phía "
    "trước đột ngột giảm tốc độ hoặc dừng lại (khoản 8 Điều 3 " + TT + ").", t("d3:k8"))
add("td", T, "quy_tac", "Cơ quan nào quyết định đặt biển hạn chế tốc độ trên quốc lộ, đường tỉnh?",
    "Theo khoản 3 Điều 10 " + TT + ": Cục Đường bộ Việt Nam, Cục Đường Cao tốc Việt Nam với đường cao tốc được Bộ giao quản "
    "lý; Cục Đường bộ Việt Nam với hệ thống quốc lộ và đường khác thuộc phạm vi quản lý của Bộ; Ủy ban nhân dân cấp tỉnh với "
    "cao tốc, quốc lộ, đường tỉnh, huyện, xã, thôn, đô thị và đường chuyên dùng thuộc phạm vi quản lý của mình.",
    t("d10:k3"), t("d10:k3:b"), t("d10:k3:c"))
add("td", T, "quy_tac", "Có được đặt biển tốc độ tối đa chỉ áp dụng cho một khoảng thời gian trong ngày không?",
    "Có. Cơ quan có thẩm quyền được quyết định đặt biển báo tốc độ khai thác tối đa cho một khoảng thời gian trong ngày (biển "
    "phụ, biển điện tử), đặt riêng cho từng chiều với đường đôi, hoặc riêng cho các loại phương tiện có nguy cơ mất an toàn "
    "cao (khoản 2 Điều 10 " + TT + ").", t("d10:k2:b"), t("d10:k2"))
add("td", T, "quy_tac", "Thông tư 38/2024 về tốc độ có áp dụng cho xe cứu thương đang làm nhiệm vụ không?",
    "Không. Thông tư quy định tốc độ khai thác và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng, trừ xe ưu tiên đang "
    "đi làm nhiệm vụ theo quy định (Điều 1 " + TT + "). QCVN 41:2024 cũng quy định xe ưu tiên đang làm nhiệm vụ không bị hạn "
    "chế tốc độ (khoản 7.3 Điều 7).", t("d1"), q("d7:k3"))

# ===== Biển báo, đèn tín hiệu (QCVN 41:2024)
add("bb", B, "quy_tac", "Khi cảnh sát điều khiển giao thông khác với đèn tín hiệu thì phải theo cái nào?",
    "Phải theo hiệu lệnh của người điều khiển giao thông. Khi các báo hiệu có ý nghĩa khác nhau, thứ tự ưu tiên chấp hành là: "
    "hiệu lệnh của người điều khiển giao thông; tín hiệu đèn giao thông; biển báo hiệu; vạch kẻ đường và dấu hiệu trên mặt "
    "đường; cọc tiêu, tường bảo vệ, rào chắn…; thiết bị âm thanh báo hiệu (khoản 4.1 Điều 4 " + QC + ").", q("d4:k1"))
add("bb", B, "doi_thuong", "đèn vàng có được đi tiếp ko",
    "Gặp đèn vàng thì phải dừng lại trước vạch dừng; nếu đang đi trên vạch dừng hoặc đã đi qua vạch dừng khi đèn chuyển vàng "
    "thì được đi tiếp. Đèn vàng nhấp nháy thì được đi nhưng phải quan sát, giảm tốc độ hoặc dừng lại nhường đường (khoản 6.3.2 "
    "Điều 6 " + QC + ").", q("d6:k3"))
add("bb", B, "quy_tac", "Đèn xanh có phải nhường người đi bộ không?",
    "Có trong trường hợp người đi bộ, xe lăn của người khuyết tật đang đi ở lòng đường: khi đó người điều khiển phương tiện "
    "phải giảm tốc độ hoặc dừng lại nhường đường cho họ qua đường, dù tín hiệu xanh là được đi (khoản 6.3.1 Điều 6 " + QC
    + ").", q("d6:k3"))
add("bb", B, "tinh_huong", "Ngã tư không có vạch dừng, đèn đỏ thì tôi phải dừng ở đâu?",
    "Tín hiệu đỏ là cấm đi, phải dừng trước vạch dừng; nếu không có vạch dừng thì phải dừng trước đèn tín hiệu theo chiều đi, "
    "tức vị trí đặt đèn tín hiệu gần nhất theo chiều đi được coi như vạch dừng (khoản 6.3.3, 6.3.4 Điều 6 " + QC + ").",
    q("d6:k3"))
add("bb", B, "quy_tac", "Đèn mũi tên xanh rẽ trái có được quay đầu không?",
    "Có. Tín hiệu mũi tên cho phép rẽ trái thì đồng thời cho phép quay đầu nếu không có báo hiệu cấm quay đầu khác (khoản "
    "6.4.1 Điều 6 " + QC + ").", q("d6:k4"))
add("bb", B, "tinh_huong", "Đèn đỏ nhưng có mũi tên xanh rẽ phải sáng cùng lúc thì tôi có được rẽ phải không?",
    "Được rẽ theo hướng mũi tên. Khi mũi tên xanh bật sáng cùng lúc với tín hiệu đỏ hoặc vàng thì phương tiện được đi theo "
    "hướng mũi tên nhưng phải nhường đường cho phương tiện đi từ các hướng khác đang được phép đi (khoản 6.4.3 Điều 6 " + QC
    + ").", q("d6:k4"))
add("bb", B, "quy_tac", "Đèn chính màu xanh nhưng mũi tên màu đỏ sáng thì sao?",
    "Khi tín hiệu mũi tên màu đỏ bật sáng cùng lúc với đèn chính màu xanh thì phương tiện không được đi theo hướng mũi tên đó "
    "(khoản 6.4.4 Điều 6 " + QC + ").", q("d6:k4"))
add("bb", B, "quy_tac", "Đèn tín hiệu lắp theo chiều đứng thì thứ tự màu thế nào?",
    "Đèn tín hiệu chính dùng ba màu xanh, vàng, đỏ; khi lắp theo chiều thẳng đứng thì đèn đỏ ở trên, đèn vàng ở giữa và đèn "
    "xanh ở dưới (khoản 6.1 Điều 6 " + QC + "). Tại một thời điểm, trên cùng một bộ đèn chỉ được sáng một trong ba màu "
    "(khoản 6.3.5).", q("d6:k1"), q("d6:k3"))
add("bb", B, "quy_tac", "Thứ tự ưu tiên của các xe ưu tiên khi qua ngã tư là gì?",
    "Theo khoản 7.1 Điều 7 " + QC + ", thứ tự từ trên xuống: xe chữa cháy đi làm nhiệm vụ chữa cháy; xe của lực lượng quân "
    "sự, công an, kiểm sát đi làm nhiệm vụ khẩn cấp và đoàn xe có Cảnh sát giao thông dẫn đường; xe cứu thương đi cấp cứu; xe "
    "hộ đê, xe đi làm nhiệm vụ cứu nạn, cứu hộ, khắc phục thiên tai, dịch bệnh; đoàn xe tang.",
    q("d7:k1"), q("d7:k1:a"), q("d7:k1:c"), q("d7:k1:đ"))
add("bb", B, "quy_tac", "Đèn ưu tiên màu đỏ, màu xanh trên nóc xe là của xe nào?",
    "Đèn nhấp nháy màu đỏ dùng cho xe chữa cháy, xe quân sự đi làm nhiệm vụ khẩn cấp, xe cứu thương đang cấp cứu; đèn nhấp "
    "nháy màu xanh và đỏ dùng cho xe công an, kiểm sát đi làm nhiệm vụ khẩn cấp, xe Cảnh sát giao thông dẫn đường; đèn nhấp "
    "nháy màu xanh dùng cho xe hộ đê, xe cứu nạn, cứu hộ, khắc phục thiên tai, dịch bệnh (khoản 7.2 Điều 7 " + QC + ").",
    q("d7:k2:a"), q("d7:k2:b"), q("d7:k2:c"))
add("bb", B, "doi_thuong", "nghe còi xe cứu thương phía sau thì phải làm gì",
    "Khi có tín hiệu của xe ưu tiên, người và phương tiện tham gia giao thông phải giảm tốc độ, đi sát lề đường bên phải hoặc "
    "dừng lại để nhường đường, không được gây cản trở (khoản 7.4 Điều 7 " + QC + ").", q("d7:k4"))
add("bb", B, "quy_tac", "Xe ưu tiên đang làm nhiệm vụ có được vượt đèn đỏ và đi ngược chiều không?",
    "Được. Xe ưu tiên (trừ đoàn xe tang) không bị hạn chế tốc độ, được đi không phụ thuộc tín hiệu đèn, được đi vào đường "
    "ngược chiều; riêng trên đường cao tốc chỉ được đi ngược chiều trên làn dừng xe khẩn cấp; nhưng vẫn phải tuân theo hiệu "
    "lệnh của người điều khiển giao thông và biển báo tạm thời (khoản 7.3 Điều 7 " + QC + ").", q("d7:k3"))
add("bb", B, "quy_tac", "Thứ tự đường ưu tiên giữa các loại đường là thế nào?",
    "Thứ tự đường ưu tiên: đường cao tốc; quốc lộ; đường đô thị; đường tỉnh; đường huyện; đường xã; đường thôn; đường chuyên "
    "dùng (khoản 5.1 Điều 5 " + QC + "). Không được quy định cả hai đường giao nhau cùng mức đồng thời là đường ưu tiên "
    "(khoản 5.3).", q("d5:k1"), q("d5:k3"))
add("bb", B, "quy_tac", "Hai đường cùng cấp giao nhau thì đường nào được ưu tiên?",
    "Xem xét lần lượt: đường được cấp có thẩm quyền quy định là ưu tiên; đường có cấp kỹ thuật cao hơn; đường có lưu lượng xe "
    "trung bình ngày đêm lớn hơn; đường có nhiều xe ô tô vận tải công cộng hơn; đường có mặt đường cấp cao hơn (khoản 5.2 Điều "
    "5 " + QC + ").", q("d5:k2"))
add("bb", B, "quy_tac", "Biển báo hiệu đường bộ được chia thành mấy nhóm?",
    "Gồm 5 nhóm cơ bản: biển báo cấm; biển hiệu lệnh; biển báo nguy hiểm và cảnh báo; biển chỉ dẫn; biển phụ, biển viết bằng "
    "chữ (Điều 11 " + QC + ").", q("d11"))
add("bb", B, "doi_thuong", "biển tròn viền đỏ là biển gì",
    "Biển hình tròn, viền đỏ, nền trắng, có hình vẽ hoặc chữ số màu đen là biển báo cấm, biểu thị điều cấm mà người tham gia "
    "giao thông không được vi phạm (khoản 11.1 Điều 11 " + QC + ").", q("d11:k1"))
add("bb", B, "quy_tac", "Biển hiệu lệnh có hình dạng, màu sắc thế nào?",
    "Biển hiệu lệnh chủ yếu có dạng hình tròn trên nền xanh lam, hình vẽ màu trắng, để báo các hiệu lệnh người tham gia giao "
    "thông phải chấp hành (khoản 11.2 Điều 11 " + QC + ").", q("d11:k2"))
add("bb", B, "doi_thuong", "biển tam giác vàng viền đỏ là biển gì",
    "Là biển báo nguy hiểm và cảnh báo: chủ yếu hình tam giác đều, viền đỏ, nền vàng, hình vẽ màu đen, báo trước các nguy "
    "hiểm trên đường để người tham gia giao thông chủ động phòng ngừa (khoản 11.3 Điều 11 " + QC + ").", q("d11:k3"))
add("bb", B, "quy_tac", "Biển chỉ dẫn có hình dạng, màu sắc thế nào?",
    "Biển chỉ dẫn cung cấp thông tin và chỉ dẫn cần thiết, chủ yếu có hình chữ nhật, hình vuông hoặc hình mũi tên, nền màu "
    "xanh (khoản 11.4 Điều 11 " + QC + ").", q("d11:k4"))
add("bb", B, "quy_tac", "Biển cấm có hiệu lực từ đâu?",
    "Biển báo cấm được đặt ở nơi đường giao nhau hoặc trước vị trí cần cấm và có hiệu lực bắt đầu từ vị trí đặt biển trở đi; "
    "nếu đặt cách xa vị trí định cấm thì phải có biển phụ S.502 chỉ rõ khoảng cách (khoản 26.1 Điều 26 " + QC + ").",
    q("d26:k1"))
add("bb", B, "quy_tac", "Biển cấm quay đầu có hiệu lực ở đâu?",
    "Biển số P.124 (a, b, c, d, e, f) có hiệu lực ở vị trí nơi đường giao nhau, chỗ mở dải phân cách nhưng không cho phép quay "
    "đầu xe, hoặc căn cứ vào biển phụ S.503 (khoản 26.7 Điều 26 " + QC + ").", q("d26:k7"))
add("bb", B, "quy_tac", "Các biển cấm số P.125, P.126, P.127, P.130, P.131 có hiệu lực đến đâu?",
    "Các biển số P.125, P.126, P.127, P.130, P.131 có hiệu lực đến nơi đường giao "
    "nhau tiếp giáp hoặc đến vị trí đặt biển hết cấm (DP.133, DP.134, DP.135, DP.127d); riêng P.130, P.131 còn căn cứ vào "
    "biển phụ (khoản 26.8 Điều 26 " + QC + ").", q("d26:k8"))
add("bb", B, "quy_tac", "Biển cấm áp dụng cho làn nào trên đường nhiều làn?",
    "Biển báo cấm và biển hiệu lệnh có giá trị trên tất cả các làn đường hoặc chỉ trên một hoặc một số làn theo biển báo trên "
    "đường; còn biển báo nguy hiểm, cảnh báo và biển chỉ dẫn có giá trị trên các làn đường của chiều xe chạy (khoản 15.1, "
    "15.2 Điều 15 " + QC + ").", q("d15:k1"), q("d15:k2"))
add("bb", B, "quy_tac", "Một cột được treo tối đa mấy biển báo và theo thứ tự nào?",
    "Nếu nhiều biển cần đặt cùng vị trí thì được đặt kết hợp trên cùng một cột nhưng không quá 3 biển, theo thứ tự ưu tiên: "
    "biển báo cấm, biển hiệu lệnh, biển báo nguy hiểm hoặc cảnh báo, biển chỉ dẫn (khoản 18.3 Điều 18 " + QC + ").",
    q("d18:k3"))
add("bb", B, "quy_tac", "Biển báo VMS là gì?",
    "Biển báo giao thông có thông tin thay đổi (VMS) là biển điện tử có thể thay đổi thông tin trên cùng một mặt biển, dùng khi "
    "thông tin cần thay đổi theo tình huống giao thông; không được dùng để quảng cáo (khoản 14.1 Điều 14 " + QC + ").",
    q("d14:k1"))
add("bb", B, "quy_tac", "Ngã tư vừa có đèn tín hiệu vừa có biển báo thì theo cái nào?",
    "Ở nơi đường giao nhau vừa có đèn tín hiệu vừa có biển báo hiệu và vạch sơn thì người lái xe phải tuân theo hiệu lệnh của "
    "đèn tín hiệu (Điều 8 " + QC + ").", q("d8"))

out = ROOT / "data/train/drafts/toc_do_bien_bao_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
