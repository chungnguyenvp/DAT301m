"""Đợt 3a G5: Đăng ký xe, Thông tư 79/2024/TT-BCA (bản đang có hiệu lực, đã sửa bởi TT 13/2025, TT 51/2025, TT 62/2026,
TT 37/2026). Ghi data/train/drafts/dang_ky_xe_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 79/2024/TT-BCA"
S = []
START = 1
A25, M25, J25, M26, J26 = "2025-01-01", "2025-03-01", "2025-07-01", "2026-05-18", "2026-06-08"


def t(s, d=A25):
    return f"tt_79_2024_bca:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"dk-{START + len(S):04d}", "chu_de": "Đăng ký xe", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def ref(where):
    return f"({where} {TT})"


# ===== Nguyên tắc đăng ký xe (Điều 3)
add("quy_tac", "Đăng ký xe ở cơ quan nào, có bắt buộc đăng ký nơi thường trú không?",
    "Chủ xe có trụ sở, nơi cư trú (nơi đăng ký thường trú, tạm trú) ở địa phương nào thì đăng ký xe tại cơ quan đăng ký xe "
    "thuộc địa phương đó (khoản 2 Điều 3 " + TT + "). Tổ chức, cá nhân trong nước được lựa chọn đăng ký xe tại Phòng Cảnh "
    "sát giao thông hoặc Công an xã, phường, đặc khu trong tỉnh, thành phố (khoản 9 Điều 3, nội dung có hiệu lực từ ngày "
    "01/7/2025).", t("d3:k2"), t("d3:k9", J25))
add("quy_tac", "Biển số định danh là gì?",
    "Biển số xe được quản lý theo mã định danh của chủ xe, gọi là biển số định danh. Với chủ xe là công dân Việt Nam, biển "
    "số được quản lý theo số định danh cá nhân; với người nước ngoài theo số định danh của người nước ngoài hoặc số thẻ "
    "thường trú, tạm trú; với tổ chức theo mã định danh điện tử của tổ chức, nếu chưa có thì theo mã số thuế hoặc số quyết "
    "định thành lập (khoản 3 Điều 3 " + TT + ").", t("d3:k3"), t("d3:k3:a"), t("d3:k3:b"), t("d3:k3:c"))
add("doi_thuong", "bán xe thì biển số định danh của mình có mất luôn ko",
    "Không mất ngay. Khi chuyển quyền sở hữu xe (hoặc xe hết niên hạn, hư hỏng), cơ quan đăng ký xe thu hồi biển số định "
    "danh và giữ lại số biển đó cho chủ xe trong thời hạn 05 năm để cấp lại khi chủ xe đăng ký cho xe khác của mình. Quá "
    "05 năm mà chưa đăng ký thì số biển được chuyển vào kho biển số để cấp cho người khác. Ngoại lệ: xe gắn với biển số "
    "trúng đấu giá được chuyển nhượng cùng biển (điểm d khoản 3 Điều 3 " + TT + ").", t("d3:k3:d"), t("d3:k3"))
add("thu_tuc", "Có thể nộp hồ sơ đăng ký xe theo những hình thức nào?",
    "Việc kê khai, nộp hồ sơ đăng ký xe được thực hiện qua cổng dịch vụ công (Cổng dịch vụ công quốc gia, Cổng dịch vụ công "
    "Bộ Công an…), qua Ứng dụng định danh quốc gia, hoặc trực tiếp tại cơ quan đăng ký xe (khoản 4 Điều 3 " + TT + ").",
    t("d3:k4"), t("d3:k4:a"), t("d3:k4:b"), t("d3:k4:c"))
add("thu_tuc", "Lệ phí đăng ký xe nộp bằng cách nào?",
    "Lệ phí đăng ký xe nộp qua ngân hàng hoặc trung gian thanh toán được kết nối với cổng dịch vụ công, hoặc nộp trực tiếp "
    "tại cơ quan đăng ký xe (khoản 5 Điều 3 " + TT + ").", t("d3:k5"))
add("thu_tuc", "Hiện nay nhận giấy đăng ký xe bằng cách nào, có bản điện tử không?",
    "Có. Chủ xe được lựa chọn nhận chứng nhận đăng ký xe bản vật lý (qua bưu chính hoặc tại cơ quan đăng ký xe) hoặc nhận "
    "dữ liệu điện tử chứng nhận đăng ký xe qua cổng dịch vụ công, ứng dụng định danh quốc gia (VNeID), ứng dụng giao thông "
    "VNeTraffic (khoản 6 Điều 3 " + TT + ", nội dung có hiệu lực từ ngày 18/5/2026).", t("d3:k6", M26))
add("quy_tac", "Chưa nộp phạt vi phạm giao thông thì có đăng ký xe được không?",
    "Chưa được. Tổ chức, cá nhân vi phạm pháp luật về trật tự, an toàn giao thông đường bộ mà chưa thực hiện xong yêu cầu "
    "của cơ quan có thẩm quyền về giải quyết vụ việc vi phạm hành chính thì chưa được giải quyết việc đăng ký phương tiện vi "
    "phạm (khoản 10 Điều 3 " + TT + ").", t("d3:k10"))
add("quy_tac", "Trúng đấu giá biển số thì đăng ký xe ở đâu?",
    "Tổ chức, cá nhân trúng đấu giá biển số được lựa chọn đăng ký, cấp biển số trúng đấu giá tại các cơ quan đăng ký xe "
    "trong tỉnh, thành phố nơi mình có trụ sở, cư trú, hoặc tại Phòng Cảnh sát giao thông quản lý biển số trúng đấu giá đó "
    "(khoản 8 Điều 3 " + TT + ", nội dung có hiệu lực từ ngày 01/7/2025).", t("d3:k8", J25))

# ===== Cơ quan đăng ký xe (Điều 4)
add("doi_thuong", "công an xã có đăng ký được ô tô ko hay phải lên tỉnh",
    "Được. Công an cấp xã đăng ký xe ô tô, xe máy chuyên dùng, xe mô tô của tổ chức, cá nhân trong nước có trụ sở, cư trú "
    "trong tỉnh, thành phố (trừ xe có nguồn gốc tịch thu và các xe thuộc thẩm quyền của Cục Cảnh sát giao thông) (khoản 4 "
    "Điều 4 " + TT + ", nội dung có hiệu lực từ ngày 01/7/2025). Việc đăng ký xe ô tô, xe máy chuyên dùng của Công an cấp "
    "xã do Giám đốc Công an tỉnh thống nhất với Cục trưởng Cục Cảnh sát giao thông quyết định theo tình hình thực tế "
    "(khoản 5 Điều 4).", t("d4:k4", J25), t("d4:k5", J25))
add("quy_tac", "Phòng Cảnh sát giao thông cấp tỉnh đăng ký những loại xe nào?",
    "Phòng Cảnh sát giao thông đăng ký xe ô tô, rơ moóc, sơ mi rơ moóc, xe chở người, chở hàng bốn bánh có gắn động cơ, xe "
    "mô tô, xe gắn máy và xe máy chuyên dùng của tổ chức, cá nhân có trụ sở, cư trú trong tỉnh, thành phố, trừ các xe thuộc "
    "thẩm quyền của Cục Cảnh sát giao thông (khoản 2 Điều 4 " + TT + ", nội dung có hiệu lực từ ngày 01/7/2025).",
    t("d4:k2", J25))

# ===== Trách nhiệm của chủ xe (Điều 6)
add("thu_tuc", "Đi đăng ký xe có phải mang xe đến cơ quan đăng ký không?",
    "Chủ xe phải đưa xe đến cơ quan đăng ký xe để kiểm tra khi cấp mới chứng nhận đăng ký, biển số (trừ trường hợp đăng ký "
    "trực tuyến toàn trình), khi cấp chứng nhận đăng ký do thay đổi chủ xe, và khi đổi chứng nhận đăng ký do cải tạo, thay "
    "đổi màu sơn (khoản 2 Điều 6 " + TT + ").", t("d6:k2"))
add("tinh_huong", "Tôi mua xe máy mới ở đại lý, đăng ký trực tuyến toàn trình trên VNeID thì có phải chở xe đến công an "
    "không?",
    "Không phải đưa xe đến kiểm tra. Công dân Việt Nam đăng ký lần đầu xe sản xuất, lắp ráp hoặc nhập khẩu bằng dịch vụ công "
    "trực tuyến toàn trình dùng tài khoản định danh điện tử mức độ 2 để kê khai, nộp hồ sơ. Khi nhận kết quả, chủ xe phải nộp "
    "phiếu kiểm tra chất lượng xuất xưởng có dán bản chà số máy, số khung được đóng dấu giáp lai của cơ sở sản xuất (với xe "
    "sản xuất lắp ráp) hoặc giấy tờ chất lượng tương ứng của xe nhập khẩu (khoản 3 Điều 6 " + TT + ").", t("d6:k3"))
add("quy_tac", "Đổi tên hoặc cải tạo xe thì trong bao lâu phải làm thủ tục đổi giấy đăng ký?",
    "Trong thời hạn 30 ngày kể từ ngày được cấp giấy chứng nhận an toàn kỹ thuật và bảo vệ môi trường xe cải tạo, hoặc thay "
    "đổi thông tin về tên chủ xe, số định danh của chủ xe, hoặc khi chứng nhận đăng ký hết thời hạn, chủ xe phải đến cơ quan "
    "đăng ký xe làm thủ tục đổi hoặc thu hồi chứng nhận đăng ký xe, biển số xe (khoản 4 Điều 6 " + TT + ").", t("d6:k4"))
add("doi_thuong", "bán xe có phải đưa cà vẹt với biển số cho người mua ko",
    "Không. Khi chuyển quyền sở hữu xe, chủ xe phải giữ lại chứng nhận đăng ký xe, biển số xe (không giao cho người nhận) "
    "và nộp cho cơ quan đăng ký xe khi làm thủ tục thu hồi. Nếu chuyển xe kèm biển số trúng đấu giá thì chủ xe chỉ nộp "
    "chứng nhận đăng ký xe (điểm a khoản 5 Điều 6 " + TT + ").", t("d6:k5:a"), t("d6:k5"))
add("tinh_huong", "Tôi bán xe cho người khác. Tôi phải làm thủ tục gì và trong bao lâu?",
    "Trong thời hạn 30 ngày kể từ ngày làm giấy tờ chuyển quyền sở hữu xe, chủ xe đứng tên trong chứng nhận đăng ký xe phải "
    "làm thủ tục thu hồi chứng nhận đăng ký xe, biển số xe. Quá thời hạn mà không làm thì bị xử phạt vi phạm hành chính "
    "trước khi được giải quyết (điểm b khoản 5 Điều 6 " + TT + "). Sau khi thu hồi, người mua làm thủ tục cấp chứng nhận "
    "đăng ký xe, biển số xe theo quy định (điểm c khoản 5 Điều 6).", t("d6:k5:b"), t("d6:k5:c"))
add("quy_tac", "Đã bán xe nhưng chưa làm thủ tục thu hồi đăng ký thì người đứng tên có còn chịu trách nhiệm không?",
    "Có. Tổ chức, cá nhân đứng tên trong giấy chứng nhận đăng ký xe tiếp tục chịu trách nhiệm của chủ xe khi chưa thực hiện "
    "thu hồi chứng nhận đăng ký xe, biển số xe đối với trường hợp phải thu hồi (khoản 7 Điều 6 " + TT + ").", t("d6:k7"))
add("quy_tac", "Xe hết niên hạn hoặc hư hỏng không dùng được nữa thì chủ xe phải làm gì?",
    "Trong thời hạn 07 ngày làm việc kể từ ngày xe hết niên hạn, hư hỏng không sử dụng được hoặc bị thải bỏ, chủ xe phải "
    "khai báo trên cổng dịch vụ công hoặc kê khai trực tiếp tại cơ quan đăng ký xe, và nộp chứng nhận đăng ký xe, biển số "
    "xe cho cơ quan đăng ký xe hoặc Công an cấp xã (không phụ thuộc nơi cư trú) để làm thủ tục thu hồi (khoản 6 Điều 6 " + TT
    + ").", t("d6:k6"))

# ===== Thời hạn giải quyết (Điều 7, bản từ 18/5/2026)
add("thu_tuc", "Đăng ký xe mới thì bao lâu có biển số và giấy đăng ký?",
    "Biển số mới được cấp ngay sau khi nhận đủ hồ sơ hợp lệ; chứng nhận đăng ký xe được cấp không quá 02 ngày làm việc kể "
    "từ ngày nhận đủ hồ sơ hợp lệ (điểm a khoản 1, điểm a khoản 2 Điều 7 " + TT + ", nội dung có hiệu lực từ ngày "
    "18/5/2026). Với trường hợp phải nộp lệ phí, thời hạn tính từ khi nhận đủ hồ sơ và chủ xe nộp xong lệ phí (khoản 5 "
    "Điều 7).", t("d7:k1:a", M26), t("d7:k2:a", M26), t("d7:k5", M26))
add("thu_tuc", "Đổi biển số hoặc cấp biển số trúng đấu giá mất bao lâu?",
    "Cấp mới biển số trúng đấu giá, đổi biển số xe, cấp biển số định danh: không quá 07 ngày làm việc kể từ ngày nhận đủ hồ "
    "sơ hợp lệ (điểm b khoản 2 Điều 7 " + TT + ", nội dung có hiệu lực từ ngày 18/5/2026).", t("d7:k2:b", M26),
    t("d7:k2", M26))
add("thu_tuc", "Mất giấy đăng ký xe, xin cấp lại thì bao lâu có?",
    "Cấp lại chứng nhận đăng ký xe không quá 02 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ, và chứng nhận cấp lại phải "
    "thể hiện rõ lần cấp lại (điểm b khoản 1 Điều 7 " + TT + ", nội dung có hiệu lực từ ngày 18/5/2026). Cấp lại biển số "
    "thì không quá 07 ngày làm việc (điểm c khoản 2 Điều 7).", t("d7:k1:b", M26), t("d7:k2:c", M26))
add("thu_tuc", "Làm thủ tục thu hồi đăng ký, biển số khi bán xe thì mất bao lâu?",
    "Nếu làm bằng dịch vụ công trực tuyến toàn trình: không quá 08 giờ làm việc kể từ khi nhận đủ hồ sơ hợp lệ. Nếu làm trực "
    "tuyến một phần hoặc trực tiếp tại cơ quan đăng ký xe: không quá 02 ngày làm việc (điểm a, điểm b khoản 3 Điều 7 " + TT
    + ", nội dung có hiệu lực từ ngày 18/5/2026).", t("d7:k3:a", M26), t("d7:k3:b", M26))
add("thu_tuc", "Xin cấp chứng nhận đăng ký xe tạm thời mất bao lâu?",
    "Làm trực tuyến toàn trình: không quá 08 giờ làm việc kể từ khi nhận đủ hồ sơ hợp lệ; làm trực tuyến một phần hoặc trực "
    "tiếp: 01 ngày làm việc (khoản 4 Điều 7 " + TT + ", nội dung có hiệu lực từ ngày 18/5/2026).",
    t("d7:k4", M26), t("d7:k4:a", M26), t("d7:k4:b", M26))

# ===== Hồ sơ (Điều 8, 10)
add("thu_tuc", "Hồ sơ đăng ký xe lần đầu gồm những giấy tờ gì?",
    "Theo Điều 8 " + TT + ", hồ sơ cấp mới chứng nhận đăng ký xe, biển số xe gồm: giấy khai đăng ký xe; giấy tờ của chủ "
    "xe; chứng nhận nguồn gốc xe; chứng nhận quyền sở hữu hợp pháp; chứng từ hoàn thành nghĩa vụ tài chính.",
    t("d8"), t("d8:k1"), t("d8:k5"))
add("thu_tuc", "Người Việt Nam đi đăng ký xe cần xuất trình giấy tờ gì của chủ xe?",
    "Chủ xe là người Việt Nam dùng tài khoản định danh điện tử mức độ 2 để đăng ký xe trên cổng dịch vụ công hoặc Ứng dụng "
    "định danh quốc gia, hoặc xuất trình căn cước, thẻ căn cước công dân, hộ chiếu (khoản 1 Điều 10 " + TT + ", nội dung có "
    "hiệu lực từ ngày 01/3/2025).", t("d10:k1", M25))
add("thu_tuc", "Người nước ngoài sống và làm việc ở Việt Nam đăng ký xe cần giấy tờ gì?",
    "Người nước ngoài sinh sống và làm việc tại Việt Nam (không phải thành viên cơ quan ngoại giao, lãnh sự, tổ chức quốc "
    "tế) xuất trình thẻ thường trú hoặc thẻ tạm trú còn thời hạn cư trú tại Việt Nam từ 06 tháng trở lên (điểm b khoản 2 "
    "Điều 10 " + TT + ").", t("d10:k2:b"), t("d10:k2"))
add("tinh_huong", "Tôi bận nên nhờ người khác đi đăng ký xe hộ. Người đó cần mang gì?",
    "Người được ủy quyền, ngoài giấy tờ của chủ xe theo quy định, còn phải xuất trình giấy tờ tùy thân và nộp văn bản ủy "
    "quyền có công chứng hoặc chứng thực theo quy định (khoản 4 Điều 10 " + TT + ").", t("d10:k4"))

# ===== Đăng ký lần đầu (Điều 14)
add("thu_tuc", "Đăng ký xe trực tuyến toàn trình thì bấm biển số và nộp lệ phí thế nào?",
    "Chủ xe bấm biển số trên cổng dịch vụ công hoặc Ứng dụng định danh quốc gia, nhận thông báo biển số được cấp và số tiền "
    "lệ phí qua tin nhắn, thư điện tử hoặc trên Ứng dụng định danh quốc gia, rồi nộp tiền qua tiện ích thanh toán tích hợp "
    "trên cổng dịch vụ công hoặc ứng dụng; sau khi thanh toán thành công, hệ thống thông báo hoàn thành nộp lệ phí (điểm b "
    "khoản 1 Điều 14 " + TT + ").", t("d14:k1:b"), t("d14:k1"))
add("tinh_huong", "Biển số định danh của tôi đã bị thu hồi khi bán xe cũ. Giờ mua xe mới thì có được cấp lại số biển cũ không?",
    "Theo điểm b khoản 2 Điều 14 " + TT + ", chủ xe có biển số định danh đã được thu hồi từ ngày 15/8/2023 thì được cấp lại "
    "biển số định danh đó; trường hợp chưa có biển số định danh, hoặc biển định danh đang đăng ký cho xe khác, thì được cấp "
    "biển số mới. Nếu muốn dùng lại chính tấm biển định danh cũ đã thu hồi thì chỉ được khi cơ quan đăng ký xe chưa tiêu hủy "
    "biển đó (điểm c khoản 2 Điều 14).", t("d14:k2:b"), t("d14:k2:c"))
add("thu_tuc", "Đăng ký xe bằng dịch vụ công trực tuyến một phần thì làm như thế nào?",
    "Chủ xe kê khai giấy khai đăng ký xe trực tuyến, nhận mã hồ sơ và lịch hẹn qua tin nhắn hoặc thư điện tử; sau đó đưa xe "
    "đến cơ quan đăng ký xe để kiểm tra, cung cấp mã hồ sơ và nộp các giấy tờ của chủ xe, nguồn gốc xe, quyền sở hữu, nghĩa "
    "vụ tài chính; đồng thời chọn hình thức nhận kết quả (điểm a khoản 2 Điều 14 " + TT + ", nội dung có hiệu lực từ ngày "
    "18/5/2026).", t("d14:k2:a", M26), t("d14:k2"))

# ===== Sang tên (Điều 15–17)
add("thu_tuc", "Mua xe cũ khác tỉnh thì sang tên làm ở đâu?",
    "Theo Điều 15 " + TT + ", khi chuyển quyền sở hữu xe, chủ xe cũ làm thủ tục thu hồi tại cơ quan đăng ký xe nơi chủ xe "
    "cũ có trụ sở, cư trú; người nhận chuyển quyền sở hữu làm thủ tục đăng ký sang tên tại cơ quan đăng ký xe theo nơi mình "
    "có trụ sở, cư trú.", t("d15:k1"), t("d15:k2"))
add("thu_tuc", "Hồ sơ thu hồi chứng nhận đăng ký xe, biển số xe khi bán xe gồm những gì?",
    "Theo khoản 1 Điều 16 " + TT + " (nội dung có hiệu lực từ ngày 18/5/2026), hồ sơ gồm: giấy khai thu hồi chứng nhận đăng "
    "ký xe, biển số xe; giấy tờ của chủ xe; 02 bản chà số máy, số khung (không cần nếu làm trên môi trường điện tử và được "
    "cấp chứng nhận thu hồi điện tử); bản sao chứng từ chuyển quyền sở hữu xe; chứng nhận đăng ký xe, biển số xe (nếu mất "
    "thì ghi rõ lý do trong giấy khai).", t("d16:k1", M26), t("d16:k1:c", M26), t("d16:k1:đ", M26))
add("thu_tuc", "Người mua xe cũ cần hồ sơ gì để đăng ký sang tên?",
    "Theo khoản 2 Điều 16 " + TT + ", hồ sơ đăng ký gồm: giấy khai đăng ký xe; giấy tờ của chủ xe; chứng từ chuyển quyền sở "
    "hữu; chứng từ lệ phí trước bạ; chứng nhận thu hồi chứng nhận đăng ký xe, biển số xe.", t("d16:k2"), t("d16:k2:d"),
    t("d16:k2:đ"))
add("tinh_huong", "Tôi mua xe cũ đang gắn biển 4 số kiểu cũ. Khi sang tên có phải đổi biển không?",
    "Có. Khi người mua nhận chứng nhận đăng ký xe sang tên, trường hợp biển số xe đã cấp là biển 3 số hoặc biển 4 số thì "
    "đổi sang biển số định danh theo quy định (điểm d khoản 2 Điều 17 " + TT + ", nội dung có hiệu lực từ ngày 01/3/2025).",
    t("d17:k2:d", M25), t("d17:k2"))
add("quy_tac", "Làm thủ tục thu hồi trực tuyến khi bán xe, trong lúc chờ kết quả có được dùng biển số không?",
    "Được. Trong thời gian chờ nhận kết quả thu hồi, chủ xe được giữ lại biển số xe để sử dụng và phải nộp lại khi nhận "
    "chứng nhận thu hồi; nếu không nộp lại biển số thì cơ quan đăng ký xe hủy kết quả (điểm đ khoản 1 Điều 16 " + TT + ", "
    "nội dung có hiệu lực từ ngày 18/5/2026).", t("d16:k1:đ", M26), t("d16:k1", M26))
add("quy_tac", "Chứng từ chuyển quyền sở hữu xe dạng điện tử trên Cổng dịch vụ công có giá trị như bản giấy không?",
    "Có, khi dữ liệu về tình trạng hôn nhân của chủ xe đã được cập nhật trên Cơ sở dữ liệu quốc gia về dân cư: khi đó dữ "
    "liệu điện tử chuyển quyền sở hữu trên Cổng dịch vụ công có giá trị pháp lý như chứng từ chuyển quyền sở hữu bản giấy "
    "(điểm c khoản 2 Điều 16 " + TT + ", nội dung có hiệu lực từ ngày 08/6/2026).", t("d16:k2:c", J26), t("d16:k2"))
add("quy_tac", "Bán xe, chủ cũ được cấp mấy bản chứng nhận thu hồi và có xin được đăng ký tạm thời không?",
    "Cơ quan đăng ký xe cấp 02 bản chứng nhận thu hồi chứng nhận đăng ký xe, biển số xe (01 bản trả chủ xe, 01 bản lưu hồ "
    "sơ). Nếu chủ xe có nhu cầu thì được cấp chứng nhận đăng ký xe tạm thời cùng với chứng nhận thu hồi, không phải có hồ "
    "sơ đăng ký tạm thời riêng (điểm b khoản 1 Điều 17 " + TT + ").", t("d17:k1:b"), t("d17:k1"))

# ===== Đổi chứng nhận đăng ký, biển số (Điều 18–20)
add("quy_tac", "Những trường hợp nào phải đổi chứng nhận đăng ký xe, biển số xe?",
    "Theo Điều 18 " + TT + ", gồm: chứng nhận đăng ký, biển số bị mờ, hỏng; xe cải tạo, thay đổi màu sơn; chuyển biển trắng "
    "sang biển vàng (xe kinh doanh vận tải) hoặc ngược lại; thay đổi thông tin chủ xe (tên, số định danh) hoặc chủ xe có "
    "nhu cầu đổi theo địa chỉ mới; chứng nhận đăng ký hết thời hạn sử dụng; đổi giấy tờ, biển số cũ sang loại theo Thông "
    "tư, hoặc đổi biển ngắn sang biển dài và ngược lại.", t("d18:k1"), t("d18:k2"), t("d18:k4"), t("d18:k6"))
add("tinh_huong", "Tôi sơn lại ô tô sang màu khác. Tôi phải làm thủ tục gì?",
    "Xe thay đổi màu sơn thuộc trường hợp phải đổi chứng nhận đăng ký xe (khoản 2 Điều 18 " + TT + "). Chủ xe kê khai giấy "
    "khai đăng ký xe, nộp hồ sơ đổi và lệ phí; với xe thay đổi màu sơn, chủ xe phải mang xe đến để kiểm tra (khoản 1 Điều 20).",
    t("d18:k2"), t("d20:k1"))
add("tinh_huong", "Tôi chuyển nơi ở sang tỉnh khác. Có bắt buộc phải đổi biển số xe không?",
    "Không bắt buộc đổi biển. Đổi chứng nhận đăng ký theo địa chỉ mới là trường hợp theo nhu cầu của chủ xe (khoản 4 Điều 18 "
    + TT + "), và khi đổi thì giữ nguyên biển số định danh (khoản 2 Điều 20, nội dung có hiệu lực từ ngày 18/5/2026). Nếu "
    "muốn đổi tại nơi ở mới ngoài phạm vi cơ quan đã đăng ký, chủ xe nộp chứng nhận đăng ký và đơn đề nghị xác nhận hồ sơ "
    "xe cho cơ quan quản lý hồ sơ để được cấp giấy xác nhận hồ sơ xe, rồi nộp giấy này cho cơ quan đăng ký xe tại địa chỉ "
    "mới (khoản 3 Điều 20).", t("d18:k4"), t("d20:k2", M26), t("d20:k3"))
add("thu_tuc", "Hồ sơ đổi chứng nhận đăng ký xe, biển số xe gồm những gì?",
    "Theo Điều 19 " + TT + ", hồ sơ gồm: giấy khai đăng ký xe; giấy tờ của chủ xe; chứng nhận đăng ký xe (nếu đổi chứng "
    "nhận) hoặc biển số xe (nếu đổi biển); và một số giấy tờ khác tùy trường hợp, ví dụ xe cải tạo thay tổng thành máy, "
    "khung thì phải có chứng nhận nguồn gốc, chứng từ lệ phí trước bạ, chứng từ chuyển quyền sở hữu của tổng thành đó.",
    t("d19:k1"), t("d19:k3"), t("d19:k4:a"))
add("quy_tac", "Đưa xe ô tô vào kinh doanh vận tải thì có phải đổi biển số không?",
    "Có. Xe đã đăng ký biển nền trắng, chữ và số đen chuyển sang hoạt động kinh doanh vận tải bằng ô tô phải đổi sang biển "
    "nền màu vàng, chữ và số màu đen (khoản 3 Điều 18 " + TT + "); khi đổi giữa biển trắng và biển vàng, cơ quan đăng ký "
    "cấp biển số định danh mới (khoản 2 Điều 20, nội dung có hiệu lực từ ngày 18/5/2026).", t("d18:k3"), t("d20:k2", M26))
add("quy_tac", "Thôi kinh doanh vận tải, muốn đổi biển vàng về biển trắng cần thêm giấy tờ gì?",
    "Trường hợp đổi biển số nền màu vàng sang biển số nền màu trắng, ngoài hồ sơ đổi thông thường phải có thêm văn bản thu "
    "hồi giấy phép kinh doanh vận tải hoặc văn bản thu hồi phù hiệu, biển hiệu (điểm d khoản 4 Điều 19 " + TT + ").",
    t("d19:k4:d"), t("d19:k4"))

# ===== Cấp lại (Điều 21, bản từ 18/5/2026)
add("thu_tuc", "Mất giấy đăng ký xe thì xin cấp lại trực tuyến như thế nào?",
    "Theo khoản 1 Điều 21 " + TT + " (nội dung có hiệu lực từ ngày 18/5/2026), chủ xe có thể làm trực tuyến toàn trình (trừ "
    "xe còn đăng ký biển 3 số hoặc 4 số): kê khai giấy khai đăng ký xe, nộp bản chà số máy, số khung qua dịch vụ bưu chính "
    "công ích cho cơ quan đăng ký xe và chọn hình thức nhận kết quả; sau khi hồ sơ hợp lệ, chủ xe nhận thông báo để nộp lệ "
    "phí và phí bưu chính trên cổng dịch vụ công.", t("d21:k1", M26), t("d21:k1:a", M26), t("d21:k1:b", M26))
add("quy_tac", "Cấp lại giấy đăng ký hoặc biển số thì có bị đổi số biển không?",
    "Không, nếu xe đã có biển số định danh: cấp lại chứng nhận đăng ký xe, biển số xe giữ nguyên biển số định danh. Riêng xe "
    "đã đăng ký biển 3 số hoặc 4 số thì được cấp sang biển số định danh (thu lại giấy tờ, biển cũ). Chứng nhận đăng ký cấp "
    "lại phải thể hiện rõ lần cấp lại (khoản 3 Điều 21 " + TT + ", nội dung có hiệu lực từ ngày 18/5/2026).",
    t("d21:k3", M26))

# ===== Đăng ký tạm thời (Điều 22, 24)
add("quy_tac", "Giấy đăng ký xe tạm thời có giá trị bao lâu?",
    "Với xe làm thủ tục thu hồi để tái xuất hoặc chuyển quyền sở hữu, và xe mới di chuyển từ nhà máy, kho, cảng, đại lý đến "
    "nơi đăng ký hoặc kho khác: chứng nhận đăng ký xe tạm thời có giá trị 15 ngày, được gia hạn một lần tối đa không quá 15 "
    "ngày (khoản 1 Điều 24 " + TT + ").", t("d24:k1"))
add("quy_tac", "Xe chạy thử nghiệm phục vụ nghiên cứu phát triển được đăng ký tạm thời trong bao lâu?",
    "Chứng nhận đăng ký xe tạm thời ghi theo thời hạn đề nghị của cơ quan, tổ chức có xe chạy thử nghiệm nhưng không quá 6 "
    "tháng; trường hợp cần thiết được gia hạn, mỗi lần không quá 6 tháng (khoản 3 Điều 24 " + TT + ").", t("d24:k3"))
add("quy_tac", "Xe đăng ký tạm thời có được chạy đi bất cứ đâu không?",
    "Không. Xe đăng ký tạm thời chỉ được tham gia giao thông theo thời hạn, tuyến đường và phạm vi hoạt động ghi trong "
    "chứng nhận đăng ký xe tạm thời (khoản 5 Điều 24 " + TT + ").", t("d24:k5"))
add("thu_tuc", "Hồ sơ xin đăng ký xe tạm thời gồm những gì?",
    "Theo Điều 22 " + TT + ", hồ sơ gồm giấy khai đăng ký xe, giấy tờ của chủ xe và chứng nhận nguồn gốc xe (ví dụ dữ liệu "
    "điện tử hoặc bản phô tô phiếu kiểm tra chất lượng xuất xưởng, giấy chứng nhận an toàn kỹ thuật xe nhập khẩu khi xe di "
    "chuyển từ nhà máy, kho, cảng, đại lý đến nơi đăng ký).", t("d22:k1"), t("d22:k2"), t("d22:k3:a"))

# ===== Thu hồi (Điều 25, 26)
add("thu_tuc", "Xe bị hỏng không dùng được nữa, muốn thu hồi đăng ký trực tuyến thì làm thế nào?",
    "Với xe hết niên hạn, hư hỏng không sử dụng được, bị thải bỏ hoặc bị mất không tìm được, chủ xe kê khai giấy khai thu "
    "hồi trên cổng dịch vụ công và nộp chứng nhận đăng ký xe, biển số xe qua dịch vụ bưu chính; cơ quan đăng ký xe cấp chứng "
    "nhận thu hồi dưới dạng điện tử, ký số và trả kết quả trên cổng dịch vụ công (khoản 1 Điều 26 " + TT + ", nội dung có "
    "hiệu lực từ ngày 18/5/2026).", t("d26:k1", M26), t("d26:k1:a", M26), t("d26:k1:b", M26))
add("quy_tac", "Bán xe gắn biển số trúng đấu giá thì thu hồi những gì?",
    "Trường hợp chuyển nhượng, trao đổi, tặng cho, để thừa kế xe gắn với biển số trúng đấu giá thì chỉ thu hồi chứng nhận "
    "đăng ký xe (khoản 1 Điều 25 " + TT + "); biển số trúng đấu giá đi cùng xe.", t("d25:k1"))
add("quy_tac", "Phát hiện hồ sơ xe bị làm giả sau khi đã đăng ký thì xử lý thế nào?",
    "Cơ quan đăng ký xe ra quyết định thu hồi chứng nhận đăng ký xe, biển số xe và thu lại giấy tờ, biển số, không phải có "
    "hồ sơ thu hồi. Cách xử lý này cũng áp dụng khi cấp đăng ký, biển số không đúng quy định, hoặc khi có kết luận về việc "
    "thay đổi trái phép số khung, số máy (khoản 3 Điều 25 " + TT + ").", t("d25:k3"))

# ===== Biển số, thời hạn đăng ký (Điều 35, 37)
add("quy_tac", "Ô tô được gắn mấy biển số và kích thước biển là bao nhiêu?",
    "Xe ô tô, xe máy chuyên dùng được gắn 02 biển số: 01 biển kích thước ngắn cao 165 mm, dài 330 mm và 01 biển kích thước "
    "dài cao 110 mm, dài 520 mm (khoản 3 Điều 37 " + TT + ").", t("d37:k3"))
add("quy_tac", "Biển số xe máy có kích thước bao nhiêu?",
    "Xe mô tô được cấp biển số gắn phía sau xe, kích thước chiều cao 140 mm, chiều dài 190 mm (khoản 4 Điều 37 " + TT + ").",
    t("d37:k4"))
add("doi_thuong", "biển số vàng là xe gì vậy",
    "Biển số xe ô tô nền màu vàng, chữ và số màu đen cấp cho xe hoạt động kinh doanh vận tải bằng ô tô (điểm đ khoản 5 Điều "
    "37 " + TT + ").", t("d37:k5:đ"), t("d37:k5"))
add("quy_tac", "Biển số nền xanh chữ trắng cấp cho xe của những cơ quan nào?",
    "Biển số ô tô nền màu xanh, chữ và số màu trắng cấp cho xe của các cơ quan của Đảng; Văn phòng Chủ tịch nước; Văn phòng "
    "Quốc hội và các cơ quan của Quốc hội; Hội đồng nhân dân các cấp; Công an nhân dân, Tòa án nhân dân, Viện kiểm sát nhân "
    "dân; các bộ, cơ quan ngang bộ, cơ quan thuộc Chính phủ; Ủy ban nhân dân các cấp; tổ chức chính trị - xã hội… (điểm a "
    "khoản 5 Điều 37 " + TT + ", nội dung có hiệu lực từ ngày 01/7/2025).", t("d37:k5:a", J25), t("d37:k5"))
add("quy_tac", "Biển số có seri CD, RM, HC là của loại xe nào?",
    "Seri CD cấp cho xe máy chuyên dùng; seri RM cấp cho rơ moóc, sơ mi rơ moóc; seri HC cấp cho xe ô tô phạm vi hoạt động "
    "hạn chế, xe chở người bốn bánh gắn động cơ, xe chở hàng bốn bánh gắn động cơ; seri KT cấp cho xe của doanh nghiệp quân "
    "đội (điểm e khoản 5 Điều 37 " + TT + ").", t("d37:k5:e"), t("d37:k5"))
add("quy_tac", "Biển số có ký hiệu NG, QT, NN là xe của ai?",
    "Biển NG (nền trắng, chữ đỏ, số đen) cấp cho xe của cơ quan đại diện ngoại giao, cơ quan lãnh sự và nhân viên nước ngoài "
    "mang chứng minh thư ngoại giao; biển QT cấp cho xe của cơ quan đại diện tổ chức quốc tế và nhân viên mang chứng minh thư "
    "ngoại giao của tổ chức đó; biển NN (nền trắng, chữ và số đen) cấp cho xe của tổ chức, văn phòng đại diện, cá nhân nước "
    "ngoài khác (khoản 6 Điều 37 " + TT + ").", t("d37:k6:a"), t("d37:k6:b"), t("d37:k6:d"))
add("quy_tac", "Xe tải có phải kẻ số biển số lên thành xe không?",
    "Có. Các loại xe ô tô (trừ xe ô tô con), chủ xe phải kẻ hoặc dán số biển số ở thành sau và hai bên thành xe; kẻ tên cơ "
    "quan, đơn vị, khối lượng hàng chuyên chở, khối lượng bản thân vào hai bên cánh cửa xe (trừ xe của cá nhân) (khoản 8 "
    "Điều 37 " + TT + ").", t("d37:k8"))
add("doi_thuong", "biển số xe bị gãy có tự ra tiệm làm lại được ko",
    "Không. Biển số xe phải được sản xuất tại các doanh nghiệp, cơ sở sản xuất biển số của Bộ Công an theo yêu cầu của cơ "
    "quan đăng ký xe (khoản 9 Điều 37 " + TT + "). Biển số bị mờ, hỏng thì làm thủ tục đổi biển tại cơ quan đăng ký xe "
    "(khoản 1 Điều 18).", t("d37:k9"), t("d18:k1"))
add("quy_tac", "Giấy đăng ký xe ô tô tải, ô tô khách có thời hạn không?",
    "Có. Chứng nhận đăng ký xe ô tô tải, ô tô khách, xe cải tạo được ghi theo niên hạn sử dụng theo quy định của pháp luật "
    "(khoản 1 Điều 35 " + TT + ").", t("d35:k1"))

out = ROOT / "data/train/drafts/dang_ky_xe_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
