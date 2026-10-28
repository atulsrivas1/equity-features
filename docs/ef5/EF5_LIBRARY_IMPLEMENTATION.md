# EF5 price structures: library implementation notes (EQ-171)

Library only (no I/O, no worker). Implements the frozen contract `PRICE_STRUCTURES_CONTRACT_PROPOSAL.json`: producers
`ef5.candle` (7 outputs), `ef5.structure` (4) and `ef5.technical` (4). Gate: `python tools/verify_ef5_library.py`
(run by `tools/pre_merge_check.py --installed`) expands every contract fixture to supplied BAR chunks, a governed
context and a final configuration, drives it through the library and compares with the contract literals; the
independent stdlib expander (`tools/verify_ef5_fixtures.py`) remains the check on those literals. Result: 89 result
fixtures (534 runs: each output alone and jointly) and 57 refusals over 12 error codes match. No new unit tests.

## Where it lives

`packages/intraday` (modules `_ef5_config`, `_ef5_registry`, `_ef5`), the same package that already holds the R17 context, the
BAR admission and the EF4 path efficiency producer. The contract text proposes `packages/features`; EF4 made the same proposal
and was implemented in `equity_features_intraday` because the admission layer is there and `equity-features` does not depend on
it. Separate catalog (`describe_ef5()`, `ef5_catalog_digest()`); `describe_intraday()` and its digest are unchanged; no package
version bump. `SlotFacts` gains one additive internal field (`open_price`).

## Rulings as implemented

- No default anywhere: `build_ef5_config` takes every parameter, the adjustment label and the adjustment policy version as
  explicit values; `None` is a missing declaration. The shared `AdjustmentSpec` defaults (`raw-v1`, `none`) are never read.
- Adjustment (PQ-1, PQ-2): `unadjusted` = shared `raw` with `raw-v1`; `split_adjusted` = shared `split` with `split-factors-v1`
  and a declared action snapshot and anchor. Anything else (including `total_return`, `dividend_adjusted`) is
  UNSUPPORTED_ADJUSTMENT. The EF5 label and the policy version are config parameters, checked against the shared spec.
- Currency is the EF5 admission rule `[A-Z]{3}` (INVALID_UNIT); the shared `PriceUnit` is unchanged.
- Basis echo (PO-4): the result carries the declared basis in its input bindings (`ResultMetadata.inputs[*].metadata.adjustment`),
  which is the library's only carrier for a basis; the gate maps `raw`/`split` back to the EF5 labels `unadjusted`/`split_adjusted`.
- E4: a `governed_history` output whose span exceeds 63, and `technical.session_return_fraction` under it, is INVALID_CONFIG.
- A forming target bar (end after the market cutoff, no row) is `future_market`; a delivered row ending after the cutoff is BOUNDS.

## Ambiguities met and how they were resolved (for the PO / architect)

1. Hosting: contract says `packages/features`; implemented in `packages/intraday` (see above). Needs a one-line confirmation.
2. Basis echo field: the contract says "result field `basis`"; `FeatureResult` has no such field, so the echo is carried by the
   input bindings. If a literal result field is wanted it is a shared change.
3. Negative volume: the contract says INVALID_SCHEMA (shared stage, RF14); the generic `validate_batch` raises BOUNDS. EF5
   admission checks the volume column first and raises INVALID_SCHEMA, leaving the shared validator untouched.
4. Undeclared coverage (RF15): rows with no per-slot coverage at all are INVALID_SCHEMA in EF5 admission; the generic admission
   would say INCONSISTENT_IDENTITY. A chunk that covers some rows but not others keeps INCONSISTENT_IDENTITY.
5. Identity vs adjustment basis (RF48): a chunk on another basis than the config is INCONSISTENT_IDENTITY here (contract), whereas
   the generic admission says UNSUPPORTED_ADJUSTMENT; EF5 checks the basis before the generic admission runs.
6. Market cutoff: the config builder allows the cutoff to fall inside the target slot (forming bar); the EF4 builder requires it
   at or after the end of the target slot.
7. Doji threshold text is capped at 18 digits per side (the contract regex has no bound).
