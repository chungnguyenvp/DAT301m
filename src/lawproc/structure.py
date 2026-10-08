import re
from dataclasses import asdict, dataclass

CHUONG = re.compile(r"^(?:Chương|CHƯƠNG)\s+([IVXLC]+|\d+)\b\.?\s*(.*)$")
MUC = re.compile(r"^(?:Mục|MỤC)\s+(\d+)\b\.?\s*(.*)$")
DIEU = re.compile(r"^Điều\s+(\d+[a-zđ]?)\.\s*(.*)$")
KHOAN = re.compile(r"^(\d+[a-zđ]?)\.\s+(.*)$")
DIEM = re.compile(r"^([a-zđ]{1,2})\)\s+(.*)$")
PHULUC = re.compile(r"^(?:PHỤ LỤC|Phụ lục)\b")
KET_THUC = re.compile(r"^Nơi nhận")


@dataclass
class Unit:
    unit_id: str
    doc_id: str
    level: str
    chuong: str | None = None
    muc: str | None = None
    dieu: str | None = None
    khoan: str | None = None
    diem: str | None = None
    title: str = ""
    text: str = ""
    line_start: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


def unit_address(doc_id: str, dieu: str | None, khoan: str | None, diem: str | None) -> str:
    s = f"{doc_id}:d{dieu}"
    if khoan:
        s += f":k{khoan}"
    if diem:
        s += f":{diem}"
    return s


def _append(unit: "Unit | None", line: str) -> None:
    if unit is not None:
        unit.text = f"{unit.text}\n{line}" if unit.text else line


def parse_units(doc_id: str, lines: list[str], dieu: str | None = None, khoan: str | None = None) -> list[Unit]:
    fragment = dieu is not None
    units: list[Unit] = []
    seen: dict[str, int] = {}
    chuong = muc = None
    pending = None  # "chuong" | "muc": dòng kế tiếp là tên Chương/Mục
    in_annex = False
    annex_n = 0
    depth = 0
    seen_dieu = fragment
    cur: Unit | None = None

    def add(unit: Unit) -> Unit:
        n = seen.get(unit.unit_id, 0) + 1
        seen[unit.unit_id] = n
        if n > 1:
            unit.unit_id = f"{unit.unit_id}#{n}"
        units.append(unit)
        return unit

    if not fragment:
        cur = add(Unit(f"{doc_id}:mo_dau", doc_id, "mo_dau"))

    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        quoted = depth > 0 or line.startswith(("“", "\""))
        depth = max(0, depth + line.count("“") - line.count("”"))
        if quoted:
            _append(cur, line)
            continue
        if not fragment and KET_THUC.match(line):
            cur = add(Unit(f"{doc_id}:ket_thuc", doc_id, "ket_thuc", text=line, line_start=i))
            continue
        if seen_dieu and not fragment and PHULUC.match(line) and len(line) < 150:
            in_annex = True
            annex_n += 1
            cur = add(Unit(f"{doc_id}:pl{annex_n}", doc_id, "phu_luc", title=line, line_start=i))
            continue
        if in_annex or (cur is not None and cur.level == "ket_thuc"):
            _append(cur, line)
            continue
        if pending:
            if pending == "chuong":
                chuong = f"{chuong} {line}"
            else:
                muc = f"{muc} {line}"
            pending = None
            continue
        if m := CHUONG.match(line):
            chuong, muc = m.group(1), None
            pending = None if m.group(2) else "chuong"
            if m.group(2):
                chuong = f"{chuong} {m.group(2)}"
            continue
        if m := MUC.match(line):
            muc = m.group(1)
            pending = None if m.group(2) else "muc"
            if m.group(2):
                muc = f"{muc} {m.group(2)}"
            continue
        if m := DIEU.match(line):
            dieu, khoan, seen_dieu = m.group(1), None, True
            cur = add(Unit(unit_address(doc_id, dieu, None, None), doc_id, "dieu", chuong, muc, dieu,
                           title=m.group(2), line_start=i))
            continue
        if dieu is not None and (m := KHOAN.match(line)):
            khoan = m.group(1)
            cur = add(Unit(unit_address(doc_id, dieu, khoan, None), doc_id, "khoan", chuong, muc, dieu, khoan,
                           text=m.group(2), line_start=i))
            continue
        if dieu is not None and (m := DIEM.match(line)):
            cur = add(Unit(unit_address(doc_id, dieu, khoan, m.group(1)), doc_id, "diem", chuong, muc, dieu,
                           khoan, m.group(1), text=m.group(2), line_start=i))
            continue
        _append(cur, line)
    return units
