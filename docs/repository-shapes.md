# Repository Shapes

## Choosing A Shape

Start with the smallest release and ownership boundary that matches the durable
output. Python is the default tooling language for every maintained profile.

| Question | Documentation only | Python single package | Python workspace |
| --- | --- | --- | --- |
| Primary output | Documents or a documentation site | One library, CLI, or service | Several related Python distributions |
| Release boundary | Documents move together | One versioned package | Packages may release independently |
| Code location | Optional tooling only | `src/<package>/` | `packages/<name>/src/<package>/` |
| Test location | Link, format, and build checks | root `tests/` | package tests plus optional integration tests |

Use a workspace only when packages have real independent boundaries. A large
single application is usually still a single-package repository.

## Documentation-Only Repository

Use this profile when documents are the product: standards, specifications,
runbooks, architecture guidance, or a knowledge base.

```text
.
|-- .github/workflows/quality.yml
|-- docs/
|   |-- adr/
|   `-- topic.md
|-- tools/                    # optional Python doc tooling
|-- AGENTS.md
|-- README.md
|-- pyproject.toml            # when Python tooling is used
`-- uv.lock                   # when Python tooling is used
```

Required concerns:

- clear navigation and ownership
- Markdown formatting or linting
- internal and external link validation
- site or generated-document build when applicable
- examples checked against the documented contract when practical

Do not add an empty `src/` package merely to look like an application. A small
Python tool belongs under `tools/` until it has a reusable API and tests that
justify packaging it.

## Python Single-Package Repository

This is the default software profile. Use it for one library, CLI, worker,
service, or deployable application with one coherent release boundary.

```text
.
|-- .github/workflows/quality.yml
|-- docs/
|   `-- adr/
|-- examples/                 # only when they help users
|-- src/<package>/
|-- tests/
|-- AGENTS.md
|-- README.md
|-- pyproject.toml
`-- uv.lock
```

Rules:

- production behavior lives under `src/<package>/`
- tests exercise public behavior and important integration boundaries
- operational wrappers stay thin; durable logic remains importable and tested
- build metadata produces one distribution
- a service MAY keep deployment assets under `deploy/` or `infra/` when their
  ownership matches the service

## Python Workspace Repository

Use this profile when multiple related packages need shared governance and
atomic cross-package changes but retain meaningful package boundaries.

```text
.
|-- .github/workflows/quality.yml
|-- docs/
|-- packages/
|   |-- package-a/
|   |   |-- src/package_a/
|   |   |-- tests/
|   |   `-- pyproject.toml
|   `-- package-b/
|       |-- src/package_b/
|       |-- tests/
|       `-- pyproject.toml
|-- tests/                    # optional cross-package integration tests
|-- AGENTS.md
|-- README.md
|-- pyproject.toml            # workspace and shared tool configuration
`-- uv.lock
```

Rules:

- each package has an explicit responsibility and dependency direction
- shared code becomes a package only when multiple packages genuinely own it
- root configuration owns common gates; package configuration owns package
  metadata
- CI SHOULD select affected packages for expensive checks only after a full
  correct baseline exists
- releases MUST state whether versions are independent or synchronized

## Directories To Add Only When Needed

- `docs/adr/`: durable technical or policy decisions
- `examples/`: executable or user-facing examples
- `scripts/`: thin orchestration that is unsuitable as a package entry point
- `infra/` or `deploy/`: owned deployment configuration
- `schemas/`: source schemas with generation and compatibility rules
- `benchmarks/`: reproducible performance checks with documented interpretation

Avoid generic `utils/`, `misc/`, `common/`, or `shared/` directories without a
specific ownership boundary.
