"""Đợt 5a G5: Đăng kiểm, Thông tư 30/2026/TT-BXD (hiệu lực 01/7/2026). Ghi data/train/drafts/dang_kiem_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 30/2026/TT-BXD"
S = []
START = 1


def t(s):
    return f"tt_30_2026_bxd:{s}@2026-07-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"dkm-{START + len(S):04d}", "chu_de": "Đăng kiểm", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Khái niệm
add("quy_tac", "Miễn kiểm định lần đầu là gì, xe nào được miễn?",
    "Miễn kiểm định lần đầu là việc cơ sở đăng kiểm căn cứ kết quả chứng nhận chất lượng trong sản xuất, lắp ráp hoặc nhập "
    "khẩu để lập hồ sơ phương tiện và cấp giấy chứng nhận kiểm định, tem kiểm định mà không kiểm tra xe (khoản 6 Điều 3 " + TT
    + "). Đối tượng được miễn là xe cơ giới (trừ xe mô tô, xe gắn máy), xe máy chuyên dùng chưa qua sử dụng có năm sản xuất "
    "đến năm nộp hồ sơ dưới 02 năm (năm sản xuất cộng 01 năm), trừ xe đã cải tạo hoặc chưa được chứng nhận chất lượng (khoản "
    "7 Điều 3).", t("d3:k6"), t("d3:k7"))
add("doi_thuong", "mua ô tô mới thì có phải mang xe đi đăng kiểm ko",
    "Thường là không phải mang xe đến kiểm tra. Xe ô tô chưa qua sử dụng có năm sản xuất đến năm nộp hồ sơ dưới 02 năm thuộc "
    "đối tượng miễn kiểm định lần đầu (khoản 7 Điều 3 " + TT + "); chủ xe nộp ảnh số khung, số động cơ và 02 ảnh tổng thể "
    "xe để được cấp giấy chứng nhận kiểm định, tem kiểm định (khoản 1 Điều 4). Xe phải đã có chứng nhận đăng ký, biển số "
    "(khoản 1 Điều 3).", t("d3:k7"), t("d4:k1"), t("d3:k1"))
add("quy_tac", "Kiểm định định kỳ là gì?",
    "Kiểm định định kỳ là việc xe được kiểm định ở các lần tiếp theo sau khi xe đã được miễn kiểm định hoặc kiểm định lần "
    "đầu (khoản 10 Điều 3 " + TT + ").", t("d3:k10"))
add("quy_tac", "Kiểm định lần đầu đối với xe máy là kiểm tra cái gì?",
    "Kiểm định lần đầu đối với xe mô tô, xe gắn máy là việc cơ sở đăng kiểm kiểm tra, đánh giá khí thải của xe để cấp giấy "
    "chứng nhận kiểm định khí thải (khoản 9 Điều 3 " + TT + ").", t("d3:k9"))
add("quy_tac", "Giấy chứng nhận kiểm định bản điện tử là gì?",
    "Là giấy chứng nhận kiểm định được số hóa dưới dạng thông điệp dữ liệu, được tạo lập và quản lý qua hệ thống phần mềm "
    "quản lý kiểm định của Cục Đăng kiểm Việt Nam (khoản 18 Điều 3 " + TT + ").", t("d3:k18"))
add("quy_tac", "Đi đăng kiểm thì giấy tờ về đăng ký xe gồm những loại nào?",
    "Là một trong các giấy tờ: bản chính chứng nhận đăng ký xe hoặc giấy hẹn trả chứng nhận đăng ký xe; bản sao có chứng "
    "thực (hoặc bản sao điện tử được chứng thực) của các giấy đó; hoặc chứng nhận đăng ký xe, giấy hẹn trả được tích hợp trên "
    "tài khoản định danh điện tử VNeID, VNeTraffic (khoản 23 Điều 3 " + TT + ").", t("d3:k23"))
add("tinh_huong", "Xe của tôi thuộc diện bị nhà sản xuất triệu hồi nhưng chưa sửa. Đi đăng kiểm có được không?",
    "Hồ sơ không được coi là đạt yêu cầu nếu xe có lỗi thiết kế, chế tạo, lắp ráp đã bị triệu hồi theo công bố của nhà sản "
    "xuất, đã đăng trên hệ thống của Cục Đăng kiểm mà chưa khắc phục, trừ khi bạn xuất trình tài liệu chứng minh đã hoàn "
    "thành việc khắc phục do nhà sản xuất hoặc đại lý ủy quyền cấp (điểm đ khoản 21 Điều 3 " + TT + ").", t("d3:k21:đ"),
    t("d3:k21"))

# ===== Miễn kiểm định, kiểm định ô tô
add("thu_tuc", "Hồ sơ đề nghị miễn kiểm định lần đầu cho ô tô mới gồm những gì?",
    "Theo Điều 4 " + TT + ", phải nộp ảnh chụp số khung, số động cơ (hoặc bản chà) dán trên phiếu kiểm tra chất lượng xuất "
    "xưởng hoặc giấy tờ chất lượng xe nhập khẩu; 02 ảnh tổng thể chéo góc 30–45 độ phía trước và phía sau thể hiện rõ biển "
    "số; bản sao phiếu xuất xưởng hoặc giấy chứng nhận chất lượng chỉ khi dữ liệu chưa chia sẻ được. Phải xuất trình giấy tờ "
    "về đăng ký xe và giấy chứng nhận kiểm định thiết bị nâng, bình chịu áp lực (nếu có).",
    t("d4:k1"), t("d4:k1:a"), t("d4:k1:b"), t("d4:k2"))
add("quy_tac", "Ảnh chụp xe nộp kèm hồ sơ miễn kiểm định phải đạt yêu cầu gì?",
    "Gồm 02 ảnh tổng thể chéo góc khoảng 30 độ đến 45 độ phía trước và phía sau, thể hiện rõ biển số; độ phân giải tối thiểu "
    "1280x720 pixels, rõ nét, thể hiện thời gian thực khi chụp (ngày, tháng, năm, giờ, phút), xe chiếm tối thiểu 75% diện "
    "tích khung ảnh (điểm b khoản 1 Điều 4 " + TT + ").", t("d4:k1:b"), t("d4:k1"))
add("thu_tuc", "Nộp hồ sơ miễn kiểm định ở đâu và bao lâu có kết quả?",
    "Người nộp hồ sơ chọn bất kỳ cơ sở đăng kiểm nào trên cả nước, nộp trực tuyến trên Cổng Dịch vụ công quốc gia, ứng dụng "
    "đăng kiểm của Cục Đăng kiểm Việt Nam, hoặc nộp trực tiếp, qua bưu chính (khoản 1 Điều 5 " + TT + "). Cơ sở đăng kiểm "
    "kiểm tra và trả kết quả trong tối đa 04 giờ làm việc (khoản 2 Điều 5), cấp giấy chứng nhận kiểm định bản điện tử và tem "
    "kiểm định trong 04 giờ làm việc kể từ khi nhận đủ hồ sơ đạt yêu cầu (khoản 3 Điều 5).",
    t("d5:k1"), t("d5:k2"), t("d5:k3"))
add("doi_thuong", "đăng kiểm có phải về đúng tỉnh mình ko hay chỗ nào cũng được",
    "Chỗ nào cũng được. Người nộp hồ sơ được lựa chọn bất kỳ cơ sở đăng kiểm nào trên phạm vi cả nước để nộp hồ sơ kiểm định "
    "(khoản 1 Điều 9 " + TT + ").", t("d9:k1"))
add("thu_tuc", "Đi kiểm định định kỳ ô tô cần mang giấy tờ gì?",
    "Kiểm định định kỳ phải xuất trình giấy tờ về đăng ký xe và giấy chứng nhận kiểm định thiết bị nâng, bình chịu áp lực "
    "(với xe có lắp thiết bị này); chỉ phải nộp văn bản đề nghị nếu kiểm định ngoài cơ sở đăng kiểm (Điều 7 " + TT + ").",
    t("d7:k2"), t("d7:k2:a"), t("d7:k1"))
add("quy_tac", "Kiểm định ô tô gồm những công đoạn nào?",
    "Việc kiểm định phải thực hiện đầy đủ hạng mục theo quy chuẩn qua 05 công đoạn: kiểm tra nhận dạng, tổng quát; kiểm tra "
    "phần trên của phương tiện; kiểm tra hiệu quả phanh và trượt ngang; kiểm tra phần dưới của phương tiện; kiểm tra môi "
    "trường (điểm b khoản 3 Điều 9 " + TT + ").", t("d9:k3:b"), t("d9:k3"))
add("quy_tac", "Kiểm định ô tô có lỗi thì xử lý thế nào, khi nào không được chạy về?",
    "Theo điểm d khoản 3 Điều 9 " + TT + ": xe không có khiếm khuyết hoặc chỉ có khiếm khuyết không quan trọng (MiD) thì được "
    "cấp giấy chứng nhận; có khiếm khuyết quan trọng (MaD) thì phải sửa chữa để kiểm định lại; có khiếm khuyết nguy hiểm "
    "(DaD) thì không được tham gia giao thông và phải sửa chữa để kiểm định lại.", t("d9:k3:d"), t("d9:k3"))
add("thu_tuc", "Kiểm định ô tô tại trung tâm đăng kiểm thì bao lâu được cấp giấy chứng nhận?",
    "Trong ngày làm việc đối với trường hợp kiểm định tại cơ sở đăng kiểm (trong 02 ngày làm việc nếu kiểm định ngoài cơ sở "
    "đăng kiểm), cơ sở đăng kiểm cấp giấy chứng nhận kiểm định, tem kiểm định hoặc thông báo kết quả không đạt (khoản 5 Điều "
    "9 " + TT + ").", t("d9:k5"))
add("tinh_huong", "Xe tôi đăng kiểm không đạt, sửa xong kiểm định lại đạt. Thông tin không đạt cũ có bị lưu mãi không?",
    "Không. Trường hợp phương tiện có kết quả không đạt, được kiểm định lại và đạt yêu cầu thì cơ sở đăng kiểm gỡ thông tin "
    "không đạt trước đó ngay sau khi kết thúc việc kiểm tra, đánh giá (điểm b khoản 5 Điều 9 " + TT + "); phương tiện bị "
    "đăng thông tin vi phạm được gỡ ngay khi có kết quả kiểm định đạt (điểm b khoản 2 Điều 25).", t("d9:k5:b"),
    t("d25:k2:b"))
add("quy_tac", "Trường hợp nào được kiểm định xe bên ngoài trung tâm đăng kiểm?",
    "Kiểm định bên ngoài cơ sở đăng kiểm áp dụng cho: xe máy chuyên dùng; một số xe cơ giới (trừ xe máy) như xe hoạt động "
    "tại đảo không có cơ sở đăng kiểm, xe chỉ hoạt động trong cảng, mỏ, công trường, xe đang làm nhiệm vụ cấp bách phòng "
    "chống thiên tai, dịch bệnh, xe quá khổ, quá tải…; và kiểm định khí thải xe mô tô, xe gắn máy (khoản 14 Điều 3 " + TT
    + ").", t("d3:k14"), t("d3:k14:a"), t("d3:k14:b"), t("d3:k14:c"))
add("thu_tuc", "Xe đăng ký tạm thời cần kiểm định thì nộp giấy tờ gì?",
    "Phải xuất trình chứng nhận đăng ký xe tạm thời hoặc bản sao có chứng thực, và nộp giấy tờ tùy trường hợp, ví dụ bản sao "
    "phiếu kiểm tra chất lượng xuất xưởng với xe sản xuất trong nước hoặc xe di chuyển giữa kho, cảng, nhà máy, đại lý, nơi "
    "đăng ký (Điều 8 " + TT + ").", t("d8:k2"), t("d8:k1:a"), t("d8:k1:c"))

# ===== Khí thải xe máy, chu kỳ
add("doi_thuong", "xe máy có phải đi kiểm định khí thải ko, khi nào bắt đầu",
    "Có. Theo " + TT + ", kiểm định lần đầu với xe mô tô, xe gắn máy là kiểm tra, đánh giá khí thải để cấp giấy chứng nhận "
    "kiểm định khí thải (khoản 9 Điều 3). Thời điểm kiểm định lần đầu theo Quyết định của Thủ tướng Chính phủ về lộ trình áp "
    "dụng khí thải; ví dụ trong Phụ lục V nêu việc kiểm định khí thải được áp dụng từ 01/01/2028.", t("d3:k9"), t("pl5"))
add("quy_tac", "Chu kỳ kiểm định khí thải xe máy là bao lâu?",
    "Theo Bảng chu kỳ kiểm định tại Phụ lục V " + TT + ": xe mô tô, xe gắn máy có thời gian sản xuất đến 12 năm có chu kỳ 24 "
    "tháng; trên 12 năm có chu kỳ 12 tháng. Riêng xe có thời gian sản xuất đến 05 năm được áp dụng chu kỳ 60 tháng tính từ "
    "ngày xuất xưởng, chỉ một lần đầu tiên (trừ xe đã cải tạo động cơ, hệ thống xử lý khí thải hoặc không có trong cơ sở dữ "
    "liệu chứng nhận chất lượng).", t("pl5"))
add("tinh_huong", "Xe máy của tôi mới mua được 2 năm. Kiểm định khí thải lần đầu có phải mang xe đến trung tâm không?",
    "Không phải. Kiểm định lần đầu với xe có thời gian tính từ năm sản xuất không quá 05 năm (trừ xe đã cải tạo động cơ, hệ "
    "thống xử lý khí thải hoặc không có trong cơ sở dữ liệu chứng nhận chất lượng) không phải mang xe đến; cơ sở đăng kiểm "
    "kiểm tra hồ sơ và trả kết quả trong tối đa 04 giờ làm việc (khoản 2 Điều 14 " + TT + ").", t("d14:k2"), t("d3:k9"))
add("quy_tac", "Những trường hợp nào xe máy phải mang đến cơ sở đăng kiểm để kiểm định khí thải?",
    "Phải mang xe đến khi: kiểm định lần đầu với xe có thời gian tính từ năm sản xuất trên 05 năm; xe đã cải tạo động cơ, hệ "
    "thống xử lý khí thải; xe không có trong cơ sở dữ liệu chứng nhận chất lượng của Cục Đăng kiểm; xe kiểm định định kỳ; "
    "xe có chứng nhận đăng ký tạm thời (khoản 3 Điều 14 " + TT + ").", t("d14:k3"))
add("thu_tuc", "Hồ sơ kiểm định khí thải lần đầu cho xe máy gồm những gì?",
    "Theo Điều 11 " + TT + ": ảnh chụp số khung, số động cơ (hoặc bản chà) dán trên phiếu xuất xưởng hoặc giấy tờ chất lượng "
    "xe nhập khẩu; 02 ảnh tổng thể chéo góc 30–45 độ thể hiện rõ biển số (trừ trường hợp phải mang xe đến); bản sao phiếu "
    "xuất xưởng hoặc giấy chứng nhận chất lượng chỉ khi dữ liệu chưa chia sẻ được. Phải xuất trình giấy tờ về đăng ký xe.",
    t("d11:k1"), t("d11:k1:a"), t("d11:k1:b"), t("d11:k2"))
add("thu_tuc", "Kiểm định khí thải định kỳ cho xe máy cần giấy tờ gì?",
    "Chỉ cần xuất trình giấy tờ về đăng ký xe; xe đã cải tạo thì nộp bản chính giấy chứng nhận cải tạo khi dữ liệu chưa chia "
    "sẻ được (Điều 12 " + TT + "). Kiểm định định kỳ thì phải mang xe đến cơ sở đăng kiểm (khoản 3 Điều 14).",
    t("d12:k2"), t("d12:k1"), t("d14:k3"))
add("thu_tuc", "Xe máy kiểm định khí thải đạt thì nhận giấy chứng nhận khi nào?",
    "Ngay sau khi kết thúc kiểm định khí thải đạt yêu cầu, cơ sở đăng kiểm cấp giấy chứng nhận kiểm định khí thải xe mô tô, "
    "xe gắn máy bản điện tử trên hệ thống trực tuyến; nếu không đạt thì thông báo cho người nộp hồ sơ và nhập nội dung không "
    "đạt vào phần mềm quản lý phương tiện vi phạm (điểm d khoản 3 Điều 14 " + TT + ").", t("d14:k3:d"), t("d14:k3"))
add("quy_tac", "Thời hạn của giấy chứng nhận kiểm định được tính thế nào?",
    "Thời hạn hiệu lực được cấp theo chu kỳ kiểm định tại Phụ lục V nhưng không vượt quá ngày hết hạn của chứng nhận đăng ký "
    "xe hoặc hết ngày 31 tháng 12 của năm hết niên hạn sử dụng của xe, tùy điều kiện nào đến trước (khoản 2 Điều 18 " + TT
    + "). Với miễn kiểm định, kiểm định lần đầu và định kỳ, thời hạn bằng ngày kiểm định đạt cộng chu kỳ tương ứng trừ 01 ngày "
    "(Phụ lục V).", t("d18:k2"), t("pl5"))
add("tinh_huong", "Ô tô con 5 chỗ không kinh doanh, mới mua, được miễn kiểm định ngày 10/8/2026 thì giấy kiểm định có hạn "
    "đến khi nào?",
    "Theo ví dụ tại Phụ lục V " + TT + ", ô tô chở người đến 8 chỗ không kinh doanh vận tải, chưa qua sử dụng, có chu kỳ đầu "
    "là 36 tháng; xe nộp hồ sơ miễn kiểm định ngày 10/8/2026 được cấp giấy chứng nhận có thời hạn đến hết ngày 09/8/2029.",
    t("pl5"))
add("quy_tac", "Năm sản xuất của xe được tính thế nào để xác định chu kỳ kiểm định?",
    "Năm sản xuất của xe là căn cứ xác định chu kỳ kiểm định, và thời gian sản xuất được tính tròn theo năm. Ví dụ xe sản xuất "
    "năm 2025 thì đến hết ngày 31/12/2027 được tính là đã sản xuất đến 02 năm; từ ngày 01/01/2028 được tính là trên 02 năm "
    "(Phụ lục V " + TT + ").", t("pl5"))
add("tinh_huong", "Xe ô tô của tôi chuyển từ không kinh doanh sang chạy dịch vụ. Hạn đăng kiểm có thay đổi không?",
    "Có thể thay đổi. Khi chuyển từ không kinh doanh vận tải sang có kinh doanh vận tải và xin cấp lại giấy chứng nhận, thời "
    "hạn được tính lại từ ngày kiểm định của lần cấp trước cộng chu kỳ kiểm định của xe kinh doanh vận tải (ngắn hơn) trừ 01 "
    "ngày; nếu thời hạn tính lại đã qua thì cơ sở đăng kiểm từ chối cấp lại và xe phải kiểm định (Phụ lục V " + TT + ").",
    t("pl5"), t("d15:k2"))

# ===== Cấp lại, tem
add("quy_tac", "Khi nào được cấp lại giấy chứng nhận, tem kiểm định mà không phải kiểm định lại xe?",
    "Cấp lại trong các trường hợp: giấy chứng nhận, tem bị sai thông tin, bị hỏng, bị mất; xe thay đổi chứng nhận đăng ký, "
    "biển số; xe chuyển giữa không kinh doanh và có kinh doanh vận tải; xe có thay đổi nhưng không coi là cải tạo. Chủ xe "
    "không phải mang xe đến kiểm định lại (khoản 1 Điều 15 " + TT + ").", t("d15:k1"))
add("tinh_huong", "Tôi vừa sang tên, đổi biển số ô tô. Giấy đăng kiểm cũ còn hạn thì xử lý thế nào?",
    "Xe thay đổi chứng nhận đăng ký, biển số thuộc trường hợp được cấp lại giấy chứng nhận, tem kiểm định, không phải mang xe "
    "đi kiểm định lại (khoản 1 Điều 15 " + TT + "). Giấy cấp lại có thời hạn bằng thời hạn còn lại của giấy đã cấp (khoản 2 "
    "Điều 15). Hồ sơ gồm đơn đề nghị cấp lại và ảnh chụp xe thể hiện biển số mới, xuất trình giấy tờ về đăng ký xe (Điều "
    "16).", t("d15:k1"), t("d15:k2"), t("d16:k1:b"))
add("thu_tuc", "Tem đăng kiểm bị sai thông tin hoặc bị hỏng thì bao lâu được cấp lại?",
    "Cơ sở đăng kiểm cấp lại giấy chứng nhận, tem kiểm định trong 04 giờ làm việc kể từ khi nhận hồ sơ hợp lệ và thu hồi "
    "giấy, tem bị sai hoặc bị hỏng (nếu bị hỏng nhưng còn đủ thông tin xác định số sêri hoặc biển số) (khoản 1, khoản 2 Điều "
    "17 " + TT + ").", t("d17:k1"), t("d17:k2"))
add("tinh_huong", "Tôi làm mất tem đăng kiểm dán trên kính ô tô. Phải làm gì?",
    "Bạn nộp hồ sơ đề nghị cấp lại (đơn theo mẫu Phụ lục IX, xuất trình giấy tờ về đăng ký xe) trực tuyến hoặc trực tiếp, qua "
    "bưu chính tới cơ sở đăng kiểm (Điều 16, Điều 17 " + TT + "). Với trường hợp bị mất, cơ sở đăng kiểm lập giấy tiếp nhận "
    "thông tin báo mất và đăng thông tin báo mất trên phần mềm quản lý phương tiện vi phạm của Cục Đăng kiểm trước khi cấp "
    "lại (khoản 3 Điều 17).", t("d17:k3"), t("d16:k1:a"), t("d17"))
add("quy_tac", "Tem kiểm định ô tô có những màu nào?",
    "Đến hết ngày 31/12/2026, tem kiểm định in trên phần mềm gồm: màu xanh lá cây cho xe không phát thải trực tiếp các-bon "
    "(như PEV, BEV, FCEV, PFCEV); màu vàng cam cho các xe cơ giới khác; màu tím hồng cho xe máy chuyên dùng (khoản 3 Điều 18 "
    + TT + ").", t("d18:k3"), t("d18:k3:a"), t("d18:k3:b"), t("d18:k3:c"))
add("quy_tac", "Tem đăng kiểm ô tô dán ở vị trí nào?",
    "Với xe có ca bin và kính chắn gió phía trước, tem dán tại góc phía trên, bên phải (theo chiều tiến của xe), ở mặt trong "
    "kính chắn gió, mặt trước tem hướng ra ngoài (điểm a khoản 6 Điều 18 " + TT + "). Quy định dán tem này thực hiện đến hết "
    "ngày 31/12/2026 (khoản 6 Điều 18).", t("d18:k6:a"), t("d18:k6"))
add("quy_tac", "Xe được miễn kiểm định thì ai dán tem kiểm định?",
    "Tổ chức, cá nhân tự dán tem trong trường hợp xe được miễn kiểm định, được kiểm định ngoài cơ sở đăng kiểm hoặc được cấp "
    "lại; còn khi kiểm định tại cơ sở đăng kiểm thì nhân viên cơ sở dán (điểm c khoản 6 Điều 18 " + TT + ").",
    t("d18:k6:c"), t("d30:k2"))
add("thu_tuc", "Có thể xin giấy chứng nhận kiểm định bản giấy không?",
    "Có. Trường hợp người nộp hồ sơ đề nghị cấp bản giấy, cơ sở đăng kiểm in trực tiếp giấy chứng nhận kiểm định từ phần mềm "
    "quản lý kiểm định (không dùng phôi) và đóng dấu xác nhận để cấp (điểm đ khoản 1 Điều 18 " + TT + ").", t("d18:k1:đ"))
add("tinh_huong", "Tôi chỉ có giấy hẹn trả đăng ký xe, đi đăng kiểm có được cấp giấy chứng nhận ngay không?",
    "Nếu chưa có dữ liệu đăng ký xe được chia sẻ từ cơ quan đăng ký, cơ sở đăng kiểm cấp giấy hẹn cấp giấy chứng nhận kiểm "
    "định và chỉ cấp giấy chứng nhận khi có dữ liệu đăng ký xe được chia sẻ (điểm d khoản 1 Điều 18 " + TT + ").",
    t("d18:k1:d"))

# ===== Cải tạo, phương tiện vi phạm, trách nhiệm chủ xe
add("quy_tac", "Khi nào phải làm thủ tục chứng nhận xe cải tạo?",
    "Xe cơ giới, xe máy chuyên dùng có sự thay đổi so với xe trước cải tạo liền kề theo nguyên tắc xác định xe cải tạo tại Phụ "
    "lục XI thì phải làm thủ tục chứng nhận cải tạo (khoản 1 Điều 20 " + TT + ").", t("d20:k1"))
add("quy_tac", "Thay động cơ xăng bằng động cơ điện cho xe thì công suất phải thế nào?",
    "Trường hợp cải tạo động cơ, kể cả thay động cơ đốt trong bằng động cơ điện và ngược lại, động cơ cải tạo phải có công "
    "suất lớn nhất theo công bố trong khoảng 90% đến 120% so với công suất lớn nhất của động cơ theo thiết kế của nhà sản "
    "xuất xe (khoản 3 Điều 20 " + TT + ").", t("d20:k3"))
add("quy_tac", "Những kiểu cải tạo nào bắt buộc do nhà sản xuất xe thiết kế và thi công?",
    "Theo khoản 4 Điều 20 " + TT + ", gồm: thay đổi kích cỡ lốp, số trục, vết bánh xe; thay đổi khoảng cách giữa các trục; "
    "thay khung xe, nối dầm sát xi (trừ nối dài về phía sau); cải tạo hệ thống phanh, treo, lái (trừ một số trường hợp như "
    "lắp phanh phụ xe tập lái, cải tạo cho người khuyết tật); cải tạo xe chỉ hoạt động trên đường chuyên dùng; cải tạo giường "
    "nằm xe khách; cải tạo, thay hệ thống pin, ắc quy của xe điện, hybrid.", t("d20:k4"), t("d20:k4:a"), t("d20:k4:g"))
add("doi_thuong", "thay đèn pha ô tô loại khác có phải làm hồ sơ cải tạo ko",
    "Không phải lập hồ sơ thiết kế cải tạo nếu thay cụm đèn chiếu sáng phía trước bằng cụm đèn khác kiểu loại đã được chứng "
    "nhận hoặc công bố hợp quy, có công suất tương đương và việc lắp đặt không cần gia công thay đổi kết cấu xe (điểm i khoản "
    "5 Điều 20 " + TT + ").", t("d20:k5:i"), t("d20:k5"))
add("quy_tac", "Có được cải tạo cùng lúc cả khung và động cơ xe không?",
    "Không. Không được cải tạo đồng thời cả khung xe và động cơ (khoản 6 Điều 20 " + TT + ").", t("d20:k6"))
add("quy_tac", "Ô tô 16 chỗ cải tạo xuống dưới 8 chỗ thì có đổi loại phương tiện không?",
    "Không. Ô tô chở người trên 08 chỗ (không kể chỗ người lái) cải tạo thành dưới 08 chỗ thì không được thay đổi loại "
    "phương tiện (khoản 8 Điều 20 " + TT + ").", t("d20:k8"))
add("quy_tac", "Phương tiện như thế nào bị đăng tên trên danh sách vi phạm của Cục Đăng kiểm?",
    "Phương tiện vi phạm là phương tiện thuộc trường hợp bị từ chối kiểm định theo khoản 1 Điều 43 Luật Trật tự, an toàn giao "
    "thông đường bộ và phương tiện có kết quả kiểm định không đạt; thông tin được đăng trên phần mềm quản lý phương tiện vi "
    "phạm của Cục Đăng kiểm Việt Nam (khoản 1, điểm a khoản 2 Điều 25 " + TT + ").", t("d25:k1"), t("d25:k2:a"))
add("tinh_huong", "Ô tô của tôi bị phạt nguội chưa nộp, có bị chặn đăng kiểm không?",
    "Có thể bị chặn. Ủy ban nhân dân cấp tỉnh giao cơ quan chuyên môn đăng thông tin phương tiện vi phạm theo yêu cầu của cơ "
    "quan chức năng khi chủ phương tiện chưa thực hiện xong yêu cầu giải quyết vụ việc vi phạm hành chính về trật tự, an toàn "
    "giao thông (điểm a khoản 3 Điều 25 " + TT + "). Thông tin được gỡ khi có bằng chứng đã khắc phục nội dung vi phạm (điểm "
    "b khoản 2 Điều 25).", t("d25:k3:a"), t("d25:k2:b"))
add("quy_tac", "Chủ xe có trách nhiệm gì khi đi đăng kiểm?",
    "Theo Điều 30 " + TT + ": nộp giá dịch vụ, phí, lệ phí theo quy định; tự dán tem kiểm định trong các trường hợp được "
    "phép; không sử dụng giấy chứng nhận, tem kiểm định bị sửa chữa, tẩy xóa, làm giả; nộp lại tem, giấy chứng nhận khi có "
    "thông báo thu hồi; bảo dưỡng, sửa chữa xe định kỳ theo khuyến cáo của nhà sản xuất.", t("d30:k1"), t("d30:k3"),
    t("d30:k5"))

out = ROOT / "data/train/drafts/dang_kiem_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
