# Coordinated pre-release bump DV1-4 (C2, with C3): contracts a5 to a6, features a6 to a7 - October 29, 2026

PO rulings D2, D4 (work/po-rulings-dv1-4-5-2026-10-29.md). Pre-release label move only (internal, synthetic, pre-release): no tag, no publish, no release claim, no performance claim. Numeric results unchanged; version labels moved and digests changed by construction. io and workers follow in separate PRs (cascade list below).

## Digest-versus-label gap (PO D2)

C1 (#760, 9d12412) added the built-in `session.price.range_over_open`; this PR is the next change on main. Measured: the registry snapshot digest `builtin_digest` is `da0bcb3d92468bb89178ba2359193a4f081cfd2e1d7075af5406d6598278f1b4` both on 9d12412 (contracts a5, features a6) and here (a6, a7), so the snapshot digest never embedded a label; the window between C1 and C2 is a label-weaker-than-catalog window only, with nothing merged inside it.

## Packages moved

| Package | From | To | Why |
| --- | --- | --- | --- |
| equity-feature-contracts | 0.0.4a5 | 0.0.4a6 | built-in catalog gains `range_over_open` (40 built-ins) |
| equity-features | 0.0.4a6 | 0.0.4a7 | dv1 package, built-in reduction, EF4 discovery text; result `backend_version` carries it |
| equity-feature-evidence | 0.1.0a3 | 0.1.0a4 | content digests embed `contracts_version` (fingerprints differ, below) |
| equity-feature-explanations | 0.1.0a3 | 0.1.0a4 | admits backend 0.0.4a7 (a4, a5, a6, a7); digests derive from the contracts label |
| equity-feature-diagnostics | 0.1.0a2 | 0.1.0a3 | pins evidence (cascade) |
| equity-feature-conformance | 0.1.0a2 | 0.1.0a3 | pins evidence and diagnostics (cascade) |
| equity-feature-agent-evidence | 0.1.0a2 | 0.1.0a3 | pins evidence (cascade) |
| equity-feature-agent-ledger | 0.1.0a2 | 0.1.0a3 | pins agent-evidence (cascade) |

Pin-only, versions unchanged (D4, on measured evidence): intraday 0.1.0a5, continuous 0.1.0a2, labels 0.1.0a1, strategies 0.1.0a1.

## Digest evidence (old = 9d12412 sources, new = this PR, same inputs)

- Same trade fixture and config: backend_version 0.0.4a6 vs 0.0.4a7; result fingerprint `6d29a417...` vs `4d089889...`; config fingerprint `a84793ad...` vs `5674de73...`; batch fingerprint `b3cbe9c1...` vs `2f774eee...`. An a5/a6 artifact cannot be confused with an a6/a7 one.
- Intraday (pin-only): all seven catalog digests are equal before and after (channels 50b34fc4070c, ef5 ccb1cdaea7eb, money_flow d0e38463e6ce, momentum 050a0a03c128, path_efficiency 5f2a343faf87, intraday 11e0c702d405, realized_variance 35ff7a733845); `verify_shared_preparation` pins pass unchanged.
- continuous (35 tests), research/labels/strategies (14 tests) and intraday (78 tests) pass against unchanged oracles.
- `verify_ef5_library`: 89 fixtures, 534 runs, 59 refusals, 12 codes, unchanged.

## Regenerated version-derived fixtures

Method as the A5/A6 record: labels substituted (`backend_version` a6 to a7, `canonical_package_version` a5 to a6, `contracts_version` a5 to a6); EQ-099 oracles regenerated from the production encoder with every differing leaf required to be a digest; EQ-108 by digest map plus recomputed block hashes; EQ-109 and EQ116 configuration and batch hashes recomputed as SHA-256 of the canonical content. Numeric expectations untouched. io `tests/ef1` and workers `tests/ef1_*_oracle.json` copy the EF1 files byte for byte (identical SHA-256 required).

| File | SHA-256 before (main) | SHA-256 after |
| --- | --- | --- |
| `docs/ef1/OBSERVABLE_CONTRACT_PROPOSAL.json` | `1b7c4190290071c9469cf4ef4176019189b310c716d32c5102c2968eb2b6c539` | `1d883a4d7d61593c0e8d9d2c8c0423933d07f3ff386e3775ccafe1aab0a0d2fd` |
| `docs/ef1/OBSERVABLE_PUBLICATION_FIXTURES.json` | `8404a1871c7841abbca8551e6c6b31e52dc3c4fd0a16eefead826d38bac9c3aa` | `7e21d4eb997cd75c100d2f1da0af74fe59ed8d45262c470bdd9d5344443cd8b4` |
| `docs/ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.json` | `298851f79f26da042fada31163c8384eb497f9769d9c3b38b1f51128ec8f93be` | `81ac55769bdd21074aacf83c8df8955a501979d22e813ccfeba55b9e5e9f9204` |
| `docs/ef1/REFERENCE_CONTRACT_PROPOSAL.json` | `5b751632a5dba5bf53ac59cbf9602124ff2fb8f50e423a80f84a5346c107fa4e` | `7eb97ec61eb1a945d39be9551c5937b3e86c7647d854b1aa507d0a8f32728a1d` |
| `docs/ef1/gap_endpoint/GAP_ENDPOINT_ORACLE.json` | `ca32e6c890697a09d1ba6450748085a4b03d2bff2eb8e711d8c79371289aede3` | `22d23e4c57fe1382c25b30aba50bde70eff002d85a9a4dc27f96b13df6b210b2` |
| `docs/ef1/gap_endpoint/GAP_ENDPOINT_ORACLE_CAUSAL_V4.json` | `ded050dc98f29a45d9f4bcbb47a3b3c0e415e93f381282500b3f1f8c72a1a0b5` | `8ff3cce116c71dbe50c8e3e8d455dd4203acddfcc9604bbc092aa85e2ca2b781` |
| `docs/ef1/regular_bar_prices/REGULAR_BAR_PRICES_ORACLE.json` | `70fcaff8038d416f8cbc00340c7084fa106944c85a8e1ec4088d3b4b5149db96` | `bd057b4042e1274ae46a8653debae90e275087f6448780f491c33a2a691bbaf0` |
| `docs/ef1/regular_first_trade_price/REGULAR_FIRST_TRADE_PRICE_ORACLE.json` | `e4cd2ec2f97c43012884a7676d7bb6b81e3643ecbe88ebccb9ac251f9bcd6a44` | `b57ac7221508310cdc812f718b19287c9e23604fddcab6a676cb4407bfdd9997` |
| `docs/stories/EQ-097_BATCH_ORACLE.json` | `5e3111793665f8f59a037ad31bcfc3750445ef82dc2848ea998232c4f4586e2a` | `9b7d3695704c2112255c8ad912e64a08a3713979909ae1e91a5453b34aea3ee2` |
| `docs/stories/EQ-097_CONFIG_ORACLE.json` | `8512465a50ee6fe7d90ef8288a339ec8c000fff0990f0d3977ff1a04c01267e0` | `5075ff01fb009c6a886a738359292391e8e315710f7965c08ae5b8d069124c87` |
| `docs/stories/EQ-097_RESULT_ORACLE.json` | `eae2d32b707262039355b035140ffebd98c81b98d5e104c0e6f5955115b1487f` | `4a9496bd0be61cfa0c9a8c2ea044f6796e5de54bf7b572711b7d386a46e6dcc7` |
| `docs/stories/EQ-099_EXPLANATION_ORACLE.json` | `2e5487fb5c7bf50fc66014f44c6ba560117450698b55c03290f9d531f265acd6` | `449216cc69f46677a26532e9e010431148cbf2310118f0aaa10c11ab15ad8820` |
| `docs/stories/EQ-099_REFERENCE_ORACLE.json` | `fb8ae1d43ceab18fc68c41fe2c2fc252f63d5798a23894cb1f2fc5cb4e2a58fe` | `23bf91a303db93e1e83d7ac17791177805d0ba1d31741c063581427b74e476d1` |
| `docs/stories/EQ-108_ORACLES.json` | `5a7726ca3c8dda7281f66acbd3c154ad66b823e98307f5068984c18a074cd168` | `38a6a05de45c6e26633fbbcf4c6f31e0ecfff9a048aac9c526c2e842074966f4` |
| `docs/stories/EQ-109_ORACLES.json` | `0ba72c1191953893e01ed61685f41583535e8b88d984d288f7694a38a017a74b` | `a64b05fc29f2f845d0787313b07a9380390dac1bbd9098589576a8d92ed3d973` |
| `docs/stories/EQ116_ORACLES.json` | `30aec747d0483ae3e95faabf704fbd37d2fa8cd40882eb3ba1c2518e6932a98a` | `a9f7e24e2463140c76b66094586abd942e0732cec807505d81db082c23b1dc9d` |
| `tests/fixtures/ef1_daily_observations.json` | `eab22b6e2f5adf82e0437f1d3aaf845d4d4dcd66e5a561600a2ccb9172573ff2` | `50257a0d648809c7987ce49d710812afdd5f1ff6dd4ddf1c65c0fafb8c121f15` |
Other pins moved with them: file-hash pins in tests/unit/test_ef1_*.py, tests/evidence/test_content.py, tests/explanations/test_explanations.py, `ORACLE_SHA256` in examples/evidence_pilot.py, and the producer fixture backend in examples/agent_research.py. Declared-environment strings (`PackageVersion(...)`) are caller data and were left.

Correction found on the way: `docs/stories/EQ116_ORACLES.json` carried a stale `configuration.sha256` (`84623ae5...`, the pre-A5/A6 EQ-109 value; no gate checked it); it now holds the recomputed value.

## C3: EF4 dispersion description (inside this PR)

Only the discovery `formula` text of `core.benchmark_return_dispersion_fraction` in `ef4/_path_projections_definitions.py` changed: RANGE of core returns (deprecated name), not dispersion, naming `core.benchmark_return_range_fraction` and `core.benchmark_return_stdev_fraction`. No id, value, dtype, unit, producer, refusal or frozen EF4 file changed; `verify_ef4_fixtures` and `verify_ef4_errata` pass; no core gate pins the text. The EF4 errata gains a cross-reference line. Removal stays at the scheduled EF4 migration (ef4-rel1 to ef4-rel2). `verify_dv1_fixtures` now allows a version-label-only difference in frozen EF1 oracle files and an append-only errata; any other difference still fails (negative mutation checked).

## Gates (clean non-editable venv with numpy, pyarrow, jsonschema; io 1ac4d7e and workers 21cf7f4 installed from origin/main)

verify_versions (incl. README pins), verify_ef4_fixtures, verify_ef4_errata, verify_ef5_fixtures, verify_ef5_library, all verify_dv1_*, check_boundary, mypy 1.15.0 --strict (118 files), `pre_merge_check.py --installed` 30 of 30. Unit suite: 1075 tests, 1 failure (`test_purity_audit`, 112 != 105), identical on main 07f5736, pre-existing; it also stops build_foundation's installed unit step. Fresh double build from git HEAD (SOURCE_DATE_EPOCH 1700000000) of the 12 core packages plus the external consumer example: 13 of 13 wheels byte-equal, sdists equal after normalization; wheel names carry the target versions. io and workers packages were not rebuilt (unchanged until their PRs). Until io bundles admits contracts a6, evidence a4 and features a7, 8 agent_research tests error and the whole evidence_pilot class (19 tests) fails at setup; with bundles patched both groups match main (49 agent_research and 19 evidence_pilot tests run). Two "absent calculator" agent_research tests need an environment without equity_features and do not apply.

**Merge window.** Order: #762, then the io bump immediately with nothing merged between, then the workers bump, then the re-pin PRs. Between #762 and the io bump, main is red for those 8 + 19 tests; no order is red-free (the io bump needs core a6/a7 on main).

## Builders

Ran end to end on this branch (archives built twice, equality asserted): build_evidence, build_explanations, build_diagnostics, build_continuous, build_research, build_agent_evidence, build_agent_ledger, build_intraday. build_foundation stops only at the pre-existing purity-audit failure. NOT RUN, open, and blocking the freeze marker: build_conformance, build_r10, build_r9, build_evidence_pilot (they read the pinned io and workers commits, which cannot build with core a6/a7 until the io and workers bumps merge and `SIBLINGS`/`SIBLING_COMMITS` are re-pinned in R-core; both deliberately unchanged here). build_evidence_evaluation stays retired (docs/RETIRED_BUILDERS.md).

Note on EQ-109: PR #749 edited `backend_version` in `docs/stories/EQ-109_ORACLES.json` after the A5/A6 record, so its file hash drifted from the recorded one; the hashes inside the file were self-consistent. The table uses main as the before value.

## Pre-existing staleness to fix in the re-pin PR

`tools/_versions.py` `SIBLINGS` (io-contracts `0.1.0a3`, while io main is a4) and `SIBLING_COMMITS` (io `94217cf`, workers `99b5fed`, older than io `1ac4d7e` and workers `21cf7f4`) are already stale on main; the comment still says post-bump main commits. This PR leaves them; the R-core re-pin PR must fix both versions and commits.

## Cascade needs (from a sweep of io 1ac4d7e and workers 21cf7f4)

io: tools/_versions.py CORE (contracts a6, features a7, evidence a4); packages/bundles `_versions.py`, pyproject (deps, replay extra), README; packages/io-contracts pyproject and `factories.py` CANONICAL_PACKAGE_VERSION; packages/duckdb pyproject; packages/files README; examples/third_party (pyproject, sink.py); examples/factory_consumer (`__init__.py`, publication.py); examples/bundles_consumer.py; tests/ef1/*.json (9 byte copies), tests/publication_goldens.json, tests/fixtures/bundle_oracle.json, tests/probe_foundation.py (versions, 39 to 40); docs/contracts/IO_V1.md, docs/COMPATIBILITY.md; bar-output lists (13 outputs) in tests/extensions, tests/matrix, tests/duckdb, tests/duckdb-sink, tests/parquet, examples/duckdb_conformance.py, benchmarks/resource_behavior.py. Own bumps per plan: io-contracts, duckdb.

workers: tools/_versions.py SIBLINGS (contracts a6, features a7, evidence a4, explanations a4, diagnostics a3); packages/workers (`_versions.py`, pyproject, equity_sessions.py text, supplied_session.py: add `range_over_open` to the session.price list); packages/provenance (pyproject, `_preflight.py`); packages/client pyproject (native extra); packages/mcp pyproject (evidence extra: evidence a4, explanations a4, diagnostics a3); tests/ef1_*_oracle.json (8 byte copies); tests/manifest_golden.json, make_manifest_oracle.py; tests/service/fixtures/{calculate,delivery_native,jobs_native}.json and docs/EQ078/079/081/084 fixtures (command digest, bar lists); EQ-108/109 copies; tests/probe_foundation.py (versions, 39 to 40), acquisition_probe.py, supplied_memory_delegate.py, test_ef1_anchors.py. Also check catalog oracles for the EF4 dispersion `formula` text.

## Left as history

Receipts, stories, releases, reviews, benchmarks, EF1 to EF4 qualification records and dated API pages keep the versions they were produced with.
