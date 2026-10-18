"""Đợt 11b G5: thủ tục GPLX (TT 108/2026) ở các Điều chưa có mẫu thủ tục: nộp hồ sơ sát hạch, thi lại, nhận bằng PET,
cấp lại, đổi bằng hỏng, đổi bằng quân sự và trong Công an, IDP, sát hạch cho người khuyết tật, người dân tộc thiểu số.
Ghi data/train/drafts/gplx_04.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 108/2026/TT-BCA"
S = []
START = 137


def t(s):
    return f"tt_108_2026_bca:{s}@2026-07-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"gp-{START + len(S):04d}", "chu_de": "GPLX", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Hồ sơ và lịch sát hạch (Điều 9, 16, 17)
add("thu_tuc", "Hồ sơ đề nghị sát hạch lái xe phải gửi trước kỳ sát hạch bao lâu?",
    "Hồ sơ điện tử đề nghị sát hạch gửi trực tuyến tại Cổng Dịch vụ công quốc gia, ứng dụng định danh Quốc gia hoặc các "
    "ứng dụng của lực lượng Công an nhân dân trước kỳ sát hạch ít nhất 07 ngày làm việc; nếu hệ thống bị lỗi hoặc hạ tầng "
    "chưa đáp ứng thì gửi hồ sơ trực tiếp đến Phòng Cảnh sát giao thông (khoản 1 Điều 9 " + TT + ").",
    t("d9:k1:a"), t("d9:k1:b"))
add("thu_tuc", "Khi nào thí sinh được báo thời gian, địa điểm thi bằng lái?",
    "Trước kỳ sát hạch ít nhất 02 ngày làm việc, Phòng Cảnh sát giao thông phải thông báo cho trung tâm sát hạch và thí "
    "sinh về thời gian, địa điểm tổ chức sát hạch, qua Cổng Dịch vụ công quốc gia, tài khoản định danh điện tử hoặc hình "
    "thức phù hợp khác (khoản 5 Điều 9 " + TT + ").", t("d9:k5"))
add("thu_tuc", "Học lái xe ở trung tâm thì ai nộp hồ sơ sát hạch và hồ sơ gồm những gì?",
    "Cơ sở đào tạo lái xe nộp hồ sơ, gồm báo cáo đề nghị tổ chức sát hạch theo mẫu 02 Phụ lục VII kèm danh sách thí sinh "
    "theo mẫu 03 Phụ lục VII và hồ sơ đề nghị sát hạch của từng cá nhân theo khoản 2 Điều 16 (khoản 1 Điều 16 " + TT + ").",
    t("d16:k1"), t("d16:k2"))
add("thu_tuc", "Giấy khám sức khỏe nộp khi thi bằng lái phải là bản giấy hay bản điện tử?",
    "Là giấy khám sức khỏe của người lái xe còn hiệu lực dưới dạng bản điện tử; chỉ khi hệ thống bị lỗi mới dùng bản giấy do "
    "cơ sở khám bệnh, chữa bệnh đủ tiêu chuẩn cấp (điểm b khoản 2 Điều 16 " + TT + ").", t("d16:k2:b"), t("d16:k2"))
add("thu_tuc", "Người nước ngoài đăng ký thi bằng lái ở Việt Nam cần thêm giấy tờ gì?",
    "Cần bản sao hoặc bản sao điện tử một trong các giấy tờ: chứng minh thư ngoại giao, chứng minh thư công vụ, thị thực "
    "hoặc thẻ tạm trú còn thời hạn từ 90 ngày trở lên, thẻ thường trú còn giá trị. Nộp bản sao thì phải xuất trình bản chính "
    "để đối chiếu, trừ bản sao có giá trị sử dụng thay bản chính theo pháp luật về chứng thực (điểm c khoản 2 Điều 16 " + TT
    + ").", t("d16:k2:c"), t("d16:k2"))
add("thu_tuc", "Thi bằng lái bị trượt, muốn đăng ký thi lại thì hồ sơ cần thêm gì?",
    "Cần thêm biên bản tổng hợp kết quả sát hạch của các kỳ sát hạch trước (điểm d khoản 2 Điều 16 " + TT + "). Thí sinh tự "
    "bảo quản biên bản tổng hợp kết quả sát hạch (khoản 4 Điều 17), nên cần giữ lại sau mỗi kỳ thi.",
    t("d16:k2:d"), t("d17:k4"))

# ===== Cấp, cấp lại (Điều 19, 20)
add("thu_tuc", "Thi đỗ rồi muốn nhận bằng lái thẻ cứng (PET) thì bao lâu có và nhận ở đâu?",
    "Nếu có nhu cầu cấp giấy phép lái xe bằng vật liệu PET, Cục Cảnh sát giao thông hoặc Phòng Cảnh sát giao thông in và trả "
    "trong thời hạn 3,5 ngày làm việc kể từ ngày kết thúc kỳ sát hạch; nhận tại Phòng Cảnh sát giao thông hoặc qua cơ sở đào "
    "tạo (nếu có), trung tâm sát hạch hoặc dịch vụ bưu chính theo yêu cầu (khoản 1 Điều 19 " + TT + ").", t("d19:k1"))
add("thu_tuc", "Bằng lái ô tô quá hạn phải sát hạch lại, muốn ôn tập hoặc thi lại khi trượt thì đăng ký ở đâu?",
    "Muốn ôn tập thì đăng ký với cơ sở đào tạo lái xe hoặc trung tâm sát hạch lái xe để được hướng dẫn (điểm b khoản 2 Điều "
    "19 " + TT + "). Sát hạch không đạt mà có nhu cầu thì đăng ký với Phòng Cảnh sát giao thông để sát hạch lại (điểm c).",
    t("d19:k2:b"), t("d19:k2:c"))
add("quy_tac", "Trường hợp nào bị mất bằng lái mà không được cấp lại?",
    "Không cấp lại khi thông tin giấy phép lái xe không có trong hệ thống thông tin giấy phép lái xe tại Cục Cảnh sát giao "
    "thông hoặc không có trong bảng kê danh sách cấp (sổ quản lý), hoặc người vi phạm pháp luật về trật tự, an toàn giao "
    "thông đường bộ chưa thực hiện xong yêu cầu giải quyết, xử lý vụ việc vi phạm hành chính (khoản 2 Điều 20 " + TT + ").",
    t("d20:k2"))

# ===== Đổi (Điều 21)
add("thu_tuc", "bằng lái bị gãy, mờ hết chữ thì làm sao",
    "Giấy phép lái xe bị hỏng không còn sử dụng được thuộc trường hợp được đổi (điểm a khoản 1 Điều 21 " + TT + "). Hồ sơ đổi "
    "gồm giấy khám sức khỏe của người lái xe còn hiệu lực (bản điện tử) (điểm a khoản 2); cá nhân lập 01 bộ hồ sơ gửi trực "
    "tuyến tại Cổng Dịch vụ công quốc gia, ứng dụng định danh Quốc gia hoặc các ứng dụng của lực lượng Công an nhân dân và "
    "nộp lệ phí đổi giấy phép lái xe (điểm a khoản 3).", t("d21:k1:a"), t("d21:k2:a"), t("d21:k3:a"))
add("thu_tuc", "Chưa có tài khoản định danh mức độ 2 thì đổi bằng lái nộp hồ sơ ở đâu?",
    "Người dân chưa có định danh mức độ 2, chưa có dữ liệu giấy phép lái xe trong hệ thống hoặc gặp lỗi hệ thống Cổng Dịch "
    "vụ công quốc gia thì nộp hồ sơ trực tiếp tại Công an cấp xã nơi bố trí điểm tiếp nhận (điểm a khoản 3 Điều 21 " + TT
    + ").", t("d21:k3:a"))
add("thu_tuc", "Hồ sơ đổi bằng lái chưa đúng quy định thì bao lâu được hướng dẫn bổ sung?",
    "Phòng Cảnh sát giao thông hoặc Công an cấp xã hướng dẫn nội dung cần bổ sung hoặc sửa đổi trong thời hạn 02 ngày làm "
    "việc kể từ ngày nhận hồ sơ; giấy phép lái xe không thuộc đối tượng được đổi thì thông báo không tiếp nhận hồ sơ (điểm b "
    "khoản 3 Điều 21 " + TT + ").", t("d21:k3:b"))
add("thu_tuc", "Đổi bằng lái nộp online thì có nhờ người khác nhận bằng hộ được không?",
    "Bằng được trả tại Phòng Cảnh sát giao thông, Công an cấp xã nơi bố trí điểm tiếp nhận hoặc qua dịch vụ bưu chính theo "
    "yêu cầu; nhưng nếu nộp hồ sơ trực tuyến thì giấy phép lái xe được trả cho đúng cá nhân đổi giấy phép lái xe (điểm d "
    "khoản 3 Điều 21 " + TT + ").", t("d21:k3:d"))

# ===== Đổi bằng quân sự, trong Công an nhân dân (Điều 22, 23)
add("thu_tuc", "Xuất ngũ muốn đổi bằng lái quân sự sang bằng lái dân sự cần hồ sơ gì?",
    "Hồ sơ gồm: bản sao giấy tờ chứng minh thôi không còn phục vụ trong Quân đội nhân dân; giấy khám sức khỏe của người lái "
    "xe còn hiệu lực (bản điện tử); giấy phép lái xe quân sự còn thời hạn hoặc xác nhận của cơ quan có thẩm quyền của Bộ "
    "Quốc phòng về việc đã được cấp và còn thời hạn (khoản 2 Điều 22 " + TT + "). Bằng quân sự hạng CX được đổi sang hạng C "
    "(điểm b khoản 1).", t("d22:k2:a"), t("d22:k2:b"), t("d22:k2:c"), t("d22:k1:b"))
add("thu_tuc", "Đổi bằng lái quân sự thì nộp hồ sơ ở đâu, có phải nộp ảnh không?",
    "Cá nhân nộp trực tiếp 01 bộ hồ sơ đến Phòng Cảnh sát giao thông hoặc Công an cấp xã; được chụp ảnh trực tiếp, dùng ảnh "
    "trong dữ liệu căn cước hoặc gửi ảnh chân dung nền trắng kích thước 3 cm x 4 cm tại nơi tiếp nhận; xuất trình bản chính "
    "giấy tờ chứng minh thôi phục vụ trong Quân đội để đối chiếu và nộp lệ phí (điểm a khoản 3 Điều 22 " + TT + ").",
    t("d22:k3:a"))
add("thu_tuc", "Thôi phục vụ trong Công an, muốn đổi bằng lái thì cần hồ sơ gì?",
    "Hồ sơ gồm: giấy phép lái xe (nếu không có trong cơ sở dữ liệu hoặc sổ quản lý giấy phép lái xe trong Công an nhân dân), "
    "hoặc bản cam kết nếu bị mất bằng mà còn hồ sơ gốc; bản sao giấy tờ chứng minh thôi phục vụ trong Công an nhân dân hoặc "
    "công văn đề nghị của đơn vị; giấy khám sức khỏe của người lái xe còn hiệu lực (bản điện tử) (khoản 2 Điều 23 " + TT
    + ").", t("d23:k2:a"), t("d23:k2:b"), t("d23:k2:c"))
add("quy_tac", "Trường hợp nào không được đổi bằng lái trong Công an nhân dân?",
    "Không đổi khi giấy phép lái xe bị tẩy xóa thông tin; người vi phạm pháp luật về trật tự, an toàn giao thông đường bộ "
    "chưa thực hiện xong yêu cầu xử lý vụ việc vi phạm hành chính; hoặc người không có thông tin trong hệ thống thông tin "
    "giấy phép lái xe tại Cục Cảnh sát giao thông hoặc bảng kê danh sách cấp (sổ quản lý) (điểm c khoản 1 Điều 23 " + TT
    + ").", t("d23:k1:c"))

# ===== IDP (Điều 27, 29)
add("thu_tuc", "Xin giấy phép lái xe quốc tế trực tiếp thì phải mang theo những gì?",
    "Phải xuất trình bản chính giấy phép lái xe quốc gia do Việt Nam cấp; được chụp ảnh trực tiếp hoặc gửi 01 ảnh chân dung "
    "nền trắng kích thước 3 cm x 4 cm; xuất trình hộ chiếu, thẻ thường trú (đối với người nước ngoài) và nộp lệ phí khi hồ "
    "sơ được tiếp nhận (điểm b khoản 1 Điều 29 " + TT + ").", t("d29:k1:b"), t("d29:k1"))
add("thu_tuc", "Người nước ngoài có thẻ tạm trú và bằng lái của nước họ thì xin IDP ở Việt Nam cần hồ sơ gì, bao lâu?",
    "Áp dụng với bằng lái do quốc gia thành viên điều ước quốc tế mà Việt Nam là thành viên cấp, còn giá trị. Hồ sơ gồm bản "
    "dịch giấy phép lái xe nước ngoài ra tiếng Việt được bảo chứng chất lượng dịch thuật, đóng dấu giáp lai với bản sao giấy "
    "phép; bản sao thẻ tạm trú hoặc thẻ thường trú (hoặc chứng minh thư ngoại giao, công vụ); 01 ảnh chân dung nền trắng "
    "3 cm x 4 cm (điểm a khoản 2 Điều 29 " + TT + "). IDP được cấp trong thời hạn 2,5 ngày làm việc kể từ ngày nhận đủ hồ sơ "
    "hợp lệ (điểm c).", t("d29:k2"), t("d29:k2:a"), t("d29:k2:c"))
add("quy_tac", "Số trên giấy phép lái xe quốc tế do Việt Nam cấp gồm những gì?",
    "Số IDP gồm ký hiệu phân biệt quốc gia của Việt Nam đối với giao thông quốc tế là VN và 12 chữ số sau là số giấy phép lái "
    "xe quốc gia (khoản 3 Điều 27 " + TT + ").", t("d27:k3"))
add("doi_thuong", "bằng lái quốc tế của VN nhìn như nào vậy",
    "IDP là một quyển sổ kích thước A6 (148 mm x 105 mm), có ký hiệu bảo mật, bìa màu xám, các trang giấy bên trong màu "
    "trắng (khoản 1 Điều 27 " + TT + ").", t("d27:k1"))

# ===== Sát hạch cho người khuyết tật, người dân tộc thiểu số (Điều 13, 14)
add("quy_tac", "Người khuyết tật thi bằng B số tự động thì sát hạch thế nào?",
    "Thí sinh thực hiện đủ nội dung và trình tự sát hạch theo Điều 4 tại trung tâm sát hạch lái xe. Với người khuyết tật bàn "
    "chân phải, bàn tay phải hoặc bàn tay trái thì có hai sát hạch viên ngồi trên xe chấm điểm trực tiếp phần lái xe trong "
    "hình và trên đường (khoản 2 Điều 13 " + TT + ").", t("d13:k2:a"), t("d13:k2:b"))
add("quy_tac", "Người khuyết tật thi bằng A1 để lái xe mô tô ba bánh thì sát hạch những phần nào?",
    "Thí sinh sát hạch lý thuyết và sát hạch lái xe trong hình theo khoản 1, 2 Điều 4 và Phụ lục I, tại trung tâm sát hạch "
    "hoặc sân tập lái dùng để sát hạch lái xe mô tô đủ điều kiện, có hai sát hạch viên chấm điểm trực tiếp (điểm a khoản 1 "
    "Điều 13 " + TT + ").", t("d13:k1:a"), t("d13:k1"))
add("quy_tac", "Người dân tộc thiểu số không biết đọc, viết tiếng Việt thi lý thuyết bằng A1 thế nào?",
    "Nội dung lý thuyết gồm các câu hỏi về pháp luật trật tự, an toàn giao thông đường bộ, kỹ thuật lái xe, quy tắc ứng xử, "
    "văn hóa giao thông và phòng, chống tác hại của rượu, bia; sát hạch bằng hình thức hỏi - đáp, sử dụng phương pháp trắc "
    "nghiệm trên giấy theo mục II phần A Phụ lục I (khoản 1 Điều 14 " + TT + ").", t("d14:k1:a"), t("d14:k1:b"))

out = ROOT / "data/train/drafts/gplx_04.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
