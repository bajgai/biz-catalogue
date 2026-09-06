# Project skills

Shared skills are in `.agents/skills/`. Consult the relevant `SKILL.md` before
using a skill, and load its references only as needed. This applies to all
agents working in this project, including delegated agents.

The Matt Pocock collection is linked from `/Users/home/scratch/skills`.
Its inventory is `.agents/matt-pocock-skills.json`. Keep that source directory
in place. Updates to the source are reflected here through symlinks.

Respect `disable-model-invocation: true` and
`policy.allow_implicit_invocation: false`: those skills require a human request.
When a skill mentions a tool unavailable in your harness, use the equivalent
supported operation and report any capability that cannot be provided.

`setup-matt-pocock-skills` is installed for the human to invoke when ready.

## Public repository boundary

This repository is public. Follow `docs/security/public-repository.md` before
staging, committing, pushing, posting, or generating publicly served assets.
Never include real store databases, exports, proprietary business records,
licensed datasets, passwords, API tokens, private keys, or authenticated state.
Keep those inputs in authorized private storage outside the checkout; use
invented examples only. Local skill installations remain excluded from Git.

Review every new public path before adding it to `.public-repo-policy.json`.
Run `python3 scripts/public_repo_guard.py --staged` before committing and
`python3 scripts/public_repo_guard.py --history` before publication. Do not
bypass hooks, weaken rules, or print secret matches. Review public issue/PR
text and attachments too; Git checks cannot protect those surfaces.
