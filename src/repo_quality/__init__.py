"""Executable checks for the repository quality reference."""

from repo_quality.checks import check_repository
from repo_quality.config import ConfigError, load_config
from repo_quality.models import (
    DocumentationConfig,
    Finding,
    Report,
    RepositoryConfig,
    RepositoryPurpose,
)

__all__ = [
    "ConfigError",
    "DocumentationConfig",
    "Finding",
    "Report",
    "RepositoryConfig",
    "RepositoryPurpose",
    "check_repository",
    "load_config",
]

__version__ = "0.1.0"
