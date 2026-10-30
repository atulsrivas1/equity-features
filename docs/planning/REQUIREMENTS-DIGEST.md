# Requirements digest: the owner's rules in the owner's words

> Working document, not a decision. Written by the PO, 2026-10-30. Internal, synthetic, pre-release. Every agent reads this before any brief.
> Each rule is **owner-stated** and quotes or closely follows its source. Nothing here is "confirmed by owner" beyond what the source says. Coordinator and PO defaults are NOT in this digest; they are in DECISIONS.md with status "decided, pending owner review".

Sources: `DECISIONS.md` (D), `docs/COORDINATOR_WORKING_AGREEMENT.md` (WA), `docs/playbook/ADOPTION.md` (AD, owner answers of 2026-10-30), `work/HANDOFF-2026-10-30.md` (HO, local only).

## Team and process

| # | Rule (owner words) | Marker | Source |
|---|---|---|---|
| T1 | "Team is 3 Developers (core, io, workers) + 1 Tester", with PO, Architect and coordinator always on. A fourth Developer only if 20+ Ready stories share no files. | owner-stated | D 2026-10-30; AD |
| T2 | "Every PR carries three independent reviews (UI design, architecture, code)"; UI design is N/A with a stated reason when no UI file is touched. | owner-stated | D 2026-10-30 |
| T3 | "One git worktree per agent." | owner-stated | D 2026-10-30 |
| T4 | "Release 0 (PO and Architect design the whole system and audit the existing one) starts now, then they work one release ahead of the builders." | owner-stated | D 2026-10-30 |
| T5 | Release gates are "the owner publish gate only". Publish, tag and sign-off stay with the owner. | owner-stated | D 2026-10-30; AD |
| T6 | Licence stays Apache-2.0. | owner-stated | D 2026-10-30 |
| T7 | Sub-agents use Haiku 5.5 or Sonnet 5.5 by complexity; never Astra; Opus/Fable only on explicit request. | owner-stated | D 2026-10-21 |
| T8 | Scope limited to Equity Features for now. | owner-stated | D 2026-10-21 |
| T9 | Never label an owner decision confirmed without the owner's answer; record decisions with their real approval state. | owner-stated | WA |
| T10 | Resolve routine blockers autonomously with the best available option; obtain owner approval before an option incurs a cost. Communicate briefly, one decision at a time. | owner-stated | WA |
| T11 | Every PR, including documentation, gets a fresh independent read-only reviewer who is not its author. | owner-stated | WA |

## Testing and merge

| # | Rule | Marker | Source |
|---|---|---|---|
| Q1 | "No unit or automated tests; acceptance is manual browser/runtime verification." | owner-stated | D 2026-10-21 |
| Q2 | Local builds and local test runs provide merge validation; hosted CI is not a merge prerequisite. Record real commands, commit, environment and results; do not claim unexecuted checks or infer another platform from a local run. | owner-stated | WA clarification 2026-10-20; D 2026-10-21 |
| Q3 | Test environment is local only. Merge gate: `python tools/pre_merge_check.py` plus manual runtime verification. | owner-stated | AD |
| Q4 | Every release includes a browser demo of completed capabilities using synthetic or explicitly licensed examples, showing actual outputs and remaining gaps. A demo does not authorize a production app or exposing private data. | owner-stated | WA |
| Q5 | Distinguish implemented, reviewed, tested, released and completed; record partial work honestly. | owner-stated | WA |

## Architecture and data

| # | Rule | Marker | Source |
|---|---|---|---|
| A1 | Library input/output contracts are source-independent and identical across adapters; no source-specific schema in calculation APIs. | owner-stated | WA |
| A2 | Flow: existing DuckDB on N: or synthetic data -> input adapter -> workers -> feature libraries -> output sink -> new output DuckDB. Libraries contain no DuckDB/storage or HTTP access; workers do not duplicate calculation mathematics. | owner-stated | WA |
| A3 | Adapters own conversion from external representations to canonical inputs; sinks own conversion from results to destination storage. | owner-stated | WA |
| A4 | Use clearly labelled synthetic mock data for unavailable inputs. Do not label real stored observations synthetic; fallback must not silently invent coverage, freshness or available-at evidence. | owner-stated | WA |
| A5 | Source databases stay separate from generated outputs (a new, separate DuckDB). Production writes need owner authorization. | owner-stated | WA |
| A6 | Capabilities are available through reusable libraries and an API suitable for future SaaS. The API is optional/secondary, its timing delegated to the coordinator, and it must not block the core local pipeline. SaaS production claims need explicit contracts and qualification; paid infrastructure and public deployment need owner approval. | owner-stated | WA |

## Escalation and boundaries

| # | Rule | Marker | Source |
|---|---|---|---|
| E1 | Paid services, trading orders, external notifications, public deployment/package or release publication, production database/worker writes and destructive shared-history changes need owner authorization. | owner-stated | WA |
| E2 | Providers, cost and data rights are not ours; they belong to the data-generating process. Legal means only that the owner decides any legal position. | owner-stated | AD (Applicability); HO |
| E3 | Owner-only items: ratifying E1-E9 and PO-1..PO-7; Linux machine/qualification; owner demo; publish/tag/sign-off; EF5 "stop at primitives" reversal; the design owner's 252-vs-253 period number; line-ending rule (.gitattributes); package version bump at release. | owner-stated (list) | HO |
| E4 | Only the coordinator authorizes contract amendments; workers report contract defects and pause. | owner-stated | WA |
| E5 | Never reuse a completed release worker for another release. | owner-stated | WA |

## Local rules

`gh auth switch -u atulsrivas1` before every push or merge; squash-merge only; wording "internal, synthetic, pre-release"; no new unit tests. Source: AD, WA.

Not owner-stated (kept out): the 2026-10-28 merge-precondition and regression-fixture rules are PO rulings recorded in WA, status pending owner review.
