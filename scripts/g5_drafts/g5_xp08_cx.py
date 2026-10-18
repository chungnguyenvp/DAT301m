"""C3: tình huống nhiều hành vi độc lập; viết tay, không ghép tích Descartes.

Mỗi mục A giữ riêng hành vi, câu dẫn tiền phạt và chế tài đã đọc từ nguồn.
Các tình huống chỉ xét xử phạt hành chính, không gây tai nạn, trừ khi nói khác.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
S = []
A = {}


def t(unit, date="2025-01-01"):
    return f"nd_168_2024:{unit}@{date}"


def act(name, unit, label, fine, sanction=None, date="2025-01-01", extra=()):
    article, clause, point = unit.split(":")
    refs = [t(unit, date), t(f"{article}:{clause}")]
    answer = f"{label}: phạt tiền từ {fine} (điểm {point} khoản {clause[1:]} Điều {article[1:]} {ND})"
    if sanction:
        su, text = sanction
        refs.append(t(su))
        ar, cl, pt = su.split(":")
        answer += f"; {text} (điểm {pt} khoản {cl[1:]} Điều {ar[1:]})"
    for ref, text in extra:
        refs.append(ref)
        answer += "; " + text
    A[name] = (answer + ".", refs, sanction is not None and "trừ điểm" in sanction[1])


# Xe mô tô: khoản 12, 13 Điều 7 đã được đối chiếu cho từng hành vi.
M1 = "200.000 đồng đến 400.000 đồng"
M2 = "400.000 đồng đến 600.000 đồng"
M3 = "600.000 đồng đến 800.000 đồng"
M4 = "800.000 đồng đến 1.000.000 đồng"
M5 = "1.000.000 đồng đến 2.000.000 đồng"
M6 = "2.000.000 đồng đến 3.000.000 đồng"
M7 = "4.000.000 đồng đến 6.000.000 đồng"
M8 = "6.000.000 đồng đến 8.000.000 đồng"
MP2 = ("d7:k13:a", "hành vi này bị trừ điểm giấy phép lái xe 02 điểm")
MP4 = ("d7:k13:b", "hành vi này bị trừ điểm giấy phép lái xe 04 điểm")
MP6 = ("d7:k13:c", "hành vi này bị trừ điểm giấy phép lái xe 06 điểm")
for name, unit, label, fine, sanction, date in [
    ("m_mu", "d7:k2:h", "Không đội mũ bảo hiểm khi lái xe mô tô", M2, None, "2025-01-01"),
    ("m_quai", "d7:k2:h", "Đội mũ bảo hiểm nhưng không cài quai đúng quy cách khi lái xe mô tô", M2, None, "2025-01-01"),
    ("m_khach", "d7:k2:i", "Chở người lớn không đội mũ bảo hiểm, không thuộc trường hợp ngoại lệ", M2, None, "2025-01-01"),
    ("m_den", "d7:k1:g", "Không bật đèn chiếu sáng khi đi xe mô tô ban đêm", M1, None, "2025-01-01"),
    ("m_coi", "d7:k1:i", "Bấm còi ban đêm trong khu đông dân cư bằng xe không được ưu tiên", M1, None, "2025-01-01"),
    ("m_pha", "d7:k1:h", "Dùng đèn chiếu xa khi gặp xe ngược chiều, không có dải phân cách chống chói", M1, None, "2025-01-01"),
    ("m_lan", "d7:k1:e", "Chuyển làn không có tín hiệu báo trước", M1, None, "2026-08-15"),
    ("m_vuot_tin", "d7:k1:b", "Không có tín hiệu trước khi vượt xe", M1, None, "2025-01-01"),
    ("m_du", "d7:k1:d", "Chở người ngồi sau sử dụng ô", M1, None, "2025-01-01"),
    ("m_7", "d7:k2:b", "Chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h", M2, None, "2025-01-01"),
    ("m_do", "d7:k2:e", "Đỗ xe tại nơi có biển Cấm đỗ xe", M2, None, "2025-01-01"),
    ("m_via_do", "d7:k2:d", "Đỗ xe trên vỉa hè trái phép", M2, None, "2025-01-01"),
    ("m_re", "d7:k3:a", "Rẽ không có tín hiệu báo hướng rẽ tại đường giao nhau", M3, None, "2025-01-01"),
    ("m_cau", "d7:k3:c", "Dừng xe trên cầu", M3, None, "2025-01-01"),
    ("m_sailan", "d7:k3:d", "Đi không đúng làn đường quy định", M3, None, "2025-01-01"),
    ("m_cong", "d7:k3:e", "Người lái mang vác vật cồng kềnh", M3, None, "2025-01-01"),
    ("m_keo", "d7:k3:g", "Điều khiển xe mô tô kéo theo xe khác", M3, None, "2025-01-01"),
    ("m_ham", "d7:k3:h", "Chạy trong hầm đường bộ không sử dụng đèn chiếu sáng gần", M3, None, "2025-01-01"),
    ("m_ngang", "d7:k3:k", "Chạy dàn hàng ngang từ 03 xe trở lên", M3, None, "2025-01-01"),
    ("m_15", "d7:k4:a", "Chạy quá tốc độ quy định từ 10 km/h đến 20 km/h", M4, None, "2025-01-01"),
    ("m_vuot", "d7:k4:c", "Vượt xe tại đoạn có biển cấm vượt đối với xe đang lái", M4, None, "2025-01-01"),
    ("m_quayham", "d7:k4:d", "Quay đầu xe trong hầm đường bộ", M4, None, "2025-01-01"),
    ("m_dt", "d7:k4:đ", "Dùng tay cầm và sử dụng điện thoại khi lái xe", M4, MP4, "2025-01-01"),
    ("m_tainghe", "d7:k4:đ", "Sử dụng tai nghe âm thanh khi lái xe, không phải thiết bị trợ thính", M4, MP4, "2025-01-01"),
    ("m_bobo", "d7:k5:b", "Chuyển hướng không nhường người đi bộ đang qua vạch dành cho người đi bộ", M5, MP2, "2025-01-01"),
    ("m_nhanh", "d7:k6:c", "Từ đường nhánh ra đường chính không giảm tốc độ và nhường đường", M6, MP2, "2025-01-01"),
    ("m_vong", "d7:k6:d", "Không giảm tốc độ và nhường xe từ bên trái tại nơi có báo hiệu vòng xuyến", M6, MP2, "2025-01-01"),
    ("m_nguoc", "d7:k7:a", "Đi ngược chiều đường một chiều thông thường bằng xe không được ưu tiên", M7, MP2, "2025-01-01"),
    ("m_via", "d7:k7:a", "Chạy trên vỉa hè để tránh ùn xe, không phải đi qua để vào nhà, cơ quan", M7, MP2, "2025-01-01"),
    ("m_caotoc", "d7:k7:b", "Xe mô tô thông thường đi vào đường cao tốc, không phục vụ quản lý, bảo trì", M7, MP6, "2025-01-01"),
    ("m_do_den", "d7:k7:c", "Không chấp hành đèn đỏ", M7, MP4, "2025-01-01"),
    ("m_uutien", "d7:k7:đ", "Không nhường xe ưu tiên đang phát tín hiệu ưu tiên đi làm nhiệm vụ", M7, MP4, "2025-01-01"),
    ("m_25", "d7:k8:a", "Chạy quá tốc độ quy định trên 20 km/h", M8, MP4, "2025-01-01"),
]:
    act(name, unit, label, fine, sanction, date)

# Ô tô: từng điểm đã được đối chiếu khoản 15, 16 Điều 6.
C1 = "400.000 đồng đến 600.000 đồng"
C2 = "600.000 đồng đến 800.000 đồng"
C3 = "800.000 đồng đến 1.000.000 đồng"
C4 = "2.000.000 đồng đến 3.000.000 đồng"
C5 = "4.000.000 đồng đến 6.000.000 đồng"
C6 = "6.000.000 đồng đến 8.000.000 đồng"
CP2 = ("d6:k16:a", "hành vi này bị trừ điểm giấy phép lái xe 02 điểm")
CP4 = ("d6:k16:b", "hành vi này bị trừ điểm giấy phép lái xe 04 điểm")
CP6 = ("d6:k16:c", "hành vi này bị trừ điểm giấy phép lái xe 06 điểm")
for name, unit, label, fine, sanction, date in [
    ("c_day", "d6:k3:k", "Người lái không thắt dây đai an toàn khi xe chạy", C3, None, "2025-01-01"),
    ("c_khach", "d6:k3:l", "Chở người không thắt dây đai an toàn tại vị trí có dây khi xe đang chạy", C3, None, "2025-01-01"),
    ("c_coi", "d6:k1:đ", "Bấm còi ban đêm trong khu đông dân cư bằng xe không được ưu tiên", C1, None, "2025-01-01"),
    ("c_rado", "d6:k1:b", "Ra khỏi vị trí đỗ không có tín hiệu báo cho xe khác", C1, None, "2025-01-01"),
    ("c_lan", "d6:k2:a", "Chuyển làn không có tín hiệu báo trước trên đường không phải cao tốc", C2, None, "2026-08-15"),
    ("c_doc", "d6:k2:d", "Đỗ xe trên dốc không chèn bánh", C2, None, "2025-01-01"),
    ("c_dung", "d6:k2:đ", "Dừng xe tại nơi có biển Cấm dừng xe và đỗ xe trên đường thông thường, không gây ùn tắc", C2, None, "2025-01-01"),
    ("c_8", "d6:k3:a", "Chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h", C3, None, "2025-01-01"),
    ("c_pha", "d6:k3:b", "Dùng đèn chiếu xa khi gặp xe ngược chiều, không có dải phân cách chống chói", C3, None, "2025-01-01"),
    ("c_re", "d6:k3:c", "Rẽ không có tín hiệu báo hướng rẽ tại đường giao nhau", C3, None, "2025-01-01"),
    ("c_do", "d6:k3:e", "Đỗ xe nơi có biển Cấm đỗ xe trên đường thông thường, không gây ùn tắc", C3, None, "2025-01-01"),
    ("c_den", "d6:k3:g", "Không bật đèn chiếu sáng khi lái ô tô ban đêm", C3, None, "2025-01-01"),
    ("c_ham", "d6:k3:n", "Chạy trong hầm đường bộ không sử dụng đèn chiếu sáng gần", C3, None, "2025-01-01"),
    ("c_etc", "d6:k4:a", "Xe không gắn thẻ đầu cuối đi vào làn thu phí điện tử tự động không dừng", C4, CP2, "2025-01-01"),
    ("c_cau", "d6:k4:b", "Dừng xe trên cầu ở nơi tổ chức giao thông không cho phép, không gây ùn tắc", C4, CP2, "2025-01-01"),
    ("c_nhuongvuot", "d6:k4:d", "Không nhường đường cho xe xin vượt dù đủ điều kiện an toàn", C4, CP2, "2025-01-01"),
    ("c_lui", "d6:k4:e", "Lùi xe trên đường một chiều thông thường", C4, None, "2025-01-01"),
    ("c_quay", "d6:k4:k", "Quay đầu tại nơi có biển cấm quay đầu đối với xe đang lái, không gây ùn tắc", C4, None, "2025-01-01"),
    ("c_vuot", "d6:k5:a", "Vượt tại đoạn đường có biển cấm vượt đối với xe đang lái", C5, CP2, "2025-01-01"),
    ("c_sailan", "d6:k5:b", "Đi không đúng làn đường quy định, không phải làn thu phí điện tử", C5, CP2, "2025-01-01"),
    ("c_khancap", "d6:k5:d", "Chạy ở làn dừng xe khẩn cấp trên đường cao tốc", C5, CP2, "2025-01-01"),
    ("c_15", "d6:k5:đ", "Chạy quá tốc độ quy định từ 10 km/h đến 20 km/h", C5, CP2, "2025-01-01"),
    ("c_lanct", "d6:k5:g", "Chuyển làn không có tín hiệu báo trước trên đường cao tốc", C5, CP2, "2026-08-15"),
    ("c_dt", "d6:k5:h", "Dùng tay cầm và sử dụng điện thoại khi ô tô đang di chuyển", C5, CP4, "2025-01-01"),
    ("c_nhanh", "d6:k5:n", "Từ đường nhánh ra đường chính không giảm tốc độ và nhường đường", C5, CP2, "2025-01-01"),
    ("c_30", "d6:k6:a", "Chạy quá tốc độ quy định trên 20 km/h đến 35 km/h", C6, CP4, "2025-01-01"),
    ("c_uutien", "d6:k6:b", "Không nhường xe ưu tiên đang phát tín hiệu ưu tiên đi làm nhiệm vụ", C6, CP4, "2025-01-01"),
    ("c_40", "d6:k7:a", "Chạy quá tốc độ quy định trên 35 km/h", "12.000.000 đồng đến 14.000.000 đồng", CP6, "2025-01-01"),
    ("c_dendo", "d6:k9:b", "Không chấp hành đèn đỏ", "18.000.000 đồng đến 20.000.000 đồng", CP4, "2025-01-01"),
]:
    act(name, unit, label, fine, sanction, date)

# Xe đạp, xe đạp máy: Điều 9 không quy định trừ điểm GPLX.
for name, unit, label, fine in [
    ("b_dt", "d9:k1:h", "Dùng tay cầm và sử dụng điện thoại khi đi xe đạp hoặc xe đạp máy", "100.000 đồng đến 200.000 đồng"),
    ("b_re", "d9:k1:b", "Chuyển hướng xe đạp hoặc xe đạp máy không báo hiệu trước", "100.000 đồng đến 200.000 đồng"),
    ("b_ngang", "d9:k1:g", "Đi xe đạp dàn hàng ngang từ 03 xe trở lên", "100.000 đồng đến 200.000 đồng"),
    ("b_den", "d9:k1:i", "Đi xe đạp ban đêm không có đèn hoặc báo hiệu trước và sau xe", "100.000 đồng đến 200.000 đồng"),
    ("b_do", "d9:k1:k", "Để xe đạp ở vỉa hè trái phép", "100.000 đồng đến 200.000 đồng"),
    ("b_keo", "d9:k2:c", "Đi xe đạp kéo theo xe khác", "150.000 đồng đến 250.000 đồng"),
    ("b_tin", "d9:k2:đ", "Đi xe đạp hoặc xe đạp máy không chấp hành đèn đỏ", "150.000 đồng đến 250.000 đồng"),
    ("b_nguoc", "d9:k3:c", "Đi xe đạp ngược chiều đường một chiều", "300.000 đồng đến 400.000 đồng"),
    ("b_mu", "d9:k4:d", "Lái xe đạp máy không đội mũ bảo hiểm", M2),
]:
    act(name, unit, label, fine)

# Giấy tờ còn hiệu lực nhưng không mang: chỉ dùng khi kinh doanh vận tải.
act("m_bh", "d18:k2:b", "Lái xe mô tô không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự còn hiệu lực", "200.000 đồng đến 300.000 đồng")
act("c_bh", "d18:k4:c", "Lái ô tô không có chứng nhận bảo hiểm bắt buộc trách nhiệm dân sự còn hiệu lực", M2)
act("m_quen", "d18:k2:d", "Lái xe mô tô kinh doanh vận tải không mang GPLX phù hợp, còn hiệu lực, không thuộc trường hợp GPLX quốc tế", "200.000 đồng đến 300.000 đồng")
act("c_quen", "d18:k3:a", "Lái ô tô kinh doanh vận tải không mang GPLX phù hợp, còn hiệu lực, không thuộc trường hợp GPLX không hợp lệ", "300.000 đồng đến 400.000 đồng")
act("m_guong", "d14:k1:a", "Lái xe mô tô không có gương chiếu hậu bên trái", M2,
    extra=((t("d14:k6:a", "2026-08-15"), "buộc thay thế thiết bị đủ tiêu chuẩn an toàn kỹ thuật (điểm a khoản 6 Điều 14)"),))
act("c_coihong", "d13:k2:b", "Lái ô tô có còi nhưng còi không có tác dụng", M2,
    extra=((t("d13:k11:a"), "buộc lắp đầy đủ thiết bị hoặc thay thế thiết bị đủ tiêu chuẩn, quy chuẩn an toàn kỹ thuật hoặc khôi phục tính năng kỹ thuật theo quy định (điểm a khoản 11 Điều 13)"),))
act("c_kiem", "d13:k5:a", "Người lái không phải chủ xe điều khiển ô tô có tem kiểm định hết hạn dưới 01 tháng", "3.000.000 đồng đến 4.000.000 đồng",
    ("d13:k13:a", "hành vi này bị trừ điểm giấy phép lái xe 02 điểm"),
    extra=((t("d47:k3:b"), "Trường hợp người điều khiển đồng thời là chủ phương tiện thì bị xử phạt theo điểm, khoản tương ứng của Điều 32 Nghị định 168/2024/NĐ-CP (điểm b khoản 3 Điều 47)"),))

PRINCIPLE = (" Một người thực hiện nhiều hành vi vi phạm hoặc vi phạm hành chính nhiều lần thì bị xử phạt về từng hành vi, "
             "trừ trường hợp vi phạm hành chính nhiều lần được Chính phủ quy định là tình tiết tăng nặng. "
             "Một hành vi vi phạm chỉ bị xử phạt một lần (điểm d khoản 1 Điều 3 Luật Xử lý vi phạm hành chính, hợp nhất 90/VBHN-VPQH năm 2026).")
XL = "vbhn_90_2026_xlvphc:d3:k1:d@2026-07-01"


def add(q, *names, chat=False):
    refs, answers = [], []
    for name in names:
        answer, citations, _ = A[name]
        answers.append(answer)
        refs.extend(citations)
    answer = " ".join(answers) + PRINCIPLE
    refs.append(XL)
    if sum(A[name][2] for name in names) > 1:
        answer += (" Nếu bị xử phạt trong cùng một lần thì chỉ áp dụng trừ điểm đối với hành vi bị trừ nhiều điểm nhất "
                   "(điểm b khoản 1 Điều 50 Nghị định 168/2024/NĐ-CP).")
        refs.append(t("d50:k1:b"))
    S.append({"key": f"xp-{1001 + len(S):04d}", "chu_de": "Xử phạt",
              "loai": "doi_thuong" if chat else "tinh_huong", "cau_hoi": q,
              "dap_an": answer, "can_cu": list(dict.fromkeys(refs))})


# Mỗi truyện là một lựa chọn viết tay; các hành vi tách biệt về bản chất.
add("Tôi đi mô tô về khuya, quên bật đèn lúc 21 giờ và còn không có bảo hiểm bắt buộc còn hiệu lực. Tôi bị phạt những lỗi nào nếu chưa gây tai nạn?", "m_den", "m_bh")
add("Tôi chạy mô tô một mình quá tốc độ 7 km/h, sau đó dừng trên cầu chụp ảnh. Không có tai nạn. Mỗi hành vi bị phạt bao nhiêu?", "m_7", "m_cau")
add("Tôi chở bạn trưởng thành không đội mũ bằng mô tô đi chơi, không cấp cứu hay áp giải ai; khi rẽ ở ngã tư tôi không bật xi nhan. Không gây tai nạn thì tôi bị phạt thế nào?", "m_khach", "m_re")
add("Tôi đi mô tô trên đường thường, chuyển làn không báo trước rồi đỗ tại biển Cấm đỗ xe. Không xảy ra tai nạn, có bị xử phạt cả hai hành vi không?", "m_lan", "m_do")
add("Tôi chạy mô tô lên vỉa hè để tránh ùn xe, không phải vào nhà hay cơ quan, đồng thời không đội mũ. Không gây tai nạn thì hai việc này bị phạt thế nào?", "m_via", "m_mu")
add("Tôi dùng mô tô kéo một xe đạp hỏng; trên đoạn đường khác tôi lại vượt một ô tô ở nơi có biển cấm vượt đối với xe mình. Không gây tai nạn thì xử lý từng lỗi thế nào?", "m_keo", "m_vuot")
add("Tôi đi mô tô qua hầm không bật đèn chiếu gần, ra khỏi hầm mới dừng đỗ trái phép trên vỉa hè. Không xảy ra tai nạn thì bị phạt các lỗi nào?", "m_ham", "m_via_do")
add("mình chạy mô tô với hai bạn thành hàng ngang ba xe rồi rẽ ở ngã tư ko bật xi nhan chưa gây tai nạn thì mình bị phạt sao", "m_ngang", "m_re", chat=True)
add("Tôi lái mô tô một mình quá tốc độ 25 km/h và không đội mũ, không gây tai nạn. Mức xử phạt riêng của hai lỗi là gì?", "m_25", "m_mu")
add("Tôi chạy mô tô đeo tai nghe nhạc, tại một giao lộ tôi đi tiếp dù đèn đỏ. Chưa xảy ra tai nạn thì từng lỗi bị phạt ra sao?", "m_tainghe", "m_do_den")
add("Tôi đi mô tô vào vòng xuyến có báo hiệu nhưng không giảm tốc độ, không nhường xe từ bên trái; sau đó tôi đỗ dưới biển Cấm đỗ xe. Không gây tai nạn thì xử phạt thế nào?", "m_vong", "m_do")
add("Tôi điều khiển mô tô rẽ ở ngã tư, không nhường người đi bộ đang qua vạch; tôi cũng không có bảo hiểm bắt buộc còn hiệu lực. Không gây tai nạn thì bị phạt hai lỗi thế nào?", "m_bobo", "m_bh")
add("Tôi chở một người cầm ô phía sau mô tô, rồi chuyển làn mà không báo trước. Nếu không gây tai nạn thì tôi là người lái bị phạt riêng từng việc ra sao?", "m_du", "m_lan")
add("Tôi chạy mô tô từ đường nhánh ra đường chính không giảm tốc độ, không nhường xe; lúc đó tôi cũng không cài quai mũ đúng quy cách. Chưa gây tai nạn thì bị phạt gì?", "m_nhanh", "m_quai")
add("Tôi đi mô tô tư nhân không phục vụ quản lý, bảo trì mà đi vào đường cao tốc, đồng thời không có bảo hiểm bắt buộc còn hiệu lực. Không gây tai nạn thì các lỗi xử lý thế nào?", "m_caotoc", "m_bh")
add("Tôi lái mô tô không nhường xe cứu thương đang phát tín hiệu ưu tiên đi làm nhiệm vụ; trước đó tôi đã vượt xe mà không có tín hiệu vượt. Không xảy ra tai nạn thì từng việc phạt ra sao?", "m_uutien", "m_vuot_tin")
add("Tôi chạy mô tô trong hầm rồi quay đầu ngay trong hầm. Khi đó tôi không đội mũ, không gây tai nạn. Mỗi hành vi bị phạt mức nào?", "m_quayham", "m_mu")
add("Tôi đi mô tô sai làn đường quy định và còn mang vác một bó ống cồng kềnh. Chưa gây tai nạn thì có thể bị phạt riêng hai hành vi thế nào?", "m_sailan", "m_cong")

add("Tôi lái ô tô đi qua đèn đỏ, sau đó đỗ xe dưới biển Cấm đỗ xe trên đường thường, không gây ùn tắc hay tai nạn. Hai lỗi phạt ra sao?", "c_dendo", "c_do")
add("Tôi chạy ô tô quá tốc độ 8 km/h, ra khỏi một chỗ đỗ khác trong chuyến đi lại không báo tín hiệu cho xe khác. Không có tai nạn thì mỗi việc bị phạt bao nhiêu?", "c_8", "c_rado")
add("Tôi lái ô tô thông thường trên đường thường, chuyển làn không xi nhan rồi bấm còi một lần lúc 23 giờ trong khu đông dân cư. Không gây tai nạn thì phạt từng lỗi thế nào?", "c_lan", "c_coi")
add("Tôi chạy ô tô trên cao tốc, chuyển làn không có tín hiệu báo trước trong khi bản thân không thắt dây an toàn. Không có tai nạn thì mức phạt riêng là gì?", "c_lanct", "c_day")
add("mình chạy ô tô ko bật đèn lúc 20 giờ lại ko có bảo hiểm bắt buộc còn hiệu lực chưa gây tai nạn thì mỗi lỗi phạt sao", "c_den", "c_bh", chat=True)
add("Tôi lái ô tô quá tốc độ 15 km/h trên đường thường, còn người lớn ngồi ghế có dây an toàn lại không thắt dây. Không xảy ra tai nạn thì người lái bị phạt thế nào?", "c_15", "c_khach")
add("Tôi lái ô tô không thắt dây đai khi chạy, sau đó đỗ trên dốc mà không chèn bánh. Không xảy ra tai nạn thì hai hành vi bị phạt bao nhiêu?", "c_day", "c_doc")
add("Tôi lái ô tô qua hầm không bật đèn chiếu sáng gần; ra khỏi hầm, tôi rẽ ở ngã tư không báo hướng rẽ. Không gây tai nạn thì từng lỗi chịu mức nào?", "c_ham", "c_re")
add("Tôi lùi ô tô trên đường một chiều trong phố rồi tại một vị trí khác quay đầu nơi có biển cấm quay đầu đối với ô tô. Không gây ùn tắc, không có tai nạn thì hai việc phạt thế nào?", "c_lui", "c_quay")
add("Tôi lái ô tô vượt xe trên đoạn có biển cấm vượt đối với xe mình; trong chuyến đó tôi còn không thắt dây đai an toàn. Nếu không gây tai nạn thì từng hành vi bị phạt gì?", "c_vuot", "c_day")
add("Tôi lái ô tô ra đường chính từ đường nhánh mà không giảm tốc độ, không nhường đường. Xe cũng không có bảo hiểm bắt buộc còn hiệu lực, nhưng chưa gây tai nạn. Tôi bị phạt hai việc ra sao?", "c_nhanh", "c_bh")
add("Tôi lái ô tô quá tốc độ 30 km/h và không có bảo hiểm bắt buộc còn hiệu lực. Không xảy ra tai nạn thì mỗi lỗi có mức phạt nào?", "c_30", "c_bh")
add("Tôi lái ô tô không nhường xe cứu hỏa đang phát tín hiệu ưu tiên đi làm nhiệm vụ; tại chặng khác tôi dừng dưới biển Cấm dừng xe và đỗ xe trên đường thường. Không ùn tắc, không tai nạn thì phạt thế nào?", "c_uutien", "c_dung")
add("Tôi dừng ô tô trên cầu để ngắm cảnh dù không được phép; trước đó lái xe trên đường mà không có bảo hiểm bắt buộc còn hiệu lực. Không gây ùn tắc hay tai nạn thì mỗi hành vi xử lý thế nào?", "c_cau", "c_bh")
add("Tôi lái ô tô rẽ tại ngã tư không báo hướng rẽ, khi xe chạy lại chở người trưởng thành ngồi ghế có dây nhưng không thắt dây an toàn. Không gây tai nạn thì tôi bị phạt riêng từng lỗi thế nào?", "c_re", "c_khach")
add("Tôi chạy ô tô sai làn đường quy định trên đường phố thông thường, sau đó đỗ dưới biển Cấm đỗ xe mà không gây ùn tắc. Không tai nạn thì hai lỗi xử lý ra sao?", "c_sailan", "c_do")
add("Tôi điều khiển ô tô một mình quá tốc độ 40 km/h và không thắt dây an toàn. Chưa gây tai nạn thì từng hành vi bị phạt thế nào?", "c_40", "c_day")
add("Tôi chạy ô tô vượt đèn đỏ rồi ở chặng sau cầm điện thoại sử dụng khi xe di chuyển. Không gây tai nạn thì mức phạt và chế tài riêng mỗi hành vi là gì?", "c_dendo", "c_dt")
add("em lái ô tô ra khỏi chỗ đỗ ko báo tín hiệu rồi chuyển làn ko xi nhan trên đường thường lại ko có bảo hiểm bắt buộc còn hiệu lực chưa có tai nạn thì phạt sao", "c_rado", "c_lan", "c_bh", chat=True)
add("Tôi đi ô tô lúc 21 giờ không bật đèn, bản thân không thắt dây an toàn và còn không có bảo hiểm bắt buộc còn hiệu lực. Không gây tai nạn thì xử lý riêng các lỗi thế nào?", "c_den", "c_day", "c_bh")

add("Tôi đi xe đạp thường, cầm điện thoại xem tin nhắn rồi đi qua ngã tư khi đèn đỏ. Chưa gây tai nạn thì hai hành vi bị phạt thế nào?", "b_dt", "b_tin")
add("Tôi đạp xe cùng hai bạn thành hàng ngang ba xe, sau đó rẽ không báo hiệu trước. Chưa gây tai nạn thì riêng tôi bị phạt những gì?", "b_ngang", "b_re")
add("Tôi đi xe đạp thường lúc 20 giờ, không có đèn hay báo hiệu phía trước và phía sau; rồi đi ngược chiều đường một chiều. Không gây tai nạn thì mỗi hành vi bị phạt bao nhiêu?", "b_den", "b_nguoc")
add("Tôi lái xe đạp máy không đội mũ bảo hiểm, đến ngã tư lại đi qua đèn đỏ. Không có tai nạn thì phạt từng lỗi thế nào?", "b_mu", "b_tin")
add("Tôi đi xe đạp thường kéo theo xe đạp hỏng của bạn, sau đó để xe trên vỉa hè trái phép. Không gây tai nạn thì bị phạt riêng thế nào?", "b_keo", "b_do")
add("Tôi lái xe đạp máy không đội mũ, vừa đi vừa dùng điện thoại cầm tay và rẽ không báo hiệu trước. Không gây tai nạn thì từng việc chịu mức phạt nào?", "b_mu", "b_dt", "b_re")
add("Tôi chạy xe ôm bằng mô tô, có GPLX trong nước phù hợp còn hiệu lực nhưng quên mang, đồng thời không đội mũ bảo hiểm. Không tai nạn thì phạt hai lỗi ra sao?", "m_quen", "m_mu")
add("Tôi lái taxi kinh doanh vận tải, có GPLX phù hợp còn hiệu lực và hợp lệ nhưng quên mang; khi xe đang chạy tôi cũng không thắt dây an toàn. Không tai nạn thì hai hành vi phạt thế nào?", "c_quen", "c_day")

add("mình chạy mô tô ko có gương trái lại ko đội mũ chưa gây tai nạn thì phạt từng lỗi bn có phải lắp gương lại ko", "m_guong", "m_mu", chat=True)
add("Tôi lái ô tô có còi bị hỏng không kêu, rồi rẽ ở ngã tư không có tín hiệu báo hướng rẽ. Không gây tai nạn thì từng lỗi bị phạt và phải khắc phục gì?", "c_coihong", "c_re")
add("Tôi là tài xế thuê, không phải chủ ô tô, lái xe của công ty có tem kiểm định hết hạn 10 ngày và không thắt dây an toàn khi xe chạy. Không gây tai nạn thì riêng tôi chịu các chế tài nào?", "c_kiem", "c_day")
add("Tôi lái ô tô của công ty, không phải chủ xe, tem kiểm định hết hạn 10 ngày; tôi còn dùng điện thoại cầm tay khi xe đang di chuyển và không có bảo hiểm bắt buộc còn hiệu lực. Không gây tai nạn thì các lỗi của tôi bị xử lý thế nào?", "c_kiem", "c_dt", "c_bh")


if __name__ == "__main__":
    out = ROOT / "data/train/drafts/xu_phat_08_cx.jsonl"
    out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
    print(f"{out.name}: {len(S)} mẫu")
