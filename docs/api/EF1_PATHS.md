# EF1 sampled paths API — EQ167

This source-authored candidate extends the existing `equity_features.ef1` API with
`path_gap` and `path_drive`. Runtime validation remains pending under the protected
study reservation. The [reviewed authoring freeze](../ef1/PATH_SOURCE_AUTHORING_FREEZE.json)
admits the exact [path contract](../ef1/PATH_CONTRACT_PROPOSAL.md) and
[independent literals](../ef1/PATH_CONTRACT_PROPOSAL.json). Original schema, codec,
package versions and anchor/clock/status behavior are retained. This is partial
EF1 capability; the full inventory audit and release acceptance remain required.

Use `build_ef1_config(full_context, *, session, window, availability, price_unit,
adjustment)`, `decode_ef1_context`, `ef1_definitions` and
`compute_ef1(batches, config, *, entity)`. There are no new public calculation
functions. Full context has exactly `version="ef1-context1"`, `producer`,
`calendar` and `selection`, within the existing canonical ASCII 4096-byte bound.
Gap selection is exactly `{sampling}`; drive selection is exactly
`{sampling,duration_ns}`. Sampling is `eligible_trade` or `completed_bar_close`.
The config identity is `ef1.path_gap` or `ef1.path_drive`, algorithm v1/schema1.

Gap calendar sessions are exactly the explicit preceding session and target,
with strictly increasing civil dates and supplied bounds. Its window is
`WindowSpec(2,target,(prior,target),"completed_eod")`. Drive calendar and window
contain only target. Calendar vocabulary/hash, finite scope, revisions and
original causal proof knowledge follow the existing supplied-clock API. The
target calendar bounds/date/timezone/scheduled close must match SessionSpec.
Every supplied session and segment, including gap's prior slot, is covered by
the actual calendar declaration. No calendar discovery or date arithmetic occurs.

Pass a concrete tuple/list containing actual present CanonicalBatch values in
the following role order; omit missing roles. `None` elements, duplicates, wrong
selected kind, reordered roles and repeated actual input IDs reject. Empty
batches remain present. Kinds uniquely identify roles.

| Producer | Declared roles and kinds |
| --- | --- |
| path_gap | calendar_provenance: REFERENCE, path: selected TRADE/BAR, prior_close: DAILY |
| path_drive | calendar_provenance: REFERENCE, path: selected TRADE/BAR |

All market input namespaces, instruments, units and adjustment specifications
must match config. Prior's session and full bounds match the explicit preceding
calendar slot, with exactly one delivered row; missing delivery is omission.
Original supplied columns are retained and canonically validated, including
unused OHLC/volume. Structurally invalid present cells raise original errors
before missingness is considered. An absent otherwise valid operand column is
missing input. See [mathematics and admission](../features/EF1_PATHS.md).

All scopes declare `eligibility_policy="supplied_path"`, original auction flags
and metadata sampling `none`. Gap scope is `[A,C)`, requiring `A<C<=Z`.
Drive requires positive int64 duration, checked `B=A+duration<=Z`, `C>A` and
scope `[A,min(C,B))`. Trades at the right endpoint reject; completed bars ending
there are admitted. Closing-auction rows reject; an opening-auction row requires
event=A and explicit session inclusion. No row sorting, filtering of future
rows, inferred completeness or generated original knowledge is permitted.

Discovery returns exactly the complete homogeneous producer, in lexical order:

| Header | Type | Unit |
| --- | --- | --- |
| session.gap.fill_fraction | float64 | fraction |
| session.gap.filled | bool | boolean |
| session.gap.first_fill_ns | int64 | ns |
| session.gap.remaining_fraction | float64 | fraction |
| session.opening_drive.excursion_down | float64 | fraction |
| session.opening_drive.excursion_up | float64 | fraction |
| session.opening_drive.return | float64 | fraction |

Result metadata preserves the actual config digest, availability, original input
bindings and backend/version. Every gap quality row counts path delivered rows
plus the delivered prior slot; expected is path expected plus one, or unknown.
Drive counts the path population alone. Calendar proof is required but excluded
from these numerical population counts. Selected original consumed evidence is
bounded to seven rows for gap or four for drive, deduplicated within each
feature/input/row identity. These witnesses do not replace the complete bindings
or establish absence from one row. No private or legacy numerical parity is claimed.
