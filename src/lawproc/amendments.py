import re

from lawproc import config
from lawproc.clean import normalize
from lawproc.structure import Unit

ACTION = re.compile(r"^(Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Bỏ|Thay thế|Thay cụm từ)\b", re.IGNORECASE)
PASSIVE = re.compile(
    r"^((?:điểm|khoản|Điều)\s+.+?)\s+được\s+(Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Thay thế)\b",
    re.IGNORECASE,
)
ADDR = re.compile(
    r"(?:điểm\s+([a-zđ]{1,2})\s+)?(?:khoản\s+(\d+[a-zđ]?)\s+)?Điều\s+(\d+[a-zđ]?)(?!\s*\.\s*\S)",
    re.IGNORECASE,
)
NEW_LABEL = re.compile(r"Bổ sung\s+((?:điểm|khoản|Điều)\s+[\wđ]+)\s+vào", re.IGNORECASE)
POINT = re.compile(r"điểm\s+([a-zđ]{1,2})(?![\wđ])", re.IGNORECASE)
KHOAN_TOK = re.compile(r"khoản\s+(\d+[a-zđ]?)(?![\wđ])", re.IGNORECASE)
QUOTED = re.compile(r"“[^”]*(?:”|$)")
ACTION_MAP = {"sửa đổi, bổ sung": "sua_doi", "sửa đổi": "sua_doi", "bổ sung": "bo_sung",
              "bãi bỏ": "bai_bo", "bỏ": "bai_bo", "thay thế": "thay_the_cum_tu", "thay cụm từ": "thay_the_cum_tu"}


def _target_from(text: str) -> str:
    t = normalize(text).lower()
    for alias, doc_id in config.TARGET_ALIASES.items():
        if normalize(alias).lower() in t:
            return doc_id
    return ""


def _new_text(full: str, first_line: str, action: str) -> str:
    if action != "thay_the_cum_tu" and "“" in first_line:
        rest = first_line[first_line.index("“"):] + (full[len(first_line):] if full.startswith(first_line) else "")
    else:
        rest = full[len(first_line):] if full.startswith(first_line) else ""
    rest = rest.strip()
    if rest.startswith("“"):
        rest = rest[1:]
    rest = re.sub(r"”\s*[.;]?\s*$", "", rest)
    return rest.strip()


def _count_tokens(text: str) -> int:
    return len(POINT.findall(text)) + len(KHOAN_TOK.findall(text))


def _join(*parts: str) -> str:
    return "; ".join(p for p in parts if p)


def extract_instructions(doc_id: str, units: list[Unit], doc_title: str) -> list[dict]:
    titles = {u.dieu: u.title for u in units if u.level == "dieu"}
    rows: list[dict] = []
    ctx: dict[tuple[str, str | None], int] = {}  # (điều, khoản | None) -> chỉ số dòng đã xác định đích
    with_children: set[int] = set()
    for u in units:
        if u.level not in ("dieu", "khoan", "diem"):
            continue
        body = u.title if u.level == "dieu" and not u.text else u.text
        first = body.split("\n")[0]
        if u.level == "dieu" and u.text:
            first, body = u.title, f"{u.title}\n{u.text}"
        m = ACTION.match(first)
        pm = None if m else PASSIVE.match(first)
        if m:
            action = ACTION_MAP[m.group(1).lower()]
        elif pm:
            action = ACTION_MAP[pm.group(2).lower()]
        else:
            continue
        head = QUOTED.sub("", first)
        if "cụm từ" in normalize(head).lower():
            action = "thay_the_cum_tu"
        count_head = NEW_LABEL.sub("", head) if action == "bo_sung" else head
        label = NEW_LABEL.search(head)
        ghi: list[str] = []
        addrs = list(ADDR.finditer(head))
        target = _target_from(head) or _target_from(titles.get(u.dieu, "")) or _target_from(doc_title)
        if addrs:
            a = addrs[-1] if action == "bo_sung" else addrs[0]
            dieu_, khoan_, diem_ = a.group(3), a.group(2) or "", a.group(1) or ""
            compound = _count_tokens(count_head) > bool(a.group(1)) + bool(a.group(2))
            if (len(addrs) > 1 and action != "bo_sung") or compound:
                ghi.append("nhiều địa chỉ")
        else:
            if u.level == "dieu":
                continue  # tiêu đề kiểu "Sửa đổi, bổ sung một số điều của ..." chỉ là ngữ cảnh
            keys = [(u.dieu, None)] if u.level == "khoan" else [(u.dieu, u.khoan), (u.dieu, None)]
            parent_idx = next((ctx[k] for k in keys if k in ctx), None)
            if parent_idx is None:
                dieu_, khoan_, diem_ = "", "", ""
                ghi.append("không rõ địa chỉ")
            else:
                p = rows[parent_idx]
                with_children.add(parent_idx)
                pts = POINT.findall(count_head)
                khs = KHOAN_TOK.findall(count_head)
                dieu_ = p["target_dieu"]
                khoan_ = khs[-1] if khs else p["target_khoan"]
                diem_ = pts[-1] if pts else ""
                target = p["target_doc_id"]
                ghi.append("địa chỉ suy từ chỉ dẫn cha")
                if len(pts) > 1 or len(khs) > 1:
                    ghi.append("nhiều địa chỉ")
        if not target:
            ghi.append("chưa rõ văn bản đích")
        rows.append({
            "amend_doc_id": doc_id, "amend_unit_id": u.unit_id, "action": action, "target_doc_id": target,
            "target_dieu": dieu_, "target_khoan": khoan_, "target_diem": diem_,
            "new_label": label.group(1) if label else "", "instruction": first,
            "new_text": "" if action in ("bai_bo", "thay_the_cum_tu") else _new_text(body, first, action),
            "status": "chua_duyet", "ghi_chu": _join(*ghi),
        })
        if dieu_ and u.level in ("dieu", "khoan"):
            ctx[(u.dieu, u.khoan if u.level == "khoan" else None)] = len(rows) - 1
    for idx in with_children:
        if rows[idx]["new_text"] == "":
            rows[idx]["ghi_chu"] = _join(rows[idx]["ghi_chu"], "chứa chỉ dẫn con")
    return rows
