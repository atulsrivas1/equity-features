# Immutable in-memory discovery (EQ-015)

Experimental 0.0.1a5 exports `builtin_registry`, `Registry`, `FeatureDefinition`,
`InputRequirement`, `OutputField` and `Capabilities`. `equity_features.registry`
is an inward convenience import. Core discovery requires no Arrow/NumPy backend.

`builtin_registry().list_features()` returns the frozen 39-ID V1 catalog. `get(id)`
returns declared input/schema fields, output types and units, accepted formula
and document, warm-up/default periods, initialization, timing, missing policy,
algorithm/schema versions and planned release. Family filtering is explicit.
The R0 snapshot initially had every execution flag false. R1 now advertises
only accepted implementations (see migration below). `require_capability` raises
a typed error for unsupported modes; filtering intersects actual support.
Unknown IDs/modes have stable typed errors.

Canonical requirements are checked against schema1. Logical result/evidence/session/
window/availability fields describe supplied structured inputs. Multi-output metadata
is a declaration; future kernels must qualify concrete FeatureColumn/quality mapping.
Formula text is descriptive and is never evaluated. The accepted formula documents
remain authoritative; a CI parity verifier compares IDs/releases and table formulas.

Create `Registry("research")` and add a definition with `with_definition`. IDs must
use `research:<name>`, with lowercase identifier syntax. Built-ins are reserved;
duplicates, overrides, unknown fields/types/versions and execution flags fail.
Definitions and concrete lists are detached into immutable tuples. Registration
returns a new instance and never changes global discovery. There are no plugin
imports, callbacks or executable serialization. Custom execution remains EQ-093/R3.

`to_json`/`from_json` round-trip data only, reject duplicate/unknown keys and check
registry schema, builtin scope and definition digest. This digest identifies the
literal reviewed catalog; it does not establish consumer code correctness. Custom
metadata correctness and eventual calculator qualification remain caller duties.
See `examples/canonical_inputs.py` for installed discovery and scoped registration.

## R1 implementation capabilities (0.0.2a0)

The twelve session.bar/session.price IDs now expose batch=True through compute_bars. Capabilities validates Boolean flags; FeatureDefinition rejects any flag without an explicit accepted built-in implementation. Custom/R2/update/restore/merge remain false and capability requests fail. Family filtering now intersects actual mode support. OHLC output metadata is float64 currency/share; exact notional is decimal128 with price-scale units. Registry digest changes deliberately. See [bar API/migration](../api/SESSION_BARS.md).
