import re
import unicodedata

CONGBAO_HEADER = re.compile(
    r"^(?:\d{1,4}\s+)?CÔNG BÁO\s*/\s*Số\s*[\d\s+]+/\s*Ngày\s*\d{1,2}-\d{1,2}-\d{4}(?:\s+\d{1,4})?$",
    re.IGNORECASE,
)
PAGE_NO = re.compile(r"^\d{1,4}$")
BANNERS = {
    "VĂN BẢN QUY PHẠM PHÁP LUẬT", "PHẦN VĂN BẢN QUY PHẠM PHÁP LUẬT", "VĂN BẢN KHÁC",
    "VĂN BẢN PHÁP LUẬT KHÁC", "VĂN BẢN HỢP NHẤT - VĂN PHÒNG QUỐC HỘI",
}
XEM_TIEP = re.compile(r"^\(\s*Xem tiếp Công báo số[^)]*\)\.?$", re.IGNORECASE)
TIEP_THEO = re.compile(r"^\(\s*Tiếp theo Công báo số\s*(\d+)", re.IGNORECASE)
# Tiêu đề phụ lục: "PHỤ LỤC", "PHỤ LỤC I", "Phụ lục số 02", "PHỤ LỤC LHI (Ban hành ...)". Câu thân bài mở đầu bằng
# "Phụ lục I ban hành kèm theo ..." (chữ thường sau số hiệu) không phải tiêu đề.
VN_UPPER = "A-ZĐÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ"
PHULUC_HEADING = re.compile(
    r"^(?:PHỤ LỤC|Phụ lục)\b(?:\s+(?:SỐ|[Ss]ố))?"
    rf"(?:$|\s+(?:[{VN_UPPER}]{{1,6}}|\d+[A-Za-zđ]?)\b\s*(?:$|[(:.\-–—/]|[{VN_UPPER}]))"
)
STRUCT_START = re.compile(
    r"^(?:Phần|PHẦN|Chương|CHƯƠNG|Mục|MỤC|Điều\s+\d+|\d+[a-zđ]?\.\s|[a-zđ]{1,2}\d?\)\s|[“\"])"
)
END_PUNCT = (".", ":", ";", "!", "?", "”", "\"", ")")
DIEU_HEADING = re.compile(r"^Điều\s+\d+[a-zđ]?\.")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.replace(" ", " ").replace("Р", "P").replace("р", "p").replace("Ð", "Đ").replace("ð", "đ")
    return re.sub(r"[ \t]+", " ", s).strip()


def strip_part(lines: list[str]) -> tuple[list[str], int | None]:
    lines = [normalize(x) for x in lines]
    cont = None
    for i, line in enumerate(lines[:20]):
        m = TIEP_THEO.match(line)
        if m:
            cont = int(m.group(1))
            lines = lines[i + 1:]
            break
    out = [
        x for x in _drop_signature_stamps(lines)
        if x and not CONGBAO_HEADER.match(x) and not PAGE_NO.match(x)
        and x.upper() not in BANNERS and not XEM_TIEP.match(x)
    ]
    return out, cont


# Dấu chữ ký số in trên trang PDF: "Ký bởi: …" rồi các dòng "Email: …", "Cơ quan: …", "Thời gian ký: …".
STAMP_START = re.compile(r"^Ký bởi\s*:")
STAMP_FIELD = re.compile(r"^(?:Email|Cơ quan|Thời gian ký|Ngày ký)\s*:")


def _drop_signature_stamps(lines: list[str]) -> list[str]:
    """Bỏ khối dấu chữ ký số; chỉ bỏ dòng "Cơ quan: …" khi nó nằm ngay sau dòng "Ký bởi: …"."""
    out, in_stamp = [], False
    for x in lines:
        if STAMP_START.match(x):
            in_stamp = True
            continue
        if in_stamp and STAMP_FIELD.match(x):
            continue
        in_stamp = False
        out.append(x)
    return out


def order_parts(parts: list[tuple[list[str], int | None]]) -> list[list[str]]:
    return [p for p, _ in sorted(parts, key=lambda pc: -1 if pc[1] is None else pc[1])]


LABEL_LINE = re.compile(r"^(?:\d+[a-zđ]?\.|[a-zđ]{1,2}\d?\))\s")
SHORT_LINE = 0.75  # so với độ dài dòng chạy hết bề ngang trang (phân vị 75 của văn bản)


def join_wrapped(lines: list[str]) -> list[str]:
    lines = [x for x in (normalize(x) for x in lines) if x]
    lengths = sorted(len(x) for x in lines)
    full = lengths[int(len(lengths) * 0.75)] if lengths else 0
    out: list[str] = []
    for line in lines:
        if out and not STRUCT_START.match(line) and not PHULUC_HEADING.match(line) and not out[-1].endswith(END_PUNCT) and not (
            DIEU_HEADING.match(out[-1]) and not line[0].islower()  # tiêu đề Điều chưa chấm câu + đoạn thân bài viết hoa
        ) and not (
            # tiêu đề khoản/điểm ngắn đứng riêng một dòng ("1. Nộp hồ sơ đề nghị") + đoạn thân viết hoa
            LABEL_LINE.match(out[-1]) and len(out[-1]) < SHORT_LINE * full and line[0].isupper()
        ):
            out[-1] = f"{out[-1]} {line}"
        else:
            out.append(line)
    return out
