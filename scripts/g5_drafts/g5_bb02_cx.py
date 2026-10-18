"""C1 G5: 80 câu Biển báo từ phần chữ của QCVN 41:2024/BGTVT.

Đã đọc toàn bộ pl2–pl7 và các Điều giao trong brief; không suy đoán hình bị thiếu.
Chú thích mục tại mỗi câu là vị trí đã đối chiếu trong đơn vị phụ lục dài.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QC = "QCVN 41:2024/BGTVT"
S = []
START = 1001


def t(s, d="2025-01-01"):
    return f"qcvn_41_2024:{s}@{d}"


def add(loai, q, a, *can_cu):
    S.append({"key": f"bb-{START + len(S):04d}", "chu_de": "Biển báo", "loai": loai,
              "cau_hoi": q, "dap_an": a, "can_cu": list(can_cu)})


# Phụ lục B: biển cấm (bb-1001–1030).
add("tinh_huong", "Tôi lái xe ưu tiên đến đường đặt P.101 và rào chắn vì cầu bị tắc. Xe ưu tiên có được qua không?",
    "Không. Khi đường cấm vì đường, cầu bị tắc và có hàng rào chắn ngang trước phần xe chạy, các xe được ưu tiên cũng không được phép đi vào (mục B.1 Phụ lục B " + QC + ").", t("pl2"))
add("doi_thuong", "biển P.102 có cấm đi bộ trên vỉa hè ko",
    "Không. Biển P.102 cấm các loại xe cơ giới và thô sơ đi vào theo chiều đặt biển, trừ xe được ưu tiên theo quy định; người đi bộ được phép đi trên vỉa hè hoặc lề đường (mục B.2 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.103a có cấm xe máy hai bánh và xe gắn máy đi qua không?",
    "Không. P.103a cấm các loại xe cơ giới, kể cả xe máy 3 bánh có thùng, nhưng trừ xe máy 2 bánh, xe gắn máy và các xe được ưu tiên theo quy định (mục B.3 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Tôi tắt máy và dắt xe máy qua đường có biển P.104. Biển này có cấm việc dắt xe không?",
    "Không. P.104 là biển “Cấm xe máy”, nhưng không có giá trị cấm những người dắt xe máy (mục B.4 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.106a chỉ cấm ô tô tải hay còn áp dụng cho máy kéo, xe máy chuyên dùng?",
    "Biển P.106a cấm các loại ô tô tải, trừ xe được ưu tiên theo quy định, và có hiệu lực cấm cả máy kéo, xe máy chuyên dùng đi vào đoạn đường đặt biển (mục B.6 Phụ lục B " + QC + ").", t("pl2"))
add("doi_thuong", "xe tải đang chở ít hàng thì xét biển P.106b theo cân hiện tại hay giấy kiểm định",
    "Xét khối lượng chuyên chở theo Giấy chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ. P.106b cấm ô tô tải có khối lượng chuyên chở theo giấy này lớn hơn giá trị ghi trên biển; biển còn cấm cả máy kéo và xe máy chuyên dùng (mục B.6 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Xe buýt có thuộc đối tượng bị cấm bởi biển P.107a “Cấm xe ô tô khách” không?",
    "Không. Biển P.107a báo cấm ô tô chở khách đi qua, trừ xe ưu tiên theo quy định, nhưng không cấm xe buýt (mục B.7a Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Muốn thể hiện biển P.107b chỉ cấm taxi vào một số giờ thì dùng cách nào?",
    "Đặt biển phụ ghi giờ cấm kèm biển P.107b “Cấm xe ô tô taxi” (mục B.7b Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.108 “Cấm xe kéo rơ-moóc” có cấm ô tô sơ-mi rơ-moóc không?",
    "Không. P.108 cấm xe cơ giới kéo theo rơ-moóc, kể cả xe máy, máy kéo, ô tô khách kéo theo rơ-moóc, nhưng trừ ô tô sơ-mi rơ-moóc và xe được ưu tiên có kéo theo rơ-moóc theo quy định (mục B.8 Phụ lục B " + QC + ").", t("pl2"))
add("doi_thuong", "P.110a cấm xe đạp vậy dắt bộ xe qua dc ko",
    "Biển P.110a không có giá trị cấm người dắt xe đạp. Biển này dùng để báo đường cấm xe đạp đi qua (mục B.10 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Đường đặt biển P.111a cấm xe gắn máy có đồng thời cấm xe đạp không?",
    "Không. Biển P.111a “Cấm xe gắn máy” không có giá trị đối với xe đạp (mục B.11 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Tôi đẩy xe nôi cho con qua đường có biển P.113 “Cấm xe người kéo, đẩy”. Có bị biển này cấm không?",
    "Không. Biển P.113 không có giá trị cấm xe nôi của trẻ em và phương tiện chuyên dùng để đi lại của người khuyết tật (mục B.13 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Trọng tải đối chiếu với biển P.115 có tính người, hành lý trên xe không?",
    "Có. P.115 xét trọng tải toàn bộ xe, gồm trọng tải bản thân xe cộng khối lượng người, hành lý và hàng hóa xếp trên xe. Biển cấm xe cơ giới, thô sơ, kể cả xe được ưu tiên, có trọng tải toàn bộ vượt trị số ghi trên biển đi qua (mục B.15 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.116 hạn chế tải trọng trên trục xe được đối chiếu với trục nào?",
    "Đối chiếu tải trọng trên một trục bất kỳ của xe. Biển cấm xe cơ giới, thô sơ, kể cả xe được ưu tiên, nếu trọng tải toàn bộ xe và hàng phân bổ trên một trục bất kỳ vượt trị số ghi trên biển (mục B.16 Phụ lục B " + QC + ").", t("pl2"))
add("doi_thuong", "P.117 tính chiều cao tới nóc xe hay tới cả hàng chất trên nóc",
    "Tính từ mặt đường, mặt cầu đến điểm cao nhất của xe hoặc hàng. P.117 cấm xe cơ giới, thô sơ có chiều cao vượt trị số ghi trên biển, kể cả xe được ưu tiên theo quy định (mục B.17 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Khi kiểm tra chiều ngang theo biển P.118 có tính cả hàng nhô ra không?",
    "Có. Chiều ngang được tính kể cả xe và hàng hóa. Biển P.118 cấm xe cơ giới, thô sơ, kể cả xe được ưu tiên, có chiều ngang vượt trị số ghi trên biển đi qua (mục B.18 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.119 và P.120 khác nhau thế nào về chiều dài được hạn chế?",
    "P.119 ghi độ dài cho phép lớn nhất đối với xe đơn chiếc, kể cả xe và hàng. P.120 ghi độ dài cho phép lớn nhất của toàn bộ đoàn xe cơ giới kéo theo rơ-moóc hoặc sơ-mi rơ-moóc, kể cả xe, moóc và hàng (mục B.19, B.20 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Tôi lái xe ô tô ưu tiên, có được đi sát xe trước hơn cự ly trên biển P.121 không?",
    "Không. P.121 cấm các xe ô tô, kể cả xe được ưu tiên theo quy định, đi cách nhau một cự ly nhỏ hơn trị số ghi trên biển (mục B.21 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.123a “Cấm rẽ trái” có giá trị cấm quay đầu xe không?",
    "Không. Biển P.123a cấm rẽ trái nhưng không có giá trị cấm quay đầu xe (mục B.23 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Tôi gặp biển P.124a ở nút giao và muốn rẽ trái sang đường khác. Biển này có cấm rẽ trái không?",
    "Không. P.124a cấm các loại xe quay đầu theo kiểu chữ U, trừ xe được ưu tiên theo quy định; biển không có giá trị cấm rẽ trái để đi sang hướng đường khác (mục B.24 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Xe máy ba bánh side car có bị biển P.124b cấm quay đầu không?",
    "Có. P.124b cấm ô tô và xe máy 3 bánh (side car) quay đầu theo kiểu chữ U, trừ xe được ưu tiên theo quy định (mục B.24 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "P.124c báo cấm riêng quay đầu hay cấm cả rẽ trái?",
    "P.124c cấm các loại xe rẽ trái đồng thời cấm quay đầu xe (mục B.24 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Trong phạm vi biển P.125, có ngoại lệ nào cho việc vượt xe máy hai bánh, xe gắn máy không?",
    "Có. Biển P.125 cấm các loại xe cơ giới vượt nhau, kể cả xe được ưu tiên theo quy định, nhưng cho phép vượt xe máy 2 bánh, xe gắn máy (mục B.25 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.126 “Cấm xe ô tô tải vượt” áp dụng theo khối lượng nào và có ngoại lệ vượt xe nào?",
    "Biển áp dụng với ô tô tải có khối lượng chuyên chở theo Giấy chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ lớn hơn 3.500 kg, kể cả xe được ưu tiên, khi vượt xe cơ giới khác. Được phép vượt xe máy 2 bánh, xe gắn máy (mục B.26 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Ban đêm tôi đang đi trong phạm vi P.127a thì gặp thêm biển P.127. Tôi theo tốc độ của biển nào?",
    "Phải tuân thủ giá trị tốc độ tối đa ghi trên biển P.127 khi gặp biển này trong phạm vi hiệu lực của P.127a “Tốc độ tối đa cho phép về ban đêm” (mục B.27a Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.127c quy định theo phương tiện trên từng làn yêu cầu người lái tuân thủ những gì?",
    "Các loại phương tiện phải đi đúng làn đường và tuân thủ tốc độ tối đa cho phép trên làn đường đó (mục B.27c Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Gặp biển P.129 “Kiểm tra”, phương tiện vận tải có phải dừng lại không?",
    "Có. Các loại phương tiện vận tải qua nơi đặt biển phải dừng lại làm thủ tục kiểm tra, kiểm soát theo quy định (mục B.29 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "Biển P.130 đặt bên đường có hiệu lực cấm dừng, đỗ ở phía nào?",
    "Biển cấm các loại xe cơ giới dừng và đỗ ở phía đường có đặt biển, trừ xe được ưu tiên theo quy định. Ô tô buýt chạy theo hành trình quy định được hướng dẫn vị trí dừng thích hợp (mục B.30 Phụ lục B " + QC + ").", t("pl2"))
add("quy_tac", "P.131b và P.131c phân biệt ngày cấm đỗ như thế nào?",
    "P.131b cấm các loại xe cơ giới đỗ ở phía đường đặt biển vào những ngày lẻ; P.131c cấm vào những ngày chẵn, trừ các xe được ưu tiên theo quy định (mục B.31 Phụ lục B " + QC + ").", t("pl2"))
add("tinh_huong", "Tôi lái xe ưu tiên gặp P.132, chiều ngược lại đang có xe cơ giới tới đường hẹp. Tôi có phải dừng nhường không?",
    "Có. P.132 có hiệu lực cả với xe được ưu tiên theo quy định. Khi hướng ngược lại đang có xe cơ giới đi tới, phải dừng ở vị trí thích hợp để nhường đường (mục B.32 Phụ lục B " + QC + ").", t("pl2"))

# Phụ lục C: biển nguy hiểm (bb-1031–1040).
add("doi_thuong", "gặp W.203 đường hẹp về phía mình thì ai nhường ai",
    "Xe đi ở chiều đường bị thu hẹp phải nhường đường cho xe đi ngược chiều và phải chú ý quan sát giao thông ngược chiều (mục C.3 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "Biển W.208 đặt trên đường không ưu tiên yêu cầu các xe làm gì khi qua giao nhau?",
    "Phải nhường đường cho xe đi trên đường ưu tiên, trừ các loại xe được quyền ưu tiên theo quy định (mục C.8 Phụ lục C " + QC + ").", t("pl3"))
add("tinh_huong", "Tôi đến cầu tạm có W.213 lúc nước đã ngập cầu. Có được tiếp tục chạy qua không?",
    "Không. Gặp báo hiệu cầu tạm phải thận trọng; khi nước ngập nhất thiết không được qua cầu (mục C.13 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "Biển W.216b dùng để báo điều gì và ở hai đầu đường ngầm còn có báo hiệu nào?",
    "W.216b báo “Đường ngầm có nguy cơ lũ quét”, dùng khi đường ngầm thường xuyên có lũ quét. Hai đầu đường ngầm phải đặt cột báo mức nước, tức cột thủy chí (mục C.16 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "Thấy biển W.224 “Đường người đi bộ cắt ngang”, người lái xe phải xử lý thế nào?",
    "Phải giảm tốc độ, nhường ưu tiên cho người đi bộ và chỉ được chạy xe khi không gây nguy hiểm cho người đi bộ (mục C.24 Phụ lục C " + QC + ").", t("pl3"))
add("tinh_huong", "Tôi thấy W.225 gần trường học nhưng chưa có trẻ nào xuống đường. Biển này yêu cầu tôi chú ý gì?",
    "Phải đi chậm và thận trọng đề phòng khả năng trẻ em xuất hiện, di chuyển bất ngờ trên mặt đường. W.225 báo gần đoạn đường thường có trẻ em đi ngang qua hoặc tụ tập trên đường (mục C.25 Phụ lục C " + QC + ").", t("pl3"))
add("tinh_huong", "Tôi muốn dừng nghỉ ở đoạn có W.228a sau một trận mưa lớn. Có nên dừng trong khu vực đá lở không?",
    "Không. Khi gặp biển báo đá lở phải chú ý, đặc biệt lúc thời tiết xấu, hạn chế tầm nhìn, và không dừng hay đỗ xe trong khu vực đá lở sau những trận mưa lớn (mục C.28 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "Gặp W.232 “Gió ngang”, cần điều chỉnh việc lái xe ra sao?",
    "Cần điều chỉnh tốc độ xe chạy cho thích hợp, đề phòng gió thổi mạnh gây lật xe (mục C.32 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "W.239b thông báo chiều cao tĩnh không thực tế được đo từ đâu đến đâu?",
    "Đó là khoảng cách từ điểm cao nhất của mặt đường đến điểm thấp nhất của chướng ngại vật. Biển W.239b dùng để báo chiều cao tĩnh không thực tế tại vị trí bị giới hạn khoảng cách này (mục C.39 Phụ lục C " + QC + ").", t("pl3"))
add("quy_tac", "Trên đường một chiều, khi dùng W.247 để cảnh báo xe đang đỗ thì cần đặt ở đâu?",
    "Chỉ đặt một biển sau xe hoặc đoàn xe đỗ. Biển đặt trực tiếp trên mặt đường, cách xe tối thiểu 5 m (mục C.47 Phụ lục C " + QC + ").", t("pl3"))

# Phụ lục D: biển hiệu lệnh (bb-1041–1052).
add("tinh_huong", "Tôi gặp R.122 nhưng không có người điều khiển, đèn tín hiệu cũng không bật. Dừng xong thì khi nào được đi?",
    "Chỉ được đi khi trên đường không còn nguy cơ mất an toàn giao thông. Biển R.122 buộc xe cơ giới, thô sơ, kể cả xe được ưu tiên, dừng trước biển hoặc trước vạch ngang đường (mục D.1 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Biển R.301g cho đi thẳng và rẽ trái có cho phép quay đầu xe không?",
    "Có. R.301g đặt trước nơi đường giao nhau cho phép đi thẳng, rẽ trái và quay đầu để đi theo hướng ngược lại (mục D.1a Phụ lục D " + QC + ").", t("pl4"))
add("doi_thuong", "R.304 đường xe thô sơ thì xe máy có dc chạy dọc theo ko",
    "Không. R.304 cấm xe cơ giới, kể cả xe gắn máy và xe được ưu tiên, đi vào đường dành cho xe thô sơ và người đi bộ. Chỉ được đi cắt ngang qua khi bảo đảm tuyệt đối an toàn cho xe thô sơ và người đi bộ (mục D.4 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Biển R.305 có cấm xe đạp và xe lăn dành cho người khuyết tật đi vào không?",
    "Không. R.305 dành đường cho người đi bộ và loại trừ xe đạp, xe lăn dành cho người khuyết tật khỏi các loại xe bị cấm đi vào (mục D.5 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Tốc độ tối thiểu trên R.306 bắt buộc trong điều kiện nào, và xe không đạt tốc độ đó có được vào không?",
    "Xe cơ giới phải vận hành không thấp hơn trị số ghi trên biển trong điều kiện giao thông thuận lợi và an toàn. Xe có tốc độ tối đa theo quy định của nhà sản xuất không đạt tốc độ tối thiểu trên biển thì không được đi vào đường này (mục D.6 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Qua biển R.307 “Hết tốc độ tối thiểu”, xe có thể chạy chậm hơn trị số tối thiểu trước đó không?",
    "Có. Hiệu lực của R.306 đã hết; xe được chạy chậm hơn trị số ghi trên biển nhưng không được gây cản trở các xe khác (mục D.7 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Biển R.403f “Đường dành cho xe máy và xe đạp” có bao gồm xe gắn máy và các xe thô sơ không?",
    "Có. R.403f báo đường dành cho xe máy, kể cả xe gắn máy, và xe đạp, kể cả xe thô sơ (mục D.11 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "R.411 “Hướng đi trên mỗi làn đường phải theo” được phối hợp với vạch gì và yêu cầu người lái thế nào?",
    "Biển phối hợp với vạch 9.3, tức vạch mũi tên chỉ hướng trên mặt đường. Người tham gia giao thông phải đi đúng làn đường được chỉ dẫn hướng phù hợp với hành trình của xe (mục D.13 Phụ lục D " + QC + ").", t("pl4"))
add("tinh_huong", "Tôi đi ô tô con cạnh làn buýt có R.412e, vạch phân làn là nét đứt. Tôi có thể đi vào làn này không?",
    "Có thể, nhưng phải ưu tiên cho xe buýt: nhường đường, chuyển sang làn khác để không ảnh hưởng việc vận hành xe buýt. Nếu vạch phân làn là nét liền thì các phương tiện khác không được đi vào làn buýt (mục D.14 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Biển R.415a có áp dụng cho xe chuyển làn để ra vào hoặc dừng, đỗ bên đường không?",
    "Không. R.415a không áp dụng với các xe chuyển làn để ra vào hoặc dừng, đỗ bên đường. Việc chuyển làn phải căn cứ vào vạch sơn thực tế giữa các làn được phép lưu thông và theo đúng quy định (mục D.16 Phụ lục D " + QC + ").", t("pl4"))
add("tinh_huong", "Tôi đi trong đô thị, đã qua R.420 rồi rẽ sang tuyến đường khác nhưng chưa thấy R.421. Hiệu lực khu đông dân cư còn không?",
    "Còn. R.420 có hiệu lực khu đông dân cư đối với tất cả các tuyến đường nằm trong khu đông dân cư đô thị cho đến vị trí đặt R.421 “Hết khu đông dân cư” (mục D.17 Phụ lục D " + QC + ").", t("pl4"))
add("quy_tac", "Biển R.E,9a “Cấm đỗ xe trong khu vực” có hiệu lực chỉ trên đường đặt biển hay cả khu vực?",
    "Có hiệu lực cho tất cả các tuyến đường trong khu vực. Đây là biển “Bắt đầu vào khu vực”, thể hiện từ ZONE ở phía trên và nội dung cấm ở bên dưới (mục D.19 Phụ lục D " + QC + ").", t("pl4"))

# Phụ lục E: biển chỉ dẫn (bb-1053–1060).
add("tinh_huong", "Tôi đang trên đường có I.401 nhưng nút giao phía trước có điều khiển giao thông. Tôi còn được ưu tiên theo biển không?",
    "Nguyên tắc chạy xe ưu tiên theo biển I.401 hết tác dụng tại chỗ giao nhau có điều khiển giao thông, trừ các xe được quyền ưu tiên theo quy định (mục E.1 Phụ lục E " + QC + ").", t("pl5"))
add("tinh_huong", "Tôi có I.406 ưu tiên qua đường hẹp, nhưng xe ngược chiều đã vào đoạn hẹp. Tôi có phải nhường không?",
    "Có. Nếu xe cơ giới hoặc thô sơ ở hướng ngược chiều đã đi vào phạm vi đường hẹp thì xe theo chiều ưu tiên cũng phải nhường đường (mục E.6 Phụ lục E " + QC + ").", t("pl5"))
add("quy_tac", "Biển I.408 cho phép đỗ xe có kéo dài hiệu lực đến sát giao lộ tiếp theo không?",
    "Không. Phạm vi quy định đỗ xe hết hiệu lực 10 m trước nơi đường giao nhau tiếp theo. Chiều dài nơi đỗ có thể được giới hạn bằng vạch kẻ hoặc hình dáng rõ ràng của bãi đỗ, và khi cần có biển phụ chỉ hiệu lực vùng cho phép đỗ (mục E.8 Phụ lục E " + QC + ").", t("pl5"))
add("doi_thuong", "đỗ theo biển I.408a thì cho bánh bên nào lên hè",
    "Xe phải đỗ sao cho các bánh phía ghế phụ ở trên hè phố. I.408a chỉ dẫn nơi được phép đỗ xe một phần trên hè phố rộng (mục E.8a Phụ lục E " + QC + ").", t("pl5"))
add("quy_tac", "I.423c “Điểm bắt đầu đường đi bộ” có dùng để đánh dấu chỗ người đi bộ cắt ngang đường không?",
    "Không. Biển này chỉ nơi bắt đầu đoạn đường dành cho người đi bộ, không dùng cho vị trí đi bộ cắt ngang qua đường (mục E.23b Phụ lục E " + QC + ").", t("pl5"))
add("quy_tac", "Gặp biển I.425 “Bệnh viện”, việc dùng còi và tốc độ phải thế nào?",
    "Phải đi chậm, chú ý quan sát và không sử dụng còi (mục E.26 Phụ lục E " + QC + ").", t("pl5"))
add("quy_tac", "Biển nào chỉ dẫn nơi có trạm nạp điện cho phương tiện?",
    "Biển I.428b “Trạm nạp điện”. Nếu nơi đó có cả cửa hàng xăng dầu và trạm nạp điện thì dùng I.428c “Cửa hàng xăng dầu và Trạm nạp điện” (mục E.30 Phụ lục E " + QC + ").", t("pl5"))
add("quy_tac", "Đi qua khu vực có I.436 “Trạm cảnh sát giao thông”, người lái có được vượt xe không?",
    "Không được vượt; phải giảm tốc độ đến mức an toàn khi đi qua khu vực này (mục E.39 Phụ lục E " + QC + ").", t("pl5"))

# Phụ lục F: biển phụ (bb-1061–1068).
add("quy_tac", "S.501 và S.502 có cùng chỉ chiều dài đoạn đường chịu tác dụng của biển chính không?",
    "Không. S.501 thông báo chiều dài đoạn đường nguy hiểm, cấm, hiệu lệnh hoặc hạn chế. S.502 thông báo khoảng cách thực tế từ vị trí đặt biển đến đối tượng báo hiệu phía trước khi vị trí đặt biển chính khác quy định chung (mục F.1, F.2 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "Biển phụ S.503b và S.503e chỉ những hướng tác dụng nào?",
    "S.503b chỉ đồng thời hướng trái và phải, vuông góc chiều đi. S.503e chỉ đồng thời hướng trước và sau tại nơi đặt biển nhắc lại lệnh cấm dừng, cấm đỗ, song song với chiều đi (mục F.3 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "Biển phụ S.505a hình một loại xe đặt dưới biển chính dùng để làm gì?",
    "Để chỉ loại xe chịu hiệu lực của biển báo cấm, biển hiệu lệnh hoặc biển chỉ dẫn phía trên. Hình vẽ trên S.505a được bố trí theo loại xe chịu hiệu lực (mục F.5 Phụ lục F " + QC + ").", t("pl6"))
add("tinh_huong", "Tôi qua cầu có cả S.505b và S.505c dưới biển cấm xe tải. Chỉ thỏa mãn biển tổng trọng tải có đủ không?",
    "Không đủ. Xe qua cầu phải thỏa mãn cả S.505b về loại xe và trọng tải toàn bộ xe cho phép, lẫn S.505c về tải trọng trục lớn nhất cho phép tương ứng mỗi loại trục. Trọng tải toàn bộ xe ở S.505b gồm trọng tải bản thân xe và khối lượng chuyên chở cho phép (mục F.6, F.7 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "S.506a và S.506b chỉ hướng đường ưu tiên được đặt trên những đường nào?",
    "S.506a đặt dưới I.401 trên đường ưu tiên; S.506b đặt dưới W.208 và R.122 trên đường không ưu tiên. Các biển này chỉ dẫn hướng đường ưu tiên ở ngã tư (mục F.8 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "Có biển S.507 chỉ hướng rẽ thì có thể bỏ biển cảnh báo chỗ ngoặt nguy hiểm không?",
    "Không. S.507 không thay thế việc đặt các biển báo nguy hiểm W.201 và W.202. S.507 được dùng độc lập để báo trước chỗ rẽ nguy hiểm, chỉ hướng rẽ khi người tham gia giao thông khó nhận biết hướng rẽ của đường (mục F.9 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "S.508 dưới biển cấm có thể quy định hiệu lực theo ngày trong tuần thay vì chỉ theo giờ không?",
    "Có. Thời gian hiệu lực trên S.508 có thể là giờ trong ngày, ngày chẵn hoặc lẻ, thứ trong tuần hoặc một khoảng thời gian nhất định (mục F.10 Phụ lục F " + QC + ").", t("pl6"))
add("quy_tac", "Biển phụ S.H,6 ghi “Except - Ngoại lệ” thể hiện điều gì?",
    "Thể hiện nhóm đối tượng tham gia giao thông mà biển cấm hoặc hạn chế không áp dụng. Nhóm đối tượng được ghi cùng cụm từ “Except - Ngoại lệ” trên biển S.H,6 (mục F.17 Phụ lục F " + QC + ").", t("pl6"))

# Phụ lục G: vạch kẻ đường (bb-1069–1076).
add("quy_tac", "Vạch tim đường 1.4 có một nét liền, một nét đứt thì phía nào được cắt qua?",
    "Xe ở làn tiếp giáp nét đứt được cắt qua và sử dụng làn ngược chiều khi cần thiết; xe ở làn tiếp giáp nét liền không được lấn làn hoặc đè lên vạch (mục G1.1 Phụ lục G " + QC + ").", t("pl7"))
add("quy_tac", "Vạch 2.2 màu trắng phân chia làn cùng chiều có cho phép xe đè vạch để chuyển làn không?",
    "Không. Vạch 2.2 là vạch đơn liền nét phân chia làn cùng chiều trong trường hợp không cho chuyển làn hoặc sử dụng làn khác; xe không được lấn làn, không được đè lên vạch (mục G1.2 Phụ lục G " + QC + ").", t("pl7"))
add("doi_thuong", "kẹt xe có dc dừng trên vạch mắt võng 4.4 ko",
    "Không. Vạch mắt võng 4.4 báo người điều khiển không được dừng phương tiện trong phạm vi mặt đường có bố trí vạch để tránh ùn tắc giao thông (mục G1.4 Phụ lục G " + QC + ").", t("pl7"))
add("tinh_huong", "Tôi đã qua vạch dừng để rẽ trái nhưng hết tín hiệu cho phép khi còn trong làn chờ 5.3. Tôi phải làm gì?",
    "Phải dừng lại trong khu vực làn chờ rẽ trái nếu đã qua vạch dừng trên nhánh dẫn nhưng chưa vượt quá khu vực giới hạn bởi làn chờ rẽ trái trong nút giao (mục G1.5 Phụ lục G " + QC + ").", t("pl7"))
add("quy_tac", "Vạch 6.1 và 6.2 ở mép đường khác nhau về điều cấm thế nào?",
    "Vạch 6.1 là vạch đứt khúc màu vàng báo cấm đỗ xe bên đường; vạch 6.2 là vạch liền nét màu vàng báo cấm cả dừng xe và đỗ xe bên đường (mục G1.6 Phụ lục G " + QC + ").", t("pl7"))
add("tinh_huong", "Tôi đi xe đạp đến vạch 7.4 ở chỗ giao nhau không có người hay tín hiệu điều khiển. Xe cơ giới cắt ngang có phải nhường tôi không?",
    "Xe đạp phải nhường đường cho phương tiện cơ giới chạy trên đường cắt ngang đường xe đạp khi nơi giao nhau không có người, tín hiệu điều khiển giao thông (mục G2.4 Phụ lục G " + QC + ").", t("pl7"))
add("quy_tac", "Vạch hình thoi màu trắng 7.6 trên mặt đường báo điều gì?",
    "Báo sắp đến chỗ có bố trí vạch đi bộ qua đường, đặc biệt ở giữa đoạn đường nối hai nút, để cảnh báo người lái phải nhường đường cho người đi bộ qua đường (mục G2.6 Phụ lục G " + QC + ").", t("pl7"))
add("quy_tac", "Phạm vi cấm dừng, đỗ của phương tiện khác tại vị trí có vạch 9.2 là bao nhiêu?",
    "Các phương tiện khác và người đi bộ không được dừng, đỗ trong phạm vi kẻ vạch và trong khoảng cách 15 m từ vị trí vạch về hai phía theo phương dọc đường. Vạch 9.2 quy định vị trí dừng xe của phương tiện vận tải hành khách công cộng như xe buýt, taxi (mục G4 Phụ lục G " + QC + ").", t("pl7"))

# Báo hiệu khác và hiệu lực chung (bb-1077–1080).
add("quy_tac", "Không có biển báo đứng thì vạch kẻ đường sử dụng độc lập có phải chấp hành không?",
    "Có. Khi vạch kẻ đường được sử dụng độc lập, người tham gia giao thông phải tuân theo ý nghĩa của vạch kẻ đường (Điều 51 " + QC + ").", t("d51"))
add("quy_tac", "Cấm đường khẩn cấp chưa kịp bố trí hệ thống báo hiệu thì cây chắn và cờ đỏ có giá trị gì?",
    "Có giá trị ngăn cấm đường khi một cây chắn ngang đường và cờ đỏ hoặc vải đỏ được treo ở giữa cây chắn; ban đêm dùng đèn đỏ thay cờ (Điều 76 " + QC + ").", t("d76"))
add("quy_tac", "Một làn của đường hai làn bị rào để sửa chữa, hai chiều phải chung làn còn lại. Có cần cảnh báo từ xa không?",
    "Có. Khi phạm vi cấm chiếm hoàn toàn một làn trên đường hai làn khiến hai chiều phải dùng chung làn còn lại, ngoài báo hiệu tại rào chắn còn phải có biện pháp cảnh báo từ xa (khoản 5 Điều 77 " + QC + ").", t("d77:k5"))
add("quy_tac", "Gương cầu lồi ở khúc cua khuất giúp người lái quan sát điều gì?",
    "Giúp quan sát từ xa phương tiện chạy ngược chiều tại đường cong bán kính nhỏ, tầm nhìn bị che khuất để điều chỉnh tốc độ cho phù hợp (khoản 1 Điều 78 " + QC + ").", t("d78:k1"))

out = ROOT / "data/train/drafts/bien_bao_02_cx.jsonl"
out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in S), encoding="utf-8", newline="\n")
print(len(S), "mẫu ->", out)
