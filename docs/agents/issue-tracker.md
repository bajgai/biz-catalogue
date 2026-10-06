# Work tracking: GitHub, local Markdown, and agent board

Use all three surfaces, with a clear source for each kind of information:

| Surface | What belongs here | Authority and visibility |
| --- | --- | --- |
| GitHub Issues and PRs in `bajgai/biz-catalogue` | Public-safe specs, delivery tickets, progress summaries, and code review | Public delivery/merge status; available across machines |
| Local Markdown under `.scratch/` | Private research, interview questions and answers, findings, drafts, and private work items | Detailed private context; gitignored and local to this clone |
| Agent board (`agentctl`) | Task assignment, claims, execution status, blockers, and handoff notes | Who is doing what on this machine; shared by this project's linked worktrees |

These surfaces do not synchronize automatically. Link records instead of copying
their full contents. A board task can reference a GitHub issue/PR or a private
Markdown path. Public records must never contain private notes or revealing links.
Private context needed on another machine requires an authorized private transfer;
it must not be uploaded to the public tracker merely to make it portable.

## Local Markdown conventions

- Validation research and interview material: `.scratch/validation/`.
- Feature drafts: `.scratch/<feature>/spec.md`.
- Private work items, when needed: `.scratch/<feature>/issues/NN-slug.md`, with a
  title, `Status: open | blocked | done`, acceptance criteria, and evidence.
- Keep questions and answers with their relevant private research document.
- Use the label vocabulary in `docs/agents/triage-labels.md` when triage applies.
- Local Markdown is a supported destination for private work, not an instruction
  to create a duplicate file for every GitHub issue.

## Agent board conventions

Run `agentctl brief` and search `agentctl tasks` before starting substantial work.
Use a unique session identity with `agentctl --actor <session-id>`. Reuse the
matching task or create one with `agentctl create`; claim it with `agentctl claim`
before implementation. Never silently take another session's claim.
Record evidence and handoffs with `agentctl note`, check `agentctl messages` at
task boundaries, and close completed work with `agentctl finish --evidence`.
Humans can inspect and supervise work using `agentctl board`.

The board owns execution status, not product requirements or public merge status.
A completed local task does not imply a PR is merged or a deployment succeeded.
Read the linked source before continuing and reconcile conflicting status against
its evidence. Keep a deferred task's prerequisites explicit; do not start it just
because it appears in an open-task listing.

## GitHub conventions

Use the `gh` CLI for GitHub operations.

- **Create an issue**: `gh issue create --title "..." --body "..."`. For multi-line bodies, write the exact text to a temporary file and pass `--body-file PATH`.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Use `--repo bajgai/biz-catalogue` outside this clone; inside it, `gh` infers the repository from `origin`.

This tracker is public. Apply `docs/security/public-repository.md` to every title, body, comment, and attachment. Never post real store records, licensed datasets, credentials, or private URLs. A skill does not grant authority to post without user authorization.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

For public-safe, authorized work, create or update a GitHub issue. For private
work, create or update the local Markdown record. Use the agent board to assign
and track execution, linking the relevant record. Do not publish private material
to GitHub or open duplicate records merely because a skill says "publish".

## When a skill says "fetch the relevant ticket"

Resolve the ticket reference: use `gh issue view <number> --comments` for a GitHub
issue, open the named Markdown file for a private item, or use `agentctl tasks`
for a board task and follow its linked source. Check the board for an existing
claim before starting work on any of these.

## Wayfinding operations

Used by `/wayfinder`. For public-safe work, the **map** is a single GitHub issue
with **child** issues as tickets, following the operations below. Private maps and
decision tickets stay in local Markdown; the board coordinates their execution.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.
