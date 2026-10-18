"""C4 G5: nguyên tắc xử phạt và người chưa thành niên; mẫu soạn từ bản hợp nhất 90.

Nguồn được đọc đầy đủ tại mốc 2026-10-01. Không suy từ tình tiết giảm nhẹ
thành miễn phạt; không thay mức trần của người chưa thành niên thành mức cố định.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L = "Luật Xử lý vi phạm hành chính"
S = []


def t(unit):
    return f"vbhn_90_2026_xlvphc:{unit}@2026-07-01"


def add(loai, q, a, *refs):
    S.append({"key": f"np-{1001 + len(S):04d}", "chu_de": "Nộp phạt, giữ xe", "loai": loai,
              "cau_hoi": q, "dap_an": a, "can_cu": [t(u) for u in refs]})


add("tinh_huong", "Em 15 tuổi, nếu một vi phạm giao thông được xác định là do vô ý thì có bị xử phạt hành chính không?",
    "Không thuộc đối tượng bị xử phạt về hành vi do vô ý đó. Người từ đủ 14 tuổi đến dưới 16 tuổi chỉ bị xử phạt vi phạm hành chính do cố ý; người chưa đủ tuổi bị xử phạt đối với trường hợp tương ứng không bị xử phạt hành chính (điểm a khoản 1 Điều 5 và khoản 5 Điều 11 " + L + ").",
    "d5:k1:a", "d11:k5")
add("quy_tac", "Người từ đủ 16 tuổi có chỉ bị xử phạt hành chính khi cố ý vi phạm giao thông không?",
    "Không. Người từ đủ 16 tuổi trở lên bị xử phạt vi phạm hành chính về mọi vi phạm hành chính; đối với người chưa thành niên còn phải áp dụng nguyên tắc xử lý riêng, trong đó có giới hạn tiền phạt (điểm a khoản 1 Điều 5 và khoản 3 Điều 134 " + L + ").",
    "d5:k1:a", "d134:k3")
add("tinh_huong", "Khách nước ngoài lái xe vi phạm hành chính trên đường bộ Việt Nam có được miễn xử phạt chỉ vì quốc tịch không?",
    "Không. Cá nhân nước ngoài vi phạm hành chính trong phạm vi lãnh thổ Việt Nam bị xử phạt theo pháp luật Việt Nam, trừ trường hợp điều ước quốc tế mà Việt Nam là thành viên có quy định khác (điểm c khoản 1 Điều 5 " + L + ").",
    "d5:k1:c")
add("doi_thuong", "bị nói vi phạm giao thông thì mình có quyền đưa bằng chứng là mình ko vi phạm ko",
    "Có. Người có thẩm quyền xử phạt có trách nhiệm chứng minh vi phạm; cá nhân, tổ chức bị xử phạt có quyền tự mình hoặc thông qua người đại diện hợp pháp chứng minh mình không vi phạm (điểm đ khoản 1 Điều 3 " + L + ").",
    "d3:k1:đ")
add("quy_tac", "Một nhóm người cùng thực hiện một hành vi vi phạm giao thông thì chỉ xử phạt người đứng đầu nhóm hay từng người?",
    "Mỗi người vi phạm đều bị xử phạt về hành vi vi phạm hành chính đó. Việc xử phạt vẫn phải căn cứ vào tính chất, mức độ, hậu quả, đối tượng và các tình tiết liên quan (điểm d và điểm c khoản 1 Điều 3 " + L + ").",
    "d3:k1:d", "d3:k1:c")
add("quy_tac", "Khi xử phạt vi phạm giao thông, có phải chỉ nhìn vào tên lỗi mà bỏ qua hậu quả và tình tiết của người vi phạm không?",
    "Không. Việc xử phạt phải căn cứ vào tính chất, mức độ, hậu quả vi phạm, đối tượng vi phạm và tình tiết giảm nhẹ, tăng nặng (điểm c khoản 1 Điều 3 " + L + ").",
    "d3:k1:c")
add("tinh_huong", "Sau vi phạm giao thông, tôi tự nguyện khai báo và thành thật hối lỗi. Đó có phải tình tiết giảm nhẹ không?",
    "Có, tự nguyện khai báo, thành thật hối lỗi là tình tiết giảm nhẹ. Điều này không tự động miễn phạt. Khi xác định mức phạt trong quyết định xử phạt theo khoản 4 Điều 23, việc giảm do tình tiết giảm nhẹ không được thấp hơn mức tối thiểu của khung tiền phạt (khoản 2 Điều 9 và khoản 4 Điều 23 " + L + ").",
    "d9:k2", "d23:k4")
add("tinh_huong", "Tôi đã tự nguyện bồi thường thiệt hại và khắc phục hậu quả của vi phạm giao thông. Việc đó được xem xét thế nào khi xử phạt?",
    "Đó là tình tiết giảm nhẹ: người vi phạm có hành vi ngăn chặn, làm giảm bớt hậu quả hoặc tự nguyện khắc phục hậu quả, bồi thường thiệt hại. Không đồng nghĩa đương nhiên được miễn xử phạt (khoản 1 Điều 9 và khoản 4 Điều 23 " + L + ").",
    "d9:k1", "d23:k4")
add("tinh_huong", "Tôi bị người mà mình lệ thuộc về vật chất ép thực hiện vi phạm hành chính trong giao thông. Có được xem xét giảm nhẹ không?",
    "Có. Vi phạm do bị ép buộc hoặc bị lệ thuộc về vật chất hoặc tinh thần là tình tiết giảm nhẹ; không phải căn cứ đương nhiên miễn mọi chế tài (khoản 4 Điều 9 " + L + ").",
    "d9:k4")
add("doi_thuong", "đang mang thai mà vi phạm giao thông thì có được xem xét giảm nhẹ ko",
    "Có. Người vi phạm là phụ nữ mang thai thuộc tình tiết giảm nhẹ, không tự động được miễn phạt. Khi xác định mức phạt trong quyết định xử phạt theo khoản 4 Điều 23, việc giảm do tình tiết giảm nhẹ không được thấp hơn mức tối thiểu của khung (khoản 5 Điều 9 và khoản 4 Điều 23 " + L + ").",
    "d9:k5", "d23:k4")
add("quy_tac", "Hoàn cảnh khó khăn nào của người vi phạm giao thông được luật coi là tình tiết giảm nhẹ?",
    "Vi phạm vì hoàn cảnh đặc biệt khó khăn mà không do mình gây ra là tình tiết giảm nhẹ. Không phải mọi lý do khó khăn đều mặc nhiên đáp ứng điều kiện này (khoản 6 Điều 9 " + L + ").",
    "d9:k6")
add("quy_tac", "Vi phạm giao thông khi bị kích động tinh thần do hành vi trái pháp luật của người khác có được xem xét giảm nhẹ không?",
    "Có. Vi phạm trong tình trạng bị kích động về tinh thần do hành vi trái pháp luật của người khác gây ra là tình tiết giảm nhẹ; khoản này còn nêu vượt quá giới hạn phòng vệ chính đáng hoặc vượt quá yêu cầu tình thế cấp thiết (khoản 3 Điều 9 " + L + ").",
    "d9:k3")
add("quy_tac", "Thế nào là vi phạm hành chính có tổ chức và tình tiết đó được xem xét tăng nặng hay giảm nhẹ?",
    "Đó là việc cá nhân, tổ chức câu kết với cá nhân, tổ chức khác để cùng thực hiện hành vi vi phạm. Đây là tình tiết tăng nặng, nhưng nếu đã được quy định là hành vi vi phạm thì không được tính lại là tình tiết tăng nặng (khoản 7 Điều 2, điểm a khoản 1 và khoản 2 Điều 10 " + L + ").",
    "d2:k7", "d10:k1:a", "d10:k2")
add("quy_tac", "Lôi kéo người chưa thành niên thực hiện vi phạm giao thông có thể là tình tiết tăng nặng không?",
    "Có. Xúi giục, lôi kéo, sử dụng người chưa thành niên vi phạm là tình tiết tăng nặng, trừ việc tính lại một tình tiết đã được quy định là hành vi vi phạm (điểm c khoản 1 và khoản 2 Điều 10 " + L + ").",
    "d10:k1:c", "d10:k2")
add("tinh_huong", "Tôi vẫn tiếp tục hành vi vi phạm giao thông sau khi người có thẩm quyền yêu cầu chấm dứt. Điều này có thể làm tăng nặng không?",
    "Có. Tiếp tục thực hiện hành vi dù người có thẩm quyền đã yêu cầu chấm dứt là tình tiết tăng nặng; không được tính lại nếu tình tiết đã được quy định là hành vi vi phạm (điểm i khoản 1 và khoản 2 Điều 10 " + L + ").",
    "d10:k1:i", "d10:k2")
add("quy_tac", "Sau khi vi phạm giao thông rồi trốn tránh, che giấu vi phạm thì có thể bị xem là có tình tiết tăng nặng không?",
    "Có. Sau khi vi phạm có hành vi trốn tránh, che giấu vi phạm là tình tiết tăng nặng, với giới hạn không tính lại tình tiết đã được quy định là hành vi vi phạm (điểm k khoản 1 và khoản 2 Điều 10 " + L + ").",
    "d10:k1:k", "d10:k2")
add("quy_tac", "Một tình tiết đã dùng để xác định hành vi vi phạm giao thông có được tính thêm là tình tiết tăng nặng nữa không?",
    "Không. Tình tiết tăng nặng được liệt kê mà đã được quy định là hành vi vi phạm hành chính thì không được coi là tình tiết tăng nặng nữa (khoản 2 Điều 10 " + L + ").",
    "d10:k2")
add("quy_tac", "Tái phạm sau một quyết định xử phạt và vi phạm hành chính nhiều lần khác nhau ở việc đã bị xử lý hay chưa như thế nào?",
    "Trong nhánh tái phạm sau khi đã bị ra quyết định xử phạt, cá nhân, tổ chức chưa hết thời hạn được coi là chưa bị xử phạt mà lại thực hiện hành vi đã bị xử phạt. Vi phạm nhiều lần là đã thực hiện hành vi đó trước đây nhưng chưa bị xử lý và chưa hết thời hiệu xử lý (khoản 5 và khoản 6 Điều 2 " + L + ").",
    "d2:k5", "d2:k6")
add("quy_tac", "Muốn được xác định là vi phạm giao thông trong tình thế cấp thiết thì chỉ cần nói có việc gấp có đủ không?",
    "Không. Phải có nguy cơ đang thực tế đe dọa lợi ích được bảo vệ, không còn cách nào khác ngoài gây thiệt hại nhỏ hơn thiệt hại cần ngăn ngừa. Hành vi trong tình thế cấp thiết thuộc trường hợp không xử phạt hành chính; không thể chỉ dựa vào lời nói có việc gấp (khoản 11 Điều 2 và khoản 1 Điều 11 " + L + ").",
    "d2:k11", "d11:k1")
add("quy_tac", "Sự kiện bất khả kháng để không xử phạt hành chính phải đáp ứng những đặc điểm nào?",
    "Sự kiện phải xảy ra khách quan, không thể lường trước và không thể khắc phục dù đã áp dụng mọi biện pháp cần thiết và khả năng cho phép. Thực hiện hành vi vi phạm do sự kiện bất khả kháng thuộc trường hợp không xử phạt (khoản 14 Điều 2 và khoản 4 Điều 11 " + L + ").",
    "d2:k14", "d11:k4")
add("quy_tac", "Cứ mắc bệnh là không phải chịu xử phạt hành chính về giao thông có đúng không?",
    "Không. Trường hợp không có năng lực trách nhiệm hành chính là đang mắc bệnh tâm thần hoặc bệnh khác làm mất khả năng nhận thức hoặc điều khiển hành vi khi thực hiện hành vi vi phạm. Người không có năng lực này không bị xử phạt hành chính (khoản 15 Điều 2 và khoản 5 Điều 11 " + L + ").",
    "d2:k15", "d11:k5")
add("doi_thuong", "cảnh cáo vi phạm hành chính chỉ nói miệng thôi hay phải có văn bản",
    "Cảnh cáo được quyết định bằng văn bản (Điều 22 " + L + ").",
    "d22")
add("quy_tac", "Vi phạm giao thông không nghiêm trọng và có tình tiết giảm nhẹ thì đương nhiên được đổi tiền phạt thành cảnh cáo không?",
    "Không đương nhiên. Với cá nhân, tổ chức nói chung, ngoài việc vi phạm không nghiêm trọng và có tình tiết giảm nhẹ, quy định áp dụng còn phải cho phép hình thức cảnh cáo. Luật có quy định riêng về cảnh cáo với người chưa thành niên thuộc độ tuổi tương ứng (Điều 22 " + L + ").",
    "d22")
add("quy_tac", "Cảnh cáo và phạt tiền có thể chỉ áp dụng làm hình thức xử phạt bổ sung không?",
    "Không. Cảnh cáo và phạt tiền chỉ được quy định, áp dụng là hình thức xử phạt chính (khoản 2 Điều 21 " + L + ").",
    "d21:k2", "d21:k1:a", "d21:k1:b")
add("quy_tac", "Một hành vi vi phạm giao thông có thể bị áp dụng hai hình thức xử phạt chính cùng lúc không?",
    "Không. Mỗi vi phạm hành chính được quy định một hình thức xử phạt chính; có thể quy định một hoặc nhiều hình thức xử phạt bổ sung kèm theo (khoản 3 Điều 21 " + L + ").",
    "d21:k3")
add("quy_tac", "Khi chưa xét tình tiết riêng, mức tiền phạt cụ thể trong một khung phạt được xác định theo nguyên tắc nào?",
    "Là mức trung bình của khung tiền phạt quy định cho hành vi đó. Có tình tiết giảm nhẹ thì có thể giảm nhưng không dưới mức tối thiểu; có tình tiết tăng nặng thì có thể tăng nhưng không vượt mức tối đa của khung (khoản 4 Điều 23 " + L + ").",
    "d23:k4")
add("tinh_huong", "Giấy phép hoạt động vận tải của tôi đang bị tước quyền sử dụng có thời hạn. Trong thời gian đó tôi có được tiếp tục hoạt động ghi trong giấy phép không?",
    "Không. Trong thời gian bị tước quyền sử dụng giấy phép, cá nhân, tổ chức không được tiến hành các hoạt động ghi trong giấy phép đó (khoản 1 Điều 25 " + L + ").",
    "d25:k1")
add("quy_tac", "Luật quy định khoảng thời hạn chung của hình thức tước quyền sử dụng giấy phép có thời hạn là bao lâu?",
    "Từ 01 tháng đến 24 tháng, kể từ ngày quyết định xử phạt có hiệu lực thi hành. Thời hạn cụ thể của từng hành vi còn phải theo khung của hành vi đó, có xét tăng nặng, giảm nhẹ trong giới hạn khung (khoản 3 Điều 25 " + L + ").",
    "d25:k3")
add("quy_tac", "Tịch thu phương tiện vi phạm hành chính có phải chỉ là giữ xe rồi trả lại như tạm giữ không?",
    "Không. Tịch thu là sung vào ngân sách nhà nước vật, tiền, hàng hóa, phương tiện liên quan trực tiếp đến vi phạm, áp dụng đối với vi phạm hành chính nghiêm trọng do lỗi cố ý. Đây không phải việc giữ xe để chờ trả lại (Điều 26 " + L + ").",
    "d26")
add("tinh_huong", "Em 15 tuổi vi phạm hành chính do cố ý trong giao thông. Có được áp dụng phạt tiền như người lớn không?",
    "Không. Người từ đủ 14 tuổi đến dưới 16 tuổi vi phạm hành chính không bị áp dụng hình thức phạt tiền; cảnh cáo được áp dụng đối với các hành vi vi phạm hành chính của người trong độ tuổi này (khoản 3 Điều 134 và Điều 22 " + L + ").",
    "d134:k3", "d22", "d5:k1:a")
add("doi_thuong", "em 17 tuổi bị phạt giao thông thì tiền phạt luôn đúng bằng nửa người lớn à",
    "Không phải luôn đúng bằng một nửa. Với người từ đủ 16 tuổi đến dưới 18 tuổi, mức tiền phạt không quá 1/2 mức tiền phạt áp dụng đối với người thành niên (khoản 3 Điều 134 " + L + ").",
    "d134:k3")
add("quy_tac", "Người chưa thành niên bị phạt mà không có tiền nộp hoặc không có khả năng khắc phục hậu quả thì ai thực hiện thay?",
    "Cha mẹ hoặc người giám hộ phải thực hiện thay trong trường hợp người chưa thành niên không có tiền nộp phạt hoặc không có khả năng thực hiện biện pháp khắc phục hậu quả (khoản 3 Điều 134 " + L + ").",
    "d134:k3")
add("quy_tac", "Khi xử lý người chưa thành niên vi phạm giao thông, bí mật riêng tư của họ có được bảo vệ không?",
    "Có. Bí mật riêng tư của người chưa thành niên phải được tôn trọng và bảo vệ trong quá trình xử lý vi phạm hành chính (khoản 4 Điều 134 " + L + ").",
    "d134:k4")
add("quy_tac", "Người chưa thành niên chấp hành xong quyết định xử phạt hành chính thì sau bao lâu không tái phạm được coi là chưa bị xử phạt?",
    "Trong thời hạn 06 tháng kể từ ngày chấp hành xong quyết định xử phạt hoặc từ ngày hết thời hiệu thi hành quyết định xử phạt mà không tái phạm thì được coi là chưa bị xử phạt vi phạm hành chính (khoản 1 Điều 137 " + L + ").",
    "d137:k1")
add("quy_tac", "Người chưa thành niên được áp dụng biện pháp thay thế xử lý vi phạm hành chính đúng điều kiện có bị coi là đã bị xử lý vi phạm hành chính không?",
    "Không. Biện pháp thay thế phải được xem xét khi đủ điều kiện luật định, và việc áp dụng không được coi là đã bị xử lý vi phạm hành chính. Các biện pháp thay thế gồm nhắc nhở, quản lý tại gia đình và giáo dục dựa vào cộng đồng (khoản 5 Điều 134 và Điều 138 " + L + ").",
    "d134:k5", "d138", "d138:k1", "d138:k2", "d138:k3")


if __name__ == "__main__":
    out = ROOT / "data/train/drafts/nop_phat_03_cx.jsonl"
    out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
    print(len(S), "mẫu ->", out)
