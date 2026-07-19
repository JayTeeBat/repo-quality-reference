# Repository Quality Reference

[![Quality](https://github.com/JayTeeBat/repo-quality-reference/actions/workflows/quality.yml/badge.svg)](https://github.com/JayTeeBat/repo-quality-reference/actions/workflows/quality.yml)

## Purpose

This repository defines a practical quality baseline for repositories maintained
by humans and coding agents. It is both documentation and an executable example:
the `repo-quality` package checks that a repository declares its purpose,
contains the expected structure, documents its operating rules, and runs its
declared quality gates in CI.

The standard is intentionally small. It favors explicit ownership,
reproducibility, fast feedback, and evidence over badges or process ceremony.
Python and `uv` are the maintained default language and tooling ecosystem.

## Quick Start

Install the development environment and verify this repository:

```bash
uv sync --locked --all-groups
uv run repo-quality check .
uv run check-docs-format
uv run check-docs-links
uv run build-docs
uv run pytest
```

To evaluate another repository, add a `repo-quality.toml` based on an example
under [`examples/`](examples/) and run:

```bash
uvx --from git+https://github.com/JayTeeBat/repo-quality-reference.git \
  repo-quality check /path/to/repository
```

Document headings are repository-owned. Add an optional `[documentation]`
table when exact README or `AGENTS.md` sections are part of the local contract;
otherwise the checker only requires non-empty documents with valid internal
links.

## Repository Shapes

| Purpose | Use when | Canonical content |
| --- | --- | --- |
| Documentation only | The durable output is guidance, policy, specifications, or a knowledge base | `docs/`, navigation or index, link checks, optional site build |
| Python single package | One independently versioned library, CLI, or service owns the repository | root `pyproject.toml`, `src/<package>/`, `tests/`, `uv.lock` |
| Python workspace | Several related packages share governance and coordinated tooling | root workspace config, `packages/<name>/`, shared docs and CI |

See [Repository Shapes](docs/repository-shapes.md) for decision criteria,
example trees, and directory responsibilities.

## Quality Gates

Every Python repository covered by this standard runs, at minimum:

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
```

Package repositories also build their distributable artifact. Local hooks
provide fast feedback, while CI runs the authoritative locked gate chain. See
[Quality Gates](docs/quality-gates.md) for universal, profile-specific, and
conditional gates.

The documentation commands are installed with the package. They check Markdown
formatting, validate local links and heading fragments, retry external link
checks, and build a strict MkDocs site. Known external exceptions can be made
explicit with repeatable `--exclude-url-prefix` arguments.

## Repository Layout

```text
.
|-- .github/                 # CI, dependency updates, ownership, PR template
|-- docs/                    # Normative standard and architecture decisions
|-- examples/                # Example configuration for each repo shape
|-- src/repo_quality/        # Self-auditing reference implementation
|-- tests/                   # Behavior and conformance tests
|-- AGENTS.md                # Instructions for coding agents
|-- CONTRIBUTING.md          # Human contribution workflow
|-- mkdocs.yml               # Strict documentation-site configuration
|-- SECURITY.md              # Vulnerability reporting and security boundary
|-- pyproject.toml           # Package and tool configuration
|-- repo-quality.toml        # Declared profile and quality contract
`-- uv.lock                  # Reproducible dependency resolution
```

## Source Of Truth

- [Standard](docs/standard.md): normative principles and requirement language
- [Repository Shapes](docs/repository-shapes.md): purpose-specific layouts
- [Quality Gates](docs/quality-gates.md): local and CI checks
- [README and AGENTS](docs/readme-and-agents.md): audience and content rules
- [Repository Lifecycle](docs/lifecycle.md): security, dependencies, PRs, and releases
- [Adoption](docs/adoption.md): introducing the standard proportionately

When documentation and implementation disagree, the normative documents define
intent and the mismatch is a defect.

## Adoption

Start with the smallest profile that matches the repository's actual purpose.
Copy an example configuration, document justified exceptions, and introduce
gates in an order that keeps the default branch usable. Existing repositories
do not need a disruptive one-shot migration; see [Adoption](docs/adoption.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the branch, test, and review workflow.
Coding agents must also follow [AGENTS.md](AGENTS.md).

## License

Licensed under the [MIT License](LICENSE).
