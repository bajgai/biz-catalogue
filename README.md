# Biz Catalogue

Public project repository for Biz Catalogue. Application development has not started yet.

This repository contains reviewed source and project documentation. Store databases,
business records, licensed datasets, credentials, and internal research belong in
private storage outside the checkout. Examples must be invented and approved for
publication.

CI scans for credentials with Gitleaks. See
[CONTRIBUTING.md](CONTRIBUTING.md) and the [public repository policy](docs/security/public-repository.md).

## For agents

- **Public status**: [GitHub Issues](https://github.com/bajgai/biz-catalogue/issues),
  open pull requests, and `docs/` (conventions in [docs/agents/](docs/agents/)).
  A current-phase status issue is pinned in the tracker.
- **Private state**: internal working notes (validation plans, findings, and
  strategy) live in git-ignored local paths and are never committed or posted
  publicly. See the [public repository policy](docs/security/public-repository.md).
- **Coordination**: this repository is enrolled in `agentctl`. Run `agentctl brief`
  before substantial work, claim tasks before starting them, and leave notes at
  task boundaries. The board is machine-local; cross-agent state that must
  survive machines goes through the public issue tracker.

Track public work in [GitHub Issues](https://github.com/bajgai/biz-catalogue/issues).
Use [private vulnerability reporting](https://github.com/bajgai/biz-catalogue/security/advisories/new)
for security reports; never attach private records or credentials to public issues.
