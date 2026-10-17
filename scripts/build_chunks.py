"""Cắt kho luật thành đoạn cho RAG và ghi `data/rag/`.

    py -3.13 scripts/build_chunks.py           # ghi chunks_khoan.jsonl, chunks_dieu.jsonl, MANIFEST.json
    py -3.13 scripts/build_chunks.py --check   # build lại trong bộ nhớ, so với file đang có

Cách cắt và quy tắc hiệu lực: xem `src/rag/chunking.py` và `docs/superpowers/plans/2026-10-17-g3-rag.md`.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawproc import config, evalset  # noqa: E402
from rag import chunking, score  # noqa: E402

OUT = config.DATA / "rag"
CUTS = ("khoan", "dieu")
SOURCE = config.PROCESSED / "legal_units_versioned.jsonl"
AMENDMENTS = config.PROCESSED / "amendments_reviewed.csv"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(chunks: list[dict]) -> bytes:
    return "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks).encode("utf-8")


def stats(chunks: list[dict]) -> dict:
    live = [c for c in chunks if chunking.in_force(c, config.CUTOFF)]
    return {"so_doan": len(chunks), "co_hieu_luc_tai_cutoff": len(live),
            "mot_phan": sum(c["mot_phan"] for c in chunks), "vuot_gioi_han": sum(c["vuot_gioi_han"] for c in chunks),
            "co_ghi_chu_hieu_luc": sum(bool(c["ghi_chu_hieu_luc"]) for c in chunks),
            "so_token_toi_da_khi_co_hieu_luc": max(c["so_token"] for c in live),
            "theo_van_ban": dict(sorted(Counter(c["doc_id"] for c in live).items()))}


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(config.ROOT).as_posix()
    except ValueError:
        return "~/" + path.resolve().relative_to(Path.home()).as_posix()


def make_manifest(built: dict[str, bytes], tokenizer: Path) -> dict:
    blob = subprocess.run(["git", "rev-parse", "data-v1:data/processed/legal_units_versioned.jsonl"],
                          cwd=config.ROOT, capture_output=True, text=True).stdout.strip()
    return {
        "nguon": {
            "path": rel(SOURCE), "sha256": sha256(SOURCE.read_bytes()), "git_blob_in_tag_data_v1": blob,
            "amendments_reviewed": {"path": rel(AMENDMENTS), "sha256": sha256(AMENDMENTS.read_bytes())},
            "ten_van_ban": {"path": rel(config.MANIFEST), "sha256": sha256(config.MANIFEST.read_bytes())},
        },
        "tokenizer": {"ten": "BAAI/bge-m3", "path": rel(tokenizer), "sha256": sha256(tokenizer.read_bytes())},
        "bang_chung": {"path": rel(score.EVIDENCE), "sha256": sha256(score.EVIDENCE.read_bytes())},
        "max_tokens": chunking.MAX_TOKENS,
        "cutoff": config.CUTOFF,
        "so_chi_dan_sua_doi_bi_loai": len(chunking.instruction_units()),
        "files": {f"data/rag/chunks_{cut}.jsonl": {"sha256": sha256(built[cut]),
                                                    **stats([json.loads(line) for line in built[cut].splitlines()])}
                  for cut in CUTS},
    }


def dump_manifest(manifest: dict) -> bytes:
    return (json.dumps(manifest, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    records = evalset.load_versions()
    count = chunking.load_tokenizer()
    built = {cut: dump(chunking.build_chunks(records, cut, count)) for cut in CUTS}
    paths = {cut: OUT / f"chunks_{cut}.jsonl" for cut in CUTS}
    manifest_bytes = dump_manifest(make_manifest(built, count.path))
    if a.check:
        bad = [cut for cut in CUTS if not paths[cut].exists() or paths[cut].read_bytes() != built[cut]]
        manifest_path = OUT / "MANIFEST.json"
        if not manifest_path.exists() or manifest_path.read_bytes() != manifest_bytes:
            bad.append("MANIFEST.json")
        print("khớp" if not bad else f"khác: {bad}")
        sys.exit(1 if bad else 0)
    OUT.mkdir(parents=True, exist_ok=True)
    for cut in CUTS:
        paths[cut].write_bytes(built[cut])
    (OUT / "MANIFEST.json").write_bytes(manifest_bytes)
    manifest = json.loads(manifest_bytes)
    for cut in CUTS:
        s = manifest["files"][f"data/rag/chunks_{cut}.jsonl"]
        print(f"{cut}: {s['so_doan']} đoạn, {s['co_hieu_luc_tai_cutoff']} có hiệu lực tại {config.CUTOFF}, "
              f"{s['mot_phan']} mẩu, {s['vuot_gioi_han']} vượt giới hạn, {len(built[cut]) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
