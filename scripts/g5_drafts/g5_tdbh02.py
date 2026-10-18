"""Đợt C7 G5: tốc độ (TT 38/2024), bảo hiểm bắt buộc trách nhiệm dân sự (NĐ 67/2023), lệ phí trước bạ (NĐ 10/2022) và lệ
phí đăng ký xe (TT 155/2025) ở các khoản chưa có mẫu. Ghi data/train/drafts/toc_do_bao_hiem_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT38 = "Thông tư 38/2024/TT-BGTVT"
ND67 = "Nghị định 67/2023/NĐ-CP"
ND10 = "Nghị định 10/2022/NĐ-CP"
TT155 = "Thông tư 155/2025/TT-BTC"
S = []
NEXT = {"td": 19, "bh": 24, "lp": 29}
TOPIC = {"td": "Tốc độ", "bh": "Bảo hiểm", "lp": "Lệ phí"}


def u38(s):
    return f"tt_38_2024_bgtvt:{s}@2025-01-01"


def u67(s, d="2023-09-06"):
    return f"nd_67_2023:{s}@{d}"


def u10(s, d="2022-03-01"):
    return f"nd_10_2022:{s}@{d}"


def u155(s):
    return f"tt_155_2025_btc:{s}@2026-01-01"


def add(prefix, loai, q, a, *can_cu):
    S.append({"key": f"{prefix}-{NEXT[prefix]:04d}", "chu_de": TOPIC[prefix], "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})
    NEXT[prefix] += 1


# ===== Tốc độ (TT 38/2024)
add("td", "quy_tac", "Xe chở hàng bốn bánh có gắn động cơ được chạy tối đa bao nhiêu km/h?",
    "Khi tham gia giao thông trong phạm vi và thời gian cho phép hoạt động, xe chở hàng bốn bánh có gắn động cơ có tốc độ khai "
    "thác tối đa là 50 km/h (khoản 2 Điều 8 " + TT38 + ").", u38("d8:k2"))
add("td", "quy_tac", "Đường cao tốc có tốc độ thiết kế 60 km/h thì tốc độ tối thiểu được tính thế nào?",
    "Tốc độ khai thác tối thiểu trên đường cao tốc là 60 km/h; riêng đường cao tốc có tốc độ thiết kế 60 km/h thì tốc độ tối "
    "thiểu thực hiện theo phương án tổ chức giao thông được cấp có thẩm quyền phê duyệt (khoản 3 Điều 9 " + TT38 + ").",
    u38("d9:k3"))
add("td", "quy_tac", "Trên đường nhánh ra, vào đường cao tốc thì tốc độ tối đa, tối thiểu do đâu quy định?",
    "Trị số tốc độ khai thác tối đa, tối thiểu trên đường cao tốc, kể cả các đường nhánh ra, vào, được xác định trong phương án "
    "tổ chức giao thông được cấp có thẩm quyền phê duyệt (khoản 4 Điều 9 " + TT38 + "); đường cao tốc phải đặt biển báo tốc độ "
    "khai thác tối đa, tối thiểu (khoản 1).", u38("d9:k4"), u38("d9:k1"))
add("td", "quy_tac", "Tốc độ thiết kế của đường và tốc độ khai thác tối đa khác nhau thế nào?",
    "Tốc độ thiết kế là giá trị vận tốc dùng để tính toán các chỉ tiêu kỹ thuật của đường, xác định khi đầu tư xây dựng, nâng "
    "cấp, cải tạo (khoản 1 Điều 5 " + TT38 + "). Tốc độ khai thác tối đa là giá trị tốc độ lớn nhất cho phép phương tiện tham "
    "gia giao thông trên đường bảo đảm an toàn và khai thác hiệu quả tuyến (khoản 6 Điều 3).", u38("d5:k1"), u38("d3:k6"))
add("td", "quy_tac", "Chạy dưới 60 km/h thì khoảng cách an toàn với xe phía trước tính thế nào?",
    "Khi chạy với tốc độ dưới 60 km/h, người lái phải chủ động giữ khoảng cách an toàn phù hợp với xe chạy liền trước; khoảng "
    "cách này tùy thuộc vào mật độ phương tiện và tình hình giao thông thực tế (điểm a khoản 2 Điều 11 " + TT38 + ").",
    u38("d11:k2:a"), u38("d11:k2"))
add("td", "tinh_huong", "Tôi chạy 110 km/h trên cao tốc, trời khô ráo, đường thẳng. Phải giữ khoảng cách tối thiểu bao nhiêu với xe trước?",
    "Trong điều kiện mặt đường khô ráo, không sương mù, đường thẳng, tầm nhìn bảo đảm, với tốc độ trên 100 km/h đến 120 km/h "
    "thì khoảng cách an toàn là 100 m (điểm a khoản 2 Điều 11 " + TT38 + "). Nếu có biển “Cự ly tối thiểu giữa hai xe” thì "
    "giữ khoảng cách không nhỏ hơn trị số ghi trên biển (khoản 1 Điều 11).", u38("d11:k2:a"), u38("d11:k1"))
add("td", "quy_tac", "Đường đôi có được đặt biển tốc độ tối đa riêng cho từng chiều không?",
    "Có. Cơ quan có thẩm quyền quyết định đặt biển báo tốc độ khai thác tối đa riêng cho từng chiều đường đối với đường đôi "
    "(điểm a khoản 2 Điều 10 " + TT38 + ").", u38("d10:k2:a"), u38("d10:k2"))
add("td", "quy_tac", "Đường trong khu đông dân cư rất hẹp, nhiều nhà sát đường thì có thể bị đặt tốc độ thấp hơn không?",
    "Có. Với đường đang khai thác trong khu đông dân cư có điều kiện bất lợi (đường một chiều hoặc hai chiều có tổng bề rộng "
    "phần xe chạy nhỏ hơn 3,0m, công trình sát mép phần xe chạy, tầm nhìn hạn chế), cơ quan quản lý đường bộ phối hợp với cảnh "
    "sát giao thông và Ủy ban nhân dân cấp huyện xem xét, quyết định tốc độ khai thác cho phép và đặt biển báo (điểm a khoản 4 "
    "Điều 10 " + TT38 + ").", u38("d10:k4:a"), u38("d10:k4"))
add("td", "quy_tac", "Theo quy định về tốc độ, trọng tải của xe là gì?",
    "Trọng tải là khối lượng hàng hóa chuyên chở cho phép, được ghi trên Giấy chứng nhận an toàn kỹ thuật và bảo vệ môi trường "
    "của phương tiện hoặc giấy chứng nhận chất lượng của xe nhập khẩu, xe sản xuất, lắp ráp (khoản 5 Điều 3 " + TT38 + ").",
    u38("d3:k5"))
add("td", "doi_thuong", "tốc độ lưu hành là gì vậy",
    "Tốc độ lưu hành là giá trị tốc độ của phương tiện tại thời điểm tham gia giao thông trên đường bộ (khoản 9 Điều 3 " + TT38
    + ").", u38("d3:k9"))

# ===== Bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe (NĐ 67/2023)
add("bh", "quy_tac", "Trong bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe, những ai không được coi là bên thứ ba?",
    "Bên thứ ba là người bị thiệt hại về sức khỏe, tính mạng, tài sản do xe cơ giới gây ra, trừ: người lái xe, người trên xe, "
    "hành khách trên chính chiếc xe đó; và chủ sở hữu xe, trừ khi chủ sở hữu đã giao cho người khác chiếm hữu, sử dụng chiếc xe "
    "đó (điểm a khoản 5 Điều 3 " + ND67 + ").", u67("d3:k5:a", "2026-07-01"), u67("d3:k5", "2026-07-01"))
add("bh", "quy_tac", "Bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe bảo hiểm cho cái gì?",
    "Đối tượng bảo hiểm là trách nhiệm dân sự của chủ xe cơ giới đối với bên thứ ba, hành khách theo quy định của pháp luật "
    "(Điều 5 " + ND67 + ").", u67("d5", "2026-07-01"))
add("bh", "quy_tac", "Ngoài bảo hiểm bắt buộc, chủ xe có mua thêm quyền lợi bảo hiểm được không?",
    "Được. Bên mua bảo hiểm và doanh nghiệp bảo hiểm có thể thỏa thuận trong hợp đồng về mở rộng điều kiện bảo hiểm, số tiền "
    "bảo hiểm tăng thêm và phí bảo hiểm bổ sung tương ứng; khi đó doanh nghiệp bảo hiểm phải tách riêng phần bảo hiểm bắt buộc "
    "trong hợp đồng (khoản 3 Điều 4 " + ND67 + ").", u67("d4:k3"))
add("bh", "quy_tac", "Giấy chứng nhận bảo hiểm bắt buộc xe cơ giới phải có những nội dung gì?",
    "Phải có: tên, địa chỉ, số điện thoại (nếu có) của chủ xe; biển số, số khung, số máy; loại xe, trọng tải, số chỗ, mục đích "
    "sử dụng (với ô tô); tên, địa chỉ, đường dây nóng của doanh nghiệp bảo hiểm; giới hạn trách nhiệm bảo hiểm với bên thứ ba; "
    "trách nhiệm của chủ xe, người lái khi xảy ra tai nạn; thời hạn, phí bảo hiểm, thời hạn thanh toán phí; ngày cấp; mã số, mã "
    "vạch định danh (khoản 2 Điều 10 " + ND67 + ").",
    u67("d10:k2"), u67("d10:k2:a"), u67("d10:k2:b"), u67("d10:k2:c"), u67("d10:k2:d"), u67("d10:k2:đ", "2026-07-01"),
    u67("d10:k2:e"), u67("d10:k2:g"), u67("d10:k2:h"), u67("d10:k2:i"))
add("bh", "doi_thuong", "giấy bảo hiểm xe điện tử trên điện thoại có dc ko hay phải bản giấy",
    "Được. Doanh nghiệp bảo hiểm có thể cấp Giấy chứng nhận bảo hiểm điện tử, nhưng phải tuân thủ Luật Giao dịch điện tử và "
    "phản ánh đầy đủ các nội dung bắt buộc như bản giấy (khoản 3 Điều 10 " + ND67 + ").", u67("d10:k3"), u67("d10:k2"))
add("bh", "thu_tuc", "Báo tai nạn cho công ty bảo hiểm rồi thì bao lâu họ phải hướng dẫn và giám định?",
    "Trong vòng 1 giờ kể từ khi nhận thông báo, doanh nghiệp bảo hiểm phải hướng dẫn các biện pháp bảo đảm an toàn, hạn chế "
    "thiệt hại và hồ sơ, thủ tục yêu cầu bồi thường; trong vòng 24 giờ phải phối hợp với các bên tổ chức giám định tổn thất để "
    "xác định nguyên nhân và mức độ tổn thất (khoản 2 Điều 12 " + ND67 + ").", u67("d12:k2", "2026-07-01"))
add("bh", "thu_tuc", "Sau tai nạn, chủ xe phải gửi thông báo tai nạn bằng văn bản cho công ty bảo hiểm trong bao lâu?",
    "Trong thời hạn 5 ngày làm việc kể từ ngày xảy ra tai nạn, trừ trường hợp bất khả kháng hoặc trở ngại khách quan, bên mua "
    "bảo hiểm phải gửi thông báo tai nạn bằng văn bản hoặc qua hình thức điện tử cho doanh nghiệp bảo hiểm (khoản 4 Điều 12 "
    + ND67 + ").", u67("d12:k4"))
add("bh", "quy_tac", "Chưa xác định được vụ tai nạn có thuộc phạm vi bồi thường không thì bảo hiểm tạm ứng bao nhiêu?",
    "Doanh nghiệp bảo hiểm vẫn phải tạm ứng trong 3 ngày làm việc: 30% giới hạn trách nhiệm bảo hiểm cho một người với trường "
    "hợp tử vong và ước tính tỷ lệ tổn thương từ 81% trở lên; 10% với trường hợp ước tính tỷ lệ tổn thương từ 31% đến dưới 81% "
    "(điểm b khoản 3 Điều 12 " + ND67 + ").", u67("d12:k3:b"), u67("d12:k3"))
add("bh", "quy_tac", "Bảo hiểm bắt buộc bồi thường thiệt hại tài sản theo cách tính nào?",
    "Mức bồi thường thiệt hại tài sản trong một vụ tai nạn được xác định theo thiệt hại thực tế và theo mức độ lỗi của chủ xe "
    "cơ giới, nhưng không vượt quá giới hạn trách nhiệm bảo hiểm (điểm b khoản 6 Điều 12 " + ND67 + ").",
    u67("d12:k6:b"), u67("d12:k6"))
add("bh", "quy_tac", "Khai khống thiệt hại để được bồi thường nhiều hơn thì bảo hiểm có trả phần đó không?",
    "Không. Doanh nghiệp bảo hiểm không có trách nhiệm bồi thường những khoản tiền phát sinh, tăng thêm do hành vi gian lận bảo "
    "hiểm theo quy định của Bộ luật Hình sự (khoản 8 Điều 4 " + ND67 + ").", u67("d4:k8"))
add("bh", "thu_tuc", "Vụ tai nạn có người chết thì hồ sơ bồi thường bảo hiểm cần thêm giấy tờ gì?",
    "Cần tài liệu chứng minh thiệt hại về tính mạng như trích lục khai tử, giấy báo tử hoặc văn bản xác nhận của cơ quan Công "
    "an hoặc kết quả giám định pháp y (điểm c khoản 3 Điều 13 " + ND67 + "); và bản sao tài liệu của cơ quan Công an như thông "
    "báo kết quả điều tra, xác minh, giải quyết vụ tai nạn (khoản 5 Điều 13).",
    u67("d13:k3:c"), u67("d13:k3"), u67("d13:k5", "2026-07-01"))
add("bh", "thu_tuc", "Khi yêu cầu bồi thường bảo hiểm, giấy tờ nào chủ xe tự nộp, giấy tờ nào công ty bảo hiểm tự thu thập?",
    "Bên mua bảo hiểm thu thập và gửi: văn bản yêu cầu bồi thường, tài liệu về xe và người lái, tài liệu chứng minh thiệt hại về "
    "người và tài sản, quyết định của Tòa án (nếu có). Doanh nghiệp bảo hiểm tự thu thập tài liệu của cơ quan Công an và biên "
    "bản giám định (khoản 7 Điều 13 " + ND67 + ").", u67("d13:k7"), u67("d13:k6"), u67("d13:k5", "2026-07-01"))
add("bh", "quy_tac", "Xe đang đỗ mà gây thiệt hại thì có được coi là xe cơ giới đang hoạt động không?",
    "Có. Xe cơ giới hoạt động là xe đang vận hành, gồm di chuyển, dừng xe, đỗ xe có sự điều khiển của chủ xe hoặc người lái xe "
    "(khoản 2 Điều 3 " + ND67 + ").", u67("d3:k2"))

# ===== Lệ phí trước bạ (NĐ 10/2022), lệ phí đăng ký xe (TT 155/2025)
add("lp", "quy_tac", "Những loại xe nào thuộc đối tượng chịu lệ phí trước bạ?",
    "Gồm xe mô tô, xe gắn máy và xe tương tự phải đăng ký, gắn biển số; xe ô tô, rơ moóc, sơ mi rơ moóc, xe chở người, chở hàng "
    "bốn bánh có gắn động cơ, xe máy chuyên dùng và xe tương tự phải đăng ký, gắn biển số (khoản 6, khoản 7 Điều 3 " + ND10
    + ").", u10("d3:k6", "2025-07-01"), u10("d3:k7", "2025-07-01"))
add("lp", "quy_tac", "Lệ phí trước bạ được tính dựa trên những căn cứ nào?",
    "Căn cứ tính lệ phí trước bạ là giá tính lệ phí trước bạ và mức thu lệ phí trước bạ theo tỷ lệ (%) (Điều 6 " + ND10 + ").",
    u10("d6"))
add("lp", "quy_tac", "Mua xe tịch thu do Nhà nước bán thì giá tính lệ phí trước bạ là giá nào?",
    "Với tài sản mua theo phương thức xử lý tài sản xác lập sở hữu toàn dân, giá tính lệ phí trước bạ là giá trên hóa đơn bán tài "
    "sản theo pháp luật về quản lý, sử dụng tài sản công (khoản 6 Điều 7 " + ND10 + ").", u10("d7:k6"))
add("lp", "quy_tac", "Giá xe trên thị trường chênh nhiều so với Bảng giá tính lệ phí trước bạ thì có được điều chỉnh không?",
    "Có. Khi giá chuyển nhượng ô tô, xe máy trên thị trường tăng hoặc giảm từ 5% trở lên so với giá tại Bảng giá, cơ quan thuế "
    "cấp tỉnh chủ trì, phối hợp Sở Tài chính tổng hợp, báo cáo Ủy ban nhân dân cấp tỉnh trước ngày mùng 5 tháng cuối quý để "
    "điều chỉnh (điểm c khoản 3 Điều 7 " + ND10 + ").", u10("d7:k3:c", "2025-07-01"), u10("d7:k3", "2025-07-01"))
add("lp", "tinh_huong", "Tôi góp chiếc ô tô đã nộp trước bạ vào công ty làm vốn. Công ty đăng ký lại xe có phải nộp lệ phí trước bạ không?",
    "Không phải nộp. Tài sản đã nộp lệ phí trước bạ (trừ trường hợp được miễn) mà chủ sở hữu đem góp vốn vào doanh nghiệp, tổ "
    "chức tín dụng, hợp tác xã thì được miễn khi bên nhận đăng ký quyền sở hữu (điểm a khoản 17 Điều 10 " + ND10 + ").",
    u10("d10:k17:a", "2025-07-01"), u10("d10:k17"))
add("lp", "quy_tac", "Doanh nghiệp điều chuyển xe giữa các đơn vị nội bộ có phải nộp lại lệ phí trước bạ không?",
    "Không. Tài sản đã nộp lệ phí trước bạ được doanh nghiệp điều động trong nội bộ doanh nghiệp đó (hoặc cơ quan, đơn vị điều "
    "động trong nội bộ theo quyết định của cấp có thẩm quyền) được miễn nộp lệ phí trước bạ (điểm b khoản 17 Điều 10 " + ND10
    + ").", u10("d10:k17:b"), u10("d10:k17"))
add("lp", "quy_tac", "Thuê tài chính ô tô, hết hạn thuê được chuyển quyền sở hữu thì có phải nộp lệ phí trước bạ không?",
    "Không. Tài sản cho thuê tài chính được chuyển quyền sở hữu cho bên thuê khi kết thúc thời hạn thuê thông qua việc nhượng, "
    "bán thì bên thuê được miễn nộp lệ phí trước bạ (khoản 12 Điều 10 " + ND10 + ").", u10("d10:k12"))
add("lp", "quy_tac", "Trúng đấu giá biển số thì nộp lệ phí đăng ký xe theo mức của khu vực nào?",
    "Người trúng đấu giá biển số nộp lệ phí cấp chứng nhận đăng ký xe và biển số theo mức thu của khu vực mà họ lựa chọn cấp "
    "biển số trúng đấu giá; các trường hợp khác nộp theo khu vực nơi có trụ sở, nơi cư trú (khoản 2 Điều 5 " + TT155 + ").",
    u155("d5:k2"))
add("lp", "doi_thuong", "xe máy điện đăng ký có tính lệ phí như xe máy xăng ko",
    "Có. Khi tính lệ phí cấp đăng ký xe, “xe mô tô” gồm xe mô tô hai bánh, ba bánh, xe gắn máy, kể cả xe máy điện và các loại xe "
    "tương tự (điểm b khoản 1 Điều 4 " + TT155 + "), nên áp dụng chung biểu lệ phí của xe mô tô.", u155("d4:k1:b"), u155("d4:k1"))
add("lp", "quy_tac", "Ô tô cũ nhập khẩu lần đầu đăng ký ở Việt Nam thì tính lệ phí theo cấp mới hay đổi?",
    "Theo cấp mới. Cấp mới chứng nhận đăng ký xe và biển số là cấp cho phương tiện đăng ký lần đầu tại Việt Nam, kể cả phương "
    "tiện đã qua sử dụng hay đã đăng ký tại nước ngoài, phương tiện bị tịch thu (khoản 3 Điều 4 " + TT155 + ").", u155("d4:k3"))
add("lp", "quy_tac", "Khi tính lệ phí, đổi chứng nhận đăng ký xe và biển số gồm những trường hợp nào?",
    "Gồm: cấp đăng ký, biển số khi sang tên, di chuyển xe; đổi, cấp lại đăng ký, biển số theo pháp luật trật tự, an toàn giao "
    "thông; và cấp đăng ký, biển số cho xe đã đăng ký tại Việt Nam không thuộc hai trường hợp trên (khoản 4 Điều 4 " + TT155
    + ").", u155("d4:k4"), u155("d4:k4:a"), u155("d4:k4:b"), u155("d4:k4:c"))

out = ROOT / "data/train/drafts/toc_do_bao_hiem_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
