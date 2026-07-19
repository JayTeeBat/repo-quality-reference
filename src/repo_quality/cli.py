"""Command-line interface for repository quality checks."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from repo_quality.checks import check_repository
from repo_quality.config import ConfigError, load_config
from repo_quality.models import Report


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        prog="repo-quality",
        description="Check a repository against its declared quality profile.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="check repository conformance")
    check_parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    check_parser.add_argument(
        "--config",
        default="repo-quality.toml",
        help="configuration path relative to the repository root",
    )
    check_parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    args = build_parser().parse_args(argv)
    root = args.root.resolve()

    try:
        config = load_config(root / args.config)
    except ConfigError as error:
        if args.json_output:
            print(json.dumps({"ok": False, "error": str(error)}, indent=2, sort_keys=True))
        else:
            print(f"ERROR {error}")
        return 2

    report = check_repository(root, config)
    if args.json_output:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    return 0 if report.ok else 1


def _print_text_report(report: Report) -> None:
    if report.ok:
        print(f"PASS {report.root} ({report.purpose.value})")
        return

    print(f"FAIL {report.root} ({report.purpose.value})")
    for finding in report.findings:
        location = f" {finding.path}:" if finding.path is not None else ""
        print(f"[{finding.code}]{location} {finding.message}")
