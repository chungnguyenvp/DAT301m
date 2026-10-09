import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_notebook.py"


def _mod():
    spec = importlib.util.spec_from_file_location("build_notebook", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cells_from_source():
    src = "# %% [markdown]\n# # Tiêu đề\n# Đoạn văn\n\n# %%\nx = 1\n\n# %%\n\n"
    cells = _mod().cells_from_source(src)
    assert [c.cell_type for c in cells] == ["markdown", "code"]
    assert cells[0].source == "# Tiêu đề\nĐoạn văn"
    assert cells[1].source == "x = 1"


def test_empty_code_cells_and_markdown_are_preserved():
    cells = _mod().cells_from_source("# %%\n\n# %% [markdown]\n# A\n#\n# B\n")
    assert [c.cell_type for c in cells] == ["markdown"]
    assert cells[0].source == "A\n\nB"
