# Contributing

## Development Setup

```bash
uv sync --locked --all-groups
uv run pre-commit install
```

## Workflow

1. Create a short-lived branch from `main`.
2. Keep the change focused on one standard or implementation concern.
3. Update normative docs before or with rule changes.
4. Add tests for behavior changes and regression fixes.
5. Run every command listed in the root `AGENTS.md`.
6. Open a pull request explaining intent, impact, and validation.

Pull requests should remain reviewable. Separate mechanical changes from policy
changes when combining them would obscure the decision.

## Commit And Review Expectations

- Use descriptive imperative commit subjects.
- Do not rewrite a shared branch.
- Require passing CI before merge.
- Require maintainer approval for security exceptions, breaking schema changes,
  or weaker mandatory gates.
- Prefer squash merge unless preserving individual commits adds lasting value.

## Proposing A Standard Change

Explain:

- the failure mode or maintenance cost being addressed
- which repository profiles are affected
- whether the rule is mandatory, recommended, or optional
- local and CI implications
- migration and compatibility considerations

Record durable or disputed choices as an ADR under `docs/adr/`.
