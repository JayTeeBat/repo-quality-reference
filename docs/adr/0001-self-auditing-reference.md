# ADR 0001: Make The Reference Self-Auditing

## Status

Accepted

## Context

A documentation-only standard can drift away from its examples. Copyable
templates can also appear authoritative even when their rationale changes.

## Decision

The repository will be a Python single-package project that implements a
read-only `repo-quality check` command. A small TOML contract declares the
profile, required paths, optional document headings, quality commands, and CI
workflow. Tests require this repository to pass its own checks.

The checker will not execute configured commands. CI remains responsible for
running them. It will not infer document meaning through synonyms or language
models; qualitative content remains a review responsibility.

## Consequences

- Structural, internal-link, and CI-command drift fail visibly.
- Repositories can enforce their own headings without inheriting this
  reference's vocabulary.
- The repository demonstrates the Python gates it mandates.
- Content quality and proportionality still require human review.
- The configuration schema becomes a compatibility surface.

## Alternatives

- Documentation only: simpler, but unable to detect drift.
- Full scaffold generator: useful for creation, but larger than the goal and
  likely to copy unnecessary files into target repositories.
- Execute declared gates from the checker: rejected because reading a repository
  should not execute untrusted commands.
