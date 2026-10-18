"""Đợt 2b G5: GPLX. TT 65/2024/TT-BCA (sửa bởi TT 105/2026) về kiểm tra để phục hồi điểm; TT 36/2024/TT-BYT về sức khỏe
người lái xe. Ghi data/train/drafts/gplx_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T65 = "Thông tư 65/2024/TT-BCA"
T105 = "Thông tư 105/2026/TT-BCA"
TYT = "Thông tư 36/2024/TT-BYT"
S = []
START = 76


def a(s, d="2025-01-01"):
    return f"tt_65_2024_bca:{s}@{d}"


def b(s):
    return f"tt_105_2026_bca:{s}@2026-07-01"


def y(s):
    return f"tt_36_2024_byt:{s}@2025-01-01"


N7 = "2026-07-01"
TIEP = b("d6:k3")
TIEPT = (" Cấu trúc bài kiểm tra này được tiếp tục thực hiện đến hết ngày 30 tháng 6 năm 2027 (khoản 3 Điều 6 " + T105
         + ").")


def add(loai, q, ans, *can_cu):
    S.append({"key": f"gp-{START + len(S):04d}", "chu_de": "GPLX", "loai": loai, "cau_hoi": q, "dap_an": ans,
              "can_cu": list(can_cu)})


# ===== Kiểm tra kiến thức pháp luật để phục hồi điểm (TT 65, TT 105)
add("quy_tac", "Ai được tham gia kiểm tra kiến thức pháp luật để phục hồi điểm giấy phép lái xe?",
    "Người được tham gia kiểm tra kiến thức pháp luật về trật tự, an toàn giao thông đường bộ là người có giấy phép lái "
    "xe bị trừ hết điểm (Điều 3 " + T65 + ").", a("d3"))
add("thu_tuc", "Hồ sơ đăng ký kiểm tra để phục hồi điểm giấy phép lái xe gồm những gì?",
    "Theo khoản 1 Điều 7 " + T65 + " (nội dung có hiệu lực từ ngày 01/7/2026), hồ sơ gồm đơn đề nghị kiểm tra kiến thức "
    "pháp luật về trật tự, an toàn giao thông đường bộ theo Mẫu số 01 và giấy khám sức khỏe của người đăng ký kiểm tra do "
    "cơ sở y tế có thẩm quyền cấp còn giá trị sử dụng (bản giấy hoặc bản điện tử).",
    a("d7:k1", N7), a("d7:k1:a", N7), a("d7:k1:b", N7))
add("thu_tuc", "Nộp hồ sơ đăng ký kiểm tra phục hồi điểm bằng lái theo những hình thức nào?",
    "Hồ sơ nộp cho Công an cấp xã, cơ quan có thẩm quyền kiểm tra trước ngày đăng ký kiểm tra bằng một trong các hình "
    "thức: trực tuyến tại Cổng dịch vụ công quốc gia, Cổng dịch vụ công Bộ Công an, qua Ứng dụng định danh quốc gia hoặc "
    "các ứng dụng của lực lượng Công an nhân dân; qua dịch vụ bưu chính; hoặc trực tiếp (điểm b khoản 2 Điều 7 " + T65
    + ", nội dung có hiệu lực từ ngày 01/7/2026).", a("d7:k2:b", N7), a("d7:k2", N7))
add("doi_thuong", "bị trừ hết điểm bằng lái thì có phải về quê nộp hồ sơ thi phục hồi ko",
    "Không bắt buộc. Người đăng ký kiểm tra có thể nộp hồ sơ cho Công an cấp xã, cơ quan có thẩm quyền kiểm tra tại nơi "
    "thường trú, tạm trú hoặc nơi ở hiện tại (khoản 3 Điều 7 " + T65 + ", nội dung có hiệu lực từ ngày 01/7/2026).",
    a("d7:k3", N7))
add("tinh_huong", "Tôi thi kiểm tra phục hồi điểm bằng lái nhưng không đạt. Bao lâu thì tôi được thi lại?",
    "Người dự kiểm tra có kết quả không đạt yêu cầu có thể đăng ký kiểm tra lại sau 07 ngày làm việc kể từ ngày kết thúc "
    "lần kiểm tra trước (khoản 4 Điều 6 " + T65 + ", nội dung có hiệu lực từ ngày 01/7/2026). Khi đăng ký kiểm tra lại, "
    "nếu giấy khám sức khỏe còn giá trị sử dụng thì chỉ cần gửi đơn đề nghị kiểm tra (khoản 3 Điều 7).",
    a("d6:k4", N7), a("d7:k3", N7))
add("quy_tac", "Bài kiểm tra phục hồi điểm cho người có bằng A1 gồm bao nhiêu câu và bao nhiêu điểm thì đạt?",
    "Người có giấy phép lái xe hạng A1 làm bài trong 19 phút, gồm 25 câu hỏi trắc nghiệm, mỗi câu 01 điểm, trong đó có "
    "01 câu điểm liệt. Kết quả từ 21/25 điểm trở lên là đạt, nhưng nếu trả lời sai câu điểm liệt thì không đạt (điểm a "
    "khoản 3 Điều 6 " + T65 + ")." + TIEPT, a("d6:k3:a"), a("d6:k3"), TIEP)
add("quy_tac", "Người có bằng A hoặc B1 làm bài kiểm tra phục hồi điểm thì cần đạt bao nhiêu điểm?",
    "Người có giấy phép lái xe hạng A, B1 làm bài trong 19 phút, gồm 25 câu hỏi trắc nghiệm, trong đó có 01 câu điểm "
    "liệt; đạt từ 23/25 điểm trở lên và không sai câu điểm liệt thì đạt yêu cầu (điểm b khoản 3 Điều 6 " + T65 + ")."
    + TIEPT, a("d6:k3:b"), a("d6:k3"), TIEP)
add("doi_thuong", "thi phục hồi điểm bằng B mấy câu, đúng bao nhiêu câu thì đậu",
    "Người có giấy phép lái xe hạng B làm bài trong 20 phút, gồm 30 câu hỏi trắc nghiệm, có 01 câu điểm liệt; đạt từ "
    "27/30 điểm trở lên và không sai câu điểm liệt thì đạt yêu cầu (điểm c khoản 3 Điều 6 " + T65 + ")." + TIEPT,
    a("d6:k3:c"), a("d6:k3"), TIEP)
add("quy_tac", "Bài kiểm tra phục hồi điểm cho người có bằng C1 được quy định thế nào?",
    "Người có giấy phép lái xe hạng C1 làm bài trong 22 phút, gồm 35 câu hỏi trắc nghiệm, có 01 câu điểm liệt; đạt từ "
    "32/35 điểm trở lên và không sai câu điểm liệt thì đạt yêu cầu (điểm d khoản 3 Điều 6 " + T65 + ")." + TIEPT,
    a("d6:k3:d"), a("d6:k3"), TIEP)
add("quy_tac", "Người có bằng C làm bài kiểm tra phục hồi điểm trong bao lâu và bao nhiêu điểm thì đạt?",
    "Người có giấy phép lái xe hạng C làm bài trong 24 phút, gồm 40 câu hỏi trắc nghiệm, có 01 câu điểm liệt; đạt từ "
    "36/40 điểm trở lên và không sai câu điểm liệt thì đạt yêu cầu (điểm đ khoản 3 Điều 6 " + T65 + ")." + TIEPT,
    a("d6:k3:đ"), a("d6:k3"), TIEP)
add("quy_tac", "Bài kiểm tra phục hồi điểm cho người có bằng D hoặc các hạng kéo rơ moóc gồm bao nhiêu câu?",
    "Người có giấy phép lái xe hạng D1, D2, D, BE, C1E, CE, D1E, D2E, DE làm bài trong 26 phút, gồm 45 câu hỏi trắc "
    "nghiệm, có 01 câu điểm liệt; đạt từ 41/45 điểm trở lên và không sai câu điểm liệt thì đạt yêu cầu (điểm e khoản 3 "
    "Điều 6 " + T65 + ")." + TIEPT, a("d6:k3:e"), a("d6:k3"), TIEP)
add("tinh_huong", "Bằng lái ô tô của tôi bị trừ hết điểm. Hiện nay tôi cần đạt những gì để được phục hồi điểm?",
    "Theo khoản 5 Điều 6 " + T105 + ", kể từ ngày 01/7/2026, người có giấy phép lái xe ô tô bị trừ hết điểm được phục "
    "hồi điểm khi có kết quả kiểm tra lý thuyết kiến thức pháp luật đạt yêu cầu theo các điểm c, d, đ và e khoản 3 Điều 6 "
    + T65 + ", tức là chỉ cần đạt bài kiểm tra lý thuyết tương ứng với hạng giấy phép của mình.", b("d6:k5"))
add("quy_tac", "Người có bằng mô tô bị trừ hết điểm được phục hồi điểm khi nào?",
    "Người có giấy phép lái xe mô tô bị trừ hết điểm được phục hồi điểm khi có kết quả kiểm tra lý thuyết kiến thức pháp "
    "luật đạt yêu cầu theo điểm a, điểm b khoản 3 Điều 6 " + T65 + " (điểm a khoản 5 Điều 6).", a("d6:k5:a"), a("d6:k5"))
add("quy_tac", "Kiểm tra phục hồi điểm bằng lái được thực hiện theo hình thức nào?",
    "Người dự kiểm tra làm bài kiểm tra trắc nghiệm trên máy tính theo phần mềm kiểm tra kiến thức pháp luật về trật tự, "
    "an toàn giao thông đường bộ (điểm a khoản 2 Điều 6 " + T65 + "). Nội dung kiểm tra lấy theo bộ câu hỏi lý thuyết "
    "dùng cho sát hạch, cấp giấy phép lái xe do Cục Cảnh sát giao thông xây dựng và ban hành (điểm a khoản 1 Điều 6).",
    a("d6:k2:a"), a("d6:k1:a", "2025-03-01"))
add("thu_tuc", "Khi đi kiểm tra phục hồi điểm bằng lái cần mang theo giấy tờ gì?",
    "Người dự kiểm tra có mặt đúng thời gian, địa điểm được thông báo và sử dụng một trong các giấy tờ: thẻ căn cước, thẻ "
    "căn cước công dân; giấy phép lái xe; giấy chứng nhận căn cước (với người gốc Việt Nam chưa xác định được quốc tịch); "
    "thẻ thường trú, thẻ tạm trú hoặc giấy tờ nhập cảnh, xuất cảnh hợp lệ (với người nước ngoài) để đối chiếu thông tin "
    "(khoản 5 Điều 7 " + T65 + ", nội dung có hiệu lực từ ngày 01/7/2026).", a("d7:k5", N7))
add("tinh_huong", "Tôi là người nước ngoài không biết tiếng Việt, bị trừ hết điểm bằng lái. Khi đi kiểm tra phục hồi điểm "
    "tôi làm thế nào?",
    "Người dự kiểm tra là người nước ngoài không biết đọc, viết tiếng Việt sử dụng người phiên dịch do cơ quan có thẩm "
    "quyền kiểm tra thuê hoặc tự thuê; người phiên dịch phải dịch đúng, đủ câu hỏi trong phần mềm và hướng dẫn đầy đủ "
    "cách thức kiểm tra (khoản 7 Điều 7 " + T65 + ", nội dung có hiệu lực từ ngày 01/7/2026).", a("d7:k7", N7))
add("thu_tuc", "Cơ quan kiểm tra phải thông báo lịch kiểm tra phục hồi điểm cho người đăng ký trước bao lâu?",
    "Trước ngày kiểm tra ít nhất 02 ngày làm việc sau khi nhận đủ hồ sơ hợp lệ, cơ quan có thẩm quyền kiểm tra thông báo "
    "thời gian, địa điểm cho người đăng ký qua email, điện thoại hoặc hình thức khác ghi trong đơn (khoản 4 Điều 7 " + T65
    + "). Ngoài ra, định kỳ trước ngày 25 hằng tháng, cơ quan kiểm tra công bố dự kiến lịch kiểm tra của tháng tiếp "
    "theo trên Cổng thông tin điện tử (khoản 4 Điều 8). Cả hai nội dung có hiệu lực từ ngày 01/7/2026.",
    a("d7:k4", N7), a("d8:k4", N7))
add("quy_tac", "Cơ quan nào có thẩm quyền tổ chức kiểm tra kiến thức pháp luật để phục hồi điểm giấy phép lái xe?",
    "Cơ quan có thẩm quyền kiểm tra gồm Cục Cảnh sát giao thông (khoản 1 Điều 4 " + T65 + ") và Phòng Cảnh sát giao "
    "thông Công an tỉnh, thành phố (khoản 2 Điều 4, nội dung có hiệu lực từ ngày 01/7/2026).", a("d4:k1"),
    a("d4:k2", N7))
add("quy_tac", "Kết thúc buổi kiểm tra phục hồi điểm, người dự kiểm tra có được giữ biên bản không?",
    "Có. Kết thúc kiểm tra, người dự kiểm tra ký biên bản theo Mẫu số 02; biên bản lập thành 02 bản, 01 bản lưu tại cơ "
    "quan có thẩm quyền kiểm tra và 01 bản giao cho người dự kiểm tra (khoản 9 Điều 7 " + T65 + ", nội dung có hiệu "
    "lực từ ngày 01/7/2026).", a("d7:k9", N7))

# ===== Sức khỏe người lái xe (TT 36/2024/TT-BYT)
add("quy_tac", "Tiêu chuẩn sức khỏe của người lái xe được chia thành mấy nhóm?",
    "Theo khoản 2 Điều 2 " + TYT + ", tiêu chuẩn sức khỏe chia theo 3 nhóm: Nhóm 1 áp dụng khi khám để cấp giấy phép "
    "lái xe hạng A1, B1 và người điều khiển xe máy chuyên dùng; Nhóm 2 áp dụng cho hạng A và B; Nhóm 3 áp dụng cho các "
    "hạng C1, C, D1, D2, D, BE, C1E, CE, D1E, D2E và DE.", y("d2:k2"), y("d2:k2:a"), y("d2:k2:b"), y("d2:k2:c"))
add("doi_thuong", "đi khám sức khỏe để thi bằng B thì khám theo nhóm nào",
    "Khám sức khỏe để cấp giấy phép lái xe hạng A và B áp dụng tiêu chuẩn sức khỏe Nhóm 2 (điểm b khoản 2 Điều 2 " + TYT
    + ").", y("d2:k2:b"), y("d2:k2"))
add("quy_tac", "Khám sức khỏe để thi bằng lái xe tải hạng C áp dụng tiêu chuẩn nhóm nào?",
    "Áp dụng tiêu chuẩn sức khỏe Nhóm 3, dành cho trường hợp khám để cấp giấy phép lái xe hạng C1, C, D1, D2, D, BE, C1E, "
    "CE, D1E, D2E và DE (điểm c khoản 2 Điều 2 " + TYT + ").", y("d2:k2:c"), y("d2:k2"))
add("quy_tac", "Người lái xe gắn máy có phải áp dụng quy định khám sức khỏe của Thông tư 36/2024/TT-BYT không?",
    "Không. Thông tư 36/2024/TT-BYT không áp dụng đối với người điều khiển xe gắn máy (khoản 2 Điều 1).", y("d1:k2"))
add("quy_tac", "Khám sức khỏe định kỳ cho người hành nghề lái xe ô tô có phải xét nghiệm ma túy, nồng độ cồn không?",
    "Có. Nội dung khám sức khỏe định kỳ đối với người hành nghề lái xe ô tô bao gồm xét nghiệm ma túy và xét nghiệm nồng "
    "độ cồn (điểm c khoản 3 Điều 3 " + TYT + ").", y("d3:k3:c"), y("d3:k3"))
add("tinh_huong", "Tôi là người khuyết tật muốn thi bằng lái xe hạng B số tự động. Việc khám sức khỏe có gì khác không?",
    "Người khuyết tật đề nghị cấp giấy phép lái xe hạng A1 hoặc hạng B theo khoản 2 Điều 57 Luật Trật tự, an toàn giao "
    "thông đường bộ được khám theo tiêu chuẩn sức khỏe tại Phụ lục I nhưng không phải khám chuyên khoa Cơ Xương Khớp "
    "(khoản 4 Điều 2 " + TYT + ").", y("d2:k4"))
add("quy_tac", "Đổi bằng A1 cấp trước năm 2025 sang hạng A thì khám sức khỏe theo nhóm nào?",
    "Người có giấy phép lái xe cấp trước ngày 01/01/2025 có nhu cầu đổi, cấp lại từ hạng A1 sang hạng A theo điểm a khoản "
    "3 Điều 89 Luật Trật tự, an toàn giao thông đường bộ thì áp dụng tiêu chuẩn sức khỏe Nhóm 1 để khám (khoản 3 Điều 2 "
    + TYT + ").", y("d2:k3"))
add("doi_thuong", "giấy khám sức khỏe lái xe làm từ năm 2024 thì giờ còn dùng được ko",
    "Giấy khám sức khỏe của người lái xe cấp trước ngày 01/01/2025 (ngày " + TYT + " có hiệu lực) được tiếp tục sử dụng "
    "theo thời hạn ghi trên giấy khám sức khỏe (khoản 1 Điều 9 " + TYT + "). Nếu thời hạn ghi trên giấy đã hết thì "
    "không còn dùng được.", y("d9:k1"), y("d7:k1"))
add("quy_tac", "Dữ liệu kết quả khám sức khỏe của người lái xe gồm những thông tin gì?",
    "Theo Điều 5 " + TYT + ", cấu trúc dữ liệu gồm: phần hành chính theo Đề án 06; tên cơ sở khám bệnh, chữa bệnh thực "
    "hiện khám và ngày khám; kết quả xét nghiệm ma túy; kết luận về tình trạng sức khỏe.", y("d5"), y("d5:k3"), y("d5:k4"))

out = ROOT / "data/train/drafts/gplx_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
