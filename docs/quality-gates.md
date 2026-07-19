# Quality Gates

## Gate Design

A gate should be deterministic, actionable, and tied to a credible failure
mode. Keep fast checks local; run the complete locked chain in CI. Commands
documented here are defaults and may be extended when risk justifies it.

## Universal Baseline

All repositories MUST check:

- invalid YAML, TOML, and JSON
- trailing whitespace and missing final newlines
- merge-conflict markers and case-conflicting paths
- accidentally committed private keys or secrets
- unexpectedly large files
- documentation changes when behavior or contracts change

Generated artifacts MUST either stay out of version control or be regenerated
and diff-checked in CI.

## Python Baseline

Python repositories MUST use `uv`, commit `uv.lock`, and run:

```bash
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
```

Package repositories MUST also run `uv build`. The minimum commands appear in
`repo-quality.toml`, and the self-check verifies that CI runs the same declared
commands.

### Formatting

Ruff owns Python formatting. Do not combine competing Python formatters. Local
hooks MAY rewrite files; CI uses `ruff format --check` and never mutates the
checkout as a substitute for a clean change.

### Linting

Start with correctness, imports, modernization, bugbear, pytest, and Ruff rules.
Expand deliberately. Do not enable a large rule set and then hide it behind
unexplained repository-wide ignores.

### Type Checking

`ty check` is mandatory for production code and tests. New suppressions require
a narrow scope and an explanation when the reason is not obvious. Typed public
interfaces are more important than chasing an arbitrary annotation percentage.

### Tests

`pytest` is mandatory. Tests SHOULD cover public behavior, error handling,
serialization boundaries, and regressions. Integration tests SHOULD use the
smallest realistic boundary; network and external service access must be
explicitly marked and isolated.

## Documentation-Only Gates

A documentation repository MUST define equivalents for:

- Markdown format or lint validation
- internal link validation
- external link validation with an intentional retry or allowlist policy
- documentation-site build when a site generator exists

The exact tools are repository decisions. Python-based tooling managed through
`uv` is preferred to preserve the default ecosystem and a single lock file.

## Conditional Gates

Add these only when the repository has the associated failure mode:

| Concern | Example gate |
| --- | --- |
| Coverage regression | `pytest-cov` threshold or diff coverage |
| Dependency declaration | `deptry` |
| Known vulnerabilities | dependency review or audit tooling |
| Public API stability | API snapshot or compatibility test |
| Schema compatibility | backward-compatibility checker |
| Generated code drift | regenerate, then `git diff --exit-code` |
| Performance budget | stable benchmark with a justified threshold |
| Container delivery | image build and vulnerability scan |
| Documentation site | production-mode site build |

Coverage is evidence, not a goal by itself. A high percentage does not replace
tests of risky behavior.

## CI Requirements

CI MUST:

- run on every pull request and on pushes to `main`
- start from a clean checkout
- install from the committed lock file
- declare least-privilege permissions
- use immutable third-party action references where practical
- set timeouts and cancel superseded runs
- preserve logs sufficient to diagnose failures

Branch protection SHOULD require the authoritative quality job before merge.

## Exceptions And Failures

Do not skip a failing gate simply to merge. Fix the defect, fix a broken gate,
or record a time-bounded exception with an owner and compensating control.
