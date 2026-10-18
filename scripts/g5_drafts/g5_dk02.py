"""Đợt 3b G5: Đăng ký xe. Đấu giá biển số (NĐ 156/2024, Luật 36 Điều 37–38) và hồ sơ chi tiết, trường hợp đặc biệt
của TT 79/2024 (Điều 9–13, 28–33). Ghi data/train/drafts/dang_ky_xe_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 79/2024/TT-BCA"
ND = "Nghị định 156/2024/NĐ-CP"
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
S = []
START = 61


def t(s, d="2025-01-01"):
    return f"tt_79_2024_bca:{s}@{d}"


def n(s):
    return f"nd_156_2024:{s}@2025-01-01"


def l(s):
    return f"luat_36_2024:{s}@2025-01-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"dk-{START + len(S):04d}", "chu_de": "Đăng ký xe", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Đấu giá biển số (NĐ 156/2024; Luật 36 Điều 37, 38)
add("quy_tac", "Đấu giá biển số xe được tổ chức theo hình thức nào?",
    "Hình thức đấu giá là đấu giá trực tuyến, phương thức trả giá lên (Điều 4 " + ND + ").", n("d4:k1"), n("d4:k2"))
add("doi_thuong", "giá khởi điểm đấu giá biển số ô tô với xe máy là bao nhiêu",
    "Giá khởi điểm của một biển số xe ô tô là 40 triệu đồng, của một biển số xe mô tô, xe gắn máy là 5 triệu đồng; giá này "
    "ba năm tăng một lần tính từ ngày 01/01/2025, mỗi lần tăng 5 triệu đồng với biển ô tô và 1 triệu đồng với biển xe máy "
    "(khoản 1, khoản 2 Điều 6 " + ND + ").", n("d6:k1"), n("d6:k2"))
add("quy_tac", "Biển số kiểu ngũ quý hoặc sảnh tiến đưa ra đấu giá lại có giá khởi điểm bao nhiêu?",
    "Biển số có định dạng AAAAA (A>4) hoặc ABCDE (A<B<C<D<E, A>4) đưa ra đấu giá lại sau lần thứ hai có giá khởi điểm 500 "
    "triệu đồng đối với biển ô tô và 50 triệu đồng đối với biển xe mô tô, xe gắn máy (khoản 3 Điều 6 " + ND + ").",
    n("d6:k3"))
add("thu_tuc", "Tham gia đấu giá biển số phải mua hồ sơ bao nhiêu tiền?",
    "Tiền bán hồ sơ tham gia đấu giá là 100 nghìn đồng trên một biển số xe ô tô và 50 nghìn đồng trên một biển số xe mô tô, "
    "xe gắn máy (khoản 1 Điều 8 " + ND + ").", n("d8:k1"))
add("thu_tuc", "Đăng ký tham gia đấu giá biển số xe như thế nào?",
    "Việc đăng ký tham gia đấu giá thực hiện hoàn toàn trên môi trường mạng tại Trang thông tin đấu giá trực tuyến của tổ "
    "chức hành nghề đấu giá tài sản. Người tham gia được cấp tài khoản truy cập, được chọn biển số trong danh sách đấu giá "
    "của tất cả các tỉnh, thành phố trên toàn quốc, nộp tiền hồ sơ và tiền đặt trước của biển đã chọn để được cấp mã đấu "
    "giá (khoản 1 Điều 14 " + ND + ").", n("d14:k1"), n("d14:k1:a"), n("d14:k1:c"), n("d14:k1:d"))
add("tinh_huong", "Tôi ở Hà Nội, có được tham gia đấu giá biển số của tỉnh khác không?",
    "Được. Người tham gia đấu giá được lựa chọn biển số xe theo nhu cầu trong danh sách biển số đưa ra đấu giá của tất cả "
    "các tỉnh, thành phố trực thuộc trung ương trên toàn quốc (điểm c khoản 1 Điều 14 " + ND + ").",
    n("d14:k1:c"), n("d14:k1"))
add("quy_tac", "Chỉ có một người đăng ký đấu giá một biển số thì sao?",
    "Khi hết thời hạn đăng ký mà chỉ có một người đăng ký tham gia đấu giá thì người đó được xác định là người trúng đấu giá "
    "biển số và nhận thông báo, biên bản trúng đấu giá trước thời điểm tổ chức cuộc đấu giá (khoản 4 Điều 14 " + ND + "; "
    "khoản 4 Điều 37 " + LUAT + ").", n("d14:k4"), l("d37:k4"))
add("quy_tac", "Danh sách biển số đưa ra đấu giá được công bố trước bao lâu?",
    "Quy chế đấu giá, danh sách biển số xe đưa ra đấu giá được thông báo công khai, niêm yết ít nhất 30 ngày trước ngày tổ "
    "chức phiên đấu giá (khoản 3 Điều 13 " + ND + ").", n("d13:k3"))
add("quy_tac", "Những hành vi nào bị truất quyền tham gia đấu giá biển số?",
    "Theo khoản 3 Điều 15 " + ND + ", bị truất quyền khi: cung cấp thông tin sai sự thật, dùng giấy tờ giả để đăng ký hoặc "
    "tham gia đấu giá; thông đồng, móc nối để dìm giá, làm sai lệch kết quả; cản trở hoạt động đấu giá, dùng phần mềm tác "
    "động đến quá trình hoặc kết quả, gây nhiễu loạn cuộc đấu giá; đe dọa, cưỡng ép đấu giá viên hoặc người tham gia khác; "
    "và các hành vi bị nghiêm cấm khác.", n("d15:k3"), n("d15:k3:a"), n("d15:k3:c"))
add("thu_tuc", "Trúng đấu giá biển số thì bao lâu phải nộp tiền?",
    "Trong thời hạn 30 ngày kể từ ngày có văn bản điện tử thông báo kết quả trúng đấu giá, người trúng đấu giá phải nộp toàn "
    "bộ số tiền trúng đấu giá sau khi đã trừ tiền đặt trước vào tài khoản chuyên thu của Bộ Công an. Tiền trúng đấu giá "
    "không bao gồm lệ phí đăng ký xe (Điều 19 " + ND + ").", n("d19"))
add("tinh_huong", "Tôi trúng đấu giá biển số nhưng không nộp đủ tiền đúng hạn. Hậu quả là gì?",
    "Biển số được đưa ra đấu giá lại hoặc chuyển vào hệ thống đăng ký, quản lý xe; bạn không được hoàn trả tiền đặt trước, "
    "số tiền đã nộp, và không được tham gia đấu giá biển số trong thời hạn 12 tháng kể từ ngày có thông báo kết quả trúng "
    "đấu giá (điểm a khoản 2 Điều 38 " + LUAT + "; điểm đ khoản 1 Điều 21 " + ND + ").", l("d38:k2:a"), n("d21:k1:đ"))
add("thu_tuc", "Nộp đủ tiền trúng đấu giá biển số rồi thì nhận được giấy tờ gì?",
    "Ngay sau khi nhận đủ số tiền trúng đấu giá, Bộ Công an cấp hóa đơn điện tử bán tài sản công và văn bản điện tử Quyết "
    "định xác nhận biển số xe trúng đấu giá, gửi vào địa chỉ thư điện tử của người trúng đấu giá để làm thủ tục đăng ký xe "
    "(Điều 20 " + ND + ").", n("d20"))
add("quy_tac", "Trúng đấu giá biển số thì phải gắn biển cho xe trong thời hạn bao lâu?",
    "Người trúng đấu giá phải làm thủ tục đăng ký xe để gắn biển số trúng đấu giá trong thời hạn 12 tháng kể từ ngày được "
    "cấp quyết định xác nhận biển số trúng đấu giá; nếu có sự kiện bất khả kháng hoặc trở ngại khách quan thì được kéo dài "
    "thêm nhưng tối đa không quá 06 tháng (điểm b khoản 2 Điều 38 " + LUAT + ").", l("d38:k2:b"), l("d38:k2"))
add("thu_tuc", "Muốn xin gia hạn thời hạn đăng ký biển số trúng đấu giá vì lý do bất khả kháng thì làm thế nào?",
    "Người trúng đấu giá gửi Đơn đề nghị gia hạn thời hạn đăng ký xe (Mẫu số 01) qua Hệ thống quản lý đấu giá biển số xe của "
    "Bộ Công an và gửi tài liệu chứng minh (bản chính) về Bộ Công an qua Cục Cảnh sát giao thông; Bộ Công an thông báo kết "
    "quả bằng văn bản điện tử. Thời gian gia hạn không quá 06 tháng (Điều 23 " + ND + ").", n("d23:k1"), n("d23:k2"),
    n("d23:k3"))
add("doi_thuong", "biển số đấu giá có bán lại riêng cái biển cho người khác được ko",
    "Không. Người trúng đấu giá không được chuyển nhượng, trao đổi, tặng cho, để thừa kế riêng biển số trúng đấu giá; chỉ "
    "được chuyển nhượng, trao đổi, tặng cho, để thừa kế xe gắn với biển số trúng đấu giá (điểm c khoản 1, điểm c khoản 2 "
    "Điều 38 " + LUAT + ").", l("d38:k2:c"), l("d38:k1:c"))
add("quy_tac", "Người trúng đấu giá biển số có những quyền gì?",
    "Theo khoản 1 Điều 38 " + LUAT + ", người trúng đấu giá được cấp quyết định xác nhận biển số trúng đấu giá sau khi nộp đủ "
    "tiền; được đăng ký biển số gắn với xe thuộc sở hữu của mình tại cơ quan Công an nơi quản lý biển số hoặc nơi cư trú, "
    "trụ sở; được chuyển nhượng, trao đổi, tặng cho, để thừa kế xe gắn với biển số trúng đấu giá.",
    l("d38:k1"), l("d38:k1:a"), l("d38:k1:b"), l("d38:k1:c"))
add("tinh_huong", "Người thân tôi trúng đấu giá biển số và đã có quyết định xác nhận, nhưng mất trước khi kịp đăng ký xe. Tiền "
    "trúng đấu giá xử lý ra sao?",
    "Trong thời hạn 12 tháng kể từ ngày được cấp quyết định xác nhận, nếu người trúng đấu giá chết mà chưa đăng ký xe để gắn "
    "biển số thì kết quả trúng đấu giá bị hủy, người thừa kế theo pháp luật về thừa kế được nhận đủ số tiền trúng đấu giá đã "
    "nộp (điểm đ khoản 1 Điều 38 " + LUAT + "). Người thừa kế nộp hồ sơ đề nghị hoàn tiền theo Phụ lục V (khoản 2 Điều 26 "
    + ND + ").", l("d38:k1:đ"), n("d26:k2"))
add("thu_tuc", "Đấu giá biển số không trúng thì bao lâu được trả lại tiền đặt trước?",
    "Người tham gia không trúng đấu giá (và không thuộc trường hợp không được nhận lại tiền đặt trước) được hoàn trả tiền "
    "đặt trước trong thời hạn 03 ngày làm việc kể từ ngày kết thúc cuộc đấu giá (khoản 3 Điều 25 " + ND + ").", n("d25:k3"))
add("tinh_huong", "Tôi đã nộp tiền đặt trước nhưng hôm đấu giá không đăng nhập vào phòng đấu giá. Tôi có được trả lại tiền "
    "không?",
    "Không, trừ trường hợp bất khả kháng. Người đủ điều kiện tham gia mà không đăng nhập vào tài khoản và truy cập phòng đấu "
    "giá trong thời gian đấu giá chính thức thì được coi là không tham gia cuộc đấu giá và thuộc trường hợp không được nhận "
    "lại tiền đặt trước (khoản 4 Điều 25 " + ND + ").", n("d25:k4"))

# ===== Đăng ký biển trúng đấu giá (TT 79 Điều 28–30)
add("thu_tuc", "Hồ sơ đăng ký biển số trúng đấu giá cho xe mới mua chưa đăng ký gồm những gì?",
    "Gồm giấy tờ đăng ký xe lần đầu theo Điều 8 " + TT + " và Quyết định xác nhận biển số xe trúng đấu giá do Cục Cảnh sát "
    "giao thông cấp còn thời hạn; nếu quá thời hạn thì phải có thêm Quyết định gia hạn thời hạn đăng ký biển số trúng đấu giá "
    "(khoản 1 Điều 28 " + TT + ").", t("d28:k1"), t("d28:k1:a"), t("d28:k1:b"))
add("tinh_huong", "Xe của tôi đã có biển số. Giờ tôi trúng đấu giá một biển số khác, muốn gắn cho chính xe này thì cần hồ "
    "sơ gì?",
    "Theo khoản 2 Điều 28 " + TT + ", hồ sơ gồm: giấy khai đăng ký xe; chứng nhận đăng ký xe và biển số xe đang dùng; Quyết "
    "định xác nhận biển số trúng đấu giá còn thời hạn (hoặc kèm quyết định gia hạn); và giấy xác nhận hồ sơ xe nếu cơ quan "
    "đăng ký biển trúng đấu giá khác cơ quan đang quản lý hồ sơ xe.", t("d28:k2"), t("d28:k2:a"), t("d28:k2:c"))
add("tinh_huong", "Tôi bán chiếc ô tô đang gắn biển số trúng đấu giá. Người mua có được giữ biển số đó không?",
    "Có, nếu chuyển quyền sở hữu xe kèm theo biển số trúng đấu giá. Khi đó chủ xe làm thủ tục thu hồi nhưng không phải nộp "
    "biển số trúng đấu giá, và chứng từ chuyển quyền sở hữu phải ghi rõ chuyển xe kèm biển số trúng đấu giá; người mua làm "
    "thủ tục sang tên và được giữ nguyên biển số trúng đấu giá (khoản 3 Điều 29 " + TT + ").",
    t("d29:k3"), t("d29:k3:a"), t("d29:k3:b"))
add("quy_tac", "Bán xe nhưng không bán kèm biển số trúng đấu giá thì biển số đó xử lý thế nào?",
    "Khi chủ xe làm thủ tục thu hồi đăng ký, biển số trúng đấu giá (trừ trường hợp chuyển xe kèm biển) thì số biển trúng đấu "
    "giá được cơ quan đăng ký xe giữ lại và cấp khi chủ xe đăng ký xe khác chưa có biển số thuộc sở hữu của mình (khoản 2 "
    "Điều 30 " + TT + "). Thủ tục mua bán xe khi đó làm như sang tên thông thường (khoản 2 Điều 29).",
    t("d30:k2"), t("d29:k2"))
add("thu_tuc", "Đăng ký, cấp biển số trúng đấu giá thực hiện theo các bước nào?",
    "Theo khoản 1 Điều 29 " + TT + ": kê khai giấy khai đăng ký xe; đưa xe đến cơ quan đăng ký xe để kiểm tra (trừ khi đăng "
    "ký lần đầu trực tuyến toàn trình), cung cấp mã hồ sơ và nộp hồ sơ theo Điều 28; sau khi hồ sơ và xe hợp lệ thì được cấp "
    "biển số trúng đấu giá, nhận giấy hẹn và nộp lệ phí đăng ký xe.", t("d29:k1"), t("d29:k1:b"), t("d29:k1:c"))

# ===== Hồ sơ chi tiết (TT 79 Điều 9, 11, 12, 13)
add("thu_tuc", "Đăng ký xe trực tuyến toàn trình thì giấy khai đăng ký xe có phải ký không?",
    "Không. Khi đăng ký xe lần đầu bằng dịch vụ công trực tuyến toàn trình, chủ xe dùng tài khoản định danh điện tử mức độ 2 "
    "đăng nhập cổng dịch vụ công hoặc Ứng dụng định danh quốc gia, kê khai đầy đủ, trung thực các nội dung trong giấy khai và "
    "không cần ký (khoản 2 Điều 9 " + TT + "). Nếu làm trực tuyến một phần thì phải ký số, hoặc in giấy khai ra ký tên (khoản "
    "1 Điều 9).", t("d9:k2"), t("d9:k1"))
add("quy_tac", "Chứng nhận nguồn gốc của xe máy, ô tô sản xuất, lắp ráp trong nước là giấy tờ gì?",
    "Là dữ liệu điện tử phiếu kiểm tra chất lượng xuất xưởng mà hệ thống đăng ký xe tiếp nhận từ cổng dịch vụ công hoặc cơ "
    "sở dữ liệu của cơ quan đăng kiểm; nếu xe chưa có dữ liệu điện tử thì dùng phiếu kiểm tra chất lượng xuất xưởng bản giấy "
    "(điểm a, điểm b khoản 2 Điều 11 " + TT + ").", t("d11:k2:a"), t("d11:k2:b"))
add("quy_tac", "Xe nhập khẩu thì chứng nhận nguồn gốc khi đăng ký là gì?",
    "Là dữ liệu hải quan điện tử mà hệ thống đăng ký xe tiếp nhận từ cổng dịch vụ công hoặc cơ sở dữ liệu hải quan; nếu xe "
    "không có dữ liệu hải quan điện tử thì dùng tờ khai nguồn gốc xe nhập khẩu (với xe nhập theo hợp đồng thương mại) hoặc "
    "các giấy tờ tương ứng khác theo quy định (khoản 1 Điều 11 " + TT + ").", t("d11:k1:a"), t("d11:k1:b"))
add("quy_tac", "Chứng nhận quyền sở hữu hợp pháp của xe khi đăng ký gồm những giấy tờ nào?",
    "Là chứng từ chuyển quyền sở hữu xe, gồm một trong các loại: dữ liệu hóa đơn điện tử tiếp nhận từ cơ quan thuế (nếu chưa "
    "có thì dùng hóa đơn giấy hoặc hóa đơn chuyển đổi); hoặc quyết định của cơ quan có thẩm quyền, văn bản chuyển nhượng, "
    "trao đổi, tặng cho, để thừa kế xe, chứng từ tài chính của xe theo quy định (Điều 12 " + TT + ").",
    t("d12"), t("d12:k1"), t("d12:k2"))
add("quy_tac", "Chứng từ hoàn thành nghĩa vụ tài chính khi đăng ký xe là gì?",
    "Là chứng từ nộp lệ phí trước bạ xe (trừ xe máy chuyên dùng): dữ liệu điện tử nộp lệ phí trước bạ tiếp nhận từ cơ quan "
    "thuế; nếu chưa có dữ liệu điện tử thì dùng giấy nộp tiền vào ngân sách nhà nước hoặc chứng từ nộp lệ phí trước bạ khác; "
    "xe được miễn lệ phí trước bạ thì phải có thông báo của cơ quan thuế ghi thông tin miễn (Điều 13 " + TT + ").",
    t("d13"), t("d13:k1"), t("d13:k2"))

# ===== Trường hợp đặc biệt (TT 79 Điều 31–33)
add("quy_tac", "Ai được đóng lại số máy, số khung cho xe khi đăng ký?",
    "Trong mọi trường hợp được phép, việc đóng lại số máy, số khung đều phải do cơ quan đăng ký xe thực hiện (khoản 3 Điều "
    "31 " + TT + "). Xe có số máy, số khung bị cắt, hàn, tẩy xóa, đục sửa, đóng lại trái phép thì không được giải quyết đăng "
    "ký (khoản 4 Điều 31).", t("d31:k3"), t("d31:k4"))
add("tinh_huong", "Số khung xe của tôi bị gỉ mờ mất vài ký tự. Có đăng ký, sang tên được không?",
    "Được, nếu cơ quan giám định kết luận số máy hoặc số khung là nguyên thủy: khi đó xe được đóng lại số theo số ghi trong "
    "chứng nhận nguồn gốc (điểm đ khoản 1 Điều 31 " + TT + "), và việc đóng lại số do cơ quan đăng ký xe thực hiện (khoản 3 "
    "Điều 31).", t("d31:k1:đ"), t("d31:k3"))
add("tinh_huong", "Tôi mua lại chiếc xe đã qua tay nhiều người, không liên lạc được chủ đứng tên. Sang tên thế nào?",
    "Người đang sử dụng xe đến cơ quan đăng ký xe đang quản lý hồ sơ xe để làm thủ tục thu hồi, rồi đến cơ quan đăng ký xe "
    "nơi mình cư trú để đăng ký sang tên (khoản 1 Điều 32 " + TT + "). Khi làm thủ tục thu hồi, người có thẩm quyền lập biên "
    "bản xử phạt đối với chủ xe đứng tên, người đang sử dụng xe ký với tư cách người chứng kiến. Nếu người đang sử dụng không "
    "có chứng từ chuyển quyền sở hữu thì được cấp giấy hẹn có giá trị được sử dụng xe trong thời gian 30 ngày "
    "(điểm b khoản 3 Điều 32).", t("d32:k1"), t("d32:k3:b"))
add("quy_tac", "Xe đang thế chấp ngân hàng có sang tên hoặc đổi giấy đăng ký được không?",
    "Xe đã đăng ký thế chấp khi làm thủ tục sang tên, đổi, cấp lại chứng nhận đăng ký, biển số thì phải có văn bản xác nhận "
    "đã giải chấp của cơ quan có thẩm quyền (bản giấy hoặc văn bản điện tử) (khoản 13 Điều 33 " + TT + ").", t("d33:k13"))
add("quy_tac", "Một chiếc xe được thay cả máy lẫn khung không?",
    "Không. Trong suốt quá trình sử dụng, mỗi xe chỉ được thay đổi 1 trong 2 tổng thành là máy hoặc khung, không được thay "
    "cả máy và khung (điểm d khoản 2 Điều 33 " + TT + ").", t("d33:k2:d"), t("d33:k2"))
add("quy_tac", "Có được lấy máy của xe đã hết niên hạn để lắp sang xe khác rồi đăng ký không?",
    "Không. Không sử dụng tổng thành máy của xe hết niên hạn sử dụng, xe thải bỏ, xe không được phép lưu hành, xe miễn thuế, "
    "xe tạm nhập, tái xuất của cơ quan đại diện ngoại giao… để thay thế cho xe khác (điểm c khoản 2 Điều 33 " + TT + ").",
    t("d33:k2:c"), t("d33:k2"))
add("quy_tac", "Xe tải cải tạo thành xe chở người có được đăng ký không?",
    "Không được giải quyết đăng ký xe ô tô loại khác cải tạo thành xe ô tô chở người (trừ xe phục vụ mục đích an ninh) "
    "(điểm b khoản 2 Điều 33 " + TT + "). Điểm này cũng không cho đăng ký xe chuyên dùng chuyển đổi tính năng, công dụng "
    "trước 05 năm và xe đông lạnh chuyển đổi trước 03 năm kể từ ngày nhập khẩu.", t("d33:k2:b"), t("d33:k2"))
add("thu_tuc", "Mua xe ngân hàng thanh lý (xe thế chấp bị bán thu hồi nợ) thì đăng ký cần hồ sơ gì?",
    "Theo điểm c khoản 7 Điều 33 " + TT + ", hồ sơ gồm bản sao hợp đồng thế chấp hoặc hợp đồng tín dụng (do tổ chức tín dụng "
    "ký sao) và hóa đơn theo quy định. Nếu xe chưa đăng ký thì bổ sung hồ sơ đăng ký lần đầu theo Điều 8; nếu xe đã đăng ký "
    "thì người mua làm thủ tục thu hồi theo Điều 16 (không còn chứng nhận đăng ký thì phải có văn bản xác nhận của tổ chức "
    "tín dụng) rồi nộp bổ sung hồ sơ đăng ký.", t("d33:k7:c"), t("d33:k7"))
add("tinh_huong", "Xe mới mua của tôi chưa đăng ký thì bị mất hóa đơn và phiếu xuất xưởng. Làm sao để đăng ký?",
    "Cán bộ đăng ký xe sẽ hướng dẫn bạn liên hệ cơ quan đã cấp các chứng từ đó để đề nghị cấp lại bản sao; với xe sản xuất, "
    "lắp ráp thì cơ sở sản xuất, lắp ráp phải cấp lại phiếu kiểm tra chất lượng xuất xưởng (khoản 18 Điều 33 " + TT + ").",
    t("d33:k18"))
add("thu_tuc", "Mua xe thanh lý của doanh nghiệp đã giải thể thì sang tên cần thêm giấy tờ gì?",
    "Người mua làm thủ tục sang tên theo Điều 16, Điều 17 " + TT + ", kèm theo chứng nhận đăng ký xe và quyết định giải thể "
    "của cấp có thẩm quyền hoặc bản sao quyết định thu hồi giấy chứng nhận đăng ký doanh nghiệp (khoản 12 Điều 33).",
    t("d33:k12"), t("d33:k12:a"), t("d33:k12:b"))
add("quy_tac", "Xe đã qua nhiều doanh nghiệp bán lại trước khi đăng ký lần đầu thì dùng hóa đơn nào?",
    "Đối với xe cấp mới chứng nhận đăng ký, biển số mà đã bán qua nhiều tổ chức, doanh nghiệp thì dùng hóa đơn của tổ chức, "
    "doanh nghiệp bán cuối cùng (điểm a khoản 1 Điều 33 " + TT + ").", t("d33:k1:a"), t("d33:k1"))

out = ROOT / "data/train/drafts/dang_ky_xe_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
