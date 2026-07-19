from pathlib import Path

import pytest

from repo_quality.config import ConfigError, load_config
from repo_quality.models import RepositoryPurpose


def write_config(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_python_single_config(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "repo-quality.toml",
        """
schema_version = 1
[repository]
purpose = "python-single"
package = "widget"
required_paths = ["SECURITY.md"]
[quality]
commands = ["uv run pytest"]
""".strip(),
    )

    config = load_config(path)

    assert config.purpose is RepositoryPurpose.PYTHON_SINGLE
    assert config.package_name == "widget"
    assert config.required_paths == (Path("SECURITY.md"),)
    assert config.quality.ci_workflow == Path(".github/workflows/quality.yml")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("schema_version = 2", "schema_version must be 1"),
        (
            'schema_version = 1\n[repository]\npurpose = "unknown"\n[quality]\ncommands = ["x"]',
            "repository.purpose must be one of",
        ),
        (
            "schema_version = 1\n"
            "[repository]\n"
            'purpose = "python-single"\n'
            "[quality]\n"
            'commands = ["x"]',
            "repository.package is required",
        ),
        (
            "schema_version = 1\n"
            "[repository]\n"
            'purpose = "doc-only"\n'
            'required_paths = ["../x"]\n'
            "[quality]\n"
            'commands = ["x"]',
            "repository.required_paths must contain repository-relative paths",
        ),
    ],
)
def test_rejects_invalid_config(tmp_path: Path, content: str, message: str) -> None:
    path = write_config(tmp_path / "repo-quality.toml", content)

    with pytest.raises(ConfigError, match=message):
        load_config(path)
