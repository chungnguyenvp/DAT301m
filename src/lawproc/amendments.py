import re

from lawproc import config
from lawproc.clean import normalize
from lawproc.structure import Unit

ACTION = re.compile(r"^(Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Thay thế|Thay cụm từ)\b", re.IGNORECASE)
ADDR = re.compile(
    r"(?:điểm\s+([a-zđ]{1,2})\s+)?(?:khoản\s+(\d+[a-zđ]?)\s+)?Điều\s+(\d+[a-zđ]?)(?!\s*\.\s*\S)",
    re.IGNORECASE,
)
NEW_LABEL = re.compile(r"Bổ sung\s+((?:điểm|khoản|Điều)\s+[\wđ]+)\s+vào", re.IGNORECASE)
ACTION_MAP = {"sửa đổi, bổ sung": "sua_doi", "sửa đổi": "sua_doi", "bổ sung": "bo_sung",
              "bãi bỏ": "bai_bo", "thay thế": "thay_the_cum_tu", "thay cụm từ": "thay_the_cum_tu"}


def _target_from(text: str) -> str:
    t = normalize(text).lower()
    for alias, doc_id in config.TARGET_ALIASES.items():
        if normalize(alias).lower() in t:
            return doc_id
    return ""


def _new_text(full: str, first_line: str) -> str:
    rest = full[len(first_line):].strip() if full.startswith(first_line) else ""
    if not rest and "“" in first_line and ACTION.match(first_line).group(1).lower() != "thay thế":
        rest = first_line[first_line.index("“"):]
    rest = rest.strip()
    if rest.startswith("“"):
        rest = rest[1:]
    rest = re.sub(r"”\s*[.;]?\s*$", "", rest)
    return rest.strip()


def extract_instructions(doc_id: str, units: list[Unit], doc_title: str) -> list[dict]:
    titles = {u.dieu: u.title for u in units if u.level == "dieu"}
    rows: list[dict] = []
    for u in units:
        if u.level not in ("dieu", "khoan", "diem"):
            continue
        body = u.title if u.level == "dieu" and not u.text else u.text
        first = body.split("\n")[0]
        if u.level == "dieu" and u.text:
            first, body = u.title, f"{u.title}\n{u.text}"
        m = ACTION.match(first)
        if not m:
            continue
        action = ACTION_MAP[m.group(1).lower()]
        head = first.split("“")[0] if action != "thay_the_cum_tu" else re.sub(r"“[^”]*”", "", first)
        addrs = list(ADDR.finditer(head))
        if not addrs:
            continue  # tiêu đề kiểu "Sửa đổi, bổ sung một số điều của ..." chỉ là ngữ cảnh
        target = _target_from(head) or _target_from(titles.get(u.dieu, "")) or _target_from(doc_title)
        label = NEW_LABEL.search(head)
        a = addrs[-1] if action == "bo_sung" else addrs[0]
        rows.append({
            "amend_doc_id": doc_id, "amend_unit_id": u.unit_id, "action": action, "target_doc_id": target,
            "target_dieu": a.group(3), "target_khoan": a.group(2) or "", "target_diem": a.group(1) or "",
            "new_label": label.group(1) if label else "", "instruction": first,
            "new_text": "" if action in ("bai_bo", "thay_the_cum_tu") else _new_text(body, first),
            "status": "chua_duyet", "ghi_chu": "nhiều địa chỉ" if len(addrs) > 1 and action != "bo_sung" else "",
        })
    return rows
