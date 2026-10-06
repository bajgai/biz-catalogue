# Public repository policy

## Publication boundary

Only source code, sanitized project documentation, and invented examples reviewed
for public release belong here. Real store catalogues and databases, customer or
employee records, scraped collections, purchased or licensed datasets, internal
business research, credentials, and authenticated browser state remain private.
Do not assume a dataset can be republished because individual records are public.

Keep operational datasets and secret stores outside this checkout. `.gitignore`
also excludes common private locations and formats as a fallback. Local agent
installations and skill links are machine configuration and are excluded.
Public source must not embed sensitive data in code, comments, tests, screenshots,
generated bundles, database seed scripts, or documentation.

## Checks

- GitHub Actions scans the full history with Gitleaks. Scanner reports and
  artifacts are not uploaded publicly.
- GitHub secret scanning and push protection block supported credential patterns.

The local publication guard (path allowlist, hooks and history scan) was removed
on 2026-10-05. Review every new file and its contents before committing.

## Limits

These checks reduce accidental publication; they cannot classify every piece of
intellectual property or every arbitrary password, and CI runs after a branch has
been uploaded. GitHub's credential push protection does
not provide a general proprietary-data filter for this personal public repository.
Review before pushing is essential, including for allowlisted files and comments.

Apply the same boundary to issues, PRs, commit messages, screenshots, logs,
artifacts, releases, and externally published sites. Keep Actions permissions
read-only by default and use narrowly scoped runtime secrets only when needed.
Do not put secrets in client-side or public-prefixed environment variables.

See `SECURITY.md` for exposure response.
