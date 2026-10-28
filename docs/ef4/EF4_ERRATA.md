# EF4 errata (PO ruling E6, 2026-10-28)

The frozen EF4 contract files (`TAPE_`, `QUOTE_VWAP_`, `PATH_EFFICIENCY_`, `PATH_PROJECTIONS_CONTRACT_PROPOSAL.json`) are **not edited**. This table is the recorded truth where a recorded `raised_by` label or code differs from what the merged layers do. Details and per-layer counts: [EF4_SHARED_AMENDMENT.md](EF4_SHARED_AMENDMENT.md) E6.

## Code errata (library codes are the recorded truth)

| Recipe | Contract | Input | Contract code | Recorded truth (code, raiser) | Ruling |
| --- | --- | --- | --- | --- | --- |
| RF18 | TAPE | `batch_kind = quote` | `INVALID_SCHEMA` | `UNSUPPORTED_SAMPLING`, shared batch validator | ACCEPT library code; shared validator not altered |
| RF35 | TAPE | two identical seed facts | `INVALID_SCHEMA` | `DUPLICATE`, shared REFERENCE validator | ACCEPT library code; shared validator not altered |

Both inputs are still refused. Census figure: tape 73 of 75 recipes raise the contract code (RF18 and RF35 are the two ruled differences); across the four EF4 contracts 306 of 308 refusal recipes match the contract code (G 75, H 80, I1 39, I2 114 = 308). 306/308 is the ruled, documented number. A reader comparing a driver's output with the contract code must apply this table.

## raised_by label errata (refused input and code unchanged)

| Recipe | Contract `raised_by` | Actual raiser |
| --- | --- | --- |
| RQ09 (QUOTE_VWAP) | shared validator | library (`S.cutoff`; the batch validator does not see the market cutoff) |
| RQ12 (QUOTE_VWAP) | library | shared batch constructor (the column schema fixes the kind) |
| RV43 (QUOTE_VWAP) | shared validator | I/O boundary (`S.bar_notional_bounds`) |
| SPR10, SPR11, SPR18, BPR10, BPR20, RXR22, RXR26, RXR27, RXR28, RXR33, RPR27 (PATH_PROJECTIONS) | producer admission | shared canonical batch constructors at the I/O boundary (library when run library-only) |
| SPR12, SPR13 (PATH_PROJECTIONS) | shared validator | library checks on top of the BAR validator (not refused at I/O) |
| RF01, RF58 (TAPE; BOUNDS) | shared validator | refused at compute in the G worker |

Worker code mapping (EF3 ruling R9): worker codes collapse to `INVALID_COMMAND`, with `RESULT_IDENTITY_MISMATCH` for library `INCONSISTENT_IDENTITY` and `CALCULATION_FAILED` for `OVERFLOW`; the closed `contract_code` carries the library code.

## Accepted limit (E8, unchanged)

The nine tape merge recipes RF41, RF42, RF43, RF54, RF55, RF60, RF65, RF66 and RF69 are library-checked only, with no worker path.
