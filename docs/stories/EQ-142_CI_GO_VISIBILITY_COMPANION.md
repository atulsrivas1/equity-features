## EQ142GO01 failure-retention correction; review renewal pending

Separate automated local /root/r17_review found EQ142GO01 in the first working regression: unittest.subTest records a failed assertion and continues, so unconditional passed=True could remove the failed diagnostic root. The retained independent fault probe observed one failure, zero errors and root absent. Exact failed-source review SHA256 `8a37fcb3960b84b98b9fd065e392d535fc186ebc6e62726c3ca87a459ae128ea`, snapshots and raw evidence remain retained. Earlier positive tests do not clear this defect.

The same11 deterministic cases now run as fail-fast loops, leaving passed false on any assertion or error. An actual external author injection corrupted the completed payload: one expected unittest failure, zero errors and the failed root/BAD bytes retained. A separate uninjected success removed its actual owned root. Two-control receipt SHA256 `34f7ac7844f4e8d5b931e1c46eb805ba5dbd72acffbb70c6a712f42d6bae636f`; no child or product execution in that injection. Corrected original Windows four physical methods passed3.523s, no skips, source/owner/package map unchanged, receipt `e97b8e73addad2b774b82b4fbfcad431a41d4ef34780417a717488b7bd133e97`. Separate correction review and committed full both-platform archive/installed/currentCI qualification remain pending.

This test-only companion has no public calculation/API/formula/unit/timing/state/readiness/example/package/version/default change. Its design, validation evidence and release limitation are recorded here and in the linked issue/PR; no public runtime release is claimed. EQ142 remains In progress and EQ143-146 Backlog. No performance study or probe was run.

## Earlier checkpoints retained as history

## EQ142 GO companion working implementation and correctness

The prospective [review constraints](https://github.com/atulsrivas1/equity-features/issues/476#issuecomment-6282381714) were published before implementation. The fixed qualification helper now refuses every existing GO/GO.tmp entry through lexists, writes exactly two bytes to the exclusively created same-directory temporary, closes it successfully and then renames. The parent uses that helper. This is complete visibility within the source-owned single-writer test namespace; POSIX rename is not general concurrent-writer no-replace protection or power-loss durability. Failures propagate without retry or undo. Before-effect rename failure retains the temporary; after-effect/unknown outcome may retain a complete target instead.

Working Windows checks passed the original four collected physical crash methods in3.466s, with11 embedded deterministic publication subcases and unchanged helper/owner/package source guards. Actual installed five-package wheels came from committed f814 package bytes in a separate owned environment; the frozen baseline environment was preserved. Receipt SHA256 `a99a85ce1944de01f4f001e48af23dcf50aec20fa07cbf77d503b07e95f76f72`, log SHA256 `347e158940baf4c20b2bf34a99a906ee8f613eb6472b905708ee3709cb339da8`. These are working correctness checks, not fresh committed four-form archive/installed or current-CI acceptance. Separate implementation review is active. The four cut modes, exit91/PID/ownership/reopen/reconcile assertions and3s/4s/20s bounds are unchanged. The earlier hosted failure's exact cause remains unknown.

EQ142 remains In progress; EQ143-146 remain Backlog. Full-root/count-index/namespace/capacity/outer-envelope work resumes after this necessary qualification companion. No performance probe, study acceptance, calculation/package/default/resource/threshold/cohort change or R18 delivery is claimed.

## Earlier checkpoints retained as history

## Prospective separate precode review constraints

Separate automated local /root/r17_review accepted the prospective design with
constraints:26 static/source/proof/public joins, zero reviewer runtime tests.
Receipt SHA25630d64b9f79dea8fd70aeb7b6b254da1e58ca1ed93564357e0ec8b29bd023c8e2.
These constraints are recorded before implementation; acceptance is design only.

1. Visibility/no-overwrite statements apply to the source-owned single-writer
   local test namespace. Path.rename can replace a target on POSIX; an existence
   precheck is not atomic no-replace protection against a second writer. No
   general concurrent-writer, fsync or power-loss guarantee is proposed.
2. Refuse every pre-existing GO or fixed GO.tmp directory entry, including
   dangling symlinks, before opening the temporary. Preserve exclusive create,
   exact2byte write and successful close-before-rename ordering.
3. A before-effect rename failure leaves GO absent and available temporary
   evidence. An exception after effect or an unknown outcome may leave complete
   GO visible and no temporary. Propagate failure, retain the actual root and
   available evidence, never retry, undo, or invent no effect. The invariant is
   that any published GO is complete/closed, not that every failure has no effect.

The retained original race remains independently supported, while the old
hosted crash's cause remains unknown. Original source/PID ownership, four cut
modes and3s/4s/20s bounds remain. Implementation/regression and actual committed
fresh installed/archive both-platform/currentCI qualification are still pending.

### Original first proposal retained as history

# EQ142 necessary CI companion: complete GO visibility

EQ142 remains In progress in E26/R18. This is a narrow test-harness correction
needed for trustworthy current CI; it adds no ledger or calculation behavior,
release scope, performance threshold, timing study or deadline change.

The older canonical push39355900764 failed the installed Linux
sdist-declarations crash test: after_COMMIT expected child91 but observed1.
The same source's PR run completed successfully. The hosted child stderr is not
available in its retained parent log, so the exact hosted cause is unknown.

Independent read-only inspection found a concrete handshake race. The original
parent opens GO with xb, then writes b"go". Its original isolated child waits for
GO.is_file() and immediately requires those two bytes. Preemption after the
parent's open creates an empty visible file. A retained Windows reproduction
ran the unmodified original entry under its original reviewed owned-process
helper, held that legal writer interleaving, and observed actual exit1 with
ValueError: fixed GO; ownership closed and original source remained unchanged.
This proves the race, not the cause of the older hosted failure. An initial
diagnostic invocation omitted the owner's required parent -I and was refused
before any child existed; it is separately retained, not a reproduction pass.

The contract for this source-owned single-writer test handshake is:

    GO visible => exact payload b"go" (2bytes), writer handle already closed

Proposed implementation, before code:

1. Add a fixed publish_go(root) helper alongside the existing entry witness
   publisher. Refuse an existing GO, exclusively create same-directory GO.tmp,
   require its write of the fixed2bytes, close successfully, then rename to GO.
   Errors retain the temporary and original test root; no retry or overwrite
   recovery. This is visibility ordering, not fsync/power-loss durability.
2. Have the parent exercise call that reviewed helper instead of directly
   exposing GO before its write. Keep original child PID/source binding,
   namespace ownership, four cut modes, exit91 proof, reopen/reconcile checks,
   fixed3s GO /4s owner observations and20s diagnostic bound unchanged.
3. Add deterministic subcase regressions inside an existing crash-test method,
   preserving the four collected crash methods: target absent during open/write
   and before close, exact payload only after rename; existing-target refusal;
   short-write/close/rename failure cannot expose a valid target. Verify actual
   parent use in source review and execute all original four physical modes.
4. Obtain separate source/reproduction/regression review. Freeze a real committed
   candidate, run the original source-closed fresh installed wheel/sdist and
   declaration variants on Windows/Linux, with unchanged accepted archive
   expectations. Require current CI and final source/artifact readback; retain
   actual failures. No current green gate is inferred from an older green run.

Implement in the active EQ142 branch as a necessary companion, not an unrelated
product change. Track the finding and its independent limitation alongside the
current issue/PR and continuity. Do not claim the historical hosted error fixed
without its missing raw child evidence; report the proven protocol defect and
new candidate validation distinctly. Worker source/calculation/defaults and the
R18 V7 study/capacity/cohort/overhead policies remain unchanged.
