# EQ-020 â€” bounded top-K trade evidence plan

Prepared before coding, issue24/epic20/R1; confirm5points. Pull only after EQ019
verified Done. Preserve concurrent roadmap/PR120; one active story, author review+CI.

## Interface and semantics

`compute_top_k(batch: CanonicalBatch | None, config: ConfigSpec, *, entity:
EntityKey) -> FeatureResult` returns session.trade.top_k only. Parameters are
eligibility_policy, top_k (exact integer1..10000) and evidence_limit (exact integer
at least top_k, at most10000). The explicit operational bound prevents accidental
unbounded retention; it does not change the frozen min(K,n) ranking formula.
Retain at mostK rows by insertion into a bounded sorted list, ordered
(-size,event_ns,order_key,event_id). Never silently sort/deduplicate input admission.
Re-use trade source/session/unit/basis/scope/coverage/C/K/E validation.

Typed immutable TopKTradeRow carries input_id,event_id,event_ns,order_key,
known_at_ns, exact price coefficient and size. TopKTrades carries configuredK
and owned ranked rows. Public Arrow list-of-struct preserves UTCns, integer
coefficients and order. Price scale/unit remain metadata. Matching EvidenceRows
bind every retained row to source and event (closing-auction boundary explicit).
Complete empty yields available empty table; absent payload/input, incomplete
coverage or unavailable knowledge yield null with truthful quality. All eligible
rows require price/size; no derived or truncated original evidence.

No streaming/restore/merge capability is advertised here. Partition conservation
is tested by independent topK of each disjoint source population followed by
ranked union, comparing the full batch. Retained duplicate IDs and overlapping
ordered ranges are detectable; a bounded summary cannot prove that nonretained
opaque IDs never overlap. Caller admission must certify population disjointness;
EQ025 owns the public legal merge API and qualified capability. Batch canonical
admission continues checking duplicates in the actual supplied population.

## Verification and delivery

Independent golden K2=t3(size5),t2(size3); K1, K>n, equal-size/time stable ties,
false eligibility, empty/missing/absent fields, invalid/bool/unboundedK, evidence
limit, identity/unit/source/coverage/knowledge/auction negatives. Inspect owned
immutability, Arrow UTCns and provenance; test partition conservation, overlap
rejection through canonical admission, retained bound across increasing populations.
Version both distributions0.0.2a3; 20 batch IDs. Update API/contracts/registry,
synthetic installed example, release notes/README/continuity and EQ019 receipt.
Run all unit/reference/type/purity/import/compat/license/planning gates, repeat
archives and fresh installed checks; draftPR, author review, exact-headCI, merge,
main bytes/OS CI and both actual bundles/four fresh installs before Done.
