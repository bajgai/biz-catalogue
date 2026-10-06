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

## Matt skill invocation in this directory

Treat the following names as a persistent project index, even when the harness
omits them from its advertised skill catalog. Read the selected skill at
`.agents/skills/<name>/SKILL.md` before following it; resolve its references
relative to that skill directory. Report a missing file rather than guessing.

- Engineering: `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`,
  `domain-modeling`, `grill-with-docs`, `implement`, `improve-codebase-architecture`,
  `prototype`, `research`, `resolving-merge-conflicts`, `setup-matt-pocock-skills`,
  `tdd`, `to-spec`, `to-tickets`, `triage`, `wayfinder`, `wizard`.
- Productivity: `grill-me`, `grilling`, `handoff`, `teach`, `to-questionnaire`,
  `wait-what`, `writing-for-agents`.
- In progress: `claude-handoff`, `implement-spec`, `loop-me`, `retro`,
  `setup-ts-deep-modules`, `writing-beats`, `writing-fragments`, `writing-shape`.

When the user explicitly invokes one of these names, accept `$<name>`,
`$mattpocock-skills:<name>`, or a leading `/<name>` or `#<name>` followed by
optional task text. These aliases select the same source skill. Quoted examples,
code blocks, and ordinary Markdown headings are not invocations. If a built-in
command consumes an alias before it reaches the agent, use the native picker.

Native discovery: Codex CLI/IDE uses `/skills` or `$`; search for
`mattpocock-skills:<name>`. ChatGPT uses `@`. The `/name` and `#name` aliases above
are agent routing for submitted text, not registered UI autocomplete commands.
Keep existing explicit-only policies: indexing a skill does not activate it.

## Public repository boundary

This repository is public. Follow `docs/security/public-repository.md` before
staging, committing, pushing, posting, or generating publicly served assets.
Never include real store databases, exports, proprietary business records,
licensed datasets, passwords, API tokens, private keys, or authenticated state.
Keep those inputs in authorized private storage outside the checkout; use
invented examples only. Local skill installations remain excluded from Git.

Review every new file for public release before committing. Never print secret
matches. Review public issue/PR text and attachments too.

## Agent skills

### Issue tracker

Use GitHub Issues/PRs for public work, local Markdown for private research and
drafts, and the `agentctl` board for task ownership and execution coordination.
See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

Use a single-context layout: root `CONTEXT.md` and `docs/adr/`.
See `docs/agents/domain.md`.
