# Contributing

1. Create a branch and keep changes focused.
2. Keep real store information, credentials, exports, internal notes, and licensed
   datasets outside this checkout. Use invented examples only.
3. Review each new file for public release.
4. Stage named files, review `git diff --cached`, commit, and push the branch.
5. Open a pull request. The secret scan must pass before merge.

Public issues, PR descriptions, screenshots, logs, Actions artifacts, and release
attachments need the same review as source files.

Sensitive inputs must be loaded at runtime from authorized private storage.
API keys and database credentials must remain on the server. Browser bundles,
static assets, and public-prefixed environment variables are public output.
