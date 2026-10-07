# R4.1 post-delivery review — October 7, 2026

Owner requested review before preparing the R5 execution handoff. Historical R4.1 acceptance is verified; a newly reproduced P2 defect blocks current worker readiness. Canonical [BUG-005 #301](https://github.com/atulsrivas1/equity-features/issues/301) owns repair in the I/O repository. No runtime fix is implemented by this report.

## Finding: incoherent Parquet completion observation

Accepted I/O main `318ecbbc551f8ad57eb4c4359fe9c3177390f2e1` equals the reviewed tree `b7f7470928de0421e74a45e7a73c2746f99964c0`. In [sink.py](https://github.com/atulsrivas1/equity-feature-io/blob/318ecbbc551f8ad57eb4c4359fe9c3177390f2e1/packages/parquet/src/equity_feature_parquet/sink.py#L211), completion lookup reads reservation before completion. A cooperating writer can commit between those reads. The new completion then conflicts with the reader's absent or old attempt snapshot and raises CORRUPTION despite intact committed storage. The related reservation existence observation at lines183–188 also needs coherent handling.

Separate local automated reviewer `/root/io_architecture_review` reproduced both ABSENT and ABORTED predecessors; the parent independently reran the probe. Each racing lookup returned CORRUPTION; the next returned COMMITTED and full result readback matched independent synthetic facts. The probe only schedules real publication after the reader's reservation read, without altering stored records. This can incorrectly terminate worker receipt recovery. No data loss or numerical corruption was demonstrated.

The documented factual lookup/complete-reader contract and existing live foreign-instance lookup test support this cooperating-reader scenario. DuckDB comparison returned BUSY during foreign writer ownership, then COMMITTED with complete readback after commitment; no equivalent defect was established there.

Repair snapshot coherence or use bounded revalidation/appropriate transient outcomes while retaining genuine stable mismatch detection. BUG-005 requires deterministic first-publication, aborted/staging retry and reservation-existence regressions, true corruption negatives, replay/conflict/ownership parity, appropriate process/installed-platform qualification, separate applicable final-head review and actual publication/readback. No formulas or source-data semantics need changing.

## Verified delivery and selected checks

- Live Project: EQ121–130 and E18/E19 Done; canonical issues closed. R4.1 milestone15 closed with zero open and13 closed entries, including epics and a PR.
- Current core `ecccbffd9ff6dcad0228a62dad0daa74aac20c1f`, I/O `318ecbbc551f8ad57eb4c4359fe9c3177390f2e1`, workers `3423c64d637885698f4ba471b2f4c969cd8b318d` match recorded reviewed trees. PR300 checks passed; examined current main producer runs succeeded.
- Sixteen preserved actual server ZIPs independently hash against live GitHub metadata, contain202 files/146 package archive files and remain unexpired. Counts include repeated dependencies/historical candidates. This audit does not execute those installed archives again.
- Existing Windows source/venv checks: 48 foundation,94 DuckDB-source,6 composition,17 Parquet physical,18 DuckDB-sink physical tests passed; foundation independently repeated. Passing suites did not cover the reproduced interleaving. Pip check passed.
- Calculation packages remain independent; workers exports only its version. Runtime workers/task claims/scheduling/retry/catalog remain R5 scope.

Reviewers: parent `/root` and separate local automated `/root/io_architecture_review`. This is neither human nor hosted review. No fresh native Linux/clean-install/process-suite/private-data qualification was performed in this post-delivery review. Original installed/native/private acceptance receipts retain their exact version-bound scope; they do not clear the new defect.

## Current next step

BUG-005 is Ready, provisionally3points, E08/R5 prerequisite. EQ057 returns Ready -> Backlog with explicit repair dependency. Historical R4.1 closure remains preserved; current readiness is superseded. Fix and verify the I/O repair before restoring EQ057 Ready and dispatching R5. [Prepared R5 resume](R5_AUTONOMOUS_HANDOFF.md) must be refreshed with the corrected package/version/artifact/readback and applicable review policy. No R5 implementation/new session is started by this review.
