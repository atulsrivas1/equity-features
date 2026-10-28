# Coordinated pre-release bump: contracts a4 to a5, features a5 to a6 - October 28, 2026

PO ruling `work/po-rulings-e1e2-followups-2026-10-28.md` item 1. This is a pre-release label move only: no tag, no publish,
no release claim. Paired changes: equity-feature-io and equity-feature-workers (see their PRs).

## Single source

`tools/_versions.py` is the one table of package versions for the tools, examples and builders of this repository.
`tools/verify_versions.py` (run by `tools/pre_merge_check.py`) fails if any live place disagrees: package `pyproject.toml`
versions and exact pins, the `__version__` of contracts, features, intraday and explanations, the expected-contracts constant
of evidence, labels and strategies (`_CONTRACTS_VERSION`), the admitted producer versions of explanations, and the external
consumer example pins. Installed packages cannot import `tools/`, so each of those packages keeps exactly one constant,
which the check ties to the table. A future bump edits the table, the `pyproject.toml` files and those constants, then runs the check.

## Packages moved (content changed since the last bump of that package)

| Package | From | To | Why |
| --- | --- | --- | --- |
| equity-feature-contracts | 0.0.4a4 | 0.0.4a5 | #734 changed `inputs`/`results` (rank-aware `TopKTrades`, governed-history window) since its last bump |
| equity-features | 0.0.4a5 | 0.0.4a6 | 19 source commits since the bump (EF3 R5, EF4 producers, #734) |
| equity-features-intraday | 0.1.0a3 | 0.1.0a4 | 6 source commits since the bump (EF2/EF3/EF4 producers, #734); catalog digests carry the package version |
| equity-feature-explanations | 0.1.0a2 | 0.1.0a3 | admitted producer backend versions widened to include 0.0.4a6 (real calculators emit the features version) |

Packages whose only change is the exact contracts pin or a documentation version string keep their version and follow the pin:
agent-evidence, agent-ledger, conformance, continuous, diagnostics, evidence, labels, strategies. Their wheels now declare
`equity-feature-contracts==0.0.4a5`; evidence encodes the contracts version in its canonical content (`contracts_version`), so its content bytes and digests change with the contracts label, and labels and strategies admit exactly that contracts version in their codecs; their own versions stay.
This is a decision for the PO to confirm: a stricter reading would also move evidence (a2 to a3) and cascade through everything that pins it.

## Left as history (not live)

Release receipts and records under `docs/stories`, `docs/releases`, `docs/reviews`, `docs/benchmarks`, `docs/ef2` to `docs/ef3`
qualification records, CHANGELOG and BUILD_DELIVERY history, the quickstart channel (`tools/quickstart_probe.py`,
`tools/test_quickstart_verifier.py`: they probe the already published core pair), `tools/build_evidence_evaluation.py`
(frozen EQ-117 inputs), declared-environment strings in examples and tests (`PackageVersion('equity-features', ...)` and
similar caller declarations, which are data, not the installed version), and the "wrong version" negative mutations in tests.

## Regenerated golden fixtures and oracles (version-derived fields only)

Method: labels substituted byte for byte (`"backend_version": "0.0.4a5"` to `a6`, `"canonical_package_version": "0.0.4a4"` to
`a5`, `"contracts_version":"0.0.4a4"` to `a5` in the typed content oracles), file hashes recomputed, and for the explanation
oracles the production encoder output was diffed against the old bytes with every differing leaf required to be a digest
(content digests re-derived as SHA-256 of the canonical content bytes, receipt digest as SHA-256 of the receipt encoding).
Numerical expectations were not touched. The same bytes are used in equity-feature-io `tests/ef1` and equity-feature-workers
`tests/ef1_*_oracle.json` (identical SHA-256 in all three repositories).

| File | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `docs/ef1/OBSERVABLE_CONTRACT_PROPOSAL.json` | `d0fb7b4fafc2b824e8998dbf10c7f27d8443fdb1218be7588c674002a2dcfc3c` | `1b7c4190290071c9469cf4ef4176019189b310c716d32c5102c2968eb2b6c539` |
| `docs/ef1/OBSERVABLE_PUBLICATION_FIXTURES.json` | `646e402e321eb97a171a2f8f64ce3c1ee399f7bcb81906fd929be4e6477170a6` | `8404a1871c7841abbca8551e6c6b31e52dc3c4fd0a16eefead826d38bac9c3aa` |
| `docs/ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.json` | `b4c78f03b3c1ec5100740803d4b853920f9aa28cb58d73446dea6b3f403db09c` | `298851f79f26da042fada31163c8384eb497f9769d9c3b38b1f51128ec8f93be` |
| `docs/ef1/REFERENCE_CONTRACT_PROPOSAL.json` | `5160d91fc966137a1728c6c26dde15d6772ea35811efc4ea9832b2f7460a28f0` | `5b751632a5dba5bf53ac59cbf9602124ff2fb8f50e423a80f84a5346c107fa4e` |
| `docs/ef1/gap_endpoint/GAP_ENDPOINT_ORACLE.json` | `751cd98fd7951aa7c2d4394d9a5fee87e184d9d484d9f43d4de4983b7333f40f` | `ca32e6c890697a09d1ba6450748085a4b03d2bff2eb8e711d8c79371289aede3` |
| `docs/ef1/gap_endpoint/GAP_ENDPOINT_ORACLE_CAUSAL_V4.json` | `698994acf9d324d3c94334b02f307b2997ce320eb397d7f7cb5f8ea359d4f239` | `ded050dc98f29a45d9f4bcbb47a3b3c0e415e93f381282500b3f1f8c72a1a0b5` |
| `docs/ef1/regular_bar_prices/REGULAR_BAR_PRICES_ORACLE.json` | `05d5b4815df3fd621993037c84f9d897a32ee84c833715e6ca1f6c4e1473d030` | `70fcaff8038d416f8cbc00340c7084fa106944c85a8e1ec4088d3b4b5149db96` |
| `docs/ef1/regular_first_trade_price/REGULAR_FIRST_TRADE_PRICE_ORACLE.json` | `e1835d416a09bd65fce59612323d23c241fe81dcb8493170002e2c3eadffe531` | `e4cd2ec2f97c43012884a7676d7bb6b81e3643ecbe88ebccb9ac251f9bcd6a44` |
| `docs/stories/EQ-097_BATCH_ORACLE.json` | `fa7e282711dc54e88bf2ae51a247a4969ea416be74e1bfe3e4e633207998e1bf` | `5e3111793665f8f59a037ad31bcfc3750445ef82dc2848ea998232c4f4586e2a` |
| `docs/stories/EQ-097_CONFIG_ORACLE.json` | `e1b12d267ef25cadd48549725e7ff1c8f1f4254bde30b910ee8fd27aaee5585d` | `8512465a50ee6fe7d90ef8288a339ec8c000fff0990f0d3977ff1a04c01267e0` |
| `docs/stories/EQ-097_RESULT_ORACLE.json` | `4f78413ee898ed72031423695a16bdb4d8a3d7f5b38b4f814bd709fbed8dc287` | `eae2d32b707262039355b035140ffebd98c81b98d5e104c0e6f5955115b1487f` |
| `docs/stories/EQ-099_EXPLANATION_ORACLE.json` | `12da2aa17eb6173a6846e825f425c2b526570a395946bd73967fbcc05587f0eb` | `2e5487fb5c7bf50fc66014f44c6ba560117450698b55c03290f9d531f265acd6` |
| `docs/stories/EQ-099_REFERENCE_ORACLE.json` | `3513cdd0a60d855e34644b36ee67ca2728d2fdf69070a7a6c4dc6f7bf4e2da49` | `fb8ae1d43ceab18fc68c41fe2c2fc252f63d5798a23894cb1f2fc5cb4e2a58fe` |
| `docs/stories/EQ-109_ORACLES.json` | `f21c1a0ba6659a8e92afd1d2d56aca0c82f17ae9ecb2c0acf4035b2778201a76` | `7cadf99d9087a77b574dc36ca6ed80d31b6d0d9c67dff6254427242498fabb7f` |
| `tests/fixtures/ef1_daily_observations.json` | `479948037cd6d2fca3901cdb9cf3fcbba6256acbbcb9440bcd68e0362d7688c5` | `eab22b6e2f5adf82e0437f1d3aaf845d4d4dcd66e5a561600a2ccb9172573ff2` |
| `docs/stories/EQ-108_ORACLES.json` | `c2c0cfd863191fbd5deda83278f0cec234f60cf41dd10be32edbf1a6de591cea` | `5a7726ca3c8dda7281f66acbd3c154ad66b823e98307f5068984c18a074cd168` |

`docs/stories/EQ-108_ORACLES.json` (copied byte for byte into equity-feature-workers) changed only in the digests derived from the contracts label and the `sha256` fields of the blocks that contain them, using the digest map of the EQ-099 explanation oracle. `docs/stories/EQ-109_ORACLES.json` changed in two `contracts_version` values and the `sha256` fields of the configuration and
batch it describes (`84623ae5...` to `de5d6626...`, `aa3697b5...` to `4aa0d784...`). Older frozen manifests and freeze
records that quote the "before" hashes (`docs/ef1/*FREEZE*.json`, `docs/ef1/*/FINAL_PUBLIC_CANDIDATE_MANIFEST.json`,
`docs/ef1/DAILY_OBSERVATIONS_VALIDATION.md` and similar) are historical and intentionally not edited; this table supersedes them for the live fixture bytes.

## Repeat-build equality (checklist 1.3)

All 27 packages of the three repositories (12 core, 8 io plus 2 example packages, 5 workers) were built twice from fresh copies with `SOURCE_DATE_EPOCH=1700000000` and the pinned `build 1.2.2.post1` / `setuptools 80.9.0`: wheels are byte-equal and sdists are equal after the repository's own normalization (`tools/build_explanations.py normalize`), 27 of 27. Not a release build: no tag, no publish.

## Not run / carried forward

Commit-pinned release builders (`tools/build_*.py` with a `CORE`/`IO`/`WORKER` commit constant) read their versions from
`tools/_versions.py` now, but their commit pins still name pre-bump commits. They must be re-pinned to the merged heads before their
next run; they were compiled and exercised only through the unit tests that load them, not executed end to end.
