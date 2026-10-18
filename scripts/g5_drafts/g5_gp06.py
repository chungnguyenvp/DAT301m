"""Đợt C8 G5: GPLX (TT 108/2026 Điều 3, 18, 28, 30, 38; Luật 36 Điều 61) và đăng kiểm (TT 30/2026 Điều 28, 29; Luật 36
Điều 41, 42) ở các khoản chưa có mẫu. Ghi data/train/drafts/gplx_dang_kiem_06.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT108 = "Thông tư 108/2026/TT-BCA"
TT30 = "Thông tư 30/2026/TT-BXD"
LUAT = "Luật Trật tự, an toàn giao thông đường bộ"
S = []
NEXT = {"gp": 170, "dkm": 65}
TOPIC = {"gp": "GPLX", "dkm": "Đăng kiểm"}


def t108(s):
    return f"tt_108_2026_bca:{s}@2026-07-01"


def t30(s):
    return f"tt_30_2026_bxd:{s}@2026-07-01"


def l36(s, d="2025-01-01"):
    return f"luat_36_2024:{s}@{d}"


def add(prefix, loai, q, a, *can_cu):
    S.append({"key": f"{prefix}-{NEXT[prefix]:04d}", "chu_de": TOPIC[prefix], "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})
    NEXT[prefix] += 1


# ===== GPLX
add("gp", "quy_tac", "Số phôi giấy phép lái xe là gì?",
    "Số phôi giấy phép lái xe là mã số do nhà sản xuất phôi ghi ở mặt sau của giấy phép lái xe, gồm 02 chữ cái và các số phía "
    "sau (khoản 1 Điều 3 " + TT108 + ").", t108("d3:k1"))
add("gp", "quy_tac", "Giấy phép lái xe quốc gia và giấy phép lái xe quốc tế khác nhau thế nào?",
    "Giấy phép lái xe quốc gia do cơ quan có thẩm quyền của từng nước cấp, có giá trị trên lãnh thổ nước đó (khoản 6 Điều 3 "
    + TT108 + "). Giấy phép lái xe quốc tế có tên tiếng Anh là International Driving Permit, gọi tắt là IDP (khoản 5 Điều 3).",
    t108("d3:k6"), t108("d3:k5"))
add("gp", "quy_tac", "Có giấy phép lái xe thì được lái những loại xe nào?",
    "Người có giấy phép lái xe được lái các hạng xe ghi trong giấy phép lái xe (khoản 4 Điều 18 " + TT108 + ").",
    t108("d18:k4"))
add("gp", "thu_tuc", "Đổi hoặc nâng hạng giấy phép lái xe thì bằng cũ được xử lý thế nào?",
    "Khi đổi, cấp giấy phép lái xe nâng hạng, Phòng Cảnh sát giao thông thu lại giấy phép lái xe cũ (nếu có) và tiêu hủy theo "
    "quy định của pháp luật về lưu trữ (khoản 5 Điều 18 " + TT108 + ").", t108("d18:k5"))
add("gp", "quy_tac", "Bằng lái thẻ PET cấp trước đây có còn giá trị không, căn cứ vào đâu để biết?",
    "Giấy phép lái xe bằng vật liệu PET, giấy phép cấp từ ngày 01 tháng 01 năm 2025 và giấy phép cấp trước khi Thông tư 108/2026 "
    "có hiệu lực là giấy phép có hiệu lực nếu số phôi, ngày cấp, ngày hết hạn in trên giấy phép trùng với thông tin trong hệ "
    "thống quản lý giấy phép lái xe, hoặc thông tin giấy phép đã được tích hợp vào tài khoản định danh điện tử, ứng dụng của "
    "lực lượng Công an nhân dân (khoản 8 Điều 18 " + TT108 + ").", t108("d18:k8"))
add("gp", "quy_tac", "Cơ quan nào quản lý việc cấp, đổi, cấp lại giấy phép lái xe trên toàn quốc?",
    "Cục Cảnh sát giao thông quản lý việc cấp, đổi, cấp lại giấy phép lái xe trên toàn quốc và cấp phôi, vật tư in giấy phép "
    "cho Phòng Cảnh sát giao thông; Cục hoặc Phòng Cảnh sát giao thông tổ chức in và trả giấy phép lái xe (khoản 1 Điều 18 "
    + TT108 + ").", t108("d18:k1"))
add("gp", "quy_tac", "Giấy phép lái xe quốc tế do Việt Nam cấp cho phép lái những hạng xe nào?",
    "Hạng xe được phép điều khiển của IDP tương ứng với các hạng xe của giấy phép lái xe quốc gia do Việt Nam cấp, theo Phụ lục "
    "XII của " + TT108 + " (Điều 28).", t108("d28"))
add("gp", "tinh_huong", "Tôi là người nước ngoài có IDP do nước tôi cấp. Tôi có được dùng IDP đó để lái xe ở Việt Nam không?",
    "Tùy điều ước quốc tế. IDP được công nhận theo điều ước quốc tế mà Việt Nam là thành viên thì việc sử dụng thực hiện theo "
    "điều ước đó (khoản 2 Điều 30 " + TT108 + "). Nếu không thuộc trường hợp này mà có giấy phép lái xe quốc gia thì phải làm thủ "
    "tục đổi sang giấy phép lái xe tương ứng của Việt Nam (điểm a khoản 7 Điều 18).", t108("d30:k2"), t108("d18:k7:a"),
    t108("d18:k7"))
add("gp", "doi_thuong", "công an xã có nhận hồ sơ đổi bằng lái ko hay phải lên tỉnh",
    "Có. Công an cấp xã có nhiệm vụ tiếp nhận, kiểm tra hồ sơ đề nghị đổi, cấp lại giấy phép lái xe (khoản 1 Điều 38 " + TT108
    + ").", t108("d38:k1"), t108("d38"))
add("gp", "quy_tac", "Ai chấm thi sát hạch lái xe và chịu trách nhiệm về kết quả?",
    "Việc sát hạch lái xe do sát hạch viên thực hiện. Sát hạch viên phải đủ điều kiện, tiêu chuẩn, được cấp thẻ sát hạch viên và "
    "chịu trách nhiệm về kết quả sát hạch của mình (khoản 5 Điều 61 " + LUAT + ").", l36("d61:k5"))
add("gp", "quy_tac", "Nội dung thi sát hạch lái xe có giống nhau cho mọi hạng bằng không?",
    "Không. Nội dung sát hạch lái xe phải phù hợp với hạng giấy phép lái xe và chương trình đào tạo lái xe (khoản 2 Điều 61 "
    + LUAT + ").", l36("d61:k2"))
add("gp", "quy_tac", "Hệ thống thông tin giấy phép lái xe được đặt ở những cơ quan nào?",
    "Hệ thống thông tin giấy phép lái xe đặt tại Cục Cảnh sát giao thông, Phòng Cảnh sát giao thông và Công an cấp xã nơi được bố "
    "trí điểm tiếp nhận (điểm b khoản 8 Điều 3 " + TT108 + ").", t108("d3:k8:b"), t108("d3:k8"))

# ===== Đăng kiểm
add("dkm", "tinh_huong", "Cơ sở đăng kiểm in sai thông tin trên giấy chứng nhận kiểm định của tôi. Cấp lại có mất tiền không?",
    "Không. Cơ sở đăng kiểm không thu giá, phí khi cấp lại giấy chứng nhận kiểm định, tem kiểm định do chính cơ sở đăng kiểm in "
    "sai thông tin (khoản 7 Điều 28 " + TT30 + ").", t30("d28:k7"))
add("dkm", "thu_tuc", "Xe thay đổi thông tin đi kiểm định ở cơ sở khác nơi quản lý hồ sơ thì hồ sơ được cập nhật trong bao lâu?",
    "Trong 03 ngày làm việc kể từ khi cấp giấy chứng nhận kiểm định, cơ sở đăng kiểm đã kiểm định gửi giấy tờ liên quan về cơ sở "
    "quản lý hồ sơ phương tiện (khoản 10 Điều 28 " + TT30 + "); trong 03 ngày làm việc kể từ khi nhận, cơ sở quản lý hồ sơ cập "
    "nhật vào hồ sơ phương tiện và phần mềm (khoản 11 Điều 28).", t30("d28:k10"), t30("d28:k11"))
add("dkm", "quy_tac", "Xe máy có phải kiểm định an toàn kỹ thuật giống ô tô không?",
    "Không. Việc kiểm định đối với xe mô tô, xe gắn máy chỉ thực hiện kiểm định khí thải, tại các cơ sở kiểm định khí thải đáp "
    "ứng quy chuẩn kỹ thuật quốc gia (khoản 2 Điều 42 " + LUAT + ").", l36("d42:k2"), l36("d42:k1"))
add("dkm", "quy_tac", "Xe mới chở từ cảng về kho, cửa hàng có phải đi kiểm định không?",
    "Không. Xe có chứng nhận về an toàn kỹ thuật và bảo vệ môi trường của cơ sở đăng kiểm hoặc chứng nhận kiểm tra xuất xưởng của "
    "nhà sản xuất thì không phải kiểm định khi di chuyển từ cửa khẩu, nơi sản xuất, lắp ráp tới kho, cảng, cửa hàng hoặc ngược "
    "lại (khoản 3 Điều 42 " + LUAT + ").", l36("d42:k3"))
add("dkm", "quy_tac", "Ai thực hiện kiểm định xe và ai cấp giấy chứng nhận kiểm định?",
    "Việc kiểm định an toàn kỹ thuật và bảo vệ môi trường xe cơ giới, xe máy chuyên dùng do đăng kiểm viên của cơ sở đăng kiểm "
    "thực hiện và được cơ sở đăng kiểm cấp giấy chứng nhận (khoản 4 Điều 42 " + LUAT + ").", l36("d42:k4", "2026-07-01"))
add("dkm", "quy_tac", "Đăng kiểm viên phải chịu trách nhiệm gì khi kiểm định xe?",
    "Đăng kiểm viên chịu trách nhiệm trước pháp luật về kết quả kiểm định và kết quả kiểm tra, đánh giá trong chứng nhận cải tạo; "
    "phải tuân thủ đúng quy định, quy trình, tiêu chuẩn, quy chuẩn kỹ thuật liên quan (Điều 29 " + TT30 + ").",
    t30("d29:k1"), t30("d29:k2"))
add("dkm", "quy_tac", "Xe nhập khẩu chỉ để trưng bày ở hội chợ có phải chứng nhận chất lượng an toàn kỹ thuật không?",
    "Không thuộc đối tượng phải bảo đảm chất lượng an toàn kỹ thuật và bảo vệ môi trường: Luật loại trừ xe để nghiên cứu khoa "
    "học, nghiên cứu phục vụ sản xuất, trưng bày, giới thiệu tại hội chợ, triển lãm thương mại (điểm a khoản 1 Điều 41 " + LUAT
    + ").", l36("d41:k1:a"), l36("d41:k1"))
add("dkm", "quy_tac", "Hãng nhập khẩu, sản xuất xe chịu trách nhiệm gì về chất lượng xe bán ra?",
    "Tổ chức, cá nhân nhập khẩu, sản xuất, lắp ráp phải tuân thủ quy định về kiểm tra, thử nghiệm, chứng nhận chất lượng; chịu "
    "trách nhiệm về chất lượng sản phẩm, việc bảo hành, bảo dưỡng xe và triệu hồi sản phẩm theo quy định của Chính phủ (khoản 5 "
    "Điều 41 " + LUAT + ").", l36("d41:k5"))

out = ROOT / "data/train/drafts/gplx_dang_kiem_06.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
