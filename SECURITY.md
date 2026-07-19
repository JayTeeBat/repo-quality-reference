# Security Policy

## Supported Versions

Security fixes apply to the latest release and the `main` branch.

## Reporting A Vulnerability

Do not open a public issue for a suspected vulnerability or exposed secret. Use
GitHub's private vulnerability reporting for this repository. If that feature is
unavailable, contact the repository owner privately through the contact method
on the owner's GitHub profile.

Include the affected version, reproduction steps, expected impact, and any known
workaround. Do not include real credentials or sensitive production data.

## Security Boundary

The `repo-quality` CLI reads repository files and reports findings. It does not
execute commands declared in `repo-quality.toml`, install dependencies, access
the network, or modify the target repository.

`check-docs-links` makes outbound HEAD or GET requests to HTTP(S) targets found
in Markdown unless `--no-external` is set. `build-docs` runs MkDocs and replaces
the configured site output directory, which is `site/` in this repository.
Review configuration and link targets before running these commands against an
untrusted repository.
