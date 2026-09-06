# Biz Catalogue

Public project repository for Biz Catalogue. Application development has not started yet.

This repository contains reviewed source and project documentation. Store databases,
business records, licensed datasets, credentials, and internal research belong in
private storage outside the checkout. Examples must be invented and approved for
publication.

Before contributing:

```sh
sh scripts/install-hooks.sh
python3 -m unittest discover -s tests
```

The local commit and push hooks check the explicit public-file list, prohibited
file types, and common credential patterns. CI also scans with Gitleaks. See
[CONTRIBUTING.md](CONTRIBUTING.md) and the [public repository policy](docs/security/public-repository.md).

Track public work in [GitHub Issues](https://github.com/bajgai/biz-catalogue/issues).
Use [private vulnerability reporting](https://github.com/bajgai/biz-catalogue/security/advisories/new)
for security reports; never attach private records or credentials to public issues.
