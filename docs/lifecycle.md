# Repository Lifecycle

## Creation

- Choose the repository shape from its release and ownership boundary.
- Start on `main`; use short-lived branches for changes.
- Establish README, `AGENTS.md`, quality config, CI, and ownership before the
  first feature expands the surface.
- Keep the repository private until content, history, license, and secret scans
  are suitable for its intended audience.

## Development Workflow

Use trunk-based development by default:

- one objective per branch
- small pull requests with purpose, impact, validation, and risk
- no rewriting of shared branches
- passing required CI before merge
- review from a code owner for security, breaking changes, and exceptions

Draft pull requests are useful for early alignment but do not replace a clear
problem statement.

## Dependencies And Reproducibility

- Declare dependencies in `pyproject.toml` and commit `uv.lock`.
- Install with `uv sync --locked` in CI.
- Keep runtime dependencies minimal; development tools belong in a dependency
  group.
- Automate dependency-update proposals, but review behavior and lock changes.
- Avoid unbounded action tags; pin third-party actions to immutable commits.

## Security And Data

- Commit no credentials, tokens, personal data, production exports, or private
  keys.
- Provide `.env.example` only when environment variables are part of the public
  contract.
- Use synthetic fixtures where realistic data would be sensitive.
- Grant CI the least permissions required per workflow or job.
- Document vulnerability reporting in `SECURITY.md` for shared or public repos.
- Review the full history before changing a private repository to public.

## Interfaces, Schemas, And Migrations

Repositories with durable consumers MUST document:

- the supported public interface
- compatibility and deprecation policy
- schema ownership and generation direction
- migration, rollback, and data-loss behavior
- how compatibility is tested

Breaking changes require human approval and a migration path appropriate to the
consumer cost.

## Releases

Release only from a green default branch. A releasable package SHOULD provide:

- semantic version or another documented version policy
- changelog or generated release notes
- reproducible build command
- artifact provenance appropriate to its risk
- rollback, yanking, or deprecation process

Internal applications may release continuously, but must still identify the
deployed revision and preserve rollback evidence.

## Archival

When a repository is no longer maintained:

- state that clearly at the top of the README
- identify the replacement when one exists
- close or transfer active work
- revoke credentials and automation no longer needed
- archive the repository when changes should stop
