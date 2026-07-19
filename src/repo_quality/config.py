"""Structured loading and validation for ``repo-quality.toml``."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

from repo_quality.models import QualityConfig, RepositoryConfig, RepositoryPurpose

SCHEMA_VERSION = 1


class ConfigError(ValueError):
    """Raised when a repository quality contract is invalid."""


def load_config(path: Path) -> RepositoryConfig:
    """Load and validate a repository quality contract from *path*."""

    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except FileNotFoundError as error:
        raise ConfigError(f"Configuration file not found: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"Invalid TOML in {path}: {error}") from error

    schema_version = raw.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != SCHEMA_VERSION:
        raise ConfigError(f"schema_version must be {SCHEMA_VERSION}")

    repository = _table(raw.get("repository"), "repository")
    quality = _table(raw.get("quality"), "quality")

    purpose_value = _string(repository, "purpose")
    try:
        purpose = RepositoryPurpose(purpose_value)
    except ValueError as error:
        supported = ", ".join(item.value for item in RepositoryPurpose)
        raise ConfigError(f"repository.purpose must be one of: {supported}") from error

    package_name = _optional_string(repository, "package")
    if purpose is RepositoryPurpose.PYTHON_SINGLE and package_name is None:
        raise ConfigError("repository.package is required for python-single")
    if package_name is not None and not package_name.isidentifier():
        raise ConfigError("repository.package must be a valid Python identifier")

    required_paths = tuple(
        _relative_path(value, "repository.required_paths")
        for value in _string_sequence(repository.get("required_paths", []), "required_paths")
    )
    commands = tuple(_string_sequence(quality.get("commands"), "quality.commands"))
    if not commands:
        raise ConfigError("quality.commands must contain at least one command")

    ci_workflow = _relative_path(
        _optional_string(quality, "ci_workflow") or ".github/workflows/quality.yml",
        "quality.ci_workflow",
    )

    return RepositoryConfig(
        schema_version=SCHEMA_VERSION,
        purpose=purpose,
        package_name=package_name,
        required_paths=required_paths,
        quality=QualityConfig(commands=commands, ci_workflow=ci_workflow),
    )


def _table(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ConfigError(f"{name} must be a TOML table")
    if not all(isinstance(key, str) for key in value):
        raise ConfigError(f"{name} contains a non-string key")
    return {str(key): item for key, item in value.items()}


def _string(table: Mapping[str, object], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string")
    return value.strip()


def _optional_string(table: Mapping[str, object], key: str) -> str | None:
    value = table.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string when provided")
    return value.strip()


def _string_sequence(value: object, name: str) -> Sequence[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{name} must be an array of strings")
    return tuple(str(item) for item in value)


def _relative_path(value: str, name: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ConfigError(f"{name} must contain repository-relative paths")
    return Path(*path.parts)
