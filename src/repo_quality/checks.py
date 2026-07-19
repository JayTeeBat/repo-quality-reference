"""Repository conformance checks."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

from repo_quality.models import Finding, Report, RepositoryConfig, RepositoryPurpose

COMMON_PATHS = (Path("README.md"), Path("AGENTS.md"), Path(".gitignore"))
PYTHON_REQUIRED_COMMANDS = (
    "uv run ruff format --check .",
    "uv run ruff check .",
    "uv run ty check",
    "uv run pytest",
)


def check_repository(root: Path, config: RepositoryConfig) -> Report:
    """Check *root* against *config* without executing repository commands."""

    root = root.resolve()
    findings: list[Finding] = []

    required_paths = (*COMMON_PATHS, *_profile_paths(config), *config.required_paths)
    for relative_path in dict.fromkeys(required_paths):
        if not (root / relative_path).exists():
            findings.append(Finding("missing-path", "Required path does not exist", relative_path))

    findings.extend(_check_markdown_document(root / "README.md"))
    findings.extend(_check_markdown_document(root / "AGENTS.md"))
    findings.extend(
        _check_markdown_sections(
            root / "README.md",
            config.documentation.readme_sections,
        )
    )
    findings.extend(
        _check_markdown_sections(
            root / "AGENTS.md",
            config.documentation.agents_sections,
        )
    )
    findings.extend(_check_markdown_links(root))

    if config.purpose is not RepositoryPurpose.DOC_ONLY:
        findings.extend(_check_python_commands(config))
        findings.extend(_check_python_project(root, config))

    workflow_path = root / config.quality.ci_workflow
    if workflow_path.exists():
        findings.extend(_check_workflow_commands(workflow_path, config))

    return Report(root=root, purpose=config.purpose, findings=tuple(findings))


def _profile_paths(config: RepositoryConfig) -> tuple[Path, ...]:
    if config.purpose is RepositoryPurpose.DOC_ONLY:
        return (Path("docs"), config.quality.ci_workflow)
    if config.purpose is RepositoryPurpose.PYTHON_SINGLE:
        assert config.package_name is not None
        return (
            Path("pyproject.toml"),
            Path("uv.lock"),
            Path(".pre-commit-config.yaml"),
            config.quality.ci_workflow,
            Path("src") / config.package_name,
            Path("tests"),
        )
    return (
        Path("pyproject.toml"),
        Path("uv.lock"),
        Path(".pre-commit-config.yaml"),
        config.quality.ci_workflow,
        Path("packages"),
    )


def _check_markdown_document(path: Path) -> list[Finding]:
    if not path.is_file():
        return []
    if path.read_text(encoding="utf-8").strip():
        return []
    return [
        Finding(
            "empty-document",
            "Required Markdown document is empty",
            Path(path.name),
        )
    ]


def _check_markdown_sections(path: Path, required: tuple[str, ...]) -> list[Finding]:
    if not path.is_file() or not required:
        return []
    if not path.read_text(encoding="utf-8").strip():
        return []

    headings = _markdown_headings(path)
    relative_path = Path(path.name)
    return [
        Finding(
            "missing-section",
            f"Required section is missing: {section}",
            relative_path,
        )
        for section in required
        if section.casefold() not in headings
    ]


def _markdown_headings(path: Path) -> set[str]:
    tokens = MarkdownIt().parse(path.read_text(encoding="utf-8"))
    return {
        tokens[index + 1].content.strip().casefold()
        for index, token in enumerate(tokens[:-1])
        if token.type == "heading_open" and tokens[index + 1].type == "inline"
    }


def _check_markdown_links(root: Path) -> list[Finding]:
    parser = MarkdownIt()
    findings: list[Finding] = []
    ignored_roots = {".git", ".venv", "build", "dist"}

    for markdown_path in sorted(root.rglob("*.md")):
        relative_path = markdown_path.relative_to(root)
        if relative_path.parts and relative_path.parts[0] in ignored_roots:
            continue
        for target in _markdown_targets(parser, markdown_path):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            linked_path = (markdown_path.parent / unquote(parsed.path)).resolve()
            if not linked_path.exists() or not linked_path.is_relative_to(root):
                findings.append(
                    Finding(
                        "broken-internal-link",
                        f"Markdown link target does not exist: {target}",
                        relative_path,
                    )
                )
    return findings


def _markdown_targets(parser: MarkdownIt, path: Path) -> tuple[str, ...]:
    targets: list[str] = []
    for token in parser.parse(path.read_text(encoding="utf-8")):
        if token.type != "inline" or token.children is None:
            continue
        for child in token.children:
            if child.type == "link_open":
                target = child.attrGet("href")
            elif child.type == "image":
                target = child.attrGet("src")
            else:
                continue
            if isinstance(target, str) and target:
                targets.append(target)
    return tuple(targets)


def _check_python_commands(config: RepositoryConfig) -> list[Finding]:
    configured = set(config.quality.commands)
    return [
        Finding(
            "missing-python-gate",
            f"Required Python quality command is not declared: {command}",
            Path("repo-quality.toml"),
        )
        for command in PYTHON_REQUIRED_COMMANDS
        if command not in configured
    ]


def _check_python_project(root: Path, config: RepositoryConfig) -> list[Finding]:
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        return []

    try:
        with pyproject_path.open("rb") as handle:
            pyproject = tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        return [
            Finding(
                "invalid-pyproject", f"pyproject.toml is invalid: {error}", Path("pyproject.toml")
            )
        ]

    findings: list[Finding] = []
    if config.purpose is RepositoryPurpose.PYTHON_SINGLE:
        if not isinstance(pyproject.get("project"), Mapping):
            findings.append(
                Finding(
                    "missing-project-table",
                    "python-single requires a [project] table",
                    Path("pyproject.toml"),
                )
            )
        if not isinstance(pyproject.get("build-system"), Mapping):
            findings.append(
                Finding(
                    "missing-build-system",
                    "python-single requires a [build-system] table",
                    Path("pyproject.toml"),
                )
            )
    elif not _has_uv_workspace(pyproject):
        findings.append(
            Finding(
                "missing-workspace-table",
                "python-workspace requires [tool.uv.workspace]",
                Path("pyproject.toml"),
            )
        )
    return findings


def _has_uv_workspace(pyproject: Mapping[str, object]) -> bool:
    tool = pyproject.get("tool")
    if not isinstance(tool, Mapping):
        return False
    uv = tool.get("uv")
    return isinstance(uv, Mapping) and isinstance(uv.get("workspace"), Mapping)


def _check_workflow_commands(path: Path, config: RepositoryConfig) -> list[Finding]:
    relative_path = config.quality.ci_workflow
    try:
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return [Finding("invalid-workflow", f"CI workflow is invalid YAML: {error}", relative_path)]

    commands = set(_workflow_run_lines(workflow))
    return [
        Finding(
            "ci-gate-mismatch",
            f"Declared quality command is not run by CI: {command}",
            relative_path,
        )
        for command in config.quality.commands
        if command not in commands
    ]


def _workflow_run_lines(workflow: object) -> tuple[str, ...]:
    if not isinstance(workflow, Mapping):
        return ()
    jobs = workflow.get("jobs")
    if not isinstance(jobs, Mapping):
        return ()

    commands: list[str] = []
    for job in jobs.values():
        if not isinstance(job, Mapping):
            continue
        steps = job.get("steps")
        if not isinstance(steps, Sequence) or isinstance(steps, str):
            continue
        for step in steps:
            if not isinstance(step, Mapping):
                continue
            run = step.get("run")
            if isinstance(run, str):
                commands.extend(line.strip() for line in run.splitlines() if line.strip())
    return tuple(commands)
