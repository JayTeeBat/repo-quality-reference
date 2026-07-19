# Repository Quality Standard

## Status And Language

This document is normative. `MUST` marks a baseline requirement, `SHOULD` marks
the normal choice with room for a documented exception, and `MAY` marks an
optional practice.

Python is the default repository language and tooling ecosystem. A repository
that uses another implementation language must define an equally explicit
profile, but that extension is outside the current maintained scope.

## Goals

A conforming repository should be:

- understandable without private context
- reproducible from committed inputs
- safe to change in small increments
- verifiable locally and in CI
- explicit about human and agent decision boundaries
- proportionate to its purpose and operational risk

## Core Contract

Every repository MUST contain:

- a user-facing `README.md`
- a repository-specific `AGENTS.md`
- a `.gitignore` appropriate to its tools and data
- a declared repository purpose and profile
- exact quality-gate commands
- CI that runs every declared authoritative gate
- a documented path for contributions and security reports when the repository
  accepts external use or contribution

Python repositories MUST commit `pyproject.toml` and `uv.lock`. Dependencies
MUST be installed from the lock file in CI.

## Principles

### Purpose Before Structure

Choose the repository shape from its durable output and release boundary. Do
not choose a workspace because several directories exist, or a package because
some scripts happen to be reusable.

### One Source For Each Fact

Keep user tasks in the README, agent operating rules in `AGENTS.md`, package
metadata in `pyproject.toml`, and detailed durable knowledge in `docs/`.
Duplicated commands and rules drift.

### Local Speed, CI Authority

Local hooks SHOULD catch fast and deterministic failures. CI MUST run the
complete authoritative chain from a clean checkout and locked environment.

### Evidence Over Ceremony

A gate must prevent a credible failure mode. A document must have a known
audience. Remove process that no longer earns its maintenance cost.

### Least Privilege

CI workflows MUST declare minimal permissions. Third-party actions SHOULD be
pinned to immutable commit SHAs with a readable version comment. Secrets MUST
not be available to untrusted code paths.

### Small Public Surface

Packages and services SHOULD expose the smallest stable interface that serves
their users. Internal helpers MUST not become public accidentally through
convenient imports.

## Roles And Decisions

Humans own product intent, security exceptions, production access, releases,
breaking changes, and acceptance of risk. Coding agents may implement scoped
changes, tests, and documentation within recorded boundaries. Agents MUST not
bypass gates, invent product policy, or silently weaken contracts.

## Exceptions

An exception MUST state:

- the rule being waived
- the reason and affected scope
- the risk and compensating control
- the owner
- the review or expiry condition

Exceptions belong in an ADR or issue, not only in a transient pull-request
conversation.

## Conformance

Automated conformance is necessary but incomplete. `repo-quality check` verifies
structure, required sections, internal Markdown links, declared Python gates,
and CI parity. Reviewers remain responsible for whether the content is accurate,
proportionate, and useful.
