import importlib.util
from dataclasses import asdict

import pytest

from lawproc import config
from rag import retrieve, score

spec = importlib.util.spec_from_file_location("run_retrieval", config.ROOT / "scripts" / "run_retrieval.py")
run_retrieval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_retrieval)


def _item(id_, nhom, ho):
    return {"id": id_, "key": id_.lower(), "tap": "test", "nhom_cau": nhom, "van_ban": "nd_x", "can_cu": ["u@v"],
            "nhom_can_cu": [["u@v"]], "ho_su_kien": ho, "ho_cau": id_, "goc_id": "TH001" if nhom == "bien_the" else None,
            "can_cu_cu": ["u@old"] if nhom == "sua_doi" else None}


def test_ablation_configs_differ_only_where_intended():
    cfgs = run_retrieval.ablation(retrieve.Config(rerank_k=20, rrf_k=60))
    assert list(cfgs) == ["bm25", "vector", "hybrid", "hybrid+rerank", "hybrid+rerank_bo_loc"]
    assert (cfgs["bm25"].dung_vector, cfgs["bm25"].rerank_k) == (False, 0)
    assert (cfgs["vector"].dung_bm25, cfgs["vector"].rerank_k) == (False, 0)
    assert cfgs["hybrid"].rerank_k == 0 and cfgs["hybrid+rerank"] == retrieve.Config()
    assert asdict(cfgs["hybrid+rerank_bo_loc"]) == dict(asdict(retrieve.Config()), loc_hieu_luc=False)


def test_summary_table_is_written_for_every_config_and_cut(tmp_path, monkeypatch):
    items = [_item("TH001", "thuong", "a"), _item("TH002", "thuong", "a"), _item("SD001", "sua_doi", "b"),
             _item("BT001", "bien_the", "a")]
    hit = {"chunk_id": "c", "doc_id": "nd_x", "units": ["u@v"], "text": ""}
    rows = [score.score_item(x, [hit] if x["id"] != "TH002" else []) for x in items]
    entry = {"tong_hop": score.summarize(rows, items, n_boot=50), "variant_gap": score.variant_gap(rows, items),
             "sua_doi_lay_ban_cu": 0}
    report = {"so_cau": 4, "cau_hinh_chinh": asdict(retrieve.Config()),
              "ket_qua": {f"{name}/{cut}": entry for name in run_retrieval.LABELS for cut in run_retrieval.CUTS}}
    monkeypatch.setattr(run_retrieval, "REPORTS", tmp_path)
    text = run_retrieval.write_summary(report).read_text(encoding="utf-8")
    assert text.count("| Hybrid + reranker | Khoản |") == 3 and text.count("| Chỉ BM25 | Điều |") == 3
    assert "## Câu thường (n = 2, 1 họ sự kiện)" in text
    assert "| Khoản | 0/1 | 0/1 |" in text
    assert "0.50 [" in text


def test_test_run_refuses_to_run_twice(tmp_path, monkeypatch):
    monkeypatch.setattr(run_retrieval, "REPORTS", tmp_path)
    monkeypatch.setattr(run_retrieval, "PARAMS", tmp_path / "params.json")
    (tmp_path / "test_results.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="một lần"):
        run_retrieval.test_run(force=False)
