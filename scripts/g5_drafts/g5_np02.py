"""Đợt 11d G5: thủ tục xử phạt, nộp phạt, tạm giữ (Luật XLVPHC hợp nhất VBHN 90/2026, NĐ 138/2021) và giấy phép kinh
doanh vận tải, phù hiệu (NĐ 158/2024) ở các Điều chưa có mẫu thủ tục. Ghi data/train/drafts/nop_phat_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Xử lý vi phạm hành chính"
ND138 = "Nghị định 138/2021/NĐ-CP"
ND158 = "Nghị định 158/2024/NĐ-CP"
S = []
NEXT = {"np": 48, "hd": 37}


def v(s):
    return f"vbhn_90_2026_xlvphc:{s}@2026-07-01"


def n138(s, d="2022-01-01"):
    return f"nd_138_2021:{s}@{d}"


def n158(s, d="2026-08-10"):
    return f"nd_158_2024:{s}@{d}"


def add(prefix, chu_de, loai, q, a, *can_cu):
    S.append({"key": f"{prefix}-{NEXT[prefix]:04d}", "chu_de": chu_de, "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})
    NEXT[prefix] += 1


def np(loai, q, a, *can_cu):
    add("np", "Nộp phạt, giữ xe", loai, q, a, *can_cu)


def hd(loai, q, a, *can_cu):
    add("hd", "Hướng dẫn", loai, q, a, *can_cu)


# ===== Hồ sơ xử phạt, giải trình (Điều 57, 61)
np("thu_tuc", "Hồ sơ xử phạt vi phạm hành chính có lập biên bản gồm những gì?",
   "Người có thẩm quyền xử phạt phải lập hồ sơ gồm biên bản vi phạm hành chính, quyết định xử phạt hành chính, các tài "
   "liệu, giấy tờ có liên quan; hồ sơ phải được đánh bút lục và lưu trữ theo pháp luật về lưu trữ (khoản 2 Điều 57 " + LUAT
   + ").", v("d57:k2"))
np("thu_tuc", "Bị lập biên bản vi phạm giao thông mức phạt cao thì tôi có quyền giải trình không?",
   "Có, nếu hành vi đó có hình thức tước quyền sử dụng giấy phép, chứng chỉ hành nghề có thời hạn hoặc mức tối đa của "
   "khung tiền phạt từ 15.000.000 đồng trở lên đối với cá nhân (từ 30.000.000 đồng trở lên đối với tổ chức). Người vi phạm "
   "được giải trình trực tiếp hoặc bằng văn bản, và người có thẩm quyền phải xem xét ý kiến giải trình trước khi ra quyết "
   "định xử phạt (khoản 1 Điều 61 " + LUAT + ").", v("d61:k1"))
np("thu_tuc", "Muốn giải trình bằng văn bản về lỗi vi phạm thì phải gửi trong bao lâu?",
   "Gửi văn bản giải trình cho người có thẩm quyền xử phạt trong thời hạn 05 ngày làm việc kể từ ngày lập biên bản vi "
   "phạm; vụ việc phức tạp thì có thể được gia hạn bằng văn bản nhưng không quá 05 ngày làm việc theo đề nghị của người vi "
   "phạm. Người vi phạm tự mình hoặc ủy quyền cho người đại diện hợp pháp giải trình (khoản 2 Điều 61 " + LUAT + ").",
   v("d61:k2"))
np("thu_tuc", "Muốn giải trình trực tiếp với người xử phạt thì làm thế nào?",
   "Gửi văn bản yêu cầu được giải trình trực tiếp đến người có thẩm quyền xử phạt trong thời hạn 02 ngày làm việc kể từ "
   "ngày lập biên bản. Người có thẩm quyền phải thông báo bằng văn bản thời gian, địa điểm phiên giải trình trong thời hạn 05 "
   "ngày làm việc kể từ ngày nhận được yêu cầu, rồi tổ chức phiên giải trình trực tiếp (khoản 3 Điều 61 " + LUAT + ").",
   v("d61:k3"))
np("tinh_huong", "Lúc lập biên bản tôi không yêu cầu giải trình, vài hôm sau đổi ý thì còn được không?",
   "Còn được, nếu bạn yêu cầu trước khi hết thời hạn giải trình (05 ngày làm việc nếu giải trình bằng văn bản, 02 ngày làm "
   "việc nếu yêu cầu giải trình trực tiếp, kể từ ngày lập biên bản); khi đó người có thẩm quyền phải xem xét ý kiến giải "
   "trình (khoản 4 Điều 61 " + LUAT + ").", v("d61:k4"), v("d61:k2"), v("d61:k3"))

# ===== Phạt nguội bằng thiết bị (Điều 64)
np("thu_tuc", "Bị camera giao thông ghi hình vi phạm thì việc xử phạt diễn ra thế nào?",
   "Khi có kết quả thu được bằng phương tiện, thiết bị kỹ thuật nghiệp vụ, người có thẩm quyền phải nhanh chóng xác định "
   "người vi phạm và thông báo bằng văn bản; xác định được người vi phạm thì lập biên bản vi phạm hành chính theo Điều 58, "
   "kết quả ghi hình được lưu theo biên bản (điểm c khoản 3 Điều 64 " + LUAT + "). Kết quả đó là bản ảnh, hình ảnh, phiếu "
   "in, chỉ số đo, dữ liệu lưu trong bộ nhớ thiết bị (điểm a).", v("d64:k3:c"), v("d64:k3:a"))
np("quy_tac", "Hình ảnh camera phạt nguội phải bảo đảm điều kiện gì mới được dùng để xử phạt?",
   "Thiết bị phải đúng tiêu chuẩn, quy chuẩn kỹ thuật và đã được kiểm định, hiệu chuẩn, thử nghiệm theo quy định; kết quả "
   "thu được phải được ghi nhận bằng văn bản và chỉ được dùng trong xử phạt vi phạm hành chính (điểm c, điểm d khoản 2 Điều "
   "64 " + LUAT + "). Kết quả chỉ được dùng để xử phạt khi bảo đảm các điều kiện đó (điểm b khoản 3).",
   v("d64:k2:c"), v("d64:k2:d"), v("d64:k3:b"))

# ===== Nộp phạt tại chỗ, tước giấy phép, cưỡng chế (Điều 69, 80, 86)
np("thu_tuc", "Bị phạt tại chỗ không lập biên bản thì nộp tiền thế nào, có được giấy tờ gì không?",
   "Người bị phạt được giao 01 bản quyết định xử phạt (khoản 1 Điều 69 " + LUAT + ") và nộp tiền phạt tại chỗ cho người có "
   "thẩm quyền xử phạt; người thu tiền phải giao chứng từ thu tiền phạt. Không có khả năng nộp tại chỗ thì nộp tại Kho bạc "
   "Nhà nước hoặc vào tài khoản Kho bạc Nhà nước ghi trong quyết định trong thời hạn tại khoản 1 Điều 78 (khoản 2 Điều 69).",
   v("d69:k1"), v("d69:k2"))
np("thu_tuc", "Bị tước quyền sử dụng giấy phép có thời hạn thì khi nào được nhận lại?",
   "Người có thẩm quyền xử phạt thu giữ, bảo quản giấy phép và thông báo ngay cho cơ quan đã cấp; khi hết thời hạn tước "
   "ghi trong quyết định xử phạt thì giao lại giấy phép cho người đã bị tước (khoản 1 Điều 80 " + LUAT + ").", v("d80:k1"))
np("thu_tuc", "Không tự nguyện nộp phạt thì bị cưỡng chế bằng những biện pháp nào?",
   "Người bị xử phạt không tự nguyện chấp hành quyết định thì bị cưỡng chế (điểm a khoản 1 Điều 86 " + LUAT + "), bằng các "
   "biện pháp: khấu trừ một phần lương, thu nhập hoặc khấu trừ tiền từ tài khoản; kê biên tài sản có giá trị tương ứng với "
   "số tiền phạt để bán đấu giá; thu tiền, tài sản khác do người khác đang giữ nếu người vi phạm cố tình tẩu tán tài sản "
   "(khoản 2 Điều 86).", v("d86:k1:a"), v("d86:k2:a"), v("d86:k2:b"), v("d86:k2:c"))

# ===== Tạm giữ, quản lý xe bị tạm giữ (Điều 125 Luật; Điều 12, 17 NĐ 138)
np("thu_tuc", "Cảnh sát tạm giữ xe ngay lúc lập biên bản vi phạm thì có phải lập thêm biên bản tạm giữ không?",
   "Không. Nếu người lập biên bản vi phạm thực hiện tạm giữ cùng thời điểm lập biên bản thì không phải lập biên bản tạm giữ, "
   "nhưng biên bản vi phạm phải thể hiện rõ tên, số lượng, chủng loại, tình trạng của phương tiện, giấy tờ bị tạm giữ "
   "(điểm b khoản 4 Điều 125 " + LUAT + "). Các trường hợp khác thì lập biên bản tạm giữ theo khoản 9 Điều 125 (điểm a).",
   v("d125:k4:b"), v("d125:k4:a"))
np("thu_tuc", "Hết thời hạn tạm giữ mà tôi chưa đến nhận xe thì xe được quản lý thế nào?",
   "Người ra quyết định tạm giữ tiếp tục tổ chức quản lý, bảo quản phương tiện khi đã hết thời hạn tạm giữ mà người có xe "
   "không đến nhận hoặc không xác định được người vi phạm, kể cả trong thời gian thông báo trên phương tiện thông tin đại "
   "chúng, cho đến khi xe bị tịch thu, xử lý theo quy định (khoản 2 Điều 17 " + ND138 + "). Việc xử lý xe hết thời hạn tạm "
   "giữ theo các khoản 4, 4a, 4b Điều 126 " + LUAT + " (khoản 1 Điều 17).",
   n138("d17:k2", "2026-03-15"), n138("d17:k1", "2026-03-15"))
np("thu_tuc", "Khi xe bị đưa vào nơi tạm giữ, người quản lý kiểm tra những gì?",
   "Người quản lý, bảo quản kiểm tra quyết định tạm giữ, biên bản tạm giữ và giấy tờ liên quan; so sánh, đối chiếu phương "
   "tiện với biên bản tạm giữ và bản thống kê (chủng loại, nhãn hiệu, tình trạng niêm phong nếu có); vào sổ theo dõi và yêu "
   "cầu bên giao ký vào sổ (Điều 12 " + ND138 + ").", n138("d12:k1"), n138("d12:k2"), n138("d12:k3"))

# ===== Giấy phép kinh doanh vận tải (NĐ 158/2024 Điều 19–21)
hd("thu_tuc", "Xin giấy phép kinh doanh vận tải bằng ô tô nộp ở đâu và bao lâu có?",
   "Đơn vị kinh doanh vận tải nộp 01 bộ hồ sơ đến Sở Xây dựng nơi đặt trụ sở chính hoặc trụ sở chi nhánh, theo hình thức "
   "trực tiếp, trực tuyến hoặc dịch vụ bưu chính; hồ sơ cần bổ sung thì được thông báo trong 03 ngày làm việc. Trong thời "
   "hạn 04 ngày làm việc kể từ ngày nhận đủ hồ sơ đúng quy định, Sở Xây dựng thẩm định và cấp giấy phép; không cấp thì trả "
   "lời bằng văn bản nêu rõ lý do (khoản 1 Điều 21 " + ND158 + ").", n158("d21:k1:a"), n158("d21:k1:b"), n158("d19:k2"))
hd("thu_tuc", "Hồ sơ đề nghị cấp giấy phép kinh doanh vận tải bằng ô tô gồm những gì?",
   "Gồm: giấy đề nghị cấp giấy phép theo mẫu Phụ lục I; văn bằng, chứng chỉ của người trực tiếp điều hành vận tải, hoặc tài "
   "liệu chứng minh kinh nghiệm làm việc tại đơn vị kinh doanh vận tải tối thiểu từ 03 năm trở lên tùy trường hợp; quyết định "
   "thành lập và quy định chức năng, nhiệm vụ bộ phận quản lý an toàn; quyết định giao nhiệm vụ cho người trực tiếp điều hành "
   "hoạt động vận tải (khoản 1 Điều 20 " + ND158 + ").",
   n158("d20:k1:a"), n158("d20:k1:b"), n158("d20:k1:c"), n158("d20:k1:d"))
hd("thu_tuc", "Doanh nghiệp đổi địa chỉ thì xin cấp lại giấy phép kinh doanh vận tải cần những gì?",
   "Hồ sơ cấp lại do thay đổi nội dung giấy phép gồm giấy đề nghị cấp lại nêu rõ lý do theo mẫu Phụ lục I và tài liệu chứng "
   "minh sự thay đổi của nội dung đó (khoản 2 Điều 20 " + ND158 + "); thủ tục thực hiện như cấp mới tại khoản 1 Điều 21 "
   "(khoản 2 Điều 21).", n158("d20:k2:a"), n158("d20:k2:b", "2025-01-01"), n158("d21:k2", "2025-01-01"))
hd("quy_tac", "Những trường hợp nào bị thu hồi giấy phép kinh doanh vận tải?",
   "Một số trường hợp: cung cấp bản sao không đúng bản chính hoặc thông tin sai lệch trong hồ sơ; không kinh doanh hoặc ngừng "
   "kinh doanh toàn bộ các loại hình trong 06 tháng trở lên; sửa chữa, làm sai lệch dữ liệu thiết bị giám sát hành trình, "
   "camera người lái; trong 01 tháng có từ 30% trở lên số phương tiện bị thu hồi, bị tước phù hiệu; trong 01 năm có từ 02 "
   "lần trở lên bị tước quyền sử dụng giấy phép (khoản 6 Điều 21 " + ND158 + ").",
   n158("d21:k6:a", "2025-01-01"), n158("d21:k6:b", "2025-01-01"), n158("d21:k6:d", "2025-01-01"),
   n158("d21:k6:e", "2025-01-01"), n158("d21:k6:g", "2025-01-01"))
hd("thu_tuc", "Bị thu hồi giấy phép kinh doanh vận tải thì bao lâu mới xin cấp lại được?",
   "Trong thời hạn 10 ngày kể từ ngày ký quyết định thu hồi, đơn vị phải dừng kinh doanh loại hình vi phạm; trong 30 ngày kể "
   "từ ngày ký, Sở Xây dựng không cấp lại giấy phép. Sau thời hạn đó, muốn tiếp tục kinh doanh thì làm thủ tục cấp giấy phép "
   "và phù hiệu theo khoản 1 Điều 21 và khoản 6 Điều 23 (điểm d khoản 7 Điều 21 " + ND158 + "), kèm tài liệu chứng minh đã "
   "khắc phục vi phạm (điểm b khoản 4 Điều 20).", n158("d21:k7:d"), n158("d20:k4:b", "2025-01-01"))

# ===== Phù hiệu (NĐ 158/2024 Điều 23)
hd("thu_tuc", "Hồ sơ đề nghị cấp phù hiệu cho xe kinh doanh vận tải gồm những gì?",
   "Gồm giấy đề nghị cấp phù hiệu theo mẫu Phụ lục V; nếu xe không thuộc sở hữu của đơn vị thì xuất trình thêm hợp đồng thuê "
   "phương tiện, hợp đồng dịch vụ giữa thành viên và hợp tác xã, hợp đồng hợp tác kinh doanh hoặc hợp đồng cho thuê tài chính "
   "(khoản 5 Điều 23 " + ND158 + ").", n158("d23:k5:a"), n158("d23:k5:b"))
hd("thu_tuc", "Nộp hồ sơ cấp phù hiệu xe ở đâu?",
   "Đơn vị kinh doanh vận tải gửi 01 bộ hồ sơ (trực tuyến, trực tiếp hoặc dịch vụ bưu chính) đến Sở Xây dựng nơi đã cấp giấy "
   "phép kinh doanh cho đơn vị; hồ sơ cần bổ sung thì được thông báo trong 01 ngày làm việc (điểm a khoản 6 Điều 23 " + ND158
   + ").", n158("d23:k6:a"))
hd("thu_tuc", "Phù hiệu xe bị thu hồi thì bao lâu được xin cấp lại?",
   "Sở Xây dựng không cấp mới, cấp lại phù hiệu cho xe trong thời gian bị tước quyền sử dụng hoặc trong 30 ngày kể từ ngày ký "
   "quyết định thu hồi phù hiệu (điểm b khoản 9 Điều 23 " + ND158 + "). Hết thời hạn đó, nếu muốn tiếp tục dùng xe kinh "
   "doanh thì đơn vị làm thủ tục cấp lại theo khoản 5, khoản 6 Điều 23 (khoản 8).", n158("d23:k9:b"), n158("d23:k8", "2025-01-01"))
hd("thu_tuc", "Bán xe đang chạy kinh doanh vận tải thì đơn vị phải làm gì với phù hiệu?",
   "Trong 10 ngày kể từ ngày ngừng sử dụng xe để kinh doanh (chuyển nhượng, cho đơn vị khác thuê hoặc ngừng kinh doanh), "
   "đơn vị phải gửi báo cáo bằng văn bản về Sở Xây dựng nơi cấp, đồng thời gỡ bỏ phù hiệu đang dán trên xe (điểm c khoản 12 "
   "Điều 23 " + ND158 + ").", n158("d23:k12:c"))
hd("thu_tuc", "Có quyết định thu hồi phù hiệu thì bao lâu đơn vị phải dừng chạy xe đó?",
   "Trong thời hạn 10 ngày kể từ ngày ký quyết định thu hồi, đơn vị kinh doanh vận tải phải dừng hoạt động kinh doanh vận "
   "tải đối với xe bị thu hồi phù hiệu (điểm c khoản 11 Điều 23 " + ND158 + ").", n158("d23:k11:c"))
hd("quy_tac", "Xe chạy tuyến cố định bị thu hồi phù hiệu trong trường hợp nào?",
   "Bị thu hồi khi đơn vị không hoạt động kinh doanh vận tải trên tuyến trong thời gian 60 ngày liên tục (điểm b khoản 10 Điều "
   "23 " + ND158 + "); ngoài ra, mọi xe của đơn vị bị thu hồi phù hiệu khi đơn vị bị tước quyền sử dụng giấy phép kinh doanh "
   "vận tải (điểm a).", n158("d23:k10:b", "2025-01-01"), n158("d23:k10:a", "2025-01-01"))

out = ROOT / "data/train/drafts/nop_phat_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
