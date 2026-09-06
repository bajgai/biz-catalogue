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

## Gates

- `.public-repo-policy.json` lists every allowed public path. Unknown files fail.
- The Python guard inspects staged Git objects, not just working files. Forced
  additions still undergo the same checks.
- It rejects prohibited paths and data formats, symlinks/submodules, binary or
  oversized files, and common credential patterns. Messages identify the rule
  and file without echoing the matched value.
- The push hook scans the history reachable from outgoing refs, including older
  files later removed. A new branch or tag is not an escape from this check.
- GitHub Actions runs the guard, its regression tests, and Gitleaks with full
  checkout history. Scanner reports and artifacts are not uploaded publicly.
- GitHub secret scanning and push protection block supported credential patterns.
  Protected `main` requires the two CI checks through a pull request, including
  for administrators; force-push and deletion are disabled.

The exact-path list is deliberately conservative. Review a new path and its
contents before adding it. Never allowlist real data or credentials. Changes to
the guard, policy, hooks, or workflows require the repository owner's attention.

## Limits

These checks reduce accidental publication; they cannot classify every piece of
intellectual property or every arbitrary password. Hooks can be bypassed, and CI
runs after a branch has been uploaded. GitHub's credential push protection does
not provide a general proprietary-data filter for this personal public repository.
Review before pushing is essential, including for allowlisted files and comments.

Apply the same boundary to issues, PRs, commit messages, screenshots, logs,
artifacts, releases, and externally published sites. Keep Actions permissions
read-only by default and use narrowly scoped runtime secrets only when needed.
Do not put secrets in client-side or public-prefixed environment variables.

## Verification

```sh
sh scripts/install-hooks.sh
python3 -m unittest discover -s tests
python3 scripts/public_repo_guard.py --staged
python3 scripts/public_repo_guard.py --history
```

The tests use temporary repositories and generated dummy strings. They exercise
blocked database/secret files and unsafe historical content without uploading it.
Run these checks after modifying publication controls. See `SECURITY.md` for
exposure response.
