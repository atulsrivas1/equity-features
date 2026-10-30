# Design coverage map (CV0)

Internal, synthetic, pre-release. Hand-maintained input for the feature coverage table; not a release claim.

- `design-coverage-map.json` (schema `ef-design-coverage-map1`) has one row per design item: 166 items in nine families (P, V, M, U, C conditions; S presets; W watchlist rules; L lifecycle; T strategy, catalogue, chart, alert), seeded from the 2026-10-29 parity check as reconciled by the Product Owner. `extras` lists the 11 shipped items with no design row. The design repository is the source of the items and is not edited here.
- Status vocabulary: `implemented`, `partial`, `missing`, `differs`, `out_of_library_scope`. `missing` and `implemented` are derived (no outputs; or every cited output exists and none is a planned DV1 output). `partial`, `differs` and `out_of_library_scope` are asserted by the Product Owner and cite a record under `records/`. There is no hand-written promotion to `implemented`.
- Provisional rows (P6, P14, P17: look-ahead safety of the opening-range interval; P25, P36, P37, V12b: window inclusion, consumer rule max of prior high and current high) are `implemented` with `provisional: true` and name the check that clears them. They are counted apart from confirmed rows.
- `differs` rows name the existing output (`existing_differs`) and the DV1 variant (`variant`). They stay `differs` until the variant has wrong-convention fixture evidence and the Product Owner records the change. DV1 outputs that exist on main count as existing; their delivery is per the Product Owner.
- `asserted.basis` is `ruling` when the reconciliation record rules on the item, and `adopted_from_parity_check` when the record leaves the parity check classification standing.
- `records/` holds verbatim copies of the Product Owner ruling records the map cites, each with a one-line source header (decision D5). `work/` stays unreleased.
- Output ids are checked against the ownership manifest and the library sources; releases agree with the manifest where it names the id. Links to input and output contracts arrive with the io catalogue story (CV1).

Check: `python tools/verify_design_coverage_map.py` (also run by `tools/pre_merge_check.py`).
