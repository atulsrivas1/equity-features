# Bounded R4 DuckDB adapter acceptance

EQ056 [issue63](https://github.com/atulsrivas1/equity-features/issues/63), E07 [issue55](https://github.com/atulsrivas1/equity-features/issues/55), [milestone5](https://github.com/atulsrivas1/equity-features/milestone/5), [pre-code plan](stories/EQ-056_PLAN.md). This final audit maps implemented behavior to accepted evidence. Exact final acceptance SHA, CI, publication, channels and lifecycle are recorded on issue63 after Released readback. Live GitHub Project is the status authority.

At preparation on October6,2026, EQ049–055 are live CLOSED/ProjectDone and EQ056 is the sole active R4 story. E07/milestone5 remain open until this audit is reviewed and delivered, all eight children are Done and the release exit is read back. Historical prepared plans and earlier package versions remain provenance, not current execution authority.

## Current package and behavior

The experimental optional package **equity-feature-duckdb0.1.0a7** supports explicit curated/prepared catalog selection, retained mapping and bounded original Parquet acquisition for trades, TBBO trade-sampled quotes, minute bars and UTCdaily bars. Matching contracts/features0.0.4a4 and independent consumer0.4.0 remain unchanged from R3. CPython3.12, DuckDB1.5.6 and NumPy2.2.6 are pinned. The accepted optional bundle was produced with CPython Linux3.12.15 and Windows3.12.10; the accepted Foundation bundle used Linux3.12.14 and Windows3.12.10. Each current report retains its own actual producer runtime.

[Resolver](api/DUCKDB_RESOLVER.md), [mapping](api/DUCKDB_MAPPING.md), [reader](api/DUCKDB_READER.md), [governance](api/DUCKDB_GOVERNANCE.md) and [evidence](api/DUCKDB_EVIDENCE.md) document actual interfaces. Resolver metadata is source support, not canonical delivery. Reader applies explicit identities/units/sessions/selection/cutoffs, bounded rows/chunks/cancellation and cumulative verification, preserving nanoseconds/physical occurrences/unknown availability. Caller calendars, exact retained-population certificates, warm-up/initialization and supplied references stay explicit; no calendar or historical reference authority is inferred from file dates/latest snapshots.

Strict ASCII UTC text is decoded with a connection-local native macro using exact HUGEINT arithmetic and guarded signed-int64 bounds, then independent Python mapping. Both endpoints, null/calendar/clock/fraction/offset/nonASCII/overflow cases are tested. Standard timestamps retain meaning; undocumented Unicode clock/fraction digits reject under a7. Equal normalized facts retain canonical identity; receipts record the actual adapter version. Contract/config/input/result/catalog schemas1, saved session state2, original-read2/retained-map1/acquisition1 and built-in mathematics remain distinct and unchanged.

All39 core built-ins retain R3 modes:23session IDs support update/restore and22conditional legal merge; continuousquote merge remains unsupported. SixteenR2 IDs and custom calculations remain batch-only. R4 adds optional acquisition/governance, not numerical kernels or provider/network/worker execution. Pure calculations contain no fetching, database/file access, credentials, scheduling or publication. Core registry execution with DuckDB absent and forbidden and before/after module/distribution metadata invariance passed.

## Eight-story evidence matrix

| Story | Implemented acceptance | Delivered version / accepted main | Durable record |
| --- | --- | --- | --- |
| EQ049 [#56](https://github.com/atulsrivas1/equity-features/issues/56) | Explicit metadata resolver, overlap choice, source receipts and pins | a1 / `6b57b641` | [Delivery](stories/EQ-049_DELIVERY.md) |
| EQ050 [#57](https://github.com/atulsrivas1/equity-features/issues/57) | Four retained mappings, exact units/times and unsupported fields | a2 / `1e5fdd7` | [Delivery](stories/EQ-050_DELIVERY.md) |
| EQ051 [#58](https://github.com/atulsrivas1/equity-features/issues/58) | Original reads, actual canonical delivery and measured costs | a3 / `aaedb7a8` | [Delivery](stories/EQ-051_DELIVERY.md) |
| EQ052 [#59](https://github.com/atulsrivas1/equity-features/issues/59) | Caller calendars/history windows/references and explicit gaps | a4 / `cd8377f8` | [Delivery](stories/EQ-052_DELIVERY.md) |
| EQ053 [#60](https://github.com/atulsrivas1/equity-features/issues/60) | Shared cumulative hash budget, source rechecks and acquisition evidence | a5 / `185859de` | [Delivery](stories/EQ-053_DELIVERY.md) |
| EQ054 [#61](https://github.com/atulsrivas1/equity-features/issues/61) | Actual DuckDB SDK outcomes and independent synthetic values | a6 / `7f0ff33` | [Delivery](stories/EQ-054_DELIVERY.md), [guide](api/DUCKDB_CONFORMANCE.md) |
| EQ055 [#62](https://github.com/atulsrivas1/equity-features/issues/62) | Frozen actual retained rows/independent goldens and a7 acquisition refinement | a7 / `85efa9d` | [Delivery](stories/EQ-055_DELIVERY.md), [methodology](api/DUCKDB_REAL_QUALIFICATION.md) |
| EQ056 [#63](https://github.com/atulsrivas1/equity-features/issues/63) | Final eight-story/two-layer/install/publication audit | a7 unchanged; final acceptance pending | This audit and issue63 final delivery/readback |

Each accepted predecessor has source and same-story receipt final-head local automated Codex reviews, actual tests/CI/installed artifacts and Released readback. Local review is neither human nor hosted review; GOV005 activation remains separate. Source review of EQ055 is [6026789989](https://github.com/atulsrivas1/equity-features/pull/272#issuecomment-6026789989), receipt review [6026980666](https://github.com/atulsrivas1/equity-features/pull/273#issuecomment-6026980666). EQ056 needs its own final-head semantic/evidence/privacy review; author self-review and CI alone are insufficient.

## Both actual testing layers

Synthetic conformance executes [the public installed example](https://github.com/atulsrivas1/equity-features/blob/2cd51cd35c0a3081f88e1752c7c1c41ffe0e62af/examples/duckdb_conformance.py) against actual temporary DuckDB catalogs/original and optimized Parquet, not just an in-memory adapter. Thirty actual outcomes include nanosecond tied occurrences, empty selection, unknown/later knowledge, identity/pin/catalog/file errors, overlap selection, whole-bar cutoff, resource/cancellation and quote sampling. Three labeled SDK envelope mutation probes test ordinal/final/cross-chunk coverage rejection. Sixteen independently expected trade/bar/history value-unit-quality-source checks pass. Whole-source coverage may exceed the selected delivery; consistency is checked separately.

Representative private qualification freezes two retained instruments/five UTCdaily slots/a five-minute window/eight original-optimized pairs and independent raw-row Fraction/Decimal80 goldens before execution. FOUR actual delivered producer/form fresh Windows installations each passed68numerical/status/unit/source checks/nine successful acquisitions/three blocked cases. Every form binds exact source/archive/runtime/script/scope/report identities and unchanged core fingerprints. Reconstruction available values match independent expectations; causal unknown knowledge/bar notional stay missing. Caller-gap finite recovery versus anchored EMA incomplete, unfinished-bar exclusion, empty selection, wronggolden rejection, TBBO trade-snapshot raw occurrence parity and eligibility/continuous/PIT unavailable cases pass.

Private scope SHA256 `357bf98b840688a77eb63948c8760c760500543748abe22bbc34828913b91156`; execution script SHA256 `700cc1e7977c0117074eb2f7653d9b60e2e3b6f7a8f16195b2a5ab9f682b742b`. Original immutable scope retains historical pre-code a6/no-result preparation stamps; completed a7 reports bind actual source9a82f1d separately. [EQ055 receipt](stories/EQ-055_DELIVERY.md) publishes only opaque hashes/counts/cost limits. Private names/paths/prices/source files/raw receipts remain private; local validation is not redistribution permission.

## Actual installed and publication baseline

Accepted main85efa9d equals separately reviewed receipt63d8f77 tree/allfive public changed blobs/owner. [Docs37544137956](https://github.com/atulsrivas1/equity-features/actions/runs/37544137956), [Foundation37544138061](https://github.com/atulsrivas1/equity-features/actions/runs/37544138061), [optional37544138119](https://github.com/atulsrivas1/equity-features/actions/runs/37544138119) succeed.24actual final archive bytes equal qualified source9a82f1d; current24native reports/harness/testsuite/nativeprobe/runtime/form/archive/core fingerprints and live channels were reread after Released6027069596. Foundation12archives equal acceptedEQ054/R3 bytes.

FOUR fresh actual delivered synthetic forms each passed94optional tests/strict6modules+example1/30SDK16numerical/64row measured parity/core absence-forbidden/invariance. FOUR additional fresh private forms each passed68/9/3. Native Windows/Linux CI qualifies synthetic behavior; Linux-produced forms installed on Windows are not nativeLinux private execution. Documentation-only EQ056 can reuse these forms only after final-main actual archive equality/current native report/private hash/channel checks. No numerical/runtime/package/harness/workflow change is included.

| Optional bundle archive | Linux SHA256 | Windows SHA256 |
| --- | --- | --- |
| equity_feature_contracts-0.0.4a4-py3-none-any.whl | `acaa84fc0340c4640ced2b7cdbef04d5ba7cfaec20cd0525b866b415147635cc` | `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2` |
| equity_feature_contracts-0.0.4a4.tar.gz | `f32a66f31759b10c9ac251f4dffb2388a3e2ce50d2e5e15c69ac7038828f97a9` | `c0f35f1fd775b83ab9fdd48177c6332f38b1c83cc2f9986467e0852ca758ae57` |
| equity_feature_duckdb-0.1.0a7-py3-none-any.whl | `da1a53188ff96b9cfcf3735480d91181654fd620b694d500ed296da2418f0960` | `c90c159c5bc5f38fce21530ee277151087c350964b5c248fb48e4168acbe555f` |
| equity_feature_duckdb-0.1.0a7.tar.gz | `333a3adea14639ac8e596aedb0078d94404d94dfcd19ce1ce22ebe67ef36056c` | `f709060aacfd4da5e2c8cd3d9522a449dee8074f6cf7214907bfb5b0218b8c4f` |
| equity_features-0.0.4a4-py3-none-any.whl | `cf8965e1600a3d8ef10dbefcfdea21f2d48ad8c8f80e0268abe12c365b1cd26e` | `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0` |
| equity_features-0.0.4a4.tar.gz | `14e7b8b0ec1b245747d53081a73c9ef060c0f637d205ae97b5e14304b4d95c8f` | `c25ab736eb267cd11a11d52cbeda6931d23796c94bb264164014f0dd542f1d06` |

## Measured costs and source limits

[Dated EQ051 measurements](benchmarks/EQ-051_READ.md) retain their actual a3 source/workload; they do not benchmark current a7 performance. Current installed synthetic read reports require numerical parity before measured verification/SQL/map/copy and native lifetime peak observations. Four delivered private whole-qualification observations after imports span8,275,026,400–8,510,678,400ns and Windows lifetime peaks138,825,728–144,539,648bytes. These samples include prior acquisitions/imports and are not throughput, exclusive phase memory, a hard resource ceiling or full-corpus guarantees. User-space hashbytes are not physical I/O. No completed old callback timing means no speedup denominator; diagnostic native-crash cause remains unproven.

Retained DOUBLE quantization is explicit binary64_exact/half_even at scale4USD, not recovered provider coefficients. Physical file occurrence is not exchange ordering or execution uniqueness. Newly frozen hash observations/pre-post equality do not establish prior provenance, source truth, atomic snapshot isolation or absence of change-and-reversion. Legacy unverified admission and daily dataset substitutions remain in lineage. Caller source count/session/reference assertions are not provider/calendar/market-wide coverage.

TBBO is trade_snapshot only; continuous requests reject. Retained actual trades lack eligibility and remain unavailable without supplied evidence. Missing known-at is preserved; receipt/current time never becomes historical knowledge. Supplied UTCdaily intervals do not imply exchange RTH. Absent governed action/membership/classification/PIT inputs remain unavailable; latest snapshots and floating action ratios are not automatically historical/rational authority. These limits constrain particular features while bounded acquisition is accepted.

## Final release exit

- Baseline `duckdb-85efa9d84ac22b47f6d38a71750e89a59c041651-ubuntu-24.04`: server `sha256:7a89eea918f69e3d30dce29013de5cae266adb10d6871d045c889c39fe03de2e`, 290100bytes, expiryUTC `2026-11-05T23:02:48Z`, observed unexpired on EQ055 readback.
- Baseline `duckdb-85efa9d84ac22b47f6d38a71750e89a59c041651-windows-latest`: server `sha256:a545c8bf72b95fa9f41001c8fd1ac4ed279cb1b42e123db92c48a86844dadb59`, 291445bytes, expiryUTC `2026-11-05T23:04:19Z`, observed unexpired on EQ055 readback.
- Baseline `foundation-85efa9d84ac22b47f6d38a71750e89a59c041651-windows-latest`: server `sha256:01813fa614bec0a33f3b65db0005b22afd95f7d349221604c6f5e5e967104b65`, 275092bytes, expiryUTC `2026-11-05T23:04:25Z`, observed unexpired on EQ055 readback.
- Baseline `foundation-85efa9d84ac22b47f6d38a71750e89a59c041651-ubuntu-24.04`: server `sha256:3497caa58a272bc9f053046efc2f767323d7b570fea035106aa00bc13d723c8a`, 273818bytes, expiryUTC `2026-11-05T23:03:32Z`, observed unexpired on EQ055 readback.

Actions retention is finite(requested30days), and server bundle digests differ from inner archive hashes. This is the existing experimental main/Actions delivery channel; no stable registry/tag/service is claimed. Exact new final-main channels/expiry and actual acceptance are recorded on issue63 after current CI/publication/archive/report/privatehash and Released reread.

After EQ056 final review/CI/delivery/readback, verify all eight issues CLOSED/ProjectDone, check and close E07, and close milestone5 with zero open issues. Record final continuity and STOP beforeR5. No worker launch, provider acquisition, remote service, historical restart, account setup or recurring automation is required or authorized by this acceptance audit.
