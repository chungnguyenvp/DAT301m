"""C5 G5: trách nhiệm dân sự sau tai nạn và các tội về giao thông đường bộ.

Chỉ dùng các đơn vị BLDS/BLHS được giao, đang có hiệu lực tại 2026-10-01.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = []
B = "Bộ luật Dân sự 2015"
H = "Bộ luật Hình sự"


def t(unit):
    doc, leaf = unit.split(":", 1)
    day = "2017-01-01" if doc == "blds_2015" else "2025-07-01"
    return f"{doc}:{leaf}@{day}"


def add(loai, q, a, *refs):
    S.append({"key": f"tn-{1001 + len(S):04d}", "chu_de": "Tai nạn", "loai": loai,
              "cau_hoi": q, "dap_an": a, "can_cu": [t(r) for r in refs]})


# Năng lực bồi thường, nhiều người cùng gây hại, thời hiệu.
add("quy_tac", "Người đã thành niên tự gây thiệt hại khi đi xe đạp thì ai dùng tài sản để bồi thường?",
    "Người từ đủ mười tám tuổi trở lên gây thiệt hại phải tự bồi thường (khoản 1 Điều 586 " + B + ").",
    "blds_2015:d586:k1")
add("tinh_huong", "Con tôi chưa đủ mười lăm tuổi đạp xe làm vỡ kính nhà bên đường; cháu còn cha mẹ. Ai bồi thường?",
    "Cha, mẹ phải bồi thường toàn bộ. Nếu tài sản cha, mẹ không đủ mà con có tài sản riêng thì dùng tài sản đó bồi thường phần còn thiếu; trường hợp trong thời gian trường học trực tiếp quản lý được Điều 599 quy định riêng (khoản 2 Điều 586 " + B + ").",
    "blds_2015:d586:k2", "blds_2015:d599:k1", "blds_2015:d599:k3")
add("tinh_huong", "Em 16 tuổi đi xe đạp gây thiệt hại, tài sản riêng không đủ bồi thường thì cha mẹ có phải trả phần thiếu không?",
    "Có. Người từ đủ mười lăm đến chưa đủ mười tám tuổi trước hết bồi thường bằng tài sản của mình; nếu không đủ, cha mẹ bồi thường phần còn thiếu bằng tài sản của mình (khoản 2 Điều 586 " + B + ").",
    "blds_2015:d586:k2")
add("quy_tac", "Người được giám hộ đi bộ làm hỏng tài sản của người khác, có thể lấy tài sản của ai để bồi thường?",
    "Nếu người gây thiệt hại thuộc nhóm được khoản 3 Điều 586 quy định và có người giám hộ, có thể dùng tài sản của người được giám hộ để bồi thường. Nếu tài sản đó không có hoặc không đủ, người giám hộ bồi thường bằng tài sản mình, trừ khi chứng minh mình không có lỗi trong việc giám hộ (khoản 3 Điều 586 " + B + ").",
    "blds_2015:d586:k3")
add("doi_thuong", "người giám hộ ko có lỗi mà người được giám hộ đi đường gây hại thì vẫn phải bỏ tiền túi à",
    "Không, nếu người giám hộ chứng minh được mình không có lỗi trong việc giám hộ thì không phải dùng tài sản riêng để bồi thường; tài sản của người được giám hộ vẫn có thể được dùng theo khoản này (khoản 3 Điều 586 " + B + ").",
    "blds_2015:d586:k3")
add("tinh_huong", "Hai người cùng gây hư hỏng xe đạp của tôi. Tôi có thể yêu cầu họ liên đới bồi thường không?",
    "Có. Khi nhiều người cùng gây thiệt hại, họ phải liên đới bồi thường cho người bị thiệt hại (Điều 587 " + B + ").",
    "blds_2015:d587")
add("quy_tac", "Nếu nhiều người cùng gây tai nạn mà không xác định được mức độ lỗi từng người, phần bồi thường chia thế nào?",
    "Họ phải liên đới bồi thường; khi không xác định được mức độ lỗi thì bồi thường theo phần bằng nhau (Điều 587 " + B + ").",
    "blds_2015:d587")
add("quy_tac", "Thời hiệu khởi kiện yêu cầu bồi thường thiệt hại do vụ va chạm xe đạp bắt đầu từ khi nào?",
    "Là 03 năm kể từ ngày người có quyền yêu cầu biết hoặc phải biết quyền, lợi ích hợp pháp của mình bị xâm phạm (Điều 588 " + B + ").",
    "blds_2015:d588")
add("tinh_huong", "Sau tai nạn, tôi bị đăng thông tin xâm phạm uy tín và phải tốn chi phí hợp lý để hạn chế thiệt hại. Khoản này có được tính không?",
    "Có. Nếu uy tín bị xâm phạm, chi phí hợp lý để hạn chế, khắc phục thiệt hại là một khoản thiệt hại được bồi thường (điểm a khoản 1 Điều 592 " + B + ").",
    "blds_2015:d592:k1:a")

# Tài sản, thời hạn hưởng cấp dưỡng, kích thích, quản lý người và vật gây hại.
add("tinh_huong", "Một xe đạp đâm làm hỏng cổng nhà tôi. Giá trị phần cổng hư hỏng có thuộc thiệt hại về tài sản không?",
    "Có. Tài sản bị hư hỏng là một khoản thiệt hại do tài sản bị xâm phạm (khoản 1 Điều 589 " + B + ").",
    "blds_2015:d589:k1")
add("tinh_huong", "Quầy hàng của tôi bị va đổ, phải ngừng sử dụng để sửa. Phần lợi ích từ việc khai thác quầy bị mất có được tính không?",
    "Có thể được tính là lợi ích gắn với việc sử dụng, khai thác tài sản bị mất hoặc giảm sút, nếu chứng minh được thiệt hại đó (khoản 2 Điều 589 " + B + ").",
    "blds_2015:d589:k2")
add("tinh_huong", "Tôi phải thuê người che chắn xe đạp hỏng sau va chạm để tránh thiệt hại tăng thêm. Chi phí hợp lý đó thuộc khoản nào?",
    "Chi phí hợp lý để ngăn chặn, hạn chế và khắc phục thiệt hại thuộc thiệt hại do tài sản bị xâm phạm (khoản 3 Điều 589 " + B + ").",
    "blds_2015:d589:k3")
add("quy_tac", "Người bị tai nạn mất hoàn toàn khả năng lao động được hưởng bồi thường trong thời hạn nào?",
    "Từ thời điểm mất hoàn toàn khả năng lao động cho đến khi chết, trừ trường hợp có thỏa thuận khác (khoản 1 Điều 593 " + B + ").",
    "blds_2015:d593:k1")
add("tinh_huong", "Người có nghĩa vụ cấp dưỡng cho con chưa thành niên tử vong trong tai nạn. Con được hưởng tiền cấp dưỡng đến khi nào?",
    "Từ thời điểm người có nghĩa vụ cấp dưỡng chết đến khi con đủ mười tám tuổi; ngoại lệ là người từ đủ mười lăm đến chưa đủ mười tám tuổi đã lao động và có thu nhập đủ nuôi sống mình (điểm a khoản 2 Điều 593 " + B + ").",
    "blds_2015:d593:k2:a", "blds_2015:d593:k2")
add("tinh_huong", "Con đã thành thai khi cha qua đời vì tai nạn, sau đó sinh ra còn sống. Tiền cấp dưỡng tính từ ngày nào?",
    "Tiền cấp dưỡng được tính từ thời điểm người con sinh ra và còn sống; thời hạn hưởng theo điểm a khoản 2 Điều 593 (khoản 3 Điều 593 " + B + ").",
    "blds_2015:d593:k3", "blds_2015:d593:k2:a")
add("quy_tac", "Người thành niên không có khả năng lao động được người chết trong tai nạn cấp dưỡng trước đó thì hưởng đến khi nào?",
    "Nếu người chết có nghĩa vụ cấp dưỡng cho người này khi còn sống, người thành niên không có khả năng lao động được hưởng tiền cấp dưỡng từ thời điểm người đó chết cho đến khi người được cấp dưỡng chết (điểm b khoản 2 Điều 593 " + B + ").",
    "blds_2015:d593:k2:b", "blds_2015:d593:k2")
add("tinh_huong", "Tôi uống rượu đến mức mất khả năng nhận thức, làm chủ hành vi rồi đạp xe làm người khác bị thương. Tôi có phải bồi thường không?",
    "Có. Người do uống rượu hoặc dùng chất kích thích khác mà mất khả năng nhận thức và làm chủ hành vi, gây thiệt hại cho người khác thì phải bồi thường (khoản 1 Điều 596 " + B + ").",
    "blds_2015:d596:k1")
add("tinh_huong", "Một người cố ý cho người khác dùng chất kích thích khiến họ mất khả năng nhận thức, làm chủ hành vi và gây hại trên đường. Ai bồi thường?",
    "Người cố ý dùng chất kích thích làm người kia rơi vào tình trạng đó phải bồi thường cho người bị thiệt hại (khoản 2 Điều 596 " + B + ").",
    "blds_2015:d596:k2")
add("tinh_huong", "Học sinh chưa đủ mười lăm tuổi làm hỏng xe đạp người khác khi trường đang trực tiếp quản lý. Trường có phải bồi thường không?",
    "Trường học phải bồi thường thiệt hại xảy ra trong thời gian trực tiếp quản lý, trừ khi chứng minh được mình không có lỗi trong quản lý; khi đó cha, mẹ hoặc người giám hộ phải bồi thường (khoản 1 và khoản 3 Điều 599 " + B + ").",
    "blds_2015:d599:k1", "blds_2015:d599:k3")
add("quy_tac", "Trường học được miễn bồi thường thiệt hại do học sinh chưa đủ mười lăm tuổi gây ra khi nào?",
    "Khi chứng minh được mình không có lỗi trong quản lý. Trường hợp này cha, mẹ hoặc người giám hộ của người dưới mười lăm tuổi phải bồi thường (khoản 3 Điều 599 " + B + ").",
    "blds_2015:d599:k3", "blds_2015:d599:k1")
add("tinh_huong", "Người mất năng lực hành vi dân sự gây hư hỏng xe của khách trong thời gian bệnh viện trực tiếp quản lý. Bệnh viện chịu trách nhiệm gì?",
    "Bệnh viện phải bồi thường thiệt hại xảy ra trong thời gian trực tiếp quản lý, trừ khi chứng minh được mình không có lỗi trong quản lý; trường hợp đó cha, mẹ hoặc người giám hộ phải bồi thường (khoản 2 và khoản 3 Điều 599 " + B + ").",
    "blds_2015:d599:k2", "blds_2015:d599:k3")
add("tinh_huong", "Người học nghề giao hàng bằng xe đạp gây hại khi đang làm công việc được giao. Bên thuê có phải bồi thường không?",
    "Cá nhân hoặc pháp nhân sử dụng người học nghề phải bồi thường thiệt hại do người đó gây ra trong khi thực hiện công việc được giao; nếu người học nghề có lỗi, bên bồi thường có quyền yêu cầu hoàn trả một khoản tiền theo pháp luật (Điều 600 " + B + ").",
    "blds_2015:d600")
add("doi_thuong", "người làm công gây hỏng xe lúc làm việc được giao, bên thuê có đòi lại tiền từ họ dc ko",
    "Có quyền yêu cầu người làm công hoàn trả một khoản tiền theo pháp luật nếu người đó có lỗi trong việc gây thiệt hại. Cá nhân, pháp nhân sử dụng họ trước hết phải bồi thường thiệt hại do công việc được giao gây ra (Điều 600 " + B + ").",
    "blds_2015:d600")
add("tinh_huong", "Tôi đang giữ và sử dụng bò của người khác, bò chạy ra đường gây hại. Ai bồi thường?",
    "Người chiếm hữu, sử dụng súc vật phải bồi thường thiệt hại trong thời gian chiếm hữu, sử dụng, trừ khi có thỏa thuận khác (khoản 1 Điều 603 " + B + ").",
    "blds_2015:d603:k1")
add("tinh_huong", "Người khác hoàn toàn có lỗi làm con bò của tôi lao ra đường gây thiệt hại. Tôi hay người đó bồi thường?",
    "Người thứ ba hoàn toàn có lỗi làm súc vật gây thiệt hại phải bồi thường; nếu người thứ ba và chủ sở hữu cùng có lỗi thì phải liên đới bồi thường (khoản 2 Điều 603 " + B + ").",
    "blds_2015:d603:k2")
add("tinh_huong", "Bò bị người khác chiếm hữu trái pháp luật rồi gây tai nạn; chủ bò cũng có lỗi để xảy ra việc chiếm hữu đó. Ai bồi thường?",
    "Người chiếm hữu, sử dụng trái pháp luật phải bồi thường. Khi chủ sở hữu cũng có lỗi trong việc để súc vật bị chiếm hữu, sử dụng trái pháp luật, họ phải liên đới bồi thường (khoản 3 Điều 603 " + B + ").",
    "blds_2015:d603:k3")
add("doi_thuong", "bò thả rông theo tập quán rồi gây hại người đi đường thì chủ bò bồi thường theo gì vậy",
    "Chủ sở hữu bồi thường theo tập quán, nhưng tập quán đó không được trái pháp luật và đạo đức xã hội (khoản 4 Điều 603 " + B + ").",
    "blds_2015:d603:k4")
add("tinh_huong", "Cây ven lối đi đổ làm hỏng xe đạp. Ai có thể phải bồi thường thiệt hại do cây gây ra?",
    "Chủ sở hữu, người chiếm hữu hoặc người được giao quản lý cây cối phải bồi thường thiệt hại do cây gây ra (Điều 604 " + B + "). Ngoại lệ chung về bất khả kháng hoặc lỗi hoàn toàn của bên bị thiệt hại cần được xét theo khoản 2 Điều 584.",
    "blds_2015:d604", "blds_2015:d584:k2")
add("tinh_huong", "Giàn mái công trình cạnh đường rơi làm hỏng xe. Người thi công có lỗi thì trách nhiệm thế nào?",
    "Chủ sở hữu, người chiếm hữu hoặc người được giao quản lý, sử dụng công trình phải bồi thường. Nếu người thi công có lỗi trong việc để công trình gây thiệt hại thì người đó phải liên đới bồi thường (Điều 605 " + B + "). Ngoại lệ chung được xét theo khoản 2 Điều 584.",
    "blds_2015:d605", "blds_2015:d584:k2")

# Các tội khác nhau: cản trở, đưa xe không an toàn, điều động người, tổ chức đua, đua xe.
add("quy_tac", "Đặt vật sắc nhọn cản trở giao thông đường bộ có thể thuộc tội nào khi gây thiệt hại đủ điều kiện?",
    "Hành vi đặt, để, đổ trái phép vật sắc nhọn hoặc chướng ngại vật khác gây cản trở giao thông, gây thiệt hại thuộc một trong các trường hợp khoản 1, có thể thuộc tội cản trở giao thông đường bộ (khoản 1 Điều 261 " + H + "). Cần xác định hành vi trái phép, hậu quả và các tình tiết khác trước khi kết luận trách nhiệm hình sự.",
    "vbhn_135_2025_blhs:d261:k1")
add("tinh_huong", "Một người trái phép che khuất biển báo trên đèo, làm chết một người. Nếu đủ dấu hiệu tội cản trở giao thông, vị trí đèo ảnh hưởng khung thế nào?",
    "Nếu đã phạm tội cản trở giao thông đường bộ, thực hiện tại đèo là tình tiết thuộc khung khoản 2 Điều 261; khung này có phạt tiền từ 100.000.000 đồng đến 300.000.000 đồng hoặc phạt tù từ 02 năm đến 07 năm. Cần kiểm tra đủ yếu tố tội và tình tiết thực tế (điểm a khoản 2 Điều 261 " + H + ").",
    "vbhn_135_2025_blhs:d261:k2:a", "vbhn_135_2025_blhs:d261:k2", "vbhn_135_2025_blhs:d261:k1")
add("quy_tac", "Cản trở giao thông chưa gây hại nhưng có khả năng thực tế dẫn đến hậu quả đặc biệt nghiêm trọng thì Điều 261 xử lý ra sao?",
    "Nếu có khả năng thực tế dẫn đến hậu quả tại điểm a, b hoặc c khoản 3 mà không được ngăn chặn kịp thời, khoản 4 Điều 261 quy định phạt tiền từ 5.000.000 đồng đến 20.000.000 đồng hoặc cải tạo không giam giữ đến 01 năm. Phải đánh giá khả năng thực tế đó, không suy từ mọi chướng ngại vật (khoản 4 Điều 261 " + H + ").",
    "vbhn_135_2025_blhs:d261:k4", "vbhn_135_2025_blhs:d261:k3:a", "vbhn_135_2025_blhs:d261:k3:b", "vbhn_135_2025_blhs:d261:k3:c")
add("quy_tac", "Điều 262 nhắm đến ai khi xe cơ giới rõ ràng không đạt an toàn kỹ thuật được đưa ra đường gây thiệt hại?",
    "Nhắm đến người chịu trách nhiệm trực tiếp về việc điều động hoặc tình trạng kỹ thuật mà cho phép đưa phương tiện rõ ràng không bảo đảm tiêu chuẩn an toàn kỹ thuật vào sử dụng, gây thiệt hại thuộc các trường hợp luật định (khoản 1 Điều 262 " + H + ").",
    "vbhn_135_2025_blhs:d262:k1")
add("tinh_huong", "Người phụ trách kỹ thuật biết xe cơ giới rõ ràng không an toàn vẫn cho sử dụng, gây chết người. Khung cơ bản Điều 262 là gì?",
    "Nếu đủ các yếu tố của khoản 1 Điều 262 và không có tình tiết thuộc khung nặng hơn, khung cơ bản là phạt tiền từ 20.000.000 đồng đến 100.000.000 đồng, cải tạo không giam giữ đến 03 năm hoặc phạt tù từ 06 tháng đến 03 năm (điểm a khoản 1 Điều 262 " + H + ").",
    "vbhn_135_2025_blhs:d262:k1:a", "vbhn_135_2025_blhs:d262:k1")
add("quy_tac", "Tội điều động người không đủ điều kiện lái xe ở Điều 263 đòi hỏi người điều động có điều kiện gì?",
    "Người điều động phải có thẩm quyền và biết rõ người được điều động không đủ điều kiện được liệt kê, như không có giấy phép lái xe hoặc không đủ sức khỏe, độ tuổi; vẫn điều động họ lái xe tham gia giao thông và gây thiệt hại thuộc các trường hợp luật định (khoản 1 Điều 263 " + H + ").",
    "vbhn_135_2025_blhs:d263:k1")
add("tinh_huong", "Người có thẩm quyền biết rõ tài xế không có giấy phép mà vẫn điều động, sau đó gây chết người. Có thể xét Điều nào?",
    "Có thể xem xét khoản 1 Điều 263 nếu chứng minh được thẩm quyền, việc biết rõ tình trạng không có giấy phép, hành vi điều động và hậu quả. Trường hợp làm chết người thuộc điểm a khoản này; không thể kết luận có tội chỉ từ hậu quả (điểm a khoản 1 Điều 263 " + H + ").",
    "vbhn_135_2025_blhs:d263:k1:a", "vbhn_135_2025_blhs:d263:k1")
add("quy_tac", "Người tổ chức cuộc đua xe máy trái phép và người trực tiếp đua có cùng một điều luật hình sự không?",
    "Không. Tổ chức trái phép việc đua xe có gắn động cơ thuộc Điều 265; hành vi trực tiếp đua trái phép thuộc Điều 266 khi đáp ứng điều kiện hậu quả hoặc tiền sử xử lý của điều này (khoản 1 Điều 265 và khoản 1 Điều 266 " + H + ").",
    "vbhn_135_2025_blhs:d265:k1", "vbhn_135_2025_blhs:d266:k1")
add("tinh_huong", "Tôi tổ chức trái phép đua xe máy và còn tổ chức cá cược. Tình tiết cá cược ảnh hưởng khung nào?",
    "Nếu đã phạm tội tổ chức đua xe trái phép, tổ chức cá cược là tình tiết khoản 2 Điều 265, với khung phạt tiền từ 100.000.000 đồng đến 500.000.000 đồng hoặc phạt tù từ 04 năm đến 10 năm (điểm b khoản 2 Điều 265 " + H + ").",
    "vbhn_135_2025_blhs:d265:k2:b", "vbhn_135_2025_blhs:d265:k2")
add("quy_tac", "Đua xe trái phép chưa gây thiệt hại có thể bị xét tội đua xe trái phép theo Điều 266 khi nào?",
    "Có thể bị xem xét nếu người đua đã bị xử phạt vi phạm hành chính về hành vi quy định tại Điều 266 hoặc Điều 265, hoặc đã bị kết án về một trong các tội này, chưa được xóa án tích mà còn vi phạm (khoản 1 Điều 266 " + H + "). Không thể kết luận chỉ từ việc có cuộc đua.",
    "vbhn_135_2025_blhs:d266:k1")
add("tinh_huong", "Người trực tiếp đua xe trái phép làm hỏng tài sản trị giá từ 50.000.000 đồng đến dưới 100.000.000 đồng, không có tình tiết nặng hơn. Khung nào áp dụng?",
    "Nếu đủ điều kiện của điểm b khoản 1 Điều 266 và không có tình tiết thuộc khung nặng hơn, khung cơ bản là phạt tiền từ 10.000.000 đồng đến 50.000.000 đồng, cải tạo không giam giữ đến 02 năm hoặc phạt tù từ 06 tháng đến 03 năm (điểm b khoản 1 Điều 266 " + H + ").",
    "vbhn_135_2025_blhs:d266:k1:b", "vbhn_135_2025_blhs:d266:k1")


if __name__ == "__main__":
    out = ROOT / "data/train/drafts/tai_nan_02_cx.jsonl"
    out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
    print(len(S), "mẫu ->", out)
