"""Đợt C10 G5: 70 mẫu từ chối để đưa tỷ lệ `tu_choi` lên khoảng 10% (eval có 11%). Gồm câu hỏi theo văn bản đã hết hiệu
lực (chỉ dùng văn bản có điều khoản bãi bỏ, thay thế trong kho hoặc đã được thay hẳn), quy định riêng của địa phương, giá
cả và tư vấn ngoài pháp luật, lĩnh vực luật khác, luật nước ngoài, và đề nghị giúp vi phạm. Không có căn cứ.
Ghi data/train/drafts/tu_choi_03.jsonl."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = []
START = 81

SCOPE = ("Câu hỏi này nằm ngoài phạm vi của tôi. Tôi chỉ hỗ trợ tra cứu pháp luật về trật tự, an toàn giao thông đường bộ "
         "Việt Nam (luật giao thông, xử phạt, giấy phép lái xe, đăng ký, đăng kiểm, phí và bảo hiểm xe) và không có căn cứ "
         "trong tài liệu để trả lời.")
REFUSE = "Tôi không thể hướng dẫn việc này vì đây là hành vi vi phạm pháp luật hoặc nhằm trốn tránh trách nhiệm."


def old(doc, now):
    return (f"{doc} đã hết hiệu lực và không có trong tài liệu tôi dùng, nên tôi không nêu quy định hay mức phạt theo văn bản "
            f"đó. Vấn đề này hiện được quy định tại {now}; bạn có thể hỏi lại theo quy định đang có hiệu lực.")


def old_road(doc):
    return (f"Các quy định xử phạt vi phạm trong lĩnh vực giao thông đường bộ của {doc} không còn được áp dụng và không có "
            f"trong tài liệu tôi dùng, nên tôi không nêu mức phạt theo văn bản đó. Hiện nay việc xử phạt được quy định tại "
            f"Nghị định 168/2024/NĐ-CP; bạn có thể hỏi lại theo quy định đang có hiệu lực.")


def add(q, a):
    S.append({"key": f"tc-{START + len(S):04d}", "chu_de": "Từ chối", "loai": "tu_choi", "cau_hoi": q, "dap_an": a,
              "can_cu": []})


L36 = "Luật Trật tự, an toàn giao thông đường bộ năm 2024"
ND168 = "Nghị định 168/2024/NĐ-CP"
TT79 = "Thông tư 79/2024/TT-BCA"

# ===== Văn bản đã hết hiệu lực hoặc phần giao thông đường bộ không còn áp dụng (20)
add("Theo Nghị định 100/2019/NĐ-CP, đi xe máy không có gương chiếu hậu bên trái bị phạt bao nhiêu?", old_road("Nghị định 100/2019/NĐ-CP"))
add("Nghị định 100/2019 phạt người đi bộ không đi đúng phần đường bao nhiêu tiền?", old_road("Nghị định 100/2019/NĐ-CP"))
add("Theo Nghị định 123/2021/NĐ-CP, xe tải chở quá tải 50% bị xử phạt thế nào?", old_road("Nghị định 123/2021/NĐ-CP"))
add("Nghị định 171/2013/NĐ-CP quy định phạt lỗi không có bằng lái xe máy bao nhiêu?",
    old("Nghị định 171/2013/NĐ-CP", ND168))
add("Theo Nghị định 46/2016/NĐ-CP, ô tô đỗ xe trên vỉa hè bị phạt thế nào?", old("Nghị định 46/2016/NĐ-CP", ND168))
add("Luật Giao thông đường bộ 2008 quy định người đủ bao nhiêu tuổi được lái xe tải?",
    old("Luật Giao thông đường bộ năm 2008", L36))
add("Theo Luật Giao thông đường bộ năm 2008, khi nào xe được quyền ưu tiên?",
    old("Luật Giao thông đường bộ năm 2008", L36))
add("luật gtđb 2008 bằng lái hạng A1 lái được xe gì",
    old("Luật Giao thông đường bộ năm 2008", L36 + " (Điều 57 quy định các hạng giấy phép lái xe hiện hành)"))
add("Theo Thông tư 15/2014/TT-BCA, đăng ký xe máy mới cần những giấy tờ gì?", old("Thông tư 15/2014/TT-BCA", TT79))
add("Thông tư 58/2020/TT-BCA quy định thời hạn sang tên xe sau khi mua là bao lâu?", old("Thông tư 58/2020/TT-BCA", TT79))
add("Theo Thông tư 24/2023/TT-BCA, biển số định danh được giữ lại bao lâu sau khi bán xe?",
    old("Thông tư 24/2023/TT-BCA", TT79 + " và " + L36))
add("Theo Thông tư 31/2019/TT-BGTVT, tốc độ tối đa của xe máy trong khu đông dân cư là bao nhiêu?",
    old("Thông tư 31/2019/TT-BGTVT", "Thông tư 38/2024/TT-BGTVT về tốc độ và khoảng cách an toàn"))
add("Nghị định 03/2021/NĐ-CP quy định bảo hiểm bắt buộc xe máy bồi thường tối đa bao nhiêu?",
    old("Nghị định 03/2021/NĐ-CP", "Nghị định 67/2023/NĐ-CP về bảo hiểm bắt buộc"))
add("Theo Nghị định 140/2016/NĐ-CP, lệ phí trước bạ ô tô lần đầu là bao nhiêu phần trăm?",
    old("Nghị định 140/2016/NĐ-CP", "Nghị định 10/2022/NĐ-CP về lệ phí trước bạ"))
add("Thông tư 60/2023/TT-BTC quy định lệ phí cấp biển ô tô ở Hà Nội là bao nhiêu?",
    old("Thông tư 60/2023/TT-BTC", "Thông tư 155/2025/TT-BTC"))
add("Theo Nghị định 10/2020/NĐ-CP, xe taxi phải có niên hạn sử dụng bao lâu?",
    old("Nghị định 10/2020/NĐ-CP", "Nghị định 158/2024/NĐ-CP về kinh doanh và điều kiện kinh doanh vận tải"))
add("Nghị định 160/2024/NĐ-CP quy định giáo viên dạy thực hành lái xe cần tiêu chuẩn gì?",
    old("Nghị định 160/2024/NĐ-CP", "Nghị định 94/2026/NĐ-CP về hoạt động đào tạo và sát hạch lái xe"))
add("Theo Thông tư 47/2024/TT-BGTVT, hồ sơ kiểm định xe lần đầu gồm những gì?",
    old("Thông tư 47/2024/TT-BGTVT", "Thông tư 30/2026/TT-BXD"))
add("Bộ luật Hình sự 1999 xử lý tội đua xe trái phép thế nào?",
    old("Bộ luật Hình sự năm 1999", "Bộ luật Hình sự hiện hành (văn bản hợp nhất), Điều 266"))
add("tt 31/2019 khoảng cách an toàn giữa 2 xe khi chạy 80km/h là bn",
    old("Thông tư 31/2019/TT-BGTVT", "Thông tư 38/2024/TT-BGTVT"))

# ===== Quy định riêng địa phương, giá cả, dịch vụ (16)
add("TP.HCM có cấm xe máy chạy xăng vào trung tâm không, từ khi nào?",
    SCOPE + " Các biện pháp hạn chế phương tiện ở từng đô thị do chính quyền địa phương quyết định; bạn nên theo dõi thông báo "
    "của Ủy ban nhân dân thành phố.")
add("Phí gửi xe máy ở bệnh viện Bạch Mai là bao nhiêu?",
    SCOPE + " Giá trông giữ xe tại từng địa điểm do đơn vị trông giữ niêm yết theo quy định của địa phương.")
add("Bãi đỗ xe ngầm ở công viên Lê Văn Tám thu phí ô tô thế nào?",
    SCOPE + " Giá dịch vụ của từng bãi đỗ xe do đơn vị khai thác công bố.")
add("Trạm thu phí cao tốc Hà Nội – Hải Phòng thu bao nhiêu với xe container?",
    SCOPE + " Mức thu tại từng trạm do cơ quan có thẩm quyền và đơn vị khai thác công bố; bạn nên tra cứu biểu phí của tuyến.")
add("Hà Nội thu phí ô tô vào nội đô từ năm nào, bao nhiêu tiền?",
    SCOPE + " Việc thu phí phương tiện vào khu vực nội đô do chính quyền thành phố quyết định và công bố.")
add("Đường nào ở Hà Nội cấm xe tải ban ngày?",
    SCOPE + " Danh sách tuyến cấm, giờ cấm do Sở Xây dựng hoặc cơ quan quản lý giao thông của thành phố công bố.")
add("Giá đăng kiểm ô tô 5 chỗ hiện nay là bao nhiêu?",
    SCOPE + " Tài liệu tôi dùng không có biểu giá dịch vụ kiểm định; bạn nên xem biểu giá niêm yết tại cơ sở đăng kiểm.")
add("Bảo hiểm thân vỏ ô tô hãng nào đền bù nhanh nhất?",
    SCOPE + " Việc chọn sản phẩm bảo hiểm tự nguyện nên dựa trên điều khoản hợp đồng của từng doanh nghiệp.")
add("Đi Grab bike hay xe ôm truyền thống thì rẻ hơn?",
    SCOPE + " Giá cước do từng nền tảng, đơn vị vận tải công bố.")
add("Thuê xe tự lái 7 chỗ ở Đà Nẵng giá bao nhiêu một ngày?",
    SCOPE + " Giá thuê xe do từng đơn vị cho thuê công bố.")
add("Học bằng lái xe máy A1 ở trung tâm nào nhanh nhất?",
    SCOPE + " Thông tin về cơ sở đào tạo bạn nên xem tại cổng thông tin của cơ quan quản lý đào tạo lái xe ở địa phương.")
add("Xe máy điện hãng nào đi được quãng đường xa nhất?",
    SCOPE + " Thông số kỹ thuật của từng mẫu xe do nhà sản xuất công bố.")
add("ô tô cũ đi 100 nghìn km có nên mua ko",
    SCOPE + " Việc đánh giá tình trạng một chiếc xe cụ thể nên nhờ cơ sở kiểm tra kỹ thuật hoặc người có chuyên môn.")
add("Bao nhiêu km thì nên thay dầu ô tô?",
    SCOPE + " Lịch bảo dưỡng nên theo khuyến cáo của nhà sản xuất xe.")
add("Cách lái xe ô tô số tự động lên dốc cho an toàn?",
    SCOPE + " Kỹ năng lái xe cụ thể bạn nên học tại cơ sở đào tạo lái xe hoặc theo hướng dẫn của nhà sản xuất.")
add("Số tổng đài cứu hộ giao thông trên cao tốc là số nào?",
    SCOPE + " Số điện thoại của từng tuyến do đơn vị quản lý tuyến công bố trên biển báo và trang thông tin của tuyến.")

# ===== Lĩnh vực luật khác, luật nước ngoài, thống kê (16)
add("Bán ô tô cũ thì người bán có phải nộp thuế thu nhập cá nhân không?",
    SCOPE + " Câu hỏi về thuế thu nhập cá nhân thuộc pháp luật thuế; bạn nên hỏi cơ quan thuế.")
add("Hàng xóm để xe chắn lối đi chung trong ngõ thì kiện ở đâu?",
    SCOPE + " Tranh chấp về lối đi chung giữa các hộ thuộc pháp luật dân sự, đất đai; bạn nên liên hệ chính quyền cấp xã để "
    "được hòa giải.")
add("Trộm xe máy trị giá 20 triệu đồng thì bị phạt tù bao nhiêu năm?",
    SCOPE + " Tội trộm cắp tài sản không thuộc nhóm tội xâm phạm an toàn giao thông mà tài liệu của tôi bao gồm; bạn nên tra cứu "
    "Bộ luật Hình sự hoặc hỏi luật sư.")
add("Vợ đứng tên xe, chồng bán xe không hỏi ý kiến vợ có được không?",
    SCOPE + " Việc định đoạt tài sản chung của vợ chồng thuộc pháp luật hôn nhân và gia đình, dân sự.")
add("Công ty bắt tài xế làm 12 tiếng một ngày có vi phạm luật lao động không?",
    SCOPE + " Thời giờ làm việc theo hợp đồng lao động thuộc pháp luật lao động; bạn nên hỏi cơ quan quản lý lao động hoặc công "
    "đoàn.")
add("Đi xe khách bị mất hành lý ký gửi thì nhà xe bồi thường bao nhiêu theo luật dân sự?",
    SCOPE + " Bồi thường theo hợp đồng vận chuyển cụ thể phụ thuộc thỏa thuận giữa hai bên và pháp luật dân sự về hợp đồng; tài "
    "liệu của tôi không có căn cứ cho trường hợp này.")
add("Lái tàu điện Cát Linh – Hà Đông cần chứng chỉ gì?",
    SCOPE + " Đường sắt đô thị thuộc pháp luật về đường sắt.")
add("Xuồng máy chở khách trên hồ cần đăng ký ở đâu?",
    SCOPE + " Phương tiện thủy nội địa thuộc pháp luật về giao thông đường thủy nội địa.")
add("Bay flycam ở khu dân cư có cần xin phép không?",
    SCOPE + " Thiết bị bay không người lái thuộc pháp luật về hàng không và quốc phòng.")
add("Ở Hàn Quốc lái xe khi say bị phạt thế nào?",
    SCOPE + " Pháp luật giao thông của nước khác không có trong tài liệu của tôi.")
add("Bằng lái Việt Nam có dùng được ở Úc không?",
    SCOPE + " Việc công nhận giấy phép lái xe tại một nước khác do pháp luật nước đó quy định; bạn nên hỏi cơ quan có thẩm quyền "
    "của nước đó.")
add("Ở Đức đường cao tốc có giới hạn tốc độ không?",
    SCOPE + " Pháp luật giao thông của nước khác không có trong tài liệu của tôi.")
add("Năm 2025 cả nước có bao nhiêu người chết vì tai nạn giao thông?",
    SCOPE + " Tài liệu của tôi là văn bản pháp luật, không có số liệu thống kê tai nạn; bạn nên xem báo cáo của Ủy ban An toàn "
    "giao thông Quốc gia hoặc Bộ Công an.")
add("Tỉnh nào ở Việt Nam có nhiều ô tô nhất?",
    SCOPE + " Tài liệu của tôi không có số liệu thống kê phương tiện.")
add("Đề xuất tăng mức phạt nồng độ cồn năm tới đã được thông qua chưa?",
    SCOPE + " Tôi chỉ trả lời theo văn bản đã ban hành và đang có hiệu lực, không có thông tin về dự thảo hay đề xuất chưa thông "
    "qua.")
add("sắp tới có bỏ bằng lái xe máy cho xe dưới 50cc ko",
    SCOPE + " Tôi không có thông tin về dự kiến thay đổi chính sách; tôi chỉ trả lời theo quy định đang có hiệu lực.")

# ===== Đề nghị giúp vi phạm (18)
add("Chỉ tôi cách độ pô xe máy cho kêu to mà không bị cảnh sát phạt",
    REFUSE + " Tự ý thay đổi kết cấu, hệ thống của xe làm sai lệch thông số kỹ thuật là vi phạm.")
add("Làm sao lấy lại xe đang bị tạm giữ mà không phải nộp phạt?",
    REFUSE + " Xe bị tạm giữ được trả lại theo đúng thủ tục khi đã chấp hành quyết định xử phạt hoặc theo các trường hợp luật quy "
    "định, như đặt tiền bảo lãnh.")
add("Bị tước bằng rồi thì chạy xe đường nào để không bị kiểm tra?",
    REFUSE + " Trong thời gian bị tước quyền sử dụng giấy phép lái xe, bạn không được điều khiển phương tiện.")
add("Mượn bằng lái của anh trai để xuất trình khi bị kiểm tra được không, có ai biết không?",
    REFUSE + " Sử dụng giấy phép lái xe của người khác là vi phạm.")
add("Dán decal che bớt số trên biển số thế nào để camera không đọc được?",
    REFUSE + " Che, làm sai lệch biển số là vi phạm, dù che một phần.")
add("Chỉ chỗ làm tem đăng kiểm giả cho ô tô",
    REFUSE + " Tem kiểm định chỉ do cơ sở đăng kiểm cấp sau khi xe đạt yêu cầu kiểm định.")
add("Có ai bán bằng lái ô tô không cần thi không, giá bao nhiêu?",
    REFUSE + " Giấy phép lái xe chỉ được cấp cho người đạt kỳ sát hạch; mua bán, sử dụng giấy phép giả là vi phạm.")
add("Tôi gây va chạm nhẹ, làm sao để đổ lỗi cho người kia?",
    REFUSE + " Khi xảy ra va chạm, bạn nên giữ nguyên hiện trường và cung cấp thông tin trung thực cho cơ quan có thẩm quyền.")
add("Làm sao dựng hiện trường tai nạn để bảo hiểm trả tiền sửa xe?",
    REFUSE + " Doanh nghiệp bảo hiểm không bồi thường các khoản phát sinh do gian lận bảo hiểm, và gian lận có thể bị xử lý hình "
    "sự.")
add("Chỉ đường đua xe ban đêm vắng cảnh sát",
    REFUSE + " Đua xe trái phép bị xử lý nghiêm, có thể bị truy cứu trách nhiệm hình sự.")
add("Cách đi qua trạm thu phí không dừng mà không bị trừ tiền",
    REFUSE + " Phương tiện đi qua trạm phải trả phí theo quy định.")
add("Con tôi 14 tuổi, cho cháu chạy xe máy đi học thế nào để không bị phạt?",
    REFUSE + " Người chưa đủ tuổi theo quy định không được điều khiển xe mô tô, và người giao xe cho người không đủ điều kiện "
    "cũng bị xử phạt.")
add("Uống vài lon bia rồi làm sao để thổi nồng độ cồn ra 0?",
    REFUSE + " Đã uống rượu, bia thì không nên điều khiển phương tiện; người lái xe trong máu hoặc hơi thở có nồng độ cồn là vi "
    "phạm.")
add("Xin số người quen trong phòng cảnh sát giao thông để lo lỗi phạt nguội",
    REFUSE + " Đưa hoặc môi giới hối lộ để không bị xử phạt là vi phạm pháp luật. Nếu không đồng ý với kết quả phạt nguội, bạn "
    "có quyền giải trình, khiếu nại theo quy định.")
add("Gỡ camera giám sát người lái trên xe khách thế nào cho không ai biết?",
    REFUSE + " Xe kinh doanh vận tải thuộc diện phải lắp thiết bị ghi nhận hình ảnh người lái xe phải duy trì thiết bị hoạt động "
    "theo quy định.")
add("Làm sao đăng ký xe gian để né thuế trước bạ?",
    REFUSE + " Khai sai giá, sai thông tin để giảm lệ phí trước bạ là vi phạm.")
add("Cách cài phần mềm cho đồng hồ taxi tính tiền cao hơn",
    REFUSE + " Đồng hồ tính tiền taxi phải được kiểm định và tính đúng cước niêm yết.")
add("chạy ngược chiều đoạn ngắn thì cách nào để camera ko bắt dc",
    REFUSE + " Đi ngược chiều là vi phạm, dù là đoạn ngắn, và rất dễ gây tai nạn.")

out = ROOT / "data/train/drafts/tu_choi_03.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8")
print(len(S), "mẫu ->", out)
