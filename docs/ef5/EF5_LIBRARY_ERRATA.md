# EF5 contract errata from the library implementation (PO ruling 2026-10-28, PO ruling, owner-visible record pending)

Additive text errata. The frozen contract prose and every fixture literal are unchanged; no behavior changed.

- **E-L1 (hosting)**: wherever the contract says the library is hosted in `packages/features` (header "Hosting proposal", DP-F8), read: hosted in
  `equity_features_intraday` (module `ef5.*`), as EF4; separate catalog, `describe_intraday()` and its digest unchanged, no package version bump (superseded: intraday a4->a5 in `docs/PRERELEASE_BUMP_EF5.md`).
- **E-L2 (basis echo)**: wherever the contract says every output echoes the basis in the "result field `basis`", read: the echo is carried by the
  input-binding metadata (`ResultMetadata.inputs[*].metadata.adjustment`), mapped raw -> `unadjusted` and split -> `split_adjusted`.
  `FeatureResult` has no basis field and adding one is a shared change. `tools/verify_ef5_library.py` asserts the echo on every result.
- **E-L3 (doji threshold limit)**: `doji_body_max_fraction` is `p/q` with 1 <= p <= q and at most 18 digits per side (bounds the exact-arithmetic cost).
  A longer text is INVALID_CONFIG, never rounded. Additive refusal fixture RF58.
- **E-L4 (partial coverage)**: a chunk that declares per-slot coverage for some bars but not for a delivered bar stays INCONSISTENT_IDENTITY
  (identity stage); rows with no coverage declared at all stay INVALID_SCHEMA (RF15). Additive refusal fixture RF59 (compact key `no_coverage`).

Fixture counts: refusals 57 -> 59 (RF58, RF59, additive); the independent expander models both and `tools/verify_ef5_fixtures.py` pins 59.
