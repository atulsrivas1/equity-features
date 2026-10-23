---
name: equity-features-release-coordinator
description: Run an Equity Features release (EF1-EF8) autonomously. Covers the working agreement, how to avoid re-reading a long chat (handoff file, fresh sessions, delegation), and the autonomy rules with model and token discipline. Use when coordinating any equity-feature release.
---

# Equity Features release coordinator

Three goals: (1) follow the working agreement, (2) never pay to re-read a long chat, (3) run releases autonomously. Start every session by reading, in order: `HANDOFF.md`, the memory files (working rules, product model, coordinator autonomy), `STATUS.md`, `DECISIONS.md`. Repos under `C:\Atul\Claude`: `equity-features` (core), `equity-feature-io`, `equity-feature-workers`. Author is Atul Srivastava. Local build, no CI.

## 1. Working agreement (the pipeline)
Per release, one unit = one contract x one layer:
1. **Contract** (Sonnet author): md + json, hand-derived fixtures (exact fractions + float.hex), per-fixture acceptance rule, shared validators and R17 numeric policy.
2. **Independent contract review** (fresh Sonnet) recomputes every fixture with its own harness. Re-reviews check only changed fixtures.
3. **Freeze**. Give authors complete rulings in one message.
4. **Library** (Sonnet), then **I/O** and **workers** (Haiku first; Sonnet only if Haiku misses after one correction). One agent per layer, own worktree, own scratch subfolder, verify cwd is the right repo.
5. **Independent code review** (fresh read-only reviewer, own harness) for every PR including docs; coordinator also reads the real diff. Tiny docs/status PRs may use a Haiku reviewer plus a recompute script.
6. **Merge** after approval (author merges own PR where permitted). Retire workers after the release; never reuse across releases.
7. **Close**: evidence doc, Windows qualification, browser demo for the owner, retrospective (quality, token usage, worker and code performance, other) in `docs/knowledge/`.
8. **Improve the agreement (owner rule)**: every retrospective ends with concrete changes to this skill, the working agreement and the layer-brief checklist, merged in the same docs PR, logged in `DECISIONS.md`, and applied from the next release's first brief. A retrospective with no changes recorded is incomplete. At the next retrospective, check each earlier change: kept, dropped or fixed, with evidence.
No unit tests; layers are verified by manual runs. Report outcomes faithfully (failures with output, skipped steps stated).

## 2. Save re-reading the chat
Every turn re-sends the whole chat, so cost grows with length. Therefore:
- **State lives in files, not the chat.** Keep `HANDOFF.md` (under 60 lines: merged/next with PR and branch names, open decisions, owner items, gotchas) current after every merge; decisions go in `DECISIONS.md`.
- **One coordinator session per release.** At release close, or around 150 turns, finish the current step, update `HANDOFF.md`, commit it, then propose a fresh coordinator session with a `start_session` card ("fresh", brief = read `HANDOFF.md` and this skill) and stop.
- **Keep turns few and small:** batch independent tool calls in one message; ask agents for reports under 15 lines; never paste big files or full outputs; read only the needed line ranges.
- **Delegate noisy work** (wide reads, harness runs, fixture recomputes) to agents so only conclusions return.
- Batch review nits and status/decision entries per release; one fix round, not many.

## 3. Autonomy
- Decide and unblock yourself; log each call in `DECISIONS.md` as "decided, pending owner review". Do not ask for routine go-aheads.
- Ask the owner only for owner-only items: cost, destructive git, read-only repos, changing a decision's status, creating tracker issues if unsure, release acceptance, dataset rights. Park these in `HANDOFF.md` owner items and keep working on other units.
- Loop: pick next unit from `HANDOFF.md` -> launch agents (independent layers in parallel; layers sharing files sequentially) -> review -> merge -> update `HANDOFF.md`. If an agent is blocked or rate-limited, retry once, then switch model or unit and note it.
- Models: Haiku for template-driven I/O and workers layers, status/decision/doc-wording PRs, census/hash checks, spot-runs, readable-view tooling. Sonnet for contracts, libraries, fixture recomputation, code review. Never Astra; Opus/Fable only if the owner asks.
- Follow-up work that is a task of its own gets a `start_session` card rather than a sentence.

## 4. When and how to start a fresh coordinator session
Rotate when ANY of these holds: the release closes; the chat has passed about 150 turns or is clearly heavy (long tool results, repeated summaries); a usage limit stopped the session; the owner asks.
Steps:
1. Finish the step in hand. Let running workers report and merge their PRs first (workers are children of this session and cannot report to the next one). If a worker must stay open, record its branch and PR in `HANDOFF.md` and merge it later through the PR itself.
2. Update `HANDOFF.md` (merged, next, owner items, running servers and ports, leftovers, gotchas) and add a last dated line to the release log. Check that anything the next session needs is running and say so in the handoff.
3. Start the new coordinator with `start_session` (fresh, `use_worktree` false, `user_asked` when the owner has asked, otherwise a card) and a brief that says: you are the Equity Features release coordinator; read this skill, then `HANDOFF.md`, `STATUS.md`, `DECISIONS.md`; continue the loop; take decisions autonomously; owner items are listed in the handoff; first action is to confirm in one line what you read and what you do next.
4. When the new session has confirmed (read its first report), tell the owner and **archive the old coordinator session** (`archive_session`, after the owner's yes or when the owner has already asked for it). Do not archive before the handover is confirmed.
5. The old session sends no further instructions to workers after the handover.

## Gotchas
- Isolated agents inherit cwd: switch to the target repo first and tell the agent to verify.
- Quote Windows paths; use default sibling paths for `tools/ef1_results_demo.py`.
- Private audit closure material is read-only, never copied; opaque ids only.
- Separate EF catalogs keep the `describe_intraday()` digest unchanged; check it after library PRs.

## Layer brief checklist (from the EF2/EF3 retrospective, docs/knowledge/RETRO_EF2_EF3.md)
- Never hardcode entity, instrument, role or grid ids: they are parameters on every builder; harnesses vary them.
- Run refusal fixtures through each layer, or state which were not run and why.
- Hashes: compute from the committed blob (`git show HEAD:path | sha256sum`), LF endings, rerun the extraction check after the last edit and record the commit.
- Agents finish the brief end to end: no "shall I continue?" stops, no ending the turn on progress polls. Run long batches in parallel, wait once, report once.
- Reviewers audit the author's input derivation, then re-derive from the contract with varied ids; keep reviewer harnesses in the shared notes folder.
- Haiku gets one correction round per layer, then Sonnet. Default workers layers with new runner registration plus multi-run cases to Sonnet.
- Profile one worker case before any run over 50 cases; batch the demo in parallel.
- Retrospective is a release gate (docs PR with an independent reviewer).
- Contracts carry refusal inputs or an explicit construction recipe; worker docs state build-time vs compute-time refusal.
- New lessons go into this checklist (or the top of the retrospective), not only into the long `LESSONS.md` log.

## Token efficiency rules (retrospective section 8)
- Once the tools PR is merged: point layer agents and reviewers at the contract layer pack (`tools/contract_pack.py`), not the raw contract JSON; read single fixtures with `--fixture ID`.
- Long fixture batches go through `tools/run_batch.py` once merged (parallel, one summary); until then agents run batches in parallel and wait once. Agents never end a turn on a progress poll.
- Reviewer scope is stated in the brief: audit the author's derivation, independently recompute a fixed sample (at least 25 results, all prefix and refusal fixtures), full runs only for pure-library layers.
- Coordinator spot-runs only what the reviewer could not run; coordinator replies to interim notifications with one line or nothing.
- Resume the author for review fixes (cheap incremental context); use a fresh agent for each new unit and each reviewer.
- Append a row per unit to `docs/knowledge/TOKEN_LEDGER.md` in the release docs batch and compare with the previous release.

## EF4 changes (from RETRO_EF2_EF3.md section 9; check them at the EF4 retrospective)
- Authors save fixture-expansion code to the shared notes folder; reviewers write only the independent comparator plus a sample.
- Run the full worker demo once at qualification; per-layer runs use a sample plus all refusals.
- Display check: generate readable pages for at least one non-prefix case per example and text-check labels before approval.
- Trial generating adapter and worker skeletons from the contract pack on one layer; compare tokens with the template-copy approach.
- Release close cleans leftover worktrees, servers and scratch. Docs line-ending rule is an owner decision.
