# Adoption

## New Repository

1. Select a profile from `docs/repository-shapes.md`.
2. Copy the matching `repo-quality.toml` from `examples/`.
3. Replace example names and add justified required paths.
4. Write the README for users and `AGENTS.md` for safe changes.
5. Add local hooks and CI with the same authoritative commands.
6. Run `repo-quality check .` and the full gate chain.
7. Protect `main` once CI exists.

Do not copy the entire reference repository. Adopt the contract and only the
files that serve the target repository.

## Existing Repository

Adopt incrementally while keeping the default branch usable:

1. Record the current commands and failure modes.
2. Add formatting and linting without mixing unrelated code changes.
3. Add typing to owned interfaces and touched areas; document a bounded backlog
   if a one-step migration is impractical.
4. Stabilize the test command and isolate non-hermetic tests.
5. Lock dependencies and make CI authoritative.
6. Add purpose-specific docs, ownership, and security guidance.
7. Enable stricter gates only after the baseline is reliably green.

## Proportionality

A small library does not need production runbooks. A documentation repository
does not need empty application directories. A critical service may need schema
compatibility, dependency review, container scanning, integration environments,
and release provenance beyond this baseline.

Add controls because the failure mode exists, not because another repository
has the file.

## Measuring Adoption

Good adoption means:

- a new contributor reaches a passing local check without private coaching
- CI failures identify the next action
- the default branch remains reproducible
- ownership and exceptions are discoverable
- README and `AGENTS.md` stay concise because detail has an authoritative home

Avoid measuring success by file count, badge count, or raw coverage percentage.
