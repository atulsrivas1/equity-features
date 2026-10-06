# Agent evidence ledger — corrected design proposal

Owner-authorized planning refinement under GOV-012. Maps to EQ-096/097 receipts/content fingerprints, EQ-101/102 diagnostics and EQ-106/107 agent events/ledger. Earlier suggested EQ-096/097 ledger identifiers are superseded; no identifiers are reassigned. Implementation remains Backlog. This plan does not establish implemented functionality or change current calculations.

## Ownership and records

Immutable caller-supplied records and pure canonicalization/verification helpers belong to separately versioned evidence contracts/helpers, with package allocation settled before code. Agent orchestration, persistence, clocks, credentials, authentication and anchoring remain outside calculation kernels. Existing result/configuration schemas and accepted equations remain unchanged unless an explicit compatible evolution is approved.

Each event binds chain ID, schema/canonicalization version, sequence, unique namespaced event ID, kind, actor declaration, supplied execution UTCns, previous hash and canonical event hash. Stable kinds cover request/trigger, tool call/result, feature read, model declaration, decision, human review, cancellation/error and correction. Kind-specific immutable subjects retain arguments/result references with explicit redaction, model/tool versions where supplied, receipt references and approval/outcome references. Caller assertions do not authenticate identities or certify source truth. Hidden chain-of-thought is not required.

Feature reads bind calculation receipt plus input/output content fingerprints, feature IDs, entities, formula/configuration versions, availability C/K/E and bounded evidence references. ResultMetadata.identity_digest covers metadata, not result values, and is insufficient alone. Exported references distinguish content unavailable, evidence truncated and evidence not supplied.

## Time and point-in-time findings

Keep real execution/event time separate from supplied simulated decision market/knowledge/effective cutoffs. Backtests executed today are evaluated at the historical decision cutoff. Record clock source/uncertainty if provided; sequence orders recording, not necessarily real-world events. Do not reject late-arriving events solely because occurred timestamps decrease. Define observation time versus recording sequence in EQ-106.

Diagnostics separately check market cutoff, known-at availability, reconstruction mode, membership and freshness. K is a declared admissibility bound, not proof of actual acquisition time; later K is a policy mismatch or insufficient proof, not proof that all input was future knowledge. Membership proof must match entity, requested universe/sector, effective time, decision knowledge cutoff and source/revision snapshot. Missing/unknown proof remains unknown/not evaluated. Checks cannot certify all survivorship or model-training contamination.

Staleness requires an explicit tolerance, age basis and target time; distinguish market observation age, reference publication age and tool-read age. An optional exact fraction of violating unique cited reads includes explicit numerator/denominator and assessed/unknown counts. Zero denominator is not evaluated, not zero leakage. Duplicate/missing/forward references have explicit validation rules. No opaque aggregate safety score.

## Chain verification and bounded operation

Canonical bytes are schema-versioned, domain-separated by record type/chain/version and pinned by independent fixtures. Reject ambiguous JSON, unsupported values and malformed hashes; preserve exact UTCns, units, nulls and specified floating representations. Corrections reference earlier retained records and never mutate history; define amend/revoke semantics rather than silently removing evidence.

verify_chain checks content hashes, sequence and linkage for supplied records. A valid shortened prefix can pass internal consistency. Detecting removal of a suffix requires a trusted externally retained expected head hash/sequence or anchor; genesis and self-declared anchors alone do not prevent whole-chain replacement. Anchor retention/authenticity and signing, if any, are separate operational responsibilities. Verification reports internal consistency and anchor coverage separately.

Pure bounded incremental state avoids repeatedly copying or verifying the entire chain at every append. State binds chain/version/head/sequence and supported bounded duplicate/reference indexes; storage-backed global uniqueness and reference lookup belong outside kernels. Define limits, checkpoint compatibility, continuation verification and explicit failure when required context is unavailable. Full verification is linear in supplied records; performance claims require measurements.

As-of reconstruction uses explicit cutoff and recorded observation knowledge, retains correction history and a chain-prefix or membership/inclusion proof. Arbitrarily filtering records breaks linkage; never claim the filtered collection is the original intact chain. Truncation, redaction, forgetting and retention policy must not silently preserve a complete-verification claim.

## Tests, documentation and end state

Independent canonical hashes and one-field mutations; metadata-identical/value-different results; valid shortened prefix versus anchored suffix loss; replacement/reorder/duplicate/gap; late events and equal times; historical decision versus current execution; matched/mismatched membership; zero/duplicate/unknown cited reads; stale age variants; correction, checkpoint, crash/concurrency and bounded-resource tests. Test pure contracts separately from external persistence. Public synthetic installed examples and migration/threat-model guidance accompany every story; standard final-head and post-delivery gates apply. No compliance certification, profitability or market-exclusivity claim.
