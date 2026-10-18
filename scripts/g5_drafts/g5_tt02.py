"""Đợt 11e G5: thủ tục và quy tắc chưa có mẫu ở Luật 36/2024 (tai nạn, dừng xe kiểm tra, di chuyển xe đỗ sai, thu
hồi đăng ký), lệ phí trước bạ (NĐ 10/2022), lệ phí đăng ký xe (TT 155/2025), hồ sơ khám sức khỏe (TT 36/2024/TT-BYT) và
đấu giá biển số (NĐ 156/2024). Ghi data/train/drafts/thu_tuc_khac_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
S = []
NEXT = {"tn": 21, "lu": 95, "lp": 26, "gp": 161, "dk": 138}
TOPIC = {"tn": "Tai nạn", "lu": "Luật lõi", "lp": "Lệ phí", "gp": "GPLX", "dk": "Đăng ký xe"}


def l36(s):
    return f"luat_36_2024:{s}@2025-01-01"


def add(prefix, loai, q, a, *can_cu):
    S.append({"key": f"{prefix}-{NEXT[prefix]:04d}", "chu_de": TOPIC[prefix], "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})
    NEXT[prefix] += 1


# ===== Tai nạn giao thông (Luật 36 Điều 80, 81)
add("tn", "thu_tuc", "Gây tai nạn giao thông thì người lái xe phải làm những gì?",
    "Người gây tai nạn phải: dừng ngay phương tiện, cảnh báo nguy hiểm, giữ nguyên hiện trường, trợ giúp người bị nạn và báo "
    "tin cho cơ quan Công an, cơ sở khám bệnh, chữa bệnh hoặc Ủy ban nhân dân nơi gần nhất; ở lại hiện trường cho đến khi "
    "người của cơ quan Công an đến; cung cấp thông tin danh tính của mình, người liên quan và thông tin về vụ tai nạn cho cơ "
    "quan có thẩm quyền (khoản 1 Điều 80 " + LUAT + ").", l36("d80:k1:a"), l36("d80:k1:b"), l36("d80:k1:c"))
add("tn", "tinh_huong", "Tôi gây tai nạn và phải tự chở người bị nạn đi cấp cứu. Tôi rời hiện trường như vậy có sai không?",
    "Không sai. Người gây tai nạn được rời hiện trường khi phải đi cấp cứu, đưa người bị nạn đi cấp cứu hoặc bị đe dọa đến tính "
    "mạng, sức khỏe, nhưng phải đến trình báo ngay cơ quan Công an, Ủy ban nhân dân nơi gần nhất (điểm b khoản 1 Điều 80 " + LUAT
    + "). Chỉ được dùng chính phương tiện liên quan đến vụ tai nạn để chở nạn nhân khi không có phương tiện nào khác, và phải "
    "xác định vị trí phương tiện, vị trí nạn nhân tại hiện trường (khoản 3 Điều 80).", l36("d80:k1:b"), l36("d80:k3"))
add("tn", "thu_tuc", "Chứng kiến một vụ tai nạn giao thông thì tôi nên làm gì?",
    "Người có mặt tại nơi xảy ra tai nạn có trách nhiệm: giúp đỡ, cứu chữa kịp thời người bị nạn; báo tin ngay cho cơ quan "
    "Công an, cơ sở khám bệnh, chữa bệnh hoặc Ủy ban nhân dân nơi gần nhất; tham gia bảo vệ hiện trường và tài sản của người "
    "bị nạn; cung cấp thông tin về vụ tai nạn theo yêu cầu của cơ quan có thẩm quyền (khoản 2 Điều 80 " + LUAT + ").",
    l36("d80:k2:a"), l36("d80:k2:b"), l36("d80:k2:c"), l36("d80:k2:d"), l36("d80:k2:đ"))
add("tn", "thu_tuc", "Phát hiện tai nạn giao thông thì phải báo cho ai?",
    "Phải báo ngay cho cơ quan Công an, cơ sở khám bệnh, chữa bệnh hoặc Ủy ban nhân dân nơi gần nhất (khoản 1 Điều 81 " + LUAT
    + "). Ủy ban nhân dân nhận tin báo phải thông tin cho cơ quan Công an có thẩm quyền để giải quyết (khoản 4).",
    l36("d81:k1"), l36("d81:k4"))
add("tn", "quy_tac", "Đi ngang qua chỗ xảy ra tai nạn thì tôi có bắt buộc phải chở người bị thương đi cấp cứu không?",
    "Có. Người điều khiển phương tiện khác khi đi qua nơi xảy ra tai nạn có trách nhiệm chở người bị thương đi cấp cứu; chỉ xe "
    "ưu tiên và xe chở người được hưởng quyền ưu đãi, miễn trừ ngoại giao không bắt buộc (khoản 4 Điều 80 " + LUAT + ").",
    l36("d80:k4"))
add("tn", "quy_tac", "Người lái xe bị tai nạn được đưa vào viện thì bệnh viện có xét nghiệm nồng độ cồn không?",
    "Có. Cơ sở khám bệnh, chữa bệnh cấp cứu ban đầu người bị tai nạn phải báo ngay cho cơ quan Công an nơi gần nhất và xét "
    "nghiệm nồng độ cồn, chất ma túy hoặc chất kích thích khác trong máu của người điều khiển phương tiện; nơi không đủ điều kiện "
    "xét nghiệm thì lấy mẫu máu bảo quản và chuyển đến cơ sở xét nghiệm (khoản 3 Điều 81 " + LUAT + ").", l36("d81:k3"))
add("tn", "thu_tuc", "Xe có bảo hiểm bị tai nạn thì doanh nghiệp bảo hiểm có phải cử người đến hiện trường không?",
    "Có. Doanh nghiệp bảo hiểm khi nhận được tin báo phải cử người trực tiếp hoặc ủy quyền cho người đại diện đến hiện trường "
    "phối hợp với đơn vị giải quyết vụ tai nạn (khoản 5 Điều 81 " + LUAT + ").", l36("d81:k5"))
add("tn", "quy_tac", "Vụ tai nạn có người chết thì người có mặt phải làm gì với hiện trường?",
    "Phải giữ nguyên hiện trường và che đậy thi thể; không được làm thay đổi, mất dấu vết liên quan đến vụ tai nạn (khoản 3 "
    "Điều 80 " + LUAT + ").", l36("d80:k3"))

# ===== Dừng xe kiểm tra, quyền và trách nhiệm người lái, di chuyển xe đỗ sai (Luật 36 Điều 66, 69, 72)
add("lu", "doi_thuong", "csgt được dừng xe kiểm tra khi nào vậy",
    "Cảnh sát giao thông được dừng phương tiện để kiểm tra khi: phát hiện hoặc có căn cứ xác định có hành vi vi phạm; thực hiện "
    "mệnh lệnh, kế hoạch tuần tra, kiểm soát của cấp có thẩm quyền; phục vụ bảo vệ an ninh, trật tự, phòng, chống tội phạm, "
    "thiên tai, cháy nổ, dịch bệnh; hoặc có tin báo, tố giác, phản ánh về tội phạm, vi phạm pháp luật (Điều 66 " + LUAT + ").",
    l36("d66:k1"), l36("d66:k2"), l36("d66:k3"), l36("d66:k4"))
add("lu", "quy_tac", "Bị cảnh sát giao thông dừng xe kiểm tra thì tôi có những quyền gì?",
    "Người lái được thông báo căn cứ dừng xe, nội dung và kết quả kiểm tra, hành vi vi phạm và biện pháp xử lý; được giải "
    "trình, khiếu nại, khởi kiện quyết định hành chính, hành vi hành chính liên quan; được tố cáo hành vi vi phạm pháp luật "
    "trong hoạt động tuần tra, kiểm soát (khoản 1 Điều 72 " + LUAT + ").", l36("d72:k1:b"), l36("d72:k1:c"), l36("d72:k1:d"))
add("lu", "quy_tac", "Khi bị dừng xe kiểm tra, người lái có trách nhiệm gì?",
    "Phải chấp hành pháp luật về trật tự, an toàn giao thông; chấp hành hiệu lệnh dừng phương tiện và yêu cầu kiểm tra, kiểm "
    "soát của lực lượng tuần tra; hỗ trợ, hợp tác với lực lượng bảo đảm trật tự, an toàn giao thông khi phát hiện, ngăn chặn, "
    "xử lý vi phạm (khoản 2 Điều 72 " + LUAT + ").", l36("d72:k2:a"), l36("d72:k2:b"), l36("d72:k2:c"))
add("lu", "tinh_huong", "Tôi đỗ xe sai chỗ gây ùn tắc, lúc quay lại thì xe đã bị cảnh sát cho kéo đi. Tôi có phải trả tiền kéo xe không?",
    "Có. Khi xe dừng, đỗ sai gây cản trở, ùn tắc hoặc nguy cơ tai nạn mà người lái, chủ xe không có mặt (hoặc có mặt nhưng "
    "không chấp hành), Cảnh sát giao thông di chuyển xe hoặc thuê tổ chức, cá nhân di chuyển (khoản 1 Điều 69 " + LUAT + "); "
    "người lái hoặc chủ xe vi phạm phải trả chi phí di chuyển (khoản 3). Bên di chuyển phải bảo đảm an toàn cho xe (khoản 4).",
    l36("d69:k1"), l36("d69:k3"), l36("d69:k4"))
add("dk", "quy_tac", "Theo Luật, khi nào phải thu hồi giấy đăng ký và biển số xe?",
    "Một số trường hợp: chuyển quyền sở hữu xe (xe gắn biển trúng đấu giá thì chỉ thu hồi chứng nhận đăng ký); xe cơ giới hết "
    "niên hạn sử dụng, hư hỏng không sử dụng được; xe bị thải bỏ, bị mất không tìm được và chủ xe đề nghị thu hồi; hồ sơ xe bị "
    "làm giả hoặc thay đổi trái phép số khung, số máy; cấp đăng ký, biển số không đúng quy định (khoản 6 Điều 39 " + LUAT + ").",
    l36("d39:k6:a"), l36("d39:k6:c"), l36("d39:k6:d"), l36("d39:k6:đ"), l36("d39:k6:e"))

# ===== Lệ phí trước bạ, lệ phí đăng ký xe (NĐ 10/2022, TT 155/2025)
add("lp", "thu_tuc", "Khai, nộp lệ phí trước bạ xe vào lúc nào?",
    "Người có tài sản thuộc đối tượng chịu lệ phí trước bạ phải nộp khi đăng ký quyền sở hữu, quyền sử dụng với cơ quan nhà "
    "nước có thẩm quyền, trừ trường hợp được miễn (Điều 4 Nghị định 10/2022/NĐ-CP); việc khai, nộp thực hiện theo pháp luật về "
    "quản lý thuế (khoản 1 Điều 11).", "nd_10_2022:d4@2022-03-01", "nd_10_2022:d11:k1@2022-03-01")
add("lp", "thu_tuc", "Nộp lệ phí trước bạ online rồi thì đi đăng ký xe có cần mang biên lai giấy không?",
    "Không cần. Dữ liệu điện tử nộp lệ phí trước bạ qua Kho bạc Nhà nước, ngân hàng thương mại hoặc tổ chức trung gian thanh "
    "toán được Cục Thuế ký số và cung cấp lên Cổng dịch vụ công có giá trị như chứng từ bản giấy để cơ quan cảnh sát giao thông "
    "khai thác khi giải quyết thủ tục (khoản 2 Điều 11 Nghị định 10/2022/NĐ-CP). Khi đăng ký xe, chứng từ nộp lệ phí trước bạ "
    "có thể là dữ liệu điện tử mà hệ thống đăng ký xe tiếp nhận từ cơ quan thuế (khoản 1 Điều 13 Thông tư 79/2024/TT-BCA).",
    "nd_10_2022:d11:k2@2025-07-01", "tt_79_2024_bca:d13:k1@2025-01-01")
add("lp", "thu_tuc", "Ai phải nộp lệ phí cấp đăng ký, biển số xe và nộp cho ai?",
    "Tổ chức, cá nhân được cấp chứng nhận đăng ký xe và biển số xe cơ giới phải nộp lệ phí (Điều 2 Thông tư 155/2025/TT-BTC); "
    "tổ chức thu là cơ quan nhà nước có thẩm quyền cấp chứng nhận đăng ký xe, biển số xe (Điều 3), và người nộp nộp tiền cho "
    "tổ chức thu theo Nghị định 362/2025/NĐ-CP (khoản 1 Điều 7).",
    "tt_155_2025_btc:d2@2026-01-01", "tt_155_2025_btc:d3@2026-01-01", "tt_155_2025_btc:d7:k1@2026-01-01")

# ===== Hồ sơ khám sức khỏe lái xe (TT 36/2024/TT-BYT)
add("gp", "thu_tuc", "Đi khám sức khỏe để thi bằng lái thì hồ sơ khám theo mẫu nào, chi phí tính thế nào?",
    "Hồ sơ khám sức khỏe của người lái xe theo mẫu Phụ lục II Thông tư 36/2024/TT-BYT (khoản 1 Điều 4); người hành nghề lái xe "
    "ô tô khám định kỳ theo mẫu tại điểm a khoản 4 Điều 34 Thông tư 32/2023/TT-BYT, có bổ sung hạng giấy phép lái xe vào mục 7 "
    "(nghề nghiệp) (khoản 2 Điều 4). Chi phí khám thực hiện theo Điều 33 Thông tư 32/2023/TT-BYT (Điều 6).",
    "tt_36_2024_byt:d4:k1@2025-01-01", "tt_36_2024_byt:d4:k2:a@2025-01-01", "tt_36_2024_byt:d4:k2:b@2025-01-01",
    "tt_36_2024_byt:d6@2025-01-01")

# ===== Đấu giá biển số (NĐ 156/2024 Điều 7, 16, 18)
add("dk", "thu_tuc", "Tiền đặt trước khi đấu giá biển số là bao nhiêu và phải nộp trước khi nào?",
    "Tiền đặt trước bằng giá khởi điểm của biển số đưa ra đấu giá, gửi vào tài khoản thanh toán riêng của tổ chức hành nghề đấu "
    "giá tài sản từ ngày niêm yết đến trước ngày mở cuộc đấu giá 02 ngày; nếu trúng đấu giá thì tiền đặt trước được chuyển vào "
    "tài khoản chuyên thu của Bộ Công an để nộp ngân sách (khoản 1 Điều 7 Nghị định 156/2024/NĐ-CP).",
    "nd_156_2024:d7:k1@2025-01-01")
add("dk", "quy_tac", "Mỗi lần trả giá khi đấu giá biển số phải tăng ít nhất bao nhiêu?",
    "Bước giá đối với biển số xe ô tô là 5 (năm) triệu đồng; đối với biển số xe mô tô, xe gắn máy là 500 (năm trăm) nghìn đồng "
    "(khoản 2 Điều 7 Nghị định 156/2024/NĐ-CP).", "nd_156_2024:d7:k2@2025-01-01")
add("dk", "thu_tuc", "Kết quả đấu giá biển số được công bố khi nào?",
    "Trong thời hạn 01 ngày làm việc kể từ ngày kết thúc đấu giá, tổ chức hành nghề đấu giá phải công khai niêm yết kết quả trên "
    "Trang thông tin đấu giá trực tuyến; trong 03 ngày làm việc phải chuyển kết quả, biên bản, danh sách người trúng và tiền đặt "
    "trước cho Bộ Công an để phê duyệt (Điều 16 Nghị định 156/2024/NĐ-CP).",
    "nd_156_2024:d16:k1@2025-01-01", "nd_156_2024:d16:k2@2025-01-01")
add("dk", "thu_tuc", "Trúng đấu giá biển số thì tôi được thông báo bằng cách nào?",
    "Trong vòng 07 ngày làm việc sau khi phê duyệt kết quả, Bộ Công an gửi văn bản điện tử Thông báo kết quả trúng đấu giá vào "
    "địa chỉ thư điện tử và nhắn tin tới số điện thoại đã đăng ký tại tài khoản; thông báo này thay thế hợp đồng mua bán tài sản "
    "đấu giá (khoản 1 Điều 18 Nghị định 156/2024/NĐ-CP). Thông báo ghi biển số trúng, giá trúng, số tiền phải nộp, tài khoản "
    "và thời hạn nộp tiền (khoản 2).", "nd_156_2024:d18:k1@2025-01-01", "nd_156_2024:d18:k2@2025-01-01")

out = ROOT / "data/train/drafts/thu_tuc_khac_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
