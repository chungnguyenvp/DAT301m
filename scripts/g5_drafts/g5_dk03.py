"""Đợt 11a G5: thủ tục đăng ký xe (TT 79/2024) ở các Điều chưa có mẫu thủ tục: các bước sang tên, đổi, cấp lại trực
tiếp, đăng ký tạm thời và gia hạn, thu hồi khi mất hoặc hư hỏng, xe tịch thu, thanh lý, đóng lại số máy, số khung, biểu
mẫu. Ghi data/train/drafts/dang_ky_xe_03.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 79/2024/TT-BCA"
S = []
START = 101


def t(s, d="2025-01-01"):
    return f"tt_79_2024_bca:{s}@{d}"


M18 = "2026-05-18"


def add(loai, q, a, *can_cu):
    S.append({"key": f"dk-{START + len(S):04d}", "chu_de": "Đăng ký xe", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Sang tên, thu hồi khi bán xe (Điều 6, 16, 17)
add("thu_tuc", "Người mua xe cũ làm thủ tục đăng ký sang tên theo những bước nào?",
    "Theo khoản 2 Điều 17 " + TT + ": (1) kê khai giấy khai đăng ký xe theo Điều 9, đưa xe đến để kiểm tra và nộp hồ sơ "
    "theo khoản 2 Điều 16; (2) hồ sơ và thực tế xe hợp lệ thì cơ quan đăng ký xe cấp chứng nhận đăng ký xe, biển số xe; "
    "(3) nhận giấy hẹn trả kết quả, nộp lệ phí đăng ký xe, nhận biển số (nếu được cấp biển) và chọn hình thức nhận kết "
    "quả; (4) nhận chứng nhận đăng ký xe tại cơ quan đăng ký xe hoặc qua đơn vị dịch vụ bưu chính. Xe đang mang biển 3 số "
    "hoặc biển 4 số thì được đổi sang biển số định danh.",
    t("d17:k2:a"), t("d17:k2:b"), t("d17:k2:c", M18), t("d17:k2:d", "2025-03-01"))
add("thu_tuc", "Bán xe thì chủ cũ kê khai giấy khai thu hồi đăng ký ở đâu, theo mẫu nào?",
    "Chủ xe kê khai giấy khai thu hồi chứng nhận đăng ký xe, biển số xe trên cổng dịch vụ công (cung cấp mã hồ sơ đăng ký "
    "xe trực tuyến) hoặc kê khai theo mẫu ĐKX11 tại cơ quan đăng ký xe; sau đó nộp hồ sơ thu hồi theo khoản 1 Điều 16 và "
    "nhận giấy hẹn trả kết quả (điểm a khoản 1 Điều 17 " + TT + ").", t("d17:k1:a"), t("d17:k1"))
add("thu_tuc", "Người mua xe cũ có cần giấy chứng nhận thu hồi đăng ký của chủ cũ không?",
    "Có. Người nhận chuyển quyền sở hữu chỉ làm thủ tục cấp chứng nhận đăng ký xe, biển số xe sau khi cơ quan đăng ký xe đã "
    "làm thủ tục thu hồi cho chủ cũ (điểm c khoản 5 Điều 6 " + TT + "), và hồ sơ đăng ký sang tên phải có chứng nhận thu hồi "
    "chứng nhận đăng ký xe, biển số xe (điểm đ khoản 2 Điều 16).", t("d6:k5:c"), t("d16:k2:đ"), t("d16:k2"))

# ===== Đổi, cấp lại (Điều 18–21)
add("thu_tuc", "giấy đăng ký xe bị mờ rách thì đi đổi thế nào",
    "Chứng nhận đăng ký xe bị mờ, hỏng thuộc trường hợp được đổi (khoản 1 Điều 18 " + TT + "). Chủ xe kê khai giấy khai "
    "đăng ký xe theo Điều 9, nộp hồ sơ đổi theo Điều 19 (trong đó có chứng nhận đăng ký xe cũ) và nộp lệ phí, bằng dịch vụ "
    "công trực tuyến một phần hoặc trực tiếp tại cơ quan đăng ký xe (khoản 1 Điều 20). Khi đổi vẫn giữ nguyên biển số định "
    "danh (khoản 2 Điều 20).", t("d18:k1"), t("d19:k3"), t("d20:k1"), t("d20:k2", M18))
add("thu_tuc", "Chuyển nơi ở sang tỉnh khác, muốn đổi giấy đăng ký xe theo địa chỉ mới thì làm những bước nào?",
    "Theo khoản 3 Điều 20 " + TT + ": (a) nộp chứng nhận đăng ký xe và đơn đề nghị xác nhận hồ sơ xe (mẫu ĐKX13) cho cơ "
    "quan đăng ký xe đang quản lý hồ sơ xe để được cấp giấy xác nhận hồ sơ xe; (b) kê khai giấy khai đăng ký xe và nộp giấy "
    "xác nhận hồ sơ xe cho cơ quan đăng ký xe tại địa chỉ mới để đổi chứng nhận đăng ký xe. Giấy xác nhận hồ sơ xe theo mẫu "
    "ĐKX14 là giấy tờ phải có thêm trong hồ sơ đổi (điểm đ khoản 4 Điều 19).",
    t("d20:k3"), t("d20:k3:a"), t("d20:k3:b"), t("d19:k4:đ"))
add("thu_tuc", "Xe cải tạo thay máy hoặc thay khung thì hồ sơ đổi đăng ký cần thêm giấy tờ gì?",
    "Ngoài giấy khai, giấy tờ của chủ xe và chứng nhận đăng ký xe, xe cải tạo thay đổi tổng thành máy, tổng thành khung phải "
    "có thêm chứng nhận nguồn gốc, chứng từ nộp lệ phí trước bạ, chứng từ chuyển quyền sở hữu của tổng thành đó; nếu tổng "
    "thành không cùng kiểu loại thì có thêm giấy chứng nhận an toàn kỹ thuật và bảo vệ môi trường xe cải tạo (điểm a khoản "
    "4 Điều 19 " + TT + "). Thay tổng thành máy lấy từ xe đã đăng ký thì phải có chứng nhận thu hồi đăng ký, biển số của xe "
    "có tổng thành đó (điểm b). Khi làm thủ tục, chủ xe phải mang xe đến để kiểm tra (khoản 1 Điều 20).",
    t("d19:k4:a"), t("d19:k4:b"), t("d20:k1"))
add("thu_tuc", "Cải tạo xe làm thay đổi kiểu loại xe thì đổi giấy đăng ký cần thêm giấy gì?",
    "Phải có thêm giấy chứng nhận an toàn kỹ thuật và bảo vệ môi trường xe cơ giới, xe máy chuyên dùng cải tạo theo quy "
    "định (điểm c khoản 4 Điều 19 " + TT + "), và mang xe đến cơ quan đăng ký xe để kiểm tra (khoản 1 Điều 20).",
    t("d19:k4:c"), t("d20:k1"))
add("thu_tuc", "Cấp lại giấy đăng ký xe trực tiếp tại cơ quan đăng ký thì phải nộp những gì?",
    "Chủ xe kê khai giấy khai đăng ký xe theo Điều 9, nộp hồ sơ theo khoản 1 và khoản 2 Điều 19 (giấy khai đăng ký xe, giấy "
    "tờ của chủ xe) và nộp lệ phí, chọn hình thức nhận kết quả (điểm a khoản 2 Điều 21 " + TT + "). Chứng nhận đăng ký xe "
    "cấp lại phải thể hiện rõ lần cấp lại (điểm b khoản 2 Điều 21).",
    t("d21:k2:a", M18), t("d21:k2:b", M18), t("d19:k1"), t("d19:k2"))

# ===== Đăng ký lần đầu: trực tiếp, giấy khai, giấy tờ khi nhận kết quả (Điều 5, 6, 9, 14, 34)
add("thu_tuc", "Đăng ký xe trực tiếp tại cơ quan đăng ký (không làm qua mạng) thì các bước thế nào?",
    "Chủ xe kê khai giấy khai đăng ký xe theo Điều 9, đưa xe đến cơ quan đăng ký xe để kiểm tra và nộp các giấy tờ quy định "
    "tại các điều 10, 11, 12 và 13 (khoản 3 Điều 14 " + TT + "). Hồ sơ và xe hợp lệ thì được cấp biển số; chủ xe nhận giấy "
    "hẹn trả kết quả, nộp lệ phí đăng ký xe, nhận biển số và nhận kết quả tại cơ quan đăng ký xe hoặc qua dịch vụ bưu chính "
    "(các điểm b, c, d khoản 2 Điều 14).",
    t("d14:k3", M18), t("d14:k2:b"), t("d14:k2:c"), t("d14:k2:d", "2025-03-01"))
add("thu_tuc", "Đăng ký xe trực tuyến toàn trình thì khi nhận giấy đăng ký phải nộp giấy tờ gì?",
    "Khi nhận kết quả, chủ xe nộp phiếu kiểm tra chất lượng xuất xưởng có dán bản chà số máy, số khung của xe được đóng dấu "
    "giáp lai của cơ sở sản xuất (xe sản xuất, lắp ráp) hoặc giấy chứng nhận chất lượng an toàn kỹ thuật và bảo vệ môi "
    "trường xe nhập khẩu, thông báo miễn kiểm tra có dán bản chà số (xe nhập khẩu) (khoản 3 Điều 6 " + TT + "). Nếu không "
    "nộp hoặc bản chà số máy, số khung không đúng với thông tin đã kê khai thì phải mang xe đến cơ quan đăng ký xe để kiểm "
    "tra và nhận kết quả (điểm d khoản 1 Điều 14).", t("d6:k3"), t("d14:k1:d"))
add("thu_tuc", "Kê khai đăng ký xe trực tuyến một phần mà không có chữ ký số thì làm sao?",
    "Chủ xe in giấy khai đăng ký xe từ cổng dịch vụ công, ký, ghi rõ họ, tên và đóng dấu (nếu là cơ quan, tổ chức) (khoản 1 "
    "Điều 9 " + TT + "). Nếu làm trực tiếp tại cơ quan đăng ký xe thì chỉ cần kê khai chính xác, đầy đủ, trung thực theo "
    "mẫu giấy khai (khoản 3 Điều 9).", t("d9:k1"), t("d9:k3"))
add("thu_tuc", "Giấy khai đăng ký xe có tự in ra được không?",
    "Được. Giấy khai đăng ký xe là mẫu ĐKX10; mẫu này cùng giấy khai thu hồi (ĐKX11), phiếu hướng dẫn hồ sơ (ĐKX12), đơn "
    "đề nghị xác nhận hồ sơ xe (ĐKX13) được in từ cổng dịch vụ công, hệ thống đăng ký, quản lý xe hoặc tự in; khi in không "
    "được thay đổi nội dung của biểu mẫu (khoản 5, khoản 6 Điều 34 " + TT + ").",
    t("d34:k2:k"), t("d34:k5"), t("d34:k6"))
add("thu_tuc", "Cơ quan đăng ký xe có nhận hồ sơ vào thứ bảy, chủ nhật không?",
    "Cơ quan đăng ký xe tiếp nhận hồ sơ các ngày làm việc trong tuần. Trường hợp cần thiết, Giám đốc Công an cấp tỉnh quyết "
    "định và thông báo công khai việc tiếp nhận đăng ký xe ngoài giờ làm việc, ngày nghỉ, ngày lễ (khoản 1 Điều 5 " + TT
    + ").", t("d5:k1"))
add("thu_tuc", "Hồ sơ đăng ký xe của tôi còn thiếu giấy tờ thì cán bộ đăng ký xử lý thế nào?",
    "Cán bộ đăng ký xe phải hướng dẫn cụ thể, đầy đủ, ghi nội dung hướng dẫn vào phiếu hướng dẫn hồ sơ và chịu trách nhiệm "
    "về nội dung hướng dẫn đó (khoản 3 Điều 5 " + TT + "); chủ xe bổ sung, hoàn thiện hồ sơ theo phiếu hướng dẫn (điểm b "
    "khoản 2 Điều 14). Phiếu hướng dẫn hồ sơ là mẫu ĐKX12 (điểm m khoản 2 Điều 34).",
    t("d5:k3"), t("d14:k2:b"), t("d34:k2:m"))
add("tinh_huong", "Cán bộ đăng ký xe đòi tôi nộp thêm giấy tờ ngoài quy định. Như vậy có đúng không?",
    "Không đúng. Cán bộ đăng ký xe phải thực hiện theo Thông tư 79/2024/TT-BCA và pháp luật liên quan, không được yêu cầu "
    "thêm các thủ tục đăng ký xe trái với quy định của Thông tư này (khoản 4 Điều 5).", t("d5:k4"))
add("thu_tuc", "Nộp lệ phí đăng ký xe trực tuyến có cần tài khoản ngân hàng không?",
    "Có. Chủ xe phải có tài khoản ngân hàng khi nộp và khi nhận hoàn trả trực tuyến lệ phí đăng ký xe (khoản 1 Điều 6 " + TT
    + ").", t("d6:k1"))

# ===== Đăng ký tạm thời (Điều 23, 24)
add("thu_tuc", "Đăng ký xe tạm thời trực tuyến toàn trình làm thế nào?",
    "Cách này áp dụng cho xe đã có dữ liệu điện tử phiếu kiểm tra chất lượng xuất xưởng hoặc dữ liệu điện tử chứng nhận an "
    "toàn kỹ thuật bảo vệ môi trường xe nhập khẩu trên cổng dịch vụ công. Chủ xe kê khai giấy khai đăng ký xe trên cổng "
    "dịch vụ công; hồ sơ hợp lệ thì cơ quan đăng ký xe thông báo để nộp lệ phí; chủ xe nhận kết quả xác thực và in chứng "
    "nhận đăng ký xe tạm thời trên cổng dịch vụ công (khoản 1 Điều 23 " + TT + ").",
    t("d23:k1"), t("d23:k1:a"), t("d23:k1:b"))
add("thu_tuc", "Đăng ký xe tạm thời trực tiếp thì làm ở cơ quan đăng ký nào?",
    "Chủ xe được làm thủ tục tại cơ quan đăng ký xe nơi thuận tiện: kê khai giấy khai đăng ký xe theo Điều 9 và nộp giấy tờ "
    "đăng ký xe tạm thời theo Điều 22; hồ sơ hợp lệ thì cơ quan đăng ký xe thu lệ phí và cấp chứng nhận đăng ký xe tạm "
    "thời, biển số xe tạm thời (khoản 2 Điều 23 " + TT + ").", t("d23:k2:a"), t("d23:k2:b"))
add("thu_tuc", "Muốn gia hạn giấy đăng ký xe tạm thời thì làm ở đâu và được gia hạn bao lâu?",
    "Chủ xe kê khai giấy khai đăng ký xe tạm thời trên cổng dịch vụ công hoặc trực tiếp tại cơ quan đăng ký xe (khoản 4 "
    "Điều 24 " + TT + "). Xe di chuyển từ nhà máy, kho, cảng, đại lý đến nơi đăng ký xe có chứng nhận tạm thời 15 ngày, được "
    "gia hạn một lần tối đa không quá 15 ngày (khoản 1); xe chạy thử nghiệm nghiên cứu phát triển được gia hạn mỗi lần không "
    "quá 6 tháng (khoản 3).", t("d24:k4"), t("d24:k1"), t("d24:k3"))

# ===== Thu hồi khi mất, hư hỏng, hết niên hạn (Điều 16, 25, 26, 27)
add("thu_tuc", "Xe bị mất trộm không tìm được, muốn thu hồi đăng ký thì hồ sơ gồm những gì?",
    "Xe bị mất không tìm được và chủ xe đề nghị thu hồi thì hồ sơ theo các điểm a, b và đ khoản 1 Điều 16 (khoản 2 Điều 25 "
    + TT + "): giấy khai thu hồi chứng nhận đăng ký xe, biển số xe; giấy tờ của chủ xe theo Điều 10; chứng nhận đăng ký xe, "
    "biển số xe, trường hợp bị mất thì ghi rõ lý do trong giấy khai thu hồi.",
    t("d25:k2"), t("d16:k1:a", M18), t("d16:k1:b", M18), t("d16:k1:đ", M18))
add("thu_tuc", "Xe hết niên hạn, làm thủ tục thu hồi trực tiếp tại cơ quan đăng ký thì được cấp mấy bản chứng nhận?",
    "Chủ xe kê khai giấy khai thu hồi trên cổng dịch vụ công hoặc trực tiếp tại cơ quan đăng ký xe, nộp hồ sơ theo Điều 25 "
    "và nhận giấy hẹn (điểm a khoản 2 Điều 26 " + TT + "). Hồ sơ hợp lệ thì được cấp 02 bản chứng nhận thu hồi: 01 bản trả "
    "cho chủ xe, 01 bản lưu hồ sơ xe (điểm b khoản 2 Điều 26).", t("d26:k2:a", M18), t("d26:k2:b", M18))
add("thu_tuc", "Khi nào làm thủ tục thu hồi đăng ký xe không cần nộp bản chà số máy, số khung?",
    "Khi thủ tục thu hồi thực hiện trên môi trường điện tử và được cấp chứng nhận thu hồi điện tử (điểm c khoản 1 Điều 16 "
    + TT + "). Việc này chỉ áp dụng khi cơ quan đăng ký xe đã hoàn thành số hóa, lưu trữ và quản lý dữ liệu số máy, số khung "
    "trên hệ thống đăng ký, quản lý xe; nếu chưa đáp ứng thì vẫn phải nộp bản chà số máy, số khung (khoản 3 Điều 26).",
    t("d16:k1:c", M18), t("d26:k3", M18))
add("thu_tuc", "Nhận được thông báo ô tô hết niên hạn thì trong bao lâu phải làm thủ tục thu hồi?",
    "Cơ quan đăng ký xe rà soát danh sách xe ô tô hết niên hạn sử dụng và thông báo cho chủ xe làm thủ tục thu hồi. Trong "
    "thời hạn 30 ngày kể từ ngày thông báo mà chủ xe không làm thủ tục thu hồi thì người có thẩm quyền xử phạt vi phạm hành "
    "chính theo quy định (điểm a khoản 1 Điều 27 " + TT + ").", t("d27:k1:a"))
add("thu_tuc", "Cơ quan đăng ký xe báo cho chủ xe về xe hết niên hạn, xe mất cắp bằng cách nào?",
    "Cơ quan đăng ký xe thông báo cho chủ xe qua địa chỉ thư điện tử hoặc qua tin nhắn điện thoại hoặc cổng dịch vụ công, "
    "đồng thời thông báo danh sách cho Công an các đơn vị, địa phương để phát hiện, xử lý (điểm c khoản 1 Điều 27 " + TT
    + ").", t("d27:k1:c"))
add("thu_tuc", "Ô tô bị tai nạn hư hỏng hoàn toàn thì giấy đăng ký và biển số được xử lý thế nào?",
    "Xe tai nạn giao thông bị phá hủy không sử dụng được thì cơ quan thụ lý giải quyết vụ tai nạn tạm giữ chứng nhận đăng "
    "ký xe, biển số xe và thông báo bằng văn bản cho cơ quan đã đăng ký xe để làm thủ tục thu hồi (điểm c khoản 2 Điều 27 "
    + TT + ").", t("d27:k2:c"))
add("thu_tuc", "Công an xã có thu hồi đăng ký của ô tô hết niên hạn không?",
    "Có. Căn cứ danh sách xe ô tô hết niên hạn sử dụng do cơ quan đăng ký xe cung cấp, Công an cấp xã thông báo chủ xe "
    "hoặc người đang sử dụng xe trên địa bàn, thu hồi chứng nhận đăng ký xe, biển số xe và cấp chứng nhận thu hồi (bản giấy "
    "hoặc bản điện tử). Công an cấp xã chưa được phân cấp đăng ký xe thì thu hồi rồi bàn giao cho đơn vị đã được phân cấp "
    "(điểm b khoản 2 Điều 27 " + TT + ").", t("d27:k2:b", "2025-03-01"))

# ===== Giấy tờ nguồn gốc, sở hữu, lệ phí trong trường hợp riêng (Điều 4, 11, 12, 13)
add("thu_tuc", "Mua xe tịch thu bán đấu giá thì khi đăng ký cần giấy tờ nguồn gốc gì?",
    "Cần quyết định tịch thu (hoặc quyết định xác lập quyền sở hữu toàn dân, trích lục bản án tịch thu) là bản chính cấp "
    "cho từng xe, ghi đủ nhãn hiệu, số loại, loại xe, số máy, số khung, dung tích xi lanh, năm sản xuất; xe phải nguyên "
    "chiếc (điểm a khoản 3 Điều 11 " + TT + "), kèm hóa đơn bán tài sản công, tài sản nhà nước, tài sản tịch thu hoặc biên "
    "bản bàn giao, tiếp nhận tài sản nếu xử lý theo hình thức điều chuyển (điểm b). Xe có nguồn gốc tịch thu không đăng ký "
    "tại Công an cấp xã (khoản 4 Điều 4).",
    t("d11:k3:a"), t("d11:k3:b", "2025-03-01"), t("d4:k4", "2025-07-01"))
add("thu_tuc", "Mua xe thanh lý của Công an hoặc Quân đội thì cần giấy tờ chứng minh sở hữu gì?",
    "Xe của cơ quan Công an thanh lý: quyết định thanh lý xe của cấp có thẩm quyền và hóa đơn theo quy định (khoản 3 Điều "
    "12 " + TT + "). Xe của cơ quan Quân đội thanh lý: văn bản xác nhận xe đã được loại khỏi trang bị quân sự của Cục Xe - "
    "Máy, Bộ Quốc phòng và hóa đơn theo quy định (khoản 4 Điều 12).", t("d12:k3"), t("d12:k4"))
add("thu_tuc", "Xe được miễn lệ phí trước bạ thì khi đăng ký nộp giấy tờ gì thay chứng từ nộp lệ phí?",
    "Phải có thông báo nộp lệ phí trước bạ xe của cơ quan quản lý thuế, trong đó có thông tin miễn lệ phí trước bạ xe "
    "(khoản 2 Điều 13 " + TT + ").", t("d13:k2"))

# ===== Đóng lại số máy, số khung (Điều 31)
add("thu_tuc", "Xe nhập khẩu không có số máy hoặc số khung thì đăng ký thế nào?",
    "Cơ quan đăng ký xe đóng lại số máy hoặc số khung theo số của biển số xe. Nếu kiểm tra thực tế tìm thấy số máy, số khung "
    "thì yêu cầu cơ quan Hải quan xác nhận lại (xe chưa đăng ký) hoặc xác nhận của nhà sản xuất được hợp thức hóa lãnh sự "
    "(xe đã đăng ký) (điểm a khoản 1 Điều 31 " + TT + "). Việc đóng lại số luôn do cơ quan đăng ký xe thực hiện (khoản 3).",
    t("d31:k1:a"), t("d31:k3"))
add("thu_tuc", "Xe chỉ có số VIN, không có số máy, số khung thì đăng ký ra sao?",
    "Cơ quan đăng ký xe đóng lại số khung theo số VIN và đóng lại số máy theo số biển số (điểm b khoản 1 Điều 31 " + TT
    + ").", t("d31:k1:b"), t("d31:k3"))
add("thu_tuc", "Thay tổng thành máy mới chưa có số thì đăng ký thế nào?",
    "Trường hợp thay tổng thành máy, thân máy (Block), tổng thành khung chưa có số thì cơ quan đăng ký xe đóng số máy, số "
    "khung theo số của biển số xe (điểm d khoản 1 Điều 31 " + TT + ").", t("d31:k1:d"), t("d31:k3"))

# ===== Quy định chuyển tiếp, biển đấu giá, năm sản xuất (Điều 30, 36, 38, 39)
add("quy_tac", "Năm sản xuất của xe khi đăng ký được xác định thế nào?",
    "Năm sản xuất được xác định qua dữ liệu điện tử do cơ quan đăng kiểm chia sẻ với hệ thống đăng ký, quản lý xe; xe nhập "
    "khẩu không có dữ liệu điện tử thì chủ xe xuất trình giấy chứng nhận chất lượng hoặc thông báo miễn kiểm tra (khoản 1 "
    "Điều 36 " + TT + "). Các trường hợp khác xác định theo ký tự thứ 10 của số khung xe (khoản 2).", t("d36:k1"), t("d36:k2"))
add("quy_tac", "Giấy đăng ký, biển số xe máy chuyên dùng do ngành giao thông vận tải cấp trước đây còn dùng được đến khi nào?",
    "Được tiếp tục sử dụng đến hết ngày 31 tháng 12 năm 2026; từ ngày 01 tháng 01 năm 2027 phải sử dụng chứng nhận đăng ký "
    "xe, biển số xe theo " + TT + " (khoản 7 Điều 39).", t("d39:k7"))
add("tinh_huong", "Xe tôi vẫn mang biển 4 số kiểu cũ. Có bắt buộc phải đổi sang biển số định danh không?",
    "Không bắt buộc ngay. Xe đã đăng ký biển 3 số, biển 4 số tiếp tục được phép tham gia giao thông; khi chủ xe có nhu cầu "
    "hoặc khi làm thủ tục đổi, cấp lại chứng nhận đăng ký xe, biển số xe hoặc đăng ký sang tên thì đổi sang biển số theo "
    "Thông tư 79/2024/TT-BCA (khoản 3 Điều 39).", t("d39:k3"))
add("quy_tac", "Biển 5 số đăng ký trước khi Thông tư 79/2024 có hiệu lực mà chưa thu hồi thì có thành biển định danh không?",
    "Có. Thông tư có hiệu lực từ ngày 01 tháng 01 năm 2025 (khoản 1 Điều 38); xe đã đăng ký biển 5 số trước ngày đó mà chưa "
    "làm thủ tục thu hồi thì số biển đó được xác định là biển số định danh của chủ xe, trừ biển có ký hiệu “MK”, “TĐ”, "
    "“LD”, “DA”, “MĐ”, “R”, “CT”, “LB”, “CD” (khoản 1 Điều 39 " + TT + ").", t("d39:k1"), t("d38:k1"))
add("tinh_huong", "Tôi trúng đấu giá biển số mới cho chiếc xe đang gắn biển đấu giá cũ. Biển cũ có bị mất không?",
    "Không mất. Khi chủ xe đăng ký biển số trúng đấu giá khác cho xe đã đăng ký biển trúng đấu giá, số biển cũ được cơ quan "
    "đăng ký xe giữ lại và cấp khi chủ xe đăng ký xe khác (chưa có biển số) thuộc sở hữu của mình (khoản 1 Điều 30 " + TT
    + ").", t("d30:k1"))

out = ROOT / "data/train/drafts/dang_ky_xe_03.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
