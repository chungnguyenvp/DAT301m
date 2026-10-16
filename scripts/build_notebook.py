"""Build a notebook from ``# %%`` cells in a Python source file."""

import sys
from pathlib import Path

import nbformat


def cells_from_source(src: str) -> list:
    blocks: list[tuple[str, list[str]]] = []
    for line in src.splitlines():
        if line.startswith("# %%"):
            blocks.append(("md" if "[markdown]" in line else "code", []))
        elif blocks:
            blocks[-1][1].append(line)
    cells = []
    for kind, lines in blocks:
        body = "\n".join(lines).strip("\n")
        if kind == "md":
            text = "\n".join(x[2:] if x.startswith("# ") else x.lstrip("#") for x in body.splitlines())
            cells.append(nbformat.v4.new_markdown_cell(text))
        elif body.strip():
            cells.append(nbformat.v4.new_code_cell(body))
    return cells


if __name__ == "__main__":
    src = Path(sys.argv[1])
    nb = nbformat.v4.new_notebook(
        cells=cells_from_source(src.read_text(encoding="utf-8")),
        metadata={"kernelspec": {"name": "python313-traffic-law",
                                 "display_name": "Python 3.13 (traffic-law)", "language": "python"}},
    )
    nbformat.write(nb, src.with_suffix(".ipynb"))
    print(f"-> {src.with_suffix('.ipynb')}")
