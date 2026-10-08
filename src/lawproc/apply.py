from lawproc.structure import Unit, parse_units, unit_address

SKIP_LEVELS = {"mo_dau", "ket_thuc"}


def _version(rec: dict) -> dict:
    rec["version_id"] = f"{rec['unit_id']}@{rec['valid_from']}"
    return rec


def apply_amendments(units: list[dict], hl: dict[str, str], amendments: list[dict]) -> list[dict]:
    out = [
        _version(dict(u, valid_from=hl.get(u["doc_id"], ""), valid_to=None, source_doc_id=u["doc_id"]))
        for u in units if u["level"] not in SKIP_LEVELS
    ]
    rows = sorted((a for a in amendments if a["status"] == "duyet"), key=lambda a: hl.get(a["amend_doc_id"], ""))
    for a in rows:
        when = hl[a["amend_doc_id"]]
        target, action = a["target_doc_id"], a["action"]
        if action == "thay_the_van_ban":
            for r in out:
                if r["doc_id"] == target and r["valid_to"] is None:
                    r["valid_to"] = when
            continue
        addr = unit_address(target, a["target_dieu"], a["target_khoan"] or None, a["target_diem"] or None)
        if action in ("sua_doi", "bai_bo"):
            for r in out:
                if r["doc_id"] == target and r["valid_to"] is None and (
                        r["unit_id"] == addr or r["unit_id"].startswith(addr + ":")):
                    r["valid_to"] = when
        if action in ("sua_doi", "bo_sung") and a["new_text"].strip():
            frag = [x for x in a["new_text"].splitlines() if x.strip()]
            new = parse_units(target, frag, dieu=a["target_dieu"], khoan=a["target_khoan"] or None)
            if not new:
                level = "diem" if a["target_diem"] else "khoan" if a["target_khoan"] else "dieu"
                new = [Unit(addr, target, level, dieu=a["target_dieu"], khoan=a["target_khoan"] or None,
                            diem=a["target_diem"] or None, text="\n".join(frag))]
            for u in new:
                out.append(_version(dict(u.as_dict(), valid_from=when, valid_to=None,
                                         source_doc_id=a["amend_doc_id"])))
    return out
