"""Immutable domain models used by repository checks."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class RepositoryPurpose(StrEnum):
    """Supported repository shapes."""

    DOC_ONLY = "doc-only"
    PYTHON_SINGLE = "python-single"
    PYTHON_WORKSPACE = "python-workspace"


@dataclass(frozen=True, slots=True)
class QualityConfig:
    """Commands and CI location declared by a repository."""

    commands: tuple[str, ...]
    ci_workflow: Path


@dataclass(frozen=True, slots=True)
class DocumentationConfig:
    """Optional document sections explicitly required by a repository."""

    readme_sections: tuple[str, ...] = ()
    agents_sections: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RepositoryConfig:
    """Parsed ``repo-quality.toml`` contract."""

    schema_version: int
    purpose: RepositoryPurpose
    package_name: str | None
    required_paths: tuple[Path, ...]
    quality: QualityConfig
    documentation: DocumentationConfig = DocumentationConfig()


@dataclass(frozen=True, slots=True)
class Finding:
    """One actionable conformance failure."""

    code: str
    message: str
    path: Path | None = None

    def as_dict(self) -> dict[str, str]:
        """Return a stable JSON-serializable representation."""

        result = {"code": self.code, "message": self.message}
        if self.path is not None:
            result["path"] = self.path.as_posix()
        return result


@dataclass(frozen=True, slots=True)
class Report:
    """Complete result of checking one repository."""

    root: Path
    purpose: RepositoryPurpose
    findings: tuple[Finding, ...]

    @property
    def ok(self) -> bool:
        """Whether the repository satisfies every automated check."""

        return not self.findings

    def as_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""

        return {
            "root": str(self.root),
            "purpose": self.purpose.value,
            "ok": self.ok,
            "findings": [finding.as_dict() for finding in self.findings],
        }
