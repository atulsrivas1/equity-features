# EQ028 moving averages delivery record

Issue #33; E05 #31; R2 milestone3. Pair0.0.3a2 source is under qualification,
not yet accepted delivery. [Pre-code plan](EQ-028_PLAN.md) commit75c7b68 preceded
implementation; [API](../api/HISTORY.md) documents exact SMA, anchored EMA, gaps,
precision, supplied exact witness and truthful batch-only modes.

Sixteen new independent production API cases and all438 prior cases pass locally
(454 total), including all defaults, hand goldens365/3 and975/8, independent
window/epoch counts, seed/warm-up, gaps/finite recovery, null/absent inputs, anchor
identity, future mutation, knowledge/reconstruction, wide/scaled long recurrence,
and exact SMA one-tick/tie/malformed/unavailable guards. Strict33targets (30package/adapter plus three typed new examples) pass; pure boundary38negative10positive fixtures pass. First local checks
found and corrected recurrence typing plus stale unsupported-SMA/capability test
expectations; these failing attempts are not final evidence.

Author Codex self-review plus CI; hosted reviewer activation remains deferred.
No independent human/hosted review or provider/performance/state/stable/tag/PyPI
claim. Remaining: all reference/import/registry/license/compatibility/docs/example
checks, clean exact-head repeat build and installed pairs, SIX exact-head PR checks,
guarded merge/exact published tree/main docs/bothOS CI/actual bundles/four installed
pairs, followed by final receipt publication and actual main byte equality. No
source merge alone establishes Done. R3 remains paused.

Pre-acceptance docs check also caught and corrected Windows-default encoding of
the new changelog em dash on ce44fae; corrected UTF8/planning/lifecycle checks pass.
No new broken local links; an inherited R1 historical link remains separately
identified in continuity. ce44fae is superseded, not final evidence.
