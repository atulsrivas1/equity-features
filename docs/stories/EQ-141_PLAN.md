# EQ141: qualify and deliver R17 — pre-code plan

[EQ141 #475](https://github.com/atulsrivas1/equity-features/issues/475), [E25 #465](https://github.com/atulsrivas1/equity-features/issues/465), [R17 milestone21](https://github.com/atulsrivas1/equity-features/milestone/21); provisional complexity5 points. Public pre-code preparation only: EQ140 remains Ready to release, so EQ141 remains Backlog/unassigned. Publish this conditional packet as a draft for review while predecessor main CI finishes; actual EQ140 Done/current accepted inputs and separate final public-packet Ready-input review remain mandatory before Ready/implementation. [Live Project](https://github.com/users/atulsrivas1/projects/2) owns status.

## Outcome and boundaries

Deliver a source- and evidence-bound R17 acceptance report, package/channel inventory, installation/migration/API/example/limitations updates and final release notes. Reconcile all six child stories, E25 and milestone21 after actual final publication and acceptance. No new numerical formula, feature ID, scheduler, provider access, persistent pool/state support, registry channel or package version is introduced solely for this audit. Source-independent calculation and unchanged core daily compatibility remain mandatory.

## Actual inputs to freeze at admission

Accepted predecessor mains: EQ1368044f2a0f59d29b85981aaa446777ac2f92fc29b; EQ137e790c30241c4420a08adbf2e92403a4cd9a74375; EQ138ee516615aec269e75f9f053ef14b39e440cae743; EQ139b1f5445eb9799b73753e413669b94166997fc468. Their final acceptance receipts, numerical/source/installed/CI evidence and actual Done status must be joined explicitly, not inferred from these commit strings.

EQ140 actually published canonicalc7010a0a7b8ad290d1fe9f10bc1528ea09b3885b and worker231349aaf2bf1b9ec21f45807382ca9c6522520c after candidate review100assertions/private9271a17b68f91eebd6f0e2b70f19b7d2465956f797d19a4baaf1b055b8c3d5f3. Actual main qualification/final acceptance remain missing inputs. Do not treat candidate passes as main acceptance. I/O inspection/unchanged delivered source18d86761aa3eebb7414e51e8fa2aba089717b5eb requires current readback.

Freeze actual six-package versions and Git source/tree/package/archive SHA mappings: contracts/core0.0.4a4, intraday0.1.0a3, I/O contracts/SDK0.1.0a2, workers0.1.0a14. Distinguish current channel artifacts from historical measurement and prerequisite artifacts, including actual run/event/attempt/producer interpreter/OS/access/expiry. Recheck open PR ownership before any edits.

## Mathematics, readiness and capability audit

Preserve accepted rational/Decimal arithmetic, scaled-price precision, seed/window/anchor/cutoff/gap/session/revision rules. No mathematical choices are unresolved or newly selected by this documentation audit. Missing evidence causes a concrete finding/rework, not a silent changed definition.

Audit core39 separately from eight own intraday IDs: intraday.ema/rsi/atr and intraday.band_middle/upper/lower/width_ratio/position. EMA/RSI consume their actual close seed/ordered recurrence. For target>anchor, ATR consumes predecessor closes anchor..target-1 and successor H/L anchor+1..target, without requiring anchor H/L or target close. When anchor==target, ATR instead observes the single anchor close (expected N+1/observed1 if eligible), with no H/L or TR and insufficient_history. Each band uses the last N scheduled epoch/grid slots with every required close eligible; missing/null/gap slots are never compacted. Width/position consume unrounded compatible mean/radius and centered-residual witnesses, never rounded published bounds. Bands have no RSI/ATR dependency. Selected compatible preparation sharing cannot introduce unrelated readiness edges.

All eight intraday IDs support batch snapshots only. Full supplied-history recalculation/replay is supported; update/restore/merge and persistent-worker operation remain unsupported. Audit supplied-core structure, top-K, continuous quotes/optional seed and bars/optional prior-close callbacks; missing optional reference cannot block unrelated valid outputs. Actual delivery absence, observed empty delivery, empty batch and unavailable output remain distinct. Preserve exact discovery/history/input/result/diagnostic bindings and existing default dispatcher/service/client/MCP boundaries.

## Evidence method and independent checks

Create a machine-readable acceptance inventory joining every public claim to original contract, independent fixture, actual source/reviewer receipt, current CI, installed archive/report and published channel. Independent rational/Decimal goldens, original arithmetic cases, selected-output subset/cancellation/quality/identity and temporal/unknown/future/revision/branch-isolation evidence remain distinct from optimized A/B parity comparisons. Do not reimplement numerical kernels to test their descriptions.

Reuse accepted numerical/installed evidence only after exact source/archive/harness equivalence or explicitly reviewed bounded applicability. Validate current both-OS base/combined wheel/selected-source SDist rebuild forms, closed source/metadata/install namespaces, exact optional/native skips, typing consumers and core fingerprints. New documentation checks cover UTF8/JSON, links, inventory joins, no contradictory current claim, no private paths and explicit scope. Run mandatory actual current CI; avoid new timing or broad repeated numerical runs for unchanged execution bytes.

## Performance claims and nonclaims

Keep preparation/indicator/band studies at their original source and workload identities. Do not sum their percentage improvements or infer an accelerated final worker. EQ140 frozen be4 completed486Jobs/6A48B/108warmups378retained; separate reviewdd6a5e66b2d81642f8bc35dbae81a1b8891c78f8845c68b4f9a5ad3d99ee38e4 accepted all48 nonwins and unchanged sequential fallback. Describe CPU, sampled concurrent RSS, serialized/pickled bytes and overlapping stage probes with their actual limits. No exclusive critical-path subtraction from overlapping probes.

Classify warmed direct-call code/import paths in EQ138/139 separately from EQ140 admitted compute and cold fresh-process end-to-end measurements. Two warmups plus seven retained calls inside an old direct harness do not establish a persistent warm-worker pool. Older raw warmup/timestamp/full SDK bodies were not retained; do not claim their redecoding. EQ140 retained actual warmup Jobs and result hashes, not raw SDK bodies. State unsupported warm/state classes explicitly. No fastest/live/SLA/Linux-speed/physical memory enforcement/durability claim.

Preserve recorded numerical-fixture corrections, generated-source closure failures, per-runner source-binding review, obsolete installed-dependency probes, HTTP502 attempt/retry and independent audit-tool corrections with actual dispositions. Historical failure is not a current failure after qualified correction, and a superseded pass is not current proof.

## Documentation and release work

Planned files: docs/stories/EQ-141_PLAN.md, docs/R17_ACCEPTANCE.md, docs/R17_ACCEPTANCE_INPUTS.json, R17 release/test/handoff/input documents, README, CHANGELOG, installation/compatibility/intraday API/example guidance as relevant, evidence-linked lessons/project knowledge/session handoff and public issue/epic/milestone records. Record no-impact decisions for formulas/schema/core39/default dispatch/executors/service integration/versioning. Keep historical checkpoints marked as historical; actual status comes from GitHub.

## Entry, exit and exact resume

Entry: all470–474 actual CLOSED/Done, relevant artifacts accessible/unexpired, exact current inputs available, concrete plan/public draft and completed separate pre-code review. Then Backlog -> Ready readback -> assigned In progress; one active story. Implementation audit -> Code review -> Test -> Ready to release only after final-head semantic/evidence review, findings disposition and actual current required checks. Guarded matched-head squash publication, actual main source/attribution/CI/channel/archive/readback and separate final acceptance precede Released readback, close/Done. Only then verify all six children Done and complete E25/milestone21 closure through actual aggregate gates.

After verified R17, prepare the concrete existing R18 E26/EQ142–146 handoff and supported separate-review route. The R17 local-review grant does not imply R18 authorization. R18 begins with exact output DAG/cost baselines, then compatible reuse, ready branches and bounded adaptive resources in dependency order. This packet starts no R18 story or new chat/automation and adds no later-release/provider/live scope.

## Preparation sequencing decision

Draft pre-code publication and conditional review may overlap predecessor CI because they change documentation only. This supersedes the local preparation draft's self-imposed wait-before-publication wording, without changing the EQ140 Done prerequisite for EQ141 Ready or starting a second implementation story. No local heavy build/timing overlaps; existing frozen sources and original dirty checkout remain untouched. Local preliminary review resolved explanatory scheduled-window and single-anchor ATR wording; changed public source still needs exact-head review.
