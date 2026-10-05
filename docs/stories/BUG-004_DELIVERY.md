# BUG-004 verified implementation delivery

PR171/head `9e78e14a8fe2572a262083af4bd207af8f84199c`, implementation main
`793a188acba054ba227a61d181897ae90236c149`, experimental pair0.0.2a11. Saved-state float conversion overflow
now raises ContractError(INVALID_SCHEMA), preserving its cause. State schema2,
mathematics and exact implementation-version/no-migration policy are unchanged.
[Plan](BUG-004_PLAN.md); [state API](../api/INCREMENTAL.md).

Three independent regressions exercise rehashed positive/negative/huge hex
exponents, inf/nan/malformed syntax, caller-state/envelope immutability, original
OverflowError cause and valid nonzero finite exact hex roundtrip/continuation.
380units/123references/strict26files/purity38negative10positive/import/registry/
compatibility/license/UTF8 pass. Four archives reproduce and pass inspection;
local fresh wheel/sdist pairs each380tests/eleven examples pass. Six final-head
checks and main bothOS package/documentation workflows must be linked on issue163.
Author self-review+CI; no independent human or completed hosted review claimed.

Both actual main OS bundles were downloaded and checked for source commit,
source_dirty=false, epoch, all four archive SHA256s, contents, license and typing.
FOUR fresh wheel/sdist pair installations each380tests/eleven examples passed on
Windows CPython3.12.10, NumPy2.2.6/PyArrow20.0.0. Linux execution is separately
established by Linux CI; local Windows installs of Linux-built universal archives
do not claim Linux local execution. Experimental main Actions channel only.

Final receipt publication/main checks and actual bothOS archive equality remain
administrative closure gates on issue163; this receipt does not infer them from
source merge. Earlier failed/cancelled/queued attempts remain in continuity and
issue comments. Installed evidence may be reused only for identical package bytes.
Owner transferred remaining repair delivery to this R2 session; after actual
BUG003/004 Done and GOV010 publication gates, follow the authorized R2 package.
No R3 feature restart, provider/private data, stable/PyPI/tag or account change.

- [foundation-793a188acba054ba227a61d181897ae90236c149-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37376045409/artifacts/11372050924); expires `2026-11-04T21:28:51Z`; Linux CPython3.12.14.
- [foundation-793a188acba054ba227a61d181897ae90236c149-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37376045409/artifacts/11371602243); expires `2026-11-04T21:29:41Z`; Windows CPython3.12.10.

| OS | Archive | SHA256 |
| --- | --- | --- |
| Linux | equity_feature_contracts-0.0.2a11-py3-none-any.whl | `0e4d71ea171d698e1fb6f8c1123e90a5e5e54c37eb632bcd5b7efce2d65c0991` |
| Linux | equity_feature_contracts-0.0.2a11.tar.gz | `cbf306922b041f79b3af4867c332393747236f12b8c18a256ad1f11b17227a04` |
| Linux | equity_features-0.0.2a11-py3-none-any.whl | `b00e4f11c98be9f4949fee1c5fca418b94362ce7a6c3be4ee387b4ea26dbe27a` |
| Linux | equity_features-0.0.2a11.tar.gz | `c19d3ad6f024826fb9ce2ee6285054f5804f0380ce32efd7b74c28a8f0c670df` |
| Windows | equity_feature_contracts-0.0.2a11-py3-none-any.whl | `8a8b2f759a46c764f69ca6ed6574bc984b453e35e0e02625cc56fc3a374b0b73` |
| Windows | equity_feature_contracts-0.0.2a11.tar.gz | `e1657afe20181265dec85f3333f5fa00a8fdc6c19466538520708684b2b83fa5` |
| Windows | equity_features-0.0.2a11-py3-none-any.whl | `8444d9b2d3839067947dc7c179548ddb562ae07865ba49a33bee4cd130b069fb` |
| Windows | equity_features-0.0.2a11.tar.gz | `b67d7134377d9d942ae6eccf686691ee0be4d641c27486fccd6ef09682c758a9` |
