# Code, story, epic and release synchronization audit

[GOV-016 #331](https://github.com/atulsrivas1/equity-features/issues/331). Captured October 7, 2026, America/New_York. This is a source/metadata audit against frozen public main snapshots and live canonical issue/Project records. It does not repeat full numerical, worker, native-installation, artifact-download or private-source qualification. The active R5 owner retains delivery.

## Findings and corrections

| Finding | Evidence | Correction |
| --- | --- | --- |
| E08 unchecked accepted children | EQ057–063 are Closed/Project Done; E08 #64 still listed them unchecked | Reconcile only accepted child checkboxes. Leave EQ064 unchecked while Released, and EQ065/066 Backlog; E08/R5 remain open. |
| Structured scope and CI omit five existing stories | All 134 active EQ issues exist; BACKLOG has 129 structured rows and documentation CI requires 129. Existing C1 plan/epic/R14 already contains EQ131–135. | Add their five rows and R14 release-map row; require all134 in documentation CI. Scope/dependencies remain those already approved in C1. |
| Public entry points describe obsolete worker skeleton/R4.1 activity | README and dashboard conflict with current worker0.1.0a9 exports and accepted R4.1/EQ063 issue evidence | Link this dated synchronization capture; retain historical snapshots and original receipts. |
| Local summary differs from delivered main | The owner's local CURRENT_STATE is untracked and the checkout has older history and uncommitted knowledge edits | Preserve those files. Prepare corrections in a separate branch from inspected public main. No local source is treated as the current delivered implementation. |

## Lifecycle and release reconciliation

All134 active EQ issues have matching issue state and Project lifecycle; retired EQ094 is deliberately closed outside active delivery. All129 previously table-listed stories have the expected milestone. EQ131–135 all belong to R14. Closed milestones R0/R1/R2/R3/R4/R4.1 have zero open issues; later milestones remain open. No premature epic/milestone closure was found. E08 is correctly In progress; its child checklist needs the correction above.

At capture, EQ057–063 are Done and EQ064 is Released/OPEN, awaiting final evidence PR330 and companion PR21 qualification/publication/readback under the R5 owner. EQ065–066 are Backlog. Worker code at main includes the released catalog implementation; source presence does not satisfy remaining acceptance. The [latest EQ063 acceptance](https://github.com/atulsrivas1/equity-features/issues/71#issuecomment-6049783551) supersedes older pending text. [EQ064](https://github.com/atulsrivas1/equity-features/issues/72) remains the live acceptance authority.

## Inspected code and validation

Exact snapshots: canonical `963bf767d7088112e9b22f2628c1fc46fd9217da`; I/O `4603c6e50331a5e8a82b13b62a0cdd5ffaa0e4bf`; workers `c483ba293a17be8f22c12e6b04a0f57ca100bdbd`. The [machine-readable capture](SYNCHRONIZATION_AUDIT_EVIDENCE.json) records all134 issue/status/release mappings, package identities and receipt checks.

Core contracts/features versions agree at0.0.4a4. Worker version metadata and export agree at0.1.0a9; dependencies point to the actual core0.0.4a4 and I/O SDK0.1.0a2. I/O contracts/SDK are0.1.0a2, DuckDB source0.1.0a8, Parquet sink0.1.0a1 and DuckDB sink0.1.0a0. These are distinct component releases, not one shared version number.

Registry verification passed all39 IDs, formula links and declared capability parity:39 batch,23 update/restore,22 conditional merge. Source import/metadata isolation, Apache/distribution naming and boundary policy checks passed, including42 negative/10 positive fixtures. All123 independent mathematical reference checks passed:17 session,26 quote,31 history,26 context,23 timing. These reference checks do not replace the full production test suite.

Current worker files match all46 source hashes in each Windows/Linux EQ064 source-receipt mapping. The receipt links prior qualification of real sinks, claims and catalog tests; this audit checked source-byte parity, not downloaded native archive bytes or rerun worker tests. Existing failed/superseded candidates remain excluded. No new correctness, throughput, peak-memory, source/PIT, pilot or production-readiness claim follows.

## Publication and continuity

This governance change changes documentation/planning coverage only. Public lifecycle metadata corrections are separately read back. The draft PR requires applicable completed separate final-head review, current CI and actual default-branch publication/readback before GOV016 can progress through Test, Ready to release, Released and Done. No completed review or released documentation is claimed by preparing this branch.

Resume with current Project/issue/PR heads. Preserve the R5 owner's final acceptance work, verify this audit's final review/checks, publish/read back the scoped corrections, then record GOV016 acceptance. Do not close EQ064, E08 or R5 from this audit.
