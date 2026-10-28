# Agent event evidence (experimental)

`equity-feature-agent-evidence==0.1.0a2` contains pure immutable declarations for
requests, supplied model identity, tool calls/results, feature reads, decisions,
human review, cancellation, errors and corrections. It requires CPython 3.12 and
the pinned public contracts/evidence packages. It performs no I/O, clock read,
model execution, calculation, storage, scheduling or publication.

Use explicit public/synthetic arguments or `redacted`, `not_supplied`, `unknown`
and `truncated` states. No prompt, secret or hidden chain-of-thought capture is
required. A mislabeled string cannot be automatically authenticated or screened
for every secret. Actor/model/clock/approval values remain supplied declarations.

`encode_event` and `decode_event` use closed canonical ASCII JSON. `event_digest`
hashes those bytes; `event_reference` makes their identity. `verify_payload`
checks only supplied retained bytes and returns a typed unavailable result when
evidence is absent. `check_references` checks at most 64 supplied prior events;
missing targets stay unresolved and conflicts refuse. SHA consistency is not
authentication, source consumption, approval authority or complete history.

Occurred and recorded times are independent supplied UTCns int64 values. C/K/E
availability remains the accepted public contract. Decreasing occurrence time
does not reorder the recording sequence. Corrections reference earlier records
without mutating them. Persistence, global uniqueness, anchors, retention and
replay belong to an external ledger, not this package.

All public records are frozen. Constructors accept exact builtin lists/tuples
where documented and retain detached tuple fields. Scalar/collection limits,
16 KiB canonical event cap, 4096 lexical nodes and depth 12 are application
limits; they are not a physical sandbox, quota or wall-clock deadline.

See the repository's `docs/stories/EQ-106_CONTRACT.md` for the complete schema,
wire keys, enum values, argument/payload state invariants, error precedence and
public API. The original independent fixture bytes are versioned beside it.
This alpha does not modify accepted numerical formulas or receipt schemas.
