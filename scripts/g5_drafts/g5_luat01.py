"""Đợt 8a G5: Luật lõi, quy tắc giao thông trong Luật Trật tự, an toàn giao thông đường bộ 36/2024 (Điều 9–33, 40).
Ghi data/train/drafts/luat_loi_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
S = []
START = 1


def l(s, d="2025-01-01"):
    return f"luat_36_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"lu-{START + len(S):04d}", "chu_de": "Luật lõi", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Hành vi bị nghiêm cấm (Điều 9)
add("quy_tac", "Uống một chút bia rồi lái xe có vi phạm luật không?",
    "Có. Điều khiển phương tiện tham gia giao thông đường bộ mà trong máu hoặc hơi thở có nồng độ cồn là hành vi bị nghiêm "
    "cấm (khoản 2 Điều 9 " + LUAT + "). Luật cấm mọi mức nồng độ cồn, không có ngưỡng được phép.", l("d9:k2"))
add("doi_thuong", "đi xe máy cầm điện thoại xem bản đồ có bị cấm ko",
    "Bị cấm nếu dùng tay cầm và sử dụng điện thoại hoặc thiết bị điện tử khác khi điều khiển phương tiện đang di chuyển trên "
    "đường bộ (khoản 6 Điều 9 " + LUAT + ").", l("d9:k6"))
add("quy_tac", "Lái xe mà trong người có chất ma túy có bị cấm không?",
    "Có. Điều khiển phương tiện tham gia giao thông mà trong cơ thể có chất ma túy hoặc chất kích thích khác mà pháp luật cấm "
    "sử dụng là hành vi bị nghiêm cấm (khoản 3 Điều 9 " + LUAT + ").", l("d9:k3"))
add("quy_tac", "Lạng lách, đánh võng, rú ga liên tục có bị luật cấm không?",
    "Có. Đua xe, tổ chức đua xe, xúi giục, giúp sức, cổ vũ đua xe trái phép; điều khiển phương tiện lạng lách, đánh võng, rú "
    "ga liên tục đều là hành vi bị nghiêm cấm (khoản 5 Điều 9 " + LUAT + ").", l("d9:k5"))
add("quy_tac", "Đứng xem và cổ vũ đua xe trái phép có vi phạm luật không?",
    "Có. Cổ vũ, xúi giục, giúp sức đua xe trái phép là hành vi bị nghiêm cấm cùng với việc đua xe và tổ chức đua xe (khoản 5 "
    "Điều 9 " + LUAT + ").", l("d9:k5"))
add("quy_tac", "Gây tai nạn rồi bỏ chạy thì vi phạm điều gì?",
    "Bỏ trốn sau khi gây tai nạn giao thông đường bộ để trốn tránh trách nhiệm, hoặc khi có điều kiện mà cố ý không cứu giúp "
    "người bị nạn, là hành vi bị nghiêm cấm (khoản 26 Điều 9 " + LUAT + ").", l("d9:k26"))
add("quy_tac", "Bẻ cong, che biển số xe có bị cấm không?",
    "Có. Bẻ cong, che lấp biển số xe; làm thay đổi chữ, số, màu sắc, hình dạng, kích thước của biển số; gắn biển số không do "
    "cơ quan có thẩm quyền cấp hoặc không đúng vị trí đều bị nghiêm cấm (khoản 17 Điều 9 " + LUAT + ").", l("d9:k17"))
add("quy_tac", "Thả flycam bay ngang đường gây cản trở giao thông có bị cấm không?",
    "Có. Điều khiển vật thể bay, tàu bay không người lái, phương tiện bay siêu nhẹ hoạt động trong phạm vi khổ giới hạn đường "
    "bộ gây cản trở hoặc nguy cơ mất an toàn cho người, phương tiện tham gia giao thông bị nghiêm cấm, trừ trường hợp được "
    "cấp phép bay (khoản 27 Điều 9 " + LUAT + ").", l("d9:k27"))
add("quy_tac", "Ném đá vào xe đang chạy trên đường thì vi phạm gì?",
    "Ném gạch, đất, đá, cát hoặc vật thể khác vào người, phương tiện đang tham gia giao thông, hoặc cản trở người, phương tiện "
    "tham gia giao thông, là hành vi bị nghiêm cấm (khoản 21 Điều 9 " + LUAT + ").", l("d9:k21"))
add("quy_tac", "Rải đinh hoặc đổ dầu nhớt ra đường có bị cấm không?",
    "Có. Rải vật sắc nhọn, đổ chất gây trơn trượt trên đường bộ; đặt chướng ngại vật trái phép; làm rơi vãi đất đá, vật liệu, "
    "phế thải; xả thải gây mất an toàn giao thông là hành vi bị nghiêm cấm (khoản 20 Điều 9 " + LUAT + ").", l("d9:k20"))
add("quy_tac", "Xe không làm nhiệm vụ mà vẫn bật còi, đèn ưu tiên thì có vi phạm không?",
    "Có. Sử dụng quyền của xe ưu tiên khi không thực hiện nhiệm vụ, hoặc lắp đặt, sử dụng thiết bị phát tín hiệu ưu tiên không "
    "đúng quy định là hành vi bị nghiêm cấm (khoản 24 Điều 9 " + LUAT + ").", l("d9:k24"))
add("quy_tac", "Hiện nay có được làm gián đoạn thiết bị giám sát hành trình, camera ghi hình người lái không?",
    "Không. Theo khoản 18 Điều 9 " + LUAT + " (nội dung có hiệu lực từ ngày 01/7/2026), làm gián đoạn hoạt động hoặc làm sai "
    "lệch dữ liệu của thiết bị giám sát hành trình, thiết bị ghi nhận hình ảnh người lái xe, khoang chở khách là hành vi bị "
    "nghiêm cấm. Dùng dữ liệu hình ảnh đó để xâm phạm nhân phẩm, đời tư người khác cũng bị cấm (khoản 18a Điều 9).",
    l("d9:k18", "2026-07-01"), l("d9:k18a", "2026-07-01"))

# ===== Quy tắc chung, dây an toàn, trẻ em (Điều 10)
add("quy_tac", "Ngồi ghế sau ô tô có phải thắt dây an toàn không?",
    "Có. Người lái xe và người được chở trên xe ô tô phải thắt dây đai an toàn tại những chỗ có trang bị dây đai an toàn khi "
    "tham gia giao thông (khoản 2 Điều 10 " + LUAT + "), không phân biệt ghế trước hay ghế sau.", l("d10:k2"))
add("tinh_huong", "Con tôi 8 tuổi, cao 1,3 mét. Cháu có được ngồi ghế trước cạnh tôi khi tôi lái ô tô không?",
    "Không. Theo khoản 3 Điều 10 " + LUAT + " (nội dung có hiệu lực từ ngày 01/7/2026), khi chở trẻ em dưới 10 tuổi và chiều "
    "cao dưới 1,35 mét, người lái xe không được cho trẻ ngồi cùng hàng ghế với mình (trừ xe chỉ có một hàng ghế), và phải sử "
    "dụng, hướng dẫn sử dụng thiết bị an toàn phù hợp cho trẻ em (trừ xe kinh doanh vận tải hành khách).",
    l("d10:k3", "2026-07-01"))
add("doi_thuong", "chở con nhỏ trên ô tô có bắt buộc ghế trẻ em ko",
    "Theo khoản 3 Điều 10 " + LUAT + " (nội dung có hiệu lực từ ngày 01/7/2026), khi chở trẻ em dưới 10 tuổi và chiều cao "
    "dưới 1,35 mét, người lái xe phải sử dụng, hướng dẫn sử dụng thiết bị an toàn phù hợp cho trẻ em, trừ xe ô tô kinh doanh "
    "vận tải hành khách; đồng thời không được cho trẻ ngồi cùng hàng ghế với người lái (trừ xe chỉ có một hàng ghế).",
    l("d10:k3", "2026-07-01"))
add("quy_tac", "Quy tắc chung khi tham gia giao thông đường bộ là gì?",
    "Người tham gia giao thông đường bộ phải đi bên phải theo chiều đi của mình, đi đúng làn đường, phần đường quy định, chấp "
    "hành báo hiệu đường bộ và các quy tắc giao thông khác (khoản 1 Điều 10 " + LUAT + ").", l("d10:k1"))

# ===== Tốc độ, làn đường, vượt xe (Điều 12–14)
add("quy_tac", "Những trường hợp nào bắt buộc phải giảm tốc độ?",
    "Theo khoản 3 Điều 12 " + LUAT + ", phải quan sát, giảm tốc độ hoặc dừng lại khi: đến nơi có vạch kẻ đường cho người đi "
    "bộ hoặc có người đi bộ, xe lăn đang qua đường; có báo hiệu nguy hiểm hoặc chướng ngại vật; chuyển hướng hoặc tầm nhìn "
    "hạn chế; nơi đường giao nhau, đường hẹp, đường vòng, đèo dốc; nơi cầu, cống hẹp, hầm; gần trường học, bệnh viện, chợ, "
    "khu đông dân cư; gặp xe ưu tiên; trời mưa, sương, đường trơn trượt…",
    l("d12:k3"), l("d12:k3:a"), l("d12:k3:e"), l("d12:k3:m"))
add("tinh_huong", "Đi qua cổng trường học lúc tan học thì tôi phải làm gì?",
    "Khu vực có trường học thuộc trường hợp người điều khiển phương tiện phải quan sát, giảm tốc độ hoặc dừng lại để bảo đảm an "
    "toàn (điểm e khoản 3 Điều 12 " + LUAT + ").", l("d12:k3:e"), l("d12:k3"))
add("quy_tac", "Đường nhiều làn thì chuyển làn phải theo quy tắc nào?",
    "Phải cho xe đi trong một làn đường và chỉ được chuyển làn ở nơi cho phép; mỗi lần chỉ được chuyển sang một làn liền kề; "
    "khi chuyển làn phải có tín hiệu báo trước và quan sát bảo đảm khoảng cách an toàn với xe phía trước, phía sau (khoản 2 "
    "Điều 13 " + LUAT + ").", l("d13:k2"))
add("quy_tac", "Trên đường có vạch phân làn, xe máy phải đi làn nào?",
    "Trên một chiều đường có vạch kẻ phân làn, xe thô sơ phải đi trên làn đường bên phải trong cùng; xe cơ giới, xe máy chuyên "
    "dùng đi trên làn đường bên trái (khoản 3 Điều 13 " + LUAT + "). Phương tiện có tốc độ thấp hơn phải đi về bên phải theo "
    "chiều đi của mình (khoản 1 Điều 13).", l("d13:k3"), l("d13:k1"))
add("quy_tac", "Có được đi vào làn đường dành riêng cho xe buýt không?",
    "Không. Trên làn đường dành riêng cho một loại hoặc một nhóm loại phương tiện, người điều khiển loại phương tiện khác không "
    "được đi vào làn đường đó (khoản 4 Điều 13 " + LUAT + ").", l("d13:k4"))
add("quy_tac", "Khi vượt xe phải vượt bên nào?",
    "Phải vượt bên trái. Chỉ được vượt bên phải khi xe phía trước có tín hiệu rẽ trái hoặc đang rẽ trái, hoặc khi xe chuyên "
    "dùng đang làm việc trên đường mà không thể vượt bên trái (khoản 2 Điều 14 " + LUAT + ").", l("d14:k2"))
add("quy_tac", "Những nơi nào không được vượt xe?",
    "Theo khoản 6 Điều 14 " + LUAT + ", không được vượt khi không bảo đảm điều kiện an toàn; trên cầu hẹp có một làn đường; "
    "đường cong tầm nhìn hạn chế; đỉnh dốc tầm nhìn hạn chế trên đường hai chiều; nơi đường giao nhau, đường bộ giao nhau cùng "
    "mức với đường sắt; thời tiết hoặc đường không an toàn; khi gặp xe ưu tiên; ở phần đường dành cho người đi bộ qua đường; "
    "khi có người đi bộ, xe lăn qua đường; trong hầm đường bộ.",
    l("d14:k6"), l("d14:k6:b"), l("d14:k6:đ"), l("d14:k6:k"))
add("tinh_huong", "Xe phía sau bấm còi xin vượt. Tôi đang lái phía trước thì phải làm gì?",
    "Bạn phải quan sát phía trước, nếu đủ điều kiện an toàn thì giảm tốc độ, có tín hiệu rẽ phải để báo cho xe sau biết được "
    "vượt và đi sát về bên phải của phần đường xe chạy cho đến khi xe sau vượt qua; không được cản trở xe xin vượt (khoản 4 "
    "Điều 14 " + LUAT + ").", l("d14:k4"))
add("quy_tac", "Xe xin vượt chỉ được vượt khi nào?",
    "Xe xin vượt chỉ được vượt khi không có chướng ngại vật phía trước, không có xe chạy ngược chiều trong đoạn đường định "
    "vượt, xe chạy trước không có tín hiệu vượt xe khác và đã có tín hiệu rẽ phải, tránh về bên phải (khoản 3 Điều 14 " + LUAT
    + ").", l("d14:k3"))

# ===== Chuyển hướng, lùi, tránh xe (Điều 15–17)
add("quy_tac", "Trước khi rẽ trái, rẽ phải hoặc quay đầu phải làm gì?",
    "Phải quan sát, bảo đảm khoảng cách an toàn với xe phía sau, giảm tốc độ và có tín hiệu báo hướng rẽ (xe thô sơ không có "
    "đèn thì ra tín hiệu bằng tay), chuyển dần sang làn gần nhất với hướng rẽ; tín hiệu phải dùng liên tục trong quá trình "
    "chuyển hướng (khoản 2 Điều 15 " + LUAT + ").", l("d15:k2"), l("d15:k1"))
add("quy_tac", "Khi rẽ thì phải nhường đường cho ai?",
    "Khi chuyển hướng, người lái xe phải nhường đường cho người đi bộ, xe thô sơ, xe đi ngược chiều và chỉ chuyển hướng khi "
    "không gây trở ngại hoặc nguy hiểm cho người, phương tiện khác (khoản 3 Điều 15 " + LUAT + ").", l("d15:k3"))
add("doi_thuong", "quay đầu xe trên cầu có được ko",
    "Không được. Không được quay đầu xe trên cầu, đầu cầu, gầm cầu vượt, ngầm, ở phần đường dành cho người đi bộ qua đường, "
    "nơi giao nhau với đường sắt, đường hẹp, đường dốc, đoạn cong khuất tầm nhìn, trên đường cao tốc, trong hầm, trên đường một "
    "chiều, trừ khi có hiệu lệnh của người điều khiển giao thông hoặc biển báo tạm thời (khoản 4 Điều 15 " + LUAT + ").",
    l("d15:k4"))
add("quy_tac", "Những nơi nào không được lùi xe?",
    "Không được lùi xe ở đường một chiều, khu vực cấm dừng, trên phần đường dành cho người đi bộ qua đường, nơi đường bộ giao "
    "nhau, nơi giao nhau cùng mức với đường sắt, nơi tầm nhìn bị che khuất, trong hầm đường bộ, trên đường cao tốc (khoản 2 "
    "Điều 16 " + LUAT + "). Khi lùi phải quan sát hai bên và phía sau, có tín hiệu lùi (khoản 1 Điều 16).",
    l("d16:k2"), l("d16:k1"))
add("tinh_huong", "Hai xe gặp nhau ở đoạn đèo, một xe lên dốc một xe xuống dốc. Xe nào phải nhường?",
    "Xe xuống dốc phải nhường đường cho xe lên dốc (điểm b khoản 2 Điều 17 " + LUAT + "). Ngoài ra, ở đường hẹp chỉ đủ một "
    "xe và có chỗ tránh thì xe nào gần chỗ tránh hơn phải vào tránh; xe có chướng ngại vật phía trước phải nhường xe không có "
    "chướng ngại vật (điểm a, điểm c khoản 2 Điều 17).", l("d17:k2:b"), l("d17:k2:a"), l("d17:k2:c"))

# ===== Dừng, đỗ, mở cửa (Điều 18, 19)
add("quy_tac", "Dừng xe và đỗ xe khác nhau thế nào?",
    "Dừng xe là trạng thái đứng yên tạm thời trong khoảng thời gian cần thiết để người lên, xuống, xếp dỡ hàng, kiểm tra kỹ "
    "thuật…; khi dừng không được tắt máy, không được rời vị trí lái (trừ một số trường hợp và phải dùng phanh đỗ). Đỗ xe là "
    "trạng thái đứng yên không giới hạn thời gian; chỉ được rời xe khi đã dùng phanh đỗ hoặc biện pháp an toàn khác (khoản 1, "
    "khoản 2 Điều 18 " + LUAT + ").", l("d18:k1"), l("d18:k2"))
add("quy_tac", "Những vị trí nào không được dừng, đỗ xe?",
    "Theo khoản 4 Điều 18 " + LUAT + ", không được dừng, đỗ: bên trái đường một chiều; đoạn cong hoặc gần đầu dốc khuất tầm "
    "nhìn; trên cầu (trừ khi tổ chức giao thông cho phép); gầm cầu vượt; song song cùng chiều với xe đang dừng, đỗ; phần đường "
    "người đi bộ qua đường; nơi đường giao nhau và trong phạm vi 05 mét từ mép đường giao nhau; điểm đón, trả khách; trước "
    "cổng và trong phạm vi 05 mét hai bên cổng cơ quan có lối xe ra vào; nơi đường chỉ đủ một làn xe cơ giới; che khuất biển "
    "báo, đèn tín hiệu; trên đường dành riêng cho xe buýt, miệng cống, chỗ xe chữa cháy lấy nước…",
    l("d18:k4"), l("d18:k4:h"), l("d18:k4:k"), l("d18:k4:o"))
add("tinh_huong", "Tôi đỗ ô tô sát ngã tư, cách mép đường giao nhau khoảng 3 mét. Như vậy có đúng không?",
    "Không đúng. Không được dừng, đỗ xe nơi đường giao nhau và trong phạm vi 05 mét tính từ mép đường giao nhau (điểm h khoản "
    "4 Điều 18 " + LUAT + ").", l("d18:k4:h"), l("d18:k4"))
add("quy_tac", "Đỗ xe trên đường phố phải cách lề bao nhiêu?",
    "Trên đường phố chỉ được dừng, đỗ xe sát theo lề đường, vỉa hè phía bên phải theo chiều đi; bánh xe gần nhất không được "
    "cách xa lề đường, vỉa hè quá 0,25 mét và không gây cản trở, nguy hiểm cho người và phương tiện khác (khoản 6 Điều 18 "
    + LUAT + ").", l("d18:k6"))
add("quy_tac", "Đỗ xe trên đường dốc phải làm gì?",
    "Xe đỗ trên đoạn đường dốc phải đánh lái về phía lề đường và chèn bánh (khoản 2 Điều 18 " + LUAT + ").", l("d18:k2"))
add("tinh_huong", "Xe tôi bị hỏng giữa đường, buộc phải đỗ chiếm một phần đường. Tôi phải làm gì?",
    "Khi gặp sự cố kỹ thuật hoặc bất khả kháng buộc phải đỗ chiếm một phần đường xe chạy hoặc tại nơi không được phép đỗ, phải "
    "có báo hiệu bằng đèn khẩn cấp hoặc đặt biển cảnh báo về phía sau xe để người khác biết (khoản 7 Điều 18 " + LUAT + ").",
    l("d18:k7"))
add("quy_tac", "Đỗ ô tô đối diện xe khác đang đỗ ngược chiều thì phải cách bao xa?",
    "Không được dừng, đỗ cách xe ô tô đang đỗ ngược chiều dưới 20 mét trên đường phố hẹp, dưới 40 mét trên đường có một làn xe "
    "cơ giới trên một chiều đường (điểm e khoản 4 Điều 18 " + LUAT + ").", l("d18:k4:e"), l("d18:k4"))
add("doi_thuong", "mở cửa ô tô thế nào cho đúng luật",
    "Chỉ được mở cửa xe khi xe đã dừng, đỗ. Trước khi mở cửa, người mở phải quan sát phía trước, phía sau và bên phía mở cửa, "
    "thấy an toàn mới mở cửa, ra khỏi xe; không để cửa xe mở nếu không bảo đảm an toàn (Điều 19 " + LUAT + ").",
    l("d19:k1"), l("d19:k2"))

# ===== Đèn, còi, nhường đường (Điều 20–22)
add("quy_tac", "Khi nào phải bật đèn chiếu sáng khi lái xe?",
    "Phải bật đèn chiếu sáng phía trước trong thời gian từ 18 giờ ngày hôm trước đến 06 giờ ngày hôm sau, hoặc khi có sương "
    "mù, khói, bụi, trời mưa, thời tiết xấu làm hạn chế tầm nhìn (khoản 1 Điều 20 " + LUAT + ").", l("d20:k1"))
add("quy_tac", "Khi nào phải chuyển từ đèn pha (chiếu xa) sang đèn cos (chiếu gần)?",
    "Phải tắt đèn chiếu xa, bật đèn chiếu gần khi: gặp người đi bộ qua đường; đi trên đoạn đường qua khu đông dân cư có hệ "
    "thống chiếu sáng đang hoạt động; gặp xe đi ngược chiều (trừ khi dải phân cách có khả năng chống chói); chuyển hướng tại "
    "nơi đường giao nhau (khoản 2 Điều 20 " + LUAT + ").", l("d20:k2"), l("d20:k2:c"))
add("doi_thuong", "bấm còi lúc nửa đêm trong khu dân cư có bị cấm ko",
    "Có. Không được sử dụng còi trong thời gian từ 22 giờ ngày hôm trước đến 05 giờ ngày hôm sau trong khu đông dân cư, khu vực "
    "cơ sở khám bệnh, chữa bệnh, trừ xe ưu tiên; cũng không được bấm còi liên tục hoặc dùng còi có âm lượng không đúng quy định "
    "(khoản 2 Điều 21 " + LUAT + ").", l("d21:k2"))
add("quy_tac", "Chỉ được bấm còi trong những trường hợp nào?",
    "Chỉ được sử dụng còi để báo hiệu cho người tham gia giao thông khi xuất hiện tình huống có thể mất an toàn, hoặc báo hiệu "
    "chuẩn bị vượt xe (khoản 1 Điều 21 " + LUAT + ").", l("d21:k1"), l("d21:k1:a"), l("d21:k1:b"))
add("quy_tac", "Đến ngã tư không có đèn, không có vòng xuyến thì nhường xe nào?",
    "Tại nơi đường giao nhau không có báo hiệu đi theo vòng xuyến, phải nhường đường cho xe đi đến từ bên phải (khoản 2 Điều 22 "
    + LUAT + ").", l("d22:k2"), l("d22"))
add("doi_thuong", "vào vòng xuyến nhường bên trái hay bên phải",
    "Tại nơi đường giao nhau có báo hiệu đi theo vòng xuyến, phải nhường đường cho xe đi đến từ bên trái (khoản 3 Điều 22 "
    + LUAT + ").", l("d22:k3"), l("d22"))
add("tinh_huong", "Tôi đi từ đường nhỏ ra đường chính. Tôi có phải nhường xe đang chạy trên đường chính không?",
    "Có. Xe đi từ đường không ưu tiên hoặc đường nhánh phải nhường đường cho xe đi trên đường ưu tiên hoặc đường chính từ bất "
    "kỳ hướng nào tới (khoản 1 Điều 22 " + LUAT + ").", l("d22:k1"), l("d22"))

# ===== Cao tốc, hầm (Điều 25, 26)
add("quy_tac", "Những xe nào không được đi vào đường cao tốc?",
    "Xe mô tô, xe gắn máy và xe tương tự, xe chở người, chở hàng bốn bánh có gắn động cơ, xe máy chuyên dùng có tốc độ thiết "
    "kế nhỏ hơn tốc độ tối thiểu của cao tốc, xe thô sơ và người đi bộ không được đi trên đường cao tốc, trừ người, phương tiện "
    "phục vụ quản lý, bảo trì cao tốc (khoản 3 Điều 25 " + LUAT + ").", l("d25:k3"))
add("quy_tac", "Nhập làn vào đường cao tốc phải làm thế nào?",
    "Trước khi nhập vào làn đường cao tốc phải có tín hiệu xin vào, nhường đường cho xe đang chạy, quan sát xe phía sau bảo đảm "
    "khoảng cách an toàn rồi mới nhập vào làn sát bên phải; nếu có làn tăng tốc thì phải chạy trên làn đó trước khi nhập vào "
    "(điểm a khoản 1 Điều 25 " + LUAT + ").", l("d25:k1:a"), l("d25:k1"))
add("quy_tac", "Có được chạy trên làn dừng khẩn cấp của cao tốc không?",
    "Không. Không được cho xe chạy ở làn dừng xe khẩn cấp và phần lề đường của đường cao tốc (điểm c khoản 1 Điều 25 " + LUAT
    + ").", l("d25:k1:c"), l("d25:k1"))
add("tinh_huong", "Xe tôi chết máy trên cao tốc, không vào được làn khẩn cấp. Tôi phải làm gì?",
    "Phải bật đèn khẩn cấp và đặt biển hoặc đèn cảnh báo về phía sau xe khoảng cách tối thiểu 150 mét, nhanh chóng báo cho cơ "
    "quan có trách nhiệm. Nếu di chuyển được thì phải đỗ ở làn dừng khẩn cấp cùng chiều và bật đèn khẩn cấp (khoản 2 Điều 25 "
    + LUAT + ").", l("d25:k2"))
add("quy_tac", "Đi trong hầm đường bộ phải tuân thủ những gì?",
    "Xe cơ giới, xe máy chuyên dùng phải bật đèn chiếu gần (xe thô sơ phải bật đèn hoặc có vật phát sáng); không dừng, đỗ xe "
    "trong hầm, nếu gặp sự cố phải đưa xe vào vị trí dừng khẩn cấp, không di chuyển được thì bật đèn khẩn cấp, đặt biển cảnh "
    "báo phía sau và báo Cảnh sát giao thông (khoản 1, khoản 2 Điều 26 " + LUAT + ").", l("d26:k1"), l("d26:k2"))

# ===== Người đi bộ (Điều 30)
add("quy_tac", "Người đi bộ được qua đường ở đâu?",
    "Người đi bộ chỉ được qua đường ở nơi có đèn tín hiệu, vạch kẻ đường hoặc cầu vượt, hầm dành cho người đi bộ và phải tuân "
    "thủ tín hiệu, báo hiệu; nơi không có các công trình đó thì phải quan sát xe tới, chỉ qua đường khi bảo đảm an toàn và phải "
    "có tín hiệu bằng tay (điểm b khoản 1 Điều 30 " + LUAT + ").", l("d30:k1:b"), l("d30:k1"))
add("quy_tac", "Trẻ em mấy tuổi khi qua đường phải có người lớn dẫn?",
    "Trẻ em dưới 07 tuổi khi đi qua đường phải có người lớn dẫn dắt (điểm a khoản 2 Điều 30 " + LUAT + ").",
    l("d30:k2:a"), l("d30:k2"))
add("quy_tac", "Người đi bộ có được trèo qua dải phân cách không?",
    "Không. Người đi bộ không được vượt qua dải phân cách, không được đu, bám vào phương tiện đang di chuyển (điểm c khoản 1 "
    "Điều 30 " + LUAT + ").", l("d30:k1:c"), l("d30:k1"))
add("quy_tac", "Đường không có vỉa hè thì người đi bộ phải đi ở đâu?",
    "Người đi bộ phải đi trên vỉa hè, lề đường, đường dành riêng cho người đi bộ; nếu không có thì phải đi sát mép đường bên phải "
    "theo chiều đi của mình (điểm a khoản 1 Điều 30 " + LUAT + ").", l("d30:k1:a"), l("d30:k1"))

# ===== Xe mô tô, xe gắn máy (Điều 33)
add("quy_tac", "Xe máy được chở mấy người?",
    "Người lái xe mô tô hai bánh, xe gắn máy chỉ được chở một người; được chở tối đa hai người khi chở người bệnh đi cấp cứu, áp "
    "giải người vi phạm pháp luật, trẻ em dưới 12 tuổi, hoặc người già yếu, người khuyết tật (khoản 1 Điều 33 " + LUAT + ").",
    l("d33:k1"), l("d33:k1:c"))
add("tinh_huong", "Tôi chở vợ và đứa con 10 tuổi trên xe máy. Như vậy có đúng luật không?",
    "Đúng luật. Người lái xe mô tô hai bánh, xe gắn máy được chở tối đa hai người nếu người được chở là trẻ em dưới 12 tuổi "
    "(điểm c khoản 1 Điều 33 " + LUAT + "). Tất cả người trên xe đều phải đội mũ bảo hiểm cài quai đúng quy cách (khoản 2 Điều "
    "33).", l("d33:k1:c"), l("d33:k2"))
add("quy_tac", "Người ngồi sau xe máy có phải đội mũ bảo hiểm không?",
    "Có. Người lái xe và người được chở trên xe mô tô hai bánh, xe mô tô ba bánh, xe gắn máy phải đội mũ bảo hiểm theo đúng quy "
    "chuẩn kỹ thuật quốc gia và cài quai đúng quy cách (khoản 2 Điều 33 " + LUAT + ").", l("d33:k2"))
add("doi_thuong", "đi xe máy vừa đi vừa che ô có bị cấm ko",
    "Có. Người lái xe mô tô, xe gắn máy không được sử dụng ô (điểm c khoản 3 Điều 33 " + LUAT + "); người ngồi sau cũng không "
    "được sử dụng ô (điểm b khoản 4 Điều 33).", l("d33:k3:c"), l("d33:k4:b"))
add("doi_thuong", "đi xe máy đeo tai nghe nghe nhạc có sao ko",
    "Không được. Người lái xe mô tô, xe gắn máy không được sử dụng thiết bị âm thanh, trừ thiết bị trợ thính (điểm c khoản 3 "
    "Điều 33 " + LUAT + ").", l("d33:k3:c"), l("d33:k3"))
add("quy_tac", "Người lái xe máy bị cấm những hành vi nào?",
    "Theo khoản 3 Điều 33 " + LUAT + ": đi xe dàn hàng ngang; đi vào phần đường dành cho người đi bộ và phương tiện khác; sử "
    "dụng ô, thiết bị âm thanh (trừ thiết bị trợ thính); buông cả hai tay, đi xe bằng một bánh; ngồi về một bên, đứng, nằm trên "
    "xe điều khiển, thay người lái khi xe đang chạy; kéo, đẩy xe khác, dẫn dắt vật nuôi, chở vật cồng kềnh, chở người đứng trên "
    "xe, ngồi trên tay lái; xếp hàng quá giới hạn…", l("d33:k3"), l("d33:k3:a"), l("d33:k3:d"), l("d33:k3:đ"))
add("tinh_huong", "Xe máy của bạn tôi hết xăng, tôi dùng chân đẩy xe bạn đi cùng. Có vi phạm không?",
    "Có. Người lái xe mô tô, xe gắn máy không được sử dụng xe để kéo, đẩy xe khác, vật khác (điểm đ khoản 3 Điều 33 " + LUAT
    + "); người ngồi sau cũng không được bám, kéo hoặc đẩy phương tiện khác (điểm c khoản 4 Điều 33).",
    l("d33:k3:đ"), l("d33:k4:c"))
add("quy_tac", "Chở hàng trên xe máy được phép vượt ra ngoài bao nhiêu?",
    "Hàng hóa trên xe mô tô, xe gắn máy không được vượt quá chiều rộng giá đèo hàng về mỗi bên 0,3 mét, không vượt quá phía sau "
    "giá đèo hàng 0,5 mét theo thiết kế của nhà sản xuất; chiều cao xếp hàng tính từ mặt đường không vượt quá 02 mét (khoản 5 "
    "Điều 33 " + LUAT + ").", l("d33:k5"))
add("quy_tac", "Người ngồi sau xe máy không được làm những gì?",
    "Người được chở trên xe mô tô, xe gắn máy không được mang, vác vật cồng kềnh; sử dụng ô; bám, kéo hoặc đẩy phương tiện khác; "
    "đứng trên yên, giá đèo hàng hoặc ngồi trên tay lái; và các hành vi khác gây mất trật tự, an toàn giao thông (khoản 4 Điều "
    "33 " + LUAT + ").", l("d33:k4"), l("d33:k4:a"), l("d33:k4:d"))

# ===== Niên hạn (Điều 40)
add("quy_tac", "Ô tô con 5 chỗ có bị giới hạn niên hạn sử dụng không?",
    "Không. Xe mô tô, xe gắn máy, xe ô tô chở người có số người cho phép chở đến 08 người (không kể người lái xe), xe ô tô "
    "chuyên dùng, rơ moóc, sơ mi rơ moóc không áp dụng niên hạn sử dụng (điểm a khoản 3 Điều 40 " + LUAT + ").",
    l("d40:k3:a"), l("d40:k3"))
add("quy_tac", "Niên hạn sử dụng của xe cơ giới được tính từ khi nào?",
    "Niên hạn sử dụng được tính bắt đầu từ năm sản xuất xe đến hết ngày 31 tháng 12 của năm hết niên hạn sử dụng (khoản 1 Điều "
    "40 " + LUAT + ").", l("d40:k1"))
add("quy_tac", "Xe khách cải tạo thành xe tải thì tính niên hạn theo loại nào?",
    "Xe ô tô chở người có số người cho phép chở từ 09 người trở lên (không kể người lái), xe chở người chuyên dùng cải tạo thành "
    "xe ô tô chở hàng thì áp dụng niên hạn của xe sau cải tạo (điểm c khoản 2 Điều 40 " + LUAT + ").",
    l("d40:k2:c"), l("d40:k2"))

out = ROOT / "data/train/drafts/luat_loi_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
