from pathlib import Path

from repo_quality.checks import check_repository
from repo_quality.models import (
    DocumentationConfig,
    QualityConfig,
    RepositoryConfig,
    RepositoryPurpose,
)

PYTHON_COMMANDS = (
    "uv run ruff format --check .",
    "uv run ruff check .",
    "uv run ty check",
    "uv run pytest",
)


def config(
    purpose: RepositoryPurpose,
    *,
    package_name: str | None = None,
    commands: tuple[str, ...] = PYTHON_COMMANDS,
    readme_sections: tuple[str, ...] = (),
    agents_sections: tuple[str, ...] = (),
) -> RepositoryConfig:
    return RepositoryConfig(
        schema_version=1,
        purpose=purpose,
        package_name=package_name,
        required_paths=(),
        documentation=DocumentationConfig(
            readme_sections=readme_sections,
            agents_sections=agents_sections,
        ),
        quality=QualityConfig(
            commands=commands,
            ci_workflow=Path(".github/workflows/quality.yml"),
        ),
    )


def write_common_docs(root: Path) -> None:
    (root / "README.md").write_text(
        "# Widget\n\n## Overview\n\nA useful widget.\n\n## Installation\n\nInstall it.\n",
        encoding="utf-8",
    )
    (root / "AGENTS.md").write_text(
        "# Agent Guidance\n\nUse the documented gates.\n",
        encoding="utf-8",
    )
    (root / ".gitignore").touch()


def write_workflow(root: Path, commands: tuple[str, ...]) -> None:
    workflow = root / ".github/workflows/quality.yml"
    workflow.parent.mkdir(parents=True)
    run_steps = "\n".join(
        f"      - name: Gate {index}\n        run: {command}"
        for index, command in enumerate(commands)
    )
    workflow.write_text(
        f"name: Quality\njobs:\n  quality:\n    steps:\n{run_steps}\n",
        encoding="utf-8",
    )


def test_doc_only_repository_passes(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    (tmp_path / "docs").mkdir()
    write_workflow(tmp_path, ("check-docs",))

    report = check_repository(
        tmp_path,
        config(RepositoryPurpose.DOC_ONLY, commands=("check-docs",)),
    )

    assert report.ok


def test_python_single_reports_missing_gates_and_structure(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    write_workflow(tmp_path, ("uv run pytest",))
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'widget'\n", encoding="utf-8")

    report = check_repository(
        tmp_path,
        config(
            RepositoryPurpose.PYTHON_SINGLE,
            package_name="widget",
            commands=("uv run pytest",),
        ),
    )

    codes = {finding.code for finding in report.findings}
    assert "missing-path" in codes
    assert "missing-python-gate" in codes
    assert "missing-build-system" in codes


def test_workflow_must_run_every_declared_command(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    (tmp_path / "docs").mkdir()
    write_workflow(tmp_path, ("check-format",))

    report = check_repository(
        tmp_path,
        config(
            RepositoryPurpose.DOC_ONLY,
            commands=("check-format", "check-links"),
        ),
    )

    assert [finding.code for finding in report.findings] == ["ci-gate-mismatch"]
    assert "check-links" in report.findings[0].message


def test_python_workspace_repository_passes(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    write_workflow(tmp_path, PYTHON_COMMANDS)
    (tmp_path / "packages").mkdir()
    (tmp_path / "uv.lock").touch()
    (tmp_path / ".pre-commit-config.yaml").touch()
    (tmp_path / "pyproject.toml").write_text(
        '[tool.uv.workspace]\nmembers = ["packages/*"]\n',
        encoding="utf-8",
    )

    report = check_repository(tmp_path, config(RepositoryPurpose.PYTHON_WORKSPACE))

    assert report.ok


def test_broken_internal_markdown_link_is_reported(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    with (tmp_path / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n[Missing](docs/missing.md)\n")
    (tmp_path / "docs").mkdir()
    write_workflow(tmp_path, ("check-docs",))

    report = check_repository(
        tmp_path,
        config(RepositoryPurpose.DOC_ONLY, commands=("check-docs",)),
    )

    broken_links = [
        finding for finding in report.findings if finding.code == "broken-internal-link"
    ]
    assert len(broken_links) == 1
    assert broken_links[0].path == Path("README.md")


def test_only_explicitly_declared_sections_are_required(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    (tmp_path / "docs").mkdir()
    write_workflow(tmp_path, ("check-docs",))

    report = check_repository(
        tmp_path,
        config(
            RepositoryPurpose.DOC_ONLY,
            commands=("check-docs",),
            readme_sections=("Installation", "Usage"),
            agents_sections=("Testing Policy",),
        ),
    )

    missing_sections = [finding for finding in report.findings if finding.code == "missing-section"]
    assert [(finding.path, finding.message) for finding in missing_sections] == [
        (Path("README.md"), "Required section is missing: Usage"),
        (Path("AGENTS.md"), "Required section is missing: Testing Policy"),
    ]


def test_empty_required_documents_are_reported(tmp_path: Path) -> None:
    write_common_docs(tmp_path)
    (tmp_path / "README.md").write_text(" \n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    write_workflow(tmp_path, ("check-docs",))

    report = check_repository(
        tmp_path,
        config(RepositoryPurpose.DOC_ONLY, commands=("check-docs",)),
    )

    empty_documents = [finding for finding in report.findings if finding.code == "empty-document"]
    assert [finding.path for finding in empty_documents] == [
        Path("README.md"),
        Path("AGENTS.md"),
    ]
