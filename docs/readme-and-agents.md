# README And AGENTS.md

## Different Audiences

`README.md` helps a user or evaluator understand and use the repository.
`AGENTS.md` tells a coding agent how to change it safely. They may link to the
same detailed documents, but they should not mirror each other.

## README.md

The README MUST make the repository evaluable before it becomes exhaustive.

Include:

- purpose and intended audience
- current status when stability is not obvious
- quickest successful setup and usage path
- representative output, screenshot, or example when the result is visual
- supported repository or deployment shape
- concise architecture or layout orientation
- exact entry point to quality checks
- links to deeper docs, contribution guidance, security policy, and license

For public portfolio repositories, also include the problem, key decisions,
personal or team ownership, and measured result when those are not otherwise
obvious.

Exclude:

- agent-specific instructions and hidden workflow conventions
- full operator manuals that obscure the first successful path
- exhaustive API references better generated or kept in `docs/`
- roadmaps presented as delivered capability
- badges without decision value
- duplicated commands likely to drift
- marketing claims unsupported by examples or measurements

The first screen should normally answer: what is this, who is it for, why does
it matter, and how do I try or verify it?

No README heading title is globally mandatory. A repository MAY opt into exact
headings when they are part of its local contract:

```toml
[documentation]
readme_sections = ["Purpose", "Installation", "Usage"]
```

## AGENTS.md

`AGENTS.md` MUST be repository-specific and operational. It is not a place for
machine-wide preferences or generic coding advice.

Include:

- repository purpose and non-goals
- authoritative files and ownership boundaries
- exact setup and quality-gate commands
- package, module, and directory responsibilities
- public API, schema, migration, or compatibility constraints
- testing expectations and fixture boundaries
- documentation synchronization rules
- human-only decisions and prohibited autonomous actions
- change-control notes for risky or breaking work

Exclude:

- product marketing and onboarding prose
- credentials, internal URLs, or environment-specific secrets
- instructions already enforced by formatter or linter configuration
- stale snapshots of directory trees that add no ownership meaning
- broad permission grants such as "change anything needed"
- copied global instructions with no repository-specific refinement
- temporary task notes that belong in an issue or pull request

## Layering

Nested `AGENTS.md` files MAY refine rules for a package or subsystem. A nested
file should describe only the narrower context and must not silently weaken root
quality or security requirements.

Like README headings, exact `AGENTS.md` headings are optional and
repository-owned:

```toml
[documentation]
agents_sections = ["Repository Purpose", "Quality Gates", "Testing Policy"]
```

The checker verifies declared titles exactly, ignoring case. It does not use
synonym lists or language-model classification to infer whether prose satisfies
a topic. When no titles are declared, it verifies that both documents exist,
are non-empty, and have valid internal links. Reviewers remain responsible for
content quality.

## Maintenance Test

When a rule changes, ask where a future contributor would look for it. Update
one authoritative location and link to it. If README and `AGENTS.md` need the
same long explanation, that explanation probably belongs in `docs/`.
