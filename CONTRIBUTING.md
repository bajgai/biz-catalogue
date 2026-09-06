# Contributing

Install the repository hooks after every clone with `sh scripts/install-hooks.sh`.
Git does not install tracked hooks automatically. Python 3 and Git must already be
available; on the maintainer's Mac, developer tools are managed through dotfiles.

1. Create a branch and keep changes focused.
2. Keep real store information, credentials, exports, internal notes, and licensed
   datasets outside this checkout. Use invented examples only.
3. Review each new file for public release, then add its exact relative path to
   `.public-repo-policy.json`. This list is a publication decision, not a way to
   bypass a data or secret finding.
4. Stage named files, review `git diff --cached`, and run
   `python3 scripts/public_repo_guard.py --staged`.
5. Run `python3 -m unittest discover -s tests`, commit, and push the branch.
   The push hook checks all history reachable from the refs being pushed.
6. Open a pull request. The public-repository and secret checks must pass before merge.

Do not bypass hooks or weaken checks to upload a blocked file. Public issues, PR
descriptions, screenshots, logs, Actions artifacts, and release attachments need
the same review as source files; Git hooks cannot check those surfaces.

Sensitive inputs must be loaded at runtime from authorized private storage.
API keys and database credentials must remain on the server. Browser bundles,
static assets, and public-prefixed environment variables are public output.
