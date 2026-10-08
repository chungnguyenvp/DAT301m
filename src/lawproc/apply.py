from lawproc.structure import DIEM, DIEU, KHOAN, Unit, parse_units, unit_address

SKIP_LEVELS = {"mo_dau", "ket_thuc"}
ACTIONS = {"sua_doi", "bo_sung", "bai_bo", "thay_the_van_ban"}
LABEL_PATTERNS = (DIEU, KHOAN, DIEM)
# Cùng ngày: thay thế trước, bổ sung sau, để bản ghi vừa bổ sung không bị thay thế xóa mất.
ACTION_RANK = {"thay_the_van_ban": 0, "sua_doi": 1, "bai_bo": 1, "bo_sung": 2}


class AmendmentError(ValueError):
    """Một hoặc nhiều dòng sửa đổi đã duyệt không áp được. Message liệt kê mọi lỗi."""


def _version(rec: dict) -> dict:
    rec["version_id"] = f"{rec['unit_id']}@{rec['valid_from']}"
    return rec


def _depth(a: dict) -> int:
    return sum(1 for k in ("target_dieu", "target_khoan", "target_diem") if a[k])


def _unit_level(a: dict) -> str:
    return "diem" if a["target_diem"] else "khoan" if a["target_khoan"] else "dieu"


def _is_label(line: str) -> bool:
    return any(p.match(line) for p in LABEL_PATTERNS)


def _early_victim(out: list[dict], match, when: str) -> str | None:
    """Trả về mô tả lỗi nếu có bản ghi sẽ bị đóng mà đã có hiệu lực sau ngày when."""
    for r in out:
        if r["valid_to"] is None and match(r) and r["valid_from"] > when:
            return (f"amendment dated {when} is before the record it would close: {r['unit_id']} "
                    f"is valid only from {r['valid_from']}")
    return None


def _close(out: list[dict], match, when: str) -> None:
    """Đóng hiệu lực các bản ghi đang hiệu lực thoả match tại ngày when.

    Bản ghi có valid_from == when (tạo cùng ngày) bị bỏ hẳn: khoảng hiệu lực bằng 0.
    """
    keep = []
    for r in out:
        if r["valid_to"] is None and match(r):
            if r["valid_from"] == when:
                continue
            r["valid_to"] = when
        keep.append(r)
    out[:] = keep


def apply_amendments(units: list[dict], hl: dict[str, str], amendments: list[dict]) -> list[dict]:
    """Áp các sửa đổi đã duyệt vào danh sách đơn vị, trả về các phiên bản.

    A record is in force at date t iff valid_from <= t and (valid_to is None or t < valid_to).
    Future-dated amendments are recorded with future dates on purpose.

    Chỉ áp dòng status == "duyet". Mọi lỗi trên các dòng đã duyệt được gom lại và raise một
    AmendmentError duy nhất; khi đó không trả kết quả nào. Bỏ mo_dau và ket_thuc.
    """
    problems: list[str] = []

    def bad(i: int, a: dict, reason: str) -> None:
        problems.append(f"row {i} (amend_doc_id={a.get('amend_doc_id', '')!r}, "
                        f"amend_unit_id={a.get('amend_unit_id', '')!r}): {reason}")

    out = [
        _version(dict(u, valid_from=hl.get(u["doc_id"], ""), valid_to=None, source_doc_id=u["doc_id"]))
        for u in units if u["level"] not in SKIP_LEVELS
    ]
    for doc in sorted({r["doc_id"] for r in out}):
        if not hl.get(doc):
            problems.append(f"base units of {doc}: no effective date in hl")

    todo = []
    for i, a in enumerate(amendments):
        if a["status"] != "duyet":
            continue
        n0 = len(problems)
        act = a["action"]
        if act == "thay_the_cum_tu":
            bad(i, a, "approved thay_the_cum_tu: reviewer must convert it to sua_doi with full new_text")
        elif act not in ACTIONS:
            bad(i, a, f"unknown action {act!r}")
        if act != "thay_the_van_ban" and not a["target_dieu"]:
            bad(i, a, "empty target_dieu")
        if not hl.get(a["amend_doc_id"]):
            bad(i, a, f"amending doc {a['amend_doc_id']} has no effective date in hl")
        if len(problems) == n0:
            todo.append((i, a))
    todo.sort(key=lambda t: (hl.get(t[1]["amend_doc_id"], ""), _depth(t[1]), ACTION_RANK[t[1]["action"]], t[0]))

    for i, a in todo:
        when = hl[a["amend_doc_id"]]
        target, action = a["target_doc_id"], a["action"]
        if action == "thay_the_van_ban":
            def whole_doc(r: dict) -> bool:
                return r["doc_id"] == target

            if not any(whole_doc(r) and r["valid_to"] is None for r in out):
                bad(i, a, f"no live unit in target_doc_id {target}")
                continue
            early = _early_victim(out, whole_doc, when)
            if early:
                bad(i, a, early)
                continue
            _close(out, whole_doc, when)
            continue
        addr = unit_address(target, a["target_dieu"], a["target_khoan"] or None, a["target_diem"] or None)

        def under(r: dict) -> bool:
            return r["doc_id"] == target and (r["unit_id"] == addr or r["unit_id"].startswith(addr + ":"))

        live = {r["unit_id"]: r for r in out if r["valid_to"] is None}
        if action in ("sua_doi", "bai_bo") and addr not in live:
            bad(i, a, f"no live unit at {addr}")
            continue
        if action == "bai_bo":
            early = _early_victim(out, under, when)
            if early:
                bad(i, a, early)
                continue
            _close(out, under, when)
            continue
        frag = [x.strip() for x in a["new_text"].splitlines() if x.strip()]
        if not frag:
            bad(i, a, f"{action} with blank new_text")
            continue
        lead: list[str] = []
        for x in frag:
            if _is_label(x):
                break
            lead.append(x)
        parsed = parse_units(target, frag, dieu=a["target_dieu"], khoan=a["target_khoan"] or None)

        if action == "sua_doi":
            outside = [u.unit_id for u in parsed if not (u.unit_id == addr or u.unit_id.startswith(addr + ":"))]
            if outside:
                bad(i, a, f"new text creates {outside} outside {addr}; split the row")
                continue
            if not any(u.unit_id == addr for u in parsed):
                if not lead:
                    bad(i, a, f"new_text has no line for {addr} and no lead-in text")
                    continue
                parsed.insert(0, Unit(addr, target, _unit_level(a), dieu=a["target_dieu"],
                                      khoan=a["target_khoan"] or None, diem=a["target_diem"] or None,
                                      text="\n".join(lead)))
            replaced = live.get(addr)
        else:  # bo_sung
            if not any(u.level in ("dieu", "khoan", "diem") for u in parsed):
                bad(i, a, "bo_sung new_text has no structural label (2a., đ), Điều 6a.)")
                continue
            if lead:
                bad(i, a, "bo_sung text before the first label cannot be placed; split the row")
                continue
            collide = [u.unit_id for u in parsed if u.unit_id in live]
            if collide:
                bad(i, a, f"label collision, already live: {collide}")
                continue
            replaced = live.get(unit_address(target, a["target_dieu"], None, None))

        for u in parsed:
            src = live.get(u.unit_id) or replaced or {}
            if u.chuong is None:
                u.chuong = src.get("chuong")
            if u.muc is None:
                u.muc = src.get("muc")
        if action == "sua_doi":
            early = _early_victim(out, under, when)
            if early:
                bad(i, a, early)
                continue
            _close(out, under, when)
        for u in parsed:
            out.append(_version(dict(u.as_dict(), valid_from=when, valid_to=None,
                                     source_doc_id=a["amend_doc_id"])))

    if problems:
        raise AmendmentError(f"{len(problems)} problem(s) in approved amendment rows:\n"
                             + "\n".join(f"  - {p}" for p in problems))
    seen: set[str] = set()
    dups: set[str] = set()
    for r in out:
        if r["version_id"] in seen:
            dups.add(r["version_id"])
        seen.add(r["version_id"])
    if dups:
        raise AmendmentError(f"duplicate version_id after applying amendments: {sorted(dups)}")
    return out
