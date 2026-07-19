"""Portable documentation quality commands."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

from markdown.extensions.toc import slugify
from markdown_it import MarkdownIt

IGNORED_DIRECTORIES = frozenset(
    {".git", ".pytest_cache", ".ruff_cache", ".ty_cache", ".venv", "build", "dist", "site"}
)
USER_AGENT = "repo-quality-reference/0.1 (+https://github.com/JayTeeBat/repo-quality-reference)"


@dataclass(frozen=True)
class DocumentationLink:
    """A link found in a Markdown document."""

    source: Path
    target: str


@dataclass(frozen=True)
class LinkIssue:
    """An invalid or unreachable documentation link."""

    source: Path
    target: str
    message: str


def format_main(argv: Sequence[str] | None = None) -> int:
    """Check Markdown formatting with mdformat."""

    parser = _root_parser("Check Markdown formatting without modifying files.")
    args = parser.parse_args(argv)
    root = _resolve_root(parser, args.root)
    paths = [str(path.relative_to(root)) for path in markdown_paths(root)]
    if not paths:
        print(f"PASS {root} (no Markdown files)")
        return 0
    return _run_module(root, "mdformat", "--check", "--number", *paths)


def links_main(argv: Sequence[str] | None = None) -> int:
    """Check local and external links in Markdown documents."""

    parser = _root_parser("Check links in Markdown documents.")
    parser.add_argument(
        "--exclude-url-prefix",
        action="append",
        default=[],
        metavar="PREFIX",
        help="skip external URLs beginning with PREFIX; may be repeated",
    )
    parser.add_argument(
        "--external-timeout",
        type=float,
        default=10.0,
        metavar="SECONDS",
        help="timeout for each external request (default: 10)",
    )
    parser.add_argument(
        "--external-retries",
        type=int,
        default=2,
        metavar="COUNT",
        help="retries after a transient external failure (default: 2)",
    )
    parser.add_argument(
        "--no-external",
        action="store_true",
        help="check local links only",
    )
    args = parser.parse_args(argv)
    if args.external_timeout <= 0:
        parser.error("--external-timeout must be greater than zero")
    if args.external_retries < 0:
        parser.error("--external-retries must not be negative")

    root = _resolve_root(parser, args.root)
    issues = check_links(
        root,
        check_external=not args.no_external,
        excluded_url_prefixes=tuple(args.exclude_url_prefix),
        timeout=args.external_timeout,
        retries=args.external_retries,
    )
    if not issues:
        print(f"PASS {root} (documentation links)")
        return 0

    for issue in issues:
        print(f"ERROR {issue.source}: {issue.message}: {issue.target}")
    return 1


def build_main(argv: Sequence[str] | None = None) -> int:
    """Build the documentation site with strict MkDocs warnings."""

    parser = _root_parser("Build the documentation site with MkDocs.")
    parser.add_argument(
        "--config-file",
        type=Path,
        default=Path("mkdocs.yml"),
        help="configuration path relative to the repository root",
    )
    args = parser.parse_args(argv)
    root = _resolve_root(parser, args.root)
    return _run_module(
        root,
        "mkdocs",
        "build",
        "--strict",
        "--config-file",
        str(args.config_file),
    )


def markdown_paths(root: Path) -> tuple[Path, ...]:
    """Return Markdown files below *root*, excluding generated directories."""

    return tuple(
        path
        for path in sorted(root.rglob("*.md"))
        if not any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts)
    )


def check_links(
    root: Path,
    *,
    check_external: bool = True,
    excluded_url_prefixes: tuple[str, ...] = (),
    timeout: float = 10.0,
    retries: int = 2,
    open_url: Callable[..., object] = urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[LinkIssue, ...]:
    """Return documentation link issues below *root*."""

    root = root.resolve()
    links = _markdown_links(root)
    issues = list(_check_local_links(root, links))
    if check_external:
        issues.extend(
            _check_external_links(
                links,
                excluded_url_prefixes=excluded_url_prefixes,
                timeout=timeout,
                retries=retries,
                open_url=open_url,
                sleep=sleep,
            )
        )
    return tuple(issues)


def _root_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    return parser


def _resolve_root(parser: argparse.ArgumentParser, path: Path) -> Path:
    root = path.resolve()
    if not root.is_dir():
        parser.error(f"repository root is not a directory: {path}")
    return root


def _run_module(root: Path, module: str, *arguments: str) -> int:
    result = subprocess.run(
        [sys.executable, "-m", module, *arguments],
        cwd=root,
        check=False,
    )
    return result.returncode


def _markdown_links(root: Path) -> tuple[DocumentationLink, ...]:
    parser = MarkdownIt()
    links: list[DocumentationLink] = []
    for path in markdown_paths(root):
        source = path.relative_to(root)
        for token in parser.parse(path.read_text(encoding="utf-8")):
            if token.type != "inline" or token.children is None:
                continue
            for child in token.children:
                attribute = "href" if child.type == "link_open" else "src"
                if child.type not in {"link_open", "image"}:
                    continue
                target = child.attrGet(attribute)
                if isinstance(target, str) and target:
                    links.append(DocumentationLink(source, target))
    return tuple(links)


def _check_local_links(root: Path, links: tuple[DocumentationLink, ...]) -> tuple[LinkIssue, ...]:
    issues: list[LinkIssue] = []
    heading_cache: dict[Path, frozenset[str]] = {}
    for link in links:
        parsed = urlsplit(link.target)
        if parsed.scheme or parsed.netloc:
            continue

        source_path = root / link.source
        target_path = source_path if not parsed.path else source_path.parent / unquote(parsed.path)
        target_path = target_path.resolve()
        if not target_path.is_relative_to(root) or not target_path.exists():
            issues.append(LinkIssue(link.source, link.target, "local target does not exist"))
            continue

        markdown_target = _markdown_target(target_path)
        if parsed.fragment and markdown_target is not None:
            headings = heading_cache.setdefault(markdown_target, _heading_ids(markdown_target))
            fragment = unquote(parsed.fragment).casefold()
            if fragment not in headings:
                issues.append(
                    LinkIssue(link.source, link.target, "heading fragment does not exist")
                )
    return tuple(issues)


def _markdown_target(path: Path) -> Path | None:
    if path.is_file() and path.suffix.casefold() == ".md":
        return path
    if path.is_dir() and (path / "index.md").is_file():
        return path / "index.md"
    return None


def _heading_ids(path: Path) -> frozenset[str]:
    tokens = MarkdownIt().parse(path.read_text(encoding="utf-8"))
    identifiers: set[str] = set()
    counts: dict[str, int] = {}
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open" or tokens[index + 1].type != "inline":
            continue
        base = slugify(tokens[index + 1].content.strip(), "-")
        count = counts.get(base, 0)
        counts[base] = count + 1
        identifiers.add(base if count == 0 else f"{base}_{count}")
    return frozenset(identifier.casefold() for identifier in identifiers)


def _check_external_links(
    links: tuple[DocumentationLink, ...],
    *,
    excluded_url_prefixes: tuple[str, ...],
    timeout: float,
    retries: int,
    open_url: Callable[..., object],
    sleep: Callable[[float], None],
) -> tuple[LinkIssue, ...]:
    sources_by_url: dict[str, set[Path]] = {}
    for link in links:
        parsed = urlsplit(link.target)
        if parsed.scheme not in {"http", "https"}:
            continue
        if any(link.target.startswith(prefix) for prefix in excluded_url_prefixes):
            continue
        sources_by_url.setdefault(link.target, set()).add(link.source)

    issues: list[LinkIssue] = []
    for target, sources in sources_by_url.items():
        error = _external_link_error(
            target,
            timeout=timeout,
            retries=retries,
            open_url=open_url,
            sleep=sleep,
        )
        if error is not None:
            issues.extend(LinkIssue(source, target, error) for source in sorted(sources))
    return tuple(issues)


def _external_link_error(
    target: str,
    *,
    timeout: float,
    retries: int,
    open_url: Callable[..., object],
    sleep: Callable[[float], None],
) -> str | None:
    for attempt in range(retries + 1):
        try:
            status = _external_status(target, timeout=timeout, open_url=open_url)
            if status < 400:
                return None
            return f"external target returned HTTP {status}"
        except HTTPError as error:
            if error.code in {401, 403}:
                return None
            if error.code not in {408, 425, 429, 500, 502, 503, 504}:
                return f"external target returned HTTP {error.code}"
            message = f"external target returned HTTP {error.code}"
        except (TimeoutError, URLError) as error:
            reason = error.reason if isinstance(error, URLError) else error
            message = f"external target could not be reached ({reason})"

        if attempt < retries:
            sleep(0.5 * (2**attempt))
    return message


def _external_status(
    target: str,
    *,
    timeout: float,
    open_url: Callable[..., object],
) -> int:
    headers = {"User-Agent": USER_AGENT}
    try:
        response = open_url(Request(target, method="HEAD", headers=headers), timeout=timeout)
    except HTTPError as error:
        if error.code not in {405, 501}:
            raise
        error.close()
        response = open_url(Request(target, method="GET", headers=headers), timeout=timeout)

    status = getattr(response, "status", 200)
    close = getattr(response, "close", None)
    if callable(close):
        close()
    return status
