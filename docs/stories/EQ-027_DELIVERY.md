# EQ027 verified experimental implementation delivery

Issue [#32](https://github.com/atulsrivas1/equity-features/issues/32), E05/R2;
[PR176](https://github.com/atulsrivas1/equity-features/pull/176).
Pre-code plan2b907e0 precedes calculation code; [plan](EQ-027_PLAN.md).
Final corrected head `27d9ff68dc30bd0bb8301c6326e36e1d3c0c0a64` passed all SIX
checks before exact-head-guarded merge to main `1896ff274ba1abfbb313829d277133a9b86d3ba7`; entire published tree
matches final head. Main [docs37383010352](https://github.com/atulsrivas1/equity-features/actions/runs/37383010352)
and [Foundation37383010306](https://github.com/atulsrivas1/equity-features/actions/runs/37383010306)
Windows/Linux CI succeeded.

Pair0.0.3a1 implements batch history.return/prior_high/prior_low with exact governed
membership, owned context/slot certificates, independent readiness and bounded
original evidence. [API](../api/HISTORY.md), [example](../../examples/history_windows.py).
39IDs retained;26batch/23session update/restore/22conditional merge. History state
modes remain false. New HistoryContext schema1; existing input/config/result schema1
and accumulator schema2 unchanged. Exact-version state/registry snapshot digest
rules remain, no migration or hidden adjustment/source/calendar lookup.

438units include16independent new history API cases: all default horizons/windows,
5/21/122/103 goldens, missing middle despite valid endpoints/finite recovery,
independent fields, prior-only target/future exclusion, C/K/E/reconstruction,
wide precision, source/grid/certificate/unit/policy failures and truthful modes.
123formula references, strict32files (30CI targets plus two typed new examples),
purity38negative10positive/import/registry/license/compatibility/UTF8/local links
pass. Repeated4archives inspected; local wheel/sdist pairs each438tests/thirteen
examples pass with clean head manifest. Initial8ea565c source tests passed but
installed canonical example/all4package CI jobs failed on stale total23batch
expectation. Corrected tutorial checks session scope and clears copied custom
metadata flags; independent catalog tests verify26total. Failures/rework preserved
in continuity and issue, not counted as final evidence.

Both actual main bundles downloaded and exact source/source_dirty=false/epoch
1700000000/all4SHA256/content/license/typing verified. FOUR fresh wheel/sdist pair
installs each438tests/thirteen examples pass on Windows CPython3.12.10 with pinned
NumPy2.2.6/PyArrow20.0.0. Linux native execution is CI evidence; local Windows
installs of Linux-built universal archives do not claim local Linux execution.

Author self-review+CI; no independent human/hosted review. Experimental main
Actions channel only; no provider/private-data/throughput/stable/tag/PyPI claim.
Final receipt documentation/head/main and bothOS actual archive equality remain
before Done; source merge alone is not closure. Reuse installed evidence ONLY for
identical package bytes. After accepted Done pull EQ028 under R2; R3 stays paused.

- [foundation-1896ff274ba1abfbb313829d277133a9b86d3ba7-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37383010306/artifacts/11376127182); expires `2026-11-04T22:33:03Z`; Windows CPython3.12.10.
- [foundation-1896ff274ba1abfbb313829d277133a9b86d3ba7-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37383010306/artifacts/11374853456); expires `2026-11-04T22:32:06Z`; Linux CPython3.12.14.

| OS | Archive | SHA256 |
| --- | --- | --- |
| Windows | equity_feature_contracts-0.0.3a1-py3-none-any.whl | `de7ee609255bb12aff33d005b3897ca816415c1631f2ff2942ff40c669b40771` |
| Windows | equity_feature_contracts-0.0.3a1.tar.gz | `3336163816337baeaa41f079ccfe767082b19f4b8ce8e36c4d3ffaed7fba84de` |
| Windows | equity_features-0.0.3a1-py3-none-any.whl | `aa44fa4621f6a973dabe4bcd7121bcd311a6477268c4c3bf0f97e1b06789c9d6` |
| Windows | equity_features-0.0.3a1.tar.gz | `a4eb984523fe0eb0e914ebd48a1a0da038e2cbdca2f263cdf69973fdadb564f2` |
| Linux | equity_feature_contracts-0.0.3a1-py3-none-any.whl | `713e2cad1e93136b0757be3740c20ffc860b088a4d18c7f2581018dae7a4001e` |
| Linux | equity_feature_contracts-0.0.3a1.tar.gz | `74aca0c0c8eb6aa391fc9334a9e812d6d2ca7c9d0bf9c2aa4f5d462fd664b4fd` |
| Linux | equity_features-0.0.3a1-py3-none-any.whl | `5f13c58380ed593bdbfe3f16bebe9ccd04237373eb6615dfef98ec91488fb7c5` |
| Linux | equity_features-0.0.3a1.tar.gz | `08db65cd9cb02732d552bfb30c2af31c8909cc905c2d051864f0ad992444cb65` |
