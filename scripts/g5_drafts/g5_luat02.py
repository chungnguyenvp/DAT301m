"""Đợt 8b G5: Luật lõi, Luật 36/2024 Điều 23, 24, 27, 28, 29, 31, 35, 56. Ghi data/train/drafts/luat_loi_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
S = []
START = 67
J7 = "2026-07-01"


def l(s, d="2025-01-01"):
    return f"luat_36_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"lu-{START + len(S):04d}", "chu_de": "Luật lõi", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Phà, cầu phao (Điều 23)
add("quy_tac", "Thứ tự ưu tiên các xe khi qua phà là gì?",
    "Các xe qua phà, cầu phao theo thứ tự ưu tiên: xe ưu tiên; xe chở thư báo; xe chở thực phẩm tươi sống; xe chở khách công "
    "cộng. Các xe cùng thứ tự ưu tiên thì xe nào đến trước được qua trước (khoản 2 Điều 23 " + LUAT + ").",
    l("d23:k2"), l("d23:k2:a"), l("d23:k2:d"))
add("tinh_huong", "Đi xe khách xuống phà, tôi có được ngồi lại trên xe không?",
    "Không, trừ khi bạn là người lái xe, trẻ em, phụ nữ mang thai, người già yếu, người khuyết tật hoặc người bệnh. Khi xe xuống "
    "phà, đang ở trên phà và khi lên bến, mọi người khác không được ở trên xe (điểm a khoản 3 Điều 23 " + LUAT + ").",
    l("d23:k3:a"), l("d23:k3"))
add("quy_tac", "Khi xuống phà và lên bến thì xe và người đi bộ đi theo thứ tự nào?",
    "Khi xuống phà, xe cơ giới, xe máy chuyên dùng xuống trước, xe thô sơ và người đi bộ xuống sau; khi lên bến, người đi bộ lên "
    "trước, các phương tiện lên sau theo hướng dẫn của người điều khiển giao thông (điểm b khoản 3 Điều 23 " + LUAT + ").",
    l("d23:k3:b"), l("d23:k3"))
add("quy_tac", "Đi qua cầu phao phải tuân thủ những gì?",
    "Xe cơ giới, xe máy chuyên dùng phải đi theo một hàng theo chiều di chuyển, không cản trở người, phương tiện ngược chiều; xe "
    "thô sơ, người đi bộ đi sát bên phải; tất cả phải tuân thủ hướng dẫn của người điều khiển giao thông (khoản 4 Điều 23 " + LUAT
    + ").", l("d23:k4"), l("d23:k4:a"), l("d23:k4:b"))

# ===== Đường ngang đường sắt (Điều 24)
add("quy_tac", "Gặp đèn đỏ nhấp nháy, chuông kêu ở đường ngang đường sắt thì phải làm gì?",
    "Khi có hiệu lệnh của nhân viên gác chắn, đèn đỏ sáng nhấp nháy, chuông kêu, chắn đường bộ đang dịch chuyển hoặc đã đóng, người "
    "tham gia giao thông phải dừng lại về bên phải đường của mình, trước vạch dừng xe (khoản 1 Điều 24 " + LUAT + ").",
    l("d24:k1"))
add("doi_thuong", "qua đường tàu không có barie thì phải làm sao",
    "Tới đường ngang không có người gác, chắn, chuông, đèn tín hiệu thì phải dừng lại về bên phải đường của mình, trước vạch dừng "
    "xe, quan sát hai phía; chỉ khi không có tàu tới mới được đi qua (khoản 2 Điều 24 " + LUAT + ").", l("d24:k2"))
add("tinh_huong", "Xe tôi chết máy ngay trên đường ray mà không đẩy ra được. Tôi phải làm gì?",
    "Khi phương tiện bị hư hỏng, tai nạn hoặc hàng hóa rơi đổ trên đường ngang mà không thể di chuyển ngay khỏi phạm vi an toàn "
    "đường sắt, người điều khiển và người có mặt phải ngay lập tức báo hiệu để dừng tàu và thực hiện các biện pháp bảo đảm an "
    "toàn (khoản 3 Điều 24 " + LUAT + ").", l("d24:k3"))

# ===== Xe ưu tiên (Điều 27)
add("quy_tac", "Những loại xe nào là xe ưu tiên theo Luật Trật tự, an toàn giao thông đường bộ?",
    "Xe ưu tiên gồm xe chữa cháy đi làm nhiệm vụ; xe của lực lượng quân sự, công an, kiểm sát đi làm nhiệm vụ khẩn cấp; đoàn xe "
    "có Cảnh sát giao thông dẫn đường; xe cứu thương đi cấp cứu; xe hộ đê đi làm nhiệm vụ; xe đi làm nhiệm vụ cứu nạn, cứu hộ, "
    "khắc phục thiên tai, dịch bệnh hoặc trong tình trạng khẩn cấp; đoàn xe tang (khoản 1, khoản 2 Điều 27 " + LUAT + ").",
    l("d27:k1"), l("d27:k2"))
add("quy_tac", "Hiện nay xe quân sự đi làm nhiệm vụ khẩn cấp dùng đèn ưu tiên màu gì?",
    "Theo điểm b khoản 3 Điều 27 " + LUAT + " (nội dung có hiệu lực từ ngày 01/7/2026), xe của lực lượng công an, quân sự, kiểm "
    "sát đi làm nhiệm vụ khẩn cấp và xe Cảnh sát giao thông dẫn đường có đèn nhấp nháy màu xanh và đỏ. Xe chữa cháy và xe cứu "
    "thương đang cấp cứu có đèn nhấp nháy màu đỏ (điểm a khoản 3 Điều 27).", l("d27:k3:b", J7), l("d27:k3:a", J7))
add("quy_tac", "Trạm thu phí có phải cho xe ưu tiên qua trước không?",
    "Có. Khi có tín hiệu của xe ưu tiên, trạm thu phí phải ưu tiên cho xe ưu tiên qua trạm trong mọi tình huống, không được gây cản "
    "trở; người và phương tiện khác phải giảm tốc độ, đi sát lề phải hoặc dừng lại nhường đường (khoản 5 Điều 27 " + LUAT + ").",
    l("d27:k5"))
add("quy_tac", "Đoàn xe tang có được vượt đèn đỏ như xe ưu tiên khác không?",
    "Không. Quyền không bị hạn chế tốc độ, được đi không phụ thuộc tín hiệu đèn và đi vào đường ngược chiều chỉ áp dụng cho các xe "
    "ưu tiên tại các điểm a, b, c, d khoản 2 Điều 27 (xe chữa cháy, quân sự, công an, kiểm sát, cứu thương, cứu nạn, cứu hộ…), "
    "không bao gồm đoàn xe tang (khoản 4 Điều 27 " + LUAT + "). Đoàn xe tang chỉ được quyền đi trước khi qua đường giao nhau theo "
    "thứ tự ưu tiên (điểm đ khoản 2 Điều 27).", l("d27:k4"), l("d27:k2:đ"))

# ===== Chở người trên xe tải, kéo xe (Điều 28, 29)
add("quy_tac", "Có được chở người trên thùng xe tải không?",
    "Chỉ trong các trường hợp: chở người đi cứu nạn, cứu hộ, phòng chống thiên tai, dịch bệnh, nhiệm vụ khẩn cấp, chở người bị nạn "
    "đi cấp cứu, đưa người ra khỏi khu vực nguy hiểm; chở lực lượng vũ trang đi làm nhiệm vụ khẩn cấp; chở người thực hành lái xe, "
    "dự sát hạch, công nhân duy tu đường bộ; chở người diễu hành theo đoàn khi được phép (khoản 1 Điều 28 " + LUAT + "). Khi đó "
    "phải bảo đảm an toàn (khoản 2 Điều 28).", l("d28:k1"), l("d28:k1:a"), l("d28:k2"))
add("tinh_huong", "Tôi chở công nhân công ty trên thùng xe tải đi làm. Như vậy có được không?",
    "Không thuộc các trường hợp được phép. Luật chỉ cho chở người trên thùng xe ô tô chở hàng trong các trường hợp cứu nạn, cứu hộ, "
    "nhiệm vụ khẩn cấp, chở người bị nạn đi cấp cứu, lực lượng vũ trang làm nhiệm vụ khẩn cấp, người tập lái, sát hạch, công nhân "
    "duy tu đường bộ, hoặc diễu hành được phép (khoản 1 Điều 28 " + LUAT + ").", l("d28:k1"))
add("quy_tac", "Ô tô kéo xe hỏng thì phải tuân thủ những gì?",
    "Một ô tô chỉ được kéo theo một ô tô hoặc xe máy chuyên dùng khác khi xe được kéo không tự chạy được; xe được kéo phải có người "
    "điều khiển và hệ thống lái còn hiệu lực; việc nối phải chắc chắn, nếu phanh của xe được kéo không còn hiệu lực thì phải nối "
    "bằng thanh nối cứng; phía trước xe kéo và phía sau xe được kéo phải có biển báo hiệu và đèn cảnh báo nhấp nháy màu vàng (khoản "
    "1 Điều 29 " + LUAT + ").", l("d29:k1"), l("d29:k1:a"), l("d29:k1:b"), l("d29:k1:c"))
add("quy_tac", "Có được chở người trên xe đang được kéo không?",
    "Không, trừ người điều khiển xe được kéo. Xe kéo rơ moóc, ô tô đầu kéo kéo sơ mi rơ moóc cũng không được kéo thêm rơ moóc, sơ "
    "mi rơ moóc hoặc xe khác (khoản 3 Điều 29 " + LUAT + ").", l("d29:k3"))

# ===== Xe đạp, xe thô sơ (Điều 31)
add("quy_tac", "Xe đạp được chở mấy người?",
    "Người điều khiển xe đạp, xe đạp máy chỉ được chở một người; trường hợp chở thêm một trẻ em dưới 07 tuổi thì được chở tối đa "
    "hai người (khoản 1 Điều 31 " + LUAT + ").", l("d31:k1"))
add("doi_thuong", "đi xe đạp điện có phải đội mũ bảo hiểm ko",
    "Có. Xe đạp máy (gồm cả xe đạp điện) thì người điều khiển và người được chở phải đội mũ bảo hiểm đúng quy chuẩn và cài quai "
    "đúng quy cách (khoản 3 Điều 31 " + LUAT + "; điểm b khoản 2 Điều 34 về xe đạp máy gồm cả xe đạp điện).",
    l("d31:k3"), l("d34:k2:b"))
add("quy_tac", "Đi xe thô sơ ban đêm phải tuân thủ gì?",
    "Người điều khiển xe thô sơ chỉ được cho xe đi hàng một, đi đúng phần đường dành cho xe thô sơ nếu có; trong thời gian từ 18 "
    "giờ ngày hôm trước đến 06 giờ ngày hôm sau phải sử dụng đèn hoặc có báo hiệu ở phía trước và phía sau xe (khoản 4 Điều 31 "
    + LUAT + ").", l("d31:k4"))
add("quy_tac", "Chở hàng trên xe ba gác, xe thô sơ được vượt ra ngoài bao nhiêu?",
    "Hàng hóa trên xe thô sơ không vượt quá 1/3 chiều dài thân xe, không vượt quá 01 mét phía trước và phía sau xe, không vượt quá "
    "0,4 mét mỗi bên bánh xe; phải bảo đảm an toàn, không cản trở giao thông, không che khuất tầm nhìn người điều khiển (khoản 5 "
    "Điều 31 " + LUAT + ").", l("d31:k5"))
add("quy_tac", "Người đi xe đạp có bị cấm những hành vi như người đi xe máy không?",
    "Có. Người điều khiển xe đạp, xe đạp máy không được thực hiện các hành vi bị cấm đối với người lái xe máy tại khoản 3 Điều 33 "
    "(như dàn hàng ngang, buông cả hai tay, sử dụng ô, kéo đẩy xe khác…); người được chở cũng không được thực hiện các hành vi tại "
    "khoản 4 Điều 33 (khoản 2 Điều 31 " + LUAT + ").", l("d31:k2"), l("d33:k3"))

# ===== Điều kiện phương tiện, giấy tờ người lái (Điều 35, 56)
add("quy_tac", "Xe cơ giới tham gia giao thông phải đáp ứng điều kiện gì?",
    "Xe cơ giới, xe máy chuyên dùng phải được cấp chứng nhận đăng ký xe, gắn biển số theo quy định và bảo đảm chất lượng an toàn kỹ "
    "thuật, bảo vệ môi trường (khoản 1 Điều 35 " + LUAT + ").", l("d35:k1"), l("d35:k1:a"), l("d35:k1:b"))
add("quy_tac", "Hiện nay những xe nào bắt buộc lắp thiết bị giám sát hành trình và camera ghi hình người lái?",
    "Theo khoản 2 Điều 35 " + LUAT + " (nội dung có hiệu lực từ ngày 01/7/2026), xe ô tô kinh doanh vận tải hàng hóa, xe kinh "
    "doanh vận tải hành khách dưới 08 chỗ (không kể chỗ người lái), xe ô tô đầu kéo, xe cứu thương, xe vận tải nội bộ phải lắp "
    "thiết bị giám sát hành trình và thiết bị ghi nhận hình ảnh người lái xe; xe kinh doanh vận tải hành khách từ 08 chỗ trở lên "
    "cũng phải lắp thiết bị giám sát hành trình cùng các thiết bị theo quy định.", l("d35:k2", J7))
add("thu_tuc", "Lái ô tô phải mang theo những giấy tờ gì?",
    "Theo khoản 1 Điều 56 " + LUAT + ", người lái xe phải mang theo: chứng nhận đăng ký xe (hoặc bản sao có chứng thực kèm giấy xác "
    "nhận của tổ chức tín dụng nếu xe đang thế chấp); giấy phép lái xe phù hợp; chứng nhận kiểm định an toàn kỹ thuật và bảo vệ "
    "môi trường đối với xe cơ giới; chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới.",
    l("d56:k1"), l("d56:k1:a"), l("d56:k1:b"), l("d56:k1:c"), l("d56:k1:d"))
add("doi_thuong", "có bằng lái trên VNeID rồi có cần mang bằng giấy ko",
    "Không bắt buộc mang bản giấy nếu giấy tờ đã được tích hợp vào tài khoản định danh điện tử: khi đó việc xuất trình, kiểm tra có "
    "thể thực hiện thông qua tài khoản định danh điện tử (khoản 3 Điều 56 " + LUAT + ").", l("d56:k3"))
add("tinh_huong", "Xe ô tô của tôi đang thế chấp ngân hàng, ngân hàng giữ bản gốc đăng ký. Khi lái xe tôi mang theo gì?",
    "Bạn mang theo bản sao chứng nhận đăng ký xe có chứng thực kèm bản gốc giấy tờ xác nhận còn hiệu lực của tổ chức tín dụng, chi "
    "nhánh ngân hàng nước ngoài đang giữ xe thế chấp (điểm a khoản 1 Điều 56 " + LUAT + ").", l("d56:k1:a"), l("d56:k1"))
add("quy_tac", "Người lái xe gắn máy có cần bằng lái không?",
    "Theo khoản 4 Điều 56 " + LUAT + ", người lái xe gắn máy phải hiểu biết quy tắc giao thông, có kỹ năng điều khiển phương tiện "
    "và đủ điều kiện về độ tuổi, sức khỏe theo điểm a khoản 1 và khoản 2 Điều 59; khoản 1 Điều 56 loại trừ người lái xe gắn máy "
    "khỏi yêu cầu có giấy phép lái xe.", l("d56:k4"), l("d56:k1"))
add("quy_tac", "Người điều khiển xe máy chuyên dùng phải có giấy tờ gì?",
    "Phải đủ tuổi, sức khỏe; có bằng hoặc chứng chỉ điều khiển xe máy chuyên dùng phù hợp; có giấy phép lái xe còn điểm, còn hiệu "
    "lực hoặc chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ; khi tham gia giao thông phải mang theo đăng ký xe, "
    "bằng hoặc chứng chỉ điều khiển, giấy phép lái xe hoặc chứng chỉ bồi dưỡng, chứng nhận kiểm định và bảo hiểm bắt buộc (khoản 2 "
    "Điều 56 " + LUAT + ").", l("d56:k2"), l("d56:k2:b"), l("d56:k2:c"))
add("quy_tac", "Người tập lái ô tô có được lái trên đường không?",
    "Người tập lái, người dự sát hạch lái xe ô tô khi tham gia giao thông phải thực hành trên xe tập lái, xe sát hạch, trên tuyến "
    "đường tập lái, sát hạch, có giáo viên dạy lái hoặc sát hạch viên bảo trợ tay lái; giáo viên, sát hạch viên phải mang theo giấy "
    "tờ như người lái xe (khoản 5 Điều 56 " + LUAT + ").", l("d56:k5"))

out = ROOT / "data/train/drafts/luat_loi_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
