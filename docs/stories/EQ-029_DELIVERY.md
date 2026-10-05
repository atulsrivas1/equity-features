# EQ029 verified experimental implementation delivery

Issue [#34](https://github.com/atulsrivas1/equity-features/issues/34), E05/R2;
[PR180](https://github.com/atulsrivas1/equity-features/pull/180).
Pre-code plan dc2bba6 precedes source; [plan](EQ-029_PLAN.md).
Final head `d1b552cfd77711a07815d4b803c7dd9fbde1bb80` passed all SIX checks before
exact-head-guarded merge to main `63118826ef99a0fbce808d1fece0b7d19ed15283`; entire published tree equals head.
Main [docs37387090395](https://github.com/atulsrivas1/equity-features/actions/runs/37387090395)
and [Foundation37387090399](https://github.com/atulsrivas1/equity-features/actions/runs/37387090399)
Windows/Linux succeeded.

Pair0.0.3a3 implements batch Wilder RSI/ATR under explicit close/TRanchors, exact
seeds and full epoch admission. Normalized RSI proportion/total magnitude avoids
nonneutral flat underflow; ATR requires preceding close and high/low while target
current close is optional. [API](../api/HISTORY.md),
[example](../../examples/history_recursive.py).30batch,23session update/restore,
22conditional merge;39mathematical definitions unchanged. All history state modes
false. Existing context/config/results schema1/sessionstate2 remain; exact-version
state/registry snapshots need caller replay/rebuild, no migration. Transient batch
prefix/TR construction costs are explicit; bounded scalar recurrence is neither
public state capability nor total-input constant-memory/performance claim.

472units include18independent new production API cases: hand4700/57 and122/9,
default14/Decimal references, gain/loss/flat seeds,20,001nonneutral flat continuation
and later movements, first movement after flat seed, ATR1/mandatory previous close/
no fallback, zeroTR, targetclose/precedinghighlow independence, field/gap/epoch/
warm-up/period/type guards, future mutation/knowledge/reconstruction/bounded original
evidence, scaled wide oscillations, action admission and unsupported state modes.
123formula references/strict35files (31CI targets plus four typed new examples),
pure boundary38negative10positive/import/registry/license/compatibility/public UTF8/
planning/lifecycle pass. No new broken local links; inherited R1 structure.py link
is separately recorded. Initial variable tuple/index typing and malformed action
fixture missing adjustment anchor/incorrect policy args were corrected before
final qualification, not counted as passed evidence.

Repeat4archives/content inspection and BOTH local fresh wheel/sdist pairs each
472tests/fifteen examples pass with clean final-head manifest/epoch1700000000.
Both actual main bundles downloaded; exact commit/source_dirty=false/epoch/allfour
SHA256/archive contents/license/typing verified. FOUR fresh Windows wheel/sdist
pair installs of bothOS universal archives each472tests/fifteen examples pass,
CPython3.12.10/NumPy2.2.6/PyArrow20.0.0. Linux-native execution is CI evidence;
Windows-local installs do not imply local Linux execution.

Author Codex self-review+CI, no independent human/hosted review; hosted activation
deferred. Experimental main Actions channel only; no source/provider/private-copy/
throughput/history-state/stable/tag/PyPI claim. Final receipt publication/head/main/
actual bothOS archive equality remains before Done. Reuse installed execution ONLY
for identical bytes. Then pull EQ030; R3 remains paused.

- [foundation-63118826ef99a0fbce808d1fece0b7d19ed15283-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37387090399/artifacts/11379357229); expires `2026-11-04T23:13:58Z`; Windows CPython3.12.10.
- [foundation-63118826ef99a0fbce808d1fece0b7d19ed15283-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37387090399/artifacts/11379031886); expires `2026-11-04T23:12:43Z`; Linux CPython3.12.14.

| OS | Archive | SHA256 |
| --- | --- | --- |
| Windows | equity_feature_contracts-0.0.3a3-py3-none-any.whl | `1deaa7511c24e722d6a67a484c3871fc44a56dcee0d2f47f80b7b7aee0fe746e` |
| Windows | equity_feature_contracts-0.0.3a3.tar.gz | `9f16dbccbf6c8e9c3c7198d48874d60083deb78a73cfa39ed3d00365e4e2c0b3` |
| Windows | equity_features-0.0.3a3-py3-none-any.whl | `25ca56bbf715569212145a1a297d72e67ebe38e23da71d272685a6995fa009c5` |
| Windows | equity_features-0.0.3a3.tar.gz | `926ab6b61931a23ea0bb7168a1ce48b0c9fcc9cc53d97ebe5794e1038e5dc2c4` |
| Linux | equity_feature_contracts-0.0.3a3-py3-none-any.whl | `b506282166745c3b06108976a10260cfbeb3db7b138ca0e79867e66ea189cee4` |
| Linux | equity_feature_contracts-0.0.3a3.tar.gz | `87e0f64bd4b85a43d41d7c602009ccfa59dbd27bebbf185e077ce643d4f4dcc0` |
| Linux | equity_features-0.0.3a3-py3-none-any.whl | `0a6be4173d0960905bf17bab1ca47d20941f251f053f6829c97fc6ad1828cc7e` |
| Linux | equity_features-0.0.3a3.tar.gz | `05107f167ad8e1c57fe959575798994dd528805ead17a73c475887b6897abe77` |
