"""Đợt 10a G5: Hướng dẫn. NĐ 158/2024 (vận tải đường bộ: taxi, xe hợp đồng, an toàn, phù hiệu) và NĐ 165/2024 (hành lang
an toàn, sử dụng tạm thời lòng đường, vỉa hè). Ghi data/train/drafts/huong_dan_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND158 = "Nghị định 158/2024/NĐ-CP"
ND165 = "Nghị định 165/2024/NĐ-CP"
S = []
START = 1
A8 = "2026-08-10"
J7 = "2026-07-01"


def a(s, d="2025-01-01"):
    return f"nd_158_2024:{s}@{d}"


def b(s, d="2025-01-01"):
    return f"nd_165_2024:{s}@{d}"


def add(loai, q, ans, *can_cu):
    S.append({"key": f"hd-{START + len(S):04d}", "chu_de": "Hướng dẫn", "loai": loai, "cau_hoi": q, "dap_an": ans,
              "can_cu": list(can_cu)})


# ===== Taxi (NĐ 158 Điều 6)
add("quy_tac", "Xe taxi phải dán những gì trên kính xe?",
    "Xe taxi phải có phù hiệu \"XE TAXI\" dán cố định ở góc trên bên phải, ngay sát phía dưới tem kiểm định, mặt trong kính chắn "
    "gió phía trước; và niêm yết cụm từ \"XE TAXI\" bằng vật liệu phản quang trên kính trước và kính sau với kích thước tối thiểu "
    "06 x 20 cm (điểm b, điểm c khoản 2 Điều 6 " + ND158 + ").", a("d6:k2:b"), a("d6:k2:c"))
add("quy_tac", "Taxi tính tiền bằng đồng hồ thì phải đáp ứng yêu cầu gì?",
    "Trên xe phải gắn đồng hồ tính tiền được cơ quan đo lường kiểm định và kẹp chì, có thiết bị in hóa đơn hoặc phiếu thu tiền kết "
    "nối với đồng hồ; đồng hồ và thiết bị in gắn cố định ở vị trí hành khách dễ quan sát; lái xe phải lập hóa đơn điện tử gửi "
    "hành khách khi kết thúc hành trình (điểm a khoản 3 Điều 6 " + ND158 + ").", a("d6:k3:a"), a("d6:k3"))
add("doi_thuong", "đi taxi xong có được đòi hóa đơn ko",
    "Có. Với taxi dùng đồng hồ, lái xe phải lập hóa đơn điện tử gửi cho hành khách khi kết thúc hành trình (điểm a khoản 3 Điều 6 "
    + ND158 + "); với taxi dùng phần mềm tính tiền, đơn vị kinh doanh phải gửi hóa đơn điện tử của chuyến đi cho hành khách qua "
    "phần mềm (khoản 6 Điều 6).", a("d6:k3:a"), a("d6:k6"))
add("quy_tac", "Phiếu thu tiền taxi phải có những thông tin gì?",
    "Phiếu thu tiền phải có tối thiểu: tên đơn vị kinh doanh vận tải, biển kiểm soát xe, cự ly chuyến đi (km) và tổng số tiền "
    "hành khách phải trả (điểm b khoản 3 Điều 6 " + ND158 + ").", a("d6:k3:b"))
add("quy_tac", "Taxi đặt qua ứng dụng thì tiền cước được tính thế nào?",
    "Với taxi dùng phần mềm tính tiền, tiền cước được tính theo quãng đường xác định trên bản đồ số; trên xe phải có thiết bị kết "
    "nối trực tiếp với hành khách để đặt xe, hủy chuyến; trước khi chở, phần mềm phải cung cấp cho khách tên đơn vị, họ tên lái "
    "xe, biển kiểm soát, hành trình, cự ly và tổng số tiền phải trả (khoản 4 Điều 6 " + ND158 + ").",
    a("d6:k4:a"), a("d6:k4:b"), a("d6:k4:c"))
add("quy_tac", "Taxi có được ưu tiên chỗ đón trả khách ở sân bay, bến xe không?",
    "Có. Xe taxi được ưu tiên bố trí nơi dừng, đỗ để đón, trả khách tại bến xe, nhà ga, sân bay, bến cảng, khu du lịch, cơ sở lưu "
    "trú, trung tâm thương mại…; và được ưu tiên hoạt động khi tổ chức giao thông tại đô thị (khoản 8 Điều 6 " + ND158 + ").",
    a("d6:k8"))
add("quy_tac", "Đơn vị nào được kinh doanh vận tải bằng taxi?",
    "Đơn vị kinh doanh vận tải có Giấy phép kinh doanh vận tải bằng ô tô, trong đó có loại hình kinh doanh vận tải hành khách bằng "
    "taxi, thì được tham gia kinh doanh vận tải hành khách bằng taxi (khoản 1 Điều 6 " + ND158 + ").", a("d6:k1"))

# ===== Xe hợp đồng (NĐ 158 Điều 7)
add("quy_tac", "Xe hợp đồng phải dán phù hiệu, ký hiệu gì?",
    "Xe ô tô kinh doanh vận tải hành khách theo hợp đồng phải có phù hiệu \"XE HỢP ĐỒNG\" dán ở góc trên bên phải, sát dưới tem "
    "kiểm định, mặt trong kính chắn gió phía trước; và niêm yết cụm từ \"XE HỢP ĐỒNG\" bằng vật liệu phản quang trên kính trước và "
    "kính sau với kích thước tối thiểu 06 x 20 cm (điểm b, điểm c khoản 2 Điều 7 " + ND158 + ").", a("d7:k2:b"), a("d7:k2:c"))
add("quy_tac", "Nhà xe chạy hợp đồng có được bán vé lẻ cho từng khách không?",
    "Không. Theo điểm a khoản 4 Điều 7 " + ND158 + " (nội dung có hiệu lực từ ngày 10/8/2026), đơn vị kinh doanh vận tải hành khách "
    "theo hợp đồng không được xác nhận đặt chỗ cho từng hành khách, không được bán vé, không được thu tiền, không được ấn định hành "
    "trình, lịch trình cố định để phục vụ nhiều hành khách hoặc nhiều người thuê vận tải khác nhau.", a("d7:k4:a", A8), a("d7:k4"))
add("quy_tac", "Lái xe hợp đồng có được đón thêm khách dọc đường không?",
    "Không. Lái xe chỉ được đón, trả khách theo đúng địa điểm trong hợp đồng vận tải đã ký; không được gom khách, đón khách ngoài "
    "danh sách đính kèm hợp đồng (điểm b khoản 4 Điều 7 " + ND158 + "). Ngoài cấp cứu người hoặc nhiệm vụ khẩn cấp theo yêu cầu lực "
    "lượng chức năng, xe hợp đồng không được đón, trả khách ngoài các địa điểm ghi trong hợp đồng (khoản 9 Điều 7).",
    a("d7:k4:b"), a("d7:k9"))
add("thu_tuc", "Lái xe hợp đồng chở khách phải mang theo giấy tờ gì?",
    "Ngoài giấy tờ người lái phải mang theo theo Luật Trật tự, an toàn giao thông đường bộ, lái xe hợp đồng phải mang theo hợp đồng "
    "vận tải bằng văn bản giấy và danh sách hành khách có xác nhận của đơn vị; nếu dùng hợp đồng điện tử thì phải có thiết bị truy "
    "cập được nội dung hợp đồng và danh sách hành khách (khoản 5 Điều 7 " + ND158 + ").",
    a("d7:k5"), a("d7:k5:a"), a("d7:k5:b"), a("d7:k5:c"))
add("tinh_huong", "Tôi thuê xe hợp đồng chở đoàn đi đám cưới. Lái xe có cần mang danh sách khách không?",
    "Không bắt buộc. Lái xe không phải mang theo hợp đồng giấy, danh sách hành khách hoặc thiết bị truy cập hợp đồng điện tử trong "
    "trường hợp thực hiện hợp đồng vận tải phục vụ đám tang, đám cưới (điểm d khoản 5 Điều 7 " + ND158 + ").", a("d7:k5:d"),
    a("d7:k5"))
add("quy_tac", "Nhà xe hợp đồng phải lưu hợp đồng và danh sách khách trong bao lâu?",
    "Đơn vị kinh doanh vận tải hành khách theo hợp đồng lưu trữ hợp đồng vận chuyển kèm danh sách hành khách tối thiểu 03 năm "
    "(khoản 6 Điều 7 " + ND158 + ").", a("d7:k6"))
add("quy_tac", "Hợp đồng vận tải hành khách phải có những nội dung tối thiểu nào?",
    "Theo khoản 2 Điều 17 " + ND158 + ": thông tin đơn vị kinh doanh vận tải; thông tin hành khách hoặc người thuê vận tải; thời "
    "gian bắt đầu, kết thúc, điểm đầu, điểm cuối, các điểm đón trả, cự ly, số lượng khách; giá trị hợp đồng và phương thức thanh "
    "toán; trách nhiệm các bên, số điện thoại tiếp nhận phản ánh, cam kết đền bù thiệt hại cho hành khách.",
    a("d17:k2"), a("d17:k2:a"), a("d17:k2:c"), a("d17:k2:đ"))

# ===== An toàn vận tải (NĐ 158 Điều 11)
add("quy_tac", "Lái taxi, xe khách chạy liên tục thì phải nghỉ tối thiểu bao lâu giữa hai lần lái?",
    "Thời gian nghỉ giữa 2 lần lái xe liên tục: lái xe ô tô taxi, xe buýt nội tỉnh tối thiểu 05 phút; lái xe khách tuyến cố định, "
    "xe buýt liên tỉnh, xe hợp đồng, xe tải tối thiểu 15 phút (khoản 13 Điều 11 " + ND158 + ").",
    a("d11:k13:a"), a("d11:k13:b"))
add("quy_tac", "Xe khách giường nằm hai tầng có được chạy đường đèo miền núi không?",
    "Không được sử dụng xe ô tô khách giường nằm hai tầng để hoạt động trên các tuyến đường cấp V và cấp VI miền núi (điểm b khoản "
    "12 Điều 11 " + ND158 + ").", a("d11:k12:b"), a("d11:k12"))
add("quy_tac", "Lái xe khách giường nằm hai tầng cần kinh nghiệm thế nào?",
    "Đơn vị kinh doanh vận tải phải sử dụng lái xe có ít nhất 02 năm kinh nghiệm điều khiển xe ô tô khách có trọng tải thiết kế trên "
    "29 chỗ (không kể chỗ người lái) để điều khiển xe ô tô khách giường nằm hai tầng (điểm c khoản 12 Điều 11 " + ND158 + ").",
    a("d11:k12:c"), a("d11:k12"))
add("quy_tac", "Trước khi xe khởi hành, nhà xe phải kiểm tra những gì đối với lái xe?",
    "Bộ phận quản lý an toàn hoặc người điều hành phải kiểm tra giấy phép lái xe, giấy chứng nhận kiểm định, giấy đăng ký xe, lệnh "
    "vận chuyển hoặc hợp đồng vận tải hoặc giấy vận tải; thông báo yêu cầu vận chuyển cho lái xe; và kiểm tra nồng độ cồn, chất ma "
    "túy đối với lái xe nếu đơn vị có thiết bị (khoản 4 Điều 11 " + ND158 + ").", a("d11:k4"), a("d11:k4:a"), a("d11:k4:c"))
add("quy_tac", "Kết thúc chuyến, lái xe khách phải làm gì trước khi rời xe?",
    "Lái xe phải dùng thẻ nhận dạng của mình để đăng xuất qua đầu đọc thẻ của thiết bị giám sát hành trình, và trước khi rời xe phải "
    "kiểm tra khoang hành khách để bảo đảm không còn hành khách trên xe (điểm b khoản 8 Điều 11 " + ND158 + ").",
    a("d11:k8:b"), a("d11:k8"))
add("quy_tac", "Xe kinh doanh vận tải hành khách phải có những trang bị an toàn gì cho khách?",
    "Phải có dây an toàn tại các vị trí ghế ngồi, giường nằm (trừ xe buýt nội tỉnh) và có hướng dẫn cho hành khách về an toàn giao "
    "thông, thoát hiểm khi xảy ra sự cố trên xe (điểm a khoản 12 Điều 11 " + ND158 + ").", a("d11:k12:a"), a("d11:k12"))
add("quy_tac", "Lái xe kinh doanh vận tải phải đáp ứng điều kiện gì?",
    "Đơn vị chỉ được sử dụng lái xe có giấy phép lái xe phù hợp loại xe theo Điều 57 Luật Trật tự, an toàn giao thông đường bộ và "
    "đã được cấp Giấy chứng nhận hoàn thành tập huấn nghiệp vụ vận tải (điểm c khoản 1 Điều 11 " + ND158 + ").",
    a("d11:k1:c"), a("d11:k1"))

# ===== Phù hiệu (NĐ 158 Điều 23)
add("quy_tac", "Phù hiệu xe kinh doanh vận tải có thời hạn bao lâu?",
    "Phù hiệu cấp cho xe kinh doanh vận tải có thời hạn theo đề nghị của đơn vị, tối thiểu 01 năm, tối đa đến 07 năm và không quá "
    "niên hạn sử dụng của phương tiện (điểm a khoản 3 Điều 23 " + ND158 + ").", a("d23:k3:a"), a("d23:k3"))
add("quy_tac", "Phù hiệu xe tăng cường dịp Tết có giá trị bao lâu?",
    "Phù hiệu \"XE TUYẾN CỐ ĐỊNH\" cấp cho xe tăng cường giải tỏa hành khách dịp Tết Nguyên đán có giá trị không quá 30 ngày; dịp "
    "Lễ, Tết dương lịch và các kỳ thi trung học phổ thông quốc gia, tuyển sinh có giá trị không quá 10 ngày (điểm b khoản 3 Điều "
    "23 " + ND158 + ").", a("d23:k3:b"), a("d23:k3"))
add("quy_tac", "Một xe có được cùng lúc gắn hai loại phù hiệu không?",
    "Không. Tại một thời điểm, mỗi xe chỉ được cấp và sử dụng một loại phù hiệu tương ứng với một loại hình kinh doanh vận tải "
    "(điểm a khoản 2 Điều 23 " + ND158 + ").", a("d23:k2:a"), a("d23:k2"))
add("quy_tac", "Xe kinh doanh vận tải chạy quá tốc độ nhiều lần có bị thu hồi phù hiệu không?",
    "Có. Phù hiệu của phương tiện bị thu hồi 01 tháng nếu dữ liệu thiết bị giám sát hành trình trong 01 tháng cho thấy có từ 05 lần "
    "vi phạm tốc độ/1000 km xe chạy (không tính các lần vi phạm từ 05 km/h trở xuống) (điểm c khoản 10 Điều 23 " + ND158 + ").",
    a("d23:k10:c"), a("d23:k10"))
add("quy_tac", "Xe tải bị cân phát hiện quá tải nhiều lần có bị thu hồi phù hiệu không?",
    "Có. Phù hiệu của phương tiện bị thu hồi 01 tháng nếu dữ liệu cân kiểm soát tải trọng tự động trong 01 tháng cho thấy có từ 03 "
    "lần vi phạm tải trọng cho phép của cầu, đường trên 10% (điểm d khoản 10 Điều 23 " + ND158 + ").",
    a("d23:k10:d"), a("d23:k10"))
add("quy_tac", "Bán xe kinh doanh vận tải cho đơn vị khác thì phù hiệu xử lý thế nào?",
    "Phù hiệu của xe kinh doanh vận tải bị thu hồi khi phương tiện đã được chuyển nhượng hoặc cho đơn vị khác thuê (điểm đ khoản 10 "
    "Điều 23 " + ND158 + "). Phù hiệu được cấp lại khi thay đổi chủ sở hữu phương tiện hoặc thay đổi đơn vị kinh doanh vận tải "
    "(khoản 7 Điều 23, nội dung có hiệu lực từ ngày 10/8/2026).", a("d23:k10:đ"), a("d23:k7", A8))
add("thu_tuc", "Cấp phù hiệu cho xe kinh doanh vận tải mất bao lâu?",
    "Theo điểm b khoản 6 Điều 23 " + ND158 + " (nội dung có hiệu lực từ ngày 10/8/2026), trong thời hạn 02 ngày làm việc kể từ khi "
    "nhận hồ sơ đúng quy định, cơ quan cấp kiểm tra dữ liệu đăng ký xe và cấp phù hiệu, cập nhật vào Cơ sở dữ liệu cấp phép hoạt "
    "động vận tải.", a("d23:k6:b", A8), a("d23:k6", A8))
add("quy_tac", "Kích thước tối thiểu của phù hiệu xe là bao nhiêu?",
    "Kích thước tối thiểu của các loại phù hiệu là 9 x 10 cm (khoản 4 Điều 23 " + ND158 + ").", a("d23:k4"))

# ===== Lòng đường, vỉa hè, hành lang an toàn (NĐ 165)
add("tinh_huong", "Nhà tôi tổ chức đám cưới, muốn dựng rạp trên lòng đường trước nhà. Có được không?",
    "Có thể, nếu được cấp phép sử dụng tạm thời lòng đường, vỉa hè: tổ chức đám cưới là một trong các mục đích được xem xét (điểm đ "
    "khoản 1 Điều 21 " + ND165 + ", nội dung có hiệu lực từ ngày 01/7/2026). Nhưng việc dùng lòng đường cho đám cưới chỉ được thực "
    "hiện trên đường xã, đường thôn, đường chuyên dùng, đường đô thị (không gồm đường phố chính đô thị); không dùng lòng đường, vỉa "
    "hè cao tốc, quốc lộ, đường tỉnh (khoản 1a Điều 21).", b("d21:k1:đ", J7), b("d21:k1a", J7))
add("thu_tuc", "Xin phép sử dụng tạm thời vỉa hè, lòng đường cần hồ sơ gì?",
    "Hồ sơ gồm 01 bộ: văn bản đề nghị cấp phép sử dụng tạm thời lòng đường, vỉa hè (Mẫu số 1 Phụ lục IV) và phương án sử dụng tạm "
    "thời, gồm mục đích, vị trí, phạm vi, chiều dài; chỉ dẫn cho người, phương tiện đi qua hoặc đi tránh; phương án hoàn trả sau khi "
    "dùng (khoản 2, khoản 3 Điều 21 " + ND165 + ", nội dung có hiệu lực từ ngày 01/7/2026).",
    b("d21:k3", J7), b("d21:k3:a", J7), b("d21:k2", J7))
add("thu_tuc", "Xin phép dùng lòng đường làm đám tang thì bao lâu có kết quả?",
    "Trong thời hạn không quá 01 ngày đối với đám tang (không quá 03 ngày làm việc với các trường hợp khác), cơ quan có thẩm quyền "
    "kiểm tra và cấp văn bản cho phép nếu đủ điều kiện (điểm c khoản 6 Điều 21 " + ND165 + ", nội dung có hiệu lực từ ngày "
    "01/7/2026). Kết quả trả bằng bản điện tử trên VNeID hoặc Cổng dịch vụ công quốc gia, hoặc bản giấy nếu có nhu cầu (điểm d "
    "khoản 6 Điều 21).", b("d21:k6:c", J7), b("d21:k6:d", J7))
add("quy_tac", "Cơ quan nào cấp phép sử dụng tạm thời lòng đường, vỉa hè?",
    "Khu Quản lý đường bộ cấp phép với đường do Bộ quản lý (trừ phần đã bàn giao cho địa phương); Sở Xây dựng với đường được Ủy ban "
    "nhân dân cấp tỉnh giao quản lý (trừ phần đã giao cấp xã); Ủy ban nhân dân cấp xã với các trường hợp còn lại (khoản 5 Điều 21 "
    + ND165 + ", nội dung có hiệu lực từ ngày 01/7/2026).", b("d21:k5", J7), b("d21:k5:c", J7))
add("quy_tac", "Sau khi dùng tạm vỉa hè xong, người được cấp phép phải làm gì?",
    "Phải trả lại nguyên trạng lòng đường, vỉa hè khi kết thúc việc sử dụng và bồi thường thiệt hại nếu làm hư hỏng kết cấu hạ tầng "
    "đường bộ; chỉ được sử dụng đúng mục đích và thời gian đã được cấp phép (điểm b, điểm đ khoản 8 Điều 21 " + ND165 + ").",
    b("d21:k8:b"), b("d21:k8:đ"))
add("quy_tac", "Hành lang an toàn của đường cao tốc rộng bao nhiêu?",
    "Với đường ngoài đô thị, chiều rộng hành lang an toàn tính từ mép ngoài phần đất bảo vệ, bảo trì đường trở ra mỗi bên: 17 mét "
    "với đường cao tốc, cấp I, cấp II; 13 mét với đường cấp III; 9,0 mét với đường cấp IV, cấp V; 4,0 mét với đường cấp VI và các "
    "đường khác (khoản 1 Điều 11 " + ND165 + ").", b("d11:k1"))
add("quy_tac", "Hành lang an toàn của cầu dài trên 300 mét ngoài đô thị là bao nhiêu?",
    "Theo điểm a khoản 2 Điều 11 " + ND165 + " (nội dung có hiệu lực từ ngày 01/7/2026), hành lang an toàn cầu ngoài đô thị tính "
    "từ mép ngoài phần đất bảo vệ cầu ra mỗi bên: 150 mét với cầu dài hơn 300 mét; 100 mét với cầu dài từ 60 mét đến 300 mét; 50 "
    "mét với cầu dài từ 20 mét đến dưới 60 mét; 20 mét với cầu dài dưới 20 mét.", b("d11:k2:a", J7), b("d11:k2"))

out = ROOT / "data/train/drafts/huong_dan_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
