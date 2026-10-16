# EQ111 finite continuous-session capability assessment

[Story213](https://github.com/atulsrivas1/equity-features/issues/213), [E16](https://github.com/atulsrivas1/equity-features/issues/212), [PR416](https://github.com/atulsrivas1/equity-features/pull/416). Executed source assessment; final candidate/main CI, documentation review and acceptance remain separate. [Validation](EQ-111_VALIDATION.json) binds source and results. The [packet](EQ111_READINESS.json) and [frozen probe](EQ111_PROBE.py.txt) were publicly reviewed before Ready/In progress and execution.

| Requirement | Executed evidence | Decision and remaining work |
| --- | --- | --- |
| Finite continuous week | Supplied UTCns start1700000000000000000, day86400000000000, seven days. Start admitted; end/cutoff equality excluded. | Reuse SessionSpec; no new session type/schema/version. |
| Seven day partitions | Shared boundaries have exactly one owner; all seven translate the existing trade fixture and round-trip configurations. | Identities and schedules remain supplied; no calendar discovery. |
| Overnight/civil bounds | Supplied22h-to26h interval and separate23h/25h bounds preserve exact duration with opaque labels. | Reuse finite bounds; no inferred DST/holidays. |
| Explicit gap | Two sessions separated by a full day admit no event in that gap. | No automatic fill or compression. |
| Auctions/identity | Disabled auction exceptions stay disabled; invalid cutoff, final-end event and foreign session fail. | Existing admission unchanged. |
| Existing numerical feature | Prices100,102,101 and sizes2,3,5 produce count3, volume10, notional1011, VWAP101.1, mean_size10/3 over the week and translated days. | Reuse existing trade kernel, not a new duration/cross-venue kernel. Full metadata/config digest remains bound. |
| Count versus completeness | WindowSpec retains first/missing slots and can have enough declared slots; HistoryContext still records missing-row coverage. | Count is not rolling duration or delivered completeness. EQ112/113 own any companion semantics. |
| Feed/freeze gating | Named overlapping intervals are labels: scheduled-freeze does not block an event. Attempted feed_state/duration_ns constructor keywords fail. | Specific schema1 APIs lack these direct fields/policies. This does not prove external/generic reference representations impossible. EQ112/113 own explicit supplied feed/product/effective/known-at behavior. |
| Knowledge versus feed health | Cutoff equality admitted; unknown/later knowledge retain distinct reasons. | Reuse AvailabilitySpec; it does not implement outage/stale/freeze classification or causal two-leg matching. |
| Compatibility | Independent literal canonical envelope matches public serialization/round trip and historical SHA256d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc. Exact subclass injection fails. | Preserve ConfigSpec1 and contracts/features0.0.4a4; no automatic new-type coercion. |

Author and separate local reviewer each passed the same16 public-API source methods in separate Python processes. The reviewer checked58 pre-execution inputs, literal arithmetic and legacy bytes/hash before/after execution. Both used the same existing CPython3.12.10 development environment/source clone: no independent reinstall, two-OS or native/service/SDK qualification. Counts overlap, not32 distinct methods. Ordinary test duration is not a benchmark.

No installable package, runtime API, builtin formula, algorithm version, dependency or workflow changed. The new test equals the reviewed probe. Current mandatory candidate/main CI and independent actual public-source/attribution readback still gate delivery; retained package evidence keeps its original scope through unchanged effective inputs.

EQ112 must freeze reference selection, units/conversion, causal alignment, ages/mismatch, weighting/coverage, fractional/overflow and reopen availability with complete independent fixtures. EQ113 implements only demonstrated missing supplied feed/duration behavior with explicit identity and preserved old digests; EQ114 supplies admitted pure kernels; EQ115 qualifies actual new Windows/Linux installed composition. These remain dependent Backlog work, not completed contracts. No new session type is justified here.

No market launch, entitlement, economic equivalence, liquidity, trading-profitability, physical-resource/deadline or operational-security claim. Calculations continue to use supplied in-memory data without fetching, credentials, clocks/calendars, file/database access, scheduling or publication.
