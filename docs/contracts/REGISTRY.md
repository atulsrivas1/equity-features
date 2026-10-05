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

EQ023/0.0.2a6 adds update flags for all23 qualified R1 IDs. Explicit batch/update/restore/merge inventories enforce exact modes, with restore/merge empty and custom/R2 false. All six actual family lifecycles and constraints are documented in [matrix](../api/INCREMENTAL.md).

EQ024 adds immutable AccumulatorState and exact compatible in-memory restore for all23 R1 IDs; see [incremental API](../api/INCREMENTAL.md). Strict schema/version/source/config checks and bounded owned state apply; digest is not authentication. Merge remains false.

EQ025 qualifies conditional adjacent caller-certified partition merge for22 noncontinuous R1 IDs; current inventory23 batch/update/restore and22 merge. Continuous merge remains false. See the incremental API for proof, order, retention and replay limits.


EQ027/0.0.3a1 qualifies history.return/prior_high/prior_low batch only.26batch and session-only23update/restore/22merge inventories are separate; unsupported history modes remain false. Builtin snapshot digest changes with capabilities; [history API](../api/HISTORY.md).


EQ028/0.0.3a2 adds history.sma/ema batch flags:28batch,23session update/restore,22conditional merge. Other history modes remain false;39 equations/identities unchanged. Builtin snapshot digest advances; [history API](../api/HISTORY.md).


EQ029/0.0.3a3 adds history.rsi/atr batch flags:30batch/23session update/restore/22conditional merge;39mathematical definitions and unsupported history modes remain unchanged. Snapshot digest advances; [API](../api/HISTORY.md).


EQ030/0.0.3a4 adds history.return_volatility batch:31batch/all8history,23session update/restore22merge.39mathematical definitions remain unchanged, state modes false and snapshot digest advances. [API](../api/HISTORY.md).

EQ031 qualifies baseline.daily_volume and baseline.relative_volume batch flags,33total. Both remain false for update/restore/merge.39 mathematical definitions and session23update/restore22merge remain unchanged; rebuild exact-version snapshots after pair0.0.3a5. [API](../api/DAILY_VOLUME.md).
