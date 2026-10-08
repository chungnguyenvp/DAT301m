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
STRUCT_START = re.compile(
    r"^(?:Phần|PHẦN|Chương|CHƯƠNG|Mục|MỤC|PHỤ LỤC|Phụ lục|Điều\s+\d+|\d+[a-zđ]?\.\s|[a-zđ]{1,2}\)\s|[“\"])"
)
END_PUNCT = (".", ":", ";", "!", "?", "”", "\"", ")")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.replace(" ", " ").replace("Р", "P").replace("р", "p")
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
        x for x in lines
        if x and not CONGBAO_HEADER.match(x) and not PAGE_NO.match(x)
        and x.upper() not in BANNERS and not XEM_TIEP.match(x)
    ]
    return out, cont


def order_parts(parts: list[tuple[list[str], int | None]]) -> list[list[str]]:
    return [p for p, _ in sorted(parts, key=lambda pc: -1 if pc[1] is None else pc[1])]


def join_wrapped(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in (normalize(x) for x in lines):
        if not line:
            continue
        if out and not STRUCT_START.match(line) and not out[-1].endswith(END_PUNCT):
            out[-1] = f"{out[-1]} {line}"
        else:
            out.append(line)
    return out
