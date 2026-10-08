import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "process_legal.py"


@pytest.fixture
def cli():
    spec = importlib.util.spec_from_file_location("process_legal_cli", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_effective_proposal_goes_to_auto_file_not_reviewed(cli):
    assert cli.EFFECTIVE_AUTO.name == "effective_dates_auto.csv"
    assert cli.EFFECTIVE.name == "effective_dates.csv"
    assert cli.EFFECTIVE_AUTO != cli.EFFECTIVE


def test_apply_without_reviewed_dates_fails_with_clear_message(cli, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "EFFECTIVE", tmp_path / "effective_dates.csv")
    with pytest.raises(SystemExit) as exc:
        cli.step_apply()
    msg = str(exc.value)
    assert "effective_dates_auto.csv" in msg and "effective_dates.csv" in msg
