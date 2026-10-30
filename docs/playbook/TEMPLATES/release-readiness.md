# Template: release READINESS (`docs/releases/<release>/READINESS.md`)

> Part of the portable playbook. Written by the PO one release ahead; refreshed at each merge that changes a story or contract. It explains the generated backlog; it does not replace it. Counts come from the generator, never typed.

```markdown
# {{Release}} readiness: Ready, Blocked, and how the Ready set grows

> Working document, not a decision. Written by the PO. Date {{YYYY-MM-DD}}. Source: the generated ordered backlog, section "{{release}}".

## 1. Counts
{{Stories: N. Ready: R (frozen F, stub S). Blocked: B. Startable with nothing else needed: K (ids). How the number moved since the last revision and why.}}

## 2. The Ready set
{{Ready (frozen): ids. Ready (stub): ids.}}

## 3. The Blocked set: exact missing item and who closes it
| Group | Stories | Exact missing item | Closer and action | Direct / waiting |
|---|---|---|---|---|
| G1 {{title}} | {{ids}} | {{the missing thing}} | {{Role: action}} | {{n}} |

Check line: group counts add to the Blocked total, each story counted once.

## 4. Contracts the release reads, and the Architect's items
{{Which exist, their state, which are not agreed with the system of record (it wins on shape). Numbered Architect items A1..An.}}

## 5. Owner and engineering items the release meets (publish, not build)
| Closer | Items | Blocks | Provisional decision in force |
|---|---|---|---|

## 6. Plan: a Ready set big enough for the builders
{{First tasks T0, T1 before any pull; lanes per Developer (core, io, workers); week-1 closers; one-release-ahead plan; refresh rule.}}

## 7. Ready buffer
{{Target vs actual for the current release and the next; when measured (half Done, at demo).}}
```

Closer codes: A Architect, PO, E engineering confirmation, O owner.
