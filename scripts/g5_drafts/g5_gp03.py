"""Đợt 2c G5: điểm GPLX (NĐ 168 Điều 49–51), đào tạo lái xe (NĐ 94/2026), đối tượng xử phạt và phạt nguội (NĐ 168 Điều
47), giấy tờ và tạm giữ xe (NĐ 168 Điều 48). Ghi data/train/drafts/gplx_03.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
ND94 = "Nghị định 94/2026/NĐ-CP"
NEW = "2026-08-15"
S = []
START = 104


def v(s, d="2025-01-01"):
    return f"nd_168_2024:{s}@{d}"


def n94(s):
    return f"nd_94_2026:{s}@2026-07-01"


def add(chu_de, loai, q, a, *can_cu):
    S.append({"key": f"gp-{START + len(S):04d}", "chu_de": chu_de, "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


G, X, P = "GPLX", "Xử phạt", "Nộp phạt, giữ xe"

# ===== Điểm GPLX: trừ điểm, phục hồi điểm (NĐ 168 Điều 49–51)
add(G, "quy_tac", "Dữ liệu điểm và trừ điểm giấy phép lái xe được lưu ở đâu?",
    "Dữ liệu về điểm, trừ điểm, phục hồi điểm giấy phép lái xe được quản lý, lưu trữ trên môi trường điện tử, trong Cơ sở "
    "dữ liệu về xử lý vi phạm hành chính về trật tự, an toàn giao thông đường bộ do Bộ Công an xây dựng, quản lý, vận "
    "hành (Điều 49 " + ND + ").", v("d49"))
add(G, "quy_tac", "Bị lập biên bản thì bằng lái bị trừ điểm ngay lúc đó hay khi nào?",
    "Việc trừ điểm giấy phép lái xe được thực hiện ngay sau khi quyết định xử phạt vi phạm hành chính đối với hành vi có "
    "quy định trừ điểm có hiệu lực thi hành (điểm a khoản 1 Điều 50 " + ND + "), không phải lúc lập biên bản.",
    v("d50:k1:a"), v("d50:k1"))
add(G, "tinh_huong", "Trong một lần bị xử phạt, tôi có hai lỗi đều bị trừ điểm bằng lái. Tôi bị trừ cộng dồn cả hai lỗi "
    "không?",
    "Không. Trường hợp cá nhân có nhiều hành vi vi phạm hoặc vi phạm nhiều lần mà bị xử phạt trong cùng một lần, nếu có "
    "từ 02 hành vi trở lên bị trừ điểm thì chỉ áp dụng trừ điểm đối với hành vi bị trừ nhiều điểm nhất (điểm b khoản 1 "
    "Điều 50 " + ND + ").", v("d50:k1:b"), v("d50:k1"))
add(G, "tinh_huong", "Bằng lái của tôi chỉ còn ít điểm, nhưng lỗi mới bị trừ nhiều điểm hơn số điểm còn lại. Thì sao?",
    "Trường hợp số điểm còn lại của giấy phép lái xe ít hơn số điểm bị trừ thì trừ hết số điểm còn lại của giấy phép lái "
    "xe đó (điểm c khoản 1 Điều 50 " + ND + "). Khi bằng bị trừ hết điểm, bạn không được lái xe theo bằng đó cho tới khi "
    "được phục hồi điểm.", v("d50:k1:c"), v("d50:k1"))
add(G, "quy_tac", "Bằng lái tích hợp cả xe máy và ô tô, khi đi xe máy vi phạm thì bị trừ điểm vào bằng nào?",
    "Với giấy phép lái xe tích hợp giấy phép không thời hạn (xe mô tô) và giấy phép có thời hạn (xe ô tô), người có thẩm "
    "quyền trừ điểm vào giấy phép không thời hạn khi người vi phạm điều khiển xe mô tô, và trừ điểm vào giấy phép có thời "
    "hạn khi điều khiển xe ô tô, xe chở người, chở hàng bốn bánh có gắn động cơ (điểm d khoản 1 Điều 50 " + ND + ").",
    v("d50:k1:d"), v("d50:k1"))
add(G, "quy_tac", "Đang trong thời gian bị tước bằng lái mà vi phạm tiếp thì có bị trừ điểm bằng đó không?",
    "Không. Theo điểm đ khoản 1 Điều 50 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), không trừ điểm giấy phép lái "
    "xe khi giấy phép lái xe đó đang trong thời hạn bị tước quyền sử dụng.", v("d50:k1:đ", NEW), v("d50:k1"))
add(G, "thu_tuc", "Bị trừ điểm bằng lái thì tôi được thông báo bằng cách nào?",
    "Ngay sau khi quyết định xử phạt có hiệu lực, dữ liệu trừ điểm được cập nhật tự động vào Cơ sở dữ liệu và người có "
    "thẩm quyền thông báo cho người bị trừ điểm (điểm a khoản 3 Điều 50, nội dung có hiệu lực từ ngày 15/8/2026). Thông "
    "báo bằng văn bản giao trực tiếp, gửi qua bưu chính hoặc qua tài khoản trên Cổng dịch vụ công, Ứng dụng giao thông "
    "trên thiết bị di động; nếu là giấy phép lái xe điện tử thì trạng thái trừ điểm được cập nhật trong tài khoản định "
    "danh điện tử (điểm b khoản 3 Điều 50 " + ND + ").", v("d50:k3:a", NEW), v("d50:k3:b"))
add(G, "quy_tac", "Ai có thẩm quyền trừ điểm giấy phép lái xe theo Nghị định 168?",
    "Người có thẩm quyền áp dụng hình thức tước quyền sử dụng giấy phép, chứng chỉ hành nghề có thời hạn hoặc đình chỉ "
    "hoạt động có thời hạn, và có thẩm quyền xử phạt đối với hành vi có quy định trừ điểm, thì có thẩm quyền trừ điểm giấy "
    "phép lái xe đối với hành vi đó (khoản 2 Điều 50 " + ND + ").", v("d50:k2"))
add(G, "doi_thuong", "điểm bằng lái tự hồi lại hay phải đi làm thủ tục",
    "Nếu bằng chưa bị trừ hết điểm thì tự động phục hồi: khi đủ 12 tháng kể từ ngày bị trừ điểm gần nhất (mà không bị trừ "
    "thêm), dữ liệu điểm tự động phục hồi đủ 12 điểm và được cập nhật trong Cơ sở dữ liệu, không cần làm thủ tục (điểm a "
    "khoản 2 Điều 51 " + ND + "). Nếu bằng đã bị trừ hết điểm thì phải đi kiểm tra kiến thức pháp luật và đạt yêu cầu "
    "mới được phục hồi (khoản 3 Điều 51).", v("d51:k2:a"), v("d51:k3:a"))
add(G, "tinh_huong", "Bằng lái của tôi đang bị tước quyền sử dụng. Đủ 12 tháng kể từ lần bị trừ điểm gần nhất thì điểm có "
    "được phục hồi không?",
    "Có. Khi đủ 12 tháng kể từ ngày bị trừ điểm gần nhất, dữ liệu điểm giấy phép lái xe được tự động phục hồi đủ 12 điểm, "
    "kể cả giấy phép lái xe đang trong thời hạn bị tước quyền sử dụng (điểm a khoản 2 Điều 51 " + ND + "). Điều kiện là "
    "giấy phép chưa bị trừ hết điểm.", v("d51:k2:a"), v("d51:k2"))
add(G, "thu_tuc", "Điểm bằng lái được phục hồi thì tôi có được báo không?",
    "Có. Ngay sau khi điểm được phục hồi, Cơ sở dữ liệu tự động gửi thông báo cho người được phục hồi điểm bằng phương "
    "thức điện tử qua tài khoản trên Cổng dịch vụ công, Ứng dụng giao thông trên thiết bị di động; thông tin cũng được cập "
    "nhật trên Trang thông tin điện tử của Cục Cảnh sát giao thông (điểm b, điểm c khoản 2 Điều 51 " + ND + ").",
    v("d51:k2:b"), v("d51:k2:c"))
add(G, "quy_tac", "Bằng bị trừ hết điểm, sau khi thi kiểm tra đạt thì ai phục hồi điểm?",
    "Cục trưởng Cục Cảnh sát giao thông, Trưởng phòng Cảnh sát giao thông nơi tổ chức kiểm tra kiến thức pháp luật có "
    "thẩm quyền phục hồi điểm (điểm b khoản 1 Điều 51 " + ND + "). Kết quả kiểm tra đạt yêu cầu được đồng bộ vào Cơ sở dữ "
    "liệu và điểm được phục hồi đủ 12 điểm (điểm a khoản 3 Điều 51).", v("d51:k1:b"), v("d51:k3:a"))

# ===== Đào tạo lái xe (NĐ 94/2026)
add(G, "quy_tac", "Học bằng lái xe máy A1 có được tự học phần lý thuyết không?",
    "Được. Hình thức tự học áp dụng đối với các môn lý thuyết để cấp giấy phép lái xe các hạng A1, A và B1; người học phải "
    "đăng ký tại cơ sở được phép đào tạo để được quản lý theo quy định của Bộ Xây dựng (Điều 4 " + ND94 + ").",
    n94("d4:k1"), n94("d4:k2"))
add(G, "doi_thuong", "học bằng B có học lý thuyết online được ko",
    "Được với phần lý thuyết. Theo khoản 1 Điều 5 " + ND94 + ", đào tạo từ xa, tự học có hướng dẫn áp dụng cho các môn "
    "pháp luật giao thông đường bộ, đạo đức, văn hóa giao thông và phòng chống tác hại của rượu, bia, cùng phần lý thuyết "
    "của các môn cấu tạo và sửa chữa thông thường; kỹ năng phòng cháy, chữa cháy và cứu nạn, cứu hộ; kỹ thuật lái xe, để "
    "cấp giấy phép lái xe hạng B trở lên. Người học vẫn phải đăng ký tại cơ sở được phép đào tạo (khoản 2 Điều 5).",
    n94("d5:k1"), n94("d5:k2"))
add(G, "quy_tac", "Đào tạo từ xa, tự học có hướng dẫn trong đào tạo lái xe là gì?",
    "Là hình thức đào tạo không tập trung, người học chủ yếu tự học qua các học liệu (giáo trình, băng hình, ứng dụng đa "
    "phương tiện trên thiết bị điện tử, mạng Internet…) dưới sự tổ chức, trợ giúp của giáo viên, cơ sở đào tạo lái xe "
    "(khoản 7 Điều 3 " + ND94 + ").", n94("d3:k7"))
add(G, "quy_tac", "Trung tâm sát hạch lái xe loại 3 được sát hạch những hạng nào?",
    "Trung tâm sát hạch lái xe loại 3 cung cấp dịch vụ tổ chức sát hạch, cấp giấy phép lái xe các hạng A1, A và B1. Trung "
    "tâm loại 2 sát hạch các hạng A1, A, B1, B, C1, C và D1; trung tâm loại 1 sát hạch tất cả các hạng, kể cả các hạng kéo "
    "rơ moóc (khoản 4 Điều 3 " + ND94 + ").", n94("d3:k4:c"), n94("d3:k4:b"), n94("d3:k4:a"))
add(G, "quy_tac", "Giáo viên dạy thực hành lái xe phải đáp ứng những tiêu chuẩn gì?",
    "Theo khoản 2 Điều 10 " + ND94 + ", giáo viên dạy thực hành lái xe phải có bằng tốt nghiệp trung cấp chuyên nghiệp "
    "hoặc trung cấp nghề hoặc bằng nghề trở lên; có giấy phép lái xe hạng tương ứng hoặc cao hơn hạng xe đào tạo; có văn "
    "bằng, chứng chỉ về nghiệp vụ sư phạm theo quy định; và đã qua tập huấn nghiệp vụ dạy thực hành lái xe theo chương "
    "trình khung tại Phụ lục II.", n94("d10:k2"), n94("d10:k2:b"))
add(G, "quy_tac", "Xe tập lái và xe sát hạch khác nhau thế nào?",
    "Xe tập lái là xe ô tô dùng để đào tạo lái xe ô tô; xe sát hạch là xe mô tô, ô tô dùng để sát hạch lái xe (khoản 1, "
    "khoản 2 Điều 3 " + ND94 + ").", n94("d3:k1"), n94("d3:k2"))

# ===== Đối tượng xử phạt, phạt nguội (NĐ 168 Điều 47)
add(X, "quy_tac", "Chủ xe tự lái ô tô hết hạn đăng kiểm thì bị phạt theo mức của người lái hay của chủ xe?",
    "Theo mức của chủ xe. Với các hành vi vi phạm về giấy chứng nhận, tem kiểm định quy định ở Điều 13, Điều 16 và các "
    "hành vi tương ứng ở Điều 32, nếu chủ phương tiện là người trực tiếp điều khiển thì bị xử phạt theo điểm, khoản tương "
    "ứng của Điều 32 (điểm b khoản 3 Điều 47 " + ND + ").", v("d47:k3:b"), v("d47:k3"))
add(X, "quy_tac", "Chủ xe tự lái xe không gắn biển số hoặc không có đăng ký xe thì bị phạt theo điều nào?",
    "Các hành vi về biển số, chứng nhận đăng ký xe, đăng ký tạm thời quy định ở Điều 13, Điều 14, Điều 16 và các hành vi "
    "tương ứng ở Điều 32, nếu chủ phương tiện là người trực tiếp điều khiển thì bị xử phạt theo điểm, khoản tương ứng của "
    "Điều 32 (điểm a khoản 3 Điều 47 " + ND + "), tức là theo mức phạt dành cho chủ phương tiện.",
    v("d47:k3:a"), v("d47:k3"))
add(X, "quy_tac", "Xe tải vừa chở quá tải trọng của xe vừa vượt tải trọng của đường bộ thì bị phạt một lỗi hay hai lỗi?",
    "Hai lỗi. Trường hợp chủ phương tiện, người điều khiển vừa vi phạm Điều 21 (tải trọng của xe), vừa vi phạm Điều 34 "
    "(tải trọng, khổ giới hạn của đường bộ) thì bị xử phạt về từng hành vi. Riêng khi vừa vượt tổng trọng lượng vừa vượt "
    "tải trọng trục xe theo điểm a khoản 4, điểm a khoản 5 Điều 34 thì chỉ bị phạt theo hành vi có mức phạt cao hơn "
    "(khoản 4 Điều 47 " + ND + ").", v("d47:k4"))
add(X, "quy_tac", "Theo Nghị định 168, chủ phương tiện bị xử phạt là ai?",
    "Chủ phương tiện bị xử phạt trước hết là cá nhân, tổ chức đứng tên trong chứng nhận đăng ký xe (điểm a khoản 6 Điều 47 "
    + ND + "). Ngoài ra có các trường hợp được áp dụng xử phạt như chủ phương tiện: vợ hoặc chồng của người đứng tên điều "
    "khiển xe; người thuê tài chính phương tiện; người đã mua, được tặng cho, thừa kế xe nhưng chưa làm thủ tục sang tên "
    "(các điểm b, c, e khoản 6 Điều 47).", v("d47:k6"), v("d47:k6:a"), v("d47:k6:b"), v("d47:k6:e"))
add(X, "tinh_huong", "Tôi lái xe ô tô do vợ tôi đứng tên đăng ký. Nếu xe vi phạm lỗi của chủ xe thì ai bị phạt?",
    "Trường hợp người điều khiển phương tiện là chồng (vợ) của cá nhân đứng tên trong chứng nhận đăng ký xe thì người điều "
    "khiển là đối tượng để áp dụng xử phạt như chủ phương tiện (điểm b khoản 6 Điều 47 " + ND + "). Như vậy bạn bị xử "
    "phạt như chủ xe.", v("d47:k6:b"), v("d47:k6"))
add(X, "tinh_huong", "Tôi mua lại xe máy cũ nhưng chưa sang tên. Nếu bị xử phạt lỗi của chủ xe thì người bán hay tôi bị phạt?",
    "Bạn bị phạt. Đối với phương tiện chưa làm thủ tục cấp chứng nhận đăng ký xe khi thay đổi chủ xe, cá nhân, tổ chức đã "
    "mua, được chuyển nhượng, trao đổi, tặng cho, thừa kế là đối tượng để áp dụng xử phạt như chủ phương tiện (điểm e "
    "khoản 6 Điều 47 " + ND + ").", v("d47:k6:e"), v("d47:k6"))
add(X, "thu_tuc", "Bị camera ghi hình vi phạm (phạt nguội) thì chủ xe được thông báo thế nào?",
    "Khi vi phạm được phát hiện qua phương tiện, thiết bị kỹ thuật nghiệp vụ mà chưa dừng được xe, cơ quan chức năng gửi "
    "thông báo yêu cầu chủ phương tiện và người liên quan đến trụ sở để giải quyết. Thông báo bằng văn bản hoặc bằng "
    "phương thức điện tử qua Ứng dụng giao thông trên thiết bị di động; đồng thời thông tin xe vi phạm được cập nhật trên "
    "Trang thông tin điện tử của Cục Cảnh sát giao thông (điểm a khoản 8 Điều 47 " + ND + ").", v("d47:k8:a"), v("d47:k8"))
add(X, "tinh_huong", "Tôi cho bạn mượn xe và xe bị phạt nguội. Nếu tôi không khai ai lái thì sao?",
    "Chủ phương tiện có nghĩa vụ hợp tác với cơ quan chức năng để xác định người đã điều khiển xe vi phạm. Nếu chủ xe là "
    "cá nhân mà không hợp tác, không chứng minh hoặc không giải trình được mình không phải người điều khiển thì bị xử phạt "
    "đối với hành vi vi phạm được phát hiện (điểm b khoản 8 Điều 47 " + ND + ").", v("d47:k8:b"), v("d47:k8"))
add(X, "quy_tac", "Chưa nộp phạt nguội thì có đi đăng kiểm hoặc đổi bằng lái được không?",
    "Không. Khi quá thời hạn hẹn giải quyết hoặc quá thời hạn thi hành quyết định xử phạt mà chưa giải quyết, người có thẩm "
    "quyền gửi thông báo cho cơ quan đăng kiểm, cơ quan đăng ký xe, cơ quan cấp giấy phép lái xe (khoản 11 Điều 47 " + ND
    + "). Nếu tra cứu thấy thông tin vi phạm thì chưa giải quyết đăng kiểm, đăng ký phương tiện vi phạm, chưa cấp, đổi, "
    "cấp lại giấy phép lái xe cho người vi phạm (điểm b khoản 11 Điều 47); sau khi giải quyết xong vụ việc thì được làm "
    "thủ tục bình thường (điểm c khoản 11).", v("d47:k11"), v("d47:k11:b"), v("d47:k11:c"))
add(X, "thu_tuc", "Chủ xe không có mặt khi xe vi phạm lỗi của chủ phương tiện thì xử lý thế nào?",
    "Người có thẩm quyền vẫn lập biên bản vi phạm hành chính đối với chủ phương tiện và xử phạt theo quy định; người điều "
    "khiển phương tiện phải ký vào biên bản với tư cách là người chứng kiến (khoản 2 Điều 47 " + ND + ").", v("d47:k2"))

# ===== Giấy tờ, tạm giữ xe (NĐ 168 Điều 48)
add(P, "tinh_huong", "Tôi quên mang bằng lái và cà vẹt khi bị cảnh sát kiểm tra. Hiện nay xử lý thế nào?",
    "Theo khoản 3 Điều 48 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), người có thẩm quyền lập biên bản đối với "
    "người lái về hành vi không có giấy tờ tương ứng, đồng thời lập biên bản đối với chủ phương tiện về hành vi tương ứng "
    "ở Điều 32, và tạm giữ phương tiện. Nếu trong thời hạn hẹn ghi trong biên bản bạn xuất trình được giấy tờ (bản giấy "
    "hoặc thông tin tích hợp trong tài khoản định danh điện tử), thì không bị xử phạt lỗi không có giấy tờ và chủ xe cũng "
    "không bị xử phạt (điểm c khoản 3).", v("d48:k3", NEW), v("d48:k3:a", NEW), v("d48:k3:c", NEW))
add(P, "doi_thuong", "quên bằng lái ở nhà bị csgt giữ xe ko",
    "Có thể bị tạm giữ xe. Khi không xuất trình được giấy phép lái xe, người có thẩm quyền lập biên bản và tạm giữ phương "
    "tiện theo quy định (điểm a khoản 3 Điều 48 " + ND + ", có hiệu lực từ ngày 15/8/2026). Nếu trong thời hạn hẹn bạn "
    "xuất trình được bằng lái hợp lệ (kể cả thông tin bằng lái tích hợp trong tài khoản định danh điện tử) thì không bị phạt lỗi không có giấy tờ "
    "(điểm c khoản 3 Điều 48).", v("d48:k3:a", NEW), v("d48:k3:c", NEW))
add(P, "tinh_huong", "Tôi lái xe kinh doanh vận tải, quên mang giấy tờ nhưng sau đó mang đến xuất trình đúng hạn. Tôi có bị "
    "phạt không?",
    "Có, nhưng chỉ bị phạt lỗi không mang theo giấy tờ. Nếu người điều khiển phương tiện kinh doanh vận tải xuất trình được giấy tờ trong thời hạn hẹn thì "
    "bị ra quyết định xử phạt về hành vi không mang theo giấy tờ, và chủ phương tiện không bị xử phạt (điểm b khoản 3 Điều "
    "48 " + ND + ", có hiệu lực từ ngày 15/8/2026).", v("d48:k3:b", NEW), v("d48:k3", NEW))
add(P, "quy_tac", "Quá hạn hẹn ghi trong biên bản mới mang giấy tờ đến xuất trình thì có được miễn phạt không?",
    "Không. Quá thời hạn hẹn giải quyết vụ việc ghi trong biên bản mà người vi phạm mới xuất trình hoặc không xuất trình "
    "được giấy tờ thì phải chấp hành quyết định xử phạt đối với các hành vi đã ghi trong biên bản (điểm d khoản 3 Điều 48 "
    + ND + ", có hiệu lực từ ngày 15/8/2026).", v("d48:k3:d", NEW), v("d48:k3", NEW))
add(P, "quy_tac", "Xe chở hàng bị tạm giữ thì chi phí chuyển hàng sang xe khác do ai chịu?",
    "Khi phương tiện bị tạm giữ, chủ phương tiện phải chịu mọi chi phí (nếu có) cho việc sử dụng phương tiện khác thay "
    "thế để vận chuyển người, hàng hóa được chở trên phương tiện bị tạm giữ (khoản 4 Điều 48 " + ND + ").", v("d48:k4"))

out = ROOT / "data/train/drafts/gplx_03.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
