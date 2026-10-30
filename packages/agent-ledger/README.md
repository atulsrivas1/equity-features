# Experimental local agent event ledger

`equity-feature-agent-ledger==0.1.0a3` is an optional owner-configured SQLite store,
separate from calculations and the pure event declaration package, introduced
by EQ107. Consult the repository's EQ107 validation and current
story/release evidence for the qualification and delivery status of a specific
source commit and its finite-retention experimental artifacts.

Create a new absolute owner path with `Ledger.create(path, chain_id)` or open an
existing supported store with `Ledger.open(path)`. Save `head()` externally and
pass that checkpoint to every `append(event, expected=before)`. Full `verify()`
checks stored integrity; supply a trusted expected checkpoint to detect suffix
loss or a replacement. A self-consistent unanchored history is not authenticated.

Canonical event bytes, IDs, predecessor and reference identities are retained.
The 4096-event/32MiB canonical-byte limits exclude SQLite pages, indexes, journals,
old files, physical bytes/nodes and kernel memory. No physical quota, hard timeout,
hostile-filesystem containment, power-loss or hosted recovery claim is made.

An uncertain commit raises `outcome_unknown`, poisons the connection and never
replays. Reopen and explicitly `reconcile` the saved exact proposal and prior
checkpoint. Observing absence is not permission for automatic replay. Close only
closes this connection; files are never automatically deleted or repaired.

Use a fixed explicit `through` checkpoint when exporting contiguous pages. Page
verification compares caller start and terminal; prior context only matches
supplied content and does not certify earlier membership or global uniqueness.
Times, actors, model identity and review assertions remain supplied declarations.
Redact before writing: corrections retain original bytes and do not erase backups.

Python 3.12; exact optional agent-evidence dependency; Apache-2.0. The package has
no caller SQL/URI/extension/callback API, model/network/provider execution or MCP
handler. See the repository EQ107 contract and validation for current evidence.
