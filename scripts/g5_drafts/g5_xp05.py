"""Đợt 1e G5: Xử phạt, Điều 32 NĐ 168/2024 (chủ phương tiện).
Ghi data/train/drafts/xu_phat_05.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ND = "Nghị định 168/2024/NĐ-CP"
NEW = "2026-08-15"
S = []
START = 214


def v(s, d="2025-01-01"):
    return f"nd_168_2024:d32:{s}@{d}"


L56 = "luat_36_2024:d56:k1@2025-01-01"


def add(loai, q, a, *can_cu):
    S.append({"key": f"xp-{START + len(S):04d}", "chu_de": "Xử phạt", "loai": loai, "cau_hoi": q, "dap_an": a,
              "can_cu": list(can_cu)})


def own(lo, hi, lo2, hi2, k, diem=None, dong2=" đồng"):
    where = (f"điểm {diem} khoản {k}" if diem else f"khoản {k}") + f" Điều 32 {ND}"
    return (f"phạt tiền từ {lo} đồng đến {hi} đồng đối với chủ xe là cá nhân, từ {lo2}{dong2} đến {hi2} đồng đối với "
            f"chủ xe là tổ chức ({where})")


K1 = lambda d: own("200.000", "300.000", "400.000", "600.000", 1, d)  # noqa: E731
K2 = lambda d: own("300.000", "400.000", "600.000", "800.000", 2, d)  # noqa: E731
K3 = lambda d: own("800.000", "1.000.000", "1.600.000", "2.000.000", 3, d)  # noqa: E731
K7 = lambda d: own("4.000.000", "6.000.000", "8.000.000", "12.000.000", 7, d)  # noqa: E731
# Khoản 8 viết "từ 8.000.000 đến 12.000.000 đồng" (không có "đồng" sau số đầu); giữ đúng chữ văn bản.
K8 = lambda d: own("4.000.000", "6.000.000", "8.000.000", "12.000.000", 8, d, "")  # noqa: E731
K9 = lambda d: own("4.000.000", "6.000.000", "8.000.000", "12.000.000", 9, d)  # noqa: E731
K9A = lambda d: own("5.000.000", "6.000.000", "10.000.000", "12.000.000", "9a", d)  # noqa: E731
K11 = lambda d: own("10.000.000", "12.000.000", "20.000.000", "24.000.000", 11, d)  # noqa: E731
K12 = lambda d: own("16.000.000", "18.000.000", "32.000.000", "36.000.000", 12, d)  # noqa: E731
K13 = lambda d: own("20.000.000", "26.000.000", "40.000.000", "52.000.000", 13, d)  # noqa: E731
K14 = lambda d: own("28.000.000", "30.000.000", "56.000.000", "60.000.000", 14, d)  # noqa: E731
K16 = lambda d: own("65.000.000", "75.000.000", "130.000.000", "150.000.000", 16, d)  # noqa: E731

DRV = "Trường hợp chủ phương tiện là người trực tiếp điều khiển phương tiện thì còn bị trừ điểm giấy phép lái xe"
TR2 = f"{DRV} 02 điểm (điểm a khoản 21 Điều 32)."
TR6 = f"{DRV} 06 điểm (điểm đ khoản 21 Điều 32)."
TR10 = f"{DRV} 10 điểm (điểm g khoản 21 Điều 32)."
G19 = ("Người vi phạm còn buộc làm thủ tục đổi, thu hồi, cấp mới, cấp chứng nhận đăng ký xe, biển số xe theo quy định "
       "(điểm g khoản 19 Điều 32).")
TUOC_KD = ("Ngoài ra còn bị tước quyền sử dụng chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi trường và tem kiểm "
           "định của phương tiện từ 01 tháng đến 03 tháng (điểm d khoản 18 Điều 32), đồng thời buộc khôi phục lại hình "
           "dáng, kích thước, tình trạng an toàn kỹ thuật ban đầu của xe và đăng kiểm lại trước khi đưa xe ra tham gia "
           "giao thông (điểm d khoản 19 Điều 32).")
BIEN_TT = "Ngoài ra còn bị tịch thu biển số (điểm a khoản 18 Điều 32)."

# ===== Đăng ký xe: sang tên, đổi, thu hồi
add("muc_phat", "Mua xe máy cũ nhưng không làm thủ tục sang tên (cấp đăng ký, biển số khi đổi chủ) thì bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy không làm thủ tục cấp chứng nhận đăng ký xe, biển số xe trong trường hợp thay đổi chủ xe "
    "theo quy định bị " + K3("a") + ".", v("k3:a"), v("k3"))
add("doi_thuong", "mua oto cũ ko sang tên thì có bị phạt ko ạ",
    "Có. Chủ xe ô tô không làm thủ tục cấp chứng nhận đăng ký xe, biển số xe khi thay đổi chủ xe theo quy định bị "
    + K7("h") + ". " + G19, v("k7:h"), v("k7"), v("k19:g", NEW))
add("tinh_huong", "Công ty tôi mua lại một chiếc xe máy của nhân viên nhưng chưa làm thủ tục đăng ký sang tên công ty. "
    "Công ty có thể bị phạt mức nào?",
    "Chủ xe là tổ chức không làm thủ tục cấp chứng nhận đăng ký xe, biển số xe khi thay đổi chủ xe đối với xe mô tô, "
    "xe gắn máy bị phạt tiền từ 1.600.000 đồng đến 2.000.000 đồng (điểm a khoản 3 Điều 32 " + ND + "); nếu chủ xe là "
    "cá nhân thì mức phạt là từ 800.000 đồng đến 1.000.000 đồng.", v("k3:a"), v("k3"))
add("muc_phat", "Chủ xe máy không làm thủ tục đổi chứng nhận đăng ký xe, biển số xe theo quy định bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy không làm thủ tục đổi chứng nhận đăng ký xe, biển số xe theo quy định bị " + K3("b")
    + ". " + G19, v("k3:b"), v("k3"), v("k19:g", NEW))
add("muc_phat", "Chủ xe ô tô không làm thủ tục đổi chứng nhận đăng ký xe, biển số xe theo quy định bị phạt bao nhiêu?",
    "Chủ xe ô tô không làm thủ tục đổi chứng nhận đăng ký xe, biển số xe theo quy định bị " + K7("c") + ". " + G19,
    v("k7:c"), v("k7"), v("k19:g", NEW))
add("tinh_huong", "Tôi đã bán chiếc xe máy cho người khác nhưng không làm thủ tục thu hồi chứng nhận đăng ký, biển số. "
    "Tôi có bị phạt không?",
    "Có. Chủ xe mô tô, xe gắn máy không làm thủ tục thu hồi chứng nhận đăng ký xe, biển số xe theo quy định bị "
    + K8("d") + ". " + G19, v("k8:d"), v("k8"), v("k19:g", NEW))
add("muc_phat", "Hiện nay chủ xe ô tô không làm thủ tục thu hồi chứng nhận đăng ký xe, biển số xe theo quy định bị phạt thế nào?",
    "Theo điểm b khoản 7 Điều 32 " + ND + " (nội dung đang có hiệu lực từ ngày 15/8/2026), chủ xe ô tô không làm thủ "
    "tục thu hồi chứng nhận đăng ký xe, biển số xe theo quy định bị phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng đối "
    "với cá nhân, từ 8.000.000 đồng đến 12.000.000 đồng đối với tổ chức. " + G19, v("k7:b", NEW), v("k7"),
    v("k19:g", NEW))

# ===== Màu sơn, kính, thiết bị âm thanh ánh sáng, cải tạo
add("muc_phat", "Tự ý thay đổi màu sơn xe máy không đúng với chứng nhận đăng ký xe bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy tự ý thay đổi nhãn hiệu, màu sơn của xe không đúng với chứng nhận đăng ký xe bị "
    + K1("a") + " và buộc khôi phục lại nhãn hiệu, màu sơn ghi trong chứng nhận đăng ký xe (điểm a khoản 19 Điều 32).",
    v("k1:a"), v("k1"), v("k19:a"))
add("tinh_huong", "Tôi sơn lại chiếc xe máy từ màu đỏ sang màu đen nhưng không làm lại giấy đăng ký. Tôi có bị phạt không?",
    "Có. Việc tự ý thay đổi màu sơn của xe không đúng với chứng nhận đăng ký xe khiến chủ xe mô tô, xe gắn máy bị "
    + K1("a") + "; đồng thời buộc khôi phục lại màu sơn ghi trong chứng nhận đăng ký xe (điểm a khoản 19 Điều 32).",
    v("k1:a"), v("k1"), v("k19:a"))
add("muc_phat", "Chủ xe ô tô tự ý thay đổi màu sơn không đúng với màu sơn ghi trong chứng nhận đăng ký xe bị phạt bao nhiêu?",
    "Chủ xe ô tô tự ý thay đổi màu sơn của xe không đúng với màu sơn ghi trong chứng nhận đăng ký xe bị " + K7("i")
    + " và buộc khôi phục lại màu sơn ghi trong chứng nhận đăng ký xe (điểm a khoản 19 Điều 32).",
    v("k7:i"), v("k7"), v("k19:a"))
add("muc_phat", "Ô tô lắp kính chắn gió, kính cửa không phải loại kính an toàn thì chủ xe bị phạt bao nhiêu?",
    "Chủ xe ô tô lắp kính chắn gió, kính cửa của xe không phải là loại kính an toàn bị " + K2("a") + " và buộc thay "
    "thế thiết bị đủ tiêu chuẩn an toàn kỹ thuật, tức lắp đúng loại kính an toàn (điểm b khoản 19 Điều 32).",
    v("k2:a"), v("k2"), v("k19:b"))
add("muc_phat", "Không khai báo với cơ quan đăng ký xe trước khi cải tạo ô tô (với loại xe phải khai báo) bị phạt bao nhiêu?",
    "Chủ xe ô tô không làm thủ tục khai báo với cơ quan đăng ký xe theo quy định trước khi cải tạo xe (đối với loại xe "
    "có quy định phải làm thủ tục khai báo) bị " + K2("b") + ".", v("k2:b"), v("k2"))
add("muc_phat", "Chủ xe máy lắp đặt thiết bị âm thanh, ánh sáng trên xe gây mất trật tự, an toàn giao thông bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy lắp đặt, sử dụng thiết bị âm thanh, ánh sáng trên xe gây mất trật tự, an toàn giao thông "
    "đường bộ bị " + K3("c") + " và buộc tháo dỡ thiết bị đã lắp đặt (điểm h khoản 19 Điều 32).",
    v("k3:c"), v("k3"), v("k19:h"))
add("doi_thuong", "độ đèn led nháy với loa to trên ô tô gây mất trật tự thì chủ xe bị phạt nhiêu",
    "Chủ xe ô tô lắp đặt, sử dụng thiết bị âm thanh, ánh sáng trên xe gây mất trật tự, an toàn giao thông đường bộ bị "
    + K7("k") + " và buộc tháo dỡ thiết bị âm thanh, ánh sáng đã lắp đặt (điểm h khoản 19 Điều 32).",
    v("k7:k"), v("k7"), v("k19:h"))
add("muc_phat", "Chủ xe máy tự ý thay đổi khung, máy, hình dáng, kích thước, đặc tính của xe bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy tự ý thay đổi khung, máy, hình dáng, kích thước, đặc tính của xe bị " + K8("b") + ".",
    v("k8:b"), v("k8"))
add("tinh_huong", "Tôi tự thay động cơ khác vào chiếc xe máy của mình mà không qua thủ tục gì. Tôi có thể bị phạt bao nhiêu?",
    "Tự ý thay đổi máy (động cơ) của xe thuộc hành vi tự ý thay đổi khung, máy, hình dáng, kích thước, đặc tính của "
    "xe; chủ xe mô tô, xe gắn máy bị " + K8("b") + ".", v("k8:b"), v("k8"))
add("muc_phat", "Chủ xe ô tô tự ý cải tạo kết cấu, hình dáng, kích thước của xe không đúng thiết kế bị xử phạt thế nào?",
    "Chủ xe ô tô tự ý thay đổi tổng thành khung, tổng thành máy, hệ thống phanh, truyền động, chuyển động hoặc tự ý "
    "cải tạo kết cấu, hình dáng, kích thước của xe không đúng thiết kế bị " + K16("c") + ". " + TUOC_KD,
    v("k16:c"), v("k16"), v("k18:d", NEW), v("k19:d"))
add("tinh_huong", "Chủ xe tải tự ý lắp thêm cơ cấu nâng hạ thùng xe để tự đổ hàng thì có bị phạt không, mức nào?",
    "Có. Tự ý lắp đặt thêm cơ cấu nâng hạ thùng xe trên xe là hành vi tại điểm c khoản 16 Điều 32 " + ND + "; chủ xe "
    "bị phạt tiền từ 65.000.000 đồng đến 75.000.000 đồng đối với cá nhân, từ 130.000.000 đồng đến 150.000.000 đồng đối "
    "với tổ chức. " + TUOC_KD, v("k16:c"), v("k16"), v("k18:d", NEW), v("k19:d"))
add("muc_phat", "Xe ô tô kinh doanh vận tải hành khách lắp thêm ghế, giường nằm không đúng thông số kiểm định thì chủ xe bị "
    "phạt bao nhiêu?",
    "Theo điểm d khoản 11 Điều 32 (nội dung có hiệu lực từ ngày 15/8/2026), đưa xe ô tô kinh doanh vận tải hành khách "
    "lắp thêm hoặc tháo bớt ghế, giường nằm, hoặc có kích thước hầm xe không đúng thông số kỹ thuật ghi trong chứng "
    "nhận kiểm định tham gia giao thông bị " + K11("d") + ". " + TUOC_KD,
    v("k11:d", NEW), v("k11"), v("k18:d", NEW), v("k19:d"))
add("muc_phat", "Đưa xe ô tô tải có kích thước thùng xe không đúng thông số kỹ thuật trong chứng nhận kiểm định tham gia "
    "giao thông thì chủ xe bị phạt bao nhiêu?",
    "Chủ xe bị " + K14("h") + ". " + TR2 + " " + TUOC_KD,
    v("k14:h", NEW), v("k14"), v("k21:a"), v("k18:d", NEW), v("k19:d"))
add("muc_phat", "Cố ý can thiệp làm sai lệch chỉ số đồng hồ báo quãng đường đã chạy (tua công-tơ-mét) của ô tô bị phạt "
    "bao nhiêu?",
    "Chủ xe ô tô cố ý can thiệp làm sai lệch chỉ số trên đồng hồ báo quãng đường đã chạy của xe bị " + K7("l")
    + " và buộc điều chỉnh lại chỉ số trên đồng hồ bị làm sai lệch (điểm k khoản 19 Điều 32).",
    v("k7:l"), v("k7"), v("k19:k"))
add("doi_thuong", "tua odo xe ô tô trước khi bán thì có bị phạt không",
    "Có. Cố ý can thiệp làm sai lệch chỉ số trên đồng hồ báo quãng đường đã chạy của xe ô tô bị " + K7("l")
    + "; ngoài ra buộc điều chỉnh lại chỉ số đã bị làm sai lệch (điểm k khoản 19 Điều 32).",
    v("k7:l"), v("k7"), v("k19:k"))

# ===== Hồ sơ, giấy tờ giả
add("muc_phat", "Chủ xe máy tẩy xóa, sửa chữa hoặc giả mạo hồ sơ đăng ký xe (chưa đến mức truy cứu hình sự) bị xử phạt thế nào?",
    "Chủ xe mô tô, xe gắn máy tẩy xóa, sửa chữa hoặc giả mạo hồ sơ đăng ký xe nhưng chưa đến mức truy cứu trách nhiệm "
    "hình sự bị " + K8("a") + "; đồng thời bị thu hồi hồ sơ đăng ký xe bị tẩy xóa, sửa chữa hoặc giả mạo (khoản 20 "
    "Điều 32).", v("k8:a"), v("k8"), v("k20", NEW))
add("muc_phat", "Chủ xe ô tô giả mạo hồ sơ đăng ký xe nhưng chưa đến mức truy cứu trách nhiệm hình sự bị phạt bao nhiêu?",
    "Chủ xe ô tô tẩy xóa, sửa chữa hoặc giả mạo hồ sơ đăng ký xe nhưng chưa đến mức truy cứu trách nhiệm hình sự bị "
    + K7("a") + "; đồng thời bị thu hồi hồ sơ đăng ký xe bị tẩy xóa, sửa chữa hoặc giả mạo (khoản 20 Điều 32).",
    v("k7:a"), v("k7"), v("k20", NEW))
add("muc_phat", "Khai báo không đúng sự thật hoặc dùng giấy tờ giả để được cấp lại biển số, chứng nhận đăng ký xe máy bị "
    "phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy khai báo không đúng sự thật hoặc sử dụng giấy tờ, tài liệu giả để được cấp lại biển số "
    "xe, chứng nhận đăng ký xe nhưng chưa đến mức bị truy cứu trách nhiệm hình sự bị " + K8("c") + ".",
    v("k8:c"), v("k8"))
add("muc_phat", "Chủ xe ô tô dùng giấy tờ giả để được cấp lại chứng nhận đăng ký xe thì bị xử phạt như thế nào hiện nay?",
    "Theo điểm d khoản 7 Điều 32 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), chủ xe ô tô khai báo không đúng "
    "sự thật hoặc sử dụng giấy tờ, tài liệu giả để được cấp lại biển số xe, chứng nhận đăng ký xe nhưng chưa đến mức "
    "bị truy cứu trách nhiệm hình sự bị phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng đối với cá nhân, từ 8.000.000 "
    "đồng đến 12.000.000 đồng đối với tổ chức; giấy tờ, tài liệu giả đó bị thu hồi (khoản 20 Điều 32).",
    v("k7:d", NEW), v("k7"), v("k20", NEW))

# ===== Biển số
add("muc_phat", "Chủ xe máy không thực hiện đúng quy định về biển số thì bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy không thực hiện đúng quy định về biển số (trừ hành vi lắp thiết bị thay đổi biển số và "
    "không gắn biển, gắn biển sai tại điểm g, điểm h khoản 8) bị phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với "
    "cá nhân, từ 1.600.000 đồng đến 2.000.000 đồng đối với tổ chức (khoản 4 Điều 32 " + ND + "), và buộc thực hiện "
    "đúng quy định về biển số xe (điểm c khoản 19 Điều 32).", v("k4"), v("k19:c"))
add("muc_phat", "Chủ xe ô tô không thực hiện đúng quy định về kẻ, dán chữ, số biển số, thông tin trên thành xe, cửa xe bị "
    "phạt bao nhiêu?",
    "Chủ xe ô tô không thực hiện đúng quy định về biển số, quy định về kẻ hoặc dán chữ, số biển số, thông tin trên "
    "thành xe, cửa xe bị " + K9("e") + " và buộc thực hiện đúng quy định đó (điểm c khoản 19 Điều 32).",
    v("k9:e"), v("k9"), v("k19:c"))
add("muc_phat", "Lắp thiết bị thay đổi biển số trên xe máy trái quy định thì chủ xe bị phạt gì?",
    "Chủ xe mô tô, xe gắn máy lắp đặt, sử dụng thiết bị thay đổi biển số trên xe trái quy định bị " + K8("g")
    + "; ngoài ra bị tịch thu biển số và thiết bị thay đổi biển số (điểm a khoản 18 Điều 32).",
    v("k8:g"), v("k8"), v("k18:a"))
add("doi_thuong", "lắp biển số lật trên ô tô thì bị phạt bao nhiêu tiền",
    "Lắp đặt, sử dụng thiết bị thay đổi biển số trên xe ô tô trái quy định khiến chủ xe bị " + K12("c")
    + "; ngoài ra bị tịch thu biển số và thiết bị thay đổi biển số (điểm a khoản 18 Điều 32).",
    v("k12:c"), v("k12"), v("k18:a"))
add("muc_phat", "Chủ xe máy đưa xe không gắn biển số tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy đưa phương tiện không gắn biển số (đối với loại xe phải gắn biển số), hoặc gắn biển số "
    "không đúng với chứng nhận đăng ký xe, không do cơ quan có thẩm quyền cấp, tham gia giao thông bị " + K8("h")
    + ". " + TR6 + " " + BIEN_TT, v("k8:h"), v("k8"), v("k21:đ"), v("k18:a"))
add("muc_phat", "Chủ xe ô tô đưa xe không gắn biển số tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe ô tô đưa phương tiện không gắn biển số (đối với loại xe có quy định phải gắn biển số) tham gia giao thông "
    "bị " + K12("b") + ". " + TR6, v("k12:b"), v("k12"), v("k21:đ"))
add("tinh_huong", "Tôi tự lái chiếc ô tô của mình gắn biển số không do cơ quan có thẩm quyền cấp (biển giả). Tôi bị xử phạt "
    "những gì?",
    "Chủ xe đưa phương tiện gắn biển số không đúng với chứng nhận đăng ký xe hoặc không do cơ quan có thẩm quyền cấp "
    "tham gia giao thông bị " + K13("d") + ". Vì chủ xe trực tiếp điều khiển nên còn bị trừ điểm giấy phép lái xe 10 "
    "điểm (điểm g khoản 21 Điều 32). " + BIEN_TT, v("k13:d"), v("k13"), v("k21:g"), v("k18:a"))

# ===== Không có đăng ký xe
add("muc_phat", "Chủ xe ô tô đưa xe không có chứng nhận đăng ký xe tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe ô tô đưa phương tiện không có chứng nhận đăng ký xe, hoặc có nhưng đã hết hạn sử dụng, hết hiệu lực, tham "
    "gia giao thông bị " + K12("a") + ". " + TR2 + " " + G19 + " Nếu không chứng minh được nguồn gốc xuất xứ của phương "
    "tiện thì còn bị tịch thu phương tiện (điểm b khoản 18 Điều 32).",
    v("k12:a"), v("k12"), v("k21:a"), v("k19:g", NEW), v("k18:b"))
add("tinh_huong", "Tôi tự lái chiếc ô tô của mình đã có đăng ký tạm thời nhưng quá thời hạn cho phép. Tôi bị xử phạt thế nào?",
    "Đưa phương tiện có chứng nhận đăng ký xe tạm thời tham gia giao thông quá thời hạn cho phép thuộc điểm a khoản 12 "
    "Điều 32 " + ND + ": chủ xe là cá nhân bị phạt tiền từ 16.000.000 đồng đến 18.000.000 đồng (tổ chức từ 32.000.000 "
    "đồng đến 36.000.000 đồng). Vì chủ xe trực tiếp điều khiển nên còn bị trừ điểm giấy phép lái xe 02 điểm (điểm a "
    "khoản 21 Điều 32). " + G19, v("k12:a"), v("k12"), v("k21:a"), v("k19:g", NEW))
add("muc_phat", "Chủ xe máy đưa xe không có chứng nhận đăng ký xe tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy đưa phương tiện không có chứng nhận đăng ký xe, hoặc có nhưng đã hết hạn sử dụng, hết "
    "hiệu lực, tham gia giao thông bị " + K8("đ") + ". " + TR2 + " " + G19,
    v("k8:đ"), v("k8"), v("k21:a"), v("k19:g", NEW))
add("muc_phat", "Đưa xe máy có chứng nhận đăng ký không đúng số khung, số máy của xe tham gia giao thông thì chủ xe bị phạt "
    "bao nhiêu?",
    "Chủ xe mô tô, xe gắn máy đưa phương tiện có chứng nhận đăng ký xe không đúng với số khung, số động cơ (số máy) "
    "của xe, hoặc không do cơ quan có thẩm quyền cấp, bị tẩy xóa, tham gia giao thông bị " + K8("e") + ". " + TR2
    + " Người vi phạm còn buộc nộp lại chứng nhận đăng ký xe đó (điểm i khoản 19 Điều 32).",
    v("k8:e"), v("k8"), v("k21:a"), v("k19:i"))

# ===== Kiểm định
add("muc_phat", "Chủ xe ô tô đưa xe có tem kiểm định hết hạn dưới 01 tháng tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe đưa xe cơ giới có giấy chứng nhận hoặc tem kiểm định an toàn kỹ thuật và bảo vệ môi trường đã hết hiệu "
    "lực dưới 01 tháng tham gia giao thông bị " + K9("b") + ". " + TR2, v("k9:b"), v("k9"), v("k21:a"))
add("doi_thuong", "xe ô tô của em hết hạn đăng kiểm mới 10 ngày, em tự lái đi thì bị phạt bn ạ",
    "Xe có chứng nhận, tem kiểm định hết hiệu lực dưới 01 tháng mà chủ xe là cá nhân đưa tham gia giao thông bị phạt "
    "tiền từ 4.000.000 đồng đến 6.000.000 đồng (điểm b khoản 9 Điều 32 " + ND + "). Vì chủ xe trực tiếp điều khiển "
    "nên còn bị trừ điểm giấy phép lái xe 02 điểm (điểm a khoản 21 Điều 32).", v("k9:b"), v("k9"), v("k21:a"))
add("tinh_huong", "Ô tô của tôi hết hạn đăng kiểm đã hơn 2 tháng mà tôi vẫn tự lái đi. Tôi bị phạt bao nhiêu?",
    "Xe có chứng nhận, tem kiểm định hết hiệu lực từ 01 tháng trở lên mà chủ xe đưa tham gia giao thông thuộc điểm a "
    "khoản 11 Điều 32 " + ND + ": chủ xe là cá nhân bị phạt tiền từ 10.000.000 đồng đến 12.000.000 đồng (tổ chức từ "
    "20.000.000 đồng đến 24.000.000 đồng). Vì chủ xe trực tiếp điều khiển nên còn bị trừ điểm giấy phép lái xe 02 điểm "
    "(điểm a khoản 21 Điều 32).", v("k11:a"), v("k11"), v("k21:a"))
add("muc_phat", "Chủ xe ô tô đưa xe không có giấy chứng nhận, tem kiểm định tham gia giao thông bị phạt bao nhiêu?",
    "Đưa xe cơ giới không có giấy chứng nhận hoặc tem kiểm định an toàn kỹ thuật và bảo vệ môi trường (đối với loại xe "
    "phải kiểm định) tham gia giao thông bị " + K11("a") + ". " + TR2, v("k11:a"), v("k11"), v("k21:a"))
add("muc_phat", "Thuê, mượn linh kiện, phụ kiện của xe ô tô khi đi kiểm định bị phạt bao nhiêu?",
    "Chủ xe ô tô thuê, mượn linh kiện, phụ kiện của xe khi kiểm định bị " + K9("a") + ".", v("k9:a"), v("k9"))
add("muc_phat", "Hiện nay chủ xe máy đưa xe không có chứng nhận kiểm định khí thải tham gia giao thông có bị phạt không?",
    "Có. Theo điểm b khoản 1 Điều 32 " + ND + " (nội dung có hiệu lực từ ngày 15/8/2026), chủ xe mô tô, xe gắn máy đưa "
    "phương tiện không có chứng nhận kiểm định khí thải, hoặc có nhưng đã hết hạn sử dụng, hoặc sử dụng chứng nhận "
    "không do cơ quan có thẩm quyền cấp, bị phạt tiền từ 200.000 đồng đến 300.000 đồng đối với cá nhân, từ 400.000 "
    "đồng đến 600.000 đồng đối với tổ chức.", v("k1:b", NEW), v("k1"))

# ===== Giao xe cho người không đủ điều kiện
add("tinh_huong", "Tôi cho bạn mượn xe máy, trong khi bạn tôi đang bị tước giấy phép lái xe. Tôi có bị phạt không?",
    "Có. Chủ xe mô tô, xe gắn máy giao xe hoặc để cho người không đủ điều kiện theo khoản 1 Điều 56 Luật Trật tự, an "
    "toàn giao thông đường bộ điều khiển xe tham gia giao thông, bao gồm cả người có giấy phép lái xe nhưng đang trong "
    "thời gian bị tước quyền sử dụng, bị phạt tiền từ 8.000.000 đồng đến 10.000.000 đồng đối với cá nhân, từ "
    "16.000.000 đồng đến 20.000.000 đồng đối với tổ chức (khoản 10 Điều 32 " + ND + ").", v("k10"), L56)
add("doi_thuong", "cho người chưa có bằng lái mượn xe máy đi thì chủ xe có bị phạt ko",
    "Có. Khoản 1 Điều 56 Luật Trật tự, an toàn giao thông đường bộ yêu cầu người lái xe phải đủ tuổi, sức khỏe và có "
    "giấy phép lái xe còn điểm, còn hiệu lực, phù hợp với loại xe (trừ người lái xe gắn máy theo khoản 4 Điều 56). Chủ "
    "xe mô tô, xe gắn máy giao xe cho người không đủ điều kiện đó điều khiển bị phạt tiền từ 8.000.000 đồng đến "
    "10.000.000 đồng đối với cá nhân, từ 16.000.000 đồng đến 20.000.000 đồng đối với tổ chức (khoản 10 Điều 32 " + ND
    + ").", v("k10"), L56)
add("tinh_huong", "Tôi giao ô tô cho người lái có giấy phép lái xe đã hết hạn. Tôi bị phạt bao nhiêu?",
    "Chủ xe ô tô giao xe hoặc để cho người không đủ điều kiện theo khoản 1 Điều 56 Luật Trật tự, an toàn giao thông "
    "đường bộ điều khiển xe, bao gồm cả người có giấy phép lái xe đã hết hạn sử dụng hoặc đang bị tước, bị " + K14("i")
    + ".", v("k14:i"), v("k14"), L56)
add("doi_thuong", "công ty giao ô tô cho tài xế không có bằng phù hợp thì bị phạt nhiêu",
    "Chủ xe là tổ chức giao xe ô tô cho người không đủ điều kiện theo khoản 1 Điều 56 Luật Trật tự, an toàn giao thông "
    "đường bộ (trong đó có yêu cầu giấy phép lái xe phù hợp với loại xe) điều khiển xe bị phạt tiền từ 56.000.000 đồng "
    "đến 60.000.000 đồng; nếu chủ xe là cá nhân thì từ 28.000.000 đồng đến 30.000.000 đồng (điểm i khoản 14 Điều 32 "
    + ND + ").", v("k14:i"), v("k14"), L56)

# ===== Tịch thu phương tiện
add("muc_phat", "Cắt, hàn, đục sửa trái phép số khung, số máy của xe thì chủ xe bị xử phạt thế nào?",
    "Chủ xe cắt, hàn, tẩy xóa, đục sửa, đóng lại trái phép số khung, số động cơ (số máy), hoặc đưa phương tiện đã bị "
    "làm như vậy tham gia giao thông, bị tịch thu phương tiện (điểm a khoản 17 Điều 32 " + ND + ").",
    v("k17:a"), v("k17"))
add("muc_phat", "Cải tạo xe ô tô tải thành xe ô tô chở người thì bị xử lý thế nào?",
    "Cải tạo xe ô tô loại khác thành xe ô tô chở người bị tịch thu phương tiện (điểm b khoản 17 Điều 32 " + ND + ").",
    v("k17:b"), v("k17"))
add("tinh_huong", "Chiếc xe tải của tôi đã hết niên hạn sử dụng nhưng tôi vẫn cho chạy trên đường. Tôi có thể bị xử lý thế nào?",
    "Chủ xe đưa phương tiện quá niên hạn sử dụng tham gia giao thông bị tịch thu phương tiện (điểm c khoản 17 Điều 32 "
    + ND + "), trừ hành vi đã được quy định riêng tại điểm i khoản 7 Điều 26.", v("k17:c"), v("k17"))

# ===== Thiết bị giám sát, xe cứu hộ, xe thông minh
add("muc_phat", "Chủ xe cứu thương đưa xe không lắp thiết bị giám sát hành trình tham gia giao thông bị phạt bao nhiêu?",
    "Chủ xe đưa xe cứu hộ giao thông đường bộ, xe cứu thương không lắp thiết bị giám sát hành trình, hoặc lắp nhưng "
    "không hoạt động, không đúng quy chuẩn, hoặc làm sai lệch dữ liệu, tham gia giao thông bị " + K7("m") + ". " + TR2,
    v("k7:m"), v("k7"), v("k21:a"))
add("muc_phat", "Đưa xe cứu hộ giao thông đường bộ không có dụng cụ, thiết bị chuyên dùng để cứu hộ tham gia giao thông bị "
    "phạt bao nhiêu?",
    "Chủ xe bị " + K7("o") + " và buộc lắp đặt dụng cụ, thiết bị chuyên dùng để cứu hộ, hỗ trợ cứu hộ theo đúng quy "
    "định (điểm l khoản 19 Điều 32).", v("k7:o"), v("k7"), v("k19:l", NEW))
add("muc_phat", "Chủ xe ô tô đầu kéo đưa xe không lắp thiết bị giám sát hành trình tham gia giao thông bị phạt bao nhiêu?",
    "Theo khoản 9a Điều 32 " + ND + " (có hiệu lực từ ngày 15/8/2026), chủ xe ô tô đầu kéo, xe vận tải nội bộ đưa xe "
    "không lắp thiết bị giám sát hành trình, hoặc có lắp nhưng không hoạt động, không đúng quy chuẩn, hoặc làm sai lệch "
    "dữ liệu, bị phạt tiền từ 5.000.000 đồng đến 6.000.000 đồng đối với cá nhân, từ 10.000.000 đồng đến 12.000.000 "
    "đồng đối với tổ chức; đồng thời buộc lắp đặt thiết bị theo đúng quy định (điểm l khoản 19 Điều 32).",
    v("k9a:a", NEW), v("k9a", NEW), v("k19:l", NEW))
add("muc_phat", "Xe vận tải nội bộ không lắp thiết bị ghi nhận hình ảnh người lái xe thì chủ xe bị phạt bao nhiêu?",
    "Chủ xe vận tải nội bộ đưa xe không lắp thiết bị ghi nhận hình ảnh người lái xe, hoặc có lắp nhưng không ghi, không "
    "lưu trữ được dữ liệu, hoặc làm sai lệch dữ liệu, bị " + K9A("b") + " (nội dung có hiệu lực từ ngày 15/8/2026); "
    "đồng thời buộc lắp đặt thiết bị theo đúng quy định (điểm l khoản 19 Điều 32).",
    v("k9a:b", NEW), v("k9a", NEW), v("k19:l", NEW))
add("muc_phat", "Đưa phương tiện giao thông thông minh không có giấy phép hoạt động tham gia giao thông bị phạt bao nhiêu?",
    "Chủ phương tiện đưa phương tiện giao thông thông minh không có giấy phép hoạt động, hoặc giấy phép hết hạn, hoặc "
    "hoạt động không đúng nội dung ghi trong giấy phép, tham gia giao thông bị " + K12("d") + ".",
    v("k12:d"), v("k12"))

out = ROOT / "data/train/drafts/xu_phat_05.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
