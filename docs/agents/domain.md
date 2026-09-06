# Domain Docs

This project uses a single-context layout: root `CONTEXT.md` and `docs/adr/`.

## Before exploring

Read root `CONTEXT.md` for resolved terms, then relevant ADRs in `docs/adr/`.
If these files do not exist, proceed silently; do not create empty scaffolding
or propose documentation solely because it is absent. `/domain-modeling`, also
reached through `/grill-with-docs` and `/improve-codebase-architecture`, creates
them when terms or decisions are resolved.

## Vocabulary and decisions

Use the glossary's domain terms in issues, proposals, code, and tests. If a term
is missing, reconsider it or note the gap for `/domain-modeling`.
When a proposal contradicts an ADR, identify the ADR and explain why the decision
might need to be reopened rather than silently overriding it.

Domain documentation is public. Describe schemas and concepts using invented
examples; keep real store records, proprietary datasets, and secrets out.
