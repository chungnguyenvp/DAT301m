"""Đợt 11c G5: thủ tục đăng kiểm (TT 30/2026/TT-BXD) ở các Điều chưa có mẫu thủ tục: kiểm định lần đầu, kiểm định khí
thải xe đăng ký tạm thời, cấp lại giấy chứng nhận kiểm định, chứng nhận xe cải tạo và cấp lại giấy chứng nhận cải tạo.
Ghi data/train/drafts/dang_kiem_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = "Thông tư 30/2026/TT-BXD"
S = []
START = 48


def t(s):
    return f"tt_30_2026_bxd:{s}@2026-07-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"dkm-{START + len(S):04d}", "chu_de": "Đăng kiểm", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


# ===== Kiểm định lần đầu, khí thải xe đăng ký tạm thời (Điều 6, 13)
add("thu_tuc", "Đưa ô tô đi kiểm định lần đầu thì phải nộp và xuất trình giấy tờ gì?",
    "Giấy tờ phải nộp: ảnh chụp số khung, số động cơ (hoặc ảnh bản chà số khung, số động cơ dán trên phiếu kiểm tra chất "
    "lượng xuất xưởng, thông báo miễn kiểm tra hoặc giấy chứng nhận chất lượng xe nhập khẩu); bản sao phiếu kiểm tra chất "
    "lượng xuất xưởng hoặc giấy chứng nhận chất lượng, bản chính giấy chứng nhận cải tạo (với xe cải tạo), chỉ nộp khi dữ "
    "liệu của Cục Đăng kiểm Việt Nam chưa chia sẻ được hoặc gặp sự cố. Giấy tờ phải xuất trình: giấy tờ về đăng ký xe và "
    "giấy chứng nhận kiểm định thiết bị nâng, bình chịu áp lực nếu xe có lắp (Điều 6 " + TT + ").",
    t("d6:k1:a"), t("d6:k1:b"), t("d6:k2:a"), t("d6:k2:b"))
add("thu_tuc", "Muốn kiểm định xe bên ngoài cơ sở đăng kiểm thì phải nộp thêm giấy gì?",
    "Phải nộp văn bản đề nghị kiểm định ngoài cơ sở đăng kiểm theo mẫu số 02 Phụ lục VII, áp dụng cho các trường hợp kiểm "
    "định ngoài cơ sở đăng kiểm tại khoản 14 Điều 3 (điểm c khoản 1 Điều 6 " + TT + ").", t("d6:k1:c"))
add("thu_tuc", "Xe máy sản xuất trong nước đang đăng ký tạm thời đi kiểm định khí thải cần giấy tờ gì?",
    "Giấy tờ phải nộp là bản sao phiếu kiểm tra chất lượng xuất xưởng, chỉ nộp khi dữ liệu của Cục Đăng kiểm Việt Nam chưa "
    "chia sẻ được hoặc gặp sự cố; giấy tờ phải xuất trình là giấy tờ về đăng ký xe tạm thời (khoản 1 Điều 13 " + TT + ").",
    t("d13:k1:a"), t("d13:k1:b"), t("d13:k1"))
add("thu_tuc", "Xe máy nhập khẩu chạy rà trước khi thử nghiệm khí thải thì hồ sơ kiểm định gồm gì?",
    "Phải nộp văn bản đề nghị kiểm định khí thải và bản thông số kỹ thuật xe nhập khẩu chạy rà theo mẫu số 01 Phụ lục VII, "
    "kèm bản dịch tiếng Việt có chứng thực phiếu kiểm tra chất lượng xuất xưởng của nhà sản xuất nước ngoài; xuất trình giấy "
    "tờ về đăng ký xe tạm thời (khoản 2 Điều 13 " + TT + ").", t("d13:k2:a"), t("d13:k2:b"))

# ===== Cấp lại giấy chứng nhận, tem kiểm định (Điều 10, 16, 17)
add("thu_tuc", "Ô tô đổi biển số thì xin cấp lại giấy chứng nhận kiểm định cần nộp gì?",
    "Nộp đơn đề nghị cấp lại giấy chứng nhận kiểm định, tem kiểm định theo mẫu Phụ lục IX và ảnh chụp xe theo điểm b khoản "
    "1 Điều 4 (áp dụng cả khi xe đổi màu nền biển số); xuất trình giấy tờ về đăng ký xe (Điều 16 " + TT + ").",
    t("d16:k1:a"), t("d16:k1:b"), t("d16:k2"))
add("thu_tuc", "Chuyển ô tô sang kinh doanh vận tải, xin cấp lại giấy kiểm định thì cần ảnh chụp gì?",
    "Cần ảnh chụp thể hiện xe có lắp thiết bị giám sát hành trình, thiết bị ghi nhận hình ảnh người lái xe, thiết bị ghi "
    "nhận hình ảnh khoang chở khách phù hợp với loại xe (điểm c khoản 1 Điều 16 " + TT + "), cùng đơn đề nghị cấp lại theo "
    "mẫu Phụ lục IX.", t("d16:k1:c"), t("d16:k1:a"))
add("thu_tuc", "Nộp hồ sơ cấp lại giấy chứng nhận, tem kiểm định theo những cách nào?",
    "Nộp 01 bộ hồ sơ trực tuyến trên Cổng Dịch vụ công quốc gia hoặc ứng dụng đăng kiểm của Cục Đăng kiểm Việt Nam, hoặc nộp "
    "trực tiếp, qua hệ thống bưu chính tới cơ sở đăng kiểm. Hồ sơ không đạt thì cơ sở đăng kiểm thông báo theo mẫu Phụ lục "
    "I; hồ sơ đạt thì cơ sở đăng kiểm cấp lại tem trực tiếp hoặc qua bưu chính (Điều 17 " + TT + ").", t("d17"))
add("quy_tac", "Ô tô đổi chủ, đổi biển số thì đi kiểm định có cần làm lại hồ sơ phương tiện không?",
    "Không phải lập lại. Khi thông tin về chủ sở hữu, biển số đăng ký xe thay đổi, cơ sở đăng kiểm cập nhật thông tin vào "
    "phiếu hồ sơ phương tiện và phần mềm quản lý kiểm định sau khi kiểm định xe (điểm a khoản 1 Điều 10 " + TT + ").",
    t("d10:k1"), t("d10:k1:a"))

# ===== Chứng nhận xe cải tạo (Điều 21, 22)
add("thu_tuc", "Hồ sơ đề nghị chứng nhận xe cải tạo nộp ở đâu và gồm những gì?",
    "Chủ xe hoặc người được ủy quyền nộp 01 bộ hồ sơ trực tuyến (Cổng Dịch vụ công quốc gia, ứng dụng đăng kiểm), trực "
    "tiếp hoặc qua bưu chính tới bất kỳ cơ sở đăng kiểm nào trên cả nước. Giấy tờ phải nộp gồm: văn bản đề nghị theo mẫu Phụ "
    "lục XVII; hồ sơ thiết kế cải tạo theo Phụ lục XIV; ảnh chụp xe tại xưởng của cơ sở cải tạo; biên bản kiểm tra xuất "
    "xưởng xe cải tạo; tài liệu thông số kỹ thuật; bảng kê hệ thống, tổng thành, phụ tùng thay thế; phiếu cân khối lượng "
    "sau cải tạo; giấy ủy quyền nếu người làm thủ tục không phải chủ xe (Điều 21 " + TT + ").",
    t("d21"), t("d21:k1:a"), t("d21:k1:b"), t("d21:k1:c"), t("d21:k1:d"), t("d21:k1:i"))
add("thu_tuc", "Khi cơ sở đăng kiểm kiểm tra thực tế xe cải tạo thì phải xuất trình giấy tờ gì?",
    "Xuất trình giấy tờ về đăng ký xe (xe nhập khẩu đã qua sử dụng chưa đăng ký thì xuất trình bản sao thông báo miễn kiểm "
    "tra hoặc giấy chứng nhận chất lượng xe nhập khẩu) và giấy chứng nhận kiểm định thiết bị nâng, bình chịu áp lực nếu xe "
    "có lắp (khoản 2 Điều 21 " + TT + ").", t("d21:k2:a"), t("d21:k2:b"))
add("thu_tuc", "Nộp hồ sơ cải tạo xe thì bao lâu cơ sở đăng kiểm xem xét xong?",
    "Trong 01 ngày làm việc kể từ khi nhận hồ sơ, cơ sở đăng kiểm kiểm tra thành phần hồ sơ (điểm a khoản 1 Điều 22 " + TT
    + "); trong 03 ngày làm việc kể từ ngày tiếp nhận, kiểm tra, đánh giá hồ sơ thiết kế cải tạo (khoản 2). Xe phải lập hồ "
    "sơ thiết kế được kiểm tra thực tế trong 03 ngày kể từ ngày thông báo kiểm tra (điểm a khoản 3); xe không phải lập hồ "
    "sơ thiết kế được kiểm tra ngay trong ngày nhận đủ hồ sơ (điểm b khoản 3).",
    t("d22:k1:a"), t("d22:k2"), t("d22:k3:a"), t("d22:k3:b"))
add("thu_tuc", "Hồ sơ thiết kế cải tạo bị yêu cầu bổ sung thì có bao lâu để bổ sung?",
    "Trong thời hạn 30 ngày kể từ ngày cơ sở đăng kiểm thông báo nội dung cần bổ sung, sửa đổi, người nộp hồ sơ có trách "
    "nhiệm bổ sung, hoàn thiện hồ sơ thiết kế cải tạo (điểm b khoản 2 Điều 22 " + TT + ").", t("d22:k2:b"))
add("tinh_huong", "Xe tôi cải tạo xong đi kiểm tra không đạt. Tôi được sửa trong bao lâu?",
    "Cơ sở đăng kiểm thông báo rõ nội dung không đạt; xe được khắc phục trong thời hạn 30 ngày kể từ ngày thông báo. Quá thời "
    "hạn mà không khắc phục hoặc kiểm tra lại vẫn không đạt thì thủ tục chứng nhận cải tạo phải làm lại từ đầu (điểm b khoản "
    "5 Điều 22 " + TT + ").", t("d22:k5:b"))
add("thu_tuc", "Kiểm tra xe cải tạo đạt thì được cấp mấy bản giấy chứng nhận cải tạo?",
    "Cơ sở đăng kiểm cấp giấy chứng nhận cải tạo (bản giấy hoặc bản điện tử): 01 bản cho chủ xe hoặc người được ủy quyền để "
    "làm thủ tục cấp đổi chứng nhận đăng ký xe, 01 bản lưu hồ sơ chứng nhận xe cải tạo và 01 bản lưu hồ sơ phương tiện "
    "(điểm a khoản 5 Điều 22 " + TT + ").", t("d22:k5:a"))
add("quy_tac", "Cơ sở đăng kiểm có được từ chối nhận hồ sơ cải tạo xe không?",
    "Có. Cơ sở đăng kiểm có quyền từ chối tiếp nhận đối với xe cải tạo bị cấm cải tạo theo quy định của pháp luật và thông "
    "báo theo mẫu Phụ lục I cho người nộp hồ sơ (điểm b khoản 1 Điều 22 " + TT + ").", t("d22:k1:b"))

# ===== Cấp lại giấy chứng nhận cải tạo (Điều 23)
add("thu_tuc", "Mất hoặc hỏng giấy chứng nhận cải tạo xe thì xin cấp lại ở đâu, cần gì và bao lâu?",
    "Cấp lại tại bất kỳ cơ sở đăng kiểm nào trên cả nước, khi giấy bị mất, hỏng hoặc sai thông tin (khoản 1, 2 Điều 23 " + TT
    + "). Nộp đơn đề nghị theo mẫu Phụ lục IX (kèm giấy bị hỏng hoặc sai thông tin) và xuất trình giấy tờ về đăng ký xe hoặc "
    "bản chính chứng nhận thu hồi đăng ký, biển số (khoản 3). Thời hạn cấp lại là 01 ngày làm việc nếu hồ sơ lưu tại cơ sở "
    "đăng kiểm đó hoặc trên phần mềm, 1,5 ngày làm việc nếu hồ sơ lưu tại cơ sở đăng kiểm khác (khoản 4).",
    t("d23:k1"), t("d23:k2"), t("d23:k3:a"), t("d23:k3:b"), t("d23:k4"))
add("thu_tuc", "Giấy chứng nhận cải tạo cũ có thời hạn, muốn cấp lại để đổi giấy đăng ký xe thì làm thế nào?",
    "Nộp 01 bộ hồ sơ đến bất kỳ cơ sở đăng kiểm nào: đơn đề nghị theo mẫu Phụ lục IX, giấy chứng nhận xe cơ giới cải tạo đã "
    "được cấp hoặc dữ liệu tra cứu; xuất trình giấy tờ về đăng ký xe hoặc bản chính chứng nhận thu hồi (điểm a khoản 5 Điều "
    "23 " + TT + "). Cơ sở đăng kiểm đối chiếu thông số xe thực tế, phù hợp thì cấp lại; không phù hợp thì phải làm lại thủ "
    "tục theo Điều 21 và Điều 22 (điểm b).", t("d23:k5:a"), t("d23:k5:b"))

out = ROOT / "data/train/drafts/dang_kiem_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
