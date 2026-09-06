# Security

Report vulnerabilities through
[GitHub private vulnerability reporting](https://github.com/bajgai/biz-catalogue/security/advisories/new).
Do not post credentials, store records, private URLs, or sensitive attachments in
public issues, pull requests, discussions, or build logs.

If a credential is exposed, revoke it at its provider immediately, replace it in
the authorized secret store, and inspect usage. Deleting a file does not revoke
the credential or remove it from history and existing clones.

If confidential data is exposed, stop further publication and notify the owner
privately. Coordinate removal from Git history, branches, tags, artifacts, and
caches. Do not assume a history rewrite can recall existing public copies.

See [the publication policy](docs/security/public-repository.md) for required checks.
