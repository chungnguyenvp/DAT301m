"""Đợt 4a G5: Nộp phạt, giữ xe. Luật Xử lý vi phạm hành chính (văn bản hợp nhất 90/2026, bản từ 01/7/2026) và
NĐ 138/2021 (bản đã sửa từ 15/3/2026). Ghi data/train/drafts/nop_phat_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Xử lý vi phạm hành chính"
ND = "Nghị định 138/2021/NĐ-CP"
S = []
START = 1


def x(s):
    return f"vbhn_90_2026_xlvphc:{s}@2026-07-01"


def n(s, d="2022-01-01"):
    return f"nd_138_2021:{s}@{d}"


M26 = "2026-03-15"


def add(loai, q, a, *can_cu):
    S.append({"key": f"np-{START + len(S):04d}", "chu_de": "Nộp phạt, giữ xe", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Thời hiệu, biên bản, quyết định
add("quy_tac", "Vi phạm giao thông bao lâu thì hết thời hiệu xử phạt?",
    "Thời hiệu xử phạt vi phạm hành chính nói chung là 01 năm (điểm a khoản 1 Điều 6 " + LUAT + "). Với vi phạm đã kết "
    "thúc, thời hiệu tính từ thời điểm chấm dứt hành vi; với vi phạm đang thực hiện, tính từ thời điểm phát hiện hành vi "
    "(điểm b khoản 1 Điều 6).", x("d6:k1:a"), x("d6:k1:b"))
add("tinh_huong", "Tôi cố tình tránh mặt để không bị xử phạt thì thời hiệu xử phạt có hết không?",
    "Không hết theo cách đó. Trong thời hạn tính thời hiệu, nếu cá nhân cố tình trốn tránh, cản trở việc xử phạt thì thời "
    "hiệu được tính lại kể từ thời điểm chấm dứt hành vi trốn tránh, cản trở (điểm d khoản 1 Điều 6 " + LUAT + ").",
    x("d6:k1:d"), x("d6:k1"))
add("quy_tac", "Khi nào cảnh sát được phạt tại chỗ mà không cần lập biên bản?",
    "Xử phạt không lập biên bản áp dụng khi xử phạt cảnh cáo hoặc phạt tiền đến 500.000 đồng đối với cá nhân, 1.000.000 "
    "đồng đối với tổ chức (điểm a khoản 1 Điều 56 " + LUAT + "); khi đó người có thẩm quyền ra quyết định xử phạt tại chỗ "
    "(khoản 3 Điều 56).", x("d56:k1:a"), x("d56:k3"))
add("quy_tac", "Vi phạm bị camera, máy bắn tốc độ phát hiện thì có được phạt không lập biên bản không?",
    "Không. Trường hợp vi phạm hành chính được phát hiện bằng phương tiện, thiết bị kỹ thuật nghiệp vụ thì phải lập biên bản "
    "(khoản 2 Điều 56 " + LUAT + "), kể cả khi mức phạt thấp.", x("d56:k2"))
add("quy_tac", "Biên bản vi phạm giao thông phải lập ở đâu?",
    "Biên bản vi phạm hành chính phải được lập tại nơi xảy ra hành vi vi phạm; nếu lập tại trụ sở cơ quan của người có thẩm "
    "quyền hoặc địa điểm khác thì phải ghi rõ lý do vào biên bản (khoản 2 Điều 58 " + LUAT + ").", x("d58:k2"))
add("tinh_huong", "Tôi không đồng ý nên không ký biên bản vi phạm. Biên bản đó còn giá trị không?",
    "Vẫn có thể có giá trị. Khi người vi phạm không ký, biên bản phải có chữ ký của đại diện chính quyền cấp xã nơi xảy ra "
    "vi phạm hoặc của ít nhất 01 người chứng kiến xác nhận việc bạn không ký; nếu không có những chữ ký này thì phải ghi rõ "
    "lý do vào biên bản (khoản 4 Điều 58 " + LUAT + "). Biên bản có ghi quyền và thời hạn giải trình để bạn trình bày ý "
    "kiến (điểm e khoản 3 Điều 58).", x("d58:k4"), x("d58:k3:e"))
add("quy_tac", "Biên bản vi phạm hành chính được lập mấy bản và người vi phạm có được giữ không?",
    "Biên bản phải được lập ít nhất 02 bản, có chữ ký của người lập và người vi phạm (khoản 4 Điều 58 " + LUAT + "); lập "
    "xong phải giao cho cá nhân, tổ chức vi phạm 01 bản (khoản 5 Điều 58).", x("d58:k4"), x("d58:k5"))
add("quy_tac", "Biên bản vi phạm giao thông có thể lập và gửi bằng điện tử không?",
    "Có. Biên bản vi phạm hành chính có thể được lập, gửi bằng phương thức điện tử khi cơ quan của người có thẩm quyền và "
    "người vi phạm đáp ứng điều kiện về hạ tầng, kỹ thuật, thông tin (khoản 7 Điều 58 " + LUAT + ").", x("d58:k7"))
add("thu_tuc", "Sau khi lập biên bản vi phạm thì bao lâu có quyết định xử phạt?",
    "Theo khoản 1 Điều 66 " + LUAT + ": thông thường là 07 ngày làm việc kể từ ngày lập biên bản (10 ngày làm việc nếu phải "
    "chuyển hồ sơ đến người có thẩm quyền xử phạt); 01 tháng nếu người vi phạm yêu cầu giải trình hoặc phải xác minh tình "
    "tiết; 02 tháng nếu vụ việc đặc biệt nghiêm trọng, phức tạp cần thêm thời gian xác minh.",
    x("d66:k1"), x("d66:k1:a"), x("d66:k1:b"), x("d66:k1:c"))
add("thu_tuc", "Quyết định xử phạt được gửi cho người vi phạm bằng cách nào?",
    "Trong thời hạn 03 ngày làm việc kể từ ngày ra quyết định, người ra quyết định phải gửi cho người bị xử phạt (khoản 1 "
    "Điều 70 " + LUAT + "). Việc gửi có thể giao trực tiếp, gửi bưu chính bảo đảm, gửi bằng phương thức điện tử; nếu không "
    "làm được thì niêm yết công khai tại nơi cư trú hoặc gửi Ủy ban nhân dân cấp xã niêm yết (khoản 2 Điều 70).",
    x("d70:k1"), x("d70:k2"), x("d70:k2:c"), x("d70:k2:d"))

# ===== Thi hành, nộp phạt
add("doi_thuong", "bị phạt giao thông thì trong bao lâu phải nộp tiền",
    "Phải chấp hành quyết định xử phạt trong thời hạn 10 ngày kể từ ngày nhận quyết định; nếu quyết định ghi thời hạn thi "
    "hành nhiều hơn 10 ngày thì theo thời hạn đó (khoản 1 Điều 73 " + LUAT + ").", x("d73:k1"))
add("tinh_huong", "Tôi đang khiếu nại quyết định xử phạt. Tôi có phải nộp phạt trước không?",
    "Có. Trường hợp người bị xử phạt khiếu nại, khởi kiện quyết định xử phạt thì vẫn phải chấp hành quyết định, trừ trường "
    "hợp được đình chỉ thi hành theo quy định; việc khiếu nại, khởi kiện được giải quyết theo pháp luật (khoản 1 Điều 73 "
    + LUAT + ").", x("d73:k1"))
add("tinh_huong", "Tôi nộp phạt giao thông trễ hạn. Có bị tính thêm tiền không?",
    "Có. Quá thời hạn thi hành mà chưa nộp tiền phạt thì bị cưỡng chế thi hành quyết định xử phạt, và cứ mỗi ngày chậm nộp "
    "phải nộp thêm 0,05% tính trên tổng số tiền phạt chưa nộp (khoản 1 Điều 78 " + LUAT + ").", x("d78:k1"))
add("thu_tuc", "Nộp tiền phạt vi phạm giao thông ở đâu?",
    "Người bị xử phạt nộp tiền phạt tại Kho bạc Nhà nước hoặc nộp vào tài khoản của Kho bạc Nhà nước ghi trong quyết định "
    "xử phạt (khoản 1 Điều 78 " + LUAT + "). Người thu tiền phạt phải giao chứng từ thu tiền phạt cho người nộp (khoản 3 "
    "Điều 78).", x("d78:k1"), x("d78:k3"))
add("quy_tac", "Cảnh sát có được thu tiền phạt trực tiếp không?",
    "Chỉ trong một số trường hợp: tại vùng sâu, vùng xa, biên giới, miền núi đi lại khó khăn thì người bị xử phạt có thể nộp "
    "cho người có thẩm quyền xử phạt, người này phải nộp vào Kho bạc trong thời hạn không quá 07 ngày; xử phạt trên biển "
    "hoặc ngoài giờ hành chính thì người có thẩm quyền được thu trực tiếp và nộp Kho bạc trong 02 ngày làm việc (khoản 2 "
    "Điều 78 " + LUAT + "). Mọi trường hợp thu tiền đều phải giao chứng từ (khoản 3 Điều 78).", x("d78:k2"), x("d78:k3"))
add("quy_tac", "Quyết định xử phạt giao thông để lâu không nộp thì có hết hiệu lực không?",
    "Thời hiệu thi hành quyết định xử phạt là 01 năm kể từ ngày ra quyết định; quá thời hạn thì không thi hành nữa, trừ phần "
    "tịch thu tang vật, phương tiện và biện pháp khắc phục hậu quả vẫn phải thực hiện (khoản 1 Điều 74 " + LUAT + "). Nếu "
    "người bị xử phạt cố tình trốn tránh, trì hoãn thì thời hiệu tính từ khi chấm dứt việc trốn tránh, trì hoãn (khoản 2 "
    "Điều 74).", x("d74:k1"), x("d74:k2"))
add("thu_tuc", "Bị phạt tiền nặng mà không đủ tiền nộp một lần thì có được nộp nhiều lần không?",
    "Được nếu đủ điều kiện: cá nhân bị phạt từ 15.000.000 đồng trở lên (tổ chức từ 150.000.000 đồng trở lên), đang gặp khó "
    "khăn đặc biệt về kinh tế và có đơn đề nghị được Ủy ban nhân dân cấp xã hoặc cơ quan, tổ chức nơi học tập, làm việc xác "
    "nhận (khoản 1 Điều 79 " + LUAT + "). Thời hạn nộp nhiều lần không quá 06 tháng, tối đa 03 lần, lần đầu tối thiểu 40% "
    "tổng số tiền phạt (khoản 2 Điều 79).", x("d79:k1:a"), x("d79:k1:b"), x("d79:k2"))
add("tinh_huong", "Xe tôi bị tạm giữ và tôi được nộp phạt nhiều lần. Khi nào tôi lấy được xe?",
    "Sau khi nộp tiền phạt lần đầu thì người vi phạm được nhận lại tang vật, phương tiện bị tạm giữ (khoản 2 Điều 125 " + LUAT
    + ").", x("d125:k2"))
add("thu_tuc", "Gặp khó khăn do tai nạn, bệnh hiểm nghèo thì có được hoãn nộp phạt không?",
    "Có thể được hoãn khi: cá nhân bị phạt tiền từ 2.000.000 đồng trở lên và đang gặp khó khăn về kinh tế do thiên tai, "
    "thảm họa, hỏa hoạn, dịch bệnh, mắc bệnh hiểm nghèo, tai nạn, có xác nhận của Ủy ban nhân dân cấp xã hoặc nơi học tập, "
    "làm việc (thêm xác nhận của cơ sở khám bệnh nếu do bệnh, tai nạn) (khoản 1 Điều 76 " + LUAT + "). Thời hạn hoãn không "
    "quá 03 tháng kể từ ngày có quyết định hoãn (khoản 2 Điều 76).", x("d76:k1:a"), x("d76:k1:b"), x("d76:k2"))
add("quy_tac", "Được hoãn nộp phạt thì có lấy lại được giấy tờ, xe đang bị tạm giữ không?",
    "Có. Cá nhân, tổ chức được hoãn chấp hành quyết định xử phạt được nhận lại giấy tờ, tang vật, phương tiện đang bị tạm "
    "giữ theo khoản 6 Điều 125 (khoản 3 Điều 76 " + LUAT + ").", x("d76:k3"))
add("quy_tac", "Trường hợp nào cá nhân được miễn toàn bộ tiền phạt?",
    "Theo khoản 4 Điều 77 " + LUAT + ", cá nhân không có khả năng thi hành được miễn toàn bộ tiền phạt nếu đã được hoãn mà "
    "tiếp tục gặp khó khăn về kinh tế do thiên tai, thảm họa, hỏa hoạn, dịch bệnh, bệnh hiểm nghèo, tai nạn (có xác nhận), "
    "hoặc bị phạt tiền từ 2.000.000 đồng trở lên và đang gặp khó khăn đặc biệt, đột xuất về kinh tế vì các lý do đó (có xác "
    "nhận theo quy định).", x("d77:k4"), x("d77:k4:a"), x("d77:k4:b"))
add("thu_tuc", "Xin giảm, miễn tiền phạt thì làm thế nào và bao lâu có trả lời?",
    "Người vi phạm làm đơn đề nghị giảm, miễn kèm xác nhận của cơ quan, tổ chức có thẩm quyền gửi người đã ra quyết định xử "
    "phạt; trong thời hạn 05 ngày làm việc kể từ ngày nhận đơn, người đó xem xét, quyết định và thông báo; nếu không đồng ý "
    "thì phải nêu rõ lý do (khoản 6 Điều 77 " + LUAT + ").", x("d77:k6"))

# ===== Tạm giữ phương tiện, giấy tờ (Luật Điều 125, 126)
add("quy_tac", "Khi nào cảnh sát được tạm giữ xe vi phạm?",
    "Việc tạm giữ tang vật, phương tiện, giấy phép chỉ được áp dụng khi thật cần thiết: để xác định vi phạm hoặc làm rõ tình "
    "tiết mà nếu không tạm giữ thì không có căn cứ lập biên bản, ra quyết định xử phạt; để ngăn chặn ngay vi phạm mà nếu "
    "không tạm giữ sẽ gây hậu quả nghiêm trọng; hoặc để bảo đảm thi hành quyết định xử phạt (khoản 1 Điều 125 " + LUAT + ").",
    x("d125:k1"), x("d125:k1:a"), x("d125:k1:b"), x("d125:k1:c"))
add("doi_thuong", "bị giữ xe thì giữ tối đa bao lâu",
    "Thời hạn tạm giữ tang vật, phương tiện, giấy phép không quá 07 ngày làm việc kể từ ngày tạm giữ; nếu phải chuyển hồ sơ "
    "đến người có thẩm quyền xử phạt thì không quá 10 ngày làm việc. Có thể kéo dài nhưng không quá 01 tháng (vụ việc phải "
    "giải trình hoặc xác minh), và không quá 02 tháng với vụ việc đặc biệt nghiêm trọng, phức tạp (khoản 8 Điều 125 " + LUAT
    + ").", x("d125:k8"))
add("quy_tac", "Chỉ bị phạt tiền thì cảnh sát giữ giấy tờ gì để bảo đảm tôi nộp phạt?",
    "Trường hợp chỉ áp dụng hình thức phạt tiền, người có thẩm quyền có quyền tạm giữ một trong các giấy tờ theo thứ tự: giấy "
    "phép lái xe, hoặc giấy phép lưu hành phương tiện, hoặc giấy tờ cần thiết khác liên quan, cho đến khi chấp hành xong quyết "
    "định xử phạt; nếu không có các giấy tờ đó thì có thể tạm giữ phương tiện (khoản 6 Điều 125 " + LUAT + ").", x("d125:k6"))
add("thu_tuc", "Bị tạm giữ xe thì có được nhận biên bản, quyết định tạm giữ không?",
    "Có. Biên bản tạm giữ phải ghi rõ tên, số lượng, chủng loại, tình trạng phương tiện bị tạm giữ, có chữ ký của người tạm "
    "giữ và người vi phạm, lập 02 bản và giao người vi phạm 01 bản (khoản 9 Điều 125 " + LUAT + "). Trong 24 giờ kể từ khi "
    "lập biên bản, người lập phải báo cáo người có thẩm quyền để ra quyết định tạm giữ, và quyết định phải giao cho người vi "
    "phạm 01 bản; nếu không ra quyết định tạm giữ thì phải trả lại ngay (điểm c, điểm d khoản 4 Điều 125).",
    x("d125:k9"), x("d125:k4:c"), x("d125:k4:d"))
add("tinh_huong", "Xe của tôi bị mất linh kiện trong thời gian bị tạm giữ. Ai chịu trách nhiệm?",
    "Người ra quyết định tạm giữ có trách nhiệm bảo quản phương tiện; nếu phương tiện bị mất, bán trái quy định, đánh tráo, "
    "hư hỏng, mất linh kiện, thay thế thì người ra quyết định tạm giữ phải chịu trách nhiệm bồi thường và bị xử lý theo quy "
    "định (khoản 5 Điều 125 " + LUAT + "). Bạn có quyền yêu cầu lập biên bản và yêu cầu bồi thường (khoản 3 Điều 10 " + ND
    + ").", x("d125:k5"), n("d10:k3"))
add("quy_tac", "Xe bị tạm giữ có được niêm phong không và niêm phong trước mặt ai?",
    "Khi tạm giữ, người có thẩm quyền phải niêm phong tang vật, phương tiện (trừ một số trường hợp như động vật, thực vật "
    "sống, hàng dễ hư hỏng, hàng siêu trường siêu trọng, hàng không thể niêm phong) (khoản 5a Điều 125 " + LUAT + "). Việc "
    "niêm phong phải tiến hành ngay trước mặt người vi phạm; nếu vắng mặt thì trước mặt đại diện gia đình, đại diện tổ chức, "
    "đại diện chính quyền cấp xã hoặc ít nhất 01 người chứng kiến (khoản 5b Điều 125).", x("d125:k5a"), x("d125:k5b"))
add("tinh_huong", "Tôi có nhà và chỗ để xe đàng hoàng. Có thể xin tự giữ xe vi phạm thay vì để ở bãi không?",
    "Có thể. Phương tiện bị tạm giữ để bảo đảm thi hành quyết định xử phạt có thể được giao cho người vi phạm giữ, bảo quản "
    "dưới sự quản lý của cơ quan có thẩm quyền nếu cá nhân có nơi thường trú, tạm trú còn thời hạn hoặc xác nhận nơi công "
    "tác, có nơi giữ, bảo quản phương tiện, hoặc có khả năng tài chính đặt tiền bảo lãnh (khoản 1 Điều 14 " + ND + "; khoản "
    "10 Điều 125 " + LUAT + "). Bạn làm đơn gửi người có thẩm quyền tạm giữ, người này xem xét trong thời hạn không quá 02 "
    "ngày làm việc (khoản 2 Điều 14 " + ND + ").", n("d14:k1"), n("d14:k1:a"), x("d125:k10"), n("d14:k2:b"))
add("quy_tac", "Trường hợp nào không được tự giữ, bảo quản xe vi phạm?",
    "Theo khoản 7 Điều 14 " + ND + ", không giao xe cho người vi phạm giữ khi: xe là vật chứng vụ án hình sự; xe dùng để đua "
    "xe trái phép, chống người thi hành công vụ, gây rối hoặc gây tai nạn giao thông; không có giấy đăng ký hoặc giấy đăng ký "
    "bị làm giả, sửa chữa; biển số giả, số khung, số máy bị thay đổi, xóa trái phép; hoặc xe sẽ bị tịch thu.",
    n("d14:k7"), n("d14:k7:b"), n("d14:k7:c"), n("d14:k7:đ"))
add("tinh_huong", "Được giao tự giữ xe vi phạm ở nhà, tôi có được chạy xe đó đi làm không?",
    "Không. Trong thời gian được giao giữ, bảo quản, người vi phạm không được sử dụng phương tiện đó tham gia giao thông và "
    "không được tự ý thay đổi nơi giữ nếu không có sự đồng ý bằng văn bản của người có thẩm quyền tạm giữ (khoản 4 Điều 14 "
    + ND + "). Vi phạm điều này thì xe có thể bị chuyển về nơi tạm giữ của cơ quan (khoản 5 Điều 14).",
    n("d14:k4"), n("d14:k5"))
add("thu_tuc", "Đặt tiền bảo lãnh để lấy xe về giữ thì phải đặt bao nhiêu?",
    "Mức tiền đặt bảo lãnh ít nhất bằng mức tiền phạt tối đa của khung tiền phạt quy định cho hành vi vi phạm; nếu có nhiều "
    "hành vi trong cùng vụ thì ít nhất bằng tổng mức phạt tối đa của các hành vi. Tiền có thể nộp trực tiếp hoặc qua tài "
    "khoản của cơ quan có thẩm quyền tạm giữ (điểm c khoản 3 Điều 15 " + ND + ", nội dung có hiệu lực từ ngày 15/3/2026).",
    n("d15:k3:c", M26), n("d15:k3"))
add("quy_tac", "Đã đặt tiền bảo lãnh mà không nộp phạt đúng hạn thì sao?",
    "Trong thời hạn 10 ngày kể từ ngày hết thời hạn thi hành quyết định xử phạt mà người vi phạm không chấp hành, người có "
    "thẩm quyền ra quyết định khấu trừ tiền đặt bảo lãnh (khoản 6 Điều 15 " + ND + ", nội dung có hiệu lực từ ngày "
    "15/3/2026). Quyết định khấu trừ được coi là căn cứ xác định đã thi hành xong quyết định xử phạt và được đưa xe vào sử "
    "dụng (khoản 7 Điều 15).", n("d15:k6", M26), n("d15:k7"))
add("thu_tuc", "Đi lấy xe bị tạm giữ cần mang theo giấy tờ gì?",
    "Phải có quyết định trả lại phương tiện của người có thẩm quyền (khoản 1 Điều 16 " + ND + "). Khi nhận, người quản lý "
    "kiểm tra quyết định trả lại và thẻ căn cước, căn cước điện tử hoặc thẻ căn cước công dân của người đến nhận; người đến "
    "nhận phải là người vi phạm, chủ sở hữu, người quản lý, người sử dụng hợp pháp hoặc người được ủy quyền theo quy định "
    "(điểm a khoản 2 Điều 16, nội dung có hiệu lực từ ngày 15/3/2026).", n("d16:k1", M26), n("d16:k2:a", M26))
add("quy_tac", "Lấy xe bị tạm giữ có phải trả phí gửi xe ở bãi không?",
    "Có, nếu xe không thuộc trường hợp bị tịch thu: người vi phạm khi nhận lại phải trả chi phí lưu kho, bến bãi, bảo quản "
    "trong thời gian bị tạm giữ (điểm a khoản 4 Điều 16 " + ND + "). Không thu các chi phí này nếu chủ phương tiện không có "
    "lỗi trong việc vi phạm hoặc phương tiện bị tịch thu (khoản 7 Điều 126 " + LUAT + ").", n("d16:k4:a"), x("d126:k7"))
add("tinh_huong", "Xe tôi bị người khác lấy trộm để đi vi phạm rồi bị tạm giữ. Tôi có phải trả phí bãi không?",
    "Không phải trả. Không thu phí lưu kho, phí bến bãi, phí bảo quản trong thời gian phương tiện bị tạm giữ nếu chủ phương "
    "tiện không có lỗi trong việc vi phạm hành chính (khoản 7 Điều 126 " + LUAT + "). Phương tiện bị chiếm đoạt, sử dụng "
    "trái phép để vi phạm thuộc trường hợp tịch thu thì được trả lại cho chủ sở hữu hợp pháp (khoản 1 Điều 126).",
    x("d126:k7"), x("d126:k1"))
add("quy_tac", "Nộp phạt xong thì giấy phép lái xe bị tạm giữ được trả khi nào?",
    "Giấy tờ, phương tiện bị tạm giữ để bảo đảm thi hành quyết định xử phạt theo khoản 6 Điều 125 phải được trả ngay cho "
    "người bị xử phạt sau khi thi hành xong quyết định xử phạt (khoản 2 Điều 126 " + LUAT + ").", x("d126:k2"))
add("tinh_huong", "Hết thời hạn tạm giữ mà tôi không đến nhận xe thì xe bị xử lý thế nào?",
    "Nếu xác định được người vi phạm, chủ sở hữu thì người ra quyết định tạm giữ phải thông báo 02 lần (lần đầu trong 03 ngày "
    "làm việc kể từ khi hết hạn tạm giữ, lần hai trong 07 ngày làm việc sau đó). Hết 01 tháng kể từ lần thông báo thứ hai mà "
    "không đến nhận thì trong 05 ngày làm việc, người có thẩm quyền ra quyết định tịch thu (điểm a khoản 4 Điều 126 " + LUAT
    + ").", x("d126:k4:a"), x("d126:k4"))
add("quy_tac", "Giữ xe để bảo đảm nộp phạt mà người vi phạm không nộp phạt thì xe bị xử lý ra sao?",
    "Trong thời hạn 05 ngày làm việc kể từ ngày hết thời hạn thi hành quyết định xử phạt mà người bị xử phạt không thi hành, "
    "người có thẩm quyền tạm giữ chuyển phương tiện cho người có thẩm quyền cưỡng chế để quyết định kê biên, bán đấu giá "
    "nhằm bảo đảm thi hành quyết định xử phạt (khoản 4a Điều 126 " + LUAT + ").", x("d126:k4a"))
add("quy_tac", "Bằng lái bị tạm giữ quá hạn mà không đến nhận thì sao?",
    "Giấy phép đã quá thời hạn tạm giữ hoặc hết thời hiệu thi hành quyết định xử phạt mà người vi phạm không đến nhận không "
    "có lý do chính đáng thì trong 10 ngày làm việc, người có thẩm quyền tạm giữ chuyển cho cơ quan đã cấp để thu hồi và "
    "thông báo cho người vi phạm (khoản 4b Điều 126 " + LUAT + ").", x("d126:k4b"))
add("quy_tac", "Đang bị tạm giữ bằng lái chờ quyết định tước thì có được lái xe không?",
    "Việc tạm giữ giấy phép trong thời gian chờ ra quyết định không làm ảnh hưởng quyền sử dụng giấy phép của người đó "
    "(khoản 7 Điều 125 " + LUAT + ").", x("d125:k7"))

# ===== Quyền, nghĩa vụ người có xe bị tạm giữ (NĐ 138)
add("quy_tac", "Người có xe bị tạm giữ có những quyền gì?",
    "Theo Điều 10 " + ND + ", người có phương tiện bị tạm giữ được khiếu nại, tố cáo, kiến nghị, phản ánh hành vi, quyết "
    "định trái pháp luật của người có thẩm quyền tạm giữ; được kiểm tra trước khi nhận lại phương tiện khi hết thời hạn tạm "
    "giữ; được yêu cầu lập biên bản và yêu cầu bồi thường nếu tài sản bị mất, đánh tráo, hư hỏng, thiếu hụt trong thời gian "
    "tạm giữ.", n("d10:k1"), n("d10:k2"), n("d10:k3"))
add("quy_tac", "Người có xe bị tạm giữ có nghĩa vụ gì?",
    "Phải chấp hành nghiêm chỉnh quyết định tạm giữ, tịch thu và nhận lại phương tiện, giấy tờ bị tạm giữ theo đúng thời hạn "
    "ghi trong quyết định tạm giữ (khoản 1, khoản 2 Điều 11 " + ND + ").", n("d11:k1"), n("d11:k2"))
add("quy_tac", "Cơ quan quản lý có được cho mượn hay sử dụng xe đang bị tạm giữ không?",
    "Không. Nghiêm cấm chiếm đoạt, bán, trao đổi, cầm cố, thế chấp, đánh tráo, thay thế, sử dụng trái pháp luật tang vật, "
    "phương tiện bị tạm giữ; mang phương tiện ra khỏi nơi tạm giữ mà không được phép; làm mất, hủy hoại, cố ý làm hư hỏng "
    "phương tiện bị tạm giữ (Điều 4 " + ND + ").", n("d4:k1"), n("d4:k2"), n("d4:k3"))
add("quy_tac", "Xe máy, ô tô bị tạm giữ phải được bảo quản thế nào?",
    "Tang vật, phương tiện bị tạm giữ phải được quản lý, bảo quản chặt chẽ, an toàn, dễ kiểm tra, tránh nhầm lẫn và bảo đảm "
    "tính nguyên vẹn (khoản 1, khoản 2 Điều 3 " + ND + "). Phương tiện có sử dụng xăng, dầu phải để cách biệt với tang vật "
    "khác, cách xa nguồn lửa, nguồn nhiệt và sẵn sàng điều kiện chữa cháy (khoản 1 Điều 13).", n("d3:k1"), n("d3:k2"),
    n("d13:k1"))
add("quy_tac", "Bãi giữ xe vi phạm ngoài trời phải đáp ứng điều kiện gì?",
    "Nơi tạm giữ là nhà, kho, bãi phải bảo đảm an toàn, an ninh, có hàng rào, nội quy; phải khô ráo, thoáng khí, nếu ở ngoài "
    "trời thì phải có mái che hoặc biện pháp chống mưa, nắng; có chiếu sáng và phương tiện phòng cháy, chữa cháy (khoản 2 "
    "Điều 6 " + ND + ").", n("d6:k2"), n("d6:k2:b"))
add("thu_tuc", "Khi nhận lại xe bị tạm giữ, thủ tục giao nhận diễn ra thế nào?",
    "Người quản lý kiểm tra quyết định trả lại và giấy tờ tùy thân của người đến nhận; người nhận đối chiếu với biên bản tạm "
    "giữ để kiểm tra chủng loại, số lượng, chất lượng, hiện trạng phương tiện dưới sự chứng kiến của người quản lý, và việc "
    "giao nhận phải được lập thành biên bản (điểm a, điểm b khoản 2 Điều 16 " + ND + ").", n("d16:k2:a", M26), n("d16:k2:b"))

out = ROOT / "data/train/drafts/nop_phat_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
