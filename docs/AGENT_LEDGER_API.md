# Local agent ledger — experimental EQ107 implementation

The optional `equity-feature-agent-ledger==0.1.0a1` stores unchanged EQ106 event
records outside calculations. It is implemented for source development and is
awaiting source review, crash qualification and installed Windows/Linux gates.
See [contract](stories/EQ-107_CONTRACT.md), [exact schema/API/profile](stories/EQ-107_PROFILE.json)
and [validation](stories/EQ-107_VALIDATION.json) for current status.

Create a new absolute trusted owner path with `Ledger.create(path, chain_id)`.
Existing destinations refuse. `Ledger.open(path)` requires a supported existing
regular store and fully verifies it; missing paths are never silently created.
The package accepts no SQL, URI options, extensions, callbacks or network/model
configuration. There is no application repair/migration or automatic deletion.
Opening can trigger SQLite's own recovery, which may physically write a journal.

`Checkpoint(chain_id, sequence, head_hash)` binds a declared chain and recording
position. Encode/decode its exact canonical ASCII JSON to retain it externally.
An append requires `expected=before` equal to the stored current checkpoint.
Separate writer connections contend without internal retry; stale expectations
refuse. Event ID uniqueness, next sequence/predecessor, <=16 indexed prior
references and logical capacity are checked inside one write transaction.
Only successful COMMIT returns the new checkpoint.

On `outcome_unknown`, keep the exact proposal and prior checkpoint externally.
The connection is poisoned. Reopen and explicitly call
`reconcile(proposal, expected_before=before)`. Static proposal/base agreement is
checked before store classification. Results are found_exact,
absent_at_unchanged_head, conflict or base_not_covered. None is automatic replay
permission or proof of historical absence after out-of-band replacement.

`verify_events(events, chain_id=..., expected=...)` checks supplied full history;
`store.verify(expected=...)` also checks schema, row mirrors, indexes and metadata
in one snapshot. Integrity errors raise. Anchor coverage is a separate status:
not_supplied, matched_terminal, matched_prefix, mismatch or not_covered. A valid
shortened/replaced unanchored history can pass internal consistency. Only an
externally retained trusted terminal detects the corresponding change.

`export_page(after=sequence, through=fixed_terminal, limit=64)` exports a contiguous
recording prefix, excluding later appends. Every call must use the same explicit
terminal. `verify_page(page, start=before, through=fixed_terminal, prior=...)`
compares caller checkpoints and links. Resolved references mean supplied content
matches; prior membership and global uniqueness are always not_verified. A page
self-description cannot authenticate a history or supply its own trusted terminal.

Immutable result constructors defensively copy/revalidate fields and enforce
cross-field consistency. They cannot certify caller-declared historical statuses.
Public errors have fixed payload-free codes; raw SQLite causes may contain private
details and must not be blindly logged. Exact count/type/error ordering is in the
profile. `close()` closes only its connection. A failed underlying close poisons
operations and retains the reference for an explicit close retry; it is not
completed physical cleanup.

Limits are4096events/32MiB canonical event bytes,16KiB/event,64events/1MiB/page
and1024 page-reference summaries. They exclude SQLite pages/indexes/journals,
deleted/replaced backing, physical nodes and kernel memory. There is no physical
quota, hard filesystem deadline, hostile-path sandbox, power-loss or hosted
recovery guarantee. Indexed append does not continuously recheck unrelated old
rows; explicit verification/reopen does.

Redact before append. Corrections retain original plaintext and do not erase
backups. Supplied times may be late/equal/decreasing; as-of means recording-sequence
prefix, not arbitrary timestamp filtering or knowledge admissibility. Actors,
models and human-review declarations remain unauthenticated. No signing/witness,
retention/deletion or R13 trust product is introduced.

Examples: `examples/agent_ledger.py`, `examples/agent_ledger_producer.py` and strict
caller `examples/agent_ledger_typed.py`. The producer example compares full original
config/input/result/quality/source/receipt bytes and actual retained content across
append/export/reopen. These examples are trusted external orchestration, never
calculation side effects or MCP handlers.
