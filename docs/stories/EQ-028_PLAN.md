# EQ-028 SMA/EMA — pre-code draft

Issue #33; E05/R2;8 provisional points. Requires delivered EQ027 typed history
context and repairs/GOV010. No implementation or Ready claim in this draft.

SMA uses exactly N complete closes; EMA uses SMA seed at explicit supplied close
anchor and alpha=2/(N+1), then every governed slot through target. Defaults
SMA20/50/200 and EMA20. Period1 equals supplied close. Anchor/config/action/source
revisions are part of result/state identity. No auto-reseed after a gap.

Extend compute_history for these two IDs using the EQ027 public context and
single-period ConfigSpec. For EMA require initialization_anchor and window count N;
dependency membership is anchor through target, not merely lastN closes. Final
Float64 acceptance rtol/atol1e-12; integer SMA sums use transient wide checked
arithmetic and EMA uses bounded binary64 recurrence after exact rational seed.
No retained recursive Fraction denominator or raw-moment variance.

Qualify a distinct HistoryAccumulator for explicitly selected history IDs only.
It accepts ordered caller-supplied single-slot canonical daily batches and supplied
coverage/session identity. Retain at most window+context prices for finite windows,
bounded EMA seed sum/count/value after initialization and fixed binding metadata.
HistoryState is immutable schema1 and exact implementation/version/config/source/
anchor/action/ordinal bound. export/restore is in-memory only with typed malformed
state rejection; no persistence, arbitrary merge or session accumulator exposure.
Once a known recursive gap occurs, later updates cannot repair it without new
explicit epoch/replay. Finite window readiness recovers when the required slots
are complete. Reject backwards cutoffs, changed basis/anchor/source revision,
repeated/out-of-order slots and incompatible restored states atomically.

Independent actual-API tests: period3 SMA365/3 and anchor0 EMA975/8 from supplied
six-close golden; periods1/defaults; different legitimate anchors; missing seed
and continuation; finite window recovery versus permanently broken EMA; target
completion/knowledge; maximum-int64 wide sum; chunk/empty boundary/restored parity
against independent high-precision recurrence; bounded retained state across long
synthetic histories; mutation/identity/malformed/atomic rejection tests.

Document HISTORY/state API, seeds/anchors/gaps/precision, truthful per-ID modes,
installed synthetic example, changelog and continuity alongside code. Pre-code
plan commit precedes implementation. All required local/repeat build/fresh install,
author self-review/exact-head CI, published main/bothOS CI/actual bundle/four
installed-pair receipt gates precede eight-stage Released/Done. Source merge alone
is not acceptance.
