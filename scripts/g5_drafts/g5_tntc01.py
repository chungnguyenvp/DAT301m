"""Đợt 9a G5: Tai nạn (BLDS 2015 về bồi thường; BLHS hợp nhất 135/2025 Điều 260, 264) và Từ chối (câu ngoài phạm vi hoặc
đề nghị giúp vi phạm). Ghi data/train/drafts/tai_nan_tu_choi_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLDS = "Bộ luật Dân sự 2015"
BLHS = "Bộ luật Hình sự"
S = []
N = {"tn": 0, "tc": 0}


def d(s):
    return f"blds_2015:{s}@2017-01-01"


def h(s):
    return f"vbhn_135_2025_blhs:{s}@2025-07-01"


def add(pre, chu_de, loai, q, a, *can_cu):
    N[pre] += 1
    S.append({"key": f"{pre}-{N[pre]:04d}", "chu_de": chu_de, "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


T = "Tai nạn"
# ===== Tai nạn: hình sự (BLHS Điều 260, 264)
add("tn", T, "muc_phat", "Gây tai nạn giao thông làm chết người thì bị xử lý hình sự thế nào?",
    "Người tham gia giao thông vi phạm quy định về an toàn giao thông đường bộ gây thiệt hại làm chết người thì bị phạt tiền từ "
    "30.000.000 đồng đến 100.000.000 đồng, phạt cải tạo không giam giữ đến 03 năm hoặc phạt tù từ 01 năm đến 05 năm (điểm a "
    "khoản 1 Điều 260 " + BLHS + "). Người phạm tội còn có thể bị cấm hành nghề hoặc làm công việc nhất định từ 01 năm đến 05 "
    "năm (khoản 5 Điều 260).", h("d260:k1:a"), h("d260:k1"), h("d260:k5"))
add("tn", T, "muc_phat", "Say rượu lái xe gây tai nạn chết người thì bị phạt tù bao nhiêu năm?",
    "Vi phạm quy định về an toàn giao thông gây hậu quả thuộc khoản 1 (như làm chết người) mà trong tình trạng có sử dụng rượu, "
    "bia có nồng độ cồn vượt quá mức quy định thì thuộc khung tăng nặng, bị phạt tù từ 03 năm đến 10 năm (điểm b khoản 2 Điều "
    "260 " + BLHS + ").", h("d260:k2:b"), h("d260:k2"), h("d260:k1"))
add("tn", T, "tinh_huong", "Tôi không có bằng lái, gây tai nạn làm một người bị thương 65%. Tôi có thể bị xử lý thế nào?",
    "Gây thương tích cho 01 người với tỷ lệ tổn thương cơ thể 61% trở lên là hậu quả thuộc khoản 1 Điều 260 " + BLHS + ". Vì "
    "không có giấy phép lái xe theo quy định nên thuộc khung khoản 2, bị phạt tù từ 03 năm đến 10 năm (điểm a khoản 2 Điều 260).",
    h("d260:k2:a"), h("d260:k1:b"), h("d260:k2"))
add("tn", T, "muc_phat", "Gây tai nạn rồi bỏ chạy, không cứu người bị nạn thì hình phạt có nặng hơn không?",
    "Có. Trường hợp bỏ chạy để trốn tránh trách nhiệm hoặc cố ý không cứu giúp người bị nạn là tình tiết thuộc khoản 2 Điều 260 "
    + BLHS + ", bị phạt tù từ 03 năm đến 10 năm (điểm c khoản 2).", h("d260:k2:c"), h("d260:k2"))
add("tn", T, "muc_phat", "Gây tai nạn làm chết từ 3 người trở lên thì khung hình phạt là gì?",
    "Làm chết 03 người trở lên thì bị phạt tù từ 07 năm đến 15 năm (điểm a khoản 3 Điều 260 " + BLHS + "). Làm chết 02 người "
    "thì thuộc khoản 2, phạt tù từ 03 năm đến 10 năm (điểm đ khoản 2 Điều 260).", h("d260:k3:a"), h("d260:k3"),
    h("d260:k2:đ"))
add("tn", T, "quy_tac", "Gây tai nạn chỉ làm hỏng tài sản thì đến mức nào mới bị truy cứu hình sự?",
    "Gây thiệt hại về tài sản từ 100.000.000 đồng đến dưới 500.000.000 đồng thuộc khoản 1 Điều 260 " + BLHS + " (phạt tiền "
    "từ 30.000.000 đồng đến 100.000.000 đồng, cải tạo không giam giữ đến 03 năm hoặc phạt tù từ 01 năm đến 05 năm); từ "
    "500.000.000 đồng đến dưới 1.500.000.000 đồng thuộc khoản 2; từ 1.500.000.000 đồng trở lên thuộc khoản 3.",
    h("d260:k1:d"), h("d260:k2:g"), h("d260:k3:c"))
add("tn", T, "quy_tac", "Vi phạm giao thông nhưng chưa gây hậu quả có bị truy cứu hình sự không?",
    "Có thể, nếu vi phạm trong trường hợp có khả năng thực tế dẫn đến hậu quả rất nghiêm trọng (làm chết 03 người trở lên, gây "
    "thương tích cho 03 người trở lên với tổng tỷ lệ 201% trở lên…) nếu không được ngăn chặn kịp thời: bị phạt tiền từ "
    "10.000.000 đồng đến 50.000.000 đồng, cải tạo không giam giữ đến 01 năm hoặc phạt tù từ 03 tháng đến 01 năm (khoản 4 Điều "
    "260 " + BLHS + ").", h("d260:k4"), h("d260:k3:a"), h("d260:k3:b"))
add("tn", T, "tinh_huong", "Tôi biết bạn đang say mà vẫn đưa xe cho bạn lái, bạn gây tai nạn chết người. Tôi có bị truy cứu không?",
    "Có thể bị truy cứu theo Điều 264 " + BLHS + ": người giao xe cho người mà biết rõ đang có nồng độ cồn vượt quá mức quy "
    "định, không có giấy phép lái xe hoặc không đủ điều kiện khác điều khiển phương tiện, gây hậu quả làm chết người, bị phạt "
    "tiền từ 10.000.000 đồng đến 50.000.000 đồng hoặc phạt cải tạo không giam giữ đến 03 năm (điểm a khoản 1 Điều 264).",
    h("d264:k1"), h("d264:k1:a"))
add("tn", T, "muc_phat", "Giao xe cho người không có bằng lái gây tai nạn làm chết 2 người thì người giao xe bị phạt thế nào?",
    "Người giao xe cho người mà biết rõ không có giấy phép lái xe điều khiển phương tiện, gây hậu quả làm chết 02 người, bị phạt "
    "tiền từ 50.000.000 đồng đến 200.000.000 đồng hoặc phạt tù từ 06 tháng đến 03 năm (điểm a khoản 2 Điều 264 " + BLHS + ").",
    h("d264:k2:a"), h("d264:k2"), h("d264:k1"))

# ===== Tai nạn: dân sự (BLDS 2015)
add("tn", T, "quy_tac", "Xe máy, ô tô có phải là nguồn nguy hiểm cao độ không?",
    "Có. Nguồn nguy hiểm cao độ bao gồm phương tiện giao thông vận tải cơ giới, cùng hệ thống tải điện, nhà máy công nghiệp đang "
    "hoạt động, vũ khí, chất nổ… Chủ sở hữu phải vận hành, sử dụng, bảo quản nguồn nguy hiểm cao độ theo đúng quy định (khoản 1 "
    "Điều 601 " + BLDS + ").", d("d601:k1"))
add("tn", T, "tinh_huong", "Xe tôi đang chạy đúng luật thì va chạm làm người khác bị thương. Tôi không có lỗi, có phải bồi "
    "thường không?",
    "Có thể vẫn phải bồi thường. Chủ sở hữu, người chiếm hữu, sử dụng nguồn nguy hiểm cao độ (như phương tiện giao thông cơ "
    "giới) phải bồi thường thiệt hại cả khi không có lỗi, trừ trường hợp thiệt hại xảy ra hoàn toàn do lỗi cố ý của người bị "
    "thiệt hại, hoặc do bất khả kháng, tình thế cấp thiết (khoản 3 Điều 601 " + BLDS + ").",
    d("d601:k3"), d("d601:k3:a"), d("d601:k3:b"))
add("tn", T, "tinh_huong", "Tôi cho bạn mượn xe máy, bạn gây tai nạn. Ai phải bồi thường cho người bị nạn?",
    "Chủ sở hữu nguồn nguy hiểm cao độ phải bồi thường thiệt hại do nó gây ra; nhưng nếu chủ sở hữu đã giao cho người khác "
    "chiếm hữu, sử dụng thì người này phải bồi thường, trừ trường hợp có thỏa thuận khác (khoản 2 Điều 601 " + BLDS + "). Như "
    "vậy người mượn xe đang sử dụng xe là người phải bồi thường, trừ khi hai bên thỏa thuận khác.", d("d601:k2"))
add("tn", T, "tinh_huong", "Xe của tôi bị trộm rồi kẻ trộm gây tai nạn. Tôi có phải bồi thường không?",
    "Khi nguồn nguy hiểm cao độ bị chiếm hữu, sử dụng trái pháp luật thì người đang chiếm hữu, sử dụng trái pháp luật phải bồi "
    "thường. Nếu chủ sở hữu có lỗi trong việc để xe bị chiếm hữu, sử dụng trái pháp luật thì phải liên đới bồi thường (khoản 4 "
    "Điều 601 " + BLDS + ").", d("d601:k4"))
add("tn", T, "quy_tac", "Người bị tai nạn giao thông bị thương thì được bồi thường những khoản gì?",
    "Theo khoản 1 Điều 590 " + BLDS + ", thiệt hại do sức khỏe bị xâm phạm gồm: chi phí hợp lý cho việc cứu chữa, bồi dưỡng, "
    "phục hồi sức khỏe; thu nhập thực tế bị mất hoặc giảm sút; chi phí hợp lý và thu nhập bị mất của người chăm sóc trong thời "
    "gian điều trị; thiệt hại khác do luật quy định. Ngoài ra còn được một khoản bù đắp tổn thất tinh thần (khoản 2 Điều 590).",
    d("d590:k1"), d("d590:k1:a"), d("d590:k1:b"), d("d590:k2"))
add("tn", T, "quy_tac", "Tiền bù đắp tổn thất tinh thần khi bị thương do tai nạn tối đa là bao nhiêu?",
    "Mức bồi thường bù đắp tổn thất tinh thần do các bên thỏa thuận; nếu không thỏa thuận được thì mức tối đa cho một người có "
    "sức khỏe bị xâm phạm không quá năm mươi lần mức lương cơ sở do Nhà nước quy định (khoản 2 Điều 590 " + BLDS + ").",
    d("d590:k2"))
add("tn", T, "quy_tac", "Người chết do tai nạn giao thông thì gia đình được bồi thường những gì?",
    "Theo Điều 591 " + BLDS + ", thiệt hại do tính mạng bị xâm phạm gồm: thiệt hại do sức khỏe bị xâm phạm trước khi chết (chi "
    "phí cứu chữa…); chi phí hợp lý cho việc mai táng; tiền cấp dưỡng cho những người mà người bị thiệt hại có nghĩa vụ cấp "
    "dưỡng; thiệt hại khác; và một khoản bù đắp tổn thất tinh thần cho những người thân thích thuộc hàng thừa kế thứ nhất.",
    d("d591:k1"), d("d591:k1:b"), d("d591:k1:c"), d("d591:k2"))
add("tn", T, "tinh_huong", "Người bị nạn cũng có lỗi một phần (đi sai làn). Họ có được bồi thường toàn bộ không?",
    "Không. Khi bên bị thiệt hại có lỗi trong việc gây thiệt hại thì không được bồi thường phần thiệt hại do lỗi của mình gây ra "
    "(khoản 4 Điều 585 " + BLDS + ").", d("d585:k4"))
add("tn", T, "quy_tac", "Hai bên gây tai nạn có được tự thỏa thuận mức bồi thường không?",
    "Có. Thiệt hại thực tế phải được bồi thường toàn bộ và kịp thời; các bên có thể thỏa thuận về mức bồi thường, hình thức bồi "
    "thường bằng tiền, hiện vật hoặc thực hiện một công việc, bồi thường một lần hoặc nhiều lần, trừ trường hợp pháp luật có "
    "quy định khác (khoản 1 Điều 585 " + BLDS + ").", d("d585:k1"))
add("tn", T, "quy_tac", "Người gây tai nạn nghèo, thiệt hại quá lớn thì có được giảm mức bồi thường không?",
    "Có thể. Người chịu trách nhiệm bồi thường có thể được giảm mức bồi thường nếu không có lỗi hoặc có lỗi vô ý và thiệt hại quá "
    "lớn so với khả năng kinh tế của mình (khoản 2 Điều 585 " + BLDS + ").", d("d585:k2"))
add("tn", T, "quy_tac", "Khi nào người gây thiệt hại không phải bồi thường?",
    "Người gây thiệt hại không phải bồi thường khi thiệt hại phát sinh do sự kiện bất khả kháng hoặc hoàn toàn do lỗi của bên bị "
    "thiệt hại, trừ trường hợp có thỏa thuận khác hoặc luật có quy định khác (khoản 2 Điều 584 " + BLDS + ").", d("d584:k2"))

# ===== Từ chối: ngoài phạm vi
TC = "Từ chối"
SCOPE = ("Câu hỏi này nằm ngoài phạm vi của tôi. Tôi chỉ hỗ trợ tra cứu pháp luật về trật tự, an toàn giao thông đường bộ "
         "Việt Nam (luật giao thông, xử phạt, giấy phép lái xe, đăng ký, đăng kiểm, phí và bảo hiểm xe) và không có căn cứ "
         "trong tài liệu để trả lời. ")
OUT = [
    ("Luật Hàng hải quy định gì về đăng ký tàu biển?", "Bạn nên tra cứu Bộ luật Hàng hải và các văn bản hướng dẫn của cơ quan quản lý hàng hải."),
    ("Thủ tục đăng ký tàu cá cần những giấy tờ gì?", "Bạn nên tra cứu pháp luật về thủy sản hoặc liên hệ cơ quan quản lý thủy sản địa phương."),
    ("Quy định về hành lý xách tay khi đi máy bay là gì?", "Bạn nên xem quy định của hãng hàng không và pháp luật về hàng không dân dụng."),
    ("Đi tàu hỏa không mua vé thì bị phạt bao nhiêu?", "Lĩnh vực đường sắt có văn bản xử phạt riêng mà tôi không có trong tài liệu."),
    ("Lái ca nô trên sông cần bằng gì?", "Bằng lái phương tiện thủy nội địa thuộc pháp luật về giao thông đường thủy nội địa, không nằm trong tài liệu của tôi."),
    ("Thuế thu nhập cá nhân năm nay tính thế nào?", "Bạn nên tra cứu pháp luật về thuế hoặc hỏi cơ quan thuế."),
    ("Làm sổ đỏ cho đất thổ cư cần giấy tờ gì?", "Thủ tục này thuộc pháp luật về đất đai; bạn nên liên hệ văn phòng đăng ký đất đai."),
    ("Ly hôn đơn phương thì nộp đơn ở đâu?", "Thủ tục ly hôn thuộc pháp luật hôn nhân gia đình và tố tụng dân sự."),
    ("Thủ tục làm hộ chiếu phổ thông như thế nào?", "Bạn nên tra cứu quy định về xuất nhập cảnh hoặc liên hệ cơ quan quản lý xuất nhập cảnh."),
    ("Lương tối thiểu vùng năm 2026 là bao nhiêu?", "Mức lương tối thiểu vùng thuộc pháp luật lao động, không có trong tài liệu của tôi."),
    ("Ở Mỹ vượt đèn đỏ bị phạt bao nhiêu đô la?", "Tôi chỉ có tài liệu pháp luật Việt Nam, không có căn cứ về luật giao thông của nước khác."),
    ("Luật giao thông Nhật Bản cho phép chở mấy người trên xe máy?", "Tôi chỉ có tài liệu pháp luật Việt Nam, không có căn cứ về luật của Nhật Bản."),
    ("Ở Singapore lái xe say rượu bị phạt thế nào?", "Tôi chỉ có tài liệu pháp luật Việt Nam, không có căn cứ về luật của Singapore."),
    ("Mua xe ô tô hãng nào bền nhất hiện nay?", "Đây là câu hỏi tư vấn mua sắm, không phải câu hỏi pháp luật giao thông."),
    ("Thay dầu xe máy bao lâu một lần là hợp lý?", "Đây là câu hỏi kỹ thuật bảo dưỡng; bạn nên làm theo khuyến cáo của nhà sản xuất xe."),
    ("Giá xăng RON 95 hôm nay là bao nhiêu?", "Giá xăng dầu không thuộc nội dung pháp luật giao thông trong tài liệu của tôi."),
    ("Đường từ Hà Nội đi Hải Phòng nên đi tuyến nào cho nhanh?", "Đây là câu hỏi chỉ đường; bạn nên dùng ứng dụng bản đồ."),
    ("Học lái xe ô tô ở trung tâm nào tốt?", "Tôi không đánh giá hay giới thiệu cơ sở đào tạo cụ thể."),
    ("Cách sửa xe máy bị chết máy giữa đường?", "Đây là câu hỏi kỹ thuật sửa chữa, không phải câu hỏi pháp luật."),
    ("Bảo hiểm nhân thọ nào có quyền lợi tốt nhất?", "Bảo hiểm nhân thọ thuộc lĩnh vực kinh doanh bảo hiểm khác, không có trong tài liệu của tôi."),
    ("Quy định về nồng độ cồn khi lái máy bay là gì?", "Lĩnh vực hàng không không nằm trong tài liệu của tôi."),
    ("Thủ tục khai sinh cho con cần những gì?", "Thủ tục này thuộc pháp luật về hộ tịch."),
    ("Tôi bị sa thải trái luật thì khởi kiện thế nào?", "Tranh chấp lao động thuộc pháp luật lao động và tố tụng."),
    ("Mở quán cà phê cần giấy phép gì?", "Thủ tục kinh doanh này thuộc pháp luật về đăng ký kinh doanh, an toàn thực phẩm."),
    ("Đăng ký bản quyền phần mềm như thế nào?", "Thủ tục này thuộc pháp luật sở hữu trí tuệ."),
    ("Xây nhà 3 tầng có cần xin giấy phép xây dựng không?", "Thủ tục này thuộc pháp luật xây dựng; bạn nên hỏi cơ quan cấp phép xây dựng địa phương."),
    ("Vé tháng xe buýt Hà Nội giá bao nhiêu?", "Giá vé xe buýt do đơn vị vận tải và địa phương công bố, không có trong tài liệu của tôi."),
    ("Thời tiết ngày mai có mưa không để tôi đi xe máy?", "Tôi không cung cấp thông tin thời tiết."),
    ("Tỷ lệ tai nạn giao thông năm ngoái ở Việt Nam là bao nhiêu?", "Tài liệu của tôi là văn bản pháp luật, không có số liệu thống kê tai nạn."),
    ("Năm sau mức phạt vượt đèn đỏ có tăng không?", "Tôi chỉ trả lời theo quy định đang có trong tài liệu, không dự đoán thay đổi pháp luật trong tương lai."),
    ("Quy định cấm xe máy ở nội thành Hà Nội khi nào áp dụng?", "Tài liệu của tôi không có văn bản nào về lộ trình hạn chế xe máy của Hà Nội."),
    ("Thủ tục nhập khẩu ô tô cũ từ nước ngoài về như thế nào?", "Thủ tục hải quan, nhập khẩu xe không nằm trong tài liệu của tôi."),
    ("Mức thuế tiêu thụ đặc biệt của ô tô là bao nhiêu?", "Thuế tiêu thụ đặc biệt thuộc pháp luật thuế, không có trong tài liệu của tôi."),
    ("Điều kiện kinh doanh dịch vụ cầm đồ xe máy là gì?", "Điều kiện kinh doanh cầm đồ không nằm trong tài liệu của tôi."),
    ("Chính sách bảo hành pin xe điện VinFast thế nào?", "Chính sách bảo hành do nhà sản xuất quy định, không phải nội dung pháp luật trong tài liệu của tôi."),
    ("Tôi nên chọn xe số hay xe tay ga để đi làm?", "Đây là câu hỏi lựa chọn cá nhân, không phải câu hỏi pháp luật."),
    ("Viết giúp tôi bài văn về an toàn giao thông", "Tôi chỉ hỗ trợ tra cứu quy định pháp luật, không viết bài văn."),
    ("Kể chuyện cười về cảnh sát giao thông đi", "Tôi chỉ hỗ trợ tra cứu quy định pháp luật về giao thông đường bộ."),
    ("Quy định về hút thuốc lá nơi công cộng là gì?", "Nội dung này thuộc pháp luật phòng chống tác hại của thuốc lá."),
    ("Mua bán đất bằng giấy viết tay có hợp pháp không?", "Nội dung này thuộc pháp luật đất đai và dân sự về hợp đồng, không nằm trong tài liệu giao thông của tôi."),
]
for q, extra in OUT:
    add("tc", TC, "tu_choi", q, SCOPE + extra)

# ===== Từ chối: đề nghị giúp vi phạm hoặc trốn tránh trách nhiệm
REFUSE = ("Tôi không thể hướng dẫn việc này vì đây là hành vi vi phạm pháp luật hoặc nhằm trốn tránh trách nhiệm. ")
BAD = [
    ("Làm sao để thổi nồng độ cồn mà máy không phát hiện?", "Nếu đã uống rượu, bia, cách an toàn và đúng luật là không lái xe và đi bằng phương tiện khác."),
    ("Chỉ tôi cách làm biển số giả cho xe máy", "Việc sản xuất, sử dụng biển số giả bị pháp luật nghiêm cấm và bị xử phạt nặng."),
    ("Cách che biển số để camera phạt nguội không chụp được?", "Che lấp biển số là hành vi bị cấm; tôi có thể giải thích quy định về biển số nếu bạn cần."),
    ("Làm sao để xóa lỗi phạt nguội trên hệ thống mà không phải nộp?", "Bạn có thể tra cứu thông báo vi phạm và thực hiện giải trình, nộp phạt theo đúng thủ tục."),
    ("Có cách nào tua lại đồng hồ công-tơ-mét để bán xe được giá không?", "Can thiệp làm sai lệch đồng hồ quãng đường là hành vi bị cấm và bị xử phạt."),
    ("Chỉ cách mua bằng lái không cần thi", "Giấy phép lái xe chỉ được cấp cho người đạt kỳ sát hạch; dùng bằng giả hoặc bằng cấp sai quy định là vi phạm."),
    ("Làm sao trốn trạm cân khi chở quá tải?", "Trốn tránh việc kiểm tra tải trọng là hành vi vi phạm và bị xử phạt nặng."),
    ("Gây tai nạn rồi nên bỏ chạy hay ở lại để không bị phát hiện?", "Bạn phải dừng lại, giữ hiện trường, cứu giúp người bị nạn và trình báo cơ quan có thẩm quyền; bỏ chạy là hành vi bị nghiêm cấm."),
    ("Cách đăng kiểm xe khi xe không đạt mà không cần sửa?", "Xe phải đạt yêu cầu an toàn kỹ thuật mới được cấp giấy chứng nhận kiểm định; bạn nên sửa chữa rồi kiểm định lại."),
    ("Làm thế nào để lắp còi ưu tiên cho xe riêng?", "Lắp đặt, sử dụng thiết bị phát tín hiệu ưu tiên không đúng quy định là hành vi bị cấm."),
    ("Chỉ tôi cách lách luật để chở 3 người lớn trên xe máy", "Xe máy chỉ được chở tối đa theo quy định; tôi có thể giải thích các trường hợp được chở hai người."),
    ("Có cách nào để thoát khi bị CSGT dừng xe kiểm tra không?", "Bạn cần chấp hành hiệu lệnh kiểm tra; chống đối hoặc bỏ chạy khi bị kiểm tra là hành vi vi phạm."),
    ("Giúp tôi làm giả giấy khám sức khỏe để thi bằng lái", "Sử dụng giấy tờ giả để được cấp giấy phép lái xe là vi phạm và giấy phép cấp sai sẽ bị thu hồi."),
    ("Làm sao chạy quá tốc độ mà không bị máy bắn tốc độ phát hiện?", "Bạn nên chạy đúng tốc độ quy định; tôi có thể cho biết tốc độ tối đa trên từng loại đường."),
    ("Cách khai báo gian dối để người khác nhận lỗi phạt nguội thay mình?", "Khai báo gian dối để trốn tránh trách nhiệm là hành vi bị nghiêm cấm."),
]
for q, extra in BAD:
    add("tc", TC, "tu_choi", q, REFUSE + extra)

# ===== Từ chối: kiểu nói thường ngày, ngoài phạm vi
CASUAL = [
    ("ê luật đi đường thủy thế nào vậy", "Giao thông đường thủy nội địa có luật riêng, không nằm trong tài liệu của tôi."),
    ("bằng lái máy bay học ở đâu", "Lĩnh vực hàng không không nằm trong tài liệu của tôi."),
    ("thi đại học năm nay môn gì", "Đây là câu hỏi giáo dục, không phải pháp luật giao thông đường bộ."),
    ("xe đạp điện nên mua loại nào", "Đây là câu hỏi tư vấn mua sắm; tôi chỉ trả lời câu hỏi pháp luật."),
    ("tối nay ăn gì ngon", "Tôi chỉ hỗ trợ tra cứu pháp luật về giao thông đường bộ."),
]
for q, extra in CASUAL:
    add("tc", TC, "tu_choi", q, SCOPE + extra)

out = ROOT / "data/train/drafts/tai_nan_tu_choi_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
