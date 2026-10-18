"""Đợt C6 G5: vận tải theo NĐ 158/2024 ở các Điều chưa có mẫu: tuyến cố định, xe buýt, vận tải hàng hóa, xe bốn bánh có
gắn động cơ, tập huấn nghiệp vụ, điều kiện và niên hạn xe, hợp đồng điện tử, vận tải nội bộ, liên vận.
Ghi data/train/drafts/huong_dan_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 158/2024/NĐ-CP"
S = []
START = 48
M10 = "2026-08-10"


def n(s, d="2025-01-01"):
    return f"nd_158_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"hd-{START + len(S):04d}", "chu_de": "Hướng dẫn", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Tuyến cố định (Điều 4)
add("quy_tac", "Xe khách chạy tuyến cố định phải xuất phát và kết thúc ở đâu?",
    "Tuyến cố định phải xuất phát và kết thúc tại bến xe khách đã được công bố đưa vào khai thác (khoản 2 Điều 4 " + ND + ").",
    n("d4:k2"))
add("quy_tac", "Xe khách tuyến cố định phải đáp ứng những yêu cầu gì trên xe?",
    "Xe phải có chỗ ưu tiên cho người khuyết tật, người cao tuổi và phụ nữ mang thai; có phù hiệu “XE TUYẾN CỐ ĐỊNH” dán cố "
    "định ở góc trên bên phải, ngay sát phía dưới tem kiểm định, mặt trong kính chắn gió phía trước; và niêm yết đầy đủ các "
    "thông tin trên xe (khoản 4 Điều 4 " + ND + ").", n("d4:k4:a"), n("d4:k4:b"), n("d4:k4:c"), n("d4:k4"))
add("quy_tac", "Xe trung chuyển hành khách của nhà xe được dùng loại xe nào và chạy trong phạm vi nào?",
    "Xe trung chuyển là xe ô tô chở người đến 29 chỗ (không kể chỗ của người lái xe), có phù hiệu “XE TRUNG CHUYỂN” và niêm "
    "yết đầy đủ thông tin; chỉ được hoạt động trung chuyển hành khách trong phạm vi địa bàn cấp tỉnh nơi cấp phù hiệu đó "
    "(khoản 5 Điều 4 " + ND + ").", n("d4:k5:a"), n("d4:k5:b"), n("d4:k5:c"), n("d4:k5"))
add("thu_tuc", "Dịp Tết nhà xe tuyến cố định muốn tăng cường thêm xe thì làm thế nào?",
    "Vào dịp Lễ, Tết và các kỳ thi trung học phổ thông quốc gia, tuyển sinh đại học, cao đẳng, đơn vị đang khai thác tuyến căn "
    "cứ nhu cầu đi lại, thống nhất với bến xe khách xây dựng hoặc điều chỉnh phương án tăng cường phương tiện, rồi gửi phương "
    "án đến Sở Xây dựng hai đầu tuyến để phối hợp, quản lý (điểm a khoản 6 Điều 4 " + ND + ").", n("d4:k6:a", M10), n("d4:k6"))
add("thu_tuc", "Cuối tuần khách tăng đột biến, nhà xe tuyến cố định tăng cường xe thế nào?",
    "Vào thứ Sáu, thứ Bảy và Chủ nhật có lượng khách tăng đột biến, đơn vị thống nhất với bến xe khách xây dựng phương án tăng "
    "cường và thông báo đến Sở Xây dựng hai đầu tuyến để thực hiện trong năm. Khi chạy, bến xe khách căn cứ phương án đã thông "
    "báo và lưu lượng khách thực tế để xác nhận chuyến tăng cường vào Lệnh vận chuyển (điểm b khoản 6 Điều 4 " + ND + ").",
    n("d4:k6:b", M10), n("d4:k6"))
add("quy_tac", "Khi xe khách xuất bến, bến xe xác nhận những gì vào lệnh vận chuyển?",
    "Đơn vị kinh doanh dịch vụ bến xe khách xác nhận vào Lệnh vận chuyển khi xe xuất bến các nội dung: biển kiểm soát xe, số "
    "lượng hành khách và giờ xe xuất bến (khoản 7 Điều 4 " + ND + ").", n("d4:k7"))
add("quy_tac", "Nhà xe tuyến cố định phải lưu lệnh vận chuyển trong bao lâu?",
    "Phải lưu trữ Lệnh vận chuyển của các chuyến xe đã thực hiện trong thời gian tối thiểu 03 năm (khoản 8 Điều 4 " + ND + ").",
    n("d4:k8"))

# ===== Xe buýt (Điều 5)
add("quy_tac", "Xe buýt phải dành chỗ ưu tiên cho những ai?",
    "Xe buýt phải có chỗ ưu tiên cho người khuyết tật, người cao tuổi, phụ nữ mang thai và trẻ em dưới 6 tuổi (điểm a khoản 2 "
    "Điều 5 " + ND + ").", n("d5:k2:a"), n("d5:k2"))
add("quy_tac", "Phù hiệu xe buýt được dán ở đâu?",
    "Xe buýt phải có phù hiệu “XE BUÝT” theo Mẫu số 03 Phụ lục XIII, dán cố định tại góc trên bên phải, ngay sát phía dưới vị "
    "trí tem kiểm định, mặt trong kính chắn gió phía trước, và phải niêm yết đầy đủ thông tin trên xe (điểm b khoản 2 Điều 5 "
    + ND + ").", n("d5:k2:b"), n("d5:k2"))
add("doi_thuong", "xe buýt có được ưu tiên chỗ đỗ đón khách ở sân bay bến xe ko",
    "Có. Xe buýt được ưu tiên bố trí nơi dừng, đỗ để đón, trả khách tại bến xe, nhà ga, sân bay, bến cảng, khu và điểm du lịch, "
    "trung tâm thương mại, đầu mối giao thông và các địa điểm kết nối với phương thức vận tải khác; được ưu tiên hoạt động khi "
    "tổ chức giao thông tại đô thị (khoản 5 Điều 5 " + ND + ").", n("d5:k5"))
add("quy_tac", "Cơ quan nào công bố giá vé và quyết định điểm dừng của tuyến xe buýt?",
    "Sở Xây dựng xây dựng, điều chỉnh và công bố danh mục mạng lưới tuyến, biểu đồ chạy xe, giá vé; đồng thời quyết định tiêu "
    "chí kỹ thuật, vị trí điểm đầu, điểm cuối và điểm dừng của tuyến xe buýt trên địa bàn (điểm a, điểm c khoản 3 Điều 5 " + ND
    + ").", n("d5:k3:a", M10), n("d5:k3:c", M10), n("d5:k3", M10))
add("quy_tac", "Nhà xe buýt không được ngân sách hỗ trợ phải lưu lệnh vận chuyển bao lâu?",
    "Lưu trữ Lệnh vận chuyển của các chuyến xe đã thực hiện (không được hỗ trợ kinh phí hoạt động từ ngân sách nhà nước) trong "
    "thời hạn ít nhất là 03 năm (điểm a khoản 4 Điều 5 " + ND + ").", n("d5:k4:a"), n("d5:k4"))

# ===== Vận tải hàng hóa (Điều 8)
add("doi_thuong", "taxi tải là xe gì vậy",
    "Kinh doanh vận tải hàng hóa bằng taxi tải là dùng xe ô tô có trọng tải từ 1.500 ki-lô-gam trở xuống để chở hàng, người "
    "thuê trả tiền cho lái xe theo đồng hồ tính tiền hoặc phần mềm tính tiền trên xe (khoản 2 Điều 8 " + ND + ").", n("d8:k2"))
add("quy_tac", "Xe taxi tải phải niêm yết những gì bên ngoài xe?",
    "Mặt ngoài hai bên thành xe hoặc cánh cửa xe phải niêm yết cụm từ “TAXI TẢI” theo Mẫu số 08 Phụ lục XIII, số điện thoại "
    "liên lạc và tên đơn vị kinh doanh vận tải (khoản 2 Điều 8 " + ND + ").", n("d8:k2"))
add("thu_tuc", "Lái xe tải kinh doanh chở hàng phải mang theo giấy vận tải không?",
    "Phải. Khi vận chuyển hàng hóa, lái xe mang theo Giấy vận tải bằng văn bản giấy hoặc có thiết bị truy cập phần mềm thể hiện "
    "nội dung Giấy vận tải, cùng giấy tờ của lái xe và phương tiện (khoản 9 Điều 8 " + ND + "). Giấy vận tải do đơn vị kinh "
    "doanh cấp, có xác nhận khối lượng hàng đã xếp lên xe của chủ hàng hoặc người xếp hàng (khoản 8 Điều 8).",
    n("d8:k9"), n("d8:k8"))
add("quy_tac", "Giấy vận tải hàng hóa phải có những thông tin gì và lưu bao lâu?",
    "Giấy vận tải (giấy hoặc điện tử) do đơn vị kinh doanh tự phát hành, tối thiểu có: tên đơn vị vận tải; biển kiểm soát xe; "
    "tên đơn vị hoặc người thuê vận tải; hành trình; số, ngày ký hợp đồng (nếu có); loại hàng và khối lượng hàng trên xe. Đơn vị "
    "phải lưu Giấy vận tải của các chuyến đã thực hiện tối thiểu 03 năm (khoản 11 Điều 8 " + ND + ").", n("d8:k11"))
add("tinh_huong", "Tôi thuê xe tải chở hàng, hàng bị vỡ một phần trên đường. Việc bồi thường tính thế nào?",
    "Việc bồi thường hàng hóa hư hỏng, mất mát, thiếu hụt được thực hiện theo hợp đồng vận chuyển hoặc theo thỏa thuận giữa "
    "người kinh doanh vận tải và người thuê vận tải (khoản 12 Điều 8 " + ND + ").", n("d8:k12"))
add("quy_tac", "Xe tải kinh doanh vận tải hàng hóa phải dán phù hiệu gì?",
    "Xe đầu kéo kéo rơ moóc, sơ mi rơ moóc, xe ô tô tải kinh doanh vận tải hàng hóa thông thường và xe taxi tải phải có phù hiệu "
    "“XE TẢI” theo Mẫu số 09 Phụ lục XIII, dán cố định tại góc trên bên phải ngay sát phía dưới tem kiểm định, mặt trong kính "
    "chắn gió phía trước (khoản 6 Điều 8 " + ND + ").", n("d8:k6"))
add("quy_tac", "Vận tải hàng siêu trường, siêu trọng là gì?",
    "Là việc dùng xe ô tô chở hàng không thể chia nhỏ, tháo rời, mà khi vận chuyển làm phương tiện hoặc tổ hợp phương tiện vượt "
    "quá giới hạn cho phép về kích thước, khối lượng; khi vận chuyển phải thực hiện theo Điều 53 Luật Trật tự, an toàn giao thông "
    "đường bộ (khoản 3 Điều 8 " + ND + ").", n("d8:k3:a"), n("d8:k3:b"), n("d8:k3"))

# ===== Xe bốn bánh có gắn động cơ (Điều 9, 10, 15)
add("quy_tac", "Kinh doanh chở khách bằng xe bốn bánh có gắn động cơ thì xe phải dán phù hiệu gì?",
    "Đơn vị có giấy phép kinh doanh loại hình vận tải bằng xe bốn bánh có gắn động cơ thì được dùng xe này chở khách (khoản 1 "
    "Điều 9 " + ND + "); xe phải có phù hiệu “XE CHỞ KHÁCH” theo Mẫu số 10 Phụ lục XIII, dán cố định phía bên phải mặt trong "
    "kính trước (khoản 4 Điều 9).", n("d9:k4"), n("d9:k1"))
add("quy_tac", "Xe bốn bánh có gắn động cơ chở khách có niên hạn sử dụng bao lâu?",
    "Xe bốn bánh có gắn động cơ kinh doanh vận tải hành khách có niên hạn sử dụng không quá 20 năm (khoản 2 Điều 15 " + ND
    + ").", n("d15:k2"))
add("quy_tac", "Đơn vị chở khách bằng xe bốn bánh có gắn động cơ phải làm gì cho an toàn của khách?",
    "Phương tiện phải đáp ứng điều kiện tham gia giao thông theo điểm d khoản 1 Điều 34 và khoản 1 Điều 48 Luật Trật tự, an toàn "
    "giao thông đường bộ, và đơn vị phải hướng dẫn hành khách bảo đảm an toàn giao thông khi ngồi trên xe (khoản 2 Điều 9 " + ND
    + ").", n("d9:k2"), "luat_36_2024:d34:k1:d@2025-01-01", "luat_36_2024:d48:k1@2025-01-01")
add("quy_tac", "Xe bốn bánh có gắn động cơ kinh doanh chở hàng phải dán phù hiệu gì?",
    "Phải có phù hiệu “XE CHỞ HÀNG” theo Mẫu số 11 Phụ lục XIII, dán cố định phía bên phải mặt trong kính trước của xe (khoản 4 "
    "Điều 10 " + ND + ").", n("d10:k4"))

# ===== Tập huấn nghiệp vụ cho lái xe kinh doanh vận tải (Điều 12)
add("thu_tuc", "Lái xe kinh doanh vận tải phải tập huấn nghiệp vụ khi nào và bao lâu một lần?",
    "Lái xe phải tập huấn trước khi tham gia hoạt động kinh doanh vận tải, và tập huấn định kỳ không quá 05 năm kể từ ngày được "
    "cấp giấy chứng nhận tập huấn (khoản 3 Điều 12 " + ND + ").", n("d12:k3:a"), n("d12:k3:b"), n("d12:k3"))
add("quy_tac", "Chương trình tập huấn nghiệp vụ cho lái xe kinh doanh vận tải tối thiểu bao nhiêu giờ?",
    "Khối lượng kiến thức tối thiểu là 04 bài (từ bài 1 đến bài 4), thời gian tập huấn tối thiểu 24 giờ (điểm a khoản 2 Điều 12 "
    + ND + ").", n("d12:k2:a"), n("d12:k2"))
add("thu_tuc", "Kiểm tra cuối khóa tập huấn nghiệp vụ vận tải diễn ra thế nào, bao nhiêu điểm thì đạt?",
    "Người dự phải tham gia đủ thời gian học mới được kiểm tra; bài kiểm tra làm trong 120 phút, chấm theo thang điểm 10, từ 5 "
    "điểm trở lên là đạt (điểm a khoản 7 Điều 12 " + ND + ").", n("d12:k7:a", M10), n("d12:k7", M10))
add("tinh_huong", "Tôi làm bài kiểm tra tập huấn nghiệp vụ vận tải được 4 điểm. Bao lâu thì tôi được kiểm tra lại?",
    "Lái xe có điểm dưới 5 điểm được Sở Xây dựng kiểm tra lại sau tối thiểu 05 ngày làm việc kể từ ngày kết thúc đợt tập huấn "
    "(điểm c khoản 7 Điều 12 " + ND + ").", n("d12:k7:c", M10), n("d12:k7", M10))
add("quy_tac", "Giấy chứng nhận tập huấn nghiệp vụ vận tải có giá trị bao lâu?",
    "Giấy chứng nhận tập huấn có giá trị trong thời hạn 05 năm kể từ ngày cấp (điểm c khoản 7 Điều 12 " + ND + ").",
    n("d12:k7:c", M10))
add("doi_thuong", "tập huấn nghiệp vụ cho tài xế học online dc ko",
    "Được. Hình thức tập huấn là trực tiếp hoặc trực tuyến (khoản 6 Điều 12 " + ND + ").", n("d12:k6", M10))
add("thu_tuc", "Đơn vị vận tải đăng ký cho lái xe đi tập huấn nghiệp vụ như thế nào?",
    "Sở Xây dựng thông báo kế hoạch tập huấn (thời gian, địa điểm, cán bộ tập huấn, hình thức, kinh phí) đến các đơn vị tối "
    "thiểu trước 30 ngày tính đến ngày bắt đầu; đơn vị có nhu cầu lập và gửi danh sách học viên đến Sở Xây dựng trong thời gian "
    "trước 20 ngày tính đến ngày bắt đầu tập huấn (điểm c khoản 5 Điều 12 " + ND + ").", n("d12:k5:c", M10), n("d12:k5", M10))

# ===== Điều kiện và niên hạn xe (Điều 13)
add("quy_tac", "Xe khách chạy tuyến cố định phải có ít nhất bao nhiêu chỗ và niên hạn bao lâu?",
    "Xe phải có sức chứa từ 08 chỗ trở lên (không kể chỗ của người lái xe); niên hạn không quá 15 năm đối với tuyến cự ly trên "
    "300 ki-lô-mét và không quá 20 năm đối với tuyến từ 300 ki-lô-mét trở xuống (khoản 3 Điều 13 " + ND + ").", n("d13:k3"))
add("quy_tac", "Xe taxi phải có bao nhiêu chỗ và được dùng tối đa bao nhiêu năm?",
    "Xe taxi phải có sức chứa dưới 08 chỗ (không kể chỗ của người lái xe), niên hạn sử dụng không quá 12 năm. Không được dùng xe "
    "thiết kế, cải tạo thành ít hơn 08 chỗ từ xe lớn hơn 08 chỗ để kinh doanh taxi (khoản 5 Điều 13 " + ND + ").", n("d13:k5"))
add("quy_tac", "Xe chở khách theo hợp đồng có niên hạn sử dụng bao lâu?",
    "Không quá 15 năm đối với xe chạy hành trình cự ly trên 300 ki-lô-mét, không quá 20 năm đối với hành trình từ 300 ki-lô-mét "
    "trở xuống; riêng xe dưới 08 chỗ dùng hợp đồng điện tử có niên hạn không quá 12 năm (khoản 6 Điều 13 " + ND + ").",
    n("d13:k6", M10))
add("tinh_huong", "Tôi muốn đưa ô tô đứng tên mình vào hợp tác xã để chạy chở khách. Cần giấy tờ gì giữa tôi và hợp tác xã?",
    "Xe đăng ký thuộc sở hữu của thành viên hợp tác xã thì phải có hợp đồng dịch vụ giữa thành viên với hợp tác xã, trong đó quy "
    "định hợp tác xã có quyền, trách nhiệm và nghĩa vụ quản lý, sử dụng, điều hành xe đó (khoản 1 Điều 13 " + ND + ").",
    n("d13:k1"))

# ===== Hợp đồng điện tử (Điều 18)
add("quy_tac", "Đặt xe bằng hợp đồng điện tử thì đơn vị vận tải phải gửi cho khách những gì?",
    "Đơn vị phải có giao diện phần mềm thể hiện tên hoặc logo, số điện thoại liên hệ khẩn cấp và các nội dung tối thiểu của hợp "
    "đồng; phải gửi nội dung tối thiểu của hợp đồng vận tải và hóa đơn điện tử của chuyến đi đến tài khoản giao kết hợp đồng của "
    "hành khách và cơ quan Thuế (điểm a, điểm b khoản 2 Điều 18 " + ND + ").", n("d18:k2:a"), n("d18:k2:b"), n("d18:k2"))
add("quy_tac", "Dữ liệu hợp đồng vận tải điện tử phải lưu trong bao lâu?",
    "Đơn vị kinh doanh vận tải sử dụng hợp đồng điện tử phải lưu trữ dữ liệu hợp đồng điện tử tối thiểu 03 năm (điểm c khoản 2 "
    "Điều 18 " + ND + ").", n("d18:k2:c"), n("d18:k2"))
add("quy_tac", "Khách đặt xe theo hợp đồng điện tử cần lưu ý gì?",
    "Khách phải dùng thiết bị truy cập được giao diện phần mềm thể hiện toàn bộ nội dung hợp đồng điện tử, và khi ký kết với đơn "
    "vị vận tải phải tuân theo Bộ luật Dân sự (khoản 4 Điều 18 " + ND + ").", n("d18:k4:a"), n("d18:k4:b"), n("d18:k4"))

# ===== Vận tải nội bộ (Điều 24, 25)
add("doi_thuong", "xe đưa đón công nhân của công ty phải dán chữ gì lên kính",
    "Xe ô tô vận tải người nội bộ phải dán cố định cụm từ “XE NỘI BỘ” bằng vật liệu phản quang trên kính phía trước và kính phía "
    "sau, kích thước tối thiểu 10 x 35 cm; nếu niêm yết bằng thiết bị điện tử thì cụm từ phải luôn bật sáng (điểm b khoản 1 Điều "
    "24 " + ND + ").", n("d24:k1:b"), n("d24:k1"))
add("quy_tac", "Lái xe chở người nội bộ phải làm gì trước khi cho xe chạy?",
    "Lái xe phải kiểm tra điều kiện an toàn của xe, hướng dẫn người ngồi trên xe về an toàn giao thông và thoát hiểm khi gặp sự "
    "cố, yêu cầu mọi người thắt dây an toàn trước khi khởi hành, và kiểm tra việc sắp xếp, chằng buộc hành lý (điểm a khoản 3 "
    "Điều 24 " + ND + ").", n("d24:k3:a"), n("d24:k3"))
add("quy_tac", "Lái xe chở người nội bộ được quyền từ chối lái xe khi nào?",
    "Lái xe từ chối điều khiển phương tiện khi phát hiện xe không bảo đảm điều kiện an toàn, không có hoặc không có đủ dây an "
    "toàn trên xe (điểm d khoản 3 Điều 24 " + ND + ").", n("d24:k3:d"), n("d24:k3"))
add("tinh_huong", "Công ty tôi có xe tải nội bộ. Có được dùng xe này chở hàng thuê cho bên ngoài không?",
    "Không. Đơn vị vận tải hàng hóa nội bộ chỉ được dùng xe để chở sản phẩm, hàng hóa do chính đơn vị sản xuất hoặc trang thiết "
    "bị, dụng cụ, nguyên vật liệu, nhiên liệu, động sản khác phục vụ hoạt động của đơn vị mình (điểm đ khoản 2 Điều 25 " + ND
    + ").", n("d25:k2:đ"), n("d25:k2"))
add("thu_tuc", "Xe tải nội bộ chở hàng của công ty có phải mang giấy vận tải không?",
    "Có. Đơn vị phải cấp cho lái xe Giấy vận tải (giấy hoặc điện tử) trước khi chở hàng, tối thiểu gồm tên đơn vị, biển kiểm "
    "soát xe, hành trình, loại hàng và khối lượng hàng (điểm h khoản 2 Điều 25 " + ND + "). Lái xe phải mang theo Giấy vận tải "
    "hoặc thiết bị truy cập phần mềm thể hiện nội dung đó, và yêu cầu người xếp hàng ký xác nhận vào Giấy vận tải (điểm b khoản 3).",
    n("d25:k2:h"), n("d25:k3:b"))

# ===== Liên vận quốc tế (Điều 28)
add("quy_tac", "Xe có giấy phép liên vận quốc tế được chạy trên những tuyến nào?",
    "Phương tiện được cấp giấy phép liên vận hoạt động theo các tuyến đường và cửa khẩu ghi trong giấy phép; không được chở hàng "
    "hóa hoặc hành khách giữa hai điểm trong lãnh thổ của một quốc gia thành viên khác, không được chở hàng giữa các điểm trong "
    "lãnh thổ của quốc gia quá cảnh (Điều 28 " + ND + ").", n("d28:k1"), n("d28:k2"))

out = ROOT / "data/train/drafts/huong_dan_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
