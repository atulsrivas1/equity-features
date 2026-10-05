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

EQ018/0.0.2a1 adds batch capabilities for both session.structure IDs. Output metadata uses interval_ohlcv and interval_volume_shares typed values with per-window quality. Only14IDs have batch support; every update/restore/merge and later/custom flag remains false. Scope and formula identities remain unchanged; registry snapshot digest advances.

EQ019/0.0.2a2 adds five session.trade aggregate batch flags (19 implemented IDs). Actual trade notional output is decimal128 with currency/10^price_scale coefficient units, matching the bar exact-amount representation. Other execution flags remain unsupported; registry digest advances without changing equations. See [trade API](../api/SESSION_TRADES.md).

EQ020/0.0.2a3 adds session.trade.top_k batch capability (20 implemented IDs), typed top_k_trades output. Other modes stay false. K/evidence bounds and retained-source proof limits: [API](../api/SESSION_TOP_K.md).

EQ021/0.0.2a4 adds two quote event-summary batch flags (22 implemented IDs), quote_state_counts/sampled_spread typed outputs and explicit sampling. Time-weighted spread and other execution modes stay false. Frozen equations exclude quantiles/variance. [API](../api/SESSION_QUOTES.md).

EQ022/0.0.2a5 adds continuous time-weighted batch capability (all23 R1 IDs), one typed time_weighted_spread value containing previous provisional scalar duration/mean fields. Unknown duration is explicit nested diagnostics. Other execution modes remain false. [API](../api/CONTINUOUS_QUOTES.md).
