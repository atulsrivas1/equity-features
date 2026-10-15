# Experimental receipt contracts — EQ096

Optional package `equity-feature-evidence==0.1.0a2`, Python3.12, depends only on
`equity-feature-contracts==0.0.4a4`. Core numerical packages never import it.
The normative schema, fixed support, canonical bytes, limits and known-hash oracle
are in [EQ096's packet](../stories/EQ-096_PLAN.md). This is an experimental API;
final reviewed CI/artifact/main qualification, not this document, establishes delivery.

Public immutable records: ContentFingerprint, InputFingerprint, FormulaBinding,
PackageVersion, EnvironmentDeclaration, ExecutionClaim, EvidenceDisclosure and
ExecutionReceipt. Public helpers: make_receipt, encode_receipt, decode_receipt,
receipt_digest. EvidenceError exposes a stable code and fixed payload-free message.
Every decoded field is explicit; no implicit defaults, extensions or dynamic imports.

`make_receipt` receives an actual FeatureResult plus caller-supplied references,
formula versions, environment/execution and disclosure declarations. It verifies
the result's input-role/input-id set, feature-id/algorithm-version set and actual
retained evidence count, and retains its full typed metadata. It never executes
the calculator, fingerprints unprovided content or infers a clock/environment.
Direct ExecutionReceipt construction validates a detached declaration; it cannot
prove an unprovided result exists. See [actual synthetic producer example](../../examples/evidence_receipt.py).

The EQ096 example deliberately uses labeled placeholder content hashes. Its success
proves structural binding, envelope identity and unchanged accepted producer values;
it does not claim the placeholder references match canonical input/output bytes.
EQ097 supplies typed full-content fingerprint generation/verification; EQ098 owns
external bundle I/O/trusted replay; EQ099 owns explanations. These are separate
release stories and are not implemented by calling receipt_digest.

Metadata/config identity digests retain their original meanings. Receipt digest
binds the complete supplied declaration under receipt-json-v1. Content references
separately bind domain/schema/canonicalization/hash/byte-length assertions.
Neither kind authenticates a source, proves acquisition time/rights, original
execution, model training facts, mathematical correctness or compliance. Hashes of
low-entropy/private values may leak information; do not treat a hash as redaction
or authorization. Export only permitted synthetic/public material by default.

Execution time, source/uncertainty and package versions are caller assertions.
Unknown fields are null. Historical C/K/E and supplied real execution time are
distinct; no false chronological comparison is enforced. `retained_complete`
describes only the explicitly declared retained evidence population, never all
physical/source/calculation events. `truncated`, `not_supplied` and `unknown` stay
distinct. A metadata identity and a retained receipt cannot prove omitted facts.

Decoder accepts exact canonical ASCII JSON bytes only. Noncanonical whitespace,
duplicate/extra/missing keys, floats/nonfinite/oversized integers, unsupported
versions, invalid UTF8/surrogates, excessive bytes/nodes/depth/records and binding
conflicts fail closed. No pickle, eval, dynamic type name, resolver, file path,
credential, SQL, network call or clock is used. Closed text labels cannot request
execution or fetching. Application parser budgets are not physical OS quotas or
hard kernel cleanup/deadline guarantees. External cleanup outcomes remain external.

All records copy accepted caller collections to bounded tuples; typed frozen core
metadata is retained without mutable list children. Deliberately bypassing frozen
Python objects with runtime reflection is not an isolation boundary. Consumers
must use the public constructors/decoder and protect their own execution environment.

Schema1/canonicalization versions are immutable. Unknown versions fail rather than
best-effort reinterpretation. Future migration must name the new schema and retain
old receipt bytes/digests. No existing core result/config/version changes occur here;
installing the optional package is not a core upgrade or stable registry promise.

EQ097 candidate adds [actual supplied content verification](EVIDENCE_CONTENT.md) while preserving these supplied-reference/schema semantics. Its final delivery gates remain separate.
