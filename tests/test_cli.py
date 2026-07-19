import json
from pathlib import Path

import pytest

from repo_quality.cli import main


def test_reference_repository_passes_its_own_check(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).parents[1]

    exit_code = main(["check", str(root)])

    assert exit_code == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_returns_two_for_missing_config(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["check", str(tmp_path), "--json"])

    assert exit_code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert "not found" in payload["error"]
