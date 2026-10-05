# EQ030 verified experimental implementation delivery

Issue [#35](https://github.com/atulsrivas1/equity-features/issues/35), E05/R2;
[PR182](https://github.com/atulsrivas1/equity-features/pull/182).
Pre-code plan7bfdfe4 precedes source; [plan](EQ-030_PLAN.md).
Final head `363b99ffa1e352a2b6e16a9884a9afd4ec3f0d35` passed all SIX checks before
exact-head-guarded merge to main `316215250387c8876a85326e41f14765b1620580`; entire published tree equals head.
Main [docs37389113015](https://github.com/atulsrivas1/equity-features/actions/runs/37389113015)
and [Foundation37389112975](https://github.com/atulsrivas1/equity-features/actions/runs/37389112975)
Windows/Linux succeeded.

Pair0.0.3a4 implements batch centered sample simple-return volatility over exactly
Nreturns/N+1governed closes with denominatorN-1 and explicit positive
annualization_factor default1. Exact transient fractions/80-digit square root
avoid cancellation and preserve tiny positive near-int64-limit variance; no
clamp, RMS, population/log-return substitution or implicit252. [API](../api/HISTORY.md),
[example](../../examples/history_volatility.py).31batch/all8history,23session
update/restore22conditional merge;39mathematical definitions unchanged. All history
state modes false. Existing schemas remain; exact-version state/registry snapshots
require caller replay/rebuild. Transient finite rational costs are explicit,
not a public accumulator/constant total-memory/throughput claim.

485units include13independent new production API cases: hand476449/44791488,
A4/default1/explicit1/declared252, centered/RMS/population distinctions, flat0 versus
missing, strict-positive ~1e-38int64-limit precision beyond absolute tolerance,
scale/unit guards, largest factor/price ratios, missing-middle/finite recovery,
future mutation/bounded evidence, completion/knowledge/reconstruction, warm-up/
fields/period/factor/mixed convention guards, action/source identity and false modes.
123formula references/strict37files (32CI targets plus five typed new examples),
purity38negative10positive/import/registry/license/compatibility/public UTF8/
planning/lifecycle pass. No new broken local links; inherited historical R1 link
remains separately recorded. Initial Fraction-sum inference/project-points ID typo
were corrected before qualification, no failed evidence counted.

Repeat4archives/content inspection and BOTH local fresh wheel/sdist pairs each
485tests/sixteen examples pass with clean final-head manifest/epoch1700000000.
Both actual main bundles downloaded, exact source/source_dirty=false/epoch/allfour
SHA256/archive contents/license/typing verified. FOUR fresh Windows wheel/sdist
pair installs of bothOS universal archives each485tests/sixteen examples pass,
CPython3.12.10/NumPy2.2.6/PyArrow20.0.0. Linux-native execution is CI evidence;
Windows-local installs do not imply local Linux execution.

Author Codex self-review+CI, no independent human/hosted review; hosted activation
deferred. Experimental main Actions channel only; no source/provider/private copy/
performance/history state/stable/tag/PyPI claim. Final receipt publication/head/main/
actual bothOS archive equality remains before Done. Reuse installed execution only
for identical bytes. Then pull EQ031; R3 remains paused.

- [foundation-316215250387c8876a85326e41f14765b1620580-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37389112975/artifacts/11380750548); expires `2026-11-04T23:33:49Z`; Linux CPython3.12.14.
- [foundation-316215250387c8876a85326e41f14765b1620580-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37389112975/artifacts/11379594537); expires `2026-11-04T23:35:07Z`; Windows CPython3.12.10.

| OS | Archive | SHA256 |
| --- | --- | --- |
| Linux | equity_feature_contracts-0.0.3a4-py3-none-any.whl | `a3189e4532c42e7d5cb777af9fe166266049c4b469fdec7d967f3996421fc51b` |
| Linux | equity_feature_contracts-0.0.3a4.tar.gz | `f650abcd0330181d72e55c6981f1babb08aea687de01573c78b5a6175e69d179` |
| Linux | equity_features-0.0.3a4-py3-none-any.whl | `a3d93bcf598a3d89bead480b2a6e7a0f6374dc7497a18656650171811eec7da6` |
| Linux | equity_features-0.0.3a4.tar.gz | `1270b961c1e5daf17ee1b81544af0aa864d43e6299d30aaacb224fc54363e532` |
| Windows | equity_feature_contracts-0.0.3a4-py3-none-any.whl | `cf8b99eba4de100df528be8b33311ef246c71dad888716db9a19f832b5f08c9e` |
| Windows | equity_feature_contracts-0.0.3a4.tar.gz | `529a10df2e8e1e6e379a629967d940f2e194623dacce918dbecf6afb95a07145` |
| Windows | equity_features-0.0.3a4-py3-none-any.whl | `880182b765c22aabd1323721cdcc80a832e91d6cd08fceb231d19560bb26a532` |
| Windows | equity_features-0.0.3a4.tar.gz | `14b532de8fc0823a829411d791172e84ca1c415c7ac259db915717da7d5edc0b` |
