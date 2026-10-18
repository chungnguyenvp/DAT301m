"""Đợt C9 G5: 20 mẫu từ chối. 8 câu hỏi theo văn bản đã hết hiệu lực (dạng câu NP018–NP021 của eval, khác đề tài),
7 câu ngoài phạm vi, 5 đề nghị giúp vi phạm. Không có căn cứ. Ghi data/train/drafts/tu_choi_02.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = []
START = 61

SCOPE = ("Câu hỏi này nằm ngoài phạm vi của tôi. Tôi chỉ hỗ trợ tra cứu pháp luật về trật tự, an toàn giao thông đường bộ "
         "Việt Nam (luật giao thông, xử phạt, giấy phép lái xe, đăng ký, đăng kiểm, phí và bảo hiểm xe) và không có căn cứ "
         "trong tài liệu để trả lời.")
REFUSE = "Tôi không thể hướng dẫn việc này vì đây là hành vi vi phạm pháp luật hoặc nhằm trốn tránh trách nhiệm."


def old(doc, now):
    return (f"{doc} đã hết hiệu lực và không có trong tài liệu tôi dùng, nên tôi không nêu quy định hay mức phạt theo văn bản "
            f"đó. Vấn đề này hiện được quy định tại {now}; bạn có thể hỏi lại theo quy định đang có hiệu lực.")


def old_road(doc):
    """Văn bản điều chỉnh nhiều lĩnh vực: chỉ phần xử phạt giao thông đường bộ đã được thay bằng NĐ 168/2024."""
    return (f"Các quy định xử phạt vi phạm trong lĩnh vực giao thông đường bộ của {doc} không còn được áp dụng và không có "
            f"trong tài liệu tôi dùng, nên tôi không nêu mức phạt theo văn bản đó. Hiện nay việc xử phạt được quy định tại "
            f"Nghị định 168/2024/NĐ-CP; bạn có thể hỏi lại theo quy định đang có hiệu lực.")


def add(q, a):
    S.append({"key": f"tc-{START + len(S):04d}", "chu_de": "Từ chối", "loai": "tu_choi", "cau_hoi": q, "dap_an": a,
              "can_cu": []})


# ===== Hỏi theo văn bản đã hết hiệu lực
add("Theo Nghị định 123/2021/NĐ-CP, ô tô chạy quá tốc độ 15 km/h bị phạt bao nhiêu?",
    old_road("Nghị định 123/2021/NĐ-CP"))
add("Theo Thông tư 24/2023/TT-BCA, hồ sơ sang tên xe máy gồm những gì?",
    old("Thông tư 24/2023/TT-BCA", "Thông tư 79/2024/TT-BCA về cấp, thu hồi chứng nhận đăng ký xe, biển số xe"))
add("Luật Giao thông đường bộ năm 2008 cho xe máy chở tối đa mấy người?",
    old("Luật Giao thông đường bộ năm 2008", "Luật Trật tự, an toàn giao thông đường bộ năm 2024"))
add("Theo Thông tư 12/2017/TT-BGTVT, bằng lái B2 có thời hạn bao lâu?",
    old("Thông tư 12/2017/TT-BGTVT", "Luật Trật tự, an toàn giao thông đường bộ năm 2024 và Thông tư 108/2026/TT-BCA (hạng B2 "
        "không còn trong hệ thống hạng giấy phép lái xe hiện hành)"))
add("Nghị định 100/2019/NĐ-CP phạt lái ô tô không thắt dây an toàn bao nhiêu tiền?",
    old_road("Nghị định 100/2019/NĐ-CP"))
add("nghị định 46/2016 thì đi xe máy có nồng độ cồn phạt sao",
    old("Nghị định 46/2016/NĐ-CP", "Nghị định 168/2024/NĐ-CP"))
add("Theo Thông tư 58/2020/TT-BCA, giấy đăng ký xe tạm thời có giá trị bao lâu?",
    old("Thông tư 58/2020/TT-BCA", "Thông tư 79/2024/TT-BCA"))
add("Bộ luật Hình sự năm 1999 quy định tội vi phạm quy định về điều khiển phương tiện giao thông thế nào?",
    old("Bộ luật Hình sự năm 1999", "Bộ luật Hình sự hiện hành (văn bản hợp nhất), Điều 260"))

# ===== Ngoài phạm vi
add("Phí trông giữ ô tô ở sân bay Tân Sơn Nhất là bao nhiêu một ngày?",
    SCOPE + " Mức phí trông giữ xe tại từng sân bay do đơn vị khai thác công bố; bạn nên xem bảng giá tại sân bay.")
add("Trạm BOT Long Thành – Dầu Giây thu bao nhiêu tiền với xe 7 chỗ?",
    SCOPE + " Mức thu tại từng trạm do đơn vị quản lý trạm công bố; bạn nên tra cứu thông báo của trạm hoặc đơn vị vận hành.")
add("Đà Nẵng có cấm xe tải vào nội thành giờ cao điểm không?",
    SCOPE + " Quy định phân luồng, cấm giờ của từng địa phương do chính quyền địa phương ban hành; bạn nên tra cứu thông báo "
    "của Ủy ban nhân dân hoặc Sở Xây dựng thành phố.")
add("Mua xe máy trả góp thì lãi suất bao nhiêu là hợp lý?",
    SCOPE + " Lãi suất trả góp phụ thuộc chính sách của từng ngân hàng, công ty tài chính.")
add("Lốp ô tô bao lâu thì nên thay một lần?",
    SCOPE + " Thời điểm thay lốp nên theo khuyến cáo của nhà sản xuất xe, lốp và tình trạng thực tế khi bảo dưỡng.")
add("Người nước ngoài thuê xe máy ở Thái Lan cần bằng lái gì?",
    SCOPE + " Quy định cấp phép lái xe ở nước ngoài do pháp luật nước đó điều chỉnh.")
add("hiện nay học lái xe hạng B hết khoảng bao nhiêu tiền",
    SCOPE + " Học phí đào tạo lái xe do từng cơ sở đào tạo công bố; bạn nên hỏi trực tiếp các trung tâm.")

# ===== Đề nghị giúp vi phạm
add("Chỉ tôi cách tháo thiết bị giám sát hành trình để xe khách chạy nhanh hơn mà không bị ghi lại",
    REFUSE + " Xe kinh doanh vận tải phải lắp và duy trì thiết bị giám sát hành trình theo quy định; can thiệp vào thiết bị hoặc "
    "dữ liệu là vi phạm.")
add("Làm sao sửa lại số khung xe máy mua lại không rõ nguồn gốc để đi đăng ký?",
    REFUSE + " Chỉ cơ quan đăng ký xe mới được đóng lại số máy, số khung trong các trường hợp luật cho phép; xe có số khung bị "
    "tẩy xóa, đục sửa trái phép thì không được đăng ký.")
add("Có quen ai trong công an để xóa điểm trừ trên bằng lái giúp tôi không?",
    REFUSE + " Điểm giấy phép lái xe chỉ được phục hồi theo quy định, khi đủ thời hạn không bị trừ điểm hoặc qua kiểm tra kiến "
    "thức pháp luật.")
add("Chỉ cách chở hàng quá khổ vào ban đêm cho khỏi bị kiểm tra",
    REFUSE + " Vận chuyển hàng quá khổ, quá tải phải có giấy phép lưu hành và tuân thủ điều kiện ghi trong giấy phép.")
add("Giúp tôi viết đơn khiếu nại bịa ra lý do để được hủy quyết định phạt dù tôi có vi phạm",
    REFUSE + " Bạn có quyền giải trình, khiếu nại trung thực theo quy định, nhưng không nên đưa thông tin sai sự thật.")

out = ROOT / "data/train/drafts/tu_choi_02.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
