"""Đợt 6a G5: Lệ phí (NĐ 10/2022 lệ phí trước bạ, bản sửa 01/7/2025; TT 155/2025/TT-BTC lệ phí đăng ký, cấp biển) và
Bảo hiểm bắt buộc TNDS chủ xe cơ giới (NĐ 67/2023, bản sửa 01/7/2026). Ghi data/train/drafts/le_phi_bao_hiem_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND10 = "Nghị định 10/2022/NĐ-CP"
TT155 = "Thông tư 155/2025/TT-BTC"
ND67 = "Nghị định 67/2023/NĐ-CP"
S = []
J25, J26 = "2025-07-01", "2026-07-01"


def a(s, d="2022-03-01"):
    return f"nd_10_2022:{s}@{d}"


def b(s):
    return f"tt_155_2025_btc:{s}@2026-01-01"


def c(s, d="2023-09-06"):
    return f"nd_67_2023:{s}@{d}"


N = {"lp": 0, "bh": 0}


def add(pre, chu_de, loai, q, ans, *can_cu):
    N[pre] += 1
    S.append({"key": f"{pre}-{N[pre]:04d}", "chu_de": chu_de, "loai": loai, "cau_hoi": q, "dap_an": ans,
              "can_cu": list(can_cu)})


L, B = "Lệ phí", "Bảo hiểm"

# ===== Lệ phí trước bạ (NĐ 10/2022)
add("lp", L, "muc_phat", "Mua xe máy mới thì nộp lệ phí trước bạ bao nhiêu phần trăm?",
    "Xe máy nộp lệ phí trước bạ với mức thu 2%; từ lần thứ 2 trở đi áp dụng mức thu 1% (khoản 4 Điều 8 " + ND10 + ", nội "
    "dung có hiệu lực từ ngày 01/7/2025).", a("d8:k4", J25))
add("lp", L, "doi_thuong", "mua xe máy cũ thì trước bạ mấy %",
    "Xe máy nộp lệ phí trước bạ từ lần thứ 2 trở đi được áp dụng mức thu 1% (khoản 4 Điều 8 " + ND10 + ", nội dung có hiệu "
    "lực từ ngày 01/7/2025). Giá tính lệ phí là giá trị còn lại của xe mới cùng kiểu loại trong Bảng giá tính lệ phí trước "
    "bạ theo thời gian sử dụng (khoản 4 Điều 7).", a("d8:k4", J25), a("d7:k4"))
add("lp", L, "muc_phat", "Ô tô con dưới 9 chỗ nộp lệ phí trước bạ lần đầu bao nhiêu?",
    "Ô tô chở người từ 09 chỗ ngồi trở xuống (bao gồm cả xe pick-up chở người) nộp lệ phí trước bạ lần đầu với mức thu 10%; "
    "Hội đồng nhân dân cấp tỉnh có thể quyết định tăng nhưng tối đa không quá 50% mức thu chung này (điểm a khoản 5 Điều 8 "
    + ND10 + ", nội dung có hiệu lực từ ngày 01/7/2025).", a("d8:k5:a", J25), a("d8:k5", J25))
add("lp", L, "muc_phat", "Mua lại ô tô con đã qua sử dụng thì nộp lệ phí trước bạ bao nhiêu?",
    "Các loại ô tô con, pick-up cabin kép, ô tô điện chạy pin nộp lệ phí trước bạ lần thứ 2 trở đi với mức thu 2%, áp dụng "
    "thống nhất trên toàn quốc (điểm d khoản 5 Điều 8 " + ND10 + ", nội dung có hiệu lực từ ngày 01/7/2025).",
    a("d8:k5:d", J25), a("d8:k5", J25))
add("lp", L, "doi_thuong", "mua ô tô điện có phải đóng trước bạ ko",
    "Hiện chưa phải đóng. Ô tô điện chạy pin nộp lệ phí trước bạ lần đầu với mức thu 0% kể từ ngày Nghị định có hiệu lực đến "
    "hết ngày 28/02/2027 (điểm c khoản 5 Điều 8 " + ND10 + ", nội dung có hiệu lực từ ngày 01/7/2025). Từ lần thứ 2 trở đi "
    "mức thu là 2% (điểm d khoản 5 Điều 8).", a("d8:k5:c", J25), a("d8:k5:d", J25))
add("lp", L, "muc_phat", "Xe tải, rơ moóc nộp lệ phí trước bạ với mức thu bao nhiêu?",
    "Ô tô, rơ moóc, sơ mi rơ moóc, xe chở người, chở hàng bốn bánh có gắn động cơ, xe máy chuyên dùng và các loại xe tương "
    "tự nộp lệ phí trước bạ với mức thu 2%, trừ các loại có mức riêng như ô tô chở người từ 09 chỗ ngồi trở xuống (khoản 5 Điều 8 " + ND10 + ", "
    "nội dung có hiệu lực từ ngày 01/7/2025).", a("d8:k5", J25), a("d8:k5:a", J25))
add("lp", L, "quy_tac", "Giá tính lệ phí trước bạ của ô tô, xe máy mới được lấy ở đâu?",
    "Là giá tại Bảng giá tính lệ phí trước bạ do Ủy ban nhân dân tỉnh, thành phố trực thuộc trung ương ban hành (trừ ô tô "
    "chuyên dùng, xe máy chuyên dùng) (khoản 3 Điều 7 " + ND10 + ", nội dung có hiệu lực từ ngày 01/7/2025).",
    a("d7:k3", J25))
add("lp", L, "quy_tac", "Mua xe trả góp thì giá tính lệ phí trước bạ có cộng tiền lãi không?",
    "Không. Giá tính lệ phí trước bạ với tài sản mua trả góp là giá trả một lần, không bao gồm lãi trả góp, nhưng bao gồm cả "
    "thuế nhập khẩu, thuế tiêu thụ đặc biệt, thuế giá trị gia tăng nếu có (khoản 5 Điều 7 " + ND10 + ").", a("d7:k5"))
add("lp", L, "quy_tac", "Mẫu xe mới chưa có trong Bảng giá tính lệ phí trước bạ thì tính thế nào?",
    "Cơ quan thuế cấp tỉnh căn cứ vào cơ sở dữ liệu giá chuyển nhượng trên thị trường để quyết định giá tính lệ phí trước bạ "
    "của loại ô tô, xe máy mới phát sinh trên địa bàn (điểm b khoản 3 Điều 7 " + ND10 + ", nội dung có hiệu lực từ ngày "
    "01/7/2025).", a("d7:k3:b", J25), a("d7:k3", J25))
add("lp", L, "quy_tac", "Thay máy hoặc khung ô tô phải đăng ký lại thì nộp lệ phí trước bạ bao nhiêu?",
    "Vỏ, tổng thành khung, tổng thành máy, thân máy (block) của ô tô được thay thế và phải đăng ký với cơ quan có thẩm quyền "
    "áp dụng mức thu lệ phí trước bạ là 2% (khoản 6 Điều 8 " + ND10 + ", nội dung có hiệu lực từ ngày 01/7/2025). Nếu thay "
    "thế và phải đăng ký lại trong thời hạn bảo hành thì được miễn (khoản 24 Điều 10).", a("d8:k6", J25), a("d10:k24"))
add("lp", L, "quy_tac", "Những loại xe nào được miễn lệ phí trước bạ?",
    "Theo khoản 21 Điều 10 " + ND10 + ", được miễn gồm xe cứu hỏa, xe cứu thương, xe chiếu chụp X-quang, xe cứu hộ; xe chở "
    "rác, xe phun nước, xe tưới nước, xe quét đường, xe hút bụi, xe hút chất thải; xe ô tô chuyên dùng, xe máy chuyên dùng "
    "cho thương binh, bệnh binh, người tàn tật đăng ký tên người đó. Ngoài ra, phương tiện vận tải hành khách công cộng bằng "
    "xe buýt sử dụng năng lượng sạch cũng được miễn (khoản 31 Điều 10).", a("d10:k21"), a("d10:k31"))
add("lp", L, "tinh_huong", "Tôi chuyển nơi ở sang tỉnh khác và mang theo xe đã nộp trước bạ. Có phải nộp lại lệ phí trước bạ "
    "không?",
    "Không. Tài sản của tổ chức, cá nhân đã nộp lệ phí trước bạ chuyển đến địa phương nơi sử dụng mà không thay đổi chủ sở "
    "hữu được miễn nộp lệ phí trước bạ (khoản 19 Điều 10 " + ND10 + ").", a("d10:k19"))
add("lp", L, "tinh_huong", "Vợ chồng ly hôn, chia chiếc xe cho một người đứng tên lại. Có phải nộp lệ phí trước bạ không?",
    "Không phải nộp. Tài sản đã được cấp giấy chứng nhận quyền sở hữu khi phân chia cho vợ, chồng khi ly hôn theo bản án, "
    "quyết định của Tòa án mà đăng ký lại được miễn lệ phí trước bạ (điểm c khoản 16 Điều 10 " + ND10 + ").",
    a("d10:k16:c"), a("d10:k16"))
add("lp", L, "quy_tac", "Xe đã được miễn lệ phí trước bạ lần đầu, nay bán cho người khác thì người mua có phải nộp không?",
    "Có, nếu người mua không thuộc diện được miễn: khi đăng ký quyền sở hữu, người mua nộp lệ phí trước bạ với mức thu lần "
    "đầu trên giá trị sử dụng còn lại của tài sản (khoản 7 Điều 8 " + ND10 + ").", a("d8:k7"))
add("lp", L, "quy_tac", "Mua xe được cấp lại giấy đăng ký do bị mất, rách có phải nộp lệ phí trước bạ lại không?",
    "Không. Tài sản đã được cấp giấy chứng nhận quyền sở hữu khi được cấp lại do giấy bị mất, rách nát, ố, nhòe, hư hỏng thì "
    "được miễn lệ phí trước bạ, và không phải kê khai, làm thủ tục miễn (điểm d khoản 16 Điều 10 " + ND10 + ").",
    a("d10:k16:d"), a("d10:k16"))

# ===== Lệ phí đăng ký, cấp biển (TT 155/2025)
add("lp", L, "muc_phat", "Lệ phí đăng ký và cấp biển ô tô con dưới 9 chỗ ở Hà Nội, TP.HCM là bao nhiêu?",
    "Cấp mới chứng nhận đăng ký và biển số cho xe ô tô chở người từ 9 chỗ trở xuống (kể cả xe con pick-up): Khu vực I (Hà "
    "Nội, TP. Hồ Chí Minh) là 14.000.000 đồng; Khu vực II là 140.000 đồng (Biểu mức thu ban hành kèm " + TT155 + ", hiệu lực "
    "từ ngày 01/01/2026).", b("pl1"), b("d4:k2:a"))
add("lp", L, "muc_phat", "Đăng ký xe máy mới ở Hà Nội mất bao nhiêu tiền lệ phí cấp biển?",
    "Cấp mới chứng nhận đăng ký và biển số xe mô tô tại Khu vực I: trị giá đến 15.000.000 đồng là 700.000 đồng; trên "
    "15.000.000 đồng đến 40.000.000 đồng là 1.400.000 đồng; trên 40.000.000 đồng là 2.800.000 đồng. Tại Khu vực II là "
    "105.000 đồng (Biểu mức thu kèm " + TT155 + "). Trị giá xe là giá tính lệ phí trước bạ tại thời điểm đăng ký (khoản 4 "
    "Điều 5).", b("pl1"), b("d5:k4"))
add("lp", L, "quy_tac", "Khu vực I và Khu vực II khi tính lệ phí đăng ký xe gồm những nơi nào?",
    "Khu vực I gồm Thành phố Hà Nội và Thành phố Hồ Chí Minh (tất cả xã, phường, không phân biệt nội thành hay ngoại thành, "
    "trừ đặc khu trực thuộc cấp tỉnh). Khu vực II gồm đặc khu thuộc khu vực I và các tỉnh, thành phố khác (khoản 2 Điều 4 "
    + TT155 + ").", b("d4:k2"), b("d4:k2:a"), b("d4:k2:b"))
add("lp", L, "quy_tac", "Lệ phí đăng ký xe tính theo nơi mua xe hay nơi cư trú?",
    "Theo nơi cư trú hoặc trụ sở: tổ chức, cá nhân có trụ sở, nơi cư trú ở khu vực nào thì nộp lệ phí theo mức thu của khu "
    "vực đó. Người trúng đấu giá biển số nộp theo mức thu của khu vực mình lựa chọn cấp biển trúng đấu giá (khoản 2 Điều 5 "
    + TT155 + ").", b("d5:k2"))
add("lp", L, "muc_phat", "Sang tên, đổi giấy đăng ký kèm biển số ô tô thì lệ phí bao nhiêu?",
    "Cấp đổi chứng nhận đăng ký xe kèm theo biển số: xe ô tô 105.000 đồng, xe mô tô 70.000 đồng, mức thu chung cho cả hai "
    "khu vực. Cấp đổi chứng nhận đăng ký không kèm biển số: 35.000 đồng (Biểu mức thu kèm " + TT155 + "). Đăng ký sang tên "
    "thuộc nhóm đổi chứng nhận đăng ký xe và biển số (điểm a khoản 4 Điều 4).", b("pl1"), b("d4:k4:a"))
add("lp", L, "muc_phat", "Đổi biển số xe máy bị hỏng thì lệ phí là bao nhiêu?",
    "Cấp đổi biển số xe: xe mô tô 50.000 đồng, xe ô tô 100.000 đồng, mức thu chung cho Khu vực I và Khu vực II (Biểu mức thu "
    "kèm " + TT155 + ").", b("pl1"), b("d4:k4:b"))
add("lp", L, "muc_phat", "Lệ phí cấp đăng ký xe tạm thời là bao nhiêu?",
    "Cấp chứng nhận đăng ký xe tạm thời và biển số tạm thời bằng giấy: 35.000 đồng; bằng kim loại: 105.000 đồng, mức thu "
    "chung cho cả hai khu vực (Biểu mức thu kèm " + TT155 + ").", b("pl1"))
add("lp", L, "quy_tac", "Trường hợp nào được miễn lệ phí đăng ký, cấp biển xe?",
    "Theo Điều 6 " + TT155 + ", được miễn: cơ quan đại diện ngoại giao, lãnh sự, cơ quan đại diện tổ chức quốc tế thuộc hệ "
    "thống Liên hợp quốc; viên chức ngoại giao, lãnh sự và thành viên gia đình không phải công dân Việt Nam được cấp chứng "
    "minh thư ngoại giao, công vụ; tổ chức, cá nhân nước ngoài được miễn theo điều ước quốc tế; và xe mô tô ba bánh chuyên "
    "dùng cho người khuyết tật.", b("d6:k1"), b("d6:k2"), b("d6:k4"))
add("lp", L, "quy_tac", "Đăng ký xe máy chuyên dùng có áp dụng biểu lệ phí của Thông tư 155/2025 không?",
    "Không. Thông tư 155/2025/TT-BTC không áp dụng đối với việc cấp chứng nhận đăng ký và biển số cho xe máy chuyên dùng và "
    "xe cơ giới của quân đội sử dụng vào mục đích quốc phòng (khoản 3 Điều 1).", b("d1:k3"))
add("lp", L, "quy_tac", "Biểu lệ phí đăng ký xe hiện hành áp dụng từ khi nào?",
    "Thông tư 155/2025/TT-BTC có hiệu lực từ ngày 01/01/2026 và thay thế Thông tư 60/2023/TT-BTC (khoản 1, khoản 2 Điều 8).",
    b("d8:k1"), b("d8:k2"))

# ===== Bảo hiểm bắt buộc TNDS (NĐ 67/2023)
add("bh", B, "muc_phat", "Phí bảo hiểm bắt buộc trách nhiệm dân sự cho xe máy là bao nhiêu một năm?",
    "Theo Phụ lục I " + ND67 + ", phí bảo hiểm cho thời hạn 1 năm, chưa gồm thuế giá trị gia tăng, tính bằng đồng: mô tô 2 "
    "bánh dưới 50 cc: 55.000; từ 50 cc trở lên: 60.000; xe máy điện: 55.000; mô tô 3 bánh: 290.000.", c("pl1"), c("d8:k1"))
add("bh", B, "doi_thuong", "bảo hiểm bắt buộc ô tô 5 chỗ gia đình hết bao nhiêu tiền",
    "Theo Phụ lục I " + ND67 + ", xe ô tô không kinh doanh vận tải loại dưới 6 chỗ có phí bảo hiểm bắt buộc trách nhiệm dân "
    "sự cho thời hạn 1 năm (đơn vị đồng, chưa gồm thuế giá trị gia tăng) là 437.000.", c("pl1"), c("d8:k1"))
add("bh", B, "muc_phat", "Phí bảo hiểm bắt buộc cho ô tô 7 chỗ không kinh doanh là bao nhiêu?",
    "Theo Phụ lục I " + ND67 + ", xe ô tô không kinh doanh vận tải loại từ 6 đến 11 chỗ có phí bảo hiểm cho thời hạn 1 năm "
    "(đơn vị đồng, chưa gồm thuế giá trị gia tăng) là 794.000.", c("pl1"))
add("bh", B, "muc_phat", "Phí bảo hiểm bắt buộc của xe tải từ 3 đến 8 tấn là bao nhiêu?",
    "Theo Phụ lục I " + ND67 + ", phí bảo hiểm xe ô tô chở hàng cho thời hạn 1 năm (đơn vị đồng, chưa gồm thuế giá trị gia "
    "tăng): từ 3 đến 8 tấn: 1.660.000; dưới 3 tấn: 853.000; trên 8 đến 15 tấn: 2.746.000; trên 15 tấn: 3.200.000.", c("pl1"))
add("bh", B, "quy_tac", "Phí bảo hiểm bắt buộc cho xe taxi được tính thế nào?",
    "Phí bảo hiểm xe taxi tính bằng 170% phí bảo hiểm của xe kinh doanh vận tải cùng số chỗ; xe tập lái tính bằng 120% phí "
    "của xe cùng chủng loại (Phụ lục I " + ND67 + ").", c("pl1"))
add("bh", B, "quy_tac", "Doanh nghiệp bảo hiểm có được tăng giảm phí bảo hiểm bắt buộc không?",
    "Có, căn cứ lịch sử bồi thường của từng xe hoặc lịch sử gây tai nạn của chủ xe, doanh nghiệp bảo hiểm được điều chỉnh "
    "tăng, giảm phí, tối đa 15% so với mức phí tại Phụ lục I (khoản 2 Điều 8 " + ND67 + ").", c("d8:k2"))
add("bh", B, "quy_tac", "Bảo hiểm bắt buộc xe máy bồi thường tối đa bao nhiêu cho người bị thương, chết?",
    "Giới hạn trách nhiệm bảo hiểm đối với thiệt hại về sức khỏe, tính mạng do xe cơ giới gây ra là 150 triệu đồng cho một "
    "người trong một vụ tai nạn (khoản 1 Điều 6 " + ND67 + ").", c("d6:k1"))
add("bh", B, "quy_tac", "Bảo hiểm bắt buộc bồi thường thiệt hại tài sản tối đa bao nhiêu?",
    "Với thiệt hại về tài sản: do xe mô tô, xe gắn máy (kể cả xe máy điện) gây ra là 50 triệu đồng trong một vụ tai nạn; do "
    "xe ô tô, máy kéo, rơ moóc, sơ mi rơ moóc gây ra là 100 triệu đồng trong một vụ tai nạn (khoản 2 Điều 6 " + ND67 + ").",
    c("d6:k2:a"), c("d6:k2:b"))
add("bh", B, "quy_tac", "Bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe bồi thường cho những thiệt hại nào?",
    "Doanh nghiệp bảo hiểm bồi thường thiệt hại ngoài hợp đồng về sức khỏe, tính mạng và tài sản đối với bên thứ ba do xe cơ "
    "giới tham gia giao thông, hoạt động gây ra (điểm a khoản 1 Điều 7 " + ND67 + ", nội dung có hiệu lực từ ngày 01/7/2026), "
    "và thiệt hại về sức khỏe, tính mạng của hành khách trên chiếc xe đó (điểm b khoản 1 Điều 7).",
    c("d7:k1:a", J26), c("d7:k1:b"))
add("bh", B, "tinh_huong", "Tôi say rượu lái xe gây tai nạn làm hỏng xe người khác. Bảo hiểm bắt buộc có trả tiền sửa xe cho "
    "họ không?",
    "Không. Doanh nghiệp bảo hiểm không bồi thường thiệt hại đối với tài sản do người lái xe điều khiển xe cơ giới mà trong máu "
    "hoặc hơi thở có nồng độ cồn vượt quá mức trị số bình thường theo hướng dẫn của Bộ Y tế, hoặc sử dụng ma túy, chất kích "
    "thích bị cấm (điểm đ khoản 2 Điều 7 " + ND67 + ").", c("d7:k2:đ"), c("d7:k2"))
add("bh", B, "tinh_huong", "Người lái xe không có bằng lái gây tai nạn thì bảo hiểm bắt buộc có bồi thường không?",
    "Không. Người lái xe không đủ tuổi, không có giấy phép lái xe, dùng giấy phép không hợp lệ, bị tẩy xóa, hết hạn hoặc không "
    "phù hợp với loại xe phải có giấy phép thuộc trường hợp loại trừ trách nhiệm bảo hiểm (điểm c khoản 2 Điều 7 " + ND67 + ").",
    c("d7:k2:c"), c("d7:k2"))
add("bh", B, "tinh_huong", "Lái xe gây tai nạn rồi bỏ chạy thì bảo hiểm có bồi thường không?",
    "Người lái xe gây tai nạn cố ý bỏ chạy không thực hiện trách nhiệm dân sự của chủ xe thuộc trường hợp loại trừ trách "
    "nhiệm bảo hiểm. Nhưng nếu bỏ chạy mà sau đó đã thực hiện trách nhiệm dân sự của chủ xe thì không thuộc trường hợp loại "
    "trừ (điểm b khoản 2 Điều 7 " + ND67 + ").", c("d7:k2:b"))
add("bh", B, "quy_tac", "Bảo hiểm bắt buộc có đền tiền cho đồ bị mất cắp trong vụ tai nạn không?",
    "Không. Thiệt hại đối với tài sản bị mất cắp hoặc bị cướp trong tai nạn, và thiệt hại đối với tài sản đặc biệt như vàng, "
    "bạc, đá quý, giấy tờ có giá, đồ cổ, tranh ảnh quý hiếm thuộc trường hợp loại trừ trách nhiệm bảo hiểm (điểm e, điểm g "
    "khoản 2 Điều 7 " + ND67 + ").", c("d7:k2:e"), c("d7:k2:g"))
add("bh", B, "quy_tac", "Thời hạn bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe là bao lâu?",
    "Tối thiểu 1 năm và tối đa 3 năm, trừ một số trường hợp được dưới 1 năm như xe nước ngoài tạm nhập tái xuất có thời hạn "
    "dưới 1 năm, xe có niên hạn sử dụng còn dưới 1 năm, xe đăng ký tạm thời (khoản 1 Điều 9 " + ND67 + ").", c("d9:k1"),
    c("d9:k1:c"))
add("bh", B, "tinh_huong", "Tôi bán xe khi bảo hiểm bắt buộc còn hạn. Tôi có lấy lại được tiền bảo hiểm không?",
    "Khi chuyển quyền sở hữu xe trong thời hạn bảo hiểm, chủ xe cũ có quyền chấm dứt hợp đồng bảo hiểm (khoản 3 Điều 9 " + ND67
    + "). Khi xe bị thu hồi chứng nhận đăng ký, biển số, hợp đồng chấm dứt kể từ thời điểm thu hồi và doanh nghiệp bảo hiểm "
    "hoàn phí tương ứng thời hạn còn lại (Điều 11).", c("d9:k3"), c("d11"))
add("bh", B, "quy_tac", "Mỗi xe được mua bao nhiêu hợp đồng bảo hiểm bắt buộc?",
    "Với mỗi xe, trách nhiệm bồi thường bảo hiểm bắt buộc chỉ phát sinh theo một hợp đồng duy nhất (khoản 4 Điều 4 " + ND67
    + "). Nếu có nhiều hợp đồng cho cùng một xe thì chỉ giải quyết theo hợp đồng giao kết đầu tiên, và doanh nghiệp phải hoàn "
    "100% phí của các hợp đồng còn lại (khoản 9 Điều 12).", c("d4:k4"), c("d12:k9"))
add("bh", B, "quy_tac", "Doanh nghiệp bảo hiểm có được từ chối bán bảo hiểm bắt buộc cho xe không?",
    "Có, khi xe cơ giới đã hết niên hạn sử dụng theo quy định (điểm a khoản 5 Điều 4 " + ND67 + ").", c("d4:k5:a"))
add("bh", B, "doi_thuong", "mất giấy bảo hiểm xe máy thì làm sao",
    "Mỗi xe được cấp 1 giấy chứng nhận bảo hiểm; chủ xe bị mất phải có văn bản đề nghị doanh nghiệp bảo hiểm cấp lại (khoản 1 "
    "Điều 10 " + ND67 + "). Doanh nghiệp bảo hiểm cũng có thể cấp giấy chứng nhận bảo hiểm điện tử (khoản 3 Điều 10).",
    c("d10:k1"), c("d10:k3"))
add("bh", B, "thu_tuc", "Khi xảy ra tai nạn, chủ xe có bảo hiểm bắt buộc phải làm gì?",
    "Theo khoản 1 Điều 12 " + ND67 + ": thông báo ngay cho doanh nghiệp bảo hiểm qua đường dây nóng, tích cực cứu chữa, hạn "
    "chế thiệt hại, bảo vệ hiện trường; không di chuyển, tháo gỡ, sửa chữa tài sản khi chưa có ý kiến của doanh nghiệp bảo "
    "hiểm (trừ trường hợp cần thiết để bảo đảm an toàn hoặc theo yêu cầu cơ quan có thẩm quyền); chủ động thu thập, cung cấp "
    "tài liệu bồi thường. Trong 5 ngày làm việc kể từ ngày xảy ra tai nạn phải gửi thông báo tai nạn bằng văn bản hoặc điện "
    "tử (khoản 4 Điều 12).", c("d12:k1:a"), c("d12:k1:b"), c("d12:k4"))
add("bh", B, "quy_tac", "Doanh nghiệp bảo hiểm phải tạm ứng bồi thường cho người bị nạn trong bao lâu?",
    "Trong vòng 3 ngày làm việc kể từ khi nhận thông báo tai nạn, doanh nghiệp bảo hiểm phải tạm ứng bồi thường về sức khỏe, "
    "tính mạng: nếu đã xác định thuộc phạm vi bồi thường thì 70% mức bồi thường ước tính với trường hợp tử vong, 50% với "
    "trường hợp tổn thương bộ phận (khoản 3 Điều 12 " + ND67 + ").", c("d12:k3"), c("d12:k3:a"))
add("bh", B, "thu_tuc", "Hồ sơ yêu cầu bồi thường bảo hiểm bắt buộc trách nhiệm dân sự gồm những gì?",
    "Theo Điều 13 " + ND67 + ": văn bản yêu cầu bồi thường; tài liệu về xe và người lái (đăng ký xe, giấy phép lái xe, giấy tờ "
    "tùy thân, giấy chứng nhận bảo hiểm); tài liệu chứng minh thiệt hại về người (giấy chứng nhận thương tích, hồ sơ bệnh án, "
    "giấy báo tử…) và về tài sản (hóa đơn, chứng từ sửa chữa); tài liệu của cơ quan Công an trong vụ tai nạn gây tử vong; "
    "biên bản giám định; quyết định của Tòa án nếu có.", c("d13:k1"), c("d13:k2"), c("d13:k3"), c("d13:k4"))
add("bh", B, "quy_tac", "Không báo tai nạn cho công ty bảo hiểm đúng hạn thì có bị trừ tiền bồi thường không?",
    "Có thể. Doanh nghiệp bảo hiểm có quyền giảm trừ tối đa 5% số tiền bồi thường thiệt hại đối với tài sản nếu bên mua bảo "
    "hiểm không thông báo tai nạn theo khoản 4 Điều 12 (khoản 7 Điều 12 " + ND67 + ").", c("d12:k7"), c("d12:k4"))
add("bh", B, "quy_tac", "Thiệt hại vượt quá giới hạn bảo hiểm bắt buộc thì ai trả?",
    "Doanh nghiệp bảo hiểm không có trách nhiệm bồi thường phần vượt quá giới hạn trách nhiệm bảo hiểm bắt buộc, trừ trường "
    "hợp chủ xe có tham gia hợp đồng bảo hiểm tự nguyện (khoản 8 Điều 12 " + ND67 + ").", c("d12:k8"))

out = ROOT / "data/train/drafts/le_phi_bao_hiem_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
