from __future__ import annotations

from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

import repo_quality.docs
from repo_quality.docs import build_main, check_links, format_main, links_main


class Response:
    status = 200

    def close(self) -> None:
        pass


def write_markdown(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_links_accepts_existing_targets_and_fragments(tmp_path: Path) -> None:
    write_markdown(
        tmp_path,
        "README.md",
        "# Project\n\n[Guide](docs/guide.md#first-steps)\n",
    )
    write_markdown(tmp_path, "docs/guide.md", "# Guide\n\n## First Steps\n")

    issues = check_links(tmp_path, check_external=False)

    assert issues == ()


def test_check_links_reports_missing_targets_and_fragments(tmp_path: Path) -> None:
    write_markdown(
        tmp_path,
        "README.md",
        "# Project\n\n[Missing](docs/missing.md)\n[Section](#missing-section)\n",
    )

    issues = check_links(tmp_path, check_external=False)

    assert [(issue.target, issue.message) for issue in issues] == [
        ("docs/missing.md", "local target does not exist"),
        ("#missing-section", "heading fragment does not exist"),
    ]


def test_check_links_retries_transient_external_failures(tmp_path: Path) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n\n[Service](https://example.com)\n")
    attempts = 0
    delays: list[float] = []

    def open_url(*_args: object, **_kwargs: object) -> Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise URLError("temporary failure")
        return Response()

    issues = check_links(
        tmp_path,
        retries=2,
        open_url=open_url,
        sleep=delays.append,
    )

    assert issues == ()
    assert attempts == 2
    assert delays == [0.5]


def test_check_links_reports_permanent_external_failure(tmp_path: Path) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n\n[Missing](https://example.com/404)\n")

    def open_url(*_args: object, **_kwargs: object) -> Response:
        raise HTTPError("https://example.com/404", 404, "Not Found", Message(), None)

    issues = check_links(tmp_path, open_url=open_url)

    assert [(issue.target, issue.message) for issue in issues] == [
        ("https://example.com/404", "external target returned HTTP 404")
    ]


def test_check_links_falls_back_to_get_when_head_is_unsupported(tmp_path: Path) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n\n[Service](https://example.com)\n")
    methods: list[str] = []

    def open_url(request: Request, **_kwargs: object) -> Response:
        methods.append(request.get_method())
        if request.get_method() == "HEAD":
            raise HTTPError(request.full_url, 405, "Method Not Allowed", Message(), None)
        return Response()

    issues = check_links(tmp_path, open_url=open_url)

    assert issues == ()
    assert methods == ["HEAD", "GET"]


def test_check_links_honors_external_url_exclusions(tmp_path: Path) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n\n[Status](https://status.example.com/x)\n")

    def fail_if_called(*_args: object, **_kwargs: object) -> Response:
        raise AssertionError("excluded URL was requested")

    issues = check_links(
        tmp_path,
        excluded_url_prefixes=("https://status.example.com/",),
        open_url=fail_if_called,
    )

    assert issues == ()


def test_links_command_reports_issues(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n\n[Missing](missing.md)\n")

    exit_code = links_main([str(tmp_path), "--no-external"])

    assert exit_code == 1
    assert "local target does not exist" in capsys.readouterr().out


def test_format_command_checks_all_markdown_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_markdown(tmp_path, "README.md", "# Project\n")
    calls: list[tuple[Path, str, tuple[str, ...]]] = []

    def run_module(root: Path, module: str, *arguments: str) -> int:
        calls.append((root, module, arguments))
        return 0

    monkeypatch.setattr(repo_quality.docs, "_run_module", run_module)

    exit_code = format_main([str(tmp_path)])

    assert exit_code == 0
    assert calls == [(tmp_path, "mdformat", ("--check", "--number", "README.md"))]


def test_build_command_uses_strict_mkdocs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Path, str, tuple[str, ...]]] = []

    def run_module(root: Path, module: str, *arguments: str) -> int:
        calls.append((root, module, arguments))
        return 0

    monkeypatch.setattr(repo_quality.docs, "_run_module", run_module)

    exit_code = build_main([str(tmp_path)])

    assert exit_code == 0
    assert calls == [(tmp_path, "mkdocs", ("build", "--strict", "--config-file", "mkdocs.yml"))]
