# AGENTS.md

## Repository Purpose

This repository defines and demonstrates a portable repository quality standard.
It also provides the `repo-quality` CLI, which checks a repository against its
declared profile and gate contract.

## Source Of Truth

- `docs/standard.md` defines normative intent.
- `docs/repository-shapes.md` defines supported repository profiles.
- `docs/quality-gates.md` defines mandatory and conditional gates.
- `repo-quality.toml` declares the profile used by this repository.
- `src/repo_quality/` implements automated conformance checks.

When changing a rule, update the normative documentation, checker, tests, and
examples together. Do not let an example silently become the standard.

## Working Agreements

- Keep changes scoped to one quality concern.
- Prefer explicit, testable rules over general advice.
- Preserve compatibility with Python 3.12 and later.
- Keep runtime dependencies minimal and justified.
- Do not copy organization-specific policy into this portable reference.
- Do not weaken a mandatory gate without explicit maintainer approval and a
  recorded decision.

Humans own scope, exceptions, releases, security decisions, and breaking-change
approval. Agents may implement documented changes, tests, and related docs, but
must surface ambiguous policy rather than invent it.

## Quality Gates

Run from the repository root:

1. `uv sync --locked --all-groups`
2. `uv run pre-commit run --all-files`
3. `uv run ruff format --check .`
4. `uv run ruff check .`
5. `uv run ty check`
6. `uv run pytest`
7. `uv run repo-quality check .`
8. `uv build`

CI must run the same validation commands. Do not bypass a failed gate or edit
generated files to hide a mismatch.

## Coding Standards

- Put reusable behavior in `src/repo_quality/`.
- Keep the CLI limited to argument parsing, orchestration, and presentation.
- Use immutable dataclasses for configuration and findings.
- Type all production function signatures.
- Parse TOML and YAML with structured parsers.
- Report all conformance findings in one run when practical.
- Use stable finding codes so callers can consume results.

## Testing Policy

- Behavior changes require focused tests.
- Bug fixes require regression coverage.
- Profile changes require positive and negative conformance fixtures.
- The test suite must check that this repository passes its own standard.
- Tests must not require network access or modify the caller's repository.

## Documentation Rules

- Keep `README.md` evaluative and task-oriented; move durable detail to `docs/`.
- Put repository operating instructions in `AGENTS.md`, not the README.
- Use `MUST`, `SHOULD`, and `MAY` only as defined in `docs/standard.md`.
- Add an ADR under `docs/adr/` for durable architectural or policy decisions.
- Keep links relative when the target is inside this repository.

## Change Control

- Changes to mandatory rules are breaking standard changes.
- Changes to configuration schema require a schema-version decision and tests.
- Changes to CLI output must preserve exit-code behavior unless explicitly
  versioned.
- Update `CHANGELOG.md` for user-visible changes.
