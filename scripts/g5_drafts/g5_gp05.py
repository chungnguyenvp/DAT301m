"""Đợt 11f G5: thủ tục cấp, cấp lại giấy chứng nhận giáo viên dạy thực hành lái xe và giấy phép xe tập lái (NĐ 94/2026).
Ghi data/train/drafts/gplx_05.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 94/2026/NĐ-CP"
S = []
START = 162


def n(s):
    return f"nd_94_2026:{s}@2026-07-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"gp-{START + len(S):04d}", "chu_de": "GPLX", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


add("thu_tuc", "Hồ sơ xin cấp giấy chứng nhận giáo viên dạy thực hành lái xe gồm những gì?",
    "Hồ sơ gồm: đơn đề nghị theo mẫu Phụ lục IV; bằng tốt nghiệp trung cấp chuyên nghiệp hoặc trung cấp nghề trở lên; văn bằng, "
    "chứng chỉ về trình độ nghiệp vụ sư phạm; 01 ảnh màu cỡ 3 cm x 4 cm nền màu xanh, kiểu thẻ căn cước, chụp trong thời gian "
    "không quá 06 tháng. Bằng cấp đã tích hợp vào tài khoản định danh điện tử thì có thể xuất trình qua tài khoản đó (khoản 1 "
    "Điều 12 " + ND + ").", n("d12:k1:a"), n("d12:k1:b"), n("d12:k1:c"), n("d12:k1:d"))
add("thu_tuc", "Lần đầu xin giấy chứng nhận giáo viên dạy thực hành lái xe thì phải qua những bước nào?",
    "Cá nhân đăng ký với cơ sở đào tạo lái xe để được tập huấn nghiệp vụ giáo viên dạy thực hành theo chương trình Phụ lục II "
    "(điểm a khoản 2 Điều 12 " + ND + "). Trong thời hạn không quá 02 ngày làm việc sau khi kết thúc tập huấn, cơ sở đào tạo "
    "gửi văn bản đề nghị kiểm tra (mẫu Phụ lục V) kèm hồ sơ cá nhân đến Trung tâm Phục vụ hành chính công cấp tỉnh, cấp xã, "
    "trực tiếp, qua bưu chính hoặc cổng dịch vụ công quốc gia (điểm b). Sở Xây dựng là cơ quan cấp giấy chứng nhận (khoản 1 "
    "Điều 11).", n("d12:k2:a"), n("d12:k2:b"), n("d11:k1"))
add("thu_tuc", "Mất giấy chứng nhận giáo viên dạy thực hành lái xe thì xin cấp lại cần gì và bao lâu có?",
    "Hồ sơ cấp lại khi bị mất, bị hỏng gồm đơn đề nghị và ảnh theo điểm a, điểm d khoản 1 Điều 12 (điểm a khoản 1 Điều 13 " + ND
    + "). Cá nhân nộp 01 bộ hồ sơ tại Trung tâm Phục vụ hành chính công cấp tỉnh, cấp xã, trực tiếp, qua bưu chính hoặc cổng dịch "
    "vụ công quốc gia; hồ sơ đầy đủ, hợp lệ thì được cấp trong thời gian không quá 02 ngày làm việc (khoản 2 Điều 13).",
    n("d13:k1"), n("d13:k1:a"), n("d13:k2:a"), n("d13:k2:b"))
add("thu_tuc", "Giáo viên dạy lái xe đổi tên thì xin cấp lại giấy chứng nhận cần thêm giấy tờ gì?",
    "Ngoài đơn đề nghị và ảnh, cần tài liệu về nội dung thay đổi: bản sao kèm bản chính để đối chiếu (hoặc bản sao có chứng "
    "thực, bản sao điện tử, dữ liệu điện tử hộ tịch) giấy tờ của cấp có thẩm quyền về việc đổi tên, thay đổi ngày tháng năm "
    "sinh (điểm b khoản 1 Điều 13 " + ND + ").", n("d13:k1:b"), n("d13:k1"))
add("thu_tuc", "Giấy chứng nhận giáo viên dạy thực hành lái xe cấp lại được trả dưới dạng nào?",
    "Kết quả được trả bằng bản điện tử có giá trị như bản giấy, qua VNeID, Cổng Dịch vụ công quốc gia hoặc hệ thống thông tin "
    "giải quyết thủ tục hành chính cấp tỉnh, cấp xã; nếu cá nhân cần bản giấy thì được cấp bổ sung (điểm c khoản 2 Điều 13 " + ND
    + ").", n("d13:k2:c"))
add("thu_tuc", "Cơ sở đào tạo xin cấp giấy phép xe tập lái cần hồ sơ gì và bao lâu có?",
    "Hồ sơ gồm danh sách đề nghị cấp giấy phép xe tập lái theo mẫu Phụ lục VIII; xe không thuộc sở hữu của cơ sở đào tạo thì "
    "xuất trình thêm giấy tờ chứng minh quyền sử dụng hợp pháp (khoản 1 Điều 16 " + ND + "). Cơ sở đào tạo gửi 01 bộ hồ sơ tại "
    "Trung tâm Phục vụ hành chính công cấp tỉnh, cấp xã; hồ sơ đầy đủ, hợp lệ thì được cấp trong thời gian không quá 02 ngày làm "
    "việc (khoản 2 Điều 16).", n("d16:k1:a"), n("d16:k1:b"), n("d16:k2:a"), n("d16:k2:b"))
add("quy_tac", "Giấy phép xe tập lái có thời hạn bao lâu?",
    "Giấy phép xe tập lái có hiệu lực tương ứng với thời hạn ghi trên giấy chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi "
    "trường của xe, nhưng không vượt quá thời hạn sử dụng hợp pháp đối với xe tập lái (khoản 1 Điều 15 " + ND + ").",
    n("d15:k1"))
add("thu_tuc", "Khi nào phải xin cấp lại giấy phép xe tập lái?",
    "Giấy phép xe tập lái được cấp lại khi bị mất, bị hỏng hoặc thay đổi thông tin trong giấy phép: tên cơ sở đào tạo, biển số "
    "xe, màu sơn (khoản 2 Điều 15 " + ND + "); hồ sơ và trình tự theo Điều 16.", n("d15:k2"), n("d16:k1:a"))

out = ROOT / "data/train/drafts/gplx_05.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
