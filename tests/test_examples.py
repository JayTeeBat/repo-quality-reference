from pathlib import Path

import pytest

from repo_quality.config import load_config
from repo_quality.models import RepositoryPurpose


@pytest.mark.parametrize(
    ("example", "purpose"),
    [
        ("doc-only", RepositoryPurpose.DOC_ONLY),
        ("python-single", RepositoryPurpose.PYTHON_SINGLE),
        ("python-workspace", RepositoryPurpose.PYTHON_WORKSPACE),
    ],
)
def test_example_config_is_valid(example: str, purpose: RepositoryPurpose) -> None:
    root = Path(__file__).parents[1]

    config = load_config(root / "examples" / example / "repo-quality.toml")

    assert config.purpose is purpose
