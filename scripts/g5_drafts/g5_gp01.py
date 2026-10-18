"""Đợt 2a G5: GPLX. Luật 36/2024 Điều 57–62 và Thông tư 108/2026/TT-BCA (sát hạch, cấp, đổi, cấp lại, thu hồi GPLX).
Ghi data/train/drafts/gplx_01.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
TT = "Thông tư 108/2026/TT-BCA"
S = []
START = 1


def l(s, d="2025-01-01"):
    return f"luat_36_2024:{s}@{d}"


def t(s):
    return f"tt_108_2026_bca:{s}@2026-07-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"gp-{START + len(S):04d}", "chu_de": "GPLX", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Hạng giấy phép lái xe (Điều 57 Luật)
add("quy_tac", "Giấy phép lái xe hạng A1 được lái loại xe nào?",
    "Theo điểm a khoản 1 Điều 57 " + LUAT + ", giấy phép lái xe hạng A1 cấp cho người lái xe mô tô hai bánh có dung tích "
    "xi-lanh đến 125 cm3 hoặc có công suất động cơ điện đến 11 kW.", l("d57:k1:a"), l("d57:k1"))
add("doi_thuong", "xe máy 150 phân khối thì phải thi bằng gì",
    "Xe mô tô hai bánh có dung tích xi-lanh trên 125 cm3 (hoặc công suất động cơ điện trên 11 kW) phải dùng giấy phép lái "
    "xe hạng A; bằng hạng A cũng được lái các loại xe của hạng A1 (điểm b khoản 1 Điều 57 " + LUAT + ").",
    l("d57:k1:b"), l("d57:k1"))
add("quy_tac", "Giấy phép lái xe hạng B1 theo luật hiện hành dùng để lái loại xe nào?",
    "Theo điểm c khoản 1 Điều 57 " + LUAT + ", hạng B1 cấp cho người lái xe mô tô ba bánh và các loại xe quy định cho "
    "giấy phép lái xe hạng A1.", l("d57:k1:c"), l("d57:k1"))
add("quy_tac", "Giấy phép lái xe hạng B được lái những loại xe nào?",
    "Hạng B cấp cho người lái xe ô tô chở người đến 08 chỗ (không kể chỗ của người lái xe); xe ô tô tải và ô tô chuyên "
    "dùng có khối lượng toàn bộ theo thiết kế đến 3.500 kg; các loại xe ô tô của hạng B kéo rơ moóc có khối lượng toàn bộ "
    "theo thiết kế đến 750 kg (điểm d khoản 1 Điều 57 " + LUAT + ").", l("d57:k1:d"), l("d57:k1"))
add("tinh_huong", "Tôi có bằng B, muốn lái xe tải có khối lượng toàn bộ theo thiết kế 5.000 kg thì có được không?",
    "Không được. Bằng hạng B chỉ cho lái xe ô tô tải có khối lượng toàn bộ theo thiết kế đến 3.500 kg. Xe tải trên 3.500 "
    "kg đến 7.500 kg phải dùng giấy phép lái xe hạng C1 (điểm d, điểm đ khoản 1 Điều 57 " + LUAT + ").",
    l("d57:k1:đ"), l("d57:k1:d"))
add("quy_tac", "Giấy phép lái xe hạng C được lái loại xe nào?",
    "Hạng C cấp cho người lái xe ô tô tải và ô tô chuyên dùng có khối lượng toàn bộ theo thiết kế trên 7.500 kg; xe tải "
    "của hạng C kéo rơ moóc có khối lượng toàn bộ theo thiết kế đến 750 kg; và các loại xe quy định cho giấy phép lái xe "
    "hạng B và hạng C1 (điểm e khoản 1 Điều 57 " + LUAT + ").", l("d57:k1:e"), l("d57:k1"))
add("quy_tac", "Muốn lái xe khách 16 chỗ thì cần giấy phép lái xe hạng gì?",
    "Xe ô tô chở người trên 08 chỗ đến 16 chỗ (không kể chỗ của người lái xe) thuộc hạng D1 (điểm g khoản 1 Điều 57 "
    + LUAT + "). Hạng D1 cũng được lái các loại xe của hạng B, C1, C.", l("d57:k1:g"), l("d57:k1"))
add("quy_tac", "Lái xe buýt 29 chỗ cần giấy phép lái xe hạng nào?",
    "Xe ô tô chở người (kể cả xe buýt) trên 16 chỗ đến 29 chỗ (không kể chỗ của người lái xe) thuộc hạng D2 (điểm h "
    "khoản 1 Điều 57 " + LUAT + ").", l("d57:k1:h"), l("d57:k1"))
add("quy_tac", "Lái xe khách giường nằm cần giấy phép lái xe hạng gì?",
    "Theo điểm i khoản 1 Điều 57 " + LUAT + ", hạng D cấp cho người lái xe ô tô chở người (kể cả xe buýt) trên 29 chỗ "
    "(không kể chỗ của người lái xe) và xe ô tô chở người giường nằm.", l("d57:k1:i"), l("d57:k1"))
add("quy_tac", "Lái ô tô con kéo rơ moóc có khối lượng toàn bộ trên 750 kg thì cần bằng hạng gì?",
    "Phải có giấy phép lái xe hạng BE: hạng này cấp cho người lái các loại xe ô tô quy định cho hạng B kéo rơ moóc có "
    "khối lượng toàn bộ theo thiết kế trên 750 kg (điểm k khoản 1 Điều 57 " + LUAT + ").", l("d57:k1:k"), l("d57:k1"))
add("quy_tac", "Lái xe đầu kéo kéo sơ mi rơ moóc (xe container) cần giấy phép lái xe hạng gì?",
    "Theo điểm m khoản 1 Điều 57 " + LUAT + ", hạng CE cấp cho người lái xe ô tô đầu kéo kéo sơ mi rơ moóc và các loại "
    "xe ô tô của hạng C kéo rơ moóc có khối lượng toàn bộ theo thiết kế trên 750 kg.", l("d57:k1:m"), l("d57:k1"))
add("quy_tac", "Người khuyết tật lái xe ô tô số tự động được cấp giấy phép lái xe hạng gì?",
    "Người khuyết tật điều khiển xe ô tô số tự động có kết cấu phù hợp với tình trạng khuyết tật thì được cấp giấy phép "
    "lái xe hạng B; nếu điều khiển xe mô tô ba bánh dùng cho người khuyết tật thì được cấp hạng A1 (khoản 2 Điều 57 "
    + LUAT + ").", l("d57:k2"))
add("quy_tac", "Lái xe chở người bốn bánh có gắn động cơ (xe điện du lịch) thì dùng giấy phép lái xe hạng nào?",
    "Người điều khiển xe chở người bốn bánh có gắn động cơ, xe chở hàng bốn bánh có gắn động cơ phải sử dụng giấy phép "
    "lái xe có hạng phù hợp với xe ô tô chở người hoặc xe ô tô tải tương ứng (khoản 3 Điều 57 " + LUAT + ").",
    l("d57:k3"))
add("doi_thuong", "bằng B số tự động có lái được xe số sàn ko",
    "Không. Người có giấy phép lái xe hạng B số tự động không được lái loại xe ô tô số cơ khí (số sàn) (khoản 6 Điều 18 "
    + TT + ").", t("d18:k6"))

# ===== Thời hạn, hiệu lực (Điều 57 Luật)
add("quy_tac", "Giấy phép lái xe hạng A1, A, B1 có thời hạn bao lâu?",
    "Giấy phép lái xe các hạng A1, A, B1 không thời hạn (điểm a khoản 5 Điều 57 " + LUAT + ").", l("d57:k5:a"), l("d57:k5"))
add("doi_thuong", "bằng lái ô tô hạng B dùng được mấy năm thì hết hạn",
    "Theo điểm b khoản 5 Điều 57 " + LUAT + ", giấy phép lái xe hạng B và hạng C1 có thời hạn 10 năm kể từ ngày cấp.",
    l("d57:k5:b"), l("d57:k5"))
add("quy_tac", "Giấy phép lái xe hạng C, D và các hạng kéo rơ moóc có thời hạn bao lâu?",
    "Giấy phép lái xe các hạng C, D1, D2, D, BE, C1E, CE, D1E, D2E và DE có thời hạn 05 năm kể từ ngày cấp (điểm c "
    "khoản 5 Điều 57 " + LUAT + ").", l("d57:k5:c"), l("d57:k5"))
add("quy_tac", "Khi nào giấy phép lái xe bị coi là không có hiệu lực?",
    "Theo khoản 7 Điều 57 " + LUAT + ", giấy phép lái xe không có hiệu lực khi hết thời hạn sử dụng hoặc bị thu hồi "
    "theo quy định tại khoản 5 Điều 62 của Luật.", l("d57:k7"), l("d57:k7:a"), l("d57:k7:b"))
add("quy_tac", "Giấy phép lái xe quốc tế có thời hạn tối đa bao lâu?",
    "Giấy phép lái xe quốc tế do cơ quan có thẩm quyền của quốc gia thành viên Công ước Viên cấp theo mẫu thống nhất, có "
    "thời hạn không quá 03 năm kể từ ngày cấp và phải phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia "
    "(điểm a khoản 8 Điều 57 " + LUAT + ").", l("d57:k8:a"), l("d57:k8"))
add("tinh_huong", "Tôi là người nước ngoài có giấy phép lái xe quốc tế, khi lái xe ở Việt Nam cần mang theo giấy tờ gì?",
    "Người có giấy phép lái xe quốc tế do quốc gia thành viên Công ước Viên cấp khi lái xe ở Việt Nam phải mang theo giấy "
    "phép lái xe quốc tế và giấy phép lái xe quốc gia phù hợp với hạng xe điều khiển, còn thời hạn sử dụng, và phải tuân "
    "thủ pháp luật giao thông của Việt Nam (điểm b khoản 8 Điều 57 " + LUAT + ").", l("d57:k8:b"), l("d57:k8"))
add("quy_tac", "Giấy phép lái xe quốc tế do Việt Nam cấp có được dùng để lái xe trong lãnh thổ Việt Nam không?",
    "Không. Giấy phép lái xe quốc tế (IDP) do Việt Nam cấp theo Công ước về giao thông đường bộ năm 1968 không có giá trị "
    "sử dụng trong lãnh thổ Việt Nam (khoản 1 Điều 30 " + TT + ").", t("d30:k1"))

# ===== Điểm GPLX (Điều 58 Luật)
add("quy_tac", "Giấy phép lái xe có bao nhiêu điểm?",
    "Điểm của giấy phép lái xe bao gồm 12 điểm, dùng để quản lý việc chấp hành pháp luật về trật tự, an toàn giao thông "
    "của người lái xe; số điểm trừ mỗi lần vi phạm tùy thuộc tính chất, mức độ của hành vi vi phạm (khoản 1 Điều 58 "
    + LUAT + ").", l("d58:k1"))
add("doi_thuong", "bằng lái bị trừ điểm thì bao lâu được hồi lại điểm",
    "Giấy phép lái xe chưa bị trừ hết điểm và không bị trừ điểm trong thời hạn 12 tháng từ ngày bị trừ điểm gần nhất thì "
    "được phục hồi đủ 12 điểm (khoản 2 Điều 58 " + LUAT + ").", l("d58:k2"))
add("tinh_huong", "Bằng lái của tôi bị trừ hết 12 điểm. Tôi còn được lái xe không và làm sao để phục hồi điểm?",
    "Khi giấy phép lái xe bị trừ hết điểm, bạn không được điều khiển phương tiện theo giấy phép lái xe đó. Sau ít nhất 06 "
    "tháng kể từ ngày bị trừ hết điểm, bạn được tham gia kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông "
    "đường bộ do lực lượng Cảnh sát giao thông tổ chức; nếu đạt yêu cầu thì được phục hồi đủ 12 điểm (khoản 3 Điều 58 "
    + LUAT + ").", l("d58:k3"))
add("quy_tac", "Đổi hoặc nâng hạng giấy phép lái xe thì số điểm có được tính lại từ đầu không?",
    "Không. Giấy phép lái xe sau khi đổi, cấp lại, nâng hạng được giữ nguyên số điểm của giấy phép lái xe trước khi đổi, "
    "cấp lại, nâng hạng (khoản 4 Điều 58 " + LUAT + ").", l("d58:k4"))
add("quy_tac", "Ai có thẩm quyền trừ điểm giấy phép lái xe?",
    "Người có thẩm quyền xử phạt vi phạm hành chính có thẩm quyền trừ điểm giấy phép lái xe (khoản 5 Điều 58 " + LUAT
    + ").", l("d58:k5"))
add("quy_tac", "Khi nào điểm trừ giấy phép lái xe được cập nhật lên hệ thống?",
    "Dữ liệu về điểm trừ giấy phép lái xe của người vi phạm được cập nhật vào hệ thống cơ sở dữ liệu ngay sau khi quyết "
    "định xử phạt có hiệu lực thi hành và được thông báo cho người bị trừ điểm biết (khoản 1 Điều 58 " + LUAT + ").",
    l("d58:k1"))

# ===== Tuổi, sức khỏe (Điều 59 Luật)
add("quy_tac", "Bao nhiêu tuổi thì được lái xe gắn máy?",
    "Người đủ 16 tuổi trở lên được điều khiển xe gắn máy (điểm a khoản 1 Điều 59 " + LUAT + ").", l("d59:k1:a"),
    l("d59:k1"))
add("doi_thuong", "mấy tuổi thì được thi bằng lái ô tô hạng B",
    "Người đủ 18 tuổi trở lên được cấp giấy phép lái xe hạng A1, A, B1, B, C1 (điểm b khoản 1 Điều 59 " + LUAT + ").",
    l("d59:k1:b"), l("d59:k1"))
add("quy_tac", "Bao nhiêu tuổi thì được cấp giấy phép lái xe hạng C?",
    "Người đủ 21 tuổi trở lên được cấp giấy phép lái xe hạng C, BE (điểm c khoản 1 Điều 59 " + LUAT + ").",
    l("d59:k1:c"), l("d59:k1"))
add("quy_tac", "Độ tuổi được cấp giấy phép lái xe hạng D1, D2 là bao nhiêu?",
    "Người đủ 24 tuổi trở lên được cấp giấy phép lái xe hạng D1, D2, C1E, CE (điểm d khoản 1 Điều 59 " + LUAT + ").",
    l("d59:k1:d"), l("d59:k1"))
add("quy_tac", "Bao nhiêu tuổi thì được cấp giấy phép lái xe hạng D?",
    "Người đủ 27 tuổi trở lên được cấp giấy phép lái xe hạng D, D1E, D2E, DE (điểm đ khoản 1 Điều 59 " + LUAT + ").",
    l("d59:k1:đ"), l("d59:k1"))
add("quy_tac", "Tuổi tối đa được lái xe khách trên 29 chỗ hoặc xe giường nằm là bao nhiêu?",
    "Tuổi tối đa của người lái xe ô tô chở người (kể cả xe buýt) trên 29 chỗ (không kể chỗ của người lái xe), xe ô tô "
    "chở người giường nằm là đủ 57 tuổi đối với nam, đủ 55 tuổi đối với nữ (điểm e khoản 1 Điều 59 " + LUAT + ").",
    l("d59:k1:e"), l("d59:k1"))
add("tinh_huong", "Tôi là nam 54 tuổi, được cấp giấy phép lái xe hạng D thì thời hạn sử dụng được tính thế nào?",
    "Khi thời gian từ ngày cấp, đổi, cấp lại đến tuổi tối đa được phép điều khiển (đủ 57 tuổi với nam, đủ 55 tuổi với "
    "nữ) không đủ 05 năm, thời hạn sử dụng giấy phép lái xe hạng D được tính từ ngày cấp, đổi, cấp lại đến thời hạn còn "
    "lại theo độ tuổi tối đa (khoản 9 Điều 18 " + TT + "). Như vậy bằng của bạn có giá trị đến khi bạn đủ 57 tuổi.",
    t("d18:k9"), l("d59:k1:e"))
add("quy_tac", "Người điều khiển xe máy chuyên dùng cần đủ bao nhiêu tuổi để được cấp chứng chỉ bồi dưỡng kiến thức pháp luật?",
    "Người đủ 18 tuổi trở lên được cấp chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ để điều khiển xe "
    "máy chuyên dùng tham gia giao thông đường bộ (điểm b khoản 1 Điều 59 " + LUAT + ").", l("d59:k1:b"), l("d59:k1"))

# ===== Đào tạo, nâng hạng (Điều 60 Luật)
add("quy_tac", "Muốn thi bằng lái có bắt buộc phải học ở cơ sở đào tạo không?",
    "Người có nhu cầu được cấp giấy phép lái xe phải được đào tạo nội dung lý thuyết và thực hành theo chương trình đào "
    "tạo quy định cho từng hạng (khoản 1 Điều 60 " + LUAT + "); người học phải được đào tạo tại các cơ sở đào tạo lái xe "
    "hoặc các hình thức đào tạo lái xe khác (khoản 2 Điều 60).", l("d60:k1"), l("d60:k2"))
add("quy_tac", "Từ bằng B có thể nâng lên những hạng nào?",
    "Theo điểm a khoản 3 Điều 60 " + LUAT + ", có thể nâng hạng giấy phép lái xe từ hạng B lên hạng C1, hạng C, hạng D1 "
    "hoặc hạng D2. Ngoài ra, có thể nâng từ hạng B lên hạng BE (điểm e khoản 3 Điều 60, nội dung có hiệu lực từ ngày "
    "01/7/2026).", l("d60:k3:a"), l("d60:k3"), l("d60:k3:e", "2026-07-01"))
add("quy_tac", "Muốn nâng hạng giấy phép lái xe lên hạng D1, D2, D thì cần điều kiện gì?",
    "Người có nhu cầu đào tạo nâng hạng khi giấy phép lái xe còn hiệu lực phải có đủ thời gian lái xe an toàn quy định "
    "cho từng hạng; riêng nâng hạng lên D1, D2, D còn phải có trình độ từ trung học cơ sở trở lên (khoản 4 Điều 60 "
    + LUAT + ").", l("d60:k4"))
add("quy_tac", "Có được học thẳng để thi bằng C hoặc D lần đầu không?",
    "Không. Giấy phép lái xe các hạng C, D1, D2, D, BE, C1E, CE, D1E, D2E, DE phải được đào tạo bằng hình thức đào tạo "
    "nâng hạng theo các điều kiện tại khoản 3 và khoản 4 Điều 60 (khoản 5 Điều 60 " + LUAT + ").", l("d60:k5"))

# ===== Sát hạch (Điều 61 Luật, TT 108)
add("quy_tac", "Ai được đăng ký dự kỳ sát hạch lái xe?",
    "Người đã hoàn thành chương trình đào tạo lái xe, có độ tuổi, sức khỏe theo quy định tại Điều 59 " + LUAT + " được "
    "đăng ký để tham dự kỳ sát hạch lái xe (khoản 1 Điều 61).", l("d61:k1"))
add("quy_tac", "Sát hạch lái xe ô tô được tổ chức ở đâu?",
    "Hoạt động sát hạch lái xe ô tô phải thực hiện tại các trung tâm sát hạch lái xe; sát hạch lái xe mô tô thực hiện tại "
    "trung tâm sát hạch hoặc tại sân tập lái đáp ứng điều kiện, tiêu chuẩn. Hoạt động sát hạch do cơ quan nhà nước có "
    "thẩm quyền thực hiện (khoản 3 Điều 61 " + LUAT + ").", l("d61:k3"))
add("thu_tuc", "Thi bằng lái xe máy hạng A1, A gồm những phần nào?",
    "Theo điểm a khoản 5 Điều 4 " + TT + ", thí sinh sát hạch mô tô thực hiện sát hạch lý thuyết, bài sát hạch số 1 và "
    "bài sát hạch số 2. Phần thực hành trong hình được chấm điểm trực tiếp kết hợp thiết bị chấm điểm tự động (điểm a "
    "khoản 2 Điều 4).", t("d4:k5:a"), t("d4:k2:a"))
add("thu_tuc", "Thi bằng lái ô tô hạng B gồm những phần nào?",
    "Thí sinh sát hạch ô tô thực hiện sát hạch lý thuyết, sát hạch thực hành lái xe trong hình và sát hạch thực hành lái "
    "xe trên đường (điểm b khoản 5 Điều 4 " + TT + "). Với hạng B, bài trong hình là bài sát hạch liên hoàn, chấm bằng "
    "thiết bị tự động kết hợp chấm trực tiếp (điểm c khoản 2 Điều 4).", t("d4:k5:b"), t("d4:k2:c"))
add("tinh_huong", "Tôi đã có bằng lái ô tô còn hiệu lực, giờ đi thi bằng xe máy hạng A1 thì có phải thi lý thuyết không?",
    "Không. Thí sinh dự sát hạch lái xe hạng A1, A có giấy phép lái xe ô tô còn hiệu lực được miễn sát hạch lý thuyết "
    "(điểm c khoản 1 Điều 4 " + TT + ").", t("d4:k1:c"), t("d4:k1"))
add("quy_tac", "Phần thi lý thuyết lái xe gồm những nội dung gì?",
    "Sát hạch lý thuyết gồm câu hỏi về pháp luật trật tự, an toàn giao thông đường bộ; kỹ thuật lái xe; quy tắc ứng xử, "
    "văn hóa giao thông và phòng, chống tác hại của rượu, bia; cấu tạo và sửa chữa thông thường, kỹ năng phòng cháy, "
    "chữa cháy và cứu nạn, cứu hộ (đối với hạng B1, B trở lên); nội dung về vận tải đường bộ (đối với hạng C1 trở lên). "
    "Phần thi thực hiện trên máy tính (điểm a, điểm b khoản 1 Điều 4 " + TT + ").", t("d4:k1:a"), t("d4:k1:b"))
add("thu_tuc", "Thi bằng xe máy trượt lý thuyết thì có được thi tiếp phần thực hành không?",
    "Không. Thí sinh hạng A1, A, B1 không đạt sát hạch lý thuyết thì không được dự bài sát hạch số 1; không đạt bài số 1 "
    "thì không được dự bài số 2 (điểm b khoản 1 Điều 12 " + TT + "). Thí sinh không đạt được đăng ký sát hạch lại ở các "
    "kỳ sát hạch khác (điểm d khoản 1 Điều 12).", t("d12:k1:b"), t("d12:k1:d"))
add("doi_thuong", "thi bằng lái đỗ lý thuyết mà trượt sa hình thì kết quả lý thuyết được giữ bao lâu",
    "Kết quả sát hạch lý thuyết đã đạt được bảo lưu trong thời gian 01 năm kể từ ngày đạt; kết quả phần thực hành trong "
    "hình (với ô tô) hoặc bài số 1 (với mô tô) được bảo lưu theo thời gian còn lại của phần lý thuyết (điểm c khoản 1, "
    "điểm b khoản 2 Điều 12 " + TT + ").", t("d12:k2:b"), t("d12:k1:c"))
add("quy_tac", "Mang điện thoại vào phòng thi lý thuyết lái xe thì bị xử lý thế nào?",
    "Thí sinh mang tài liệu, điện thoại di động hoặc phương tiện, thiết bị kỹ thuật vào phòng sát hạch lý thuyết, trên xe "
    "sát hạch, hoặc có hành vi gian dối khác làm sai lệch kết quả sẽ bị đình chỉ, hủy bỏ kết quả kỳ sát hạch (khoản 4 "
    "Điều 12 " + TT + ").", t("d12:k4"))
add("thu_tuc", "Thi đỗ bằng lái thì bao lâu có giấy phép lái xe?",
    "Cục Cảnh sát giao thông cấp giấy phép lái xe điện tử cho người đạt kết quả sát hạch và tích hợp vào hệ thống dữ liệu "
    "điện tử trong thời hạn 02 giờ kể từ khi kết thúc kỳ sát hạch. Nếu cần bằng vật liệu PET thì được in và trả trong thời "
    "hạn 3,5 ngày làm việc kể từ ngày kết thúc kỳ sát hạch (khoản 1 Điều 19 " + TT + ").", t("d19:k1"))
add("thu_tuc", "Điều kiện để được dự sát hạch lái xe theo Thông tư 108/2026 là gì?",
    "Thí sinh phải đủ tuổi (tính đến ngày dự sát hạch), sức khỏe theo khoản 1, 2 Điều 59 " + LUAT + " và được cơ sở đào "
    "tạo xác nhận hoàn thành khóa đào tạo hoặc được cấp chứng chỉ sơ cấp hoặc giấy xác nhận hoàn thành chương trình đào "
    "tạo lái xe (Điều 15 " + TT + ").", t("d15:k1"), t("d15:k2"))
add("thu_tuc", "Hồ sơ cá nhân đề nghị sát hạch lái xe gồm những gì?",
    "Theo khoản 2 Điều 16 " + TT + ", hồ sơ gồm: chứng chỉ sơ cấp hoặc chứng chỉ đào tạo hoặc giấy xác nhận hoàn thành "
    "khóa đào tạo; giấy khám sức khỏe của người lái xe còn hiệu lực (bản điện tử, nếu hệ thống lỗi thì dùng bản giấy); "
    "giấy tờ cư trú hợp lệ đối với người nước ngoài; và biên bản tổng hợp kết quả các kỳ sát hạch trước nếu là người thi "
    "lại.", t("d16:k2"), t("d16:k2:a"), t("d16:k2:b"))

# ===== Cấp, đổi, cấp lại (Điều 62 Luật, Điều 19–21 TT 108)
add("thu_tuc", "Bằng lái ô tô của tôi đã quá hạn 6 tháng thì phải làm gì?",
    "Giấy phép lái xe quá thời hạn sử dụng từ đủ 30 ngày đến dưới 01 năm kể từ ngày hết hạn đến khi nộp đủ hồ sơ hợp lệ "
    "thì phải sát hạch lý thuyết để được cấp lại giấy phép lái xe (điểm a khoản 2 Điều 19 " + TT + "); người đó phải có "
    "tên trong hệ thống thông tin giấy phép lái xe hoặc sổ quản lý.", t("d19:k2:a"), t("d19:k2"))
add("tinh_huong", "Bằng lái xe hạng B của tôi đã hết hạn hơn 2 năm. Tôi có phải thi lại toàn bộ không?",
    "Có. Giấy phép lái xe quá thời hạn sử dụng từ đủ 01 năm trở lên kể từ ngày hết hạn thì phải sát hạch lý thuyết, thực "
    "hành lái xe trong hình và trên đường để được cấp giấy phép lái xe (điểm a khoản 2 Điều 19 " + TT + "). Hồ sơ đề "
    "nghị sát hạch thực hiện theo khoản 3 Điều 16.", t("d19:k2:a"), t("d16:k3"))
add("thu_tuc", "Hồ sơ đề nghị sát hạch lại khi giấy phép lái xe quá hạn gồm những gì?",
    "Theo khoản 3 Điều 16 " + TT + ", hồ sơ gồm: bản sao giấy phép lái xe (nếu bị mất thì cung cấp thông tin về giấy phép "
    "lái xe); giấy tờ cư trú hợp lệ đối với người nước ngoài; giấy phép lái xe quân sự hoặc xác nhận của cơ quan đã cấp "
    "nếu là bằng quân sự bị mất; giấy khám sức khỏe của người lái xe còn hiệu lực; bản sao giấy tờ chứng minh thôi phục "
    "vụ trong quân đội, công an nếu là bằng quân sự, bằng công an.", t("d16:k3"), t("d16:k3:a"), t("d16:k3:d"))
add("quy_tac", "Người có lỗi vi phạm giao thông chưa nộp phạt có được thi, đổi hoặc cấp lại bằng lái không?",
    "Chưa được. Chưa cấp, đổi, cấp lại giấy phép lái xe đối với người vi phạm pháp luật về trật tự, an toàn giao thông "
    "đường bộ khi người đó chưa thực hiện xong yêu cầu của cơ quan nhà nước có thẩm quyền về giải quyết vụ việc vi phạm "
    "hành chính (khoản 4 Điều 62 " + LUAT + "; khoản 3 Điều 19 " + TT + ").", l("d62:k4"), t("d19:k3"))
add("quy_tac", "Những trường hợp nào được đổi, cấp lại giấy phép lái xe?",
    "Theo khoản 2 Điều 62 " + LUAT + ", người có giấy phép lái xe được đổi, cấp lại khi: giấy phép bị mất; bị hỏng "
    "không còn sử dụng được; trước thời hạn ghi trên giấy phép; thay đổi thông tin ghi trên giấy phép; có giấy phép lái "
    "xe nước ngoài còn giá trị sử dụng; có giấy phép do Bộ Quốc phòng, Bộ Công an cấp khi có yêu cầu hoặc khi không còn "
    "làm nhiệm vụ quốc phòng, an ninh.", l("d62:k2"), l("d62:k2:a"), l("d62:k2:b"))
add("tinh_huong", "Tôi làm mất bằng lái xe còn hạn. Tôi phải làm gì?",
    "Người có giấy phép lái xe còn thời hạn sử dụng mà bị mất được đề nghị cấp lại giấy phép lái xe; hồ sơ, trình tự cấp "
    "lại thực hiện theo khoản 2, 3, 4 Điều 21 " + TT + " (khoản 1 Điều 20). Không cấp lại nếu thông tin giấy phép không "
    "có trong hệ thống hoặc sổ quản lý, hoặc người đó chưa chấp hành xong việc xử lý vi phạm giao thông (khoản 2 Điều 20).",
    t("d20:k1"), t("d20:k2"))
add("thu_tuc", "Hồ sơ đổi giấy phép lái xe gồm những giấy tờ gì?",
    "Theo khoản 2 Điều 21 " + TT + ", hồ sơ gồm: giấy khám sức khỏe của người lái xe còn hiệu lực (bản điện tử, nếu lỗi "
    "kỹ thuật thì dùng bản giấy); hộ chiếu còn thời hạn đối với người nước ngoài, người Việt Nam định cư ở nước ngoài; "
    "các giấy tờ khác để đối chiếu nếu thông tin trên giấy phép sai lệch với căn cước.", t("d21:k2"), t("d21:k2:a"),
    t("d21:k2:b"))
add("thu_tuc", "Đổi giấy phép lái xe trực tuyến nộp hồ sơ ở đâu?",
    "Cá nhân lập 01 bộ hồ sơ gửi trực tuyến tại Cổng Dịch vụ công quốc gia hoặc ứng dụng định danh Quốc gia hoặc các ứng "
    "dụng của lực lượng Công an nhân dân, kê khai theo hướng dẫn và nộp lệ phí. Nếu chưa có định danh mức độ 2, chưa có "
    "dữ liệu giấy phép trong hệ thống hoặc Cổng bị lỗi thì nộp trực tiếp tại Công an cấp xã nơi có điểm tiếp nhận hoặc "
    "Phòng Cảnh sát giao thông (điểm a khoản 3 Điều 21 " + TT + ").", t("d21:k3:a"), t("d21:k3"))
add("thu_tuc", "Đổi giấy phép lái xe bao lâu thì có kết quả?",
    "Phòng Cảnh sát giao thông chuyển dữ liệu về Cục Cảnh sát giao thông để cấp và tích hợp giấy phép lái xe trên ứng "
    "dụng định danh trong thời hạn 01 ngày kể từ khi nhận đủ hồ sơ hợp lệ; nếu người dân cần bản in thì được in và trả "
    "trong thời hạn 2,5 ngày làm việc (điểm c khoản 3 Điều 21 " + TT + ").", t("d21:k3:c"), t("d21:k3"))
add("tinh_huong", "Ngày sinh trên bằng lái của tôi bị sai so với căn cước. Tôi phải làm gì?",
    "Trường hợp ngày, tháng, năm sinh, họ, tên, tên đệm, quốc tịch ghi trên giấy phép lái xe sai lệch với căn cước công "
    "dân, căn cước hoặc hộ chiếu thì cơ quan có thẩm quyền làm thủ tục đổi giấy phép lái xe mới phù hợp với thông tin "
    "trong căn cước hoặc hộ chiếu (điểm c khoản 1 Điều 21 " + TT + "); kèm hồ sơ là các giấy tờ thể hiện thông tin để "
    "đối chiếu (điểm c khoản 2 Điều 21).", t("d21:k1:c"), t("d21:k2:c"))
add("quy_tac", "Có được đổi giấy phép lái xe xuống hạng thấp hơn không?",
    "Được. Trường hợp người lái xe có nhu cầu đổi giấy phép lái xe xuống hạng thấp hơn thì phải đăng ký với cơ quan "
    "tiếp nhận hồ sơ (khoản 4 Điều 21 " + TT + ").", t("d21:k4"))
add("quy_tac", "Giấy phép lái xe hiện nay được cấp dưới dạng nào?",
    "Giấy phép lái xe được cấp dưới dạng điện tử hoặc bằng vật liệu PET; mỗi người được cấp 01 số giấy phép lái xe dùng "
    "chung cho cả giấy phép không thời hạn và có thời hạn (khoản 2 Điều 18 " + TT + ").", t("d18:k2"))
add("quy_tac", "Giấy phép lái xe điện tử là gì?",
    "Theo khoản 2 Điều 3 " + TT + ", giấy phép lái xe điện tử là giấy phép lái xe thể hiện dưới dạng thông điệp dữ liệu, "
    "được tích hợp lên hệ thống dữ liệu điện tử, tài khoản định danh điện tử.", t("d3:k2"))
add("doi_thuong", "có bằng xe máy với bằng ô tô riêng thì gộp chung 1 bằng được ko",
    "Được. Cá nhân có nhu cầu tích hợp giấy phép lái xe không thời hạn với giấy phép lái xe có thời hạn thì đăng ký, làm "
    "thủ tục đổi giấy phép lái xe (khoản 3 Điều 18 " + TT + "); đây là một trong các trường hợp được đổi giấy phép lái "
    "xe (điểm d khoản 1 Điều 21).", t("d18:k3"), t("d21:k1:d"))

# ===== Bằng nước ngoài, IDP, thu hồi
add("thu_tuc", "Người nước ngoài có bằng lái của nước họ muốn lái xe ở Việt Nam thì làm thế nào?",
    "Người nước ngoài có giấy phép lái xe quốc gia thì phải làm thủ tục đổi sang giấy phép lái xe tương ứng của Việt Nam, "
    "trừ khi điều ước quốc tế mà Việt Nam là thành viên có quy định khác (khoản 7 Điều 18 " + TT + "). Điều kiện là giấy "
    "phép quốc gia còn thời hạn và có một trong các giấy tờ: chứng minh thư ngoại giao, công vụ, thị thực hoặc thẻ tạm "
    "trú còn thời hạn từ 90 ngày trở lên, thẻ thường trú (điểm a khoản 1 Điều 24).", t("d18:k7"), t("d24:k1:a"))
add("tinh_huong", "Tôi là người Việt, đi du học và được cấp bằng lái ở nước ngoài. Về nước có đổi sang bằng Việt Nam được không?",
    "Được, nếu bạn mang quốc tịch Việt Nam, cư trú, học tập, làm việc ở nước ngoài liên tục từ 03 tháng trở lên và được cơ "
    "quan có thẩm quyền nước ngoài cấp giấy phép lái xe quốc gia còn thời hạn sử dụng (điểm b khoản 1 Điều 24 " + TT
    + ").", t("d24:k1:b"), t("d24:k1"))
add("quy_tac", "Những loại giấy phép lái xe nước ngoài nào không được đổi sang bằng Việt Nam?",
    "Không đổi giấy phép lái xe tạm thời của nước ngoài; giấy phép lái xe quốc tế; giấy phép nước ngoài quá thời hạn, bị "
    "tẩy xóa, rách nát không còn đủ thông tin hoặc có sự khác biệt về nhận diện; giấy phép nước ngoài không do cơ quan có "
    "thẩm quyền cấp (điểm c khoản 1 Điều 24 " + TT + ").", t("d24:k1:c"), t("d24:k1"))
add("thu_tuc", "Hồ sơ đổi giấy phép lái xe nước ngoài sang giấy phép Việt Nam gồm những gì?",
    "Theo khoản 2 Điều 24 " + TT + ", hồ sơ gồm: bản dịch giấy phép lái xe nước ngoài ra tiếng Việt được bảo chứng chất "
    "lượng dịch thuật của cơ quan Công chứng tại Việt Nam hoặc của cơ quan đại diện Việt Nam ở nước ngoài; giấy khám sức "
    "khỏe của người lái xe còn hiệu lực (trừ người nước ngoài đổi theo thời hạn thị thực hoặc thẻ tạm trú); bản sao một "
    "trong các giấy tờ cư trú hợp lệ đối với người nước ngoài.", t("d24:k2"), t("d24:k2:a"), t("d24:k2:b"))
add("thu_tuc", "Muốn xin cấp giấy phép lái xe quốc tế (IDP) thì nộp hồ sơ ở đâu?",
    "Người có giấy phép lái xe quốc gia do Việt Nam cấp còn giá trị sử dụng thực hiện trực tiếp tại Cục Cảnh sát giao "
    "thông hoặc Phòng Cảnh sát giao thông, hoặc trực tuyến tại Cổng Dịch vụ công quốc gia (điểm a khoản 1 Điều 29 " + TT
    + ").", t("d29:k1:a"), t("d29:k1"))
add("quy_tac", "Trường hợp nào không được cấp giấy phép lái xe quốc tế?",
    "Không cấp IDP khi giấy phép lái xe quốc gia bị tẩy xóa không còn đủ thông tin cần thiết hoặc có sự khác biệt về nhận "
    "diện, hoặc giấy phép lái xe quốc gia không do cơ quan có thẩm quyền cấp (khoản 3 Điều 29 " + TT + ").",
    t("d29:k3"), t("d29:k3:a"), t("d29:k3:b"))
add("quy_tac", "Khi nào giấy phép lái xe bị thu hồi?",
    "Theo khoản 5 Điều 62 " + LUAT + ", giấy phép lái xe bị thu hồi khi: người được cấp không đủ điều kiện sức khỏe theo "
    "kết luận của cơ sở khám bệnh, chữa bệnh; giấy phép cấp sai quy định hoặc người được cấp có hành vi gian dối để được "
    "cấp, đổi, cấp lại (điểm b, nội dung có hiệu lực từ ngày 01/7/2026); giấy phép đã quá thời hạn tạm giữ hoặc hết thời "
    "hiệu thi hành quyết định xử phạt mà người vi phạm không đến nhận mà không có lý do chính đáng.",
    l("d62:k5"), l("d62:k5:a"), l("d62:k5:b", "2026-07-01"), l("d62:k5:c"))
add("tinh_huong", "Tôi bị phát hiện gian dối để được cấp bằng lái. Bao lâu sau tôi mới được thi lại?",
    "Giấy phép lái xe bị thu hồi do cấp sai quy định hoặc người được cấp gian dối (điểm b khoản 5 Điều 62 " + LUAT + "). "
    "Theo điểm b khoản 2 Điều 25 " + TT + ", người có hành vi vi phạm không được cấp giấy phép lái xe trong thời hạn 05 "
    "năm kể từ ngày phát hiện vi phạm; sau 05 năm, nếu có nhu cầu thì phải học và sát hạch lại như cấp lần đầu.",
    t("d25:k2:b"), l("d62:k5:b", "2026-07-01"))
add("thu_tuc", "Giấy phép lái xe điện tử bị thu hồi thì người dân có phải nộp lại bằng không?",
    "Đối với giấy phép lái xe đã có trên hệ thống dữ liệu điện tử, Cục trưởng Cục Cảnh sát giao thông ra quyết định thu "
    "hồi để hủy bỏ trong thời hạn 03 ngày làm việc kể từ ngày phát hiện, đồng thời hủy tích hợp trên ứng dụng định danh; "
    "cá nhân không phải nộp lại giấy phép lái xe (điểm a khoản 1 Điều 25 " + TT + ").", t("d25:k1:a"), t("d25:k1"))
add("thu_tuc", "Nhận quyết định thu hồi bằng lái (bằng không có trên hệ thống điện tử) thì phải nộp lại trong bao lâu?",
    "Trong thời hạn 05 ngày làm việc kể từ ngày nhận được quyết định thu hồi, cá nhân phải nộp giấy phép lái xe bị thu "
    "hồi đến Phòng Cảnh sát giao thông (điểm b khoản 1 Điều 25 " + TT + ").", t("d25:k1:b"), t("d25:k1"))

out = ROOT / "data/train/drafts/gplx_01.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
